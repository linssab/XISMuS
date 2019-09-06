#################################################################
#                                                               #
#          Graphical Interface and Core file                    #
#                        version: 1.0a                          #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

from tkinter import *
from tkinter import ttk
from tkinter import simpledialog
import numpy as np
import SpecRead
SpecRead.conditional_setup()
import SpecMath
import Mapping
import ImgMath
import sys, os, pickle
import logging
from matplotlib import pyplot as plt

global MY_DATACUBE
MY_DATACUBE = None
try: load_cube()
except: pass

class ProgressWindow(simpledialog.Dialog):
    
    def __init__(__self__, parent, name):
        ''' Init progress window '''
        Toplevel.__init__(__self__, master=parent)
        __self__.name = name
        __self__.length = 400
        #
        __self__.create_window()
        __self__.create_widgets()

    def create_window(__self__):
        ''' Create progress window '''
        __self__.focus_set()  # set focus on the ProgressWindow
        __self__.grab_set()  # make a modal window, so all events go to the ProgressWindow
        #__self__.transient(self.master)  # show only one window in the task bar
        #
        __self__.title("Busy...")
        __self__.resizable(False, False)  # window is not resizable
        # self.close gets fired when the window is destroyed
        __self__.protocol('WM_DELETE_WINDOW', __self__.close)
        # Set proper position over the parent window
        dx = (__self__.master.winfo_width() >> 1) - (__self__.length >> 1)
        dy = (__self__.master.winfo_height() >> 1) - 50
        __self__.geometry('+{x}+{y}'.format(x = __self__.master.winfo_rootx() + dx,
                                         y = __self__.master.winfo_rooty() + dy))

    def create_widgets(__self__):
        ''' Widgets for progress window are created here '''
        __self__.num = IntVar()
        progress_maximum = SpecRead.getdimension()
        progress_maximum = progress_maximum[0]*progress_maximum[1]
        __self__.maximum = progress_maximum
        __self__.progress = ttk.Progressbar(__self__, maximum=__self__.maximum, orient='horizontal', \
                length=__self__.length, variable=__self__.num, mode='determinate')
        __self__.progress.pack(padx=2, pady=2)
        __self__.next()

    def next(__self__):
        ''' Take next file from the list and do something with it '''
        n = __self__.num.get()
        n += 1
        __self__.num.set(n)
        if n < __self__.maximum:
            __self__.after(1, __self__.next)  # call itself after some time
        else:
            __self__.close()  # close window

    def close(__self__, event=None):
        ''' Close progress window '''
        if __self__.progress['value'] == __self__.maximum:
            print('Ok: process finished successfully')
        else:
            print('Cancel: process is cancelled')
        __self__.master.focus_set()  # put focus back to the parent window
        __self__.destroy()  # destroy progress window

def plot(image,color):
    image_color = ImgMath.colorize(image,color)
    fig, ax = plt.subplots()
    plt.imshow(image_color)
    plt.show()
    return 0

def convert_bytes(num):
    """
    Obtained from https://stackoverflow.com/questions/210408
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def ErrorMessage(message):
    
    ErrorWindow = Toplevel(master=root)
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

def sample_select(event):
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
        SampleVar.set("Sample on memory: "+SpecRead.selected_sample_folder)
        
        try:
           if StatWindow.winfo_exists():
                StatWindow.destroy()
                call_stat()
                root.focus_force()
           else: 
                call_stat()
                root.focus_force()
        except:
            call_stat()
            root.focus_force()
    else: 
        SpecRead.conditional_setup(name=value)
        call_configure()


def call_help():
    HelpWindow = Toplevel(master=root)
    HelpWindow.title("Help")
    HelpWindow.resizable(False,False)
    HelpText= "I will write something here. I promise."
    HelpLabel = Label(HelpWindow, text=HelpText, wraplength=640, anchor=W, justify=LEFT)
    HelpLabel.grid(sticky=W)
    HelpWindow.mainloop()
    return np.nan


class StatWindow:

    def __init__(__self__,master):
        __self__.master = Toplevel(master=master)
        __self__.master.title("Status")
        __self__.master.resizable(False,False)
        __self__.place_widgets()
        __self__.write_stat()

    def place_widgets(__self__):
        __self__.databox = Listbox(__self__.master)
        __self__.databox.pack(side=TOP, fill=BOTH, expand=1)
        __self__.dataframe = Frame(__self__.master, padx=5,pady=5,relief=SUNKEN)
        __self__.dataframe.pack(side=BOTTOM, fill=BOTH)
        
        if os.path.exists(SpecRead.cube_path):
            __self__.TableLabel1 = Label(\
                    __self__.dataframe,text="Configuration embedded:",justify=CENTER)
            __self__.TableLabel2 = Label(__self__.dataframe,text="KEY")
            __self__.TableLabel3 = Label(__self__.dataframe,text="PACKED IN CUBE")
            __self__.TableLabel4 = Label(__self__.dataframe,text="IN CONFIG.CFG")
            __self__.TableLabel1.grid(row=0, columnspan=3)
            __self__.TableLabel2.grid(row=1, column=0)
            __self__.TableLabel3.grid(row=1, column=1)
            __self__.TableLabel4.grid(row=1, column=2)

            __self__.TableLeft = Listbox(__self__.dataframe)
            __self__.TableMiddle = Listbox(__self__.dataframe)
            __self__.TableRight = Listbox(__self__.dataframe)
            __self__.TableLeft.grid(pady=5,row=2, column=0)
            __self__.TableMiddle.grid(pady=5, row=2, column=1)
            __self__.TableRight.grid(pady=5, row=2, column=2)
        else:
            __self__.TableLeft = Listbox(__self__.dataframe)
            __self__.TableRight = Listbox(__self__.dataframe)
            __self__.TableLeft.grid(pady=5, row=2,column=0)
            __self__.TableRight.grid(pady=5, row=2,column=1)

    def write_stat(__self__):
        
        if os.path.exists(SpecRead.selected_sample_folder):
            __self__.databox.insert(\
                    END, "\nSample files location: {0}\n".format(SpecRead.selected_sample_folder))
            __self__.no_sample = False
        else: 
            __self__.databox.insert(END, "\nSample {} not found!\n".format(SpecRead.DIRECTORY))
            __self__.no_sample = True

        if os.path.exists(SpecRead.cube_path):
            cube_stats = os.stat(SpecRead.cube_path)
            cube_size = convert_bytes(cube_stats.st_size)
            __self__.databox.insert(END,"Datacube is compiled. Cube size: {0}".format(cube_size))
            __self__.databox.insert(END,"Verifying packed elements...")
            
            packed_elements = MY_DATACUBE.check_packed_elements()
            if len(packed_elements) == 0: __self__.databox.insert(END,"None found.")
            else: 
                for element in packed_elements:
                    __self__.databox.insert(END,"Found a map for {0}".format(element))
            __self__.databox.insert(END,"Done.")
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
            __self__.databox.insert(END, "No sample configured!") 
            for key in SpecRead.CONFIG:
                __self__.TableLeft.insert(END,key)
                __self__.TableRight.insert(END, "{}".format(SpecRead.CONFIG[key]))

        else: 
            __self__.databox.insert(END, "Datacube not compiled.") 
            __self__.databox.insert(END, "Please compile the cube first.")
            for key in SpecRead.CONFIG:
                __self__.TableLeft.insert(END,key)
                __self__.TableRight.insert(END, "{}".format(SpecRead.CONFIG[key]))

def call_stat():
    
    sample_status = StatWindow(root)
    """ 
    global StatWindow, TableRight
    load_cube()

    StatWindow = Toplevel(master=root)
    StatWindow.title("Status")
    StatWindow.resizable(False,False)
    DataBox = Listbox(StatWindow)
    DataBox.pack(side=TOP, fill=BOTH, expand=1)
    
    if os.path.exists(SpecRead.selected_sample_folder):
        DataBox.insert(END, "\nSample files location: {0}\n".format(SpecRead.selected_sample_folder))
        no_sample = False
    else: 
        DataBox.insert(END, "\nSample {} not found!\n".format(SpecRead.DIRECTORY))
        no_sample = True
    
    DataFrame1 = Frame(StatWindow,padx=5,pady=5,relief=SUNKEN)
    DataFrame1.pack(side=BOTTOM, fill=BOTH)
     
    if os.path.exists(SpecRead.cube_path):
        TableLabel1 = Label(DataFrame1,text="Configuration embedded:",justify=CENTER)
        TableLabel2 = Label(DataFrame1,text="KEY")
        TableLabel3 = Label(DataFrame1,text="PACKED IN CUBE")
        TableLabel4 = Label(DataFrame1,text="IN CONFIG.CFG")
        TableLabel1.grid(row=0, columnspan=3)
        TableLabel2.grid(row=1, column=0)
        TableLabel3.grid(row=1, column=1)
        TableLabel4.grid(row=1, column=2)

        TableLeft = Listbox(DataFrame1)
        TableMiddle = Listbox(DataFrame1)
        TableRight = Listbox(DataFrame1)
        TableLeft.grid(pady=5,row=2, column=0)
        TableMiddle.grid(pady=5, row=2, column=1)
        TableRight.grid(pady=5, row=2, column=2)
    else:
        TableLeft = Listbox(DataFrame1)
        TableRight = Listbox(DataFrame1)
        TableLeft.grid(pady=5, row=2,column=0)
        TableRight.grid(pady=5, row=2,column=1)

    if os.path.exists(SpecRead.cube_path):
        cube_stats = os.stat(SpecRead.cube_path)
        cube_size = convert_bytes(cube_stats.st_size)
        DataBox.insert(END,"Datacube is compiled. Cube size: {0}".format(cube_size))
        DataBox.insert(END,"Verifying packed elements...")
        
        packed_elements = MY_DATACUBE.check_packed_elements()
        if len(packed_elements) == 0: DataBox.insert(END,"None found.")
        else: 
            for element in packed_elements:
                DataBox.insert(END,"Found a map for {0}".format(element))
        DataBox.insert(END,"Done.")
        values_cube, values_cfg, values_keys = [],[],[]
        for key in MY_DATACUBE.config:
            values_cube.append(str(MY_DATACUBE.config[key]))
            values_cfg.append(str(SpecRead.CONFIG[key]))
            values_keys.append(str(key))
        for item in range(len(values_cube)):
            TableLeft.insert(END, "{}".format(values_keys[item]))
            TableMiddle.insert(END, "{}".format(values_cube[item]))
            TableRight.insert(END, "{}".format(values_cfg[item]))
    
    elif no_sample == True:
        DataBox.insert(END, "No sample configured!") 
        for key in SpecRead.CONFIG:
            TableLeft.insert(END,key)
            TableRight.insert(END, "{}".format(SpecRead.CONFIG[key]))

    else: 
        DataBox.insert(END, "Datacube not compiled.") 
        DataBox.insert(END, "Please compile the cube first.")
        for key in SpecRead.CONFIG:
            TableLeft.insert(END,key)
            TableRight.insert(END, "{}".format(SpecRead.CONFIG[key]))
    StatWindow.mainloop()
"""
def refresh_stat():
    try: 
        if StatWindow.winfo_exists():
            StatWindow.destroy()
            call_stat()
    except: 
        load_cube()
        pass

def call_listsamples():
    SamplesWindow = Toplevel(master=root)
    SamplesWindow.title("Sample List")
    SamplesWindow.resizable(False,False) 
    LabelLeft = Label(SamplesWindow, text="FOLDER")
    LabelRight = Label(SamplesWindow, text="MCA PREFIX")
    TableLeft = Listbox(SamplesWindow, height=40)
    TableLeft.bind('<Double-Button-1>', sample_select)
    TableRight = Listbox(SamplesWindow, height=40)
    
    LabelLeft.grid(row=0,column=0)
    LabelRight.grid(row=0,column=1)
    TableLeft.grid(pady=5, row=1,column=0)
    TableRight.grid(pady=5, row=1,column=1)
    
    samples = [name for name in os.listdir(SpecRead.samples_folder) \
            if os.path.isdir(SpecRead.samples_folder+name)]
    samples_database = {}
    for folder in samples:
        TableLeft.insert(END,"{}".format(folder))
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
        samples_database[folder] = mca_prefix
        TableRight.insert(END,"{}".format(mca_prefix))
    SamplesWindow.mainloop()

def reset_sample():
    
    def repack():
        import shutil
        shutil.rmtree(SpecRead.output_path)
        call_compilecube()
        LocalWindow.destroy()
        refresh_stat()   

    if os.path.exists(SpecRead.cube_path):
        
        # creates dialogue to warn cube exists and promp to repack data
        LocalWindow = Toplevel(master=root)
        LocalWindow.title("Attention!")
        LocalWindow.resizable(False,False)
        LocalLabel = Label(LocalWindow, text="Resetting the sample will erase all files in the OUTPUT folder of sample {}! Are you sure you want to proceed?".format(SpecRead.DIRECTORY),\
                padx=10, pady=4, wraplength=root_tuple_size[0])
        LocalLabel.pack()
        Erase_ico = PhotoImage(file = os.getcwd()+'\images\icons\erase.png')
        Erase_ico = Erase_ico.zoom(2, 2)
        EraseLabel = Label(LocalWindow, image = Erase_ico).pack(side=LEFT, pady=8, padx=16)
        YesButton = Button(LocalWindow, text="Yes", justify=CENTER,\
                command=repack, width=10, bd=3).pack(side=TOP,pady=5)
        NoButton = Button(LocalWindow, text="No", justify=CENTER,\
                command=LocalWindow.destroy, width=10, bd=3).pack(side=TOP, pady=5)
        LocalWindow.mainloop()
    else:
        ErrorMessage("Can't find sample {}!".format(SpecRead.DIRECTORY))

def call_compilecube():
    
    try: os.mkdir(SpecRead.output_path)
    except: pass
    if os.path.exists(SpecRead.cube_path): pass
    else:
        #try: 
        
        specbatch = SpecMath.datacube(['xrf'],SpecRead.CONFIG)
        specbatch.compile_cube()

        Progress = ProgressWindow(root,"Loading...")
        root.wait_window(Progress)
    
        #except:
        #    ErrorMessage("Can't find sample {}!".format(SpecRead.DIRECTORY))

def call_configure():
    
    global ConfigDiag
    global ManualParam
    ManualParam = []

    def manual_calib():
        
        global CalibDiag
        
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

        CalibDiag = Toplevel(master=ConfigDiag)
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
        
        ConfigDiag_header = Label(ParamFrame, text="Channel\tEnergy").grid(\
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

        CalibDiag.mainloop()
    
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
            ConfigDiag.destroy()
            try: CalibDiag.destroy()
            except: pass
            
            call_compilecube()
            refresh_stat()
        
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
            ConfigDiag.destroy()
            try: CalibDiag.destroy()
            except: pass
            refresh_stat()

        return 0
   
    ConfigDiag = Toplevel(master=root)
    ConfigDiag.resizable(False,False)
    ConfigDiag.title("Configuration")

    Label1 = Label(ConfigDiag, text="Sample directory:")
    Label2 = Label(ConfigDiag, text="Background strip mode:")
    Label3 = Label(ConfigDiag, text="Calculate ratios?")
    Label4 = Label(ConfigDiag, text="Thick ratio:")
    Label5 = Label(ConfigDiag, text="Calibration:")
    Label6 = Label(ConfigDiag, text="Enhance image?")
    Label7 = Label(ConfigDiag, text="Netpeak area method:")
    
    Label1.grid(row=0,column=0,sticky=W,pady=3)
    Label2.grid(row=1,column=0,sticky=W,pady=3)
    Label3.grid(row=2,column=0,sticky=W,pady=3)
    Label4.grid(row=3,column=0,sticky=W,pady=3)
    Label5.grid(row=4,column=0,sticky=W,pady=3)
    Label6.grid(row=5,column=0,sticky=W,pady=3)
    Label7.grid(row=6,column=0,sticky=W,pady=3)
    
    DirectoryVar = StringVar(ConfigDiag)
    ConfigDiagDirectory = Entry(ConfigDiag,textvariable=DirectoryVar)
    
    BgstripVar = StringVar(ConfigDiag)
    ConfigDiagBgstrip = ttk.Combobox(ConfigDiag, textvariable=BgstripVar, values=("None","SNIPBG"))
    
    RatioVar = BooleanVar()
    ConfigDiagRatio = Checkbutton(ConfigDiag, variable=RatioVar)
    
    ThickVar = DoubleVar()
    ConfigDiagThick = Entry(ConfigDiag, textvariable=ThickVar)
    
    CalibVar = StringVar(ConfigDiag)
    ConfigDiagCalib = ttk.Combobox(ConfigDiag, textvariable=CalibVar, values=("from_source","manual"))

    EnhanceVar = BooleanVar()
    ConfigDiagEnhance = Checkbutton(ConfigDiag, variable=EnhanceVar)
    
    MethodVar = StringVar(ConfigDiag)
    ConfigDiagMethod = ttk.Combobox(ConfigDiag, textvariable=MethodVar, values=("simple_roi","auto_roi","PyMcaFit"))
    
    DirectoryVar.set(SpecRead.CONFIG.get('directory'))
    BgstripVar.set(SpecRead.CONFIG.get('bgstrip'))
    RatioVar.set(SpecRead.CONFIG.get('ratio'))
    ThickVar.set(SpecRead.CONFIG.get('thickratio'))
    CalibVar.set(SpecRead.CONFIG.get('calibration'))
    MethodVar.set(SpecRead.CONFIG.get('peakmethod'))
    EnhanceVar.set(SpecRead.CONFIG.get('enhance'))

    ConfigDiagDirectory.grid(row=0,column=1,sticky=E,padx=16)
    ConfigDiagBgstrip.grid(row=1,column=1,sticky=E,padx=16)
    ConfigDiagRatio.grid(row=2,column=1,sticky=E,padx=16)
    ConfigDiagThick.grid(row=3,column=1,sticky=E,padx=16)
    ConfigDiagCalib.grid(row=4,column=1,sticky=E,padx=16)
    ConfigDiagEnhance.grid(row=5,column=1,sticky=E,padx=16)
    ConfigDiagMethod.grid(row=6,column=1,sticky=E,padx=16)
    
    Label(ConfigDiag).grid(row=7)
    ButtonsFrame = Frame(ConfigDiag)
    ButtonsFrame.grid(row=8,columnspan=2)
    SaveButton = Button(ButtonsFrame, text="SAVE", justify=CENTER, width=12, pady=4, bd=3,\
            command=check_method_and_save)
    SaveButton.grid(row=8,column=0,sticky=S,padx=16)
    CancelButton = Button(ButtonsFrame, text="CANCEL", justify=CENTER, width=12, pady=4, bd=3,\
            command=ConfigDiag.destroy)
    CancelButton.grid(row=8,column=1,sticky=S,padx=16)

    ConfigDiag.mainloop()

def prompt_folder():
        print("Prompting for samples folder...")

def check_calibration():
    print("Checking calibration...")

def find_elements():
    print("Finding elements...")
    lista_elementos = ['Cu']
    MAPS = Mapping.getpeakmap(lista_elementos,MY_DATACUBE)
    ImgMath.split_and_save(MY_DATACUBE,MAPS,lista_elementos)
    refresh_stat()

def call_heightmap():
    print("Opening heightmap dialogue...")

def root_quit():
    for widget in root.master.winfo_children():
        if isinstance(widget, Toplevel):
            widget.destroy()
    root.destroy()

def call_summation():
    if os.path.exists(SpecRead.cube_path): 
        plt.clf()
        SpecMath.getstackplot(MY_DATACUBE,'-semilog')
    else: ErrorMessage("Can't locate {0}!".format(SpecRead.cube_path))

def call_mps():
    if os.path.exists(SpecRead.cube_path): 
        plt.clf()
        SpecMath.getstackplot(MY_DATACUBE,'-mps')
    else: ErrorMessage("Can't locate {0}!".format(SpecRead.cube_path))

def call_complete():
    if os.path.exists(SpecRead.cube_path): 
        plt.clf()
        SpecMath.getstackplot(MY_DATACUBE,'-bg')
    else: ErrorMessage("Can't locate {0}!".format(SpecRead.cube_path))

def load_cube():
    if os.path.exists(SpecRead.cube_path):
        cube_file = open(SpecRead.cube_path,'rb')
        global MY_DATACUBE
        MY_DATACUBE = pickle.load(cube_file)
        cube_file.close()
    else: pass
    return MY_DATACUBE


class MainGUI:
    def __init__(__self__):
        __self__.master = Tk()
        __self__.master.title("Nichteroy v.1.00 pre-alpha")
        __self__.master.resizable(False,False)
        __self__.build_widgets()
        __self__.master.mainloop()

    def build_widgets(__self__):
        
        # define the frame and layout
        __self__.ButtonsFrame = Frame(__self__.master).pack(side=TOP)
        __self__.ImageFrame = Frame(__self__.master).pack(side=BOTTOM)
        __self__.DataFrame = Frame(__self__.master).pack(side=RIGHT)
        
        __self__.StatusBox = Listbox(__self__.DataFrame)
        __self__.StatusBox.pack(side=TOP, fill=BOTH)
        __self__.ConfigFrame = Frame(__self__.DataFrame, padx=5,pady=5,relief=SUNKEN)
        __self__.ConfigFrame.pack(side=BOTTOM, fill=BOTH)
        
        #####
        # define the tables which go inside the DataFrame (bottom left corner)
        
        __self__.TableLabel1 = Label(\
                __self__.DataFrame,text="Configuration embedded:",justify=CENTER)
        __self__.TableLabel2 = Label(__self__.DataFrame,text="KEY")
        __self__.TableLabel3 = Label(__self__.DataFrame,text="PACKED IN CUBE")
        __self__.TableLabel4 = Label(__self__.DataFrame,text="IN CONFIG.CFG")
        __self__.TableLabel1.pack(side=TOP,fill=X)
        __self__.TableLabel2.pack(side=LEFT,anchor=CENTER)
        __self__.TableLabel3.pack(side=LEFT,anchor=CENTER)
        __self__.TableLabel4.pack(side=LEFT,anchor=CENTER)

        __self__.TableLeft = Listbox(__self__.DataFrame)
        __self__.TableMiddle = Listbox(__self__.DataFrame)
        __self__.TableRight = Listbox(__self__.DataFrame)
        __self__.TableLeft.pack(side=BOTTOM)
        __self__.TableMiddle.pack(side=LEFT)
        __self__.TableRight.pack(side=LEFT)
        
        #####
        # define the menu bar

        __self__.MenuBar = Menu(__self__.master,tearoff=0)
        __self__.Toolbox = Menu(__self__.MenuBar,tearoff=0)
        __self__.derived_spectra = Menu(__self__.Toolbox,tearoff=0)

        __self__.MenuBar.add_cascade(label="Toolbox", menu=__self__.Toolbox)
        __self__.MenuBar.add_command(label="Help", command=call_help)
        __self__.derived_spectra.add_command(label="Summation", command=call_summation)
        __self__.derived_spectra.add_command(label="Maximum Pixel Spectra (MPS)", command=call_mps)
        __self__.derived_spectra.add_command(label="Complete", command=call_complete)
        __self__.Toolbox.add_command(label="Set samples folder...", command=prompt_folder)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_cascade(label="Derived spectra", menu=__self__.derived_spectra)
        __self__.Toolbox.add_command(label="Check calibration", command=check_calibration)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_command(label="Find elements", command=find_elements)
        __self__.Toolbox.add_command(label="Height-mapping", command=call_heightmap)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_command(label="Exit", command=root_quit)

        __self__.master.config(menu=__self__.MenuBar)
        
        #####
        # define the buttons wich go inside the ButtonsFrame (top left corner)

        ImgAnalButton_icon = PhotoImage(file = os.getcwd()+'\images\icons\img_anal.png')
        __self__.ImgAnalButton_icon = ImgAnalButton_icon.subsample(2,2)
        QuitButton_icon = PhotoImage(file = os.getcwd()+'\images\icons\quit.png')
        __self__.QuitButton_icon = QuitButton_icon.subsample(2,2)
        SettingsButton_icon = PhotoImage(file = os.getcwd()+'\images\icons\settings.png')
        __self__.SettingsButton_icon = SettingsButton_icon.subsample(2,2)

        __self__.ButtonStat = Button(__self__.ButtonsFrame, text="Check Sample Status", command=call_stat)
        __self__.ButtonStat.pack(fill=X)
        __self__.ButtonList = Button(__self__.ButtonsFrame, text="Load Sample", command=call_listsamples)
        __self__.ButtonList.pack(fill=X)
        __self__.ButtonReset = Button(__self__.ButtonsFrame, text="Reset Sample", command=reset_sample)
        __self__.ButtonReset.pack(fill=X)
        __self__.ImgAnalButton = Button(__self__.ButtonsFrame, text="Image Analyzer",\
                image=__self__.ImgAnalButton_icon, compound=LEFT, bd=3)
        __self__.ImgAnalButton.pack(fill=X,side=LEFT)
        __self__.QuitButton = Button(__self__.ButtonsFrame, text="Quit",\
                image=__self__.QuitButton_icon, compound=LEFT, bd=3, command=root_quit)
        __self__.QuitButton.pack(fill=X,side=LEFT)
        __self__.SettingsButton = Button(__self__.ButtonsFrame, \
                image=__self__.SettingsButton_icon, bd=3, command=call_configure)
        __self__.SettingsButton.pack(fill=X, side=RIGHT)
        
        #####

        __self__.SampleVar = StringVar()
        __self__.SampleVar.set("Sample on memory: "+SpecRead.selected_sample_folder)
        __self__.StatusBar = Label(__self__.master, textvariable=__self__.SampleVar,\
                bd=1, relief=SUNKEN, anchor=W)
        __self__.StatusBar.pack(side=BOTTOM, fill=X)

        __self__.master.protocol("WM_DELETE_WINDOW", root_quit)

root = MainGUI()

"""
from win32api import GetSystemMetrics
root = Tk()
sample_status = None
root.title("Scanner")
screen_width = GetSystemMetrics(0)
screen_height = GetSystemMetrics(1)
root_tuple_size = (int(round(screen_width*0.15)),int(round(screen_height*0.15)))
root_str_size = str(root_tuple_size[0])+'x'+str(str(root_tuple_size[1]))
root.geometry(root_str_size) 
root.resizable(False,False)

UpperFrame = Frame(root)
UpperFrame.pack(fill=X)
LowerFrame = Frame(root)

MenuBar = Menu(root,tearoff=0)
Toolbox = Menu(MenuBar,tearoff=0)
derived_spectra = Menu(Toolbox,tearoff=0)

MenuBar.add_cascade(label="Toolbox", menu=Toolbox)
MenuBar.add_command(label="Help", command=call_help)
derived_spectra.add_command(label="Summation", command=call_summation)
derived_spectra.add_command(label="Maximum Pixel Spectra (MPS)", command=call_mps)
derived_spectra.add_command(label="Complete", command=call_complete)
Toolbox.add_command(label="Set samples folder...", command=prompt_folder)
Toolbox.add_separator()
Toolbox.add_cascade(label="Derived spectra", menu=derived_spectra)
Toolbox.add_command(label="Check calibration", command=check_calibration)
Toolbox.add_separator()
Toolbox.add_command(label="Find elements", command=find_elements)
Toolbox.add_command(label="Height-mapping", command=call_heightmap)
Toolbox.add_separator()
Toolbox.add_command(label="Exit", command=root_quit)

root.config(menu=MenuBar)
ImgAnalButton_icon = PhotoImage(file = os.getcwd()+'\images\icons\img_anal.png')
ImgAnalButton_icon = ImgAnalButton_icon.subsample(2,2)
QuitButton_icon = PhotoImage(file = os.getcwd()+'\images\icons\quit.png')
QuitButton_icon = QuitButton_icon.subsample(2,2)
SettingsButton_icon = PhotoImage(file = os.getcwd()+'\images\icons\settings.png')
SettingsButton_icon = SettingsButton_icon.subsample(2,2)

ButtonStat = Button(UpperFrame, text="Check Sample Status", command=call_stat)
ButtonStat.pack(fill=X)
ButtonList = Button(UpperFrame, text="Load Sample", command=call_listsamples)
ButtonList.pack(fill=X)
ButtonCompile = Button(UpperFrame, text="Reset Sample", command=reset_sample)
ButtonCompile.pack(fill=X)
ImgAnalButton = Button(LowerFrame, text="Image Analyzer",\
        image=ImgAnalButton_icon, compound=LEFT, bd=3)
ImgAnalButton.pack(fill=X,side=LEFT)
QuitButton = Button(LowerFrame, text="Quit",\
        image=QuitButton_icon, compound=LEFT, bd=3, command=root_quit)
QuitButton.pack(fill=X,side=LEFT)
SettingsButton = Button(LowerFrame, image=SettingsButton_icon, bd=3, command=call_configure)
SettingsButton.pack(fill=X, side=RIGHT)

SampleVar = StringVar()
SampleVar.set("Sample on memory: "+SpecRead.selected_sample_folder)
StatusBar = Label(root, textvariable=SampleVar,\
        bd=1, relief=SUNKEN, anchor=W)
StatusBar.pack(side=BOTTOM, fill=X)

LowerFrame.pack(side=BOTTOM, fill=X)

root.protocol("WM_DELETE_WINDOW", root_quit)
root.mainloop()
"""
#if __name__=="__main__":
"""
    import Compounds
    import numpy as np
    import SpecRead
    import SpecMath
    import ImgMath
    import Mapping
    import EnergyLib
    import matplotlib.pyplot as plt
    
    if flag1 == '-threshold':
        
        if os.path.exists(cube_path):
            print("Loading {0} ...".format(cube_path))
            sys.stdout.flush()
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
        else:
            print("Cube {0} not found. Please run Core.py -compilecube".format(cube_name))

        try: 
            element = sys.argv[2]
            if sys.argv[3].isdigit(): t = int(sys.argv[3])
            if element not in EnergyLib.ElementList:
                raise ValueError("{0} not an element!".format(element))
        except:
            raise ValueError("No threshold input.")
        element_matrix = datacube.unpack_element(element) 
        element_matrix = ImgMath.threshold(element_matrix,t)
        
        fig, ax = plt.subplots()
        image = ax.imshow(element_matrix,cmap='gray')
        ImgMath.colorbar(image)
        ax.set_title("{0} map. Threshold {1}".format(element,t))
        plt.show()
    
    if flag1 == '-lowpass':
        
        if os.path.exists(cube_path):
            print("Loading {0} ...".format(cube_path))
            sys.stdout.flush()
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
        else:
            print("Cube {0} not found. Please run Core.py -compilecube".format(cube_name))

        try: 
            element = sys.argv[2]
            if sys.argv[3].isdigit(): t = int(sys.argv[3])
            if element not in EnergyLib.ElementList:
                raise ValueError("{0} not an element!".format(element))
        except:
            raise ValueError("No threshold input.")
        element_matrix = datacube.unpack_element(element) 
        element_matrix = ImgMath.low_pass(element_matrix,t)
        
        fig, ax = plt.subplots()
        image = ax.imshow(element_matrix,cmap='gray')
        ImgMath.colorbar(image)
        ax.set_title("{0} map. Cutting signals above {1}".format(element,t))
        plt.show()

    if flag1 == '-findelement':    
        input_elements = input('Please input which elements are to be mapped: \n')
        input_elements = input_elements.split(' ')
        for arg in range(len(input_elements)):
            if input_elements[arg] in EnergyLib.ElementList:
                elementlist.append(input_elements[arg])
            else: 
                raise Exception("%s not an element!" % input_elements[arg])
                logging.exception("{0} is not a chemical element!".format(input_elements[arg]))
       
        print("Loading {0}".format(cube_path))
        sys.stdout.flush()
        if os.path.exists(cube_path):
            
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close() 
            
            if '-normalize' in sys.argv:
                Mapping.getpeakmap(elementlist,datacube)
            else:
                Mapping.getpeakmap(elementlist,datacube)
    
        else:
            print("Compile is necessary.")
            print("Please run 'python Core.py -compilecube' and try again.")

    
    if flag1 == '-plotmap':
        print("Loading {0}".format(cube_path))
        sys.stdout.flush()
        if os.path.exists(cube_path):
            
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
            
            Mapping.getdensitymap(datacube)
        else:
            print("Compile is necessary.")
            print("Please run 'python Core.py -compilecube' and try again.")

    if flag1 == '-getratios':
        
        #######################################################################
        # Calculates the thickness of a given layer by using the attenuation  #
        # of the input element. The input element must be from the underlying #
        # layer. Ex.: '-getratios Pb' will calculate the thickness of the pre #
        # defined outer layer (reffered as compound) by using the Pb lines    #
        # attenuation                                                         #
        #######################################################################
        
        for arg in range(len(sys.argv)):
            if sys.argv[arg] in EnergyLib.ElementList:
                elementlist.append(sys.argv[arg])
            else: 
                if sys.argv[arg] in inputlist:
                    pass
                else: 
                    raise Exception("%s not an element!" % sys.argv[arg])
        
        try: 
            ratiofile = SpecRead.output_path + '{1}_ratio_{0}.txt'\
                    .format(elementlist[0],SpecRead.DIRECTORY)
            ratiomatrix = SpecRead.RatioMatrixReadFile(ratiofile)
        except: raise FileNotFoundError("ratio file for {0} not found.".format(elementlist))
        
        if os.path.exists(cube_path):
            print("Loading {0} ...".format(cube_path))
            sys.stdout.flush()
            cube_file = open(cube_path,'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
        else:
            print("Cube {0} not found. Please run Core.py -compilecube".format(cube_name))

        compound = Compounds.compound()
        compound.set_compound('PbWhite')
        compound.identity = 'Pb'
        compound.set_attenuation(elementlist[0])

        #############################
        # COMPOUND IDENTITY ELEMENT #
        #############################
        
        # abundance element method is deprecated
        # preference is given for the identy element from database. nonetheless,
        # if identity element does not exist (for custom or mixture compounds) abundance
        # element is used
        
        mask = ImgMath.mask(datacube,compound)
        mask = ImgMath.threshold(mask,105)
        mae = compound.identity

        print("Most abundant element in compound: {}".format(mae))
        

        #######################################

        try:
            maps = []
            fig, ax = plt.subplots(1,2,sharey=True)
            maps.append(ax[0].imshow(ratiomatrix))
            ax[0].set_title('{} ratio map'.format(elementlist[0]))
            maps.append(ax[1].imshow(mask))
            ax[1].set_title('{} mask'.format(compound.identity))
            ImgMath.colorbar(maps[0])
            ImgMath.colorbar(maps[1])
            plt.show()
            plt.cla()
            plt.clf()
            plt.close()
        except: raise FileNotFoundError("{0} ratio file not found!".format(mae))
        
        heightmap = ImgMath.getheightmap(ratiomatrix,mask,\
                config.get('thickratio'),compound)
        fig, ax = plt.subplots()
        cbar = ax.imshow(heightmap,cmap='gray')
        ax.set_title('heightmap')
        ImgMath.colorbar(cbar)
        plt.show()
        plt.cla()
        plt.clf()
        plt.close()
        ImgMath.plot3D(heightmap)
        """

