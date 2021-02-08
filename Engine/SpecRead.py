#################################################################
#                                                               #
#          SPEC READER                                          #
#                        version: 2.0.0 - Feb - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

###########
# imports #
###########
import logging
import Constants
from ReadConfig import unpack_cfg as CONFIGURE
from ReadConfig import pop_error, __PERSONAL__, __BIN__ 
# User space is picked from ReadConfig, then passed to global variables here
import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
###########

global __PERSONAL__, __BIN__
__PERSONAL__ = __PERSONAL__
__BIN__ = __BIN__

def get_samples_folder(inifile):
    """ Returns the last set samples folder input by the user in the GUI """

    ini = open(inifile,"r")
    folder = ini.readline()
    ini.close() 
    return folder

Constants.SAMPLES_FOLDER = get_samples_folder(os.path.join(__BIN__,"folder.ini"))

def getfirstfile():
    """ This function is called to get the last updated value of
    Constants.FIRSTFILE_ABSPATH """
    
    return Constants.FIRSTFILE_ABSPATH

def setup(prefix, indexing, extension):
    """ Reads config.cfg file and sets up the configuration according to what is
    contained there """

    global workpath, cube_path, output_path

    Constants.CONFIG,Constants.CALIB = CONFIGURE()
    Constants.DIRECTORY = Constants.CONFIG.get("directory")
    
    # build paths
    workpath = __PERSONAL__
    cube_path = os.path.join(workpath,"output",
            Constants.DIRECTORY,"{}.cube".format(Constants.DIRECTORY))
    output_path = os.path.join(workpath,"output",Constants.DIRECTORY)
    Constants.DIMENSION_FILE = os.path.join(Constants.SAMPLE_PATH,"colonneXrighe.txt")

    Constants.NAME_STRUCT = [prefix,indexing,extension]
    
    return np.nan

def setup_from_datacube(datacube,sample_database):
    """ Read Cube class object configuration and sets up the application
    configuration parameters accordingly """

    global workpath, cube_path, output_path
    
    Constants.CONFIG,Constants.CALIB = datacube.config, datacube.calibration
    Constants.DIRECTORY = Constants.CONFIG.get("directory")
    
    # build sample paths
    Constants.SAMPLE_PATH = datacube.path
    workpath = __PERSONAL__
    cube_path = os.path.join(workpath,"output",
            Constants.DIRECTORY,"{}.cube".format(Constants.DIRECTORY))
    output_path = os.path.join(workpath,"output",Constants.DIRECTORY)
    Constants.DIMENSION_FILE = os.path.join(datacube.path, "colonneXrighe.txt")
    Constants.FIRSTFILE_ABSPATH = sample_database[Constants.DIRECTORY]
    
    return np.nan 

def conditional_setup(name="None",path="auto"):
    """ Reads Config.cfg file configuration parameters and changes Constants.DIRECTORY
    parameter to input value. """
    
    global workpath, cube_path, output_path
    
    Constants.CONFIG,Constants.CALIB = CONFIGURE()
    Constants.CONFIG['directory'] = name
    
    # build paths
    Constants.DIRECTORY = Constants.CONFIG.get("directory")
    if path=="auto":
        Constants.SAMPLE_PATH = os.path.join(Constants.SAMPLES_FOLDER,Constants.DIRECTORY)
    else: Constants.SAMPLE_PATH = path
    workpath = __PERSONAL__
    cube_path = os.path.join(workpath,"output",
            Constants.DIRECTORY,"{}.cube".format(Constants.DIRECTORY))
    output_path = os.path.join(workpath,"output",Constants.DIRECTORY)
    Constants.DIMENSION_FILE = os.path.join(Constants.SAMPLE_PATH, "colonneXrighe.txt")
    Constants.FIRSTFILE_ABSPATH = os.path.join(Constants.SAMPLE_PATH, name)

    return np.nan

def load_cube():
    """ Loads cube to memory (unpickle). Cube name is passed according to
    latest SpecRead parameters. See setup conditions inside SpecRead module.
    Returns the datacube object """

    if os.path.exists(SpecRead.cube_path):
        cube_file = open(SpecRead.cube_path,'rb')
        del Constants.MY_DATACUBE
        Constants.MY_DATACUBE = pickle.load(cube_file)
        cube_file.close()
        Constants.MY_DATACUBE.densitymap = Constants.MY_DATACUBE.densitymap.astype("float32")
    else:
        pass
    return Constants.MY_DATACUBE

def RatioMatrixReadFile(ratiofile):
    """ Reads a ratio file created by any mapping module and transforms into
    a 2D-array.

    ------------------------------------------------------------------------

    INPUT:
        ratiofile; path
    OUTPUT:
        RatesMatrix; 2D-array """

    reader = []
    with open (ratiofile,'rt') as in_file:
        for line in in_file:
            reader.append(line.strip("\n"))
        for i in range(len(reader)): 
            reader[i] = reader[i].split()
        for j in range(len(reader)):
            for k in range(len(reader[j])):
                if reader[j][k].isdigit() == True: 
                    reader[j][k]=int(reader[j][k])
                else: reader[j][k]=1
        if len(reader[-1]) == 0: reader[-1]=[1, 1, 1, 1]
    reader = np.asarray(reader)
    iterx=0
    itery=0
    
    for i in range(len(reader)):
        if len(reader[i]) > 1:
            if reader[i][0] > 0\
                    and reader[i][0] > reader[i-1][0]\
                    and reader[i][0] > iterx: iterx=int(reader[i][0])
        if len(reader[i]) > 1:
            if reader[i][1] > 0\
                    and reader[i][1] > reader[i-1][1]\
                    and reader[i][1] > itery: itery=int(reader[i][1])

    RatesMatrix=np.zeros((iterx+1,itery+1))
    for i in range(len(reader)):
        x=int(reader[i][0])
        y=int(reader[i][1])
        ka=int(reader[i][2])
        kb=int(reader[i][3])
        if kb == 0: ka,kb = 0,1
        RatesMatrix[x,y] = ka/kb
    return RatesMatrix

def getheader(mca):
    """ Gets PMCA spectra file (*.mca) header
    
    -----------------------------------------

    INPUT:
        mca; path
    OUTPUT:
        ObjectHeader; string """

    ObjectHeader=[]
    specile = open(mca)
    line = specfile.readline()
    while "<<DATA>>" not in line:
        ObjectHeader.append(line.replace('\n',' '))
        line = specfile.readline()
        if "<<CALIBRATION>>" in line:
            specfile.close()
            break
    return ObjectHeader

def getcalibration():
    """ Extracts the calibration anchors from source 
    if configuration is set to manual, returns the anchors input by
    user via GUI. """

   
    if Constants.CONFIG['calibration'] == 'from_source':
        param = []
        try: mca_file = open(getfirstfile(),'r')
        except:
            try: 
                calib = Constants.MY_DATACUBE.calibration
            except:
                pop_error("Calibration Error",
                    "Could not fetch calibration from source! Retry with manual calibration")
                raise ValueError("Couldn't fetch calibration from source!")
            return

        line = mca_file.readline()
        while line != "":
            while "<<CALIBRATION>>" not in line:
                line = mca_file.readline()
                if line == "": break
            while "<<DATA>>" not in line:
                line = mca_file.readline()
                if line == "": break
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                try: param.append([int(aux[0]),float(aux[1])])
                except: pass 
            line = mca_file.readline()
        mca_file.close()
        if param == []: 
            pop_error("Calibration Error",
                    "Could not fetch calibration from source! Retry with manual calibration")
            raise ValueError("Couldn't fetch calibration from source!")
        for parameter in param:
            if len(param) <= 1: 
                pop_error("Calibration Error","Need at least two calibration points!")
                raise ValueError("Need at least two calibration points!")
            elif parameter[0] < 0 or parameter[1] < 0: 
                pop_error("Calibration Error","Can't receive negative values!")
                raise ValueError("Cant receive negative values!")
            elif parameter[0] == 0 or parameter[1] == 0:
                pop_error("Calibration Error","Can't receive zero as parameter!")
                raise ValueError("Cant receive zero as parameter!")
        else: pass
    else:
        param = Constants.CALIB
    #else: 
    #    raise ValueError("Calibration mode {0} unknown! Check config.cfg")
    return param

def getdata(mca):
    """ Extract the data contained in spectrum files 

    ------------------------------------------------ 
        
    INPUT:
        mca; path
    OUTPUT:
        Data; 1D-array """

    name = str(mca)
    name = name.split("\\")[-1]
    name = name.replace('_',' ')
    
    # custom MC generated files
    if '#XRMC#' in name:
        Data = []
        datafile = open(mca)
        lines = datafile.readlines()
        for line in lines:
            line = line.split()
            try: counts = float(line[1])
            except: counts = float(line[0])
            counts = counts * 10e3
            Data.append(counts)
        Data = np.asarray(Data)

    # this works for mca extension files
    else:
        ObjectData=[]
        with open(mca) as datafile:
            line = datafile.readline()
            line = line.replace("\r","")
            line = line.replace("\n","")

            # AMPTEK files start with this tag
            if "<<PMCA SPECTRUM>>" in line:
                while "<<DATA>>" not in line:
                    line = datafile.readline()
                    if line == "": break
                line = datafile.readline()
                while "<<END>>" not in line:
                    try: ObjectData.append(int(line))
                    except ValueError as exception:
                        datafile.close()
                        raise exception.__class__.__name__
                    line = datafile.readline()
                    if line == "": break

            # Works if file is just counts per line
            elif line.isdigit():
                while line:
                    ObjectData.append(int(line))
                    line = datafile.readline()
                    if line == "": break
            
            # if file has two columns separated by space or tab
            elif "\t" in line or " " in line: 
                while line:
                    counts = line.split("\t")[-1]
                    if counts.isdigit(): ObjectData.append(int(counts))
                    else:
                        counts = line.split(" ")[-1]
                        ObjectData.append(float(counts)*10e3)
                    line = datafile.readline()
                    if line == "": break
            del datafile
        Data = np.asarray(ObjectData)
    return Data

def calibrate(lead=0, tail=0, specsize=None):
    """ Returns the energy axis and gain of the calibrated axis
    The parameters are taken from config.cfg if calibration is set to manual
    or from the mca files if calibration is set to from_source """
    from .SpecMath import linregress

    param = getcalibration()
    x=[]
    y=[]
    for i in range(len(param)):
        for k in range(len(param[i])):
            x.append(param[i][0])
            y.append(param[i][1])
    x=np.asarray([x])-lead
    y=np.asarray([y])
    coefficients=list(linregress(x,y))
    GAIN=coefficients[0]
    B=coefficients[1]
    R=coefficients[2]
    try: n = len(getdata(getfirstfile()))-lead-tail
    except:
        try:
            n = Constants.MY_DATACUBE.matrix.shape[2]
        except:
            n = specsize
    curve = []
    for i in range(n):
        curve.append((GAIN*i)+B)
    curve = np.asarray(curve)
    return curve,GAIN,B

def getgain():
    """ Calculates the energy axis and returns only the gain """

    calibration = calibrate()
    curve = calibration[0]
    n = len(curve)
    GAIN=0
    for i in range(n-1):
        GAIN+=curve[i+1]-curve[i]
    return GAIN/n
   
def updatespectra(specfile,size,from_list=False):
    """ Returns the next spectrum file to be read

    ---------------------------------------------

    INPUT:
        specfile; string
        size; int
    OUTPUT:
        newfile; string """        
    
    try:
        index = Constants.FILE_POOL.index(specfile)
        return Constants.FILE_POOL[index+1]
    
    except (IndexError, ValueError): 

        name=str(specfile)
        specfile_name = name.split("\\")[-1]
        name = specfile_name.split(".")[0]
        extension = specfile_name.split(".")[-1]
        for i in range(len(name)):
            if not name[-i-1].isdigit(): 
                prefix = name[:-i]
                index = name[-i:]
                break
        
        if int(index) < size: index = str(int(index)+1)
        else: index = str(size)
        newfile = os.path.join(Constants.SAMPLES_FOLDER,
                Constants.CONFIG["directory"],
                str(prefix+index+"."+extension))
        
    return newfile

def getdimension():
    """ Gets the sample image dimension
    from colonneXrighe file

    -----------------------------------

    OUTPUT:
        x; int
        y; int
        user_input; bool """

    dimension_file = Constants.DIMENSION_FILE

    if not os.path.exists(dimension_file):
        dimension_file = os.path.join(Constants.SAMPLES_FOLDER,"colonneXrighe.txt")
        if not os.path.exists(dimension_file):
            dimension_file = os.path.join(output_path,"colonneXrighe.txt")
            if not os.path.exists(dimension_file):
                dimension_file = os.path.join(__PERSONAL__,
                        "Example Data",Constants.DIRECTORY,"colonneXrighe.txt") 
                if not os.path.exists(dimension_file):
                    raise IOError("Dimension file not found!") 
    user_input = False
    dm_file = open(dimension_file, "r")
    line = dm_file.readline()
    if "righe" in line:
        line=line.replace("\r","")
        line=line.replace("\n","")
        line=line.replace("\t"," ")
        aux = line.split()
        x = int(aux[1])
        line = dm_file.readline() 
    if "colonne" in line:
        line=line.replace("\r","")
        line=line.replace("\n","")
        line=line.replace("\t"," ")
        aux = line.split()
        y = int(aux[1])
        line = dm_file.readline() 
    while line != "":
        if line.startswith("*"): user_input = True
        line = dm_file.readline()
    dm_file.close()
    return x,y,user_input

def dump_ratios(maps_list,element_list):
    """ Writes all ratio files to disk 

    ----------------------------------

    INPUT:
        maps_list; nD-array (element(string), line([0] or [0,1]), 2D-array)
        element_list; 1D string array """

    # this is to work with multiprocessing Mapping mode
    
    ratiofiles = ["" for x in range(len(element_list))]
    for Element in range(len(element_list)): 
        ratiofiles[Element] = str(os.path.join(
            output_path,"{1}_ratio_{0}.txt".format(
                element_list[Element],Constants.DIRECTORY)))
        r_file = open(ratiofiles[Element],'w+')
        r_file.readline()
        r_file.truncate()
        r_file.write("-"*10 + " Counts of Element {0} ".format(
            element_list[Element]) + 10*"-" + '\n')
        r_file.write("row\tcolumn\tline1\tline2\tratio\n")
        r_file.close() 

    for Element in range(len(element_list)):
        r_file = open(ratiofiles[Element],"a")
        for x in range(maps_list[Element][0][0].shape[0]):
            for y in range(maps_list[Element][0][0].shape[1]):
                a = int(maps_list[Element][0][0][x][y])
                b = int(maps_list[Element][0][1][x][y])
                if b > 0: 
                    r_file.write("{}\t{}\t{}\t{}\t{}\n".format(x,y,a,b,a/b))
                else: 
                    r_file.write("{}\t{}\t{}\t{}\t{}\n".format(x,y,a,b,0))
        r_file.close()
    return 0

