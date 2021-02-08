#################################################################
#                                                               #
#          DLL FUNCTIONS                                        #
#                        version: 2.0.0 - Feb - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import numpy as np
import time
import ctypes
from numpy.ctypeslib import ndpointer

lib = "./booster.dll"
dll = ctypes.cdll.LoadLibrary(lib);

dll.apply_scaling.argtypes = [
        ndpointer(ctypes.c_float),
        ndpointer(ctypes.c_float),
        ctypes.c_int,
        ctypes.c_int
        ]
dll.apply_scaling.restype = ctypes.c_void_p

dll.threshold.argtypes = [
        ndpointer(ctypes.c_float),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int
        ]
dll.threshold.restype = ctypes.c_void_p

dll.apply_smooth.argtypes = [
        ndpointer(ctypes.c_float),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int
        ]
dll.apply_smooth.restype = ctypes.c_void_p

def fast_scaling(datacube, image, scalemode=0, mask=np.zeros(0)):
    """ image is passed to C as a pointer, to maintain the original data, 
    a copy must me made beforehand. Python garbage collector takes care of cleaning
    the memory space of the original data used in this function. In python, functions
    receive the value of the data, not the variable. Local variables are ocntained in the
    local function namespace

    scalemode:
    0 = Returns
    1 = Applies scaling to datacube.matrix
    -1 = Reverse scaling applied to datacube.matrix """


    if scalemode == 0: 
        return image
    else:
        if mask.any(): scaling_matrix = mask
        else: scaling_matrix = datacube.scale_matrix

    shape = image.shape
    scaling_matrix = scaling_matrix.flatten()
    image = image.flatten()
    newimg = image.copy()
    size = int(image.shape[0])
    
    dll.apply_scaling(scaling_matrix,newimg,scalemode,size)
    newimg.shape = (newimg.size//shape[1], shape[1])
    return newimg

def fast_threshold(image, mode, t):
    """ Applies a threshold filter to input 2D-array.
    modes:
    0 cuts lower than t values;
    1 cuts higher than t values """

    t = int(t)
    shape = image.shape
    image = image.flatten()
    newimg = image.copy()
    size = int(image.shape[0])

    dll.threshold(newimg,mode,t,size)
    newimg.shape = (newimg.size//shape[1], shape[1])
    return newimg

def fast_smooth(image, iterations):
    """ Applies a median filter with central weight = 2 to an image.
    As usual, the image is converted from 2D to 1D before being sent to the
    DLL function. """

    shape = image.shape
    image = image.flatten()
    newimg = image.copy()
    size = int(image.shape[0])
    
    dll.apply_smooth(newimg,int(iterations),int(shape[0]),int(shape[1]))
    newimg.shape = (newimg.size//shape[1], shape[1])
    return newimg

def fast_combo(image, mode, thresh, iterations):
    """ When applying both threshold and smooth filter, it is convenient to create
    a function that performs both operations, avoiding the unnecessary reshaping of
    the array from 2D -> 1D -> 2D. """

    shape = image.shape
    image = image.flatten()
    newimg = image.copy()
    size = int(image.shape[0])

    dll.threshold(newimg,mode,int(thresh),size)
    dll.apply_smooth(newimg,int(iterations),int(shape[0]),int(shape[1]))
    newimg.shape = (newimg.size//shape[1], shape[1])
    return newimg

if __name__.endswith("__main__"):
    import matplotlib.pyplot as plt

    a = [
            [1,1,1,1,2,2,1,1,1,1],
            [1,1,1,1,2,2,1,1,1,1],
            [1,1,1,1,2,2,1,1,1,1],
            [1,1,1,1,2,2,1,1,1,1],
            [1,1,1,1,2,2,1,1,1,1],
            [1,1,1,1,2,2,1,1,1,1],
            [1,1,1,1,2,2,1,1,1,1],
            [1,1,1,1,2,2,1,1,1,1],
            [1,1,1,1,2,2,1,1,1,1],
            [1,1,1,1,2,2,1,1,1,1],
            [1,1,1,1,2,2,1,1,1,1]
            ]
    
    a = np.asarray(a,dtype="float32")
    b = np.ones([10,10],dtype="float32")+2
    #c = fast_scaling(a,b,scalemode=1,mask=a)
    #c = fast_threshold(a,1,2)
    c = fast_smooth(a,1)

    fig = plt.figure()
    gs = plt.GridSpec(1,2)
    ax1 = fig.add_subplot(gs[0,0])
    ax2 = fig.add_subplot(gs[0,1])
    ax1.imshow(a)
    ax2.imshow(c)
    plt.show()

