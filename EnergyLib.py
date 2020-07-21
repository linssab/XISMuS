#################################################################
#                                                               #
#          DATABASE FOR ELEMENTS                                #
#                        version: 1.1.0 - Jul - 2020            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import numpy as np
import logging
import random, os
import Constants
logger = logging.getLogger("logfile")
logger.debug("Importing module EnergyLib.py...")
try: 
    import xraylib as xlib
    Constants.USEXLIB = True
    xlib.SetErrorMessages(0)
except: 
    logger.warning("xraylib module not found!")
    print("FAILED TO LOAD XRAYLIB MODULE\nContinuing with internal library, errors may occur.")
    Constants.USEXLIB = False

"ELEMENT, ,DENSITY, MASS, KA OR LA, KB OR LB, MU(20KeV), MU(PB-LA), MU(PB-LB), MU(CU-KA), MU(CU-KB)"

ElementsInfo = [
   ["Custom", 0.0001, 1.01,   0,      0,     0,      0,      0,      0,      0], 
   ["H",    0.0007, 1.01,   0,          0,          0.3695, 0.384,  0.3803, 0.3912, 0.3883],
   ["He",   0.0002, 4.00,   0,          0,          0,      0,      0,      0,      0,],
   ["Li",   0.53,   6.94,   0,          0,          0,      0,      0,      0,      0],
   ["Be",   1.85,   9.01,   0.108,      0,          0,      0,      0,      0,      0],
   ["B",    2.34,   10.81,  0.183,      0,          0,      0,      0,      0,      0],
   ["C",    2.27,   12.01,  0.277,      0,          0.442,  2.037,  1.248,  4.496,  3.328],
   ["N",    0.001,  14.01,  0.392,      0,          0,      0,      0,      0,      0],
   ["O",    0.001,  16.00,  0.525,      0,          0.8653, 5.077,  3.003,  11.43,  8.427],
   ["F",    0.001,  19.00,  0.677,      0,          0,      0,      0,      0,      0],
   ["Ne",   0.0009, 20.18,  0.849,      0,          0,      0,      0,      0,      0],
   ["Na",   0.97,   22.99,  1.040,      1.06700003, 0,      0,      0,      0,      0],
   ["Mg",   1.74,   24.31,  1.25399995, 1.29700005, 0,      0,      0,      0,      0],
   ["Al",   2.70,   26.98,  1.48699999, 1.55299997, 3.442,  22.41,  13.24,  49.47,  36.83],
   ["Si",   2.33,   28.09,  1.74000001, 1.83200002, 0,      0,      0,      0,      0],
   ["P",    1.82,   30.97,  2.0150001,  2.13599992, 0,      0,      0,      0,      0],
   ["S",    2.07,   32.07,  2.30800009, 2.46399999, 0,      0,      0,      0,      0],
   ["Cl",   0.003,  35.45,  2.62199998, 2.81500006, 0,      0,      0,      0,      0],
   ["Ar",   0.002,  39.95,  2.95700002, 3.19199991, 8.63,   52.26,  32.63,  116.1,  87.54],
   ["K",    0.86,   39.01,  3.31299996, 3.58899999, 0,      0,      0,      0,      0],
   ["Ca",   1.54,   40.08,  3.69099998, 4.01200008, 13.06,  80.44,  48.71,  169.9,  128.8],
   ["Sc",   2.99,   44.96,  4.09000015, 4.46000004, 0,      0,      0,      0,      0],
   ["Ti",   4.54,   47.87,  4.51000023, 4.9310023,  0,      0,      0,      0,      0],
   ["V",    6.11,   50.94,  4.95200014, 5.42700005, 0,      0,      0,      0,      0],
   ["Cr",   7.15,   52.00,  5.41400003, 5.9460001,  0,      0,      0,      0,      0],
   ["Mn",   7.44,   54.94,  5.89799976, 6.48999977, 0,      0,      0,      0,      0],
   ["Fe",   7.87,   55.85,  6.40299988, 7.05700016, 0,      0,      0,      0,      0],
   ["Co",   8.86,   58.93,  6.92999983, 7.64900017, 28.03,  160.00, 99.31,  320.2,  248.5],
   ["Ni",   8.91,   58.69,  7.47700024, 8.26399994, 0,      0,      0,      0,      0],
   ["Cu",   8.93,   63.55,  8.04699993, 8.90400028, 33.80,  189.3,  118.7,  51.71,  39.18],
   ["Zn",   7.13,   65.38,  8.63799953, 9.571001,   0,      0,      0,      0,      0],
   ["Ga",   5.91,   69.72,  9.2510004,  10.2629995, 0,      0,      0,      0,      0],
   ["Ge",   5.32,   72.64,  9.88500023, 10.9809999, 0,      0,      0,      0,      0],
   ["As",   5.78,   74.92,  10.5430002, 11.7250004, 0,      0,      0,      0,      0],
   ["Se",   4.81,   78.96,  11.2209997, 12.4949999, 0,      0,      0,      0,      0],
   ["Br",   3.12,   79.90,  11.9230003, 13.29,      0,      0,      0,      0,      0],
   ["Kr",   0.004,  83.80,  12.6479998, 14.1120005, 0,      0,      0,      0,      0],
   ["Rb",   1.53,   85.47,  13.3940001, 14.96,      0,      0,      0,      0,      0],
   ["Sr",   2.64,   87.62,  14.1639996, 15.8339996, 0,      0,      0,      0,      0],
   ["Y",    4.47,   88.91,  14.9569998, 16.7360001, 0,      0,      0,      0,      0],
   ["Zr",   6.51,   91.22,  15.7740002, 17.6660004, 0,      0,      0,      0,      0],
   ["Nb",   8.57,   92.91,  16.6140003, 18.6210003, 0,      0,      0,      0,      0],
   ["Mo",   10.22,  95.94,  17.4780006, 19.6070004, 0,      0,      0,      0,      0],
   ["Tc",   11.50,  98.00,  18.4099998, 20.5849991, 0,      0,      0,      0,      0],
   ["Ru",   12.37,  101.07, 19.277999,  21.6550007, 0,      0,      0,      0,      0],
   ["Rh",   12.41,  102.91, 20.2140007, 22.7210007, 0,      0,      0,      0,      0],
   ["Pd",   12.02,  106.92, 21.1749992, 23.816,     0,      0,      0,      0,      0],
   ["Ag",   10.50,  107.87, 22.1620007, 24.9419994, 18.36,  103.1,  63.67,  213.0,  162.5],
   ["Cd",   8.69,   112.41, 23.1720009, 26.093,     0,      0,      0,      0,      0],
   ["In",   7.31,   114.82, 24.2070007, 27.2740002, 0,      0,      0,      0,      0],
   ["Sn",   7.29,   118.71, 25.2700005, 28.4829998, 0,      0,      0,      0,      0],

# FROM HERE ONLY L-LINES EMISSION ARE SET FOR THE ELEMENTS #   
   
   ["Sb",   6.69,   121.76, 3.60500002, 3.84299994, 0,      0,      0,      0,      0],
   ["Te",   6.23,   127.60, 3.76900005, 4.02899981, 0,      0,      0,      0,      0],
   ["I",    4.93,   126.90, 3.93700004, 4.21999979, 0,      0,      0,      0,      0],
   ["Xe",   0.006,  131.29, 4.11100006, 4.42199993, 0,      0,      0,      0,      0],
   ["Cs",   1.87,   132.91, 4.28599977, 4.61999989, 0,      0,      0,      0,      0],
   ["Ba",   3.59,   137.33, 4.46700001, 4.82800007, 0,      0,      0,      0,      0],
   ["La",   6.15,   138.91, 4.65100002, 5.04300022, 0,      0,      0,      0,      0],
   ["Ce",   6.77,   140.12, 4.84000015, 5.26200008, 0,      0,      0,      0,      0],
   ["Pr",   6.77,   140.91, 5.03399992, 5.48899984, 0,      0,      0,      0,      0],
   ["Nd",   7.01,   144.24, 5.43100023, 5.95599985, 0,      0,      0,      0,      0],
   ["Pm",   7.26,   145.00, 5.432,      5.961,      0,      0,      0,      0,      0],
   ["Sm",   7.52,   150.36, 5.633,      6.201,      0,      0,      0,      0,      0],
   ["Eu",   5.24,   151.96, 6.05900002, 6.71400023, 0,      0,      0,      0,      0],
   ["Gd",   7.90,   157.25, 6.2750001,  6.97900009, 0,      0,      0,      0,      0],
   ["Tb",   8.23,   158.93, 6.49499989, 7.24900007, 0,      0,      0,      0,      0],
   ["Dy",   8.55,   162.50, 6.71999979, 7.52799988, 0,      0,      0,      0,      0],
   ["Ho",   8.80,   164.93, 6.720,      7.526,      0,      0,      0,      0,      0],
   ["Er",   9.07,   167.26, 6.949,      7.811,      0,      0,      0,      0,      0],
   ["Tm",   9.32,   168.93, 7.180,      8.102,      0,      0,      0,      0,      0],
   ["Yb",   6.97,   173.04, 7.416,      8.402,      0,      0,      0,      0,      0],
   ["Lu",   9.84,   174.47, 7.655,      8.710,      0,      0,      0,      0,      0], 
   ["Hf",   13.31,  178.49, 7.899,      9.023,      0,      0,      0,      0,      0],
   ["Ta",   16.65,  180.95, 8.146,      9.343,      0,      0,      0,      0,      0],
   ["W",    19.25,  183.84, 8.398,      9.672,      0,      0,      0,      0,      0],
   ["Re",   21.02,  186.21, 8.652,      10.010,     0,      0,      0,      0,      0],
   ["Os",   22.61,  190.23, 8.911,      10.354,     0,      0,      0,      0,      0],
   ["Ir",   22.65,  192.22, 9.175,      10.708,     0,      0,      0,      0,      0],
   ["Pt",   21.46,  195.08, 9.442,      11.071,     0,      0,      0,      0,      0],
   ["Au",   19.28,  196.97, 9.71100044, 11.4390001, 78.81,  103.1,  160.8,  204.1,  159.2],
   ["Hg",   13.53,  200.59, 9.98700047, 11.823,     0,      0,      0,      0,      0],
   ["Tl",   11.85,  204.37, 10.2659998, 12.21,      0,      0,      0,      0,      0],
   ["Pb",   11.34,  207.20, 10.5489998, 12.614,     86.37,  114.1,  72.75,  225.3,  174.7],
   ["Bi",   9.81,   208.98, 10.8360004, 13.0209999, 0,      0,      0,      0,      0],
   ["Po",   9.32,   209.00, 11.131,     13.446,     0,      0,      0,      0,      0],
   ["At",   7.00,   210.00, 11.427,     13.876,     0,      0,      0,      0,      0],
   ["Rn",   0.01,   222.00, 11.727,     14.315,     0,      0,      0,      0,      0],
   ["Fr",   1.87,   223.00, 12.031,     14.771,     0,      0,      0,      0,      0],
   ["Ra",   5.50,   226.00, 12.339,     15.236,     0,      0,      0,      0,      0],
   ["Ac",   10.07,  227.00, 12.652,     15.713,     0,      0,      0,      0,      0],
   ["Th",   11.72,  232.04, 12.968,     16.202,     0,      0,      0,      0,      0],
   ["Pa",   15.37,  231.04, 13.291,     16.702,     0,      0,      0,      0,      0],
   ["U",    18.95,  238.03, 13.614,     17.220,     0,      0,      0,      0,      0],
   ["Np",   20.45,  237.00, 13.946,     17.751,     0,      0,      0,      0,      0],
   ["Pu",   19.84,  244.00, 14.282,     18.296,     0,      0,      0,      0,      0],
   ["Am",   13.69,  243.00, 14.620,     18.856,     0,      0,      0,      0,      0],
   ["Cm",   13.51,  247.00, 0,  0,  0,  0,  0,  0,  0],
   ["Bk",   14.79,  247.00, 0,  0,  0,  0,  0,  0,  0],
   ["Cf",   15.10,  251.00, 0,  0,  0,  0,  0,  0,  0],
   ["Es",   13.5,   252.00, 0,  0,  0,  0,  0,  0,  0],
   ["Fm",   0,      257.00, 0,  0,  0,  0,  0,  0,  0],
   ["Md",   0,      258.00, 0,  0,  0,  0,  0,  0,  0],
   ["No",   0,      259.00, 0,  0,  0,  0,  0,  0,  0],
   ["Lr",   0,      262.00, 0,  0,  0,  0,  0,  0,  0],
   ["Rf",   0,      0,      0,  0,  0,  0,  0,  0,  0],
   ["Db",   0,      0,      0,  0,  0,  0,  0,  0,  0],
   ["Sg",   0,      0,      0,  0,  0,  0,  0,  0,  0],
   ["Bh",   0,      0,      0,  0,  0,  0,  0,  0,  0],
   ["Hs",   0,      0,      0,  0,  0,  0,  0,  0,  0],
   ["Mt",   0,      0,      0,  0,  0,  0,  0,  0,  0],
]

ElementList = [index[0] for index in ElementsInfo]
banlist = []
for i in range(len(ElementsInfo)):
    if i < 10: banlist.append(ElementsInfo[i][0])

def SetPeakLines():
    ConfigPeakLines = {'K':['K','Ka','Kb'],'L':['L','L1','L2','L3']}
    ConfigLines = []
    elt = 0
    L = False
    while elt in range(len(ElementList)):
        while ElementList[elt] != 'Mt': 
            if ElementList[elt] == 'Xe': L = True
            if L == True:
                while ElementList[elt] != 'Mt':
                    ConfigLines.append(ConfigPeakLines['L'])
                    elt += 1
                ConfigLines.append(ConfigPeakLines['L'])
                break 
            ConfigLines.append(ConfigPeakLines['K'])
            elt += 1
        break
    PeakConfigDict = {"{0}".format(ElementList[element]):ConfigLines[element] for element in range(len(ElementList))}
    return PeakConfigDict

def set_energies_from_xlib():
    cutoff = 0.25
    cutoff_K = 0.05
    EnergyList, EnergyListKb, plottables_, plottables_dict = [],[],[],{}
    L = False
    elt = 0
    while elt in range(len(ElementList)):
        while ElementList[elt] != 'Mt': 
            if ElementList[elt] == 'Xe': L = True
            if L == True:
                while ElementList[elt] != 'Mt':
                    try: 
                        EnergyList.append(xlib.LineEnergy(elt,2))
                        EnergyListKb.append(xlib.LineEnergy(elt,3))
                        if xlib.RadRate(elt,xlib.LA1_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LA1_LINE))
                        if xlib.RadRate(elt,xlib.LA2_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LA2_LINE))
                        if xlib.RadRate(elt,xlib.LB1_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LB1_LINE))
                        if xlib.RadRate(elt,xlib.LB2_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LB2_LINE))
                        if xlib.RadRate(elt,xlib.LB3_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LB3_LINE))
                        if xlib.RadRate(elt,xlib.LB4_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LB4_LINE))
                        if xlib.RadRate(elt,xlib.LB5_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LB5_LINE))
                        if xlib.RadRate(elt,xlib.LB6_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LB6_LINE))
                        if xlib.RadRate(elt,xlib.LB7_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LB7_LINE))
                        if xlib.RadRate(elt,xlib.LB9_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LB9_LINE))
                        if xlib.RadRate(elt,xlib.LB10_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LB10_LINE))
                        if xlib.RadRate(elt,xlib.LB15_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LB15_LINE))
                        if xlib.RadRate(elt,xlib.LB17_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LB17_LINE))
                        if xlib.RadRate(elt,xlib.LG1_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LG1_LINE))
                        if xlib.RadRate(elt,xlib.LG2_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LG2_LINE))
                        if xlib.RadRate(elt,xlib.LG3_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LG3_LINE))
                        if xlib.RadRate(elt,xlib.LG4_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LG4_LINE))
                        if xlib.RadRate(elt,xlib.LG5_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LG5_LINE))
                        if xlib.RadRate(elt,xlib.LG6_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LG6_LINE))
                        if xlib.RadRate(elt,xlib.LG8_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.LG8_LINE))
                        if xlib.RadRate(elt,xlib.MA1_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.MA1_LINE))
                        if xlib.RadRate(elt,xlib.MA2_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.MA2_LINE))
                        if xlib.RadRate(elt,xlib.MB_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.MB_LINE))
                        if xlib.RadRate(elt,xlib.MG_LINE) > cutoff:
                            plottables_.append(xlib.LineEnergy(elt,xlib.MG_LINE))
                        plottables_dict[ElementList[elt]] = plottables_
                        plottables_ = []
                        elt += 1
                    except: pass
                break 
            try:
                EnergyList.append(xlib.LineEnergy(elt,0))
                EnergyListKb.append(xlib.LineEnergy(elt,1))
                if xlib.RadRate(elt,xlib.KA1_LINE) > cutoff_K:
                    plottables_.append(xlib.LineEnergy(elt,xlib.KA1_LINE))
                if xlib.RadRate(elt,xlib.KA2_LINE) > cutoff_K:
                    plottables_.append(xlib.LineEnergy(elt,xlib.KA2_LINE))
                if xlib.RadRate(elt,xlib.KA3_LINE) > cutoff_K:
                    plottables_.append(xlib.LineEnergy(elt,xlib.KA3_LINE))
                if xlib.RadRate(elt,xlib.KB1_LINE) > cutoff_K:
                    plottables_.append(xlib.LineEnergy(elt,xlib.KB1_LINE))
                if xlib.RadRate(elt,xlib.KB2_LINE) > cutoff_K:
                    plottables_.append(xlib.LineEnergy(elt,xlib.KB2_LINE))
                if xlib.RadRate(elt,xlib.KB3_LINE) > cutoff_K:
                    plottables_.append(xlib.LineEnergy(elt,xlib.KB3_LINE))
                if xlib.RadRate(elt,xlib.KB4_LINE) > cutoff_K:
                    plottables_.append(xlib.LineEnergy(elt,xlib.KB4_LINE))
                if xlib.RadRate(elt,xlib.KB5_LINE) > cutoff_K:
                    plottables_.append(xlib.LineEnergy(elt,xlib.KB5_LINE))
                plottables_dict[ElementList[elt]] = plottables_
                plottables_ = []
                elt += 1
            except: pass
        break
    for element in plottables_dict:
        for emission in plottables_dict[element]:
            if emission == 0: plottables_dict[element] = None
        if plottables_dict[element] == []: plottables_dict[element] = None
    return EnergyList, EnergyListKb, plottables_dict

def set_densities_from_xlib():
    DensityDict = {}
    for i in range(len(ElementList)):
        loc_element = ElementsInfo[i][0]
        try: 
            if ElementList.index(loc_element)+1 < 95: 
                DensityDict["{0}".format(loc_element)] = xlib.ElementDensity(ElementList.index(loc_element))
            else:
                DensityDict["{0}".format(loc_element)] = 0.0 
        except: DensityDict["{0}".format(loc_element)] = np.nan
    return DensityDict

def which_macro(element):
    if element == "custom": return "" 
    idx = ElementList.index(element)
    if idx >= 54: return "L"
    else: return "K"

# Lists below uses the definition written manually in this file
if Constants.USEXLIB == False:
    DensityDict = {index[0]:index[1] for index in ElementsInfo}
    Energies = [index[3] for index in ElementsInfo]
    kbEnergies = [index[4] for index in ElementsInfo]
    plottables_dict = {}
    for elt in ElementList:
        plottables_dict[elt] = [Energies[ElementList.index(elt)], 
            kbEnergies[ElementList.index(elt)]]

# Energy lists where updated to use xraylib values:
if Constants.USEXLIB == True: 
    Energies, kbEnergies, plottables_dict = set_energies_from_xlib()
    DensityDict = set_densities_from_xlib()

AtomWeight = {"{0}".format(index[0]):index[2] for index in ElementsInfo}
Element_No = {"{0}".format(index[0]):ElementList.index(index[0]) for index in ElementsInfo}
ElementColors = {}
try: 
    f = open(os.path.join(os.getcwd(),"images","colours.txt"),"r")
    for element in ElementList:
        line = f.readline()
        line = line.replace("\r","")
        line = line.replace("\n","")
        ElementColors[element] = line.split("\t")[-1]
    f.close()
except: 
    ElementColors = {element:"#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for element in ElementList}

if __name__ == "__main__":
    """
    import os
    print(DensityDict)
    print(DensityDict["Au"])
    print(ElementColors)
    f_colour = open(os.path.join(os.getcwd(),"images","colours.txt"),"w")
    for element in ElementColors:
        f_colour.write("{}\t{}\r".format(element,ElementColors[element]))
    f_colour.close()
    """
