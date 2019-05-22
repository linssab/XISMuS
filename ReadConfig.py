import logging
import os

workpath = os.getcwd()
configfile = workpath + '\config.cfg'

def getconfig():
    modesdict = {}
    file = open(configfile, 'r')
    line = file.readline()
    if "<<CONFIG_START>>" in line:
        line = file.readline()
        while "<<CALIBRATION>>" not in line:
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
            file.close()
    return modesdict

CONFIG = getconfig()

