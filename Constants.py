import logging

VERSION = "1.1.0"
LOGLEVEL = logging.INFO
MY_DATACUBE = None
FIND_ELEMENT_LIST = None
DEFAULTBTN_COLOR = "SystemButtonFace"
LOW_RES = None
FANO = 0.114
NOISE = 80
FIT_CYCLES = 1000
PEAK_TOLERANCE = 1.30
SETROI_TOLERANCE = [3,4,3]
SAVE_FIT_FIGURES = True
SAVE_INTERVAL = 500
SAVE_PATH = None
MATCHES = None
TARGET_RES = 1024
FILE_POOL = []
FIRSTFILE_ABSPATH = None
CONFIG = {}
CALIB = []
DIRECTORY = None
SAMPLES_FOLDER = ""
DIMENSION_FILE = ""
USER_DATABASE = {}
COLORMAP = "hot"
MULTICORE = True
PLOTMODE = "Logarithmic"
RAM_LIMIT = None
WELCOME = False
CPUS = 12

def list_all():
    return {"version":VERSION,
            "my datacube":MY_DATACUBE,
            "find element list":FIND_ELEMENT_LIST,
            "defaultbtn color":DEFAULTBTN_COLOR,
            "low res":LOW_RES,
            "fano":FANO,
            "noise":NOISE,
            "fit cycles":FIT_CYCLES,
            "peak tolerance":PEAK_TOLERANCE,
            "save fit figures":SAVE_FIT_FIGURES,
            "matches":MATCHES,
            "target resolution":TARGET_RES,
            "file pool":FILE_POOL,
            "firstfile abspath":FIRSTFILE_ABSPATH,
            "config":CONFIG,
            "calib":CALIB,
            "directory":DIRECTORY,
            "samples folder":SAMPLES_FOLDER,
            "dimension file":DIMENSION_FILE,
            "user database":USER_DATABASE,
            "colormap":COLORMAP,
            "multicore":MULTICORE,
            "plotmode":PLOTMODE,
            "ram limit":RAM_LIMIT,
            "welcome":WELCOME,
            "cpu count":CPUS}

