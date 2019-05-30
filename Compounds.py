#################################################################
#                                                               #
#          CHEMEX                                               #
#                        version: 2.0                           #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
#################################################################

import numpy as np
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

class compound:
    
    def __init__(__self__):
        __self__.chem = {}
        __self__.mass = 0
        __self__.density = 0
        __self__.weight = {}
        __self__.name = 'new_compound'
    
    def set_compound(__self__,*args,ctype=None,mode='by_atom'):
        if ctype == 'custom' and mode == 'by_atom':
            __self__.create_compound(args[0][0],args[0][1])
            __self__.origin = 'by_atom'
        elif ctype == 'custom' and mode == 'by_weight':
            __self__.create_compound_by_weight(args[0][0],args[0][1])
        else:
            try: __self__.set_from_database(args[0])
            except: raise ValueError("{} not recognized".format(args[0]))
        pass

    def create_compound(__self__,atoms,elements):
        __self__.chem = {"{0}".format(elements[i]):(EnergyLib.AtomWeight[elements[i]]*atoms[i])\
                for i in range(len(atoms))}
        mass = __self__.total_mass()
        __self__.weightpercent()
        __self__.give_density()
    
    def create_compound_by_weight(__self__,ratios,elements):
        if len(ratios) == len(elements):
            __self__.weight = {"{0}".format(elements[i]):ratios[i] for i in range(len(ratios))}
            for key in __self__.weight:
                if __self__.weight[key] > 1:
                    raise ValueError("Sum of weights larger than 100%! {}".format(ratios))
                    break
            __self__.give_density()
            __self__.mass = None
            __self__.chem = None
            __self__.origin = 'by_weight'
        else: raise ValueError('{0} and {1} have different lenghts'.format(ratios,elements))

    def set_from_database(__self__,name_of_compound):
        __self__.chem = CompoundList[name_of_compound]
        mass = __self__.total_mass()
        __self__.weightpercent()
        __self__.give_density()
        __self__.origin = 'from_database'
    
    def weightpercent(__self__):
        for element in __self__.chem:
            __self__.weight[element] = __self__.chem[element]/__self__.mass 
         
    def total_mass(__self__):
        total_mass = 0
        for element in __self__.chem:
            total_mass += __self__.chem[element]
        __self__.mass = total_mass
        return total_mass
    
    def give_density(__self__):
        try:
            for element in __self__.weight:
                __self__.density += __self__.weight[element]*EnergyLib.DensityList[element]
        except:
            raise ValueError("{} has no property weight!".format(__self__))

    def mix(__self__,proportion,compounds):
        sum_of_ratios = sum(proportion)
        if sum_of_ratios > 1:
            for index in range (len(proportion)): 
                proportion[index] = proportion[index]/sum_of_ratios
        mixture = compound()
        compounds.append(__self__)
        for i in range(len(proportion)): 
            for key in compounds[i].weight:
                mixture.weight[key] = 0
                mixture.weight[key] = compounds[i].weight[key]*proportion[i]
        mixture.give_density()
        mixture.mass = None
        mixture.chem = None
        mixture.origin = \
                {'Mode':'by_mixing','Proportion':proportion,'Origin':compounds}
        return mixture

    def set_attenuation(__self__,energy):
        mu1_w ,mu2_w = 0,0
        for element in __self__.weight:
            total_att = linattenuation(element,energy)
            mu1,mu2 = total_att[0],total_att[1]
            mu1_w += mu1*__self__.weight[element]
            mu2_w += mu2*__self__.weight[element]
        __self__.tot_att = (mu1_w,mu2_w) 
        __self__.lin_att = (__self__.density * mu1_w , __self__.density * mu2_w)
    
    def give_name(__self__,a_string):
        __self__.name = a_string

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
        compound_density += EnergyLib.DensityList[element]*CompoundList[compound][element]
    return compound_density

#############################################
#   coefficients parameters are: the name   #
#   of the compound and which energy it is  #
#   attenuating                             #
#############################################

def coefficients(a_compound,KaKb):
    comp_ele_list = [*CompoundList[a_compound]]
    mu1weighted, mu2weighted = 0, 0
    for element in comp_ele_list:
        coeffs = linattenuation(element,KaKb)
        mu1 = coeffs[0]
        mu2 = coeffs[1]
        mu1weighted += mu1*CompoundList[a_compound][element]
        mu2weighted += mu2*CompoundList[a_compound][element]
    mu1weighted = mu1weighted*density(a_compound)
    mu2weighted = mu2weighted*density(a_compound)
    return mu1weighted, mu2weighted

if __name__=="__main__":
    
    rho_coblue = density('CoBlue')
    print(rho_coblue)
    print(coefficients('CoBlue','Pb'))

    water_chem = [[2,1],['H','O']]
    coblue_perc = [[0.3331,0.3050,0.3619],['Co','Al','O']]

    water = compound()
    water.set_compound(water_chem,ctype='custom')
    coblue = compound()
    coblue.set_compound(coblue_perc,ctype='custom',mode='by_weight')

    linoil = compound()
    linoil.set_compound('LinOil')

    print("Water DATA:\nWeight percentage of atoms: {0}\nTotal mass: {1}\nElements mass: {2}\nDensity: {3}\n".format(water.weight,water.mass,water.chem,water.density))

    print("Cobalt Blue DATA:\nWeight percentage of atoms: {0}\nTotal mass: {1}\nElements mass: {2}\nDensity: {3}\n".format(coblue.weight,coblue.mass,coblue.chem,coblue.density))

    mixture = coblue.mix([10,2,4],[linoil,water])

    print("Mixture DATA:\nWeight percentage of atoms: {0}\nTotal mass: {1}\nElements mass: {2}\nDensity: {3}\n".format(mixture.weight,mixture.mass,mixture.chem,mixture.density))
    print(coblue.origin)
    print(water.origin)
    print(linoil.origin)

    mixture.set_attenuation('Pb')
    print(mixture.tot_att)
    print(mixture.lin_att)

