#################################################################
#                                                               #
#          ELEMENT MAP GENERATOR                                #
#                        version: a2.20                         #
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
import SpecFitter
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
    
    print(Element)

    partialtimer = time.time()
    KaElementsEnergy = EnergyLib.Energies
    KbElementsEnergy = EnergyLib.kbEnergies
    
    logging.info("Started energy axis calibration")
    energyaxis = SpecMath.energyaxis()
    logging.info("Finished energy axis calibration")
    
    if Element in Elements.ElementList:
        logging.info("Started acquisition of {0} map".format(Element))
        print("Fetching map image for %s..." % Element)
        
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
            ratiofile = open(SpecRead.workpath + '/output/ratio_{0}.txt'.format(Element),'w+')
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
                    print("\tCHANNEL COUNT\t")
                    logging.warning("\tFIT FAILED! USING CHANNEL COUNT METHOD!\t")
                    specdata = SpecRead.getdata(spec)
            elif peakmethod == 'Simple': specdata = SpecRead.getdata(spec)   
 
            if svg == 'SNIPBG': background = SpecMath.peakstrip(RAW,24,5)
            else: background = np.zeros([len(specdata)])
            
            logging.info("current x = {0} / current y = {1}".format(currentx,currenty))
            logging.info("Specfile being processed is: {0}\n".format(spec))
 
#            plt.semilogy(SpecMath.energyaxis(),specdata)
#            plt.semilogy(SpecMath.energyaxis(),RAW)
#            plt.semilogy(SpecMath.energyaxis(),background)
#            plt.show()
                
            netpeak = SpecMath.getpeakarea(kaenergy,specdata,energyaxis,background,svg,RAW)
            elmap[currentx][currenty] = netpeak
               
            if ratio == True:
                ka = netpeak
                if ka == 0: kb = 0
                elif ka > 0:
                    kb = SpecMath.getpeakarea(kbenergy,specdata,energyaxis,background,svg,RAW)
                row = scan[0]
                column = scan[1]
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
        
        logging.info("Finished iteration process for element {}\n".format(Element))
            
        if ratio == True: ratiofile.close()
           
        if normalize == False: 
            try:
                image = elmap/elmap.max()*255
            except ValueError: 
                logging.warning("Element {0} not present! elmap.max() = {1}!"\
                        .format(Element,elmap.max()))
                pass
        
#        fig = plt.figure()
        figure = plt.imshow(image)   
        plt.savefig(SpecRead.workpath+'\output'+'\{0}_bgtrip={1}_ratio={2}_enhance={3}.png'\
            .format(Element,configdict.get('bgstrip'),\
            configdict.get('ratio'),configdict.get('enhance')),dpi=150,transparent=False) 
        plt.clf()        
        print("Execution took %s seconds" % (time.time() - partialtimer))
        partialtimer = time.time()
    
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

