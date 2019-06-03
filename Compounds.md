## Compounds.py usage

This module creates virtual compounds either from a database or from user input.
The virtual compound will have a name, density, mass, attenuation factors and its origin.

### Initializing a compound



### Attributes

* **.name**
  returns a string containing the name of the compound (if given during its initalization)
* **.mass**
  returns a float value with the atomic mass of the compound
* **.chem**
  returns a dictionary with the total atomic mass of each constituent chemical element.
  ```
  water = compound()
  water.setcompound('water')
  print(water.chem)
  ```
  > {'H':2.02, 'O':16}
* **.density**
  return a float value with the total density of the compound
* **.weight**
  returns a dictionary with the weight fraction of each constituent chemical element in a similar way of .chem
* **.origin**
  returns a string with the origin of the compound. Values are: 'by_weight', 'by_atom', 'by_mixing' or 'from_database'
* **.tot_att** and **.lin_att**
  each will return a tuple with the attenuation coefficients of a given element. .tot_att will return the total attenuation while .lin_att will return the linear attenuation (the same as .tot_att divided by the compound's density).
