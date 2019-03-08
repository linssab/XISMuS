#################################################################
#                                                               #
#          DENSITY MAP GENERATOR                                #
#                        version: a1.2                          #
# @author: Sergio Lins                                          #
#################################################################

import sys
import os
import numpy as np
from multiprocessing import Process
import SpecMath
import SpecRead
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

def plotpeakmap(element):
    currentspectra = start
    elmap = np.zeros([imagex,imagey])
    scan=([0,0])
    currentx=scan[0]
    currenty=scan[1]
    energyaxis = SpecRead.calibrate(currentspectra,'data')

    for ITERATION in range(dimension):
        spec = currentspectra
#        print("Current X= %d\nCurrent Y= %d" % (currentx,currenty))
#        print("Current spectra is: %s" % spec)
        sum = SpecMath.getpeakarea(spec,element,energyaxis)
#        print("Sum is: %.f" % sum)
        elmap[currentx][currenty]=sum          #_update matrix
        scan=updateposition(scan[0],scan[1])
        currentx=scan[0]
        currenty=scan[1]
        currentspectra = SpecRead.updatespectra(spec,dimension)
        if isinstance(timer,int): print("Partial! %s seconds!" % (time.time() - timer))    
    print("Execution took %s seconds" % (time.time() - timer))    
    
    elmap = elmap.astype(np.float64)/elmap.max()
    elmap = 255*elmap
    image = elmap.astype(np.uint8)
    plt.imshow(image)
    plt.show()
    return image

if __name__=="__main__":
    flag1 = sys.argv[1]
    flag2 = None
    print(sys.argv)
    if len(sys.argv) > 2: flag2 = sys.argv[2]
    elements = Elements.ElementList
    elements = ['Au','Ag','Cu','S','Fe']
    energies = [9710,22500,8400,2200,6410]
    if flag1 == '-help':
        print("USAGE: '-findelement x'; plots a 2D map of the element 'x'\n\
       '-plotmap'; plots a density map\n\
       '-plotstack'; plots the sum spectra of all sample Optional: you can add '-semilog' to plot it in semilog mode.")
    if flag1 == '-findelement' and flag2 in elements:
        index = elements.index(flag2)
        element = energies[index]
        print("Fetching map image for %s" % flag2)
        plotpeakmap(element)
    if flag1 == '-plotmap':
        print("DENSITY MAP")
        plotdensitymap()
    if flag1 == '-plotstack':
        SpecRead.getstackplot(start,flag2)
