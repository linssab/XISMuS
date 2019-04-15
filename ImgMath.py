#################################################################
#                                                               #
#          IMAGE MATH	                                        #
#                        version: a1.2                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import numpy as np
import SpecRead
import SpecMath
import Compounds
import math
import logging
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

configdict = SpecRead.getconfig()

def normalize_fnc(energyaxis):
    MaxDetectedArea = 0
    spec = SpecRead.getfirstfile()
    RAW_data = SpecRead.getdata(spec)
    
    imagesize = SpecRead.getdimension()
    imagex = imagesize[0]
    imagey = imagesize[1]
    imagedimension = imagex*imagey
    
    stackeddata = SpecMath.stacksum(spec,imagedimension)
    stackedlist = stackeddata.tolist()
    absenergy = energyaxis[stackedlist.index(stackeddata.max())] * 1000
    print("ABSENERGY: {0}".format(absenergy))
    
    bg = SpecMath.peakstrip(stackeddata,24,3)

# NO FITTING IS USED TO CALCULATE MAX AREA!        

    sum = SpecMath.getpeakarea(absenergy,stackeddata,energyaxis,bg,\
            configdict.get('bgstrip'),RAW_data)
    return sum

def getheightmap(depth_matrix,thickratio,compound,KaKb='Pb'):
    imagesize = SpecRead.getdimension()
    imagex = imagesize[0]
    imagey = imagesize[1]
    heightmap = np.zeros([imagex,imagey])
    
    coefficients = Compounds.coefficients(compound,KaKb)
    
    if compound == 'OceanBlue':
        coefficients = Compounds.mixture([6,4],KaKb,'Air','OceanBlue')
    if compound == 'CoBlue':
        coefficients = Compounds.mixture([6,4],KaKb,'Air','CoBlue')

    mu1 = coefficients[0]
    mu2 = coefficients[1]
    logging.warning("mu1 = {0} / mu2 = {1}".format(mu1,mu2))
    for i in range(len(depth_matrix)):
        for j in range(len(depth_matrix[i])):
            if depth_matrix[i][j] != 0:
                d = -1 * ((math.sin(90)*math.log((depth_matrix[i][j]+0.00001)\
                        /thickratio))/(mu1-mu2))
            else: d = 0
            if d < 0: heightmap[i][j] = 0
            elif depth_matrix[i][j] <= thickratio*1.10 and \
                    depth_matrix[i][j] >= thickratio*0.90:
                heightmap[i][j] = 0
            else: heightmap[i][j] = 10000 * d
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
    imagex = imagesize[0]
    imagey = imagesize[1]
    imagedimension = imagex*imagey
    R = np.zeros([imagex,imagey])
    G = np.zeros([imagex,imagey])
    B = np.zeros([imagex,imagey])
    A = np.zeros([imagex,imagey])
    elmap = elementmap
    pixel = []
    myimage = [[]]*(imagex-1)
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
        R=R+elmap
        G=G+elmap
        B=B+0
        A=A+255
    elif color == 'gray':
        R=R+elmap
        G=G+elmap
        B=B+elmap
        A=A+255
    for line in range(imagex-1):    
        for i in range(imagey-1):
            pixel.append(np.array([R[line][i],G[line][i],B[line][i],A[line][i]],dtype='float32'))
            myimage[line]=np.asarray(pixel,dtype='uint8')
        pixel = []
    image = np.asarray(myimage)
    return image

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

