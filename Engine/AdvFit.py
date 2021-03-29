#################################################################
#                                                               #
#          Advanced fit                                         #
#                        version: 2.2.0 - Mar - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import Constants
from Elements import *
import xraylib as xlib
import numpy as np
from scipy.optimize import least_squares
from scipy.optimize import curve_fit
import csv

SIGMA = lambda noise, fano, peaks: np.sqrt(((noise/2.3548200450309493)**2)+3.85*fano*peaks)

class CsvWriter:
    def __init__(__self__,data,path):
        lines = []
        __self__.ElementData = {}
        for element in data.keys(): 
            __self__.ElementData[element] = {}
            __self__.ElementData[element]["Element"] = element
            ellines = list(data[element]["Lines"])
            lines.extend(ellines)
            for i in range(len(ellines)):
                __self__.ElementData[element][ellines[i]] = data[element]["Areas"][i]
            i = 0
            lines = list(set(lines))
        fields = ["Element"]
        fields.extend(lines)
        fields.append("Area")
        __self__.fields = fields
        __self__.path = path

    def dump(__self__):
        with open(__self__.path, mode="w") as f:
            writer = csv.DictWriter(f, fieldnames=__self__.fields)
            writer.writeheader()
            for element in __self__.ElementData.keys():
                writer.writerow(__self__.ElementData[element])
        f.close()

def work_results(popt, element_pool, element_params, lines):
    i = 0
    results = {}
    parameters = {}
    for key in sorted(element_pool):
        results[key] = {}
        parameters[key] = {}
        lines_no = len(lines[key])
        results[key]["Areas"] = np.asarray(popt[i:i+lines_no])
        results[key]["Lines"] = lines[key]
        parameters[key]["indexes"] = element_params["indexes"][i:i+lines_no]
        parameters[key]["peaks"] = element_params["peaks"][i:i+lines_no]
        parameters[key]["rad_rates"] = element_params["rad_rates"][i:i+lines_no]
        i+=lines_no
    return results, parameters

def work_elements(e_axis, pool, gain, global_spec, split=0):
    """ e_axis: energy axis in eV; 1D-array
        element_pool: elements and lines; python dictionary
        gain: calibration gain in eV
        global_spec: reference spectrum for adjusting peaks; 1D-array """

    def nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx], idx

    element_pool = list(pool["elements"].keys())
    lines_pool = {element:pool["elements"][element] for element in pool["elements"].keys()}

    element = {}
    lines = {}
    for i in range(len(element_pool)):
        element[element_pool[i]] = {}
        line_names = pool["elements"][element_pool[i]]
        pool_lines = {key:ALL_LINES[xlib.SymbolToAtomicNumber(element_pool[i])][key] for key in line_names}
        # NOTE: pool_lines[line] has [0] energy in KeV and [1] radiative rate

        duplicates = []
        energies = [idx for idx in [nearest(e_axis, 1000*pool_lines[line][0]) for line in line_names]]

        """
        for j in range(len(line_names)-1):
            if energies[j+1][0]==energies[j][0] or \
                    abs(energies[j+1][0]-energies[j][0]) < gain*2:
                duplicates.append(j+1)
                del pool_lines[line_names[j+1]]
        for dp in duplicates: energies[dp] = -1
        while -1 in energies:
            energies.remove(-1)
        """

        rad_rates = [pool_lines[line][1] for line in pool_lines.keys()]
        peaks = [energies[i][0] for i in range(len(energies))]
        indexes = np.asarray([e[1] for e in energies])

        lines[element_pool[i]] = list(pool_lines.keys())
        element[element_pool[i]]["indexes"] = np.asarray(indexes,dtype=np.int32)
        element[element_pool[i]]["peaks"] = np.asarray(peaks,dtype=np.float32)
        element[element_pool[i]]["rad_rates"] = np.asarray(rad_rates,dtype=np.float32)
        #print("#"*10)
        #print(element[element_pool[i]])
        #print(lines)
        #print("#"*10)

    if split:
        return element, lines

    else:

        big_batch = {}
        big_batch["indexes"] = []
        big_batch["peaks"] = []
        big_batch["rad_rates"] = []

        """ NOTE: big_batch is ordered alphabetically, so unpacking fit results is easier
        We also return the lines dictionary, so we can get how many lines each element
        has when unpacking the fit results """

        for e in sorted(element.keys()):
            big_batch["indexes"].extend(element[e]["indexes"])
            big_batch["peaks"].extend(element[e]["peaks"])
            big_batch["rad_rates"].extend(element[e]["rad_rates"])
        big_batch["indexes"] = np.asarray(big_batch["indexes"], dtype=np.int32)
        big_batch["peaks"] = np.asarray(big_batch["peaks"], dtype=np.float32)
        big_batch["rad_rates"] = np.asarray(big_batch["rad_rates"], dtype=np.float32)

        """
        peaks_positions = findpeaks(global_spec)
        tolerance = Constants.SETROI_TOLERANCE
        peaks = big_batch["peaks"]
        indexes = big_batch["indexes"]
        rad_rates = big_batch["rad_rates"]
        print(Constants.SETROI_TOLERANCE)
        for p in range(peaks.shape[0]):
            located_peaks = e_axis[peaks_positions]
            for lc in range(len(located_peaks)):
                if peaks[p] < 4800: w = Constants.SETROI_TOLERANCE[0]
                elif peaks[p] > 12000:
                    w = Constants.SETROI_TOLERANCE[2]
                else: w = Constants.SETROI_TOLERANCE[1]
                if peaks[p]-(w*gain) < located_peaks[lc] < peaks[p]+(w*gain):
                    # checks if findpeaks peak is within acceptable range
                    # of the theoretical position.
                    # Then, checks if there is a peak previously detected there
                    print("\nPEAK CAN BE SHIFTED")
                    print(peaks[p],indexes[p],"|",located_peaks[lc],np.where(peaks==located_peaks[lc])[0])
                    doublet = np.where(peaks==located_peaks[lc])[0]
                    replace = 0
                    if doublet.size == 0: replace = 1
                    else:
                        for db in doublet:
                            if rad_rates[db] < rad_rates[p]:
                                replace += 1
                        if replace == len(doublet): replace = 1
                        else: replace = 0
                    if replace:
                        print("before",peaks[p], indexes[p])
                        big_batch["peaks"][p] = located_peaks[lc]
                        big_batch["indexes"][p] = peaks_positions[lc]
                        print("fixed",big_batch["peaks"][p], big_batch["indexes"][p])
                        #big_batch["indexes"] = np.delete(big_batch["indexes"],doublet)
                        #big_batch["rad_rates"] = np.delete(big_batch["rad_rates"],doublet)
                        #big_batch["peaks"] = np.delete(big_batch["peaks"],doublet)
        """
        return big_batch, lines

def run_spectrum(spectrum,      #spectrum to be fitted
        continuum,              #spectrum continuum
        e_axis,                 #calibrated energy axis in eV
        fano_and_noise,         #tuple with fano factor and noise contribution
        elements_parameters,    
        gain,                   #gain in eV
        sigma_array,
        p0=None):

    output = {}

    fano, noise = fano_and_noise
    indexes = elements_parameters["indexes"]
    peaks = elements_parameters["peaks"]
    rad_rates = elements_parameters["rad_rates"]
    params = [gain, noise, fano],[indexes, peaks, rad_rates],sigma_array
    try: popt, pcov = fit_peaks(e_axis, spectrum, continuum, params, p0=p0)
    except ValueError: return None 
    return popt.clip(0)

def residuals(popt, x, y, y_, parameters):
    indexes, energies, rad_rates, gain, noise, fano, s = parameters
    return GAUSS(x, energies, rad_rates, gain, noise, fano, s[indexes], popt) - (y-y_)

def GAUSS(x, E_peak, rad_rate, gain, Noise, Fano, s, *A):
    return gain*np.sum((A*rad_rate)/(s*2.5066282746310002)*np.exp(-np.square(x[:,None]-E_peak)/(2*np.square(s))),1)

def fit_peaks(e_axis, spectrum, continuum, PARAMS, p0=None,
        cycles=Constants.FIT_CYCLES):
    gain, noise, fano = PARAMS[0]
    indexes, peaks, rad_rates = PARAMS[1]
    sigma = PARAMS[-1]
    params = PARAMS[1]
    params.extend(PARAMS[0])
    params.append(PARAMS[-1]) #sigma_array
    LEASTSQ = 1

    if p0 is None:
        p0=(spectrum[indexes]*rad_rates)/(sigma[indexes]*2.5066282746310002)*np.exp(
                -np.square(e_axis[indexes]-peaks)/(2*np.square(
                    sigma[indexes]))) + continuum[indexes]

    if LEASTSQ:
        popt = least_squares(
            residuals,
            p0,
            #bounds=[np.array([-np.inf for i in range(indexes.shape[0])]),
            bounds=[np.zeros(peaks.shape[0])-1,
                np.array(spectrum[indexes]*p0*gain)],
            args=(e_axis, spectrum, continuum, params))
        pcov = 0
        popt = popt.x
    else:
        popt, pcov = curve_fit(lambda x, *A: GAUSS(
            e_axis, peaks, rad_rates, gain, noise, fano, sigma[indexes], *A) + continuum,
            e_axis,
            spectrum,
            sigma=np.sqrt(spectrum).clip(1),
            bounds=[np.zeros(peaks.size)-1,
                np.array(spectrum[indexes]*p0*gain)],
            p0=p0,
            maxfev=cycles)
    return popt, pcov

def fit_single_spectrum(CUBE,spectrum,continuum,pool):
    gain = CUBE.gain*1000
    e_axis = CUBE.energyaxis*1000
    fano, noise = CUBE.FN

    elements_parameters, lines = work_elements(
            e_axis,
            pool,
            gain, CUBE.sum)

    sigma = SIGMA(noise, fano, e_axis)

    output = run_spectrum(spectrum, continuum,
        e_axis, [fano,noise],
        elements_parameters, gain, sigma)
    if output is None: return None, None

    results, parameters = work_results(output, list(pool["elements"].keys()),
            elements_parameters, lines)

    plots = {}
    for element in results.keys():
        indexes = parameters[element]["indexes"]
        peaks = parameters[element]["peaks"]
        rad_rates = parameters[element]["rad_rates"]
        plots[element] = GAUSS(e_axis, peaks, rad_rates, gain, noise, fano, sigma[indexes],
            results[element]["Areas"])+continuum
    return results, plots

