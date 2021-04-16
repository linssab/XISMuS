#################################################################
#                                                               #
#          CONFIGURATION PARSER                                 #
#                        version: 2.3.0 - Apr - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import logging, os
import Constants
from win32com.shell import shell, shellcon

def pop_error(title,message):

    """ Displays TK error message """

    from tkinter import messagebox
    messagebox.showerror(title,message)
    return 0

""" Get working path and config.cfg path """

docs = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
__PERSONAL__ = os.path.join(docs,"XISMuS")
__BIN__ = os.path.join(__PERSONAL__,"bin")

cfgfile = os.path.join(__BIN__,"config.cfg")
logger = logging.getLogger("logfile")
logger.debug("Importing module ReadConfig.py...")

def check_config():
    """ Tries to read Config.cfg and verifies it contain all needed entries.
    Returns tags found in file. """

    lines, tags = [],[]
    try: c_file = open(cfgfile, 'r')
    except: 
        pop_error("Configuration Error","No calibration file {0} found!".format(cfgfile))
        raise FileNotFoundError("No calibration file {0} found!".format(cfgfile))
    for line in c_file:
        line = line.replace('\n','')
        lines.append(line)
    for sentence in lines:
        if "<<CONFIG_START>>" in sentence: tags.append(sentence)
        elif "<<CALIBRATION>>" in sentence: tags.append(sentence)
        elif "<<END>>" in sentence: tags.append(sentence)
    if "<<CONFIG_START>>" not in tags: raise IOError("Cant find <<CONFIG_START>>")
    if "<<CALIBRATION>>" not in tags: raise IOError("No <<CALIBRATION>>!")
    if "<<END>>" not in tags: raise IOError("No <<END>> of configuration!")
    return tags

def getconfig():
    """ Extracts all configuration information in Config.cfg

    --------------------------------------------------------

    OUTPUT:
        modesdict; dict
        CalParam; 2D-list """

    tags = check_config()
    modesdict = {}
    CalParam = []
    configfile = open(cfgfile, 'r')
    line = configfile.readline()
    if "<<CONFIG_START>>" in line:
        line = configfile.readline()
        while "<<CALIBRATION>>" not in line:
            if 'directory' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                # removes key and "="
                aux.pop(0)
                aux.pop(0)
                directory = ""
                # build up the folder name with spaces. can't have space at the end
                for i in range(len(aux)):
                    if i < len(aux)-1: directory += aux[i] + " "
                    else: directory += aux[i]
                modesdict['directory'] = directory
            if 'bgstrip' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                modesdict['bgstrip'] = str(aux[2])
            if 'ratio' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                if aux[2] == 'True': modesdict['ratio'] = True
                elif aux[2] == 'False': modesdict['ratio'] = False
            if 'thickratio' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                modesdict['thickratio'] = float(aux[2])
            if 'calibration' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                modesdict['calibration'] = str(aux[2])
            if 'enhance' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                if aux[2] == 'True': modesdict['enhance'] = True
                elif aux[2] == 'False': modesdict['enhance'] = False
            if 'peakmethod' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                modesdict['peakmethod'] = str(aux[2])
            if 'bg_settings' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t','')
                line=line.replace(',','')
                line=line.replace('(','')
                line=line.replace(')','')
                aux = line.split(" ")
                bs_list = []
                for i in aux:
                    if i.isdigit(): bs_list.append(int(i))
                modesdict['bg_settings'] = bs_list
                del bs_list
            line = configfile.readline()
        line = configfile.readline()
        while "<<END>>" not in line:
            line=line.replace('\r','')
            line=line.replace('\n','')
            line=line.replace('\t',' ')
            aux = line.split()
            try: CalParam.append([float(aux[0]),float(aux[1])])
            except: CalParam = [[0,0]]
            line = configfile.readline()
        configfile.close()
    for parameter in CalParam:
        if len(CalParam) <= 1: raise IOError("Need at least two calibration points!")
        if parameter[0] < 0 or parameter[1] < 0: 
            raise IOError("Cant receive negative channel or energy!")
        else: pass
    return modesdict,CalParam

def checkout_config():
    """ Re-sets Config.cfg file with default values if any tag is missing. """
    
    cfgfile = os.path.join(__BIN__,"config.cfg")
    lines, tags = [],[]
    c_file = open(cfgfile, "r")
    for line in c_file:
        line = line.replace("\n","")
        lines.append(line)
    for sentence in lines:
        if "<<CONFIG_START>>" in sentence: tags.append(sentence)
        elif "<<CALIBRATION>>" in sentence: tags.append(sentence)
        elif "<<END>>" in sentence: tags.append(sentence)
    c_file.close()
    if "<<CONFIG_START>>" not in tags: 
        c_file = open(cfgfile, "a+")
        c_file.write("<<CONFIG_START>>\r")
        c_file.write("directory = None\r")
        c_file.write("bgstrip = None\r")
        c_file.write("ratio = False\r")
        c_file.write("thickratio = 0\r")
        c_file.write("calibration = manual\r")
        c_file.write("enhance = False\r")
        c_file.write("peakmethod = simple_roi\r")
        c_file.write("bgsettings = None\r")
        c_file.write("<<CALIBRATION>>\r")
        c_file.write("<<END>>\r")
        c_file.close()
        pop_error("Configuration issue",\
                "Config.cfg file corrupted, re-setting default configuration.")
        
    elif "<<CALIBRATION>>" not in tags: 
        c_file = open(cfgfile, "a")
        c_file.write("<<CALIBRATION>>\r")
        c_file.write("<<END>>\r")
        c_file.close()
    elif "<<END>>" not in tags: 
        c_file = open(cfgfile, "a")
        c_file.write("<<END>>\r")
        c_file.close()
    return 0

def unpack_cfg():
    """ Calls getconfig to get configuration parameters """

    all_parameters = getconfig()
    CONFIG = all_parameters[0]
    CALIB = all_parameters[1]
    return CONFIG, CALIB

def set_settings(inifile):
    ini = open(inifile,"r")
    for line in ini:
        line = line.replace("\n","")
        line = line.replace("\r","")
        if line.split("\t")[0] == "<ColorMap>": 
            ColorMapMode = str(line.split("\t")[1])
            ColorMapMode = ColorMapMode.replace("\n","")
        elif line.split("\t")[0] == "<MultiCore>": 
            if line.split("\t")[1] == "False":
                CoreMode = False
            else: CoreMode = True
        elif line.split("\t")[0] == "<PlotMode>": 
            PlotMode = str(line.split("\t")[1])
        elif line.split("\t")[0] == "<RAMLimit>": 
            if line.split("\t")[1] == "False":
                RAMMode = False
            else: RAMMode = True
        elif line.split("\t")[0] == "<welcome>": 
            if line.split("\t")[1] == "False":
                WlcmMode = False
            else: WlcmMode = True
        elif line.split("\t")[0] == "<Tolerance>":
            PeakTolerance=[]
            line = line.split("\t")[1].replace("[","").replace("]","")
            line = line.split(",")
            for i in line:
                PeakTolerance.append(float(i))
        elif line.split("\t")[0] == "<Cycles>":
            Cycles = int(line.split("\t")[1])
        elif line.split("\t")[0] == "<Sensitivity>":
            Sensitivity = float(line.split("\t")[1])
        elif line.split("\t")[0] == "<Suppression>":
            ContSuppr = float(line.split("\t")[1])
        elif line.split("\t")[0] == "<WizTolerance>":
            WizTol = float(line.split("\t")[1])
        elif line.split("\t")[0] == "<SaveInterval>":
            SaveInterval = int(line.split("\t")[1])
        elif line.split("\t")[0] == "<SavePlot>":
            if line.split("\t")[1] == "False":
                SavePlot = False
            else: SavePlot = True
    ini.close() 
    Constants.COLORMAP = ColorMapMode
    Constants.MULTICORE = CoreMode
    Constants.PLOTMODE = PlotMode
    Constants.RAM_LIMIT = RAMMode
    Constants.WELCOME = WlcmMode
    Constants.SETROI_TOLERANCE = PeakTolerance
    Constants.FIT_CYCLES = Cycles
    Constants.PEAK_TOLERANCE = Sensitivity
    Constants.CONTINUUM_SUPPRESSION = ContSuppr
    Constants.CHECK_TOLERANCE = WizTol
    Constants.SAVE_INTERVAL = SaveInterval
    Constants.SAVE_FIT_FIGURES = SavePlot

    if PlotMode == "Logarithmic": Constants.PLOTSCALE = "-semilogy"
    else: Constants.PLOTSCALE = None

    output = Constants.list_all()

    return

if __name__ == "__main__":
    logger.info("This is ReadConfig")
