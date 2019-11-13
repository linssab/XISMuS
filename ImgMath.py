#################################################################
#                                                               #
#          IMAGE MATH	                                        #
#                        version: 0.0.2α                        #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import logging,os
logging.info("Importing module ImgMath.py...")
import numpy as np
import SpecRead
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
logging.debug("Importing module matplotlib.colors...")
from matplotlib.colors import ListedColormap
logging.debug("Importing module mpl_toolkits.axes_grid1...")
#from mpl_toolkits.axes_grid1 import make_axes_locatable
try: from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
except: logging.warning("Failed to load make_axes_locatable from mpl_toolkits.axes_grid1.axes_divider")
import cv2
import math
logging.info("Finished ImgMath imports.")

LEVELS = 255

def colorbar(mappable):
    
    ##############################################
    # FROM:                                      #
    # https://joseph-long.com/writing/colorbars/ #
    ##############################################
    
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    return fig.colorbar(mappable, cax=cax)

def median_filter(a_2D_array,x,y):
    try: average = (2*a_2D_array[x,y] + a_2D_array[x-1,y] + a_2D_array[x+1,y] +\
            a_2D_array[x,y-1] + a_2D_array[x-1,y-1] + a_2D_array[x+1,y-1] +\
            a_2D_array[x,y+1] + a_2D_array[x-1,y+1] + a_2D_array[x+1,y+1])/10
    except: 
        # ignore upper row
        try: average = (2*a_2D_array[x,y] + a_2D_array[x-1,y] + a_2D_array[x+1,y] +\
                a_2D_array[x,y-1] + a_2D_array[x-1,y-1] + a_2D_array[x+1,y-1])/7
        except:
            # ignore lower row
            try: average = (2*a_2D_array[x,y] + a_2D_array[x-1,y] + a_2D_array[x+1,y] +\
                    a_2D_array[x,y+1] + a_2D_array[x-1,y+1] + a_2D_array[x+1,y+1])/7
        
            except:
                # ignore left column
                try: average = (2*a_2D_array[x,y] + a_2D_array[x+1,y] +\
                        a_2D_array[x,y-1] + a_2D_array[x+1,y-1] +\
                        a_2D_array[x,y+1] + a_2D_array[x+1,y+1])/7
                except:
                    # ignore right column
                    try: average = (2*a_2D_array[x,y] + a_2D_array[x-1,y] +\
                            a_2D_array[x,y-1] + a_2D_array[x-1,y-1] +\
                            a_2D_array[x,y+1] + a_2D_array[x-1,y+1])/7
                    except:
                        try: average = (2*a_2D_array[x,y] + a_2D_array[x+1,y] +\
                                a_2D_array[x,y+1] + a_2D_array[x+1,y+1])/5
                        except:
                            try: average = (2*a_2D_array[x,y] + a_2D_array[x-1,y] +\
                                    a_2D_array[x,y+1] + a_2D_array[x-1,y+1])/5
                            except:
                                try: average = (2*a_2D_array[x,y] + a_2D_array[x+1,y] +\
                                        a_2D_array[x,y-1] + a_2D_array[x+1,y-1])/5
                                except:
                                    try: average = (2*a_2D_array[x,y] + a_2D_array[x-1,y] +\
                                            a_2D_array[x,y-1] + a_2D_array[x-1,y-1])/5
                                    except: logging.warning("Something went wrong with the median filter!")
    return average

def iteractive_median(a_2D_array,iterations=1):
    for i in range(iterations):
        for x in range(a_2D_array.shape[0]):
            for y in range(a_2D_array.shape[1]):
                a_2D_array[x,y] = median_filter(a_2D_array,x,y)
    return a_2D_array 

def threshold(a_2D_array,t):
    for x in range(a_2D_array.shape[0]):
        for y in range(a_2D_array.shape[1]):
            average = median_filter(a_2D_array,x,y)
            if a_2D_array[x,y] < t and average < t: a_2D_array[x,y] = 0
    return a_2D_array 

def low_pass(a_2D_array,t):
    for x in range(a_2D_array.shape[0]):
        for y in range(a_2D_array.shape[1]):
            average = median_filter(a_2D_array,x,y)
            if a_2D_array[x,y] > t: a_2D_array[x,y] = 0
    return a_2D_array 

def mask(a_datacube,a_compound,mask_threshold):
    try: 
        # tries to get identity element from compound
        id_element = a_compound.identity
    except: 
        unpacked = []
        abundance = 0
        for key in a_compound.weight:
            unpacked.append(key)
            if a_compound.weight[key] > abundance: id_element, abundance = key, a_compound.weight[key]
    
    try: 
        # tries to get element map (of line series A) from cube file
        id_element_matrix = a_datacube.unpack_element(id_element,"a")
    except:
        try: 
            id_element_ratio = SpecRead.output_path + '{1}_ratio_{0}.txt'\
                .format(id_element,SpecRead.DIRECTORY)
            id_element_matrix = SpecRead.RatioMatrixReadFile(id_element_ratio)
        except: raise FileNotFoundError("{0} ratio file not found!".format(id_element))
    
    # TO DO:
    # check histogram to understand contrast and define threshold
    id_element_matrix = threshold(id_element_matrix,mask_threshold)

    return id_element_matrix


def getheightmap(depth_matrix,mask,thickratio,compound):
    average = [[],0]
    imagesize = SpecRead.getdimension()
    imagex = imagesize[0]
    imagey = imagesize[1]
    heightmap = np.zeros([imagex,imagey])
    coefficients = compound.lin_att
    
    heightfile = open(SpecRead.output_path + '{0}_heightmap.txt'\
            .format(SpecRead.DIRECTORY),'w+')
    heightfile.write("-"*10 + " Thickness Values (um) of {0} "\
            .format(compound.name) + 10*"-" + '\n')
    heightfile.write("row\tcolumn\tthickness\n")

    mu1 = coefficients[0]
    mu2 = coefficients[1]
    logging.warning("mu1 = {0} / mu2 = {1}".format(mu1,mu2))
    
    ANGLE = 73  # IN DEGREES #
    for i in range(len(depth_matrix)):
        for j in range(len(depth_matrix[i])):
            if depth_matrix[i][j] > 0 and mask[i][j] > 0.001:
                d = (math.sin(math.radians(ANGLE))/(-mu1+mu2))*\
                        (math.log((depth_matrix[i][j]/thickratio)))
            else: d = 0
            
            #############################################
            #  WRITES d TO HEIGHMAP AND CONVERTS TO um  #
            #############################################

            if d <= 0: heightmap[i][j] = 0
            else: heightmap[i][j] = 10000 * d
             
            if d > 0: 
                heightfile.write("%d\t%d\t%f\n" % (i, j, heightmap[i][j]))
                average[0].append(d)
                average[1] = average[1]+1  #counts how many values are
    
    median = sum(average[0])/(average[1])*10000  #calculates the average (mean) value
    deviation = np.std(average[0])*10000         #calculates the standard deviation

    print("Deviation {}".format(deviation))
    print("Average {}".format(median))
    print("max: {0} min: {1}".format(max(average[0])*10000,min(average[0])*10000))
    heightfile.write("Average: {0}um, sampled points: {1}".format(median,average[1]))
    return heightmap,median, deviation

def set_axes_equal(ax):
    
    #####################################################
    #   set_axes_equal(ax) FUNCTION OBTAINED FROM:      #
    #   https://stackoverflow.com/questions/13685386    #
    #####################################################

    '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    '''

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
    #ax.set_zlim3d([z_middle - plot_radius, z_middle + plot_radius])
    ax.set_zlim3d([0, plot_radius])

def plot3D(depth_matrix):
    fig = plt.figure()
    ax = fig.gca(projection = '3d')
    imagesize = SpecRead.getdimension()
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
    set_axes_equal(ax)
    fig.savefig(os.getcwd()+'\\myimage.svg', format='svg', dpi=1200)
    plt.show()
    return 0

def colorize(elementmap,color=None):
    imagesize = SpecRead.getdimension()
    try: imagesize = len(elementmap),len(elementmap[0])
    except: 
        imagesize = len(elementmap),1
        elementmap = np.expand_dims(elementmap, axis = 1)
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
                pixel.append(np.array([R[line][i],G[line][i],B[line][i],A[line][i]],\
                        dtype='float32'))
            else: pixel.append(np.array([0,0,0,A[line][i]],dtype='float32'))
            myimage[line]=np.asarray(pixel,dtype='uint8')
        pixel = []
    image = np.asarray(myimage)
    return image

def createcmap(color):
    z = z = np.zeros(256)
    R = np.linspace(0,1,256)/(256-color[0])
    G = np.linspace(0,1,256)/(256-color[1])
    B = np.linspace(0,1,256)/(256-color[2])

    alpha = np.ones(256)

    colorcode = np.c_[R,G,B,alpha]
    cmap = ListedColormap(colorcode)
    return cmap

def flattenhistogram(image):
    hist,bins = np.histogram(image.flatten(),256,[0,256])
    cdf = hist.cumsum()
    cdf_norm = cdf * hist.max()/cdf.max()
    cdf_mask = np.ma.masked_equal(cdf,0)
    cdf_mask = (cdf_mask - cdf_mask.min())*255/(cdf_mask.max()-cdf_mask.min())
    cdf = np.ma.filled(cdf_mask,0).astype('uint8')
    image = cdf[image]
    return image

def interpolate_zeros(map_array):
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
                            newvalue = median_filter(map_array[:,:,line,Element],x,y)
                            new_map[x,y,line,Element] = newvalue
    except:
    # to work with multiprocess images were the input objects shape is different
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
    fig, ax = plt.subplots()
    plt.imshow(image)
    ax.set_title(name)
    plt.show()

def split_and_save(datacube,map_array,element_list):
    if datacube.config["ratio"] == True:
        lines = np.asarray(["a","b"])
    else: lines = np.asarray(["a"])

    imagsize = datacube.dimension
    imagex = imagsize[0]
    imagey = imagsize[1]
    image = np.zeros([imagex,imagey])

    #color_image = ImgMath.colorize(image,'copper')
    cmap = createcmap([255,215,51])
    
    target_size = 1024
    factor = target_size/max(imagsize)
    newX,newY = int(factor*imagex),int(factor*imagey)

    ####################
    # Normalizes every #
    ####################
    
    fig, axs = plt.subplots(1,len(element_list),sharey=True)
    
    #mapimage = ax.imshow(image,cmap='gray')
    #plt.colorbar(mapimage)
    
    fig_list = []
    for Element in range(len(element_list)):
        for line in range(lines.shape[0]):
            image = map_array[:,:,line,Element]
            raw_image = map_array[:,:,line,Element]
            if image.max() > 0: image = image/image.max()*LEVELS
             
            histogram,bins = np.histogram(image.flatten(),LEVELS,[0,LEVELS])
            datacube.pack_element(raw_image,element_list[Element],lines[line])
            if lines[line] == "a": datacube.pack_hist(histogram,bins,element_list[Element])
            
            #plt.hist(datacube.__dict__[element_list[Element]],bins='auto')
            #plt.show()
            
            if len(element_list) > 1: ax = axs[Element]
            else: ax=axs
            fig_list.append(ax.imshow(image,cmap='gray'))
            colorbar(fig_list[Element])
            if datacube.config['ratio'] == False:
                ax.set_title(element_list[Element]+' alpha line')
            else: ax.set_title(element_list[Element])
            
            if imagex > target_size or imagey > target_size: large_image = image/image.max()*255
            else: 
                if image.max() > 0: 
                    large_image = image/image.max()*255
                else:
                    large_image = image
                large_image = cv2.resize(large_image,(newY,newX),interpolation=cv2.INTER_NEAREST)
            
            cv2.imwrite(SpecRead.workpath+'/output/'+SpecRead.DIRECTORY+
                '/{0}_bgtrip={1}_ratio={2}_enhance={3}_peakmethod={4}.png'\
                .format(element_list[Element]+"_"+lines[line],datacube.config.get('bgstrip'),datacube.config.get('ratio')\
                ,datacube.config.get('enhance'),datacube.config.get('peakmethod')),large_image)
        
            #checker = datacube.unpack_element('Cu')
            #plotlastmap(checker,element_list[Element])

    ##################################################
    
    fig.savefig(SpecRead.workpath+'/output/'+SpecRead.DIRECTORY+
            '/elements_plot_bgtrip={0}_ratio={1}_enhance={2}_peakmethod={3}.png'\
            .format(datacube.config.get('bgstrip'),datacube.config.get('ratio')\
            ,datacube.config.get('enhance'),datacube.config.get('peakmethod'))) 
    
    datacube.save_cube() 
    logging.warning("cube has been saved and {} packed!".format(element_list))
    IMAGE_PATH = str(SpecRead.workpath+'\output\\'+SpecRead.DIRECTORY+'\\')
    logging.info("\nImage(s) saved in {0}\nResized dimension: {1} pixels".format(IMAGE_PATH,(newY,newX)))
    return 0

def stackimages(*args):
    imagelist = args
    colorlist = ['red','green','blue']
    color = 0
    stackedimage = ImgMath.colorize(np.zeros([imagex,imagey]),'none')
    for image in imagelist:
        color += 1
        image = ImgMath.colorize(image,colorlist[color])
        stackedimage = cv2.addWeighted(stackedimage,1,image,1,0)
    return stackedimage

def binary_thresh(image,thresh):
    counts = 0
    for x in range(len(image)):
        for y in range(len(image[x])):
            if image[x][y] >= thresh: 
                image[x][y] = 1
                counts += 1
            else: image[x][y] = 0
        return image, counts

def blacks_(image,thresh):
    print(image)
    img = cv2.imread("{}".format(image), cv2.IMREAD_GRAYSCALE)
    img,counts = binary_thresh(img,thresh)
    print(counts/len(img))
    return img

def large_pixel_smoother(image,iterations):
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

if __name__ == "__main__":
    import os
    image1 = os.getcwd()+"\\mumble.png"
    """ 
    image2 = os.getcwd()+"\\image2.png"
    queue = [image1,image2]
    img = blacks_(image1,125)
    img2 = blacks_(image2,125)
    cv2.imshow("mammamia",img)
    """
    img = cv2.imread("{}".format(image1), cv2.IMREAD_GRAYSCALE)
    img1 = large_pixel_smoother(img,10)
    cv2.imshow("mammamia2",img1)
    cv2.waitKey(0)
