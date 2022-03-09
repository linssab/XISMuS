"""
Copyright (c) 2020 Sergio Augusto Barcellos Lins & Giovanni Ettore Gigante

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

import copy
import gc
#############
# Utilities #
#############
import os

#################
# Local imports #
#################
import Constants
import numpy as np

#############

Constants.LOGGER.info("In ImageAnalyzer: Importing local modules...")
from Engine.CBooster import *
from Engine.ImgMath import LEVELS, correlate, stackimages, write_image
from Graphics import *
from Utilities import *

from GUI import create_tooltip
from GUI.IndexNavigator import Navigator
from GUI.PlotWindow import PlotWin
from GUI.ProgressBar import Busy

#################

####################
# External modules #
####################
from tkinter import *
from tkinter import filedialog, messagebox, ttk

import matplotlib
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

####################

class Annotator:
    """ Creates an annotator to select areas on matplotlib canvases
    Annotator is invoked from Image Analyzer and is destroyed when Set ROI
    button is toggled off """

    def __init__(__self__,parent):

        # parent is the Image Analyzer object. The PlotWin object is the plot attribute:
        # parent.plot

        __self__.parent = parent
        __self__.alive = True #This exists because killing this object seems impossible
        __self__.element1 = parent.Map1Var.get()
        __self__.element2 = parent.Map2Var.get()
        __self__.roibox1 = parent.roibox1
        __self__.roibox2 = parent.roibox2
        __self__.ratebox = parent.ratebox
        __self__.area1 = Rectangle((0,0),1,1,fill=False,snap=True,color="red",linewidth=3)
        __self__.area2 = Rectangle((0,0),1,1,fill=False,snap=True,color="red",linewidth=3)
        __self__.x0 = None
        __self__.y0 = None
        __self__.x1 = None
        __self__.y1 = None
        __self__.parent.plot1.add_patch(__self__.area1)
        __self__.parent.plot2.add_patch(__self__.area2)
        __self__.parent.canvas1.mpl_connect("button_press_event",__self__.on_press)
        __self__.parent.canvas1.mpl_connect("motion_notify_event",__self__.on_drag)
        __self__.parent.canvas1.mpl_connect("button_release_event",__self__.on_release)
        __self__.parent.canvas2.mpl_connect("button_press_event",__self__.on_press)
        __self__.parent.canvas2.mpl_connect("motion_notify_event",__self__.on_drag)
        __self__.parent.canvas2.mpl_connect("button_release_event",__self__.on_release)
        __self__.press, __self__.move = False, False

    def refresh_annotator(__self__):
        __self__.element1 = __self__.parent.Map1Var.get()
        __self__.element2 = __self__.parent.Map2Var.get()
        __self__.area1.remove()
        __self__.area2.remove()
        __self__.canvas1.draw()
        __self__.canvas2.draw()
        __self__.parent.plot1.add_patch(__self__.area1)
        __self__.parent.plot2.add_patch(__self__.area2)

    def wipe_annotator(__self__):
        __self__.parent.plot.fit_plots = []
        __self__.area1.remove()
        __self__.area2.remove()
        __self__.parent.canvas1.draw()
        __self__.parent.canvas2.draw()
        __self__.roibox1["text"] = "Roi 1: None"
        __self__.roibox2["text"] = "Roi 2: None"
        __self__.ratebox["text"] = "Ratio: None"
        try: __self__.parent.plot.wipe_plot()
        except: pass
        __self__.parent.canvas1.mpl_connect("button_press_event",__self__.do_nothing)
        __self__.parent.canvas1.mpl_connect("button_notify_event",__self__.do_nothing)
        __self__.parent.canvas1.mpl_connect("button_release_event",__self__.do_nothing)
        __self__.parent.canvas2.mpl_connect("button_press_event",__self__.do_nothing)
        __self__.parent.canvas2.mpl_connect("button_notify_event",__self__.do_nothing)
        __self__.parent.canvas2.mpl_connect("button_release_event",__self__.do_nothing)
        __self__.parent.master.after(50,delattr(__self__.parent,"annotator"))
        __self__.alive = False #prevents on_drag from working
        del __self__

    def do_nothing(__self__,e=""):
        """ doing bunches of nothing """
        return

    def refresh_roi_plot(__self__):
        if __self__.parent.plot.fit_plots != []:
            for plot in __self__.parent.plot.fit_plots: 
                try: plot.pop(0).remove()
                except: pass
        __self__.parent.plot.fit_plots = []
        if len(Constants.FIND_ELEMENT_LIST) > 0: 
            lines = True
        else: 
            lines = False
        
        __self__.parent.plot.DATA.set_ydata(__self__.parent.sum_spectrum)
        __self__.parent.plot.plot.legend().get_texts()[0].set_text(
                f"{__self__.spec_no} Spectra (X: {__self__.x0};{__self__.x1}, Y: {__self__.y0};{__self__.y1})")
        __self__.parent.plot.plot.set_ylim(
                bottom=1,
                top=1.20*__self__.parent.sum_spectrum.max())
        __self__.parent.plot.limits = (__self__.x0, __self__.x1, __self__.y0, __self__.y1)
        try:
            __self__.parent.plot.canvas.draw()
        except: pass

    def on_press(__self__,event):
        __self__.press = True
        try: __self__.x0 = int(event.xdata)
        except: pass
        try: __self__.y0 = int(event.ydata)
        except: pass

    def on_drag(__self__,event):
        if __self__.press and __self__.alive:
            __self__.move = True
            try: __self__.x1 = int(event.xdata)+1
            except: pass
            try: __self__.y1 = int(event.ydata)+1
            except: pass
            __self__.area1.set_width(__self__.x1 - __self__.x0)
            __self__.area2.set_width(__self__.x1 - __self__.x0)
            __self__.area1.set_height(__self__.y1 - __self__.y0)
            __self__.area2.set_height(__self__.y1 - __self__.y0)
            __self__.area1.set_xy((__self__.x0,__self__.y0))
            __self__.area2.set_xy((__self__.x0,__self__.y0))
            __self__.parent.canvas1.draw()
            __self__.parent.canvas2.draw()
            __self__.calculate_area()

            try: __self__.refresh_roi_plot()
            except: pass

    def on_release(__self__,event):
        __self__.press = False
        if __self__.press and not __self__.move:
            __self__.press = False
            __self__.move = False

    def calculate_area(__self__):
        __self__.area1_sum = 0
        __self__.area2_sum = 0
        __self__.spec_no = 0
        __self__.parent.sum_spectrum = np.ones([__self__.parent.DATACUBE.sum.shape[0]],
                dtype="float32")
        unpacker1 = __self__.element1
        unpacker2 = __self__.element2
        
        #print("MPL X:",__self__.x0,__self__.x1)
        #print("MPL Y:",__self__.y0,__self__.y1)
        # in matplotlib canvas directions are swapped
        x_ = [__self__.y0,__self__.y1]
        y_ = [__self__.x0,__self__.x1]
        #print("SHAPE:", __self__.parent.DATACUBE.matrix.shape)
        x_.sort()
        y_.sort()

        #print("x",x_)
        #print("y",y_)
        #print(__self__.parent.DATACUBE.matrix[x_[0]:x_[1],y_[0]:y_[1]].shape)
        
        if unpacker1 != "" or unpacker2 != "":
            image1 = __self__.parent.DATACUBE.unpack_element(unpacker1)
            image2 = __self__.parent.DATACUBE.unpack_element(unpacker2)
        else:
            __self__.parent.sum_spectrum = \
                    __self__.parent.DATACUBE.matrix[x_[0]:x_[1],y_[0]:y_[1]].sum(0).sum(0)
            __self__.spec_no = (y_[1]-y_[0]) * (x_[1]-x_[0])
            return

        #################################################################################
        #NOTE: if the image on display in the panel is a result of masking with         #
        # the correlation plot window, we need to crop the unpacked image to match what #
        # is displayed. Then, coordinates must be changed to pick the corresponding spec#
        #################################################################################
        if __self__.parent.masked:
            x = __self__.parent.crop_y
            y = __self__.parent.crop_x #NOTE: coordinates in matplotlib canvas are swapped
            image1 = image1[x[0]:x[1],y[0]:y[1]]
            image2 = image2[x[0]:x[1],y[0]:y[1]]
            #x_ = [-__self__.y0+image1.shape[0],
            #    -__self__.y1+image1.shape[0]]
            #x_.sort()
            cx = [x_[0]+x[0], x_[0]+x[0]+(x_[1]-x_[0])]
            cy = [y_[0]+y[0], y_[0]+y[0]+(y_[1]-y_[0])]
            __self__.parent.sum_spectrum = \
                    __self__.parent.DATACUBE.matrix[cx[0]:cx[1],cy[0]:cy[1]].sum(0).sum(0)
        else:
            __self__.parent.sum_spectrum = \
                    __self__.parent.DATACUBE.matrix[x_[0]:x_[1],y_[0]:y_[1]].sum(0).sum(0)
        #################################################################################
        
        __self__.area1_sum = image1[x_[0]:x_[1],y_[0]:y_[1]].sum()
        __self__.area2_sum = image2[x_[0]:x_[1],y_[0]:y_[1]].sum()
        __self__.spec_no = (y_[1]-y_[0]) * (x_[1]-x_[0])
        __self__.roibox1["text"] = "Roi 1: {}".format(int(__self__.area1_sum))
        __self__.roibox2["text"] = "Roi 2: {}".format(int(__self__.area2_sum))
        if __self__.area2_sum > 0:
            __self__.ratebox["text"] = "Ratio: {:.2f}".format(
                    __self__.area1_sum/__self__.area2_sum)

class ImageAnalyzer:
    def __init__(__self__,parent,datacube):
        __self__.DATACUBE = datacube
        __self__.masked = 0
        __self__.packed_elements = __self__.DATACUBE.check_packed_elements()
        __self__.sum_spectrum = __self__.DATACUBE.sum
        __self__.master = Toplevel(master=parent.master)
        __self__.master.attributes("-alpha",0.0)
        __self__.master.tagged = False
        __self__.master.title("Image Analyzer")
        __self__.MenuBar = Menu(__self__.master, tearoff=0)
        __self__.Menu = Menu(__self__.MenuBar, tearoff=0)
        __self__.MenuBar.add_cascade(label="More", menu=__self__.Menu)
        __self__.Menu.add_command(label="Navigate by index . . .",
                command=__self__.call_index_navigator)
        
        __self__.alt = False
        __self__.openFrames = []

        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.master.bind("<Alt_L>",__self__.AltOn)
        __self__.master.bind("<KeyRelease-Alt_L>",__self__.AltOff)
        __self__.master.bind("<Return>",__self__.maximize)

        __self__.sampler = Frame(__self__.master)
        __self__.SampleFrame = Frame(__self__.master)
        __self__.LeftCanvas = Canvas(__self__.SampleFrame)
        __self__.RightCanvas = Canvas(__self__.SampleFrame)
        __self__.sliders = ttk.LabelFrame(__self__.master,text="Control Panel")
        __self__.buttons = ttk.Frame(__self__.sliders)
        __self__.buttons1 = ttk.Frame(__self__.sliders)
        __self__.buttons2 = ttk.Frame(__self__.sliders)
        __self__.roibox = ttk.Frame(__self__.buttons, width=80)
        __self__.ColoursPanel = Frame(__self__.master, relief=SUNKEN, height=36)

        __self__.sampler.grid(row=0,column=0,columnspan=2,sticky=W+E)
        __self__.SampleFrame.grid(row=1,column=0,columnspan=2,sticky=W+E+N+S)
        __self__.LeftCanvas.grid(row=0,column=0,sticky=N+S+E+W)
        __self__.RightCanvas.grid(row=0,column=1,sticky=N+S+E+W)
        __self__.ColoursPanel.grid(row=2,column=0,sticky=N+E,pady=(16,3), padx=(3,3))
        __self__.sliders.grid(row=2,column=0,columnspan=2,sticky=N+W+S+E,padx=(16,16),pady=(6,6))
        __self__.buttons.grid(row=0,column=0,padx=(15,30),pady=(6,3),sticky=E)
        __self__.buttons1.grid(row=0,column=1,padx=(5,5),pady=(6,3),sticky=E+W)
        __self__.buttons2.grid(row=0,column=2,padx=(30,15),pady=(6,3),sticky=W)

        __self__.RightCanvas.grid_propagate(1)
        __self__.LeftCanvas.grid_propagate(1)
        __self__.SampleFrame.grid_propagate(1)
        __self__.master.grid_propagate(1)
        __self__.sliders.grid_propagate(1)
        
        __self__.SampleFrame.grid_columnconfigure(0,weight=1)
        __self__.SampleFrame.grid_columnconfigure(1,weight=1)
        __self__.SampleFrame.grid_rowconfigure(0,weight=1)

        Grid.rowconfigure(__self__.SampleFrame, 0, weight=1)
        Grid.columnconfigure(__self__.SampleFrame, 0, weight=1)
        Grid.columnconfigure(__self__.SampleFrame, 1, weight=1)
        Grid.columnconfigure(__self__.sliders, 0, weight=1)
        Grid.columnconfigure(__self__.sliders, 2, weight=1)
        Grid.columnconfigure(__self__.sampler, 0, weight=1)
        Grid.columnconfigure(__self__.sampler, 1, weight=1)
        Grid.columnconfigure(__self__.sampler, 2, weight=1)
        Grid.columnconfigure(__self__.sampler, 3, weight=1)

        __self__.master.grid_columnconfigure(0,weight=1)
        __self__.master.grid_columnconfigure(1,weight=1)
        __self__.master.grid_rowconfigure(1,weight=1)
        __self__.master.config(menu=__self__.MenuBar)

        __self__.build_widgets()

    def call_index_navigator(__self__):
        if hasattr(__self__, "IndexNavigator"):
            pass
        else:
            __self__.IndexNavigator = Navigator(__self__)
        __self__.IndexNavigator.master.focus_set()

    def get_version(__self__):
        """ version attribute was implemented in XISMuS 1.3.0, 
        any cube prior to this version has no version attribute """
        
        def get_old_version():
            if hasattr(__self__.DATACUBE,"update_info"):
                return __self__.DATACUBE.update_info
            elif hasattr(__self__.DATACUBE,"version"): return __self__.DATACUBE.version
            else: return "pre v1.3"

        if hasattr(__self__.DATACUBE,"version"):
            __self__.cube_version = "Cube version: "+get_old_version()
            if hasattr(__self__.DATACUBE,"scalable"):
                __self__.scale.config(state=NORMAL)
            else:
                __self__.scale.config(state=DISABLED)
        else:
            __self__.cube_version = "Cube version: "+get_old_version()
            __self__.scale.config(state=DISABLED)

    def build_widgets(__self__):
        __self__.Map1Var = StringVar()
        __self__.Map1Counts = StringVar()
        __self__.Map1Counts.set("Select an element")
        __self__.Map2Var = StringVar()
        __self__.Map2Counts = StringVar()
        __self__.Map2Counts.set("Select an element")
        __self__.apply_scale_mask = BooleanVar()
        
        try:
            __self__.ElementalMap1 = np.zeros([__self__.DATACUBE.dimension[0],
                    __self__.DATACUBE.dimension[1]])
            __self__.ElementalMap2 = np.zeros([__self__.DATACUBE.dimension[0],
                    __self__.DATACUBE.dimension[1]])
        except:
            __self__.ElementalMap1 = np.zeros([1,1])
            __self__.ElementalMap2 = np.zeros([1,1])
        
        # popup commands
        __self__.popup = Menu(__self__.master, tearoff=0)
        __self__.popup.add_command(
                label="Export as...",
                command=__self__.export_clicked)

        # map 1
        __self__.Map1Label = Label(
                __self__.sampler, 
                textvariable=__self__.Map1Counts,
                width=30)
        __self__.Map1Combo = ttk.Combobox(
                __self__.sampler, 
                textvariable=__self__.Map1Var,
                values=__self__.packed_elements,
                width=10,
                state="readonly")
        
        # map 2
        __self__.Map2Label = Label(
                __self__.sampler, 
                textvariable=__self__.Map2Counts,
                width=30)
        __self__.Map2Combo = ttk.Combobox(
                __self__.sampler, 
                textvariable=__self__.Map2Var,
                values=__self__.packed_elements,
                width=10,
                state="readonly")

        # matplotlib canvases
        __self__.figure1 = Figure(figsize=(5,4), dpi=75)
        __self__.plot1 = __self__.figure1.add_subplot(111)
        __self__.plot1.axis('Off')
        __self__.canvas1 = FigureCanvasTkAgg(__self__.figure1,__self__.LeftCanvas)
        canvas1 = __self__.canvas1.get_tk_widget().pack(fill=BOTH,anchor=N+W,expand=True)
        __self__.canvas1.mpl_connect("button_press_event",
                lambda event: __self__.pop(event,1))
        
        __self__.figure2 = Figure(figsize=(5,4), dpi=75)
        __self__.plot2 = __self__.figure2.add_subplot(111)
        __self__.plot2.axis('Off')
        __self__.canvas2 = FigureCanvasTkAgg(__self__.figure2,__self__.RightCanvas)
        canvas2 = __self__.canvas2.get_tk_widget().pack(fill=BOTH,anchor=N+W,expand=True)
        __self__.canvas2.mpl_connect("button_press_event",
                lambda event: __self__.pop(event,2))

        # image controls Threshold, LowPass and Smooth
        __self__.T1check = BooleanVar()
        __self__.LP1check = BooleanVar()
        __self__.S1check = BooleanVar()
        __self__.BVar = BooleanVar()
        __self__.GVar = BooleanVar()
        __self__.WVar = BooleanVar()
        __self__.BVar.set(True)
        __self__.T2check = BooleanVar()
        __self__.LP2check = BooleanVar()
        __self__.S2check = BooleanVar()
        __self__.T2check.set(False)
        __self__.LP2check.set(False)
        __self__.S2check.set(False)
        __self__.T1check.set(False)
        __self__.LP1check.set(False)
        __self__.S1check.set(False)

        Label(__self__.ColoursPanel,text="Background colour: ").grid(row=0,column=0)
        __self__.Black = ttk.Checkbutton(__self__.ColoursPanel, 
                text="Black",
                takefocus=False, variable=__self__.BVar,
                command=lambda: __self__.set_bg("black"))
        __self__.Grey = ttk.Checkbutton(__self__.ColoursPanel, 
                text="Grey",
                takefocus=False, variable=__self__.GVar,
                command=lambda: __self__.set_bg("#3b3b38"))
        __self__.White = ttk.Checkbutton(__self__.ColoursPanel, 
                text="White",
                takefocus=False, variable=__self__.WVar,
                command=lambda: __self__.set_bg())

        __self__.T1 =ttk.Checkbutton(
                __self__.buttons1,
                takefocus=False,
                text="Threshold (high)",
                variable=__self__.T1check,
                command=__self__.switchLP1T1)
        __self__.LP1 =ttk.Checkbutton(__self__.buttons1,
                takefocus=False,
                text="Threshold (low)",
                variable=__self__.LP1check,
                command=__self__.switchT1LP1)
        __self__.S1 =ttk.Checkbutton(
                __self__.buttons1,
                takefocus=False,
                text="Smooth",
                variable=__self__.S1check,
                command=lambda:__self__.draw_image1(0))
        
        # sliders for image 1
        __self__.T1Slider = ttk.Scale(
                __self__.buttons1, 
                orient='horizontal', 
                from_=0, 
                to=LEVELS,
                command=__self__.draw_image1)
        __self__.LP1Slider = ttk.Scale(
                __self__.buttons1, 
                orient='horizontal', 
                from_=0, 
                to=LEVELS,
                command=__self__.draw_image1)
        __self__.S1Slider = ttk.Scale(
                __self__.buttons1, 
                orient='horizontal', 
                from_=0, 
                to=2,
                command=__self__.draw_image1)

        # image controls Threshold, LowPass and Smooth
        __self__.T2 =ttk.Checkbutton(
                __self__.buttons1, 
                takefocus=False,
                text="Threshold (high)",
                variable=__self__.T2check,
                command=__self__.switchLP2T2)
        __self__.LP2 =ttk.Checkbutton(
                __self__.buttons1, 
                takefocus=False,
                text="Threshold (low)",
                variable=__self__.LP2check,
                command=__self__.switchT2LP2)
        __self__.S2 =ttk.Checkbutton(
                __self__.buttons1, 
                takefocus=False,
                text="Smooth",
                variable=__self__.S2check,
                command=lambda:__self__.draw_image2(0))
               
        # sliders for image 2
        __self__.T2Slider = ttk.Scale(
                __self__.buttons1, 
                orient='horizontal', 
                from_=0, 
                to=LEVELS,
                command=__self__.draw_image2)
        __self__.LP2Slider = ttk.Scale(
                __self__.buttons1, 
                orient='horizontal', 
                from_=0, 
                to=LEVELS,
                command=__self__.draw_image2)
        __self__.S2Slider = ttk.Scale(
                __self__.buttons1, 
                orient='horizontal', 
                from_=0, 
                to=2,
                command=__self__.draw_image2)
    
        # buttons
        __self__.roibox1 = Label(__self__.buttons1,text="Roi 1: None",relief=GROOVE) 
        __self__.roibox2 = Label(__self__.buttons1,text="Roi 2: None",relief=GROOVE)
        __self__.ratebox = Label(__self__.buttons,text="Ratio: None") 
        
        __self__.annotate = Button(
                __self__.buttons,
                text="Set ROI",
                cursor="hand2",
                command=__self__.toggle_annotator,
                relief="raised",
                width=14)
        create_tooltip(__self__.annotate,"When toggled, use the mouse to draw a square in any of the maps above.")
        __self__.correlate = ttk.Button(
                __self__.buttons,
                text="Correlate",
                command=__self__.get_correlation,
                width=round(__self__.annotate.winfo_width()/2))
        __self__.export = ttk.Button(
                __self__.buttons,
                text="Export",
                command=__self__.export_maps,
                width=round(__self__.annotate.winfo_width()/2))
        __self__.subtract_btn = ttk.Button(
                __self__.buttons2,
                text="Add Images",
                command=__self__.add_images,
                width=round(__self__.annotate.winfo_width()/2))
        __self__.add_btn = ttk.Button(
                __self__.buttons2,
                text="Subtract Images",
                command=__self__.subtract_images,
                width=round(__self__.annotate.winfo_width()/2))
        __self__.scale =ttk.Checkbutton(
                __self__.buttons2, 
                takefocus=False,
                text="Apply scaling mask",
                variable=__self__.apply_scale_mask,
                command=__self__.refresh)
        __self__.get_version()
        __self__.CubeVersionLabel = Label(__self__.master,
                text=__self__.cube_version,
                bd=1,
                relief=SUNKEN,
                anchor=W)

        __self__.Map1Label.grid(row=0, column=0, sticky=E)
        __self__.Map1Combo.grid(row=0,column=1, sticky=W,padx=(16,16),pady=(8,4))
        __self__.Map2Label.grid(row=0, column=3, sticky=W)
        __self__.Map2Combo.grid(row=0,column=2, sticky=E,padx=(16,16),pady=(8,4))
        __self__.plot1.grid(b=None)
        __self__.plot2.grid(b=None)

        pady = 6
        __self__.T1Slider.grid(row=1,column=1,pady=pady)
        __self__.LP1Slider.grid(row=2,column=1,pady=pady)
        __self__.S1Slider.grid(row=3,column=1,pady=pady)
        __self__.T2Slider.grid(row=1,column=3,pady=pady)
        __self__.LP2Slider.grid(row=2,column=3,pady=pady)
        __self__.S2Slider.grid(row=3,column=3,pady=pady)
        __self__.T1.grid(row=1,column=0,padx=(0,6),sticky=W,pady=pady)
        __self__.LP1.grid(row=2,column=0,padx=(0,6),sticky=W,pady=pady)
        __self__.S1.grid(row=3,column=0,padx=(0,6),sticky=W,pady=pady)
        __self__.T2.grid(row=1,column=2,padx=(24,6),sticky=W,pady=pady)
        __self__.LP2.grid(row=2,column=2,padx=(24,6),sticky=W,pady=pady)
        __self__.S2.grid(row=3,column=2,padx=(24,6),sticky=W,pady=pady)

        __self__.White.grid(row=0, column=1, padx=6)
        __self__.Grey.grid(row=0, column=2, padx=6)
        __self__.Black.grid(row=0, column=3, padx=6)

        __self__.roibox1.grid(row=0,column=0,columnspan=2,sticky=W+E,pady=(12,6))
        __self__.roibox2.grid(row=0,column=2,columnspan=2,sticky=W+E,pady=(12,6))
        __self__.ratebox.grid(row=2,column=0,columnspan=2,sticky=W+E)
        __self__.export.grid(row=0,column=1,sticky=W+E)
        __self__.correlate.grid(row=0,column=0,sticky=W+E)
        __self__.annotate.grid(row=1,column=0,columnspan=2,sticky=W+E,pady=(3,3))

        __self__.subtract_btn.grid(row=0,column=0,sticky=W+E)
        __self__.add_btn.grid(row=1,column=0,sticky=W+E)
        __self__.scale.grid(row=2,column=0, sticky=W)

        __self__.CubeVersionLabel.grid(row=3,columnspan=2,sticky=W+E)#pack(side=BOTTOM, expand=False, fill=X, anchor=W)

        __self__.Map1Combo.bind("<<ComboboxSelected>>", __self__.update_sample1)
        __self__.Map2Combo.bind("<<ComboboxSelected>>", __self__.update_sample2)
        
        icon = os.path.join(os.getcwd(),"images","icons","img_anal.ico")
        __self__.master.iconbitmap(icon)  

        # Disable sliders
        __self__.T1Slider.state(["disabled"])
        __self__.T2Slider.state(["disabled"])
        __self__.LP1Slider.state(["disabled"])
        __self__.LP2Slider.state(["disabled"])
        
        # presents a first image, if no element maps exist, displays the sum map. 
        __self__.nomaps = False
        try: 
            try: __self__.Map1Combo.current(0)
            except: 
                __self__.nomaps = True
                pass
            try: __self__.Map2Combo.current(1)
            except: 
                try: __self__.Map2Combo.current(0)
                except: pass
            if __self__.ElementalMap1.max() == 0:
                __self__.ElementalMap1 = Constants.MY_DATACUBE.densitymap.astype("float32")*LEVELS/Constants.MY_DATACUBE.densitymap.max()
                __self__.left_image = __self__.plot1.imshow(__self__.ElementalMap1)
                __self__.draw_image1(0)
            else: __self__.left_image = __self__.plot1.imshow(np.zeros([20,20]))
            if __self__.ElementalMap2.max() == 0:
                __self__.ElementalMap2 = Constants.MY_DATACUBE.densitymap.astype("float32")*LEVELS/Constants.MY_DATACUBE.densitymap.max()
                __self__.right_image = __self__.plot2.imshow(__self__.ElementalMap2)
                __self__.draw_image2(0)
            else: __self__.right_image = __self__.plot2.imshow(np.zeros([20,20]))
            __self__.plot1.grid(False)
            __self__.plot2.grid(False)
            __self__.update_sample1(None)
            __self__.update_sample2(None)
        except: 
            pass
        x = __self__.master.winfo_width()
        y = __self__.master.winfo_height()

        __self__.toggle_() 

        __self__.master.minsize(x,y)
        __self__.set_bg("#3b3b38")
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)

    def toggle_(__self__):
        if __self__.nomaps == True:
            __self__.add_btn.config(state=DISABLED)
            __self__.subtract_btn.config(state=DISABLED)
            __self__.correlate.config(state=DISABLED)
            __self__.export.config(state=DISABLED)
            __self__.scale.config(state=DISABLED)
        else:
            __self__.add_btn.config(state=NORMAL)
            __self__.subtract_btn.config(state=NORMAL)
            __self__.annotate.config(state=NORMAL)
            __self__.correlate.config(state=NORMAL)
            __self__.export.config(state=NORMAL)

    def set_bg(__self__,colour="white"):
        if colour == "white":
            __self__.WVar.set(True)
            __self__.GVar.set(False)
            __self__.BVar.set(False)
        elif colour == "#3b3b38":
            __self__.WVar.set(False)
            __self__.GVar.set(True)
            __self__.BVar.set(False)
        elif colour == "black":
            __self__.WVar.set(False)
            __self__.GVar.set(False)
            __self__.BVar.set(True)

        __self__.LeftCanvas.config(bg=colour)
        __self__.RightCanvas.config(bg=colour)
        __self__.figure1.set_facecolor(colour)
        __self__.figure2.set_facecolor(colour)
        __self__.canvas1.draw()
        __self__.canvas2.draw()

    def kill(__self__):
        for widget in __self__.master.winfo_children():
            widget.destroy()
        try: __self__.plot.wipe_plot()
        except: pass
        for frame in __self__.openFrames:
            frame.wipe_plot()
        __self__.master.destroy()
        Constants.ROOT.ImageAnalyzers.remove(__self__)
        gc.collect()
        del __self__

    def refresh(__self__,e=""):
        __self__.draw_image1(0)
        __self__.draw_image2(0)

    def subtract_images(__self__,e=""):
        __self__.OperationDiag = ImageOperationWarning(
                __self__,
                mode="subtract",
                scaled=__self__.apply_scale_mask.get())
        place_center(__self__.master,__self__.OperationDiag.master)

    def add_images(__self__,e=""):
        __self__.OperationDiag = ImageOperationWarning(
                __self__,
                mode="add",
                scaled=__self__.apply_scale_mask.get())
        place_center(__self__.master,__self__.OperationDiag.master)
    
    def AltOn(__self__,e=""):
        __self__.alt = True
    
    def AltOff(__self__,e=""):
        __self__.alt = False

    def maximize(__self__,e=""):
        maximize_window(__self__)

    def pop(__self__,event,img_idx):
        if event.button == 3:
            __self__.triggered_figure = img_idx
            Constants.ROOT.master.update_idletasks()
            x = Constants.ROOT.master.winfo_pointerx()
            y = Constants.ROOT.master.winfo_pointery()
            abs_coord_x = Constants.ROOT.master.winfo_pointerx() - Constants.ROOT.master.winfo_vrootx()
            abs_coord_y = Constants.ROOT.master.winfo_pointery() - Constants.ROOT.master.winfo_vrooty()
            try: __self__.popup.tk_popup(int(abs_coord_x), int(abs_coord_y), entry="")
            finally: __self__.popup.grab_release()
        else: return

    def resize(__self__, event):
        wi = __self__.LeftCanvas.winfo_width()
        hi = __self__.LeftCanvas.winfo_height()
        wi_t = __self__.RightCanvas.winfo_width()
        hi_t = __self__.RightCanvas.winfo_height()

    def toggle_annotator(__self__):
        """ passes the current datacube, so if the user changes it, 
        for the current ImgAnal api open when
        using the annotation function, the cube is still the 
        one loaded when ImgAnal was opened
        the api is passed as argument so the annotator knows where to draw """

        if __self__.annotate.config("relief")[-1] == "raised":
            __self__.annotate.config(relief="sunken")
            __self__.annotate.config(bg="yellow")
            __self__.annotator = Annotator(__self__) 
            __self__.plot = PlotWin(__self__)
            if Constants.LOW_RES == None:
                place_topright(__self__.master, __self__.plot.master)
            elif Constants.LOW_RES == "moderate":
                spawn_center(__self__.plot.master)
            elif Constants.LOW_RES == "high":
                place_center(__self__.master, __self__.plot.master)
            __self__.plot.draw_selective_sum(__self__.DATACUBE,
                    __self__.DATACUBE.sum,
                    Constants.PLOTSCALE,lines=True)
        else:
            __self__.annotate.config(relief="raised")
            __self__.annotate.config(bg=__self__.master.cget("background"))
            __self__.annotator.wipe_annotator()
            __self__.plot.wipe_plot()
 
    def update_sample1(__self__,event=""):
        label1 = "Maximum net counts: {}".format(
                int(__self__.DATACUBE.max_counts[__self__.Map1Var.get()]))
        __self__.Map1Counts.set(label1)
        unpacker = __self__.Map1Var.get()
        __self__.ElementalMap1 = __self__.DATACUBE.unpack_element(unpacker)
        __self__.ElementalMap1 = __self__.ElementalMap1/__self__.ElementalMap1.max()*LEVELS
        __self__.left_image.set_extent([0,__self__.ElementalMap1.shape[1],
            __self__.ElementalMap1.shape[0],0])
        __self__.draw_image1(0)
        try: 
            __self__.annotator.wipe_annotator()
            del __self__.plot
        except: pass
        if __self__.masked: 
            __self__.masked = 0
            __self__.correlate.state(["!disabled"])
            __self__.update_sample2()
     
    def update_sample2(__self__,event=""):
        label2 = "Maximum net counts: {}".format(
                int(__self__.DATACUBE.max_counts[__self__.Map2Var.get()]))
        __self__.Map2Counts.set(label2)
        unpacker = __self__.Map2Var.get()
        __self__.ElementalMap2 = __self__.DATACUBE.unpack_element(unpacker)
        __self__.ElementalMap2 = __self__.ElementalMap2/__self__.ElementalMap2.max()*LEVELS
        __self__.right_image.set_extent([0,__self__.ElementalMap2.shape[1],
            __self__.ElementalMap2.shape[0],0])
        __self__.draw_image2(0)
        try: 
            __self__.annotator.wipe_annotator()
            del __self__.plot
        except: pass
        if __self__.masked:
            __self__.masked = 0
            __self__.correlate.state(["!disabled"])
            __self__.update_sample1()

    def prepare_to_correlate(__self__):
        scalemode = __self__.apply_scale_mask.get()

        unpacker1 = __self__.Map1Var.get()
        unpacker2 = __self__.Map2Var.get()
        Map1 = __self__.DATACUBE.unpack_element(unpacker1)
        Map2 = __self__.DATACUBE.unpack_element(unpacker2)

        CACHEMAP1 = copy.deepcopy(Map1)
        image1 = fast_scaling(__self__.DATACUBE, CACHEMAP1, scalemode)
        CACHEMAP2 = copy.deepcopy(Map2)
        image2 = fast_scaling(__self__.DATACUBE, CACHEMAP2, scalemode)

        th1 = __self__.T1Slider.get()*image1.max()/LEVELS
        tl1 = __self__.LP1Slider.get()*image1.max()/LEVELS

        th2 = __self__.T2Slider.get()*image2.max()/LEVELS
        tl2 = __self__.LP2Slider.get()*image2.max()/LEVELS

        if __self__.T1check.get() == True:
            image1 = fast_threshold(image1,0,th1)
        elif __self__.LP1check.get() == True:
            image1 = fast_threshold(image1,1,tl1)
        if __self__.T2check.get() == True:
            image2 = fast_threshold(image2,0,th2)
        elif __self__.LP2check.get() == True:
            image2 = fast_threshold(image2,1,tl2)
        return image1, image2
    
    def switchT1LP1(__self__):
        if __self__.LP1check.get() == True: __self__.LP1Slider.state(["!disabled"])
        else: __self__.LP1Slider.state(["disabled"])
        if __self__.T1check.get() == True: 
            __self__.T1check.set(False)
            __self__.T1Slider.state(["disabled"])
        __self__.draw_image1(0)

    def switchLP1T1(__self__):
        if __self__.T1check.get() == True: __self__.T1Slider.state(["!disabled"])
        else: __self__.T1Slider.state(["disabled"])
        if __self__.LP1check.get() == True: 
            __self__.LP1check.set(False)
            __self__.LP1Slider.state(["disabled"])
        __self__.draw_image1(0)

    def switchT2LP2(__self__):
        if __self__.LP2check.get() == True: __self__.LP2Slider.state(["!disabled"])
        else: __self__.LP2Slider.state(["disabled"])
        if __self__.T2check.get() == True: 
            __self__.T2check.set(False)
            __self__.T2Slider.state(["disabled"])
        __self__.draw_image2(0)
    
    def switchLP2T2(__self__):
        if __self__.T2check.get() == True: __self__.T2Slider.state(["!disabled"])
        else: __self__.T2Slider.state(["disabled"])
        if __self__.LP2check.get() == True: 
            __self__.LP2check.set(False)
            __self__.LP2Slider.state(["disabled"])
        __self__.draw_image2(0)

    def transform1(__self__,image):
        if __self__.T1check.get() == True:
            if __self__.S1check.get() == True: 
                image = fast_combo(image,0,__self__.T1Slider.get(),__self__.S1Slider.get())
            else:
                image = fast_threshold(image,0,__self__.T1Slider.get())
        elif __self__.LP1check.get() == True:
            if __self__.S1check.get() == True: 
                image = fast_combo(image,1,__self__.LP1Slider.get(),__self__.S1Slider.get())
            else:
                image = fast_threshold(image,1,__self__.LP1Slider.get())
        else:
            if __self__.S1check.get() == True:
                image = fast_smooth(image,__self__.S1Slider.get())
        try:
            __self__.annotate.config(relief="raised")
            __self__.annotate.config(bg=__self__.master.cget("background"))
            __self__.annotator.wipe_annotator()
            del __self__.plot
        except: pass
            
        return image
 
    def transform2(__self__,image):
        if __self__.T2check.get() == True:
            if __self__.S2check.get() == True: 
                image = fast_combo(image,0,__self__.T2Slider.get(),__self__.S2Slider.get())
            else:
                image = fast_threshold(image,0,__self__.T2Slider.get())
        elif __self__.LP2check.get() == True:
            if __self__.S2check.get() == True: 
                image = fast_combo(image,1,__self__.LP2Slider.get(),__self__.S2Slider.get())
            else:
                image = fast_threshold(image,1,__self__.LP2Slider.get())
        else:
            if __self__.S2check.get() == True:
                image = fast_smooth(image,__self__.S2Slider.get())
        try:
            __self__.annotate.config(relief="raised")
            __self__.annotate.config(bg=__self__.master.cget("background"))
            __self__.annotator.wipe_annotator()
            del __self__.plot
        except: pass
         
        return image   
    
    # the Sliders are the widgets that calls draw_image functions
    # they always pass their respective values as argument when using command
    # argument i is there just to make it work. The value passed doesn't change a thing

    def draw_image1(__self__,i):
        scalemode = __self__.apply_scale_mask.get()
        if scalemode: scalemode = 1
        else: scalemode = 0
        __self__.CACHEMAP1 = copy.deepcopy(__self__.ElementalMap1)
        __self__.newimage1 = fast_scaling(__self__.DATACUBE, __self__.CACHEMAP1, scalemode) 
        __self__.newimage1 = __self__.transform1(__self__.newimage1)
        __self__.left_image.set_data(__self__.newimage1)
        __self__.left_image.set_clim(vmin=0, vmax=__self__.newimage1.max())
        __self__.left_image.set_cmap(Constants.COLORMAP)
        __self__.canvas1.draw()
        del __self__.CACHEMAP1
    
    def draw_image2(__self__,i):
        scalemode = __self__.apply_scale_mask.get()
        if scalemode: scalemode = 1
        else: scalemode = 0
        __self__.CACHEMAP2 = copy.deepcopy(__self__.ElementalMap2)
        __self__.newimage2 = fast_scaling(__self__.DATACUBE,__self__.CACHEMAP2, scalemode) 
        __self__.newimage2 = __self__.transform2(__self__.newimage2)
        __self__.right_image.set_data(__self__.newimage2)
        __self__.right_image.set_clim(vmin=0, vmax=__self__.newimage2.max())
        __self__.right_image.set_cmap(Constants.COLORMAP)
        __self__.canvas2.draw()
        del __self__.CACHEMAP2

    def get_correlation(__self__):
        labels = __self__.Map1Var.get(),__self__.Map2Var.get()
        
        """ Transformed and displayed maps are converted to 0-LEVELS scale (usually 255)
        to correlate raw values i.e. the net area contained in each pixel,
        maps must be unpacked from cube again """
        """ This could be avoided by NOT deleting the CACHEMAP variables, but since 
        correlation tool is used much less than the filters (which perform several 
        iterations), the gain in performance is more important in filtering than correlating
        maps """

        #Map1 = copy.deepcopy(__self__.newimage1)
        #Map2 = copy.deepcopy(__self__.newimage2)

        Map1, Map2 = __self__.prepare_to_correlate()

        """ Correlation region must now be limited according to the transformed area
        (any applied filter) and to selected area made with set ROI tool (Annotator class) """
        bar = Busy(1,0)
        bar.update_text("Thinking...")
        

        if __self__.annotate.config("relief")[-1] == "sunken" and \
                __self__.annotator.x0 is not None:
            x = [__self__.annotator.x0, __self__.annotator.x1]
            y = [__self__.annotator.y0, __self__.annotator.y1]
            #y = [Map1.shape[0]-__self__.annotator.y0-1, Map1.shape[0]-__self__.annotator.y1-1]
            x.sort()
            y.sort()
            Map1 = Map1[y[0]:y[1],x[0]:x[1]]
            Map2 = Map2[y[0]:y[1],x[0]:x[1]]
            __self__.crop_x = x
            __self__.crop_y = y
        else: 
            __self__.crop_x = [0,Map1.shape[0]]
            __self__.crop_y = [0,Map1.shape[1]]
        dim = Map1.shape[0]
        bar.progress["maximum"] = dim

        corr = correlate(Map1,Map2,bar=bar)
        if not corr: 
            messagebox.showerror("Error","Cannot correlate an empty image or region!")
            bar.destroybar()
            return
        bar.update_text("Loading plot...")
        corr_plot = PlotWin(__self__)
        corr_plot.draw_correlation(corr,labels,images=[Map1,Map2])
        bar.destroybar()

    def export_clicked(__self__):
        f = filedialog.asksaveasfile(mode='w', 
                    defaultextension=".png",
                    filetypes=[("Portable Network Graphic", "*.png")],
                    title="Save as...")
        if f is None: 
            return
        if __self__.triggered_figure == 1: img = __self__.newimage1
        elif __self__.triggered_figure == 2: img = __self__.newimage2
        else: 
            messagebox.showerror("Error","Could not export.")
            return 1
        write_image(
                img,
                Constants.TARGET_RES, 
                f.name, 
                enhance=Constants.MY_DATACUBE.config["enhance"],
                merge=False)
        __self__.master.focus_set()
        return 0

    def export_maps(__self__):
        export = ExportDiag(__self__)
        return 0

class ExportDiag():
    """ Creates a dialog to export ImageAnalyzer API images.
    Target is the desired output image size. If enhance configuration is True,
    image is interpolated """

    def __init__(__self__, parent):
        __self__.master = Toplevel(master = parent.master)
        __self__.master.grab_set()
        __self__.master.title("Export dialog")
        __self__.parent = parent
        __self__.master.withdraw()
        __self__.master.resizable(False,False)
        __self__.master.bind("<Escape>",__self__.kill)

        __self__.build_widgets()

    def build_widgets(__self__):
        __self__.Frame = Frame(__self__.master, height=64, width=288)
        __self__.Frame.grid(pady=32)
        
        icon1 = PhotoImage(data=ICO_EXPORT1)
        icon2 = PhotoImage(data=ICO_EXPORT2)
        icon3 = PhotoImage(data=ICO_EXPORT_MERGE)
        
        __self__.icon1 = icon1.subsample(1,1)
        __self__.icon2 = icon2.subsample(1,1)
        __self__.icon3 = icon3.subsample(1,1)

        size_x, size_y = 64,64

        __self__.Button1 = ttk.Button(
                __self__.Frame, 
                image=__self__.icon1, 
                style="main.TButton",
                command=lambda:__self__.export(tag=1), 
                width=size_x)
        __self__.Button2 = ttk.Button(
                __self__.Frame, 
                image=__self__.icon2, 
                style="main.TButton",
                command=lambda:__self__.export(tag=2), 
                width=size_x)
        __self__.Button3 = ttk.Button(
                __self__.Frame, 
                image=__self__.icon3, 
                style="main.TButton",
                command=__self__.merge, 
                width=size_x)

        __self__.Button1.grid(row=0,column=0,padx=32)
        __self__.Button2.grid(row=0,column=1,padx=32)
        __self__.Button3.grid(row=0,column=2,padx=32)
        
        __self__.master.update()

        place_center(__self__.parent.master,__self__.master)
        __self__.master.deiconify()
        __self__.master.focus_set()
        icon = os.path.join(os.getcwd(),"images","icons","img_anal.ico")
        __self__.master.iconbitmap(icon)

    def export(__self__,tag=0):
        enhance = __self__.parent.DATACUBE.config["enhance"]
        try:
            if tag == 1: 
                f = filedialog.asksaveasfile(mode='w', 
                        defaultextension=".png",
                        filetypes=[("Portable Network Graphic", "*.png")],
                        title="Save image 1 as...")
                if f is None: 
                    return
                write_image(
                        __self__.parent.newimage1,
                        Constants.TARGET_RES,
                        f.name,
                        enhance=enhance)
            elif tag == 2: 
                f = filedialog.asksaveasfile(mode='w', 
                        defaultextension=".png",
                        filetypes=[("Portable Network Graphic", "*.png")],
                        title="Save image 2 as...")
                if f is None: 
                    return
                write_image(
                        __self__.parent.newimage2,
                        Constants.TARGET_RES,
                        f.name,
                        enhance=enhance)
            else: pass
        except PermissionError as exception: 
            messagebox.showerror("Error!",exception.__class__.__name__)
            return
        __self__.parent.master.focus_set()
        __self__.kill()

    def merge(__self__):
        enhance = __self__.parent.DATACUBE.config["enhance"]
        stack = stackimages(__self__.parent.newimage1,__self__.parent.newimage2)
        f = filedialog.asksaveasfile(mode='w', 
                defaultextension=".png",
                filetypes=[("Portable Network Graphic", "*.png")],
                title="Save merge as...")
        if f is None: 
            return
        write_image(stack,Constants.TARGET_RES,f.name,enhance=enhance,merge=True)
        __self__.kill()

    def kill(__self__,e=""):
        __self__.parent.master.focus_set()
        __self__.parent.master.focus_force()
        __self__.master.grab_release()
        __self__.master.destroy()

class ImageOperationOutput:
    def __init__(__self__, image, el1, el2, operation, cube_datatypes, cube, parent):
        __self__.image = image
        __self__.parent = parent #ImageAnalyzer
        __self__.master = Toplevel()
        __self__.cube = cube
        __self__.master.attributes("-alpha",0.0)
        __self__.alt = False
        __self__.master.bind("<Alt_L>",__self__.AltOn)
        __self__.master.bind("<KeyRelease-Alt_L>",__self__.AltOff)
        __self__.master.bind("<Return>",__self__.maximize)

        __self__.master.title("Result: {} {} {}".format(el1,operation,el2))
        __self__.master.tagged = None
        __self__.master.minsize(width=600,height=480)
        __self__.master.configure(bg='white')
        __self__.master.resizable(True,True)
        __self__.upper = Canvas(__self__.master)
        __self__.upper.config(bg='white')
        __self__.upper.pack(side=TOP, expand=True, fill=BOTH)
        __self__.lower = Frame(__self__.master,height=35)
        __self__.lower.pack(side=BOTTOM, anchor=N, fill=BOTH, expand=0)

        # Save and replace buttons #
        save_icon = PhotoImage(data=ICO_SAVE)
        replace_icon = PhotoImage(data=ICO_RUBIK)
        __self__.SAVE_ICO = save_icon.subsample(1,1)
        __self__.REPLACE_ICO = replace_icon.subsample(1,1)

        __self__.replace = Button(__self__.lower,
                text=" Replace {} in Cube".format(el1),
                image=__self__.REPLACE_ICO,
                compound=LEFT,
                command= lambda: __self__.replace_on_cube(image,el1),
                width=180,
                height=24,
                bd=1,
                pady=10)
        __self__.replace.grid(row=0,column=0,sticky="")
        __self__.save = Button(__self__.lower,
                text=" Save output image",
                image=__self__.SAVE_ICO,
                compound=LEFT,
                command=lambda: __self__.save_image(image),
                width=180,
                bd=1,
                pady=10)
        __self__.save.grid(row=0,column=1,sticky="")

        __self__.figure = Figure(figsize=(5,4), dpi=75)
        __self__.plot = __self__.figure.add_subplot(111)
        __self__.plot.grid(which="both",axis="both")
        __self__.plot.axis("Off")
        __self__.plot.set_title("Result: {} {} {}".format(el1,operation,el2))
        __self__.canvas = FigureCanvasTkAgg(__self__.figure,__self__.upper)
        __self__.canvas.draw()
        __self__.mplCanvas = __self__.canvas.get_tk_widget()
        __self__.mplCanvas.pack(fill=BOTH, anchor=N+W,expand=True)
        __self__.canvas._tkcanvas.pack()
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.wipe_plot)
        if __self__.parent.masked:
            __self__.replace.config(state=DISABLED)
        icon = os.path.join(os.getcwd(),"images","icons","plot.ico")

        if any("temp" in x for x in cube_datatypes):
            __self__.replace.config(state=DISABLED)

        __self__.master.iconbitmap(icon)
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)
        __self__.draw(image)

    def AltOn(__self__,e=""):
        __self__.alt = True

    def AltOff(__self__,e=""):
        __self__.alt = False

    def maximize(__self__,e=""):
        maximize_window(__self__)

    def draw(__self__,image=None):
        __self__.plot.imshow(image, vmin=0, cmap=Constants.COLORMAP)
        spawn_center(__self__.master)

    def replace_on_cube(__self__,image,element):
        p = messagebox.askquestion("Warning!","You are about to replace {} map in your datacube with the output image. This operation is irreversible. Do you want to proceed?".format(element))
        if p =="yes":
            __self__.cube.replace_map(image,element)
            __self__.parent.update_sample1()
            __self__.parent.update_sample2()
            __self__.wipe_plot()
            return
        else: 
            __self__.parent.master.focus_set()
            __self__.master.focus_set()
            return

    def save_image(__self__,image):
        f = filedialog.asksaveasfile(mode='w',
                        defaultextension=".png",
                        filetypes=[("Portable Network Graphic", "*.png")],
                        title="Save as...")
        if f is not None: 
            write_image(image,
                Constants.TARGET_RES,
                f.name,
                enhance=Constants.MY_DATACUBE.config["enhance"],
                save=True)
        else: 
            __self__.master.focus_set()
            return

    def wipe_plot(__self__):
        __self__.parent.openFrames.remove( __self__ )
        __self__.parent.master.focus_set()
        __self__.master.destroy()
        del __self__

class ImageOperationWarning:
    def __init__(__self__,parent,mode=None,scaled=False):
        __self__.master = Toplevel(parent.master)
        __self__.parent = parent
        __self__.scaled = scaled
        __self__.mode = mode
        if mode == "add": 
            __self__.gif_size = 8
            text="Image 2 is going to be added to image 1. Click OK to proceed."
            speed = 200
        if mode == "subtract": 
            text="Image 2 is going to be subtracted from image 1. Click OK to proceed."
            speed = 125
            __self__.gif_size = 11
        __self__.master.geometry("400x330")
        __self__.master.title("Operation Warning")
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.master.resizable(False, False)
        path=os.path.join(os.getcwd(),"images","animation_{}.gif".format(mode))
        __self__.gif = [PhotoImage(file=path,format = 'gif -index %i' %(i),
            master = __self__.master) for i in range(__self__.gif_size)]
        __self__.frameno = 0
        __self__.speed = speed
        __self__.animation = Label(__self__.master, 
                image=__self__.gif[__self__.frameno])
        __self__.text = Label(__self__.master, 
                text=text,
                wraplength=300)
        __self__.ok = ttk.Button(__self__.master,text="OK",width=13,
                command = __self__.perform)
        __self__.animation.pack(side=TOP,fill=BOTH,anchor=CENTER,padx=15,pady=15)
        __self__.ok.pack(side=BOTTOM,anchor=CENTER,padx=15,pady=15)
        __self__.text.pack(side=BOTTOM,fill=BOTH,anchor=CENTER,padx=15)
        icon = os.path.join(os.getcwd(),"images","icons","plot.ico")
        __self__.master.iconbitmap(icon)
        __self__.master.grab_set()
        __self__.master.after(__self__.speed, __self__.update_frame)

    def update_frame(__self__):
        __self__.frameno += 1
        if __self__.frameno >= __self__.gif_size: __self__.frameno = 0
        __self__.frame = __self__.gif[__self__.frameno]
        __self__.animation.configure(image=__self__.frame)
        __self__.master.update()
        __self__.master.after(__self__.speed, __self__.update_frame)

    def kill(__self__):
        __self__.master.grab_release()
        __self__.parent.master.focus_force()
        __self__.master.destroy()
        del __self__

    def perform(__self__):

        from Engine.ImgMath import add as add_
        from Engine.ImgMath import subtract as sub_

        if __self__.mode == "subtract": 
            operation = "minus"
            output = sub_(__self__.parent.newimage1,
                    __self__.parent.newimage2,norm=True)
        elif __self__.mode == "add":
            operation = "plus"
            output = add_(__self__.parent.newimage1,
                    __self__.parent.newimage2,norm=True)
        else: pass
        if output is None: 
            messagebox.showerror("Error!","Images have incompatible shapes!")
            return
        if __self__.scaled:
            output = fast_scaling(__self__.parent.DATACUBE, output, -1)
        
        __self__.parent.openFrames.append( 
            ImageOperationOutput(output,__self__.parent.Map1Var.get(),
                __self__.parent.Map2Var.get(),operation, 
                __self__.parent.DATACUBE.datatypes, __self__.parent.DATACUBE,
                __self__.parent)
        )

        __self__.master.grab_release()
        __self__.master.destroy()
