#################################################################
#                                                               #
#          Fit Panels                                           #
#                        version: 2.2.0 - Mar - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import Constants

# tcl/Tk imports
try:
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
    from tkinter import font as tkFont
except:
    from Tkinter import *
    from Tkinter import ttk
    from Tkinter import messagebox
    from Tkinter import filedialog
    import tkFont

#############
# utilities #
#############
import os, gc
import logging
import random
import numpy as np
logger = logging.getLogger("logfile")
#############

######################
# matplotlib imports #
######################
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
from matplotlib import style
style.use('ggplot')
######################

####################
# internal imports #
from Engine import SpecRead
from Engine import SpecMath
from .ProgressBar import BusyManager
from Graphics import *
from Elements import *
####################
global SELECTED_ELEMENT
SELECTED_ELEMENT = ""

class SimpleFitPanel:
    def __init__(__self__,parent,configuration):
       __self__.parent = parent
       __self__.master = Toplevel(master=__self__.parent.master)
       __self__.busy = BusyManager(__self__.master)
       __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
       icon = os.path.join(os.getcwd(),"images","icons","adv.ico")
       __self__.master.iconbitmap(icon)
       __self__.master.title("Fit Elements Poller")
       __self__.master.attributes("-alpha",0.0)
       __self__.master.resizable(False,False)
       __self__.UpperPanel = Frame(__self__.master)
       __self__.MainPanel = ttk.LabelFrame(__self__.master, text="Elements")
       __self__.LowerPanel = Frame(__self__.master)
       __self__.UpperPanel.grid(row=0,sticky=W+E)
       __self__.MainPanel.grid(row=1,padx=15,pady=15,sticky=N+W+E+S)
       __self__.LowerPanel.grid(row=2,sticky=E, padx=15, pady=(0,15))
       __self__.ElementsData = ALL_LINES 
       __self__.build_widgets()
       __self__.set_initial_params(configuration)

    def build_widgets(__self__):
        __self__.ElementsPane = Frame(__self__.MainPanel) 
        __self__.ElementsScroll = ttk.Scrollbar(__self__.ElementsPane)
        __self__.ElementsList = Listbox(__self__.ElementsPane,
                yscrollcommand=__self__.ElementsScroll.set) 
        __self__.ElementsList.bind("<Button-1>",__self__.set_selected_element)
        __self__.LinesPane = Frame(__self__.MainPanel)
        __self__.LinesScroll = ttk.Scrollbar(__self__.LinesPane)
        __self__.LinesList = Listbox(__self__.LinesPane,
                yscrollcommand=__self__.LinesScroll.set)
        __self__.BG = BooleanVar()
        __self__.BgOption = ttk.Checkbutton(__self__.UpperPanel,
                variable=__self__.BG,
                text="Use background?")
        __self__.PoolPane = Frame(__self__.MainPanel)
        __self__.PoolScroll = ttk.Scrollbar(__self__.PoolPane)
        __self__.Pool = ttk.Treeview(__self__.PoolPane, takefocus=False,
                yscrollcomman=__self__.PoolScroll.set)
        __self__.Pool.heading("#0",text="Pool")
        __self__.AddRemovePane = Frame(__self__.MainPanel)
        __self__.AddBtn = Button(__self__.AddRemovePane, text=">>>", bd=0,
                command=__self__.add_to_tree)
        __self__.RemoveBtn = Button(__self__.AddRemovePane, text="<<<", bd=0,
                command=__self__.remove_from_tree)
        __self__.SaveBtn = ttk.Button(__self__.LowerPanel, text="Save")
        __self__.EmbedBtn = ttk.Button(__self__.LowerPanel, 
                text="Embed to Cube", command=__self__.embed_to_cube)
        
        __self__.ElementsPane.grid(row=0,column=0,padx=(15,2),pady=15,sticky=N+S+W+E)
        __self__.LinesPane.grid(row=0,column=1,padx=(2,15),pady=15,sticky=N+S+W+E)
        __self__.AddRemovePane.grid(row=0,column=2,padx=(15,15),pady=15,sticky=N+S)
        __self__.PoolPane.grid(row=0,column=3,padx=(15,15),pady=15)
        Grid.rowconfigure(__self__.AddRemovePane, 0, weight=1)
        Grid.rowconfigure(__self__.AddRemovePane, 1, weight=1)
        Grid.rowconfigure(__self__.ElementsPane, 0, weight=1)
        Grid.rowconfigure(__self__.LinesPane, 0, weight=1)
        Grid.rowconfigure(__self__.PoolPane, 0, weight=1)
        __self__.BgOption.grid(padx=15,pady=(15,0),sticky=W)
        __self__.ElementsList.grid(row=0,column=0,sticky=N+S+W+E)
        __self__.ElementsScroll.grid(row=0,column=1,sticky=N+S)
        __self__.LinesList.grid(row=0,column=0,sticky=N+S+W+E)
        __self__.LinesList.config(selectmode=MULTIPLE)
        __self__.LinesScroll.grid(row=0,column=1,sticky=N+S)
        __self__.AddBtn.grid(row=0)
        __self__.RemoveBtn.grid(row=1)
        __self__.SaveBtn.grid(row=0, column=0, padx=(0,5), sticky=E)
        __self__.EmbedBtn.grid(row=0, column=1, padx=(5,0), sticky=E)
        __self__.Pool.grid(row=0,column=0,sticky=N+S+W+E)
        __self__.PoolScroll.grid(row=0,column=1,sticky=N+S)
        __self__.ElementsScroll.config(command=__self__.ElementsList.yview)
        __self__.LinesScroll.config(command=__self__.LinesList.yview)
        __self__.PoolScroll.config(command=__self__.Pool.yview)
        __self__.PoolElements = {}

        __self__.fill_elements()
        x = __self__.master.winfo_width()
        y = __self__.master.winfo_height()
        __self__.master.minsize(x,y)
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)
        return

    def set_initial_params(__self__, params):
        if bool(params) == False: 
            return
        else:
            __self__.BG.set(params["bg"])
            for element in params["elements"].keys():
                __self__.Pool.insert("", 0, text=element, iid=element)
                for line in params["elements"][element]:
                    __self__.Pool.insert(element,0,text=line,iid=element+line)
    
    def embed_to_cube(__self__, e=""):
        NORMAL_ICO = __self__.parent.plot.FIT_NORMAL_ICO
        DISABLED_ICO = __self__.parent.plot.FIT_DISABLED_ICO
        configuration = {}
        configuration["elements"] = {}
        for element in __self__.Pool.get_children():
            configuration["elements"][element] = []
            for line in __self__.Pool.get_children(element):
                line = line.split(element)[-1]
                configuration["elements"][element].append(line)
        if bool(configuration["elements"]):
            configuration["bg"] = __self__.BG.get()
            __self__.parent.DATACUBE.fit_config = configuration
            __self__.parent.plot.fit_btn.config(state=NORMAL)
            #__self__.parent.plot.fit_btn.config(image=NORMAL_ICO)
        else: 
            try: del __self__.parent.DATACUBE.fit_config
            except: pass
            __self__.parent.plot.fit_btn.config(state=DISABLED)
            #__self__.parent.plot.fit_btn.config(image=DISABLED_ICO)
        __self__.busy.busy()
        __self__.parent.DATACUBE.save_cube()
        __self__.busy.notbusy()
        __self__.kill()

    def set_selected_element(__self__, e=""):
        global SELECTED_ELEMENT
        y = e.y
        idx = e.widget.nearest(y)
        SELECTED_ELEMENT = e.widget.get(idx)
        __self__.element_select()

    def remove_from_tree(__self__,e=""):
        items = __self__.Pool.selection()
        for item in items:
            __self__.Pool.delete(item)
        for element in __self__.Pool.get_children():
            if bool(__self__.Pool.get_children(element)):
                pass
            else: __self__.Pool.delete(element)

    def add_to_tree(__self__):
        global SELECTED_ELEMENT
        element = SELECTED_ELEMENT.split(" ")[-1]
        idxs = __self__.LinesList.curselection()
        lines = []
        for i in idxs:
            lines.append(__self__.LinesList.get(i))
        if lines == []: return
        if __self__.Pool.exists(element):
            for line in lines:
                if not __self__.Pool.exists(element+line):
                    __self__.Pool.insert(element,0,text=line,iid=element+line)
        else: 
            __self__.Pool.insert("",0,iid=element, text=element)
            for line in lines:
                if not __self__.Pool.exists(element+line): 
                    __self__.Pool.insert(element,0,text=line,iid=element+line)

    def fill_elements(__self__):
        elements = list(__self__.ElementsData.keys())
        Symbol = ElementList 
        for i in range(1,len(elements)):
            element = str(elements[i]) + " " + Symbol[i]
            __self__.ElementsList.insert(i,element)

    def element_select(__self__, e=""):
        global SELECTED_ELEMENT
        index = __self__.ElementsList.get(0,END).index(SELECTED_ELEMENT)
        __self__.LinesList.delete(0,END)
        for line in __self__.ElementsData[index].keys():
            __self__.LinesList.insert(END,line)
    
    def kill(__self__):
        __self__.parent.Panel = None
        __self__.master.destroy()
        del __self__
        gc.collect()
