#################################################################
#                                                               #
#          SPEC MATHEMATICS                                     #
#                        version: a1.0                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import logging
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
#    plt.plot(xinterval,dif2curve)
#    yinterval = yinterval[2:-2]
#    plt.plot(xinterval,yinterval)
#    plt.show()
    return dif2curve

def stacksum(firstspec,dimension):
    # FIRSTSPEC IS A STRING WITH THE NAME OF THE FIRST FILE IN THE BATCH #
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

# GAUSSIAN FUNCTIONS #

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

# END OF GAUSSIAN FUNCTIONS #

def getindex(value,array):
    # AUXILIARY FUNTION TO QUICKLY FIND AN ELEMENT POSITION IN A NP ARRAY #
    # WITHOUT THE USE OF .WHERE                                           # 
    ydata = array.tolist()
    return ydata.index(value)

# setROI(lookup,xarray,yarray)
# INPUT: eV energy, energy array (x axis) and data array
# OUTPUT: indexes corresponding to 2*FWHM of a gaussian centered
# at eV energy position

def setROI(lookup,xarray,yarray):
    lookup = int(lookup)
    peak_corr = 0
    logging.debug("-"*51)
    for peak_corr in range(3):
        logging.debug("-"*20 + "iteration {0}".format(peak_corr) + "-"*20)
        logging.debug("lookup: %d" % lookup)
        FWHM = 2.3548 * sigma(lookup)
        lowx = (lookup - (FWHM))/1000
        highx = (lookup + (FWHM))/1000
        logging.debug("FWHM: %feV lowx: %fKeV highx: %fKeV" % (FWHM, lowx,highx))
        idx = 0
        while xarray[idx] <= lowx:
            idx+=1
        lowx_idx = idx-1
        logging.debug("lowx_idx: %d" % lowx_idx)
        while xarray[idx] <= highx:
            idx+=1
        highx_idx = idx+1
        logging.debug("highx_idx: %d" % highx_idx)
        ROI = xarray[lowx_idx:highx_idx]
        data = yarray[lowx_idx:highx_idx]
        shift = Arithmetic.search_peak(ROI,data)
        logging.debug("Shift: {0}".format(shift))
        if 1.03*(-FWHM/2) < (shift[0]*1000)-lookup < 1.03*(FWHM/2):
            if (shift[0]*1000)-lookup == 0: break
            lookup = shift[0]*1000
            peak_corr = 0
            logging.debug("GAP IS LESSER THAN {0}!".format(FWHM/2))
        else: 
            logging.debug("Difference is: {0}".format((shift[0]*1000)-lookup))
            shift = (0,0,0)
            break
        logging.debug("ROI[0] = {0}, ROI[-1] = {1}".format(ROI[0],ROI[-1]))
#    plt.plot(xarray,yarray)
#    plt.plot(ROI,data)
#    plt.show()
    return lowx_idx,highx_idx,shift[2]

def getpeakarea(lookup,data,energyaxis,svg=True):
    Area = 0
    if svg == True:
        data = scipy.signal.savgol_filter(\
                data,9,5,deriv=0,delta=1,axis=0,mode="interp",cval=0.0)
    idx = setROI(lookup,energyaxis,data)
    xdata = energyaxis[idx[0]:idx[1]]
    ydata = data[idx[0]:idx[1]]
    smooth_dif2 = scipy.signal.savgol_filter(\
            getdif2(ydata,xdata,1),9,4)
    for i in range(len(smooth_dif2)):
        if smooth_dif2[i] < -1: smooth_dif2[i] = smooth_dif2[i]
        elif smooth_dif2[i] > -1: smooth_dif2[i] = 0
    if idx[2] != 0 and smooth_dif2[idx[2]] < 0:
        logging.debug("Dif2 < 0!")
        for i in range(len(xdata)):
            Area += ydata[i]
    else: logging.debug("{0} has no peak!".format(lookup))
    return Area

"""if __name__=="__main__":
    dirname = os.path.join(SpecRead.dirname)
    file = dirname+'Cesareo_98.mca'
    xdata = SpecRead.calibrate(file,'file')
    ydata = SpecRead.getdata(file)
    ydata = scipy.signal.savgol_filter(\
             ydata,13,4,deriv=0,delta=1,axis=-1,mode="interp",cval=0.0)
    gain = SpecRead.getgain(file,'data')
    lookup = 9885
    print(getpeakarea(lookup,ydata,xdata,svg=True))
    smooth_dif2 = scipy.signal.savgol_filter(\
            getdif2(ydata,xdata,1),9,4)
    for i in range(len(smooth_dif2)):
        if smooth_dif2[i] < -1: smooth_dif2[i] = smooth_dif2[i]
        elif smooth_dif2[i] > -1: smooth_dif2[i] = 0
    plt.plot(xdata,ydata)
    plt.plot(xdata,smooth_dif2)
    plt.show()
"""
