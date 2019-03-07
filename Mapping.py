#################################################################
#                                                               #
#          DENSITY MAP GENERATOR                                #
#                        version: a1.1                          #
# @author: Sergio Lins                                          #
#################################################################

import sys
import os
import numpy as np
import SpecMath
import SpecRead
from PyMca5.PyMcaMath import SpecArithmetic as Arithmetic
import matplotlib.pyplot as plt
import time

timer=time.time()
#_for now the first spectra is given manually
start = SpecRead.dirname+'Cesareo_1.mca'

loadconfig = os.path.join(SpecRead.dirname,"config.cfg")
if not os.path.exists(loadconfig):
    raise IOError("Config file not found!") 
else: config_file = SpecRead.dirname+'config.cfg'

file = open(config_file, 'r')
line = file.readline()
if "<<SIZE>>" in line:
    print("IMAGE SIZE IS: ")
    while "<<END>>" not in line:
        if 'lines' in line:
            line=line.replace('\r','')
            line=line.replace('\n','')
            line=line.replace('\t',' ')
            aux = line.split()
            x = int(aux[1])
            print("%d Line(s)" % x)
        if 'rows' in line:
            line=line.replace('\r','')
            line=line.replace('\n','')
            line=line.replace('\t',' ')
            aux = line.split()
            y = int(aux[1])
            print("%d Rows(s)" % y)
        line = file.readline()
    dimension = x*y

def updateposition(a,b):
    currentx=a
    currenty=b
    if currenty == y-1:
#        print("We reached the end of the line, y= %d" % currenty)
        currenty=0
#        print("Now we reset the column, y= %d" % currenty)
        currentx+=1
#        print("And last we move to the next line, x= %d" % currentx)
    else:
        currenty+=1
#        print("We are still in the middle of the line, y+1 = %d" % currenty)
    if currentx == x-1 and currenty == y-1:
        print("END OF IMAGE")
    actual=([currentx,currenty])
    return actual

def getpeaks(file):
    data = SpecRead.getdata(file)
    data = np.asarray(data, dtype='int')
    energies = SpecRead.calibrate(file)
    return Arithmetic.search_peak(energies,data)

def createmap():
    currentspectra = start
    density_map = np.zeros([x,y])
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

createmap()
