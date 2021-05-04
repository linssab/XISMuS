#################################################################
#                                                               #
#          CSV Writer                                           #
#                        version: 2.3.2 - May - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

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

