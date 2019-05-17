import numpy as np
from numba import cuda
from numba import *
import time
import sys
from matplotlib import pyplot as plt
import os

os.environ['NUMBAPRO_NVVM']      =\
        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvvm\bin\nvvm64_33_0.dll'

os.environ['NUMBAPRO_LIBDEVICE'] =\
        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvvm\libdevice'

os.environ['NUMBAPRO_CUDA_DRIVER']      =\
        r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.1\nvcc'

size = 10000
rimage = np.zeros((size,size), dtype = 'float64')

@jit
def pow(a,b):
    return float64(a**b)

pow_gpu = cuda.jit(device=True)(pow)

@cuda.jit
def apply_kernel(v1,v2,v3):
    
    startX, startY = cuda.grid(2)
    gridX = cuda.gridDim.x * cuda.blockDim.x
    gridY = cuda.gridDim.y * cuda.blockDim.y
    
    for i in range(startX, len(v1), gridX):
        for j in range(startY, len(v1[i]), gridY):
            v1[i][j] = pow_gpu(v2[i],v3[i])

@jit
def apply(v1,v2,v3):
    
    for i in range(len(v1)):
        for j in range(len(v1[i])):
            v1[i][j] = pow(v2[i],v3[i])


v2,v3 = np.random.rand(size),np.random.rand(size)

blockdim = (10, 10)
griddim = (10,10)

start = time.time()

#########################################

output = cuda.to_device(rimage)

apply_kernel[griddim,blockdim](output,v2,v3)

output.to_host()

#########################################

print(time.time() - start)
plt.imshow(output)
plt.show()
