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

# This module reads *.tz files to extract icons and images used
# in the GUI

import base64
import numpy as np
import cv2
import os

global IMG_SPLASH
global IMG_DIFFDIAGRAM

def b64_to_array(uri):
    nparr = np.frombuffer(base64.b64decode(uri), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    return img

def unpack_images():
    global IMG_DIFFDIAGRAM, IMG_SPLASH
    image_file = open(os.path.join(os.path.dirname(__file__),"graphics.tz"),"rb")
    IMG_SPLASH = image_file.read(751468)
    IMG_DIFFDIAGRAM = image_file.read(49172)
    return

def unpack_icons():
    global ICO_ACCEPT, ICO_CCW, ICO_CW, ICO_DOWN
    global ICO_ERASE, ICO_EXPORT1, ICO_EXPORT2, ICO_EXPORT_MERGE, ICO_IMGANAL
    global ICO_LOAD, ICO_NEXT, ICO_PREVIOUS, ICO_QUIT, ICO_REFRESH, ICO_RESET
    global ICO_FIT_NORMAL, ICO_FIT_DISABLED
    global ICO_REJECT, ICO_RUBIK, ICO_SETTINGS, ICO_UP, ICO_MAGNIFIER
    global ICO_SAVE, ICO_SAVE_SPEC, ICO_LOG, ICO_LIN, ICO_ADVCALIB
    global ICO_MASK_NORMAL, ICO_MASK_TOGGLED 
    global ICO_LINREGRESS_NORMAL, ICO_LINREGRESS_TOGGLED, ICO_CLEAR 
    global ICO_MOSAIC, ICO_HFLIP, ICO_VFLIP
    global ICO_VALSUCCESS, ICO_VALFAIL

    icons_file = open(os.path.join(os.getcwd(),"images","icons","icons.tz"),"rb")
    ICO_ACCEPT = icons_file.read(1548)
    ICO_ADVCALIB = icons_file.read(4324)
    ICO_CCW = icons_file.read(4364)
    ICO_CLEAR = icons_file.read(6024)
    ICO_CW = icons_file.read(4328)
    ICO_DOWN = icons_file.read(4028)
    ICO_ERASE = icons_file.read(1944)
    ICO_EXPORT1 = icons_file.read(4548)
    ICO_EXPORT2 = icons_file.read(4512)
    ICO_EXPORT_MERGE = icons_file.read(4664)
    ICO_FIT_DISABLED = icons_file.read(6252)
    ICO_FIT_NORMAL = icons_file.read(7176)
    ICO_HFLIP = icons_file.read(4304)
    ICO_IMGANAL = icons_file.read(2416)
    ICO_LIN = icons_file.read(4020)
    ICO_LINREGRESS_NORMAL = icons_file.read(7732)
    ICO_LINREGRESS_TOGGLED = icons_file.read(6524)
    ICO_LOAD = icons_file.read(2184)
    ICO_LOG = icons_file.read(4004)
    ICO_MAGNIFIER = icons_file.read(3876)
    ICO_MASK_NORMAL = icons_file.read(5964)
    ICO_MASK_TOGGLED = icons_file.read(5284)
    ICO_MOSAIC = icons_file.read(5968)
    ICO_NEXT = icons_file.read(4020)
    ICO_PREVIOUS = icons_file.read(4064)
    ICO_QUIT = icons_file.read(2476)
    ICO_REFRESH = icons_file.read(6596)
    ICO_REJECT = icons_file.read(1832)
    ICO_RESET = icons_file.read(2184)
    ICO_RUBIK = icons_file.read(8120)
    ICO_SAVE = icons_file.read(928)
    ICO_SAVE_SPEC = icons_file.read(8060)
    ICO_SETTINGS = icons_file.read(3624)
    ICO_UP = icons_file.read(4064)
    ICO_VALFAIL = icons_file.read(4736)
    ICO_VALSUCCESS = icons_file.read(4588)
    ICO_VFLIP = icons_file.read(4272)

unpack_images()
unpack_icons()

