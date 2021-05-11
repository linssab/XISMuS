#################################################################
#                                                               #
#          Fit Panels                                           #
#                        version: 2.4.0 - May - 2021            #
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
####################
logger.info("In FitPanels: Importing local modules...")
from Engine import SpecRead
from Engine import SpecMath
from .ProgressBar import BusyManager
from Graphics import *
from .Utils import *
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
        __self__.SnipConfig = []
        __self__.build_widgets()
        __self__.set_initial_params(configuration)
        __self__.toggle()

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
        __self__.BgOption = ttk.Checkbutton(__self__.LowerPanel,
                variable=__self__.BG,
                text="Use background",
                command=__self__.toggle)
        __self__.SetBG = ttk.Button(__self__.LowerPanel,
                text="Configure fit bg",
                command=__self__.spawn_bgconfig)
        __self__.PoolPane = Frame(__self__.MainPanel)
        __self__.PoolScroll = ttk.Scrollbar(__self__.PoolPane)
        __self__.Pool = ttk.Treeview(__self__.PoolPane, takefocus=False,
                yscrollcommand=__self__.PoolScroll.set)
        __self__.Pool.heading("#0",text="Pool")
        __self__.AddRemovePane = Frame(__self__.MainPanel)
        __self__.AddBtn = Button(__self__.AddRemovePane, text=">>>", bd=0,
                command=__self__.add_to_tree)
        __self__.RemoveBtn = Button(__self__.AddRemovePane, text="<<<", bd=0,
                command=__self__.remove_from_tree)
        __self__.CancelBtn = ttk.Button(__self__.LowerPanel, text="Cancel",
                command=__self__.kill)
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
        __self__.ElementsList.grid(row=0,column=0,sticky=N+S+W+E)
        __self__.ElementsScroll.grid(row=0,column=1,sticky=N+S)
        __self__.LinesList.grid(row=0,column=0,sticky=N+S+W+E)
        __self__.LinesList.config(selectmode=MULTIPLE)
        __self__.LinesScroll.grid(row=0,column=1,sticky=N+S)
        __self__.AddBtn.grid(row=0)
        __self__.RemoveBtn.grid(row=1)
        __self__.BgOption.grid(row=0, column=0, padx=(0,5), sticky=W)
        __self__.SetBG.grid(row=0,column=1, padx=(5,25), sticky=W)
        __self__.EmbedBtn.grid(row=0, column=2, padx=(0,5), sticky=E)
        __self__.CancelBtn.grid(row=0, column=3, padx=(5,0), sticky=E)
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

    def toggle(__self__, e=""):
        switch = __self__.BG.get()
        if switch: __self__.SetBG.state(["!disabled"])
        else: __self__.SetBG.state(["disabled"])

    def set_initial_params(__self__, params):
        if bool(params) == False: 
            return
        else:
            __self__.BG.set(params["bg"])
            for element in params["elements"].keys():
                __self__.Pool.insert("", 0, text=element, iid=element)
                for line in params["elements"][element]:
                    __self__.Pool.insert(element,0,text=line,iid=element+line)

    def spawn_bgconfig(__self__, e=""):
        __self__.BgPanel = PeakClipper(__self__)
    
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
            configuration["bg_settings"] = __self__.SnipConfig
            __self__.parent.DATACUBE.fit_config = configuration
            __self__.parent.plot.fit_btn.config(state=NORMAL)
            #__self__.parent.plot.fit_btn.config(image=NORMAL_ICO)
        else: 
            try: del __self__.parent.DATACUBE.fit_config
            except: pass
            __self__.parent.plot.fit_btn.config(state=DISABLED)
            #__self__.parent.plot.fit_btn.config(image=DISABLED_ICO)
        if not any("temp" in x for x in Constants.MY_DATACUBE.datatypes):
            __self__.busy.busy()
            __self__.parent.DATACUBE.save_cube()
            __self__.busy.notbusy()
        else: pass
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
        try: index = __self__.ElementsList.get(0,END).index(SELECTED_ELEMENT)
        except: return
        __self__.LinesList.delete(0,END)
        for line in __self__.ElementsData[index].keys():
            __self__.LinesList.insert(END,line)
    
    def kill(__self__):
        __self__.parent.Panel = None
        __self__.master.destroy()
        del __self__
        gc.collect()


class PeakClipper:
    def __init__(__self__,parent,mode="SNIPBG"):
        __self__.master = Toplevel(master = parent.master)
        __self__.parent = parent
        __self__.mode = mode
        __self__.master.tagged = True
        __self__.master.attributes("-alpha",0.0)
        __self__.master.resizable(True,True)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.master.bind("<Escape>",__self__.kill)

        __self__.right_panel = Frame(__self__.master,height=480)
        __self__.frame1 = Frame(__self__.master,height=480,width=320)
        __self__.frame2 = LabelFrame(__self__.right_panel,
                height=320,width=120,
                padx=15, pady=15,
                text="SNIPBG Parameters:")
        __self__.frame3 = LabelFrame(__self__.right_panel,
                padx=15, pady=15,
                height=320,width=120,
                text="Polynomial Parameters:")
        __self__.frame4 = Frame(__self__.right_panel)

        __self__.frame1.grid(row=0,rowspan=3,column=0,sticky=N+E+W+S)
        __self__.right_panel.grid(row=0,rowspan=2,column=1,padx=(10,35),sticky="")
        __self__.frame2.grid(row=2,column=1,padx=15,sticky="")
        __self__.frame4.grid(row=3,column=1,columnspan=2,padx=15,pady=15,sticky="")
        __self__.master.grid_columnconfigure(0,weight=1)
        __self__.master.grid_rowconfigure(0,weight=1)

        __self__.savgol = IntVar() #Savgol window
        __self__.order = IntVar() #Savgol order function order
        __self__.window = IntVar() #Clip window
        __self__.iter = IntVar() #No. of cycles
        __self__.nglobal = IntVar() #Polynomial function degree for global spectrum
        __self__.nsingle = IntVar() #Polynomial function degree for all other spectra
        __self__.r_factor = IntVar() #Polyfit r factor

        if __self__.parent.SnipConfig != []:
            a,b,c,d = __self__.parent.SnipConfig
            __self__.iter.set(a)
            __self__.savgol.set(b)
            __self__.window.set(c)
            __self__.order.set(d)
        elif __self__.parent.parent.DATACUBE.config["bg_settings"] != []:
            a,b,c,d = __self__.parent.parent.DATACUBE.config["bg_settings"]
            __self__.iter.set(a)
            __self__.savgol.set(c)
            __self__.window.set(b)
            __self__.order.set(d)
        elif mode == "SNIPBG":
            __self__.iter.set(24)
            __self__.savgol.set(5)
            __self__.window.set(5)
            __self__.order.set(3)
        elif mode == "Polynomial":
            __self__.nglobal.set(6)
            __self__.r_factor.set(2)

        __self__.build_widgets()
        #NOTE: Disables
        if mode == "SNIPBG":
            # Not yet implemented #
            #__self__.frame3.config(state=DISABLED)
            pass
        elif mode == "Polynomial":
            __self__.entry_savgol.config(state=DISABLED)
            __self__.entry_order.config(state=DISABLED)
            __self__.entry_window.config(state=DISABLED)
            __self__.entry_iter.config(state=DISABLED)
            __self__.button_save.config(state=DISABLED)
            __self__.button_try.config(state=DISABLED)
            __self__.randomize.config(state=DISABLED)

    def build_widgets(__self__):
        # frame 1 (left)
        __self__.upper = Canvas(__self__.frame1)
        fig_bg_color = __self__.master.cget("background")
        rgb = __self__.master.winfo_rgb(fig_bg_color)
        color = (rgb[0]/65535, rgb[1]/65535, rgb[2]/65535)
        __self__.upper.pack(side=TOP, expand=True, fill=BOTH, padx=(16,16),pady=(0,16))
        __self__.figure = Figure(figsize=(5,4), dpi=75)
        __self__.figure.patch.set_facecolor(color)
        __self__.plot = __self__.figure.add_subplot(111)
        __self__.plot.grid(which='both',axis='both')
        __self__.plot.axis('On')
        __self__.canvas = FigureCanvasTkAgg(__self__.figure,__self__.upper)
        __self__.canvas.draw()
        __self__.mplCanvas = __self__.canvas.get_tk_widget()
        __self__.mplCanvas.pack(expand=True,fill=BOTH,anchor=N+W)
        __self__.canvas._tkcanvas.pack()

        # right panel (top)
        __self__.randomize = ttk.Button(
                __self__.right_panel,
                text="Pick random spectrum",
                width=17,
                command= lambda: __self__.random_sample())
        __self__.pick_summation = ttk.Button(
                __self__.right_panel,
                text="Pick summation spectrum",
                width=17,
                command= lambda: __self__.random_sample(summation=1))
        
        # frame 2 (top-right)
        __self__.label_savgol = Label(__self__.frame2, text="Sav-gol window: ")
        __self__.label_order = Label(__self__.frame2, text="Sav-gol order: ")
        __self__.label_window = Label(__self__.frame2, text= "Clipping window: ")
        __self__.label_iter = Label(__self__.frame2, text="Number of iterations: ")
        __self__.entry_savgol = Entry(__self__.frame2,textvariable=__self__.savgol,width=15)
        __self__.entry_order = Entry(__self__.frame2,textvariable=__self__.order,width=15)
        __self__.entry_window = Entry(__self__.frame2,textvariable=__self__.window,width=15)
        __self__.entry_iter = Entry(__self__.frame2,textvariable=__self__.iter,width=15)

        # frame 3 (middle-right)
        __self__.label_nglobal = Label(__self__.frame3, text="Global spectrum degree: ")
        __self__.label_r_factor = Label(__self__.frame3, text= "R factor: ")
        __self__.entry_nglobal = Entry(__self__.frame3,
                textvariable=__self__.nglobal,width=15)
        __self__.entry_r_factor = Entry(__self__.frame3,
                textvariable=__self__.r_factor,width=15)

        # frame 4 (lower-right)
        __self__.button_try = ttk.Button(__self__.frame4,text="Try",width=10,
                command=__self__.refresh_plot)
        __self__.button_save = ttk.Button(__self__.frame4, text="Save",width=10,
                command=__self__.save)
        __self__.button_cancel = ttk.Button(__self__.frame4, text="Cancel",width=10,
                command=__self__.kill)

        __self__.randomize.grid(row=0,column=0,columnspan=2,pady=(15,0),padx=25,sticky=W+E)
        __self__.pick_summation.grid(row=1,column=0,columnspan=2,pady=(0,15),padx=25,sticky=W+E)
        __self__.label_savgol.grid(row=0,column=0)
        __self__.label_order.grid(row=1,column=0)
        __self__.label_window.grid(row=2,column=0)
        __self__.label_iter.grid(row=3,column=0)
        __self__.entry_savgol.grid(row=0,column=1,sticky=E)
        __self__.entry_order.grid(row=1,column=1,sticky=E)
        __self__.entry_window.grid(row=2,column=1,sticky=E)
        __self__.entry_iter.grid(row=3,column=1,sticky=E)
        __self__.label_nglobal.grid(row=0,column=0)
        __self__.label_r_factor.grid(row=1,column=0)
        __self__.entry_nglobal.grid(row=0,column=1,sticky=E)
        __self__.entry_r_factor.grid(row=1,column=1,sticky=E)
        __self__.button_try.grid(row=0,column=0)
        __self__.button_save.grid(row=0,column=1)
        __self__.button_cancel.grid(row=1,column=0,columnspan=2, sticky=W+E)

        __self__.master.update()
        place_center(__self__.parent.master,__self__.master)
        __self__.master.focus_set()
        __self__.master.grab_set()
        icon = os.path.join(os.getcwd(),"images","icons","settings.ico")
        __self__.master.iconbitmap(icon)
        __self__.boot_plot()
        __self__.random_sample()
        x = __self__.master.winfo_width()
        y = __self__.master.winfo_height()
        __self__.master.minsize(x,y)
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)

    def stripbg(__self__):
        if __self__.mode == "SNIPBG":
            savgol = __self__.savgol.get()
            order = __self__.order.get()
            window = __self__.window.get()
            cycles = __self__.iter.get()
            background = SpecMath.peakstrip(__self__.spectrum,cycles,window,savgol,order)
        elif __self__.mode == "Polynomial":
            nglobal = __self__.nglobal.get()
            r_factor = __self__.r_factor.get()
            background = SpecMath.peakstrip(__self__.spectrum,cycles,window,savgol,order)
        return background

    def boot_plot(__self__):
        label = f"{__self__.parent.parent.DATACUBE.name}"
        __self__.plot.spines["top"].set_color("black")
        __self__.plot.spines["bottom"].set_color("black")
        __self__.plot.spines["left"].set_color("black")
        __self__.plot.spines["right"].set_color("black")
        __self__.plot.set_ylabel("Counts")
        __self__.plot.set_xlabel("Channels")
        __self__.SPECPLOT, = __self__.plot.plot(
                __self__.parent.parent.DATACUBE.sum,
                color="blue",
                label=label)
        __self__.BGPLOT, = __self__.plot.plot( 
                __self__.parent.parent.DATACUBE.sum_bg,
                label="Background",
                color="yellow")

    def refresh_plot(__self__):
        label = f"{__self__.parent.parent.DATACUBE.name} - {__self__.sample}"
        try:
            __self__.background = __self__.stripbg()
        except Exception as e:
            __self__.background = np.zeros([__self__.spectrum.shape[0]],dtype=np.float32)
            pass
        __self__.SPECPLOT.set_ydata(__self__.spectrum)
        __self__.BGPLOT.set_ydata(__self__.background)
        if Constants.PLOTSCALE == "-semilogy": 
            __self__.plot.set_ylim(bottom=10e-1)
            __self__.plot.set_yscale("log")
        else:
            __self__.plot.set_ylim(bottom=0)
            __self__.plot.set_yscale("linear")
        __self__.plot.set_ylim(top=1.10*__self__.spectrum.max())
        __self__.plot.set_xlim([0,__self__.spectrum.shape[0]])
        __self__.plot.legend().get_texts()[0].set_text(label)
        __self__.plot.legend(loc="upper right")
        __self__.canvas.draw()

    def random_sample(__self__,summation=0):
        if summation:
            __self__.sample = "Summation"
            __self__.spectrum = __self__.parent.parent.DATACUBE.sum
        else:
            spec_no = __self__.parent.parent.DATACUBE.img_size
            __self__.sample = random.randint(1,spec_no-1)
            __self__.spectrum = __self__.parent.parent.DATACUBE.matrix.reshape(
                    -1,__self__.parent.parent.DATACUBE.matrix.shape[-1])[__self__.sample]
        __self__.refresh_plot()
        return

    def save(__self__):
        values = __self__.iter.get(),__self__.window.get(),__self__.savgol.get(),__self__.order.get()
        proceed = __self__.verify_values(values)
        if proceed == True: 
            __self__.parent.SnipConfig = values
            __self__.kill()
        else: messagebox.showerror("Value Error", "Parameters not valid. No negative or zero values are valid. Sav-gol window must be odd and greater than Sav-gol order.")

    def kill(__self__, event=""):
        __self__.master.grab_release()
        __self__.parent.master.grab_set()
        __self__.parent.master.focus_set()
        __self__.master.destroy()

    def verify_values(__self__,snip):
        if snip[0] <= 0 or snip[1] <= 0: return False
        if int(snip[2]%2) == 0: return False
        if snip[3] > snip[2]: return False
        else: return True

