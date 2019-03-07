#################################################################
#                                                               #
#          SPEC READER                                          #
#                        version: a1.4                          #
# @author: Sergio Lins                                          #
#################################################################

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from PyMca5.PyMcaMath import SimpleMath
from PyMca5.PyMcaMath.fitting import RateLaw

dirname = "C:/misure/"
if not os.path.exists(dirname):
    dirname = os.getcwd()
    print("Workpath is: %s" % dirname)
    if not os.path.exists(dirname):
        raise IOError("File or directory does no exist!")

"""
TEST FILE
"""
input=dirname+'Cesareo_1.mca'

# MCA MEANS THE INPUT MUST ME AN MCA FILE
# SELF MEANS THE INPUT CAN BE EITHER A DATA ARRAY OR AN MCA FILE
# THE FLAG MUST SAY IF ITS AN MCA 'file' OR A DATA ARRAY 'data'

def getheader(self):
    ObjectHeader=[]
    file = open(self)
    line = file.readline()
    while "<<DATA>>" not in line:
        ObjectHeader.append(line.replace('\n',' '))
        line = file.readline()
        if "<<CALIBRATION>>" in line:
            file.close()
            break
    return ObjectHeader

def getcalibration(self,flag):
    checker=0
    CalParam=[]
    if flag == 'file':
        file = open(self)
        line = file.readline()
        for line in file:
            if "<<CALIBRATION>>" in line and flag == 'file':
                print("Using calibration data from specfile.")
                checker=1
        file.close()
        if checker == 1:
            file = open(self)
            line = file.readline()
            while "<<CALIBRATION>>" not in line:
                line = file.readline()
            line = file.readline()
            line = file.readline()
            while "<<DATA>>" not in line:
                aux = line.split(" ")
                CalParam.append([int(aux[0]),float(aux[1])])
                line = file.readline()
            file.close()
    elif os.path.exists(dirname+'config.cfg') and checker==0 or flag == 'data'\
            and os.path.exists(dirname+'config.cfg'):
            configfile=dirname+'config.cfg'
            file = open(configfile)
            for line in file:
                if "<<CALIBRATION>>" in line:
                    print("Using calibration data from config.cfg!")
                    checker=1
            file.close()
            if checker == 1:
                file = open(configfile)
                line = file.readline()
                while "<<CALIBRATION>>" not in line:
                    line = file.readline()
                line = file.readline()
                while "<<END>>" not in line:
                    aux = line.split(" ")
                    CalParam.append([int(aux[0]),float(aux[1])])
                    line = file.readline()
                file.close()
            else: raise IOError("No calibration values on config.cfg!")
    else: raise IOError("No calibration data available! Or 'config.cfg' does not exist!")
    return CalParam

def getdata(mca):
    ObjectData=[]
    file = open(mca)
    line = file.readline()
    while "<<DATA>>" not in line:
        line = file.readline()
    line = file.readline()
    while "<<END>>" not in line:
        ObjectData.append(int(line))
        line = file.readline()
    file.close()
    return ObjectData

def getchannels(mca):
    return len(getdata(mca))

def calibrate(self,flag):
    param=getcalibration(self,flag)
    x=[]
    y=[]
    for i in range(len(param)):
        for k in range(len(param[i])):
            x.append(param[i][0])
            y.append(param[i][1])
    x=np.asarray([x])
    y=np.asarray([y])
    coefficients=list(RateLaw.linregress(x,y))
    GAIN=coefficients[0]
    B=coefficients[1]
    R=coefficients[2]
    print("Correlation coefficient R = %f" % R)
    if flag == 'data':
        n = len(self)
    elif flag == 'file':
        n = len(getdata(self))
    n = getchannels(self)
    curve = np.zeros([n])
    curve=[]
    for i in range(n):
        curve.append((GAIN*i)+B)
    return curve

def getgain(self,flag):
    curve=calibrate(self,flag)
    n=len(curve)
    GAIN=0
    for i in range(n-1):
        GAIN+=curve[i+1]-curve[i]
    return GAIN/n

def getsum(mca):
    DATA = getdata(mca)
    SUM = 0
    for i in range(len(DATA)):
        SUM+=DATA[i]
    return SUM

def getplot(mca):
    energy=calibrate(mca,'file')
    data=getdata(mca)
    plt.plot(energy,data)
    plt.show()
    return 0

def updatespectra(file,size):
    name=str(file)
    name=name.replace('_',' ')
    name=name.replace('.',' ')
    name=name.split()
    for i in range(len(name)):
        if name[i].isdigit()==True: index=int(name[i])
        if name[i] == "mca": extension=name[i]
        if len(name[i]) > 3: prefix = name[i]
    if index < size: index=str(index+1)
    else: index = str(size)
    newfile=str(prefix+'_'+index+'.'+extension)
    return newfile

def getdimension():
    loadconfig = os.path.join(dirname,"config.cfg")
    if not os.path.exists(loadconfig):
        raise IOError("Config file not found!") 
    else: config_file = dirname+'config.cfg'

    file = open(config_file, 'r')
    line = file.readline()
    if "<<SIZE>>" in line:
        while "<<END>>" not in line:
            if 'lines' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                x = int(aux[1])
            if 'rows' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                y = int(aux[1])
            line = file.readline()
        print("From SpecRead.getdimension():\nImage size is: ")
        print("%d Line(s) and %d Row(s)" % (x,y))
    return x,y

if __name__=="__main__":
    #specfile=sys.argv[0]
    specfile=input
