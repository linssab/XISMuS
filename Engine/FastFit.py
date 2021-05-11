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
import threading
from psutil import cpu_count
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
try: from tkinter import messagebox
except: from Tkinter import messagebox

SIGMA = lambda noise, fano, peaks: np.sqrt(((noise/2.3548200450309493)**2)+3.85*fano*peaks)

def check(bar,lim):
    global kill
    global it
    try:
        while it < lim and not kill:
            bar.updatebar(it)
    except: kill = 1
    return

def bite_data(length):
    cpus = cpu_count()
    if cpus == 1:
        bite_size = int(length)
        leftovers = 0
        print("Only one core")
    else:
        bite_size = 0
        while bite_size < 400:
            bite_size = int(length/cpus)
            leftovers = int(length%cpus)
            print("bite size: ",bite_size,"leftovers ",leftovers)
            cpus -= 1
            if bite_size == length: break
        cpus += 1
        bite_size = bite_size
        leftovers = leftovers
    return bite_size, cpus, leftovers

def work_images(CUBE, frame, element_pool, element_params, lines, shape, **kwargs):
    if "bar" in kwargs:
        bar = kwargs["bar"]
        bar.progress["maximum"] = len(frame)
        bar.update_text("Working images...")
        bar.updatebar(0)
    global it
    global kill 
    bg = CUBE.background.flatten()
    lock = threading.Lock()
    bite_size, cpus, leftovers = bite_data(len(frame))
    fano, noise = CUBE.FN
    e_axis = CUBE.energyaxis*1000
    gain = CUBE.gain*1000
    sigma = SIGMA(noise, fano, e_axis)
    spec_count = 0
    it = 0
    kill = 0
    threads = []
    image = {}
    plots = {}

    for el in element_pool["elements"].keys():
        image[el] = {}
        plots[el] = np.zeros(len(lines[el]))
        for line in lines[el]:
            image[el][line] = np.zeros(shape[0]*shape[1],dtype=np.float32)

    def iterate_over_frame(frame,position,bite_size,bg,parameters,lock):
        global it
        element_pool, plots, image = parameters
        for i in range(bite_size):
            pos = position + i
            if CUBE.config["bgstrip"] != "None":
                j = bg[i]
            else: j = np.zeros(shape[2])
            try: 
                results, params = work_results(frame[pos], 
                        list(element_pool["elements"].keys()), 
                        element_params, lines)
            except IndexError: 
                print(pos,len(frame))
            for element in results.keys():
                ellines = results[element]["Lines"]
                plots[element] += results[element]["Areas"]
                with lock:
                    for l in range(len(ellines)):
                        image[element][ellines[l]][pos] = \
                                results[element]["Areas"][l]*params[element]["rad_rates"][l]
            with lock: it += 1
            if kill: return
        return

    for k in range(cpus):
        chunk0 = k*bite_size
        chunk1 = chunk0+bite_size
        t = threading.Thread(target=iterate_over_frame,
                args=(frame,chunk0,bite_size,bg,(element_pool,plots,image),lock,))
        threads.append(t)
        for i in range(bite_size):
            spec_count += 1
    if leftovers >= 1:
        t = threading.Thread(target=iterate_over_frame,
                args=(frame,spec_count,leftovers,bg,(element_pool,plots,image),lock,))
        threads.append(t)
    for t in threads:
        t.start()
    check(bar,len(frame))
    bar.master.focus_set()
    bar.master.focus_force()
    for t in threads:
        t.join()
    kill = 1
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
    try: results, params = work_results(frame[0], list(element_pool["elements"].keys()), 
                    element_params, lines)
    except: return None, None
    for el in image.keys():
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

def save_plot(results,parameters,spec,energyaxis,bg=None):
    global PATH
    global GNFS
    gain, noise, fano, sigma = GNFS
    if bg is None: bg = np.zeros([spec.shape[0]],dtype=np.float32)
    plt.clf()
    plots = {}
    for element in results.keys():
        indexes = parameters[element]["indexes"]
        peaks = parameters[element]["peaks"]
        rad_rates = parameters[element]["rad_rates"]
        plots[element] = GAUSS(energyaxis,
                peaks,
                rad_rates,
                gain,
                noise, fano,
                sigma[indexes],
                results[element]["Areas"])+bg

    for element in results.keys():
        plt.plot(energyaxis, plots[element], color=ElementColors[element],
                linewidth=0.90,linestyle="--",label=element)
    plt.semilogy(energyaxis,spec, label="Spectrum",
            color="black",linewidth=0.90)
    plt.semilogy(energyaxis,bg, label="Continuum",
            color="green", linewidth=0.85)
    plt.ylim([1,spec.max()*1.10])
    plt.xlim([1,energyaxis.max()])
    plt.ylabel("Counts")
    plt.xlabel("Energy (eV)")
    plt.legend(loc="upper right")
    plt.savefig(os.path.join(PATH,f"spectrum_{it}.png"),dpi=300)

def do_stuff(CUBE,pool,**kwargs):
    global MAX_UNIT
    global PATH
    global GNFS
    global it
    global kill
    if "bar" in kwargs:
        bar = kwargs["bar"]
        bar.update_text("Calculating...")
        bar.progress["maximum"] = 4
    else: bar = ""
    restore_original_bg = 0
    shape = CUBE.matrix.shape[:-1]
    specrange = CUBE.matrix.reshape(-1, CUBE.matrix.shape[-1])
    bgrange = CUBE.background.reshape(-1, CUBE.background.shape[-1])

    gain = CUBE.gain*1000
    e_axis = CUBE.energyaxis*1000
    
    if CUBE.fit_config["bg"]: 
        try:
            cycles, window, savgol, order = CUBE.fit_config["bg_settings"]
        except:
            cycles, window, savgol, order = Constants.SNIPBG_DEFAULTS
        continuum = peakstrip(CUBE.sum,cycles,window,savgol,order)
        CUBE.sum_bg = continuum
        if not hasattr(CUBE,"FN"): CUBE.fit_fano_and_noise()
        bar.updatebar(1)
    else:
        print("Not using BG")
        restore_original_bg = 1
        original_bg = CUBE.sum_bg[:]
        CUBE.sum_bg = np.zeros([CUBE.sum.shape[0]],dtype=np.float32)
        bar.updatebar(1)

    fano, noise = CUBE.FN
    bar.update_text("Figuring elements...")
    elements_parameters, lines = work_elements(
            e_axis,
            pool, 
            gain, CUBE.sum)
    sigma = SIGMA(noise, fano, e_axis)
    bar.updatebar(2)
    PATH = os.path.join(__PERSONAL__,"output",CUBE.name,
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
    print("#"*10,"BATCH STARTED","#"*10)
    GNFS = (gain, noise, fano, sigma)
    import matplotlib
    matplotlib.rc('axes',edgecolor='black',linewidth=1.3)
    matplotlib.rcParams['figure.facecolor'] = "white"
    bar.update_text("Calculating...")
    bar.progress["maximum"] = len(specrange)
    threads = []
    frame = [None]*len(specrange)
    it = 0
    kill = 0
    lock = threading.Lock()
    if os.path.exists(PATH): pass
    else: os.makedirs(PATH)

    bite_size, cpus, leftovers = bite_data(specrange.shape[0])

    parameters = (elements_parameters, pool, lines)
    spec_count = 0
    for k in range(cpus):
        chunk0 = k*bite_size
        chunk1 = chunk0+bite_size
        if CUBE.config["bgstrip"] == "None":
            t = threading.Thread(target=iterate_batch,
                    args=(parameters,
                        specrange[chunk0:chunk1],
                        e_axis, frame, chunk0,
                        lock,), kwargs={"bar":bar})
        else:
            t = threading.Thread(target=iterate_batch,
                    args=(parameters,
                        specrange[chunk0:chunk1],
                        e_axis, frame, chunk0,
                        lock,), kwargs={"bar":bar,"bgrange":bgrange[chunk0:chunk1]})
        threads.append(t)
        for i in range(bite_size):
            spec_count += 1
    if leftovers >= 1:
        if CUBE.config["bgstrip"] == "None":
            t = threading.Thread(target=iterate_batch,
                    args=(parameters,
                        specrange[spec_count:],
                        e_axis, frame, spec_count,
                        lock,), kwargs={"bar":bar})
        else:
            t = threading.Thread(target=iterate_batch,
                    args=(parameters,
                        specrange[spec_count:],
                        e_axis, frame, spec_count,
                        lock,), kwargs={"bar":bar,"bgrange":bgrange[spec_count:]})
        threads.append(t)

    for t in threads:
        t.start()
    check(bar,specrange.shape[0])
    bar.master.focus_set()
    bar.master.focus_force()
    for t in threads:
        t.join()
    #np.save(os.path.join(os.path.dirname(__file__),f"{CUBE.name}_frame.npy"),frame)
    kill = 1
    if restore_original_bg: 
        return frame, original_bg
    return frame, CUBE.sum_bg

def iterate_batch(parameters,
        specrange,xaxis,
        frame,START,
        lock,**kwargs):
    global MAX_UNIT
    global kill
    global it
    if "bgrange" in kwargs: bgrange = kwargs["bgrange"]
    else: bgrange = None
    if "bar" in kwargs: 
        bar = kwargs["bar"]
        if bar is None: bar = False
    else: bar = False
    elements_parameters, pool, lines = parameters

    it00 = START+0
    if bgrange is None:
        for i in specrange:
            p0 = (i[elements_parameters["indexes"]])*MAX_UNIT
            output = p0
            if Constants.SAVE_FIT_FIGURES and (it+1)%Constants.SAVE_INTERVAL==0:
                results, parameters = work_results(output, list(pool["elements"].keys()),
                                                    elements_parameters, lines)
                with lock: 
                    if bar: bar.update_text(f"Saving fit plot {it}")
                    save_plot(results,parameters,i,xaxis)
                    if bar: bar.update_text("Calculating...")
            with lock:
                it += 1
                frame[it00] = output
            it00 += 1
            if kill: return
    else:
        for i,j in zip(specrange, bgrange):
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
            if Constants.SAVE_FIT_FIGURES and (it+1)%Constants.SAVE_INTERVAL==0:
                results, parameters = work_results(output, list(pool["elements"].keys()),
                                                    elements_parameters, lines)
                with lock:
                    if bar: bar.update_text(f"Saving fit plot {it}")
                    save_plot(results,parameters,i,xaxis)
                    if bar: bar.update_text("Calculating...")
            with lock:
                it += 1
                frame[it00] = output
            it00 += 1
            if kill: return
        return

def fit_and_run():
    CUBE = Constants.MY_DATACUBE
    if hasattr(CUBE,"fit_config"):
        element_pool = CUBE.fit_config
    else:
        print("Cube fit is not configured.")
        messagebox.showinfo("Fit not configured!","You must first set the fit parameters. Go to \"Image Analyzer\" -> \"Set ROI\" -> \"Options\" -> \"Configure Fit\".")
        return
    bar = Busy(0,CUBE.img_size)
    bar.master.focus_set()
    bar.master.focus_force()
    try: frame, restored_bg = do_stuff(CUBE, element_pool,bar=bar)
    except Exception as e: 
        messagebox.showerror("Uh-oh!",f"Something went wrong.\n{e}")
        bar.destroybar()
        return
    CUBE.prepack_elements(list(element_pool["elements"].keys()))
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
    bar.update_text("Writing to disk...")
    CUBE.sum_bg = restored_bg
    CUBE.save_cube()
    bar.destroybar()
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

