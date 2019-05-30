#################################################################
#                                                               #
#          ELEMENT MAP GENERATOR                                #
#                        version: a3.20                         #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
#################################################################

import cv2
import sys
import numpy as np
import logging
import SpecMath
import SpecRead
import EnergyLib
import ImgMath
from PyMca5.PyMcaPhysics import Elements
import matplotlib.pyplot as plt
import time

timer = time.time()

#################################################
#   EXTRACT IMAGE DIMENSIONS FROM CONFIG.CFG    #
#   AND SETS UP THE CONFIG DICTIONARY           #
#################################################

imagsize = SpecRead.getdimension()
imagex = imagsize[0]
imagey = imagsize[1]
dimension = imagex*imagey

configdict = SpecRead.CONFIG

def getpeakmap(element_list,ratio=configdict.get('ratio'),\
        normalize=configdict.get('enhance'),bgstrip=configdict.get('bgstrip'),\
        peakmethod=configdict.get('peakmethod')):

    ################-getpeakmap-#####################
    #   GETPEAKMAP READS THE BATCH OF SPECTRA AND   #
    #   RETURNS A 2D-ARRAY WITH THE COUNTS FOR THE  #
    #   KA AND KB LINES OF INPUT ELEMENT(S).        #
    #################################################

    if peakmethod == 'PyMcaFit': import SpecFitter
    KaElementsEnergy = EnergyLib.Energies
    KbElementsEnergy = EnergyLib.kbEnergies
    
    logging.info("Started energy axis calibration")
    energyaxis = SpecMath.energyaxis()
    logging.info("Finished energy axis calibration")
    current_peak_factor = 0
    max_peak_factor = 0
    ymax_spec = None
    usedif2 = True
    ratiofiles = ['' for x in range(len(element_list))]

    #########################################
    # ERROR VARIABLES CUMSUM AND CUMSUM_RAW #
    #########################################
    
    CUMSUM = np.zeros([len(energyaxis)])
    CUMSUM_RAW = np.zeros([len(energyaxis)])
    BGSUM = np.zeros([len(energyaxis)])

    #########################################

    if element_list[0] in Elements.ElementList:
        logging.info("Started acquisition of {0} map(s)".format(element_list))
        print("Fetching map image for " + ", ".join(element_list) + "...")
        
        if bgstrip != 'None': logging.warning("Background stripping is ON! - slow -")
        
        partialtimer = time.time()
        currentspectra = SpecRead.getfirstfile()
        elmap = np.zeros([imagex,imagey,len(element_list)])
        scan = ([0,0])
        currentx = scan[0]
        currenty = scan[1]
        kaindex,kbindex,kaenergy,kbenergy = \
                (np.zeros(len(element_list),dtype='int') for i in range(4))
         
        for Element in range(len(element_list)):

            # sets ka energy
            kaindex[Element] = Elements.ElementList.index(element_list[Element])
            kaenergy[Element] = KaElementsEnergy[kaindex[Element]]*1000
        
            logging.warning("Energy {0:.0f} eV for element {1} being used as lookup!"\
                .format(kaenergy[Element],element_list[Element]))
        
            if ratio == True:
                ratiofiles[Element] = str(SpecRead.workpath + '/output/'+\
                        '{1}_ratio_{0}.txt'.format(element_list[Element],SpecRead.DIRECTORY))
                r_file = open(ratiofiles[Element],'w+')
                r_file.readline()
                r_file.truncate()
                r_file.write("-"*10 + " Counts of Element {0} "\
                        .format(element_list[Element]) + 10*"-" + '\n')
                r_file.write("row\tcolumn\tline1\tline2\n")

                # sets kb energy
                kbindex[Element] = Elements.ElementList.index(element_list[Element])
                kbenergy[Element] = EnergyLib.kbEnergies[kbindex[Element]]*1000
                r_file.close() 
                logging.warning("Energy {0:.0f} eV for element {1} being used as lookup!"\
                        .format(kbenergy[Element],element_list[Element]))
        
    ################################
    #  SETS SIMPLE ROI PARAMETERS  #
    ################################

        stacksum = SpecMath.stacksum(currentspectra,dimension)
        if peakmethod == 'simple_roi':
            ka_idx = SpecMath.setROI(kaenergy[0],energyaxis,stacksum,configdict)
            kb_idx = SpecMath.setROI(kbenergy[0],energyaxis,stacksum,configdict)
            print(ka_idx,kb_idx)
            ka_peakdata = stacksum[ka_idx[0]:ka_idx[1]]
            kb_peakdata = stacksum[kb_idx[0]:kb_idx[1]]
            
    #############################################
    #   STARTS ITERATION OVER SPECTRA BATCH     #
    #############################################
        
        FITFAIL = 0
        logging.info("Starting iteration over spectra...\n")
        for ITERATION in range(dimension):
               
            spec = currentspectra
            RAW = SpecRead.getdata(spec)
            
            #######################################
            #     ATTEMPT TO FIT THE SPECFILE     #
            # PYMCAFIT DOES NOT USE 2ND DIF CHECK #
            #######################################

            if peakmethod == 'PyMcaFit': 
                try:
                    usedif2 = False
                    specdata = SpecFitter.fit(spec)
                except:
                    FITFAIL += 1
                    usedif2 = True
                    print("\tCHANNEL COUNT METHOD USED FOR {0}!\t".format(spec))
                    logging.warning("\tFIT FAILED! USING CHANNEL COUNT METHOD FOR {0}!\t"\
                            .format(spec))
                    specdata = SpecRead.getdata(spec)
            elif peakmethod == 'simple_roi': specdata = SpecRead.getdata(spec)
            elif peakmethod == 'auto_roi': specdata = SpecRead.getdata(spec)
            else: 
                raise Exception("peakmethod {0} not recognized.".format(peakmethod))
 
            #########################
            #  SETS THE BACKGROUND  #
            #########################
            
            if bgstrip == 'SNIPBG': 
                background = SpecMath.peakstrip(RAW,24,3)
                logging.debug('SNIPGB calculated for spec {0}'.format(spec))
            else: background = np.zeros([len(specdata)])
            
            BGSUM += background
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
                    ymax_index = Elements.ElementList.index(ymax_element)
                    ymax_ka = KaElementsEnergy[ymax_index]
                    ymax_kb = KbElementsEnergy[ymax_index]
                    ymax_spec = currentspectra
                    
            #############################

            #####################################
            #  ACTUALLY RECORDS NET PEAKS AREA  #
            #   ITERATE OVER LIST OF ELEMENTS   #
            #####################################
            
            logging.info("current x = {0} / current y = {1}".format(currentx,currenty))
            logging.info("Specfile being processed is: {0}\n".format(spec))
 
            for Element in range(len(element_list)):
            
                if peakmethod == 'auto_roi' or peakmethod == 'PyMcaFit':
                   
                    ################################################################
                    #    Kx_INFO[0] IS THE NET AREA AND [1] IS THE PEAK INDEXES    #
                    # Be aware that PyMcaFit method peaks are returned always True #
                    # Check SpecMath.py This is due to the high noise in the data  #
                    ################################################################
                        
                    ka_info = SpecMath.getpeakarea(kaenergy[Element],specdata,\
                            energyaxis,background,configdict,RAW,usedif2)
                    ka = ka_info[0]
                
                    for channel in range(len(specdata)):
                        if energyaxis[ka_info[1][0]] < energyaxis[channel]\
                            < energyaxis[ka_info[1][1]]:
                            CUMSUM[channel] += specdata[channel]
                            CUMSUM_RAW[channel] += RAW[channel]

                    if ka == 0: kb = 0
                    elif ka > 0:
                        kb_info = SpecMath.getpeakarea(kbenergy[Element],specdata,\
                                energyaxis,background,configdict,RAW,usedif2)
                        kb = kb_info[0]

                        for channel in range(len(specdata)):
                            if energyaxis[kb_info[1][0]] < energyaxis[channel]\
                                < energyaxis[kb_info[1][1]]:
                                CUMSUM[channel] += specdata[channel]
                                CUMSUM_RAW[channel] += RAW[channel]
                
                    if ka > 0 and kb > 0: elmap[currentx][currenty][Element] = ka+kb
                    
                    else:
                        elmap[currentx][currenty][Element] = 0
                        ka, kb = 0, 0
                
                elif peakmethod == 'simple_roi':
                    if len(element_list) > 1: 
                        print("{0}".format(element_list))
                        print("Too many elements! simple_roi works with only one element!")
                        raise ValueError("Too many element inputs for method simple_roi")
                        break

                    ###############################################
                    # Calculates ka and kb with simple roi method #
                    ###############################################
                    
                    ka, kb = 0, 0
                    ka_ROI = RAW[ka_idx[0]:ka_idx[1]]
                    ka_bg = background[ka_idx[0]:ka_idx[1]]
                    kb_ROI = RAW[kb_idx[0]:kb_idx[1]]
                    kb_bg = background[kb_idx[0]:kb_idx[1]]
                
                    if ka_idx[3] == True:
                        for channel in range(len(ka_ROI)):
                            CUMSUM_RAW[channel+ka_idx[0]] += RAW[channel+ka_idx[0]]
                            ka += ka_ROI[channel] - ka_bg[channel]
                    if kb_idx[3] == True and ka_idx[3] == True:
                        for channel in range(len(kb_ROI)):
                            CUMSUM_RAW[channel+kb_idx[0]] += RAW[channel+kb_idx[0]]
                            kb += kb_ROI[channel] - kb_bg[channel]

               ###  if kb_idx[3] == False: ka, kb = 0, 0
                
                    logging.debug("ka {0}, kb {1}".format(ka,kb))
                    elmap[currentx][currenty][Element] = ka+kb
                
                row = scan[0]
                column = scan[1]

                if ratio == True: 
                    try: 
                        r_file = open(ratiofiles[Element],'a')
                        r_file.write("%d\t%d\t%d\t%d\t%s\n" % (row, column, ka, kb, spec))
                        logging.info("File {0} has net peaks of {1} and {2} for element {3}\n"\
                             .format(spec,ka,kb,element_list[Element]))
                    except:
                        print("ka and kb not calculated for some unknown reason.\
                                Check Config.cfg for the correct spelling of peakmethod option!")

            #####################################

            #########################################
            #   UPDATE ELMAP POSITION AND SPECTRA   #
            #########################################        

            scan = ImgMath.updateposition(scan[0],scan[1])
            currentx = scan[0]
            currenty = scan[1]
            currentspectra = SpecRead.updatespectra(spec,dimension)
            progress = int(ITERATION/dimension*20)
            blank = 20 - progress - 1
            print("[" + progress*"\u25A0" + blank*" " + "]" + " / {0:.2f}"\
                    .format(ITERATION/dimension*100), "Percent complete  \r", end='')
            sys.stdout.flush()
        
        ################################    
        #  FINISHED ITERATION PROCESS  #
        #  OVER THE BATCH OF SPECTRA   #
        ################################
        
        logging.info("Finished iteration process for element(s) {0}\n".format(element_list))
        
        
        timestamp = time.time() - partialtimer
        print("\nExecution took %s seconds" % (timestamp))
        if peakmethod == 'PyMcaFit': print("Fit fail: {0}%".format(100*FITFAIL/dimension))
        
        timestamps = open(SpecRead.workpath + '/timestamps.txt'\
                    .format(Element,SpecRead.DIRECTORY),'a')
        timestamps.write("\n{5}\n{0} bgtrip={1} enhance={2} peakmethod={3}\t\n{4} seconds\n"\
                    .format(Element,configdict.get('bgstrip'),configdict.get('enhance'),\
                    configdict.get('peakmethod'),timestamp,\
                    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))
        
        if peakmethod == 'PyMcaFit': plt.plot(energyaxis,CUMSUM,label='CUMSUM CURRENT DATA')
        plt.plot(energyaxis,CUMSUM_RAW,label='CUMSUM RAW DATA')
        plt.plot(energyaxis,stacksum,label='stackplot')
        plt.plot(energyaxis,BGSUM,label='background')
        plt.legend()
        plt.show()
                        
        logging.info("Finished map acquisition!")
    else:
        logging.warning("{0} not an element!".format(element_list))
        raise ValueError("{0} not an element!".format(element_list))
    
    ImgMath.split_and_save(elmap,element_list,configdict)
    return elmap

def getdensitymap():
    
    ##########-getdensitymap-############
    #   RETUNRS A 2D-ARRAY WITH TOTAL   #
    #   COUNTS PER PIXEL.               #
    #####################################

    currentspectra = SpecRead.getfirstfile()
    density_map = np.zeros([imagex,imagey])
    scan=([0,0])
    currentx=scan[0]
    currenty=scan[1]

    print("BG mode: {0}".format(configdict.get('bgstrip')))
    logging.info("Started acquisition of density map")
    for ITERATION in range(dimension):
        spec = currentspectra
 
        if configdict.get('bgstrip') == 'SNIPBG': 
            background = SpecMath.peakstrip(SpecRead.getdata(spec),24,3)
        else: 
            background = np.zeros([len(SpecRead.getdata(spec))])
        
        netcounts = SpecRead.getsum(spec)
        bgcounts = background.sum()
        density_map[currentx][currenty] = netcounts - bgcounts
        scan = ImgMath.updateposition(scan[0],scan[1])
        currentx=scan[0]
        currenty=scan[1]
        currentspectra = SpecRead.updatespectra(spec,dimension)
    logging.info("Finished fetching density map!")
    
    print("Execution took %s seconds" % (time.time() - timer))
    
    fig, ax = plt.subplots()
    mapimage = ax.imshow(density_map,cmap='jet',label='Dense Map')
    plt.savefig(SpecRead.workpath+'/output/'+SpecRead.DIRECTORY+'\{0}_{1}_densitymap.png'\
            .format(SpecRead.DIRECTORY,configdict.get('bgstrip')),dpi=150,transparent=False) 
    plt.show()
    return density_map


if __name__=="__main__":
    print("Test silver map")
    configdict['peakmethod'] = 'auto_roi'
    configdict['bgstrip'] = 'SNIPBG'
    print(configdict)
    myelements = ['Ag', 'Pb', 'Ca', 'Fe', 'Cu']
    myimage = getpeakmap(myelements,\
            bgstrip=configdict['bgstrip'],peakmethod=configdict['peakmethod'])
    ImgMath.split_and_save(myimage,myelements,configdict)
