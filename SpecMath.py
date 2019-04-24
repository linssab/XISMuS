#################################################################
#                                                               #
#          SPEC MATHEMATICS                                     #
#                        version: a2.2                          #
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
    value = (function(ydata, x + 2*gain) - 2*function(ydata, x + gain)\
            + function(ydata, x)) / (gain * gain)
    return value

def getdif2(ydata,xdata,gain):
    dif2curve = []
    xinterval = np.pad(xdata,2,'edge')
    yinterval = np.pad(ydata,2,'edge')
    for x in range(len(xinterval)-2):
        difvalue = dif2(yinterval,x,1)
        dif2curve.append(difvalue)
    dif2curve = dif2curve[1:-1]
    return dif2curve

def energyaxis():
    calibration = SpecRead.calibrate(SpecRead.getdata(SpecRead.getfirstfile()),'data')
    return calibration[0]

def getstackplot(mca,energy,*args):
    energy = energy
    size = SpecRead.getdimension()
    dimension = size[0]*size[1]
    data = stacksum(mca,dimension)
    if '-semilog' in args: plt.semilogy(energy,data)
    else:
        plt.plot(energy,data)
    plt.show()
    return 0

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

# setROI(lookup,xarray,yarray)                                      #
# INPUT: eV energy, energy array (x axis) and data array            #
# OUTPUT: indexes corresponding to 2*FWHM of a gaussian centered    #
# at eV energy position                                             #

def setROI(lookup,xarray,yarray,svg):
    lookup = int(lookup)
    peak_corr = 0
    isapeak = True
    
    if svg == 'SNIPBG': yarray  = scipy.signal.savgol_filter(yarray,5,3)
    
    logging.debug("-"*15 + " Setting ROI " + "-"*15)
    
    for peak_corr in range(2):
        logging.debug("-"*15 + " iteration {0} ".format(peak_corr) + "-"*15)
        logging.debug("lookup: %d" % lookup)
        FWHM = 2.3548 * sigma(lookup)
        lowx = (lookup - (FWHM))/1000
        highx = (lookup + (FWHM))/1000
        logging.debug("FWHM: %feV lowx: %fKeV highx: %fKeV" % (FWHM, lowx,highx))
        idx = 0
        while xarray[idx] <= lowx:
            idx+=1
        lowx_idx = idx-2
        logging.debug("lowx_idx: %d" % lowx_idx)
        while xarray[idx] <= highx:
            idx+=1
        highx_idx = idx+2
        logging.debug("highx_idx: %d" % highx_idx)
        ROIaxis = xarray[lowx_idx:highx_idx]
        ROIdata = yarray[lowx_idx:highx_idx]
        shift = Arithmetic.search_peak(ROIaxis,ROIdata)
        logging.debug("Shift: {0}".format(shift))
        
        if 1.20*(-FWHM/2) < (shift[0]*1000)-lookup < 1.20*(FWHM/2):
            if (shift[0]*1000)-lookup == 0:
                logging.debug("Shift - lookup = {0}!".format((shift[0]*1000)-lookup))
            lookup = shift[0]*1000
            peak_corr = 0
            logging.debug("GAP IS LESSER THAN {0}!".format(1.05 * FWHM/2))
        else: 
            logging.debug("Difference is too large: {0}".format((shift[0]*1000)-lookup))
            lookupcenter = int(len(ROIaxis)/2)
            shift = (0,0,lookupcenter)
            isapeak = False
        
        logging.debug("ROI[0] = {0}, ROI[-1] = {1}".format(ROIaxis[0],ROIaxis[-1]))
    
    lowx_idx = lowx_idx + 2
    highx_idx = highx_idx - 2
    peak_center = shift[2]-2
    logging.debug("peak_center = {0}".format(peak_center)) 
    return lowx_idx,highx_idx,peak_center,isapeak

def getpeakarea(lookup,data,energyaxis,continuum,svg,RAW):
    Area = 0
    
    idx = setROI(lookup,energyaxis,data,svg)
    isapeak = idx[3]
    xdata = energyaxis[idx[0]:idx[1]]
    ydata = data[idx[0]:idx[1]]
    original_data = RAW[idx[0]:idx[1]] 
    ROIbg = continuum[idx[0]:idx[1]]
    
# SIGNAL TO NOISE PEAK TEST CRITERIA #
 
    if isapeak == True: 
        if original_data.sum() <= (3*ROIbg.sum()): isapeak = False
    
    try: 
        smooth_dif2 = scipy.signal.savgol_filter(getdif2(RAW,energyaxis,1),5,3)
        smooth_dif2 = smooth_dif2[idx[0]:idx[1]]
    except:
        loggin.warning("Cannot apply savgol filter to 2nd derivate! Vector is too short!")
        smooth_dif2 = getdif2(RAW,energyaxis,1)
        raise Exception("Cannot smooth 2nd derivate!")
        pass
    
    for i in range(len(smooth_dif2)):
        if smooth_dif2[i] < -1: smooth_dif2[i] = smooth_dif2[i]
        elif smooth_dif2[i] > -1: smooth_dif2[i] = 0
    
# 2ND DERIVATIVE CHECK - LEFT AND RIGHT - #    

    if smooth_dif2[idx[2]] < 0 and isapeak == True\
            or smooth_dif2[idx[2]+1] < 0 and isapeak == True\
            or smooth_dif2[idx[2]-1] < 0 and isapeak == True:
        logging.debug("Dif2 is: {0}".format(smooth_dif2[idx[2]]))
        logging.debug("Dif2 left = {0} and Dif2 right = {1}".format(\
                smooth_dif2[idx[2]-1],smooth_dif2[idx[2]+1]))
        for i in range(len(xdata)):
            if ROIbg[i] < ydata[i]: Area += (ydata[i]-ROIbg[i])
            logging.debug("Area: {0}\t Estimated BG: {1}".format(ydata[i],ROIbg[i]))
                
    else: 
        logging.debug("{0} has no peak! Dif2 = {1}\n".format(lookup,smooth_dif2[idx[2]]))
        logging.debug("Dif2 left = {0} and Dif 2 right = {1}".format(
            smooth_dif2[idx[2]-1],smooth_dif2[idx[2]+1]))

    ##############
    # TEST BLOCK #          
    TESTFNC = False
    ##############    
    
    if TESTFNC == True:    
        print(5*"*" + " IS A PEAK? " + 5*"*" + "\n\t{0}\t".format(isapeak))
        print("RAW peak: {0}\t bg: {1}\nyDATA peak: {2}"\
               .format(original_data.sum(),(3*ROIbg.sum()),ydata.sum()))
        chi2 = 0
        for i in range(len(original_data)):
            aux = math.pow((ydata[i] - original_data[i]),2)
            chi2 += aux
        chi2 = chi2/len(original_data)
        print("chi2 = {0:.2f}".format(chi2))

        print("ydata = {0}".format(ydata))
        print("len(ydata) = {0}".format(len(ydata)))
        print("ydata[idx[2]] = {0}, smooth_dif2[idx[2]] = {1}".format(\
                ydata[idx[2]],smooth_dif2[idx[2]]))
        print("idx[2] = {0}".format(idx[2]))
        print("Lookup: {0} Area: {1}\n".format(lookup,Area))
    
        plt.semilogy(xdata,ydata)
        plt.semilogy(xdata,original_data)
    #    plt.semilogy(xdata,smooth_dif2)
        plt.semilogy(xdata,ROIbg)
        plt.show()
    
    return Area

# W IS THE WIDTH OF THE FILTER. THE WINDOW WILL BE (2*W)+1       #
# W VALUE MUST BE LARGER THAN 3 AND ODD, SINCE 3 IS THE MINIMUM  #
# SATISFACTORY POLYNOMIAL DEGREE TO SMOOTHEN THE DATA            #

def ryan_snip(dataarray,cycles,w):
    for k in range(cycles):
        l = w
        for l in range(len(dataarray)-w):
            m = (dataarray[l-w] + dataarray[l+w])/2
            if dataarray[l] > m: dataarray[l] = m
    return dataarray

def peakstrip(spectrum,cycles,w):
    spectrum_sq = np.zeros([len(spectrum)])
    logging.debug("TIMESTAMP: BEGIN of background estimation!")
    for i in range(len(spectrum)): spectrum_sq[i] = math.sqrt(spectrum[i])
    spectrum_smth = scipy.signal.savgol_filter(spectrum_sq,w,2)
    spectrum_filtered = ryan_snip(spectrum_smth,cycles,w)
    for j in range(len(spectrum_filtered)):\
            spectrum_filtered[j] = math.pow(spectrum_filtered[j],2)
    
    background = scipy.signal.savgol_filter(spectrum_filtered,9,3)
    logging.debug("TIMESTAMP: END of background estimation!")
    
#    plt.semilogy(background)
#    plt.semilogy(spectrum)
#    plt.show()
    
    return background
   

if __name__=="__main__":
    dirname = os.path.join(SpecRead.dirname)
    specfile = dirname+'Cesareo_74.mca'
    xdata = energyaxis()
    import SpecFitter
    testdata = SpecFitter.fit(specfile)
#    testdata = SpecRead.getdata(specfile)
    RAW_data = SpecRead.getdata(specfile)
    lookup = 9711
    
#    continuum = peakstrip(testdata,18,3)
    continuum = np.zeros([len(testdata)])
    getpeakarea(lookup,testdata,xdata,continuum,'SNIPBG',RAW_data)
#    smooth_dif2 = scipy.signal.savgol_filter(\
#            getdif2(ydata,xdata,1),5,3)
#    for i in range(len(smooth_dif2)):
#        if smooth_dif2[i] < -1: smooth_dif2[i] = smooth_dif2[i]
#        elif smooth_dif2[i] > -1: smooth_dif2[i] = 0

