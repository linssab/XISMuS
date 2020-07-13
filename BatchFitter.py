#################################################################
#                                                               #
#          BATCH FITTER                                         #
#                        version: 1.1.0 - Jul - 2020            #
# @authors: Boris Bremmers & Sergio Lins                        #
#################################################################

import logging
logger = logging.getLogger("logfile")
logger.info("Importing module BatchFitter.py...")
from multiprocessing import freeze_support
freeze_support()

#################
# Local imports #
#################
import Constants
import SpecRead
from SpecMath import savgol_filter, peakstrip, polfit_batch, refresh_position 
from ImgMath import split_and_save
import EnergyLib
import SpecMath
from ProgressBar import Busy
#################

import xraylib as xlib
import sys, os, multiprocessing, copy, pickle
from scipy.optimize import curve_fit
import numpy as np
import matplotlib.pyplot as plt

#from scipy.special import erfc #Complementary errorfunction
#from scipy.special import wofz #Faddeeva function defined as exp(-z**2) * erfc(-i*z)

import time,timeit

lock = multiprocessing.Lock()

def convert_bytes(num):

    """ Obtained from https://stackoverflow.com/questions/210408 """

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def gausfit(
        x,
        y_savgol,
        y_cont,
        x_peak,
        Z_dict,
        zero,
        gain,
        fit_path,
        figures_path,
        SUM,
        iterator,
        bar=None,
        work_done=None,
        results=None):

    """
    Input:
        x:              (channels,)            <class 'numpy.ndarray'>     
        Calibrated energy-axis applicable for all spectra
        y_savgol:       (files,channels)       <class 'numpy.ndarray'>     
        Counts spectra with Savitzky-Golay filter
        x_peak:         (peaks,)               <class 'numpy.ndarray'>     
        Peak indices 
        Z_dict:         {}                     <class 'dict'>              
        Z-number to matched peak indices 
        zero:           ()                     <class 'numpy.float64'>     
        Slope from linear regression calibration data
        gain:           ()                     <class 'numpy.float64'>     
        Intercept from linear regression calibration data
        Fit path

    Output:
        frame:          (files+1,channels)     <class 'list'>              
        Saved 2D array with areas peaks (dictionaries)
        (fig):          (files+1,)             <class 'matplotlib'>        
        Figures of fitted spectra                                              
    """

    time0 = timeit.default_timer()
    cycles = Constants.FIT_CYCLES
    #############################################################################
    # Fit using linregression calibration with x_peaks deduced from this and    #
    # hence automatically located perfectly at peaks and after element          #
    # recognition via xraylib. Like this stay in spectrum raum as well as no    #
    # need to refit Zero & Gain x/energy-axis parameters. Besides small shifts  #
    # in true spectrum values on x/energy-axis dont matter for peak area!       #
    #############################################################################

    ######################################
    # Prepend global spectrum to spectra #
    ######################################
    
    #y_savgol=np.concatenate((np.sum(y_savgol,0)[None,:],y_savgol),axis=0) 
    y_savgol=np.insert(y_savgol,0,SUM,axis=0) 

    ######################################

    ####################################################################################
    # Calculate uncertainty y_savgol + clip to one as default value in curve_fit sigma #
    ####################################################################################

    uncertainty = np.sqrt(y_savgol).clip(1) 

    ####################################################################################

    Noise0 = 80  # To be globally fitted
    Fano0 = 0.114  # To be globally fitted
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

    ########################
    # To be locally fitted #
    ########################

    A0 = y_peak*np.sqrt((np.square(Noise0/2.3548))+(3.85*Fano0*E_peak))*np.sqrt(2*np.pi)/gain

    ########################
    params_gaus = np.insert(A0,[0],[Noise0,Fano0],axis=1)  #Params Gaussian fit
    params_voigt = np.insert(A0,[0],[Noise0,Fano0,gamma0],axis=1) #Params Voigt fit

    ''' Plotting params '''
    element = [*Z_dict][:-1] #To be plotted elements
    color=plt.cm.jet(np.linspace(0,1,len(element))) #Create fixed color for specific element
    
    ########################################
    # Get duplicate values from dictionary #
    ########################################

    seen=set() #Define set of all values seen so far in set comprehension
    dupl_value=set(x for x in [value for sublist in Z_dict.values() \
            for value in sublist] if x in seen or seen.add(x)) 

    ########################################

    #######################################################
    # Get corresponding duplicate keys and reversely sort #
    #######################################################

    dupl_key=sorted([key for key,sublist in Z_dict.items() \
            for value in sublist if value in dupl_value],reverse=True) 

    #######################################################

    tot = len(y_savgol)
    for it in range(tot):

        if bar!=None and not bar.make_abortion: 
            iterator += 1
            percent = iterator/tot*100
            bar.updatebar(iterator)
            bar.update_text("Fitting data... {0:0.2f}%".format(percent))
        else:
            with lock: iterator.value = iterator.value + 1

        #print("Shapes")
        #print("x",x.shape)
        #print("E_peak",E_peak.shape)
        #print("y_savgol",y_savgol.shape)
        #print("y_savgol[0]",y_savgol[0].shape)
        #print("y_cont",y_cont.shape)
        #print("y_cont[0]",y_cont[0].shape)
        #print("uncertainty",uncertainty.shape)
        #print("params gaus",params_gaus.shape)

        ''' Gaussian Fit '''
        try: 
            popt_gaus, pcov_gaus = curve_fit(lambda x,Noise,Fano,*A: gaus(
                x,E_peak,gain,Noise,Fano, *A) + y_cont[it], 
                x, 
                y_savgol[it], 
                p0=params_gaus[it], 
                sigma=uncertainty[it], 
                maxfev=cycles) #Clean Gaus
        except:
            print("WARNING:\nFit failed for spec {}".format(it))
            popt_gaus = np.zeros(E_peak.shape[0]+2,dtype="int32")
        
        ############################################################################
        # Determine boundaries of fitted Noise and Fano for which to print warning #
        ############################################################################

        #if not (0<popt_gaus[0]<200)|(0<popt_gaus[1]<0.2): 
        #    print(
        #            "  -  Non-physical value of fitted noise {} and fano {}".format(
        #        popt_gaus[1],popt_gaus[0]))

        ############################################################################
            
        ######################################
        # Exclude global spectrum from frame #
        ######################################
        
        if it:

            ########################################################
            # Put combined area's peaks belonging to corresponding #
            # elements into dictionary only taking positive area's #
            ########################################################
            
            Area_dict_gaus={i: [p for p in popt_gaus[2:][Z_dict[i]] if p>0]\
            #Area_dict_gaus={i: sum(popt_gaus[2:][Z_dict[i]][popt_gaus[2:][Z_dict[i]]>0])\
                    for i in [*Z_dict][:-1]} #-1 excludes last key "Unmatched"

            ########################################################

            frame.append(Area_dict_gaus) #Append dictionaries in frame list chronologically

        ######################################
        
        y_gaus = gaus(x,E_peak,gain,*popt_gaus)+y_cont[it]

        


        #############################################################################
        #Residuals devided by sigma y_i/y_savgol or eventual 1 in case of sigma = 0 #
        #############################################################################

        residuals_gaus = (y_savgol[it]-y_gaus)/np.maximum(uncertainty[it],1) 

        #############################################################################

        ############################################
        #Residual sum squares, in this case chi-sq #
        ############################################

        ss_res_gaus= np.sum(np.square(residuals_gaus)) 

        ############################################

        rchisq_gaus=ss_res_gaus/(len(y_savgol[it])-len(popt_gaus)) #Reduced chi-sq

        # print("\rReduced chi-sq Gaus_%s: %.2f"%(it+1,rchisq_gaus))

        # s_params = np.sqrt(np.diag(pcov_gaus)) #Standard error params
        # print("\rStandard error params:",s_params)
        # FWHM_gaus=2.355*np.sqrt((np.square(popt_gaus[0]/2.3548))+(3.85*popt_gaus[1]*E_peak)) #(Divide /gain to get FWHM expressed in channels)
        # print("\rFWHM_gaus (eV):",FWHM)
        

        ################### END OF GAUSS FIT ####################

        ''' Voigt Fit '''
        # popt_voigt, pcov_voigt = curve_fit(lambda x,Noise,Fano,gamma,*A: voigt(x,E_peak,Noise,Fano,gamma,*A) + y_cont[it], x, y_savgol[it], p0=params_voigt[it], sigma=uncertainty[it], maxfev=1000) #Clean Voigt + clip sigma to 1 for 0 values
        #
        # if not (0<popt_voigt[0]<200)|(0<popt_voigt[1]<0.2): #Determine boundaries of fitted Noise and Fano for which to print warning
        #     print("  -  Non-physical value of fitted parameter")
        # if it: #Exclude global spectrum from frame
        #     Area_dict_voigt={i: sum(popt_voigt[3:][Z_dict[i]][popt_voigt[3:][Z_dict[i]]>0]) for i in [*Z_dict][:-1]} #Put combined area's peaks belonging to corresponding elements into dictionary
        #     frame.append(Area_dict_voigt) #Append dictionaries in frame list chronologically
        #
        # print("\rParams Voigt (Noise Fano gamma):",*popt_voigt[:3])
        # print("\rVoigt peak area's:",popt_voigt[3:])
        #
        # y_voigt = voigt(x,E_peak,*popt_voigt)+y_cont[it]
        # y_voigt_single = np.asarray([voigt(x,E_peak[i],*popt_voigt[[0,1,2,3+i]]) for i in range(E_peak.size)]) + y_cont[it]
        #
        # residuals_voigt = (y_savgol[it]-y_voigt)/np.maximum(uncertainty[it],1) #Residuals devided by sigma y_i/y_savgol or eventual 1 in case of sigma = 0
        # ss_res_voigt= np.sum(np.square(residuals_voigt)) #Residual sum squares, in this case chi-sq
        # rchisq_voigt=ss_res_voigt/(len(y_savgol[it])-len(popt_voigt)) #Reduced chi-sq
        # print("\rReduced chi-sq Voigt_%s: %.2f"%(it+1,rchisq_voigt))
        #
        # s_params_voigt = np.sqrt(np.diag(pcov_voigt)) #Standard error params
        # print("\rStandard error params Voigt:",s_params_voigt)
        # FWHM_voigt=2.355*np.sqrt((np.square(popt_voigt[0]/2.3548))+(3.85*popt_voigt[1]*E_peak)) #(Divide /gain to get FWHM expressed in channels)
        # print("\rFWHM_voigt (eV):",FWHM)

        #############################
        # FROM HERE TO PLOT SPECTRA #
        #############################
        
        if Constants.SAVE_FIT_FIGURES and (it+1)%Constants.SAVE_INTERVAL==0:
        #if (it+1)%500==0:
            
            y_gaus_single = np.asarray(
                [gaus(x,E_peak[i],gain,*popt_gaus[[0,1,2+i]]) for i in range(
                        E_peak.size)]) + y_cont[it]

            fig,ax=plt.subplots(2,gridspec_kw={'height_ratios': [3,1]})
            ax[0].set_title('Element deconvolution',fontsize=16)
            plt.setp(ax, xlim=(x.min(),x.max())) #Set xlim on both axes
            
            ax[0].text(
                    14000,
                    np.max(y_savgol[it]),
                    "$\chi^2$: %.3f"%rchisq_gaus,
                    fontsize=15,
                    bbox={'facecolor':'white', 'edgecolor':'None', 'pad':10})
            ax[0].semilogy(x,y_cont[it],linewidth=1,zorder=1,label='Continuum')
            ax[0].plot(x,y_savgol[it],linewidth=1,zorder=1, label='Counts')
            ax[0].plot(x,y_gaus,label='Fit')
            ax[0].set_ylim([1,y_savgol[it].max()])
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
                    ax[0].axvline(
                            x=E_peak[j], 
                            color='m', 
                            linewidth=1, 
                            zorder=2, 
                            label='Found peaks')
                    ax[0].plot(x, y_gaus_single[j], color='k', linewidth=1, zorder=3)
                    ax[0].fill_between(
                            x, 
                            y_cont[it], 
                            y_gaus_single[j], 
                            facecolor=color[element.index(i)], 
                            alpha=0.5,
                            zorder=3)

                    #################################################################
                    # Make sure if double assigned peak latter is plotted slightly  #
                    # higher so no overlap occurs in plotting element indication    #
                    #################################################################

                    if i in dupl_key[:int(len(dupl_key)/2)] and j in dupl_value: 
                        ax[0].text(
                                E_peak[j]+25, 
                                y_peak[it][j]*1.35, 
                                EnergyLib.ElementList[i], 
                                fontsize=7)

                    #################################################################

                    ##############################################
                    # Plot element indication at standard height #
                    ##############################################

                    else: 
                        ax[0].text(
                                E_peak[j]+25, 
                                y_peak[it][j]*1.15, 
                                EnergyLib.ElementList[i], 
                                fontsize=7)

                    ##############################################

                ###############################################################

            #######################################################################

            for i in [*Z_dict['Unmatched']]:
                ax[0].axvline(
                        x=E_peak[i], 
                        color='m', 
                        linestyle='dashed',
                        linewidth=1,
                        zorder=2,
                        label='Unmatched peaks')

            ax[1].set_ylim([-2,2])
            ax[1].set_yticks([-2,-1,0,1,2])
            ax[1].plot(x, residuals_gaus, linewidth=1)
            ax[1].axhline(y=0, color='k')
            ax[1].set_xlabel('Energy (eV)')
            ax[0].set_ylabel('Counts')
            ax[1].set_ylabel('Residuals / $\sigma$')
            handles,labels = ax[0].get_legend_handles_labels()
            by_label = dict(zip(labels,handles))
            ax[0].legend(by_label.values(), by_label.keys(),prop={'size': 7})

            plt.savefig(
                    os.path.join(figures_path,"Fit_{}.png".format(it+1)),
                    dpi=600,
                    format="png")
            plt.close()
            del y_gaus_single

        ############# END OF SAVE BLOCK #############

        time_avg = (timeit.default_timer()-time0)/(it+1) 
        print("Avg time: {0:0.2f}".format(time_avg),end="\r")

        #print("\rFitting spectrum: %s of %s (%.2f%%)  time left: %i min"%(it+1,len(y_savgol),
        #    100*(it+1)/len(y_savgol),time_avg*(len(y_savgol)-it)/60),end='',flush=True)

        del popt_gaus
        del y_gaus
        del residuals_gaus
        del ss_res_gaus
        del rchisq_gaus

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

    return 0

""" Model functions ------------------------------------------------------------"""

def gaus(x, E_peak, gain, Noise, Fano, *A):
    
    """ Sum changes although summing over rows automatically back to one row 
    array and hence only x needs to be Transposed instead of A,E_peak and 
    s --- A using gausfit seperated from params concatenate ndarray and put 
    in solo tuple, so not ndarray within tuple like when calling specifically 
    funcs and hence does not need to be unpacked """

    s = np.sqrt(np.square(Noise/(2*np.sqrt(2*np.log(2))))+3.85*Fano*E_peak)
    #s = np.sqrt(np.square(Noise/2.3548)+3.85*Fano*E_peak)
    return gain*np.sum(
            A/(s*np.sqrt(2*np.pi))*np.exp(
                -np.square(x[:,None]-E_peak)/(2*np.square(s))
                ),1
            )

"""-----------------------------------------------------------------------------"""
            
def voigt(x, E_peak, Noise, Fano, gamma, *A):

    """ Both sigma and gamma energy dependance E_peak, sigma since 
    direct function and gamma since divided by sigma """

    s = np.sqrt(np.square(Noise/(2*np.sqrt(2*np.log(2))))+3.85*Fano*E_peak)
    return np.sum(
            A/(s*np.sqrt(2*np.pi))*np.real(
                wofz(((x[:,None]-E_peak)+1j*gamma)/(s*np.sqrt(2)))
                ),1
            )

"""-----------------------------------------------------------------------------"""

def findpeak(
        y_savgol,
        y_cont,
        zero,
        gain,
        energies,
        path,
        width=9,
        r=2): 

    """
    Input:
        y_savgol        (files,channels)       <class 'numpy.ndarray'>     
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

    """ Pay attention to pass to findpeak function the CLIPPED sum spectrum 
    Obtained by summing each spectrum in the dataset by clipping them at 1 """

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

    y_global = np.sum(y_savgol.clip(1),0)
    #y_global = Constants.MY_DATACUBE.sum
    #y_global = savgol_filter(Constants.MY_DATACUBE.mps,5,3)
    #y_cont[0] = 0.75*peakstrip(y_global,24,5,5,3)

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
                    (y_global>Constants.PEAK_TOLERANCE*y_cont[0])) 

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

    E_lib = np.asarray(
            [(
                xlib.LineEnergy(i, xlib.KA1_LINE)*1000,
                xlib.LineEnergy(i, xlib.KB_LINE)*1000,
                xlib.LineEnergy(i, xlib.LA1_LINE)*1000,
                xlib.LineEnergy(i, xlib.LB_LINE)*1000) for i in range(5,84)
                ]) 

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

    double_match = np.flatnonzero(E_mesh[:,:2,:].any(0).all(0)) 

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

    KA_correction = KB_double[KA_present]!=np.roll(KA_double[KA_present],1)

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
    #plt.xlim([energies.min(),energies.max()])
    #plt.xlim([2000,16000])
    plt.ylim([10e-3,y_global.max()])
    spectrum=0
    plt.plot(energies,y_global)
    plt.plot(energies,y_conv)
    plt.plot(energies,(np.sqrt(var_conv)*r))
    plt.plot(energies,y_cont[spectrum])
    plt.semilogy(energies,Constants.PEAK_TOLERANCE*y_cont[spectrum])
    
    E_peak = zero + gain * x_peak
    for j in E_peak:
        plt.axvline(x=j)
    plt.savefig(path,format="png",dpi=600)

    return x_peak, Z_dict


class Interrupt(Exception):
    pass


class SingleFit():

    def __init__(__self__,path):
        __self__.iterator = 0
        __self__.energies = Constants.MY_DATACUBE.energyaxis*1000
        __self__.intercept = __self__.energies[0]
        __self__.slope = Constants.MY_DATACUBE.gain*1000
        __self__.counts = Constants.MY_DATACUBE.matrix.reshape(
                -1,Constants.MY_DATACUBE.matrix.shape[-1])
        __self__.continuum = Constants.MY_DATACUBE.background.reshape(
                -1,Constants.MY_DATACUBE.background.shape[-1])
        
        ################
        # Prepare data #
        ################

        __self__.bar = Busy(len(__self__.counts),0)
        __self__.bar.update_text("Preparing data...")
        for i in range(len(__self__.counts)):
            __self__.bar.updatebar(i)
            __self__.counts[i] = savgol_filter(__self__.counts[i],5,3).clip(0)

        del Constants.MY_DATACUBE.matrix
        del Constants.MY_DATACUBE.background
        __self__.SUM = np.sum(__self__.counts,0)

        #########################################################################
        # Continuum of global sum (sum of all prepared data) must be parsed to  #
        # findpeak function. The clipped global spectrum is calculated inside   #
        # the function                                                          #
        #########################################################################

        if Constants.MY_DATACUBE.config["bgstrip"] == "SNIPBG":
            global_continuum = peakstrip(__self__.SUM,24,5,5,3)
        elif Constants.MY_DATACUBE.config["bgstrip"] == "Polynomial":
            global_continuum = SpecMath.polfit_batch(
                    __self__.counts,custom_global_spec=__self__.SUM)[0]

        #global_continuum = peakstrip(copy.deepcopy(__self__.SUM),24,5,5,3)
        __self__.continuum = np.insert(__self__.continuum,0,global_continuum, axis=0)

        #########################################################################

        __self__.bar.destroybar()

        ################

        __self__.fit_path = os.path.join(path,"Fit_Chunk_1.npy")

        #start = timeit.default_timer()
        #dimension, energies, intercept, slope, counts = getData(spectrum_path)
        #stop = timeit.default_timer()
        #print("Data: ", stop - start)

        #print("BORIS")
        #print(counts.shape)
        #print(type(counts))

        # start2 = timeit.default_timer()
        # continuum = SNIPBG(counts,11,3,24)
        # stop2 = timeit.default_timer()
        # print("SNIPGB: ", stop2 - start2)
        # start1 = timeit.default_timer()
        # continuum = polfit(counts)
        # stop1 = timeit.default_timer()
        # print("Polynomial: ", stop1 - start1)

        ########################

    def run_fit(__self__):
        
        figures_path = os.path.join(SpecRead.output_path,"Fit plots","Single")
        try: os.makedirs(figures_path)
        except: pass
        peaks, matches = Constants.MATCHES
        percent = __self__.iterator/len(__self__.counts)*100
        __self__.bar = Busy(len(__self__.counts),0)
        __self__.bar.add_abort(multiprocess=False)
        fitted_spec = gausfit(
                __self__.energies,
                __self__.counts,
                __self__.continuum,
                peaks,
                matches,
                __self__.intercept,
                __self__.slope,
                __self__.fit_path,
                figures_path,
                __self__.SUM,
                __self__.iterator,
                bar = __self__.bar)
        __self__.bar.destroybar()

    def locate_peaks(__self__,add_list=None,path="./"):

        peaks, matches = findpeak(
                __self__.counts,
                __self__.continuum,
                __self__.intercept,
                __self__.slope,
                __self__.energies,
                path=path)

        ########################
        # Add element manually #
        ########################

        if add_list:
            for el in add_list:

                element_a = EnergyLib.Energies[el]*1000
                element_b = EnergyLib.kbEnergies[el]*1000

                logger.debug("Element {}, {}".format(element_a,element_b))

                elka_peak = SpecMath.setROI(
                        element_a,
                        __self__.energies/1000,__self__.SUM,{"gain":__self__.slope/1000})
                elkb_peak = SpecMath.setROI(
                        element_b,
                        __self__.energies/1000,__self__.SUM,{"gain":__self__.slope/1000})

                logger.debug("setROI output: {}".format(elka_peak))
                logger.debug("setROI output: {}".format(elkb_peak))

                el = [[el,int((elka_peak[0]+elka_peak[1])/2),
                        int((elkb_peak[0]+elkb_peak[1])/2)]]

                try: peaks, matches = add_elements(peaks,matches,el)
                except: logger.warning("Could not add element {} to chunk".format(el))

        Constants.MATCHES = peaks, matches
        logger.info("Elements being fitted: {}".format(matches))
        return peaks, matches


class MultiFit():
        
    def __init__(__self__,path):
        __self__.workers = []
        __self__.name = Constants.MY_DATACUBE.name
        __self__.save_plots_path = os.path.join(SpecRead.output_path,"Fit plots")
        __self__.results = multiprocessing.Queue()
        __self__.global_iterator = multiprocessing.Value('i',0)
        __self__.global_iterator.value = 0
        __self__.work_done = multiprocessing.Value('i',0)
        __self__.work_done.value = 0
        __self__.cores = int(Constants.CPUS)-1
        __self__.path = path
        __self__.energies = Constants.MY_DATACUBE.energyaxis*1000
        __self__.intercept = __self__.energies[0]
        __self__.slope = Constants.MY_DATACUBE.gain*1000
        __self__.counts = Constants.MY_DATACUBE.matrix.reshape(
            -1,Constants.MY_DATACUBE.matrix.shape[-1])
        __self__.continuum = Constants.MY_DATACUBE.background.reshape(
            -1,Constants.MY_DATACUBE.background.shape[-1])
        __self__.bar = Busy(len(__self__.counts),0)
        __self__.bar.update_text("Preparing data...")

        ###############################################################
        # Smooths the data (renders peak detection easier) and create #
        # the sum spectrum of the soothed data                        #
        ###############################################################
        
        for i in range(len(__self__.counts)):
            __self__.bar.updatebar(i)
            __self__.counts[i] = savgol_filter(__self__.counts[i],5,3).clip(0)
        __self__.SUM = np.sum(__self__.counts,0)

        __self__.bar.destroybar()
        ###############################################################

    def eat_data(__self__):
        __self__.bar.update_text("Eating data...")
        __self__.bar.updatebar(0)

        counts, continuum,block = [],[],[]
        if __self__.cores == 1: 
            print("Only one core")
            return
        else:
            __self__.cores -= 1
            bite_size = 0
            while bite_size < 500:
                bite_size = int(__self__.counts.shape[0]/__self__.cores)
                leftovers = int(__self__.counts.shape[0]%__self__.cores)
                print("bite size: ",bite_size,"leftovers ",leftovers)
                __self__.cores -= 1
            __self__.cores+=1
            __self__.bite_size = bite_size
            __self__.leftovers = leftovers

            __self__.bar.progress["max"] = bite_size*__self__.cores
                
            #########################################
            # Splits the data in pieces accordingly #
            # Available RAM is also considered      #
            #########################################

            spec = 0
            for k in range(__self__.cores):
                print("Block ",k)
                for i in range(bite_size):
                    __self__.bar.updatebar(spec)
                    counts.append(__self__.counts[spec])
                    continuum.append(__self__.continuum[spec])
                    spec += 1
                data = (counts,continuum)
                block.append(data)
                counts, continuum = [],[]
            if leftovers >= 1:
                __self__.bar.update_text("Eating leftovers...")
                __self__.bar.updatebar(0)
                __self__.bar.progress["max"] = leftovers
                for i in range(leftovers):
                    __self__.bar.updatebar(i)
                    counts.append(__self__.counts[spec])
                    continuum.append(__self__.continuum[spec])
                    spec += 1
                leftovers = (counts,continuum)

            #########################################

            #######################################################################

            block = np.asarray(block)
            print("Data blocks shape: ",block.shape)

            #######################################################################

        return block, leftovers
    
    def locate_peaks(__self__,add_list=None,path="./"):

        if Constants.MY_DATACUBE.config["bgstrip"] == "SNIPBG":
            global_continuum = peakstrip(__self__.SUM,24,5,5,3)
        elif Constants.MY_DATACUBE.config["bgstrip"] == "Polynomial":
            global_continuum = SpecMath.polfit_batch(
                    __self__.counts,
                    custom_global_spec=__self__.SUM)[0]

        #global_continuum = peakstrip(copy.deepcopy(__self__.SUM),24,5,5,3)
        continuum = np.insert(__self__.continuum,0,global_continuum, axis=0)

        peaks, matches = findpeak(
                __self__.counts,
                continuum,
                __self__.intercept,
                __self__.slope,
                __self__.energies,
                path)

        ########################
        # Add element manually #
        ########################
        
        if add_list:
            for el in add_list:
            
                element_a = EnergyLib.Energies[el]*1000
                element_b = EnergyLib.kbEnergies[el]*1000

                logger.debug("Element {}, {}".format(element_a,element_b))

                elka_peak = SpecMath.setROI(
                        element_a,
                        __self__.energies/1000,__self__.SUM,{"gain":__self__.slope/1000})
                elkb_peak = SpecMath.setROI(
                        element_b,
                        __self__.energies/1000,__self__.SUM,{"gain":__self__.slope/1000})

                logger.debug("setROI output: {}".format(elka_peak))
                logger.debug("setROI output: {}".format(elkb_peak))

                el = [[el,int((elka_peak[0]+elka_peak[1])/2),
                        int((elkb_peak[0]+elkb_peak[1])/2)]]

                try: peaks, matches = add_elements(peaks,matches,el)
                except: logger.warning("Could not add element {} to chunk".format(el))

        Constants.MATCHES = peaks, matches
        logger.info("Elements being fitted: {}".format(matches))
        return peaks, matches

    def check_progress(__self__):
        __self__.bar.update_text("Fitting data...")
        tot = int(__self__.cores*__self__.bite_size)+__self__.leftovers
        while __self__.global_iterator.value < tot and \
                __self__.work_done.value < len(__self__.workers):
            __self__.bar.updatebar(__self__.global_iterator.value)
            percent = __self__.global_iterator.value/tot*100
            __self__.bar.update_text("Fitting data... {0:0.2f}%".format(percent))
        try: 
            __self__.bar.destroybar()
            return 0
        except: 
            return 1

    def launch_workers(__self__):

        del Constants.MY_DATACUBE.matrix
        del Constants.MY_DATACUBE.background
        
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

            __self__.bar.update_text("Polling chunks...")

            counts, continuum = np.asarray(copy.deepcopy(block),dtype="int32")
            del block
            
            counts = np.asarray(counts,dtype="int32")

            it += 1
            chunk += 1
            p = multiprocessing.Process(target=find_and_fit,
                    name="chunk_{}".format(chunk),
                    args=(
                        (counts,continuum),
                        __self__.intercept,
                        __self__.slope,
                        __self__.path,
                        __self__.save_plots_path,
                        chunk,
                        __self__.results,
                        __self__.energies,
                        __self__.global_iterator,
                        __self__.work_done,
                        __self__.SUM,
                        peaks,
                        matches))

            __self__.workers.append(p)
            del counts, continuum
        del bites

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
                        __self__.slope,
                        __self__.path,
                        __self__.save_plots_path,
                        chunk,
                        __self__.results,
                        __self__.energies,
                        __self__.global_iterator,
                        __self__.work_done,
                        __self__.SUM,
                        peaks,
                        matches))

            __self__.workers.append(p)

        ######################################

        workers_count=0
        __self__.bar.add_abort(__self__.workers)
        for p in __self__.workers:
            workers_count+=1
            print("\nPolling chunk ", workers_count)
            __self__.bar.updatebar(workers_count)
            p.daemon = True
            p.start()
        
        __self__.bar.progress["max"]= \
                int(__self__.cores*__self__.bite_size)+__self__.leftovers
        __self__.bar.updatebar(0)
        __self__.check_progress()
    
        for i in range(chunk):
            data = __self__.results.get()
            partial_.append(data)
        
        for p in __self__.workers:
            if p.exitcode !=0:
                p.join()

        return partial_ 

def find_and_fit(
        data,
        intercept,
        slope,
        path,
        plots_save_path,
        chunk,
        results,
        energies,
        iterator,
        work_done,
        global_spec,
        peaks,
        matches):

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
        iterator; <Synchronized> - counter to verify processes progress
        global_spec; <1D-array> - summation derived spectrum
        clipped_global_spec; <1D-array> - obtained by summing the clipped data (clipped to 1)
    """
    
    #####################################################################################
    # regardless of the continuum mode selected by the user, here, the SNIPBG           #
    # method is always used. It doen's matter much, since the global spectrum in the    #
    # chunks is always overlooked                                                       #
    #####################################################################################

    counts, continuum = np.asarray(data[0]), np.asarray(data[1])
    global_continuum = peakstrip(global_spec,24,5,5,3)
    continuum = np.insert(continuum,0,global_continuum, axis=0)

    #####################################################################################

    print("Chunk {} data size: ".format(chunk),convert_bytes(counts.nbytes))
    print("Chunk {} data size (cont): ".format(chunk),convert_bytes(continuum.nbytes))

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
            global_spec,
            iterator,
            bar=None,
            work_done=work_done,
            results=results)
    return 0

def add_elements(peaks,matches,element_list):
    
    """ element: 2D list with element Z and peak position """

    print("INFO:\nAdding element...")
    iterator = 0
    for element in element_list:
        if element[0] not in matches:
            peaks = np.insert(peaks,-1,element[1])
            peaks = np.insert(peaks,-1,element[2])
            matches[element[0]] = [
                np.where(peaks==element[1])[0][0],
                np.where(peaks==element[2])[0][0]]
        un_ = matches["Unmatched"]
        matches.pop("Unmatched")
        matches = {int(k) : v for k, v in matches.items()}
        matches["Unmatched"] = un_

    return peaks, matches

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
        frames_path) if npy.lower().endswith(".npy")]
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
    element_list = [EnergyLib.ElementList[key] for key in elements]

    #################################################################
    # reload cube because data is changed somewhere down the road   #
    # making a copy can cost a lot of memory (large cubes +/- 3Gb)  #
    #################################################################

    from SpecRead import cube_path
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

    logger.info("\n"+"-"*5+"Starting image builder"+"-"*5)
    x,y,iteration,frmcount = 0,0,0,0
    start_x, start_y = 0,0
    bar.updatebar(0)
    bar.progress["max"]=len(elements)
    bar.update_text("Building images - {}/{}".format(0,len(frames)))
    for frmfile in frames:
        frmcount += 1
        bar.update_text("Building images - {}/{}".format(frmcount,len(frames)))
        print("\nFrame {}".format(frmcount))
        frame = np.load(
                os.path.abspath(os.path.join(frames_path,frmfile)),
                allow_pickle=True)
        size = frame.shape[0]*len(element_list)
        print("Size: ",frame.shape[0]*len(element_list))
        for key in elements:
            maximum_counts = 0
            line = 0
            for c in range(frame.shape[0]):
                iteration+=1
                percent = iteration/size
                print("Map {}: {}, pos {} x {}\t {:0.2f} percent complete...".format(
                    maps_count,element_list[maps_count],x,y,percent*100),end="\r")
                try:
                    for line in range(len(frame[c][key])):
                        try: 
                            el_maps[x][y][line][maps_count] = frame[c][key][line]
                        except: 
                            el_maps[x][y][line][maps_count] = 0
                except:
                    pass
                pos = refresh_position(x,y,Constants.MY_DATACUBE.dimension)
                x,y = pos[0],pos[1]
            x,y = start_x, start_y
            maps_count += 1
            bar.updatebar(maps_count)
            
        iteration, maps_count = 0,0
        print("\npos: ",pos)
        start_x, start_y, x, y = pos[0], pos[1], pos[0], pos[1]

    ####################################################
    
    ##########################################################
    # split images into individual maps and pack to datacube #
    ##########################################################
    try:
        for key in Constants.MATCHES[1]:
            if key != "Unmatched":
                peak1 = Constants.MATCHES[0][Constants.MATCHES[1][key][0]]
                try:
                    peak2 = Constants.MATCHES[0][Constants.MATCHES[1][key][1]]
                except: peak2 = 0
                Constants.MY_DATACUBE.ROI[EnergyLib.ElementList[key]] = peak1, peak2
    except:
        print("Running module alone, MATCHES variable may have not been declared.")
    print("Done. Splitting and saving...")
    print(el_maps.shape)
    split_and_save(Constants.MY_DATACUBE,el_maps,element_list,
            force_alfa_and_beta=True)
    bar.destroybar()

    ##########################################################
    
def fit_wiz(ordered_elements_list=None):
    
    els = ordered_elements_list

    ##################################################
    # List all files in Fit Chunks, divided by chunk #
    ##################################################

    paths = [i for i in os.listdir(SpecRead.output_path) if "Fit_Chunk" \
            in i and os.path.isdir(os.path.join(SpecRead.output_path,i))]
    files = {}
    for i in range(len(paths)):
        paths[i] = os.path.abspath(os.path.join(SpecRead.output_path,paths[i]))
        files["Chunk_{}".format(i)] = \
                [os.path.join(paths[i],f) for f in os.listdir(paths[i]) \
                if f.lower().startswith("spec")]

    ##################################################
    
    fit = np.zeros(1024)
    for key in files.keys():
        for f in files[key]:
            spectrum = np.load(f,allow_pickle=True)
            print("Spec",f,"No of elements: ",spectrum.shape[0])
            for element in range(spectrum.shape[0]):
                fit += spectrum[element]
            del spectrum

    E_axis = Constants.MY_DATACUBE.energyaxis
    plt.semilogy(E_axis,fit)
    plt.semilogy(E_axis,Constants.MY_DATACUBE.sum,color="blue",label="Sum")
    plt.semilogy(E_axis,Constants.MY_DATACUBE.sum_bg,color="green",label="Sum BG")
    plt.legend()
    plt.show()
    return 0

if __name__.endswith('__main__'):

    """ Spectrum file path """
    #spectrum_path = Path(
    #os.path.join(SpecRead.__PERSONAL__,"Example_Data","Training Data 2"))
    # spectrum_path = Path.cwd() / "L_Cu_Sn_As_Zn_Ni_Fe_Co_Sb_Ag_Bi_Full"
    # spectrum_path = Path.cwd() / 'dippintofabio'
    # spectrum_path = Path.cwd() / 'dippintofabio_1_1'

    """ Save fit file path """
    # fit_path = Path.cwd() / 'Frame/Training_Data_2'
    # fit_path = Path.cwd() / 'Frame/dippintofabio'
    # fit_path = Path.cwd() / 'Frame/dippintofabio_gaus'
    
    import Constants
    import pickle
    import time

    try: mode = sys.argv[-1]
    except: mode = None
    
    ####################
    name = "cuoio1"
    ####################

    cube_path = r"C:\Users\sergi\Documents\XISMuS\output\{0}\{0}.cube".format(name)
    if os.path.exists(cube_path):
        cube_file = open(cube_path,'rb')
        Constants.MY_DATACUBE = pickle.load(cube_file)
        SpecRead.setup_from_datacube(Constants.MY_DATACUBE,
                {"{}".format(name):Constants.MY_DATACUBE.path})
        cube_file.close()
    fit_path = SpecRead.output_path
    print("Dataset path: ",fit_path)
    
    ###################################################
    # Cuts lead and tail zeros basing on sum spectrum #
    ###################################################

    #lead, tail = Constants.MY_DATACUBE.cut_zeros()

    ###################################################

    ###################
    # MULTIPROCESSING # 
    ###################
    
    if mode == "-multi":

        workers = MultiFit(fit_path)
        peaks, matches = workers.locate_peaks()
        print("We have found the following elements: ")
        for key in matches.keys():
            if key!="Unmatched":
                print("{}".format(key),end=" ")
        print("LAUNCHING PROCESSES\n")
        workers.launch_workers()
        print("\nPROCESSES DONE\n")

    ###################

    #################
    # SINGLE THREAD #
    #################
    
    if mode == "-single":

        print("starting fit")
        np.set_printoptions(threshold=False)
        energies = Constants.MY_DATACUBE.energyaxis*1000
        intercept = energies[0]
        slope = Constants.MY_DATACUBE.gain*1000
        counts = Constants.MY_DATACUBE.matrix.reshape(
                -1,Constants.MY_DATACUBE.matrix.shape[-1])
        continuum = Constants.MY_DATACUBE.background.reshape(
                -1,Constants.MY_DATACUBE.background.shape[-1])
        print("\t",Constants.MY_DATACUBE.matrix.shape)
        #print("\t",Constants.MY_DATACUBE.background.shape,"\n")

        global_cont = peakstrip(Constants.MY_DATACUBE.sum,24,5,5,3)
        continuum = np.insert(continuum,0,global_cont, axis=0)

        for i in range(len(counts)):
            counts[i] = savgol_filter(counts[i],5,3)

        #print(intercept,slope)
        #print(len(energies))
        #print(energies.shape)
        #print("\tCounts")
        #print(counts.shape)
        #print(type(counts))

        path = SpecRead.output_path
        workers = SingleFit(path)
        workers.locate_peaks()
        print("\nPROCESSES DONE\n")
        
    #################

    #fit_wiz()
    build_images(fit_path)

    #dimension = [110,130]
    #start5 = timeit.default_timer()
    #getImage(fit_path,dimension)
    #stop5 = timeit.default_timer()
    #print("Image: ", stop5 - start5)
