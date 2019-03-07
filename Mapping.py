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
import matplotlib.pyplot as plt
import time
import math

timer=time.time()
#_for now the first spectra is given manually
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
    if currentx == imagex-1 and currenty == imagey-1:
        print("END OF IMAGE")
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
    #    print("Current X= %d\nCurrent Y= %d" % (currentx,currenty))
    #    print("Current spectra is: %s" % spec)
        sum = SpecRead.getsum(spec)
        density_map[currentx][currenty]=sum          #_update matrix
        scan=updateposition(scan[0],scan[1])
        currentx=scan[0]
        currenty=scan[1]
        currentspectra = SpecRead.updatespectra(spec,dimension)
    print("Execution took %s seconds" % (time.time() - timer))    
    plt.imshow(density_map,cmap='gray')
    plt.show()

def plotpeakmap(element):
    currentspectra = start
    density_map = np.zeros([imagex,imagey])
    scan=([0,0])
    currentx=scan[0]
    currenty=scan[1]
    energyaxis = SpecRead.calibrate(currentspectra,'data')

    for ITERATION in range(dimension):
        spec = currentspectra
    #    print("Current X= %d\nCurrent Y= %d" % (currentx,currenty))
    #    print("Current spectra is: %s" % spec)
        sum = SpecMath.getpeakarea(spec,element,energyaxis)
        density_map[currentx][currenty]=sum          #_update matrix
        scan=updateposition(scan[0],scan[1])
        currentx=scan[0]
        currenty=scan[1]
        currentspectra = SpecRead.updatespectra(spec,dimension)
        if isinstance(timer,int): print("Partial! %s seconds!" % (time.time() - timer))    
    print("Execution took %s seconds" % (time.time() - timer))    
    plt.imshow(density_map,cmap='gray')
    plt.show()

if __name__=="__main__":
    elementen = int(float(sys.argv[1])*1000)
    plotpeakmap(elementen)
