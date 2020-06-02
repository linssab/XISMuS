#################################################################
#                                                               #
#          SPEC MATHEMATICS                                     #
#                        version: a3.21                         #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
#################################################################

import logging
import os
import sys
import numpy as np
import math
<<<<<<< Updated upstream
import scipy.signal
import matplotlib.pyplot as plt
import pickle
import SpecRead
import EnergyLib
from numba import guvectorize, float64, int64
from numba import cuda
from numba import jit
=======
from math import factorial
logger.info("Finished SpecMath imports.")

from tkinter import *
from tkinter import ttk

def FN_reset():
    Constants.FANO = 0.114
    Constants.NOISE = 80

def FN_set(F, N):
    Constants.FANO = F
    Constants.NOISE = N

def build_pool(size):
    Constants.FILE_POOL = []
    spec = getfirstfile()
    
    name=str(spec)
    specfile_name = name.split("\\")[-1]
    name = specfile_name.split(".")[0]
    extension = specfile_name.split(".")[-1]
    for i in range(len(name)):
        if not name[-i-1].isdigit(): 
            prefix = name[:-i]
            index = name[-i:]
            break
    index = int(index)+1

    Constants.FILE_POOL.append(spec)
    for idx in range(index,size+index-1,1):
        spec = os.path.join(Constants.SAMPLES_FOLDER,
                Constants.CONFIG["directory"],
                str(Constants.NAME_STRUCT[0]+str(idx)+"."+Constants.NAME_STRUCT[2]))
        Constants.FILE_POOL.append(spec)

def digest_psdinv(y,energies):
    
    """ -- y is an array with the measured FWHM.
    -- energies is an array with the corresponding energies for the corresponding 
    FWHM peaks

    This function performs a pseudo inverse regression to equation 1 (see OSP article) 
    with singular value decomposition (numpy.pinv()) to find FANO and NOISE values
    that satisfies the equation """

    x = [(2.3548**2)*3.85*en for en in energies]
    Y = np.asarray([i**2 for i in y], dtype="float32")
    X = np.array([np.ones(len(x)), x], dtype="float32")
    C = np.dot(Y,np.linalg.pinv(X))

    return abs(C)

def digest_lstsq(y,energies):
    
    """ -- y is an array with the measured FWHM.
    -- energies is an array with the corresponding energies for the corresponding 
    FWHM peaks

    This function performs a least-squares fitting to equation 1 (see OSP article) 
    to find FANO and NOISE values that satisfies it """

>>>>>>> Stashed changes

os.environ['NUMBAPRO_NVVM']      =\
        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvvm\bin\nvvm64_33_0.dll'

os.environ['NUMBAPRO_LIBDEVICE'] =\
        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvvm\libdevice'

os.environ['NUMBAPRO_CUDA_DRIVER']      =\
        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvcc'


NOISE = 80
FANO = 0.114

class datacube:
    
<<<<<<< Updated upstream
    ndim = 0
    specsize = SpecRead.getdata(SpecRead.getfirstfile()) 

    def __init__(__self__,dtypes,configuration):
        __self__.dimension = SpecRead.getdimension()
        __self__.img_size = __self__.dimension[0]*__self__.dimension[1]
        __self__.datatypes = np.array(["{0}".format(dtypes[type]) for type in range(len(dtypes))])
        __self__.matrix = np.zeros([__self__.dimension[0],__self__.dimension[1],\
                datacube.specsize.shape[0]],dtype='float64',order='C')
        __self__.config = configuration
        __self__.calibration = SpecRead.getcalibration()
        __self__.energyaxis = energyaxis()

    def MPS(__self__):
        __self__.mps = np.zeros([__self__.matrix.shape[2]],dtype='float64')
        for c in range(__self__.matrix.shape[2]):
            for x in range(__self__.matrix.shape[0]):
                for y in range(__self__.matrix.shape[1]):
                    if __self__.mps[c] < __self__.matrix[x,y,c]: __self__.mps[c] = __self__.matrix[x,y,c]

    def stacksum(__self__):
        __self__.sum = np.zeros([__self__.matrix.shape[2]],dtype='float64')
=======
    def __init__(__self__,dtypes,configuration,mode="",name=""):
        if mode == "merge": 
            __self__.name = name
            __self__.path = "No path, this cube was merged"
        else:
            from Constants import SAMPLES_FOLDER
            __self__.name = configuration["directory"]
            __self__.path = os.path.join(SAMPLES_FOLDER,__self__.name)
        logger.debug("Initializing cube file")
        
        try: specsize = getdata(getfirstfile()) 
        except: specsize = 0
        __self__.datatypes = np.array(["{0}".format(
            dtypes[type]) for type in range(len(dtypes))])
        if mode != "merge":
            __self__.dimension = getdimension()
            __self__.img_size = __self__.dimension[0]*__self__.dimension[1]
            __self__.matrix = np.zeros([__self__.dimension[0],__self__.dimension[1],\
                specsize.shape[0]],dtype="int32",order='C')
            __self__.config = configuration
            __self__.calibration = getcalibration()
            __self__.energyaxis, __self__.gain = calibrate()
            __self__.config["gain"] = __self__.gain
            __self__.mps = np.zeros([specsize.shape[0]],dtype="int32")
        __self__.ROI = {}
        __self__.hist = {}
        __self__.max_counts = {}

    def MPS(__self__,mps):

        """ Read all data in datacube.matrix and returns a spectrum where each index
        is the maximum value found in the matrix for that same index.
        MPS stands for Maximum Pixel Spectrum """

        size = int(len(mps))
        shape = np.asarray(__self__.matrix.shape)
        cy_funcs.cy_MPS(__self__.matrix, shape, mps, size)

    def stacksum(__self__):

        """ Reall all data in datacube.matrix and return the summation derived spectrum """

        __self__.sum = np.zeros([__self__.matrix.shape[2]],dtype="int32")
        __self__.sum_bg = np.zeros([__self__.matrix.shape[2]],dtype="float32")
>>>>>>> Stashed changes
        for x in range(__self__.matrix.shape[0]):
            for y in range(__self__.matrix.shape[1]):
                __self__.sum += __self__.matrix[x,y]
    
    def write_sum(__self__):
        output_path = SpecRead.output_path
        sum_file = open(output_path+'stacksum.mca','w')
        
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

        ANSII_file = open(output_path+'ANSII_SUM.txt','w')
        ANSII_file.write("counts\tenergy (KeV)\n")
        for index in range(__self__.sum.shape[0]):
            ANSII_file.write("{0}\t{1}\n".format(int(__self__.sum[index]),__self__.energyaxis[index]))
        ANSII_file.close()

    def strip_background(__self__,bgstrip=None):
        bgstrip = __self__.config['bgstrip']
        __self__.background = np.zeros([__self__.dimension[0],__self__.dimension[1],\
                datacube.specsize.shape[0]],dtype='float64',order='C')
        if bgstrip == None:
            pass
        elif bgstrip == 'SNIPBG':
            __self__.sum_bg = np.zeros([__self__.matrix.shape[2]])
            for x in range(__self__.matrix.shape[0]):
                for y in range(__self__.matrix.shape[1]):
                    stripped = peakstrip(__self__.matrix[x,y],24,5)
                    __self__.background[x,y] = stripped
                    __self__.sum_bg += stripped

    def save_cube(__self__):
        p_output = open(SpecRead.cube_path,'wb')
        pickle.dump(__self__,p_output)
        p_output.close()
<<<<<<< Updated upstream
        print("File {0}.cube sucessfully compiled.".format(SpecRead.DIRECTORY))

    def compile_cube(__self__):
        currentspectra = SpecRead.getfirstfile()
        x,y,scan = 0,0,(0,0)
        for iteration in range(__self__.img_size):
            spec = currentspectra
            specdata = SpecRead.getdata(spec)
            for i in range(len(specdata)):
                __self__.matrix[x][y][i] = specdata[i]
            scan = updateposition(scan[0],scan[1])
            x,y = scan[0],scan[1]
            currentspectra = SpecRead.updatespectra(spec,__self__.img_size)
            progress = int(iteration/__self__.img_size*20)
            blank = (20 - progress - 1)
            print("[" + progress*"#" + blank*" " + "]" + " / {0:.2f}"\
                    .format(iteration/__self__.img_size*100), "Compiling cube...  \r", end='')
            sys.stdout.flush()
        print("\nCalculating Summation and Maximum Pixel Spectrum and stripping background.")
        sys.stdout.flush()
        datacube.MPS(__self__)
=======

    def digest_merge(__self__,bar=None):
        if bar != None: 
            bar.progress["maximum"] = 5
            bar.updatebar(1)
            bar.update_text("1/5 Calculating MPS...")
        mps = np.zeros([__self__.matrix.shape[2]],dtype="int32")
        datacube.MPS(__self__,mps)
        __self__.mps = mps
        if bar != None: 
            bar.update_text("2/5 Calculating Stacksum...")
            bar.updatebar(2)
        datacube.stacksum(__self__)
        datacube.write_sum(__self__)
        if bar != None:
            bar.update_text("3/5 Finding Fano and Noise...")
            bar.updatebar(3)
        datacube.fit_fano_and_noise(__self__)
        if bar != None:
            bar.update_text("4/5 Creating densemap...")
            bar.updatebar(4)
        datacube.create_densemap(__self__)
        if bar != None:
            bar.update_text("5/5 Writing to disk...")
            bar.updatebar(5)
        datacube.save_cube(__self__)

    def compile_cube(__self__):

        """ Iterate over the spectra dataset, reading each spectrum file saving it to the 
        proper xy matrix indexes and calculating the background contribution as well. 
        This method saves all derived spectra, writes summation mca to disk and calculates
        the density map. """

        logger.debug("Started mca compilation")
        timer = time.time()
        __self__.progressbar = Busy(__self__.img_size,0)
        x,y,scan = 0,0,(0,0)
        if not isinstance(Constants.FILE_POOL,tuple):
            build_pool(__self__.img_size)
        else: pass
        iteration = 0
        for spec in Constants.FILE_POOL:
            try: specdata = getdata(spec)
            except: 
                __self__.progressbar.destroybar()
                return 1, spec
            if isinstance(specdata,np.ndarray) == False: 
                __self__.progressbar.interrupt(specdata,5)
                __self__.progressbar.destroybar()
                return 1,specdata
            __self__.matrix[x][y] = specdata
            scan = refresh_position(scan[0],scan[1],__self__.dimension)
            x,y = scan[0],scan[1]
            __self__.progressbar.updatebar(iteration)
            iteration += 1
        logger.info("Packed spectra in {} seconds".format(time.time()-timer))

        logger.debug("Calculating MPS...")
        __self__.progressbar.update_text("Calculating MPS...")
        mps = np.zeros([__self__.matrix.shape[2]],dtype="int32")
        datacube.MPS(__self__,mps)
        __self__.mps = mps
        logger.debug("Stripping background...")
        __self__.progressbar.update_text("Stripping background...")
        datacube.strip_background(__self__)
        logger.debug("Calculating summation spectrum...")
        __self__.progressbar.update_text("Calculating sum spec...")
>>>>>>> Stashed changes
        datacube.stacksum(__self__)
        datacube.strip_background(__self__)
        datacube.save_cube(__self__)
        datacube.write_sum(__self__)
    
    def pack_element(__self__,image,element):
        __self__.__dict__[element] = image
        print("Packed {0} map to datacube {1}".format(element,SpecRead.cube_path))

    def unpack_element(__self__,element):
        unpacked = __self__.__dict__[element]
        print("Unpacked {0} map from datacube {1}".format(element,SpecRead.cube_path))
        return unpacked

    def check_packed_elements(__self__):
        packed = []
        for element in EnergyLib.ElementList:
            if hasattr(__self__,element): 
                packed.append(element)
                print("Found a map for {0}".format(element))
            else: pass
        return packed

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

def getstackplot(datacube,*args):
    print(args)
    stack = datacube.sum
    mps = datacube.mps
    bg = datacube.sum_bg
    energy = datacube.energyaxis
    if '-bg' in args:
        plt.semilogy(energy,stack,label="Summation")
        plt.semilogy(energy,mps,label="Maximum Pixel Spectrum")
        plt.semilogy(energy,bg,label="Background estimation")
    elif '-semilog' in args and '-bg' not in args: 
        stack = stack/stack.max()
        mps = mps/mps.max()
        plt.semilogy(energy,stack,label="Summation")
        plt.semilogy(energy,mps,label="Maximum Pixel Spectrum")
        plt.ylabel("Normalized counts")
    else:
        plt.plot(energy,stack,label="Summation")
        plt.plot(energy,mps,label="Maximum Pixel Spectrum")
    plt.legend()
    plt.xlabel("Energy (KeV)")
    plt.show()
    return 0

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
    # at eV energy position                                            #
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
    
<<<<<<< Updated upstream
    lowx_idx = lowx_idx + 3
    highx_idx = highx_idx - 3
    peak_center = shift[2]-3
    logging.debug("peak_center = {0}".format(peak_center)) 
    return lowx_idx,highx_idx,peak_center,isapeak

def getpeakarea(lookup,data,energyaxis,continuum,localconfig,RAW,usedif2,dif2):
=======
    logger.debug("peak_center = {0}, channels = {1} {2}, peakwidth= {3}".format(
        peak_center,lowx_idx,highx_idx,(highx_idx-lowx_idx))) 
    return lw,hi,peak_center,isapeak

def getpeakarea(lookup,data,energyaxis,continuum,localconfig,usedif2,dif2):

    """ Calculates the netpeak area of a given lookup energy.

    ---------------------------------------------------------

    INPUT:
        lookup; int (theoretical peak center eV energy)
        data; np.array (counts)
        energyaxis; np.array (calibrated energy axis KeV)
        continuum; np.array (background counts)
        localconfig; dict (condiguration)
        usedif2; bool
        dif2; np.array (second differential of counts)
    OUTPUT:
        area; float
        idx; list (containing setROI function outputs) """

>>>>>>> Stashed changes
    Area = 0
   
    idx = setROI(lookup,energyaxis,data,localconfig)
    isapeak = idx[3]
    xdata = energyaxis[idx[0]:idx[1]]
    ydata = data[idx[0]:idx[1]]
    ROIbg = continuum[idx[0]:idx[1]]
    
    ######################################
    # SIGNAL TO NOISE PEAK TEST CRITERIA # After Bright, D.S. & Newbury, D.E. 2004 
    ######################################

    if isapeak == True: 
<<<<<<< Updated upstream
        if original_data.sum() - ROIbg.sum() < 3*math.sqrt(ROIbg.sum()): isapeak = False
=======
        if ydata.sum() - ROIbg.sum() < 3*math.sqrt(abs(ROIbg.sum())): isapeak = False
>>>>>>> Stashed changes
    
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
<<<<<<< Updated upstream
        print("RAW peak: {0}\t bg: {1}\nyDATA peak: {2}"\
               .format(original_data.sum(),(3*ROIbg.sum()),ydata.sum()))
        chi2 = 0
        for i in range(len(original_data)):
            aux = math.pow((ydata[i] - original_data[i]),2)
            chi2 += aux
        chi2 = chi2/len(original_data)
        print("chi2 = {0:.2f}".format(chi2))

=======
>>>>>>> Stashed changes
        print("ydata = {0}".format(ydata))
        print("len(ydata) = {0}".format(len(ydata)))
        try: print("ydata[idx[2]] = {0}, smooth_dif2[idx[2]] = {1}".format(\
                ydata[idx[2]],smooth_dif2[idx[2]]))
        except: pass
        print("idx[2] = {0}".format(idx[2]))
        print("Lookup: {0} Area: {1}\n".format(lookup,Area))
    
        plt.plot(xdata,ydata, label='data')
        try: plt.plot(xdata,smooth_dif2, label='2nd Differential')
        except: pass
        plt.plot(xdata,ROIbg, label='BG estimation')
        plt.legend()
        plt.show()
    
    return Area,idx

@jit
def ryan_snip(an_array,cycles,width):
    
    ##################################################################
    # W IS THE WIDTH OF THE FILTER. THE WINDOW WILL BE (1*W)+1       #
    # W VALUE MUST BE LARGER THAN 2 AND ODD, SINCE 3 IS THE MINIMUM  #
    # SATISFACTORY POLYNOMIAL DEGREE TO SMOOTHEN THE DATA            #
    ##################################################################
    
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
    print("Null.")
