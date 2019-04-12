#################################################################
#                                                               #
#          COMPOUND LIST                                        #
#                        version: 1.0                           #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import EnergyLib

CompoundList = {
        'CoBlue'    :{'Co':0.3331,'Al':0.3050,'O':0.3619},
        'PbWhite'   :{'Pb':0.8014,'O':0.1650,'C':0.031,'H':0.0026},
        'AuSheet'   :{'Au':0.75,'Ag':0.25}
        }

def linattenuation(element,energy):
    coefficients = EnergyLib.muPb[element]
    mu1 = coefficients[0]*EnergyLib.density[element]
    mu2 = coefficients[1]*EnergyLib.density[element]
    return mu1,mu2

def coefficients(compound):
    comp_ele_list = [*CompoundList[compound]]
    mu1weighted, mu2weighted = 0, 0
    for element in comp_ele_list:
        coeffs = linattenuation(element,'Pb')
        mu1 = coeffs[0]
        mu2 = coeffs[1]
        mu1weighted += mu1*CompoundList[compound][element]
        mu2weighted += mu2*CompoundList[compound][element]
    return mu1weighted, mu2weighted

