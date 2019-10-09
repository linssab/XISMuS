#################################################################
#                                                               #
#          ELEMENT MAP GENERATOR                                #
#                        version: 0.0.1α                        #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
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

timer = time.time()

#################################################
#   EXTRACT IMAGE DIMENSIONS FROM CONFIG.CFG    #
#################################################

def getpeakmap(element_list,datacube):
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
    save_energy_axis = open(SpecRead.workpath + '/' + 'axis.txt','a')
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
        #print("Fetching map image for " + ", ".join(element_list) + "...")
        
        ####### this is for debug mode #######
        currentspectra = SpecRead.getfirstfile()
        debug = False 
        ####### to register the NAME of the file #######

        ##############################
        # INITIALIZE OTHER VARIABLES #
        ##############################
        
        FITFAIL = 0
        partialtimer = time.time()
        elmap = np.zeros([imagex,imagey,len(element_list)])
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
        if peakmethod == 'simple_roi':
            ka_idx = SpecMath.setROI(kaenergy[0],energyaxis,stacksum,configdict)
            ka_peakdata = stacksum[ka_idx[0]:ka_idx[1]]
            if ratio == True:
                kb_idx = SpecMath.setROI(kbenergy[0],energyaxis,stacksum,configdict)
                kb_peakdata = stacksum[kb_idx[0]:kb_idx[1]]
                #print(ka_idx,kb_idx)
                if kb_idx[3] == False and ka_idx[3] == False:
                    logging.info("No alpha nor beta lines found. Aborting...")
                    sys.exit()
                elif kb_idx[3] == False: 
                    logging.warning("No beta line detected. Continuing with alpha only.")
                    ratio = False
            else:
                #print(ka_idx)
                pass
    
        #############################################
        #   STARTS ITERATION OVER SPECTRA BATCH     #
        #############################################
            
        logging.info("Starting iteration over spectra...\n")
        
        # starts the loading bar
        
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
            
            logging.info("current x = {0} / current y = {1}".format(currentx,currenty))
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
                
                    for channel in range(len(specdata)):
                        if energyaxis[ka_info[1][0]] < energyaxis[channel]\
                            < energyaxis[ka_info[1][1]]:
                            
                            datacube.ROI[element_list[Element]][channel] += specdata[channel]
                            #CUMSUM[Element][channel] += specdata[channel]
                            #CUMSUM_RAW[Element][channel] += RAW[channel]

                    if ka == 0: 
                        ka,kb = 0, 0
                        elmap[currentx][currenty][Element] = 0
                    
                    elif ka > 0 and ratio == False: kb = 0
                    
                    elif ka > 0 and ratio == True:
                        kb_info = SpecMath.getpeakarea(kbenergy[Element],specdata,\
                                energyaxis,background,configdict,RAW,usedif2,dif2)
                        kb = kb_info[0]

                        for channel in range(len(specdata)):
                            if energyaxis[kb_info[1][0]] < energyaxis[channel]\
                                < energyaxis[kb_info[1][1]]:
                                
                                datacube.ROI[element_list[Element]][channel] += specdata[channel]    
                                #CUMSUM[Element][channel] += specdata[channel]
                                #CUMSUM_RAW[Element][channel] += RAW[channel]
                    
                    elmap[currentx][currenty][Element] = ka+kb
                
                elif peakmethod == 'simple_roi':
                    if len(element_list) > 1: 
                        #print("{0}".format(element_list))
                        #print("Too many elements! simple_roi works with only one element!")
                        raise ValueError("Too many element inputs for method simple_roi")
                        break

                    ###############################################
                    # Calculates ka and kb with simple roi method #
                    ###############################################
                    
                    # KA AND KB ARE 0 BY DEFAULT
                    ka, kb = 0, 0
                    ka_ROI = RAW[ka_idx[0]:ka_idx[1]]
                    ka_bg = background[ka_idx[0]:ka_idx[1]]
                    
                    if ratio == True:
                        kb_ROI = RAW[kb_idx[0]:kb_idx[1]]
                        kb_bg = background[kb_idx[0]:kb_idx[1]]
               
                    # CALCULATES KA
                    if ka_idx[3] == True:
                        for channel in range(len(ka_ROI)):
                            #CUMSUM_RAW[Element][channel+ka_idx[0]] += RAW[channel+ka_idx[0]]
                            ka += ka_ROI[channel] - ka_bg[channel]
                   
                    # CALCULATES KB (MUST CHECK IF RATIO IS TRUE)
                    # IF RATIO IS FALSE, KB REMAINS AS 0
                    if ratio == True:
                        if kb_idx[3] == True and ka_idx[3] == True:
                            for channel in range(len(kb_ROI)):
                                #CUMSUM_RAW[Element][channel+kb_idx[0]] += RAW[channel+kb_idx[0]]
                                kb += kb_ROI[channel] - kb_bg[channel]
                    
                    logging.debug("ka {0}, kb {1}".format(ka,kb))
                    elmap[currentx][currenty][Element] = ka+kb
                
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

            scan = SpecMath.updateposition(scan[0],scan[1])
            currentx = scan[0]
            currenty = scan[1]
            if debug == True: currentspectra = SpecRead.updatespectra(spec,dimension)
            
            progress = int(ITERATION/dimension*20)
            blank = 20 - progress - 1
            print("[" + progress*"#" + blank*" " + "]" + " / {0:.2f}"\
                    .format(ITERATION/dimension*100), "Percent complete  \r", end='')
            sys.stdout.flush()
        
        ################################    
        #  FINISHED ITERATION PROCESS  #
        #  OVER THE BATCH OF SPECTRA   #
        ################################
        
        logging.info("Finished iteration process for element(s) {0}\n".format(element_list))
        
        
        timestamp = time.time() - partialtimer
        logging.info("\nExecution took %s seconds" % (timestamp))
        if peakmethod == 'PyMcaFit': logging.warning("Fit fail: {0}%".format(100*FITFAIL/dimension))
        
        timestamps = open(SpecRead.workpath + '/timestamps.txt'\
                    .format(Element,SpecRead.DIRECTORY),'a')
        timestamps.write("\n{5}\n{0} bgtrip={1} enhance={2} peakmethod={3}\t\n{6} elements\n{4} seconds\n"\
                    .format(Element,bgstrip,normalize,peakmethod,timestamp,\
                    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),element_list))
       
        #for element in element_list:
        #    plt.plot(energyaxis,datacube.ROI[element],label=element)
        #plt.plot(energyaxis,datacube.sum)
        #plt.legend()
        #plt.show()
                  
        logging.info("Finished map acquisition!")
    
    else:
        logging.warning("{0} not an element!".format(element_list))
        raise ValueError("{0} not an element!".format(element_list))
    
    if peakmethod == 'auto_roi': 
        elmap = ImgMath.interpolate_zeros(elmap)
    
    # split_and_save is disabled for use with GUI. MainGUI.find_elements() calls 
    # it at the end of the execution
    
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

"""
if __name__=="__main__":
    print("Test silver map")
    configdict['peakmethod'] = 'auto_roi'
    configdict['bgstrip'] = 'SNIPBG'
    print(configdict)
    myelements = ['Ag', 'Pb', 'Ca', 'Fe', 'Cu']
    myimage = getpeakmap(myelements,\
            bgstrip=configdict['bgstrip'],peakmethod=configdict['peakmethod'])
    ImgMath.split_and_save(myimage,myelements,configdict)
"""
