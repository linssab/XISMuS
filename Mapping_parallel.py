import numpy as np
import os, sys, logging, multiprocessing
import pickle
import time
import SpecRead
from matplotlib import pyplot as plt
from SpecMath import getpeakarea, refresh_position, setROI, getdif2
from EnergyLib import ElementList, Energies, kbEnergies
from ImgMath import interpolate_zeros, split_and_save

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

        if all_parameters["configure"]["peakmethod"] == 'auto_roi' or \
                all_parameters["configure"]["peakmethod"] == 'PyMcaFit':
           
            ################################################################
            #    Kx_INFO[0] IS THE NET AREA AND [1] IS THE PEAK INDEXES    #
            # Be aware that PyMcaFit method peaks are returned always True #
            # Check SpecMath.py This is due to the high noise in the data  #
            ################################################################
                
            ka_info = getpeakarea(lines[0],specdata,\
                    energyaxis,background,all_parameters["configure"],RAW,usedif2,dif2)
            ka = ka_info[0]
        
            for channel in range(len(specdata)):
                if energyaxis[ka_info[1][0]] < energyaxis[channel]\
                    < energyaxis[ka_info[1][1]]:
                    ROI[channel] += specdata[channel]
            
            kb_info = getpeakarea(lines[1],specdata,\
                    energyaxis,background,all_parameters["configure"],RAW,usedif2,dif2)
            kb = kb_info[0]
        
            for channel in range(len(specdata)):
                if energyaxis[kb_info[1][0]] < energyaxis[channel]\
                    < energyaxis[kb_info[1][1]]:
                    ROI[channel] += specdata[channel]
            
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

def netpeak(all_parameters,Element):
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

    # prepares necessary variables according to peakmethod simple_roi
    if all_parameters["configure"]["peakmethod"] == "simple_roi":
        ka_idx = setROI(kaenergy,all_parameters["energyaxis"],\
                all_parameters["stacksum"],all_parameters["configure"])
        ka_peakdata = all_parameters["stacksum"][ka_idx[0]:ka_idx[1]]
        if all_parameters["configure"]["ratio"] == True:
            kb_idx = setROI(kbenergy,all_parameters["energyaxis"],\
                all_parameters["stacksum"],all_parameters["configure"])
            kb_peakdata = all_parameters["stacksum"][kb_idx[0]:kb_idx[1]]
            if kb_idx[3] == False: 
                logging.warning("No beta line detected for {}. Continuing with alpha only.".\
                        format(Element))
                #resets variables to avoid running the matrix looking for a non existant peak
                elmap = np.zeros([1,all_parameters["dimension"][0],all_parameters["dimension"][1]])
                max_counts = [0]
                line_no = 1
                lines = [kaenergy]
            else: 
                pass
        else: 
             pass

    # prepares necessary variables according to peakmethod auto_roi

    # prepares necessary variables according to peakmethod PyMcaFit
   
    elmap, ROI = grab_line_image(all_parameters,lines)
    
    return elmap, ROI

def prepare_cube(datacube,element_list):
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
 
    # for each element, launches a process
    pool_iterator = []
    for element in element_list:
        pool_iterator.append((all_parameters,element))
    print(convert_bytes(sys.getsizeof(all_parameters)))
    print(convert_bytes(sys.getsizeof(datacube)))
    with multiprocessing.Pool() as pool:
        print("Starting pool")
        results = pool.starmap(netpeak,pool_iterator)

    return results

if __name__=="__main__":
    SpecRead.setup()
    cube_name = SpecRead.DIRECTORY
    cube_path = SpecRead.cube_path
    cube_file = open(cube_path,'rb')
    datacube = pickle.load(cube_file)
    cube_file.close() 
    print(cube_name)
    for setting in datacube.config:
        print(setting,datacube.config[setting])
    print("Start?")
    start = input()
    #elements = ["Ca","Mn","Cl","Ti","Cr","Fe","Pb","Hg"]
    elements = ["Au","Ti"]
    datacube.prepack_elements(elements)
    if start == "Y": 
        results = prepare_cube(datacube,elements)
    else: pass
  
    element_map = np.zeros([datacube.dimension[0],datacube.dimension[1],2,len(elements)])
    print(len(results))
    line = ["_a","_b"]
    for element in range(len(results)):
        for dist_map in range(len(results[element][0])):
            element_map[:,:,dist_map,element] = results[element][0][dist_map]
            datacube.max_counts[elements[element]+line[dist_map]] = results[element][0][dist_map].max()
        datacube.ROI[elements[element]] = results[element][1]
    SpecRead.dump_ratios(results,elements) 
    split_and_save(datacube,element_map,elements)

