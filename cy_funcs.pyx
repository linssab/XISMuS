#################################################################
#                                                               #
#          CYTHON FUNCTIONS                                     #
#                        version: 1.3.0 - Oct - 2020            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import cython
import numpy as np
cimport numpy as np
from GUI import Busy

cdef int cy_second_min(
        float[:,:] matrix, 
        int[:] shape, 
        float[:] TARGET):
    cdef int x = 0
    cdef int y = 0

    for x in range(shape[0]):
        for y in range(shape[1]):
            if matrix[x][y] < TARGET[1] and matrix[x][y] > 0:
                if matrix[x][y] < TARGET[0]:
                    TARGET[0] = matrix[x][y]

def cy_stack(int[:,:,:] stack, 
        int[:,:] a, 
        int[:,:] b,
        int[:] shape):

    cdef int i = 0
    cdef int j = 0

    for i in range(shape[0]):
        for j in range(shape[1]):
            stack[i][j][0] = a[i][j]
            stack[i][j][1] = b[i][j]

def cy_apply_scaling(float[:,:] scale_matrix,
    float[:,:] image,
    int scale_mode,
    int[:] shape):
 
    for i in range(shape[0]):
        for j in range(shape[1]):
            if scale_mode == 1 and scale_matrix[i][j] != 0:
                image[i][j] = image[i][j]*scale_matrix[i][j]
            elif scale_mode == -1 and scale_matrix[i][j] != 0:
                image[i][j] = image[i][j]/scale_matrix[i][j]
    return

###################################################################
# Now the mask is applied to IMAGES only, not the dataset anymore #
# The function below has been replaced by that above              #
###################################################################
"""
def cy_apply_scaling(float[:,:] scale_matrix,
    float[:,:,:] cube_matrix,
    int scale_mode,
    int[:] shape):
    
    mec = Busy(shape[0],0)
    mec.update_text("4/11 Applying scale factor...")
    for i in range(shape[0]):
        for j in range(shape[1]):
            for c in range(shape[2]):
                if scale_mode == 1:
                    cube_matrix[i][j][c] = cube_matrix[i][j][c]*scale_matrix[i][j]
                elif scale_mode == -1 and scale_matrix[i][j] != 0:
                    cube_matrix[i][j][c] = cube_matrix[i][j][c]/scale_matrix[i][j]
        mec.updatebar(i)
    mec.destroybar()
"""

def cy_img_linear_contrast_expansion(float[:,:] grayimg, int a, int b,
        int[:] shape, int c, int d):

    # b and d are the target and local maxima respectively
    # if the maximum is zero, than the whole image is zero
    
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
            if a_2D_array[x,y] > t: 
                new_array[x,y] = 0
            else:
                new_array[x,y] = a_2D_array[x,y]
    return new_array

cdef float cy_simple_median(float[:,:] m, int x, int y, list shape):
    """ Returns the average value of pixel x,y. """
    """ For use with Cython exclusively """

    cdef float average = 0.0
    if x == 0:
        if y == 0: 
            return (2*m[x,y] + m[x+1,y] + m[x,y+1] + m[x+1,y+1])/5 #upper-left corner
        elif y == shape[1]-1:
            return (2*m[x,y] + m[x+1,y] + m[x,y-1] + m[x+1,y-1])/5 #upper-right corner
        else:
            return (2*m[x,y] + m[x+1,y] +\
            m[x,y-1] + m[x+1,y-1] +\
            m[x,y+1] + m[x+1,y+1])/7
    elif x == shape[0]-1:
        if y == 0: 
            return (2*m[x,y] + m[x-1,y] + m[x,y+1] + m[x-1,y+1])/5 #bottom-left corner
        elif y == shape[1]-1: 
            return (2*m[x,y] + m[x-1,y] + m[x,y-1] + m[x-1,y-1])/5 #bottom-right corner
        else: 
            return (2*m[x,y]  + m[x-1,y] +\
            m[x,y-1] + m[x-1,y-1] +\
            m[x,y+1] + m[x-1,y+1])/7
    elif y == 0:
        return (2*m[x,y] + m[x-1,y] + m[x+1,y] +\
            m[x,y+1] + m[x-1,y+1] + m[x+1,y+1])/7
    elif y == shape[1]-1:
        return (2*m[x,y] + m[x-1,y] + m[x+1,y] +\
            m[x,y-1] + m[x-1,y-1] + m[x+1,y-1])/7
    else:
        return (2*m[x,y] + m[x-1][y] + m[x+1,y] +\
            m[x,y-1] + m[x-1,y-1] + m[x+1,y-1] +\
            m[x,y+1] + m[x-1,y+1] + m[x+1,y+1])/10

def cy_average(float[:,:] a_2D_array, int x, int y):
    """ Returns the average value of pixel x,y. Ignores edges """
    """ This function can be called by pure python modules """ 
    cdef float average = 0.0
    return (2*a_2D_array[x,y] + a_2D_array[x-1,y] + a_2D_array[x+1,y] +\
            a_2D_array[x,y-1] + a_2D_array[x-1,y-1] + a_2D_array[x+1,y-1] +\
            a_2D_array[x,y+1] + a_2D_array[x-1,y+1] + a_2D_array[x+1,y+1])/10

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
                new_image[x,y] = cy_simple_median(current_image,x,y,[shape[0],shape[1]])
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
            output[i,j] = map1[i,j] - map2[i,j]
            if output[i,j] < 0: output[i,j] = 0
    return output

def cy_add(float[:,:] map1, 
        float[:,:] map2, 
        int[:] shape,
        float[:,:] output):

    cdef int i = 0
    cdef int j = 0

    for i in range(shape[0]):
        for j in range(shape[1]):
            output[i,j] = map1[i,j] + map2[i,j]
    return output

def cy_read_densemap_pixels(dict layers, int i, int j, int mode):
    """ Operates over single pixels at a time.
    Reads all layers and returns the uppermost value for the DENSEMAP matrix """

    cdef int front_layer = -1 
    cdef float pixel = 0

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
        if x <= i < x_ and y <= j < y_ \
                and layers[layer]["layer"] > front_layer:
            if mode == 1: 
                pixel = layers[layer]["dense"][conv_x][conv_y]
            elif mode == 2: 

                # To avoid ZeroDivision when creating the mask, each img pixel has
                # its value increased by one. Therefore, "empty" pixels are equal to 1

                if layers[layer]["img"][conv_x][conv_y] > 1.001:
                    pixel = layers[layer]["mask"][conv_x][conv_y]
                else: pixel = 0
                
                #####################################################################

            front_layer = layers[layer]["layer"]
    return pixel

def cy_iterate_img_and_mask(
        float[:,:] img,
        float[:,:] mask,
        int[:] shape,
        float[:,:] xy,
        float a,
        float b):

    cdef int i = 0
    cdef int j = 0
    cdef float x1 = xy[0,0]
    cdef float y1 = xy[1,0]
    cdef float x2 = xy[0,1]
    cdef float y2 = xy[1,1]

    for i in range(shape[0]):
        for j in range(shape[1]):
            if img[i,j] <= x1:
                mask[i,j] = y1/img[i,j]
            elif img[i,j] >= x2:
                mask[i,j] = y2/img[i,j]
            else:
                mask[i,j] = (img[i,j]*a + b)/img[i,j]
    return

def cy_build_densemap(float[:,:] image, 
        int[:] size, 
        dict all_layers, 
        float[:] TARGET,
        int mode):

    """ DENSEMAP image constructor """

    cdef int i = 0
    cdef int j = 0
    for i in range(size[0]):
        for j in range(size[1]):
            image[i,j] = cy_read_densemap_pixels(all_layers,i,j,mode)
            if image[i,j] > TARGET[1]:
                TARGET[0] = image[i,j]
                TARGET[1] = image[i,j]
    cy_second_min(image, size, TARGET)
    return image

def cy_read_pixels(dict layers, int i, int j):
    """ Operates over single pixels at a time.
    Reads all layers and returns the uppermost PIXEL value """

    cdef int front_layer = -1 
    cdef float pixel = 59.0
    cdef int v = 0

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
                v = layers[layer]["img"][conv_x,conv_y]
                if v > 0:
                    pixel = v
                    front_layer = layers[layer]["layer"]
                else: pass
        except:
            return pixel
    return pixel

def cy_build_image(float[:,:] image, int[:,:] boundaries, dict all_layers):
    """ Display image constructor.
    Builds the image to be shown at Mosaic screen """
        
    cdef int i = 0
    cdef int j = 0
    cdef float[:,:] new_image = image

    for i in range(boundaries[0,0],boundaries[0,1]):
        for j in range(boundaries[1,0],boundaries[1,1]):
            new_image[i,j] = cy_read_pixels(all_layers,i,j)
    return new_image

def cy_build_merge_cube(dict layers, 
        int[:] x_limit, 
        int[:] y_limit, 
        int[:] spectrum,
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
    mec.update_text("3/11 Merging...")
    for i in range(x_limit[0],x_limit[1]):
        for j in range(y_limit[0],y_limit[1]):
            cy_pack_spectra(
                    layers,
                    i,
                    j,
                    spectrum,
                    size)
            for c in range(size):
                cube_matrix[x,y,c] = spectrum[c]
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
        int[:] specout, 
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
    cdef int v = 0
    
    for layer in layers.keys():
        x = layers[layer]["start"][0]
        y = layers[layer]["start"][1]
        x_ = layers[layer]["end"][0]
        y_ = layers[layer]["end"][1]
        conv_x, conv_y = i-x, j-y
        if x <= i < x_ and y <= j < y_ \
            and layers[layer]["layer"] > front_layer:
                v = layers[layer]["img"][conv_x,conv_y]
                if v != 0:
                    for c in range(shape):
                        specout[c] = layers[layer]["matrix"][conv_x,conv_y,c]
                        front_layer = layers[layer]["layer"]
    if front_layer >= 0: 
        return specout
    else: 
        for c in range(shape):
            specout[c] = 0
        return specout

cdef float cy_stretch(float r, float a, float b, float c, float d):
    # b and d are the target and local maxima respectively
    # if the maximum is zero, than the whole image is zero
    cdef float toss = 0
    if b == 0 or d == 0: return r
    else: 
        toss = ((r-c)*((b-a)/(d-c)))+a
    return toss

def cy_build_intense_scaling_matrix(
        float[:,:] m,
        int[:] shape,
        dict all_layers):

    def read_value(dict layers, int i, int j):
        """ Operates over single pixels at a time.
        Reads all layers and returns the uppermost PIXEL value """

        cdef int front_layer = -1
        cdef float pixel = 0.0

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
                    pixel = layers[layer]["max"]
                    front_layer = layers[layer]["layer"]
            except:
                return pixel
        return pixel

    cdef int i = 0
    cdef int j = 0
    for i in range(shape[0]):
        for j in range(shape[1]):
            m[i,j] = read_value(all_layers,i,j)

def cy_build_scaling_matrix(float[:,:] scale_matrix, 
        int[:] size, 
        dict all_layers,
        float[:] target,
        int gross,
        int mode):
    
    mec = Busy(size[0],0)
    mec.update_text("2/11 Creating scale matrix...")
    cdef int i = 0
    cdef int j = 0
    cdef int iterator = 0
    for i in range(size[0]):
        for j in range(size[1]):
            iterator += 1
            if mode == 1:
                scale_matrix[i,j] = cy_get_linstr_scaling(all_layers,i,j,target)
            elif mode == 2:
                scale_matrix[i,j] = cy_get_sum_scaling(all_layers,i,j,gross)
            else:
                return scale_matrix
        mec.updatebar(i)
    mec.destroybar()
    return scale_matrix

def cy_get_linstr_scaling(dict layers, int i, int j, float[:] target):
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
                r = layers[layer]["dense"][conv_x,conv_y]
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

def cy_MPS(int[:,:,:] matrix, int[:] m_size, int[:] mps_spec, int spec_size):
    cdef int c = 0
    cdef int x = 0
    cdef int y = 0
    for c in range(spec_size):
        for x in range(m_size[0]):
            for y in range(m_size[1]):
                if mps_spec[c] < matrix[x,y,c]: mps_spec[c] = matrix[x,y,c]
    return mps_spec

