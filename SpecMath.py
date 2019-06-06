#################################################################
#                                                               #
#          SPEC MATHEMATICS                                     #
#                        version: a3.00                         #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
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
from numba import guvectorize, float64, int64
from numba import cuda
from numba import jit

os.environ['NUMBAPRO_NVVM']      =\
        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvvm\bin\nvvm64_33_0.dll'

os.environ['NUMBAPRO_LIBDEVICE'] =\
        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvvm\libdevice'

os.environ['NUMBAPRO_CUDA_DRIVER']      =\
        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvcc'


NOISE = 80
FANO = 0.114

def function(ydata,x):
    return ydata[x]

def dif2(ydata,x,gain):
    value = (function(ydata, x + 2*gain) - 2*function(ydata, x + gain)\
            + function(ydata, x)) / (gain * gain)
    return value

def getdif2(ydata,xdata,gain):
    xinterval = np.pad(xdata,2,'edge')
    yinterval = np.pad(ydata,2,'edge')
    dif2curve = np.zeros([len(yinterval)])
    for x in range(len(xinterval)-2):
        difvalue = dif2(yinterval,x,1)
        dif2curve[x] = difvalue
    dif2curve = dif2curve[1:-3]
    return dif2curve

def energyaxis():
    calibration = SpecRead.calibrate(SpecRead.getdata(SpecRead.getfirstfile()),'data')
    return calibration[0]

def getstackplot(mca,energy,*args):
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

#####################################################################
# setROI(lookup,xarray,yarray)                                      #
# INPUT: eV energy, energy array (x axis) and data array            #
# OUTPUT: indexes corresponding to 2*FWHM of a gaussian centered    #
# at eV energy position                                             #
#####################################################################

def setROI(lookup,xarray,yarray,localconfig):
    lookup = int(lookup)
    peak_corr = 0
    isapeak = True
    
    if localconfig.get('bgstrip') == 'SNIPBG' and\
    localconfig.get('peakmethod') != 'PyMcaFit': 
        yarray  = scipy.signal.savgol_filter(yarray,5,3)
    
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
        lowx_idx = idx-3
        logging.debug("lowx_idx: %d" % lowx_idx)
        while xarray[idx] <= highx:
            idx+=1
        highx_idx = idx+3
        logging.debug("highx_idx: %d" % highx_idx)
        ROIaxis = xarray[lowx_idx:highx_idx]
        ROIdata = yarray[lowx_idx:highx_idx]
        shift = Arithmetic.search_peak(ROIaxis,ROIdata)
        logging.debug("Shift: {0}".format(shift))
        
        if 1.10*(-FWHM/2) < (shift[0]*1000)-lookup < 1.10*(FWHM/2):
            if (shift[0]*1000)-lookup == 0:
                logging.debug("Shift - lookup = {0}!".format((shift[0]*1000)-lookup))
            lookup = shift[0]*1000
            peak_corr = 0
            logging.debug("GAP IS LESSER THAN {0}!".format(1.10 * FWHM/2))
        else: 
            logging.debug("Difference is too large: {0}".format((shift[0]*1000)-lookup))
            lookupcenter = int(len(ROIaxis)/2)
            shift = (0,0,lookupcenter)
            isapeak = False
        
        logging.debug("ROI[0] = {0}, ROI[-1] = {1}".format(ROIaxis[0],ROIaxis[-1]))
    
    lowx_idx = lowx_idx + 3
    highx_idx = highx_idx - 3
    peak_center = shift[2]-3
    logging.debug("peak_center = {0}".format(peak_center)) 
    return lowx_idx,highx_idx,peak_center,isapeak

def getpeakarea(lookup,data,energyaxis,continuum,localconfig,RAW,usedif2):
    Area = 0
   
    idx = setROI(lookup,energyaxis,data,localconfig)
    isapeak = idx[3]
    xdata = energyaxis[idx[0]:idx[1]]
    ydata = data[idx[0]:idx[1]]
    original_data = RAW[idx[0]:idx[1]] 
    ROIbg = continuum[idx[0]:idx[1]]
    
# SIGNAL TO NOISE PEAK TEST CRITERIA #
 
    if isapeak == True: 
        if original_data.sum() < 2*ROIbg.sum(): isapeak = False
    
    ##########################
    # 2ND DIFFERENTIAL CHECK #
    ##########################
    if usedif2 == True and isapeak == True:
        smooth_dif2 = scipy.signal.savgol_filter(getdif2(RAW,energyaxis,1),5,3)
        smooth_dif2 = smooth_dif2[idx[0]:idx[1]]
    
        ##################################
        # 2ND DIFFERENTIAL CUTOFF FILTER #
        ##################################
    
        for i in range(len(smooth_dif2)):
            if smooth_dif2[i] < -1: smooth_dif2[i] = smooth_dif2[i]
            elif smooth_dif2[i] > -1: smooth_dif2[i] = 0
    
        if smooth_dif2[idx[2]] < 0 or smooth_dif2[idx[2]+1] < 0 or smooth_dif2[idx[2]-1] < 0:
            logging.debug("Dif2 is: {0}".format(smooth_dif2[idx[2]]))
            logging.debug("Dif2 left = {0} and Dif2 right = {1}".format(\
                    smooth_dif2[idx[2]-1],smooth_dif2[idx[2]+1]))
            for i in range(len(xdata)):
                if ROIbg[i] < ydata[i]: Area += (ydata[i]-ROIbg[i])
                logging.debug("Area: {0}\t Estimated BG: {1}".format(ydata[i],ROIbg[i]))
        else: 
            logging.debug("{0} has no peak! Dif2 = {1} and isapeak = {2}\n"\
                    .format(lookup,smooth_dif2[idx[2]],isapeak))
            logging.debug("Dif2 left = {0} and Dif 2 right = {1}".format(
                smooth_dif2[idx[2]-1],smooth_dif2[idx[2]+1]))
    
    ##########################
    
    ####################################################
    # Isapeak is not invoked for PyMcaFit method       #
    # this makes it work similar to simple_roi method. #
    # With low-count datasets this is better to obtain #
    # images that look better                          #
    ####################################################

    elif localconfig.get('peakmethod') == 'PyMcaFit':
        logging.info("No dif 2 criteria for {0} method".format(localconfig.get('peakmethod')))
        smooth_dif2 = np.zeros([len(xdata)])
        for i in range(len(xdata)):
            if ROIbg[i] < ydata[i]: Area += (ydata[i]-ROIbg[i])
            logging.debug("Area: {0}\t Estimated BG: {1}".format(ydata[i],ROIbg[i]))
               
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
        try: print("ydata[idx[2]] = {0}, smooth_dif2[idx[2]] = {1}".format(\
                ydata[idx[2]],smooth_dif2[idx[2]]))
        except: pass
        print("idx[2] = {0}".format(idx[2]))
        print("Lookup: {0} Area: {1}\n".format(lookup,Area))
    
        plt.plot(xdata,ydata, label='data')
        plt.plot(xdata,original_data, label='RAW data')
        try: plt.plot(xdata,smooth_dif2, label='2nd Differential')
        except: pass
        plt.plot(xdata,ROIbg, label='BG estimation')
        plt.legend()
        plt.show()
    
    return Area,idx

# W IS THE WIDTH OF THE FILTER. THE WINDOW WILL BE (2*W)+1       #
# W VALUE MUST BE LARGER THAN 3 AND ODD, SINCE 3 IS THE MINIMUM  #
# SATISFACTORY POLYNOMIAL DEGREE TO SMOOTHEN THE DATA            #

@jit
def ryan_snip(an_array,cycles,width):
    for k in range(cycles):
        l = width
        for l in range(an_array.shape[0]-width):
            m = (an_array[l-width] + an_array[l+width])/2
            if an_array[l] > m: an_array[l] = m
    return an_array

#@guvectorize([(float64[:], int64, int64, float64[:])], '(n),(),()->(n)')       
def peakstrip(an_array,cycles,width):
    
    #initialize snip_bg array
    snip_bg = np.zeros(an_array.shape[0])
    
    #apply savgol filter to input spectrum
    smooth_sqr = scipy.signal.savgol_filter(an_array,width,3)
    for i in range(smooth_sqr.shape[0]): 
        if smooth_sqr[i] < 0: smooth_sqr[i] = 0
    
    #squareroot transformation of the spectrum
    smooth_sqr **= 0.5
    
    #strip peaks
    snip_bg = ryan_snip(smooth_sqr,cycles,width)
    
    #transform back
    snip_bg **= 2
    
    return snip_bg

if __name__=="__main__":
    dirname = SpecRead.dirname
    specfile = dirname+'Cesareo_217.mca'
    xdata = energyaxis()
#    import SpecFitter
#    testdata = SpecFitter.fit(specfile)
#    testdata = SpecRead.getdata(specfile)
    RAW_data = SpecRead.getdata(specfile)
    lookup = 9711
    
    continuum = peakstrip(RAW_data,24,5)
    plt.plot(continuum, label='bg')
    plt.plot(RAW_data, label='raw')
    plt.show()

#    continuum = np.zeros([len(testdata)])
#    getpeakarea(lookup,testdata,xdata,continuum,'SNIPBG',RAW_data)
#    smooth_dif2 = scipy.signal.savgol_filter(\
#            getdif2(ydata,xdata,1),5,3)
#    for i in range(len(smooth_dif2)):
#        if smooth_dif2[i] < -1: smooth_dif2[i] = smooth_dif2[i]
#        elif smooth_dif2[i] > -1: smooth_dif2[i] = 0



