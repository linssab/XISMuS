#################################################################
#                                                               #
#          COMPOUND LIST                                        #
#                        version: 1.2                           #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import EnergyLib
import logging

CompoundList = {
        'Air'           :{'N':0.66,'O':0.34},
        'CoBlue'        :{'Co':0.3331,'Al':0.3050,'O':0.3619},
        'OceanBlue'     :{'H':0.0413,'C':0.2925,'O':0.2674,'Al':0.1907,'Co':0.2082},
        'Co'            :{'Co':1},
        'PbWhite'       :{'Pb':0.8014,'O':0.1650,'C':0.031,'H':0.0026},
        'PbWhitePrimer' :{'Pb':0.6612,'O':0.1722,'C':0.1328,'H':0.0163,'Ca':0.0174}, \
                # After Favaro, 2010 and Gonzalez, 2015
        'AuSheet'       :{'Au':0.917,'Ag':0.083},
        'LinOil'        :{'C':0.78,'O':0.11,'H':0.11},
        'Tumbaga'       :{'Au':0.12,'Ag':0.16,'Cu':0.72}
        }

def linattenuation(element,KaKb):
    if KaKb == 'E0':
        coefficients = EnergyLib.muE0[element]
        mu1 = coefficients*EnergyLib.density[element]
        mu2 = 0
    elif KaKb == 'Pb': 
        coefficients = EnergyLib.muPb[element]
        mu1 = coefficients[0]
        mu2 = coefficients[1]
    elif KaKb == 'Cu':
        coefficients = EnergyLib.muCu[element]
        mu1 = coefficients[0]
        mu2 = coefficients[1]
    else:
        print("Impossible to create heightmap for {0}!".format(KaKb))
        logging.warning("{0} is not a valid element for ratio calculation!\n\t\t\
                Try again using a different element such as Au, Pb or Zn.".format(KaKb))
        raise ValueError
    return mu1,mu2

def density(compound):
    compound_density = 0
    for element in CompoundList[compound]:
        compound_density += EnergyLib.density[element]*CompoundList[compound][element]
    return compound_density

#############################################
#   coefficients parameters are: the name   #
#   of the compound and which energy it is  #
#   attenuating                             #
#############################################

def coefficients(compound,KaKb):
    comp_ele_list = [*CompoundList[compound]]
    mu1weighted, mu2weighted = 0, 0
    for element in comp_ele_list:
        coeffs = linattenuation(element,KaKb)
        mu1 = coeffs[0]
        mu2 = coeffs[1]
        mu1weighted += mu1*CompoundList[compound][element]
        mu2weighted += mu2*CompoundList[compound][element]
    mu1weighted = mu1weighted*density(compound)
    mu2weighted = mu2weighted*density(compound)
    return mu1weighted, mu2weighted

def mixture(rate,KaKb='Pb',*args):
    stratalist = args
    if len(stratalist) == len(rate):
        print("OK! Every layer has a proportion!")
    else:
        print("Missing proportion correspondence!")
    mu1 = 0
    mu2 = 0
    count = 0
    for compound in stratalist:
        count = count
        comp_rate = rate[count]/sum(rate)
        print("compound {0}, rate {1}".format(compound,comp_rate))
        coeff = coefficients(compound,KaKb)
        mu1compound = coeff[0]
        mu2compound = coeff[1]
        mu1 += mu1compound*comp_rate
        mu2 += mu2compound*comp_rate
        count = count + 1
    return mu1,mu2

#rho_tumbaga = density('Tumbaga')
#print(rho_tumbaga)
#print(coefficients('AuSheet','E0'))

def overlap_element(compound):
    # most abundant element (mae) #
    mae = None
    mae_concentration = 0
    for element in CompoundList[compound]:
        if element not in EnergyLib.banlist:
            if CompoundList[compound][element] > mae_concentration:
                mae = element
                mae_concentration = CompoundList[compound][element]
    return mae

