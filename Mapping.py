#################################################################
#                                                               #
#          XRF MAP GENERATOR                                    #
#                        version: a2.01                         #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
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
import cv2

timer = time.time()

imagsize = SpecRead.getdimension()
imagex = imagsize[0]
imagey = imagsize[1]
dimension = imagex*imagey

configdict = SpecRead.getconfig()

def plotdensitymap():
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
    density_map = density_map.astype(np.float32)/density_map.max()
    density_map = 255*density_map
    image = colorize(density_map,'gray')
    plt.imshow(image, cmap='gray')
    plt.show()
    return image


def getpeaks(elementlist,ratio=configdict.get('ratio'),plot=None,\
	normalixe=configdict.get('enhance'),bgstrip=configdict.get('bgstrip')):
	
    partialtimer = time.time()
    LocalElementList = elementlist
    currentspectra = SpecRead.getfirstfile()
    energyaxis = SpecMath.energyaxis()
    scan = ([0,0])
    currentx = scan[0]
    currenty = scan[1]
    KaElementsEnergy = EnergyLib.Energies
    KbElementsEnergy = EnergyLib.kbEnergies
 
    for Element in LocalElementList: 
        if ratio == True: 
            ratiofile = open('ratio_{0}.txt'.format(Element),'w+')
            ratiofile.write("-"*10 + " Counts of Element {0} ".format(Element) + 10*"-" + '\n')
            ratiofile.write("row\tcolumn\tline1\tline2\n")
            logging.warning("Ratio map will be generated for element {0}!".format(Element))
            ratiofile.close()
        else:
            kafile = open('counts_{0}.txt'.format(Element),'w+')
            kafile.write("-"*10 + " Counts of Element {0} ".format(Element) + 10*"-" + '\n')
            kafile.write("row\tcolumn\tcounts\n")
            kafile.close()
          
    logging.info("Starting iteration over spectra...\n")
    for ITERATION in range(dimension):
        spec = currentspectra
        specdata = SpecRead.getdata(spec)
        if bgstrip == 'SNIPBG': background = SpecMath.peakstrip(specdata,24,3)
        else: background = np.zeros([len(specdata)])
        logging.info("Specfile being processed is: {0}\n".format(spec))
            
        for Element in LocalElementList:
            kaindex = Elements.ElementList.index(Element)
            kaenergy = KaElementsEnergy[kaindex]*1000
            ka = SpecMath.getpeakarea(kaenergy,specdata,energyaxis,background,bgstrip)
            if ratio == True:
                localratiofile = open('ratio_{0}.txt'.format(Element),'w')
                kbindex = Elements.ElementList.index(Element)
                kbenergy = EnergyLib.kbEnergies[kbindex]*1000
                kb = SpecMath.getpeakarea(kbenergy,specdata,energyaxis,background,bgstrip)
                row = scan[0]
                column = scan[1]
                localratiofile.write("%d\t%d\t%d\t%d\t%s\n" % (row, column, ka, kb, spec))
                localratiofile.close()
            else:
                localkafile = open('counts_{0}.txt'.format(Element),'w')
                row = scan[0]
                column = scan[1]
                localkafile.write("%d\t%d\t%d\t%s\n" % (row, column, ka, spec))
                localkafile.close()

        scan = ImgMath.updateposition(scan[0],scan[1])
        currentx = scan[0]
        currenty = scan[1]
        currentspectra = SpecRead.updatespectra(spec,dimension)
           
    if ratio == True: ratiofile.close()
    else: kafile.close()
    return 0

def plotpeakmap(args,ratio=configdict.get('ratio'),plot=None,\
        normalize=configdict.get('enhance'),svg=configdict.get('bgstrip')):
    
    partialtimer = time.time()
    LocalElementList = args
    print(LocalElementList)
    colorcode = ['red','green','blue','yellow','purple','pink']
    KaElementsEnergy = EnergyLib.Energies
    KbElementsEnergy = EnergyLib.kbEnergies
    logging.info("Started energy axis calibration")
    energyaxis = SpecMath.energyaxis()
    logging.info("Finished energy axis calibration")
    stackimage = ImgMath.colorize(np.zeros([imagex,imagey]),'none')

    if normalize == True: 
        norm_timer = time.time()
        logging.warning("Searching for largest peak area in batch! - slow -")
        norm = ImgMath.normalize_fnc(energyaxis)
        logging.info("Process took: {0}s\n".format(time.time()-norm_timer))

    for argument in range(len(LocalElementList)):
        Element = LocalElementList[argument]
        
        #    STARTS IMAGE ACQUISITION FOR ELEMENT 'Element'    #
        
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
                ratiofile = open('ratio_{0}.txt'.format(Element),'w+')
                ratiofile.write("-"*10 + " Counts of Element {0} "\
                        .format(Element) + 10*"-" + '\n')
                ratiofile.write("row\tcolumn\tline1\tline2\n")
                if svg != 'None': logging.warning("Background stripping is ON! - slow -")
                logging.warning("Ratio map will be generated!")
                kbindex = Elements.ElementList.index(Element)
                kbenergy = EnergyLib.kbEnergies[kbindex]*1000
                logging.warning("Energy {0:.0f} eV for element {1} being used as lookup!"\
                        .format(kbenergy,Element))

            logging.info("Starting iteration over spectra...\n")
            for ITERATION in range(dimension):
                spec = currentspectra
                specdata = SpecRead.getdata(spec)
                if svg == 'SNIPBG': background = SpecMath.peakstrip(specdata,24,3)
                else: background = np.zeros([len(specdata)])
                logging.info("Specfile being processed is: {0}\n".format(spec))
                netpeak = SpecMath.getpeakarea(kaenergy,specdata,energyaxis,background,svg)
                elmap[currentx][currenty] = netpeak
               
                if ratio == True:
                    ka = netpeak
                    if ka == 0: kb = 0
                    elif ka > 0:
                        kb = SpecMath.getpeakarea(kbenergy,specdata,energyaxis,background,svg)
                    logging.info("Kb is larger than Ka for element {0}".format(Element))
                    row = scan[0]
                    column = scan[1]
                    ratiofile.write("%d\t%d\t%d\t%d\t%s\n" % (row, column, ka, kb, spec))
                    logging.info("File {0} has net peaks of {1} and {2} for element {3}\n"\
                             .format(spec,ka,kb,Element))
                                    
                scan = ImgMath.updateposition(scan[0],scan[1])
                currentx = scan[0]
                currenty = scan[1]
                currentspectra = SpecRead.updatespectra(spec,dimension)
            
            logging.info("Finished iteration process for element {}\n".format(Element))
            
            if ratio == True: ratiofile.close()
            
            if normalize == True:
                logging.info("Normalizing image...")
                logging.warning("Maximum detected area is: {0}".format(norm))
                print("NORM AREA = {0}".format(norm))
                logging.warning("{0} maximum detected area is: {1}".format(Element,elmap.max()))
                print("{0} MAX AREA = {1}".format(Element,elmap.max()))
                image = elmap/norm*255

            elif normalize == False: 
                try:
                    image = elmap/elmap.max()*255
                except ValueError: 
                    logging.warning("Element {0} not present!".format(Element))
                    pass
            logging.info("Started coloring step")
            image = ImgMath.colorize(image,colorcode[argument])
            stackimage = cv2.addWeighted(image, 1, stackimage, 1, 0)
            logging.info("Finished coloring step")
            print("Execution took %s seconds" % (time.time() - partialtimer))
            partialtimer = time.time()
    
    logging.info("Finished map acquisition!")
    
    if plot == True: 
        if normalize == True: 
            hist,bins = np.histogram(stackimage.flatten(),256,[0,256])
            cdf = hist.cumsum()
            cdf_norm = cdf * hist.max()/cdf.max()
            cdf_mask = np.ma.masked_equal(cdf,0)
            cdf_mask = (cdf_mask - cdf_mask.min())*255/(cdf_mask.max()-cdf_mask.min())
            cdf = np.ma.filled(cdf_mask,0).astype('uint8')
            stackimage = cdf[stackimage]
        plt.imshow(stackimage)
        plt.savefig(SpecRead.workpath+'\output'+'\{0}_bgtrip={1}_ratio={2}_enhance={3}.png'\
                .format(LocalElementList,configdict.get('bgstrip'),configdict.get('ratio'),\
                configdict.get('enhance')),dpi=150,transparent=True) 
        plt.show()
    return stackimage

if __name__=="__main__":
    inputlist = ['-findelement','Mapping.py','-normalize','-getratios'] 
    elementlist = []
    flag1 = sys.argv[1]
    if flag1 == '-help':
        print("\nUSAGE: '-findelement x y'; plots a 2D map of elements 'x' and/or 'y'\
additionally, you can type '-normalize' when finding one element to generate\
an image where the element is displeyd in proportion to the most abundant element.\n\
       '-plotmap'; plots a density map\n\
       '-plotstack'; plots the sum spectra of all sample. Optional: you can add '-semilog' to plot it in semilog mode.\n\
       '-getratios x'; creates the ka/kb or la/lb ratio image for element 'x'. K or L are chosen accordingly.")
    if flag1 == '-findelement':    
        for arg in range(len(sys.argv)):
            if sys.argv[arg] in Elements.ElementList:
                elementlist.append(sys.argv[arg])
            else: 
                if sys.argv[arg] in inputlist:
                    pass
                else: 
                    raise Exception("%s not an element!" % sys.argv[arg])
                    logging.exception("{0} is not a chemical element!".format(sys.argv[arg]))
            if '-normalize' in sys.argv:
                pass
        if '-normalize' in sys.argv:
            plotpeakmap(elementlist,plot=True,normalize=True)
        else:
            plotpeakmap(elementlist,plot=True)
        logging.exception("No element input!")
    
    if flag1 == '-plotmap':
        print("Fetching density map...")
        plotdensitymap()
    if flag1 == '-plotstack':
        if len(sys.argv) >= 3:
            flag2 = sys.argv[2]
        else:
            flag2 = None
        SpecMath.getstackplot(SpecRead.getfirstfile(),SpecMath.energyaxis())
    if flag1 == '-getratios':
        for arg in range(len(sys.argv)):
            if sys.argv[arg] in Elements.ElementList:
                elementlist.append(sys.argv[arg])
            else: 
                if sys.argv[arg] in inputlist:
                    pass
                else: 
                    raise Exception("%s not an element!" % sys.argv[arg])
        ratiofile = 'ratio_{0}.txt'.format(elementlist[0])
        ratiomatrix = SpecRead.RatioMatrixReadFile(ratiofile)
        ratiomatrix = SpecRead.RatioMatrixTransform(ratiomatrix)
        plt.imshow(ratiomatrix,cmap='gray')
        plt.show()
