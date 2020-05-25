#################################################################
#                                                               #
#          Mapping module for multi-core processing             #
#                        version: 1.0.1 - May - 2020            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import numpy as np
import os, sys, logging, multiprocessing
logger = logging.getLogger("logfile")
from multiprocessing import freeze_support
from psutil import cpu_count
freeze_support()
#in python 3 Queue is lowercase:
import queue
import pickle
import time
import SpecMath
from SpecRead import dump_ratios, setup, __BIN__, __PERSONAL__
from matplotlib import pyplot as plt
from EnergyLib import ElementList, Energies, kbEnergies
from ImgMath import interpolate_zeros, split_and_save

def convert_bytes(num):

    """ Obtained from https://stackoverflow.com/questions/210408 """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def break_list(element_list,max_instances):
    
    """ cores variable governs how many instances can be 
    called and divides the chuncks """

    cores = cpu_count()
    if max_instances == 0:
        cores = cpu_count()
    elif max_instances < cores:
        cores = max_instances
    chunks = []
    chunk_slice = 0
    quo = int(len(element_list)/cores)
    rest = int(len(element_list)%cores)
    for i in range(quo):
        slice1 = []
        if i >= 1: chunk_slice += 1
        for j in range(cores):
            slice1.append(element_list[chunk_slice*cores+j])
        chunks.append(slice1)
    if rest >= 1:
        slice1 = []
        for i in range(rest):
            slice1.append(element_list[quo*cores+i])
        chunks.append(slice1)
    return chunks

def grab_line(cube,lines,iterator,Element):

    """ Uses SpecMath library to get the net area of the energies passed as
    arguments to this funcion
    This funcion is called by call_peakmethod inside start_reader function  """
    
    start_time = time.time()
    energyaxis = cube["energyaxis"]
    matrix = cube["matrix"]
    matrix_dimension = cube["dimension"]
    usedif2 = True
    scan = ([0,0])
    currentx = scan[0]
    currenty = scan[1]
    el_dist_map = np.zeros([2,matrix_dimension[0],matrix_dimension[1]],dtype="float32") 
    ROI = np.zeros([energyaxis.shape[0]],dtype="float32")
    FITFAIL = 0

    for pos in range(cube["img_size"]):
               
        RAW = matrix[currentx][currenty]
        specdata = matrix[currentx][currenty]
        
        if cube["config"]["peakmethod"] == 'auto_roi': specdata = specdata
        else: 
            raise Exception("peakmethod {0} not recognized.".\
                    format(cube["config"]["peakmethod"]))

        ###########################
        #   SETS THE BACKGROUND   #
        # AND SECOND DIFFERENTIAL #
        ###########################
        
        background = cube["background"][currentx][currenty]
       
        # low-passes second differential
        if usedif2 == True: 
            dif2 = SpecMath.getdif2(specdata,1)
            for i in range(len(dif2)):
                if dif2[i] < -1: dif2[i] = dif2[i]
                elif dif2[i] > -1: dif2[i] = 0
        else: dif2 = np.zeros([specdata.shape[0]])

        ###################################
        #  CALCULATE NET PEAKS AREAS AND  #
        #  ITERATE OVER LIST OF ELEMENTS  #
        ###################################
        
        logger.debug("current x = {0} / current y = {1}".format(currentx,currenty))

        ################################################################
        #    Kx_INFO[0] IS THE NET AREA AND [1] IS THE PEAK INDEXES    #
        ################################################################
            
        ka_info = SpecMath.getpeakarea(lines[0],specdata,\
                energyaxis,background,cube["config"],RAW,usedif2,dif2)
        ka = ka_info[0]
        if ka>0: ROI[ka_info[1][0]:ka_info[1][1]] += specdata[ka_info[1][0]:ka_info[1][1]]
        el_dist_map[0][currentx][currenty] = ka

        if cube["config"]["ratio"]: 
            kb_info = SpecMath.getpeakarea(lines[1],specdata,\
                    energyaxis,background,cube["config"],RAW,usedif2,dif2)
            kb = kb_info[0]
            if kb>0: ROI[kb_info[1][0]:kb_info[1][1]] += specdata[kb_info[1][0]:kb_info[1][1]]
            el_dist_map[1][currentx][currenty] = kb
        
        iterator.value = iterator.value + 1

        #########################################
        #   UPDATE ELMAP POSITION AND SPECTRA   #
        #########################################        
        
        scan = SpecMath.refresh_position(scan[0],scan[1],matrix_dimension)
        currentx = scan[0]
        currenty = scan[1]
        
    ################################    
    #  FINISHED ITERATION PROCESS  #
    #  OVER THE BATCH OF SPECTRA   #
    ################################
    
    timestamp = time.time() - start_time
    logger.info("Execution took %s seconds" % (timestamp))
    timestamps = open(os.path.join(__BIN__,"timestamps.txt"),"a")
    timestamps.write("\n{5} - MULTIPROCESSING\n{0} bgtrip={1} enhance={2} peakmethod={3}\n{4} seconds\n".format(
        Element,
        cube["config"]["bgstrip"],
        cube["config"]["enhance"],
        cube["config"]["peakmethod"],
        timestamp,
        time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
       
    logger.info("Finished map acquisition!")
    if cube["config"]["peakmethod"] == 'auto_roi': 
        el_dist_map = interpolate_zeros(el_dist_map)
    
    logger.warning("Element {0} energies are: {1:.0f}eV and {2:.0f}eV".\
            format(Element,lines[0],lines[1]))
    logger.info("Runtime for {}: {}".format(Element,time.time()-start_time))
    return el_dist_map, ROI

def digest_results(datacube,results,elements):
    element_map = np.zeros([datacube.dimension[0],datacube.dimension[1],2,len(elements)],
            dtype="float32")
    line = ["_a","_b"]
    for element in range(len(results)):
        for dist_map in range(len(results[element][0])):
            element_map[:,:,dist_map,element] = results[element][0][dist_map]
            datacube.max_counts[elements[element]+line[dist_map]] = results[element][0][dist_map].max()
        datacube.ROI[elements[element]] = results[element][1]
    dump_ratios(results,elements) 
    split_and_save(datacube,element_map,elements)
    return 0

def sort_results(results,element_list):
    sorted_results = []
    for element in range(len(element_list)):
        for packed in range(len(results)):
            if results[packed][2] == element_list[element]:
                sorted_results.append(results[packed])
    return sorted_results

def start_reader(cube,Element,iterator,results,F,N):
    SpecMath.FN_set(F,N)
    
    def call_peakmethod(cube,Element,iterator,results):
        
        """ verifies the peakmethod and lines and calls
        a function to calculate the peak area throughout
        the spectra matrix """
     
        #############################
        # sets the element energies #
        #############################

        element_idx = ElementList.index(Element)
        kaenergy = Energies[element_idx]*1000
        kbenergy = kbEnergies[element_idx]*1000
        logger.warning("Element {0} energies are: {1:.0f}eV and {2:.0f}eV".format(
            Element,kaenergy,kbenergy))

        if  cube["config"]["ratio"] == True:
            elmap = np.zeros([2,cube["dimension"][0],cube["dimension"][1]],dtype="float32")
            max_counts = [0,0]
            line_no = 2
            lines = [kaenergy,kbenergy]
        else: 
            elmap = np.zeros([1,cube["dimension"][0],cube["dimension"][1]],dtype="float32")
            max_counts = [0]
            line_no = 1
            lines = [kaenergy,0]

        elmap, ROI = grab_line(cube,lines,iterator,Element)
        results.put((elmap,ROI,Element))
        
        return results
   
    call_peakmethod(cube,Element,iterator,results) 
    return results

class Cube_reader():
    
    def __init__(__self__,matrix,energyaxis,background,config,element_list,instances):
        __self__.cube = {}
        __self__.cube["matrix"] = matrix
        __self__.cube["background"] = background
        __self__.cube["energyaxis"] = energyaxis
        __self__.cube["config"] = config
        __self__.cube["dimension"] = matrix.shape
        __self__.element_list = element_list
        __self__.cube["img_size"] = __self__.cube["matrix"].shape[0]*\
                __self__.cube["matrix"].shape[1]
        __self__.bar_max = len(element_list)*__self__.cube["img_size"]
        __self__.p_bar = SpecMath.Busy(len(element_list),0)
        __self__.p_bar.update_text("Pre-loading data...")
        __self__.results = multiprocessing.Queue()
        __self__.p_bar_iterator = multiprocessing.Value('i',0)
        __self__.p_bar_iterator.value = 0
        __self__.processes = []
        __self__.process_names = []
        __self__.run_count = 0 
        __self__.chunks = break_list(__self__.element_list,instances)
    
    def start_workers(__self__,N,F):
        __self__.p_bar.progress["maximum"] = __self__.cube["img_size"]\
                *len(__self__.element_list)
        __self__.p_bar.update_text("Processing data...")
        __self__.p_bar.updatebar(__self__.p_bar_iterator.value)


        partial_ = []
        for chunk in __self__.chunks:
            try:
                for p in __self__.processes:
                    p.terminate()
                    logger.info("Terminated {}".format(p))
            except: pass
            __self__.processes = []
            __self__.process_names = []
            i = 0
            for element in chunk:
                p = multiprocessing.Process(target=start_reader,
                    name=element,
                    args=(__self__.cube,element,__self__.p_bar_iterator,__self__.results,N,F))
                __self__.processes.append(p)
                __self__.process_names.append(p.name)
                logger.info("Polling process {}".format(p))
            
        
            for p in __self__.processes:
                i = i + 1
                __self__.p_bar.update_text("Polling "+p.name)
                __self__.p_bar.updatebar(__self__.p_bar_iterator.value)
                p.start()
                
            __self__.run_count += 1
            __self__.periodic_check()
        
            for i in range(len(chunk)):
                data = __self__.results.get()
                partial_.append(data)
            
            for p in __self__.processes:
                if p.exitcode != 0:
                    p.join()

        return partial_ 
    
    def checkbar(__self__):
        __self__.p_bar.update_text("Processing data...")
        while __self__.p_bar_iterator.value < \
                int(len(__self__.chunks[__self__.run_count-1]*__self__.run_count)*\
                __self__.cube["img_size"]*0.98):
            __self__.p_bar.updatebar(__self__.p_bar_iterator.value)
        if __self__.run_count == len(__self__.chunks):
            while __self__.p_bar_iterator.value < int(__self__.p_bar.progress["maximum"]*0.98):
                __self__.p_bar.updatebar(__self__.p_bar_iterator.value)
        return 0

    def periodic_check(__self__):
        __self__.checkbar()
      
    
if __name__=="__main__":
    """
    setup()
    from SpecRead import DIRECTORY as cube_name
    from SpecRead import cube_path
    cube_file = open(cube_path,'rb')
    datacube = pickle.load(cube_file)
    cube_file.close() 
    print(cube_name)
    for setting in datacube.config:
        print(setting,datacube.config[setting])
    print("Start?")
    #start = input()
    start = "N"
    elements = ["Zn","Ca","Ti","Cr","Fe","Pb","Hg","Cu"]
    #elements = ["Cu","Pb","Fe"]
    
    from psutil import virtual_memory
    from psutil import cpu_count
    cube_status = os.stat(cube_path)
    cube_size = cube_status.st_size
    sys_mem = dict(virtual_memory()._asdict())
    rnt_mem = [(cube_size*len(elements)),sys_mem["available"]]
    process_memory = (convert_bytes(rnt_mem[0]),convert_bytes(rnt_mem[1]))
    print(process_memory)


    # prepack must be done from GUI before calling image_cube()
    datacube.prepack_elements(elements)
    if start == "Y": 
        results = image_cube(datacube,elements)
    else:
        reader = Cube_reader(datacube,elements)
        results = reader.start_workers()
        reader.p_bar.update_text("Sorting maps...")
        results = sort_results(results,elements)
        reader.p_bar.update_text("Digesting results...")
        digest_results(datacube,results,elements)
    """
    logger.info("This is Mapping_parallel.py module")
