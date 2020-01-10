#################################################################
#                                                               #
#          CONFIGURATION PARSER                                 #
#                        version: 0.0.2α                        #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import logging
import os

workpath = os.getcwd()
cfgfile = workpath + '\config.cfg'
logging.debug("Importing module ReadConfig.py...")

def check_config():
    lines, tags = [],[]
    try: c_file = open(cfgfile, 'r')
    except: raise FileNotFoundError("No calibration file {0} found!".format(cfgfile))
    for line in c_file:
        line = line.replace('\n','')
        lines.append(line)
    for sentence in lines:
        if "<<CALIBRATION>>" in sentence: tags.append(sentence)
        elif "<<CONFIG_START>>" in sentence: tags.append(sentence)
        elif "<<END>>" in sentence: tags.append(sentence)
    if "<<CALIBRATION>>" not in tags: raise IOError("No <<CALIBRATION>>!")
    if "<<END>>" not in tags: raise IOError("No <<END>> of configuration!")
    if "<<CONFIG_START>>" not in tags: raise IOError("Cant find <<CONFIG_START>>")
    return tags

def getconfig():
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

def unpack_cfg():
    all_parameters = getconfig()
    CONFIG = all_parameters[0]
    CALIB = all_parameters[1]
    return CONFIG, CALIB

if __name__ == "__main__":
    logging.info("This is ReadConfig")
