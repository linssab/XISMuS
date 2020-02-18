#################################################################
#                                                               #
#          ELEMENT MAP GENERATOR                                #
#                        version: 0.0.0                         #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import logging
logging.debug("Importing module Mapping.py...")
import sys
import numpy as np
import pickle
import SpecMath
import SpecRead
import EnergyLib
import ImgMath
import matplotlib.pyplot as plt
import time
import cv2
logging.debug("Finished Mapping imports.")


from tkinter import *
from tkinter import ttk


class Busy:
    
    def __init__(__self__,max_,min_):
        __self__.master = Toplevel()
        __self__.master.resizable(False,False)
        __self__.master.overrideredirect(True)
        x = __self__.master.winfo_screenwidth()
        y = __self__.master.winfo_screenheight()
        win_x = __self__.master.winfo_width()
        win_y = __self__.master.winfo_height()
        __self__.master.geometry('{}x{}+{}+{}'.format(166, 71,\
                int((x/2)-80), int((y/2)-35)))
        __self__.outerframe = Frame(__self__.master, bd=3, relief=RIDGE)
        __self__.outerframe.grid(row=0, column=0)
        __self__.master.label = Label(__self__.outerframe, text="Reading spectra...").\
                grid(row=0,column=0) 
        __self__.master.body = Frame(__self__.outerframe)        
        __self__.master.body.grid(row=1,column=0)
        __self__.progress = ttk.Progressbar(__self__.master.body, orient="horizontal",length=160, mode="determinate",maximum=max_)
        __self__.progress.grid(row=0,column=0)
        __self__.spec = Label(__self__.master.body, text="")       
        __self__.spec.grid(row=2,column=0)

    def updatebar(__self__,value):
        if value == __self__.progress["maximum"]-1: 
            __self__.master.destroy()
        else:
            __self__.progress["value"] = value
            __self__.progress.update()
            __self__.spec["text"] = "Spec {0} of {1}".format(value,__self__.progress["maximum"])
            __self__.spec.update()

def select_lines(element,ratio):
    element_idx = EnergyLib.ElementList.index(element)
    kaenergy = EnergyLib.Energies[element_idx]*1000
    kbenergy = EnergyLib.kbEnergies[element_idx]*1000
    
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
    
    '''
    Prepare the variables to pass into the matrix slicer
    using SpecMath function setROI it calculates the start and
    end position of the peaks in lines variable
    The position is read from the stacksum derived spectrum
    
    idea: verify the existence of the peak in MPS AND stacksum
    '''
    results = []
    ROI = np.zeros(cube.energyaxis.shape[0])
    
    if custom_energy == True:
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
        # sets up the indexes to slice
        ka_map = np.zeros([cube.dimension[0],cube.dimension[1]])
        kb_map = np.zeros([cube.dimension[0],cube.dimension[1]])
        
        ka_idx = SpecMath.setROI(lines[0],cube.energyaxis,cube.sum,cube.config)
        # verifies beta line for the element
        if cube.config["ratio"] == True:
            kb_idx = SpecMath.setROI(lines[1],cube.energyaxis,cube.sum,cube.config)
            if kb_idx[3] == False and ka_idx[3] == False:
                logging.info("No alpha {} nor beta {} lines found. Skipping...".format(lines[0],lines[1]))
            elif kb_idx[3] == False: 
                logging.warning("No beta line {} detected. Continuing with alpha only.".format(lines[1]))
        else:
            pass
        
        # follows the execution and slice the data
        slice_matrix(cube.matrix,cube.background,ka_map,ka_idx,ROI)
        if cube.config["ratio"] == True:
            if kb_idx[3] == True:
                slice_matrix(cube.matrix,cube.background,kb_map,kb_idx,ROI)
        
        # append results
        results.append(ka_map)
        results.append(kb_map)
    return results, ROI

#@jit
def slice_matrix(matrix,bg_matrix,new_image,indexes,ROI):
    """
    Slices the matrix
    """
    c = 0
    for x in range(matrix.shape[0]):
        for y in range(matrix.shape[1]):
            a = float(matrix[x][y][indexes[0]:indexes[1]].sum())
            b = float(bg_matrix[x][y][indexes[0]:indexes[1]].sum())
            if b > a: c == 0
            else: c = a-b
            new_image[x,y] = c
            ROI[indexes[0]:indexes[1]]=ROI[indexes[0]:indexes[1]] + matrix[x][y][indexes[0]:indexes[1]]
    return new_image

def getpeakmap(element_list,datacube):
    timer = time.time()
    imagsize = SpecRead.getdimension()
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
    
    if peakmethod == 'PyMcaFit': import SpecFitter
    KaElementsEnergy = EnergyLib.Energies
    KbElementsEnergy = EnergyLib.kbEnergies
    
    logging.info("Started energy axis calibration")
    energyaxis = datacube.energyaxis
    save_energy_axis = open(SpecRead.workpath + '/' + 'axis.txt','w+')
    for i in range(energyaxis.shape[0]):
        save_energy_axis.write("{0}\n".format(energyaxis[i]))
    logging.info("Finished energy axis calibration")
    current_peak_factor = 0
    max_peak_factor = 0
    ymax_spec = None
    usedif2 = True
    ratiofiles = ['' for x in range(len(element_list))]

    ######################################################
    # INITIALIZE CONTROL VARIABLES CUMSUM AND CUMSUM_RAW #
    ######################################################
    #CUMSUM = np.zeros([len(energyaxis)])
    #CUMSUM_RAW = np.zeros([len(energyaxis)])

    ######################################################

    if element_list[0] in EnergyLib.ElementList:
        logging.info("Started acquisition of {0} map(s)".format(element_list))
        
        ####### this is for debug mode #######
        currentspectra = SpecRead.FIRSTFILE_ABSPATH
        debug = False 
        ####### to register the NAME of the file #######

        ##############################
        # INITIALIZE OTHER VARIABLES #
        ##############################
        
        FITFAIL = 0
        partialtimer = time.time()
        if ratio == True: elmap = np.zeros([imagex,imagey,2,len(element_list)])
        else: elmap = np.zeros([imagex,imagey,1,len(element_list)])
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
            kaindex[Element] = EnergyLib.ElementList.index(element_list[Element])
            kaenergy[Element] = KaElementsEnergy[kaindex[Element]]*1000
        
            logging.warning("Energy {0:.0f} eV for element {1} being used as lookup!"\
                .format(kaenergy[Element],element_list[Element]))
        
            if ratio == True:
                ratiofiles[Element] = str(SpecRead.output_path+\
                        '{1}_ratio_{0}.txt'.format(element_list[Element],SpecRead.DIRECTORY))
                r_file = open(ratiofiles[Element],'w+')
                r_file.readline()
                r_file.truncate()
                r_file.write("-"*10 + " Counts of Element {0} "\
                        .format(element_list[Element]) + 10*"-" + '\n')
                r_file.write("row\tcolumn\tline1\tline2\tratio\n")

                # sets kb energy
                kbindex[Element] = EnergyLib.ElementList.index(element_list[Element])
                kbenergy[Element] = EnergyLib.kbEnergies[kbindex[Element]]*1000
                r_file.close() 
                logging.warning("Energy {0:.0f} eV for element {1} being used as lookup!"\
                        .format(kbenergy[Element],element_list[Element]))
        
        ################################
        #  SETS SIMPLE ROI PARAMETERS  #
        ################################
        stacksum = datacube.sum
        conditional_ratio = np.zeros([len(element_list)])
        for Element in range(len(element_list)):
            if peakmethod == 'simple_roi':
                ka_idx[Element] = SpecMath.setROI(kaenergy[Element],energyaxis,stacksum,configdict)
                ka_peakdata[Element] = stacksum[ka_idx[Element][0]:ka_idx[Element][1]]
                if ratio == True:
                    conditional_ratio[Element] = True
                    kb_idx[Element] = SpecMath.setROI(kbenergy[Element],energyaxis,stacksum,configdict)
                    kb_peakdata[Element] = stacksum[kb_idx[Element][0]:kb_idx[Element][1]]
                    if kb_idx[Element][3] == False and ka_idx[Element][3] == False:
                        logging.info("No alpha nor beta lines found for {}. Aborting...".\
                                format(element_list[Element]))
                    elif kb_idx[Element][3] == False: 
                        logging.warning("No beta line detected for {}. Continuing with alpha only.".\
                                format(element_list[Element]))
                        conditional_ratio[Element] = False
                else:
                    pass
    
        #############################################
        #   STARTS ITERATION OVER SPECTRA BATCH     #
        #############################################
            
        logging.info("Starting iteration over spectra...\n")
        
        # starts the loading bar
        progressbar = Busy(datacube.img_size,0) 
        
        for ITERATION in range(dimension):
               
            spec = currentspectra  #updates the current file name / debug mode only
            RAW = datacube.matrix[currentx][currenty]
            specdata = datacube.matrix[currentx][currenty]
            
            #######################################
            #     ATTEMPT TO FIT THE SPECFILE     #
            # PYMCAFIT DOES NOT USE 2ND DIF CHECK #
            #######################################

            if peakmethod == 'PyMcaFit': 
                try:
                    usedif2 = False
                    specdata = SpecFitter.fit(specdata)
                except:
                    FITFAIL += 1
                    usedif2 = True
                    #print("\tCHANNEL COUNT METHOD USED FOR FILE {0}/{1}!\t"\
                    #        .format(ITERATION,datacube.img_size))
                    logging.warning("\tFIT FAILED! USING CHANNEL COUNT METHOD FOR {0}/{1}!\t"\
                            .format(ITERATION,datacube.img_size))
            elif peakmethod == 'simple_roi': specdata = specdata
            elif peakmethod == 'auto_roi': specdata = specdata
            else: 
                raise Exception("peakmethod {0} not recognized.".format(peakmethod))
 
            ###########################
            #   SETS THE BACKGROUND   #
            # AND SECOND DIFFERENTIAL #
            ###########################
            
            background = datacube.background[currentx][currenty]
            
            if usedif2 == True: 
                dif2 = SpecMath.getdif2(specdata,energyaxis,1)
                for i in range(len(dif2)):
                    if dif2[i] < -1: dif2[i] = dif2[i]
                    elif dif2[i] > -1: dif2[i] = 0
            else: dif2 = np.zeros([specdata.shape[0]])

            ############################
            #  VERIFIES THE PEAK SIZE  #
            # EXPERIMENTAL FOR NRMLIZE #
            ############################
            
            if normalize == True:
                ymax = specdata.max()
                RAW_list = specdata.tolist()
                ymax_idx = RAW_list.index(ymax)
                LOCAL_MAX = [ymax, energyaxis[ymax_idx], ymax_idx,ymax_spec]
                FWHM = 2.3548 * SpecMath.sigma(LOCAL_MAX[1]*1000)
                current_peak_factor = (ymax-background[ymax_idx])*(2*FWHM)
                
                if current_peak_factor > max_peak_factor:
                    max_peak_factor = current_peak_factor
                    target = 0
                    while EnergyLib.Energies[target] <= LOCAL_MAX[1]:
                        ymax_element = EnergyLib.ElementList[target]
                        target+=1
                    ymax_index = EnergyLib.ElementList.index(ymax_element)
                    ymax_ka = KaElementsEnergy[ymax_index]
                    ymax_kb = KbElementsEnergy[ymax_index]
                    if debug == True: ymax_spec = currentspectra
                    
            #############################

            ###################################
            #  CALCULATE NET PEAKS AREAS AND  #
            #  ITERATE OVER LIST OF ELEMENTS  #
            ###################################
            
            logging.debug("current x = {0} / current y = {1}".format(currentx,currenty))
            if debug == True: logging.info("Specfile being processed is: {0}\n".format(spec))
 
            for Element in range(len(element_list)):
            
                if peakmethod == 'auto_roi' or peakmethod == 'PyMcaFit':
                   
                    ################################################################
                    #    Kx_INFO[0] IS THE NET AREA AND [1] IS THE PEAK INDEXES    #
                    # Be aware that PyMcaFit method peaks are returned always True #
                    # Check SpecMath.py This is due to the high noise in the data  #
                    ################################################################
                        
                    ka_info = SpecMath.getpeakarea(kaenergy[Element],specdata,\
                            energyaxis,background,configdict,RAW,usedif2,dif2)
                    ka = ka_info[0]
                
                    datacube.ROI[element_list[Element]][ka_info[1][0]:ka_info[1][1]] += \
                            specdata[ka_info[1][0]:ka_info[1][1]]

                    if ka == 0: 
                        ka,kb = 0, 0
                        elmap[currentx][currenty][0][Element] = 0
                    
                    elif ka > 0 and ratio == False: kb = 0
                    
                    elif ka > 0 and ratio == True:
                        kb_info = SpecMath.getpeakarea(kbenergy[Element],specdata,\
                                energyaxis,background,configdict,RAW,usedif2,dif2)
                        kb = kb_info[0]
                        
                        datacube.ROI[element_list[Element]][kb_info[1][0]:kb_info[1][1]] += \
                            specdata[kb_info[1][0]:kb_info[1][1]]

                        elmap[currentx][currenty][1][Element] = kb
                    
                    elmap[currentx][currenty][0][Element] = ka

                    if datacube.max_counts[element_list[Element]+"_a"] < ka:
                        datacube.max_counts[element_list[Element]+"_a"] = ka
                    if datacube.max_counts[element_list[Element]+"_b"] < kb:
                        datacube.max_counts[element_list[Element]+"_b"] = kb

                elif peakmethod == 'simple_roi':
                    
                    ################################################
                    # Calculates ka and kb with simple roi method  #
                    # simple_roi uses a conditional ratio to save  #
                    # time when kb is not detected in the stacksum #
                    # for the current element                      #
                    ################################################
                    
                    # KA AND KB ARE 0 BY DEFAULT
                    ka, kb = 0, 0
                    ka_ROI = RAW[ka_idx[Element][0]:ka_idx[Element][1]]
                    ka_bg = background[ka_idx[Element][0]:ka_idx[Element][1]]
                    
                    if conditional_ratio[Element] == True:
                        kb_ROI = RAW[kb_idx[Element][0]:kb_idx[Element][1]]
                        kb_bg = background[kb_idx[Element][0]:kb_idx[Element][1]]
               
                    # CALCULATES KA
                    if ka_idx[Element][3] == True:
                        datacube.ROI[element_list[Element]]\
                                [ka_idx[Element][0]:ka_idx[Element][1]] += ka_ROI
                        ka += ka_ROI.sum() - ka_bg.sum()
                   
                    # CALCULATES KB (MUST CHECK IF RATIO IS TRUE)
                    # IF RATIO IS FALSE, KB REMAINS AS 0
                    if conditional_ratio[Element] == True:
                        datacube.ROI[element_list[Element]]\
                                [kb_idx[Element][0]:kb_idx[Element][1]] += kb_ROI
                        kb += kb_ROI.sum() - kb_bg.sum()

                        elmap[currentx][currenty][1][Element] = kb

                    logging.debug("ka {0}, kb {1}".format(ka,kb))
                    elmap[currentx][currenty][0][Element] = ka
                    if datacube.max_counts[element_list[Element]+"_a"] < ka:
                        datacube.max_counts[element_list[Element]+"_a"] = ka
                    if datacube.max_counts[element_list[Element]+"_b"] < kb:
                        datacube.max_counts[element_list[Element]+"_b"] = kb
                
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
                            logging.info("File {0} has net peaks of {1} and {2} for element {3}\n"\
                                    .format(spec,ka,kb,element_list[Element]))
                        else:
                            if ka == 0: ka,kb,ka_kb = 0,0,0
                            elif kb == 0: ka_kb = 0
                            elif ka > 0 and kb > 0: ka_kb = ka/kb
                            r_file.write("%d\t%d\t%d\t%d\t%f\n" % (row, column, ka, kb, (ka_kb)))
                    except:
                        logging.warning("ka and kb not calculated for some unknown reason.\
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
        
        logging.info("Finished iteration process for element(s) {0}".format(element_list))
        
        
        timestamp = time.time() - partialtimer
        logging.info("Execution took %s seconds" % (timestamp))
        if peakmethod == 'PyMcaFit': logging.warning("Fit fail: {0}%".format(100*FITFAIL/dimension))
        
        timestamps = open(SpecRead.workpath + '/timestamps.txt'\
                    .format(Element,SpecRead.DIRECTORY),'a')
        timestamps.write("\n{5}\n{0} bgtrip={1} enhance={2} peakmethod={3}\t\n{6} elements\n{4} seconds\n"\
                    .format(Element,bgstrip,normalize,peakmethod,timestamp,\
                    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),element_list))
       
        logging.info("Finished map acquisition!")
    
    else:
        logging.warning("{0} not an element!".format(element_list))
        raise ValueError("{0} not an element!".format(element_list))
    
    if peakmethod == 'auto_roi': 
        elmap = ImgMath.interpolate_zeros(elmap)
    
    #print("Time:")
    #print(time.time()-timer)
    ImgMath.split_and_save(datacube,elmap,element_list)
    return elmap

def getdensitymap(datacube):
    
    timer = time.time()
    ##########-getdensitymap-############
    #   RETUNRS A 2D-ARRAY WITH TOTAL   #
    #   COUNTS PER PIXEL.               #
    #####################################

    #print("BG mode: {0}".format(datacube.config.get('bgstrip')))
    logging.info("Started acquisition of density map")
    
    density_map = np.zeros([datacube.dimension[0],datacube.dimension[1]])
    for x in range(datacube.dimension[0]):
        for y in range(datacube.dimension[1]):
            spec = datacube.matrix[x][y]
            background = datacube.background[x][y]    
            density_map[x][y] = sum(spec)-sum(background)
     
    logging.info("Finished fetching density map!")
    logging.info("Execution took %s seconds" % (time.time() - timer))
    return density_map

if __name__=="__main__":
    SpecRead.setup()
    cube_name = SpecRead.DIRECTORY
    cube_path = SpecRead.cube_path
    cube_file = open(cube_path,'rb')
    datacube = pickle.load(cube_file)
    cube_file.close() 
    print(cube_name)
    configdict = datacube.config
    myelements = ["Cu","Au","Fe","Pb"]
    myimage = getpeakmap(myelements,datacube)
   
