#################################################################
#                                                               #
#          SPEC MATHEMATICS                                     #
#                        version: a0.2                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import os
import numpy as np
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
