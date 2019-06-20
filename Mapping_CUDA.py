import SpecRead
import EnergyLib 
import SpecMath
import scipy
import numpy as np
from numba import *
from numba import guvectorize, float64
from numba import cuda
from numba import jit
import math
from matplotlib import pyplot as plt
import os
import ImgMath
import sys
import time

#os.environ['NUMBAPRO_NVVM']      =\
#        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvvm\bin\nvvm64_33_0.dll'
#
#os.environ['NUMBAPRO_LIBDEVICE'] =\
#        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvvm\libdevice'
#
#os.environ['NUMBAPRO_CUDA_DRIVER']      =\
#        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvcc'

time_init = time.time()

class datacube:
    
    ndim = 0

    def __init__(__self__,dtypes):
        __self__.dimension = SpecRead.getdimension()
        __self__.img_size = __self__.dimension[0]*__self__.dimension[1]
        __self__.datatypes = np.array(["{0}".format(dtypes[type]) for type in range(len(dtypes))])
        
        #last dimension is 1024 because of the spectra size
        __self__.matrix = np.zeros([__self__.dimension[0],__self__.dimension[1],1024])

    def compile_cube(__self__):
        currentspectra = SpecRead.getfirstfile()
        x,y,scan = 0,0,(0,0)
        for iteration in range(__self__.img_size):
            spec = currentspectra
            specdata = SpecRead.getdata(spec)
            for i in range(len(specdata)):
                __self__.matrix[x][y][i] = specdata[i]
            scan = ImgMath.updateposition(scan[0],scan[1])
            x,y = scan[0],scan[1]
            currentspectra = SpecRead.updatespectra(spec,\
                    __self__.dimension[0]*__self__.dimension[1])
            progress = int(iteration/__self__.img_size*20)
            blank = (20 - progress - 1)
            print("[" + progress*"\u25A0" + blank*" " + "]" + " / {0:.2f}"\
                    .format(iteration/__self__.img_size*100), "Compiling cube...  \r", end='')
            sys.stdout.flush()
    
    def unpack(__self__,mode,an_array):
        print("\n",an_array) 
        # attribute matrix with all elements
        __self__.element = \
                np.zeros([__self__.dimension[0],__self__.dimension[1],an_array.shape[0]])
        
        data_to_unpack = __self__.matrix

        if configdict.get('peakmethod') == 'PyMcaFit': import SpecFitter
        KaElementsEnergy = EnergyLib.Energies
        KbElementsEnergy = EnergyLib.kbEnergies
        
        energyaxis = SpecMath.energyaxis()
        current_peak_factor = 0
        max_peak_factor = 0
        ymax_spec = None
        usedif2 = True
        ratiofiles = ['' for x in range(an_array.shape[0])]

        #########################################
        # ERROR VARIABLES CUMSUM AND CUMSUM_RAW #
        #########################################
        
        CUMSUM = np.zeros([energyaxis.shape[0]])
        CUMSUM_RAW = np.zeros([energyaxis.shape[0]])
        BGSUM = np.zeros([energyaxis.shape[0]])

        #########################################

        kaindex,kbindex,kaenergy,kbenergy = \
                (np.zeros(len(an_array),dtype='int') for i in range(4))
         
        for Element in range(an_array.shape[0]):

            # sets ka energy
            kaindex[Element] = EnergyLib.ElementList.index(an_array[Element])
            kaenergy[Element] = KaElementsEnergy[kaindex[Element]]*1000
            
            # sets kb energy
            kbindex[Element] = EnergyLib.ElementList.index(an_array[Element])
            kbenergy[Element] = EnergyLib.kbEnergies[kbindex[Element]]*1000

            if configdict.get('ratio') == True:
                ratiofiles[Element] = str(SpecRead.workpath + '/output/'+\
                        '{1}_ratio_{0}.txt'.format(an_array[Element],SpecRead.DIRECTORY))
                r_file = open(ratiofiles[Element],'w+')
                r_file.readline()
                r_file.truncate()
                r_file.write("-"*10 + " Counts of Element {0} "\
                        .format(an_array[Element]) + 10*"-" + '\n')
                r_file.write("row\tcolumn\tline1\tline2\n")
                r_file.close() 

        x,y,scan = 0,0,(0,0)
        for iteration in range(__self__.img_size):
            
            specdata, RAW = __self__.matrix[x][y], __self__.matrix[x][y]
            background = np.zeros(specdata.shape[0])
            SpecMath.peakstrip(specdata,23,3,background)

            for Element in range(an_array.shape[0]):
                    
                ################################################################
                #    Kx_INFO[0] IS THE NET AREA AND [1] IS THE PEAK INDEXES    #
                # Be aware that PyMcaFit method peaks are returned always True #
                # Check SpecMath.py This is due to the high noise in the data  #
                ################################################################
                    
                ka_info = SpecMath.getpeakarea(kaenergy[Element],specdata,\
                        energyaxis,background,configdict,RAW,usedif2)
                ka = ka_info[0]
            
                for channel in range(len(specdata)):
                    if energyaxis[ka_info[1][0]] < energyaxis[channel]\
                        < energyaxis[ka_info[1][1]]:
                        CUMSUM[channel] += specdata[channel]
                        CUMSUM_RAW[channel] += RAW[channel]

                if ka == 0: 
                    kb = 0
                elif ka > 0:
                    kb_info = SpecMath.getpeakarea(kbenergy[Element],specdata,\
                            energyaxis,background,configdict,RAW,usedif2)
                    kb = kb_info[0]

                    for channel in range(len(specdata)):
                        if energyaxis[kb_info[1][0]] < energyaxis[channel]\
                            < energyaxis[kb_info[1][1]]:
                            CUMSUM[channel] += specdata[channel]
                            CUMSUM_RAW[channel] += RAW[channel]
            
                if ka > 0 and kb > 0: __self__.element[x][y][Element] = ka+kb
                
                else:
                    __self__.element[x][y][Element] = 0
                    ka, kb = 0, 0
                
                row = scan[0]
                column = scan[1]
             
                if configdict.get('ratio') == True: 
                    try: 
                        r_file = open(ratiofiles[Element],'a')
                        r_file.write("%d\t%d\t%d\t%d\t%s\n" % (row, column, ka, kb))
                        r_file.close()
                    except:
                        print("ka and kb not calculated for some unknown reason.\
            Check Config.cfg for the correct spelling of peakmethod option!")
            
            ########################################
            #   UPDATE CUBE POSITION AND SPECTRA   #
            ########################################        

            # Reset background value since it runs inside a ufunc
            background = np.zeros([specdata.shape[0]])

            scan = ImgMath.updateposition(scan[0],scan[1])
            x,y = scan[0],scan[1]
            progress = int(iteration/__self__.img_size*20)
            blank = 20 - progress - 1
            print("[" + progress*"\u25A0" + blank*" " + "]" + " / {0:.2f}"\
                    .format(iteration/__self__.img_size*100), "Percent complete  \r", end='')
            sys.stdout.flush()
        print("Finished unpacking. Time: {0}".format(time.time()-time_init))
        
        stacksum = SpecMath.stacksum(SpecRead.getfirstfile(),__self__.img_size)
        plt.plot(energyaxis,CUMSUM_RAW,label='CUMSUM RAW DATA')
        plt.plot(energyaxis,stacksum,label='stackplot')
        plt.plot(energyaxis,BGSUM,label='background')
        plt.legend()
        plt.show()
         
        ImgMath.split_and_save(__self__.element,an_array,configdict)


configdict = SpecRead.CONFIG
data = np.array(['xrf'])
cube = datacube(data)
print(cube.datatypes)
energyaxis = SpecMath.energyaxis()
cube.compile_cube()
cube.unpack(0,np.array(['Cu','Ag','Au']))

stacksum = np.zeros([cube.matrix[0][0].shape[0]])
densitymap = np.zeros([cube.dimension[0],cube.dimension[1]])
for x in range(cube.dimension[0]):
    for y in range(cube.dimension[1]):
        spec = cube.matrix[x][y]
        stacksum += spec
        if configdict.get('bgstrip') == 'SNIPBG': 
            snip_bg = np.zeros([spec.shape[0]])
            SpecMath.peakstrip(spec,24,3,snip_bg)
        else: background = np.zeros([spec.shape[0]])
        densitymap[x][y] = sum(spec)-sum(snip_bg)
        
print("TIME: {0}".format(time.time()-time_init))

fig, ax = plt.subplots(1,1)
img_densitymap = ax.imshow(densitymap,cmap='jet')
ImgMath.colorbar(img_densitymap)
plt.show()




def manipulate_array(array):
    for i in range(len(array)):
        array[i] = math.pow(array[i],2)
    return array

myfile = SpecRead.getfirstfile()
mydata = SpecRead.getdata(myfile)
myaxis = SpecMath.energyaxis()

def transformed_array(array):
    new_array = array[10:20]
    return new_array

def differential(array1,array2):
    dif2 = SpecMath.getdif2(array1,array2,1)
    return dif2

dimension = SpecRead.getdimension()

mydif = differential(mydata,myaxis)

my2darray = np.zeros([dimension[0],dimension[1]])

threadsperblock = (5,5)
blockspergrid_x = int(math.ceil(my2darray.shape[0]) / threadsperblock[0])
blockspergrid_y = int(math.ceil(my2darray.shape[1]) / threadsperblock[1])
blockspergrid = (blockspergrid_x,blockspergrid_y)

@cuda.jit
def fill_image(a2Darray):
    x,y = cuda.grid(2)
    if x < a2Darray.shape[0] and y < a2Darray.shape[1]:
        a2Darray[x,y] = 100

#fill_image[blockspergrid, threadsperblock](my2darray)
