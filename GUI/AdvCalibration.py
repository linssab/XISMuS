#################################################################
#                                                               #
#          Advanced Calibration Window                          #
#                        version: 2.0.0 - Feb - 2021            #
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
from .ProgressBar import Busy
from Graphics import *
####################

class AdvCalib():
    def __init__(__self__, parent, root, hascube=0):
        __self__.master = Toplevel(master = parent.master)
        __self__.master.title("Advanced calibration")
        __self__.hascube = hascube
        icon = os.path.join(os.getcwd(),"images","icons","adv.ico")
        __self__.master.iconbitmap(icon)
        __self__.master.attributes("-alpha",0.0)
        __self__.master.resizable(True,True)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.master.bind("<Escape>",__self__.kill)
        x, y = 480, 320 
        __self__.frame1 = LabelFrame(__self__.master, height=x, width=y, 
                text="Partial sum spectrum")
        __self__.frame2 = Frame(__self__.master, height=x-60, width=120)
        __self__.frame3 = Frame(__self__.master, width=y, height=60)
        __self__.frame1.grid(row=0, column=0, sticky=N+E+W+S, padx=(8,0))
        __self__.frame2.grid(row=0, column=1, rowspan=2, padx=(16,16), pady=(16,16), 
                sticky=N+S)
        __self__.frame3.grid(row=1, column=0, columnspan=2, pady=(24,16), sticky=W+E)
        __self__.root = root
        __self__.parent = parent
        __self__.plotmode = "Linear"
        __self__.xhover = 0
        __self__.spec_no = root.mcacount[Constants.CONFIG.get("directory")]
        __self__.folder = Constants.CONFIG.get("directory")
        __self__.window = DoubleVar()
        __self__.equation = StringVar()
        __self__.window.set(Constants.PEAK_TOLERANCE)
        __self__.equation.set("E(i) = GAIN*i + ZERO")
        __self__.loaded = []
        
        __self__.master.grid_columnconfigure(0,weight=1)
        __self__.master.grid_rowconfigure(0,weight=1)

        __self__.build_widgets()
        __self__.master.focus_force()
        __self__.master.grab_set()

    def set_cursor_selection(__self__, event):
        global CURSOR_SELECTION
        y = event.y
        idx = event.widget.nearest(y)
        name = event.widget.myId
        if name == "ch":
            CURSOR_SELECTION = event.widget.get(idx)
        elif name == "en":
            CURSOR_SELECTION = event.widget.get(idx)
        else: CURSOR_SELECTION = None

    def write_equation(__self__):
        x, y = list(__self__.channels.get(0,END)),list(__self__.energies.get(0,END))
        op = "+"
        if len(x) > 1:
            gain, zero, r, = SpecMath.linregress(x,y) 
        else:
            __self__.equation.set("E(i) = GAIN*i + ZERO")
            __self__.results.update()
            return
        if zero < 0: op = ""
        text = "E(i) = {0:.3f}*i {2} {1:.3f}".format(gain, zero, op)
        __self__.equation.set(text)
        __self__.results.update()

    def random_generator(__self__):
        n = 0
        while n not in __self__.loaded:
            n = random.randint(1,__self__.spec_no-5)
            __self__.loaded.append(n)
        return n

    def get_spectrum_length(__self__):
        if __self__.parent.matrix.shape[2] > 1:
            __self__.chan = __self__.parent.matrix.shape[2]
        else:
            mca = __self__.get_mca(1)
            __self__.chan = SpecRead.getdata(mca).shape[0]
        __self__.spectrum = np.zeros(__self__.chan, dtype="int32")

    def get_mca(__self__,n): 
        if __self__.folder == "Training Data 1" or \
                    __self__.folder == "Training Data 2":
                mca = os.path.join(SpecRead.__PERSONAL__,"Example Data",__self__.folder,
                        __self__.root.samples[__self__.folder]+"{0}.{1}".format(n,
                        __self__.root.mca_extension[__self__.folder]))
        elif isinstance(__self__.root.samples[__self__.folder],tuple):
            mca = __self__.root.samples[__self__.folder][n]
        else:
            mca = os.path.join(Constants.SAMPLE_PATH,
                    __self__.root.samples[__self__.folder]+"{0}.{1}".format(n,
                        __self__.root.mca_extension[__self__.folder]))
        return mca
    
    def create_reference_spectrum(__self__,hascube=0):
        if hascube: 
            __self__.spectrum = Constants.MY_DATACUBE.sum
            return

        __self__.get_spectrum_length()

        limit = int(__self__.spec_no*0.20)
        if limit > 300: limit = 300 #sample is too large
        elif limit < 100: limit = __self__.spec_no #sample is too small

        bar = Busy(limit,0)
        bar.update_text("Thinking...")

        ################################################
        # IF PARENT HAS A MATRIX, IT LOADED AN H5 FILE #
        ################################################
        if __self__.parent.matrix.shape[2] > 1:
            data = __self__.parent.matrix.reshape(-1,__self__.parent.matrix.shape[-1])
            for i in range(limit):
                bar.updatebar(i)
                n = __self__.random_generator()
                __self__.spectrum += data[n]
            del data
            gc.collect()
        ################################################

        ####################################################################
        # ELSE, IT IS READING MCA EITHER FROM USER LIST OR DETECTED FOLDER #
        ####################################################################
        else:
            for i in range(limit):
                bar.updatebar(i)
                n = __self__.random_generator()
                mca = __self__.get_mca(n)
                __self__.spectrum += SpecRead.getdata(mca)
        ####################################################################
        bar.destroybar()

    def get_peaks(__self__):
        try: w = __self__.window.get()
        except: return 1
        if 1 <= w <= 32:
            __self__.peaks = SpecMath.findpeaks(__self__.spectrum, 
                    w=w,
                    r=2)
            return
        else: return 1

    def refresh(__self__, e=""):
        w = __self__.get_peaks()
        if w is None:
            pass
        else: return
        __self__.plot_peaks()
    
    def plot_peaks(__self__):
        __self__.plot.clear()
        if __self__.plotmode == "Linear":
            __self__.plot.plot(__self__.spectrum, color="blue", lw=2)
            __self__.plot.set_ylim(
                bottom=1,
                top=1.10*__self__.spectrum.max())
        else:
            __self__.plot.semilogy(__self__.spectrum, color="blue", lw=2)
            __self__.plot.set_ylim(
                bottom=10,
                top=1.30*__self__.spectrum.max())
        for line in __self__.peaks:
            __self__.plot.axvline(
                    x=line)
        __self__.plot.set_xlabel("Channels")
        __self__.canvas.draw()
        return

    def set_lin(__self__, e=""):
        __self__.plotmode = "Linear"
        __self__.plot_peaks()
    
    def set_log(__self__, e=""):
        __self__.plotmode = "Log"
        __self__.plot_peaks()

    def kill(__self__, e=""):
        try: __self__.kill_popup()
        except: pass
        __self__.master.grab_release()
        __self__.parent.master.focus_set()
        __self__.parent.master.grab_set()
        __self__.master.destroy()
        del __self__
        return

    def cancel(__self__, e=""):
        __self__.parent.calibration_params = None
        __self__.kill()
        return

    def hover_line(__self__, event):

        def find_nearest(array, value):
            array = np.asarray(array)
            idx = (np.abs(array - value)).argmin()
            return array[idx]

        if event.xdata is not None:
            match = False
            nearest = find_nearest(__self__.peaks, event.xdata) 
            if int(event.xdata)-3 < nearest < int(event.xdata)+3:
                __self__.xhover = nearest
                match = True
            if match:
                __self__.selected_peak = __self__.peaks.index(__self__.xhover)
                __self__.master.config(cursor="hand2")
            elif not __self__.xhover-3 < event.xdata < __self__.xhover+3:
                __self__.master.config(cursor="arrow")
        else: __self__.master.config(cursor="arrow")

    def on_click(__self__, event):
        if event.xdata is not None:
            if __self__.xhover-3 < event.xdata < __self__.xhover+3:
                __self__.popup(event.x, event.y)
        else: return

    def popup(__self__, x,y):
        __self__.win = Toplevel(master = __self__.master)
        __self__.win.bind("<Escape>",__self__.kill_popup)
        __self__.win.bind("<FocusOut>",__self__.kill_popup)
        __self__.win.withdraw()
        __self__.win.resizable(False,False)
        __self__.win.overrideredirect(True)
        __self__.diag = ttk.Frame(__self__.win, relief=RIDGE, style="dark.TFrame")

        label1 = ttk.Label(__self__.diag,text="Channel: ", style="dark.TLabel")
        label2 = ttk.Label(__self__.diag,text="Energy (KeV): ", style="dark.TLabel")

        __self__.en = DoubleVar()
        __self__.ch = IntVar()
        __self__.ch.set(__self__.xhover)
        __self__.win.bind("<Return>",__self__.add_values)

        ch_ = ttk.Entry(__self__.diag, textvariable=__self__.ch,validate="focusout",
                width=9)
        ch_.config(state=DISABLED)
        en_ = ttk.Entry(__self__.diag, textvariable=__self__.en,validate="focusout",
                width=9)
        
        accept = ttk.Button(__self__.diag,text="Ok", width=8, 
                command=__self__.add_values)
        cancel = ttk.Button(__self__.diag,text="Cancel", width=8, 
                command=__self__.kill_popup)

        __self__.diag.grid()
        label1.grid(row=1,column=0, pady=(6,0),padx=(6,0))
        label2.grid(row=2,column=0, padx=(6,0))
        ch_.grid(row=1,column=1,pady=(6,0))
        en_.grid(row=2,column=1)
        accept.grid(row=3,column=0,pady=(6,6),sticky=W+E,padx=(10,3))
        cancel.grid(row=3,column=1,pady=(6,6),sticky=W+E,padx=(3,10))

        __self__.win.update()
        width = __self__.win.winfo_width()
        height = __self__.win.winfo_height()
        posx = __self__.root.master.winfo_pointerx()
        posy = __self__.root.master.winfo_pointery()

        __self__.win.geometry(f"{width}x{height}+{posx}+{posy}")
        __self__.win.update()
        __self__.win.deiconify()
        en_.focus_set()
    
    def kill_popup(__self__, e=""):
        try:
            if __self__.win.focus_get().cget("text") == "Ok":
                __self__.add_values()
                return
            else:  
                __self__.win.destroy()
                del __self__.win 
        except:
            __self__.win.destroy()
            del __self__.win 

    def add_values(__self__, e=""):
        try: ch, en = __self__.ch.get(), __self__.en.get()
        except: return
        if (not ch in __self__.channels.get(0,END)) \
                and\
                (not en in __self__.energies.get(0,END)):
            __self__.channels.insert(END,ch)
            __self__.energies.insert(END,en)
            __self__.write_equation()
        __self__.kill_popup()

    def remove_value(__self__, e=""):
        global CURSOR_SELECTION
        active = None
        try: 
            active = __self__.channels.get(__self__.channels.curselection())
            idx = __self__.channels.get(0,END).index(active)
        except:
            try:
                active = __self__.energies.get(__self__.energies.curselection())
                idx = __self__.energies.get(0,END).index(active)
            except: return
        if active is None: return
        else:
            if active == CURSOR_SELECTION: CURSOR_SELECTION = None
            __self__.channels.delete(idx)
            __self__.energies.delete(idx)
            __self__.write_equation()

    def validate(__self__):
        parameters = [[i,j] for i,j in zip(__self__.channels.get(0,END),
            __self__.energies.get(0,END))]
        if __self__.hascube:
            __self__.parent.calibration_params = parameters
            __self__.plot.clear()
            __self__.kill()
            return
        __self__.parent.save_param(advparams=parameters)
        __self__.plot.clear()

    def build_widgets(__self__):
        
        # PlotPanel
        __self__.upper = Canvas(__self__.frame1)
        fig_bg_color = __self__.master.cget("background")
        rgb = __self__.master.winfo_rgb(fig_bg_color)
        color = (rgb[0]/65535, rgb[1]/65535, rgb[2]/65535)
        __self__.upper.pack(side=TOP, expand=True, fill=BOTH, pady=(16,0))
        __self__.figure = Figure(figsize=(6,4), dpi=75)
        __self__.figure.subplots_adjust(bottom=0.12, top=1, left=0.05, right=0.95)
        __self__.figure.patch.set_facecolor(color)
        __self__.plot = __self__.figure.add_subplot(111)
        __self__.plot.get_yaxis().set_visible(False)
        __self__.plot.grid(which="both",axis="x")
        __self__.plot.axis('On')
        __self__.canvas = FigureCanvasTkAgg(__self__.figure,__self__.upper)
        __self__.canvas.mpl_connect("motion_notify_event",__self__.hover_line)
        __self__.canvas.mpl_connect("button_press_event",__self__.on_click)
        __self__.canvas.draw()
        __self__.mplCanvas = __self__.canvas.get_tk_widget()
        __self__.mplCanvas.pack(expand=True,fill=BOTH,anchor=N+W)
        __self__.canvas._tkcanvas.pack()

        #right panel
        __self__.listlabel = Label(__self__.frame2, text="Channel - Energy", width=25)
        __self__.channels = Listbox(__self__.frame2, width=12, height=11)
        __self__.channels.bind("<Button-1>",__self__.set_cursor_selection)
        __self__.channels.myId = "ch"
        __self__.channels.config(selectmode=SINGLE)
        __self__.energies = Listbox(__self__.frame2, width=12, height=11)
        __self__.energies.bind("<Button-1>",__self__.set_cursor_selection)
        __self__.energies.myId = "en"
        __self__.energies.config(selectmode=SINGLE)
        __self__.remove = ttk.Button(__self__.frame2, text="Remove", width=11,
                command=__self__.remove_value)
        __self__.results = Label(__self__.frame2, width=20,
                textvariable=__self__.equation, justify=CENTER)
        __self__.save_and_exit = ttk.Button(__self__.frame2, text="Save and Compile",
                command=__self__.validate)
        __self__.cancel = ttk.Button(__self__.frame2, text="Cancel",
                command=__self__.cancel)

        __self__.listlabel.grid(row=0, column=0, columnspan=2, sticky=W+E)
        __self__.channels.grid(row=1, column=0, sticky=N+S)
        __self__.energies.grid(row=1, column=1, sticky=N+S)
        __self__.results.grid(row=2, column=0, columnspan=2, pady=(6,0))
        __self__.remove.grid(row=3, column=0, columnspan=2, pady=(6,3))
        __self__.save_and_exit.grid(row=4, column=0, columnspan=2, pady=(6,3), padx=(16,16), 
                sticky=W+E)
        __self__.cancel.grid(row=5, column=0, columnspan=2, pady=(0,6), padx=(16,16),
                sticky=W+E)

        #bottom panel
        __self__.label1 = Label(__self__.frame3, text="Peakfind tolerance:",justify=LEFT)
        __self__.entry1 = Entry(__self__.frame3, textvariable=__self__.window)
        __self__.retry = ttk.Button(__self__.frame3, text="Refresh", command=__self__.refresh)
        icon = PhotoImage(data=ICO_LIN)
        __self__.ico_lin = icon.subsample(1,1)
        icon = PhotoImage(data=ICO_LOG)
        __self__.ico_log = icon.subsample(1,1)
        __self__.lin = ttk.Button(
                __self__.frame3, 
                image=__self__.ico_lin,
                width=20,
                command=__self__.set_lin)
        __self__.log = ttk.Button(
                __self__.frame3, 
                image=__self__.ico_log,
                width=20,
                command=__self__.set_log)
        
        __self__.label1.grid(row=0, column=0, padx=(16,0), sticky=W)
        __self__.entry1.grid(row=0, column=1, sticky=W)
        __self__.retry.grid(row=0, column=2, padx=(32,0), sticky=W)
        __self__.lin.grid(row=0, column=3, padx=(6,0))
        __self__.log.grid(row=0, column=4)


        # execute 
        if __self__.hascube == False:
            __self__.create_reference_spectrum()
            __self__.plot.data, = __self__.plot.plot(__self__.spectrum)
            __self__.refresh()
        else: 
            __self__.create_reference_spectrum(hascube=1)
            __self__.plot.data, = __self__.plot.plot(__self__.spectrum)
            __self__.save_and_exit.config(text="Save")
            print(__self__.parent.calibration_params)
            if __self__.parent.calibration_params is not None:
                for anchor in __self__.parent.calibration_params:
                    __self__.channels.insert(END,anchor[0])
                    __self__.energies.insert(END,anchor[1])
                    __self__.add_values()
            __self__.refresh()

        x = __self__.master.winfo_width()
        y = __self__.master.winfo_height()
        __self__.master.minsize(x,y)
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)


