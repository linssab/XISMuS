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

import Constants
Constants.LOGGER.info("In AdvFit: Importing Elements...")
from Elements import *
try: 
    import xraylib as xlib
    Constants.LOGGER.info("In AdvFit: Imported xraylib!")
except: Constants.LOGGER.info("In AdvFit: Failed to import xraylib!")
import numpy as np
Constants.LOGGER.info("In AdvFit: Importing SciPy...")
from scipy.optimize import least_squares
from scipy.optimize import curve_fit

SIGMA = lambda noise, fano, peaks: np.sqrt(((noise/2.3548200450309493)**2)+3.85*fano*peaks)

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

        rad_rates = [pool_lines[line][1] for line in pool_lines.keys()]
        peaks = [energies[i][0] for i in range(len(energies))]
        indexes = np.asarray([e[1] for e in energies])

        lines[element_pool[i]] = list(pool_lines.keys())
        element[element_pool[i]]["indexes"] = np.asarray(indexes,dtype=np.int32)
        element[element_pool[i]]["peaks"] = np.asarray(peaks,dtype=np.float32)
        element[element_pool[i]]["rad_rates"] = np.asarray(rad_rates,dtype=np.float32)

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
                np.array(spectrum[indexes]*p0*Constants.PEAK_TOLERANCE*gain)],
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
                np.array(spectrum[indexes]*p0*Constants.PEAK_TOLERANCE*gain)],
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

