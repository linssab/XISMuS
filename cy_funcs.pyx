#################################################################
#                                                               #
#          Cython Functions                                     #
#                        version: 1.0.0 - Mar - 2020            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import cython
import numpy as np
from cpython cimport array
import array

# from ImgMath:

def cy_threshold(float[:,:] a_2D_array, int[:] shape, int t):
    
    """ Applies a threshold filter cutting the values BELOW threshold.
    Returns a 2D-array """

    cdef int x = 0
    cdef int y = 0
    cdef float average = 0.0
    cdef float[:,:] new_array = a_2D_array[:,:]
    for x in range(shape[0]):
        for y in range(shape[1]):
            average = cy_median_filter(a_2D_array,x,y)
            if a_2D_array[x][y] < t and average < t: 
                new_array[x][y] = 0
            else:
                new_array[x][y] = a_2D_array[x][y]
    return new_array

def cy_median_filter(float[:,:] a_2D_array, int x, int y):

    """ Returns the average value of pixel x,y. Includes edges """
    cdef float average = 0.0
    try: average = (2*a_2D_array[x][y] + a_2D_array[x-1][y] + a_2D_array[x+1][y] +\
            a_2D_array[x][y-1] + a_2D_array[x-1][y-1] + a_2D_array[x+1][y-1] +\
            a_2D_array[x][y+1] + a_2D_array[x-1][y+1] + a_2D_array[x+1][y+1])/10
    except: 
        # ignore upper row
        try: average = (2*a_2D_array[x][y] + a_2D_array[x-1][y] + a_2D_array[x+1][y] +\
                a_2D_array[x][y-1] + a_2D_array[x-1][y-1] + a_2D_array[x+1][y-1])/7
        except:
            # ignore lower row
            try: average = (2*a_2D_array[x][y] + a_2D_array[x-1][y] + a_2D_array[x+1][y] +\
                    a_2D_array[x][y+1] + a_2D_array[x-1][y+1] + a_2D_array[x+1][y+1])/7
            except:
                # ignore left column
                try: average = (2*a_2D_array[x][y] + a_2D_array[x+1][y] +\
                        a_2D_array[x][y-1] + a_2D_array[x+1][y-1] +\
                        a_2D_array[x][y+1] + a_2D_array[x+1][y+1])/7
                except:
                    # ignore right column
                    try: average = (2*a_2D_array[x][y] + a_2D_array[x-1][y] +\
                            a_2D_array[x][y-1] + a_2D_array[x-1][y-1] +\
                            a_2D_array[x][y+1] + a_2D_array[x-1][y+1])/7
                    except:
                        try: average = (2*a_2D_array[x][y] + a_2D_array[x+1][y] +\
                                a_2D_array[x][y+1] + a_2D_array[x+1][y+1])/5
                        except:
                            try: average = (2*a_2D_array[x][y] + a_2D_array[x-1][y] +\
                                    a_2D_array[x][y+1] + a_2D_array[x-1][y+1])/5
                            except:
                                try: average = (2*a_2D_array[x][y] + a_2D_array[x+1][y] +\
                                        a_2D_array[x][y-1] + a_2D_array[x+1][y-1])/5
                                except:
                                    try: average = (2*a_2D_array[x][y] + a_2D_array[x-1][y] +\
                                            a_2D_array[x][y-1] + a_2D_array[x-1][y-1])/5
                                    except: average = 0.0
    return average

def cy_iteractive_median(float[:,:] img, int[:] shape, int iterations):

    """ Applies the median_filter funtion to all pixels within a 2D-array.
    iterations is the amount of times the operation will be performed.
    Returns a smoothed 2D-array """
    
    cdef float[:,:] new_image 
    cdef float[:,:] current_image
    new_image = img[:,:]
    current_image = img[:,:]
    cdef int i = 0
    cdef int x = 0
    cdef int y = 0
    for i in range(iterations):
        for x in range(shape[0]):
            for y in range(shape[1]):
                new_image[x][y] = cy_median_filter(current_image,x,y)
        current_img = new_image
    return new_image 

# from Mosaic

def cy_read_pixels(dict layers, int i, int j):
    cdef int front_layer = -1 
    cdef int pixel = 59

    cdef int x = 0
    cdef int y = 0
    cdef int x_ = 0
    cdef int y_ = 0
    cdef int onv_x = 0
    cdef int conv_y = 0

    for layer in layers.keys():
        try:
            x = layers[layer]["start"][0]
            y = layers[layer]["start"][1]
            x_ = layers[layer]["end"][0]
            y_ = layers[layer]["end"][1]
            conv_x, conv_y = i-x, j-y
            if x <= i < x_ and y <= j < y_ \
                    and layers[layer]["layer"] > front_layer:
                pixel = layers[layer]["img"][conv_x][conv_y]
                front_layer = layers[layer]["layer"]
        except:
            return pixel
    return pixel

def cy_build_image(int[:,:] image, int[:] size, dict all_layers):
    cdef int i = 0
    cdef int j = 0
    cdef int[:,:] new_image = image
    for i in range(size[0]):
        for j in range(size[1]):
            new_image[i][j] = cy_read_pixels(all_layers,i,j)
    return new_image

# from SpecMath

def cy_MPS(float[:,:,:] matrix, int[:] m_size, float[:] mps_spec, int spec_size):
    cdef int c = 0
    cdef int x = 0
    cdef int y = 0
    for c in range(spec_size):
        for x in range(m_size[0]):
            for y in range(m_size[1]):
                if mps_spec[c] < matrix[x][y][c]: mps_spec[c] = matrix[x][y][c]
    return mps_spec

