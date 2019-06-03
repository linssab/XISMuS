#################################################################
#                                                               #
#          IMAGE MATH	                                        #
#                        version: a1.3                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
#################################################################

import numpy as np
import SpecRead
import SpecMath
import Compounds
import math
import logging
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import ListedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cv2

configdict = SpecRead.CONFIG

def colorbar(mappable):
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    return fig.colorbar(mappable, cax=cax)

def getheightmap(depth_matrix,mask,thickratio,compound):
    imagesize = SpecRead.getdimension()
    imagex = imagesize[0]
    imagey = imagesize[1]
    heightmap = np.zeros([imagex,imagey])
    coefficients = compound.lin_att
    
    heightfile = open(SpecRead.workpath + '/output/{0}_heightmap.txt'\
            .format(SpecRead.DIRECTORY),'w+')
    heightfile.write("-"*10 + " Thickness Values (um) of {0} "\
            .format(compound.name) + 10*"-" + '\n')
    heightfile.write("row\tcolumn\tthickness\n")

    mu1 = coefficients[0]
    mu2 = coefficients[1]
    logging.warning("mu1 = {0} / mu2 = {1}".format(mu1,mu2))
    
    ANGLE = 90  # IN DEGREES #
    
    for i in range(len(depth_matrix)):
        for j in range(len(depth_matrix[i])):
            if depth_matrix[i][j] > 0 and mask[i][j] > 0:
                d = -1 * math.sin(math.radians(ANGLE)) *\
                        (math.log((depth_matrix[i][j]/thickratio))/(mu1-mu2))
            else: d = 0
            
            #############################################
            #  WRITES d TO HEIGHMAP AND CONVERTS TO um  #
            #############################################

            if d <= 0: heightmap[i][j] = 0
            else: heightmap[i][j] = 10000 * d
            
            if heightmap[i][j] != 0:
                heightfile.write("%d\t%d\t%d\n" % (i, j, heightmap[i][j]))
            else:  
                heightfile.write("%d\t%d\n" % (i, j))
    return heightmap

#####################################################
#   set_axes_equal(ax) FUNCTION OBTAINED FROM:      #
#   https://stackoverflow.com/questions/13685386    #
#####################################################

def set_axes_equal(ax):
    '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    '''

    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

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
            Z.append(depth_matrix[i][j])
    Z = np.asarray(Z)

    depth_matrix = depth_matrix.transpose()
    MAP = ax.plot_surface(X,Y,depth_matrix,\
            cmap='BuGn',linewidth=0,antialiased=True)
#    ax.set_zlim(-1*depth_matrix.max(),depth_matrix.max()*2)
#    ax.set_ylim(-1,imagesize[1]*1.10)
#    ax.set_xlim(-1,imagesize[0]*1.10)
    set_axes_equal(ax)
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

def updateposition(a,b):
    imagesize = SpecRead.getdimension()
    imagex = imagesize[0]
    imagey = imagesize[1]
    imagedimension = imagex*imagey
    currentx = a
    currenty = b 
    if currenty == imagey-1:
        currenty=0
        currentx+=1
    else:
        currenty+=1
    actual=([currentx,currenty])
    return actual

def flattenhistogram(image):
    hist,bins = np.histogram(image.flatten(),256,[0,256])
    cdf = hist.cumsum()
    cdf_norm = cdf * hist.max()/cdf.max()
    cdf_mask = np.ma.masked_equal(cdf,0)
    cdf_mask = (cdf_mask - cdf_mask.min())*255/(cdf_mask.max()-cdf_mask.min())
    cdf = np.ma.filled(cdf_mask,0).astype('uint8')
    image = cdf[image]
    return image

def split_and_save(map_array,element_list,configdict):
    
    imagsize = SpecRead.getdimension()
    imagex = imagsize[0]
    imagey = imagsize[1]
    image = np.zeros([imagex,imagey])

    #color_image = ImgMath.colorize(image,'copper')
    cmap = createcmap([255,215,51])
    
    target_size = 1024
    factor = target_size/max(imagsize)
    newX,newY = int(factor*imagex),int(factor*imagey)

    ###################################################
    # Normalizes every map in respect to each element #
    ###################################################
    
    fig, axs = plt.subplots(1,len(element_list),sharey=True)
    
    #mapimage = ax.imshow(image,cmap='gray')
    #plt.colorbar(mapimage)
    
    fig_list = []
    for Element in range(len(element_list)):
        for i in range(imagex):
            for j in range(imagey):
                image[i][j] = map_array[i][j][Element]
        if image.max() > 0: image = image/image.max()*255

        if len(element_list) > 1: ax = axs[Element]
        else: ax=axs
        fig_list.append(ax.imshow(image,cmap='gray'))
        if configdict.get('alpha_only') == True:
            ax.set_title(element_list[Element]+' alpha line')
        else: ax.set_title(element_list[Element])
        if imagex > target_size or imagey > target_size: large_image = image
        else: large_image = cv2.resize(image,(newY,newX),interpolation=cv2.INTER_NEAREST)
        cv2.imwrite(SpecRead.workpath+'/output/'+SpecRead.DIRECTORY+
            '/{0}_bgtrip={1}_ratio={2}_alpha_only={3}_peakmethod={4}.png'\
            .format(element_list[Element],configdict.get('bgstrip'),configdict.get('ratio')\
            ,configdict.get('alpha_only'),configdict.get('peakmethod')),large_image)

    ##################################################
    
    #plt.colorbar(fig_list[0],ax=axs, orientation = 'horizontal',fraction=.1)
    #map_ = plt.imshow(axs)
    #plt.colorbar(map_, orientation = 'vertical')
    fig.savefig(SpecRead.workpath+'/output/'+SpecRead.DIRECTORY+
            '/elements_plot_bgtrip={0}_ratio={1}_alpha_only={2}_peakmethod={3}.png'\
            .format(configdict.get('bgstrip'),configdict.get('ratio')\
            ,configdict.get('alpha_only'),configdict.get('peakmethod'))) 
    plt.show()
    
    IMAGE_PATH = str(SpecRead.workpath+'\output\\'+SpecRead.DIRECTORY+'\\')
    print("\nImage(s) saved in {0}\nResized dimension: {1} pixels".format(IMAGE_PATH,(newY,newX)))
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

