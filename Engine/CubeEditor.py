"""
Copyright (c) 2020 Sergio Augusto Barcellos Lins & Giovanni Ettore Gigante

The example data distributed together with XISMuS was kindly provided by
Giovanni Ettore Gigante and Roberto Cesareo. It is intelectual property of 
the universities "La Sapienza" University of Rome and Università degli studi di
Sassari. Please do not publish, commercialize or distribute this data alone
without any prior authorization.

This software is distrubuted with an MIT license.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Credits:
Few of the icons used in the software were obtained under a Creative Commons 
Attribution-No Derivative Works 3.0 Unported License (http://creativecommons.org/licenses/by-nd/3.0/) 
from the Icon Archive website (http://www.iconarchive.com).
XISMuS source-code can be found at https://github.com/linssab/XISMuS
"""

import numpy as np

def un_phase(
        datacube,
        start,
        stop,
        n,
        el=None, line=None):

    # n = number of pixels to move [-inf,+inf]

    print("start: ", start)
    print("stop: ", stop)
    for i in range(start, stop+1, 2):
        datacube.matrix[i,:,:] = np.roll(datacube.matrix[i,:,:], n, 0)
    print(datacube.matrix.shape)
    if n>0: datacube.matrix = datacube.matrix[ :, n: ,: ]
    else: datacube.matrix = datacube.matrix[ :, :n, : ]
    print(datacube.matrix.shape)
    datacube.dimension = datacube.matrix.shape[0], datacube.matrix.shape[1]
    datacube.specsize = datacube.matrix.shape[-1]
    datacube.img_size = datacube.dimension[0] * datacube.dimension[1]
    datacube.create_densemap()
    save = input("SAVE (Y/N)? ")
    if save == "Y": datacube.save_cube()
    else: pass
    if el is not None:
        try: return datacube.unpack_element(el,line)
        except: 
            return datacube.densitymap
    else:
        return datacube.densitymap
