#################################################################
#                                                               #
#          DENSITY MAP GENERATOR                                #
#                        version: a1.3                          #
# @author: Sergio Lins                                          #
#################################################################

import sys
import os
import numpy as np
from multiprocessing import Process
import SpecMath
import SpecRead
import EnergyLib
from PyMca5.PyMcaMath import SpecArithmetic as Arithmetic
from PyMca5.PyMcaPhysics import Elements
import matplotlib.pyplot as plt
import time
import math

timer=time.time()
# FOR NOW THE STARTING SPECTRA MUST BE GIVEN MANUALLY IN SpecRead.py FILE
start = SpecRead.input

imagsize = SpecRead.getdimension()
imagex = imagsize[0]
imagey = imagsize[1]
dimension = imagex*imagey

def updateposition(a,b):
    currentx=a
    currenty=b
    if currenty == imagey-1:
#        print("We reached the end of the line, y= %d" % currenty)
        currenty=0
#        print("Now we reset the column, y= %d" % currenty)
        currentx+=1
#        print("And last we move to the next line, x= %d" % currentx)
    else:
        currenty+=1
#        print("We are still in the middle of the line, y+1 = %d" % currenty)
#    if currentx == imagex-1 and currenty == imagey-1:
#        print("END OF IMAGE")
    actual=([currentx,currenty])
    return actual

def plotdensitymap():
    currentspectra = start
    density_map = np.zeros([imagex,imagey])
    scan=([0,0])
    currentx=scan[0]
    currenty=scan[1]

    for ITERATION in range(dimension):
        spec = currentspectra
#        print("Current X= %d\nCurrent Y= %d" % (currentx,currenty))
#        print("Current spectra is: %s" % spec)
        sum = SpecRead.getsum(spec)
        density_map[currentx][currenty]=sum          #_update matrix
        scan=updateposition(scan[0],scan[1])
        currentx=scan[0]
        currenty=scan[1]
        currentspectra = SpecRead.updatespectra(spec,dimension)
    print("Execution took %s seconds" % (time.time() - timer))
    density_map = density_map.astype(np.float64)/density_map.max()
    density_map = 255*density_map
    image = density_map.astype(np.uint8)
    plt.imshow(density_map, cmap='gray')
    plt.show()
    return image

def plotpeakmap(*args):
    partialtimer = time.time()
    LocalElementList = args
    colorcode=['green','blue','red']
    eleenergy = EnergyLib.Energies
    stackimage = colorize(np.zeros([imagex,imagey]))
    for input in range(len(LocalElementList)):
        Element = LocalElementList[input]
        
        # STARTS IMAGE ACQUISITION FOR ELEMENT 'Element'
        
        if Element in Elements.ElementList:
            print("Fetching map image for %s..." % Element)
            pos = Elements.ElementList.index(Element) 
            element = eleenergy[pos]*1000
            currentspectra = start
            energyaxis = SpecRead.calibrate(currentspectra,'data')
            elmap = np.zeros([imagex,imagey])
            scan=([0,0])
            currentx=scan[0]
            currenty=scan[1]
        
            for ITERATION in range(dimension):
                spec = currentspectra
#               print("Current X= %d\nCurrent Y= %d" % (currentx,currenty))
#               print("Current spectra is: %s" % spec)
                sum = SpecMath.getpeakarea(spec,element,energyaxis)
                elmap[currentx][currenty] = sum
                scan = updateposition(scan[0],scan[1])
                currentx = scan[0]
                currenty = scan[1]
                currentspectra = SpecRead.updatespectra(spec,dimension)
            image = elmap/elmap.max()*255
            tintimage = colorize(image,colorcode[input])
            stackimage = tintimage + stackimage
        print("Execution took %s seconds" % (time.time() - partialtimer))
        partialtimer = time.time()
    plt.imshow(stackimage)
    cax = plt.axes([0,255,1,10])
    plt.colorbar(cax=cax)
    plt.show()
    return stackimage

def colorize(elementmap,color=None):
    R = np.zeros([imagex,imagey])
    G = np.zeros([imagex,imagey])
    B = np.zeros([imagex,imagey])
    elmap = elementmap
    pixel = []
    myimage = [[]]*(imagex-1)
    if color == 'blue':
        B=elementmap
    elif color == 'red':
        R=elementmap
    elif color == 'green':
        G=elementmap
    for line in range(imagex-1):    
        for i in range(imagey-1):
            pixel.append(np.array([R[line][i],G[line][i],B[line][i],255],dtype='float32'))
            myimage[line]=np.asarray(pixel,dtype='uint8')
        pixel = []
    image = np.asarray(myimage)
    return image

if __name__=="__main__":
    flag1 = sys.argv[1]
    if flag1 == '-help':
        print("USAGE: '-findelement x'; plots a 2D map of the element 'x'\n\
       '-plotmap'; plots a density map\n\
       '-plotstack'; plots the sum spectra of all sample. Optional: you can add '-semilog' to plot it in semilog mode.")
    if flag1 == '-findelement':    
        if len(sys.argv) > 4: raise Exception("More than 2 elements were selected! Try again with 2 or less inputs!")
        if len(sys.argv) > 2:
            element1 = None
            element2 = None
            if sys.argv[2] in Elements.ElementList:
                element1 = sys.argv[2]
            else: raise Exception("%s not an element!" % sys.argv[2])
            if len(sys.argv) > 3:
                if sys.argv[3] in Elements.ElementList:
                    element2 = sys.argv[3]
                else: raise Exception("%s not an element!" % sys.argv[3])
            plotpeakmap(element1,element2)
        else: raise Exception("No element input!")
    if flag1 == '-plotmap':
        print("Fetching density map...")
        plotdensitymap()
    if flag1 == '-plotstack':
        SpecRead.getstackplot(start,flag2)
