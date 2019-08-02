#################################################################
#                                                               #
#          SPEC READER                                          #
#                        version: a2.3                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
#################################################################

from ReadConfig import CONFIG
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

DIRECTORY = CONFIG.get('directory')
dirname = 'C:\samples\\'+DIRECTORY+'\\'
firstfile = CONFIG.get('firstfile')
workpath = os.getcwd()

# cube_path will be changed to the SAMPLE folder in upcoming versions
cube_path = workpath+'\output\\'+DIRECTORY+'\\'+DIRECTORY+'.cube'
output_path = workpath+'\output\\'+DIRECTORY+'\\'
dimension_file = dirname + '\colonneXrighe.txt'

try: os.mkdir(output_path)
except: pass

def getfirstfile():
    return dirname+firstfile

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

def getcalibration():
    from ReadConfig import CALIB 
    return CALIB 

def getdata(mca):
    name = str(mca)
    name = name.replace('_',' ')
    name = name.replace('\\',' ')
    name = name.split()
    if 'test' in name or 'obj' in name or 'newtest' in name:
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

def calibrate():
    param = getcalibration()
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
    n = len(getdata(getfirstfile()))
    curve = []
    for i in range(n):
        curve.append((GAIN*i)+B)
    curve = np.asarray(curve)
    return curve,GAIN

def getgain():
    calibration = calibrate()
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
    if not os.path.exists(dimension_file):
        raise IOError("Dimension file not found!") 

    file = open(dimension_file, 'r')
    line = file.readline()
    if 'righe' in line:
        line=line.replace('\r','')
        line=line.replace('\n','')
        line=line.replace('\t',' ')
        aux = line.split()
        x = int(aux[1])
        line = file.readline() 
    if 'colonne' in line:
        line=line.replace('\r','')
        line=line.replace('\n','')
        line=line.replace('\t',' ')
        aux = line.split()
        y = int(aux[1])
    line = file.readline()
#    print("Read.getdimension:\nImage size is: %d Line(s) and %d Row(s)" % (x,y))
    return x,y

