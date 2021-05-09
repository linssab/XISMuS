#################################################################
#                                                               #
#          Linear interpolation fit approximation               #
#                        version: 2.4.0 - May - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

from .SpecRead import __PERSONAL__
from .SpecMath import *
from .AdvFit import *
from .CBooster import fast_scaling
from .ImgMath import write_image
import Engine.SpecRead as SpecRead
import Constants
from Elements import *
import numpy as np
from scipy.optimize import least_squares
from scipy.optimize import curve_fit
import time
from matplotlib.figure import Figure
from matplotlib.figure import figaspect
import sys,os,copy
import csv
import pickle
import matplotlib.pyplot as plt

SIGMA = lambda noise, fano, peaks: np.sqrt(((noise/2.3548200450309493)**2)+3.85*fano*peaks)

def work_images(CUBE, frame, element_pool, element_params, lines, shape, **kwargs):
    if "bar" in kwargs:
        bar = kwargs["bar"]
        bar.update_text("Working images...")
        bar.updatebar(0)
    fano, noise = CUBE.FN
    e_axis = CUBE.energyaxis*1000
    gain = CUBE.gain*1000
    sigma = SIGMA(noise, fano, e_axis)

    image = {}
    plots = {}
    for el in element_pool["elements"].keys(): 
        image[el] = {}
        plots[el] = np.zeros(len(lines[el]))
        for line in lines[el]:
            image[el][line] = np.zeros(shape[0]*shape[1],dtype=np.float32)
    bg = CUBE.background.flatten()
    bar.progress["maximum"] = len(frame)
    for i in range(len(frame)):
        bar.updatebar(i)
        #timer = time.time()
        if CUBE.config["bgstrip"] != "None":
            j = bg[i]
        else: j = np.zeros(shape[2])
        results, params = work_results(frame[i], list(element_pool["elements"].keys()), 
                element_params, lines)

        for element in results.keys():
            """
            #This is ridiculously slow if you have large datasets
            indexes = params[element]["indexes"]
            peaks = params[element]["peaks"]
            rad_rates = params[element]["rad_rates"]
            plots[element] += GAUSS(e_axis,
                    peaks,
                    rad_rates,
                    gain,
                    noise, fano,
                    sigma[indexes],
                    results[element]["Areas"])+j
            """
            ellines = results[element]["Lines"]
            plots[element] += results[element]["Areas"]
            for l in range(len(ellines)):
                image[element][ellines[l]][i] = results[element]["Areas"][l]*params[element]["rad_rates"][l]
            #print(f"Spec: {i}\ttime:{time.time()-timer:.4f}",end="\r")

    if CUBE.fit_config["bg"]:
        if CUBE.sum_bg.sum(0) == 0:
            try:
                cycles, window, savgol, order = CUBE.config["bg_settings"]
            except:
                cycles, window, savgol, order = Constants.SNIPBG_DEFAULTS
                continuum = peakstrip(CUBE.sum,cycles,window,savgol,order)
        else: continuum = CUBE.sum_bg
    else: continuum = CUBE.sum_bg

    # for SNIPBG != None
    spec = CUBE.matrix.reshape(-1, CUBE.matrix.shape[-1])
    bg = CUBE.background.reshape(-1, CUBE.background.shape[-1])

    bar.update_text("Hang in there...")
    bar.updatebar(0)
    bar.progress["maximum"] = len(image.keys())
    it = 0
    for el in image.keys():
        bar.updatebar(it)
        it += 1
        line_no = 0
        indexes = params[el]["indexes"]
        peaks = params[el]["peaks"]
        rad_rates = params[el]["rad_rates"]
        plots[el] =  GAUSS(e_axis,
                    peaks,
                    rad_rates,
                    gain,
                    noise, fano,
                    sigma[indexes],
                    plots[el]) + continuum
        for line in image[el].keys():
            #path = os.path.join(os.getcwd(),f"{el}_{line}.txt")
            #p = indexes[line_no] 
            #print(el,line,"max",image[el][line].max(),"p=",p)
            #f = open(path,"w")
            #spec_no = 0
            #for value in image[el][line]:
            #    counts = spec[spec_no][p]-bg[spec_no][p]
            #    f.write(f"{value}\t{counts}\n")
            #    spec_no += 1
            #f.close()
            image[el][line].shape = shape[:-1]
            #line_no += 1 
    return image, plots

def do_stuff(CUBE,pool,**kwargs):
    if "bar" in kwargs:
        bar = kwargs["bar"]
        bar.update_text("Calculating...")
        bar.progress["maximum"] = 4
    else: bar = ""
    shape = CUBE.matrix.shape[:-1]
    specrange = CUBE.matrix.reshape(-1, CUBE.matrix.shape[-1])
    bgrange = CUBE.background.reshape(-1, CUBE.background.shape[-1])

    gain = CUBE.gain*1000
    e_axis = CUBE.energyaxis*1000

    Constants.CONTINUUM_SUPPRESSION = 1
    Constants.FIT_CYCLES = 1000
    
    wipe_bg = 0
    if CUBE.fit_config["bg"]: 
        if CUBE.sum_bg.sum(0) == 0:
            try:
                cycles, window, savgol, order = CUBE.config["bg_settings"]
            except:
                cycles, window, savgol, order = Constants.SNIPBG_DEFAULTS
                continuum = peakstrip(CUBE.sum,cycles,window,savgol,order)
            wipe_bg = 1
        else: continuum = CUBE.sum_bg
        CUBE.fit_fano_and_noise()
        CUBE.sum_bg = continuum
        bar.updatebar(1)

    fano, noise = CUBE.FN
    bar.update_text("Figuring elements...")
    elements_parameters, lines = work_elements(
            e_axis,
            pool, 
            gain, CUBE.sum)
    sigma = SIGMA(noise, fano, e_axis)
    bar.updatebar(2)

    path = os.path.join(__PERSONAL__,"output",CUBE.name,
            f"Interpolation-Fit-Plots-{CUBE.name}")

    bar.update_text("Generating fit...")
    output = run_spectrum(CUBE.sum, CUBE.sum_bg,
        e_axis, [fano,noise],
        elements_parameters, gain, sigma)
    MAX_UNIT = output/(CUBE.sum[elements_parameters["indexes"]])
    bar.updatebar(3)

    bar.update_text("Reading fit data...")
    results, parameters = work_results(output, list(pool["elements"].keys()), 
            elements_parameters, lines)
    bar.updatebar(4)

    plots = {}
    for element in results.keys():
        indexes = parameters[element]["indexes"]
        peaks = parameters[element]["peaks"]
        rad_rates = parameters[element]["rad_rates"]
        plots[element] = GAUSS(e_axis, peaks, rad_rates, gain, noise, fano, sigma[indexes],
            results[element]["Areas"])+CUBE.sum_bg

    """
    for element in results.keys():
        plt.plot(CUBE.energyaxis, plots[element], color=ElementColors[element], 
                linewidth=2,linestyle="--",label=element)
    plt.semilogy(CUBE.energyaxis,CUBE.sum, label="Spectrum")
    plt.plot(CUBE.energyaxis,CUBE.sum_bg, label="Continuum")
    plt.legend()
    plt.show()
    elements_parameters, lines = work_elements(
            e_axis,
            pool,
            gain, CUBE.sum)
    fano, noise = CUBE.FN
    sigma = SIGMA(noise, fano, e_axis)
    path = os.path.dirname(__file__)
    MAX_UNIT = CUBE.fit["output"]/(CUBE.fit["spec"][elements_parameters["indexes"]])
    """

    #############
    # RUN BATCH # 
    #############
    print("#"*10,"BATCH STARTED","#"*10)
    bar.update_text("Calculating...")
    bar.progress["maximum"] = len(specrange)

    frame = []
    it = 0

    if os.path.exists(path): pass
    else: os.makedirs(path)

    import matplotlib
    matplotlib.rc('axes',edgecolor='black',linewidth=1.3)
    matplotlib.rcParams['figure.facecolor'] = "white"

    iteration = 0
    if CUBE.config["bgstrip"] == "None":
        for i in specrange:
            if bar: bar.updatebar(iteration)
            iteration += 1
            timer = time.time()
            p0 = (i[elements_parameters["indexes"]])*MAX_UNIT
            output = p0

            #output = run_spectrum(i, bgrange[0],
            #        e_axis, CUBE.FN,
            #        elements_parameters, gain, sigma, 
            #        p0=p0)
        
            ###############################
            # SINGLE SPEC PLOT SAVE BLOCK #
            ###############################
            if Constants.SAVE_FIT_FIGURES and (it+1)%Constants.SAVE_INTERVAL==0:
                results, parameters = work_results(output, list(pool["elements"].keys()),
                                                    elements_parameters, lines)
                plt.clf()
                plots = {}
                for element in results.keys():
                    indexes = parameters[element]["indexes"]
                    peaks = parameters[element]["peaks"]
                    rad_rates = parameters[element]["rad_rates"]
                    plots[element] = GAUSS(e_axis,
                            peaks,
                            rad_rates,
                            gain,
                            noise, fano,
                            sigma[indexes],
                            results[element]["Areas"])

                for element in results.keys():
                    plt.plot(CUBE.energyaxis, plots[element], color=ElementColors[element],
                            linewidth=0.90,linestyle="--",label=element)
                plt.semilogy(CUBE.energyaxis,i, label="Spectrum", 
                        color="black",linewidth=0.90)
                plt.ylim([1,i.max()*1.10])
                plt.xlim([1,26])
                plt.legend(loc="upper right")
                if bar: bar.update_text(f"Saving fit plot {it}")
                plt.savefig(os.path.join(path,f"spectrum_{it}.png"),dpi=300)
            ###############################

            frame.append(output)
            if bar: bar.update_text("Calculating...")
            #print("Spec", it, "Time: ", time.time()-timer, end="\r")
            it += 1
    else:
        for i,j in zip(specrange, bgrange):
            if bar: bar.updatebar(iteration)
            #timer = time.time()
            p0 = (i[elements_parameters["indexes"]] - \
                    j[elements_parameters["indexes"]])*MAX_UNIT
            output = p0

            #output = run_spectrum(i, j,
            #        CUBE.energyaxis*1000, CUBE.FN,
            #        elements_parameters, CUBE.gain*1000, sigma, 
            #        p0=p0)
            if output is None: 
                output = np.zeros(i[elements_parameters["indexes"]].shape)
            else: pass

            ###############################
            # SINGLE SPEC PLOT SAVE BLOCK #
            ###############################
            if Constants.SAVE_FIT_FIGURES and (it+1)%Constants.SAVE_INTERVAL==0:
                results, parameters = work_results(output, list(pool["elements"].keys()),
                                                    elements_parameters, lines)
                plt.clf()
                plots = {}
                for element in results.keys():
                    indexes = parameters[element]["indexes"]
                    peaks = parameters[element]["peaks"]
                    rad_rates = parameters[element]["rad_rates"]
                    plots[element] = GAUSS(e_axis,
                            peaks,
                            rad_rates,
                            gain,
                            noise, fano,
                            sigma[indexes],
                            results[element]["Areas"])+j

                for element in results.keys():
                    plt.plot(CUBE.energyaxis, plots[element], color=ElementColors[element],
                            linewidth=0.90,linestyle="--",label=element)
                plt.semilogy(CUBE.energyaxis,i, label="Spectrum", 
                        color="black",linewidth=0.90)
                plt.semilogy(CUBE.energyaxis,j, label="Continuum", 
                        color="green", linewidth=0.85)
                plt.ylim([1,i.max()*1.10])
                plt.xlim([1,26])
                plt.legend(loc="upper right")
                if bar: bar.update_text(f"Saving fit plot {it}")
                plt.savefig(os.path.join(path,f"spectrum_{it}.png"),dpi=300)
            ###############################
            
            frame.append(output)
            if bar: bar.update_text("Calculating...")
            #print("Spec", it, "Time: ", time.time()-timer, end="\r")
            it += 1
    #if wipe_bg: CUBE.sum_bg=np.zeros(CUBE.sum.shape[0])
    #np.save(os.path.join(os.path.dirname(__file__),f"{CUBE.name}_frame.npy"),frame)
    return frame

def fit_and_run():
    CUBE = Constants.MY_DATACUBE
    if hasattr(CUBE,"fit_config"):
        element_pool = CUBE.fit_config
    else:
        print("Cube fit is not configured.")
        messagebox.showinfo("Fit not configured!","You must first set the fit parameters. Go to \"Image Analyzer\" -> \"Set ROI\" -> \"Options\" -> \"Configure Fit\".")
        return
    bar = Busy(0,CUBE.img_size)
    frame = do_stuff(CUBE, element_pool,bar=bar)
    CUBE.prepack_elements(list(element_pool["elements"].keys()))
    cmaps = ["gray","Spectral","jet","hot"]
    if len(sys.argv) >= 3:
        color = sys.argv[2]
        if color in cmaps:
            Constants.COLORMAP = color
        else: print(f"Color {color} not recognized!\nContinuing with default.")
    else: pass
    bar.update_text("Working...")
    params, lines = work_elements(
            CUBE.energyaxis*1000,
            element_pool,
            CUBE.gain*1000, CUBE.sum)
    images, plots = work_images(CUBE,
            frame,
            element_pool,
            params,
            lines,
            CUBE.matrix.shape,
            bar=bar)
    for el in element_pool["elements"].keys():
        for line in lines[el]:
            CUBE.pack_element(images[el][line], el, line)
            CUBE.ROI[el] = plots[el]
    bar.destroybar()
    CUBE.save_cube()
    return 0

if __name__.endswith("__main__"):
    ALL = 1
    SpecRead.samples_folder = os.getcwd()
    SpecRead.conditional_setup()
    name = sys.argv[1]
    cube_path = r"C:\Users\sergi\Documents\XISMuS\output\{0}\{0}.cube".format(name)
    if not os.path.exists(cube_path):
        print(f"Cube {name} not found.")
        sys.exit(1)

    cube_file = open(cube_path,'rb')
    CUBE = pickle.load(cube_file)
    shape = CUBE.matrix.shape[:-1]
    cube_file.close()

    if hasattr(CUBE,"fit_config"):
        element_pool = CUBE.fit_config
    else:
        print("Cube fit is not configured.")
        sys.exit(1)

    if os.path.exists(os.path.join(os.path.dirname(__file__),f"{CUBE.name}_frame.npy")):
        frame = np.load(os.path.join(os.path.dirname(__file__),f"{CUBE.name}_frame.npy"))
    else: 
        frame = do_stuff(CUBE, element_pool)

    ################
    # BUILD IMAGES #
    ################
    CUBE.prepack_elements(list(element_pool["elements"].keys()))
    cmaps = ["gray","Spectral","jet","hot"] 
    if len(sys.argv) >= 3:
        color = sys.argv[2]
        if color in cmaps:
            Constants.COLORMAP = color
        else: print(f"Color {color} not recognized!\nContinuing with default.")
    else: pass
    params, lines = work_elements(
            CUBE.energyaxis*1000,
            element_pool,
            CUBE.gain*1000, CUBE.sum)
    images, plots = work_images(CUBE, 
            frame, 
            element_pool, 
            params, 
            lines, 
            CUBE.matrix.shape)
    for el in element_pool["elements"].keys():
        for line in lines[el]:
            CUBE.pack_element(images[el][line], el, line)
            CUBE.ROI[el] = plots[el]
            print(f"Packed {el}_{line}")
            print(images[el][line].shape)
            #image = fast_scaling(CUBE, images[el][line], 1)
            #path = os.path.join(os.path.dirname(__file__),f"{el}_{line}.png")
            #write_image(image,0,path)
    CUBE.save_cube()
    ################

