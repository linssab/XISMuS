#################################################################
#                                                               #
#          IMAGE MATH	                                        #
#                        version: 1.3.1 - Oct - 2020            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

""" import all modules """

import logging, os, time
import threading
logger = logging.getLogger("logfile")
logger.info("Importing module ImgMath.py...")
import numpy as np
import SpecRead
import Constants
import cy_funcs
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
logger.debug("Importing module matplotlib.colors...")
from matplotlib.colors import ListedColormap
logger.debug("Importing module mpl_toolkits.axes_grid1...")
try: from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
except: logger.warning("Failed to load make_axes_locatable from mpl_toolkits.axes_grid1.axes_divider")
import cv2
import math
logger.info("Finished ImgMath imports.")

""" Set the gray levels variable """

LEVELS = 255

def colorbar(mappable):
    ##############################################
    # FROM:                                      #
    # https://joseph-long.com/writing/colorbars/ #
    ##############################################
    """ Adds a colorblar with correct colormap next to subplot axis """
    
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    return fig.colorbar(mappable, cax=cax)

def mse(img1, img2):
    """ Returns the mean-squared error between two images """
    error = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
    error = error/float(img1.shape[0] * img2.shape[1])
    return error

def median_filter(array,x,y):
    """ Returns the average value of pixel x,y. Includes edges """

    average = cy_funcs.cy_average(array,x,y)
    return average

def iteractive_median(img,iterations=1):
    """ Applies the median_filter funtion to all pixels within a 2D-array.
    iterations is the amount of times the operation will be performed.
    Returns a smoothed 2D-array """

    shape = np.asarray(img.shape)
    cy_funcs.cy_iteractive_median(img, shape, iterations)
    return img

def threshold(a_2D_array,t):
    """ Applies a threshold filter cutting the values BELOW threshold.
    Returns a 2D-array """

    if len(a_2D_array.shape) != 2:
        raise ValueError("Input shape {} is not bi-dimensional")
    shape = np.asarray(a_2D_array.shape)
    cy_funcs.cy_threshold(a_2D_array, shape, t)
    return a_2D_array

def low_pass(a_2D_array,t):
    """ Applies a threshold filter cutting the values ABOVE threshold.
    Returns a 2D-array """

    if len(a_2D_array.shape) != 2:
        raise ValueError("Input shape {} is not bi-dimensional")
    shape = np.asarray(a_2D_array.shape)
    cy_funcs.cy_threshold_low(a_2D_array, shape, t)
    return a_2D_array

def apply_scaling(datacube, image, scalemode=0, mask=np.zeros(0)):
    """ scalemode:
    0 = Returns
    1 = Applies scaling to datacube.matrix
    -1 = Reverse scaling applied to datacube.matrix """

    if scalemode == 0: return
    else:
        if mask.any(): scaling_matrix = mask
        else: scaling_matrix = datacube.scale_matrix
        cy_funcs.cy_apply_scaling(scaling_matrix,
                image,
                scalemode,
                np.asarray(image.shape,dtype="int32"))
        return image

def mask(a_datacube,a_compound,mask_threshold):
    """ Creates a mask to limit the heightmap calculation.
    
    ------------------------------------------------------

    INPUT:
        a_datacube; cube class object
        a_compound; compound class object
        mask_threshold; int
    OUTPUT:
        id_element_matrix; a 2D-array """

    try: 

        #####################################################
        # tries to get identity element from compound       #
        # if compound has no identity, tries to create it   #
        #####################################################

        id_element = a_compound.identity
    except: 
        unpacked = []
        abundance = 0
        for key in a_compound.weight:
            unpacked.append(key)
            if a_compound.weight[key] > abundance: 
                id_element, abundance = key, a_compound.weight[key]
    
    try: 

        ######################################################################
        # tries to unpack an element map from cube class object              #
        # if it fails, looks for a ratio txt file under the cube file folder #
        ######################################################################

        id_element_matrix = a_datacube.unpack_element(id_element,"a")
    except:
        try: 
            id_element_ratio = os.path.join(SpecRead.output_path,"{1}_ratio_{0}.txt".format(
                    id_element,Constants.DIRECTORY))
            id_element_matrix = SpecRead.RatioMatrixReadFile(id_element_ratio)
        except: raise FileNotFoundError("{0} ratio file not found!".format(id_element))
    
    id_element_matrix = id_element_matrix/id_element_matrix.max()*LEVELS
    id_element_matrix = threshold(id_element_matrix,mask_threshold)

    return id_element_matrix

def getheightmap(depth_matrix,mask,thickratio,compound):
    """ Creates a heightmap of a given layer on top of the samples substrate through
    the differential attenuation method.
    The function writes the thickness values to a txt file.
    
    References:
    [1] Cesareo, R.; Rizzutto, M.A.; Brunetti, A.; Rao, D. v. Metal location and 
        thickness in a multilayered sheet by measuring Kα/Kβ, Lα/Lβ and 
        Lα/Lγ X-ray ratios. Nucl Instrum Methods Phys Res B 2009; 267, 2890-2896
    [2] Barcellos Lins, S.A.; Ridolfi, S.; Gigante, G.E.; Cesareo, R.; Albini, M.; 
        Riccucci C.; di Carlo, G.; Fabbri, A.; 401 Branchini, P.; Tortora, L. 
        Differential X-Ray Attenuation in MA-XRF Analysis for a Non-invasive 
        Determination of Gilding Thickness. Front. Chem 2020, 8, 1-9
    [3] Nardes, R. C., Silva, M. S., Rezier, A. N. S., Sanches, F. A. C. R. A., 
        Filho, H. S. G., and Santos, R. S. (2019). Study on Brazilian 18th century 
        imperial carriage using x-ray nondestructive techniques. Radiat. Phys. 
        Chem. 154, 74–78.

    --------------------------------------------------------------------------------

    INPUT:
        depth_matrix; a 2D-array
        mask; a 2D-array
        thickratio; float
        compound; compound class object
    OUTPUT:
        heightmap; a 2D-array
        median; float
        deviation; float """

    average = [[],0]
    imagesize = mask.shape
    imagex = imagesize[0]
    imagey = imagesize[1]
    heightmap = np.zeros([imagex,imagey])
    coefficients = compound.lin_att
    
    heightfile = open(os.path.join(SpecRead.output_path,f"{Constants.DIRECTORY}_heightmap.txt"),'w+')
    heightfile.write("-"*10 + f" Thickness Values (um) of {compound.name} " + 10*"-" + '\n')
    heightfile.write("row\tcolumn\tthickness\n")

    mu1 = coefficients[0]
    mu2 = coefficients[1]
    logger.warning(f"mu1 = {mu1} / mu2 = {mu2}")
    
    ANGLE = 90
    for i in range(len(depth_matrix)):
        for j in range(len(depth_matrix[i])):
            if depth_matrix[i][j] > 0 and mask[i][j] > 0.001:
                d = (math.sin(math.radians(ANGLE))/(-mu1+mu2))*(math.log((depth_matrix[i][j]/thickratio)))
            else: d = 0
            
            #############################################
            #  WRITES d TO HEIGHMAP AND CONVERTS TO um  #
            #############################################

            if d <= 0: heightmap[i][j] = 0
            else: heightmap[i][j] = 10000 * d
             
            if d > 0: 
                heightfile.write(f"{i}\t{j}\t{heightmap[i][j]}\n")
                average[0].append(d)
                average[1] = average[1]+1  #counts how many values are
    
    median = sum(average[0])/(average[1])*10000  #calculates the average (mean) value
    deviation = np.std(average[0])*10000         #calculates the standard deviation

    print(f"Deviation {deviation}")
    print(f"Average {median}")
    print("max: {0} min: {1}".format(max(average[0])*10000,min(average[0])*10000))
    heightfile.write("Average: {0}um, sampled points: {1}".format(median,average[1]))
    return heightmap, median, deviation

def set_axes_equal(ax,z_lim):
    #####################################################
    #   set_axes_equal(ax) FUNCTION OBTAINED FROM:      #
    #   https://stackoverflow.com/questions/13685386    #
    #####################################################
    """ Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

    ----------------------------------------------------------------------------

    INPUT:
      ax; a matplotlib axis, e.g., as output from plt.gca() """

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()
    
    ax.set_xlabel("mm")
    ax.set_ylabel("mm")
    ax.set_zlabel("Thickness (μm)")

    x_range = abs(x_limits[1] - x_limits[0])
    x_middle = np.mean(x_limits)
    y_range = abs(y_limits[1] - y_limits[0])
    y_middle = np.mean(y_limits)
    z_range = abs(z_limits[1] - z_limits[0])
    z_middle = np.mean(z_limits)

    # The plot bounding box is a sphere in the sense of the infinity
    # norm, hence I call half the max range the plot radius.
    plot_radius = 0.5*max([x_range, y_range, z_range])

    ax.set_xlim3d([x_middle - plot_radius, x_middle + plot_radius])
    ax.set_ylim3d([y_middle - plot_radius, y_middle + plot_radius])
    ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])
    #ax.set_zlim3d([z_middle - 1, z_middle + 1])
    if z_lim == None: ax.set_zlim3d([0, plot_radius])
    else: ax.set_zlim3d([0, z_lim])

def plot3D(depth_matrix,z_lim=None):
    """ Displays a 3D-plot of a heightmap.

    --------------------------------------

    INPUT:
        depth_matrix; a 2D-array
        z_lim (optional); int
    OUTPUT:
        0 """

    fig = plt.figure()
    ax = fig.gca(projection = '3d')
    imagesize = depth_matrix.shape
    imagex = np.arange(imagesize[0])
    imagey = np.arange(imagesize[1])
    Z = []
    X, Y = np.meshgrid(imagex,imagey)
    for i in range(len(depth_matrix)):
        for j in range(len(depth_matrix[i])):
            if depth_matrix[i][j] > 0: Z.append(depth_matrix[i][j])
            else: Z.append(np.nan)

    depth_matrix = depth_matrix.transpose()
    MAP = ax.plot_surface(X,Y,depth_matrix,\
            cmap='BuGn',linewidth=0,antialiased=True)
    set_axes_equal(ax,z_lim)
    fig.savefig(os.getcwd()+'\\myimage.svg', format='svg', dpi=1200)
    plt.show()
    return 0

def colorize(elementmap,color=None):
    """ Adds a third dimension to a 2D-array image. Pixels becomes a 4 element list
    instead of being a single value.

    -------------------------------------------------------------------------------

    INPUT:
        elementmap; 2D-array
        color (optional); string
    OUTPUT:
        image; 3D-array """    

    imagesize = elementmap.shape
    imagex = imagesize[0]
    imagey = imagesize[1]
    imagedimension = imagex*imagey
    R = np.zeros([imagex,imagey])
    G = np.zeros([imagex,imagey])
    B = np.zeros([imagex,imagey])
    A = np.zeros([imagex,imagey])
    elmap = elementmap
    pixel = []
    myimage = [[]]*(imagex)
    if color == 'red':
        R=R+elmap
        G=G+0
        B=B+0
        A=A+255
    elif color == 'green':
        R=R+0
        G=G+elmap
        B=B+0
        A=A+255
    elif color == 'blue':
        R=R+0
        G=G+0
        B=B+elmap
        A=A+255
    elif color == 'gold':
        R=(R+elmap+255)
        R=R/R.max()*255
        G=(G+elmap+215)
        G=G/G.max()*215
        B=B+0
        A=A+255
    elif color == 'copper':
        R=(R+elmap+184)
        R=R/R.max()*184
        G=(G+elmap+115)
        G=G/G.max()*115
        B=(B+elmap+51)
        B=B/B.max()*51
        A=A+255
    elif color == 'gray':
        R=R+elmap
        G=G+elmap
        B=B+elmap
        A=A+255
    for line in range(imagex):    
        for i in range(imagey):
            if elmap[line][i] > 0:
                pixel.append(np.array([R[line][i],G[line][i],B[line][i],A[line][i]],
                    dtype='float32'))
            else: pixel.append(np.array([0,0,0,A[line][i]],dtype='float32'))
            myimage[line]=np.asarray(pixel,dtype='uint8')
        pixel = []
    image = np.asarray(myimage)
    return image

def createcmap(color):
    """ Creates a mappable colormap to be used with matplotlib.

    -----------------------------------------------------------

    INPUT:
        color; int
    OUTPUT:
        cmap; matplotlib colors object """ 

    z = z = np.zeros(256)
    R = np.linspace(0,1,256)/(256-color[0])
    G = np.linspace(0,1,256)/(256-color[1])
    B = np.linspace(0,1,256)/(256-color[2])

    alpha = np.ones(256)

    colorcode = np.c_[R,G,B,alpha]
    cmap = ListedColormap(colorcode)
    return cmap

def flattenhistogram(image):
    """ test """

    hist,bins = np.histogram(image.flatten(),256,[0,256])
    cdf = hist.cumsum()
    cdf_norm = cdf * hist.max()/cdf.max()
    cdf_mask = np.ma.masked_equal(cdf,0)
    cdf_mask = (cdf_mask - cdf_mask.min())*255/(cdf_mask.max()-cdf_mask.min())
    cdf = np.ma.filled(cdf_mask,0).astype('uint8')
    image = cdf[image]
    return image

def hist_match(source, template):
    """
    TAKEN FROM: https://stackoverflow.com/questions/32655686/histogram-matching-of-two-images-in-python-2-x
    Adjust the pixel values of a grayscale image such that its histogram
    matches that of a target image

    Arguments:
    -----------
        source: np.ndarray
            Image to transform; the histogram is computed over the flattened
            array
        template: np.ndarray
            Template image; can have different dimensions to source
    Returns:
    -----------
        matched: np.ndarray
            The transformed output image
    """

    oldshape = source.shape
    source = source.ravel()
    template = template.ravel()

    # get the set of unique pixel values and their corresponding indices and
    # counts
    s_values, bin_idx, s_counts = np.unique(source, return_inverse=True,
                                            return_counts=True)
    t_values, t_counts = np.unique(template, return_counts=True)

    # take the cumsum of the counts and normalize by the number of pixels to
    # get the empirical cumulative distribution functions for the source and
    # template images (maps pixel value --> quantile)
    s_quantiles = np.cumsum(s_counts).astype(np.float64)
    s_quantiles /= s_quantiles[-1]
    t_quantiles = np.cumsum(t_counts).astype(np.float64)
    t_quantiles /= t_quantiles[-1]

    # interpolate linearly to find the pixel values in the template image
    # that correspond most closely to the quantiles in the source image
    interp_t_values = np.interp(s_quantiles, t_quantiles, t_values)

    return interp_t_values[bin_idx].reshape(oldshape)

def interpolate_zeros(map_array):
    """ Fills few dead pixels present in auto_roi elemental maps caused by low
    counts, peak identification failure or other issues while generating the map.
    The pixel is filled if any of its right and left neighbors is different than 0.

    -------------------------------------------------------------------------------

    INPUT:
        map_array; 4D-array of maps [x, y, lines ([0] or [0,1]), elements]
        or a 3D-array of maps [lines ([0] or [0,1]), x, y]
    OUTPUT:
        new_map; according to input """

    new_map = map_array[:]
    try: 
        for Element in range(map_array.shape[3]):
            for line in range(map_array.shape[2]):
                for x in range(1,map_array.shape[0]-1,1):
                    for y in range(1,map_array.shape[1]-1,1):
                        a,b,c = map_array[x-1,y-1,line,Element],\
                                map_array[x-1,y,line,Element],\
                                map_array[x-1,y+1,line,Element]
                        before = [a,b,c]
                        d,e,f = map_array[x-1,y-1,line,Element],\
                                map_array[x-1,y,line,Element],\
                                map_array[x-1,y+1,line,Element]
                        after = [d,e,f]
                        if map_array[x,y,line,Element] == 0 and any(before) and any(after): 
                            # median_filter only accepts 2D-arrays
                            newvalue = median_filter(map_array[:,:,line,Element],x,y)
                            new_map[x,y,line,Element] = newvalue
    except:
        
        ##############################################################################
        # to work with multiprocess images were the input objects shape is different #
        # in multiprocessing each map is digested individually                       #
        ##############################################################################

        for line in range(map_array.shape[0]):
            for x in range(1,map_array.shape[1]-1,1):
                for y in range(1,map_array.shape[2]-1,1):
                    a,b,c = map_array[line,x-1,y-1],\
                            map_array[line,x-1,y],\
                            map_array[line,x-1,y+1]
                    before = [a,b,c]
                    d,e,f = map_array[line,x-1,y-1],\
                            map_array[line,x-1,y],\
                            map_array[line,x-1,y+1]
                    after = [d,e,f]
                    if map_array[line,x,y] == 0 and any(before) and any(after): 
                        newvalue = median_filter(map_array[line,:,:],x,y)
                        new_map[line,x,y] = newvalue
    return new_map

def plotlastmap(image,name):
    """ test """

    fig, ax = plt.subplots()
    plt.imshow(image)
    ax.set_title(name)
    plt.show()

def split_and_save(datacube,map_array,element_list,force_alfa_and_beta=False):
    """ Sorts the element maps contained in map_array and packs them into the
    datacube cube class object prior pickling to disk. Saves each map as a grayscale png
    image, enlarged if the map dimension is smaller than target_size.

    ------------------------------------------------------------------------------------

    INPUT:
        datacube; cube class object
        map_array; 4D-array
        element_list; list """

    if datacube.config["ratio"] or force_alfa_and_beta:
        lines = np.asarray(["a","b"])
    else: lines = np.asarray(["a"])

    imagsize = datacube.dimension
    imagex = imagsize[0]
    imagey = imagsize[1]
    image = np.zeros([imagex,imagey])

    cmap = createcmap([255,215,51])
    
    target_size = 1024
    factor = target_size/max(imagsize)
    newX,newY = int(factor*imagex),int(factor*imagey)

    fig, axs = plt.subplots(1,len(element_list),sharey=True)
    
    fig_list = []
    for Element in range(len(element_list)):
        for line in range(lines.shape[0]):

            if line == 0: siegbahn = "_a"
            else: siegbahn = "_b"

            image = map_array[:,:,line,Element]
            raw_image = map_array[:,:,line,Element]

            Constants.MY_DATACUBE.max_counts[element_list[Element]+siegbahn] = image.max()
            print(element_list[Element],image.max())

            if image.max() > 0: image = image/image.max()*LEVELS
             
            histogram,bins = np.histogram(image.flatten(),LEVELS,[0,LEVELS])
            datacube.pack_element(raw_image,element_list[Element],lines[line])
            if lines[line] == "a": datacube.pack_hist(histogram,bins,element_list[Element])
            
            # test histogram
            #plt.hist(datacube.__dict__[element_list[Element]],bins='auto')
            #plt.show()
            
            if len(element_list) > 1: ax = axs[Element]
            else: ax=axs
            fig_list.append(ax.imshow(image,cmap='gray'))
            colorbar(fig_list[Element])
            if datacube.config['ratio'] == False:
                ax.set_title(element_list[Element]+' alpha line')
            else: ax.set_title(element_list[Element])
            
            if imagex > target_size or imagey > target_size: 
                large_image = image/image.max()*255
            else: 
                if image.max() > 0: 
                    large_image = image/image.max()*255
                else:
                    large_image = image
                large_image = cv2.resize(
                        large_image,
                        (newY,newX),
                        interpolation=cv2.INTER_NEAREST)
            save_path = os.path.join(SpecRead.workpath,"output",Constants.DIRECTORY,       
            "{0}_bgtrip={1}_ratio={2}_enhance={3}_peakmethod={4}.png".format(
                    element_list[Element]+"_"+lines[line],
                    datacube.config.get('bgstrip'),
                    datacube.config.get('ratio'),
                    datacube.config.get('enhance'),
                    datacube.config.get('peakmethod')))
            cv2.imwrite(save_path,large_image)
            
    ##################################################
    
    fig.savefig(SpecRead.workpath+'/output/'+Constants.DIRECTORY+
            '/elements_plot_bgtrip={0}_ratio={1}_enhance={2}_peakmethod={3}.png'\
            .format(datacube.config.get('bgstrip'),datacube.config.get('ratio')\
            ,datacube.config.get('enhance'),datacube.config.get('peakmethod'))) 
    
    if any("temp" in x for x in datacube.datatypes): pass
    else: datacube.save_cube() 
    logger.warning("cube has been saved and {} packed!".format(element_list))
    IMAGE_PATH = str(SpecRead.workpath+'\output\\'+Constants.DIRECTORY+'\\')
    logger.info("\nImage(s) saved in {0}\nResized dimension: {1} pixels".format(
        IMAGE_PATH,(newY,newX)))
    fig.clf()
    return

def write_image(image,resize,path,enhance=False,merge=False,save=True):
    """ Writes a 2D-array image to disk. Similar to split_and_save function.
    
    ------------------------------------------------------------------------

    INPUT:
        image; 2D-array
        size; desired output target (int)
        path; string
        enhance (optional); bool (default: false) """

    imagsize = image.shape
    imagex = image.shape[0]
    imagey = image.shape[1]
    if resize == 0:
        factor = 1
    elif resize > 0:
        factor = resize/max(imagsize)
    else: raise ValueError("Can't have negative resize shape")
    newX,newY = int(factor*imagex),int(factor*imagey)
    
    if imagex > resize or imagey > resize: 
        large_image = image/image.max()*255
    else: 
        if image.max() > 0: 
            large_image = image/image.max()*255
        else:
            large_image = image
        if enhance == False:
            large_image = cv2.resize(
                large_image,(newY,newX),interpolation=cv2.INTER_NEAREST)
        if enhance == True:
            large_image = cv2.resize(
                large_image,(newY,newX),interpolation=cv2.INTER_CUBIC)
    if save:
        if merge== False: plt.imsave(path,large_image,cmap=Constants.COLORMAP)
        elif merge== True: cv2.imwrite(path,large_image)
    return large_image

def stackimages(*args):
    """ Stack a series of images together with different colors.
    
    ------------------------------------------------------------

    INPUT: At least 2 2D-arrays
    OUTPUT: 2D-array """
    
    if len(args) < 2: 
        raise ValueError("At least 2 images must be given, got {}".format(len(args)))
    elif len(args) > 3:
        raise ValueError("No more than 3 images can be parsed, got {}".format(len(args)))

    imagex, imagey = args[0].shape[0], args[0].shape[1]
    imagelist = args
    imagea = args[0]
    imageb = args[1]
    imagea = np.asarray(imagea,dtype="int32")
    imageb = np.asarray(imageb,dtype="int32")
    stackedimage = np.zeros([imagex,imagey,3],dtype="int32")
     
    cy_funcs.cy_stack(stackedimage,imagea,imageb,np.asarray([imagex,imagey],dtype="int32"))

    return stackedimage

def binary_thresh(image,thresh):
    """ Thresholds image into a binary image.
    
    -----------------------------------------

    INPUT:
        image; 2D-array
        thresh; int
    OUTPUT:
        image; 2D-array
        counts; int """

    counts = 0
    for x in range(len(image)):
        for y in range(len(image[x])):
            if image[x][y] >= thresh: 
                image[x][y] = 1
                counts += 1
            else: image[x][y] = 0
        return image, counts

def subtract(image1, image2,norm=True):
    """ Subtracts image2 from image1 """

    output = np.zeros([image1.shape[0],image1.shape[1]],dtype="float32")
    if norm == True:
        hi1 = image1.max()
        hi2 = image2.max()
        lo1 = image1.min()
        lo2 = image2.min()
        if hi1 > hi2:
            image2 = (image2/hi2)*hi1
        elif hi2 > hi1:
            image1 = (image1/hi1)*hi2
        else:
            pass
    shape = [image1.shape[0], image1.shape[1]]
    shape = np.asarray(shape,dtype="int32")
            
    cy_funcs.cy_subtract(image1,image2,shape,output)
    return output
 
def add(image1, image2,norm=True):
    """ Subtracts image2 from image1 """

    output = np.zeros([image1.shape[0],image1.shape[1]],dtype="float32")
    if norm == True:
        hi1 = image1.max()
        hi2 = image2.max()
        lo1 = image1.min()
        lo2 = image2.min()
        if hi1 > hi2:
            image2 = (image2/hi2)*hi1
        elif hi2 > hi1:
            image1 = (image1/hi1)*hi2
        else:
            pass
    shape = [image1.shape[0], image1.shape[1]]
    shape = np.asarray(shape,dtype="int32")
            
    cy_funcs.cy_add(image1,image2,shape,output)
    return output

def large_pixel_smoother(image,iterations):
    """ test """
    
    for i in range(iterations):
        for x in range(0,image.shape[0],1):
            for y in range(0,image.shape[1],1):
                try:
                    if image[x,y] != image[x,y+1]:
                        image[x,y] = (image[x,y]+image[x,y+1])/2
                        image[x,y+1] = image[x,y]
                        y+=y
                    else: pass
                except: pass
            try:
                if image[x,y] != image[x+1,y]:
                    image[x,y] = (image[x,y]+image[x+1,y])/2
                    image[x+1,y] = image[x,y]
                    x+=x
                else: pass
            except: pass
    return image

