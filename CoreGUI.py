#################################################################
#                                                               #
#          Graphical Interface and Core file                    #
#                        version: 1.0a                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import numpy as np
import sys, os, copy, pickle
import logging
import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
style.use('ggplot')

import SpecRead
SpecRead.conditional_setup()
import SpecMath
import Mapping
import ImgMath

logging.debug("Setting up...")
global MY_DATACUBE
MY_DATACUBE = None
try: load_cube()
except: pass
logging.debug("Done.")

def place_topleft(window1,window2):
    
    # adapted from: https://stackoverflow.com/questions/3352918/
    
    window1.update_idletasks()
    window2.update_idletasks()
    
    width = window1.winfo_width()
    frm_width = window1.winfo_rootx() - window1.winfo_x()
    win_width = width + (2 * frm_width)
    width2 = window2.winfo_width()
    print(width,width2)

    height = window1.winfo_height()
    titlebar_height = window1.winfo_rooty() - window1.winfo_y()
    win_height = height + titlebar_height + frm_width
    height2 = window2.winfo_height()
    print(height,height2)
    
    x = window1.winfo_rootx() + width
    y = window1.winfo_rooty() - titlebar_height
    window2.geometry('{}x{}+{}+{}'.format(width2, height2, x, y))
    window2.deiconify()

def place_center(window1,window2):
    window1.update_idletasks()
    window2.update_idletasks()
    
    width = window1.winfo_width()
    frm_width = window1.winfo_rootx() - window1.winfo_x()
    win_width = width + (2 * frm_width)
    width2 = window2.winfo_width()
    print(width,win_width)

    height = window1.winfo_height()
    titlebar_height = window1.winfo_rooty() - window1.winfo_y()
    win_height = height + titlebar_height + frm_width
    height2 = window2.winfo_height()
    
    x = window1.winfo_rootx() + (int(win_width/2)) - (int(width2/2))
    y = window1.winfo_rooty() - titlebar_height + (int(height/2)) - (int(height2/2))
    window2.geometry('{}x{}+{}+{}'.format(width2, height2, x, y))
    #window2.deiconify()

def convert_bytes(num):
    """
    Obtained from https://stackoverflow.com/questions/210408
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def ErrorMessage(message):
    
    ErrorWindow = Toplevel()
    ErrorWindow.title("Error")
    ErrorWindow.resizable(False,False)
    WindowFrame = Frame(ErrorWindow, bd=3)
    WindowFrame.pack()
    ErrorLabel = Label(WindowFrame, text=message,padx=16)
    ErrorLabel.pack_propagate(0)
    ErrorLabel.pack(fill=X)
    OkButton = Button(WindowFrame, text="OK", justify=CENTER, \
            command=ErrorWindow.destroy, width=10, bd=3)
    OkButton.pack_propagate(0)
    OkButton.pack()
    place_center(root.master,ErrorWindow)

def doNothing():
    messagebox.showinfo("Information","Will be implemented soon.")   

def call_help():
    HelpWindow = Toplevel(master=root.master)
    HelpWindow.title("Help")
    HelpWindow.resizable(False,False)
    HelpText= "I will write something here. I promise."
    HelpLabel = Label(HelpWindow, text=HelpText, wraplength=640, anchor=W, justify=LEFT)
    HelpLabel.grid(sticky=W)
    return np.nan

def open_analyzer():
    ImgAnalyzer = ImageAnalyzer(root.master)

def call_compilecube():
    
    try: os.mkdir(SpecRead.output_path)
    except: 
        print("Cannot create folder {}".format(SpecRead.output_path))
        pass
    
    if os.path.exists(SpecRead.cube_path): 
        pass
    else:
        #try: 
        specbatch = SpecMath.datacube(['xrf'],SpecRead.CONFIG)
        specbatch.compile_cube()
        #except:
        #    ErrorMessage("Can't find sample {}!".format(SpecRead.DIRECTORY))

def prompt_folder():
        print("Prompting for samples folder...")

def check_calibration():
    print("Checking calibration...")

def call_heightmap():
    print("Opening heightmap dialogue...")

def load_cube():
    logging.debug("Trying to load cube file.")
    logging.debug(SpecRead.cube_path)
    if os.path.exists(SpecRead.cube_path):
        cube_file = open(SpecRead.cube_path,'rb')
        global MY_DATACUBE
        MY_DATACUBE = pickle.load(cube_file)
        cube_file.close()
        logging.debug("Loaded cube {} to memory.".format(cube_file))
    else:
        logging.debug("No cube found.")
        MainGUI.toggle_(root,toggle='Off') 
        pass
    return MY_DATACUBE


class PeriodicTable:

    def __init__(__self__,parent):
        __self__.master = Toplevel(parent)
        __self__.master.title("Periodic Table of Elements")
        __self__.master.resizable(False,False)


class ImageAnalyzer:


    def __init__(__self__,parent):

        global MY_DATACUBE
        
        __self__.packed_elements = MY_DATACUBE.check_packed_elements()
        print(__self__.packed_elements)
        __self__.master = Toplevel(master=parent)
        __self__.master.title("Image Analyzer v1.01a")
        __self__.master.resizable(False,False)
        __self__.sampler = Frame(__self__.master)
        __self__.sampler.pack(side=TOP)
        __self__.SampleFrame = Frame(__self__.master)
        __self__.SampleFrame.pack(side=TOP)
        __self__.LeftCanvas = Canvas(__self__.SampleFrame)
        __self__.LeftCanvas.pack(side=LEFT)
        __self__.RightCanvas = Canvas(__self__.SampleFrame)
        __self__.RightCanvas.pack(side=RIGHT)
        __self__.sliders = Frame(__self__.master)
        __self__.sliders.pack()
        
        __self__.Map1Var = StringVar()
        __self__.Map2Var = StringVar()
        __self__.ElementalMap1 = np.zeros([20,20])
        __self__.ElementalMap2 = np.zeros([20,20])
        __self__.Map1Combo = ttk.Combobox(__self__.sampler, textvariable=__self__.Map1Var,\
                values=__self__.packed_elements)
        __self__.Map1Combo.grid(row=0,column=0,columnspan=4, sticky=W+E,padx=(16,16),pady=(8,4))
        __self__.Map2Combo = ttk.Combobox(__self__.sampler, textvariable=__self__.Map2Var,\
                values=__self__.packed_elements)
        __self__.Map2Combo.grid(row=0,column=4,columnspan=4, sticky=W+E,padx=(16,16),pady=(8,4))
        print(__self__.__dict__)
        __self__.Map1Combo.bind("<<ComboboxSelected>>", __self__.update_sample1)
        __self__.Map2Combo.bind("<<ComboboxSelected>>", __self__.update_sample2)

        __self__.figure1 = Figure(figsize=(5,4), dpi=75)
        __self__.plot1 = __self__.figure1.add_subplot(111)
        __self__.plot1.axis('On')
        __self__.plot1.grid(b=None)
        __self__.canvas1 = FigureCanvasTkAgg(__self__.figure1,__self__.LeftCanvas)
        __self__.canvas1.get_tk_widget().pack(fill=BOTH,anchor=N+W)
        
        __self__.figure2 = Figure(figsize=(5,4), dpi=75)
        __self__.plot2 = __self__.figure2.add_subplot(111)
        __self__.plot2.axis('On')
        __self__.plot2.grid(b=None)
        __self__.canvas2 = FigureCanvasTkAgg(__self__.figure2,__self__.RightCanvas)
        __self__.canvas2.get_tk_widget().pack(fill=BOTH,anchor=N+W)
       

        # image controls Threshold, LowPass and Smooth
        __self__.T1check = BooleanVar()
        __self__.T1check.set(False)
        __self__.T1 = Checkbutton(__self__.sliders, variable=__self__.T1check, \
                command=__self__.switchLP1T1).grid(row=0,column=0)
        __self__.LP1check = BooleanVar()
        __self__.LP1check.set(False)
        __self__.LP1 = Checkbutton(__self__.sliders, variable=__self__.LP1check, \
                command=__self__.switchT1LP1).grid(row=1,column=0)
        __self__.S1check = BooleanVar()
        __self__.S1check.set(False)
        __self__.S1 = Checkbutton(__self__.sliders, variable=__self__.S1check).grid(row=2,column=0)
       
        __self__.T1Label = Label(__self__.sliders, text="Threshold ")
        __self__.T1Label.grid(row=0,column=1)
        __self__.T2Label = Label(__self__.sliders, text="Threshold ")
        __self__.T2Label.grid(row=0,column=5)
        __self__.LP1Label = Label(__self__.sliders, text="Low Pass ")
        __self__.LP1Label.grid(row=1,column=1)
        __self__.LP2Label = Label(__self__.sliders, text="Low Pass ")
        __self__.LP2Label.grid(row=1,column=5)
        __self__.S1Label = Label(__self__.sliders, text="Smooth ")
        __self__.S1Label.grid(row=2,column=1)
        __self__.S2Label = Label(__self__.sliders, text="Smooth ")
        __self__.S2Label.grid(row=2,column=5)

        # slider for image 1
        __self__.T1Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=ImgMath.LEVELS, \
                command=__self__.draw_image1)
        __self__.T1Slider.grid(row=0,column=2)
        __self__.LP1Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=ImgMath.LEVELS, \
                command=__self__.draw_image1)
        __self__.LP1Slider.grid(row=1,column=2)
        __self__.S1Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=7, \
                command=__self__.draw_image1)
        __self__.S1Slider.grid(row=2,column=2)

        # image controls Threshold, LowPass and Smooth
        __self__.T2check = BooleanVar()
        __self__.T2check.set(False)
        __self__.T2 = Checkbutton(__self__.sliders, variable=__self__.T2check, \
                command=__self__.switchLP2T2).grid(row=0,column=4)
        __self__.LP2check = BooleanVar()
        __self__.LP2check.set(0)
        __self__.LP2 = Checkbutton(__self__.sliders, variable=__self__.LP2check, \
                command=__self__.switchT2LP2).grid(row=1,column=4)
        __self__.S2check = BooleanVar()
        __self__.S2check.set(0)
        __self__.S2 = Checkbutton(__self__.sliders, variable=__self__.S2check).grid(row=2,column=4)
               
        # slider for image 2
        __self__.T2Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=ImgMath.LEVELS, \
                command=__self__.draw_image2)
        __self__.T2Slider.grid(row=0,column=6)
        __self__.LP2Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=ImgMath.LEVELS, \
                command=__self__.draw_image2)
        __self__.LP2Slider.grid(row=1,column=6)
        __self__.S2Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=7, \
                command=__self__.draw_image2)
        __self__.S2Slider.grid(row=2,column=6)
    
        # Disabled sliders
        __self__.T1Slider.config(state=DISABLED)
        __self__.T2Slider.config(state=DISABLED)
        __self__.LP1Slider.config(state=DISABLED)
        __self__.LP2Slider.config(state=DISABLED)
        
        __self__.draw_image1(0)
        __self__.draw_image2(0)
        #__self__.master.mainloop()
 
    def update_sample1(__self__,event):
        global MY_DATACUBE
        print(__self__.Map1Var.get())
        __self__.ElementalMap1 = MY_DATACUBE.unpack_element(__self__.Map1Var.get())
        __self__.draw_image1(0)
     
    def update_sample2(__self__,event):
        global MY_DATACUBE
        print(__self__.Map2Var.get())
        __self__.ElementalMap2 = MY_DATACUBE.unpack_element(__self__.Map2Var.get())
        __self__.draw_image2(0)
    
    def switchT1LP1(__self__):
        if __self__.LP1check.get() == True: __self__.LP1Slider.config(state=NORMAL)
        else: __self__.LP1Slider.config(state=DISABLED)
        if __self__.T1check.get() == True: 
            __self__.T1check.set(False)
            __self__.T1Slider.config(state=DISABLED)

    def switchLP1T1(__self__):
        if __self__.T1check.get() == True: __self__.T1Slider.config(state=NORMAL)
        else: __self__.T1Slider.config(state=DISABLED)
        if __self__.LP1check.get() == True: 
            __self__.LP1check.set(False)
            __self__.LP1Slider.config(state=DISABLED)

    def switchT2LP2(__self__):
        if __self__.LP2check.get() == True: __self__.LP2Slider.config(state=NORMAL)
        else: __self__.LP2Slider.config(state=DISABLED)
        if __self__.T2check.get() == True: 
            __self__.T2check.set(False)
            __self__.T2Slider.config(state=DISABLED)
    
    def switchLP2T2(__self__):
        if __self__.T2check.get() == True: __self__.T2Slider.config(state=NORMAL)
        else: __self__.T2Slider.config(state=DISABLED)
        if __self__.LP2check.get() == True: 
            __self__.LP2check.set(False)
            __self__.LP2Slider.config(state=DISABLED)

    def transform1(__self__,image):
        if __self__.T1check.get() == True:
            if __self__.S1check.get() == True: 
                # Threshold and then Smooth
                print("1 Thresholding . . .")
                image = ImgMath.threshold(image,__self__.T1Slider.get())
                print("1 Now Smoothening . . .")
                image = ImgMath.iteractive_median(image,__self__.S1Slider.get())
            else:
                # Just Threshold
                print("1 Just Thresholding . . .")
                image = ImgMath.threshold(image,__self__.T1Slider.get())
        elif __self__.LP1check.get() == True:
            if __self__.S1check.get() == True: 
                # LowPass and then Smooth
                print("1 Low Passing . . .")
                image = ImgMath.low_pass(image,__self__.LP1Slider.get())
                print("1 Now Smoothening . . .")
                image = ImgMath.iteractive_median(image,__self__.S1Slider.get())
            else:
                # Just LowPass
                print("1 Low Passing . . .")
                image = ImgMath.low_pass(image,__self__.LP1Slider.get())
        else:
            if __self__.S1check.get() == True:
                # Just Smooth
                print("1 Just Smoothening . . .")
                image = ImgMath.iteractive_median(image,__self__.S1Slider.get())
        return image
 
    def transform2(__self__,image):
        if __self__.T2check.get() == True:
            if __self__.S2check.get() == True: 
                # Threshold and then Smooth
                print("2 Thresholding . . .")
                image = ImgMath.threshold(image,__self__.T2Slider.get())
                print("2 Now Smoothening . . .")
                image = ImgMath.iteractive_median(image,__self__.S2Slider.get())
            else:
                # Just Threshold
                print("2 Just Thresholding . . .")
                image = ImgMath.threshold(image,__self__.T2Slider.get())
        elif __self__.LP2check.get() == True:
            if __self__.S2check.get() == True: 
                # LowPass and then Smooth
                print("2 Low Passing . . .")
                image = ImgMath.low_pass(image,__self__.LP2Slider.get())
                print("2 Now Smoothening . . .")
                image = ImgMath.iteractive_median(image,__self__.S2Slider.get())
            else:
                # Just LowPass
                print("2 Low Passing . . .")
                image = ImgMath.low_pass(image,__self__.LP2Slider.get())
        else:
            if __self__.S2check.get() == True:
                # Just Smooth
                print("2 Just Smoothening . . .")
                image = ImgMath.iteractive_median(image,__self__.S2Slider.get())
        return image   
    
    # the Sliders are the widgets that calls draw_image functions
    # they always pass their respective values as argument when using command
    # argument i is there just to make it work. The value passed doesn't change a thing

    def draw_image1(__self__,i):
        print("draw1")
        __self__.CACHEMAP1 = copy.deepcopy(__self__.ElementalMap1)
        newimage1 = __self__.transform1(__self__.CACHEMAP1)
        __self__.CACHEMAP1
        __self__.plot1.clear()
        __self__.plot1.imshow(newimage1, cmap='gray')
        __self__.plot1.grid(b=None)
        __self__.canvas1.draw()
    
    def draw_image2(__self__,i):
        print("draw2")
        __self__.CACHEMAP2 = copy.deepcopy(__self__.ElementalMap2)
        newimage2 = __self__.transform2(__self__.CACHEMAP2)
        __self__.CACHEMAP2 = None
        __self__.plot2.clear()
        __self__.plot2.imshow(newimage2, cmap='gray')
        __self__.plot2.grid(b=None)
        __self__.canvas2.draw()


class PlotWin:

    global MY_DATACUBE

    def __init__(__self__,master):
        plot_font = {'fontname':'Times New Roman','fontsize':10}
        __self__.master = Toplevel(master=master)
        __self__.master.title("Plot")
        __self__.master.configure(bg='white')
        __self__.master.resizable(True,False) 
        __self__.upper = Canvas(__self__.master)
        __self__.upper.config(bg='white')
        __self__.upper.pack(side=TOP, expand=True, fill=BOTH, padx=(16,16),pady=(16,16))
        __self__.lower = Canvas(__self__.master)
        __self__.lower.pack(side=BOTTOM, expand=False, fill=BOTH)

        __self__.figure = Figure(figsize=(5,4), dpi=100)
        __self__.plot =__self__.figure.add_subplot(111)
        __self__.plot.grid(which='both',axis='both')
        __self__.plot.axis('On')
        __self__.canvas = FigureCanvasTkAgg(__self__.figure,__self__.upper)
        __self__.canvas.draw()
        __self__.canvas.get_tk_widget().pack(fill=BOTH,anchor=N+W)
        __self__.toolbar = NavigationToolbar2Tk(__self__.canvas,__self__.lower)
        __self__.toolbar.update()
        __self__.canvas._tkcanvas.pack(anchor=W, fill=BOTH)

    def draw_calibration(__self__):
        plot_font = {'fontname':'Times New Roman','fontsize':10}
        __self__.plotdata = MY_DATACUBE.energyaxis
        channels = np.arange(1,__self__.plotdata.shape[0]+1)
        anchors = MY_DATACUBE.calibration
        __self__.plot.set_title('{0} Calibration curve'.format(SpecRead.DIRECTORY),**plot_font)
        __self__.plot.plot(channels,__self__.plotdata,label="Calibration curve")
        for pair in anchors:
            __self__.plot.plot(pair[0],pair[1], marker='+', label="{0}".format(pair))
        __self__.plot.set_ylabel("Energy (KeV)")
        __self__.plot.set_xlabel("Channel")
        __self__.plot.legend()
        place_center(__self__.master.master,__self__.master)

    def draw_spec(__self__,mode,display_mode='-semilog'):
        plot_font = {'fontname':'Times New Roman','fontsize':10}
        if display_mode == '-semilog':
            __self__.plot.set_title('{0}'.format(SpecRead.DIRECTORY),**plot_font)
            __self__.plot.set_ylabel("Counts")
            for option in mode:
                if len(option) > 0:
                    __self__.plotdata = SpecMath.getstackplot(MY_DATACUBE,option)
                    __self__.plotdata = __self__.plotdata/__self__.plotdata.max()
                    __self__.plot.semilogy(MY_DATACUBE.energyaxis,__self__.plotdata,label=str(option))
            __self__.plot.set_xlabel("Energy (KeV)")
            __self__.plot.legend()
        else:
            for option in mode:
                if len(option) > 0:
                    __self__.plotdata = SpecMath.getstackplot(MY_DATACUBE,option)
                    __self__.plotdata = __self__.plotdata/__self__.plotdata.max()
                    __self__.plot.plot(MY_DATACUBE.energyaxis,__self__.plotdata,label=str(option))
            __self__.plot.set_xlabel("Energy (KeV)")
            __self__.plot.legend()
        place_center(__self__.master.master,__self__.master)


class Samples:

    def __init__(__self__):
        __self__.samples_database = {}

    def list_all(__self__):
        logging.info("Loading sample list...")
        samples = [name for name in os.listdir(SpecRead.samples_folder) \
                if os.path.isdir(SpecRead.samples_folder+name)]
        for folder in samples:
            files = [name for name in os.listdir(SpecRead.samples_folder+folder)]
            for item in range(len(files)): 
                try:
                    files[item] = files[item].split("_",1)[0]
                except: pass
            counter = dict((x,files.count(x)) for x in files)
            mca_prefix_count = 0
            for counts in counter:
                if counter[counts] > mca_prefix_count:
                    mca_prefix = counts
                    mca_prefix_count = counter[counts]
            __self__.samples_database[folder] = mca_prefix
        logging.info("Finished.")
    

class MainGUI:
    
    # *** Methods *** #
    
    # root_quit()
    # find_elements()
    # list_samples()
    # sample_select(event)
    # build_widgets()
    # write_stat()
    # call_listsamples()
    # reset_sample()
    # call_configure()
    # enable_
    # disable_

    def __init__(__self__,samples):
        logging.info("Initializing program...")
        __self__.master = Tk()
        __self__.master.title("Piratininga SM v.1.00 pre-α")
        __self__.master.resizable(False,False)
        __self__.samples = samples
        __self__.sample_figure = Figure(figsize=(3,2), dpi=100)
        __self__.sample_plot =__self__.sample_figure.add_subplot(111)
        __self__.sample_plot.grid(b=None)
        __self__.sample_plot.axis('off')
        mapfont = {'fontname':'Times New Roman','fontsize':10}
        __self__.sample_plot.set_title('Sample Counts Map',**mapfont)
        __self__.build_widgets()
        __self__.toggle_(toggle='off')

    def root_quit(__self__):
        for widget in __self__.master.winfo_children():
            if isinstance(widget, Toplevel):
                widget.destroy()
        __self__.master.destroy()
    
    def toggle_(__self__,toggle='on'):
        if toggle == 'on':
            __self__.Toolbox.entryconfig("Derived spectra", state=NORMAL)
            __self__.Toolbox.entryconfig("Image Analyzer . . .", state=NORMAL)
            __self__.ButtonReset.config(state=NORMAL)
            __self__.ImgAnalButton.config(state=NORMAL)
            __self__.Toolbox.entryconfig("Reset sample",state=NORMAL)
            __self__.Toolbox.entryconfig("Check calibration",state=NORMAL)
            __self__.Toolbox.entryconfig("Find elements",state=NORMAL)
            __self__.Toolbox.entryconfig("Height-mapping",state=NORMAL)
        if toggle == 'off':
            __self__.Toolbox.entryconfig("Derived spectra", state=DISABLED)
            __self__.Toolbox.entryconfig("Image Analyzer . . .", state=DISABLED)
            __self__.ButtonReset.config(state=DISABLED)
            __self__.ImgAnalButton.config(state=DISABLED)
            __self__.Toolbox.entryconfig("Reset sample",state=DISABLED)
            __self__.Toolbox.entryconfig("Check calibration",state=DISABLED)
            __self__.Toolbox.entryconfig("Find elements",state=DISABLED)
            __self__.Toolbox.entryconfig("Height-mapping",state=DISABLED)

    def find_elements(__self__):
        print("Finding elements...")
        lista_elementos = ['S','Cl','Ti','Cr','Fe','Cu','Sn','Mn','Ca']
        #lista_elementos = ['Cr']
        MAPS = Mapping.getpeakmap(lista_elementos,MY_DATACUBE)
        ImgMath.split_and_save(MY_DATACUBE,MAPS,lista_elementos)
        __self__.write_stat()

    def call_listsamples(__self__):
        __self__.SamplesWindow = Toplevel(master=__self__.master)
        __self__.SamplesWindow.title("Sample List")
        __self__.SamplesWindow.resizable(False,False) 
        SamplesWindow_LabelLeft = Label(__self__.SamplesWindow, text="FOLDER")
        SamplesWindow_LabelRight = Label(__self__.SamplesWindow, text="MCA PREFIX")
        SamplesWindow_TableLeft = Listbox(__self__.SamplesWindow, height=40)
        SamplesWindow_TableLeft.bind('<Double-Button-1>', __self__.sample_select)
        SamplesWindow_TableRight = Listbox(__self__.SamplesWindow, height=40)
        
        SamplesWindow_LabelLeft.grid(row=0,column=0)
        SamplesWindow_LabelRight.grid(row=0,column=1)
        SamplesWindow_TableLeft.grid(pady=5, row=1,column=0)
        SamplesWindow_TableRight.grid(pady=5, row=1,column=1)
       
        for key in __self__.samples:
            SamplesWindow_TableLeft.insert(END,"{}".format(key))
            SamplesWindow_TableRight.insert(END,"{}".format(__self__.samples[key]))
        place_topleft(__self__.master,__self__.SamplesWindow)

    def list_samples(__self__):
        try:
            if __self__.SamplesWindow.state() == 'normal': 
                __self__.SamplesWindow.focus_force()
                pass
            else: __self__.call_listsamples()
        except: __self__.call_listsamples()
    
    def draw_map(__self__):
        global MY_DATACUBE
        try: 
            __self__.sample_plot.imshow(MY_DATACUBE.densitymap, cmap='jet')
            __self__.plot_canvas.draw()
        except: 
            blank = np.zeros([20,20])
            __self__.sample_plot.imshow(blank, cmap='jet')
            __self__.plot_canvas.draw()

    def wipe(__self__):
        global MY_DATACUBE
        MY_DATACUBE = None
        load_cube()
        __self__.write_stat()
        __self__.draw_map()
        __self__.toggle_(toggle='off')
        __self__.SampleVar.set("Sample on memory: None")
        __self__.ConfigDiag.destroy()

    def refresh_ImageCanvas(__self__,i):
        
        # for use with animation
        # it slows down performance significatvely
        
        try: 
            __self__.sample_plot.imshow(__self__.densitymap,cmap='jet',label='Counts Map')
        except: 
            __self__.sample_plot.imshow(np.zeros([20,20]))
    

    def sample_select(__self__,event):
        
        __self__.toggle_('off')
        # destroy any open configuration window
        try: __self__.ConfigDiag.destroy()
        except: pass

        index = int(event.widget.curselection()[0])
        value = event.widget.get(index)
        
        # to avoid unecessarily changing the global variable cube_path, a local version
        # is created to check the existance of a cube file for the selected sample. If it exists,
        # then the global variable is changed, the cube is loaded to memory and the aplication load
        # the configuration embedded in the cube file. Config.cfg remains unchanged.
        # If the cube does not exists, the user is promped to config the sample and click ok to compile it.
        # Let the user cancel the cofiguration dialogue, the global variable cube_path is unchanged.
        
        local_cube_path = SpecRead.workpath+'\output\\'+value+'\\'+value+'.cube'
        if os.path.exists(local_cube_path): 
            global MY_DATACUBE
            SpecRead.cube_path = SpecRead.workpath+'\output\\'+value+'\\'+value+'.cube'
            load_cube()
            print(MY_DATACUBE.calibration)
            SpecRead.setup_from_datacube(MY_DATACUBE)
            __self__.SampleVar.set("Sample on memory: "+SpecRead.selected_sample_folder)
            __self__.toggle_(toggle='on')    
            __self__.write_stat()   
            __self__.draw_map()

        else: 
            SpecRead.conditional_setup(name=value)
            __self__.call_configure()
            __self__.master.wait_window(__self__.ConfigDiag)

    def plot_calibration_curve(__self__):
        master = __self__.master
        calibration_plot = PlotWin(master)
        calibration_plot.draw_calibration()
    
    def call_summation(__self__):
        master = __self__.master
        summation = PlotWin(master)
        summation.draw_spec(mode=['summation'],display_mode='-semilog')
    
    def call_mps(__self__):
        master = __self__.master
        MPS = PlotWin(master)
        MPS.draw_spec(mode=['mps'],display_mode='-semilog')
    
    def call_combined(__self__):
        master = __self__.master
        combined = PlotWin(master)
        combined.draw_spec(mode=['summation','mps'],display_mode='-semilog')

    def build_widgets(__self__):
        
        # define the frame and layout
        __self__.ButtonsFrame = Frame(__self__.master)
        __self__.ButtonsFrame.grid_propagate(1)
        __self__.ButtonsFrame.grid(row=0, column=0, rowspan=3, columnspan=2,padx=16)
        __self__.ImageCanvas = Canvas(__self__.master,width=200, height=200,\
                bg='black', relief=SUNKEN, bd=5)
        __self__.ImageCanvas.grid(row=3, column=0, rowspan=3, columnspan=2, padx=(8,8))
        __self__.ImageCanvas.propagate(0)
        __self__.DataFrame = Frame(__self__.master).grid(padx=16, pady=16, row=0, column=2, rowspan=3, columnspan=3)
        __self__.StatusScroller = Scrollbar(__self__.DataFrame, relief=SUNKEN)
        __self__.StatusBox = Listbox(__self__.DataFrame, yscrollcommand=__self__.StatusScroller.set)
        __self__.StatusBox.grid(row=0, column=2, rowspan=3, columnspan=3, sticky=W+E, padx=(16,0))
        __self__.StatusScroller.grid(row=0, column=5, rowspan=3, sticky=N+W+E+S, padx=(0,16))
        __self__.StatusScroller.config(command=__self__.StatusBox.yview) 
        __self__.ConfigFrame = Frame(__self__.DataFrame, padx=5,pady=5,relief=SUNKEN)
        __self__.ConfigFrame.grid(row=3, column=2, rowspan=3, columnspan=3, padx=16)
         
        # start matplotlib call inside __self__.ImageCanvas
        blank_image = np.zeros([1,1])
        __self__.plot_canvas = FigureCanvasTkAgg(__self__.sample_figure,__self__.ImageCanvas)
        __self__.plot_canvas.draw()
        __self__.plot_canvas.get_tk_widget().grid(\
                row=3, column=0, rowspan=3, columnspan=2, sticky=E, padx=(3,3), pady=(3,3))
        
        __self__.draw_map()

        #####
        # define the tables which go inside the DataFrame (bottom left corner)
        
        __self__.TableLabel1 = Label(\
                __self__.ConfigFrame,text="Configuration embedded:",justify=CENTER)
        __self__.TableLabel2 = Label(__self__.ConfigFrame,text="KEY")
        __self__.TableLabel3 = Label(__self__.ConfigFrame,text="PACKED IN CUBE")
        __self__.TableLabel4 = Label(__self__.ConfigFrame,text="IN CONFIG.CFG")
        __self__.TableLabel1.grid(row=3, column=2, columnspan=3, sticky=W+E)
        __self__.TableLabel2.grid(row=4, column=2)
        __self__.TableLabel3.grid(row=4, column=3)
        __self__.TableLabel4.grid(row=4, column=4)

        __self__.TableLeft = Listbox(__self__.ConfigFrame)
        __self__.TableMiddle = Listbox(__self__.ConfigFrame)
        __self__.TableRight = Listbox(__self__.ConfigFrame)
        __self__.TableLeft.grid(row=5, column=2, sticky=N+S)
        __self__.TableMiddle.grid(row=5, column=3, sticky=N+S)
        __self__.TableRight.grid(row=5, column=4, sticky=N+S)
        
        #####
        # define the menu bar

        __self__.MenuBar = Menu(__self__.master,tearoff=0)
        __self__.Toolbox = Menu(__self__.MenuBar,tearoff=0)
        __self__.derived_spectra = Menu(__self__.Toolbox,tearoff=0)

        __self__.MenuBar.add_cascade(label="Toolbox", menu=__self__.Toolbox)
        __self__.MenuBar.add_command(label="Help", command=call_help)
        __self__.derived_spectra.add_command(label="Summation", command=__self__.call_summation)
        __self__.derived_spectra.add_command(label="Maximum Pixel Spectra (MPS)", \
                command=__self__.call_mps)
        __self__.derived_spectra.add_command(label="Combined", command=__self__.call_combined)
        __self__.Toolbox.add_command(label="Set samples folder . . .", command=doNothing)
        __self__.Toolbox.add_command(label="Load sample", command=__self__.list_samples)
        __self__.Toolbox.add_command(label="Reset sample", command=__self__.reset_sample)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_cascade(label="Derived spectra", menu=__self__.derived_spectra)
        __self__.Toolbox.add_command(label="Check calibration", command=__self__.plot_calibration_curve)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_command(label="Find elements", command=__self__.find_elements)
        __self__.Toolbox.add_command(label="Height-mapping", command=doNothing)
        __self__.Toolbox.add_command(label="Image Analyzer . . .", command=open_analyzer)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_command(label="Settings", command=doNothing)
        __self__.Toolbox.add_command(label="Exit", command=__self__.root_quit)

        __self__.master.config(menu=__self__.MenuBar)
        
        #####
        # define the buttons wich go inside the ButtonsFrame (top left corner)
        subx,suby = 1,1

        ButtonLoad_icon = PhotoImage(file = os.getcwd()+'\images\icons\load.png')
        __self__.ButtonLoad_icon = ButtonLoad_icon.subsample(subx,suby)
        ButtonReset_icon = PhotoImage(file = os.getcwd()+'\images\icons\\reset.png')
        __self__.ButtonReset_icon = ButtonReset_icon.subsample(subx,suby)
        ImgAnalButton_icon = PhotoImage(file = os.getcwd()+'\images\icons\img_anal.png')
        __self__.ImgAnalButton_icon = ImgAnalButton_icon.subsample(subx,suby)
        QuitButton_icon = PhotoImage(file = os.getcwd()+'\images\icons\quit.png')
        __self__.QuitButton_icon = QuitButton_icon.subsample(subx,suby)
        SettingsButton_icon = PhotoImage(file = os.getcwd()+'\images\icons\settings.png')
        __self__.SettingsButton_icon = SettingsButton_icon.subsample(subx,suby)

        __self__.ButtonLoad = Button(__self__.ButtonsFrame, text="  Load Sample", anchor=W,\
                image=__self__.ButtonLoad_icon, bd=3, compound=LEFT, command=__self__.list_samples)
        __self__.ButtonLoad.grid(row=0,column=0, sticky=W+E)
        __self__.ButtonReset = Button(__self__.ButtonsFrame, text="  Reset Sample", anchor=W,\
                image=__self__.ButtonReset_icon, compound=LEFT, bd=3, command=__self__.reset_sample)
        __self__.ButtonReset.grid(row=0,column=1, sticky=W+E)
        __self__.ImgAnalButton = Button(__self__.ButtonsFrame, text="  Image Analyzer", anchor=W,\
                image=__self__.ImgAnalButton_icon, compound=LEFT, bd=3, command=open_analyzer)
        __self__.ImgAnalButton.grid(row=1,column=0, sticky=W+E)
        __self__.QuitButton = Button(__self__.ButtonsFrame, text="  Quit", anchor=W,\
                image=__self__.QuitButton_icon, compound=LEFT, bd=3, command=__self__.root_quit)
        __self__.QuitButton.grid(row=2,column=1,sticky=W+E)
        __self__.SettingsButton = Button(__self__.ButtonsFrame, text="  Settings", anchor=W,\
                image=__self__.SettingsButton_icon, compound=LEFT, bd=3, command=doNothing)
        __self__.SettingsButton.grid(row=1,column=1,sticky=W+E)
        
        #####

        __self__.SampleVar = StringVar()
        __self__.SampleVar.set("Sample on memory: "+SpecRead.DIRECTORY)
        __self__.StatusBar = Label(__self__.master, textvariable=__self__.SampleVar,\
                bd=1, relief=SUNKEN, anchor=W)
        __self__.StatusBar.grid(row=6, column=0, columnspan=6, sticky=W+E)

        __self__.master.protocol("WM_DELETE_WINDOW", __self__.root_quit)
    
    def write_stat(__self__):
        
        __self__.TableRight.config(state=NORMAL)
        __self__.TableMiddle.config(state=NORMAL)
        __self__.TableLeft.config(state=NORMAL)
        # must update the cube stored in memory!
        # everytime wrtie_stat is called, it means the cube has been changed or a different sample
        # has been called. Updates the StatsBar variable 
        
        load_cube()
        __self__.SampleVar.set("Sample on memory: "+SpecRead.DIRECTORY)
        
        # wipe all text
        __self__.StatusBox.delete(0,END)
        __self__.TableRight.delete(0,END)
        __self__.TableMiddle.delete(0,END)
        __self__.TableLeft.delete(0,END)

        if os.path.exists(SpecRead.selected_sample_folder):
            __self__.StatusBox.insert(\
                    END, "\nSample files location: {0}\n".format(SpecRead.selected_sample_folder))
            __self__.no_sample = False
        else: 
            __self__.StatusBox.insert(END, "\nSample {} not found!\n".format(SpecRead.DIRECTORY))
            __self__.no_sample = True

        if os.path.exists(SpecRead.cube_path):
            cube_stats = os.stat(SpecRead.cube_path)
            cube_size = convert_bytes(cube_stats.st_size)
            print(SpecRead.cube_path)
            __self__.StatusBox.insert(END,"Datacube is compiled. Cube size: {0}".format(cube_size))
            __self__.StatusBox.insert(END,"Verifying packed elements...")
            
            packed_elements = MY_DATACUBE.check_packed_elements()
            if len(packed_elements) == 0: __self__.StatusBox.insert(END,"None found.")
            else: 
                for element in packed_elements:
                    __self__.StatusBox.insert(END,"Found a map for {0}".format(element))
            __self__.StatusBox.insert(END,"Done.")
            values_cube, values_cfg, values_keys = [],[],[]
            for key in MY_DATACUBE.config:
                values_cube.append(str(MY_DATACUBE.config[key]))
                values_cfg.append(str(SpecRead.CONFIG[key]))
                values_keys.append(str(key))
            for item in range(len(values_cube)):
                __self__.TableLeft.insert(END, "{}".format(values_keys[item]))
                __self__.TableMiddle.insert(END, "{}".format(values_cube[item]))
                __self__.TableRight.insert(END, "{}".format(values_cfg[item]))
        
        elif __self__.no_sample == True:
            __self__.StatusBox.insert(END, "No sample configured!") 
            for key in SpecRead.CONFIG:
                __self__.TableLeft.insert(END,key)
                __self__.TableRight.insert(END, "{}".format(SpecRead.CONFIG[key]))

        else: 
            __self__.StatusBox.insert(END, "Datacube not compiled.") 
            __self__.StatusBox.insert(END, "Please compile the cube first.")
            for key in SpecRead.CONFIG:
                __self__.TableLeft.insert(END,key)
                __self__.TableRight.insert(END, "{}".format(SpecRead.CONFIG[key]))

        __self__.TableLeft.config(state=DISABLED)
        __self__.TableMiddle.config(state=DISABLED)
        __self__.TableRight.config(state=DISABLED)
       
    
    def reset_sample(__self__):
        
        def repack(__self__):
            import shutil
            #shutil.rmtree(SpecRead.output_path)
            os.remove(SpecRead.cube_path)
            load_cube()
            __self__.write_stat()
            __self__.toggle_(toggle='off')
            __self__.call_configure()
            __self__.ResetWindow.wait_window(__self__.ConfigDiag)
            __self__.draw_map()
            __self__.ResetWindow.destroy()

        if os.path.exists(SpecRead.cube_path):
            
            # creates dialogue to warn cube exists and promp to repack data
            __self__.ResetWindow = Toplevel(master=__self__.master)
            __self__.ResetWindow.title("Attention!")
            __self__.ResetWindow.resizable(False,False)
            LocalLabel = Label(__self__.ResetWindow, text="Resetting the sample will erase all files in the OUTPUT folder of sample {}! Are you sure you want to proceed?".format(SpecRead.DIRECTORY),\
                    padx=10, pady=4, wraplength=250)
            LocalLabel.pack()
            Erase_ico = PhotoImage(file = os.getcwd()+'\images\icons\erase.png')
            __self__.Erase_ico = Erase_ico.zoom(2, 2)
            EraseLabel = Label(__self__.ResetWindow, image = __self__.Erase_ico).\
                    pack(side=LEFT, pady=8, padx=16)
            YesButton = Button(__self__.ResetWindow, text="Yes", justify=CENTER,\
                    command=lambda: repack(__self__), width=10, bd=3).pack(side=TOP,pady=5)
            NoButton = Button(__self__.ResetWindow, text="No", justify=CENTER,\
                    command=__self__.ResetWindow.destroy, width=10, bd=3).pack(side=TOP, pady=5)
            
            place_center(__self__.master,__self__.ResetWindow)

        else:
            ErrorMessage("Can't find sample {}!".format(SpecRead.DIRECTORY))


    def call_configure(__self__):
        
        ManualParam = []

        def manual_calib():
            
            def save_param():
                EntryParam = [\
                        [ch1.get(),en1.get()],\
                        [ch2.get(),en2.get()],\
                        [ch3.get(),en3.get()],\
                        [ch4.get(),en4.get()]]
                for index in range(len(EntryParam)):
                    if EntryParam[index][0] or EntryParam[index][1] > 0:
                        ManualParam.append(EntryParam[index])
                save_config()
                return ManualParam

            CalibDiag = Toplevel(master=__self__.ConfigDiag)
            CalibDiag.title("Manual configuration")
            CalibDiag.resizable(False,False)
            ParamFrame = Frame(CalibDiag)
            ParamFrame.pack()
            ButtonFrame = Frame(CalibDiag)
            ButtonFrame.pack()
            
            ch1 = IntVar()
            ch2 = IntVar()
            ch3 = IntVar()
            ch4 = IntVar()
            
            en1 = DoubleVar()
            en2 = DoubleVar()
            en3 = DoubleVar()
            en4 = DoubleVar()
            
            try: 
                SpecRead.CONFIG['calibration'] = 'manual'
                calibparam = SpecRead.getcalibration()
                ch1.set(calibparam[0][0])
                en1.set(calibparam[0][1])
                ch2.set(calibparam[1][0])
                en2.set(calibparam[1][1])
                ch3.set(calibparam[2][0])
                en3.set(calibparam[2][1])
                ch4.set(calibparam[3][0])
                en4.set(calibparam[3][1])
            except: 
                pass
            
            __self__.ConfigDiag_header = Label(ParamFrame, text="Channel\tEnergy").grid(\
                    row=0,columnspan=2,sticky=W+E)
            Channel1 = Entry(ParamFrame,textvariable=ch1).grid(row=1,column=0)
            Channel2 = Entry(ParamFrame,textvariable=ch2).grid(row=2,column=0)
            Channel3 = Entry(ParamFrame,textvariable=ch3).grid(row=3,column=0)
            Channel4 = Entry(ParamFrame,textvariable=ch4).grid(row=4,column=0)
            EnergyBox1 = Entry(ParamFrame,textvariable=en1).grid(row=1,column=1)
            EnergyBox2 = Entry(ParamFrame,textvariable=en2).grid(row=2,column=1)
            EnergyBox3 = Entry(ParamFrame,textvariable=en3).grid(row=3,column=1)
            EnergyBox4 = Entry(ParamFrame,textvariable=en4).grid(row=4,column=1)
            
            OkButton = Button(ButtonFrame,text="SAVE",command=save_param).grid(row=5,columnspan=2)
            
            place_center(__self__.ConfigDiag,CalibDiag)
        
        def check_method_and_save():
            if CalibVar.get() == 'manual':
                manual_calib()
            else: save_config()

        def save_config():
            configdict = {'directory':DirectoryVar.get(),'bgstrip':BgstripVar.get(),\
                    'ratio':RatioVar.get(),'thickratio':ThickVar.get(),'calibration':CalibVar.get(),\
                    'enhance':EnhanceVar.get(),'peakmethod':MethodVar.get()}
            
            if os.path.exists(SpecRead.samples_folder + configdict['directory'] + '\\'):
                cfgpath = os.getcwd() + '\config.cfg'
                cfgfile = open(cfgpath,'w+')
                cfgfile.write("<<CONFIG_START>>\r")
                for key in configdict:
                    cfgfile.write("{} = {}\r".format(key,configdict[key]))
                cfgfile.write("<<CALIBRATION>>\r")
                
                SpecRead.DIRECTORY = configdict['directory'] + '\\'
                SpecRead.selected_sample_folder = SpecRead.samples_folder + SpecRead.DIRECTORY+'\\'
                SpecRead.FIRSTFILE_ABSPATH = SpecRead.findprefix()
                
                if configdict['calibration'] == 'manual': 
                    calibparam = ManualParam
                else: 
                    SpecRead.CONFIG['calibration'] = 'from_source'
                    calibparam = SpecRead.getcalibration()

                for pair in calibparam:
                    cfgfile.write("{0}\t{1}\r".format(pair[0],pair[1]))
                cfgfile.write("<<END>>\r")
                cfgfile.close()
                
                SpecRead.setup()
                print(SpecRead.CONFIG)
                __self__.ConfigDiag.destroy()
                try: 
                    __self__.ResetWindow.destroy()
                    CalibDiag.destroy()
                except: pass
                
                call_compilecube()
                __self__.write_stat()
                __self__.draw_map()
                __self__.toggle_(toggle='on')

            else:
                ErrorMessage("Directory {} not found!\nConfig.cfg saved!".format(configdict['directory']))
                
                cfgpath = os.getcwd() + '\config.cfg'
                cfgfile = open(cfgpath,'w+')
                cfgfile.write("<<CONFIG_START>>\r")
                for key in configdict:
                    cfgfile.write("{} = {}\r".format(key,configdict[key]))
                cfgfile.write("<<CALIBRATION>>\r")
                
                if configdict['calibration'] == 'manual': 
                    calibparam = ManualParam
                else: 
                    calibparam = [[0,0],[0,0],[0,0]]

                for pair in calibparam:
                    cfgfile.write("{0}\t{1}\r".format(pair[0],pair[1]))
                cfgfile.write("<<END>>\r")
                cfgfile.close()
                
                SpecRead.setup()
                __self__.ConfigDiag.destroy()
                try: 
                    __self__.ResetWindow.destroy()
                    CalibDiag.destroy()
                except: pass
                __self__.write_stat()
                __self__.draw_map()
       
        __self__.ConfigDiag = Toplevel()
        __self__.ConfigDiag.resizable(False,False)
        __self__.ConfigDiag.title("Configuration")

        Label1 = Label(__self__.ConfigDiag, text="Sample directory:")
        Label2 = Label(__self__.ConfigDiag, text="Background strip mode:")
        Label3 = Label(__self__.ConfigDiag, text="Calculate ratios?")
        Label4 = Label(__self__.ConfigDiag, text="Thick ratio:")
        Label5 = Label(__self__.ConfigDiag, text="Calibration:")
        Label6 = Label(__self__.ConfigDiag, text="Enhance image?")
        Label7 = Label(__self__.ConfigDiag, text="Netpeak area method:")
        
        Label1.grid(row=0,column=0,sticky=W,pady=3)
        Label2.grid(row=1,column=0,sticky=W,pady=3)
        Label3.grid(row=2,column=0,sticky=W,pady=3)
        Label4.grid(row=3,column=0,sticky=W,pady=3)
        Label5.grid(row=4,column=0,sticky=W,pady=3)
        Label6.grid(row=5,column=0,sticky=W,pady=3)
        Label7.grid(row=6,column=0,sticky=W,pady=3)
        
        DirectoryVar = StringVar(__self__.ConfigDiag)
        __self__.ConfigDiagDirectory = Entry(__self__.ConfigDiag,textvariable=DirectoryVar)
        
        BgstripVar = StringVar(__self__.ConfigDiag)
        __self__.ConfigDiagBgstrip = ttk.Combobox(__self__.ConfigDiag, textvariable=BgstripVar, values=("None","SNIPBG"))
        
        RatioVar = BooleanVar()
        __self__.ConfigDiagRatio = Checkbutton(__self__.ConfigDiag, variable=RatioVar)
        
        ThickVar = DoubleVar()
        __self__.ConfigDiagThick = Entry(__self__.ConfigDiag, textvariable=ThickVar)
        
        CalibVar = StringVar(__self__.ConfigDiag)
        __self__.ConfigDiagCalib = ttk.Combobox(__self__.ConfigDiag, textvariable=CalibVar, values=("from_source","manual"))

        EnhanceVar = BooleanVar()
        __self__.ConfigDiagEnhance = Checkbutton(__self__.ConfigDiag, variable=EnhanceVar)
        
        MethodVar = StringVar(__self__.ConfigDiag)
        __self__.ConfigDiagMethod = ttk.Combobox(__self__.ConfigDiag, textvariable=MethodVar, values=("simple_roi","auto_roi","PyMcaFit"))
        
        DirectoryVar.set(SpecRead.CONFIG.get('directory'))
        BgstripVar.set(SpecRead.CONFIG.get('bgstrip'))
        RatioVar.set(SpecRead.CONFIG.get('ratio'))
        ThickVar.set(SpecRead.CONFIG.get('thickratio'))
        CalibVar.set(SpecRead.CONFIG.get('calibration'))
        MethodVar.set(SpecRead.CONFIG.get('peakmethod'))
        EnhanceVar.set(SpecRead.CONFIG.get('enhance'))

        __self__.ConfigDiagDirectory.grid(row=0,column=1,sticky=E,padx=16)
        __self__.ConfigDiagBgstrip.grid(row=1,column=1,sticky=E,padx=16)
        __self__.ConfigDiagRatio.grid(row=2,column=1,sticky=E,padx=16)
        __self__.ConfigDiagThick.grid(row=3,column=1,sticky=E,padx=16)
        __self__.ConfigDiagCalib.grid(row=4,column=1,sticky=E,padx=16)
        __self__.ConfigDiagEnhance.grid(row=5,column=1,sticky=E,padx=16)
        __self__.ConfigDiagMethod.grid(row=6,column=1,sticky=E,padx=16)
        
        Label(__self__.ConfigDiag).grid(row=7)
        ButtonsFrame = Frame(__self__.ConfigDiag)
        ButtonsFrame.grid(row=8,columnspan=2)
        SaveButton = Button(ButtonsFrame, text="SAVE", justify=CENTER, width=12, pady=4, bd=3,\
                command=check_method_and_save)
        SaveButton.grid(row=8,column=0,sticky=S,padx=16)
        CancelButton = Button(ButtonsFrame, text="CANCEL", justify=CENTER, width=12, pady=4, bd=3,\
                command=__self__.wipe)
        CancelButton.grid(row=8,column=1,sticky=S,padx=16)
        
        place_center(root.master,__self__.ConfigDiag)

        return 0

logging.info("Loading GUI...")
Samples = Samples()
Samples.list_all()
root = MainGUI(Samples.samples_database)
#ani = animation.FuncAnimation(root.sample_figure, root.refresh_ImageCanvas, blit=True, interval=1200)
root.master.mainloop()

