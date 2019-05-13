##########################################
#              SPEC FITTER               #
# uses PyMca modules from Armando Solè   #
##########################################

import os
import numpy
from PyMca5.PyMcaIO import specfilewrapper as Specfile
from PyMca5.PyMcaIO import ConfigDict
from PyMca5.PyMcaPhysics.xrf import ClassMcaTheory
from PyMca5.PyMcaPhysics.xrf import ConcentrationsTool
from PyMca5 import PyMcaDataDir
import SpecRead
import SpecMath
import matplotlib.pyplot as plt
import random

print(5*'*'+" FIT CONFIGURATION STEP " + 5*'*')
fit_elements = input('Which elements may be found in your sample?:\
 (split them with spaces)\n')

import EnergyLib
PeakList = EnergyLib.SetPeakLines()
fit_elements = fit_elements.split(' ')
peaks = {"{0}".format(elt):PeakList[elt] for elt in fit_elements}

print("FIT CONFIG")
cfg =  ('fitconfigGUI.cfg')
config = ConfigDict.ConfigDict()
config.read(cfg)

mcafit = ClassMcaTheory.ClassMcaTheory()
mcafit.configure(config)

# concentrationsTool = ConcentrationsTool.ConcentrationsTool()
# concentrationsFormat = ConcentrationsTool.ConcentrationsConversion()

currentConfig = mcafit.configure()

print(currentConfig['detector']['gain'])
calibration = SpecRead.calibrate(SpecRead.getfirstfile(),'data')
currentConfig['detector']['gain'] = calibration[1] 
print(currentConfig['detector']['gain'])

currentConfig['detector']['fano'] = SpecMath.FANO

currentConfig['peaks'] = peaks
print(currentConfig['peaks'])
mcafit.configure(currentConfig)

def fit(specfile):
    
    currentConfig['fit']['stripiterations'] = 0
    
    counts = SpecRead.getdata(specfile)
    channels = numpy.arange(len(counts))
    if counts.max() <= 13: counts = counts + random.randint(1,2)
    if counts.max() >= 14: 
        mcafit.setData(channels, counts)
        mcafit.estimate()
        fitresult, result = mcafit.startfit(digest=1)
        xdata = result.get('xdata')
        ydata = result.get('ydata')
        yfit = result.get('yfit')
        energy = result.get('energy')
#        plt.plot(energy, ydata)
#        plt.plot(energy, yfit)
#        plt.show()
    
#        concentrationsConfig = concentrationsTool.configure()
#        concentrationsConfig = mcafit.configure()["concentrations"]
        
#        concentrations, info = concentrationsTool.processFitResult(\
#                             config=concentrationsConfig,
#                             fitresult={"result":result},
#                             elementsfrommatrix=False,
#                             fluorates=mcafit._fluoRates,
#                             addinfo=True)
#        print(concentrations)
    else:
        logging.warning("yfit = 0! Because counts.max() = {0}".format(counts.max()))
        yfit = numpy.zeros([len(channels)])
    return yfit

