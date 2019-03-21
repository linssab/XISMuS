import random
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.image import imread
import cv2


def randomimg(a,b): #arguments are the x and y dimensions of the desired random image
    height=b;
    width=a;
    N=height*width
    test_vector=np.zeros((height,width));
    for x in range(height):
        for y in range(width):
            test_vector[x,y]=int((random.random()*255))
    print(test_vector)

    plt.imshow(test_vector,cmap='gray')
    plt.show()
    mpimg.imsave('test_map.tif',test_vector, format='tiff', cmap='gray')
    return test_vector
    
def generatemap(a): #argument must be an array
    element_array=a;
    dimension=element_array.shape
    height=dimension[0];
    width=dimension[1];
    N=height*width
    print(element_array)
    
    filter_med=([[0,1,0],
                 [1,0,1],
                 [0,1,0]])
    
    for x in range(0,height-1,1):
        for y in range(0,width-1,1):
            element_array[x,y] = ((element_array[x-1,y-1]+element_array[x,y-1]+element_array[x+1,y-1]+\
                                   element_array[x-1,y]+element_array[x,y]+element_array[x+1,y]+\
                                   element_array[x-1,y+1]+element_array[x,y+1]+element_array[x+1,y+1])/9)

                
    print(element_array)
    plt.imshow(element_array,cmap='gray')
    plt.show()
    mpimg.imsave('element_map.tif',element_array, format='tiff', cmap='gray')

    
iron=np.array([[255,255,255,255,255,255],
               [25,25,255,255,25,25],
               [55,55,255,255,55,55],
               [100,100,25,25,100,100],
               [155,155,25,25,155,155],
               [25,25,25,25,25,25]])
plt.imshow(iron,cmap='gray')
plt.show()
#image = imread('element_map.tif')
#image.setflags(write=1)
#plt.imshow(image,cmap='gray')
generatemap(iron)

