#################################################################
#                                                               #
#          CYTHON FUNCTIONS                                     #
#                        version: 1.0.0 - Mar - 2020            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import cython
import numpy as np
cimport numpy as np
from ProgressBar import Busy

# utils

cdef int cy_second_min(
        int[:,:] matrix, 
        int[:] shape, 
        int[:] TARGET):
    cdef int x = 0
    cdef int y = 0
    cdef int min2 = 0

    for x in range(shape[0]):
        for y in range(shape[1]):
            if matrix[x][y] < TARGET[1] and matrix[x][y] > 0:
                if matrix[x][y] < TARGET[0]:
                    TARGET[0] = matrix[x][y]

def cy_apply_scaling(float[:,:] scale_matrix,
    float[:,:,:] cube_matrix,
    int scale_mode,
    float[:,:,:] scaled_matrix,
    int[:] shape):
    
    for i in range(shape[0]):
        for j in range(shape[1]):
            for c in range(shape[2]):
                if scale_mode == 1:
                    scaled_matrix[i][j][c] = cube_matrix[i][j][c]*scale_matrix[i][j]
                elif scale_mode == -1:
                    scaled_matrix[i][j][c] = cube_matrix[i][j][c]/scale_matrix[i][j]
    return scaled_matrix

def cy_img_linear_contrast_expansion(int[:,:] grayimg, int a, int b,
        int[:] shape, int c, int d):
    
    cdef int i = 0
    cdef int j = 0
    for i in range(shape[0]):
        for j in range(shape[1]):
            grayimg[i][j] = cy_stretch(grayimg[i][j],a,b,c,d)
    return 0

def cy_threshold(float[:,:] a_2D_array, int[:] shape, int t):
    
    """ Applies a threshold filter cutting the values BELOW threshold.
    Returns a 2D-array """

    cdef int x = 0
    cdef int y = 0
    cdef float average = 0.0
    cdef float[:,:] new_array = a_2D_array[:,:]
    for x in range(shape[0]):
        for y in range(shape[1]):
            if a_2D_array[x][y] < t: 
                new_array[x][y] = 0
            else:
                new_array[x][y] = a_2D_array[x][y]
    return new_array

def cy_threshold_low(float[:,:] a_2D_array, int[:] shape, int t):
    
    """ Applies a threshold filter cutting the values ABOVE threshold.
    Returns a 2D-array """

    cdef int x = 0
    cdef int y = 0
    cdef float average = 0.0
    cdef float[:,:] new_array = a_2D_array[:,:]
    for x in range(shape[0]):
        for y in range(shape[1]):
            if a_2D_array[x][y] > t: 
                new_array[x][y] = 0
            else:
                new_array[x][y] = a_2D_array[x][y]
    return new_array

cdef float cy_simple_median(float[:,:] m, int x, int y, list shape):

    """ Returns the average value of pixel x,y. """
    """ For use with Cython exclusively """

    cdef float average = 0.0
    if x == 0:
        if y == 0: 
            return (2*m[x][y] + m[x+1][y] + m[x][y+1] + m[x+1][y+1])/5 #upper-left corner
        elif y == shape[1]-1:
            return (2*m[x][y] + m[x+1][y] + m[x][y-1] + m[x+1][y-1])/5 #upper-right corner
        else:
            return (2*m[x][y] + m[x+1][y] +\
            m[x][y-1] + m[x+1][y-1] +\
            m[x][y+1] + m[x+1][y+1])/7
    elif x == shape[0]-1:
        if y == 0: 
            return (2*m[x][y] + m[x-1][y] + m[x][y+1] + m[x-1][y+1])/5 #bottom-left corner
        elif y == shape[1]-1: 
            return (2*m[x][y] + m[x-1][y] + m[x][y-1] + m[x-1][y-1])/5 #bottom-right corner
        else: 
            return (2*m[x][y]  + m[x-1][y] +\
            m[x][y-1] + m[x-1][y-1] +\
            m[x][y+1] + m[x-1][y+1])/7
    elif y == 0:
        return (2*m[x][y] + m[x-1][y] + m[x+1][y] +\
            m[x][y+1] + m[x-1][y+1] + m[x+1][y+1])/7
    elif y == shape[1]-1:
        return (2*m[x][y] + m[x-1][y] + m[x+1][y] +\
            m[x][y-1] + m[x-1][y-1] + m[x+1][y-1])/7
    else:
        return (2*m[x][y] + m[x-1][y] + m[x+1][y] +\
            m[x][y-1] + m[x-1][y-1] + m[x+1][y-1] +\
            m[x][y+1] + m[x-1][y+1] + m[x+1][y+1])/10

def cy_average(float[:,:] a_2D_array, int x, int y):

    """ Returns the average value of pixel x,y. Ignores edges """
    """ This function can be called by pure python modules """ 
    cdef float average = 0.0
    return (2*a_2D_array[x][y] + a_2D_array[x-1][y] + a_2D_array[x+1][y] +\
            a_2D_array[x][y-1] + a_2D_array[x-1][y-1] + a_2D_array[x+1][y-1] +\
            a_2D_array[x][y+1] + a_2D_array[x-1][y+1] + a_2D_array[x+1][y+1])/10


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
                new_image[x][y] = cy_simple_median(current_image,x,y,[shape[0],shape[1]])
        current_img = new_image
    return new_image 

def cy_subtract(float[:,:] map1, 
        float[:,:] map2, 
        int[:] shape,
        float[:,:] output):

    cdef int i = 0
    cdef int j = 0

    for i in range(shape[0]):
        for j in range(shape[1]):
            output[i][j] = map1[i][j] - map2[i][j]
            if output[i][j] < 0: output[i][j] = 0
    return output


def cy_read_densemap_pixels(dict layers, int i, int j):

    """ Operates over single pixels at a time.
    Reads all layers and returns the uppermost value for the DENSEMAP matrix """

    cdef int front_layer = -1 
    cdef int pixel = 0

    cdef int x = 0
    cdef int y = 0
    cdef int x_ = 0
    cdef int y_ = 0
    cdef int conv_x = 0
    cdef int conv_y = 0

    for layer in layers.keys():
        x = layers[layer]["start"][0]
        y = layers[layer]["start"][1]
        x_ = layers[layer]["end"][0]
        y_ = layers[layer]["end"][1]
        conv_x, conv_y = i-x, j-y
        #print(layers[layer]["layer"],
        #        "index",i,j,"start",x,y,"end",x_,y_,"conv",conv_x,conv_y)
        if x <= i < x_ and y <= j < y_ \
                and layers[layer]["layer"] > front_layer:
            pixel = layers[layer]["dense"][conv_x][conv_y]
            front_layer = layers[layer]["layer"]
    return pixel

def cy_build_densemap(int[:,:] image, 
        int[:] size, 
        dict all_layers, 
        int[:] TARGET):

    """ DENSEMAP image constructor """

    cdef int i = 0
    cdef int j = 0
    for i in range(size[0]):
        for j in range(size[1]):
            image[i][j] = cy_read_densemap_pixels(all_layers,i,j)
            if image[i][j] > TARGET[1]:
                TARGET[0] = image[i][j]
                TARGET[1] = image[i][j]
    cy_second_min(image, size, TARGET)
    return image


def cy_read_pixels(dict layers, int i, int j):

    """ Operates over single pixels at a time.
    Reads all layers and returns the uppermost PIXEL value """

    cdef int front_layer = -1 
    cdef int pixel = 59

    cdef int x = 0
    cdef int y = 0
    cdef int x_ = 0
    cdef int y_ = 0
    cdef int conv_x = 0
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

def cy_build_image(int[:,:] image, int[:,:] boundaries, dict all_layers):

    """ Display image constructor.
    Builds the image to be shown at Mosaic screen """
        
    cdef int i = 0
    cdef int j = 0
    cdef int[:,:] new_image = image

    for i in range(boundaries[0][0],boundaries[0][1]):
        for j in range(boundaries[1][0],boundaries[1][1]):
            new_image[i][j] = cy_read_pixels(all_layers,i,j)
    return new_image

def cy_build_merge_cube(dict layers, 
        int[:] x_limit, 
        int[:] y_limit, 
        float[:] spectrum,
        float[:,:,:] cube_matrix,
        int size):
    
    cdef int total_iterations = 0
    total_iterations = (x_limit[1]-x_limit[0])

    """ DATACUBE constructor. Calls cy_pack_spectra() to grab the
    corresponding spectrum and attribute it to the new datacube x y index. """

    cdef int i = 0
    cdef int j = 0
    cdef int c = 0
    cdef int x = 0
    cdef int y = 0
    cdef int iterator = 0
    
    print("Started packing")
    mec = Busy(total_iterations,0)
    for i in range(x_limit[0],x_limit[1]):
        for j in range(y_limit[0],y_limit[1]):
            cy_pack_spectra(
                    layers,
                    i,
                    j,
                    spectrum,
                    size)
            for c in range(size):
                cube_matrix[x][y][c] = spectrum[c]
            c = 0
            y+=1
        i = 0
        y = 0
        x+=1
        iterator += 1
        mec.updatebar(iterator)
    mec.destroybar()
    print("Finished packing, bar destroyed")
    return 1

def cy_pack_spectra(dict layers, 
        int i, 
        int j, 
        float[:] specout, 
        int shape):

    """ Similar to pixel reader functions, but instead or returning one value,
    it returns a spectrum array """
    """ OBS: Function MODIFIES specout variable, 
    as it is passed as a memoryview object """

    cdef int front_layer = -1 
    
    cdef int x = 0
    cdef int y = 0
    cdef int x_ = 0
    cdef int y_ = 0
    cdef int conv_x = 0
    cdef int conv_y = 0
    cdef int c = 0
    
    for layer in layers.keys():
        x = layers[layer]["start"][0]
        y = layers[layer]["start"][1]
        x_ = layers[layer]["end"][0]
        y_ = layers[layer]["end"][1]
        conv_x, conv_y = i-x, j-y
        if x <= i < x_ and y <= j < y_ \
            and layers[layer]["layer"] > front_layer:
                for c in range(shape):
                    specout[c] = layers[layer]["matrix"][conv_x][conv_y][c]
                    front_layer = layers[layer]["layer"]
    if front_layer >= 0: 
        return specout
    else: 
        for c in range(shape):
            specout[c] = 0.0
        return specout

cdef int cy_stretch(int r, int a, int b, int c, int d):
    # b and d are the target and local maxima respectively
    # if the maximum is zero, than the whole image is zero
    cdef int toss = 0
    if b == 0 or d == 0: return r
    else: 
        toss = int(((r-c)*((b-a)/(d-c)))+a)
    return toss

def cy_build_scaling_matrix(float[:,:] scale_matrix, 
        int[:] size, 
        dict all_layers,
        int[:] target,
        int gross,
        int mode):
    
    cdef int i = 0
    cdef int j = 0
    for i in range(size[0]):
        for j in range(size[1]):
            if mode == 1:
                scale_matrix[i][j] = cy_get_linstr_scaling(all_layers,i,j,target)
            elif mode == 2:
                scale_matrix[i][j] = cy_get_sum_scaling(all_layers,i,j,gross)
            else:
                return scale_matrix
    return scale_matrix

def cy_get_linstr_scaling(dict layers, int i, int j,int[:] target):
    cdef int front_layer = -1 
    cdef float scaling = 1.0

    cdef int x = 0
    cdef int y = 0
    cdef int x_ = 0
    cdef int y_ = 0
    cdef int conv_x = 0
    cdef int conv_y = 0

    cdef int r = 0
    cdef float s = 0

    for layer in layers.keys():
        try:
            x = layers[layer]["start"][0]
            y = layers[layer]["start"][1]
            x_ = layers[layer]["end"][0]
            y_ = layers[layer]["end"][1]
            conv_x, conv_y = i-x, j-y
            if x <= i < x_ and y <= j < y_ \
                    and layers[layer]["layer"] > front_layer:
                loc_max = layers[layer]["max"]
                loc_min = layers[layer]["min"]
                r = layers[layer]["dense"][conv_x][conv_y]
                if r == 0: return 1.0
                else: pass 
                s = cy_stretch(r,target[0],target[1],loc_min,loc_max)
                scaling = s/r
                front_layer = layers[layer]["layer"]
        except:
            return scaling
    return scaling

def cy_get_sum_scaling(dict layers, int i, int j, int gross):
    cdef int front_layer = -1 
    cdef float scaling = 1.0

    cdef int x = 0
    cdef int y = 0
    cdef int x_ = 0
    cdef int y_ = 0
    cdef int conv_x = 0
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
                layer_max = layers[layer]["dense"].sum()/((x-x_)*(y-y_))
                scaling = gross/layer_max
                front_layer = layers[layer]["layer"]
        except:
            return scaling
    return scaling

def cy_MPS(float[:,:,:] matrix, int[:] m_size, float[:] mps_spec, int spec_size):
    cdef int c = 0
    cdef int x = 0
    cdef int y = 0
    for c in range(spec_size):
        for x in range(m_size[0]):
            for y in range(m_size[1]):
                if mps_spec[c] < matrix[x][y][c]: mps_spec[c] = matrix[x][y][c]
    return mps_spec

