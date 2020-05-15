VERSION = "1.0.0"
MY_DATACUBE = None
FIND_ELEMENT_LIST = None
DEFAULTBTN_COLOR = "#000000"
LOW_RES = None
FANO = 80
NOISE = 0.114
FILE_POOL = []
FIRSTFILE_ABSPATH = None
CONFIG = {}
CALIB = []
DIRECTORY = None
SAMPLES_FOLDER = ""

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
