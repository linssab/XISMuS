#################################################################
#                                                               #
#          SPEC MATHEMATICS                                     #
#                        version: 1.0.0                         #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################
TESTFNC = False

# import utilities
import logging
logging.debug("Importing module SpecMath.py...")
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

# import other modules
import matplotlib.pyplot as plt
logging.debug("Importing numba jit...")
try:
    from numba import jit
except:
    print("Failed to load numba")
logging.debug("Importing module math...")
import math
from math import factorial
logging.info("Finished SpecMath imports.")

from tkinter import *
from tkinter import ttk

NOISE = 80
FANO = 0.114


class Busy:
    
    """ Progress bar class. """
    
    def __init__(__self__,max_,min_):
        __self__.master = Toplevel()
        __self__.master.resizable(False,False)
        __self__.master.overrideredirect(True)
        x = __self__.master.winfo_screenwidth()
        y = __self__.master.winfo_screenheight()
        win_x = __self__.master.winfo_width()
        win_y = __self__.master.winfo_height()
        __self__.master.geometry('{}x{}+{}+{}'.format(166, 49,\
                int((x/2)-80), int((y/2)-23)))
        __self__.outerframe = Frame(__self__.master, bd=3, relief=RIDGE)
        __self__.outerframe.grid(row=0,column=0)
        __self__.master.label = Label(__self__.outerframe, text="Packing spectra...")
        __self__.master.label.grid(row=0,column=0)       
        __self__.master.body = Frame(__self__.outerframe)        
        __self__.master.body.grid(row=1,column=0)
        __self__.progress = ttk.Progressbar(__self__.master.body, orient="horizontal",length=160, mode="determinate",maximum=max_)
        __self__.progress.grid(row=0,column=0)
        __self__.master.grab_set()

    def updatebar(__self__,value):

        """ update bar progress. Value is the progress literal value. The maximum value is 
        defined according to the amount of spectra to be read. """

        __self__.progress["value"] = value
        __self__.progress.update()

    def update_text(__self__,text):

        """ update text displayed on bar """

        __self__.master.label["text"] = text
        __self__.master.update()

    def destroybar(__self__):

        """ Destroys the bar window """

        __self__.master.grab_release()
        __self__.master.destroy()

    def interrupt(__self__,mca,timeout):

        """ In case of read failure, progress is interrupted """

        __self__.progress["maximum"] = timeout
        __self__.updatebar(timeout)
        __self__.update_text("Failed to read mca!")
        for i in range(timeout):
            __self__.updatebar(timeout-i)
            time.sleep(1)
        __self__.destroybar()


class datacube:

    """ Cube class. Comprises all data read from spectra, elemental maps created,
    background extracted (as a separate xy matrix), derived spectra, image size, image
    dimension, datacube configuration, calibrated energy axis """
    
    """
    Methods:
    compile_cube()
    pack_element(image, element_name, line)
    unpack_element(element_name, line)
    check_packed_elements()
    """

    ndim = 0
    
    def __init__(__self__,dtypes,configuration,mode="",name=""):
        if mode == "merge": 
            __self__.name = name
        else:
            __self__.name = configuration["directory"]
        logging.debug("Initializing cube file")
        try: specsize = getdata(getfirstfile()) 
        except: specsize = 0
        __self__.datatypes = \
                np.array(["{0}".format(dtypes[type]) for type in range(len(dtypes))])
        if mode != "merge":
            __self__.dimension = getdimension()
            __self__.img_size = __self__.dimension[0]*__self__.dimension[1]
            __self__.matrix = np.zeros([__self__.dimension[0],__self__.dimension[1],\
                specsize.shape[0]],dtype='float64',order='C')
            __self__.config = configuration
            __self__.calibration = getcalibration()
            __self__.energyaxis = energyaxis()
        __self__.ROI = {}
        __self__.hist = {}
        __self__.max_counts = {}

    def MPS(__self__):

        """ Read all data in datacube.matrix and returns a spectrum where each index
        is the maximum value found in the matrix for that same index.
        MPS stands for Maximum Pixel Spectrum """

        __self__.mps = np.zeros([__self__.matrix.shape[2]],dtype='float64')
        for c in range(__self__.matrix.shape[2]):
            for x in range(__self__.matrix.shape[0]):
                for y in range(__self__.matrix.shape[1]):
                    if __self__.mps[c] < __self__.matrix[x,y,c]: __self__.mps[c] = __self__.matrix[x,y,c]

    def stacksum(__self__):

        """ Reall all data in datacube.matrix and return the summation derived spectrum """

        __self__.sum = np.zeros([__self__.matrix.shape[2]],dtype='float64')
        for x in range(__self__.matrix.shape[0]):
            for y in range(__self__.matrix.shape[1]):
                __self__.sum += __self__.matrix[x,y]
    
    def write_sum(__self__):

        """ Saves the summation derived spectrum as an mca file to disk """

        # import internal variables.
        # they must be imported here in order to be the most recent ones (they are constantly
        # updated by the GUI).
        from SpecRead import output_path, cube_path
        try: os.mkdir(output_path)
        except: pass
        sum_file = open(output_path+'stacksum.mca','w+')
        
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

        ANSII_file = open(output_path+'ANSII_SUM.txt','w+')
        ANSII_file.write("counts\tenergy (KeV)\n")
        for index in range(__self__.sum.shape[0]):
            ANSII_file.write("{0}\t{1}\n".format(
                int(__self__.sum[index]),
                __self__.energyaxis[index]))
        ANSII_file.close()

    def strip_background(__self__,bgstrip=None):

        """ Calculates the background contribution to each invidual spectrum.
        The calculated data is saved into the datacube object.
        bgstrip; a string """

        bgstrip = __self__.config['bgstrip']
        counter = 0
        __self__.background = np.zeros([__self__.dimension[0],__self__.dimension[1],\
                __self__.energyaxis.shape[0]],dtype='float64',order='C')
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
                    __self__.sum_bg += stripped
                    counter = counter + 1
                    __self__.progressbar.updatebar(counter)

    def create_densemap(__self__):

        """ Calls getdensitymap and attributes the 2D-array output to the object """

        __self__.densitymap = getdensitymap(__self__)

    def save_cube(__self__):

        """ Writes (pickle) the datacube object to memory, if the cube already exists, it is
        replaced (updated) """ 

        from SpecRead import output_path, cube_path, samples_folder
        __self__.root = samples_folder
        try: 
            if not os.path.exists(output_path):
                logging.info("Creating outputh path {0}".forma(output_path))
                os.mkdir(output_path)
            else: logging.debug("Output path exists")
        except: 
            logging.warning("Could not create output folder {}".format(output_path))
            pass
        p_output = open(cube_path,'wb')
        pickle.dump(__self__,p_output)
        p_output.close()

    def digest_merge(__self__):
        datacube.MPS(__self__)
        datacube.stacksum(__self__)
        datacube.write_sum(__self__)
        datacube.create_densemap(__self__)
        datacube.save_cube(__self__)

    def compile_cube(__self__):

        """ Iterate over the spectra dataset, reading each spectrum file saving it to the 
        proper xy matrix indexes and calculating the background contribution as well. 
        This method saves all derived spectra, writes summation mca to disk and calculates
        the density map. """

        logging.debug("Started mca compilation")
        __self__.progressbar = Busy(__self__.img_size,0)
        currentspectra = getfirstfile()
        logging.debug("First mca on list: {}".format(currentspectra))
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
        return 0,None
        
    def pack_element(__self__,image,element,line):

        """ Saves elemental distribution image to datacibe object 
        image; a 2d-array
        element; a string
        line; a string """

        from SpecRead import output_path, cube_path
        __self__.__dict__[element+"_"+line] = image
        logging.info("Packed {0} map to datacube {1}".format(element,cube_path))
    
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
        logging.info("Unpacked {0} map from datacube {1}".format(element,cube_path))
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
            __self__.__dict__[element+"_a"] = np.zeros([__self__.dimension[0],__self__.dimension[1]])
            __self__.__dict__[element+"_b"] = np.zeros([__self__.dimension[0],__self__.dimension[1]])
            __self__.ROI[element] = np.zeros([__self__.energyaxis.shape[0]])
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


def function(ydata,x):
    
    """ Returns x index value of ydata array """
    
    return ydata[x]

def dif2(ydata,x,gain):
    
    """ Complementary function to getdif2 """
    
    value = (function(ydata, x + 2*gain) - 2*function(ydata, x + gain)\
            + function(ydata, x)) / (gain * gain)
    return value

def getdif2(ydata,xdata,gain):
    
    """ Returns the second differential of ydata """
    
    xinterval = np.pad(xdata,2,'edge')
    yinterval = np.pad(ydata,2,'edge')
    dif2curve = np.zeros([len(yinterval)])
    for x in range(len(xinterval)-2):
        difvalue = dif2(yinterval,x,1)
        dif2curve[x] = difvalue
    dif2curve = dif2curve[1:-3]
    return dif2curve

def savgol_filter(y, window_size, order, deriv=0, rate=1):
   
    """ This function was taken from https://gist.github.com/krvajal 
    and compared to scipy.signal package, an affidable and renown package
    for signal analysis. """
    """ References
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
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

    """ Calculates sigma value based on energy input (Sole et al., 2007) 
    INPUT:
        energy; electronvolts - eV (int)
    OUTPUT:
        float """

    return math.sqrt(((NOISE/2.3548)**2)+(3.85*FANO*energy))

def gaussianbuilder(channel,energy):

    """ Calculates point in gaussian (Sole et al., 2007) 
    INPUT:
        channel; int
        energy electronvolts - eV (int) 
    OUTPUT:
        float """

    sigma = sigma(energy)
    chEnergy = (channel*GAIN + B)*1000
    A = GAIN/(sigma)*math.sqrt(2*math.pi)
    return A*(math.exp(-(((energy-chEnergy)**2)/(2*(sigma**2)))))

def creategaussian(channels,energy):

    """ Creates a gaussian distribution according to input channel list.
    INPUT:
        channels; 1D-list or int
        energy; electronvolts - eV (int)
    OUTPUT:
        Gaussian; 1D-list """

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
        - indexes corresponding to 2*FWHM of a gaussian centered
        at eV energy position (int, int, int, bool) 
    """
    
    lookup = int(lookup)
    peak_corr = 0
    isapeak = True
    
    if localconfig.get('bgstrip') == 'SNIPBG' and\
    localconfig.get('peakmethod') != 'PyMcaFit': 
        yarray  = savgol_filter(yarray,5,3)
    
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
    logging.debug("peak_center = {0}, channels = {1} {2}, peakwidth= {3}"\
            .format(peak_center,lowx_idx,highx_idx,(highx_idx-lowx_idx))) 
    return lowx_idx,highx_idx,peak_center,isapeak

def getpeakarea(lookup,data,energyaxis,continuum,localconfig,RAW,usedif2,dif2):

    """
    Calculates the netpeak area of a given lookup energy.
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
        idx; list (containing setROI function outputs)
    """

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
            logging.debug("Dif2 is: {0}".format(smooth_dif2[idx[2]]))
            logging.debug("Dif2 left = {0} and Dif2 right = {1}".format(\
                    smooth_dif2[idx[2]-1],smooth_dif2[idx[2]+1]))
            if ROIbg.sum() < ydata.sum(): Area += ydata.sum() - ROIbg.sum()
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
    
    # PyMcaFit method does not check for second differential
    elif localconfig.get('peakmethod') == 'PyMcaFit':
        logging.info("No dif 2 criteria for {0} method".format(localconfig.get('peakmethod')))
        smooth_dif2 = np.zeros([len(xdata)])
        if ROIbg.sum() < ydata.sum(): Area += ydata.sum() - ROIbg.sum()
               
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
    iteractive peak clipping method (van Espen, Chapter 4 in Van Grieken, 2002)
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
    the SNIPBG method described in van Espen, Chapter 4 in Van Grieken, 2002.
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

    #initialize snip_bg array
    snip_bg = np.zeros(an_array.shape[0])

    #square root the data
    sqr_data = an_array**0.5

    #apply savgol filter to the square root data
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
    
    ######### NUMBA PRESENTS SERIOUS ISSUES DEPENDING ON VERSION ########
    ######### THIS SNIPPET WORKS WITH NUMBA 0.42.1 !!!
    # strip peaks
    # numba functions do not return an output, the output must be passed as an argument.
    # in this case, smooth_sqr is CHANGED.
    
    strip(smooth_sqr,cycles,width)
    
    # points snip_bg to the 
    # transformed smooth_sqr after applying the strip function
    snip_bg = smooth_sqr[:] 

    #transform back
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

    correlation_matrix = np.zeros([map1.shape[0],map1.shape[1],2])
    for x in range(map1.shape[0]):
        for y in range(map2.shape[1]):
            correlation_matrix[x][y] = [map1[x][y],map2[x][y]]
    return correlation_matrix

if __name__=="__main__":
    logging.info("This is SpecMath")

