#################################################################
#                                                               #
#          SPEC MATHEMATICS                                     #
#                        version: a0.3                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import os
import numpy as np
import math
from scipy.fftpack import fft
import matplotlib.pyplot as plt
import SpecRead

def DFT(fx):
    Fu = np.fft.fft(fx)
    Power = np.abs(Fu)**2
    FuFilt = np.fft.ifft(Fu)
    plt.plot(fx)
    plt.plot(FuFilt)
    plt.show()
    return FuFilt

def stacksum(firstspec,dimension):
    " DIMENSION STANDS FOR THE MAP DIMENSION, LINES*ROWS (OR THE NUMBER OF FILES) "
    " SO THE FUNCTION GETS THE TOTAL NUMBER OF SPECTRA TO BE STACKED "
    aux = SpecRead.getdata(firstspec)
    currentspectra = firstspec
    Stack = np.array([len(aux)])
    for i in range(dimension):
        spec = currentspectra
        data = np.asarray(SpecRead.getdata(spec))
        Stack = Stack + data
        currentspectra = SpecRead.updatespectra(spec,dimension)
    return Stack

def gaussianbuilder(channel,energy,NOISE,FANO):
    sigma = math.sqrt(((NOISE/3.3548)**2)+(3.85*FANO*energy))
    chEnergy = (channel*GAIN + B)*1000
    A = GAIN/(sigma)*math.sqrt(2*math.pi)
    return A*(math.exp(-(((energy-chEnergy)**2)/(2*(sigma**2)))))

def creategaussian(channels,energy,NOISE,FANO):
    Gaussian = np.zeros([channels])
    if isinstance(energy,int):
        for i in range(channels):
            Gaussian[i]+=gaussianbuilder(i,energy,NOISE,FANO)
    elif isinstance(energy,list): 
        for i in range(channels):
            for k in range(len(energy)):
                    Gaussian[i]+=gaussianbuilder(i,energy[k],NOISE,FANO)
    return Gaussian

if __name__=="__main__":

    # THIS GETS A DEFAULT CALIBRATION FROM config.cfg FILE
    # THIS IS ONLY USEFUL FOR PLOTTING THE GAUSSIANS
    file = SpecRead.dirname+'Cesareo_1.mca'
    calibration = SpecRead.calibrate(file,'data')
    GAIN = calibration[-1]/len(calibration)
    B = calibration[0]
