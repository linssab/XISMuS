#################################################################
#                                                               #
#          IMAGE MATH	                                        #
#                        version: a1.0                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import numpy as np
import SpecRead
import SpecMath

def normalize_fnc(energyaxis):
    MaxDetectedArea = 0
    currentspectra = SpecRead.getfirstfile()
    imagesize = SpecRead.getdimension()
    imagex = imagesize[0]
    imagey = imagesize[1]
    imagedimension = imagex*imagey
    stackeddata = SpecMath.stacksum(currentspectra,imagedimension)
    stackedlist = stackeddata.tolist()
    absenergy = energyaxis[stackedlist.index(stackeddata.max())] * 1000
    print("ABSENERGY: {0}".format(absenergy))
    for iteration in range(imagedimension):
        spec = currentspectra
        specdata = SpecRead.getdata(spec)
        sum = SpecMath.getpeakarea(absenergy,specdata,energyaxis,0)
        if sum > MaxDetectedArea: MaxDetectedArea = sum
        currentspectra = SpecRead.updatespectra(spec,imagedimension)
    return MaxDetectedArea
        
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

