#################################################################
#                                                               #
#          Configuration Parser                                 #
#                        version: 2.4.0 - May - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import Engine.SpecRead as sp 
import Engine.SpecMath as sm
from GUI.Utils import *
from .AdvCalibration import AdvCalib
import Constants
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import numpy as np
import sys, os, gc, copy, random
import shutil

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
from matplotlib import style
style.use('ggplot')

# only display the buttons we need
class NavigationToolbar(NavigationToolbar2Tk):
    toolitems = (
    ('Home', 'Reset original view', 'home', 'home'),
    ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
    ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
    ('Save', 'Save the figure', 'filesave', 'save_figure')
  )


def wipe_stats(root):
    if Constants.CONFIG["directory"] == root.temporaryh5 and root.temporaryh5 != "None":
        root.TableMiddle.config(state=NORMAL)
        root.TableMiddle.delete(0,END)
        root.StatusBox.delete(0,END)
        root.TableMiddle.config(state=DISABLED)
        root.TableMiddle.update_idletasks()
        root.StatusBox.update_idletasks()
        ##################################################

        del root.samples[Constants.CONFIG["directory"]]
        del root.samples_path[Constants.CONFIG["directory"]]
        del root.mcacount[Constants.CONFIG["directory"]]
        del root.mca_indexing[Constants.CONFIG["directory"]]
        del root.mca_extension[Constants.CONFIG["directory"]]
        gc.collect()
        try:
            temph5_idx = root.SamplesWindow_TableLeft.get(0, END).index(root.temporaryh5)
            root.SamplesWindow_TableLeft.delete(temph5_idx)
        except: pass
        root.temporaryh5 = "None"
        temp_path = os.path.join(
            sp.__PERSONAL__,"output",Constants.CONFIG["directory"])
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
        Constants.MY_DATACUBE = None
        gc.collect()
        sp.conditional_setup()
        root.load_cube()
        root.draw_map()
        root.toggle_(toggle="off")
        root.SampleVar.set("Sample on memory: None")
        try:
            if root.SamplesWindow.state() == "normal":
                root.SamplesWindow.deiconify()
                root.SamplesWindow_TableLeft.focus_set()
        except: pass
        return
    sp.conditional_setup()
    Constants.MY_DATACUBE = None
    root.h5path = "None"
    gc.collect()
    try:
        if isinstance( root.samples[Constants.CONFIG["directory"]],tuple):
            root.samples.pop(Constants.CONFIG["directory"])
    except KeyError:
        pass
    root.load_cube()
    root.write_stat()
    root.draw_map()
    root.toggle_(toggle="off")
    root.SampleVar.set("Sample on memory: None")
    try:
        if root.SamplesWindow.state() == "normal":
            root.SamplesWindow_TableLeft.focus_set()
    except: pass
    return


class PeakClipper:
    """Creates a dialog to set-up SNIPBG parameters"""
    def __init__(__self__,parent,mode=None):
        """ Parent is ConfigDiag class """
        __self__.root = parent.root
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

        __self__.right_panel.grid(row=0,rowspan=2,column=1,padx=10,sticky="") 
        __self__.frame1.grid(row=0,rowspan=3,column=0,sticky=N+E+W+S)
        __self__.frame2.grid(row=1,column=1,padx=15,sticky="")
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

        if mode == "SNIPBG":
            __self__.savgol.set(5)
            __self__.order.set(3)
            __self__.window.set(5)
            __self__.iter.set(24)
        elif mode == "Polynomial":
            __self__.nglobal.set(6)
            __self__.r_factor.set(2)
        
        __self__.build_widgets()
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
        __self__.randomize = Button(
                __self__.right_panel, 
                text="Pick random spectrum",
                command=__self__.random_sample, 
                justify=CENTER)
        __self__.randomize.grid(row=0,column=0,columnspan=2,pady=15)
        
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

        __self__.label_savgol.grid(row=1,column=0)
        __self__.label_order.grid(row=2,column=0)
        __self__.label_window.grid(row=3,column=0)
        __self__.label_iter.grid(row=4,column=0)
        __self__.entry_savgol.grid(row=1,column=1,sticky=E)
        __self__.entry_order.grid(row=2,column=1,sticky=E)
        __self__.entry_window.grid(row=3,column=1,sticky=E)
        __self__.entry_iter.grid(row=4,column=1,sticky=E)
        
        __self__.label_nglobal.grid(row=1,column=0)
        __self__.label_r_factor.grid(row=2,column=0)
        __self__.entry_nglobal.grid(row=1,column=1,sticky=E)
        __self__.entry_r_factor.grid(row=2,column=1,sticky=E)

        # frame 4 (lower-right)
        __self__.button_try = Button(__self__.frame4,text="Try",width=10,
                justify=CENTER,command=__self__.refresh_plot)
        __self__.button_save = Button(__self__.frame4, text="Save",width=10,
                justify=CENTER,command=__self__.save)
        __self__.button_cancel = Button(__self__.frame4, text="Cancel",width=10,
                justify=CENTER,command=__self__.kill)

        __self__.button_try.grid(row=0,column=0)
        __self__.button_save.grid(row=0,column=1)
        __self__.button_cancel.grid(row=1,column=0,columnspan=2)

        __self__.master.update()
        place_center(__self__.parent.master,__self__.master)
        __self__.master.focus_set()
        icon = os.path.join(os.getcwd(),"images","icons","settings.ico")
        __self__.master.iconbitmap(icon)
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
            background = sm.peakstrip(__self__.spectrum,cycles,window,savgol,order)
        elif __self__.mode == "Polynomial":
            nglobal = __self__.nglobal.get()
            r_factor = __self__.r_factor.get()
            background = sm.peakstrip(__self__.spectrum,cycles,window,savgol,order)
        return background

    def refresh_plot(__self__):
        __self__.plot.clear()
        folder = Constants.CONFIG.get('directory')

        """ Gives the spectrum name for label according to need. Is user loaded a list
        of files, name must be taken straight from the list. Else, the file builder
        concatenates prefix, index and prefix to form the name """
        
        if isinstance(__self__.root.samples[folder],tuple): 
            label = __self__.root.samples[folder][__self__.sample].split("/")[-1]
        else:
            label = __self__.root.samples[folder]+"{0}.{1}".format(
                        __self__.sample,__self__.root.mca_extension[folder])

        if Constants.PLOTSCALE == None:
            __self__.plot.set_ylabel("Counts")
            __self__.plot.set_xlabel("Channels")
            __self__.plot.plot(__self__.spectrum,
                    color="blue",
                    label=label)
            try: 
                background = __self__.stripbg()
                __self__.plot.plot(background, label="Background",color="yellow")
            except Exception as e: 
                pass
            __self__.plot.set_ylim(bottom=0)
        else:
            __self__.plot.set_ylabel("Counts")
            __self__.plot.set_xlabel("Channels")
            __self__.plot.semilogy(__self__.spectrum,
                    color="blue",
                    label=label)
            try: 
                background = __self__.stripbg()
                __self__.plot.plot(background, label="Background",color="yellow")
            except Exception as e: 
                print(e)
                pass
            __self__.plot.set_ylim(bottom=10e-2)
            __self__.plot.set_ylim(top=1.10*__self__.spectrum.max())

        __self__.plot.legend(loc="upper right")
        __self__.canvas.draw()

    def random_sample(__self__):
        folder = Constants.CONFIG.get("directory")
        spec_no = __self__.root.mcacount[folder]

        ################################################################
        # IF PARENT HAS A MATRIX, IT LOADED AN H5 FILE OR AN EDF STACK #
        ################################################################
        if __self__.parent.matrix.shape[2] > 1:
            __self__.sample = random.randint(1,spec_no-1)
            __self__.spectrum = __self__.parent.matrix.reshape(-1,__self__.parent.matrix.shape[-1])[__self__.sample]
        ################################################
        
        ####################################################################
        # ELSE, IT IS READING MCA EITHER FROM USER LIST OR DETECTED FOLDER #
        ####################################################################
        else:
            """ When loading a list of files - when the sample is manually loaded by the user,
            not detected automatically - __self__.root.samples carries the list of all mca's path """
            if folder == "Training Data 1" or folder == "Training Data 2":
                __self__.sample = random.randint(1,spec_no-1)
                mca = os.path.join(sp.__PERSONAL__,"Example Data",folder,
                        __self__.root.samples[folder]+"{0}.{1}".format(__self__.sample,
                            __self__.root.mca_extension[folder]))
            elif isinstance(__self__.root.samples[folder],tuple):
                __self__.sample = random.randint(1,len(__self__.root.samples[folder]))
                mca = __self__.root.samples[folder][__self__.sample]
            else:
                __self__.sample = random.randint(1,spec_no-1)
                mca = os.path.join(Constants.SAMPLE_PATH,
                        __self__.root.samples[folder]+"{0}.{1}".format(__self__.sample,
                            __self__.root.mca_extension[folder]))
                
            __self__.spectrum = sp.getdata(mca)
        ####################################################################

        if isinstance(__self__.spectrum,np.ndarray):
            __self__.refresh_plot() 
        else:
            messagebox.showerror("EOF Error!","Could not read {} file!".\
                    format(__self__.spectrum))

    def save(__self__):
        __self__.parent.snip_config = __self__.iter.get(),__self__.window.get(),__self__.savgol.get(),__self__.order.get()
        proceed = __self__.verify_values(__self__.parent.snip_config)
        if proceed == True: __self__.kill()
        else: messagebox.showerror("Value Error", "Parameters not valid. No negative or zero values are valid. Sav-gol window must be odd and greater than Sav-gol order.")

    def kill(__self__, event=""):
        __self__.master.grab_release()
        __self__.root.ConfigDiag.master.grab_set()
        __self__.master.destroy()
    
    def verify_values(__self__,snip):
        if snip[0] <= 0 or snip[1] <= 0: return False
        if int(snip[2]%2) == 0: return False
        if snip[3] > snip[2]: return False
        else: return True
        

class ConfigDiag:
    def __init__(__self__, root, matrix=None, calib=None):
        __self__.root = root
        __self__.calibparams = calib
        #NOTE: only parsed when loading an h5 file
        #NOTE: It does not matter if we change the global DATACUBE here
        #In any way we close the dialog, the global variable is reset
        if Constants.MY_DATACUBE is not None: Constants.MY_DATACUBE.calibration = calib 
        __self__.master = Toplevel(master = __self__.root.master)
        __self__.master.grab_set()
        __self__.master.resizable(False,False)
        __self__.master.title("Configuration")
        __self__.master.bind("<Escape>",__self__.wipe)
        __self__.master.bind("<Return>",__self__.check_method_and_save)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.wipe)
        __self__.Frame = Frame(__self__.master,padx=15,pady=15)
        __self__.Labels = Frame(__self__.master,padx=15,pady=15)
        __self__.Frame.grid(row=0, column=1)
        __self__.Labels.grid(row=0, column=0)
        __self__.matrix = matrix
        __self__.specsize = matrix.shape[2]

    def check_method_and_save(__self__,e=""):
        if __self__.CalibVar.get() == "simple":
            __self__.manual_calib()
        elif __self__.CalibVar.get() == "advanced":
            AdvCalib(__self__, __self__.root)
        else: __self__.save_config()

    def save_param(__self__, advparams=None):
        if __self__.CalibVar.get() == "simple":
            EntryParam = []
            entries = [
                    [__self__.ch1.get(),__self__.en1.get()],
                    [__self__.ch2.get(),__self__.en2.get()],
                    [__self__.ch3.get(),__self__.en3.get()],
                    [__self__.ch4.get(),__self__.en4.get()]]
            for index in range(len(entries)):
                if entries[index][0] != 0 or entries[index][1] != 0:
                    EntryParam.append(entries[index])

        elif __self__.CalibVar.get() == "advanced":
            EntryParam = advparams

        ##############################
        # VERIFIES CALIBRATION INPUT #
        ##############################
        if EntryParam == []:
            messagebox.showerror("Calibration Error",
                    "No acceptable parameters passed!")
            try: __self__.CalibDiag.focus_set()
            except: pass
            __self__.root.ManualParam = []
            raise ValueError("No acceptable parameters passed!")
        elif len(EntryParam) <= 1:
            messagebox.showerror("Calibration Error",
                    "Need at least two anchors!")
            try: __self__.CalibDiag.focus_set()
            except: pass
            __self__.root.ManualParam = []
            raise ValueError("Calibration need at least two anchors!")
        for index in range(len(EntryParam)):
            if EntryParam[index][0] > 0 and EntryParam[index][1] > 0:
                __self__.root.ManualParam.append(EntryParam[index])
            elif EntryParam[index][0] <= 0 or EntryParam[index][1] <= 0:
                messagebox.showerror("Calibration Error",
                        "Can't receive negative or zero values!")
                __self__.root.ManualParam = []
                raise ValueError("Manual calibration can't receive negative or zero values!")
        ##############################

        if __self__.CalibVar.get() == "simple": __self__.CalibDiag.grab_release()
        __self__.save_config()

    def wipe(__self__,e=""):
        try:
            __self__.master.grab_release()
            __self__.master.destroy()
        except: pass
        Constants.FTIR_DATA = 0
        wipe_stats(__self__.root)

    def manual_calib(__self__):
        __self__.CalibDiag = Toplevel(master = __self__.master)
        __self__.CalibDiag.title("Manual configuration")
        __self__.CalibDiag.resizable(False,False)
        __self__.CalibDiag.protocol("WM_DELETE_WINDOW",__self__.kill_manual_calib)
        __self__.CalibDiag.grab_set()
        icon = os.path.join(os.getcwd(),"images","icons","settings.ico")
        __self__.CalibDiag.iconbitmap(icon)
        ParamFrame = Frame(__self__.CalibDiag)
        ParamFrame.pack()
        ButtonFrame = Frame(__self__.CalibDiag)
        ButtonFrame.pack()

        __self__.ch1 = IntVar()
        __self__.ch2 = IntVar()
        __self__.ch3 = IntVar()
        __self__.ch4 = IntVar()

        __self__.en1 = DoubleVar()
        __self__.en2 = DoubleVar()
        __self__.en3 = DoubleVar()
        __self__.en4 = DoubleVar()

        try:
            # gets calibration parameters read while performing last
            # setup or conditional setup and fills entries

            Constants.CONFIG['calibration'] = 'simple'
            if __self__.calibparams is None: calibparam = sp.getcalibration()
            else: calibparam = __self__.calibparams
            __self__.ch1.set(calibparam[0][0])
            __self__.en1.set(calibparam[0][1])
            __self__.ch2.set(calibparam[1][0])
            __self__.en2.set(calibparam[1][1])
            __self__.ch3.set(calibparam[2][0])
            __self__.en3.set(calibparam[2][1])
            __self__.ch4.set(calibparam[3][0])
            __self__.en4.set(calibparam[3][1])
        except:
            pass

        __self__.ConfigDiag_header = Label(ParamFrame, text="Channel\tEnergy").grid(
                row=0,columnspan=2,sticky=W+E)
        Channel1 = Entry(ParamFrame,textvariable=__self__.ch1).grid(row=1,column=0)
        Channel2 = Entry(ParamFrame,textvariable=__self__.ch2).grid(row=2,column=0)
        Channel3 = Entry(ParamFrame,textvariable=__self__.ch3).grid(row=3,column=0)
        Channel4 = Entry(ParamFrame,textvariable=__self__.ch4).grid(row=4,column=0)
        EnergyBox1 = Entry(ParamFrame,textvariable=__self__.en1).grid(row=1,column=1)
        EnergyBox2 = Entry(ParamFrame,textvariable=__self__.en2).grid(row=2,column=1)
        EnergyBox3 = Entry(ParamFrame,textvariable=__self__.en3).grid(row=3,column=1)
        EnergyBox4 = Entry(ParamFrame,textvariable=__self__.en4).grid(row=4,column=1)

        OkButton = ttk.Button(ButtonFrame,text="Save",command=__self__.save_param).grid(
                row=5,columnspan=2,pady=(6,6))

        __self__.CalibDiag.grab_set()
        place_center(__self__.master,__self__.CalibDiag)

    def call_PeakClipper(__self__):
        if __self__.BgstripVar.get() == "None":
            messagebox.showinfo("BG Config","No background estimation mode selected!")
            return
        elif __self__.BgstripVar.get() == "SNIPBG":
            __self__.master.grab_release()
            __self__.clipper = PeakClipper(__self__,mode="SNIPBG")
            __self__.clipper.master.grab_set()
        elif __self__.BgstripVar.get() == "Polynomial":
            __self__.master.grab_release()
            __self__.clipper = PeakClipper(__self__,mode="Polynomial")
            __self__.clipper.master.grab_set()

    def kill_manual_calib(__self__):
        __self__.CalibDiag.grab_release()
        __self__.master.focus_set()
        __self__.CalibDiag.destroy()
        del __self__

    def save_config(__self__,e=""):

        """ A workaround to always have Training Data in samples list and working, is
        backing up the samples_folder variable, changing it temporarily to compile the
        Training Data datacube and then set it back so the other samples can be compiled
        properly """

        samples_folder_backup = copy.deepcopy(Constants.SAMPLES_FOLDER)
        if __self__.DirectoryVar.get() == "Training Data 1" or\
                __self__.DirectoryVar.get() == "Training Data 2":
            Constants.SAMPLES_FOLDER = os.path.join(sp.__PERSONAL__,"Example Data")

        ##########################################################

        configdict = {"directory":__self__.DirectoryVar.get(),
                "bgstrip":__self__.BgstripVar.get(),
                "ratio":__self__.RatioVar.get(),
                "calibration":__self__.CalibVar.get(),
                "enhance":__self__.EnhanceVar.get(),
                "peakmethod":__self__.MethodVar.get(),
                "bg_settings":__self__.root.snip_config}
        if Constants.FTIR_DATA:
            configdict["ftir"] = True
        else: pass

        if not os.path.exists(sp.output_path):
            try:
                os.mkdir(sp.output_path)
            except IOError as exception:
                logger.warning("Error {}.".format(exception.__class__.__name__))
                logger.warning("Can't create output folder {}".format(sp.output_path))
                if exception.__class__.__name__ == "FileExistsError":
                    exists = "Folder already exists!"
                else: exists = None
                messagebox.showerror("{}".format(exception.__class__.__name__),
                        "Cannot create output folder {}\n{}".format(
                            sp.output_path, exists))
                __self__.root.write_stat()
                __self__.root.draw_map()
                return
            if not os.path.exists(Constants.DIMENSION_FILE):
                dm_file = open(os.path.join(sp.output_path,"colonneXrighe.txt"),"w")
                dm_file.write("righe\t{}\n".format(__self__.root.config_xy[0]))
                dm_file.write("colonne\t{}\n".format(__self__.root.config_xy[1]))
                dm_file.write(5*"*"+" user input data "+5*"*")
                dm_file.close()

        if os.path.exists(__self__.root.samples_path[Constants.DIRECTORY])\
                or isinstance(__self__.root.samples[configdict["directory"]],tuple):
            Constants.DIRECTORY = configdict["directory"]
            Constants.SAMPLE_PATH = __self__.root.samples_path[configdict["directory"]]
            if not isinstance(__self__.root.samples[configdict["directory"]],tuple):
                Constants.FIRSTFILE_ABSPATH = os.path.join(Constants.SAMPLE_PATH,
                    __self__.root.samples[configdict["directory"]]+\
                    __self__.root.mca_indexing[configdict["directory"]]+\
                    "."+__self__.root.mca_extension[configdict["directory"]])

            # reads configuration integrity prior opening config.cfg for writing
            if configdict["calibration"] == "simple" \
                    or\
                    configdict["calibration"] == "manual"\
                    or\
                    configdict["calibration"] == "advanced":
                calibparam = __self__.root.ManualParam

            elif configdict["calibration"] == "from_source":
                Constants.CONFIG["calibration"] = "from_source"
                if __self__.calibparams is None: calibparam = sp.getcalibration()
                else: calibparam = __self__.calibparams
            elif configdict["calibration"] == "ftir_source":
                Constants.CONFIG["calibration"] = "ftir_source"
                if __self__.calibparams is None: calibparam = sp.getcalibration()
                else: calibparam = __self__.calibparams
            else:
                raise ValueError("Didn't understand caibration method {0} input".format(configdict["calibration"]))
                return

            cfgpath = os.path.join(sp.__PERSONAL__,"bin","config.cfg")
            cfgfile = open(cfgpath,"w+")
            cfgfile.write("<<CONFIG_START>>\r")
            for key in configdict:
                cfgfile.write("{} = {}\r".format(key,configdict[key]))
            cfgfile.write("<<CALIBRATION>>\r")
            for pair in calibparam:
                cfgfile.write("{0}\t{1}\r".format(pair[0],pair[1]))
            cfgfile.write("<<END>>\r")
            cfgfile.close()

            sp.setup(__self__.root.samples[configdict["directory"]],
                    __self__.root.mca_indexing[configdict["directory"]],
                    __self__.root.mca_extension[configdict["directory"]])
            __self__.master.grab_release()
            __self__.master.destroy()
            try: __self__.CalibDiag.destroy()
            except: pass
            try: __self__.root.ResetWindow.destroy()
            except: pass

            __self__.root.call_compilecube()
            __self__.root.load_cube()
            __self__.root.write_stat()
            __self__.root.draw_map()
            __self__.root.toggle_(toggle='on')
            if __self__.root.temporaryh5 != "None": 
                __self__.root.ButtonReset.config(state=DISABLED)

        else:
            cfgpath = os.path.join(sp.__PERSONAL__,"bin","config.cfg")
            cfgfile = open(cfgpath,'w+')
            cfgfile.write("<<CONFIG_START>>\r")
            for key in configdict:
                cfgfile.write("{} = {}\r".format(key,configdict[key]))
            cfgfile.write("<<CALIBRATION>>\r")

            if configdict['calibration'] == 'simple':
                calibparam = __self__.root.ManualParam
            else:
                calibparam = [[0,0],[0,0],[0,0]]

            for pair in calibparam:
                cfgfile.write("{0}\t{1}\r".format(pair[0],pair[1]))
            cfgfile.write("<<END>>\r")
            cfgfile.close()
            messagebox.showerror("Directory not found!",
                    "Directory {} not found!\nConfig.cfg saved!".format(
                        configdict['directory']))
            sp.setup(__self__.root.samples[configdict["directory"]],
                    __self__.root.mca_indexing[configdict["directory"]],
                    __self__.root.mca_extension[configdict["directory"]])
            __self__.master.grab_release()
            __self__.master.destroy()
            try: __self__.root.ResetWindow.destroy()
            except: pass
            try: __self__.CalibDiag.destroy()
            except: pass
            __self__.root.write_stat()
            __self__.root.draw_map()
        Constants.SAMPLES_FOLDER = samples_folder_backup

    def build_widgets(__self__):

        Label2 = Label(__self__.Labels, text="Background strip mode:")
        Label3 = Label(__self__.Labels, text="Configure BG strip:")
        Label4 = Label(__self__.Labels, text="Calibration:")
        Label7 = Label(__self__.Labels, text="Area method:")
        Label8 = Label(__self__.Labels, text="Calculate ratios?")

        Label2.grid(row=1,column=0,sticky=W,pady=2)
        Label3.grid(row=2,column=0,sticky=W,pady=2)
        Label4.grid(row=3,column=0,sticky=W,pady=2)
        Label7.grid(row=6,column=0,sticky=W,pady=2)
        Label8.grid(row=7,column=0,sticky=W,pady=2)

        ConfigDiagRatioYes = Label(__self__.Frame, text="Yes/No")
        ConfigDiagRatioYes.grid(row=7,column=1,sticky=E,pady=2)
        ConfigDiagEnhanceYes = Label(__self__.Frame, text="Yes/No")
        ConfigDiagEnhanceYes.grid(row=6,column=1,sticky=E,pady=2)

        __self__.BgstripVar = StringVar()
        __self__.ConfigDiagBgstrip = ttk.Combobox(
                __self__.Frame,
                textvariable=__self__.BgstripVar,
                values=("None","SNIPBG","Polynomial"),
                state="readonly",
                width=13+ConfigDiagRatioYes.winfo_width())

        __self__.DirectoryVar = StringVar()

        __self__.RatioVar = BooleanVar()
        __self__.ConfigDiagRatio = ttk.Checkbutton(__self__.Frame, variable=__self__.RatioVar,
                takefocus=False)

        __self__.ConfigDiagSetBG = ttk.Button(__self__.Frame, text="Set BG",
               width=14+ConfigDiagRatioYes.winfo_width(),
               command=__self__.call_PeakClipper)

        __self__.CalibVar = StringVar()
        __self__.ConfigDiagCalib = ttk.Combobox(
                __self__.Frame,
                textvariable=__self__.CalibVar,
                values=("from_source","simple","advanced"),
                state="readonly",width=13+ConfigDiagRatioYes.winfo_width())

        __self__.EnhanceVar = BooleanVar()

        __self__.MethodVar = StringVar()
        __self__.ConfigDiagMethod = ttk.Combobox(
                __self__.Frame,
                textvariable=__self__.MethodVar,
                values=("simple_roi","auto_roi","auto_wizard","fit_approx"),
                state="readonly",
                width=13+ConfigDiagRatioYes.winfo_width())


        __self__.ConfigDiagBgstrip.grid(row=1,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagSetBG.grid(row=2,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagCalib.grid(row=3,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagMethod.grid(row=6,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagRatio.grid(row=7,column=0,sticky=E,pady=2)

        dimension_text = "Image size = {0} x {1} pixels".format(
                __self__.root.config_xy[0],__self__.root.config_xy[1])
        img_dimension_display = Label(__self__.master,text=dimension_text)
        img_dimension_display.grid(row=1,column=0,sticky=W,padx=17,pady=2)

        ButtonsFrame = Frame(__self__.master)
        ButtonsFrame.grid(row=8,columnspan=2,pady=10,padx=10)
        SaveButton = ttk.Button(
                ButtonsFrame,
                text="Save",
                width=10,
                command=__self__.check_method_and_save)
        SaveButton.grid(row=8,column=0,sticky=S)
        CancelButton = ttk.Button(
                ButtonsFrame,
                text="Cancel",
                width=10,
                command=__self__.wipe)
        CancelButton.grid(row=8,column=1,sticky=S)

        if Constants.FTIR_DATA:
            __self__.CalibVar.set("ftir_source")
            __self__.BgstripVar.set("not_applicable")
            __self__.ConfigDiagBgstrip.state(["disabled"])
            __self__.ConfigDiagSetBG.config(state=DISABLED)
            __self__.ConfigDiagCalib.config(values=["ftir_source"])
        else:
            __self__.CalibVar.set("from_source")
            __self__.BgstripVar.set("None")
        __self__.DirectoryVar.set(Constants.CONFIG.get('directory'))
        __self__.RatioVar.set(Constants.CONFIG.get('ratio'))
        __self__.MethodVar.set(Constants.CONFIG.get('peakmethod'))
        __self__.EnhanceVar.set(Constants.CONFIG.get('enhance'))

        place_center(__self__.root.master,__self__.master)
        icon = os.path.join(os.getcwd(),"images","icons","settings.ico")
        __self__.master.iconbitmap(icon)
        __self__.root.master.wait_window(__self__.master)
