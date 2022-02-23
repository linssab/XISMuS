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

import csv
import os

class FitWriter:
    def __init__(__self__,data,path):
        lines = []
        __self__.ElementData = {}
        for element in data.keys(): 
            __self__.ElementData[element] = {}
            __self__.ElementData[element]["Element"] = element
            ellines = list(data[element]["Lines"])
            lines.extend(ellines)
            for i in range(len(ellines)):
                __self__.ElementData[element][ellines[i]] = data[element]["Areas"][i]
            i = 0
            lines = list(set(lines))
        fields = ["Element"]
        fields.extend(lines)
        fields.append("Area")
        __self__.fields = fields
        __self__.path = path

    def dump(__self__):
        with open(__self__.path, mode="w") as f:
            writer = csv.DictWriter(f, fieldnames=__self__.fields)
            writer.writeheader()
            for element in __self__.ElementData.keys():
                writer.writerow(__self__.ElementData[element])
        f.close()

