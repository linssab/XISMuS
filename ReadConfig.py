#################################################################
#                                                               #
#          CONFIGURATION PARSER                                 #
#                                                               #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
#################################################################

import logging
import os

workpath = os.getcwd()
configfile = workpath + '\config.MC.cfg'

logging.basicConfig(format = '%(asctime)s\t%(levelname)s\t%(message)s',\
        filename = 'logfile.log',level = logging.DEBUG)
with open('logfile.log','w+') as mylog: mylog.truncate(0)
logging.info('*'* 10 + ' LOG START! ' + '*'* 10)

def check_config():
    lines, tags = [],[]
    try: c_file = open(configfile, 'r')
    except: raise FileNotFoundError("No calibration file {0} found!".format(configfile))
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
    return True

def getconfig():
    check_config()
    modesdict = {}
    CalParam = []
    file = open(configfile, 'r')
    line = file.readline()
    if "<<CONFIG_START>>" in line:
        line = file.readline()
        while "<<CALIBRATION>>" not in line:
            if 'filename' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                modesdict['firstfile'] = str(aux[2])
                line = file.readline()
            if 'directory' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                modesdict['directory'] = str(aux[2])
                line = file.readline()
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
            if 'thick_ratio' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                modesdict['thickratio'] = float(aux[2])
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
            if 'netpeak_method' in line:
                line=line.replace('\r','')
                line=line.replace('\n','')
                line=line.replace('\t',' ')
                aux = line.split()
                modesdict['peakmethod'] = str(aux[2])
                line = file.readline()
        line = file.readline()
        while "<<END>>" not in line:
            line=line.replace('\r','')
            line=line.replace('\n','')
            line=line.replace('\t',' ')
            aux = line.split()
            try: CalParam.append([int(aux[0]),float(aux[1])])
            except: CalParam = [[0]]
            line = file.readline()
        file.close()
    for parameter in CalParam:
        if len(CalParam) <= 1: raise IOError("Need at least two calibration points!")
        if parameter[0] < 0 or parameter[1] < 0: 
            raise IOError("Cant receive negative channel or energy!")
        else: pass
    return modesdict,CalParam

all_parameters = getconfig()
CONFIG = all_parameters[0]
CALIB = all_parameters[1]

