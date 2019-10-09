#################################################################
#                                                               #
#          SPEC MATHEMATICS                                     #
#                        version: 0.0.1α                        #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
#################################################################

import logging
logging.debug("Importing module SpecMath.py...")
import os
import sys
import numpy as np
import pickle
import SpecRead
import EnergyLib
from Mapping import getdensitymap
from ImgMath import LEVELS as LEVELS
import matplotlib.pyplot as plt
#from numba import guvectorize, float64, int64
#from numba import cuda
logging.debug("Importing numba jit...")
try: from numba import jit
except: logging.warning("Could not import numba package.")
from numba import jit
logging.debug("Importing module math...")
import math
logging.debug("Importing module scipy.signal...")
try: import scipy.signal
except: logging.warning("Could not import scipy package.")
logging.debug("Finished SpecMath imports.")

from tkinter import *
from tkinter import ttk

class Busy:
    
    def __init__(__self__,max_,min_):
        __self__.master = Toplevel()
        __self__.master.resizable(False,False)
        __self__.master.overrideredirect(True)
        x = __self__.master.winfo_screenwidth()
        y = __self__.master.winfo_screenheight()
        win_x = __self__.master.winfo_width()
        win_y = __self__.master.winfo_height()
        __self__.master.geometry('{}x{}+{}+{}'.format(166, 51,\
                int((x/2)-80), int((y/2)-23)))
        __self__.outerframe = Frame(__self__.master, bd=3, relief=RIDGE)
        __self__.outerframe.grid(row=0,column=0)
        __self__.master.label = Label(__self__.outerframe, text="Packing spectra...")
        __self__.master.label.grid(row=0,column=0)       
        __self__.master.body = Frame(__self__.outerframe)        
        __self__.master.body.grid(row=1,column=0)
        __self__.progress = ttk.Progressbar(__self__.master.body, orient="horizontal",length=160, mode="determinate",maximum=max_)
        __self__.progress.grid(row=0,column=0)

    def updatebar(__self__,value):
        __self__.progress["value"] = value
        __self__.progress.update()

    def update_text(__self__,text):
        __self__.master.label["text"] = text
        __self__.master.update()

    def destroybar(__self__):
        __self__.master.destroy()

#logging.debug("Importing numba environmental variables...")
#os.environ['NUMBAPRO_NVVM']      =\
#        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvvm\bin\nvvm64_33_0.dll'
#
#os.environ['NUMBAPRO_LIBDEVICE'] =\
#        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvvm\libdevice'
#
#os.environ['NUMBAPRO_CUDA_DRIVER']      =\
#        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvcc'


NOISE = 80
FANO = 0.114
compilation_progress = 0

class datacube:
    
    ndim = 0
    
    def __init__(__self__,dtypes,configuration):
        logging.debug("Initializing cube file")
        try: specsize = SpecRead.getdata(SpecRead.getfirstfile()) 
        except: specsize = 0
        __self__.dimension = SpecRead.getdimension()
        __self__.img_size = __self__.dimension[0]*__self__.dimension[1]
        __self__.datatypes = np.array(["{0}".format(dtypes[type]) for type in range(len(dtypes))])
        __self__.matrix = np.zeros([__self__.dimension[0],__self__.dimension[1],\
                specsize.shape[0]],dtype='float64',order='C')
        __self__.config = configuration
        __self__.calibration = SpecRead.getcalibration()
        __self__.energyaxis = energyaxis()
        __self__.ROI = {}
        __self__.hist = {}
        __self__.max_counts = {}

    def MPS(__self__):
        __self__.mps = np.zeros([__self__.matrix.shape[2]],dtype='float64')
        for c in range(__self__.matrix.shape[2]):
            for x in range(__self__.matrix.shape[0]):
                for y in range(__self__.matrix.shape[1]):
                    if __self__.mps[c] < __self__.matrix[x,y,c]: __self__.mps[c] = __self__.matrix[x,y,c]

    def stacksum(__self__):
        __self__.sum = np.zeros([__self__.matrix.shape[2]],dtype='float64')
        for x in range(__self__.matrix.shape[0]):
            for y in range(__self__.matrix.shape[1]):
                __self__.sum += __self__.matrix[x,y]
    
    def write_sum(__self__):
        try: os.mkdir(SpecRead.output_path)
        except: pass
        output_path = SpecRead.output_path
        sum_file = open(output_path+'stacksum.mca','w+')
        
        #writes header
        sum_file.write("<<PMCA SPECTRUM>>\nTAG - live_data_2\nDESCRIPTION -\n")
        sum_file.write("GAIN - 2\nTHRESHOLD - 0\nLIVE_MODE - 0\nPRESET_TIME - 280\n")
        sum_file.write("LIVE_TIME - 28.5880\nREAL_TIME - 29.3560\nSTART_TIME - 05/11/2017 22:10:19\n")
        sum_file.write("SERIAL_NUMBER - 1912\n<<CALIBRATION>>\nLABEL - Channel\n")
        for pair in __self__.calibration:
            sum_file.write("{0} {1}\n".format(pair[0],pair[1]))
        sum_file.write("<<DATA>>\n")
        ###############
        
        for counts in __self__.sum:
            sum_file.write("{}\n".format(int(counts)))
        sum_file.write("<<END>>")
        sum_file.close()

        ANSII_file = open(output_path+'ANSII_SUM.txt','w+')
        ANSII_file.write("counts\tenergy (KeV)\n")
        for index in range(__self__.sum.shape[0]):
            ANSII_file.write("{0}\t{1}\n".format(int(__self__.sum[index]),__self__.energyaxis[index]))
        ANSII_file.close()

    def strip_background(__self__,bgstrip=None):
        bgstrip = __self__.config['bgstrip']
        counter = 0
        __self__.background = np.zeros([__self__.dimension[0],__self__.dimension[1],\
                __self__.energyaxis.shape[0]],dtype='float64',order='C')
        if bgstrip == 'None':
            __self__.sum_bg = np.zeros([__self__.matrix.shape[2]])
        elif bgstrip == 'SNIPBG':
            __self__.sum_bg = np.zeros([__self__.matrix.shape[2]])
            for x in range(__self__.matrix.shape[0]):
                for y in range(__self__.matrix.shape[1]):
                    stripped = peakstrip(__self__.matrix[x,y],24,7)
                    __self__.background[x,y] = stripped
                    __self__.sum_bg += stripped
                    counter = counter + 1
                    __self__.progressbar.updatebar(counter)

    def create_densemap(__self__):
        __self__.densitymap = getdensitymap(__self__)

    def save_cube(__self__):
        try: 
            if not os.path.exists(SpecRead.output_path):
                logging.info("Creating outputh path {0}".forma(SpecRead.output_path))
                os.mkdir(SpecRead.output_path)
            else: logging.debug("Output path exists")
        except: 
            logging.warning("Could not create output folder {}".format(SpecRead.output_path))
            pass
        p_output = open(SpecRead.cube_path,'wb')
        pickle.dump(__self__,p_output)
        p_output.close()
        #print("File {0}.cube sucessfully compiled.".format(SpecRead.DIRECTORY))

    def compile_cube(__self__):
        logging.debug("Started mca compilation")
        __self__.progressbar = Busy(__self__.img_size,0)
        currentspectra = SpecRead.getfirstfile()
        logging.debug("First mca on list: {}".format(currentspectra))
        x,y,scan = 0,0,(0,0)
        for iteration in range(__self__.img_size):
            spec = currentspectra
            specdata = SpecRead.getdata(spec)
            for i in range(len(specdata)):
                __self__.matrix[x][y][i] = specdata[i]
            scan = updateposition(scan[0],scan[1])
            x,y = scan[0],scan[1]
            currentspectra = SpecRead.updatespectra(spec,__self__.img_size)
            __self__.progressbar.updatebar(iteration)
            
            #progress = int(iteration/__self__.img_size*20)
            #blank = (20 - progress - 1)
            #print("[" + progress*"#" + blank*" " + "]" + " / {0:.2f}"\
            #        .format(iteration/__self__.img_size*100), "Compiling cube...  \r", end='')
            #sys.stdout.flush()
        
        logging.debug("Calculating MPS...")
        __self__.progressbar.update_text("Calculating MPS...")
        datacube.MPS(__self__)
        logging.debug("Calculating summation spectrum...")
        __self__.progressbar.update_text("Calculating sum spec...")
        datacube.stacksum(__self__)
        logging.debug("Stripping background...")
        __self__.progressbar.update_text("Stripping background...")
        datacube.strip_background(__self__)
        logging.debug("Writing summation mca and ANSII files...")
        datacube.write_sum(__self__)
        logging.debug("Calculating sum map...")
        __self__.progressbar.update_text("Calculating sum map...")
        datacube.create_densemap(__self__)
        logging.debug("Saving cube file to disk...")
        __self__.progressbar.update_text("Writing to disk...")
        __self__.progressbar.destroybar()
        del __self__.progressbar 
        datacube.save_cube(__self__)
        logging.debug("Finished packing.")
        
    def pack_element(__self__,image,element):
        __self__.__dict__[element] = image
        logging.info("Packed {0} map to datacube {1}".format(element,SpecRead.cube_path))
        #print("Packed {0} map to datacube {1}".format(element,SpecRead.cube_path))
    
    def pack_hist(__self__,hist,bins,element):
        histfile = open(SpecRead.output_path+"\\"+element+"_hist.txt",'w')
        histfile.write("<<START>>\n")
        histfile.write("hist\n")
        for i in range(len(hist)):
            histfile.write("{0}\n".format(hist[i]))
        histfile.write("<<END>>")
        histfile.close()
        __self__.hist[element] = [hist,bins]
     
    def unpack_element(__self__,element):
        unpacked = __self__.__dict__[element]
        #print("Unpacked {0} map from datacube {1}".format(element,SpecRead.cube_path))
        logging.info("Unpacked {0} map from datacube {1}".format(element,SpecRead.cube_path))
        return unpacked

    def check_packed_elements(__self__):
        packed = []
        for element in EnergyLib.ElementList:
            if hasattr(__self__,element): 
                packed.append(element)
                #print("Found a map for {0}".format(element))
            else: pass
        return packed

    def prepack_elements(__self__,element_list):
        for element in element_list:
            __self__.__dict__[element] = np.zeros([__self__.dimension[0],__self__.dimension[1]])
            __self__.ROI[element] = np.zeros([__self__.energyaxis.shape[0]])
            __self__.max_counts[element] = np.nan
            __self__.hist[element] = [np.zeros([__self__.img_size]),np.zeros([LEVELS])]
    
def shift_center(xarray,yarray):
    ymax = yarray.max()
    y_list = yarray.tolist()
    idx = y_list.index(ymax)
    return xarray[idx],ymax,idx

def updateposition(a,b):
    imagesize = SpecRead.getdimension()
    imagex = imagesize[0]
    imagey = imagesize[1]
    imagedimension = imagex*imagey
    currentx = a
    currenty = b 
    if currenty == imagey-1:
        currenty=0
        currentx+=1
    else:
        currenty+=1
    actual=([currentx,currenty])
    return actual

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
    calibration = SpecRead.calibrate()
    return calibration[0]

def getstackplot(datacube,mode=None):
    stack = datacube.sum
    mps = datacube.mps
    bg = datacube.sum_bg
    energy = datacube.energyaxis
    if mode == 'summation':
        output = stack
       # plt.semilogy(energy,stack,label="Summation")
       # plt.semilogy(energy,mps,label="Maximum Pixel Spectrum")
       # plt.semilogy(energy,bg,label="Background estimation")
    elif mode == 'combined': 
        stack = stack/stack.max()
        mps = mps/mps.max()
        output = np.asarray([stack, mps])
       # plt.semilogy(energy,stack,label="Summation")
       # plt.semilogy(energy,mps,label="Maximum Pixel Spectrum")
       # plt.ylabel("Normalized counts")
    elif mode == 'mps':
        output = mps
        # plt.semilogy(energy,stack,label="Summation")
       # plt.ylabel("Counts")
    else:
       # plt.plot(energy,stack,label="Summation")
    #plt.legend()
    #plt.title("Sample: {}".format(SpecRead.DIRECTORY))
    #plt.xlabel("Energy (KeV)")
    #plt.grid(which='both',axis='both')
    #plt.show()
        pass
    return output

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

def setROI(lookup,xarray,yarray,localconfig):
    
    ####################################################################
    # setROI(lookup,xarray,yarray,localconfig)                         #
    # INPUT: eV energy, energy array (x axis) and data array           #
    # OUTPUT: indexes corresponding to 2*FWHM of a gaussian centered   #
    # at eV energy position (int, int, int, bool)                      #
    ####################################################################
    
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
        shift = shift_center(ROIaxis,ROIdata)
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
    logging.info("peak_center = {0}, channels = {1} {2}, peakwidth= {3}"\
            .format(peak_center,lowx_idx,highx_idx,(highx_idx-lowx_idx))) 
    return lowx_idx,highx_idx,peak_center,isapeak

def getpeakarea(lookup,data,energyaxis,continuum,localconfig,RAW,usedif2,dif2):
    Area = 0
   
    idx = setROI(lookup,energyaxis,data,localconfig)
    isapeak = idx[3]
    xdata = energyaxis[idx[0]:idx[1]]
    ydata = data[idx[0]:idx[1]]
    original_data = RAW[idx[0]:idx[1]] 
    ROIbg = continuum[idx[0]:idx[1]]
    
    ######################################
    # SIGNAL TO NOISE PEAK TEST CRITERIA # After Bright, D.S. & Newbury, D.E. 2004 
    ######################################

    if isapeak == True: 
        if original_data.sum() - ROIbg.sum() < 3*math.sqrt(ROIbg.sum()): isapeak = False
    
    ##########################
    # 2ND DIFFERENTIAL CHECK #
    ##########################
    if usedif2 == True and isapeak == True:
        smooth_dif2 = dif2[idx[0]:idx[1]]
    
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

@jit
def strip(an_array,cycles,width):
    ##################################################################
    # W IS THE WIDTH OF THE FILTER. THE WINDOW WILL BE (1*W)+1       #
    # W VALUE MUST BE LARGER THAN 2 AND ODD, SINCE 3 IS THE MINIMUM  #
    # SATISFACTORY POLYNOMIAL DEGREE TO SMOOTHEN THE DATA            #
    ##################################################################
    
    for k in range(cycles):
        l = width
        for l in range(an_array.shape[0]-width):
            m = (an_array[l-width] + an_array[l+width])/2
            if an_array[l] > m and an_array[l] !=0: an_array[l] = m
    return an_array

#@guvectorize([(float64[:], int64, int64, float64[:])], '(n),(),()->(n)')       
def peakstrip(an_array,cycles,width):
   
    TEST = False

    #initialize snip_bg array
    snip_bg = np.zeros(an_array.shape[0])

    #square root the data
    sqr_data = an_array**0.5

    #apply savgol filter to the square root data
    smooth_sqr = scipy.signal.savgol_filter(sqr_data,width,3)
    for i in range(smooth_sqr.shape[0]): 
        if smooth_sqr[i] < 0: smooth_sqr[i] = 0
    
    #strip peaks
    snip_bg = strip(smooth_sqr,cycles,width)

    #transform back
    snip_bg **= 2
    snip_bg = scipy.signal.savgol_filter(snip_bg,width,3)
    
    if TEST == True:
        plt.semilogy(snip_bg,label="background")
        plt.semilogy(an_array,label="spectrum")
        plt.legend()
        plt.show()

    return snip_bg

if __name__=="__main__":
    SpecRead.setup()
    cube = datacube(['xrf'],SpecRead.CONFIG)
    cube.compile_cube()
