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
from Utilities import *
from .SpecRead import (__PERSONAL__, conditional_setup)
from .EdfFile import * 
from GUI.ConfigurationParser import *
from psutil import virtual_memory
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import numpy as np
import h5py, gc, os


class Mock:
    def __init__(__self__, dtypes, name="Mock"):
        __self__.name = name
        __self__.datatypes = dtypes
        __self__.calibration = None
        __self__.matrix = np.zeros([1,1,1],dtype=np.float32)
        __self__.background = np.zeros([1,1,1],dtype=np.float32)
        if "ftir" in dtypes: Constants.FTIR_DATA = 1
        else: Constants.FTIR_DATA = 0

def check_memory( needed_memory ):
        sys_mem = dict(virtual_memory()._asdict())
        available_memory = sys_mem["available"]
        if hasattr(Constants.MY_DATACUBE,"matrix"):
            m_size = Constants.MY_DATACUBE.matrix.itemsize
            b_size = Constants.MY_DATACUBE.background.itemsize
            temp_mem = Constants.MY_DATACUBE.matrix.size * m_size + \
                    Constants.MY_DATACUBE.background.size * b_size
        else: temp_mem = 0
        if needed_memory > ( available_memory + temp_mem ):
            print("Needed memory",needed_memory,
                    "\nAvailable:",available_memory, "\nTemp:",temp_mem)
            Constants.LOGGER.warning(f"Cannot load data! Not enough RAM!")
            messagebox.showerror("Memory error!",f"No RAM available! Cube size: {convert_bytes(needed_memory)}, Memory available: {convert_bytes(available_memory)}.")
            return 1
        else: return 0

def write(root):
    try:
        value = Constants.MY_DATACUBE.name
    except:
        messagebox.showerror("No datacube!","Please load a datacube first.")
        return

    h5f = filedialog.asksaveasfile(mode='w',
                    defaultextension=".h5",
                    filetypes=[("Hierarchical Data Format", "*.h5")],
                    title="Save as...")
    if h5f is None:
        return
    else:
        h5 = h5py.File(h5f.name, "w")
        data = Constants.MY_DATACUBE.matrix
        h5.create_dataset("dataset_1", data=data)
        if any("ftir" in x for x in Constants.MY_DATACUBE.datatypes):
            v = 1
        else: v = 0
        h5.attrs.create("datatypes", v, dtype=np.int32)
        h5.attrs.create("calibration", Constants.MY_DATACUBE.calibration, dtype=np.float32)
        h5.close()

def readh5(name):
    with h5py.File(name, "r") as f:
        group_keys = list(f.keys())
        for key in group_keys:
            shape = np.array(f[key]).shape
            if len(shape) >= 3: #data matrix has 3 dimensions
                if shape[2] >= 256: #spectra have to have at least 256 channels
                    a_group_key = key
                break

        if "datatypes" in f.attrs:
            dtypes = f.attrs["datatypes"]
        else: dtypes = 0
        if "calibration" in f.attrs:
            calib = f.attrs["calibration"]
        else: calib = None

        if dtypes:
            dtypes = ["ftir","h5"]
            usefloat = 1
        else:
            dtypes = ["h5"]
            usefloat = 0

        data = list(f[a_group_key])
        cube = Mock(dtypes)
        if usefloat: cube.matrix = np.asarray(data, dtype=np.float32, order="C")
        else: cube.matrix = np.asarray(data, dtype=np.int32, order="C")
        cube.background = np.array(cube.matrix.shape[-1], dtype=np.int32, order="C")
        cube.calibration = calib
        del data
        gc.collect()
    return cube

def readStack(batch):
    firstfile = EdfFile(batch[0], access="r")
    HEADER = firstfile.GetStaticHeader(0)
    specsize = int(HEADER["Dim_1"])
    cols = int(HEADER["Dim_2"])
    rows = len(batch)

    name = str(batch[0]).split("/")[-1].split(".")[0]
    cube = Mock(["edf"],name=name)

    float_size = np.float32(0.0).itemsize
    size = float_size * specsize * cols * rows
    check_memory(size)

    cube.matrix = np.zeros([rows,cols,specsize],dtype=np.int32)
    fill_row = rows-1
    for row in range(rows):
        edf = EdfFile(batch[row], access="r") 
        data = edf.GetData(0)
        cube.matrix[fill_row,:] = data
        fill_row -= 1
    
    HEADER01 = firstfile.GetHeader(0) 
    curve = []
    for item in HEADER01.keys():
        if "MCA" in item:
            curve.append(float(HEADER01[item]))
    if curve != []:
        calibration = [
                [1, (curve[1]*1) + curve[0]],
                [specsize, (curve[1]*specsize) + curve[0]]
                ]
        cube.calibration = calibration
    return cube

def load(root, ftype="h5"):
    if ftype == "h5":
        h5f = filedialog.askopenfilename(parent=root.master,
                title="Select h5 file",
                filetypes=(
                    ("H5 files", "*.h5"),
                    ("All files", "*.*")))
        if h5f == "": return
        else: wipe_stats(root)

        root.h5path = h5f
        sample_name = str(h5f).split("/")[-1].split(".")[0]
    elif ftype == "edf":
        file_batch = filedialog.askopenfilenames(parent=root.master,
                    title="Select EDF files",
                    filetypes=(
                        ("EDF files", "*.edf"),
                        ("All files", "*.*")))
        if file_batch == "": return
        else: 
            wipe_stats(root)
            h5f = file_batch[0]
            sample_name = os.path.dirname(str(h5f)).split("/")[-1]
    else:
        raise TypeError("No filetype specfied!")
        return

    ##################################
    # Verifies if h5 datacube exists #
    ##################################
    path_to_test = os.path.join(
        __PERSONAL__,"output",sample_name,sample_name+".cube")
    if os.path.exists(path_to_test):
        try: 
            f = open(path_to_test,"rb")
            f.close()
        except:
            messagebox.showinfo("Cube exists","Datacube for {} already exist!".format(
                sample_name))
            return
    else:
        ##############################################
        # Verifies if h5 is loaded as a temporary h5 #
        ##############################################
        if sample_name == root.temporaryh5:
            messagebox.showinfo("Info!","Sample {} is already loaded as a temporary h5 file. Select another sample and try again!".format(sample_name))
            return
        ##############################################
    ##################################

    conc_path = os.path.dirname(str(h5f))
    conditional_setup(name=sample_name,path=conc_path)

    ###############################
    # EXTRACT INFORMATION FROM h5 #
    ###############################
    #NOTE: Attention to root.images_dict, that exists to hold any previously existing
    # images in the h5 file to parse them to the SpecMath.datacube.__init__

    root.images_dict = {}
    if ftype == "h5": 
        try: Constants.MY_DATACUBE = readh5(h5f)
        except Exception as e: 
            messagebox.showerror("Uh-oh!",f"Something went wrong!\n{e}")
            return
        img_size = Constants.MY_DATACUBE.matrix.shape[0]*Constants.MY_DATACUBE.matrix.shape[1]
        specsize = Constants.MY_DATACUBE.matrix.shape[2]
        root.mcacount[sample_name] = img_size
        root.samples[sample_name] = ".h5"
        root.samples_path[sample_name] = conc_path
        root.mca_indexing[sample_name] = ".h5"
        root.mca_extension[sample_name] = ".h5"
        root.temporaryh5 = sample_name
        Constants.FIRSTFILE_ABSPATH = h5f
    elif ftype == "edf": 
        Constants.TEMP_PATH = conc_path
        try: Constants.MY_DATACUBE = readStack(file_batch)
        except Exception as e: 
            messagebox.showerror("Uh-oh!",f"Something went wrong!\n{e}")
            return
        img_size = Constants.MY_DATACUBE.matrix.shape[0]*Constants.MY_DATACUBE.matrix.shape[1]
        specsize = Constants.MY_DATACUBE.matrix.shape[2]
        root.mcacount[sample_name] = img_size
        root.samples[sample_name] = Constants.MY_DATACUBE.name
        root.samples_path[sample_name] = conc_path
        root.mca_indexing[sample_name] = ".edf"
        root.mca_extension[sample_name] = ".edf"
        root.temporaryh5 = "None"
        Constants.FIRSTFILE_ABSPATH = conc_path
    ###############################

    #3 ask for a sample name and dimension (modified dimension diag)
    try:
        root.config_xy = (Constants.MY_DATACUBE.matrix.shape[0],
                Constants.MY_DATACUBE.matrix.shape[1])
        root.ManualParam = []
    except:
        dimension = (Constants.MY_DATACUBE.matrix.shape[0],
                Constants.MY_DATACUBE.matrix.shape[1])
        root.master.wait_window(dimension.master)
        if dimension.exit_code == "cancel":
            root.wipe()
            return 0
        root.ManualParam = []

    # calls the configuration window
    root.toggle_(toggle="off")
    root.ConfigDiag = ConfigDiag(root,matrix=Constants.MY_DATACUBE.matrix,
            calib=Constants.MY_DATACUBE.calibration)
    root.ConfigDiag.build_widgets()