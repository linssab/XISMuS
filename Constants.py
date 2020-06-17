import logging

VERSION = "1.0.1dev"
LOGLEVEL = logging.INFO
MY_DATACUBE = None
FIND_ELEMENT_LIST = None
DEFAULTBTN_COLOR = "SystemButtonFace"
LOW_RES = None
FANO = 0.114
NOISE = 80
FILE_POOL = []
FIRSTFILE_ABSPATH = None
CONFIG = {}
CALIB = []
DIRECTORY = None
SAMPLES_FOLDER = ""
COLORMAP = "hot"
MULTICORE = True
PLOTMODE = "Logarithmic"
RAM_LIMIT = None
WELCOME = False
CPUS = 1

def list_all():
    return {"version":VERSION,
            "my datacube":MY_DATACUBE,
            "find element list":FIND_ELEMENT_LIST,
            "defaultbtn color":DEFAULTBTN_COLOR,
            "low res":LOW_RES,
            "fano":FANO,
            "noise":NOISE,
            "file pool":FILE_POOL,
            "firstfile abspath":FIRSTFILE_ABSPATH,
            "config":CONFIG,
            "calib":CALIB,
            "directory":DIRECTORY,
            "samples folder":SAMPLES_FOLDER}
