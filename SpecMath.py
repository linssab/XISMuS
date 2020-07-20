#################################################################
#                                                               #
#          SPEC MATHEMATICS                                     #
#                        version: 1.1.0 - Jul - 2020            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################
TESTFNC = False

# import utilities
import logging
import threading
logger = logging.getLogger("logfile")
logger.debug("Importing module SpecMath.py...")
import os, time
import sys
import numpy as np
import pickle
import random

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
lock = threading.Lock()

from tkinter import *
from tkinter import ttk

iterator = 0

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
        spec = os.path.join(Constants.SAMPLE_PATH,
                str(Constants.NAME_STRUCT[0]+str(idx)+"."+Constants.NAME_STRUCT[2]))
        Constants.FILE_POOL.append(spec)

def read_pool(start,end,pool,dimension,m):
    
    """ INPUT:
        - start: int; starting row
        - end: int; lower boundary row
        - pool: list; contains the spectra to be read
        - dimension: int; row length
        - m: np.array (int); spectra matrix """
        
    global iterator
    scan = (start,0)
    x, y = scan[0], scan[1]
    for spec in pool:
        logger.debug("Coordinates: x {}, y {}. Spectra: {}".format(x,y,spec))
        with lock: m[x][y] = getdata(spec)
        scan = refresh_position(scan[0],scan[1],dimension)
        x,y = scan[0],scan[1]
        with lock: iterator += 1

def get_chunks(size):
    max_chunks = Constants.CPUS*2
    bites = int(((size[0]*size[1])/max_chunks)/size[1])
    
    ###################################################################
    # missing lines at the end (cannot fit into more chunks or bites) #
    ###################################################################

    leftovers = size[0]-(bites*max_chunks) 

    ###################################################################

    return max_chunks, bites, leftovers

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

def FN_fit_pseudoinv(specdata,gain):

    """ Finds suitable FANO and NOISE factors to the input spectrum using only 
    the gain and no background.

    --------------------------------------------------------------------------

    INPUT:
        specdata; <1D-array> - spectrum to be used
        gain; <float> - calibration gain (eV)
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
    i, x = 0, 80
    avg_F, avg_N = 0,0
    data = savgol_filter(specdata,5,3)
    w, r = 9,2
    v = (w/2)+1
    while i < x:
        F, N = FN_iter(data,gain,v,w,r)
        if 0.114-(2*0.0114) <= F <= 0.114+(2*0.0114): 
            logger.warning("Fano and Noise matched: F:{} N:{}".format(F,N))
            return F,N
        avg_F += F
        avg_N += N
        r += 1
        if r > 12:
            r = 4
            w += 2
            v = int(w/2)+1
            if w >= 13:
                w = 2
                v = int(w/2)+1
        i += 1
    N = avg_N/i
    F = avg_F/i
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
            break
    j=0
    for j in range(i,i+win):
        if data[j]<=half: 
            up = j-1
            break
    if lw >= up: return 0,0,0
    return lw, up, up-lw

def FN_fit_gaus(spec,spec_bg,e_axis,gain):

    """ Finds a series of relevant peaks between 2100 and 30000 eV and fits them
    with a gaussian fuction to obtain the global Fano and Noise factors.

    ----------------------------------------------------------------------------
    INPUT:
        spec; <1D-array> - global spectrum to be used in the peak sampling and fit
        spec_bg; <1D-array> - continuum of the above spectrum
        e_axis; <1D-array> - calibrated energy axis in KeV
        gain; <float> - calibration gain in KeV
    OUTPU:
        Fano; <float> - Fano factor of the input spectrum
        Noise; <float> - Noise factor of the input spectrum """

    from scipy.optimize import curve_fit
    import copy

    ####################################

    Fano = 0.114
    Noise = 80
    gain = gain*1000
    energyaxis = e_axis*1000
    zero = energyaxis[0]
    y_array, y_cont = spec, spec_bg

    ####################################

    #########################
    # perform deconvolution #
    #########################

    w = Constants.PEAK_TOLERANCE
    v = int(w/2)+1
    r = 2 
    peaks = []
    y_conv, y_delta, pre_peaks = tophat(y_array,v,w)
    for i in pre_peaks:
        if y_conv[i-1]<=y_conv[i]>=y_conv[i+1]: 
            if y_conv[i]>(r*y_delta[i]) and \
                    y_conv[i]>y_cont[i]*Constants.CONTINUUM_SUPPRESSION: 
                peaks.append(i)

    #########################

    ######################################
    # filters peaks and exclude outliers #
    ######################################

    filtered_peaks, E_peaks, y_peaks = [],[],[]
    for i in peaks:
        if 2100<=energyaxis[i]<=30000:
            E_peaks.append(energyaxis[i])
            filtered_peaks.append(i)
            y_peaks.append(y_array[i])

    peaks = np.asarray(filtered_peaks)
    E_peaks = np.asarray(E_peaks) 
    y_peaks = np.asarray(y_peaks)

    ######################################

    guess = y_peaks*np.sqrt(
            (np.square(Noise/2.3548))+(3.85*Noise*E_peaks))*np.sqrt(2*np.pi)/gain
    guess = np.insert(guess,0,[Noise,Fano],axis=0)
    uncertainty = np.sqrt(y_array).clip(1)
    
    popt_gaus, pcov_gaus = curve_fit(lambda x,Noise,Fano,*A: gaus(
            energyaxis,E_peaks,gain,Noise,Fano,
                *A) + y_cont,
            energyaxis,
            y_array,
            p0=guess,
            sigma=uncertainty,
            maxfev=Constants.FIT_CYCLES)

    #print(popt_gaus.shape)
    #print("NOISE",popt_gaus[0])
    #print("FANO",popt_gaus[1])

    #y_gaus = np.asarray(
    #        [gaus(energyaxis,E_peaks[i],gain,*popt_gaus[[0,1,2+i]]) \
    #                for i in range(E_peaks.size)])+ y_cont
    #for i in y_gaus:
    #    plt.semilogy(energyaxis,i,label="Fit")
    #plt.semilogy(energyaxis,y_array,label="Data")
    #plt.semilogy(energyaxis,y_cont,label="Continuum")
    #plt.legend()
    #plt.show()

    return popt_gaus[1], popt_gaus[0]

def batch_continuum_for_wizard(
        spectra_batch,
        bgstrip=None,
        bgparams=(24,5,5,3),
        bar=None,
        global_spectrum=None):

    """ Used to fit a batch of spectra for auto_wizard method. Auto wizard requires
    the data to be filtered, otherwise the peak detection and gaussian fit performs
    very poorly. For tis reason, the continuum matrix must be recalculated everytime
    the wizard is invoked. This avoid harming the data. The RAW data remains always
    untouched in the datacube after fitting the data with auto wizard. """

    continuum = np.zeros([spectra_batch.shape[0],spectra_batch.shape[1]],dtype="float32")
    global_continuum = np.zeros([spectra_batch.shape[1]],dtype="float32")

    if bgstrip == "None":
        return continuum, global_continuum

    elif bgstrip == "SNIPBG":
        try: cycles, window, savgol, order = bgparams
        except: cycles, window, savgol, order = 24,5,5,3
        for i in range(spectra_batch.shape[0]):
            if bar!= None: bar.updatebar(i)
            stripped = peakstrip(spectra_batch[i],cycles,window,savgol,order)
            continuum[i] = stripped
        global_continuum = peakstrip(global_spectrum,cycles,window,savgol,order)
        return continuum, global_continuum

    elif bgstrip == "Polynomial":
        ndegree_global, ndegree_single, r_fact = 6,0,2
        attempt = 0
        while continuum.sum()==0:
            attempt += 1
            continuum = polfit_batch(
                spectra_batch,
                ndegree_global=ndegree_global,
                ndegree_single=ndegree_single,
                r=r_fact,
                custom_global_spec=global_spectrum)
            r_fact+=1
        for i in range(spectra_batch.shape[0]):
            if i: continuum[i] = continuum[i]
            else: global_continuum = continuum[i]
            if bar!= None: bar.updatebar(i)
        return continuum, global_continuum


class datacube:

    """ Cube class. Comprises all data read from spectra, elemental maps created,
    background extracted (as a separate xy matrix), derived spectra, image size, image
    dimension, datacube configuration, calibrated energy axis """

    ndim = 0
    
    def __init__(__self__,dtypes,configuration,mode="",name=""):
        if mode == "merge": 
            __self__.name = name
            __self__.path = name
        else:
            from Constants import SAMPLE_PATH
            __self__.name = configuration["directory"]
            __self__.path = SAMPLE_PATH
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
        for x in range(__self__.matrix.shape[0]):
            for y in range(__self__.matrix.shape[1]):
                __self__.sum += __self__.matrix[x,y]

    def fit_fano_and_noise(__self__):
        __self__.FN = FN_fit_gaus(__self__.sum,
                __self__.sum_bg,
                __self__.energyaxis,
                __self__.gain)

    def flush_spectra(__self__,path):
        print("Flushing data to {}".format(path))
        try: os.makedirs(path)
        except: 
            print("Path {} exists.".format(path))
            print("Do you want to overwrite the data? (Y/N)")
            proceed = input()
            if proceed == "Y" or proceed == "y":
                shutil.rmtree(path)
                try: os.makedirs(path)
                except: 
                    print("Failed to create new directory. Aborting...")
                    sys.exit(1)
            else:  
                print("Aborted by user.")
                sys.exit(1)
        iterator = 1
        name = "Spec_"
        for i in range(__self__.matrix.shape[0]):
            for j in range(__self__.matrix.shape[1]):
                spec = open(os.path.join(path,name+str(iterator)+".txt"),"+w")
                spec.write(
            "<<PMCA SPECTRUM>>\nTAG - TAG\nDESCRIPTION - Piratininga SM Sum Spectrum\n")
                spec.write("GAIN - 2\nTHRESHOLD - 0\nLIVE_MODE - 0\nPRESET_TIME - OFF\n")
                spec.write("LIVE_TIME - 0\nREAL_TIME - 0\nSTART_TIME - {}\n".format(
                    time.strftime("%Y-%m-%d %H:%M:%S",
                        time.gmtime())))
                spec.write("SERIAL_NUMBER - 00001\n<<CALIBRATION>>\nLABEL - Channel\n")
                for pair in __self__.calibration:
                    spec.write("{0} {1}\n".format(pair[0],pair[1]))
                spec.write("<<DATA>>\n")
                for c in __self__.matrix[i][j]:
                    spec.write("{}\n".format(int(c)))
                spec.write("<<END>>")
                spec.close()
                iterator += 1
                percent = iterator/__self__.img_size*100
                print("{:0.2f} percent complete...".format(percent),end="\r")
    
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
        
        if recalculating == True: 
            bgstrip = bgstrip
            progressbar = progressbar
        else: 
            bgstrip = __self__.config['bgstrip']
            progressbar = __self__.progressbar
        counter = 0
        
        ##########################
        # initialize empty array #
        ##########################

        __self__.background = np.zeros([__self__.dimension[0],__self__.dimension[1],
                __self__.matrix.shape[2]],dtype="float32",order='C')
        __self__.sum_bg = np.zeros([__self__.matrix.shape[2]])

        ##########################
       
        if bgstrip == "SNIPBG":
            progressbar.update_text("Calculating SNIPBG")
            try: cycles, window,savgol,order= __self__.config["bg_settings"] 
            except: cycles, window, savgol, order = 24,5,5,3
            for x in range(__self__.matrix.shape[0]):
                for y in range(__self__.matrix.shape[1]):
                    # default cycle and sampling window = 24,5
                    stripped = peakstrip(__self__.matrix[x,y],cycles,window,savgol,order)
                    __self__.background[x,y] = stripped
                    counter = counter + 1
                    progressbar.updatebar(counter)
            __self__.sum_bg = peakstrip(__self__.sum,cycles,window,savgol,order)

        elif bgstrip == "Polynomial":
            try: ndegree_global, ndegree_single, r_fact, =  __self__.config["bg_settings"]
            except: ndegree_global, ndegree_single, r_fact = 6,0,2
            matrix_flatten = __self__.matrix.reshape(-1,__self__.matrix.shape[-1])
            
            y_cont, attempt = np.zeros([__self__.matrix.shape[2]]), 0
            progressbar.update_text(
                    "Fitting continuum. Trial: {}".format(attempt))
            while y_cont.sum()==0:
                attempt += 1
                y_cont = polfit_batch(
                    matrix_flatten,
                    ndegree_global=ndegree_global,
                    ndegree_single=ndegree_single,
                    r=r_fact)
                progressbar.update_text(
                        "Fitting continuum. Trial: {}".format(attempt))
                logger.warning(
                "Attempt {} to fit continuum. Too slow, increasing R factor".format(
                            attempt))
                r_fact+=1

            __self__.sum_bg = y_cont[0]
            for x in range(__self__.matrix.shape[0]):
                for y in range(__self__.matrix.shape[1]):
                    counter += 1 #ignores first continuum which is the global one
                    __self__.background[x][y] = y_cont[counter]
                    progressbar.updatebar(counter)
            del y_cont

        return

    def create_densemap(__self__):

        """ Calls getdensitymap and attributes the 2D-array output to the object """

        __self__.densitymap = getdensitymap(__self__)

    def save_cube(__self__):

        """ Writes (pickle) the datacube object to memory, if the cube already exists, it is
        replaced (updated) """ 

        from SpecRead import output_path, cube_path
        __self__.self_path = cube_path
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
            bar.progress["maximum"] = 6
            bar.updatebar(1)
            bar.update_text("1/6 Calculating MPS...")
        mps = np.zeros([__self__.matrix.shape[2]],dtype="int32")
        __self__.MPS(mps)
        __self__.mps = mps
        if bar != None: 
            bar.update_text("2/6 Calculating Stacksum...")
            bar.updatebar(2)
        __self__.stacksum()
        __self__.write_sum()
        if bar != None:
            bar.update_text("3/6 Creating densemap...")
            bar.updatebar(3)
        __self__.create_densemap()
        if bar != None:
            bar.update_text("4/6 Calculating continuum...")
            bar.updatebar(4)
        __self__.strip_background(
                recalculating=True,
                bgstrip=__self__.config["bgstrip"],
                progressbar=bar)
        if bar != None:
            bar.update_text("5/6 Finding Fano and Noise...")
            bar.updatebar(5)
        __self__.fit_fano_and_noise()
        if bar != None:
            bar.update_text("6/6 Writing to disk...")
            bar.updatebar(6)
        __self__.save_cube()

    def compile_cube(__self__):

        """ Iterate over the spectra dataset, reading each spectrum file saving it to the 
        proper xy matrix indexes and calculating the background contribution as well. 
        This method saves all derived spectra, writes summation mca to disk and calculates
        the density map. """

        global iterator
        iterator = 0

        logger.debug("Started mca compilation")
        timer = time.time()
        __self__.progressbar = Busy(__self__.img_size,0)
        x,y,scan = 0,0,(0,0)
        if not isinstance(Constants.FILE_POOL,tuple):
            build_pool(__self__.img_size)
        else: pass
        
        chunks, bite, leftovers = get_chunks(__self__.dimension)
        if Constants.CPUS > 1 and bite > 4:
            running_chunks = []
            for chunk in range(chunks):
                
                ############################
                # matrix iteration indexes #
                ############################

                start = (chunk*bite)
                end = start+bite

                ############################

                ################
                # pool indexes #
                ################

                a = (bite*__self__.dimension[1])*chunk
                b = a+(bite*__self__.dimension[1])

                ################

                pool_chunk = Constants.FILE_POOL[a:b]

                t = threading.Thread(target=read_pool, 
                        args=(start,
                            end,
                            pool_chunk,
                            __self__.dimension,
                            __self__.matrix,))
                running_chunks.append(t)
                logger.info("Polling chunk {}. Leftovers: {}".format(chunk,leftovers))

            if leftovers > 0:

                start = (__self__.dimension[0]-leftovers)
                end = __self__.dimension[0]
                a = (__self__.img_size - (leftovers*__self__.dimension[1]))
                pool_chunk = Constants.FILE_POOL[a:]
                t = threading.Thread(target=read_pool, 
                        args=(start,
                            end,
                            pool_chunk,
                            __self__.dimension,
                            __self__.matrix,))
                running_chunks.append(t)
                logger.info("Polling Leftovers")

            for thread in running_chunks:
                thread.start()

            __self__.periodic_check()

            for thread in running_chunks:
                thread.join()

        else:
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
                __self__.progressbar.updatebar(iterator)
                iterator += 1
        logger.info("Packed spectra in {} seconds".format(time.time()-timer))


        logger.debug("Calculating MPS...")
        __self__.progressbar.update_text("Calculating MPS...")
        mps = np.zeros([__self__.matrix.shape[2]],dtype="int32")
        datacube.MPS(__self__,mps)
        __self__.mps = mps

        logger.debug("Calculating summation spectrum...")
        __self__.progressbar.update_text("Calculating sum spec...")
        datacube.stacksum(__self__)
        #datacube.cut_zeros(__self__)
        __self__.energyaxis, __self__.gain, __self__.zero = calibrate()
        __self__.config["gain"] = __self__.gain
        
        logger.debug("Stripping background...")
        __self__.progressbar.update_text("Stripping background...")
        datacube.strip_background(__self__)
        
        logger.debug("Calculating sum map...")
        __self__.progressbar.update_text("Calculating sum map...")
        datacube.create_densemap(__self__)
        
        logger.debug("Writing summation mca and ANSII files...")
        datacube.write_sum(__self__)

        __self__.progressbar.update_text("Finding Noise and Fano...")
        datacube.fit_fano_and_noise(__self__)

        logger.debug("Saving cube file to disk...")
        __self__.progressbar.update_text("Writing to disk...")
        __self__.progressbar.destroybar()
        del __self__.progressbar 
        datacube.save_cube(__self__)
        logger.debug("Finished packing.")
        return 0,None

    def periodic_check(__self__):
        __self__.check()

    def check(__self__):
        global iterator
        __self__.progressbar.update_text("Packing spectra...")
        while iterator < __self__.img_size:
            __self__.progressbar.updatebar(iterator)
        return 0

    def cut_zeros(__self__):
        
        """ Sliced the data cutting off the necessary lead and tail zeros.
        Lead and tail are verified through the sum spectrum to avoid data loss """

        lead_zeros, tail_zeros = 0,__self__.matrix.shape[2]
        for i in range(__self__.sum.shape[0]):
            if __self__.sum[i] < __self__.img_size:
                lead_zeros = i
            else: break
        for i in range(1,__self__.sum.shape[0]):
            if __self__.sum[-i] < __self__.img_size:
                tail_zeros = __self__.matrix.shape[2]-i
            else: break
        
        print("lead",lead_zeros,"tail",tail_zeros)

        __self__.energyaxis, __self__.gain, __self__.zero = calibrate(
                lead=lead_zeros,tail=__self__.matrix.shape[2]-tail_zeros)
        __self__.config["gain"] = __self__.gain
    
        __self__.matrix = __self__.matrix[:,:,lead_zeros:tail_zeros]
        __self__.background = __self__.background[:,:,lead_zeros:tail_zeros]
        __self__.sum = __self__.sum[lead_zeros:tail_zeros]
        __self__.sum_bg = __self__.sum_bg[lead_zeros:tail_zeros]
        __self__.mps = __self__.mps[lead_zeros:tail_zeros]
        
        print(len(__self__.sum),"sum")
        print(len(__self__.sum_bg),"sum_bg")
        print(len(__self__.mps),"mps")
        print(len(__self__.energyaxis),"energy")
        return lead_zeros, tail_zeros

        
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

    def prepack_elements(__self__,element_list,wipe=False):

        """ Allocates keys in the datacube object to store the elemental distribution maps """
        for element in set(element_list):

            if wipe == False:
                __self__.__dict__[element+"_a"] = np.zeros([__self__.dimension[0],
                    __self__.dimension[1]],dtype="float32")
                __self__.__dict__[element+"_b"] = np.zeros([__self__.dimension[0],
                    __self__.dimension[1]],dtype="float32")
                __self__.ROI[element] = np.zeros([__self__.energyaxis.shape[0]],
                        dtype="float32")
                __self__.max_counts[element+"_a"] = 0
                __self__.max_counts[element+"_b"] = 0
                __self__.hist[element] = [np.zeros([__self__.img_size]),np.zeros([LEVELS])]
            __self__.__dict__["custom"] = np.zeros(
                    [__self__.dimension[0],__self__.dimension[1]],dtype="float32")

            if wipe == True: 
                try: del __self__.__dict__[element+"_a"]
                except KeyError: print("No alpha map for {}".format(element))
                try: del __self__.__dict__[element+"_b"]
                except KeyError: print("No beta map for {}".format(element))
        if wipe == True:
            __self__.max_counts = {}
            __self__.hist = {}
            __self__.ROI = {}
            try: del __self__.__dict__["custom"]
            except KeyError: pass

    def wipe_maps(__self__):
        element_list = [i.split("_")[0] for i in __self__.check_packed_elements()]
        __self__.prepack_elements(element_list,wipe=True)
        __self__.save_cube()
    
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
    if currentx > imagex:
        currentx = 0
    if currenty > imagey:
        currenty = 0
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

def sigma(energy,F=Constants.FANO,N=Constants.NOISE):

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

    return np.sqrt(((N/2.3548)**2)+(3.85*F*energy))

def gaussianbuilder(E_axis,energy,A,F,N):

    """ Deprecated, to be removed in future updates.
    
    ---------------------------------------------------------------------

    INPUT:
        E_axis; energy axis - electronvolts (1D-array)
        energy; peak energies - electronvolts (1D-array)
        A; fitted peak amplitudes (1D-array) """

    gaus = np.zeros([energy.shape[0],E_axis.shape[0]],dtype="float32")
    for i in range(energy.shape[0]):
        s = sigma(energy[i],F,N)
        for j in range(E_axis.shape[0]):
            gaus[i][j]=A[i]*(math.exp(-(((E_axis[j]-energy[i])**2)/(2*(s**2)))))
    return gaus

def setROI(lookup,xarray,yarray,localconfig,tolerance=Constants.SETROI_TOLERANCE):
    
    """
    INPUT: 
        lookup; <int> - eV energy of peak being searched for
        xarray; <np.array> - energyaxis in KeV
        yarray; <np.array> - counts
        localconfig; <dict> - configuration parameters
        tolerance; <optional> 1D-array - tolerance indexes
    OUTPUT: 
        low_idx; <int>
        high_idx; <int>
        peak_center; <int>
        isapeak; <bool>
    
    - indexes correspond to 2*FWHM of a gaussian centered
    at eV energy position (int, int, int, bool) 
    """
   
    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]
    
    def shift_center(xarray,yarray):
        ymax = yarray.max()
        idx = np.where(yarray==ymax)[0][0]
        return xarray[idx],ymax,idx

    lookup = int(lookup)
    if lookup < 4800: w_tolerance = tolerance[0]
    elif lookup > 12000: w_tolerance = tolerance[1]
    else: w_tolerance = tolerance[2]
    peak_corr = 0
    peak_center = 0
    shift = [0,0,0]
    isapeak = True
    idx, lowx_idx, highx_idx = 0,0,0
    
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

        try:
            idx = np.where(xarray==find_nearest(xarray,lookup/1000))[0][0]
            lowx_idx = np.where(xarray==find_nearest(xarray,lowx))[0][0]
            highx_idx = np.where(xarray==find_nearest(xarray,highx))[0][0]
        except:
            logger.debug("ROI error. Index out of bounds.")
            return 0,2,1,False
        logger.debug("{}, {}".format(lowx_idx,highx_idx))
        logger.debug("Closest peak index: {}; Value (KeV): {}".format(idx,xarray[idx]))
            
        ROIaxis = xarray[lowx_idx:highx_idx]
        ROIdata = yarray[lowx_idx:highx_idx]
        
        # skipped at first run, since shift is [0,0,0]
        if shift[0]*1000-lookup == 0: 
            lw,hi = lowx_idx, highx_idx
            try: 
                peak_center, = np.where((ROIaxis == shift[0]))[0]
            except: return 0,2,1,False
            break
        
        shift = shift_center(ROIaxis,ROIdata)
        logger.debug("Shift: {0}".format(shift))
       
        ##########################################
        # verify the distance from a higher peak #
        ##########################################

        difference = abs((shift[0])-xarray[idx])*1000
        logger.debug("DIFFERENCE: {}, Tolerable: {}. Peak is at: {}".format(
            int(difference),
            int((w_tolerance)*localconfig["gain"]*1000),
            shift[0]))
        if int(difference) <= int((w_tolerance)*localconfig["gain"]*1000):
            logger.debug("Shift - lookup = {0}!".format(difference))
            logger.debug("GAP IS LESSER THAN {0}!".format((
                w_tolerance)*localconfig["gain"]*1000))
            peak_center = shift[2]
            peak_corr += 1
            lookup = shift[0]*1000
            if peak_corr == 2:
                lowx_idx = np.where(xarray==find_nearest(xarray,lowx))[0][0]
                highx_idx = np.where(xarray==find_nearest(xarray,highx))[0][0]
                ROIaxis = xarray[lowx_idx:highx_idx]
                ROIdata = yarray[lowx_idx:highx_idx]
        
            lw, hi = lowx_idx, highx_idx
        else: 
            logger.debug("Difference is too large: {0}".format((shift[0]*1000)-lookup))
            
            ############################################################
            # if peak_corr = 0 here, shift failed in the first attempt #
            ############################################################

            if peak_corr == 0: 
                isapeak = False
                lw, hi = lowx_idx, highx_idx
            logger.debug("Failed at first for energy: {}".format(lookup))
            return lw,hi,peak_center,isapeak
        
        logger.debug("ROI[0] = {0}, ROI[-1] = {1}".format(ROIaxis[0],ROIaxis[-1]))
    
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
        if ydata.sum() - ROIbg.sum() < 3*math.sqrt(abs(ROIbg.sum())): isapeak = False
    
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
        print("ydata = {0}".format(ydata))
        print("len(ydata) = {0}".format(len(ydata)))
        try: print("ydata[idx[2]] = {0}, smooth_dif2[idx[2]] = {1}".format(\
                ydata[idx[2]],smooth_dif2[idx[2]]))
        except: pass
        print("idx[2] = {0}".format(idx[2]))
        print("Lookup: {0} Area(DATA_PEAK - BG): {1}\n".format(lookup,Area))
    
        plt.plot(xdata,ydata, label='data')
        try: plt.plot(xdata,smooth_dif2, label='2nd Differential')
        except: pass
        #plt.plot(xdata,ROIbg, label='BG estimation')
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

def polfit_batch(spectra_batch,ndegree_global=6,ndegree_single=0,r=2,
        custom_global_spec=None):

    """ Calculates the continuum following a polynomial fitting function for the entire
    dataset and the summation derived spectrum. A custom summation spectrum can be passed
    instead, as in the case of find_and_fit function in BatchFitter.py. There, for finding
    the peaks, the summation spectrum is calculated for the savgol filtered dataset, 
    clipping values lower than 1.

    -------------------------------------------------------------------------------------    
    
    INPUT:
        spectra_batch; <2D-array> - contains all dataset (shape is: no. os spectra,channels)
        ndegree_global; <int> - polynomial function degree to fit summation spectrum continuum
        ndegree_single; <int> - polynomial degree to find the continuum of all other spectra
        r; <int> - adjustable parameter used for weights
    OUTPUT:
        y_cont_global; <2D-array> - Continuum of global and single spectra
    """
     
    if isinstance(custom_global_spec,np.ndarray):
        spectra_batch = np.insert(
            spectra_batch,
            0,
            custom_global_spec,
            axis=0) 
    else:
        spectra_batch=np.concatenate(
            (np.sum(spectra_batch,0)[None,:],
                spectra_batch),
            axis=0)   

    #####################################################
    # Create list of ndegree settings to enumerate over #
    #####################################################

    ndegree=[ndegree_global,ndegree_single] 

    #####################################################

    ##################################################################################    
    #Create empty numpy array representing final y_cont size including y_cont global #
    ##################################################################################    

    y_cont_global=np.empty((0,spectra_batch.shape[1])) 

    ##################################################################################    

    timeout=0.5
    for it,spectra_batch in enumerate([spectra_batch[[0]],spectra_batch[1:]]): 
        start=time.time()

        if ndegree[it]==0:
            y_cont=np.zeros(spectra_batch.shape)

        else:
            #"Shape every first axis represents new spectrum"
            x = np.arange(spectra_batch.shape[1])
            y_cont = np.zeros(spectra_batch.shape)

            #########################################################
            # Make space +1 for recurrence relation, with gamma[-1] # 
            # unchanging starting point                             #
            #########################################################

            gamma = np.zeros((len(spectra_batch),ndegree[it]+1)) 

            #########################################################

            gamma[:,-1] = 1  # Last digit gammma remains unchanged
            a,b,c_prev,c,sc = (np.zeros((len(spectra_batch),ndegree[it])) for _ in range(5))
            p = np.zeros((len(spectra_batch),ndegree[it]+1,spectra_batch.shape[1]))
            w=np.zeros(spectra_batch.shape)
            iteration=0

            while np.any(np.abs(c_prev-c)>=sc):
                w[y_cont <= 0] = 1/spectra_batch[y_cont <= 0].clip(1)
                
                ########################################################################
                # Negative y_cont can be now clipped to zero for next sqrt calculation #
                ########################################################################

                y_cont[y_cont<=0]=0 

                ########################################################################

                w[(y_cont > 0) & (spectra_batch<=(y_cont+r*np.sqrt(y_cont)))] = \
                        1/y_cont[(y_cont > 0) & (spectra_batch<=(y_cont+r*np.sqrt(y_cont)))]
                w[(y_cont > 0) & (spectra_batch>(y_cont+r*np.sqrt(y_cont)))] = \
                        1/np.square(spectra_batch[(y_cont > 0) & \
                        (spectra_batch>(y_cont+r*np.sqrt(y_cont)))]-y_cont[(y_cont > 0) & \
                        (spectra_batch>(y_cont+r*np.sqrt(y_cont)))])

                len_cont = np.count_nonzero((y_cont>0) & \
                        (spectra_batch<=(y_cont+r*np.sqrt(y_cont)))|(y_cont<=0),axis=1)
                p[:,0,:] = 1
                p[:,-1,:] = 0

                #######################################################################
                # Make deep ndarray copy in order to compare previous to new c-values #
                #######################################################################

                c_prev = c.copy()  

                #######################################################################

                #################################################################
                # Significance new c needs to be tested two tail because        #
                # can be smaller or bigger than 0; Then test for 2sigma         #
                # so 95% conficence, meaning alpha=0.05/5% significance level   #
                # having C bigger than 0 (=null hypothesis). If not fullfilled  #
                # C not significantly bigger than 0!                            #
                #################################################################
                
                for j in range(ndegree[it]): #Determining coefficients for ndegree
                    gamma[:,j]=np.sum(w*p[:,j,:]*p[:,j,:]) #Sum of normalization
                    a[:,j]=np.sum(w*x*p[:,j,:]*p[:,j,:])/gamma[:,j]
                    b[:,j]=np.sum(w*x*p[:,j,:]*p[:,j-1,:])/gamma[:,j-1]

                    c[:,j]=np.sum(w*spectra_batch*p[:,j,:])/gamma[:,j]
                    sc[:,j]=np.sqrt(1/gamma[:,j]) #Standard deviation coefficients

                    p[:,j+1,:]=(x-a[:,[j]])*p[:,j,:]-b[:,[j]]*p[:,j-1,:]
                    

                #################################################################

                #################################################################
                # Matrix multiplication using @ operator with c having on first #
                # axis representing each spectrum similar to p + change to 2d   #
                # array / remain 2d array by squeezing axis=1                   #
                #################################################################

                y_cont=np.squeeze(c[:,None]@p[:,:-1,:],axis=1) 

                #################################################################

                rchisq = np.sum(w*np.square(spectra_batch-y_cont))/(len_cont-ndegree[it])

                #################################################################
                # Actual sd must be element-wise multiplied by chi since error  #
                # data points unkown, so np.sqrt(rchisq) represents overall     #
                # error data points sigma(i)=sigma                              #
                #################################################################
                
                sc=np.sqrt(rchisq)[:,None]*sc 

                #################################################################

                iteration += 1
                if time.time()-start > timeout: return np.zeros([spectra_batch.shape[1]])
                
            logger.info("Iterations polynomial to overall converge: {}".format(iteration))

        ########################################################################
        # Concatenate continuum global spectrum with continuum single spectra  #
        # to empty y_cont_global                                               #
        ########################################################################

        y_cont_global=np.concatenate((y_cont_global,y_cont),0)

        ########################################################################

    return y_cont_global

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

def findpeaks(spectrum,v=4,w=9,r=1):
    y,var,indexes = tophat(spectrum,v,w)
    selected_peaks = []
    for i in indexes:
        if y[i]>r*var[i]:
            selected_peaks.append(i)
    plt.semilogy(spectrum)
    plt.semilogy(y,color="green")
    plt.semilogy(var,color="tomato")
    for idx in indexes:
        plt.axvline(x=idx)
    plt.show()
    return selected_peaks

def gaus(x, E_peak, gain, Noise, Fano, *A):

    """ Model function to be fitted.

    ---------------------------------------------

    INPUT:
        x; <1D-array> - contains the calibrated energy axis
        E_peak; <1D-array> - contains the energy where peaks where found 
        gain; <float> - energy gain per channel in electronvolts
        Noise; <float> - Noise factor
        Fano; <float> - Fano factor
        A; <1D-array> - Gaussian amplitude array """

    s = np.sqrt(np.square(Noise/(2*np.sqrt(2*np.log(2))))+3.85*Fano*E_peak)
    return gain*np.sum(
            A/(s*np.sqrt(2*np.pi))*np.exp(-np.square(x[:,None]-E_peak)/(2*np.square(s))),1)


if __name__=="__main__":
    logger.info("This is SpecMath")
    import Constants
    _path_ = r"C:\Users\sergi\Documents\XISMuS\output\Training Data 2\Training Data 2.cube"
    cube_file = open(_path_,'rb')
    Constants.MY_DATACUBE = pickle.load(cube_file)
    cube_file.close()
    data = Constants.MY_DATACUBE.sum
    e_axis = Constants.MY_DATACUBE.energyaxis
    #getpeakarea(6441,data,Constants.MY_DATACUBE.energyaxis,
    #        Constants.MY_DATACUBE.background,
    #        Constants.MY_DATACUBE.config,True,
    #        np.zeros([Constants.MY_DATACUBE.matrix.shape[2]]))

