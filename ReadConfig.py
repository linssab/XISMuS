#################################################################
#                                                               #
#          CONFIGURATION PARSER                                 #
#                        version: 1.0.0                         #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import logging
import os

def pop_error(title,message):

    """ Displays TK error message """

    from tkinter import messagebox
    messagebox.showerror(title,message)
    return 0

""" Get working path and config.cfg path """

workpath = os.getcwd()
cfgfile = workpath + '\config.cfg'
logging.debug("Importing module ReadConfig.py...")

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
                modesdict['directory'] = str(aux[2])
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
            try: CalParam.append([int(aux[0]),float(aux[1])])
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
    
    cfgfile = os.getcwd() + '\config.cfg'
    lines, tags = [],[]
    c_file = open(cfgfile, 'r')
    for line in c_file:
        line = line.replace('\n','')
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

if __name__ == "__main__":
    logging.info("This is ReadConfig")
