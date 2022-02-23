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

import logging
from psutil import cpu_count

VERSION = "2.5.0"
ROOT = None
VERSION_MOS = VERSION
LOGLEVEL = logging.INFO
MY_DATACUBE = None
FIND_ELEMENT_LIST = None
DEFAULTBTN_COLOR = "SystemButtonFace"
LOW_RES = None
FANO = 0.114
NOISE = 80
USEXLIB = False
FIT_CYCLES = 1000
PEAK_TOLERANCE = 9
CONTINUUM_SUPPRESSION = 1.5
SNIPBG_DEFAULTS = 24,5,5,3
CHECK_TOLERANCE = 10
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
PLOTSCALE = "-semilogy"
RAM_LIMIT = None
WELCOME = False
FILTER = 1
CPUS = cpu_count(logical=False)
FTIR_DATA = 0
TEMP_PATH = ""
NCHAN = 0
MSHAPE = (0,0,0)
LOGGER = logging.getLogger("logger")