"""
Copyright (c) 2022 Sergio Augusto Barcellos Lins & Giovanni Ettore Gigante

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

#############
# tcl/Tk ####
#############
from tkinter import *
from tkinter import ttk
#############

#############
# utilities #
#############
import os
from tkinter import messagebox
#############

#############
# Internal ##
#############
from Elements import Compounds
from Elements import ElementList
#############

MATERIAL = Compounds.compound()

class AlchemyLab:
    def __init__(__self__, parent):
        __self__.parent = parent
        __self__.master = Toplevel(master = parent.master)
        __self__.master.title("Alchemy lab")
        __self__.master.iconbitmap(os.path.join(os.getcwd(),"images","icons","adv.ico"))
        __self__.master.attributes("-alpha", 0.0)
        __self__.master.resizable(False, False)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.compoundsNumber = 1
        __self__.material = Compounds.compound()
        __self__.compoundsInMaterial = []

        x, y = 640, 480 
        __self__.mainFrame = ttk.Frame(__self__.master, height=x, width=y)
        __self__.mainFrame.grid()

        __self__.build_widgets()
        __self__.master.after( 200, __self__.master.attributes, "-alpha", 1.0)
        __self__.master.focus_force()
        __self__.master.grab_set()

    def kill(__self__, e=""):
        __self__.master.destroy()
        MATERIAL.reset()
        __self__.parent.master.after( 50, delattr(__self__.parent, "AlchemyLab") )
        __self__.parent.master.focus_set()
        __self__.parent.display_material()
        del __self__
        return

    def save(__self__):
        MATERIAL.create_compound_by_weight( 
            [i[1] for i in __self__.material.weight.items()],
            [i[0] for i in __self__.material.weight.items()] )
        __self__.master.destroy()
        __self__.parent.master.after( 50, delattr(__self__.parent, "AlchemyLab") )
        __self__.parent.master.focus_set()
        __self__.parent.display_material()
        del __self__
        return
    
    def build_widgets(__self__):
        w = 7
        height = 400
        padding = 10
        __self__.leftPanel = ttk.LabelFrame(__self__.mainFrame, text="Material", padding=padding)
        __self__.materialFrame = Frame(__self__.leftPanel, bd=1, bg="black", height=height)
        __self__.materialLabels = ttk.Label(__self__.materialFrame, text="Compound name | %")
        __self__.materialName = Listbox(__self__.materialFrame, bd=0, highlightthickness=0)
        __self__.removeCompound = ttk.Button(__self__.leftPanel, text="Remove compound", command=__self__.remove_from_material)

        __self__.compoundName = StringVar()
        __self__.compoundName.set(f"Compound {__self__.compoundsNumber}")
        __self__.compoundAssembleMode = StringVar()
        __self__.assembleModeView = StringVar()
        __self__.compoundAssembleMode.set("by_weight")
        __self__.assembleModeView.set("Weight percentage")
        __self__.quantity = DoubleVar()
        __self__.quantity.set(100.0)

        __self__.rightPanel = ttk.LabelFrame(__self__.mainFrame, padding=padding)
        __self__.databaseCompoundSelectorLabel = ttk.Label(__self__.rightPanel, text="Select a compound from compwizard:")
        __self__.databaseCompoundSelector = ttk.Combobox(__self__.rightPanel, values=[i for i in Compounds.ListDatabase().keys()])
        __self__.compoundFrame = ttk.LabelFrame(__self__.rightPanel, text="Compound", height=height, padding=int( padding / 2 ) )
        __self__.buttonsPanel = ttk.Frame(__self__.rightPanel)
        __self__.symbolsFrame = ttk.Frame(__self__.compoundFrame)
        __self__.compoundLabel1 = ttk.Label(__self__.compoundFrame, text="Element Symbol")
        __self__.compoundLabel2 = ttk.Label(__self__.compoundFrame, textvariable=__self__.assembleModeView)
        __self__.addSymbol = ttk.Button(__self__.compoundFrame, text="Add element", command=__self__.add_symbol)
        __self__.removeSymbol = ttk.Button(__self__.compoundFrame, text="Remove element", command=__self__.remove_symbol)
        __self__.compoundNameLabel = ttk.Label(__self__.compoundFrame, text="Compound name:")
        __self__.compoundNameEntry = ttk.Entry(__self__.compoundFrame, textvariable=__self__.compoundName)

        __self__.compoundMaterialPercentageLabel = ttk.Label(__self__.buttonsPanel, text="Percentage in material:")
        __self__.compoundMaterialPercentageEntry = ttk.Entry(__self__.buttonsPanel, textvariable=__self__.quantity)
        __self__.addCompoundToMaterial = ttk.Button(__self__.buttonsPanel, text="Add to material", command=__self__.add_to_material)
        __self__.buttonsSubPanel = ttk.Frame(__self__.buttonsPanel)
        __self__.exitButton = ttk.Button(__self__.buttonsSubPanel, text="Exit", command=__self__.kill, width=w)
        __self__.saveButton = ttk.Button(__self__.buttonsSubPanel, text="Save", command=__self__.save, width=w)
        __self__.changeAssembleMode = ttk.Button(__self__.compoundFrame, text="Switch make mode", command=__self__.switch_assemble_mode)

        __self__.leftPanel.grid(row=0, column=0, sticky="NSEW", pady=padding, padx=(padding, 0))
        __self__.rightPanel.grid(row=0, column=1, sticky="NSEW", padx=(0, padding), pady=padding)

        __self__.materialFrame.grid(row=0, sticky="NSEW")
        __self__.materialLabels.grid(row=0, sticky="EW")
        __self__.materialName.grid(row=1, sticky="NSEW")
        __self__.removeCompound.grid(row=1, sticky="EW", pady=(10,0))

        __self__.databaseCompoundSelectorLabel.grid(row=0, sticky="W")
        __self__.databaseCompoundSelector.grid(row=1, pady=(5,0), sticky="EW")

        __self__.compoundFrame.grid(row=2, pady=(10,15), sticky="NSEW")
    	#### Childs of compoundFrame
        __self__.addSymbol.grid(row=0, column=0, pady=(10,10), sticky="EW" )
        __self__.removeSymbol.grid(row=0, column=1, pady=(10,10), sticky="EW" )
        __self__.compoundLabel1.grid(row=1, column=0)
        __self__.compoundLabel2.grid(row=1, column=1)
        __self__.symbolsFrame.grid(row=2, columnspan=2, sticky="NSEW")
        ####

        __self__.compoundNameLabel.grid(row=3, column=0, sticky="E", pady=(5,0))
        __self__.compoundNameEntry.grid(row=3, column=1, sticky="E", pady=(5,0))
        __self__.changeAssembleMode.grid(row=4, column=0, sticky="W", pady=(5,0))

        __self__.buttonsPanel.grid(row=4, sticky="EW", pady=(20,0))
        __self__.buttonsSubPanel.grid(row=1, column=1, sticky="W", pady=(5,0))
        
        __self__.compoundMaterialPercentageLabel.grid(row=0, column=0)
        __self__.compoundMaterialPercentageEntry.grid(row=0, column=1)
        __self__.addCompoundToMaterial.grid(row=1, column=0, sticky="W", pady=(5,0))
        __self__.exitButton.grid(row=0, column=1)
        __self__.saveButton.grid(row=0, column=0)

        __self__.symbolsEntries = []
        __self__.valuesEntries = []
        __self__.elementsCount = 0
        elementsSymbols = ttk.Entry(__self__.symbolsFrame)
        elementsSymbols.grid(row=__self__.elementsCount, column=0)
        elementsPercentage = ttk.Entry(__self__.symbolsFrame)
        elementsPercentage.grid(row=__self__.elementsCount, column=1)
        __self__.symbolsEntries.append( elementsSymbols )
        __self__.valuesEntries.append( elementsPercentage )
        __self__.databaseCompoundSelector.bind("<<ComboboxSelected>>", __self__.fill_symbols)

        for i in range(4):
            __self__.add_symbol()
        return

    def fill_symbols(__self__, e=""):
        value = e.widget.get()
        if __self__.compoundAssembleMode.get() == "by_atom": __self__.switch_assemble_mode()
        comp = Compounds.compound()
        comp.set_compound(value)
        symbols = []
        values = []
        for symbol, value in comp.weight.items():
            symbols.append( symbol )
            values.append( value )

        if len( symbols ) > __self__.elementsCount + 1:
            while __self__.elementsCount + 1 < len( symbols ): __self__.add_symbol()
        else:
            while __self__.elementsCount + 1 > len( symbols ): __self__.remove_symbol()
        
        for symbol, value, symbolEntry, valueEntry in zip( symbols, values, __self__.symbolsEntries, __self__.valuesEntries ):
            symbolEntry.delete( 0, END )
            valueEntry.delete( 0, END )
            symbolEntry.insert( 0, symbol )
            valueEntry.insert( 0, f"{value * 100:.2f}%" )
        __self__.compoundName.set( comp.name )
        return

    def add_symbol(__self__):
        if __self__.elementsCount < 9:
            __self__.elementsCount += 1
            elementsSymbols = ttk.Entry(__self__.symbolsFrame)
            elementsSymbols.grid(row=__self__.elementsCount + 1, column=0)
            elementsPercentage = ttk.Entry(__self__.symbolsFrame)
            elementsPercentage.grid(row=__self__.elementsCount + 1, column=1)
            __self__.symbolsEntries.append( elementsSymbols )
            __self__.valuesEntries.append( elementsPercentage )
        else: 
            messagebox.showinfo("Uh-oh!","Maximum number of elements allowed is 10.")
        return

    def remove_symbol(__self__):
        if __self__.elementsCount > 0:
            __self__.elementsCount -= 1
            __self__.symbolsEntries[-1].destroy()
            __self__.valuesEntries[-1].destroy()
            __self__.symbolsEntries.pop(-1)
            __self__.valuesEntries.pop(-1)
        else: pass
        return

    def switch_assemble_mode(__self__, e=""):
        if __self__.compoundAssembleMode.get() == "by_weight":
            __self__.compoundAssembleMode.set("by_atom")
            __self__.assembleModeView.set("No. of atoms")
        else:
            __self__.compoundAssembleMode.set("by_weight")
            __self__.assembleModeView.set("Weight percentage")
        __self__.changeAssembleMode.update_idletasks()
        return

    def build_material(__self__, **kwargs):
        remake = False
        __self__.material = Compounds.compound()
        for arg in kwargs:
            if arg == "compound": compound = kwargs[arg]
            elif arg == "quantity": quantity = kwargs[arg]
            elif arg == "remake": remake = kwargs[arg]
        
        if not remake:
            __self__.compoundsInMaterial.append( [ compound, quantity ] )
            __self__.compoundsNumber = len( __self__.compoundsInMaterial ) + 1
            __self__.compoundName.set(f"Compound {__self__.compoundsNumber}")

        if __self__.compoundsInMaterial != []:
            __self__.material = Compounds.make_mixutre_of(
                [ i[1] for i in __self__.compoundsInMaterial ], 
                [ i[0] for i in __self__.compoundsInMaterial ] )
        
        MATERIAL.reset()
        MATERIAL.create_compound_by_weight( 
            [i[1] for i in __self__.material.weight.items()],
            [i[0] for i in __self__.material.weight.items()] )
        __self__.refresh_material_view()
        return

    def remove_from_material(__self__, e=""):
        try: selectedCompound = __self__.materialName.get( __self__.materialName.curselection() ).split(",")[0]
        except: return
        if selectedCompound == "": 
            return
        for compound in __self__.compoundsInMaterial:
            if compound[0].name == selectedCompound:
                idx = __self__.compoundsInMaterial.index( compound )
        __self__.compoundsInMaterial.pop( idx )
        __self__.materialName.delete( __self__.materialName.curselection() )

        __self__.build_material( remake=True )
        __self__.materialName.focus_set()
        return

    def add_to_material(__self__, e=""):
        userCompound = Compounds.compound()
        symbols, values = [], []

        for sym, val in zip( __self__.symbolsEntries, __self__.valuesEntries ):
            
            if sym.get() != "" and sym.get() not in ElementList: 
                messagebox.showerror("Error", f"{sym.get()} not a valid symbol!")
                return
            if val.get() != "" and not val.get().replace("%","").replace(".","",1).isdigit(): 
                messagebox.showerror("Error", f"{__self__.assembleModeView.get()} input for element {sym.get()} must be numerical!")
                return

            if sym.get() != "":
                values.append( float( val.get().replace("%","") ) )
                symbols.append( sym.get() )
        
        if symbols == [] or values == []: return

        if __self__.compoundAssembleMode.get() == "by_weight":
            for i in range( len(values) ):
                if values[i] <= 0:
                    messagebox.showerror("Error","Cannot accept negative or null values!")
                    return
                values[i] = values[i] / 100
            if sum( values ) > 1:
                messagebox.showerror("Error",f"Weight sum of elements in compound {__self__.compoundName.get()} exceeds 100%!")
                return
        else:
            for value in values: 
                if value % int( value ) != 0 or value <= 0:
                    messagebox.showerror("Error",f"Cannot accept fraction, negative or null values as atom numbers!")
                    return

        ################################################################
        #NOTE: checks if adding a compound to material wil surpass 100%
        ################################################################
        try: 
            quantity = float( __self__.quantity.get() )
            if quantity <= 0: 
                messagebox.showerror("Error","Invalid percentage value!")
                return
        except: 
            messagebox.showerror("Error","Invalid percentage value!")
            return
        totalWeight = 0
        for compound in __self__.compoundsInMaterial:
            totalWeight += compound[1]
        if totalWeight + quantity > 100:
            messagebox.showerror("Error","Material already at 100%! Remove unwanted compounds from material and try again.")
            return
        ################################################################
            
        userCompound.set_compound( 
            values, 
            symbols, 
            mode=__self__.compoundAssembleMode.get(), 
            ctype="custom", 
            name=__self__.compoundName.get())

        __self__.build_material( compound=userCompound, quantity=quantity )
        return

    def refresh_material_view(__self__):
        __self__.materialName.delete(0, END)
        for compound in __self__.compoundsInMaterial:
            __self__.materialName.insert(END, compound[0].name + ", " + str(compound[1]) )
        __self__.parent.display_material()
        return

if __name__.endswith("__main__"):
    root = Tk()
    a = AlchemyLab( root )
    root.mainloop()