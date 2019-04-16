#   SPEC FITTER    #
#   Armando Solè   #

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
print(currentConfig['peaks'])
mcafit.configure(currentConfig)

def fit(specfile):
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
        yfit = numpy.zeros([len(channels)])
    return yfit

