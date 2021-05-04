#################################################################
#                                                               #
#          Exotic files reader                                  #
#                        version: 2.3.2 - May - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import Constants
from .SpecRead import (__PERSONAL__, conditional_setup)
from GUI.ConfigurationParser import *
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import numpy as np
import h5py, gc, os

class Mock:
    def __init__(__self__, dtypes):
        __self__.name = "Mock"
        __self__.datatypes = dtypes
        if "ftir" in dtypes: Constants.FTIR_DATA = 1
        else: Constants.FTIR_DATA = 0

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

def load(root):
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

    h5f = filedialog.askopenfilename(parent=root.master,
            title="Select h5 file",
            filetypes=(
                ("H5 Files", "*.h5"),
                ("All files", "*.*")))
    if h5f == "": return

    root.h5path = h5f
    sample_name = str(h5f).split("/")[-1].split(".")[0]

    ##################################
    # Verifies if h5 datacube exists #
    ##################################
    if os.path.exists(os.path.join(
        __PERSONAL__,"output",sample_name,sample_name+".cube")):
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

    path = str(h5f).split("/")
    path.pop(-1)
    conc_path = ""
    for i in path:
        conc_path += i+"\\"
    conc_path = os.path.abspath(conc_path)
    conditional_setup(name=sample_name,path=conc_path)

    ###############################
    # EXTRACT INFORMATION FROM h5 #
    ###############################
    #NOTE: Attention to root.images_dict, that exists to hold any previously existing
    # images in the h5 file to parse them to the SpecMath.datacube.__init__

    root.images_dict = {}
    Constants.MY_DATACUBE = readh5(h5f)
    img_size = Constants.MY_DATACUBE.matrix.shape[0]*Constants.MY_DATACUBE.matrix.shape[1]
    specsize = Constants.MY_DATACUBE.matrix.shape[2]
    root.mcacount[sample_name] = img_size
    root.samples[sample_name] = ".h5"
    root.samples_path[sample_name] = conc_path
    root.mca_indexing[sample_name] = ".h5"
    root.mca_extension[sample_name] = ".h5"
    root.temporaryh5 = sample_name
    Constants.FIRSTFILE_ABSPATH = h5f
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

