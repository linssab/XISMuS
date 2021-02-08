#################################################################
#                                                               #
#          DECODER                                              #
#                        version: 1.3.2                         #
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
    image_file = open(os.path.join(os.getcwd(),"images","utils.tz"),"rb")
    IMG_SPLASH = image_file.read(502440)
    no_data = image_file.read(38872) 
    IMG_NODATA = b64_to_array(no_data)

def unpack_icons():
    global ICO_ACCEPT, ICO_CCW, ICO_CW, ICO_DOWN
    global ICO_ERASE, ICO_EXPORT1, ICO_EXPORT2, ICO_EXPORT_MERGE, ICO_IMGANAL
    global ICO_LOAD, ICO_NEXT, ICO_PREVIOUS, ICO_QUIT, ICO_REFRESH, ICO_RESET
    global ICO_REJECT, ICO_RUBIK, ICO_SETTINGS, ICO_UP, ICO_MAGNIFIER
    global ICO_SAVE, ICO_LOG, ICO_LIN, ICO_ADVCALIB

    icons_file = open(os.path.join(os.getcwd(),"images","icons","icons.tz"),"rb")
    ICO_ACCEPT = icons_file.read(1548)
    ICO_ADVCALIB = icons_file.read(4324)
    ICO_CCW = icons_file.read(4364)
    ICO_CW = icons_file.read(4328)
    ICO_DOWN = icons_file.read(4028)
    ICO_ERASE = icons_file.read(1944)
    ICO_EXPORT1 = icons_file.read(4548)
    ICO_EXPORT2 = icons_file.read(4512)
    ICO_EXPORT_MERGE = icons_file.read(4664)
    ICO_IMGANAL = icons_file.read(2416)
    ICO_LIN = icons_file.read(4020)
    ICO_LOAD = icons_file.read(2184)
    ICO_LOG = icons_file.read(4004)
    ICO_MAGNIFIER = icons_file.read(3876)
    ICO_NEXT = icons_file.read(4020)
    ICO_PREVIOUS = icons_file.read(4064)
    ICO_QUIT = icons_file.read(2476)
    ICO_REFRESH = icons_file.read(5848)
    ICO_REJECT = icons_file.read(1832)
    ICO_RESET = icons_file.read(2184)
    ICO_RUBIK = icons_file.read(4348)
    ICO_SAVE = icons_file.read(928)
    ICO_SETTINGS = icons_file.read(3624)
    ICO_UP = icons_file.read(4064)

unpack_images()
unpack_icons()

