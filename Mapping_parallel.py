import numpy as np
import os, sys, logging, multiprocessing
import pickle
import time
from SpecRead import dump_ratios, setup
from matplotlib import pyplot as plt
from SpecMath import getpeakarea, refresh_position, setROI, getdif2
from EnergyLib import ElementList, Energies, kbEnergies
from ImgMath import interpolate_zeros, split_and_save
from numba import jit

def convert_bytes(num):
    """
    Obtained from https://stackoverflow.com/questions/210408
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def grab_line_image(all_parameters,lines):
    start_time = time.time()
    print("\nLine(s): {}\n".format(lines))
    energyaxis = all_parameters["energyaxis"]
    matrix = all_parameters["matrix"]
    matrix_dimension = all_parameters["dimension"]
    usedif2 = True
    scan = ([0,0])
    currentx = scan[0]
    currenty = scan[1]
    el_dist_map = np.zeros([2,all_parameters["dimension"][0],all_parameters["dimension"][1]]) 
    ROI = np.zeros([energyaxis.shape[0]])

    for pos in range(all_parameters["img_size"]):
               
        RAW = matrix[currentx][currenty]
        specdata = matrix[currentx][currenty]
        
        #######################################
        #     ATTEMPT TO FIT THE SPECFILE     #
        # PYMCAFIT DOES NOT USE 2ND DIF CHECK #
        #######################################

        if all_parameters["configure"]["peakmethod"] == 'PyMcaFit': 
            try:
                usedif2 = False
                specdata = SpecFitter.fit(specdata)
            except:
                FITFAIL += 1
                usedif2 = True
                logging.warning("\tFIT FAILED! USING CHANNEL COUNT METHOD FOR {0}/{1}!\t"\
                        .format(pos,all_parameters["img_size"]))
        elif all_parameters["configure"]["peakmethod"] == 'simple_roi': specdata = specdata
        elif all_parameters["configure"]["peakmethod"] == 'auto_roi': specdata = specdata
        else: 
            raise Exception("peakmethod {0} not recognized.".\
                    format(all_parameters["configure"]["peakmethod"]))

        ###########################
        #   SETS THE BACKGROUND   #
        # AND SECOND DIFFERENTIAL #
        ###########################
        
        background = all_parameters["background"][currentx][currenty]
       
        # low-passes second differential
        if usedif2 == True: 
            dif2 = getdif2(specdata,energyaxis,1)
            for i in range(len(dif2)):
                if dif2[i] < -1: dif2[i] = dif2[i]
                elif dif2[i] > -1: dif2[i] = 0
        else: dif2 = np.zeros([specdata.shape[0]])

        ###################################
        #  CALCULATE NET PEAKS AREAS AND  #
        #  ITERATE OVER LIST OF ELEMENTS  #
        ###################################
        
        logging.info("current x = {0} / current y = {1}".format(currentx,currenty))

        ################################################################
        #    Kx_INFO[0] IS THE NET AREA AND [1] IS THE PEAK INDEXES    #
        # Be aware that PyMcaFit method peaks are returned always True #
        # Check SpecMath.py This is due to the high noise in the data  #
        ################################################################
            
        ka_info = getpeakarea(lines[0],specdata,\
                energyaxis,background,all_parameters["configure"],RAW,usedif2,dif2)
        ka = ka_info[0]
        ROI[ka_info[1][0]:ka_info[1][1]] += specdata[ka_info[1][0]:ka_info[1][1]]

        kb_info = getpeakarea(lines[1],specdata,\
                energyaxis,background,all_parameters["configure"],RAW,usedif2,dif2)
        kb = kb_info[0]
        ROI[kb_info[1][0]:kb_info[1][1]] += specdata[kb_info[1][0]:kb_info[1][1]]
        
        el_dist_map[0][currentx][currenty] = ka
        el_dist_map[1][currentx][currenty] = kb

        #########################################
        #   UPDATE ELMAP POSITION AND SPECTRA   #
        #########################################        

        scan = refresh_position(scan[0],scan[1],matrix_dimension)
        currentx = scan[0]
        currenty = scan[1]
        
    ################################    
    #  FINISHED ITERATION PROCESS  #
    #  OVER THE BATCH OF SPECTRA   #
    ################################
    
    logging.info("Finished iteration process for energy {0}\n".format(lines))
    
    timestamp = time.time() - start_time
    logging.info("\nExecution took %s seconds" % (timestamp))
    if all_parameters["configure"]["peakmethod"] == 'PyMcaFit': 
        logging.warning("Fit fail: {0}%".format(100*FITFAIL/all_parameters["dimension"]))
    logging.info("Finished map acquisition!")
    print("Maps maximum: ")
    print(el_dist_map[0].max())
    print(el_dist_map[1].max())

    if all_parameters["configure"]["peakmethod"] == 'auto_roi': 
        el_dist_map = interpolate_zeros(el_dist_map)

    print("Time:")
    print(time.time()-start_time)
    return el_dist_map, ROI

def grab_simple_roi_image(all_parameters,lines):
    
    '''
    Prepare the variables to pass into the matrix slicer
    using SpecMath function setROI it calculates the start and
    end position of the peaks in lines variable
    The position is read from the stacksum derived spectrum
    
    idea: verify the existence of the peak in MPS AND stacksum
    '''
    
    ROI = np.zeros(all_parameters["energyaxis"].shape[0])
    ka_idx = setROI(lines[0],all_parameters["energyaxis"],all_parameters["stacksum"],\
            all_parameters["configure"])
    ka_peakdata = all_parameters["stacksum"][ka_idx[0]:ka_idx[1]]
    ka_map = np.zeros([all_parameters["dimension"][0],all_parameters["dimension"][1]])
    if all_parameters["configure"]["ratio"] == True:
        kb_idx = setROI(lines[1],all_parameters["energyaxis"],all_parameters["stacksum"],\
                all_parameters["configure"])
        kb_peakdata = all_parameters["stacksum"][kb_idx[0]:kb_idx[1]]
        kb_map = np.zeros([all_parameters["dimension"][0],all_parameters["dimension"][1]])
        if kb_idx[3] == False and ka_idx[3] == False:
            logging.info("No alpha {} nor beta {} lines found. Aborting...".format(lines[0],lines[1]))
        elif kb_idx[3] == False: 
            logging.warning("No beta line {} detected. Continuing with alpha only.".format(lines[1]))
    else:
        pass
    slice_matrix(all_parameters["matrix"],all_parameters["background"],ka_map,ka_idx,ROI)
    if all_parameters["configure"]["ratio"] == True:
        slice_matrix(all_parameters["matrix"],all_parameters["background"],kb_map,kb_idx,ROI)
    
    results = []
    results.append(ka_map)
    results.append(kb_map)
    return results, ROI

@jit
def slice_matrix(matrix,bg_matrix,new_image,indexes,ROI):
    for x in range(matrix.shape[0]):
        for y in range(matrix.shape[1]):
            a = float(matrix[x][y][indexes[0]:indexes[1]].sum())
            new_image[x,y] = a
            ROI[indexes[0]:indexes[1]] = ROI[indexes[0]:indexes[1]]+matrix[x][y][indexes[0]:indexes[1]]
    return new_image

def netpeak(all_parameters,Element,results):
    all_parameters = all_parameters.get()

    '''
    verifies the peakmethod and lines and calls
    a function to calculate the peak area throughout
    the spectra matrix
    '''
    
    
    # sets the element energies
    element_idx = ElementList.index(Element)
    kaenergy = Energies[element_idx]*1000
    kbenergy = kbEnergies[element_idx]*1000
    logging.warning("Element {0} energies are: {1:.0f}eV and {2:.0f}eV".\
            format(Element,kaenergy,kbenergy))
    
    if all_parameters["configure"]["ratio"] == True:
        elmap = np.zeros([2,all_parameters["dimension"][0],all_parameters["dimension"][1]])
        max_counts = [0,0]
        line_no = 2
        lines = [kaenergy,kbenergy]
    else: 
        elmap = np.zeros([1,all_parameters["dimension"][0],all_parameters["dimension"][1]])
        max_counts = [0]
        line_no = 1
        lines = [kaenergy]

    if all_parameters["configure"]["peakmethod"] == "simple_roi":
        elmap, ROI = grab_simple_roi_image(all_parameters,lines)

    else: elmap, ROI = grab_line_image(all_parameters,lines)
    
    #results.append((elmap,ROI))
    results.put((elmap,ROI,Element))
    return elmap, ROI

def digest_results(datacube,results,elements):
    element_map = np.zeros([datacube.dimension[0],datacube.dimension[1],2,len(elements)])
    print(element_map.shape)
    print(np.shape(results[0][0]))
    line = ["_a","_b"]
    for element in range(len(results)):
        for dist_map in range(len(results[element][0])):
            element_map[:,:,dist_map,element] = results[element][0][dist_map]
            datacube.max_counts[elements[element]+line[dist_map]] = results[element][0][dist_map].max()
        datacube.ROI[elements[element]] = results[element][1]
    dump_ratios(results,elements) 
    split_and_save(datacube,element_map,elements)
    return 0

def load_data(queue_load,no_elements,variable):
        for i in range(no_elements):
            queue_load.put(variable)

def sort_results(results,element_list):
    sorted_results = []
    for element in range(len(element_list)):
        for packed in range(len(results)):
            if results[packed][2] == element_list[element]:
                print("Matching:")
                print(results[packed][2],element_list[element])
                sorted_results.append(results[packed])
    return sorted_results

def image_cube(datacube,element_list):
    print("Searching elements: {}".format(element_list))
    
    all_parameters = {}
    all_parameters["configure"] = datacube.config
    all_parameters["matrix"] = datacube.matrix
    if all_parameters["configure"]["bgstrip"] != None:
        all_parameters["background"] = datacube.background
    else: all_parameters["background"] = np.zeros([datacube.dimension[0],datacube.dimension[1]])
    all_parameters["energyaxis"] = datacube.energyaxis
    all_parameters["stacksum"] = datacube.sum
    all_parameters["img_size"] = datacube.img_size
    all_parameters["dimension"] = datacube.dimension
    all_parameters["elements"] = element_list
     
    if all_parameters["configure"]["peakmethod"] == "PyMcaFit": import SpecFitter

    processes = []
    results = []
    queue_load = multiprocessing.Queue()
    queue_data = multiprocessing.Queue()
    
    for i in range(len(element_list)):
        if i == 0:
            p = multiprocessing.Process(target=load_data,
                    name="load data",
                    args=(queue_load,len(element_list),all_parameters))
            processes.append(p)
            p.start()

        p = multiprocessing.Process(target=netpeak,
                name=element_list[i],
                args=(queue_load,element_list[i],queue_data))
        processes.append(p)
        p.start()
        
        print(p.name)

    for i in range(len(element_list)):
        data = queue_data.get()
        results.append(data)

    for p in processes:
        p.join()
    print(processes)
    
    
    #mngr1 = multiprocessing.Manager() 
    #results = mngr1.list()
    #jobs= [
    #    multiprocessing.Process(target=netpeak, name=str(element), args=(all_parameters,element,results))
    #for element in element_list
    #]
    #for job in jobs: job.start()
    #for job in jobs: 
    #    job.join()
    #    print("running {}".format(job.name))
    #
     
    srt_results = sort_results(results,element_list)
    digest_results(datacube,srt_results,element_list)
    return results



if __name__=="__main__":
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
    start = input()
    elements = ["Zn","Ca","Mn","Cl","Ti","Cr","Fe","Pb","Hg","S","Cu"]
    #elements = ["Cu","Ti"]
    
    # prepack must be done from GUI before calling image_cube()
    datacube.prepack_elements(elements)
    if start == "Y": 
        results = image_cube(datacube,elements)
    else: pass
    

