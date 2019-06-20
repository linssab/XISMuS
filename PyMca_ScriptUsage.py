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

DATA_directory = SpecRead.dirname
DATA_file = DATA_directory + 'Cesareo_100.mca'

# read the data to be fitted
fname = os.path.join(DATA_directory, DATA_file)
print(fname)
spec_RAW = SpecRead.getdata(fname)
sf = Specfile.Specfile(fname)
nScans = sf.scanno() 
# number of scans in file, one in this case

nMcaInScan = sf[0].nbmca() 
# number of MCA in scan[0]

counts = sf[0].mca(1)
counts = SpecRead.getdata(fname)
# retrieve data of 1st MCA in scan[0]

channels = numpy.arange(len(counts))
sf = None

# read the dictionnary containing the fit configuration to be used
# I recommend to generate at least once that configuration with the
# Graphical User Interface in order to see what changes
cfg =  ('fitconfigGUI.cfg')
config = ConfigDict.ConfigDict()
config.read(cfg)

# to calculate the concentrations will need a ConcentrationTool instance
concentrationsTool = ConcentrationsTool.ConcentrationsTool()

# handy tools for formatting output
concentrationsFormat = ConcentrationsTool.ConcentrationsConversion()


# Typical usage
mcafit = ClassMcaTheory.ClassMcaTheory()
mcafit.configure(config)

# the previous command can also be used to retrieve the config
# for instance:

currentConfig = mcafit.configure()

# this gives back a dictionary that can be modified by the user and set back
currentConfig['detector']['gain'] = SpecRead.getgain(fname,'data')
currentConfig['detector']['fano'] = SpecMath.FANO

mcafit.configure(currentConfig)
print(currentConfig['detector']['gain'])

# this is to be done for every spectra to fit with that configuration
if counts.max() > 1: 
#    channels = channels[min:max]
#    counts = counts[min:max]
    mcafit.setData(channels, counts)
    mcafit.estimate()
else:
    raise ValueError("counts max is {0}!".format(counts.max()))
fitresult, result = mcafit.startfit(digest=1)
xdata = result.get('xdata')
ydata = result.get('ydata')
yfit = result.get('yfit')
energy = result.get('energy')

plt.plot(SpecMath.energyaxis(),ydata)
plt.plot(SpecMath.energyaxis(),yfit)
plt.show()

"""
# the concentrations tool has its own configuration
concentrationsConfig = concentrationsTool.configure()

# however, the simplest way to use it is to use the configuration
# set when sending the fit configuration
concentrationsConfig = result["config"]["concentrations"]
# or the one used with the fit
concentrationsConfig = mcafit.configure()["concentrations"]

concentrations, info = concentrationsTool.processFitResult( \
                             config=concentrationsConfig,
                             fitresult={"result":result},
                             elementsfrommatrix=False,
                             fluorates=mcafit._fluoRates, # internal speed up
                             addinfo=True) # additional important info

# I suggest you to print the concentrations to get an idea of the information
# returned
print(concentrations)
print(info)

# get some nicer output
print(concentrationsFormat.getConcentrationsAsAscii(concentrations))

# for instance, if we want to consider tertiary excitation
config = mcafit.configure()
config["concentrations"]['usemultilayersecondary'] = 2
mcafit.configure(config)
mcafit.setData(channels, counts)
mcafit.estimate()
fitresult, result = mcafit.startfit(digest=1)
concentrationsConfig = mcafit.configure()["concentrations"]
concentrations, info = concentrationsTool.processFitResult( \
                             config=concentrationsConfig,
                             fitresult={"result":result},
                             elementsfrommatrix=False,
                             fluorates=mcafit._fluoRates, # internal speed up
                             addinfo=True) # additional important info
# get some nicer output
print(concentrationsFormat.getConcentrationsAsAscii(concentrations))
"""
