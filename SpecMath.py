#################################################################
#                                                               #
#          SPEC MATHEMATICS                                     #
#                        version: 1.0.0 - May - 2020            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################
TESTFNC = False

# import utilities
import logging
logger = logging.getLogger("logfile")
logger.debug("Importing module SpecMath.py...")
import os, time
import sys
import numpy as np
import pickle

# import internal modules (only needed functions)
from SpecRead import (getdata, 
getdimension, 
getcalibration, 
getfirstfile, 
calibrate, 
updatespectra)

from EnergyLib import ElementList
from ImgMath import LEVELS
from Mapping import getdensitymap
from ProgressBar import Busy
import Constants
import cy_funcs

# import other modules
import matplotlib.pyplot as plt
logger.debug("Importing numba jit...")
try:
    from numba import jit
except:
    print("Failed to load numba")
logger.debug("Importing module math...")
import math
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


    x = [(2.3548**2)*3.85*en for en in energies]
    Y = np.asarray([i**2 for i in y], dtype="float32")
    X = np.vstack([np.ones(len(x)), x]).T
    C = np.linalg.lstsq(X,Y,rcond=None)[0]

    return abs(C)

def FN_fit(specdata,gain):

    """ Finds suitable FANO and NOISE factors to the input spectrum
    INPUT:
        specdata; 1D-array
        gain; calibration gain (eV)
    OUTPUT:
        1D-tuple (F, N) 
        
        --------------------------------------------------------

    The fit is performed by changing the tophat filter parameters
    (window and tolerance to the variance) iteratively. This is 
    performed to automate the function to any input spectrum, since 
    different parameters work differently for each spectrum profile.
    The output is the averaged value, unless a reasonable value
    (between 0.040 and 0.240) is found for the FANO factor. """

    F, N = 0, 0
    i, x = 0, 200
    avg_F, avg_N = 0,0
    data = savgol_filter(specdata,5,3)
    v, w, r = 4,9,4
    while i < x:
        F, N = FN_iter(data,gain,v,w,r)
        if 0.040 <= F <= 0.240: 
            logger.warning("Fano in between 0.040 and 0.240")
            logger.warning("Fano and Noise matched: F:{} N:{}".format(F,N))
            return F, N
        avg_F += F
        avg_N += N
        r += 1
        if r > 12:
            r = 4
            w += 2
            if w >= 13:
                w = 2
                v += 1
                if v == 7: v=1
        i += 1
    N = avg_N/i
    F = avg_F/i
    logger.warning("Fano and Noise averaged: F:{} N:{}".format(F,N))
    return F, N

def FN_iter(data,gain,v,w,r):

    """ Verifies if the peak detected is greater than the 
    variance. r is a tolerance factor that multiplies the variance coef. """

    th, delt, pks = tophat(data,v,w)
    widths = []
    energies = []
    for i in pks:
        if th[i]>r*delt[i]:
            try: lw, up, width = fwhm(data,i,r)
            except: break
            widths.append(width*gain*1000)
            energies.append(gain*i*1000)
    N, F = digest_psdinv(widths,energies)
    return F, N**.5


def tophat(y,v,w):


    """ Applies a tophat filter to a 1D-array following the recipe
    given reference below:
    [1] Van Grieken, R.E.; Markowicz, A.A. Handbook of X-ray spectrometry, 
    Marcel Dekker, Inc., 2002.
    
    --------------------------------------------------------------------

    INPUT:
        y; 1D-array
        v; side window width (int)
        w; central window width (int)
    OUTPUT:
        new_y; filtered pectrum (1D-array)
        delta; variance (1D-array)
        peaks; identified peaks indexes (1D-list)
    """
    
    def hk_(k,v,w):

        if -v-(w/2) <= k < -w/2: return -1/(2*v)
        elif -w/2 <= k <= w/2: return 1/w
        elif w/2 < k <= v+(w/2): return -1/(2*v)
        else: return 0

    new_y = np.zeros([y.shape[0]])
    delta = np.zeros([y.shape[0]])
    peaks = []
    for i in range(y.shape[0]-(int(v+w/2))):
        y_star = 0
        y_delta = 0
        for k in range(int(-v-w/2),int(v+w/2)):
            hk = hk_(k,v,w)
            y_star += hk*y[i+k]
            y_delta += abs((hk**2)*y[i+k])
        new_y[i] = y_star
        delta[i] = y_delta**.5
    for j in range(1,y.shape[0]-1):
        if new_y[j-1] <= new_y[j] and new_y[j] > new_y[j+1]:
            peaks.append(j)
    return new_y, delta, peaks

def fwhm(data,i,win):

    """ Finds the indexes where half the peaks' height is
    found for peak located at index i 
    
    INPUT:
        data; 1D-array
        i; peak index
        win; tolearnce window
    OUTPUT:
        lw; lower index
        up; upper index
        up-lw; peak width """

    half = data[i]/2
    lw, up = 0, 0
    for j in range(i-win,i):
        if data[j]>=half: 
            lw = j-1
    j=0
    for j in range(i,i+win):
        if data[j]<=half: 
            up = j-1
            break
    if lw >= up: return 0,0,0
    return lw, up, up-lw


class datacube:

    """ Cube class. Comprises all data read from spectra, elemental maps created,
    background extracted (as a separate xy matrix), derived spectra, image size, image
    dimension, datacube configuration, calibrated energy axis """

    ndim = 0
    
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
                specsize.shape[0]],dtype="float32",order='C')
            __self__.config = configuration
            __self__.calibration = getcalibration()
            __self__.energyaxis, __self__.gain = calibrate()
            __self__.config["gain"] = __self__.gain
            __self__.mps = specsize.shape[0]
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

        __self__.sum = np.zeros([__self__.matrix.shape[2]],dtype="float32")
        __self__.sum_bg = np.zeros([__self__.matrix.shape[2]],dtype="float32")
        for x in range(__self__.matrix.shape[0]):
            for y in range(__self__.matrix.shape[1]):
                __self__.sum += __self__.matrix[x,y]
                __self__.sum_bg += __self__.background[x,y]

    def fit_fano_and_noise(__self__):
        __self__.FN = FN_fit(__self__.sum,__self__.gain)
    
    def write_sum(__self__):

        """ Saves the summation derived spectrum as an mca file to disk """

        # import internal variables.
        # they must be imported here in order to be the most recent ones (they are constantly
        # updated by the GUI).
        from SpecRead import output_path, cube_path
        try: os.mkdir(output_path)
        except: pass
        sum_file = open(os.path.join(output_path,"stacksum.mca"),'w+')
        
        #writes header
        sum_file.write("<<PMCA SPECTRUM>>\nTAG - TAG\nDESCRIPTION - Piratininga SM Sum Spectrum\n")
        sum_file.write("GAIN - 2\nTHRESHOLD - 0\nLIVE_MODE - 0\nPRESET_TIME - OFF\n")
        sum_file.write("LIVE_TIME - 0\nREAL_TIME - 0\nSTART_TIME - {}\n".format(
            time.strftime("%Y-%m-%d %H:%M:%S", 
                time.gmtime())))
        sum_file.write("SERIAL_NUMBER - 00001\n<<CALIBRATION>>\nLABEL - Channel\n")
        for pair in __self__.calibration:
            sum_file.write("{0} {1}\n".format(pair[0],pair[1]))
        sum_file.write("<<DATA>>\n")
        ###############
        
        for counts in __self__.sum:
            sum_file.write("{}\n".format(int(counts)))
        sum_file.write("<<END>>")
        sum_file.close()

        ANSII_file = open(os.path.join(output_path,"ANSII_SUM.txt"),'w+')
        ANSII_file.write("counts\tenergy (KeV)\n")
        for index in range(__self__.sum.shape[0]):
            ANSII_file.write("{0}\t{1}\n".format(
                int(__self__.sum[index]),
                __self__.energyaxis[index]))
        ANSII_file.close()

    def strip_background(__self__,
            bgstrip=None,
            recalculating=False,
            progressbar=None):

        """ Calculates the background contribution to each invidual spectrum.
        The calculated data is saved into the datacube object.
        bgstrip; a string """
        
        if recalculating == True: bgstrip = bgstrip
        else: bgstrip = __self__.config['bgstrip']
        counter = 0
        __self__.background = np.zeros([__self__.dimension[0],__self__.dimension[1],\
                __self__.energyaxis.shape[0]],dtype="float32",order='C')
        if bgstrip == 'None':
            __self__.sum_bg = np.zeros([__self__.matrix.shape[2]])
        elif bgstrip == 'SNIPBG':
            try: cycles, window,savgol,order= __self__.config["bg_settings"] 
            except: cycles, window, savgol, order = 24,5,5,3
            __self__.sum_bg = np.zeros([__self__.matrix.shape[2]])
            for x in range(__self__.matrix.shape[0]):
                for y in range(__self__.matrix.shape[1]):
                    # default cycle and sampling window = 24,5
                    stripped = peakstrip(__self__.matrix[x,y],cycles,window,savgol,order)
                    __self__.background[x,y] = stripped
                    counter = counter + 1
                    if recalculating == True: progressbar.updatebar(counter)
                    else: __self__.progressbar.updatebar(counter)

    def create_densemap(__self__):

        """ Calls getdensitymap and attributes the 2D-array output to the object """

        __self__.densitymap = getdensitymap(__self__)

    def save_cube(__self__):

        """ Writes (pickle) the datacube object to memory, if the cube already exists, it is
        replaced (updated) """ 

        from SpecRead import output_path, cube_path
        from Constants import SAMPLES_FOLDER
        __self__.root = SAMPLES_FOLDER
        try: 
            if not os.path.exists(output_path):
                logger.info("Creating outputh path {0}".forma(output_path))
                os.mkdir(output_path)
            else: logger.debug("Output path exists")
        except: 
            logger.warning("Could not create output folder {}".format(output_path))
            pass
        p_output = open(cube_path,'wb')
        pickle.dump(__self__,p_output)
        p_output.close()

    def digest_merge(__self__,bar=None):
        if bar != None: 
            bar.progress["maximum"] = 5
            bar.updatebar(1)
            bar.update_text("1/5 Calculating MPS...")
        mps = np.zeros([__self__.matrix.shape[2]],dtype="float32")
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
        __self__.progressbar = Busy(__self__.img_size,0)
        currentspectra = getfirstfile()
        logger.debug("First mca on list: {}".format(currentspectra))
        x,y,scan = 0,0,(0,0)
        for iteration in range(__self__.img_size):
            spec = currentspectra
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
            currentspectra = updatespectra(spec,__self__.img_size)
            __self__.progressbar.updatebar(iteration)

        logger.debug("Calculating MPS...")
        __self__.progressbar.update_text("Calculating MPS...")
        mps = np.zeros([__self__.matrix.shape[2]],dtype="float32")
        datacube.MPS(__self__,mps)
        __self__.mps = mps
        logger.debug("Stripping background...")
        __self__.progressbar.update_text("Stripping background...")
        datacube.strip_background(__self__)
        logger.debug("Calculating summation spectrum...")
        __self__.progressbar.update_text("Calculating sum spec...")
        datacube.stacksum(__self__)
        logger.debug("Writing summation mca and ANSII files...")
        datacube.write_sum(__self__)
        logger.debug("Calculating sum map...")
        __self__.progressbar.update_text("Calculating sum map...")
        datacube.create_densemap(__self__)
        __self__.progressbar.update_text("Finding Noise and Fano...")
        datacube.fit_fano_and_noise(__self__)
        logger.debug("Saving cube file to disk...")
        __self__.progressbar.update_text("Writing to disk...")
        __self__.progressbar.destroybar()
        del __self__.progressbar 
        datacube.save_cube(__self__)
        logger.debug("Finished packing.")
        return 0,None
        
    def pack_element(__self__,image,element,line):

        """ Saves elemental distribution image to datacibe object 
        image; a 2d-array
        element; a string
        line; a string """

        from SpecRead import output_path, cube_path
        __self__.__dict__[element+"_"+line] = image
        logger.info("Packed {0} map to datacube {1}".format(element,cube_path))
    
    def pack_hist(__self__,hist,bins,element):
        
        """ Saves the histogram of the last calculated elemental distribution map. 
        This method is called by ImgMath.py while saving the maps """

        from SpecRead import output_path, cube_path
        histfile = open(output_path+"\\"+element+"_hist.txt",'w')
        histfile.write("<<START>>\n")
        histfile.write("hist\n")
        for i in range(len(hist)):
            histfile.write("{0}\n".format(hist[i]))
        histfile.write("<<END>>")
        histfile.close()
        __self__.hist[element] = [hist,bins]
     
    def unpack_element(__self__,element,line):

        """ Retrieves a 2d-array elemental distribution map from the datacube.
        element; a string
        line; a string """

        from SpecRead import output_path, cube_path
        unpacked = __self__.__dict__[element+"_"+line]
        logger.info("Unpacked {0} map from datacube {1}".format(element,cube_path))
        return unpacked

    def check_packed_elements(__self__):
        
        """ Returns a list with all elemental distribution maps packed into the
        datacube object """

        packed = []
        for element in ElementList:
            if hasattr(__self__,element+"_a"):
                if hasattr(__self__,element+"_b"):
                    if __self__.__dict__[element+"_a"].max() > 0:
                        packed.append(element+"_a")
                    if __self__.__dict__[element+"_b"].max() > 0:
                        packed.append(element+"_b")
                else:
                    if __self__.__dict__[element+"_a"].max() > 0:
                        packed.append(element+"_a")
            else: pass
        if hasattr(__self__,"custom_a"): packed.append("custom_a")
        return packed

    def prepack_elements(__self__,element_list):

        """ Allocates keys in the datacube object to store the elemental distribution maps """

        for element in element_list:
            __self__.__dict__[element+"_a"] = np.zeros([__self__.dimension[0],
                __self__.dimension[1]],dtype="float32")
            __self__.__dict__[element+"_b"] = np.zeros([__self__.dimension[0],
                __self__.dimension[1]],dtype="float32")
            __self__.ROI[element] = np.zeros([__self__.energyaxis.shape[0]],dtype="float32")
            __self__.max_counts[element+"_a"] = 0
            __self__.max_counts[element+"_b"] = 0
            __self__.hist[element] = [np.zeros([__self__.img_size]),np.zeros([LEVELS])]
        __self__.__dict__["custom"] = np.zeros([__self__.dimension[0],__self__.dimension[1]])
    
def shift_center(xarray,yarray):
    
    """ Returns the highest value and its index in yarray and its corresponding value
    in xarray """

    ymax = yarray.max()
    y_list = yarray.tolist()
    idx = y_list.index(ymax)
    return xarray[idx],ymax,idx

def refresh_position(a,b,length):
    
    """ Returns the next pixel position """

    imagex = length[0]
    imagey = length[1]
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

def dif2(ydata,x,gain):
    
    """ Complementary function to getdif2 """
    
    value = (ydata[x + 2*gain] - 2*ydata[x + gain] + ydata[x]) / (gain * gain)
    return value

def getdif2(ydata,gain):
    
    """ Returns the second differential of ydata """
    
    yinterval = np.pad(ydata,2,'edge')
    dif2curve = np.zeros([len(yinterval)])
    for x in range(len(yinterval)-2):
        difvalue = dif2(yinterval,x,1)
        dif2curve[x] = difvalue
    dif2curve = dif2curve[1:-3]
    return dif2curve

def savgol_filter(y, window_size, order, deriv=0, rate=1):
   
    """ This function was taken from https://gist.github.com/krvajal 
    and compared to scipy.signal package, a reliable widely known package
    for signal analysis.

    References
    [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688 """

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError as msg:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')

def energyaxis():
    
    """ Returns the energyaxis array according to input calibration parameters (anchors) """
    
    calibration = calibrate()
    return calibration[0]

def getstackplot(datacube,mode=None):
    
    """ Returns the requested derived spectrum from datacube object """
    
    stack = datacube.sum
    mps = datacube.mps
    bg = datacube.sum_bg
    energy = datacube.energyaxis
    if mode == 'summation':
        output = stack
    elif mode == 'mps':
        output = mps
    else:
        pass
    return output

def sigma(energy):

    """ Calculates sigma value based on energy input 
    Reference:
    [1] V.A. Solé, E. Papillon, M. Cotte, Ph. Walter, J. Susini, A multiplatform 
    code for the analysis of energy-dispersive X-ray fluorescence spectra, 
    Spectrochim. Acta Part B 62 (2007) 63-68. 
    
    ---------------------------------------------------------------------

    INPUT:
        energy; electronvolts - eV (int)
    OUTPUT:
        float """

    return math.sqrt(((Constants.NOISE/2.3548)**2)+(3.85*Constants.FANO*energy))

def gaussianbuilder(channel,energy):

    """ Deprecated, to be removed in future updates """

    sigma = sigma(energy)
    chEnergy = (channel*GAIN + B)*1000
    A = GAIN/(sigma)*math.sqrt(2*math.pi)
    return A*(math.exp(-(((energy-chEnergy)**2)/(2*(sigma**2)))))

def creategaussian(channels,energy):
    
    """ Deprecated, to be removed in future updates """

    gaussian = np.zeros([channels])
    if isinstance(energy,int):
        for i in range(channels):
            gaussian[i]+=gaussianbuilder(i,energy)
    elif isinstance(energy,list): 
        for i in range(channels):
            for k in range(len(energy)):
                    gaussian[i]+=gaussianbuilder(i,energy[k])
    return gaussian

def setROI(lookup,xarray,yarray,localconfig):
    
    """
    INPUT: 
        lookup; eV energy (int)
        xarray; np.array
        yarray; np.array
        localconfig; dict
    OUTPUT: 
        low_idx; int
        high_idx; int
        peak_center; int
        isapeak; bool
    
    - indexes correspond to 2*FWHM of a gaussian centered
    at eV energy position (int, int, int, bool) 
    """
    
    lookup = int(lookup)
    if lookup < 4800: w_tolerance = 2
    elif lookup > 15000: w_tolerance = 3
    else: w_tolerance = 1
    peak_corr = 0
    peak_center = 0
    shift = [0,0,0]
    isapeak = True
    
    if localconfig.get('bgstrip') == 'SNIPBG':
        yarray  = savgol_filter(yarray,5,3)
    
    logger.debug("-"*15 + " Setting ROI " + "-"*15)
    
    for peak_corr in range(3):
        logger.debug("-"*15 + " iteration {0} ".format(peak_corr) + "-"*15)
        logger.debug("lookup: %d" % lookup)
        FWHM = 2.3548 * sigma(lookup)
        lowx = (lookup - (FWHM))/1000
        highx = (lookup + (FWHM))/1000
        logger.debug("FWHM: %feV lowx: %fKeV highx: %fKeV" % (FWHM, lowx,highx))

        #################### 
        # gets ROI indexes #
        #################### 

        idx = 0
        while xarray[idx] <= lowx:
            idx+=1
        lowx_idx = idx-1
        logger.debug("lowx_idx: %d" % lowx_idx)
        while xarray[idx] <= highx:
            idx+=1
        highx_idx = idx+1
        logger.debug("highx_idx: %d" % highx_idx)
        
        ROIaxis = xarray[lowx_idx:highx_idx]
        ROIdata = yarray[lowx_idx:highx_idx]
        
        if shift[0]*1000-lookup == 0: 
            lw,hi = lowx_idx, highx_idx
            try: peak_center, = np.where((ROIaxis == shift[0]))[0]
            except: return 0,2,1,False
            break
        
        shift = shift_center(ROIaxis,ROIdata)
        logger.debug("Shift: {0}".format(shift))
       
        ##########################################
        # verify the distance from a higher peak #
        ##########################################

        difference = abs((shift[0]*1000)-lookup)
        if difference < (3+w_tolerance)*localconfig["gain"]*1000:
            logger.debug("Shift - lookup = {0}!".format((shift[0]*1000)-lookup))
            logger.debug("GAP IS LESSER THAN {0}!".format((
                3+w_tolerance)*localconfig["gain"]*1000))
            peak_center = shift[2]
            peak_corr += 1
            lookup = shift[0]*1000
            if peak_corr == 2:
                while xarray[idx] <= lowx:
                    idx+=1
                lowx_idx = idx-1
                logger.debug("lowx_idx: %d" % lowx_idx)
                while xarray[idx] <= highx:
                    idx+=1
                highx_idx = idx+1
                logger.debug("highx_idx: %d" % highx_idx)
            lw, hi = lowx_idx, highx_idx
        else: 
            logger.debug("Difference is too large: {0}".format((shift[0]*1000)-lookup))
            
            ############################################################
            # if peak_corr = 0 here, shift failed in the first attempt #
            ############################################################

            if peak_corr == 0: 
                isapeak = False
                lw, hi = lowx_idx, highx_idx
            return lw,hi,peak_center,isapeak
        
        logger.debug("ROI[0] = {0}, ROI[-1] = {1}".format(ROIaxis[0],ROIaxis[-1]))
    
    logger.debug("peak_center = {0}, channels = {1} {2}, peakwidth= {3}"\
            .format(peak_center,lowx_idx,highx_idx,(highx_idx-lowx_idx))) 
    return lw,hi,peak_center,isapeak

def getpeakarea(lookup,data,energyaxis,continuum,localconfig,RAW,usedif2,dif2):

    """ Calculates the netpeak area of a given lookup energy.

    ---------------------------------------------------------

    INPUT:
        lookup; int (theoretical peak center eV energy)
        data; np.array (counts)
        energyaxis; np.array (calibrated energy axis KeV)
        continuum; np.array (background counts)
        localconfig; dict (condiguration)
        RAW; np.array (counts, same as data)
        usedif2; bool
        dif2; np.array (second differential of counts)
    OUTPUT:
        area; float
        idx; list (containing setROI function outputs) """

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
        if original_data.sum() - ROIbg.sum() < 3*math.sqrt(abs(ROIbg.sum())): isapeak = False
    
    ##########################
    # 2ND DIFFERENTIAL CHECK #
    ##########################

    if usedif2 == True and isapeak == True:
        smooth_dif2 = dif2[idx[0]:idx[1]]
    
        # checks second differential and calculates the net area - background
        if smooth_dif2[idx[2]] < 0 or smooth_dif2[idx[2]+1] < 0 or smooth_dif2[idx[2]-1] < 0:
            logger.debug("Dif2 is: {0}".format(smooth_dif2[idx[2]]))
            logger.debug("Dif2 left = {0} and Dif2 right = {1}".format(\
                    smooth_dif2[idx[2]-1],smooth_dif2[idx[2]+1]))
            Area += ydata.sum() - ROIbg.sum()
        else: 
            logger.debug("{0} has no peak! Dif2 = {1} and isapeak = {2}\n"\
                    .format(lookup,smooth_dif2[idx[2]],isapeak))
            logger.debug("Dif2 left = {0} and Dif 2 right = {1}".format(
                smooth_dif2[idx[2]-1],smooth_dif2[idx[2]+1]))
    
    ##########################
                  
    ##############
    # TEST BLOCK #          
    ##############    
    
    if TESTFNC == True:
 
        print(5*"*" + " IS A PEAK? " + 5*"*" + "\n\t{0}\t".format(isapeak))
        print("RAW peak: {0}\t 3*BG: {1}\nDATA peak: {2}"\
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
        print("Lookup: {0} Area(DATA_PEAK - BG): {1}\n".format(lookup,Area))
    
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

    """
    Strips the peaks contained in the input array following an
    iteractive peak clipping method.

    Reference: 
    [1] van Grieken, R.E.; Markowicz, A.A. Handbook of X-ray spectrometry,
    Marcel Dekker, Inc., 2002.
    [2] Clayton CA, Hines JW, Elkins PD. Anal Chem 59:2506, 1987.

    ----------------------------------------------------------------------

    INPUT:
        an_array; np.array
        cycles; int
        width; int
    OUTPUT:
        an_array; np.array
    """

    ##################################################################
    # W IS THE WIDTH OF THE FILTER. THE WINDOW WILL BE (1*W)+1       #
    # W VALUE MUST BE LARGER THAN 2 AND ODD, SINCE 3 IS THE MINIMUM  #
    # SATISFACTORY POLYNOMIAL DEGREE TO SMOOTHEN THE DATA            #
    ##################################################################
    
    size = an_array.shape[0]
    for k in range(cycles):
        if k >= cycles-8:
            width = int(width/np.sqrt(2))
        for l in range(0, size):
            if l-width < 0: low = 0
            else: low = l-width
            if l+width >= size: high = size-1
            else: high = l+width
            m = (an_array[low] + an_array[high])/2
            if m < 1: m = 1
            if an_array[l] > m: an_array[l] = m
    return an_array


def peakstrip(an_array,cycles,width,*args):
    
    """
    Calculates the continuum/background contribution of the input spectrum following
    the SNIPBG method.

    Reference:
    [1] van Grieken, R.E.; Markowicz, A.A. Handbook of X-ray spectrometry,
    Marcel Dekker, Inc., 2002.

    --------------------------------------------------------------------------------

    INPUT:
        an_array; np.array
        cycles; int
        width; int
        args; list (cycles, width, sav_gol order and sav_gol window can be fully    
        given as a list instead)
    OUTPUT:
        snip_bg; np.array
    """

    TEST = False

    ############################
    # initialize snip_bg array #
    ############################

    snip_bg = np.zeros(an_array.shape[0])
    
    ########################
    # square root the data #
    ########################

    sqr_data = an_array**0.5

    ###############################################
    # apply savgol filter to the square root data #
    ###############################################

    if len(args) > 0:
        savgol_window,order = args[0],args[1]
        try: 
            smooth_sqr = savgol_filter(sqr_data,savgol_window,order)
        except:
            raise ValueError
    else: 
        smooth_sqr = savgol_filter(sqr_data,width,3)
    
    for i in range(smooth_sqr.shape[0]): 
        if smooth_sqr[i] < 0: smooth_sqr[i] = 0
    
    ################## NUMBA PRESENTS SERIOUS ISSUES DEPENDING ON VERSION ################
    # THIS SNIPPET WORKS WITH NUMBA 0.42.1 (win10 only) and 0.45.1 (win7 AND win10)      #
    # numba functions do not return an output, the output must be passed as an argument. #
    # in this case, smooth_sqr is CHANGED.                                               #
    ######################################################################################
     
    strip(smooth_sqr,cycles,width)

    ##################################################################################
    # change snip_bg to the transformed smooth_sqr after applying the strip function #
    ##################################################################################

    snip_bg = smooth_sqr[:] 

    ##################
    # transform back #
    ##################

    snip_bg **= 2
       
    if TEST == True:
        plt.semilogy(snip_bg,label="background")
        plt.semilogy(an_array,label="spectrum")
        plt.legend()
        plt.show()

    return snip_bg

def correlate(map1,map2):

    """ Correlates the pixels of two bi-dimensional arrays
    - This function is deprecated and will be replaced in future releases """

    corr_x, corr_y = [],[]
    for x in range(map1.shape[0]):
        for y in range(map2.shape[1]):
            if map1[x][y] > 0 and map2[x][y] > 0:
                corr_x.append(map1[x][y])
                corr_y.append(map2[x][y])
    if corr_x == [] or corr_y == []:
        return
    corr_x, corr_y = np.asarray(corr_x), np.asarray(corr_y)
    return corr_x, corr_y

if __name__=="__main__":
    logger.info("This is SpecMath")

