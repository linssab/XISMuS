#################################################################
#                                                               #
#          CHEMEX                                               #
#                        version: 2.0                           #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#                                                               #
#################################################################

import numpy as np
import logging
logging.debug("Importing module Compounds.py...")
import EnergyLib
try: import xraylib as xlib
except: print("Failed to load xraylib module!")

CompoundList = {
        'Azurite'       :{'Cu':3,'C':2,'O':8,'H':2},
        'AuSheet'       :{'Au':9,'Ag':1},
        'CoBlue'        :{'Co':1,'Al':2,'O':4},
        'Cuprite'       :{'Cu':2,'O':1},
        'Ethanol'       :{'C':2,'H':6,'O':1},
        'PbWhite'       :{'Pb':3,'O':4,'C':1,'H':2},
        'PbCarbonate'   :{'Pb':1,'C':1,'O':3},
        'PureGold'      :{'Au':100},
        'Tenorite'      :{'Cu':1,'O':1},
        'Vermilion'     :{'Hg':1,'S':1},
        'Water'         :{'H':2,'O':1},
        'ZnWhite'       :{'Zn':1,'O':1},
        }

WeightList = {

        'AuSheet'       :{'Au':0.917,'Ag':0.083},
        'Tumbaga'       :{'Au':0.12,'Ag':0.16,'Cu':0.72},
        'LinOil'        :{'C':0.78,'O':0.11,'H':0.11},
        'OceanBlue'     :{'H':0.0413,'C':0.2925,'O':0.2674,'Al':0.1907,'Co':0.2082},
        'PbWhitePrimer' :{'Pb':0.6612,'O':0.1722,'C':0.1328,'H':0.0163,'Ca':0.0174}, \
                # After Favaro, 2010 and Gonzalez, 2015
        }

class compound:
    
    def __init__(__self__):
        __self__.chem = {}
        __self__.mass = 0
        __self__.density = 0
        __self__.weight = {}
        __self__.name = 'new_compound'
        __self__.identity = np.nan
    
    def set_compound(__self__,*args,ctype=None,mode='by_atom',name='new_compound'):
        if ctype == 'custom' and mode == 'by_atom':
            for atom in range(len(args[0])):
                if args[0][atom] < 1: raise ValueError("Can't compute fraction of atom!")
            __self__.create_compound(args[0],args[1])
            __self__.origin = 'by_atom'
        elif ctype == 'custom' and mode == 'by_weight':
            if sum(args[0]) > 1: raise ValueError("Sum of weights exceeds 1!")
            __self__.create_compound_by_weight(args[0],args[1])
        else:
            try: __self__.set_from_database(args[0])
            except: raise ValueError("{} not recognized".format(args[0]))
        pass
        if ctype == None: name = args[0]
        __self__.give_name(name)

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
        elements = [element for element in CompoundList[name_of_compound]]
        atoms = [CompoundList[name_of_compound][atom] for atom in elements]
        __self__.chem = {"{0}".format(elements[i]):(EnergyLib.AtomWeight[elements[i]]*atoms[i])\
                for i in range(len(atoms))}
        mass = __self__.total_mass()
        __self__.weightpercent()
        __self__.give_density()
        __self__.origin = 'from_database'
        __self__.name = name_of_compound
    
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
                __self__.density += __self__.weight[element]*EnergyLib.DensityDict[element]
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
        name_list = []
        for ingredient in compounds:
            name_list.append(ingredient.name)
        mixture.origin = \
                {'Mode':'by_mixing','Proportion':proportion,'Origin':name_list}
        return mixture

    def set_attenuation(__self__,energy):
        mu1_w ,mu2_w = 0,0
        if type(energy) == int:
            for element in __self__.weight:
                ele_no = EnergyLib.Element_No[element]
                mu1 = xlib.CS_Total(ele_no,energy)
                mu2 = 0
                mu1_w += mu1*__self__.weight[element]
                mu2_w += mu2*__self__.weight[element]
        else:
            for element in __self__.weight:
                attenuated_no = EnergyLib.Element_No[energy]
                ele_no = EnergyLib.Element_No[element]
                attenergy_a = EnergyLib.Energies[attenuated_no]
                attenergy_b = EnergyLib.kbEnergies[attenuated_no]
                #total_att = linattenuation(element,energy)
                mu1,mu2 = xlib.CS_Total(ele_no,attenergy_a),xlib.CS_Total(ele_no,attenergy_b)
                #mu1,mu2 = total_att[0],total_att[1]
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

def split_energies(element):
    energy_a = EnergyLib.Energies[EnergyLib.Element_No[element]]
    energy_b = EnergyLib.kbEnergies[EnergyLib.Εlement_No[element]]
    return(energy_a,energy_b)

def density(compound):
    compound_density = 0
    for element in CompoundList[compound]:
        compound_density += EnergyLib.DensityDict[element]*CompoundList[compound][element]
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
    
    water = compound()
    water.set_compound([2,1],['H','O'],ctype='custom')
    
    coblue = compound()
    coblue.set_compound('CoBlue')

    linoil = compound()
    linoil.set_compound([0.78,0.11,0.11],['C','O','H'],ctype='custom',mode='by_weight',name='Linoil')

    print("Water DATA:\nWeight percentage of atoms: {0}\nTotal mass: {1}\nElements mass: {2}\nDensity: {3}\n".format(water.weight,water.mass,water.chem,water.density))

    print("Cobalt Blue DATA:\nWeight percentage of atoms: {0}\nTotal mass: {1}\nElements mass: {2}\nDensity: {3}\n".format(coblue.weight,coblue.mass,coblue.chem,coblue.density))

    mixture = linoil.mix([2,10],[coblue])

    print("Mixture DATA:\nWeight percentage of atoms: {0}\nTotal mass: {1}\nElements mass: {2}\nDensity: {3}\n".format(mixture.weight,mixture.mass,mixture.chem,mixture.density))
    print(water.origin)
    print(coblue.origin)
    print(linoil.origin)
    print(mixture.origin)
    
    ############################################

    gold = compound()
    gold.set_compound('PureGold')
    gold.set_attenuation(20)

    print(gold.tot_att)
    
