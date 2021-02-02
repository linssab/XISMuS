#################################################################
#                                                               #
#          ELEMENT MAP GENERATOR                                #
#                        version: 1.3.2 - Feb - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

#############
# Utilities #
#############
import logging
logger = logging.getLogger("logfile")
import sys, os
import numpy as np
import pickle
#############

#################
# Local imports #
#################
import Elements
import Constants
from . import SpecMath
from . import SpecRead
from . import ImgMath
from GUI.ProgressBar import ReadProgress
#################

####################
# External modules #
####################
import matplotlib.pyplot as plt
import time
import cv2
from tkinter import *
from tkinter import ttk
####################


def select_lines(element,ratio):
    """ Returns the theoretical peak position (in eV)
    for the alpha and beta energy macros """

    element_idx = Elements.ElementList.index(element)
    kaenergy = Elements.Energies[element_idx]*1000
    kbenergy = Elements.kbEnergies[element_idx]*1000
    
    if  ratio == True:
        max_counts = [0,0]
        line_no = 2
        lines = [kaenergy,kbenergy]
    else: 
        max_counts = [0]
        line_no = 1
        lines = [kaenergy,0]
    return lines

def grab_simple_roi_image(cube,lines,custom_energy=False):
    """ Prepare the variables to pass into the matrix slicer.
    Using SpecMath function setROI it calculates the start and
    end position of the peaks in lines variable
    The position is read from the MPS spectrum """
    
    results = []
    ROI = np.zeros(cube.energyaxis.shape[0])
    
    if custom_energy == True:
        
        ####################################################
        # slices the mtrix for a custom energy range input #
        ####################################################

        indexes = [0,0]
        custom_map = np.zeros([cube.dimension[0],cube.dimension[1]])
        idx = 0
        while cube.energyaxis[idx] <= lines[0]:
            idx+=1
        indexes[0] = idx
        while cube.energyaxis[idx] <= lines[1]:
            idx+=1
        indexes[1] = idx
        
        slice_matrix(cube.matrix,cube.background,custom_map,indexes,ROI)
        results.append(custom_map)
        results.append(custom_map)
    
    else:

        ################################
        # sets up the indexes to slice #
        ################################

        ka_map = np.zeros([cube.dimension[0],cube.dimension[1]])
        kb_map = np.zeros([cube.dimension[0],cube.dimension[1]])
        ka_idx = SpecMath.setROI(lines[0],cube.energyaxis,cube.sum,cube.config)
        
        ######################################
        # verifies beta line for the element #
        ######################################

        if cube.config["ratio"] == True:
            kb_idx = SpecMath.setROI(lines[1],cube.energyaxis,cube.mps,cube.config)
            if kb_idx[3] == False and ka_idx[3] == False:
                logger.info(
                        "No alpha {} nor beta {} lines found. Skipping...".format(
                            lines[0],lines[1]))
            elif kb_idx[3] == False: 
                logger.warning(
                        "No beta line {} detected. Continuing with alpha only.".format(
                            lines[1]))
        else:
            pass
        
        #####################
        # slices the matrix #
        #####################

        slice_matrix(cube.matrix,cube.background,ka_map,ka_idx,ROI)
        if cube.config["ratio"] == True:
            if kb_idx[3] == True:
                slice_matrix(cube.matrix,cube.background,kb_map,kb_idx,ROI)

        ##################
        # append results #
        ##################

        results.append(ka_map)
        results.append(kb_map)
    return results, ROI

def slice_matrix(matrix,bg_matrix,new_image,indexes,ROI):
    """ Slices the matrix """

    c = 0
    for x in range(matrix.shape[0]):
        for y in range(matrix.shape[1]):
            a = float(matrix[x][y][indexes[0]:indexes[1]].sum())
            b = float(bg_matrix[x][y][indexes[0]:indexes[1]].sum())
            if b > a: c == 0
            else: c = a-b
            new_image[x][y] = c
            ROI[indexes[0]:indexes[1]] = ROI[indexes[0]:indexes[1]] + matrix[x][y][indexes[0]:indexes[1]]
    return new_image

def getpeakmap(element_list,datacube):
    """ Iterates the datacube objects and return a matrix with 
    shape: [X][Y][MACROS][ELEMENT] """

    timer = time.time()
    imagsize = datacube.dimension
    imagex = imagsize[0]
    imagey = imagsize[1]
    dimension = imagex*imagey
    
    datacube.prepack_elements(element_list)
   
    configdict = datacube.config
    ratio = configdict.get('ratio')
    normalize = configdict.get('enhance')
    bgstrip = configdict.get('bgstrip')
    peakmethod = configdict.get('peakmethod')

    ################-getpeakmap-#####################
    #   GETPEAKMAP READS THE BATCH OF SPECTRA AND   #
    #   RETURNS A 2D-ARRAY WITH THE COUNTS FOR THE  #
    #   KA AND KB LINES OF INPUT ELEMENT(S).        #
    #################################################
    
    KaElementsEnergy = Elements.Energies
    KbElementsEnergy = Elements.kbEnergies
    
    logger.info("Started energy axis calibration")
    energyaxis = datacube.energyaxis
    logger.info("Finished energy axis calibration")
    current_peak_factor = 0
    max_peak_factor = 0
    ymax_spec = None
    usedif2 = True
    ratiofiles = ['' for x in range(len(element_list))]


    if element_list[0] in Elements.ElementList:
        logger.info("Started acquisition of {0} map(s)".format(element_list))
        
        currentspectra = Constants.FIRSTFILE_ABSPATH
        debug = False 

        ##############################
        # INITIALIZE OTHER VARIABLES #
        ##############################
        
        FITFAIL = 0
        partialtimer = time.time()
        if ratio == True: elmap = np.zeros([imagex,imagey,2,len(element_list)],dtype="float32")
        else: elmap = np.zeros([imagex,imagey,1,len(element_list)],dtype="float32")
        ka_idx, kb_idx = [],[]
        ka_peakdata, kb_peakdata = [],[]
        for Element in element_list:
            ka_idx.append([np.nan,np.nan,np.nan,np.nan])
            kb_idx.append([np.nan,np.nan,np.nan,np.nan])
            ka_peakdata.append(np.nan)
            kb_peakdata.append(np.nan)
        scan = ([0,0])
        currentx = scan[0]
        currenty = scan[1]
        kaindex,kbindex,kaenergy,kbenergy = \
                (np.zeros(len(element_list),dtype='int') for i in range(4))
        
        ##############################

        for Element in range(len(element_list)):

            # sets ka energy
            kaindex[Element] = Elements.ElementList.index(element_list[Element])
            kaenergy[Element] = KaElementsEnergy[kaindex[Element]]*1000
        
            logger.warning("Energy {0:.0f} eV for element {1} being used as lookup!"\
                .format(kaenergy[Element],element_list[Element]))
        
            if ratio == True:
                ratiofiles[Element] = str(os.path.join(SpecRead.output_path,
                        "{1}_ratio_{0}.txt".format(element_list[Element],Constants.DIRECTORY)))
                r_file = open(ratiofiles[Element],"w+")
                r_file.readline()
                r_file.truncate()
                r_file.write("-"*10 + " Counts of Element {0} "\
                        .format(element_list[Element]) + 10*"-" + '\n')
                r_file.write("row\tcolumn\tline1\tline2\tratio\n")

                # sets kb energy
                kbindex[Element] = Elements.ElementList.index(element_list[Element])
                kbenergy[Element] = Elements.kbEnergies[kbindex[Element]]*1000
                r_file.close() 
                logger.warning("Energy {0:.0f} eV for element {1} being used as lookup!"\
                        .format(kbenergy[Element],element_list[Element]))
           
        logger.info("Starting iteration over spectra...\n")
        
        # starts the loading bar
        progressbar = ReadProgress(datacube.img_size,0) 
        
        for ITERATION in range(dimension):
               
            spec = currentspectra  #updates the current file name / debug mode only
            specdata = datacube.matrix[currentx][currenty]
            
            #############################################
            #     TO ADD MORE METHODS IN THE FUTURE     #
            #############################################
            
            if peakmethod == 'auto_roi': specdata = specdata
            else: 
                raise Exception("peakmethod {0} not recognized.".format(peakmethod))
 
            ###########################
            #   SETS THE BACKGROUND   #
            # AND SECOND DIFFERENTIAL #
            ###########################
            
            background = datacube.background[currentx][currenty]
            
            if usedif2 == True: 
                dif2 = SpecMath.getdif2(specdata,1)
                for i in range(len(dif2)):
                    if dif2[i] < -1: dif2[i] = dif2[i]
                    elif dif2[i] > -1: dif2[i] = 0
            else: dif2 = 0

            ###################################
            #  CALCULATE NET PEAKS AREAS AND  #
            #  ITERATE OVER LIST OF ELEMENTS  #
            ###################################
            
            logger.debug("----- current x = {0} / current y = {1} -----".format(
                currentx,currenty))
            if debug == True: logger.info("Specfile being processed is: {0}\n".format(spec))
 
            for Element in range(len(element_list)):
            
                if peakmethod == 'auto_roi':
                   
                    ################################################################
                    #    Kx_INFO[0] IS THE NET AREA AND [1] IS THE PEAK INDEXES    #
                    # Check SpecMath.py This is due to the high noise in the data  #
                    ################################################################
                        
                    ka_info = SpecMath.getpeakarea(
                            kaenergy[Element],
                            specdata,
                            energyaxis,
                            background,
                            configdict,
                            usedif2,
                            dif2)
                    ka = ka_info[0]
                    
                    if ka > 0:
                        datacube.ROI[element_list[Element]][ka_info[1][0]:ka_info[1][1]] += \
                            specdata[ka_info[1][0]:ka_info[1][1]]

                    if ka == 0: 
                        ka,kb = 0, 0
                        elmap[currentx][currenty][0][Element] = 0
                    
                    elif ka > 0 and ratio == False: kb = 0
                    
                    elif ka > 0 and ratio == True:
                        kb_info = SpecMath.getpeakarea(
                                kbenergy[Element],
                                specdata,
                                energyaxis,
                                background,
                                configdict,
                                usedif2,
                                dif2)
                        kb = kb_info[0]
                        
                        datacube.ROI[element_list[Element]][kb_info[1][0]:kb_info[1][1]] += \
                            specdata[kb_info[1][0]:kb_info[1][1]]

                        elmap[currentx][currenty][1][Element] = kb
                    
                    elmap[currentx][currenty][0][Element] = ka

                    if datacube.max_counts[element_list[Element]+"_a"] < ka:
                        datacube.max_counts[element_list[Element]+"_a"] = ka
                    if datacube.max_counts[element_list[Element]+"_b"] < kb:
                        datacube.max_counts[element_list[Element]+"_b"] = kb

                elif peakmethod == "insert new spectra iterative methods here":
                    pass
                
                row = scan[0]
                column = scan[1]
                if ratio == True: 
                   
                    #################################
                    # WRITES NET PEAK AREAS TO FILE #
                    #################################
                    
                    try: 
                        r_file = open(ratiofiles[Element],'a')
                        if debug == True: 
                            r_file.write("%d\t%d\t%d\t%d\t%s\n" % (row, column, ka, kb, spec))
                            logger.info(
                                    "File {0} has net peaks of {1} and {2} for element {3}\n"\
                                    .format(spec,ka,kb,element_list[Element]))
                        else:
                            if ka == 0: ka,kb,ka_kb = 0,0,0
                            elif kb == 0: ka_kb = 0
                            elif ka > 0 and kb > 0: ka_kb = ka/kb
                            r_file.write(
                                    "%d\t%d\t%d\t%d\t%f\n" % (row, column, ka, kb, (ka_kb)))
                    except:
                        logger.warning("ka and kb not calculated for some unknown reason.\
                    Check Config.cfg for the correct spelling of peakmethod option!\
                    ka={0},kb={1}".format(ka,kb))

                    #################################

            #########################################
            #   UPDATE ELMAP POSITION AND SPECTRA   #
            #########################################        

            scan = SpecMath.refresh_position(scan[0],scan[1],datacube.dimension)
            currentx = scan[0]
            currenty = scan[1]
            if debug == True: currentspectra = SpecRead.updatespectra(spec,dimension)
            
            progressbar.updatebar(ITERATION)

        ################################    
        #  FINISHED ITERATION PROCESS  #
        #  OVER THE BATCH OF SPECTRA   #
        ################################
        
        logger.info("Finished iteration process for element(s) {0}".format(element_list))
        
        
        timestamp = time.time() - partialtimer
        logger.info("Execution took %s seconds" % (timestamp))
        
        timestamps = open(os.path.join(SpecRead.__BIN__,"timestamps.txt"),"a")
        timestamps.write("\n{5}\n{0} bgtrip={1} enhance={2} peakmethod={3}\t\n{6} elements\n{4} seconds\n".format(Element,
            bgstrip,
            normalize,
            peakmethod,
            timestamp,
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            element_list))
       
        logger.info("Finished map acquisition!")
    
    else:
        logger.warning("{0} not an element!".format(element_list))
        raise ValueError("{0} not an element!".format(element_list))
    
    if peakmethod == 'auto_roi': 
        elmap = ImgMath.interpolate_zeros(elmap)
    
    #print("Time:")
    #print(time.time()-timer)
    ImgMath.split_and_save(datacube,elmap,element_list)
    return elmap

def getdensitymap(datacube):
    
    ##########-getdensitymap-############
    #   RETUNRS A 2D-ARRAY WITH TOTAL   #
    #   COUNTS PER PIXEL.               #
    #####################################

    timer = time.time()
    logger.info("Started acquisition of density map")
    
    density_map = np.zeros([datacube.dimension[0],datacube.dimension[1]],dtype="float32")
    for x in range(datacube.dimension[0]):
        for y in range(datacube.dimension[1]):
            spec = datacube.matrix[x][y]
            background = datacube.background[x][y]    
            density_map[x][y] = abs(spec.sum()-background.sum())
    logger.info("Finished fetching density map!")
    logger.info("Execution took %s seconds" % (time.time() - timer))
    return density_map

if __name__=="__main__":
    SpecRead.setup()
    cube_name = Constants.DIRECTORY
    cube_path = SpecRead.cube_path
    cube_file = open(cube_path,'rb')
    datacube = pickle.load(cube_file)
    cube_file.close() 
    print(cube_name)
    configdict = datacube.config
    myelements = ["Cu","Au","Fe","Pb"]
    myimage = getpeakmap(myelements,datacube)
   
