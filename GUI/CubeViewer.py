#################################################################
#                                                               #
#          Cube viewer utility                                  #
#                        version: 2.4.3 - Oct - 2021            #
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
from .Utils import *
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


class ImageWindow:
    def __init__(__self__, parent, title):
        icon = os.path.join(os.getcwd(),"images","icons","plot.ico")
        __self__.parent = parent
        __self__.master = Toplevel()
        __self__.master.iconbitmap(icon)
        __self__.master.attributes("-alpha",0.0)
        __self__.alt = False
        __self__.master.bind("<Alt_L>",__self__.AltOn)
        __self__.master.bind("<KeyRelease-Alt_L>",__self__.AltOff)
        __self__.master.bind("<Return>",__self__.maximize)
        __self__.master.title(title)
        __self__.master.minsize(width=600,height=480)
        __self__.master.configure(bg='white')
        __self__.master.resizable(True,True)
        __self__.upper = Canvas(__self__.master)
        __self__.upper.config(bg='white')
        __self__.upper.pack(side=TOP, expand=True, fill=BOTH)#, padx=(16,16),pady=(16,16))
        text="Press Alt+Enter for full screen. To save the image, please use the Image Analyzer."
        __self__.lower = Frame(__self__.master,height=35)
        __self__.lower.pack(side=BOTTOM, anchor=N, fill=BOTH, expand=0)
        Label(__self__.lower, text=text).pack(padx=15, anchor=E, fill=BOTH, expand=1)

        # Save and replace buttons #
        __self__.figure = Figure(figsize=(5,4), dpi=75)
        __self__.plot = __self__.figure.add_subplot(111)
        __self__.plot.grid(which="both",axis="both")
        __self__.plot.axis("Off")
        __self__.plot.set_title(title)
        __self__.canvas = FigureCanvasTkAgg(__self__.figure,__self__.upper)
        __self__.canvas.draw()
        __self__.mplCanvas = __self__.canvas.get_tk_widget()
        __self__.mplCanvas.pack(fill=BOTH, anchor=N+W,expand=True)
        __self__.canvas._tkcanvas.pack()
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.wipe_plot)
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)

    def AltOn(__self__,e=""):
        __self__.alt = True

    def AltOff(__self__,e=""):
        __self__.alt = False

    def maximize(__self__,e=""):
        maximize_window(__self__)

    def draw_image(__self__,image=None):
        __self__.image = image
        __self__.display = __self__.plot.imshow(image, vmin=0, cmap=Constants.COLORMAP)
        place_center(__self__.parent.master, __self__.master)

    def refresh(__self__):
        __self__.display.set_data(__self__.image)
        __self__.display.set_clim(vmin=0, vmax=__self__.image.max())
        __self__.display.set_cmap(Constants.COLORMAP)
        __self__.canvas.draw()

    def create_connection(__self__):
        __self__.toolbar = NavigationToolbar(__self__.canvas,__self__.lower)
        __self__.toolbar.update()
        __self__.master.update_idletasks()
        __self__.Clicker = Clicker(__self__)
        __self__.Clicker.connect()

    def remove_connection(__self__):
        __self__.Clicker.disconnect()

    def wipe_plot(__self__):
        __self__.parent.master.focus_set()
        __self__.master.destroy()
        del __self__

class Clicker:
    def __init__(__self__, parent):
        __self__.canvas = parent.canvas
        __self__.parent = parent

    def getclick(__self__,e=""):
        __self__.x, __self__.y = round(e.xdata), round(e.ydata)
        print("X, Y = ",__self__.x,__self__.y)
        __self__.pop()

    def connect(__self__):
        __self__.connection = __self__.canvas.mpl_connect(
                "button_press_event",
                __self__.getclick)

    def disconnect(__self__):
        __self__.mplcanvas.mpl_disconnect(__self__.connection)

    def pop(__self__):
        __self__.win = Toplevel(master = __self__.parent.master)
        __self__.win.bind("<Escape>",__self__.kill_popup)
        __self__.win.bind("<FocusOut>",__self__.kill_popup)
        __self__.win.withdraw()
        __self__.win.resizable(False,False)
        __self__.win.overrideredirect(True)
        __self__.diag = ttk.Frame(__self__.win, relief=RIDGE, style="dark.TFrame")

        label1 = ttk.Label(__self__.diag,text="Move (px): ", style="dark.TLabel")

        __self__.en = IntVar()
        __self__.win.bind("<Return>",__self__.dummy)

        value_entry = ttk.Entry(__self__.diag, textvariable=__self__.en,validate="focusout",
                width=9)

        accept = ttk.Button(__self__.diag,text="Ok", width=8,
                command=__self__.dummy)
        cancel = ttk.Button(__self__.diag,text="Cancel", width=8,
                command=__self__.kill_popup)

        __self__.diag.grid()
        label1.grid(row=0,column=0, pady=(6,0),padx=(6,0))
        value_entry.grid(row=0,column=1,pady=(6,0),padx=(0,6))
        accept.grid(row=1,column=0,pady=(6,6),sticky=W+E,padx=(10,3))
        cancel.grid(row=1,column=1,pady=(6,6),sticky=W+E,padx=(3,10))

        __self__.win.update()
        width = __self__.win.winfo_width()
        height = __self__.win.winfo_height()
        posx = __self__.parent.parent.master.winfo_pointerx() #root window
        posy = __self__.parent.parent.master.winfo_pointery()

        __self__.win.geometry(f"{width}x{height}+{posx}+{posy}")
        __self__.win.update()
        __self__.win.deiconify()
        value_entry.focus_set()

    def kill_popup(__self__,e=""):
        try:
            if __self__.win.focus_get().cget("text") == "Ok":
                print("Ok!")
                __self__.dummy()
                return
            else:
                __self__.win.destroy()
                del __self__.win
        except:
            __self__.win.destroy()
            del __self__.win

    def dummy(__self__,e=""):
        value = __self__.en.get()
        row = int(__self__.y)
        __self__.parent.image[row,:] = np.roll(__self__.parent.image[row,:], value, 0)
        __self__.parent.refresh()
        __self__.win.destroy()
        del __self__.win
        print("Moo")


class Writer:
    def __init__(__self__,path):
        __self__.file = open(path,"w")
    
    def write(__self__,row,value):
        __self__.file.write(f"{row}\t{value}\n")

    def close(__self__):
        __self__.file.close()
