#################################################################
#                                                               #
#          SPEC READER                                          #
#                        version: 1.0.0                         #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import logging
logger = logging.getLogger("logfile")
from ReadConfig import unpack_cfg as CONFIGURE
from ReadConfig import pop_error, __PERSONAL__, __BIN__ 
logger.debug("Importing module SpecRead.py...")
import sys
import os
import time
import numpy as np
import matplotlib.pyplot as plt
logger.debug("Finished SpecRead imports.")

global __PERSONAL__, __BIN__
__PERSONAL__ = __PERSONAL__
__BIN__ = __BIN__

def get_samples_folder(inifile):

    """ Returns the last set samples folder input by the user in the GUI """

    ini = open(inifile,"r")
    folder = ini.readline()
    ini.close() 
    return folder

samples_folder = get_samples_folder(os.path.join(__BIN__,"folder.ini"))
logger.info("Samples path: {0}".format(samples_folder))
FIRSTFILE_ABSPATH = None

def getfirstfile():
    
    """ Returns global variable.
    This function is called to get the last updated value of
    FIRSTFILE_ABSPATH, without importing the whole module """
    
    return FIRSTFILE_ABSPATH

def setup(prefix, indexing, extension):
    
    """ Reads config.cfg file and sets up the configuration according to what is
    contained there """

    logger.debug("Running setup from Config.cfg") 
    global CONFIG, CALIB, DIRECTORY, samples_folder, selected_sample_folder, workpath, cube_path, output_path, dimension_file, FIRSTFILE_ABSPATH, global_list, file_pool

    CONFIG,CALIB = CONFIGURE()
    DIRECTORY = CONFIG.get("directory")
    
    # build paths
    selected_sample_folder = os.path.join(samples_folder,DIRECTORY)
    workpath = __PERSONAL__
    cube_path = os.path.join(workpath,"output",DIRECTORY,"{}.cube".format(DIRECTORY))
    output_path = os.path.join(workpath,"output",DIRECTORY)
    dimension_file = os.path.join(selected_sample_folder,"colonneXrighe.txt")
    
    # builds path to first spectrum file
    ### being deprecated, for the direct setup, FIRSTFILE_ABSPATH is built on GUI
    #FIRSTFILE_ABSPATH = os.path.join(selected_sample_folder,prefix+indexing+"."+extension)
    file_pool = []
    global_list =  [CONFIG, CALIB, DIRECTORY, 
            samples_folder, selected_sample_folder, workpath, 
            cube_path, output_path, dimension_file, 
            FIRSTFILE_ABSPATH]
    return np.nan

def setup_from_datacube(datacube,sample_database):
    
    """ Read Cube class object configuration and sets up the application
    configuration parameters accordingly """

    logger.debug("Running setup from datacube {}".format(datacube.name)) 
    global CONFIG, CALIB, DIRECTORY, samples_folder, selected_sample_folder, workpath, cube_path, output_path, dimension_file, FIRSTFILE_ABSPATH, global_list
    
    CONFIG,CALIB = datacube.config, datacube.calibration
    DIRECTORY = CONFIG.get("directory")
    
    # build sample paths
    selected_sample_folder = os.path.join(samples_folder,DIRECTORY)
    workpath = __PERSONAL__
    cube_path = os.path.join(workpath,"output",DIRECTORY,"{}.cube".format(DIRECTORY))
    output_path = os.path.join(workpath,"output",DIRECTORY)
    dimension_file = os.path.join(selected_sample_folder, "colonneXrighe.txt")
    
    try: FIRSTFILE_ABSPATH = sample_database[DIRECTORY]
    except: FIRSTFILE_ABSPATH = selected_sample_folder+'void.mca'
    
    global_list =  [CONFIG, CALIB, DIRECTORY,
            samples_folder, selected_sample_folder, workpath,
            cube_path, output_path, dimension_file,
            FIRSTFILE_ABSPATH]

    return np.nan 

def conditional_setup(name='None'):

    """ Reads Config.cfg file configuration parameters and changes DIRECTORY
    parameter to input value. """
    
    logger.debug("Running conditional setup for {}".format(name)) 
    global CONFIG, CALIB, DIRECTORY, samples_folder, selected_sample_folder, workpath, cube_path, output_path, dimension_file, FIRSTFILE_ABSPATH, global_list
    
    CONFIG,CALIB = CONFIGURE()
    CONFIG['directory'] = name
    
    # build paths
    DIRECTORY = CONFIG.get("directory")
    selected_sample_folder = os.path.join(samples_folder,DIRECTORY)
    workpath = __PERSONAL__
    cube_path = os.path.join(workpath,"output",DIRECTORY,"{}.cube".format(DIRECTORY))
    output_path = os.path.join(workpath,"output",DIRECTORY)
    dimension_file = os.path.join(selected_sample_folder, "colonneXrighe.txt")
    
    FIRSTFILE_ABSPATH = os.path.join(selected_sample_folder, name)

    global_list =  [CONFIG, CALIB, DIRECTORY,
            samples_folder, selected_sample_folder, workpath,
            cube_path, output_path, dimension_file,
            FIRSTFILE_ABSPATH]
    
    return np.nan

def RatioMatrixReadFile(ratiofile):

    """ Reads a ratio file created by any mapping module and transforms into
    a 2D-array.
    INPUT:
        ratiofile; path
    OUTPUT:
        RatesMatrix; 2D-array """

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

    """ Gets PMCA spectra file (*.mca) header
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

    if CONFIG['calibration'] == 'manual':
        param = CALIB 
    elif CONFIG['calibration'] == 'from_source':
        param = []
        mca_file = open(getfirstfile(),'r')
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
            pop_error("Calibration Error","Could not fetch calibration from source! Retry with manual calibration")
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
        raise ValueError("Calibration mode {0} unknown! Check config.cfg")
    return param

def getdata(mca):
    
    """ Extract the data contained in spectrum files 
    INPUT:
        mca; path
    OUTPUT:
        Data; 1D-array """

    name = str(mca)
    name = name.split("\\")[-1]
    name = name.replace('_',' ')
    
    # custom MC generated files
    if 'test' in name or 'obj' in name or 'newtest' in name:
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
        datafile = open(mca)
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
            while "<<END>>" not in line:
                ObjectData.append(int(line))
                line = datafile.readline()
                if line == "": break
        
        # if file has two columns separated by space or tab
        elif "\t" in line or " " in line: 
            while "<<END>>" not in line:
                counts = line.split("\t")[-1]
                if counts.isdigit(): ObjectData.append(int(counts))
                else:
                    counts = line.split(" ")[-1]
                    ObjectData.append(int(counts))
                line = datafile.readline()
                if line == "": break

        Data = np.asarray(ObjectData)
    datafile.close()
    return Data

def calibrate():
    
    """ Returns the energy axis and gain of the calibrated axis
    The parameters are taken from config.cfg if calibration is set to manual
    or from the mca files if calibration is set to from_source """

    param = getcalibration()
    x=[]
    y=[]
    for i in range(len(param)):
        for k in range(len(param[i])):
            x.append(param[i][0])
            y.append(param[i][1])
    x=np.asarray([x])
    y=np.asarray([y])
    coefficients=list(linregress(x,y))
    GAIN=coefficients[0]
    B=coefficients[1]
    R=coefficients[2]
    logger.info("Correlation coefficient R = %f!" % R)
    n = len(getdata(getfirstfile()))
    curve = []
    for i in range(n):
        curve.append((GAIN*i)+B)
    curve = np.asarray(curve)
    return curve,GAIN

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
    INPUT:
        specfile; string
        size; int
    OUTPUT:
        newfile; string """        
    
    try:
        global file_pool
        index = file_pool.index(specfile)
        newfile = file_pool[index+1]
    
    except (IndexError, ValueError): 

        global samples_folder

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
        newfile = os.path.join(samples_folder,
                CONFIG["directory"],
                str(prefix+index+"."+extension))
        
    return newfile

def getdimension():

    """ Gets the sample image dimension
    OUTPUT:
        x; int
        y; int
        user_input; bool """

    global dimension_file, samples_folder
    if not os.path.exists(dimension_file):
        dimension_file = os.path.join(samples_folder,"colonneXrighe.txt")
        if not os.path.exists(dimension_file):
            dimension_file = os.path.join(output_path,"colonneXrighe.txt")
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
    INPUT:
        maps_list; nD-array (element(string), line([0] or [0,1]), 2D-array)
        element_list; 1D string array 
    OUTPUT: 0 """

    # this is to work with multiprocessing Mapping mode
    
    ratiofiles = ["" for x in range(len(element_list))]
    for Element in range(len(element_list)): 
        ratiofiles[Element] = str(os.path.join(output_path,"{1}_ratio_{0}.txt".format(element_list[Element],DIRECTORY)))
        r_file = open(ratiofiles[Element],'w+')
        r_file.readline()
        r_file.truncate()
        r_file.write("-"*10 + " Counts of Element {0} "\
                .format(element_list[Element]) + 10*"-" + '\n')
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
                    logger.debug("{}\t{}\t{}\t{}\t{}\n".format(x,y,a,b,a/b))
                else: 
                    r_file.write("{}\t{}\t{}\t{}\t{}\n".format(x,y,a,b,0))
                    logger.debug("{}\t{}\t{}\t{}\t{}\n".format(x,y,a,b,0))
        r_file.close()
    return 0

def linregress(x, y, sigmay=None, full_output=False):

    # DISCLAIMER #
    # function extracted from PyMca5.PyMcaMath.fitting.RateLaw script

    """
    Linear fit to a straight line following P.R. Bevington:
    "Data Reduction and Error Analysis for the Physical Sciences"
    Parameters
    ----------
    x, y : array_like
        two sets of measurements.  Both arrays should have the same length.
    sigmay : The uncertainty on the y values
    Returns
    -------
    slope : float
        slope of the regression line
    intercept : float
        intercept of the regression line
    r_value : float
        correlation coefficient
    if full_output is true, an additional dictionary is returned with the keys
    sigma_slope: uncertainty on the slope
    sigma_intercept: uncertainty on the intercept
    stderr: float
        square root of the variance
    """

    x = np.asarray(x, dtype=np.float).flatten()
    y = np.asarray(y, dtype=np.float).flatten()
    N = y.size
    if sigmay is None:
        sigmay = np.ones((N,), dtype=y.dtype)
    else:
        sigmay = np.asarray(sigmay, dtype=np.float).flatten()
    w = 1.0 / (sigmay * sigmay + (sigmay == 0))

    n = S = w.sum()
    Sx = (w * x).sum()
    Sy = (w * y).sum()    
    Sxx = (w * x * x).sum()
    Sxy = ((w * x * y)).sum()
    Syy = ((w * y * y)).sum()
    # SSxx is identical to delta in Bevington book
    delta = SSxx = (S * Sxx - Sx * Sx)

    tmpValue = Sxx * Sy - Sx * Sxy
    intercept = tmpValue / delta
    SSxy = (S * Sxy - Sx * Sy)
    slope = SSxy / delta
    sigma_slope = np.sqrt(S /delta)
    sigma_intercept = np.sqrt(Sxx / delta)

    SSyy = (n * Syy - Sy * Sy)
    r_value = SSxy / np.sqrt(SSxx * SSyy)
    if r_value > 1.0:
        r_value = 1.0
    if r_value < -1.0:
        r_value = -1.0

    if not full_output:
        return slope, intercept, r_value

    ddict = {}
    # calculate the variance
    if N < 3:
        variance = 0.0
    else:
        variance = ((y - intercept - slope * x) ** 2).sum() / (N - 2)
    ddict["variance"] = variance
    ddict["stderr"] = np.sqrt(variance)
    ddict["slope"] = slope
    ddict["intercept"] = intercept
    ddict["r_value"] = r_value
    ddict["sigma_intercept"] = np.sqrt(Sxx / SSxx)
    ddict["sigma_slope"] = np.sqrt(S / SSxx)
    return slope, intercept, r_value, ddict

if __name__ == "__main__":
    logger.info("This is SpecRead")
