#################################################################
#                                                               #
#          Index Navigator Module for Image Analyzer            #
#                        version: 2.3.0 - Apr - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

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
# Utilities #
#############
import os, sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib import style
style.use('ggplot')
#############
import Constants
    

class Navigator():
    def __init__(__self__,parent):
        __self__.master = Toplevel(master=parent.master)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.master.title("Index navigator")
        __self__.master.geometry("1280x600")
        __self__.master.attributes("-alpha",0.0)
        __self__.parent = parent
        __self__.LeftCanvas = Canvas(__self__.master, bg="white")
        __self__.RightCanvas = Canvas(__self__.master, bg="white")
        __self__.Footer = ttk.LabelFrame(__self__.master,text="Commands",padding=12)
        __self__.BarL = ttk.Frame(__self__.Footer)
        __self__.BarR = ttk.Frame(__self__.Footer)
        __self__.Footer.grid(row=1,column=0,columnspan=2,pady=6,padx=6,sticky=N+S+E+W)
        __self__.LeftCanvas.grid(row=0,column=0,sticky=N+S+E+W)
        __self__.RightCanvas.grid(row=0,column=1,sticky=N+S+E+W)
        __self__.BarL.grid(row=0,column=0,sticky=W+E)
        __self__.BarR.grid(row=0,column=1,sticky=W+E)

        ###########################################################
        __self__.FigureLeft = Figure(figsize=(5,4), dpi=75)
        __self__.PlotLeft = __self__.FigureLeft.add_subplot(111)
        __self__.PlotLeft.grid(which="both",axis="both")
        __self__.PlotLeft.axis("Off")
        __self__.PlotCanvasL = FigureCanvasTkAgg(__self__.FigureLeft,__self__.LeftCanvas)
        __self__.PlotCanvasL.draw()
        __self__.mplCanvasL = __self__.PlotCanvasL.get_tk_widget()
        __self__.mplCanvasL.pack(fill=BOTH, anchor=N+W,expand=True)
        __self__.PlotCanvasL._tkcanvas.pack()
        ###########################################################
        __self__.FigureRight = Figure(figsize=(4,3), dpi=75)
        __self__.PlotRight = __self__.FigureRight.add_subplot(111)
        __self__.PlotRight.grid(which='both',axis='both')
        __self__.PlotRight.grid(color="gray", ls="--", lw=1)
        __self__.PlotRight.set_facecolor("white")
        __self__.PlotRight.axis('On')
        __self__.PlotCanvasR = FigureCanvasTkAgg(__self__.FigureRight,__self__.RightCanvas)
        __self__.PlotCanvasR.draw()
        __self__.mplCanvasR = __self__.PlotCanvasR.get_tk_widget()
        __self__.mplCanvasR.pack(fill=BOTH, anchor=N+W,expand=True)
        __self__.PlotCanvasR._tkcanvas.pack()
        ###########################################################
        __self__.build_widgets()

    def build_widgets(__self__):
        icon = os.path.join(os.getcwd(),"images","icons","adv.ico")
        __self__.master.iconbitmap(icon)
        __self__.PlotRight.spines["top"].set_linewidth(2)
        __self__.PlotRight.spines["bottom"].set_linewidth(2)
        __self__.PlotRight.spines["left"].set_linewidth(2)
        __self__.PlotRight.spines["right"].set_linewidth(2)

        __self__.Slider = ttk.Scale(
                __self__.BarR,
                orient="horizontal",
                from_=1,
                to=__self__.parent.DATACUBE.energyaxis.size,
                command=__self__.update_index)
        __self__.ValueDisplay = ttk.Label(__self__.BarR,
                text="Value")
        __self__.PackImage = ttk.Button(__self__.BarL, text="Pack slice to Datacube",
                command=__self__.save_to_datacube)
        __self__.DisplayImage = __self__.parent.DATACUBE.densitymap
        __self__.LeftImage = __self__.PlotLeft.imshow(
                __self__.DisplayImage,
                cmap=Constants.COLORMAP)
        __self__.PlotRight.plot(
                __self__.parent.DATACUBE.energyaxis,
                __self__.parent.DATACUBE.sum,
                label="Summation spec",
                color="blue")
        __self__.VerticalLine = __self__.PlotRight.axvline(
                x=0,
                color="tomato",
                linewidth=2,
                label="Index")

        __self__.Slider.grid(row=0,column=0,sticky=W+E,padx=(36,0))
        __self__.ValueDisplay.grid(row=0,column=1,sticky=W,padx=(12,0))
        __self__.PackImage.grid(row=0,column=0,sticky=W,padx=(12,0))
        __self__.PlotRight.set_xlim([
            __self__.parent.DATACUBE.energyaxis.min(),
            __self__.parent.DATACUBE.energyaxis.max()])
        __self__.PlotRight.set_ylabel("Counts")
        __self__.PlotRight.set_xlabel("Energy (KeV)")
        if Constants.PLOTSCALE == "-semilogy":
            __self__.PlotRight.set_yscale("log")
        __self__.PlotRight.set_ylim([1,__self__.parent.DATACUBE.sum.max()*1.20])
        __self__.PlotRight.legend(
                    fancybox=True,
                    shadow=True,
                    fontsize=12,
                    framealpha=1,
                    borderpad=1,
                    loc="upper right",
                    facecolor="white")
        Grid.rowconfigure(__self__.master, 0, weight=1)
        Grid.rowconfigure(__self__.LeftCanvas, 0, weight=1)
        Grid.rowconfigure(__self__.RightCanvas, 0, weight=1)
        Grid.columnconfigure(__self__.master, 0, weight=1)
        Grid.columnconfigure(__self__.master, 1, weight=2)
        Grid.columnconfigure(__self__.Footer, 0, weight=1)
        Grid.columnconfigure(__self__.Footer, 1, weight=1)
        Grid.columnconfigure(__self__.BarR, 0, weight=1)
        Grid.columnconfigure(__self__.BarR, 1, weight=0)
        Grid.columnconfigure(__self__.LeftCanvas, 0, weight=1)
        Grid.columnconfigure(__self__.RightCanvas, 0, weight=1)
        __self__.PlotCanvasR.draw()
        __self__.PlotCanvasL.draw()
        __self__.set_bg()
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)

    def set_bg(__self__,colour="#3b3b38"):
        __self__.LeftCanvas.config(bg=colour)
        __self__.RightCanvas.config(bg=colour)
        __self__.FigureLeft.set_facecolor(colour)
        __self__.FigureRight.set_facecolor(colour)
        if colour != "white":
            __self__.PlotRight.xaxis.label.set_color("white")
            __self__.PlotRight.yaxis.label.set_color("white")
            __self__.PlotRight.tick_params(axis="x", colors="white")
            __self__.PlotRight.tick_params(axis="y", colors="white")
            __self__.PlotRight.spines["top"].set_color("white")
            __self__.PlotRight.spines["bottom"].set_color("white")
            __self__.PlotRight.spines["left"].set_color("white")
            __self__.PlotRight.spines["right"].set_color("white")
        else:
            __self__.PlotRight.xaxis.label.set_color("black")
            __self__.PlotRight.yaxis.label.set_color("black")
            __self__.PlotRight.tick_params(axis="x", colors="black")
            __self__.PlotRight.tick_params(axis="y", colors="black")
            __self__.PlotRight.spines["top"].set_color("black")
            __self__.PlotRight.spines["bottom"].set_color("black")
            __self__.PlotRight.spines["left"].set_color("black")
            __self__.PlotRight.spines["right"].set_color("black")
        __self__.PlotCanvasL.draw()
        __self__.PlotCanvasR.draw()

    def save_to_datacube(__self__,e=""):
        value = __self__.parent.DATACUBE.energyaxis[int(__self__.Slider.get())-1]
        __self__.parent.DATACUBE.pack_element(__self__.DisplayImage,"Slice",f"{value:.2f}")
        __self__.parent.packed_elements = __self__.parent.DATACUBE.check_packed_elements()
        if __self__.parent.nomaps:
            __self__.parent.nomaps = False
            __self__.parent.toggle_()
            __self__.parent.Map1Combo.set(__self__.parent.packed_elements[0])
            __self__.parent.Map2Combo.set(__self__.parent.packed_elements[0])
        __self__.parent.Map1Combo.configure(values=__self__.parent.packed_elements)
        __self__.parent.Map2Combo.configure(values=__self__.parent.packed_elements)
        __self__.parent.Map1Combo.update()
        __self__.parent.Map2Combo.update()
        __self__.parent.update_sample1()
        __self__.parent.update_sample2()
        __self__.parent.master.update()

    def update_index(__self__,e=""):
        idx = int(__self__.Slider.get())-1
        value = __self__.parent.DATACUBE.energyaxis[idx]
        __self__.DisplayImage = __self__.parent.DATACUBE.matrix[:,:,idx].astype(np.float32)
        __self__.ValueDisplay.configure(text=f"{value:.2f}")
        __self__.VerticalLine.set_xdata(value)
        __self__.LeftImage.set_data(__self__.DisplayImage)
        __self__.LeftImage.set_clim(0,__self__.DisplayImage.max())
        __self__.PlotCanvasL.draw_idle()
        __self__.PlotCanvasR.draw_idle()
        
    def kill(__self__):
        del __self__.parent.IndexNavigator
        __self__.master.destroy()

