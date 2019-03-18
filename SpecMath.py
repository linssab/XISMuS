#################################################################
#                                                               #
#          SPEC MATHEMATICS                                     #
#                        version: a1.0                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import os
import numpy as np
import math
import scipy.signal
import matplotlib.pyplot as plt
import SpecRead
import EnergyLib
from PyMca5.PyMcaMath import SpecArithmetic as Arithmetic

NOISE = 80
FANO = 0.114

def function(ydata,x):
    return ydata[x]

def dif2(ydata,x,gain):
    value = (function(ydata, x + 2*gain) - 2*function(ydata, x + gain) + function(ydata, x)) / (gain * gain)
    return value

def getdif2(ydata,xdata,gain):
    dif2curve = []
    xinterval = xdata
#    print("xinterval = {0}".format(xinterval))
    yinterval = np.pad(ydata,2,'edge')
#    print("yinterval = {0}".format(yinterval))
    for x in range(len(xinterval)):
        difvalue = dif2(yinterval,x,1)
        dif2curve.append(difvalue)
    plt.plot(xinterval,dif2curve)
#    yinterval = yinterval[2:-2]
#    plt.plot(xinterval,yinterval)
#    plt.show()
    return dif2curve

def stacksum(firstspec,dimension):
    " DIMENSION STANDS FOR THE MAP DIMENSION, LINES*ROWS (OR THE NUMBER OF FILES) "
    " SO THE FUNCTION GETS THE TOTAL NUMBER OF SPECTRA TO BE STACKED "
    aux = SpecRead.getdata(firstspec)
    currentspectra = firstspec
    Stack = np.zeros([len(aux)])
    for i in range(dimension):
        spec = currentspectra
        data = SpecRead.getdata(spec)
        Stack = Stack + data
        currentspectra = SpecRead.updatespectra(spec,dimension)
    return Stack

def sigma(energy):
    return math.sqrt(((NOISE/2.3548)**2)+(3.85*FANO*energy))

def gaussianbuilder(channel,energy):
    sigma = sigma(energy)
    chEnergy = (channel*GAIN + B)*1000
    A = GAIN/(sigma)*math.sqrt(2*math.pi)
    return A*(math.exp(-(((energy-chEnergy)**2)/(2*(sigma**2)))))

def creategaussian(channels,energy):
    Gaussian = np.zeros([channels])
    if isinstance(energy,int):
        for i in range(channels):
            Gaussian[i]+=gaussianbuilder(i,energy)
    elif isinstance(energy,list): 
        for i in range(channels):
            for k in range(len(energy)):
                    Gaussian[i]+=gaussianbuilder(i,energy[k])
    return Gaussian

def getindex(value,array):
    ydata = array.tolist()
    return ydata.index(value)

def setROI(lookup,xarray,yarray,isapeak=True):
    lookup = int(lookup)
    peak_corr = 0
    print("-"*51)
    for peak_corr in range(3):
        print("-"*20 + "iteration {0}".format(peak_corr) + "-"*20)
        print("lookup: %d" % lookup)
        FWHM = 2.3548 * sigma(lookup)
        lowx = (lookup - (FWHM))/1000
        highx = (lookup + (FWHM))/1000
        print("FWHM: %f\nlowx: %f\nhighx: %f" % (FWHM, lowx,highx))
        idx = 0
        while xarray[idx] <= lowx:
            idx+=1
        lowx_idx = idx-2
        print("lowx_idx: %d" % lowx_idx)
        while xarray[idx] <= highx:
            idx+=1
        highx_idx = idx+2
        print("highx_idx: %d" % highx_idx)
        ROI = xarray[lowx_idx:highx_idx]
        data = yarray[lowx_idx:highx_idx]
        shift = Arithmetic.search_peak(ROI,data)
        print(shift[0])
        if -120 < (shift[0]*1000)-lookup < 120:
            if (shift[0]*1000)-lookup == 0: break
            lookup = shift[0]*1000
            peak_corr = 0
            print("GAP IS LESSER THAN 120eV!")
        else: 
            print(" difference is: {0}".format((shift[0]*1000)-lookup))
            isapeak = False
            break
        print(ROI[0],ROI[-1])
#    plt.plot(xarray,yarray)
#    plt.plot(ROI,data)
#    plt.show()
    return lowx_idx,highx_idx,isapeak

def getpeakarea(lookup,data,energyaxis,svg=True):
    Area = 0
    if svg == True:
        data = scipy.signal.savgol_filter(\
                data,5,3,deriv=0,delta=1,axis=0,mode="interp",cval=0.0)
    idx = setROI(lookup,energyaxis,data)
    xdata = energyaxis[idx[0]:idx[1]]
    ydata = data[idx[0]:idx[1]]
    if idx[2] == True:
        for i in range(len(xdata)):
            Area += ydata[i]
    else: print("{0} has no peak!".format(lookup))
    return Area

if __name__=="__main__":
    dirname = os.path.join('C:/misure/')
    file = dirname+'Cesareo_200.mca'
    xdata = SpecRead.calibrate(file,'file')
    ydata = SpecRead.getdata(file)
    gain = SpecRead.getgain(file,'data')
    lookup = 11939
    print(getpeakarea(lookup,ydata,xdata,svg=True))
