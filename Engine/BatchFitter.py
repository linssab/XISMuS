"""
Copyright (c) 2020 Sergio Augusto Barcellos Lins & Giovanni Ettore Gigante

The example data distributed together with XISMuS was kindly provided by
Giovanni Ettore Gigante and Roberto Cesareo. It is intelectual property of 
the universities "La Sapienza" University of Rome and Università degli studi di
Sassari. Please do not publish, commercialize or distribute this data alone
without any prior authorization.

This software is distrubuted with an MIT license.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Credits:
Few of the icons used in the software were obtained under a Creative Commons 
Attribution-No Derivative Works 3.0 Unported License (http://creativecommons.org/licenses/by-nd/3.0/) 
from the Icon Archive website (http://www.iconarchive.com).
XISMuS source-code can be found at https://github.com/linssab/XISMuS
"""

#############
# Utilities #
#############
import logging
import gc
import sys, os, multiprocessing, copy, pickle
from multiprocessing import freeze_support
lock = multiprocessing.Lock()
freeze_support()
from psutil import cpu_count
import numpy as np
import time,timeit
import threading
#############

#################
# Local imports #
#################
import Constants
Constants.LOGGER.info("In BatchFitter: Importing local modules...")
import Elements
from . import SpecRead
from . import SpecMath 
from . import ImgMath
from GUI.ProgressBar import Busy
#################

####################
# External modules #
####################
from matplotlib.figure import Figure
from matplotlib.figure import figaspect
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
try:
    import xraylib as xlib
    xlib.SetErrorMessages(0)
except: 
    Constants.LOGGER.warning("xraylib module not found!")
    print("FAILED TO LOAD XRAYLIB MODULE\nCannot run module BatchFitter.py")
####################

def convert_bytes(num):
    """ Obtained from https://stackoverflow.com/questions/210408 """

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def prepare_data(FitClass):
    global progress
    progress = 0
    FitClass.bar.KILL = 0

    threads = []
    cpus = cpu_count() #NOTE: includes logical cores
    lock = threading.Lock()

    if cpus == 1:
        bite_size = int(FitClass.counts.shape[0])
        leftovers = 0
        print("Only one core")
        Constants.LOGGER.warning("Sample is too small, running with one core only...")
    else:
        bite_size = 0
        while bite_size < 400:
            bite_size = int(FitClass.counts.shape[0]/cpus)
            leftovers = int(FitClass.counts.shape[0]%cpus)
            print("bite size: ",bite_size,"leftovers ",leftovers)
            cpus -= 1
            if bite_size == FitClass.counts.shape[0]: break
        cpus += 1
        bite_size = bite_size
        leftovers = leftovers

    global kill
    kill = 0
    def filter_specs(spec_arr, bar, lock):
        global progress
        global kill
        for i in range(spec_arr.shape[0]):
            if kill: 
                print("Thread killed")
                return 0
            with lock: 
                spec_arr[i] = SpecMath.savgol_filter(spec_arr[i],5,3).clip(0)
                progress += 1
        return
    
    def check(bar, lim):
        global progress
        global kill
        try: 
            while progress < lim: 
                bar.updatebar(progress)
        except: 
            kill = 1
        return

    spec = 0
    for k in range(cpus):
        chunk0 = k*bite_size
        chunk1 = chunk0+bite_size
        t = threading.Thread(target=filter_specs, 
                args=(FitClass.counts[chunk0:chunk1], 
                    FitClass.bar, lock))
        threads.append(t)
        for i in range(bite_size):
            spec += 1
    if leftovers >= 1:
        for i in range(leftovers):
            FitClass.counts[spec] = SpecMath.savgol_filter(
                    FitClass.counts[spec],5,3).clip(0)
            spec += 1

    #for i in range(len(FitClass.counts)):
    #    FitClass.bar.updatebar(i)
    #    FitClass.counts[i] = SpecMath.savgol_filter(
    #            FitClass.counts[i],5,3).clip(0)

    progress += leftovers
    for t in threads:
        t.start()
    FitClass.bar.add_cancel_btn()
    check(FitClass.bar, FitClass.counts.shape[0])
    for t in threads:
        t.join()

    FitClass.SUM = np.sum(FitClass.counts.clip(1),0)
    FitClass.global_continuum = batch_continuum_for_wizard(
            FitClass.counts,
            bgstrip=Constants.MY_DATACUBE.config["bgstrip"],
            bgparams=Constants.MY_DATACUBE.config["bg_settings"],
            bar=FitClass.bar,
            global_spectrum=FitClass.SUM)
    return 0

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
    # NOTE: Commented lines were used in previous versions to recalculate the 
    # entire continuum array. Since the SavGol filter doesn't alter significantly
    # the spectra, recalculating tenths of thousands of continuums is a waste of time.

    #continuum = np.zeros([spectra_batch.shape[0],spectra_batch.shape[1]],dtype="float32")

    global_continuum = np.zeros([spectra_batch.shape[1]],dtype="float32")

    if bgstrip == "None":
        #return continuum, global_continuum
        return global_continuum

    elif bgstrip == "SNIPBG":
        try: cycles, window, savgol, order = bgparams
        except: cycles, window, savgol, order = 24,5,5,3
        #for i in range(spectra_batch.shape[0]):
        #    if bar!= None: bar.updatebar(i)
        #    stripped = SpecMath.peakstrip(spectra_batch[i],cycles,window,savgol,order)
        #    continuum[i] = stripped
        global_continuum = SpecMath.peakstrip(global_spectrum,cycles,window,savgol,order)
        #return continuum, global_continuum
        return global_continuum

    elif bgstrip == "Polynomial":
        ndegree_global, ndegree_single, r_fact = 6,0,2
        attempt = 0
        while global_continuum.sum()==0:
            attempt += 1
            global_continuum = SpecMath.polfit_batch(
                #spectra_batch,
                np.asarray([global_spectrum]),
                ndegree_global=ndegree_global,
                ndegree_single=ndegree_single,
                r=r_fact,
                custom_global_spec=global_spectrum)[0]
            r_fact+=1
        #for i in range(spectra_batch.shape[0]):
        #    if i: continuum[i] = continuum[i]
        #    else: global_continuum = continuum[i]
        #    if bar!= None: bar.updatebar(i)
        #return continuum, global_continuum
        return global_continuum

def save_plot(
        x,                  #Energy axis
        Y_DATA,             #Smoothed spectrum
        Y_CONT,             #Continuum
        y_gaus_single,      #Array with single fitted peaks
        y_gaus,             #Fitted spectrum
        rchisq_gaus,        #Chi-squared error
        residuals_gaus,     #Fit residuals
        Z_dict,             #Dictionary with elements
        E_peak,             #Peaks energies
        y_peak,             #Peaks positions
        figures_path, it,    #Save path and iterator number
        SCALE
        ):

    ############################
    element = [*Z_dict][:-1] #To be plotted elements
    color=plt.cm.jet(np.linspace(0,1,len(element))) #Create fixed color for specific element
    ########################################
    # Get duplicate values from dictionary #
    ########################################
    seen=set() #Define set of all values seen so far in set comprehension
    dupl_value=set(int(x) for x in [value for sublist in Z_dict.values() \
            for value in sublist] if x in seen or seen.add(x))
    ########################################

    #######################################################
    # Get corresponding duplicate keys and reversely sort #
    #######################################################
    un_ = Z_dict["Unmatched"]
    Z_dict.pop("Unmatched")
    dupl_key=sorted([key for key,sublist in Z_dict.items() \
            for value in sublist if value in dupl_value],reverse=True)
    Z_dict["Unmatched"] = un_
    #######################################################

    figure = Figure(figsize=(16,9))
    #fig, ax = plt.subplots(2,gridspec_kw={'height_ratios': [3,1]})
    plot0 = figure.add_subplot(4,1,(1,3))
    plot1 = figure.add_subplot(4,1,4)
    plot0.set_yscale(SCALE)
    plot0.set_title('Element deconvolution',fontsize=10)
    #figure.setp(ax, xlim=(x.min(),x.max())) #Set xlim on both axes

    plot0.text(
            0,
            np.max(Y_DATA),
            "$\chi^2$: %.3f"%rchisq_gaus,
            fontsize=10,
            bbox={'facecolor':'None', 'edgecolor':'None', 'pad':8})

    plot0.plot(x,Y_CONT,linewidth=1,zorder=1,label='Continuum',color="green")
    plot0.plot(x,Y_DATA,linewidth=1,zorder=1, label='Counts',color="blue")
    plot0.plot(x,y_gaus,label='Fit')
    if SCALE == "linear": plot0.set_ylim([-1,Y_DATA.max()])
    else: plot0.set_ylim([1, Y_DATA.max()])
    plot0.set_xlim(x.min(), x.max())
    element = [*Z_dict][:-1] #To be plotted elements

    #######################################################################
    # Loop over list of keys with elements, disregarding last 'unmatched' #
    # key (For iteration list needed, with list(Z_dict.keys()) being same #
    # as [*Z_dict])                                                       #
    #######################################################################

    for i in element:

        ###############################################################
        # Loop over list of specific values with corresponding peak   #
        # index (Values are already of type(list) and since .values() #
        # not used no need to convert to list like needed with keys)  #
        ###############################################################

        for j in Z_dict[i]:
            plot0.axvline(
                    x=E_peak[j],
                    color='m',
                    linewidth=1,
                    zorder=2,
                    label='Found peaks')
            plot0.plot(x, y_gaus_single[j], color='k', linewidth=1, zorder=3)
            plot0.fill_between(
                    x,
                    Y_CONT,
                    y_gaus_single[j],
                    facecolor=color[element.index(i)],
                    alpha=0.5,
                    zorder=3)

            #################################################################
            # Make sure if double assigned peak latter is plotted slightly  #
            # higher so no overlap occurs in plotting element indication    #
            #################################################################

            if i in dupl_key[:int(len(dupl_key)/2)] and j in dupl_value:
                plot0.text(
                        E_peak[j]+25,
                        y_peak[j]*1.35,
                        Elements.ElementList[i],
                        fontsize=7)

            #################################################################

            ##############################################
            # Plot element indication at standard height #
            ##############################################

            else:
                plot0.text(
                        E_peak[j]+25,
                        y_peak[j]*1.15,
                        Elements.ElementList[i],
                        fontsize=7)

            ##############################################

        ###############################################################

    #######################################################################

    for i in [*Z_dict['Unmatched']]:
        plot0.axvline(
                x=E_peak[i],
                color='m',
                linestyle='dashed',
                linewidth=1,
                zorder=2,
                label='Unmatched peaks')

    plot1.set_ylim([-2,2])
    plot1.set_yticks([-2,-1,0,1,2])
    plot1.plot(x, residuals_gaus, linewidth=1)
    plot1.axhline(y=0, color='k')
    plot1.set_xlabel('Energy (eV)')
    plot0.set_ylabel('Counts')
    plot1.set_ylabel('Residuals / $\sigma$')
    handles,labels = plot0.get_legend_handles_labels()
    by_label = dict(zip(labels,handles))
    plot0.legend(by_label.values(), by_label.keys(),prop={'size': 7},loc="upper right")

    figure.savefig(
            os.path.join(figures_path,"Fit_{}.png".format(it+1)),
            dpi=300,
            format="png")
    plot0.clear()
    plot1.clear()

def gausfit(
        x,                  #Energy axis
        y_savgol,           #Array with spectra
        y_cont,             #Array with corresponding continuum
        x_peak,             #Peaks indexes
        Z_dict,             #Matched elements
        zero,               #Calibration zero
        gain,               #Calibration gain
        fit_path,           #Path to save FRAMEs
        figures_path,       #Path to save plots
        SUM,                #Global sum spectrum and corresponding continuum (tuple) RAW
        FN,                 #Fano and Noise tuple
        iterator,           #Progressbar iterator (uses lock)
        configurations,     #Datacube configuration
        bar=None,
        work_done=None,
        results=None,
        scalemode=None):

    from scipy.optimize import curve_fit
    import gc
    cycles = Constants.FIT_CYCLES

    ######################################################################################
    # Prepend global spectrum to spectra. Each gausfit instance receives the RAW         #
    # global spectrum (not modified by filtering) and its corresponding continuum        #
    # This global spectrum is then fitted to be displayed as the selected calculated ROI #
    ######################################################################################

    y_savgol = np.insert(y_savgol,0,SUM[0],axis=0) 
    y_cont = np.insert(y_cont,0,SUM[1],axis=0) 
    print("y_savgol shape",y_savgol.shape)
    print("y_cont shape",y_cont.shape)

    ######################################################################################

    ####################################################################################
    # Calculate uncertainty y_savgol + clip to one as default value in curve_fit sigma #
    ####################################################################################

    uncertainty = np.sqrt(y_savgol).clip(1) 

    ####################################################################################

    #######################################################################################
    # FANO and NOISE can be locally fitted, however, this consumes considerably more      #
    # resources. Using a global value for these parameters reduces the fitting complexity #
    # and runs much faster                                                                #
    #######################################################################################

    Fano0 = FN[0]
    Noise0 = FN[1]

    gamma0 = 1
    frame = [] 

    ######################################################################
    # Cut-off X_peak to length channels by disregarding                  #
    # eventual out-of-bound added K-beta lines + calculate peak energies #
    ######################################################################

    E_peak = zero+gain*x_peak[x_peak<=len(x)] 

    ######################################################################

    #############################################################
    # Determine y_peak height at corresponding x_peak locations #
    #############################################################

    y_peak = y_savgol[:,x_peak[x_peak<=len(x)]] 

    #############################################################

    ############################
    # Parameters initial guess #
    ############################

    A0 = y_peak*np.sqrt(((Noise0/2.3548)**2)+(3.85*Fano0*E_peak))*2.5066282746310002/gain
    params_gaus = A0

    tot = y_savgol.shape[0]
    for it in range(tot):
        time0 = timeit.default_timer()

        if bar!=None and not bar.make_abortion and it: 
            iterator += 1
            percent = iterator/tot*100
            bar.updatebar(iterator)
            bar.update_text("Fitting data... {0:0.2f}%".format(percent))
        elif bar!=None and bar.make_abortion: return
        elif it:
            with lock: iterator.value = iterator.value + 1
        else: pass

        time_fit = timeit.default_timer()
        ''' Gaussian Fit '''
        try: 
            if configurations["bgstrip"] == "None":
                popt_gaus, pcov_gaus = curve_fit(lambda x,*A: gaus(
                    x,E_peak,gain,Noise0,Fano0,*A),
                    x,
                    y_savgol[it],
                    p0=params_gaus[it],
                    sigma=uncertainty[it],
                    ftol=1,
                    xtol=1,
                    epsfcn=gain,
                    method="lm",
                    maxfev=cycles) #Clean Gaus
            else:
                 popt_gaus, pcov_gaus = curve_fit(lambda x,*A: gaus(
                    x,E_peak,gain,Noise0,Fano0,*A) + y_cont[it],
                    x,
                    y_savgol[it],
                    p0=params_gaus[it],
                    sigma=uncertainty[it],
                    ftol=1,
                    xtol=1,
                    epsfcn=gain,
                    method="lm",
                    maxfev=cycles) #Clean Gaus
        except:
            print("WARNING:\nFit failed for spec {}".format(it))
            popt_gaus = np.zeros(E_peak.shape[0],dtype="int32")
        print("curve_fit time: {0:0.2f}".format(timeit.default_timer()-time_fit),end="\r")
        
        ######################################
        # Exclude global spectrum from frame #
        ######################################
        if it:
            ########################################################
            # Put combined area's peaks belonging to corresponding #
            # elements into dictionary only taking positive area's #
            ########################################################
            Area_dict_gaus={i: popt_gaus[:][Z_dict[i]]\
                    for i in [*Z_dict][:-1]} #-1 excludes last key "Unmatched"
            ########################################################
            frame.append(Area_dict_gaus) #Append dictionaries in frame list chronologically

        ######################################
        
        else: 
            y_gaus_single = np.asarray(

            #########################################################
            # This line is used when fitting fano and noise locally #
            #########################################################
            #        [gaus(x,E_peak[i],gain,*popt_gaus[[0,1,2+i]]) for i in range(
            #########################################################

                    [gaus(x,E_peak[i],gain,Noise0,Fano0,popt_gaus[i]) for i in range(
                        E_peak.size)]) + y_cont[it]

            g_fit_path = fit_path.split(".")[0]
            g_fit_path, chunk = g_fit_path.split("Fit_Chunk_",1)
            g_peak_order_path = g_fit_path + "Global_Peak_Order.npy"
            g_fit_path = g_fit_path + "Global_Fit_Chunk.npy"
            np.save(g_fit_path,y_gaus_single)
            ordered_peaks = E_peak,Z_dict
            np.save(g_peak_order_path,ordered_peaks)
       
        if configurations["bgstrip"] == "None":
            y_gaus = gaus(x,E_peak,gain,Noise0,Fano0,popt_gaus)
        else:
            y_gaus = gaus(x,E_peak,gain,Noise0,Fano0,popt_gaus)+y_cont[it]

        #############################################################################
        #Residuals devided by sigma y_i/y_savgol or eventual 1 in case of sigma = 0 #
        #############################################################################
        residuals_gaus = (y_savgol[it]-y_gaus)/np.maximum(uncertainty[it],1) 
        #############################################################################

        ############################################
        #Residual sum squares, in this case chi-sq #
        ############################################
        ss_res_gaus= np.sum(np.square(residuals_gaus)) 
        rchisq_gaus=ss_res_gaus/(len(y_savgol[it])-len(popt_gaus)) #Reduced chi-sq
        ################### END OF GAUSS FIT ####################
        
        ##########################
        # SAVE PLOT IS REQUESTED #
        ##########################
        
        if Constants.SAVE_FIT_FIGURES and (it+1)%Constants.SAVE_INTERVAL==0:
            
            if configurations["bgstrip"] == "None":
                y_gaus_single = np.asarray(
                    [gaus(x,E_peak[i],gain,Noise0,Fano0,popt_gaus[i]) for i in range(
                            E_peak.size)])
                y_continuum = np.zeros(y_savgol[it].shape)
            else:
                y_gaus_single = np.asarray(
                    [gaus(x,E_peak[i],gain,Noise0,Fano0,popt_gaus[i]) for i in range(
                            E_peak.size)]) + y_cont[it]
                y_continuum = y_cont[it]

            save_plot(
                    x,
                    y_savgol[it],
                    y_continuum,
                    y_gaus_single,
                    y_gaus,
                    rchisq_gaus,
                    residuals_gaus,
                    Z_dict,
                    E_peak,
                    y_peak[it],
                    figures_path, it,
                    scalemode
                    )
            
            del y_gaus_single

        ########### END OF SAVE BLOCK ###########

        del popt_gaus
        del y_gaus
        del residuals_gaus
        del ss_res_gaus
        del rchisq_gaus
        gc.collect()

    np.save(fit_path,frame)
    print("Saved frame chunk to {}".format(fit_path))
    
    if work_done != None:
        with lock: work_done.value = work_done.value + 1
    if results != None: results.put(frame)

    del frame
    del E_peak
    del y_peak
    del A0
    del Area_dict_gaus
    gc.collect()

    return 0

""" Model functions ------------------------------------------------------------"""
    
""" Sum changes although summing over rows automatically back to one row 
array and hence only x needs to be Transposed instead of A,E_peak and 
s --- A using gausfit seperated from params concatenate ndarray and put 
in solo tuple, so not ndarray within tuple like when calling specifically 
funcs and hence does not need to be unpacked """

def gaus(x, E_peak, gain, Noise, Fano, *A):
    s = np.sqrt(((Noise/2.3548200450309493)**2)+3.85*Fano*E_peak) #np.sqrt works for arrays
    return gain*np.sum(A/(s*2.5066282746310002)*np.exp(-np.square(x[:,None]-E_peak)/(2*np.square(s))),1)

"""-----------------------------------------------------------------------------"""
    
""" Both sigma and gamma energy dependance E_peak, sigma since 
direct function and gamma since divided by sigma """        

def voigt(x, E_peak, Noise, Fano, gamma, *A):
    s = np.sqrt(np.square(Noise/(2*np.sqrt(2*np.log(2))))+3.85*Fano*E_peak)
    return np.sum(A/(s*np.sqrt(2*np.pi))*np.real(wofz(((x[:,None]-E_peak)+1j*gamma)/(s*np.sqrt(2)))),1)

"""-----------------------------------------------------------------------------"""

def findpeak(
        y_global,
        y_cont,
        zero,
        gain,
        energies,
        path,
        width=9,
        r=2): 

    """
    Input:
        y_global        (channels)             <class 'numpy.ndarray'>     
        Counts spectra with Savitzky-Golay filter
        width:          ()                     <class 'int'>               
        Width of filter: (default = 9)
        r:              ()                     <class 'int'>               
        Peak search sensitivity factor: (default = 2)
        y_cont:         (files+1,channels)     <class 'numpy.ndarray'>     
        Continuum of global and single spectra
        zero:           ()                     <class 'numpy.float64'>     
        Slope from linear regression calibration data
        gain:           ()                     <class 'numpy.float64'>     
        Intercept from linear regression calibration data
        energies:       ()                     <class 'numpy.ndarray'>     
        path:           ()                     <class 'string'>

    Output:
        x_peak:         (peaks,)               <class 'numpy.ndarray'>     
        Peak indices 
        Z_dict:         {}                     <class 'dict'>              
        Z-number to matched peak indices 
    """

    """ Pay attention to pass to findpeak function the PREPARED sum spectrum 
    Obtained by summing each spectrum in the dataset by clipping them at 0.
    y_savgol is clipped to 1 in this function """

    #################################################################
    # Findpeaks from y_savgol to avoid redundant significant        #
    # convolution peaks from distorted background                   #
    # Usually between 2-4, but needs to be adjusted if continuum    #
    # varies between spectra from e2 to even e4                     #
    # Width should be odd and equal to FWHM; v should be between    #
    # FWHM/2 and FWHM/3. FWHM are around 10 for peaks               #
    # As width gets lower, y_conv is more susceptible to smaller    #
    # peak variations and hence smaller peaks in general. Overal    #
    # intensity y_conv does not change significantly and hence is   #
    # mostly dependend on intensity spectrum.                       #
    #################################################################

    width=int(Constants.PEAK_TOLERANCE)
    continuum_tol = Constants.CONTINUUM_SUPPRESSION

    #################################################################
    # Calculating fill and width value side windows by by adding 1  #
    # to round down real number after giving it int() value         #
    #################################################################

    v = int(width/2)+1 

    #################################################################
    
    #################################################################
    # Create normalized window with side values approaching but not #
    # equal to center values but due to odd width number and        #
    # slicing side windows needs to be in integers                  #
    #################################################################

    window = np.concatenate((
        np.full(v,fill_value=-1/(2*v)),
                np.full(width,fill_value=1/width),
                np.full(v,fill_value=-1/(2*v)))) 

    #################################################################
    
    ######################################################################
    # Using numpy discrete convolve method with mode='same' resulting in #
    # y_conv ndarray having same width as original y ndarray + execute   #
    # subsequent clipping to neglect negative convolution values         #
    ######################################################################

    y_conv = np.convolve(y_global,window,mode='same').clip(0) 

    ######################################################################
    
    ##############################################################
    # Using numpy discrete convolve method to calculate variance #
    # to be used as significance level                           #
    ##############################################################

    var_conv = np.convolve(y_global,np.square(window),mode='same')

    ##############################################################
    
    ##########################################################################
    # Renormalize r so that difference between max(y_conv) and max(var_conv) #
    # from initial spectrum is 130 (Because taken r=2 for this case, but in  #
    # general difference should be around 100)                               #
    ##########################################################################

    r*=(np.max(y_conv)/(np.max(np.sqrt(var_conv)*r)))/130 

    ##########################################################################

    #######################################################
    # Generate peak indices from boolean array based on   #
    # convolution conditions + global continuum times 1.5 #
    #######################################################
    
    x_peak = np.flatnonzero(
            (np.roll(y_conv,-1)<y_conv) & \
                    (np.roll(y_conv,1)<y_conv) & \
                    (y_conv>np.sqrt(var_conv)*r) & \
                    (y_global>continuum_tol*y_cont[0])) 

    #######################################################
    
    ###################################################
    # Confine x_peak array in interval [width,-width] #
    ###################################################

    x_peak = x_peak[(x_peak>width) & (x_peak<len(y_global)-width)] 
    
    ###################################################

    ###########################
    # Calculate peak energies #
    ###########################

    E_peak = zero + gain * x_peak 

    ###########################
    
    ###############################################################
    # Unpacking xlib from four different macros in tuple until Bi #
    ###############################################################

    E_lib = []
    for i in range(5,84):
        try: a = xlib.LineEnergy(i, xlib.KA1_LINE)*1000
        except ValueError: a = 0 
        try: b = xlib.LineEnergy(i, xlib.KB_LINE)*1000
        except ValueError: b = 0 
        try: c = xlib.LineEnergy(i, xlib.LA1_LINE)*1000
        except ValueError: c = 0 
        try: d = xlib.LineEnergy(i, xlib.LB_LINE)*1000
        except ValueError: d = 0
        E_lib.append( (a,b,c,d) )

    E_lib = np.asarray( E_lib, dtype=np.float32 ) 

    ###############################################################
    
    ##################################################################
    # Insert Element to disregard, keeping in mind Z_true is index+5 #
    ##################################################################
    E_lib[50:,:2]=False #Set elements K-alpha & K-beta lines to zero after Xenon (Z=54)
    E_lib[:51,2:]=False #Set elements L-alpha & L-beta lines to zero prior to Hg (Z=80)
    E_lib[52:74,2:]=False #Set elements L-alpha & L-beta lines to zero prior to Hg (Z=80)
    ##################################################################

    #####################################################################
    # Relative margin <0.006. It should be so that no found peaks are   #
    # unmatched that instead should have been matched but instead get   #
    # a double added K-beta peak + minimum of 2 channels (~60eV)        #
    # starting from 4000eV, so 2*gain/4000                              #
    #####################################################################
    
    #########################################################################
    # 3D boolean area with shape (50,2,23) resulting from substraction      #
    # (50,2,1)-(1,1),23. E_lib represented by axis=0, K-alpha/beta couple   #
    # by axis=1 and E_peak by axis=2                                        #
    #########################################################################

    E_mesh = np.isclose(E_lib[:,:,None],E_peak,rtol=2*gain/4000)#rtol=0.006) 

    """ If two peaks put for one (by means of two peaks within 4 channels), i
    remove latter (rare: means y_conv has mistakenly added two lines for only one peak): """
    
    ####################################################################################
    # Get Mask of x_peak_array where difference between two peaks is within 4 channels #
    ####################################################################################

    double_peak=np.diff(x_peak,prepend=0)<=4

    ####################################################################################
    
    #############################################################################
    # Set matches latter double peak to False meaning it becomes unmatched peak #
    #############################################################################

    E_mesh[:,:,double_peak]=False

    #############################################################################

    ######################################################################
    # Set latter double unmatched peak at channel# 0 to exclude from fit #
    ######################################################################

    x_peak[double_peak]=False 

    ######################################################################

    if np.any(double_peak):
        print("Warning double peak single element found in global spectrum")

    """If two peaks share same K-alpha / K-beta / L-alpha / L-beta remove 
    prior/latter/prior/latter (Happens more often than double_peak usually 
    for higher channels due to rtol being relative):"""
    
    ##########################################################
    # K-alpha / K-beta / L-alpha / L-beta coordinate matches #
    ##########################################################

    KA_match,KB_match,LA_match,LB_match = (np.nonzero(E_mesh[:,i,:]) for i in range(4)) 

    ##########################################################

    E_mesh[:,0,KA_match[1][~np.diff(KA_match[0],append=0).astype(bool)]]=False
    E_mesh[:,1,KB_match[1][~np.diff(KB_match[0],prepend=0).astype(bool)]]=False
    E_mesh[:,2,LA_match[1][~np.diff(LA_match[0],append=0).astype(bool)]]=False
    E_mesh[:,3,LB_match[1][~np.diff(LB_match[0],prepend=0).astype(bool)]]=False


    """If K-alpha(Z[1]) from double matched peak keep K-beta(Z[1]) and 
    throw away K-alpha(Z[2]):"""
    
    #####################################################################
    #Determine column indices double matches between K-alpha and K-beta #
    # regarding different elements                                      #
    #####################################################################

    double_match = np.flatnonzero(E_mesh[:,[0,1],:].any(0).all(0)) 
    print("double matches",double_match.shape)

    #####################################################################
    
    ######################################################################################
    # Row indices double matched K-beta lines with an subsequent (higher Z) K-alpha line #
    ######################################################################################

    KB_double = np.flatnonzero(E_mesh[:,1,double_match].any(1)) 

    ######################################################################################
    
    ###############################################################################
    #Row indices double matched K-alpha lines with an prior (lower Z) K-beta line #
    ###############################################################################

    KA_double = np.flatnonzero(E_mesh[:,0,double_match].any(1)) 

    ###############################################################################
    
    ###############################################################################
    # Test if K-alpha line is present of corresponding double matched K-beta line #
    ###############################################################################
    
    KA_present = E_mesh[KB_double,0,:].any(1) 

    ###############################################################################
    
    #########################################################################
    # Set correction in case of subsequent True elements in K-alpha present #
    #########################################################################

    try: KA_correction = KB_double[KA_present]!=np.roll(KA_double[KA_present],1)
    except: KA_correction = KB_double[KA_present]

    #########################################################################
    
    ###########################################################
    # Check for two or more subsequent False in KA_correction #
    ###########################################################

    double_correction=np.diff(np.flatnonzero(KA_correction),append=len(KA_correction)) 

    ###########################################################
    
    #############################################################################
    # In case of two or more subsequent False in KA_correction,                 #
    # change ::2 to True for first occurence (only happens once                 #
    # with single or double correction needed in low eV zone with much overlap) #
    #############################################################################

    if np.any(double_correction>=3): 
        
        ##########################################################
        # Update KA_correction when double correction is present #
        ##########################################################

        KA_correction[np.flatnonzero(
                KA_correction)[double_correction>=3][0]:(
            np.flatnonzero(
                KA_correction)[double_correction>=3][0]+\
                        double_correction[double_correction>=3][0]
                        ):2]=True

        ##########################################################

        KA_present[KA_present]=KA_correction #Update K-alpha present
        print("KA correction shape",KA_correction.shape)

    if KA_present.size > double_match.size: #This means there are more KB lines corresponding to KA than recorded double matches
        print("large KA present")
        KA_present = np.ones(double_match.shape).astype(bool)

    #############################################################################
    
    #######################################################################
    # Set K-alpha(Z[2]) double matched peaks to False if K-alpha(Z[1])    #
    # peak is present (in double matched K-beta(Z[1]) with K-alpha(Z[2])) #
    #######################################################################

    E_mesh[:,0,double_match[KA_present]]=False

    #######################################################################

    """Else keep K-alpha(Z[2]) and throw away K-beta(Z[1]):"""
    ############################################################
    # Set K-beta(Z[1]) remaining double matched peaks to False #
    ############################################################
    
    E_mesh[:,1,double_match[~KA_present]]=False 

    ############################################################

    """If not K-beta(Z[1]) from double matched L-alpha & L-beta peak 
    with K-alpha(Z[1]), throw away K-alpha(Z[1]):"""
    ################################################################################
    # Determine column indices double matches between K-alpha and L-alpha / L-beta #
    ################################################################################
    
    double_match_L = np.flatnonzero((E_mesh[:,0,:].any(0))&(E_mesh[:,2:,:].any((1,0)))) 

    ################################################################################
    
    ##################################################################
    # Row indices double matched K-alpha lines with L-alpha / L-beta #
    ##################################################################
    
    KA_double_L = np.flatnonzero(E_mesh[:,0,double_match_L].any(1)) 

    ##################################################################
    
    ##############################################################################
    #Test if K-beta line is present of corresponding double matched K-alpha line #
    ##############################################################################

    KB_present_L = E_mesh[KA_double_L,1,:].any(1)

    ##############################################################################

    #######################################################################################
    # Set K-alpha(Z[1]) double matched peaks to False if K-beta(Z[1]) peak is not present #
    #######################################################################################
    
    E_mesh[:,0,double_match_L[~KB_present_L]]=False 

    #######################################################################################

    """Else take both:" (Done automatically in x_peak_id)"""
    ################################################################################
    # Extract E_lib indices missing K-beta lines from E_mesh only if K-alpha==True #
    ################################################################################
    
    KB_miss = np.flatnonzero((E_mesh[:,0,:].any(1)==True)&(E_mesh[:,1,:].any(1)==False)) 

    ################################################################################
    
    ###############################################################################
    # Determine channel nummer position missing K-beta lines and use to disregard #
    # eventual out-of-bound added K-beta lines > len(energies)                    #
    ###############################################################################

    x_KB_miss = ((E_lib[KB_miss,1]-zero)/gain).astype(int) 

    ###############################################################################
    
    ##############################################################################
    # Individually extract indices coupled E_peak lines with E_lib K & L-lines + #
    # add in the end missing K-beta lines                                        #
    ##############################################################################

    x_peak_id = np.concatenate(
            (np.nonzero(
                np.vstack((E_mesh[:,:2,:].any((1,0)),E_mesh[:,2:,:].any((1,0)))).T)[0],
                len(x_peak)+np.arange(len(x_KB_miss[x_KB_miss<=len(y_global)]))))

    ##############################################################################
    
    #################################################################################
    # Keep order from E_peak with increasing energy for coupling Z-numbers (K-alpha #
    # and K-beta) by transposing mask array + concatenating Z-numbers from missing  #
    # K-beta lines with increasing number                                           #
    #################################################################################

    Z_peak = 5+np.concatenate(
            (np.nonzero(E_mesh.any(1).T)[1],KB_miss[x_KB_miss<=len(y_global)]))

    #################################################################################
    
    ###############################################################
    # Add channels missing K-beta lines to x_peak in x_peak_array #
    ###############################################################

    x_peak = np.concatenate((x_peak,x_KB_miss[x_KB_miss<=len(y_global)]))

    ###############################################################

    # print("Peaks:",x_peak)
    # print("Peak matched/added:",x_peak[x_peak_id])
    # print("Peak energy matched/added:",zero+gain*x_peak_total[x_peak_id])
    # print("Index peak found/added:", x_peak_id)
    # print("Z-number peak found/added",Z_peak)

    Z_dict = {} 
    for i,j in zip(Z_peak,x_peak_id):
        Z_dict.setdefault(i,[]).append(j)
    Z_dict['Unmatched']=list(set(range(len(x_peak))).difference(x_peak_id)) 
    
    plt.figure()
    spectrum=0
    plt.plot(energies,y_global)
    plt.plot(energies,y_conv)
    plt.plot(energies,(np.sqrt(var_conv)*r))
    plt.plot(energies,y_cont[spectrum])
    plt.semilogy(energies,continuum_tol*y_cont[spectrum])
    plt.ylim([10e-2,y_global.max()])
    #plt.xlim([0,4000])
    
    E_peak = zero + gain * x_peak
    for j in E_peak:
        plt.axvline(x=j)
    plt.savefig(path,format="png",dpi=1200)

    return x_peak, Z_dict

def find_and_fit(
        data,
        intercept,
        configurations,
        path,
        plots_save_path,
        chunk,
        results,
        energies,
        fano_and_noise,
        iterator,
        work_done,
        global_spec_and_bg,
        peaks,
        matches,
        global_parameters):

    """ Target function for MultiFit class 

    ------------------------------------------------------------------------

    INPUT:
        data; <3D-array> - containing the splitted data block x data/continuum x channels
        intercept; <float> - calibration parameter 
        slope; <float> - calibration parameter (gain)
        path; <string> - where to save *.npy fit chunks
        chunk; <integer> - chunk number
        results; <multiprocessing Queue object> - collects outputs from processes
        energies; <1D-array> - calibrated energy axis of datacube in memory
        fano_and_noise; <1D-array> - contains the global fitted Fano and Noise values
        iterator; <Synchronized> - counter to verify processes progress
        global_spec_and_bg; <2D-array> - summation derived spectrum [0] and its continuum [1]
        clipped_global_spec; <1D-array> - obtained by summing the clipped data (clipped to 1)
    """
    
    slope = configurations["gain"]*1000
    Constants.FIT_CYCLES = global_parameters[0]
    Constants.SAVE_INTERVAL = global_parameters[1]
    Constants.SAVE_FIT_FIGURES = global_parameters[2]
    Constants.PLOTSCALE = global_parameters[3]
    print(Constants.PLOTSCALE)
    if Constants.PLOTSCALE == "-semilogy": scalemode = "log"
    else: scalemode = "linear"
    counts, continuum = np.asarray(data[0]), np.asarray(data[1])

    print("Chunk {} data size: ".format(chunk),convert_bytes(counts.nbytes))
    print("Chunk {} continuum size: ".format(chunk),convert_bytes(continuum.nbytes))

    del data

    if chunk < 10:
        fit_path = os.path.join(path,"Fit_Chunk_0{0}.npy".format(chunk))
        plots_save_path = os.path.join(plots_save_path,"Chunk 0{}".format(chunk))
    else:
        fit_path = os.path.join(path,"Fit_Chunk_{0}.npy".format(chunk))
        plots_save_path = os.path.join(plots_save_path,"Chunk {}".format(chunk))

    try: os.makedirs(plots_save_path)
    except: pass

    print("\n\nELEMENTS IN CHUNK {}: {}".format(chunk,matches.keys()))

    ########################

    fitted_spec = gausfit(
            energies,
            counts,
            continuum,
            peaks,
            matches,
            intercept,
            slope,
            fit_path,
            plots_save_path,
            global_spec_and_bg,
            fano_and_noise,
            iterator,
            configurations,
            bar=None,
            work_done=work_done,
            results=results,
            scalemode=scalemode)
    return 0

def add_elements(peaks,matches,element_list):
    """ element_list: 2D list with element Z and peak position """

    print("INFO:\nAdding element {}...".format(element_list[0][0]))

    iterator = 0
    for element in element_list:
        if element[0] not in matches:
            print("Trying to insert on peaks array")
            print(element[1])
            print(element[2])
            peaks = np.insert(peaks,-1,element[1])
            peaks = np.insert(peaks,-1,element[2])
            matches[element[0]] = [
                np.where(peaks==element[1])[0][0],
                np.where(peaks==element[2])[0][0]]
        un_ = matches["Unmatched"]
        matches.pop("Unmatched")
        matches = {int(k) : v for k, v in matches.items()}
        matches["Unmatched"] = un_

    peaks, matches = recheck_peaks(peaks,matches)
    return peaks, matches

def recheck_peaks(peaks,matches):
    """ Must run always after the findpeak() function. This function re-checks the 
    outputs from findpeak() by verifiying how far the identified peaks are from the
    theoretical position. This solves issues with doubled peaks or mis-identification
    that happens usually with higher energy peaks """

    un_ = matches["Unmatched"]
    matches.pop("Unmatched")

    energies = {key:peaks[peak] for key,peak in matches.items()}
    checked_matches = {}
    gain = Constants.MY_DATACUBE.config["gain"]*1000
    W = Constants.CHECK_TOLERANCE

    for key in matches.keys():
        checked_matches[key] = []
        element = Elements.ElementList[key]
        theoretical_energies = [Elements.Energies[key]*1000,
                Elements.kbEnergies[key]*1000]
        for peak in range(len(matches[key])):
            lower = theoretical_energies[peak] - (W*gain)
            high = (W*gain) + theoretical_energies[peak]
            pos = Constants.MY_DATACUBE.energyaxis[energies[key][peak]]*1000
            if len(matches[key])>1:
                if lower <= pos <= high:
                    checked_matches[key].append(matches[key][peak])
            else: 

                #################################################################
                # If, from findpeak(), only beta line is detected, check twice  #
                # the only value inside the matches key as the only key in this #
                # case is the beta one                                          #
                #################################################################

                for line in range(2):
                    lower = theoretical_energies[line] - (Constants.CHECK_TOLERANCE*gain)
                    high = (Constants.CHECK_TOLERANCE*gain) + theoretical_energies[line]
                    if lower <= pos <= high:
                        checked_matches[key].append(matches[key][peak])

                #################################################################

        if checked_matches[key] == []: checked_matches.pop(key)

    checked_matches["Unmatched"] = un_
    return peaks, checked_matches

def mock(data,intercept,slope,path,chunk,results,energies):
    counts, continuum = data[0], data[1]

    fit_path = os.path.join(path,"Fit_Chunk_{0}.npy".format(chunk))

    for i in range(len(counts)):
        time.sleep(0.0001)
    
    for i in range(len(counts)):
        time.sleep(0.010)
    results.put(1)
    return 0

def build_images(
        frames_path,
        bar=None): 
    
    ####################################
    # Reads frame files in frames_path #
    ####################################

    elements = []
    frames = [npy for npy in os.listdir(
        frames_path) if npy.startswith("Fit_Chunk") and not \
                os.path.isdir(os.path.join(frames_path,npy))]
    frmcount = 0

    ####################################
    
    #########################################################
    # Verify which elements are fitted and prepare the list #
    #########################################################

    bar.progress["max"]=len(frames)
    for frmfile in frames:
        bar.updatebar(frmcount)
        frmcount += 1
        frame = np.load(
                os.path.abspath(os.path.join(frames_path,frmfile)),
                allow_pickle=True)
        print("\n","-"*5,"FRAME {}".format(frmcount),"-"*5)
        print("len frame ",len(frame))
        print("type frame ",type(frame))
        print("shape frame ",frame.shape)
        print("len frame[0] ",len(frame[0]))
        print("frame[0] ",frame[0])
        print("Keys ",frame[0].keys())
        for i in range(len(frame)):
            for key in frame[i].keys():
                elements.append(key)
    elements = set(elements)
    try: elements.remove("Unmatched")
    except: print("No unmatched peaks! Elements:",elements)
    for element in elements: print(element,type(element))
    element_list = [Elements.ElementList[key] for key in elements]

    #################################################################
    # reload cube because data is changed somewhere down the road   #
    # making a copy can cost a lot of memory (large cubes +/- 3Gb)  #
    #################################################################

    from .SpecRead import cube_path
    if os.path.exists(cube_path):
        cube_file = open(cube_path,'rb')
        Constants.MY_DATACUBE = pickle.load(cube_file)
        SpecRead.setup_from_datacube(Constants.MY_DATACUBE,
                {"{}".format(Constants.MY_DATACUBE.name):Constants.MY_DATACUBE.path})
        cube_file.close()

    #################################################################

    Constants.MY_DATACUBE.prepack_elements(element_list)
    maps_count,line = 0,0
    
    ####################################################
    # Builds the images using data from FRAME variable #
    ####################################################

    #alfa_beta = 1 #images are their sum
    alfa_beta = 2
    Constants.MY_DATACUBE.config["ratio"] == True

    el_maps = np.zeros([Constants.MY_DATACUBE.matrix.shape[0],
        Constants.MY_DATACUBE.matrix.shape[1],
        alfa_beta,len(element_list)],dtype="float32")

    Constants.LOGGER.info("\n"+"-"*5+"Starting image builder"+"-"*5)
    x,y,iteration,frmcount = 0,0,0,0
    start_x, start_y = 0,0
    bar.updatebar(0)
    bar.progress["max"]=len(elements)
    bar.update_text("Building images - {}/{}".format(0,len(frames)))
    
    for frmfile in frames:
        frmcount += 1
        bar.update_text("Building images - {}/{}".format(frmcount,len(frames)))
        frame = np.load(
                os.path.abspath(os.path.join(frames_path,frmfile)),
                allow_pickle=True)
        size = frame.shape[0]*len(element_list)
        if not elements: continue
        for key in elements:
            maximum_counts = 0
            for c in range(frame.shape[0]):
                iteration+=1
                percent = iteration/size
                for line in range(len(frame[c][key])):
                    if frame[c][key][line] > 0:
                        try: 
                            el_maps[x][y][line][maps_count] = frame[c][key][line]
                        except: 
                            el_maps[x][y][line][maps_count] = 0
                    else:
                        el_maps[x][y][line][maps_count] = 0
                pos = SpecMath.refresh_position(x,y,Constants.MY_DATACUBE.dimension)
                x,y = pos[0],pos[1]
            x,y = start_x, start_y
            maps_count += 1
            bar.updatebar(maps_count)
            
        iteration, maps_count = 0,0
        start_x, start_y, x, y = pos[0], pos[1], pos[0], pos[1]

    ####################################################
    
    ###############################################################################
    # Gives ROI attribute to datacube object. It can be a tuple with the          #  
    # peaks indexes (for each element) or the curve, set at add_roi_to_datacube() #
    ###############################################################################
    
    add_roi_to_datacube()
    
    ###############################################################################

    print("Splitting and saving...")
    ImgMath.split_and_save(Constants.MY_DATACUBE,el_maps,element_list,
            force_alfa_and_beta=True)
    bar.destroybar()
    
def add_roi_to_datacube():
    #######################################
    # List all Global Fit files in output #
    #######################################
    spectra_paths = [i for i in os.listdir(SpecRead.output_path) if "Global_Fit" in i]
    elements_order_paths = [i for i in os.listdir(SpecRead.output_path) if "Global_Peak" in i]
    for i in range(len(spectra_paths)):
        spectra_paths[i] = os.path.abspath(
                os.path.join(SpecRead.output_path,spectra_paths[i]))
        elements_order_paths[i] = os.path.abspath(
                os.path.join(SpecRead.output_path,elements_order_paths[i]))

    #######################################
    
    E_axis = Constants.MY_DATACUBE.energyaxis
    it = 0
    for f,o in zip(spectra_paths,elements_order_paths):
        it += 1
        idx = 0
        spectrum = np.load(f,allow_pickle=True)
        el_order = np.load(o,allow_pickle=True)
        print("Chunk",it,"No of elements: ",spectrum.shape[0])
        for key in el_order[1].keys():
            if key == "Unmatched": continue
            for plots in range(len(el_order[1][key])):
                idx = el_order[1][key][plots]
                print("Key", key, "line", plots,"in frame ",it, "spec index:",idx)
                
                #############################################################################
                # Each fitted peak carries the continuum with it, by summing both peaks to  #
                # create a single array to represent them, the continuum is doubled.        #
                # Therefore, each added peak has the continuum subtracted at each addition  #
                # and then added one single time at the end                                 #
                #############################################################################

                if not np.isnan(np.sum(spectrum[idx])):
                    Constants.MY_DATACUBE.ROI[
                Elements.ElementList[int(key)]]+=(spectrum[idx]-Constants.MY_DATACUBE.sum_bg)
            
            Constants.MY_DATACUBE.ROI[
                    Elements.ElementList[int(key)]]+=Constants.MY_DATACUBE.sum_bg

                #############################################################################
        del spectrum
    return 0

class Interrupt(Exception):
    pass


class MultiFit():
    def __init__(__self__,path):
        __self__.workers = []
        __self__.name = Constants.MY_DATACUBE.name
        __self__.save_plots_path = os.path.join(SpecRead.output_path,"Fit plots")
        __self__.results = multiprocessing.Queue()
        __self__.shutdown_event = multiprocessing.Event()
        __self__.global_iterator = multiprocessing.Value('i',0)
        __self__.global_iterator.value = 0
        __self__.work_done = multiprocessing.Value('i',0)
        __self__.work_done.value = 0
        __self__.cores = Constants.CPUS
        __self__.path = path
        __self__.energies = Constants.MY_DATACUBE.energyaxis*1000
        __self__.intercept = __self__.energies[0]
        __self__.slope = Constants.MY_DATACUBE.gain*1000
        __self__.FN = Constants.MY_DATACUBE.FN
        __self__.counts = Constants.MY_DATACUBE.matrix.reshape(
            -1,Constants.MY_DATACUBE.matrix.shape[-1])

        ###################################################################################
        # Prepare the data. Spectra are filtered with a savgol filter and the global      #
        # spectrum must be recalculated for the filtered data. The same for the continuum #
        ###################################################################################

        __self__.bar = Busy(len(__self__.counts),0)
        __self__.bar.update_text("Filtering data...")

        prepare_data(__self__)
        if __self__.bar.KILL:
            return

        __self__.continuum = Constants.MY_DATACUBE.background.reshape(
            -1,Constants.MY_DATACUBE.background.shape[-1])
        __self__.raw_sum_and_bg = Constants.MY_DATACUBE.sum, Constants.MY_DATACUBE.sum_bg
        __self__.bar.update_text("Thinking...")

        ###################################################################################

    def eat_data(__self__):

        ##############################################################
        # Split the data into blocks to distribute accross processes #
        # Here, the continuum array has the same size as the counts  #
        ##############################################################

        __self__.bar.update_text("Splitting data...")
        __self__.bar.updatebar(0)

        counts, continuum, block = [],[],[]
        if __self__.cores == 1:
            print("Only one core")
            Constants.LOGGER.warning("Sample is too small, running with one core only...")
            __self__.bite_size = __self__.counts.shape[0]
            __self__.leftovers = 0
            if Constants.MY_DATACUBE.config["bgstrip"] != "None":
                return [(__self__.counts, __self__.continuum)], []
            else:
                return [(__self__.counts)],[]
        else:
            bite_size = 0
            while bite_size < 400:
                bite_size = int(__self__.counts.shape[0]/__self__.cores)
                leftovers = int(__self__.counts.shape[0]%__self__.cores)
                print("bite size: ",bite_size,"leftovers ",leftovers)
                __self__.cores -= 1
                if bite_size == __self__.counts.shape[0]: break
            __self__.cores+=1
            __self__.bite_size = bite_size
            __self__.leftovers = leftovers

            __self__.bar.progress["max"] = bite_size*__self__.cores

            #########################################
            # Splits the data in pieces accordingly #
            # Available RAM is also considered      #
            #########################################

            if Constants.MY_DATACUBE.config["bgstrip"] != "None":
                spec = 0
                for k in range(__self__.cores):
                    counts, continuum = [],[]
                    chunk0 = k*bite_size
                    chunk1 = chunk0+bite_size
                    print("Block ",k)
                    counts = __self__.counts[chunk0:chunk1]
                    continuum = __self__.continuum[chunk0:chunk1]
                    for i in range(bite_size):
                        spec +=1
                    data = (counts,continuum)
                    block.append(data)
                if leftovers >= 1:
                    counts, continuum = [],[]
                    __self__.bar.update_text("Eating leftovers...")
                    __self__.bar.updatebar(0)
                    __self__.bar.progress["max"] = leftovers
                    for i in range(leftovers):
                        __self__.bar.updatebar(i)
                        counts.append(__self__.counts[spec])
                        continuum.append(__self__.continuum[spec])
                        spec += 1
                    leftovers = (counts,continuum)
            else:
                spec = 0
                for k in range(__self__.cores):
                    counts = []
                    chunk0 = k*bite_size
                    chunk1 = chunk0+bite_size
                    print("Block ",k)
                    counts = __self__.counts[chunk0:chunk1]
                    for i in range(bite_size):
                        spec += 1
                    data = (counts)
                    block.append(data)
                if leftovers >= 1:
                    counts = []
                    __self__.bar.update_text("Eating leftovers...")
                    __self__.bar.updatebar(0)
                    __self__.bar.progress["max"] = leftovers
                    for i in range(leftovers):
                        __self__.bar.updatebar(i)
                        counts.append(__self__.counts[spec])
                        spec += 1
                    leftovers = (counts)

            #########################################

            #######################################################################

            block = np.asarray(block)
            print("Data blocks shape: ",block.shape)

            #######################################################################
        del __self__.counts
        del __self__.continuum
        gc.collect()
        return block, leftovers

    def locate_peaks(__self__,add_list=None,path="./"):

        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx]

        ######################################################################
        # The global continuum of the filtered spectra is parsed to findpeak #
        # function. It uses this background as a criteria to select peaks    #
        ######################################################################

        continuum = np.insert(__self__.continuum,0,__self__.global_continuum, axis=0)

        ######################################################################

        peaks, matches = findpeak(
                __self__.SUM,
                continuum,
                __self__.intercept,
                __self__.slope,
                __self__.energies,
                path)

        peaks, matches = recheck_peaks(peaks,matches)

        ########################
        # Add element manually #
        ########################

        if add_list:
            for el in add_list:

                element_a = Elements.Energies[el]*1000
                element_b = Elements.kbEnergies[el]*1000

                #############################################
                #NOTE: uses the theoretical energies to fit #
                #############################################
                idx_a = np.where(__self__.energies==find_nearest(__self__.energies,element_a))
                idx_b = np.where(__self__.energies==find_nearest(__self__.energies,element_b))
                el = [[el, idx_a[0][0], idx_b[0][0]]]
                Constants.LOGGER.info("{} alpha, Theoretical: {}, Matched: {}".format(el,element_a,__self__.energies[idx_a]))
                Constants.LOGGER.info("{} beta, Theoretical: {}, Matched: {}".format(el,element_b,__self__.energies[idx_b]))
                #############################################

                #####################################################################
                #NOTE: uses setROI function. This returns the index of the nearest  #
                # peak to the theoretical value                                     #
                #####################################################################
                """
                elka_peak = SpecMath.setROI(
                        element_a,
                        __self__.energies/1000,__self__.SUM,{"gain":__self__.slope/1000})
                elkb_peak = SpecMath.setROI(
                        element_b,
                        __self__.energies/1000,__self__.SUM,{"gain":__self__.slope/1000})

                Constants.LOGGER.debug("setROI output: {}".format(elka_peak))
                Constants.LOGGER.debug("setROI output: {}".format(elkb_peak))

                el = [[el,int((elka_peak[0]+elka_peak[1])/2),
                        int((elkb_peak[0]+elkb_peak[1])/2)]]
                """
                #####################################################################

                try: peaks, matches = add_elements(peaks,matches,el)
                except: Constants.LOGGER.warning("Could not add element {} to chunk".format(el))

        Constants.MATCHES = peaks, matches
        Constants.LOGGER.info("Elements being fitted: {}".format(matches))
        return peaks, matches

    def check_progress(__self__):
        tot = int(__self__.cores*__self__.bite_size)+__self__.leftovers
        while __self__.work_done.value < len(__self__.workers) \
                and not __self__.bar.make_abortion:
            __self__.bar.updatebar(__self__.global_iterator.value)
            percent = __self__.global_iterator.value/tot*100
            __self__.bar.update_text("Fitting data... {0:0.2f}%".format(percent))
        try:

            __self__.bar.destroybar()
            #########################################################################
            # For long processes, kill processes and move on if any data is hanging #
            #########################################################################

            for p in __self__.workers:
                print("shutting ",p)
                __self__.shutdown_event.set()
                p.terminate()
                print(p,"SHUT")
            del __self__
            gc.collect()

            #########################################################################

            return 0
        except:

            __self__.bar.destroybar()
            #############
            # same here #
            #############

            for p in __self__.workers:
                print("shutting ",p)
                __self__.shutdown_event.set()
                p.terminate()
                print(p,"SHUT")
            del __self__
            gc.collect()

            #############

            return 1

    def launch_workers(__self__,
            cycles,
            plot_save_interval,
            save_plots):

        del Constants.MY_DATACUBE.matrix
        del Constants.MY_DATACUBE.background
        gc.collect()

        __self__.bar = Busy(len(__self__.counts),0)
        __self__.bar.updatebar(0)

        peaks, matches = Constants.MATCHES
        partial_ = []
        chunk, it = 0,0

        #########################
        # Create main processes #
        #########################

        bites, leftovers = __self__.eat_data()
        __self__.bar.progress["max"] = len(bites)

        for block in bites:
            print(block)
            print(len(block))

            __self__.bar.update_text("Polling chunks...")

            if Constants.MY_DATACUBE.config["bgstrip"] != "None":
                counts, continuum = np.asarray(copy.deepcopy(block),dtype="int32")
            else:
                counts = np.asarray(copy.deepcopy(block),dtype="int32")
                continuum = np.zeros([1,counts.shape[1]])
            del block

            print("Counts shape", counts.shape)
            print("Continuum shape", continuum.shape)

            it += 1
            chunk += 1
            p = multiprocessing.Process(target=find_and_fit,
                    name="chunk_{}".format(chunk),
                    args=(
                        (counts,continuum),
                        __self__.intercept,
                        Constants.MY_DATACUBE.config,       #configurations (gain included)
                        __self__.path,
                        __self__.save_plots_path,
                        chunk,
                        __self__.results,
                        __self__.energies,
                        __self__.FN,
                        __self__.global_iterator,
                        __self__.work_done,
                        __self__.raw_sum_and_bg,
                        peaks,
                        matches,
                        (cycles,plot_save_interval,save_plots,Constants.PLOTSCALE)))

            __self__.workers.append(p)
            del counts, continuum
            gc.collect()
        del bites
        gc.collect()

        #########################

        ######################################
        # Create a process for the leftovers #
        ######################################

        if isinstance(leftovers,tuple):
            counts, continuum = leftovers
            counts = np.asarray(counts,dtype="int32")
            it += 1
            chunk += 1
            p = multiprocessing.Process(target=find_and_fit,
                    name="chunk_{}".format(chunk),
                    args=(
                        (counts,continuum),
                        __self__.intercept,
                        Constants.MY_DATACUBE.config,       #configurations (gain included)
                        __self__.path,
                        __self__.save_plots_path,
                        chunk,
                        __self__.results,
                        __self__.energies,
                        __self__.FN,
                        __self__.global_iterator,
                        __self__.work_done,
                        __self__.raw_sum_and_bg,
                        peaks,
                        matches,
                        (cycles,plot_save_interval,save_plots,Constants.PLOTSCALE)))

            __self__.workers.append(p)

        ######################################

        workers_count=0
        __self__.bar.add_abort(__self__.workers,mode="auto_wizard")
        __self__.bar.toggle_abort("off")
        for p in __self__.workers:
            workers_count+=1
            print("\nPolling chunk ", workers_count)
            __self__.bar.updatebar(workers_count)
            p.daemon = True
            p.start()

        __self__.bar.progress["max"]= \
                int(__self__.cores*__self__.bite_size)+__self__.leftovers
        __self__.bar.updatebar(0)
        __self__.bar.update_text("Fitting data...")
        __self__.bar.toggle_abort("on")
        __self__.check_progress()

        #for i in range(chunk):
        while not __self__.shutdown_event.is_set():
            try:
                data = __self__.results.get(block=True)
                partial_.append(data)
            except queue.Empty:
                continue
            if data == "END": break
        __self__.results.close()
        __self__.results.join_thread()

        for p in __self__.workers:
            if p.exitcode !=0:
                p.join()
        return partial_

if __name__.endswith('__main__'):
    print("BatchFitter")
