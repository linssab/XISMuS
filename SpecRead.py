#################################################################
#                                                               #
#          SPEC READER                                          #
#                        version: a2.1                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
#################################################################

import sys
import os
import numpy as np
import logging
import matplotlib.pyplot as plt
from PyMca5.PyMcaMath.fitting import RateLaw

logging.basicConfig(format = '%(asctime)s\t%(levelname)s\t%(message)s',\
        filename = 'logfile.log',level = logging.DEBUG)
with open('logfile.log','w+') as mylog: mylog.truncate(0)
logging.info('*'* 10 + ' LOG START! ' + '*'* 10)

DIRECTORY = 'campioneperu'
dirname = 'C:/'+DIRECTORY+'/'
firstfile = 'Cesareo_1.mca'
workpath = os.getcwd()
configfile = workpath + '\config.cfg'

def getfirstfile():
    return dirname+firstfile

def getconfig():
    modesdict = {}
    file = open(configfile, 'r')
    line = file.readline()
    if "<<CONFIG_START>>" in line:
        line = file.readline()
        while "<<SIZE>>" not in line:
            if 'bgstrip' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                modesdict['bgstrip'] = str(aux[2])
                logging.info("Bgstrip mode? {0}".format(modesdict.get('bgstrip')))
                line = file.readline()
            if 'ratio' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                if aux[2] == 'True': modesdict['ratio'] = True
                elif aux[2] == 'False': modesdict['ratio'] = False
                logging.info("Create ratio matrix? {0}".format(modesdict.get('ratio')))
                line = file.readline()
            if 'enhance' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                if aux[2] == 'True': modesdict['enhance'] = True
                elif aux[2] == 'False': modesdict['enhance'] = False
                logging.info("Enhance image? {0}".format(modesdict.get('enhance')))
                line = file.readline()
            if 'thick_ratio' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                modesdict['thickratio'] = int(aux[2])
                line = file.readline()
            if 'netpeak_method' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                modesdict['peakmethod'] = str(aux[2])
                line = file.readline()
        file.close()
    return modesdict
 
# MCA MEANS THE INPUT MUST BE AN MCA FILE
# SELF MEANS THE INPUT CAN BE EITHER A DATA ARRAY OR AN MCA FILE
# THE FLAG MUST SAY IF THE FILE IS AN MCA 'file' OR A DATA ARRAY 'data'

def RatioMatrixReadFile(ratiofile):
    MatrixArray = []
    with open (ratiofile,'rt') as in_file:
        for line in in_file:
            MatrixArray.append(line.strip("\n"))
        for i in range(len(MatrixArray)): 
            MatrixArray[i] = MatrixArray[i].split()
        for j in range(len(MatrixArray)):
            for k in range(len(MatrixArray[j])):
                if MatrixArray[j][k].isdigit() == True: MatrixArray[j][k]=int(MatrixArray[j][k])
                else: MatrixArray[j][k]=1
        if len(MatrixArray[-1]) == 0: MatrixArray[-1]=[1, 1, 1, 1]
    MatrixArray = np.asarray(MatrixArray)
    iterx=0
    itery=0
    
    for i in range(len(MatrixArray)):
        if len(MatrixArray[i]) > 1:
            if MatrixArray[i][0] > 0\
                    and MatrixArray[i][0] > MatrixArray[i-1][0]\
                    and MatrixArray[i][0] > iterx: iterx=int(MatrixArray[i][0])
        if len(MatrixArray[i]) > 1:
            if MatrixArray[i][1] > 0\
                    and MatrixArray[i][1] > MatrixArray[i-1][1]\
                    and MatrixArray[i][1] > itery: itery=int(MatrixArray[i][1])

    RatesMatrix=np.zeros((iterx+1,itery+1))
    for i in range(len(MatrixArray)):
        x=int(MatrixArray[i][0])
        y=int(MatrixArray[i][1])
        ka=int(MatrixArray[i][2])
        kb=int(MatrixArray[i][3])
        if kb == 0: ka,kb = 0,1
        RatesMatrix[x,y] = ka/kb
        if ka/kb > 15: RatesMatrix[x,y] = 0  # CUTOFF FILTER FOR PEAK ERRORS #
    return RatesMatrix


def getheader(mca):
    ObjectHeader=[]
    file = open(mca)
    line = file.readline()
    while "<<DATA>>" not in line:
        ObjectHeader.append(line.replace('\n',' '))
        line = file.readline()
        if "<<CALIBRATION>>" in line:
            file.close()
            break
    return ObjectHeader

def getcalibration(self,flag=None):
    checker=0
    CalParam=[]
    if flag == None:
        file = open(self)
        line = file.readline()
        for line in file:
            if "<<CALIBRATION>>" in line and flag == None:
                print("Using calibration data from specfile %s!" % self)
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
    elif os.path.exists(configfile) and checker==0 or flag == 'data'\
            and os.path.exists(configfile):
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
    name = str(mca)
    name = name.replace('_',' ')
    name = name.replace('/',' ')
    name = name.split()
    if 'test' in name or 'obj' in name:
        Data = []
        file = open(mca)
        lines = file.readlines()
        for line in lines:
            line = line.split()
            counts = float(line[1])
            counts = counts * 10e3
            Data.append(counts)
        Data = np.asarray(Data)
    else:
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
        Data = np.asarray(ObjectData)
    return Data

# CALIBRATE RETURNS A CALIBRATION CURVE USING CALIBRATION INFORMATION
# FROM EITHER THE MCA FILE OR FROM 'config.cfg'. PRIORITY IS GIVEN TO 
# THE MCA FILE CALIBRATION DATA. IT CAN BE OVERRUN USING THE 'data' 
# FLAG OPTION

def calibrate(self,flag=None):
    if flag == 'data':
        param = getcalibration(self,'data')
    else:
        param = getcalibration(self,flag=None)
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
    logging.info("Correlation coefficient R = %f!" % R)
    if flag == 'data':
        n = len(self)
    elif flag == 'file':
        n = len(getdata(self))
    curve = []
    for i in range(n):
        curve.append((GAIN*i)+B)
    curve = np.asarray(curve)
    return curve,GAIN

def getgain(self,flag):
    calibration = calibrate(self,flag)
    curve = calibration[0]
    n = len(curve)
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
    calibration = calibrate(mca,'file')
    energy = calibration[1]
    data=getdata(mca)
    plt.plot(energy,data)
    plt.show()
    return 0
   
def updatespectra(file,size):
    name=str(file)
    name=name.replace('_',' ')
    name=name.replace('-',' ')
    name=name.replace('.',' ')
    name=name.split()
    for i in range(len(name)):
        if name[i].isdigit()==True: index=int(name[i])
        if name[i] == "mca": extension=name[i]
        elif name[i] == "txt": extension=name[i]
        if len(name[i]) > 6: prefix = name[i]
    if index < size: index = str(index+1)
    else: index = str(size)
    newfile = str(prefix+'_'+index+'.'+extension)
    return newfile

def getdimension():
    if not os.path.exists(configfile):
        raise IOError("Config file not found!") 

    file = open(configfile, 'r')
    line = file.readline()
    if "<<CONFIG_START>>" in line:
        while "<<CALIBRATION>>" not in line:
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
#        print("Read.getdimension:\nImage size is: %d Line(s) and %d Row(s)" % (x,y))
    else: line = file.readline()
    return x,y

