#################################################################
#                                                               #
#          THIS IS A FIT TEST FILE                              #
#                        version: null                          #
#                                                               #
#################################################################

import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math
from PyMca5.PyMcaPhysics.xrf import Elements
import SpecRead
import SpecMath

ElementList = [ elt[0] for elt in Elements.ElementsInfo ]
ElementBinding=Elements.ElementBinding
ElementsInfo=Elements.ElementsInfo

"""
DEFINE THE GLOBAL VAR FOR CALCULATING G(i,Ej) AND s
"""
specfile = SpecRead.getfirstfile()
energyaxis = SpecMath.energyaxis()
n = len(energyaxis)      #__number of channels
FANO = 0.114                              #__SILICON
NOISE = 90
ZERO = 0
CHANNEL = np.zeros([n])
ENERGY = np.zeros([n])
GAIN = SpecRead.getgain(specfile,'data')*1000

"""
END OF GLOBAL VARIABLES DEFINITION
"""
    
def normGauss(channel,eVline):
    width = s(eVline)
    energy = 1000*energyaxis[channel]
    A = GAIN/(width)*math.sqrt(2*math.pi)
    return A * (math.exp(-(((eVline-energy)**2)/(2*(width**2)))))

def E(ch):
    return ZERO+(GAIN*ch)

def s(eV):
    return math.sqrt(((NOISE/3.3548)**2)+(3.85*FANO*eV))

def GiEj(element_energy):
    G=np.zeros([n])
    for j in range(len(element_energy)):
        for i in range(n):
            G[i] += normGauss(i,element_energy[j])
    return G

for i in range(n):
    CHANNEL[i]=i
    ENERGY[i]=E(i)/1000

data = SpecRead.getdata(SpecRead.getfirstfile())
data = data/data.max()
energies = [10501]
plt.plot(SpecMath.energyaxis(),GiEj(energies))
plt.plot(SpecMath.energyaxis(),data)
plt.show()


if __name__=="__main__":
    #ele = sys.argv[1]
    ele = 'Au'
    Analytic=[]
    for rays in Elements.Element[ele]['rays']:
        print(rays, ":")
        for transition in Elements.Element[ele][rays]:
            print("%s energy = %.5f rate %.5f" % \
                    (transition, Elements.Element[ele][transition]['energy'],\
                    Elements.Element[ele][transition]['rate']))
            Analytic.append(Elements.Element[ele][transition]['energy']*1000)
    print("Every transition for element %s : %r" % (ele,Analytic))
