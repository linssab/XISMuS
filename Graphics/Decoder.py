#################################################################
#                                                               #
#          DECODER                                              #
#                        version: 2.3.0 - Apr 2021              #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

""" This module reads *.tz files to extract icons and images used
in the GUI """

import base64
import numpy as np
import cv2
import os

global IMG_SPLASH
global IMG_NODATA

def b64_to_array(uri):
    nparr = np.frombuffer(base64.b64decode(uri), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    return img

def unpack_images():
    global IMG_NODATA, IMG_SPLASH
    image_file = open(os.path.join(os.path.dirname(__file__),"graphics.tz"),"rb")
    IMG_SPLASH = image_file.read(751304)

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
    ICO_VFLIP = icons_file.read(4272)

unpack_images()
unpack_icons()

