<<<<<<< HEAD
VERSION = "1.0.1"
=======
#################################################################
#                                                               #
#          CONSTANTS                                            #
#                        version: 1.1.9 - Jul - 2020            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import logging

VERSION = "1.1.0"
LOGLEVEL = logging.DEBUG
>>>>>>> dev
MY_DATACUBE = None
FIND_ELEMENT_LIST = None
DEFAULTBTN_COLOR = "SystemButtonFace"
LOW_RES = None
<<<<<<< HEAD
FANO = 80
NOISE = 0.114
=======
FANO = 0.114
NOISE = 80
USEXLIB = False
FIT_CYCLES = 1000
PEAK_TOLERANCE = 9
CONTINUUM_SUPPRESSION = 1.5
CHECK_TOLERANCE = 10
SETROI_TOLERANCE = [3,4,3]
SAVE_FIT_FIGURES = True
SAVE_INTERVAL = 500
SAVE_PATH = None
MATCHES = None
TARGET_RES = 1024
>>>>>>> dev
FILE_POOL = []
FIRSTFILE_ABSPATH = None
CONFIG = {}
CALIB = []
DIRECTORY = None
SAMPLES_FOLDER = ""
<<<<<<< HEAD
COLORMAP = "Jet"
=======
DIMENSION_FILE = ""
USER_DATABASE = {}
COLORMAP = "hot"
>>>>>>> dev
MULTICORE = True
PLOTMODE = "Logarithmic"
RAM_LIMIT = None
WELCOME = False
<<<<<<< HEAD
=======
CPUS = 12
>>>>>>> dev

def list_all():
    return {"version":VERSION,
            "my datacube":MY_DATACUBE,
            "find element list":FIND_ELEMENT_LIST,
            "defaultbtn color":DEFAULTBTN_COLOR,
            "low res":LOW_RES,
            "fano":FANO,
            "noise":NOISE,
<<<<<<< HEAD
=======
            "fit cycles":FIT_CYCLES,
            "peak tolerance":PEAK_TOLERANCE,
            "save fit figures":SAVE_FIT_FIGURES,
            "matches":MATCHES,
            "target resolution":TARGET_RES,
>>>>>>> dev
            "file pool":FILE_POOL,
            "firstfile abspath":FIRSTFILE_ABSPATH,
            "config":CONFIG,
            "calib":CALIB,
            "directory":DIRECTORY,
<<<<<<< HEAD
            "samples folder":SAMPLES_FOLDER}
=======
            "samples folder":SAMPLES_FOLDER,
            "dimension file":DIMENSION_FILE,
            "user database":USER_DATABASE,
            "colormap":COLORMAP,
            "multicore":MULTICORE,
            "plotmode":PLOTMODE,
            "ram limit":RAM_LIMIT,
            "welcome":WELCOME,
            "cpu count":CPUS}

>>>>>>> dev
