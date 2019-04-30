#################################################################
#                                                               #
#          ELEMENT MAP GENERATOR                                #
#                        version: a2.4                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
#################################################################

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

configdict = SpecRead.getconfig()

################-getpeakmap-#####################
#   GETPEAKMAP READS THE BATCH OF SPECTRA AND   #
#   RETURNS A 2D-ARRAY WITH THE COUNTS FOR THE  #
#   INPUT ELEMENT.                              #
#################################################

def getpeakmap(Element,ratio=configdict.get('ratio'),plot=None,\
        normalize=configdict.get('enhance'),svg=configdict.get('bgstrip'),\
        peakmethod=configdict.get('peakmethod')):
    
    if peakmethod == 'PyMcaFit': import SpecFitter
    KaElementsEnergy = EnergyLib.Energies
    KbElementsEnergy = EnergyLib.kbEnergies
    
    logging.info("Started energy axis calibration")
    energyaxis = SpecMath.energyaxis()
    logging.info("Finished energy axis calibration")
    current_peak_factor = 0
    max_peak_factor = 0
    ymax_spec = None

    if Element in Elements.ElementList:
        logging.info("Started acquisition of {0} map".format(Element))
        print("Fetching map image for %s..." % Element)
        
        partialtimer = time.time()
        kaindex = Elements.ElementList.index(Element)
        kaenergy = KaElementsEnergy[kaindex]*1000
        
        logging.warning("Energy {0:.0f} eV for element {1} being used as lookup!"\
                .format(kaenergy,Element))
        
        currentspectra = SpecRead.getfirstfile()
        elmap = np.zeros([imagex,imagey])
        scan = ([0,0])
        currentx = scan[0]
        currenty = scan[1]
        
        if ratio == True: 
            ratiofile = open(SpecRead.workpath + '/output/{1}_ratio_{0}.txt'\
                    .format(Element,SpecRead.DIRECTORY),'w+')
            ratiofile.write("-"*10 + " Counts of Element {0} "\
                    .format(Element) + 10*"-" + '\n')
            ratiofile.write("row\tcolumn\tline1\tline2\n")
            
            if svg != 'None': logging.warning("Background stripping is ON! - slow -")
            
            logging.warning("Ratio map will be generated!")
            kbindex = Elements.ElementList.index(Element)
            kbenergy = EnergyLib.kbEnergies[kbindex]*1000
            logging.warning("Energy {0:.0f} eV for element {1} being used as lookup!"\
                    .format(kbenergy,Element))

    #############################################
    #   STARTS ITERATION OVER SPECTRA BATCH     #
    #############################################

        logging.info("Starting iteration over spectra...\n")
        for ITERATION in range(dimension):
               
            spec = currentspectra
            RAW = SpecRead.getdata(spec)
            
            if peakmethod == 'PyMcaFit': 
                try:
                    specdata = SpecFitter.fit(spec)
                except:
                    print("\tCHANNEL COUNT METHOD USED FOR {0}!\t".format(spec))
                    logging.warning("\tFIT FAILED! USING CHANNEL COUNT METHOD!\t")
                    specdata = SpecRead.getdata(spec)
            elif peakmethod == 'Simple': specdata = SpecRead.getdata(spec)   
 
            if svg == 'SNIPBG': background = SpecMath.peakstrip(RAW,24,3)
            else: background = np.zeros([len(specdata)])
            
            ############################
            #  VERIFIES THE PEAK SIZE  #
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

            logging.info("current x = {0} / current y = {1}".format(currentx,currenty))
            logging.info("Specfile being processed is: {0}\n".format(spec))
 
#            plt.plot(SpecMath.energyaxis(),specdata)
#            plt.plot(SpecMath.energyaxis(),RAW)
#            plt.plot(SpecMath.energyaxis(),background)
#            plt.show()
                
            ka = SpecMath.getpeakarea(kaenergy,specdata,energyaxis,background,svg,RAW)
               
            if ka == 0: kb = 0
            elif ka > 0:
                kb = SpecMath.getpeakarea(kbenergy,specdata,energyaxis,background,svg,RAW)
            
            if ka > 0 and kb > 0: elmap[currentx][currenty] = ka+kb
                
            else:
                elmap[currentx][currenty] = 0
                ka, kb = 0, 0
            
            row = scan[0]
            column = scan[1]
            if ratio == True: 
                ratiofile.write("%d\t%d\t%d\t%d\t%s\n" % (row, column, ka, kb, spec))
                logging.info("File {0} has net peaks of {1} and {2} for element {3}\n"\
                         .format(spec,ka,kb,Element))
    
        #########################################
        #   UPDATE ELMAP POSITION AND SPECTRA   #
        #########################################        

            scan = ImgMath.updateposition(scan[0],scan[1])
            currentx = scan[0]
            currenty = scan[1]
            currentspectra = SpecRead.updatespectra(spec,dimension)
            print("{0:.2f}".format(ITERATION/dimension*100), "Percent complete  \r", end='')
            sys.stdout.flush()
        
    #################################    
    #   FINISHED ITERATION PROCESS  #
    #################################
        
        if ratio == True: ratiofile.close()
        logging.info("Finished iteration process for element {}\n".format(Element))
     
        try: image = elmap/elmap.max()*255
        except: 
            image = elmap+1
            logging.warning("ValueError, elmap.max() = {0}!".format(elmap.max()))
        timestamp = time.time() - partialtimer
        print("Execution took %s seconds" % (timestamp))
        
        timestamps = open(SpecRead.workpath + '/timestamps.txt'\
                    .format(Element,SpecRead.DIRECTORY),'a')
        timestamps.write("\n{5}\n{0} bgtrip={1} enhance={2} peakmethod={3}\t\n{4} seconds\n"\
                    .format(Element,configdict.get('bgstrip'),configdict.get('enhance'),\
                    configdict.get('peakmethod'),timestamp,\
                    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())))

        ##################################
        #  COLORIZING STEP IS DONE HERE  #
        ##################################
        
        color_image = ImgMath.colorize(image,'green')
        
        #################################

        figure = plt.imshow(color_image) 
        plt.savefig(SpecRead.workpath+'\output'+\
                '\{0}_bgtrip={1}_ratio={2}_enhance={3}_peakmethod={4}.png'\
                .format(Element,configdict.get('bgstrip'),configdict.get('ratio')\
                ,configdict.get('enhance'),configdict.get('peakmethod')),\
                dpi=150,transparent=False) 
        
        partialtimer = time.time()
        plt.clf()
        plt.close()
    logging.info("Finished map acquisition!")
    
    return image

##########-getdensitymap-############
#   RETUNRS A 2D-ARRAY WITH TOTAL   #
#   COUNTS PER PIXEL.               #
#####################################

def getdensitymap():
    currentspectra = SpecRead.getfirstfile()
    density_map = np.zeros([imagex,imagey])
    scan=([0,0])
    currentx=scan[0]
    currenty=scan[1]
    
    logging.info("Started acquisition of density map")
    for ITERATION in range(dimension):
        spec = currentspectra

        netcounts = SpecRead.getsum(spec)
        density_map[currentx][currenty] = netcounts
        scan = ImgMath.updateposition(scan[0],scan[1])
        currentx=scan[0]
        currenty=scan[1]
        currentspectra = SpecRead.updatespectra(spec,dimension)
    logging.info("Finished fetching density map!")
    
    print("Execution took %s seconds" % (time.time() - timer))
    return density_map

def stackimages(*args):
    import cv2
    imagelist = args
    colorlist = ['red','green','blue']
    color = 0
    stackedimage = ImgMath.colorize(np.zeros([imagex,imagey]),'none')
    for image in imagelist:
        color += 1
        image = ImgMath.colorize(image,colorlist[color])
        stackedimage = cv2.addWeighted(stackedimage,1,image,1,0)
    return stackedimage

