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
from copy import copy
from email import message
from tkinter import *
from tkinter import ttk
#############

#############
# utilities #
#############
import os
from tkinter import messagebox
from tkinter import filedialog
from tokenize import Double
from turtle import width
from matplotlib.pyplot import text
import numpy as np
#############

#############
# MPL #######
#############
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#############

#############
# Internal ##
#############
import Constants
from Utilities import *
from GUI.AlchemyLab import AlchemyLab, MATERIAL
from Engine import ImgMath
from Engine.SpecMath import datacube
#############


class MplBackendFrame():
    def __init__(__self__, parent, guiCanvas):
        __self__.guiCanvas = guiCanvas
        __self__.guiCanvas.configure(bg='white')
        __self__.parent = parent
        __self__.plotFont = {'fontname':'Arial','fontsize':14}
        __self__.lw = 3
        __self__.plots = []
        __self__.figure = Figure(figsize=(4,3), dpi=75)
        __self__.canvas = FigureCanvasTkAgg(__self__.figure, __self__.guiCanvas)
        __self__.mplCanvas = __self__.canvas.get_tk_widget()
        __self__.mplCanvas.pack(fill=BOTH, anchor=N+W, expand=True)
        __self__.canvas.draw_idle()
        return
    
    def add_toolbar(__self__, toolBarFrame):
        __self__.toolbar = NavigationToolbar(__self__.canvas, toolBarFrame)
        __self__.toolbar.update()
        __self__.canvas._tkcanvas.pack()
        return

    def draw_datacube_image(__self__, datacube: datacube, elementMap=None):
        color = Constants.DEFAULTBTN_COLOR
        rgb = __self__.guiCanvas.winfo_rgb(color)
        color = (rgb[0]/65535, rgb[1]/65535, rgb[2]/65535)
        __self__.figure.set_facecolor( color )
        __self__.plot = __self__.figure.add_subplot(111)
        __self__.plot.grid(b=None)
        __self__.plot.axis('off')
        if elementMap is not None:
            image = datacube.unpack_element( elementMap )
        else:
            image = datacube.densitymap
        
        if __self__.plots != []: __self__.plots.pop(0)
        __self__.plots = __self__.plot.imshow(image, 
                cmap=Constants.COLORMAP, 
                vmin=0,
                vmax=image.max())
        __self__.canvas.draw_idle()
        return

    def draw_histogram(__self__, X):
        __self__.plot = __self__.figure.add_subplot(111)
        __self__.plot.grid(which='both',axis='both')
        __self__.plot.grid(color="black", ls="--", lw=0.5)
        __self__.plot.axis('On')
        __self__.plot.hist( X, bins=(X.size) )
        __self__.canvas.draw_idle()
        return

    def make_3d_plot(__self__, array, zlim=None):
        __self__.plot = __self__.figure.gca(projection = '3d')
        imagesize = array.shape
        imagex = np.arange(imagesize[0])
        imagey = np.arange(imagesize[1])
        Z = []
        X, Y = np.meshgrid(imagex,imagey)
        for i in range(len(array)):
            for j in range(len(array[i])):
                if array[i][j] > 0: Z.append(array[i][j])
                else: Z.append(np.nan)

        depth_matrix = array.transpose()
        __self__.canvas.draw_idle()

        __self__.plot.cla()
        __self__.plot.plot_surface(
            X,
            Y,
            depth_matrix,
            cmap='BuGn',
            linewidth=0,
            rstride=6,
            cstride=6,
            antialiased=False)
        ImgMath.set_axes_equal(__self__.plot, zlim)
        __self__.plot.elev = 24
        __self__.canvas.draw()
        return


class HeighMappingMain:
    def __init__(__self__, parent, datacube: datacube):
        __self__.datacube = datacube
        __self__.parent = parent
        __self__.master = Toplevel(master = parent.master)
        __self__.master.title("Differential Attenuation Utility")
        __self__.master.iconbitmap(os.path.join(os.getcwd(),"images","icons","adv.ico"))
        __self__.master.attributes("-alpha", 0.0)
        __self__.master.resizable(True, True)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.build_widgets()
        __self__.datacubePlot.draw_datacube_image( __self__.datacube )
        __self__.animatedPlot.make_3d_plot( np.zeros( __self__.datacube.densitymap.shape ), zlim=1 )
        __self__.histogramPlot.draw_histogram( np.arange(20) )
        __self__.master.after( 100, __self__.master.attributes, "-alpha", 1.0 )
        __self__.master.focus_force()
        __self__.master.grab_set()
        w, h = __self__.master.winfo_width(), __self__.master.winfo_height()
        __self__.master.minsize(w,h)
        return

    def build_widgets(__self__):
        framePadding = 10
        w = 20

        # left panel
        __self__.rightPanel = ttk.LabelFrame(__self__.master, text="Results", padding=framePadding)
        __self__.histogramFrame = ttk.Frame(__self__.rightPanel)
        __self__.histogramCanvas = Canvas(__self__.histogramFrame)
        __self__.animatedPlotFrame = ttk.Frame(__self__.rightPanel)
        __self__.animatedPlotFrameCanvas = Canvas(__self__.animatedPlotFrame)
        __self__.animatedPlotFrameOption = ttk.Frame(__self__.animatedPlotFrame)

        # right panel
        __self__.symbol = StringVar()
        __self__.ratio = DoubleVar()
        __self__.theta = DoubleVar()
        __self__.diagram = PhotoImage( file=os.path.join( os.getcwd(), "images", "diagram.png") )
        __self__.leftPanel = ttk.LabelFrame(__self__.master, text="Control panel", padding=framePadding)
        __self__.leftPanelRowOne = ttk.Frame(__self__.leftPanel)
        __self__.diagramPanel = ttk.Frame(__self__.leftPanelRowOne, padding=framePadding)
        __self__.diagramImage = Label(__self__.diagramPanel, image=__self__.diagram)
        __self__.formFrame = ttk.LabelFrame(__self__.leftPanelRowOne, text="Model parameters", padding=framePadding)
        __self__.entryTheta = ttk.Entry(__self__.formFrame, textvariable=__self__.theta, width=w)
        __self__.entryRatio = ttk.Entry(__self__.formFrame, textvariable=__self__.ratio, width=w)
        __self__.entrySymbol = ttk.Entry(__self__.formFrame, textvariable=__self__.symbol, width=w)
        __self__.createMaterial = ttk.Button(__self__.formFrame, text="Set layer material", command=__self__.open_alchemy)
        __self__.startButton = ttk.Button(__self__.formFrame, text="Start!", command=__self__.run_differential_attenuation)
        __self__.cancelButton = ttk.Button(__self__.formFrame, text="Exit", command=__self__.kill)

        # right panel second row (datacube and material display)
        __self__.roiX = StringVar()
        __self__.roiY = StringVar()
        __self__.ratioBetweenMaps = StringVar()
        __self__.selectedPixels = StringVar()
        __self__.selectedMaps = StringVar()
        __self__.roiX.set("X: Full")
        __self__.roiY.set("Y: Full")
        __self__.ratioBetweenMaps.set("Ratio: None")
        __self__.selectedMaps.set("Using maps: None")
        __self__.selectedPixels.set(f"Selected pixels: {__self__.datacube.densitymap.size}")

        __self__.leftPanelRowTwo = ttk.LabelFrame(__self__.leftPanel, text="Datacube and Material", padding=framePadding)
        __self__.datacubeFrame = ttk.Frame(__self__.leftPanelRowTwo)
        __self__.materialFrame = ttk.Frame(__self__.leftPanelRowTwo)
        __self__.materialLabels = ttk.Label(__self__.materialFrame, text="Material properties")
        __self__.materialName = Listbox(__self__.materialFrame, bd=1, highlightthickness=0)
        __self__.datacubeDisplayFrame = ttk.Frame(__self__.datacubeFrame)
        __self__.datacubeDisplayCanvas = Canvas(__self__.datacubeDisplayFrame)
        __self__.datacubeOptionsFrame = ttk.Frame(__self__.datacubeFrame)
        __self__.mapSelectorOne = ttk.Combobox(__self__.datacubeOptionsFrame, values=__self__.datacube.check_packed_elements(), width=20)
        __self__.mapSelectorTwo = ttk.Combobox(__self__.datacubeOptionsFrame, values=__self__.datacube.check_packed_elements(), width=20)
        __self__.toggleAnnotatorButton = ttk.Button(__self__.datacubeOptionsFrame, text="Toggle area selection", width=10, command=__self__.toggle_annotator)
        __self__.leftPanelFooter = Frame(__self__.leftPanel, relief=GROOVE, bd=1)
        __self__.statusLabelDatacubeName = Label(__self__.leftPanelFooter, text=f"Datacube name: {__self__.datacube.name}")
        __self__.statusLabelRoiX = Label(__self__.leftPanelFooter, textvariable=__self__.roiX, width=10)
        __self__.statusLabelRoiY = Label(__self__.leftPanelFooter, textvariable=__self__.roiY, width=10)
        __self__.statusLabelRatioBetween = Label(__self__.leftPanelFooter, textvariable=__self__.ratioBetweenMaps, width=15)
        __self__.statusLabelSelectedPixels = Label(__self__.leftPanelFooter, textvariable=__self__.selectedPixels, width=17)
        __self__.statusLabelSelectedMaps = Label(__self__.leftPanelFooter, textvariable=__self__.selectedMaps)

        __self__.leftPanel.grid(row=0, column=0, sticky="NSEW", padx=(framePadding, 0), pady=(0, framePadding))
        __self__.rightPanel.grid(row=0, column=1, sticky="NSEW", padx=(0, framePadding), pady=(0, framePadding))
        __self__.histogramFrame.grid(row=0, sticky="NSEW")
        __self__.histogramCanvas.grid(sticky="NSEW")
        __self__.animatedPlotFrame.grid(row=1, sticky="NSEW")
        __self__.animatedPlotFrameCanvas.grid(sticky="NSEW")
        __self__.animatedPlotFrameOption.grid(row=1, sticky="NSEW")
        __self__.leftPanelRowOne.grid(row=0, sticky="NSEW")
        __self__.diagramPanel.grid(row=0, column=0, sticky="NSEW")
        __self__.diagramImage.grid(row=0)
        __self__.formFrame.grid(row=0, column=1, sticky="NSEW")
        __self__.entryTheta.grid(row=0, column=1)
        __self__.entryRatio.grid(row=1, column=1)
        __self__.entrySymbol.grid(row=2, column=1)
        __self__.createMaterial.grid(row=3, columnspan=2, sticky="NSEW",pady=(10,10))
        __self__.startButton.grid(row=4, column=0, sticky="NSEW", padx=(0,10))
        __self__.cancelButton.grid(row=4, column=1, sticky="NSEW", padx=(10,0))
        __self__.leftPanelRowTwo.grid(row=1, sticky="NSEW")
        __self__.datacubeFrame.grid(row=0, column=0, sticky="NSEW")
        __self__.materialFrame.grid(row=0, column=1, sticky="NSEW", padx=(framePadding, 0))
        __self__.materialLabels.grid(row=0)
        __self__.materialName.grid(row=1, column=0, sticky="NSEW")
        __self__.datacubeDisplayFrame.grid(row=0, sticky="NSEW") 
        __self__.datacubeDisplayCanvas.grid(sticky="NSEW")

        __self__.datacubeOptionsFrame.grid(row=1, sticky="NSEW")
        __self__.toggleAnnotatorButton.grid(row=0, column=0, sticky="E", padx=(10, 10), pady=(10,5))
        ttk.Label(__self__.datacubeOptionsFrame, text="Map one:").grid(row=0, column=1, sticky="W", pady=(10,5))
        __self__.mapSelectorOne.grid(row=0, column=2, sticky="W", pady=(10,5), padx=(5,15))
        ttk.Label(__self__.datacubeOptionsFrame, text="Map two:").grid(row=0, column=3, sticky="W", pady=(10,5))
        __self__.mapSelectorTwo.grid(row=0, column=4, sticky="W", pady=(10,5), padx=(5,15))

        __self__.leftPanelFooter.grid(row=2, sticky="NSEW", pady=(10,0))
        __self__.statusLabelDatacubeName.grid(row=0, column=0)
        ttk.Label(__self__.leftPanelFooter, text=" | ").grid(row=0, column=1)
        __self__.statusLabelRoiX.grid(row=0, column=2)
        ttk.Label(__self__.leftPanelFooter, text=" | ").grid(row=0, column=3)
        __self__.statusLabelRoiY.grid(row=0, column=4)
        ttk.Label(__self__.leftPanelFooter, text=" | ").grid(row=0, column=5)
        __self__.statusLabelRatioBetween.grid(row=0, column=6)
        ttk.Label(__self__.leftPanelFooter, text=" | ").grid(row=0, column=7)
        __self__.statusLabelSelectedPixels.grid(row=0, column=8)
        ttk.Label(__self__.leftPanelFooter, text=" | ").grid(row=0, column=9)
        __self__.statusLabelSelectedMaps.grid(row=0, column=10)

        __self__.master.grid_rowconfigure(0, weight=1)
        __self__.master.grid_columnconfigure(0, weight=1)
        __self__.master.grid_columnconfigure(1, weight=2)
        __self__.leftPanel.grid_rowconfigure(1, weight=1)
        __self__.leftPanel.grid_columnconfigure(0, weight=1)
        __self__.leftPanelRowTwo.grid_rowconfigure(0, weight=1)
        __self__.leftPanelRowTwo.grid_columnconfigure(0, weight=1)
        __self__.leftPanelRowOne.grid_columnconfigure(0, weight=1)
        __self__.rightPanel.grid_columnconfigure(0, weight=1)
        __self__.rightPanel.grid_rowconfigure(0, weight=1)
        __self__.rightPanel.grid_rowconfigure(1, weight=1)

        __self__.histogramFrame.grid_columnconfigure(0, weight=1)
        __self__.histogramFrame.grid_rowconfigure(0, weight=1)
        __self__.datacubeFrame.grid_columnconfigure(0, weight=1)
        __self__.datacubeFrame.grid_rowconfigure(0, weight=1)
        __self__.datacubeDisplayFrame.grid_columnconfigure(0, weight=1)
        __self__.datacubeDisplayFrame.grid_rowconfigure(0, weight=1)
        __self__.animatedPlotFrame.grid_columnconfigure(0, weight=1)
        __self__.animatedPlotFrame.grid_rowconfigure(0, weight=1)
        __self__.materialFrame.grid_rowconfigure(1, weight=1)

        ttk.Label(__self__.formFrame, text="Theta:", width=w).grid(row=0, column=0, sticky="W")
        ttk.Label(__self__.formFrame, text="Thick ratio:", width=w).grid(row=1, column=0, sticky="W")
        ttk.Label(__self__.formFrame, text="Matrix element:", width=w).grid(row=2, column=0, sticky="W")

        __self__.datacubePlot = MplBackendFrame(__self__, __self__.datacubeDisplayCanvas)
        __self__.animatedPlot = MplBackendFrame(__self__, __self__.animatedPlotFrameCanvas)
        __self__.histogramPlot = MplBackendFrame(__self__, __self__.histogramCanvas)
        return

    def kill(__self__):
        __self__.master.destroy()
        __self__.parent.heightMapping = None
        __self__.parent.master.focus_set()
        del __self__
        return

    def open_alchemy(__self__):
        if not hasattr(__self__, "AlchemyLab"):
            __self__.AlchemyLab = AlchemyLab( __self__ )
        else: pass
        return

    def display_material(__self__):
        symbols = []
        values = []
        __self__.materialName.delete( 0, END )
        for symbol, value in MATERIAL.weight.items():
            symbols.append( symbol )
            values.append( value )
        for symbol, value in zip( symbols, values ):
            __self__.materialName.insert( 0, f"{symbol}, \t{value * 100:.2f}%" )
        __self__.materialName.update_idletasks()
        return

    def run_differential_attenuation(__self__):

        def prompt_path():
            path = filedialog.askdirectory(parent=__self__.master,
                title="Select output folder")
            if path == "":
                return __self__.datacube.path
            else:
                return path

        compound = MATERIAL

        angle = __self__.theta.get()
        attenuatedElement = __self__.symbol.get()
        thickRatio = __self__.ratio.get()
        
        messagebox.showinfo("Info","We will be runnig with the following parameters:" +
            f"\nTheta angle: {angle}" + 
            f"\nAttenuated element (from within matrix): {attenuatedElement}" + 
            f"\nInfinitely thick ratio (matrix): {thickRatio}" + 
            f"\nIntensity (Alpha/Beta): {__self__.mapSelectorOne.get()} / {__self__.mapSelectorTwo.get()}")
        ratioMatrix = __self__.datacube.unpack_element( __self__.mapSelectorOne.get() ) / __self__.datacube.unpack_element( __self__.mapSelectorTwo.get() )
        mask = ratioMatrix # means no mask at all

        compound.set_attenuation( attenuatedElement )
        if hasattr(__self__, "Annotator"):
            mask = np.zeros( ratioMatrix.shape )
            x_ = [__self__.Annotator.y0, __self__.Annotator.y1]
            y_ = [__self__.Annotator.x0, __self__.Annotator.x1]
            x_.sort()
            y_.sort()
            x0, x1 = x_[0], x_[1]
            y0, y1 = y_[0], y_[1]
            mask[x0:x1, y0:y1] = 1
        else: mask = ratioMatrix

        hist, avg, d = ImgMath.getheightmap( 
            ratioMatrix, 
            mask,
            thickRatio,
            compound, 
            path=prompt_path(),
            angle=angle)
        
        __self__.animatedPlot.make_3d_plot( hist, zlim=hist.max() )
        print( avg, d )
        return

    def toggle_annotator(__self__,  e=""):
        if not hasattr(__self__, "Annotator"):
            __self__.Annotator = Annotator( __self__ )
        else: __self__.Annotator.wipe_annotator()


class Annotator:
    """ Creates an annotator to select areas on matplotlib canvases
    Annotator is invoked from Image Analyzer and is destroyed when Set ROI
    button is toggled off """

    def __init__(__self__, parent: HeighMappingMain):
        __self__.parent = parent
        __self__.alive = True
        __self__.element1 = parent.mapSelectorOne.get()
        __self__.element2 = parent.mapSelectorTwo.get()
        __self__.parent.selectedMaps.set(f"Using maps {__self__.element1} and {__self__.element2}")
        __self__.ratebox = parent.ratioBetweenMaps
        __self__.area = Rectangle((0,0),1,1,fill=False,snap=True,color="red",linewidth=3)
        __self__.x0 = None
        __self__.y0 = None
        __self__.x1 = None
        __self__.y1 = None
        __self__.parent.datacubePlot.plot.add_patch(__self__.area)
        __self__.parent.datacubePlot.canvas.mpl_connect("button_press_event", __self__.on_press)
        __self__.parent.datacubePlot.canvas.mpl_connect("motion_notify_event", __self__.on_drag)
        __self__.parent.datacubePlot.canvas.mpl_connect("button_release_event", __self__.on_release)
        __self__.press, __self__.move = False, False
        return

    def refresh_annotator(__self__):
        __self__.element1 = __self__.parent.Map1Var.get()
        __self__.element2 = __self__.parent.Map2Var.get()
        __self__.area.remove()
        __self__.parent.datacubePlot.canvas.draw()
        __self__.parent.datacubePlot.add_patch(__self__.area)
        return

    def wipe_annotator(__self__):
        __self__.area.remove()
        __self__.parent.datacubePlot.canvas.draw()
        __self__.parent.ratioBetweenMaps.set("Ratio: None")
        __self__.parent.datacubePlot.canvas.mpl_connect("button_press_event", __self__.do_nothing)
        __self__.parent.datacubePlot.canvas.mpl_connect("button_notify_event", __self__.do_nothing)
        __self__.parent.datacubePlot.canvas.mpl_connect("button_release_event", __self__.do_nothing)
        __self__.parent.roiX.set("X: Full")
        __self__.parent.roiY.set("Y: Full")
        __self__.parent.ratioBetweenMaps.set("Ratio: None")
        __self__.parent.selectedPixels.set(f"Selected pixels: {__self__.parent.datacube.densitymap.size}")
        __self__.parent.selectedMaps.set("Using maps: None")
        __self__.parent.master.after( 50, delattr(__self__.parent, "Annotator") )
        __self__.alive = False #prevents on_drag from working
        del __self__
        return

    def do_nothing(__self__, e=""):
        """ doing bunches of nothing """
        return

    def on_press(__self__, event):
        __self__.press = True
        try: __self__.x0 = int(event.xdata)
        except: pass
        try: __self__.y0 = int(event.ydata)
        except: pass

    def on_drag(__self__, event):
        if __self__.press and __self__.alive:
            __self__.move = True
            try: __self__.x1 = int(event.xdata)+1
            except: pass
            try: __self__.y1 = int(event.ydata)+1
            except: pass
            __self__.area.set_width(__self__.x1 - __self__.x0)
            __self__.area.set_height(__self__.y1 - __self__.y0)
            __self__.area.set_xy((__self__.x0,__self__.y0))
            __self__.parent.datacubePlot.canvas.draw()
            __self__.calculate_area()
        return

    def calculate_area(__self__,  e=""):
        __self__.area1Sum = 0
        __self__.area2Sum = 0
        __self__.selectedPixels = 0
        unpacker1 = __self__.element1
        unpacker2 = __self__.element2
        x_ = [__self__.y0,__self__.y1]
        y_ = [__self__.x0,__self__.x1]
        x_.sort()
        y_.sort()
        
        if unpacker1 != "" or unpacker2 != "":
            image1 = __self__.parent.datacube.unpack_element(unpacker1)
            image2 = __self__.parent.datacube.unpack_element(unpacker2)
        else:
            image1 = __self__.parent.datacube.densitymap
            image2 = image1
        
        __self__.area1Sum = image1[x_[0]:x_[1],y_[0]:y_[1]].sum()
        __self__.area2Sum = image2[x_[0]:x_[1],y_[0]:y_[1]].sum()
        __self__.selectedPixels = (y_[1]-y_[0]) * (x_[1]-x_[0])
        if __self__.area2Sum > 0:
            ratio = __self__.area1Sum / __self__.area2Sum
        else: ratio = 0

        __self__.parent.ratioBetweenMaps.set(f"Ratio: {ratio:.4f}")
        __self__.parent.selectedPixels.set(f"Selected pixels: {__self__.selectedPixels}")
        __self__.parent.roiX.set(f"X: {x_}")
        __self__.parent.roiY.set(f"Y: {y_}")
        __self__.parent.datacubeOptionsFrame.update_idletasks()
        return

    def on_release(__self__,  e=""):
        __self__.press = False
        if __self__.press and not __self__.move:
            __self__.press = False
            __self__.move = False
