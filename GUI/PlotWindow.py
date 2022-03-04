
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

#############
# Utilities #
#############
from ast import Constant
import os
import numpy as np
#############

#################
# Local imports #
#################
import Constants
Constants.LOGGER.info("In ImageAnalyzer: Importing local modules...")
from GUI import create_tooltip
from GUI import Mask
from GUI import SimpleFitPanel
import Engine
from Engine.ImgMath import LEVELS, write_image
from Engine.CBooster import *
from Engine.SpecMath import getstackplot, peakstrip, linregress
from Utilities import *
from Graphics import *
from Elements import *
#################

####################
# External modules #
####################
try:
    from numba import jit
except:
    print("Failed to load numba")
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import font as tkFont
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
####################

class PlotWin:
    def __init__(__self__,parent):
        __self__.parent = parent
        __self__.master = Toplevel(master=parent.master)
        __self__.master.attributes("-alpha",0.0)
        __self__.alt = False
        __self__.master.bind("<Alt_L>",__self__.AltOn)
        __self__.master.bind("<KeyRelease-Alt_L>",__self__.AltOff)
        __self__.master.bind("<Return>",__self__.maximize)
        __self__.master.title("Plot")

        __self__.master.minsize(width=600,height=480)
        __self__.master.configure(bg='white')
        __self__.master.resizable(True,True) 
        __self__.plot_font = {'fontname':'Arial','fontsize':14}

        __self__.lw = 3                 #plot linewidth
        __self__.master.tagged = None
        __self__.limits = ()            #boundaries of selected region with Annotator class
        __self__.menubar = Menu(__self__.master, tearoff=0)
        __self__.options = Menu(__self__.menubar, tearoff=0)
        __self__.upper = Canvas(__self__.master)
        __self__.upper.config(bg='white')
        __self__.lower = Frame(__self__.master,height=35)

        __self__.upper.pack(side=TOP, expand=True, fill=BOTH, padx=(16,16),pady=(16,16))
        __self__.lower.pack(side=BOTTOM, anchor=N, fill=BOTH, expand=0)
        
        __self__.figure = Figure(figsize=(4,3), dpi=60)
        __self__.plot = __self__.figure.add_subplot(111)
        __self__.plot.grid(which='both',axis='both')
        __self__.plot.grid(color="black", ls="--", lw=0.5)
        __self__.plot.axis('On')
        __self__.canvas = FigureCanvasTkAgg(__self__.figure,__self__.upper)
        __self__.canvas.draw()
        __self__.mplCanvas = __self__.canvas.get_tk_widget()
        __self__.mplCanvas.pack(fill=BOTH, anchor=N+W,expand=True)
        __self__.toolbar = NavigationToolbar(__self__.canvas,__self__.lower)
        __self__.toolbar.update()
        __self__.canvas._tkcanvas.pack()
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.wipe_plot)

        __self__.plot.spines["top"].set_color("black")
        __self__.plot.spines["top"].set_linewidth(2)
        __self__.plot.spines["bottom"].set_color("black")
        __self__.plot.spines["bottom"].set_linewidth(2)
        __self__.plot.spines["left"].set_color("black")
        __self__.plot.spines["left"].set_linewidth(2)
        __self__.plot.spines["right"].set_color("black")
        __self__.plot.spines["right"].set_linewidth(2)

        icon = os.path.join(os.getcwd(),"images","icons","plot.ico")
        __self__.master.iconbitmap(icon)
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)
    
    def AltOn(__self__,e=""):
        __self__.alt = True

    def AltOff(__self__,e=""):
        __self__.alt = False

    def maximize(__self__,e=""):
        maximize_window(__self__)
    
    def wipe_plot(__self__):
        """clears and destroy plot"""
        try: 
            __self__.plot.clear()
            __self__.figure.clf()
            del __self__.plot
            __self__.master.destroy()
            del __self__
        except: pass

    def draw_calibration(__self__):
        __self__.master.tagged = True
        __self__.plotdata = Constants.MY_DATACUBE.energyaxis
        channels = np.arange(1,__self__.plotdata.shape[0]+1)
        anchors = Constants.MY_DATACUBE.calibration
        __self__.plot.set_title("{0} Calibration curve".format(
            Constants.DIRECTORY),**__self__.plot_font)
        __self__.plot.plot(channels,__self__.plotdata,label="Calibration curve")
        for pair in anchors:
            __self__.plot.plot(pair[0],pair[1], marker='+',mew=3,ms=12,
                    label="{0}".format(pair))
        __self__.plot.set_ylabel("Energy (KeV)")
        __self__.plot.set_xlabel("Channel")
        __self__.plot.grid(color="black", ls="--", lw=0.5)
        __self__.plot.legend(
                fancybox=True,
                shadow=True,
                fontsize=12,
                framealpha=1,
                borderpad=1,
                facecolor="white")

    def draw_spec(__self__,mode,display_mode=None,lines=False):
        __self__.lw = 1.8 
        __self__.master.minsize(width=800,height=450)
        __self__.plot.grid(which='both',axis='both')
        __self__.plot.grid(color="gray", ls="--", lw=1)
        __self__.plot.axis('On')
        __self__.plot.set_facecolor("white")
        __self__.plot.set_xlim([
            Constants.MY_DATACUBE.energyaxis.min(),
            Constants.MY_DATACUBE.energyaxis.max()])

        energy_list=[]
        __self__.master.tagged = False
        if __self__.master.winfo_exists() == True:
            __self__.plot.clear()
            colors = ["blue","red","green"]
            if display_mode == '-semilogy':
                __self__.plot.set_ylabel("Counts")
                i = 0
                for option in mode:
                    __self__.plotdata = getstackplot(Constants.MY_DATACUBE,option)
                    __self__.plotdata = __self__.plotdata/__self__.plotdata.max()
                    __self__.plot.semilogy(Constants.MY_DATACUBE.energyaxis,__self__.plotdata,
                            label=str(option),color=colors[i],lw=2)
                    i+=1
                if lines==True:
                    __self__.master.tagged = True
                    for element in Constants.FIND_ELEMENT_LIST:
                        if element == "custom":
                            energies = plottables_dict[element]
                            __self__.plot.plot((energies[0],energies[0]),
                                    (0,__self__.plotdata.max()),'k--',color="cornflowerblue",
                                    label="Custom Low",linewidth=__self__.lw)
                            __self__.plot.plot((energies[1],energies[1]),
                                    (0,__self__.plotdata.max()),'k--',color="tomato",
                                    label="Custom High",linewidth=__self__.lw)
                        else:
                            energies = plottables_dict[element]
                            for value in energies: 
                                energy_list.append(value)
                                __self__.EL = __self__.plot.axvline(
                                x=value, color=ElementColors[element],
                                label=element,linewidth=__self__.lw)
                            energy_list=[]

                __self__.plot.set_title('{0} {1}'.format(
                    Constants.DIRECTORY,mode),**__self__.plot_font)
                __self__.plot.set_xlabel("Energy (KeV)")
                __self__.plot.legend()
            else:
                i = 0
                for option in mode:
                    __self__.plotdata = getstackplot(Constants.MY_DATACUBE,option)
                    __self__.plotdata = __self__.plotdata/__self__.plotdata.max()
                    __self__.plot.plot(Constants.MY_DATACUBE.energyaxis,__self__.plotdata,
                            label=str(option),color=colors[i],lw=2)
                    i+=1
                if lines==True:
                    __self__.master.tagged = True
                    for element in Constants.FIND_ELEMENT_LIST:
                        if element == "custom":
                            energies = plottables_dict[element]
                            __self__.plot.plot((energies[0],energies[0]),
                                    (0,__self__.plotdata.max()),'k--',color="cornflowerblue",
                                    label="Custom Low",linewidth=__self__.lw)
                            __self__.plot.plot((energies[1],energies[1]),
                                    (0,__self__.plotdata.max()),'k--',color="tomato",
                                    label="Custom High",linewidth=__self__.lw)
                        else:
                            energies = plottables_dict[element]
                            for value in energies: 
                                energy_list.append(value)
                                __self__.EL = __self__.plot.axvline(
                                x=value, color=ElementColors[element],
                                label=element,linewidth=__self__.lw)
                            energy_list=[]

                mode_string = "- "
                if len(mode)>1:
                    for i in range(len(mode)): 
                        if not i: mode_string = mode_string + mode[i] + " & "
                        else: mode_string = mode_string + mode[i]
                else: mode_string = "- " + mode[0]
                __self__.plot.set_title('{0} {1}'.format(
                    Constants.DIRECTORY, mode_string),**__self__.plot_font)
                __self__.plot.set_xlabel("Energy (KeV)")
                __self__.plot.legend(
                        fancybox=True,
                        shadow=True,
                        fontsize=12,
                        framealpha=1,
                        borderpad=1,
                        facecolor="white")

            __self__.canvas.draw()
    
    def draw_ROI(__self__):
        __self__.master.minsize(width=1280,height=720)
        __self__.plot.grid(which='both',axis='both')
        __self__.plot.grid(color="gray", ls="--", lw=1)
        __self__.plot.axis('On')
        __self__.plot.set_facecolor("white")
        __self__.plot.set_xlim([
            Constants.MY_DATACUBE.energyaxis.min(), 
            Constants.MY_DATACUBE.energyaxis.max()])

        __self__.master.tagged = True

        patches = []
        for element in Constants.MY_DATACUBE.ROI:
            __self__.plotdata = Constants.MY_DATACUBE.ROI[element]
            
            net = [0,""]
            #############################################
            if Constants.MY_DATACUBE.max_counts[element+"_a"] == 0:
                try: net = [Constants.MY_DATACUBE.max_counts[element+"_b"],"Beta"]
                except: net = [Constants.MY_DATACUBE.max_counts[element+"_a"],"Alpha"]
            else: net = [Constants.MY_DATACUBE.max_counts[element+"_a"],"Alpha"]
            #############################################
            # NEW DATACUBES SUPPORT ALL SIEGBAHN MACROS #
            #############################################
            try: 
                for line in SIEGBAHN:
                    max_ = Constants.MY_DATACUBE.max_counts[element + f"_{line}"]
                    if max_ > net[0]:
                        net = [max_, line]
            except: pass
            #############################################

            roi_label = element + " Max net: {} in {}".format(int(net[0]),net[1])
            if element != "custom":

                ###########################################################################
                # This block can be used if the ROI's are set as the peak indexes instead #
                # of the plot curve itself. Changes must be done inside                   #
                # BatchFitter.build_image()                                               #
                ###########################################################################

                if isinstance(__self__.plotdata,tuple):
                    for i in [j for j in __self__.plotdata if j>0]:
                        __self__.plot.axvline(x=Constants.MY_DATACUBE.energyaxis[i],
                        color=ElementColors[element],
                        label=element,linewidth=__self__.lw)
                    patches.append(
                        mpatches.Patch(
                            color=ElementColors[element], 
                            label=roi_label))

                ###########################################################################

                __self__.plot.fill_between(
                        Constants.MY_DATACUBE.energyaxis,
                        Constants.MY_DATACUBE.sum_bg,
                        __self__.plotdata,
                        color=ElementColors[element],
                        where=__self__.plotdata > Constants.MY_DATACUBE.sum_bg,
                        alpha=0.85,
                        interpolate=True,
                        linewidth=0,
                        zorder=1)
                __self__.plot.plot(Constants.MY_DATACUBE.energyaxis,
                        __self__.plotdata,
                        color="black",
                        linewidth=0.8)
                patches.append(
                        mpatches.Patch(
                            color=ElementColors[element], 
                            label=roi_label))
            else: 
                __self__.plot.fill_between(
                        Constants.MY_DATACUBE.energyaxis,
                        Constants.MY_DATACUBE.sum_bg,
                        __self__.plotdata,
                        color=ElementColors["Custom"],
                        where=__self__.plotdata > Constants.MY_DATACUBE.sum_bg,
                        alpha=0.85,
                        zorder=1)
                patches.append(
                        mpatches.Patch(
                            color=ElementColors["Custom"], 
                            label=roi_label))

        if Constants.PLOTSCALE == "-semilogy":
            __self__.plot.semilogy(
                    Constants.MY_DATACUBE.energyaxis,
                    Constants.MY_DATACUBE.sum,
                    color="blue",
                    label="Sum spectrum",
                    linewidth=3)
            if hasattr(Constants.MY_DATACUBE,"sum_fit"):
                __self__.plot.semilogy(
                        Constants.MY_DATACUBE.energyaxis,
                        Constants.MY_DATACUBE.sum_fit,
                        color="red",
                        label="Fit",
                        linewidth=2)
            __self__.plot.semilogy(
                    Constants.MY_DATACUBE.energyaxis,
                    Constants.MY_DATACUBE.sum_bg,
                    color="green",
                    label="Continuum",
                    linewidth=3)
        else:
            __self__.plot.plot(
                    Constants.MY_DATACUBE.energyaxis,
                    Constants.MY_DATACUBE.sum,
                    color="blue",
                    label="Sum spectrum",
                    linewidth=2)
            if hasattr(Constants.MY_DATACUBE,"sum_fit"):
                __self__.plot.plot(
                        Constants.MY_DATACUBE.energyaxis,
                        Constants.MY_DATACUBE.sum_fit,
                        color="red",
                        label="Fit",
                        linewidth=2)
            __self__.plot.plot(
                    Constants.MY_DATACUBE.energyaxis,
                    Constants.MY_DATACUBE.sum_bg,
                    color="green",
                    label="Continuum",
                    linewidth=2)
            
        patches.append(mpatches.Patch(
                        color="blue",
                        label="Sum spectrum"))
        patches.append(mpatches.Patch(
                    color="green",
                    label="Continuum"))

        __self__.plot.set_title("{0} Stacked ROI's sum for all spectra".format(
            Constants.DIRECTORY),**__self__.plot_font)
        __self__.plot.set_ylabel("Counts")
        __self__.plot.set_xlabel("Energy (KeV)")
        __self__.plot.set_ylim([1,Constants.MY_DATACUBE.sum.max()*1.20])
        __self__.plot.legend(
                fancybox=True,
                shadow=True,
                fontsize=12,
                framealpha=1,
                borderpad=1,
                facecolor="white",
                handles=patches,
		loc="upper right")

    def filter_images(__self__):
        def filterXx(X,x,k):
            a = X.min()
            b = X.max()
            v = np.zeros(k+1)
            newX = np.zeros(X.shape[0], dtype=np.float32)
            for elem in x:
                v[int((elem-a)*k/(b-a))] = 1
            for i in range(X.shape[0]):
                if v[int((X[i]-a)*k/(b-a))] == 1:
                    newX[i] = X[i]
            return newX

        shape = __self__.map1.shape
        img1 = __self__.map1.flatten()
        img2 = __self__.map2.flatten()
       
        x = __self__.selection[0]
        y = __self__.selection[1]
        
        __self__.parent.ElementalMap1 = filterXx(img1,x,2*LEVELS)
        __self__.parent.ElementalMap2 = filterXx(img2,y,2*LEVELS)
        __self__.parent.ElementalMap1 = __self__.parent.ElementalMap1*LEVELS/__self__.parent.ElementalMap1.max()
        __self__.parent.ElementalMap2 = __self__.parent.ElementalMap2*LEVELS/__self__.parent.ElementalMap2.max()
        
        __self__.parent.ElementalMap1.shape = (shape)
        __self__.parent.ElementalMap2.shape = (shape)
        __self__.parent.left_image.set_data(__self__.parent.ElementalMap1)
        __self__.parent.left_image.set_clim(vmin=0, vmax=LEVELS)
        __self__.parent.left_image.set_cmap(Constants.COLORMAP)
        __self__.parent.left_image.set_extent([0,shape[1],shape[0],0])
        __self__.parent.right_image.set_data(__self__.parent.ElementalMap2)
        __self__.parent.right_image.set_clim(vmin=0, vmax=LEVELS)
        __self__.parent.right_image.set_cmap(Constants.COLORMAP)
        __self__.parent.right_image.set_extent([0,shape[1],shape[0],0])
        __self__.parent.refresh()
        __self__.canvas.draw_idle()

    def place_anchor(__self__, e=""):
        def make_selection():
            mask = Mask.polygon(__self__.anchors)

            #i = 0
            #a = np.zeros(__self__.corrplot.get_offsets().shape[0],bool)
            #for point in __self__.corrplot.get_offsets(): 
            #   a[i] = Mask.isInside(mask,point)
            #   i+=1

            xys = __self__.corrplot.get_offsets()
            idxs = np.nonzero(mask.contains_points(xys))[0]
            __self__.selection = np.asarray(xys[idxs], dtype=np.float32)
            __self__.selection = [__self__.selection[:,0],__self__.selection[:,1]]

            Constants.ROOT.busy.busy()
            __self__.SelectionPlot = __self__.plot.scatter(__self__.selection[0],__self__.selection[1], color="purple")
            __self__.canvas.draw()
            __self__.filter_images()
            __self__.parent.masked = 1
            __self__.parent.correlate.state(["disabled"])
            Constants.ROOT.busy.notbusy()

        if __self__.MASK_ENABLE: 
            x, y = e.xdata, e.ydata
            
            # MASK COMPLETE
            if Mask.is_complete(e, __self__.anchors):
                line_x, line_y = Mask.line(__self__.anchors[-1], __self__.anchors[0])
                __self__.MaskLines.append(
                    __self__.plot.plot(line_x,line_y,linewidth=0.5,color="blue"))
                __self__.canvas.draw()

                make_selection()

                __self__.toggle_mask(complete=True)

            # NOT NOMPLETE
            elif not Mask.is_too_close(e, __self__.anchors): 
                anchor = Mask.Anchor(x,y,
                        __self__.anchor_width,__self__.anchor_height,
                        __self__.AnchorCount)
                if anchor.dot is None: return
                __self__.AnchorCount += 1
                __self__.plot.add_patch(anchor.dot)
                __self__.plot.set_xlim(__self__.limit_x)
                __self__.plot.set_ylim(__self__.limit_y)
                if __self__.AnchorCount > 1: #only draw line if not adding the first anchor 
                    line_x, line_y = Mask.line(__self__.anchors[-1], anchor)
                    __self__.MaskLines.append(
                        __self__.plot.plot(line_x,line_y,linewidth=1,color="blue"))
                __self__.anchors.append(anchor)
                __self__.canvas.draw()
            else: pass
        else: pass

    def clear_mask(__self__):
        for line in __self__.MaskLines: line.pop(0).remove()
        try: __self__.SelectionPlot.remove()
        except: pass
        __self__.AnchorCount = 0
        __self__.anchors = []
        __self__.MaskLines = []
        __self__.plot.patches = []
        __self__.selection = __self__.data
        __self__.parent.update_sample1()
        __self__.parent.update_sample2()
        __self__.parent.masked = 0
        __self__.parent.correlate.state(["!disabled"])
        __self__.canvas.draw_idle()

    def toggle_regression(__self__, e=""):
        if __self__.linregress: 
            __self__.LinRegressBtn.config(image=__self__.LINREGRESS_NORMAL_ICO)
            __self__.linregress.pop(0).remove()
            __self__.linregress = 0
            __self__.plot.get_legend().remove()
            __self__.canvas.draw_idle()
        else:
            __self__.LinRegressBtn.config(image=__self__.LINREGRESS_TOGGLED_ICO)
            corr = __self__.selection
            A, B, R = linregress(corr[0],corr[1])
            fit = []
            for i in range(int(corr[0].max())):
                value = A*i+B
                if value < corr[1].max():
                    fit.append(value)
                if B < 0: sig = "-"
                else: sig = "+"
            __self__.linregress = __self__.plot.plot(fit, color="blue",
                    label="y(x) = {0:0.2f}x {1} {2:0.2f}\nR = {3:0.4f}".format(
                        A,sig,abs(B),R))
            __self__.plot.legend(shadow=True,fontsize=10,facecolor="white",loc="upper right")
            __self__.canvas.draw_idle()

    def toggle_mask(__self__, complete=False):
        __self__.anchors = []
        if not __self__.MASK_ENABLE:
            __self__.clear_mask()
            __self__.MASK_ENABLE = 1
            __self__.MaskBtn.config(image=__self__.MASK_TOGGLED_ICO)
            __self__.connection = __self__.canvas.mpl_connect(
                    "button_press_event",__self__.place_anchor)
        elif __self__.MASK_ENABLE:
            __self__.MASK_ENABLE = 0
            __self__.MaskBtn.config(image=__self__.MASK_NORMAL_ICO)
            __self__.canvas.mpl_disconnect(__self__.connection)
            if not complete: __self__.clear_mask() 

    def draw_correlation(__self__,corr,labels,images):
        __self__.map1 = images[0]
        __self__.map2 = images[1]
        __self__.anchors = []
        __self__.AnchorCount = 0
        __self__.MaskLines = []
        __self__.data = corr
        __self__.selection = __self__.data
        max_xy = corr[0].max(), corr[1].max()
        __self__.limit_x = [-max_xy[0]*0.10,max_xy[0]*1.10]
        __self__.limit_y = [-max_xy[1]*0.10,max_xy[1]*1.10]
        __self__.anchor_width = corr[0].max()*0.015
        __self__.anchor_height = corr[1].max()*0.015
        __self__.plot.set_xlim(__self__.limit_x)
        __self__.plot.set_ylim(__self__.limit_y)
        __self__.MASK_ENABLE = 0

        def spawn_mask_button():
            __self__.original_shape = __self__.parent.newimage1.shape
            mask_normal_icon = PhotoImage(data=ICO_MASK_NORMAL)
            mask_toggled_icon = PhotoImage(data=ICO_MASK_TOGGLED)
            clear_icon = PhotoImage(data=ICO_CLEAR)
            linregress_normal_icon = PhotoImage(data=ICO_LINREGRESS_NORMAL)
            linregress_toggled_icon = PhotoImage(data=ICO_LINREGRESS_TOGGLED)
            __self__.MASK_NORMAL_ICO = mask_normal_icon.subsample(1,1)
            __self__.MASK_TOGGLED_ICO = mask_toggled_icon.subsample(1,1)
            __self__.CLEAR_ICO = clear_icon.subsample(1,1)
            __self__.LINREGRESS_NORMAL_ICO = linregress_normal_icon.subsample(1,1)
            __self__.LINREGRESS_TOGGLED_ICO = linregress_toggled_icon.subsample(1,1)

            __self__.add_ons = Frame(__self__.master, bg=__self__.master.cget("background"))
            __self__.add_ons.pack(side=BOTTOM,fill=X)
            __self__.linregress = 0
            __self__.MaskBtn = Button(__self__.add_ons, 
                    image=__self__.MASK_NORMAL_ICO,
                    command= lambda:__self__.toggle_mask(), 
                    bd=0,
                    bg=__self__.master.cget("background"))
            __self__.MaskBtn.pack(side=LEFT)
            Button(__self__.add_ons, 
                    image=__self__.CLEAR_ICO,
                    bd=0,
                    bg=__self__.master.cget("background"), 
                    command= lambda: __self__.clear_mask()).pack(side=LEFT)
            Info = Button(__self__.add_ons,
                    text="?",
                    bg=__self__.master.cget("background"),
                    font=tkFont.Font(family="Tahoma",weight="bold",size=10), 
                    bd=0)
            Info.pack(side=LEFT)
            Info.config(state=DISABLED)

            __self__.LinRegressBtn = Button(__self__.add_ons,
                    image=__self__.LINREGRESS_NORMAL_ICO,
                    bg=__self__.master.cget("background"),
                    bd=0,
                    command= lambda: __self__.toggle_regression(corr))
            __self__.LinRegressBtn.pack(side=RIGHT, anchor=E)

            create_tooltip(Info,"Click on the plot to place anchors. To close the mask, click the purple anchor.\nWhen the mask is complete, \"Draw mask\" will be toggled off.")
        
        __self__.plot.set_title('{0}'.format(Constants.DIRECTORY),**__self__.plot_font)
        labelx,macrox = labels[0].split("_")[0],labels[0].split("_")[1]
        labelx = labelx+" "+macrox
        labely,macroy = labels[1].split("_")[0],labels[1].split("_")[1]
        labely = labely+" "+macroy
        __self__.plot.set_xlabel(labelx,fontsize=16)
        __self__.plot.set_ylabel(labely,fontsize=16)
        __self__.corrplot = __self__.plot.scatter(corr[0],corr[1])

        spawn_mask_button()

        place_topright(__self__.master.master,__self__.master)

    def draw_map(__self__):
        __self__.plot.set_title('{0}'.format(Constants.DIRECTORY),**__self__.plot_font)
        __self__.plot.set_xlabel("Size [pixel]",fontsize=16)
        __self__.plot.set_ylabel("Size [pixel]",fontsize=16)
        __self__.plot.axis("Off")
        __self__.plot.grid(b=None, which="both", axis="both")
        fixed_image = write_image(Constants.MY_DATACUBE.densitymap,
                resize=Constants.TARGET_RES,
                path=None,
                enhance=Constants.MY_DATACUBE.config["enhance"],
                save=False)
        __self__.plot.imshow(fixed_image, cmap=Constants.COLORMAP, vmin=0)
        place_topright(__self__.master.master,__self__.master)

    def configure_fit(__self__):
        if __self__.parent.Panel is None:
            fit_config = {}
            if hasattr(__self__.parent.DATACUBE, "fit_config"):
                fit_config = __self__.parent.DATACUBE.fit_config
            __self__.parent.Panel = SimpleFitPanel(__self__.parent, fit_config)
            """ __self__.parent is the ImageAnalyzer window """
        else: return

    def export_fit(__self__):
        f = filedialog.asksaveasfile(mode='w',
                        defaultextension=".csv",
                        filetypes=[("Comma separated values", "*.csv")],
                        title="Save as...")
        if f is not None:
           writer = Engine.FitWriter(__self__.results,f.name) 
           writer.dump()

    def fit_roi(__self__):
        if not Constants.USEXLIB:
            messagebox.showerror("Xraylib not found!","Cannot perform fit!")
            __self__.master.focus_set()
            return
        Constants.ROOT.busy.busy()
        x,spec = __self__.DATA.get_data()
        if __self__.fit_plots != []:
            for plot in __self__.fit_plots: 
                try: plot.pop(0).remove()
                except: pass
        if __self__.parent.DATACUBE.fit_config["bg"]:
            try: 
                cycles, window, savgol, order = \
                        __self__.parent.DATACUBE.fit_config["bg_settings"]
            except: 
                cycles, window, savgol, order = \
                        Constants.SNIPBG_DEFAULTS
            continuum = peakstrip(spec,cycles,window,savgol,order)
            __self__.parent.DATACUBE.fit_fano_and_noise()

        else: continuum = np.ones(spec.shape[0])
        areas, curves = Engine.fit_single_spectrum(
                __self__.parent.DATACUBE,
                spec,
                continuum,
                __self__.parent.DATACUBE.fit_config)
        if areas is None:
            messagebox.showinfo("Fit failed!","Fit failed!")
            Constants.ROOT.busy.notbusy()
            __self__.parent.master.focus_set()
            __self__.master.focus_set()
            __self__.options.entryconfig("Export fit data . . .", state=DISABLED)
            return
        for element in areas.keys():
            __self__.fit_plots.append(
                    __self__.plot.plot(
                        __self__.parent.DATACUBE.energyaxis, curves[element], 
                    label=element, color=ElementColors[element],linestyle="--"))

        __self__.plot.set_ylim([1,spec.max()*1.20])
        if Constants.PLOTSCALE == "-semilogy": mode = "log"
        else: mode = "linear"
        __self__.plot.set_yscale(mode)
        __self__.canvas.draw()
        __self__.results = areas
        __self__.options.entryconfig("Export fit data . . .", state=NORMAL)
        Constants.ROOT.busy.notbusy()

    def draw_selective_sum(__self__,
            DATACUBE,
            y_data,
            display_mode=None,
            lines=False,
            refresh=False):

        __self__.fit_plots = []
        __self__.parent.Panel = None
        __self__.plot.grid(which='both',axis='both')
        __self__.plot.grid(color="gray", ls="--", lw=1)
        __self__.plot.axis('On')
        __self__.plot.set_facecolor("white")
        __self__.plot.set_xlim([
            __self__.parent.DATACUBE.energyaxis.min(),
            __self__.parent.DATACUBE.energyaxis.max()])


        def add_buttons():
            save_icon = PhotoImage(data=ICO_SAVE_SPEC)
            fit_normal_icon = PhotoImage(data=ICO_FIT_NORMAL)
            fit_disabled_icon = PhotoImage(data=ICO_FIT_DISABLED)
            __self__.SAVE_SPEC_ICO = save_icon.subsample(1,1)
            __self__.FIT_NORMAL_ICO = fit_normal_icon.subsample(1,1)
            __self__.FIT_DISABLED_ICO = fit_disabled_icon.subsample(1,1)
            __self__.master.config(menu=__self__.menubar)
            __self__.menubar.add_cascade(label="Options", menu=__self__.options)
            __self__.options.add_command(label="Configure fit . . .",
                    command=__self__.configure_fit)
            __self__.options.add_command(label="Export fit data . . .",
                    command=__self__.export_fit)

            __self__.add_ons = Frame(__self__.master, 
                    bg=__self__.master.cget("background"))
            __self__.save_raw_btn = Button(__self__.add_ons,
                    image=__self__.SAVE_SPEC_ICO,
                    bd=0,
                    bg=__self__.master.cget("background"),
                    command=lambda: save_raw_spectrum())
            __self__.fit_btn = Button(__self__.add_ons,
                    image=__self__.FIT_NORMAL_ICO,
                    bd=0,
                    bg=__self__.master.cget("background"),
                    command=__self__.fit_roi)
            Info = Button(__self__.add_ons,
                    text="?",
                    bg=__self__.master.cget("background"),
                    font=tkFont.Font(family="Tahoma",weight="bold",size=10),
                    bd=0)

            create_tooltip(Info,"Datacube fitting configurations must be first set via the \n\"Options\" menu on top. When using background, SNIPBG method \nwill be used to calculate the continuum for the selected ROI.")

            __self__.add_ons.pack(side=TOP,fill=X)
            __self__.save_raw_btn.pack(side=RIGHT)
            __self__.fit_btn.pack(side=LEFT)
            Info.pack(side=LEFT)
            Info.config(state=DISABLED)
            
            if not hasattr(__self__.parent.DATACUBE,"fit_config"):
                __self__.fit_btn.config(state=DISABLED)

            __self__.options.entryconfig("Export fit data . . .", state=DISABLED)
            return

        def save_raw_spectrum():
            x, spec = __self__.DATA.get_data()
            f = filedialog.asksaveasfile(mode='w',
                        defaultextension=".mca",
                        filetypes=[("MCA file", "*.mca")],
                        title="Save as...")
            if f is not None:
                sum_file = open(f.name,'w+')
                
                if __self__.limits == ():
                    limits = "FULL AREA"
                else:
                    limits =  f"X: {__self__.limits[0]};{__self__.limits[1]}, Y: {__self__.limits[2]};{__self__.limits[3]}"
                
                #################
                # writes header #
                #################
                sum_file.write(
                        f"<<PMCA SPECTRUM>>\nTAG - TAG\nDESCRIPTION - {DATACUBE.name} - ROI {limits}\n"
                        )
                sum_file.write("GAIN - 2\nTHRESHOLD - 0\nLIVE_MODE - 0\nPRESET_TIME - OFF\n")
                sum_file.write("LIVE_TIME - 0\nREAL_TIME - 0\nSTART_TIME - {}\n".format(
                    time.strftime("%Y-%m-%d %H:%M:%S", 
                        time.gmtime())))
                sum_file.write("SERIAL_NUMBER - 00001\n<<CALIBRATION>>\nLABEL - Channel\n")
                for pair in DATACUBE.calibration:
                    sum_file.write("{0} {1}\n".format(pair[0],pair[1]))
                sum_file.write("<<DATA>>\n")
                ###############
                
                for counts in spec:
                    sum_file.write("{}\n".format(int(counts)))
                sum_file.write("<<END>>")
                sum_file.close()
                __self__.master.focus_set()
                __self__.parent.master.focus_set()
                __self__.master.focus_force()
            else: return
        
        if not refresh:
            add_buttons()
   
        __self__.plot.clear()
        colors = ["blue","red","green"]
        __self__.plot.set_title('{0}'.format(DATACUBE.name),**__self__.plot_font)
        __self__.plot.set_ylabel("Counts")
        __self__.plot.set_xlabel("Energy (KeV)")

        if display_mode == '-semilogy':
            __self__.plotdata = y_data
            __self__.DATA, = __self__.plot.semilogy(
                    DATACUBE.energyaxis,
                    __self__.plotdata,
                    label="ROI Sum",
                    color=colors[0])
        else:
            __self__.plotdata = y_data
            __self__.DATA, = __self__.plot.plot(
                    DATACUBE.energyaxis,
                    __self__.plotdata,
                    label="ROI Sum",
                    color=colors[0])
        if lines==True:
            energy_list = []
            __self__.master.tagged = True
            for element in Constants.FIND_ELEMENT_LIST:
                if element == "custom":
                    energies = plottables_dict[element]
                    __self__.EL_CUST_LOW, = __self__.plot.plot(
                            (energies[0],energies[0]),
                            (0,__self__.plotdata.max()),
                            'k--',color="cornflowerblue",
                            label="Custom Low",linewidth=__self__.lw)
                    __self__.EL_CUST_HIGH, =__self__.plot.plot(
                            (energies[1],energies[1]),
                            (0,__self__.plotdata.max()),
                            'k--',color="tomato",
                            label="Custom High",linewidth=__self__.lw)
                else:
                    energies = plottables_dict[element]
                    for value in energies: 
                        energy_list.append(value)
                        __self__.EL = __self__.plot.axvline(
                        x=value, color=ElementColors[element],
                        label=element,linewidth=__self__.lw)
                    energy_list=[]
        __self__.plot.legend(
                fontsize=12,
                borderpad=1,
                loc="upper right")
        __self__.plot.grid(color="black", ls="--", lw=0.5)
        __self__.canvas.draw()
