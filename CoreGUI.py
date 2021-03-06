#################################################################
#                                                               #
#          Graphical Interface and Core file                    #
#                        version: 1.3.2 - Jan - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

""" Global variables: 
Constants.MY_DATACUBE is the last loaded cube into memory. It is used for almost
every operation, since configuration parameters and data are extracted from it.
Constants.FIND_ELEMENT_LIST: list of elements to be mapped from the datacube. It is
passed to Mapping or Mapping_parallel module. """

def start_up():
    """ Initializes SpecRead global variables and paths """

    SpecRead.conditional_setup()
    logger.info("Setting up...")
    try: load_cube()
    except: pass
    logger.info("Done.")
    Constants.FIND_ELEMENT_LIST = []

def load_user_database():
    """ Read database file and load all entries to global variable """    

    path = os.path.join(SpecRead.__BIN__,"database.dat")
    db = open(path,"r")
    lines = db.readlines() 
    for i in range(1,len(lines),7):
        if lines[i].replace("\n","").startswith("SAMPLE"):
            try:
                name = lines[i].replace("\n","").split("\t")[-1]
                Constants.USER_DATABASE[name] = {}
                Constants.USER_DATABASE[name]["path"] = \
                        lines[i+1].replace("\n","").split("\t")[-1]
                Constants.USER_DATABASE[name]["prefix"] = \
                        lines[i+2].replace("\n","").split("\t")[-1]
                Constants.USER_DATABASE[name]["mcacount"] = \
                        int(lines[i+3].replace("\n","").split("\t")[-1])
                Constants.USER_DATABASE[name]["extension"] = \
                        lines[i+4].replace("\n","").split("\t")[-1]
                Constants.USER_DATABASE[name]["indexing"] = \
                        lines[i+5].replace("\n","").split("\t")[-1]
            except IndexError as exception:
                logging.error("Database.dat integrity may be compromised. Could not load.")
    db.close()

def write_to_user_database(name,sample_path,prefix,count,extension,indexing):
    path = os.path.join(SpecRead.__BIN__,"database.dat")
    db = open(path,"a+")
    db.write("\nSAMPLE\t{}\n".format(name))
    Constants.USER_DATABASE[name] = {}
    db.write("path\t{}\n".format(sample_path))
    Constants.USER_DATABASE[name]["path"] = sample_path
    db.write("prefix\t{}\n".format(prefix))
    Constants.USER_DATABASE[name]["prefix"] = prefix
    db.write("mcacount\t{}\n".format(count))
    Constants.USER_DATABASE[name]["mcacount"] = count
    db.write("extension\t{}\n".format(extension))
    Constants.USER_DATABASE[name]["extension"] = extension
    db.write("indexing\t{}\n".format(indexing))
    Constants.USER_DATABASE[name]["indexing"] = indexing
    db.close()

def remove_entry_from_database(smpl_name):
    path = os.path.join(SpecRead.__BIN__,"database.dat")
    db = open(path,"r")
    lines = db.readlines()
    new_lines = copy.deepcopy(lines)
    db.close()
    for i in range(len(lines)):
        line = lines[i]
        if line.replace("\n","").startswith("SAMPLE") and smpl_name == line.replace("\n","").split("\t")[-1]:
            del new_lines[i:i+7]
            continue
    db = open(path,"w+")
    if len(new_lines) < 2:
        db.close()
        return
    else:
        for line in new_lines:
            db.write(line)
        db.close()
    return

def refresh_all_plots():
    try:
        root.draw_map()
    except: pass
    try:
        for API in root.ImageAnalyzers: 
            try:
                API.draw_image1(0)
                API.draw_image2(0)
            except: pass
    except:
        pass
    return

def wipe_list():
    """ Self-explanatory. Clears the global variable and
    destroys the Periodic Table Tk.Toplevel window """

    Constants.FIND_ELEMENT_LIST = []
    try: root.find_elements_diag.master.destroy()
    except AttributeError: pass #for auto_wizard method

def openURL(url):
    webbrowser.open(url)

def maximize_window(window,e=""):
    if window.alt == False: return
    else:
        if window.master.state()=="zoomed":
            window.master.state("normal")
        else: 
            window.master.state("zoomed")

def place_topright(window1,window2):
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    w_user, h_user = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    
    # adapted from: https://stackoverflow.com/questions/3352918/
    """ Places window2 next to window1 top-right end """ 
    
    window1.update_idletasks()
    window2.update_idletasks()
    
    width = window1.winfo_width()
    frm_width = window1.winfo_rootx() - window1.winfo_x()
    win_width = width + (2 * frm_width)
    width2 = window2.winfo_width()

    height = window1.winfo_height()
    titlebar_height = window1.winfo_rooty() - window1.winfo_y()
    win_height = height + titlebar_height + frm_width
    height2 = window2.winfo_height()
    
    x = window1.winfo_rootx() + width
    y = window1.winfo_rooty() - titlebar_height

    if x + width2 > w_user or y + height2 > h_user: 
        place_center(window1,window2) 
        return 1 
    if Constants.LOW_RES == None:
        window2.geometry("{}x{}+{}+{}".format(width2, height2, x, y))
        window2.deiconify()
    elif Constants.LOW_RES == "high":
        width = window2.winfo_screenwidth()
        height = window2.winfo_screenheight()
        w_width = window2.winfo_width()
        w_height = window2.winfo_height()
        window2.geometry("{}x{}+{}+{}".format(w_width,w_height,\
                int((width/2)-(w_width/2)),int((height/2)-(w_height/2))))
        window2.deiconify()

def place_center(window1,window2):
    """ Places window2 on center of window1 """

    window1.update_idletasks()
    window2.update_idletasks()
    
    width = window1.winfo_width()
    frm_width = window1.winfo_rootx() - window1.winfo_x()
    win_width = width + (2 * frm_width)
    width2 = window2.winfo_width()

    height = window1.winfo_height()
    titlebar_height = window1.winfo_rooty() - window1.winfo_y()
    win_height = height + titlebar_height + frm_width
    height2 = window2.winfo_height()

    ##############################
    # GETS USER SCREEN DIMENSION #
    ##############################

    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    w_user, h_user = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)   

    ##############################

    x = window1.winfo_rootx() + (int(win_width/2)) - (int(width2/2))
    y = window1.winfo_rooty() - titlebar_height + (int(height/2)) - (int(height2/2))
    
    if y < 0 or y + height2 > h_user: spawn_center(window2)
    elif x > w_user or x + width2 > w_user or x < 0: spawn_center(window2)
    else:
        window2.geometry('{}x{}+{}+{}'.format(width2, height2, x, y))
        window2.deiconify()
        window2.focus_force()
    return

def spawn_center(window):
    """ Spawns the window on center of screen. There are known issues
    with multiple monitors, specially of different dpi """

    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    
    w_width = window.winfo_width()
    w_height = window.winfo_height()

    window.geometry("{}x{}+{}+{}".format(w_width,w_height,\
            int((width/2)-(w_width/2)),int((height/2)-(w_height/2))))
    window.focus_force() 

def convert_bytes(num):
    """ Obtained from https://stackoverflow.com/questions/210408 """

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
        
def restore_bytes(num,unit):
    """ Reverse operation of convert_bytes function """

    units = ['KB', 'MB', 'GB', 'TB']
    for x in units:
        if unit == x:
            return num * (1024**(units.index(x)+1))

def call_help():
    """ Spawns help dialogue """
    proceed = messagebox.askquestion("Attention!","You are about to be redirected to github webpage.\nDo you want to proceed?")
    if proceed == "yes":
        webbrowser.open("https://github.com/linssab/XISMuS/blob/master/HELP.md")
        return 0
    else:
        return 0

def call_compilecube():
    """ Tries to create output folder (name is Constants.CONFIG['directory']) 
    and calls SpecMath to compile the data. Spectra to compile are looked under the directory
    set by the user (default is C:/samples/) and inside a directory named 
    Constants.CONFIG['directory'].
    
    If a certain file cannot be read, an error is raised. SpecMath returns the name 
    of the file. """

    try: 
        os.mkdir(SpecRead.output_path)
    except IOError as exception:
        logger.warning("Error {}.".format(exception.__class__.__name__))
        logger.warning("Can't create output folder {}".format(SpecRead.output_path))
    
    if os.path.exists(SpecRead.cube_path): 
        pass
    else:
        root.ButtonLoad.config(state=DISABLED)
        root.MenuBar.entryconfig("Toolbox", state=DISABLED)

        #######################################
        # Tries to destroy the samples window #
        #######################################

        try: root.SamplesWindow.destroy()
        except: pass

        #######################################

        root.StatusBox.delete(0,END)
        root.StatusBox.insert(END, "\nStarting cube compilation.\n")
        root.StatusBox.insert(END, "\nImage size: {} x {}.\n".format(
            root.config_xy[0], root.config_xy[1]))
        root.StatusBox.insert(END, "\nSpectra count: {}.\n".format(
            root.mcacount[Constants.CONFIG["directory"]]))
        logger.warning("Starting cube {} compilation!".format(Constants.CONFIG["directory"]))
        
        ##########################################################################
        # IF LOADING AN H5 FILE, USER CAN COMPILE A DATACUBE OR USE THE H5 AS IS #
        ##########################################################################
        if root.mca_extension[Constants.CONFIG["directory"]] == ".h5":
            m = messagebox.askquestion("Attention!",
                    "You can proceed without compiling the H5 file into a datacube, however, it won't be saved to the database nor will be recognized by Mosaic. It is recommended that you COMPILE it into a datacube. To save disk space, you can compress the H5 file later. DO YOU WANT TO CREATE A DATACUBE FILE?")
            if m == "yes":
                specbatch = Cube(["h5"],Constants.CONFIG)
                fail = specbatch.compile_cube()
                root.ButtonLoad.config(state=NORMAL)
                root.MenuBar.entryconfig("Toolbox", state=NORMAL)
                root.temporaryh5 = "None"
            elif m == "no":
                Constants.MY_DATACUBE = converth5() 
                root.samples[Constants.CONFIG["directory"]] = "temp .h5"
                SpecRead.cube_path = ""
                root.ButtonLoad.config(state=NORMAL)
                root.MenuBar.entryconfig("Toolbox", state=NORMAL)
                root.temporaryh5 = Constants.CONFIG["directory"]

        ##########################################################################
        
        else:

            ############################################################
            # Fills the file pool in case spectra were loaded manually #
            ############################################################

            Constants.FILE_POOL = root.samples[Constants.CONFIG["directory"]]

            ############################################################

            specbatch = Cube(["mca"],Constants.CONFIG)
            fail = specbatch.compile_cube()
            root.ButtonLoad.config(state=NORMAL)
            root.MenuBar.entryconfig("Toolbox", state=NORMAL)

            ####################################################
            # changes the prefix if sample was loaded manually #
            ####################################################

            if isinstance(Constants.FILE_POOL,tuple):
                root.samples[Constants.CONFIG["directory"]] = \
                root.samples[Constants.CONFIG["directory"]][0].split("/")[-1].split(".")[0]
            
            ####################################################
            
            if fail[0] == True:
                messagebox.showerror("Error!",
                        "Could not read {} file! Aborting compilation".format(fail[1]))
                shutil.rmtree(SpecRead.output_path) 

def prompt_folder():
    """ Opens dialogue to change the samples folder """

    folder = filedialog.askdirectory(title="Select the samples folder")
    if folder != "":
        ini_file = open(os.path.join(SpecRead.__BIN__,"folder.ini"),"w")
        ini_file.write(os.path.abspath(folder))
        ini_file.close()
        Constants.SAMPLES_FOLDER = os.path.abspath(folder)
        root.refresh_samples()
    else:
        pass
    return 0

def load_cube():
    """ Loads cube to memory (unpickle). Cube name is passed according to
    latest SpecRead parameters. See setup conditions inside SpecRead module.
    Returns the datacube object """


    logger.debug("Trying to load cube file.")
    logger.debug(SpecRead.cube_path)
    if os.path.exists(SpecRead.cube_path):
        root_busy.busy()
        cube_file = open(SpecRead.cube_path,'rb')
        del Constants.MY_DATACUBE
        Constants.MY_DATACUBE = pickle.load(cube_file)
        cube_file.close()
        logger.debug("Loaded cube {} to memory.".format(cube_file))
        Constants.MY_DATACUBE.densitymap = Constants.MY_DATACUBE.densitymap.astype("float32") 
        root_busy.notbusy()
    elif os.path.exists(os.path.join(SpecRead.output_path,
        "{}.lz".format(Constants.DIRECTORY))):
        lz_file = open(SpecRead.cube_path,'rb')
        data = lz_file.read()
        del Constants.MY_DATACUBE
        Constants.MY_DATACUBE = data
        lz_file.close()
    else:
        logger.debug("No cube found.")
        MainGUI.toggle_(root,toggle='Off') 
        pass
    return Constants.MY_DATACUBE

def refresh_plots(exclusive=""):
    """refresh one plot window exclusively or all open windows"""

    if len(Constants.FIND_ELEMENT_LIST) > 0: 
        lines = True
    else: 
        lines = False
    
    if exclusive == "mps":
        try:
            root.MPS.draw_spec(
                mode=['mps'],display_mode=root.plot_display,lines=lines)
            root.MPS.update_idletasks()
        except: pass
    elif exclusive == "summation":
        try: 
            root.summation.draw_spec(
                mode=['summation'],display_mode=root.plot_display,lines=lines)
            root.summation.update_idletasks()
        except: pass
    elif exclusive == "combined":
        try: 
            root.combined.draw_spec(
                mode=['summation','mps'],display_mode=root.plot_display,lines=lines)
            root.combined.update_idletasks()
        except: pass
    elif exclusive == "roi_sum":
        for API in root.ImageAnalyzers: 
            try:
                API.plot.draw_selective_sum(API.DATACUBE,
                        API.sum_spectrum,
                        display_mode = root.plot_display,
                        lines = lines,
                        refresh=True)
                API.plot.master.update_idletasks()
            except: pass
    else:
        try:
            root.MPS.draw_spec(
                mode=['mps'],display_mode=root.plot_display,lines=lines)
            root.MPS.update_idletasks()
        except: pass
        try: 
            root.summation.draw_spec(
                mode=['summation'],display_mode=root.plot_display,lines=lines)
            root.summation.update_idletasks()
        except: pass
        try: 
            root.combined.draw_spec(
                mode=['summation','mps'],display_mode=root.plot_display,lines=lines)
            root.combined.update_idletasks()
        except: pass
        for API in root.ImageAnalyzers:
            try :
                API.plot.draw_selective_sum(API.DATACUBE,
                        API.sum_spectrum,
                        display_mode = root.plot_display,
                        lines = lines,
                        refresh=True)
                API.plot.master.update_idletasks()
            except: pass

    try: root.find_elements_diag.master.focus_force()
    except: pass

def check_screen_resolution(resolution_tuple):
    Constants.LOW_RES = None
    pop = Tk()
    pop.withdraw()
    limit_w, limit_h = resolution_tuple[0], resolution_tuple[1]
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    if w > limit_w or h > limit_h:
        messagebox.showinfo("Info","Your current screen resolution is {}x{}. This program was optmized to work in 1080p resolution. If the windows are too small or if any problems are experienced with buttons and icons, please try lowering your screen resolution and setting the Windows scaling option to 100%.".format(w,h))
    elif w < limit_w and h < limit_h:
        Constants.LOW_RES = "moderate"
        if 800 < w <= 1024 or 600 < h <= 768: Constants.LOW_RES = "high"
        elif w <= 640 or h <= 480: Constants.LOW_RES = "extreme"
        messagebox.showinfo("Info","Your current screen resolution is {}x{}. This program was optmized to work in 1080p resolution. If the windows are too large, off-scale or if any problems are experienced with buttons and icons, please try increasing your screen resolution. Shall problems persist, verify your Windows scaling option.".format(w,h))
    pop.destroy()

def _init_numpy_mkl():
    import os
    import ctypes
    if os.name != 'nt':
        return
    # disable Intel Fortran default console event handler
    env = 'FOR_DISABLE_CONSOLE_CTRL_HANDLER'
    if env not in os.environ:
        os.environ[env] = '1'
    try:
        _core = ".\\MKLs"
        for _dll in ('mkl_rt', 'libiomp5md', 'mkl_core', 'mkl_intel_thread', 
                     'libmmd', 'libifcoremd', 'libimalloc'):
            ctypes.cdll.LoadLibrary(os.path.join(_core,_dll))
            print("Loaded {}".format(_dll))
    except Exception:
        pass


class About:
    """ Spawns author information """
    def __init__(__self__,root):
        __self__.master = Toplevel(master=root.master)
        __self__.master.title("About")
        __self__.master.resizable(False,False)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.master.destroy)
        icon = os.path.join(os.getcwd(),"images","icons","icon.ico")
        __self__.master.iconbitmap(icon)  
        infotext="Software version: {0}\nContact: sergio.lins@roma3.infn.it".format(Constants.VERSION)
        __self__.winFrame = Frame(__self__.master)
        __self__.winFrame.pack(padx=(16,16),pady=(16,16))
        __self__.Info = Label(__self__.winFrame,text=infotext, wraplength=640, anchor=W, justify=LEFT)
        __self__.Info.pack()
        __self__.Link = Label(__self__.winFrame, text="Contact via ResearchGate", fg="blue", cursor="hand2")
        __self__.Link.bind("<Button-1>", __self__.go_to_RS)
        __self__.Link.pack(side=LEFT)
        place_center(root.master,__self__.master)

    def go_to_RS(__self__,e=""):
        openURL("https://www.researchgate.net/profile/Sergio_Augusto_Lins")
        __self__.master.destroy()


class CanvasSizeDialog:
    def __init__(__self__):
        __self__.win = Toplevel(root.master)
        __self__.win.bind("<Escape>",__self__.kill)
        __self__.win.withdraw()
        __self__.win.resizable(False,False)
        __self__.win.overrideredirect(True)
        __self__.win.grab_set()
        __self__.diag = Frame(__self__.win,relief=RIDGE,bd=3)
        __self__.diag.grid()
        label0 = Label(__self__.diag,text="Canvas Size")
        label0.grid(row=0,column=0,columnspan=2)
        label1 = Label(__self__.diag,text="Height (px): ")
        label1.grid(row=1,column=0)
        label2 = Label(__self__.diag,text="Width (px): ")
        label2.grid(row=2,column=0)
        __self__.x = IntVar()
        __self__.y = IntVar()
        __self__.x.set(100)
        __self__.y.set(100)
        __self__.win.bind("<Return>",__self__.spawn_mosaic)
        
        x_ = Entry(__self__.diag,textvariable=__self__.x,validate="focusout",
                width=9)
        x_.grid(row=1,column=1)
        y_ = Entry(__self__.diag,textvariable=__self__.y,validate="focusout",
                width=9)
        y_.grid(row=2,column=1)
        
        accept = Button(__self__.diag,text="Ok", width=10, 
                command=__self__.spawn_mosaic)
        cancel = Button(__self__.diag,text="Cancel", width=10, 
                command=__self__.kill)
        accept.grid(row=3,column=0,pady=5,sticky=W+E,padx=3)
        cancel.grid(row=3,column=1,pady=5,sticky=W+E,padx=3)
        
        __self__.win.update()
        place_center(root.master,__self__.win)
        __self__.win.deiconify()
        x_.focus_set()

    def kill(__self__,e=""):
        __self__.win.grab_release()
        __self__.win.destroy()
        root.master.focus_set()
        del __self__

    def spawn_mosaic(__self__,e=""):
        if __self__.x.get() == 0 or __self__.y.get()==0:
            messagebox.showerror("Ivalid dimension!",
                    "Can't create {}x{} canvas!".format(__self__.x.get(),__self__.y.get()))
            return
        try:
            size = (__self__.x.get(),__self__.y.get())
            __self__.kill()
            Mosaic_API(size, root)
        except: 
            messagebox.showerror("Ivalid dimension!",
                    "Can't create {}x{} canvas!".format(__self__.x.get(),__self__.y.get()))
            return


class Convert_File_Name:
    def __init__(__self__,parent):
        __self__.master = Toplevel(master=parent)
        __self__.master.withdraw()
        __self__.master.title("Spectrum name converter")
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.master.bind("<Escape>",__self__.kill)
        __self__.master.bind("<Return>",__self__.grab_file_list)
        icon = os.path.join(os.getcwd(),"images","icons","icon.ico")
        __self__.master.iconbitmap(icon)
        __self__.master.resizable(False,False)
        __self__.files = []
        
        __self__.prefix = StringVar()
        __self__.starting_index = IntVar()
        __self__.width = IntVar()
        __self__.height = IntVar()

        __self__.prefix.set("Spectrum")
        __self__.starting_index.set(1)

        __self__.LeftPane = LabelFrame(__self__.master,height=250,width=128,text="Input")
        __self__.LeftPane.grid(row=0,column=0,sticky=N+W+S+E,padx=(3,2),pady=2)
        __self__.RightPane = LabelFrame(__self__.master, height=250,text="Output",padx=15)
        __self__.RightPane.grid(row=0, column=1,sticky=N+S,padx=(2,3),pady=2)

        __self__.build_widgets()
        place_center(root.master,__self__.master)
        __self__.master.grab_set()

    def build_widgets(__self__):
        
        """ Left Pane """
        icon = PhotoImage(data=ICO_LOAD)
        __self__.LoadIco = icon.subsample(1,1)
        __self__.LoadBtn = Button(__self__.LeftPane, 
                text="Load",
                image=__self__.LoadIco,
                command=__self__.grab_file_list,
                compound=TOP,
                width=64, height=64, bd=2)
        
        """ Right Pane Labels """
        __self__.PrefixLabel = Label(__self__.RightPane, text="Prefix")
        __self__.StartLabel = Label(__self__.RightPane, text="Starting No.")
        __self__.WidthLabel = Label(__self__.RightPane, text="Width (optional)")
        __self__.HeightLabel = Label(__self__.RightPane, text="Height (optional)")

        """ Right Pane Entries """
        __self__.PrefixEntry = Entry(__self__.RightPane, 
                textvariable=__self__.prefix,
                width=10)
        __self__.StartEntry = Entry(__self__.RightPane,
                textvariable=__self__.starting_index,
                width=10)
        __self__.WidthEntry = Entry(__self__.RightPane,
                textvariable=__self__.width,
                width=10)
        __self__.HeightEntry = Entry(__self__.RightPane,
                textvariable=__self__.height,
                width=10)
        
        """ Right Pane Buttons """
        icon = PhotoImage(data=ICO_ACCEPT)
        __self__.OkIcon = icon.subsample(1,1)
        __self__.OkBtn = Button(__self__.RightPane, 
                image=__self__.OkIcon, 
                text= " Convert",
                anchor=CENTER,
                compound=LEFT,
                command=__self__.start_conversion,
                width=80,
                height=24, bd=1)
        icon = PhotoImage(data=ICO_REJECT)
        __self__.QuitIcon = icon.subsample(1,1)
        __self__.QuitBtn = Button(__self__.RightPane, 
                text=" Cancel",
                anchor=CENTER,
                compound=LEFT,
                image=__self__.QuitIcon,
                command=__self__.kill,
                width=80,
                height=24, bd=1)
        
        __self__.LoadBtn.grid(row=1,column=0,rowspan=5,padx=24,pady=24)
        __self__.PrefixLabel.grid(row=1,column=1)
        __self__.StartLabel.grid(row=2,column=1)
        __self__.HeightLabel.grid(row=3,column=1)
        __self__.WidthLabel.grid(row=4,column=1)
        __self__.PrefixEntry.grid(row=1,column=2)
        __self__.StartEntry.grid(row=2,column=2)
        __self__.HeightEntry.grid(row=3,column=2)
        __self__.WidthEntry.grid(row=4,column=2)
        __self__.OkBtn.grid(row=5,column=1,pady=8,padx=(3,0),sticky=W+E)
        __self__.QuitBtn.grid(row=5,column=2,pady=8,padx=(3,3),sticky=W+E)
        
        __self__.master.columnconfigure(0, weight=1,minsize=128)
        __self__.master.columnconfigure(1, weight=0)
        __self__.master.columnconfigure(2, weight=0,pad=15)
        for i in range(5):
            __self__.master.rowconfigure(i, weight=1)
        __self__.master.rowconfigure(5, weight=0)
        __self__.master.deiconify()

    def grab_file_list(__self__,e=""):
        __self__.files = []
        __self__.files = filedialog.askopenfilenames(
                parent=__self__.master, title="Select spectra",
                filetypes=(("MCA Files", "*.mca"),("Text Files", "*.txt"),("All files", "*.*")))
        if __self__.files == "": return

    def start_conversion(__self__):
        
        if __self__.files == "" or __self__.files == []: 
            messagebox.showinfo("No files selected!",
                    "Please first select the spectra you wish to rename.")
            return
        out_path = filedialog.askdirectory(parent=__self__.master,
                title="Select output folder")
        if out_path == "": return
        else: 
            __self__.bar = Busy(len(__self__.files),0)
            __self__.bar.update_text("Copying files...")
            new_folder = __self__.files[0].split("/")[-2]+"-conv"
            try: os.mkdir(os.path.join(out_path,new_folder))
            except FileExistsError:
                messagebox.showerror("Folder exists!",
                        "Can't create folder {}, it already exists.".format(
                            os.path.join(out_path,new_folder)))
                __self__.bar.destroybar()
                __self__.master.deiconify()
                __self__.master.focus_set()
                return
            
            if __self__.width.get() > 0 and __self__.height.get() > 0: 
                dm_file = open(os.path.join(out_path,new_folder,"colonneXrighe.txt"),"w")
                dm_file.write("righe\t{}\n".format(__self__.height.get()))
                dm_file.write("colonne\t{}\n".format(__self__.width.get()))
                dm_file.close()
            elif __self__.width.get() < 0 or __self__.height.get() < 0:
                messagebox.showerror("Invalid values!",
                        "The dimensions can't be negative or zero!")
                __self__.bar.destroybar()
                __self__.files = []
                return
            index = __self__.starting_index.get()
            extension = __self__.files[0].split(".")[-1]
            for spectrum in __self__.files:
                new_name = __self__.prefix.get()+str(index)+"."+extension
                shutil.copy(os.path.join(spectrum), 
                        os.path.join(out_path,new_folder,new_name))
                index += 1
                __self__.bar.updatebar(index)
            __self__.bar.destroybar()
            messagebox.showinfo("File name conversion","Conversion finished!")
            __self__.kill()

    def kill(__self__,e=""):
        __self__.files = []
        __self__.master.grab_release()
        root.master.focus_set()
        __self__.master.destroy()


class Welcome:
    """ Welcome window class. Spawns a window with given texts at the center
    of MainGUI window """

    def __init__(__self__,parent):

        """parent is a Tk window"""

        __self__.h, __self__.w = 400, 240
        __self__.master = Toplevel(master=parent)
        icon = os.path.join(os.getcwd(),"images","icons","icon.ico")
        __self__.master.iconbitmap(icon)  
        __self__.master.bind("<Return>",__self__.checkout)
        __self__.master.bind("<Escape>",__self__.checkout)
        __self__.font = tkFont.Font(family="Arial", size=8)

        __self__.master.resizable(False,False)
        __self__.master.title("Welcome!")
        __self__.page = StringVar()
        __self__.tag = BooleanVar()
        __self__.infotext = StringVar()
        __self__.messages = ["Welcome to XISMuS {}\n\nClick the left or right arrows to navigate through this menu.".format(Constants.VERSION),\
                "Getting started:\nClick \"Load Sample\" to open the \"Sample List\" window.\nBy default, XISMuS looks for mca files under C:\\Users\\user\\Documents\\XISMuS\\ folder. To change it, click on \"Toolbox\" and select \"Change samples folder\"\nSelect the folder that contains the folder with your data.\nXISMuS also manages your samples, so if any sample is already compiled, it will appear in the list.","Compiling a sample:\nTo compile your data, double click on the sample name inside the \"Samples List\" window in the right corner. You will be prompted to configure your sample parameters.\nTo save the \"sample counts map\", right-click the sample name in the \"Samples List\" window and select \"Save density map\"."]
        change = __self__.read_log() 
        if change:
            for i in range(len(change)):
                __self__.messages.insert(0,change[len(change)-1-i])
        __self__.current_page = 1
        __self__.page.set("Page {}/{}".format(__self__.current_page,len(__self__.messages)))
        __self__.tag.set(False)
        __self__.infotext.set(__self__.messages[0])
        __self__.build_widgets()

    def build_widgets(__self__):
        __self__.page_counter = Label(
                __self__.master, 
                textvariable=__self__.page, 
                relief=RIDGE)
        __self__.page_counter.grid(row=0, column=0, sticky=W+E, columnspan=2, pady=3)
        __self__.text_frame = Frame(
                __self__.master,
                width=320, height=150)
        __self__.text_frame.grid(row=1, column=0, sticky=W+E, columnspan=2)
        __self__.info = Label(__self__.text_frame,
                textvariable=__self__.infotext,
                anchor=CENTER,
                justify=CENTER,
                wraplength=400,
                width=70,
                height=7,
                padx=5,
                bg=Constants.DEFAULTBTN_COLOR, 
                cursor="arrow",
                relief=FLAT)
        __self__.info["font"] = __self__.font
        __self__.info.grid(row=0, column=1, sticky=W+E)
        icon_fw = PhotoImage(data=ICO_NEXT)
        __self__.icon_fw = icon_fw.subsample(1,1)
        icon_bw= PhotoImage(data=ICO_PREVIOUS)
        __self__.icon_bw = icon_bw.subsample(1,1)
        __self__.fw = Button(
                __self__.text_frame, 
                image=__self__.icon_fw, 
                command=__self__.next_page, 
                width=32,height=32)
        __self__.fw.grid(row=0, column=2,padx=6)
        __self__.bw = Button(
                __self__.text_frame, 
                image=__self__.icon_bw, 
                command=__self__.previous_page, 
                width=32, height=32)
        __self__.bw.grid(row=0, column=0,padx=6)

        __self__.button_frame = Frame(__self__.master)
        __self__.button_frame.grid(row=3,column=0,columnspan=2)
        
        __self__.tag_button = Checkbutton(__self__.master, variable=__self__.tag) 
        __self__.tag_button.grid(row=2, column=0, padx=10)
        
        __self__.tag_label = Label(__self__.master, text="Don't show me again on startup.")
        __self__.tag_label.grid(row=2, column=1, sticky=W)

        __self__.accept = Button(
                __self__.button_frame, 
                text="Ok", width=13, 
                command=__self__.checkout)
        __self__.accept.grid(pady=10)
        
        for i in range(5):
            __self__.master.columnconfigure(i, weight=0)
            __self__.master.rowconfigure(i, weight=0)
        __self__.master.columnconfigure(1, weight=1)

    def read_log(__self__):
        changelog = os.path.join(os.getcwd(),"changelog.log")
        try: f = open(changelog, "r")
        except:
            return 
        lines = f.readlines()
        tot = int(len(lines)/6)
        message,counter,page = [""],0,1
        for i in range(len(lines)):
            line = lines[i]
            counter += 1
            if counter >= 6:
                counter = 0
                message[page-1] += "Log {} of {}".format(page,tot+1)
                message.append("")
                page += 1
            message[page-1] += line
            if i == len(lines)-1: message[page-1] += "\nLog {} of {}".format(page,tot+1)
        f.close()
        return message
        
    def next_page(__self__):
        if __self__.current_page+1 <= len(__self__.messages):
            __self__.current_page +=1
            text = __self__.current_page-1
            __self__.infotext.set(__self__.messages[text])
            __self__.page.set("Page {}/{}".format(
                __self__.current_page,len(__self__.messages)))
            __self__.info.update()
        elif __self__.current_page+1 > len(__self__.messages):
            __self__.current_page = 1
            text = 0
            __self__.infotext.set(__self__.messages[text])
            __self__.page.set("Page {}/{}".format(
                __self__.current_page,len(__self__.messages)))
            __self__.info.update()
        else: pass
        
    def previous_page(__self__):
        if __self__.current_page-1 >= 1:
            __self__.current_page -=1
            text = __self__.current_page-1
            __self__.infotext.set(__self__.messages[text])
            __self__.page.set("Page {}/{}".format(
                __self__.current_page,len(__self__.messages)))
            __self__.info.update()
        elif __self__.current_page-1 < 1:
            __self__.current_page = len(__self__.messages)
            text = len(__self__.messages)
            __self__.infotext.set(__self__.messages[text-1])
            __self__.page.set("Page {}/{}".format(
                __self__.current_page,len(__self__.messages)))
            __self__.info.update()
        else: pass
        
    def checkout(__self__,e=""):

        """ Writes the welcome setting (spawn or not at startup) to settings.tag file """

        checker = True
        if __self__.tag.get() == True:
            Constants.WELCOME = False
            checker = False
        inipath = os.path.join(SpecRead.__BIN__,"settings.tag")
        ini = open(inipath,'w+')
        ini.write("{}\n".format(Constants.SAMPLES_FOLDER))
        ini.write("<ColorMap>\t{}\n".format(Constants.COLORMAP))
        ini.write("<MultiCore>\t{}\n".format(Constants.MULTICORE))
        ini.write("<PlotMode>\t{}\n".format(Constants.PLOTMODE))
        ini.write("<RAMLimit>\t{}\n".format(Constants.RAM_LIMIT))
        ini.write("<welcome>\t{}\n".format(checker))
        ini.write("<Tolerance>\t{}\n".format(Constants.SETROI_TOLERANCE))
        ini.write("<Cycles>\t{}\n".format(Constants.FIT_CYCLES))
        ini.write("<Sensitivity>\t{}\n".format(Constants.PEAK_TOLERANCE))
        ini.write("<Suppression>\t{}\n".format(Constants.CONTINUUM_SUPPRESSION))
        ini.write("<WizTolerance>\t{}\n".format(Constants.CHECK_TOLERANCE))
        ini.write("<SaveInterval>\t{}\n".format(Constants.SAVE_INTERVAL))
        ini.write("<SavePlot>\t{}".format(Constants.SAVE_FIT_FIGURES))
        ini.close()
        root.master.focus_set()
        root.master.focus_force()
        __self__.master.destroy()


class ExportDiag():
    """ Creates a dialog to export ImageAnalyzer API images.
    Target is the desired output image size. If enhance configuration is True,
    image is interpolated """

    def __init__(__self__,parent):
        __self__.master = Toplevel(parent.master)
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

        __self__.Button1 = Button(
                __self__.Frame, 
                image=__self__.icon1, 
                bd=3, 
                command=lambda:__self__.export(tag=1), 
                width=size_x, height=size_y)
        __self__.Button2 = Button(
                __self__.Frame, 
                image=__self__.icon2, 
                bd=3, 
                command=lambda:__self__.export(tag=2), 
                width=size_x, height=size_y)
        __self__.Button3 = Button(
                __self__.Frame, 
                image=__self__.icon3, 
                bd=3, 
                command=__self__.merge, 
                width=size_x, height=size_y)

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
        __self__.master.grab_release()
        __self__.master.destroy()
        __self__.parent.master.focus_set()
        __self__.parent.master.focus_force()


class DimensionDiag():
    """ Creates a pop-up dialog to prompt the datacube dimension
    if no colonneXrighe.txt file is found for the data selected.
    It writes a custom colonneXrighe.txt file to the sample output
    folder, which is deleted if the sample is RESET """

    def __init__(__self__,folder):
        __self__.win = Toplevel(root.master)
        __self__.win.withdraw()
        __self__.win.resizable(False,False)
        __self__.win.overrideredirect(True)
        __self__.win.bind("<Escape>",__self__.kill)
        __self__.exit_code = None
        __self__.win.grab_set()
        __self__.folder = folder
        diag = Frame(__self__.win,relief=RIDGE,bd=3)
        diag.grid()
        label0 = Label(diag,text="Image size")
        label0.grid(row=0,column=0,columnspan=2)
        label1 = Label(diag,text="Height: ")
        label1.grid(row=1,column=0)
        label2 = Label(diag,text="Width: ")
        label2.grid(row=2,column=0)
        __self__.x = StringVar()
        __self__.x.trace("w",__self__.callback_x)
        __self__.y = StringVar()
        __self__.y.trace("w",__self__.callback_y)
        
        __self__.x_ = Entry(diag,textvariable=__self__.x,validate="focusout")
        __self__.x_.grid(row=1,column=1)
        __self__.y_ = Entry(diag,textvariable=__self__.y,validate="focusout")
        __self__.y_.grid(row=2,column=1)
        
        __self__.win.bind("<Return>",__self__.send)
        
        accept = Button(diag,text="Ok", width=13, command=__self__.send)
        accept.grid(row=3,column=0,columnspan=2,pady=5)
        
        __self__.win.update()
        place_center(root.master,__self__.win)
        __self__.win.deiconify()
        __self__.x_.focus_set()

    def check_values(__self__,x,y):
        x,y = x.get(),y.get()
        if x == "" or y == "": 
            messagebox.showerror("Error!","No input! Please add a value.")
            return
        if x.isdigit(): 
            x=int(x)
            if x > root.mcacount[__self__.folder]: x = root.mcacount[__self__.folder]
            elif x == 0: x = 1
        else: 
            messagebox.showerror("Error!","{} not a number!".format(x))
            return
        if y.isdigit(): 
            y=int(y)
            if y > root.mcacount[__self__.folder]: y = root.mcacount[__self__.folder]
            elif y == 0: y = 1
        else:
            messagebox.showerror("Error!","{} not a number!".format(y))
            return
        while x*y > root.mcacount[__self__.folder]:
            if x > y: x-=1
            elif y > x: y-=1
        return x,y
    
    def send(__self__,event=""):
        root.config_xy = __self__.check_values(__self__.x,__self__.y)
        if root.config_xy == None: return
        __self__.win.grab_release()
        __self__.win.destroy()
        __self__.exit_code = "save"
        return __self__.x.get(),__self__.y.get()

    def callback_x(__self__,name="",index="",mode=""):
        try: 
            value = int(root.mcacount[__self__.folder]/int(__self__.x.get()))
            __self__.y.set(value)
        except: 
            pass
    
    def callback_y(__self__,name="",index="",mode=""):
        try: 
            value = int(root.mcacount[__self__.folder]/int(__self__.y.get()))
            __self__.x.set(value)
        except:
            pass
    
    def kill(__self__,e):
        __self__.exit_code = "cancel"
        #root.samples.pop(Constants.CONFIG["directory"])
        __self__.win.destroy()


class PeakClipper:
    """Creates a dialog to set-up SNIPBG parameters"""
    
    def __init__(__self__,parent,mode=None):
        __self__.master = Toplevel(parent.master)
        __self__.mode = mode
        __self__.master.tagged = True
        __self__.parent = parent
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
        #__self__.frame3.grid(row=2,column=1,padx=15,sticky=W+E)
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
            background = peakstrip(__self__.spectrum,cycles,window,savgol,order)
        elif __self__.mode == "Polynomial":
            nglobal = __self__.nglobal.get()
            r_factor = __self__.r_factor.get()
            background = peakstrip(__self__.spectrum,cycles,window,savgol,order)
        return background

    def refresh_plot(__self__):
        __self__.plot.clear()
        folder = Constants.CONFIG.get('directory')

        """ Gives the spectrum name for label according to need. Is user loaded a list
        of files, name must be taken straight from the list. Else, the file builder
        concatenates prefix, index and prefix to form the name """
        
        if isinstance(root.samples[folder],tuple): 
            label = root.samples[folder][__self__.sample].split("/")[-1]
        else:
            label = root.samples[folder]+"{0}.{1}".format(
                        __self__.sample,root.mca_extension[folder])

        if Constants.PLOTMODE == "Linear":
            __self__.plot.set_ylabel("Counts")
            __self__.plot.set_xlabel("Channels")
            __self__.plot.plot(__self__.spectrum,
                    color="blue",
                    label=label)
            try: 
                background = __self__.stripbg()
                __self__.plot.plot(background, label="Background",color="yellow")
            except: pass
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
            except: pass
            __self__.plot.set_ylim(bottom=10e-2)
            __self__.plot.set_ylim(top=1.10*__self__.spectrum.max())

        __self__.plot.legend()
        __self__.canvas.draw()

    def random_sample(__self__):
        folder = Constants.CONFIG.get("directory")
        spec_no = root.mcacount[folder]

        ################################################
        # IF PARENT HAS A MATRIX, IT LOADED AN H5 FILE #
        ################################################
        if __self__.parent.matrix.shape[2] > 1:
            __self__.sample = random.randint(1,spec_no-1)
            __self__.spectrum = __self__.parent.matrix.reshape(-1,__self__.parent.matrix.shape[-1])[__self__.sample]
        ################################################
        
        ####################################################################
        # ELSE, IT IS READING MCA EITHER FROM USER LIST OR DETECTED FOLDER #
        ####################################################################
        else:
            """ When loading a list of files - when the sample is manually loaded by the user,
            not detected automatically - root.samples carries the list of all mca's path """
            if folder == "Training Data 1" or folder == "Training Data 2":
                __self__.sample = random.randint(1,spec_no-1)
                mca = os.path.join(SpecRead.__PERSONAL__,"Example Data",folder,
                        root.samples[folder]+"{0}.{1}".format(__self__.sample,
                            root.mca_extension[folder]))
            elif isinstance(root.samples[folder],tuple):
                __self__.sample = random.randint(1,len(root.samples[folder]))
                mca = root.samples[folder][__self__.sample]
            else:
                __self__.sample = random.randint(1,spec_no-1)
                mca = os.path.join(Constants.SAMPLE_PATH,
                        root.samples[folder]+"{0}.{1}".format(__self__.sample,
                            root.mca_extension[folder]))
                
            __self__.spectrum = SpecRead.getdata(mca)
        ####################################################################

        if isinstance(__self__.spectrum,np.ndarray):
            __self__.refresh_plot() 
        else:
            messagebox.showerror("EOF Error!","Could not read {} file!".\
                    format(__self__.spectrum))

    def save(__self__):
        root.snip_config = __self__.iter.get(),__self__.window.get(),__self__.savgol.get(),__self__.order.get()
        proceed = __self__.verify_values(root.snip_config)
        if proceed == True: __self__.kill()
        else: messagebox.showerror("Value Error", "Parameters not valid. No negative or zero values are valid. Sav-gol window must be odd and greater than Sav-gol order.")

    def kill(__self__, event=""):
        __self__.master.grab_release()
        root.ConfigDiag.master.grab_set()
        __self__.master.destroy()
    
    def verify_values(__self__,snip):
        if snip[0] <= 0 or snip[1] <= 0: return False
        if int(snip[2]%2) == 0: return False
        if snip[3] > snip[2]: return False
        else: return True


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
        __self__.element1 = parent.Map1Var.get()
        __self__.element2 = parent.Map2Var.get()
        __self__.area1.remove()
        __self__.area2.remove()
        __self__.canvas1.draw()
        __self__.canvas2.draw()
        __self__.parent.plot1.add_patch(__self__.area1)
        __self__.parent.plot2.add_patch(__self__.area2)

    def wipe_annotator(__self__):
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
        Constants.FIND_ELEMENT_LIST
        if len(Constants.FIND_ELEMENT_LIST) > 0: 
            lines = True
        else: 
            lines = False
        
        __self__.parent.plot.DATA.set_ydata(__self__.parent.sum_spectrum)
        __self__.parent.plot.plot.legend().get_texts()[0].set_text(
                "{} Spectra".format(__self__.spec_no))
        __self__.parent.plot.plot.set_ylim(
                bottom=1,
                top=1.20*__self__.parent.sum_spectrum.max())
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
            try: __self__.x1 = int(event.xdata)
            except: pass
            try: __self__.y1 = int(event.ydata)
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
                dtype="int32")
        unpacker1 = __self__.element1.split("_")
        unpacker2 = __self__.element2.split("_")
        
        x_ = [__self__.x0,__self__.x1]
        y_ = [__self__.y0,__self__.y1]
        x_.sort()
        y_.sort()
        
        ###############################################################################
        # unpacks raw image, notice no normalization is done to match LEVELS          # 
        # levels of gray. If NO MAPS are available at the cube, the sum image appears #
        ###############################################################################

        if unpacker1 != [""] or unpacker2 != [""]:
            image1 = __self__.parent.DATACUBE.unpack_element(unpacker1[0],unpacker1[1])
            image2 = __self__.parent.DATACUBE.unpack_element(unpacker2[0],unpacker2[1])
         
        ################################################################
        # IF NO MAPS ARE AVAILABLE, ONLY ITERATES TO SHOW THE ROI PLOT #
        ################################################################
        else:
            for x in range(y_[0],y_[1]):
                for y in range(x_[0],x_[1]):
                    __self__.parent.sum_spectrum += __self__.parent.DATACUBE.matrix[x][y]
                    __self__.spec_no += 1
            return
        ################################################################
        
        for x in range(y_[0],y_[1]):
           for y in range(x_[0],x_[1]):
               __self__.area1_sum += image1[x][y]
               __self__.area2_sum += image2[x][y]
               __self__.parent.sum_spectrum += __self__.parent.DATACUBE.matrix[x][y]
               __self__.spec_no += 1
        __self__.roibox1["text"] = "Roi 1: {}".format(int(__self__.area1_sum))
        __self__.roibox2["text"] = "Roi 2: {}".format(int(__self__.area2_sum))
        if __self__.area2_sum > 0:
            __self__.ratebox["text"] = "Ratio: {:.2f}".format(
                    __self__.area1_sum/__self__.area2_sum)


class ImageAnalyzer:
    def __init__(__self__,parent,datacube):
        __self__.DATACUBE = datacube
        __self__.packed_elements = __self__.DATACUBE.check_packed_elements()
        __self__.sum_spectrum = __self__.DATACUBE.sum
        __self__.master = Toplevel(parent)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.master.attributes("-alpha",0.0)
        __self__.master.tagged = False
        __self__.master.title("Image Analyzer")
        __self__.alt = False
        __self__.master.bind("<Alt_L>",__self__.AltOn)
        __self__.master.bind("<KeyRelease-Alt_L>",__self__.AltOff)
        __self__.master.bind("<Return>",__self__.maximize)
        __self__.sampler = Frame(__self__.master)
        __self__.sampler.pack(side=TOP,anchor=CENTER)
        __self__.SampleFrame = Frame(__self__.master)
        __self__.SampleFrame.pack(side=TOP,expand=True,fill=BOTH)
        __self__.LeftCanvas = Canvas(__self__.SampleFrame)
        __self__.LeftCanvas.pack(side=LEFT,expand=True,fill=BOTH)
        __self__.RightCanvas = Canvas(__self__.SampleFrame)
        __self__.RightCanvas.pack(side=RIGHT,expand=True,fill=BOTH)
        __self__.sliders = LabelFrame(__self__.master,text="Control Panel")
        __self__.sliders.pack(side=TOP,fill=X,anchor=CENTER,padx=(5,5),pady=(0,5))
        __self__.buttons = Frame(__self__.sliders)
        __self__.buttons.grid(row=0,column=0,rowspan=4,columnspan=2,padx=(60,30),sticky=W+E)
        __self__.buttons2 = Frame(__self__.sliders)
        __self__.buttons2.grid(row=0,column=9,rowspan=4,padx=(60,30),sticky=E)
        __self__.build_widgets()

    def get_version(__self__):
        """ version attribute was implemented in XISMuS 1.3.0, 
        any cube prior to this version has no version attribute """

        if hasattr(__self__.DATACUBE,"version"):
            __self__.cube_version = "Cube version: "+__self__.DATACUBE.version
            if hasattr(__self__.DATACUBE,"scalable"):
                __self__.scale.config(state=NORMAL)
                __self__.scaleLabel.config(state=NORMAL)
            else:
                __self__.scale.config(state=DISABLED)
                __self__.scaleLabel.config(state=DISABLED)
        else:
            __self__.cube_version = "Cube version: pre-1.3"
            __self__.scale.config(state=DISABLED)
            __self__.scaleLabel.config(state=DISABLED)

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
        __self__.Map1Label.grid(row=0, column=0, columnspan=3, sticky=W)
        __self__.Map1Combo = ttk.Combobox(
                __self__.sampler, 
                textvariable=__self__.Map1Var,
                values=__self__.packed_elements,
                width=5,
                state="readonly")
        __self__.Map1Combo.grid(row=0,column=3, sticky=W,padx=(16,16),pady=(8,4))
        __self__.Map1Combo.bind("<<ComboboxSelected>>", __self__.update_sample1)
        
        # map 2
        __self__.Map2Label = Label(
                __self__.sampler, 
                textvariable=__self__.Map2Counts,
                width=30)
        __self__.Map2Label.grid(row=0, column=5, columnspan=3, sticky=E)
        __self__.Map2Combo = ttk.Combobox(
                __self__.sampler, 
                textvariable=__self__.Map2Var,
                values=__self__.packed_elements,
                width=5,
                state="readonly")
        __self__.Map2Combo.grid(row=0,column=4, sticky=E,padx=(16,16),pady=(8,4))
        __self__.Map2Combo.bind("<<ComboboxSelected>>", __self__.update_sample2)

        # matplotlib canvases
        __self__.figure1 = Figure(figsize=(5,4), dpi=75)
        __self__.plot1 = __self__.figure1.add_subplot(111)
        __self__.plot1.axis('On')
        __self__.plot1.grid(b=None)
        __self__.canvas1 = FigureCanvasTkAgg(__self__.figure1,__self__.LeftCanvas)
        __self__.canvas1.get_tk_widget().pack(fill=BOTH,anchor=N+W,expand=True)
        __self__.canvas1.mpl_connect("button_press_event",
                lambda event: __self__.pop(event,1))
        
        __self__.figure2 = Figure(figsize=(5,4), dpi=75)
        __self__.plot2 = __self__.figure2.add_subplot(111)
        __self__.plot2.axis('On')
        __self__.plot2.grid(b=None)
        __self__.canvas2 = FigureCanvasTkAgg(__self__.figure2,__self__.RightCanvas)
        __self__.canvas2.get_tk_widget().pack(fill=BOTH,anchor=N+W,expand=True)
        __self__.canvas2.mpl_connect("button_press_event",
                lambda event: __self__.pop(event,2))

        # image controls Threshold, LowPass and Smooth
        __self__.T1check = BooleanVar()
        __self__.T1check.set(False)
        __self__.T1 = Checkbutton(
                __self__.sliders, 
                variable=__self__.T1check,
                command=__self__.switchLP1T1).grid(row=0,column=2)

        __self__.LP1check = BooleanVar()
        __self__.LP1check.set(False)
        __self__.LP1 = Checkbutton(__self__.sliders, 
                variable=__self__.LP1check,
                command=__self__.switchT1LP1).grid(row=1,column=2)

        __self__.S1check = BooleanVar()
        __self__.S1check.set(False)
        __self__.S1 = Checkbutton(
                __self__.sliders, 
                variable=__self__.S1check,
                command=lambda:__self__.draw_image1(0)).grid(row=2,column=2)
       
        __self__.T1Label = Label(__self__.sliders, text="Threshold ")
        __self__.T1Label.grid(row=0,column=3)
        __self__.T2Label = Label(__self__.sliders, text="Threshold ")
        __self__.T2Label.grid(row=0,column=7)
        __self__.LP1Label = Label(__self__.sliders, text="Low Pass ")
        __self__.LP1Label.grid(row=1,column=3)
        __self__.LP2Label = Label(__self__.sliders, text="Low Pass ")
        __self__.LP2Label.grid(row=1,column=7)
        __self__.S1Label = Label(__self__.sliders, text="Smooth ")
        __self__.S1Label.grid(row=2,column=3)
        __self__.S2Label = Label(__self__.sliders, text="Smooth ")
        __self__.S2Label.grid(row=2,column=7)

        # sliders for image 1
        __self__.T1Slider = Scale(
                __self__.sliders, 
                orient='horizontal', 
                from_=0, 
                to=LEVELS,
                command=__self__.draw_image1)
        __self__.T1Slider.grid(row=0,column=4)
        __self__.LP1Slider = Scale(
                __self__.sliders, 
                orient='horizontal', 
                from_=0, 
                to=LEVELS,
                command=__self__.draw_image1)
        __self__.LP1Slider.grid(row=1,column=4)
        __self__.S1Slider = Scale(
                __self__.sliders, 
                orient='horizontal', 
                from_=0, 
                to=2,
                command=__self__.draw_image1)
        __self__.S1Slider.grid(row=2,column=4)

        # image controls Threshold, LowPass and Smooth
        __self__.T2check = BooleanVar()
        __self__.T2check.set(False)
        __self__.T2 = Checkbutton(
                __self__.sliders, 
                variable=__self__.T2check,
                command=__self__.switchLP2T2).grid(row=0,column=6)

        __self__.LP2check = BooleanVar()
        __self__.LP2check.set(0)
        __self__.LP2 = Checkbutton(
                __self__.sliders, 
                variable=__self__.LP2check,
                command=__self__.switchT2LP2).grid(row=1,column=6)

        __self__.S2check = BooleanVar()
        __self__.S2check.set(0)
        __self__.S2 = Checkbutton(
                __self__.sliders, 
                variable=__self__.S2check,
                command=lambda:__self__.draw_image2(0)).grid(row=2,column=6)
               
        # sliders for image 2
        __self__.T2Slider = Scale(
                __self__.sliders, 
                orient='horizontal', 
                from_=0, 
                to=LEVELS,
                command=__self__.draw_image2)
        __self__.T2Slider.grid(row=0,column=8)
        __self__.LP2Slider = Scale(
                __self__.sliders, 
                orient='horizontal', 
                from_=0, 
                to=LEVELS,
                command=__self__.draw_image2)
        __self__.LP2Slider.grid(row=1,column=8)
        __self__.S2Slider = Scale(
                __self__.sliders, 
                orient='horizontal', 
                from_=0, 
                to=2,
                command=__self__.draw_image2)
        __self__.S2Slider.grid(row=2,column=8)
    
        # buttons
        __self__.roibox1 = Label(__self__.buttons,text="Roi 1: None") 
        __self__.roibox1.grid(row=0,column=0,columnspan=2)
        __self__.roibox2 = Label(__self__.buttons,text="Roi 2: None") 
        __self__.roibox2.grid(row=1,column=0,columnspan=2)
        __self__.ratebox = Label(__self__.buttons,text="Ratio: None") 
        __self__.ratebox.grid(row=2,column=0,columnspan=2)
        
        __self__.annotate = Button(
                __self__.buttons,
                text="Set ROI",
                command=__self__.toggle_annotator,
                relief="raised",
                width=14)
        __self__.annotate.grid(row=4,column=0,columnspan=2,sticky=W+E)
        __self__.correlate = Button(
                __self__.buttons,
                text="Correlate",
                command=__self__.get_correlation,
                width=round(__self__.annotate.winfo_width()/2))
        __self__.correlate.grid(row=3,column=0,sticky=W+E)
        __self__.export = Button(
                __self__.buttons,
                text="Export",
                command=__self__.export_maps,
                width=round(__self__.annotate.winfo_width()/2))
        __self__.export.grid(row=3,column=1,sticky=W+E)
        __self__.subtract_btn = Button(
                __self__.buttons2,
                text="Add Images",
                command=__self__.add_images,
                width=round(__self__.annotate.winfo_width()/2))
        __self__.subtract_btn.grid(row=0,column=9,sticky=W+E)
        __self__.add_btn = Button(
                __self__.buttons2,
                text="Subtract Images",
                command=__self__.subtract_images,
                width=round(__self__.annotate.winfo_width()/2))
        __self__.add_btn.grid(row=1,column=9,sticky=W+E)

        __self__.scale = Checkbutton(
                __self__.buttons2, 
                variable=__self__.apply_scale_mask,
                command=__self__.refresh)
        __self__.scaleLabel = Label(__self__.buttons2, text="Apply scaling mask")
        __self__.scale.grid(row=3,column=9, sticky=W)
        __self__.scaleLabel.grid(row=3,column=9, sticky=E, padx=(25,0))
        __self__.get_version()
        __self__.CubeVersionLabel = Label(__self__.master,
                text=__self__.cube_version,
                bd=1,
                relief=SUNKEN,
                anchor=W)
        __self__.CubeVersionLabel.pack(side=BOTTOM, expand=False, fill=X, anchor=W)
        
        # Disable sliders
        __self__.T1Slider.config(state=DISABLED)
        __self__.T2Slider.config(state=DISABLED)
        __self__.LP1Slider.config(state=DISABLED)
        __self__.LP2Slider.config(state=DISABLED)
        
        __self__.draw_image1(0)
        __self__.draw_image2(0)
        
        icon = os.path.join(os.getcwd(),"images","icons","img_anal.ico")
        __self__.master.iconbitmap(icon)  
        
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
                __self__.ElementalMap1 = Constants.MY_DATACUBE.densitymap
                __self__.draw_image1(0)
            if __self__.ElementalMap2.max() == 0:
                __self__.ElementalMap2 =  Constants.MY_DATACUBE.densitymap
                __self__.draw_image2(0)
            __self__.update_sample1(None)
            __self__.update_sample2(None)
        except: 
            pass
        x = __self__.master.winfo_width()
        y = __self__.master.winfo_height()

        if __self__.nomaps == True:
            __self__.add_btn.config(state=DISABLED)
            __self__.subtract_btn.config(state=DISABLED)
            __self__.correlate.config(state=DISABLED)
            __self__.export.config(state=DISABLED)
            __self__.scale.config(state=DISABLED)
            __self__.scaleLabel.config(state=DISABLED)
        else:
            __self__.add_btn.config(state=NORMAL)
            __self__.subtract_btn.config(state=NORMAL)
            __self__.annotate.config(state=NORMAL)
            __self__.correlate.config(state=NORMAL)
            __self__.export.config(state=NORMAL)

        __self__.master.minsize(x,y)
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)

    def kill(__self__):
        for widget in __self__.master.winfo_children():
            widget.destroy()
            checkout_config()
            __self__.master.destroy()   
        try: __self__.plot.wipe_plot()
        except: pass
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
            root.master.update_idletasks()
            x = root.master.winfo_pointerx()
            y = root.master.winfo_pointery()
            abs_coord_x = root.master.winfo_pointerx() - root.master.winfo_vrootx()
            abs_coord_y = root.master.winfo_pointery() - root.master.winfo_vrooty()
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
            __self__.plot = PlotWin(__self__.master)
            if Constants.LOW_RES == None:
                place_topright(__self__.master, __self__.plot.master)
            elif Constants.LOW_RES == "moderate":
                spawn_center(__self__.plot.master)
            elif Constants.LOW_RES == "high":
                place_center(__self__.master, __self__.plot.master)
            __self__.plot.draw_selective_sum(__self__.DATACUBE,
                    __self__.DATACUBE.sum,
                    root.plot_display,lines=True)
        else:
            __self__.annotate.config(relief="raised")
            # the easiest way to recover the default 
            #color button is pointing to an existing button that never changes its color
            __self__.annotate.config(bg=__self__.correlate.cget("background"))
            __self__.annotator.wipe_annotator()
            __self__.plot.wipe_plot()
 
    def update_sample1(__self__,event):
        label1 = "Maximum net counts: {}".format(
                int(__self__.DATACUBE.max_counts[__self__.Map1Var.get()]))
        __self__.Map1Counts.set(label1)
        unpacker = __self__.Map1Var.get()
        unpacker = unpacker.split("_")
        __self__.ElementalMap1 = __self__.DATACUBE.unpack_element(unpacker[0],unpacker[1])
        __self__.ElementalMap1 = __self__.ElementalMap1/__self__.ElementalMap1.max()*LEVELS
        __self__.draw_image1(0)
        try: 
            __self__.annotator.wipe_annotator()
            del __self__.plot
        except: pass
     
    def update_sample2(__self__,event):
        label2 = "Maximum net counts: {}".format(
                int(__self__.DATACUBE.max_counts[__self__.Map2Var.get()]))
        __self__.Map2Counts.set(label2)
        unpacker = __self__.Map2Var.get()
        unpacker = unpacker.split("_")
        __self__.ElementalMap2 = __self__.DATACUBE.unpack_element(unpacker[0],unpacker[1])
        __self__.ElementalMap2 = __self__.ElementalMap2/__self__.ElementalMap2.max()*LEVELS
        __self__.draw_image2(0)
        try: 
            __self__.annotator.wipe_annotator()
            del __self__.plot
        except: pass
    
    def switchT1LP1(__self__):
        if __self__.LP1check.get() == True: __self__.LP1Slider.config(state=NORMAL)
        else: __self__.LP1Slider.config(state=DISABLED)
        if __self__.T1check.get() == True: 
            __self__.T1check.set(False)
            __self__.T1Slider.config(state=DISABLED)
        __self__.draw_image1(0)

    def switchLP1T1(__self__):
        if __self__.T1check.get() == True: __self__.T1Slider.config(state=NORMAL)
        else: __self__.T1Slider.config(state=DISABLED)
        if __self__.LP1check.get() == True: 
            __self__.LP1check.set(False)
            __self__.LP1Slider.config(state=DISABLED)
        __self__.draw_image1(0)

    def switchT2LP2(__self__):
        if __self__.LP2check.get() == True: __self__.LP2Slider.config(state=NORMAL)
        else: __self__.LP2Slider.config(state=DISABLED)
        if __self__.T2check.get() == True: 
            __self__.T2check.set(False)
            __self__.T2Slider.config(state=DISABLED)
        __self__.draw_image2(0)
    
    def switchLP2T2(__self__):
        if __self__.T2check.get() == True: __self__.T2Slider.config(state=NORMAL)
        else: __self__.T2Slider.config(state=DISABLED)
        if __self__.LP2check.get() == True: 
            __self__.LP2check.set(False)
            __self__.LP2Slider.config(state=DISABLED)
        __self__.draw_image2(0)

    def transform1(__self__,image):
        if __self__.T1check.get() == True:
            if __self__.S1check.get() == True: 
                image = threshold(image,__self__.T1Slider.get())
                image = iteractive_median(image,__self__.S1Slider.get())
            else:
                image = threshold(image,__self__.T1Slider.get())
        elif __self__.LP1check.get() == True:
            if __self__.S1check.get() == True: 
                image = low_pass(image,__self__.LP1Slider.get())
                image = iteractive_median(image,__self__.S1Slider.get())
            else:
                image = low_pass(image,__self__.LP1Slider.get())
        else:
            if __self__.S1check.get() == True:
                image = iteractive_median(image,__self__.S1Slider.get())
        try:
            __self__.annotate.config(relief="raised")
            __self__.annotate.config(bg=__self__.correlate.cget("background"))
            __self__.annotator.wipe_annotator()
            del __self__.plot
        except: pass
            
        return image
 
    def transform2(__self__,image):
        if __self__.T2check.get() == True:
            if __self__.S2check.get() == True: 
                image = threshold(image,__self__.T2Slider.get())
                image = iteractive_median(image,__self__.S2Slider.get())
            else:
                image = threshold(image,__self__.T2Slider.get())
        elif __self__.LP2check.get() == True:
            if __self__.S2check.get() == True: 
                image = low_pass(image,__self__.LP2Slider.get())
                image = iteractive_median(image,__self__.S2Slider.get())
            else:
                image = low_pass(image,__self__.LP2Slider.get())
        else:
            if __self__.S2check.get() == True:
                image = iteractive_median(image,__self__.S2Slider.get())
        try:
            __self__.annotate.config(relief="raised")
            __self__.annotate.config(bg=__self__.correlate.cget("background"))
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
        __self__.newimage1 = __self__.transform1(__self__.CACHEMAP1)
        del __self__.CACHEMAP1
        __self__.plot1.clear()
        apply_scaling(__self__.DATACUBE,__self__.newimage1, scalemode) 
        __self__.plot1.imshow(__self__.newimage1, cmap=Constants.COLORMAP)
        __self__.plot1.grid(b=None)
        __self__.canvas1.draw()
    
    def draw_image2(__self__,i):
        scalemode = __self__.apply_scale_mask.get()
        if scalemode: scalemode = 1
        else: scalemode = 0
        __self__.CACHEMAP2 = copy.deepcopy(__self__.ElementalMap2)
        __self__.newimage2 = __self__.transform2(__self__.CACHEMAP2)
        del __self__.CACHEMAP2
        __self__.plot2.clear()
        apply_scaling(__self__.DATACUBE,__self__.newimage2, scalemode) 
        __self__.plot2.imshow(__self__.newimage2, cmap=Constants.COLORMAP)
        __self__.plot2.grid(b=None)
        __self__.canvas2.draw()

    def get_correlation(__self__):
        labels = __self__.Map1Var.get(),__self__.Map2Var.get()
        
        """ Transformed and displayed maps are converted to 0-LEVELS scale (usually 255)
        to correlate raw values i.e. the net area contained in each pixel,
        maps must be unpacked from cube again """
        """ This could be avoided by NOT deleting the CACHEMAP variables, but since 
        correlation tool is used much less than the filters (which perform several 
        iterations), the gain in performance is more important in filtering than correlating
        maps """

        #unpacker1 = __self__.Map1Var.get()
        #unpacker1 = unpacker1.split("_")
        #Map1 = copy.deepcopy(__self__.DATACUBE.unpack_element(unpacker1[0],unpacker1[1]))
        #unpacker2 = __self__.Map2Var.get()
        #unpacker2 = unpacker2.split("_")
        #Map2 = copy.deepcopy(__self__.DATACUBE.unpack_element(unpacker2[0],unpacker2[1]))

        Map1 = copy.deepcopy(__self__.newimage1)
        Map2 = copy.deepcopy(__self__.newimage2)

        """ Correlation region must now be limited according to the transformed area
        (any applied filter) and to selected area made with set ROI tool (Annotator class) """
        bar = Busy(1,0)
        bar.update_text("Thinking...")
        
        """
        i = 0 
        for x in range(__self__.newimage1.shape[0]):
            for y in range(__self__.newimage1.shape[1]):
                if __self__.newimage1[x,y] <= 0: Map1[x,y] = 0
                if __self__.newimage2[x,y] <= 0: Map2[x,y] = 0
            bar.updatebar(i)
            i = i+1
        """

        if __self__.annotate.config("relief")[-1] == "sunken":
            x = [__self__.annotator.x0, __self__.annotator.x1]
            y = [__self__.annotator.y0, __self__.annotator.y1]
            x.sort()
            y.sort()
            Map1 = Map1[y[0]:y[1],x[0]:x[1]]
            Map2 = Map2[y[0]:y[1],x[0]:x[1]]
        dim = Map1.shape[0]
        bar.progress["maximum"] = dim

        corr = correlate(Map1,Map2,bar=bar)
        if not corr: 
            messagebox.showerror("Error","Cannot correlate an empty image!")
            bar.destroybar()
            return
        bar.update_text("Loading plot...")
        corr_plot = PlotWin(__self__.master)
        corr_plot.draw_correlation(corr,labels)
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
        #plt.imsave(f.name, img, cmap=Constants.COLORMAP) 
        return 0

    def export_maps(__self__):
        export = ExportDiag(__self__)
        return 0


class PlotWin:
    def __init__(__self__,master):
        __self__.plot_font = {'fontname':'Arial','fontsize':14}
        __self__.lw = 3
        __self__.master = Toplevel(master=master)
        __self__.master.attributes("-alpha",0.0)
        __self__.alt = False
        __self__.master.bind("<Alt_L>",__self__.AltOn)
        __self__.master.bind("<KeyRelease-Alt_L>",__self__.AltOff)
        __self__.master.bind("<Return>",__self__.maximize)

        __self__.master.title("Plot")
        __self__.master.tagged = None
        __self__.master.minsize(width=600,height=480)
        __self__.master.configure(bg='white')
        __self__.master.resizable(True,True) 
        __self__.upper = Canvas(__self__.master)
        __self__.upper.config(bg='white')
        __self__.upper.pack(side=TOP, expand=True, fill=BOTH, padx=(16,16),pady=(16,16))
        __self__.lower = Frame(__self__.master,height=35)
        __self__.lower.pack(side=BOTTOM, anchor=N, fill=BOTH, expand=0)
        
        __self__.figure = Figure(figsize=(5,4), dpi=75)
        __self__.plot = __self__.figure.add_subplot(111)
        __self__.plot.grid(which='both',axis='both')
        __self__.plot.axis('On')
        __self__.canvas = FigureCanvasTkAgg(__self__.figure,__self__.upper)
        __self__.canvas.draw()
        __self__.mplCanvas = __self__.canvas.get_tk_widget()
        __self__.mplCanvas.pack(fill=BOTH, anchor=N+W,expand=True)
        __self__.toolbar = NavigationToolbar(__self__.canvas,__self__.lower)
        __self__.toolbar.update()
        __self__.canvas._tkcanvas.pack()
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.wipe_plot)
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
            __self__.plot.plot(pair[0],pair[1], marker='+',mew=1,ms=10,
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
        energy_list=[]
        __self__.master.tagged = False
        if __self__.master.winfo_exists() == True:
            __self__.plot.clear()
            colors = ["blue","red","green"]
            if display_mode == '-semilog':
                __self__.plot.set_ylabel("Counts")
                i = 0
                for option in mode:
                    __self__.plotdata = getstackplot(Constants.MY_DATACUBE,option)
                    __self__.plotdata = __self__.plotdata/__self__.plotdata.max()
                    __self__.plot.semilogy(Constants.MY_DATACUBE.energyaxis,__self__.plotdata,
                            label=str(option),color=colors[i])
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
                    __self__.plot.plot(Constants.MY_DATACUBE.energyaxis,__self__.plotdata,\
                            label=str(option),color=colors[i])
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
                __self__.plot.legend(
                        fancybox=True,
                        shadow=True,
                        fontsize=12,
                        framealpha=1,
                        borderpad=1,
                        facecolor="white")

            __self__.canvas.draw()
    
    def draw_ROI(__self__):
        __self__.master.tagged = True
        patches = []
        for element in Constants.MY_DATACUBE.ROI:
            __self__.plotdata = Constants.MY_DATACUBE.ROI[element]
            if Constants.MY_DATACUBE.max_counts[element+"_a"] == 0:
                try: net = (Constants.MY_DATACUBE.max_counts[element+"_b"],"Beta")
                except: net = (Constants.MY_DATACUBE.max_counts[element+"_a"],"Alpha")
            else: net = (Constants.MY_DATACUBE.max_counts[element+"_a"],"Alpha")
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

                #elif element=="Au" or element=="Hg":
                #__self__.plot.semilogy(
                #    Constants.MY_DATACUBE.energyaxis,
                #    __self__.plotdata,
                #    label=roi_label,
                #    color=ElementColors[element])
                __self__.plot.fill_between(
                        Constants.MY_DATACUBE.energyaxis,
                        Constants.MY_DATACUBE.sum_bg,
                        __self__.plotdata,
                        color=ElementColors[element],
                        where=__self__.plotdata > Constants.MY_DATACUBE.sum_bg,
                        alpha=0.85,
                        interpolate=True,
                        linewidth=3,
                        zorder=1)
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

        __self__.plot.semilogy(
                Constants.MY_DATACUBE.energyaxis,
                Constants.MY_DATACUBE.sum,
                color="blue",
                label="Sum spectrum",
                linewidth=3)
        patches.append(mpatches.Patch(
                    color="blue",
                    label="Sum spectrum"))
        __self__.plot.semilogy(
                Constants.MY_DATACUBE.energyaxis,
                Constants.MY_DATACUBE.sum_bg,
                color="green",
                label="Continuum",
                linewidth=3)
        patches.append(mpatches.Patch(
                    color="green",
                    label="Continuum"))
        __self__.plot.grid(color="black", ls="--", lw=0.5)
        __self__.plot.set_title("{0} Stacked ROI's sum for all spectra".format(
            Constants.DIRECTORY),**__self__.plot_font)
        __self__.plot.set_ylabel("Counts")
        __self__.plot.set_xlabel("Energy (KeV)")
        __self__.plot.set_ylim([1,Constants.MY_DATACUBE.sum.max()*1.20])
        #__self__.plot.set_xlim([9.20,10.90])
        __self__.plot.legend(
                fancybox=True,
                shadow=True,
                fontsize=12,
                framealpha=1,
                borderpad=1,
                facecolor="white",
                handles=patches)

    def draw_correlation(__self__,corr,labels):
        A, B, R = SpecRead.linregress(corr[0],corr[1]) 
        fit = []
        labelx,macrox = labels[0].split("_")[0],labels[0].split("_")[1]
        linex = which_macro(labelx)
        labelx = labelx+" "+linex+macrox
        labely,macroy = labels[1].split("_")[0],labels[1].split("_")[1]
        liney = which_macro(labely)
        labely = labely+" "+liney+macroy

        __self__.plot.set_title('{0}'.format(Constants.DIRECTORY),**__self__.plot_font)
        __self__.plot.set_xlabel(labelx,fontsize=16)
        __self__.plot.set_ylabel(labely,fontsize=16)
        __self__.plot.scatter(corr[0],corr[1])
        for i in range(int(corr[0].max())):
            value = A*i+B
            if value < corr[1].max(): 
                fit.append(value)
            if B < 0: sig = "-"
            else: sig = "+"
        __self__.plot.plot(fit, color="blue", 
                label="y(x) = {0:0.2f}x {1} {2:0.2f}\nR = {3:0.4f}".format(A,sig,abs(B),R))
        __self__.plot.legend(shadow=True,fontsize=10,facecolor="white",loc="upper right")
        place_topright(__self__.master.master,__self__.master)

    def draw_map(__self__):
        __self__.plot.set_title('{0}'.format(Constants.DIRECTORY),**__self__.plot_font)
        __self__.plot.set_xlabel("Size [pixel]",fontsize=16)
        __self__.plot.set_ylabel("Size [pixel]",fontsize=16)
        fixed_image = write_image(Constants.MY_DATACUBE.densitymap,
                resize=Constants.TARGET_RES,
                path=None,
                enhance=Constants.MY_DATACUBE.config["enhance"],
                save=False)
        __self__.plot.imshow(fixed_image, cmap=Constants.COLORMAP)
        place_topright(__self__.master.master,__self__.master)

    def draw_selective_sum(__self__,
            DATACUBE,
            y_data,
            display_mode=None,
            lines=False,
            refresh=False):
        
        if not refresh:
            
            save_icon = PhotoImage(data=ICO_SAVE)
            __self__.SAVE_ICO = save_icon.subsample(1,1)

            __self__.add_ons = Frame(__self__.master)
            __self__.add_ons.pack(side=RIGHT,fill=X)
            __self__.save_raw_btn = Button(__self__.add_ons,
                    text=" Save ROI spectrum",
                    image=__self__.SAVE_ICO,
                    compound=LEFT,
                    width=160,
                    bd=1,
                    command=lambda: save_raw_spectrum())
            __self__.save_raw_btn.grid(row=0,column=0,sticky="")

        def save_raw_spectrum():
            x,spec = __self__.DATA.get_data()
            f = filedialog.asksaveasfile(mode='w',
                        defaultextension=".mca",
                        filetypes=[("MCA file", "*.mca")],
                        title="Save as...")
            if f is not None:
                sum_file = open(f.name,'w+')
                
                #################
                # writes header #
                #################
                sum_file.write(
                        "<<PMCA SPECTRUM>>\nTAG - TAG\nDESCRIPTION - {} ROI\n".format(
                            DATACUBE.name))
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
            else: return
   
        __self__.plot.clear()
        colors = ["blue","red","green"]
        __self__.plot.set_title('{0}'.format(DATACUBE.name),**__self__.plot_font)
        __self__.plot.set_ylabel("Counts")
        __self__.plot.set_xlabel("Energy (KeV)")

        if display_mode == '-semilog':
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


class Samples:
    def __init__(__self__):
        __self__.samples_database = {}
        __self__.samples_path = {}
        __self__.mcacount = {}
        __self__.mca_indexing = {}
        __self__.mca_extension = {}

    def splash_screen(__self__,parent):
        __self__.splash = Toplevel(parent.master)
        __self__.splash.resizable(False,False)
        __self__.splash.configure(bg="#DCDCDC")
        __self__.splash.geometry("640x400")
        __self__.splash.overrideredirect(True)
        __self__.splash.withdraw()
        __self__.splash.grid_rowconfigure(0,weight=10)
        __self__.splash.grid_rowconfigure(1,weight=1)
        __self__.splash.grid_columnconfigure(0,weight=1)
        __self__.splash.grid_columnconfigure(1,weight=1)
        __self__.splash_image = PhotoImage(data=IMG_SPLASH)
        __self__.canvas = Label(__self__.splash, 
                image = __self__.splash_image,
                height=374)
        __self__.canvas.grid(row=0,column=0,columnspan=2)
        __self__.filequeue = StringVar()
        __self__.filequeue.set(" ")
        __self__.bar = Frame(__self__.splash,bg="#DCDCDC")
        __self__.bar.grid(row=1,column=0,columnspan=2,sticky=W+E)
        __self__.label1 = Label(__self__.bar, text="Adding to database...\t",bg="#DCDCDC")
        __self__.label1.grid(row=0,column=0,sticky=W)
        __self__.label2 = Label(__self__.bar, textvariable = __self__.filequeue,bg="#DCDCDC")
        __self__.label2.grid(row=0,column=1)
        __self__.splash.update()
        __self__.splash.update_idletasks()
        __self__.splash.wm_attributes("-topmost",True)
        __self__.splash.wm_attributes("-disabled",True)
        #__self__.splash.wm_attributes("-transparentcolor","white")
        spawn_center(__self__.splash)
        __self__.splash.deiconify()

    def splash_kill(__self__):
        try: 
            __self__.splash.destroy()
            __self__.popup.grab_set()
            __self__.popup.destroy()
        except:
            pass

    def pop_loader(__self__):
        __self__.popup = Toplevel(master=root.master)
        __self__.popup.grab_set()
        __self__.popup.resizable(False,False)
        __self__.popup.overrideredirect(True)
        x = __self__.popup.winfo_screenwidth()
        y = __self__.popup.winfo_screenheight()
        __self__.popup.geometry(
                "{}x{}+{}+{}".format(166, 51,
                int((x/2)-80), int((y/2)-23)))
        __self__.outerframe = Frame(
                __self__.popup, 
                bd=3, 
                relief=RIDGE,
                width=166, height=52)
        __self__.outerframe.grid(row=0,column=0,sticky=E+W)
        __self__.outerframe.grid_propagate(0)
        __self__.popup.label1 = Label(__self__.outerframe, text="Adding to database...")
        __self__.popup.label1.grid(row=0,column=0,sticky=W)       
        __self__.label2 = Label(__self__.outerframe, textvariable = __self__.filequeue)
        __self__.label2.grid(row=1,column=0,sticky=W)

    def load_folder_from_database(__self__,folder):
        __self__.samples_database[folder] = Constants.USER_DATABASE[folder]["prefix"]
        __self__.samples_path[folder] = Constants.USER_DATABASE[folder]["path"]
        __self__.mcacount[folder] = Constants.USER_DATABASE[folder]["mcacount"]
        __self__.mca_extension[folder] = Constants.USER_DATABASE[folder]["extension"]
        __self__.mca_indexing[folder] = Constants.USER_DATABASE[folder]["indexing"]

    def pre_load_from_database(__self__):
        not_found_samples = []
        for folder in Constants.USER_DATABASE.keys():
            if os.path.exists(Constants.USER_DATABASE[folder]["path"]):
                __self__.load_folder_from_database(folder)
                logger.info("Loaded {} parameters from database...".format(folder))
                __self__.skip_list.append(folder)
                continue
            else:
                not_found_samples.append(folder)
                logger.info(
                        "{} path ({}) does not exist. Removed from database...".format(
                            folder,Constants.USER_DATABASE[folder]["path"]))
                remove_entry_from_database(folder)
        for folder in not_found_samples:
            Constants.USER_DATABASE.pop(folder)

    def list_all(__self__):
        __self__.skip_list = []
        logger.info("Loading sample list...")
        logger.info("Reading database...")
        load_user_database()
        __self__.pre_load_from_database()
        logger.info("Done with reading database...")
        indexing = None
        mca_prefix = None
        
        try:
                        
            """ Lists all possible samples """
            samples = [name for name in os.listdir(Constants.SAMPLES_FOLDER) \
                    if os.path.isdir(os.path.join(Constants.SAMPLES_FOLDER,name))]
            
            """ Verifies which samples have a compiled datacube in output folder """
            for folder in samples:
                indexing = None
                if os.path.exists(os.path.join(SpecRead.__PERSONAL__,"output",folder)):
                    for name in os.listdir(os.path.join(SpecRead.__PERSONAL__,
                        "output",folder)):
                        if name.lower().endswith(".cube"):
                            __self__.filequeue.set(
                                    "Cube for {} already compiled, skipping mca\'s".format(
                                        folder))
                            logger.info("Cube {} already compiled".format(folder))
                            __self__.label2.update()
                            try: __self__.splash.update_idletasks()
                            except: __self__.popup.update_idletasks()
                            finally: pass
                            __self__.skip_list.append(name.split(".cube")[0])
                
                """ Lists the spectra files """            
                files = [name for name in os.listdir(os.path.join(Constants.SAMPLES_FOLDER,
                    folder))if name.lower().endswith(".mca") or name.lower().endswith(".txt")]
                extension = files[:]

                """ If spectra are found, list and get the files prefix, 
                indexing and extension """

                if files != []:
                    if folder not in __self__.skip_list:
                        for item in range(len(files)): 
                            # displays file being read on splash screen
                            __self__.filequeue.set("{}".format(files[item]))
                            __self__.label2.update()
                            try: __self__.splash.update_idletasks()
                            except: __self__.popup.update_idletasks()
                            finally:
                                try:
                                    files[item], extension[item] = \
                                            files[item].split(".",1)[0],\
                                            files[item].split(".",1)[1]

                                    """ Gets rid of file numbering """
                                    for i in range(len(files[item])):
                                        if not files[item][-1].isdigit(): break
                                        if files[item][-i].isdigit() and \
                                                not files[item][-i-1].isdigit(): 
                                            if indexing == None:
                                                indexing = files[item][-i:]
                                            files[item] = files[item][:-i]
                                            break
                                except: pass

                        files_set = set(files)
                        extension_set = set(extension)
                        counter = dict((x,files.count(x)) for x in files_set)
                        counter_ext = dict((x,extension.count(x)) for x in extension_set)
                        mca_prefix_count = 0
                        mca_extension_count = 0
                        # counts mca files and stores the prefix string and no. of files
                        for counts in counter:
                            if counter[counts] > mca_prefix_count:
                                mca_prefix = counts
                                mca_prefix_count = counter[counts]
                        for ext in counter_ext:
                            if counter_ext[ext] > mca_extension_count:
                                mca_extension = ext
                                mca_extension_count = counter_ext[ext]
                        
                        # creates a dict key only if the numer of mca's is larger than 20.
                        if mca_prefix_count >= 20 and mca_extension_count >= mca_prefix_count:
                            p = os.path.join(Constants.SAMPLES_FOLDER,folder)
                            __self__.samples_database[folder] = mca_prefix
                            __self__.samples_path[folder] = p
                            __self__.mcacount[folder] = len(files)
                            __self__.mca_extension[folder] = mca_extension
                            __self__.mca_indexing[folder] = indexing
                            write_to_user_database(
                                    folder,
                                    p,
                                    mca_prefix,
                                    len(files),
                                    mca_extension,
                                    indexing)

        except IOError as exception:
            if exception.__class__.__name__ == "FileNotFoundError":
                logger.info("No folder {} found.".format(Constants.SAMPLES_FOLDER))
            elif exception.__class__.__name__ == "PermissionError":
                logger.info("Cannot load samples. Error {}.".format(
                    exception.__class__.__name__))
                messagebox.showerror(exception.__class__.__name__,
                        "Acess denied to folder {}.\nIf error persists, try running the program with administrator rights.".format(Constants.SAMPLES_FOLDER))
            else: pass
        try:

            """ After trying to look at every folder under the folder selected, 
            priority is given to the actual selected folder """

            #if __self__.samples_database == {}:
            local_path = Constants.SAMPLES_FOLDER.split("\\")
            folder = local_path.pop(-1)
            
            # builds new path
            new_path = ""
            for name in local_path:
                new_path = new_path + name + "\\"

            if os.path.exists(os.path.join(SpecRead.__PERSONAL__,"output",folder)):
                for name in os.listdir(os.path.join(SpecRead.__PERSONAL__,
                    "output")):
                    if name.lower().endswith(".cube"):
                        __self__.filequeue.set(
                                "Cube for {} already compiled, skipping mca\'s".format(
                                    folder))
                        __self__.label2.update()
                        try: __self__.splash.update_idletasks()
                        except: __self__.popup.update_idletasks()
                        finally: pass
                        __self__.skip_list.append(name.split(".cube")[0])
            files = [name for name in os.listdir(Constants.SAMPLES_FOLDER) \
                    if name.lower().endswith(".mca") or name.lower().endswith(".txt")]
            extension = files[:]
            if files == []: pass
            else:
                if folder not in __self__.skip_list:
                    for item in range(len(files)): 
                        # displays file being read on splash screen
                        __self__.filequeue.set("{}".format(files[item]))
                        __self__.label2.update()
                        try: __self__.splash.update_idletasks()
                        except: __self__.popup.update_idletasks()
                        finally: 
                            try:
                                files[item], extension[item] = \
                                        files[item].split(".",1)[0],\
                                        files[item].split(".",1)[1]

                                """ Gets rid of file numbering """
                                for i in range(len(files[item])):
                                    if not files[item][-1].isdigit(): break
                                    if files[item][-i].isdigit() and \
                                            not files[item][-i-1].isdigit(): 
                                        if indexing == None:
                                            indexing = files[item][-i:]
                                        files[item] = files[item][:-i]
                                        break
                            except: pass

                    files_set = set(files)
                    extension_set = set(extension)
                    counter = dict((x,files.count(x)) for x in files_set)
                    counter_ext = dict((x,extension.count(x)) for x in extension_set)
                    mca_prefix_count = 0
                    mca_extension_count = 0
                    # counts mca files and stores the prefix string and no. of files
                    for counts in counter:
                        if counter[counts] > mca_prefix_count:
                            mca_prefix = counts
                            mca_prefix_count = counter[counts]
                    for ext in counter_ext:
                        if counter_ext[ext] > mca_extension_count:
                            mca_extension = ext
                            mca_extension_count = counter_ext[ext]
                    # creates a dict key only if the numer of mca's is larger than 20.
                    if mca_prefix_count >= 20 and mca_extension_count >= mca_prefix_count:
                        p = os.path.join(Constants.SAMPLES_FOLDER)
                        __self__.samples_database[folder] = mca_prefix
                        __self__.samples_path[folder] = os.path.abspath(Constants.SAMPLES_FOLDER)
                        __self__.mcacount[folder] = len(files)
                        __self__.mca_extension[folder] = mca_extension
                        __self__.mca_indexing[folder] = indexing
                        write_to_user_database(
                                folder,
                                p,
                                mca_prefix,
                                len(files),
                                mca_extension,
                                indexing)
        
        except IOError as exception:
            if exception.__class__.__name__ == "FileNotFoundError":
                logger.info("No folder {} found.".format(Constants.SAMPLES_FOLDER))
            elif exception.__class__.__name__ == "PermissionError":
                logger.info("Cannot load samples. Error {}.".format(
                    exception.__class__.__name__))
            else: pass
        
        try:
        
            """ Try looking for training_data """

            folder = "Example Data"
            new_path = os.path.join(SpecRead.__PERSONAL__,folder)
            
            if os.path.exists(new_path):
                examples = [folder for folder in os.listdir(new_path) if \
                        os.path.isdir(os.path.join(new_path,folder))]
                for folder in examples:
                    files = [name for name in os.listdir(os.path.join(new_path,folder)) \
                            if name.lower().endswith(".mca") or name.lower().endswith(".txt")]
                    extension = files[:]
                    for item in range(len(files)): 
                        # displays file being read on splash screen
                        __self__.filequeue.set("{}".format(files[item]))
                        __self__.label2.update()
                        try: __self__.splash.update_idletasks()
                        except: __self__.popup.update_idletasks()
                        finally: 
                            try:
                                files[item], extension[item] = \
                                        files[item].split(".",1)[0],\
                                        files[item].split(".",1)[1]

                                """ Gets rid of file numbering """
                                for i in range(len(files[item])):
                                    if not files[item][-1].isdigit(): break
                                    if files[item][-i].isdigit() and \
                                            not files[item][-i-1].isdigit(): 
                                        if indexing == None:
                                            indexing = files[item][-i:]
                                        files[item] = files[item][:-i]
                                        break
                            except: pass
                    files_set = set(files)
                    extension_set = set(extension)
                    counter = dict((x,files.count(x)) for x in files_set)
                    counter_ext = dict((x,extension.count(x)) for x in extension_set)
                    mca_prefix_count = 0
                    mca_extension_count = 0
                    # counts mca files and stores the prefix string and no. of files
                    for counts in counter:
                        if counter[counts] > mca_prefix_count:
                            mca_prefix = counts
                            mca_prefix_count = counter[counts]
                    for ext in counter_ext:
                        if counter_ext[ext] > mca_extension_count:
                            mca_extension = ext
                            mca_extension_count = counter_ext[ext]
                    # creates a dict key only if the numer of mca's is larger than 20.
                    if mca_prefix_count >= 20 and mca_extension_count >= mca_prefix_count:
                        __self__.samples_database[folder] = mca_prefix
                        __self__.samples_path[folder] = os.path.abspath(os.path.join(
                            new_path,folder))
                        __self__.mcacount[folder] = len(files)
                        __self__.mca_extension[folder] = mca_extension
                        __self__.mca_indexing[folder] = "1"

        except: logger.info("Could not locate Training Data.")

        try:
                                        
            """ Verify packed cubes """

            output_folder = os.path.join(SpecRead.__PERSONAL__,"output")
            outputs = [folder for folder in os.listdir(output_folder) \
                    if os.path.isdir(os.path.join(output_folder,folder))]
            for folder in outputs:
                cubes = [cube for cube in os.listdir(os.path.join(output_folder,folder)) \
                        if cube.lower().endswith('.cube')]
                if folder not in __self__.samples_database: 
                    if cubes != []: 
                        # sampes_database keys hold the mca prefixes
                        __self__.samples_database[folder] = "---"
                        __self__.samples_path[folder] = "---"
                        __self__.mcacount[folder] = 0
                        __self__.mca_extension[folder] = "---"
                        logger.info("Datacube {} located. Ignoring mca files".format(folder))
        
        except IOError as exception:
            if exception.__class__.__name__ == "FileNotFoundError":
                logger.info("No folder {} found.".format(Constants.SAMPLES_FOLDER))
            elif exception.__class__.__name__ == "PermissionError":
                logger.info("Cannot load samples. Error {}.".format(
                    exception.__class__.__name__))
            else: pass

        __self__.splash_kill()
       

class Settings:        
    def __init__(__self__,parent):

        __self__.Settings = Toplevel(master=parent.master)
        __self__.Settings.title("Settings")
        __self__.Settings.resizable(False,False)
        __self__.Settings.protocol("WM_DELETE_WINDOW",__self__.kill_window)

        __self__.CoreCount = Constants.CPUS
        sys_mem = dict(virtual_memory()._asdict())

        __self__.GeneralOptions = LabelFrame(__self__.Settings, 
                text="General options",padx=15,pady=15)
        __self__.PeakOptions = LabelFrame(__self__.Settings, 
                text="Peakmethod options",padx=15,pady=15)

        __self__.GeneralOptions.grid(row=0,column=0,padx=(15,15),sticky=N+S+W+E)
        __self__.PeakOptions.grid(row=1,column=0,padx=(15,15),sticky=N+S+W+E)

        __self__.RAM_tot = convert_bytes(sys_mem["total"])
        __self__.RAM_free = convert_bytes(sys_mem["available"])
        __self__.build_widgets()

        icon = os.path.join(os.getcwd(),"images","icons","settings.ico")
        __self__.Settings.iconbitmap(icon)  

        place_center(root.master,__self__.Settings)

        __self__.Settings.grab_set()

    def build_widgets(__self__):

        ########################
        # Set window variables #
        ########################
        
        __self__.PlotMode = StringVar()
        __self__.ColorMapMode = StringVar()
        __self__.CoreMode = BooleanVar()
        __self__.RAMMode = BooleanVar()
        __self__.RAMEntry = DoubleVar()
        __self__.RAMUnit = StringVar()
        __self__.WlcmMode = BooleanVar()
        __self__.TolVar1 = DoubleVar()
        __self__.TolVar2 = DoubleVar()
        __self__.TolVar3 = DoubleVar()
        __self__.CycVar = DoubleVar()
        __self__.Sensitivity = DoubleVar()
        __self__.WizTol = DoubleVar()
        __self__.ContSuppr = DoubleVar()
        __self__.PlotSaveVar = DoubleVar()
        __self__.PlotSaveBoolVar = BooleanVar()
        
        __self__.PlotMode.set(Constants.PLOTMODE)
        __self__.ColorMapMode.set(Constants.COLORMAP)
        __self__.CoreMode.set(Constants.MULTICORE)
        __self__.RAMMode.set(Constants.RAM_LIMIT)
        __self__.RAMEntry.set(
                "%.2f"%(float(convert_bytes(root.RAM_limit_value).split(" ")[0])))
        __self__.RAMUnit.set(convert_bytes(root.RAM_limit_value).split(" ")[1])
        __self__.WlcmMode.set(Constants.WELCOME)
        __self__.TolVar1.set(Constants.SETROI_TOLERANCE[0])
        __self__.TolVar2.set(Constants.SETROI_TOLERANCE[1])
        __self__.TolVar3.set(Constants.SETROI_TOLERANCE[2])
        __self__.CycVar.set(Constants.FIT_CYCLES)
        __self__.Sensitivity.set(Constants.PEAK_TOLERANCE)
        __self__.WizTol.set(Constants.CHECK_TOLERANCE)
        __self__.ContSuppr.set(Constants.CONTINUUM_SUPPRESSION)
        __self__.PlotSaveVar.set(Constants.SAVE_INTERVAL)
        __self__.PlotSaveBoolVar.set(Constants.SAVE_FIT_FIGURES)

        ########################
        
        PlotLabel = Label(__self__.GeneralOptions,text="Plot mode: ")
        PlotOption = ttk.Combobox(__self__.GeneralOptions, 
                textvariable=__self__.PlotMode, 
                values=("Linear","Logarithmic"),
                width=12,
                state="readonly")

        ColorMapLabel = Label(__self__.GeneralOptions,text="Color scale: ")
        ColorMapOption = ttk.Combobox(__self__.GeneralOptions, 
                textvariable=__self__.ColorMapMode, 
                values=("gray","jet","hot","Spectral"),
                width=12,
                state="readonly")

        CoreLabel = Label(__self__.GeneralOptions,text="Enable Multi-Core? ")
        CoreOption = Checkbutton(__self__.GeneralOptions, variable=__self__.CoreMode,
                command=__self__.toggle_multicore)
        CoreOptionText = Label(__self__.GeneralOptions, text="Yes")
        CoreCountLabel = Label(__self__.GeneralOptions,
                text="Total number of cores: "+str(__self__.CoreCount),
                relief=GROOVE)
        
        __self__.RAMLabel = Label(__self__.GeneralOptions,text="Limit RAM in Multi-Core? ")
        __self__.RAMUnitLabel = Label(__self__.GeneralOptions, text=__self__.RAMUnit.get())
        __self__.RAMOption = Checkbutton(__self__.GeneralOptions, variable=__self__.RAMMode,
                command=__self__.toggle_ram)
        __self__.RAMOptionText = Label(__self__.GeneralOptions, text="Yes")
        __self__.RAMEntryBox = Entry(__self__.GeneralOptions, 
                textvariable=__self__.RAMEntry,
                width=10)
        __self__.RAMCountLabel = Label(__self__.GeneralOptions,
                text="Available RAM: "+str(__self__.RAM_free))

        WlcmLabel = Label(__self__.GeneralOptions,text="Welcome message at startup? ")
        WlcmOption = Checkbutton(__self__.GeneralOptions, variable=__self__.WlcmMode)
        WlcmOptionText = Label(__self__.GeneralOptions, text="Yes")
        
        PlotLabel.grid(row=0,column=0,sticky=W)
        PlotOption.grid(row=0,column=1,columnspan=2,sticky=E)
        ColorMapLabel.grid(row=1,column=0,sticky=W)
        ColorMapOption.grid(row=1,column=1,columnspan=2,sticky=E)
        CoreLabel.grid(row=3,column=0,sticky=W)
        CoreOption.grid(row=3,column=1,sticky=E)
        CoreOptionText.grid(row=3,column=2,sticky=E)
        CoreCountLabel.grid(row=2,column=0,columnspan=12,sticky=N+S+W+E,pady=(8,0))
        __self__.RAMLabel.grid(row=4,column=0,sticky=W)
        __self__.RAMUnitLabel.grid(row=5,column=2,sticky="")
        __self__.RAMOption.grid(row=4,column=1,sticky=E)
        __self__.RAMOptionText.grid(row=4,column=2,sticky=E)
        __self__.RAMEntryBox.grid(row=5,column=1,sticky=E)
        __self__.RAMCountLabel.grid(row=5,column=0,sticky=W)
        WlcmLabel.grid(row=6,column=0,sticky=W)
        WlcmOption.grid(row=6,column=1,sticky=E)
        WlcmOptionText.grid(row=6,column=2,sticky=E)

        ###########################
        # Peakmethod Option Frame #
        ###########################

        # LABELS # 
        ToleranceLabel = Label(__self__.PeakOptions, 
                text="Auto and simple roi peak tolerance ",
                relief=GROOVE)
        Tolerance1 = Label(__self__.PeakOptions, text="< 4 KeV")
        Tolerance2 = Label(__self__.PeakOptions, text="4-12 KeV")
        Tolerance3 = Label(__self__.PeakOptions, text="> 12 KeV")
        ToleranceDescription1 = Label(__self__.PeakOptions, text="*gain")
        ToleranceDescription2 = Label(__self__.PeakOptions, text="*gain")
        ToleranceDescription3 = Label(__self__.PeakOptions, text="*gain")
        
        # ENTRIES #
        ToleranceEntry1 = Entry(__self__.PeakOptions, 
                textvariable=__self__.TolVar1,
                width=7)
        ToleranceEntry2 = Entry(__self__.PeakOptions, 
                textvariable=__self__.TolVar2,
                width=7)
        ToleranceEntry3 = Entry(__self__.PeakOptions, 
                textvariable=__self__.TolVar3,
                width=7)

        ToleranceLabel.grid(row=0,column=0,columnspan=3,sticky=N+S+W+E)
        Tolerance1.grid(row=1,column=0,sticky=W)
        Tolerance2.grid(row=2,column=0,sticky=W)
        Tolerance3.grid(row=3,column=0,sticky=W)
        ToleranceEntry1.grid(row=1,column=1,sticky=W)
        ToleranceEntry2.grid(row=2,column=1,sticky=W)
        ToleranceEntry3.grid(row=3,column=1,sticky=W)
        ToleranceDescription1.grid(row=1,column=2,sticky=E)
        ToleranceDescription2.grid(row=2,column=2,sticky=E)
        ToleranceDescription3.grid(row=3,column=2,sticky=E)

        # LABELS #
        AutoWizardLabel = Label(__self__.PeakOptions, text="Auto wizard parameters ",
                relief=GROOVE)
        FitCycles = Label(__self__.PeakOptions, text="Fit cycles/spectrum: ")
        PeakFindTolerance = Label(__self__.PeakOptions, text="Peakfind sensitivity: ")
        ContSupprLabel = Label(__self__.PeakOptions, 
                text="Continuum suppression factor: ")
        PeakCheckTolerance = Label(__self__.PeakOptions, text="Peakfind tolerance: ")
        PeakCheckLabel = Label(__self__.PeakOptions, text="*gain")
        __self__.PlotSaveInterval = Label(__self__.PeakOptions, 
                text="Save plots w/ interval: ")
        PlotSave = Label(__self__.PeakOptions, text="Save fit plots? ")
        PlotSaveYes = Label(__self__.PeakOptions, text="Yes")

        # ENTRIES #
        FitCyclesEntry = Entry(__self__.PeakOptions, 
                textvariable=__self__.CycVar,
                width=13)
        PeakFindEntry = Entry(__self__.PeakOptions,
                textvariable=__self__.Sensitivity,
                width=13)
        create_tooltip(PeakFindTolerance,"Works best when set closer to the peaks FWHM average.\nLower values usually yield more peaks.")
        create_tooltip(PeakFindEntry,"Works best when set closer to the peaks FWHM average.\nLower values usually yield more peaks.")
        ContSupprEntry = Entry(__self__.PeakOptions,
                textvariable=__self__.ContSuppr,
                width=13)
        create_tooltip(ContSupprLabel,"Spuppress misleading peaks, usually occasioned by a low peakfind sensitivity.\nHigher values will suppress more peaks.")
        create_tooltip(ContSupprEntry,"Spuppress misleading peaks, usually occasioned by a low peakfind sensitivity.\nHigher values will suppress more peaks.")
        PeakCheckEntry = Entry(__self__.PeakOptions,
                textvariable=__self__.WizTol,
                width=7)
        __self__.PlotSaveIntervalEntry = Entry(__self__.PeakOptions, 
                textvariable=__self__.PlotSaveVar,
                width=13)
        PlotSaveBool = Checkbutton(__self__.PeakOptions, 
                variable=__self__.PlotSaveBoolVar,
                command=__self__.toggle_save_plot)

        AutoWizardLabel.grid(row=4,column=0,columnspan=3,sticky=N+S+W+E,pady=(8,0))
        FitCycles.grid(row=5,column=0,sticky=W)
        PeakFindTolerance.grid(row=6,column=0,sticky=W)
        ContSupprLabel.grid(row=7,column=0,sticky=W)
        PeakCheckTolerance.grid(row=8,column=0,sticky=W)
        PeakCheckLabel.grid(row=8,column=2,sticky=E)
        __self__.PlotSaveInterval.grid(row=9,column=0,sticky=W)
        PlotSave.grid(row=10,column=0,sticky=W)
        FitCyclesEntry.grid(row=5,column=1,columnspan=2,sticky=E)
        PeakFindEntry.grid(row=6,column=1,columnspan=2,sticky=E)
        ContSupprEntry.grid(row=7,column=1,columnspan=2,sticky=E)
        PeakCheckEntry.grid(row=8,column=1,sticky=W)
        __self__.PlotSaveIntervalEntry.grid(row=9,column=1,columnspan=2,sticky=E)
        PlotSaveBool.grid(row=10,column=1,sticky=E)
        PlotSaveYes.grid(row=10,column=2,sticky=E)

        ###########################
        
        __self__.GeneralOptions.grid_columnconfigure(0,weight=1,pad=32)
        __self__.PeakOptions.grid_columnconfigure(0,weight=1,pad=32)
        __self__.toggle_ram()
        __self__.toggle_multicore()
        __self__.toggle_save_plot()
        
        ButtonsFrame = Frame(__self__.Settings, padx=10, pady=10)
        ButtonsFrame.grid(row=4,column=0,columnspan=2)
        OKButton = Button(
                ButtonsFrame, 
                text="OK", 
                justify=CENTER,
                width=10,
                command=__self__.save_settings)
        OKButton.grid(row=4,column=0)
        CancelButton = Button(
                ButtonsFrame, 
                text="Cancel", 
                justify=CENTER,
                width=10,
                command=__self__.kill_window)
        CancelButton.grid(row=4,column=1)

    def toggle_save_plot(__self__,e=""):
        yn = __self__.PlotSaveBoolVar.get()
        if yn:
            __self__.PlotSaveInterval.config(state=NORMAL)
            __self__.PlotSaveIntervalEntry.config(state=NORMAL)
        else:
            __self__.PlotSaveInterval.config(state=DISABLED)
            __self__.PlotSaveIntervalEntry.config(state=DISABLED)

    def toggle_ram(__self__,e=""):
        yn = __self__.RAMMode.get()
        if yn:
            __self__.RAMUnitLabel.config(state=NORMAL)
            __self__.RAMEntryBox.config(state=NORMAL)
            __self__.RAMCountLabel.config(state=NORMAL)
        else:
            __self__.RAMUnitLabel.config(state=DISABLED)
            __self__.RAMEntryBox.config(state=DISABLED)
            __self__.RAMCountLabel.config(state=DISABLED)
    
    def toggle_multicore(__self__,e=""):
        yn = __self__.CoreMode.get()
        if yn:
            __self__.RAMLabel.config(state=NORMAL)
            __self__.RAMOption.config(state=NORMAL)
            __self__.RAMOptionText.config(state=NORMAL)
        elif __self__.RAMMode.get():
            __self__.RAMMode.set(0)
            __self__.RAMLabel.config(state=DISABLED)
            __self__.RAMOption.config(state=DISABLED)
            __self__.RAMOptionText.config(state=DISABLED)
            __self__.RAMUnitLabel.config(state=DISABLED)
            __self__.RAMEntryBox.config(state=DISABLED)
            __self__.RAMCountLabel.config(state=DISABLED)
        else:
            __self__.RAMLabel.config(state=DISABLED)
            __self__.RAMOption.config(state=DISABLED)
            __self__.RAMOptionText.config(state=DISABLED)
            __self__.RAMUnitLabel.config(state=DISABLED)
            __self__.RAMEntryBox.config(state=DISABLED)
            __self__.RAMCountLabel.config(state=DISABLED)
    
    def write_to_ini(__self__):
        try: 
            inipath = os.path.join(SpecRead.__BIN__,"settings.tag")
            ini = open(inipath,'w+')
            ini.write("{}\n".format(Constants.SAMPLES_FOLDER))
            ini.write("<ColorMap>\t{}\n".format(__self__.ColorMapMode.get()))
            ini.write("<MultiCore>\t{}\n".format(__self__.CoreMode.get()))
            ini.write("<PlotMode>\t{}\n".format(__self__.PlotMode.get()))
            ini.write("<RAMLimit>\t{}\n".format(__self__.RAMMode.get()))
            ini.write("<welcome>\t{}\n".format(__self__.WlcmMode.get()))
            ini.write("<Tolerance>\t{}\n".format(Constants.SETROI_TOLERANCE))
            ini.write("<Cycles>\t{}\n".format(int(__self__.CycVar.get())))
            ini.write("<Sensitivity>\t{}\n".format(float(__self__.Sensitivity.get())))
            ini.write("<Suppression>\t{}\n".format(float(__self__.ContSuppr.get())))
            ini.write("<WizTolerance>\t{}\n".format(float(__self__.WizTol.get())))
            ini.write("<SaveInterval>\t{}\n".format(int(__self__.PlotSaveVar.get())))
            ini.write("<SavePlot>\t{}".format(__self__.PlotSaveBoolVar.get()))
            ini.close()
            __self__.kill_window()
        except: 
            messagebox.showerror("Error","File settings.tag not found.")
            root.master.destroy()

    def kill_window(__self__):
        try: 
            del root.SettingsWin 
            __self__.Settings.grab_release()
            __self__.Settings.destroy()
        except: pass

    def save_settings(__self__):
        Constants.RAM_LIMIT = __self__.RAMMode.get()
        root.RAM_limit_value = restore_bytes(
                float(__self__.RAMEntry.get()),
                __self__.RAMUnit.get())
        Constants.COLORMAP = __self__.ColorMapMode.get()
        Constants.MULTICORE = __self__.CoreMode.get()
        Constants.PLOTMODE = __self__.PlotMode.get()
        Constants.WELCOME = __self__.WlcmMode.get()
        if Constants.PLOTMODE == "Logarithmic": root.plot_display = "-semilog"
        if Constants.PLOTMODE == "Linear": root.plot_display = None

        Constants.SETROI_TOLERANCE = [__self__.TolVar1.get(),
                __self__.TolVar2.get(),__self__.TolVar3.get()]
        Constants.FIT_CYCLES = int(__self__.CycVar.get())
        Constants.PEAK_TOLERANCE = float(__self__.Sensitivity.get())
        Constants.CONTINUUM_SUPPRESSION = float(__self__.ContSuppr.get())
        Constants.CHECK_TOLERANCE = float(__self__.WizTol.get())
        Constants.SAVE_INTERVAL = int(__self__.PlotSaveVar.get())
        Constants.SAVE_FIT_FIGURES = __self__.PlotSaveBoolVar.get()

        refresh_plots()
        try: root.clipper.refresh_plot() 
        except: pass
        __self__.write_to_ini()
        refresh_all_plots()


class MainGUI:
    def __init__(__self__):

        if Constants.LOW_RES == "extreme": 
            quit = messagebox.showinfo("WARNING",
        "Your screen resolution is too low! XISMuS lowest supported resolution is 800x600.")
            if quit == "ok": sys.exit(1)
        logger.info("Initializing program...")
        f = open(os.path.join(SpecRead.__BIN__,"settings.tag"),"r")
        for line in f:
            if line.startswith("<welcome>"):
                if line.split("\t")[1] == "True": 
                    Constants.WELCOME = True
                else: 
                    Constants.WELCOME = False
        f.close()
        
        __self__.master = Tk()
        __self__.master.title("XISMuS {}".format(Constants.VERSION))
        __self__.master.withdraw() 
        __self__.master.attributes("-alpha",0.0)
                
        __self__.snip_config = []
        __self__.find_elements_diag = None
        __self__.ImageAnalyzers = [] 
        #everytime ImgAnalyzer API is opened, instance is appended
        
        __self__.ConfigDiag = None
        __self__.master.resizable(False,False)
        __self__.sample_figure = Figure(figsize=(3,2), dpi=100)
        __self__.sample_plot =__self__.sample_figure.add_subplot(111)
        __self__.sample_plot.grid(b=None)
        __self__.sample_plot.axis('off')
        mapfont = {'fontname':'Arial','fontsize':10}

        sys_mem = dict(virtual_memory()._asdict())
        inipath = os.path.join(SpecRead.__BIN__,"settings.tag")
        set_settings(inipath)
        __self__.RAM_limit_value = sys_mem["available"]
        if Constants.PLOTMODE == "Logarithmic": __self__.plot_display = "-semilog"
        if Constants.PLOTMODE == "Linear": __self__.plot_display = None
        
        __self__.build_widgets()
        __self__.plot_canvas.mpl_connect("button_press_event",__self__.pop)
        
        #####################################################################
        # Spawn splash screen and look for samples under the search folder  #
        # set at folder.ini # It also check the database.dat file to avoid  #
        # reading thousands of files that were read before at some time     #
        #####################################################################

        __self__.SampleLoader = Samples()
        __self__.SampleLoader.splash_screen(__self__)
        __self__.master.after(100,__self__.SampleLoader.list_all())

        #####################################################################

        #############################################
        # Attributes that carry samples information #
        #############################################

        __self__.samples = __self__.SampleLoader.samples_database
        __self__.samples_path = __self__.SampleLoader.samples_path
        __self__.mcacount = __self__.SampleLoader.mcacount
        __self__.mca_indexing = __self__.SampleLoader.mca_indexing
        __self__.mca_extension = __self__.SampleLoader.mca_extension
        __self__.temporaryh5 = "None"

        #############################################

        __self__.plot_canvas_popup = Menu(__self__.master, tearoff=0)
        __self__.plot_canvas_popup.add_command(
                label="Save density map as . . .",
                command=__self__.export_density_map)
        __self__.plot_canvas_popup.add_command(
                label="Open files location",
                command=__self__.open_files_location_from_cube)
        __self__.plot_canvas_popup.add_command(
                label="Open output folder",
                command=__self__.open_output_folder_from_cube)

        time.sleep(0.1)
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)
        __self__.master.deiconify()

        __self__.toggle_(toggle='off')
        __self__.pop_welcome()
               
    def root_quit(__self__):
        r = messagebox.askquestion("Attention","Are you sure you want to exit?")
        if r == "yes":
            for widget in __self__.master.winfo_children():
                if isinstance(widget, Toplevel):
                    widget.destroy()
            checkout_config()
            __self__.master.destroy()
            sys.exit()
        else: return
    
    def toggle_(__self__,toggle='on'):
        if toggle == 'on':
            __self__.Toolbox.entryconfig("Derived spectra", state=NORMAL)
            __self__.Toolbox.entryconfig("Image Analyzer . . .", state=NORMAL)
            __self__.ButtonReset.config(state=NORMAL)
            __self__.ImgAnalButton.config(state=NORMAL)
            __self__.FindElementButton.config(state=NORMAL)
            __self__.Toolbox.entryconfig("Reset sample",state=NORMAL)
            __self__.Toolbox.entryconfig("Check calibration",state=NORMAL)
            __self__.Toolbox.entryconfig("Verify calculated ROI",state=NORMAL)
            __self__.Toolbox.entryconfig("Map elements",state=NORMAL)
            __self__.re_configure.config(state=NORMAL)
            __self__.magnifier.config(state=NORMAL)
        if toggle == 'off':
            __self__.Toolbox.entryconfig("Derived spectra", state=DISABLED)
            __self__.Toolbox.entryconfig("Image Analyzer . . .", state=DISABLED)
            __self__.ButtonReset.config(state=DISABLED)
            __self__.ImgAnalButton.config(state=DISABLED)
            __self__.FindElementButton.config(state=DISABLED)
            __self__.Toolbox.entryconfig("Reset sample",state=DISABLED)
            __self__.Toolbox.entryconfig("Check calibration",state=DISABLED)
            __self__.Toolbox.entryconfig("Verify calculated ROI",state=DISABLED)
            __self__.Toolbox.entryconfig("Map elements",state=DISABLED)
            __self__.re_configure.config(state=DISABLED)
            __self__.magnifier.config(state=DISABLED)
    
    def pop(__self__,event):
        if event.button == 3:
            __self__.master.update_idletasks()
            x = __self__.master.winfo_pointerx()
            y = __self__.master.winfo_pointery()
            abs_coord_x = __self__.master.winfo_pointerx() - __self__.master.winfo_vrootx()
            abs_coord_y = __self__.master.winfo_pointery() - __self__.master.winfo_vrooty()
            
            try: __self__.plot_canvas_popup.tk_popup(
                    int(abs_coord_x), int(abs_coord_y), entry="")
            finally: __self__.plot_canvas_popup.grab_release()
        else: return

    def refresh_samples(__self__):
        __self__.SampleLoader.pop_loader()
        __self__.SampleLoader.list_all()
        __self__.samples = __self__.SampleLoader.samples_database
        __self__.samples_path = __self__.SampleLoader.samples_path
        try: 
            __self__.SamplesWindow.destroy()
            __self__.list_samples()
        except: __self__.list_samples()

    def invoke_wizard(__self__):

        """ This function invokes the auto wizard (BatchFitting)

        --------------------------------------------------------- """

        fit_path = SpecRead.output_path
        
        def call_table(elements):
            __self__.PoolTable = PeriodicTable(root)
            __self__.PoolTable.auto(elements)
            return
        
        def verify_existing_fit_chunks():
            frames = [npy for npy in os.listdir(
                fit_path) if npy.lower().endswith(".npy")]
            if frames == []:
                return 0
            else: 
                return frames

        if Constants.USEXLIB:

            p0 = verify_existing_fit_chunks()
            p01 = None
            if p0:
                p01 = messagebox.askquestion("Fit pieces found!",
                        "We have detected few *.npy fit pieces in the output folder. Do you wish to ERASE them and fit again? (Fitting the data can take some considerable time. If you don't wish to re-fit the data, the existing *.npy files will be used to build elemental maps, replacing the existing ones).\n\nClicking YES will ERASE the existing fitted data!")    
                if p01 == "yes":
                    try: shutil.rmtree(os.path.join(fit_path,"Fit Plots"))
                    except: pass
                    for chunk in p0:
                        try: os.remove(os.path.join(fit_path,chunk))
                        except: pass
                else:
                    root.bar = Busy(1,0)
                    root.bar.update_text("Building images...")
                    build_images(fit_path,bar=root.bar)
                    wipe_list()
                    __self__.toggle_(toggle="on")
                    __self__.MenuBar.entryconfig("Toolbox", state=NORMAL)
                    __self__.ButtonLoad.config(state=NORMAL)
                    __self__.write_stat()
                    refresh_plots()
                    return
            
            if p0 and p01 == "yes":
                p1="yes"
            else:
                p1 = messagebox.askquestion("Attention!",
        "The wizard is going to look for elements in your sample. Do you want to proceed?")
            if p1 == "yes":

                ###########################################################
                # Checks number of cores, starts MultiFitter class object #
                # and verifies which elements were detected in findpeak   #
                ###########################################################

                if Constants.MULTICORE == True and \
                        Constants.CPUS>1 and \
                        Constants.MY_DATACUBE.img_size > 400:
                    root.Fitter = MultiFit(fit_path)
                else:
                    root.Fitter = SingleFit(fit_path)
                
                save_path = os.path.join(SpecRead.output_path,"peak_find.png")
                __self__.peaks, __self__.matches = root.Fitter.locate_peaks(path=save_path)

                elements = [key for key in __self__.matches.keys()]
                elements = [ElementList[int(i)] for i in elements[:-1]]

                ###########################################################
                
                #########################
                # create message string #
                #########################
                message1 = ""
                for i in elements:
                    if i == elements[-1]:
                        message1 += "and {}".format(i)
                    else: message1 += "{}, ".format(i)
                #########################

                root.Fitter.bar.destroybar()
                p2 = messagebox.askyesnocancel("Attention!","We have found {} in your sample {}. Do you want to add more elements to the pool?".format(
            message1,Constants.MY_DATACUBE.name))

                if p2 == None:
                    del root.Fitter
                    return

                elif p2 == True:
                    call_table(elements)
                    return

                elif p2 == False:

                    start_time = time.time()
                    if Constants.MULTICORE == True and \
                            Constants.CPUS>1 and\
                            Constants.MY_DATACUBE.img_size > 400:
                        root.Fitter.launch_workers(
                                Constants.FIT_CYCLES,
                                Constants.SAVE_INTERVAL,
                                Constants.SAVE_FIT_FIGURES)
                    else: 
                        root.Fitter.run_fit()
                        del root.Fitter

                    root.bar = Busy(1,0)
                    root.bar.update_text("Building images...")
                    build_images(fit_path,bar=root.bar)

                    timestamps = open(os.path.join(SpecRead.__BIN__,"timestamps.txt"),"a")
                    timestamps.write(
                    "\n{4} - {5} WIZARD\n{0} bgtrip={1} enhance={2}\n{3} seconds\n".format(
                        elements,
                        Constants.MY_DATACUBE.config["bgstrip"],
                        Constants.MY_DATACUBE.config["enhance"],
                        time.time()-start_time,
                        time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                        Constants.MY_DATACUBE.name))
                    timestamps.close()

                ######################################################

                #################################################################### 
                # Updates mainGUI panels when running without pooling new elements #
                #################################################################### 
                
                gc.collect()
                wipe_list()
                __self__.toggle_(toggle="on")
                __self__.MenuBar.entryconfig("Toolbox", state=NORMAL)
                __self__.ButtonLoad.config(state=NORMAL)
                __self__.write_stat()
                refresh_plots()

                #################################################################### 
            else: pass
        else: 
            install = messagebox.askquestion("Xraylib not installed!","Xraylib module is required to proceed with auto wizard method. Do you wish to install it?")
            if install == "yes":
                openURL("http://lvserver.ugent.be/xraylib/")
                return
            else: return
            return
        #root.master.mainloop()

    def find_elements(__self__):

        mode = Constants.MY_DATACUBE.config["peakmethod"]
        if Constants.MY_DATACUBE.config["peakmethod"] == "auto_wizard" and\
                any("temp" in x for x in Constants.MY_DATACUBE.datatypes):
                    messagebox.showerror("Error",
                    "Temporarily loaded *.h5 files cannot be fitted! To use this method, reload the corresponding file and try again.")
                    return __self__.master.focus_force()
        elif mode == "auto_wizard":
            __self__.invoke_wizard()
        else: 
            if mode == "simple_roi":
                messagebox.showinfo("Attention!",
                "Simple roi method does NOT separate peaks. Always verify the Calculated ROI data in the Toolbox menu.")
            try:
                if __self__.find_elements_diag.master.winfo_exists() == False:
                    __self__.find_elements_diag = PeriodicTable(__self__)
                    __self__.find_elements_diag.master.protocol("WM_DELETE_WINDOW",
                            lambda: wipe_list())
                else:
                    __self__.find_elements_diag.master.focus_force()
                    place_center(__self__.master,__self__.find_elements_diag.master)
                    pass
            except:
                __self__.find_elements_diag = PeriodicTable(__self__)
                __self__.find_elements_diag.master.protocol("WM_DELETE_WINDOW",
                        lambda: wipe_list())
        
    def call_listsamples(__self__):

        """ Draws the sample list window.
        This is not a window class, but still a child of root """


        __self__.SamplesWindow = Toplevel(master=__self__.master, name="samples list")
        __self__.SamplesWindow.tagged = False
        __self__.SamplesWindow.title("Sample List")
        icon = os.path.join(os.getcwd(),"images","icons","icon.ico")
        __self__.SamplesWindow.resizable(False,True) 
        __self__.SamplesWindow.minsize(0,340)
        __self__.SamplesWindow_LabelLeft = Label(__self__.SamplesWindow, text="FOLDER")
        __self__.SamplesWindow_LabelRight = Label(__self__.SamplesWindow, text="MCA PREFIX")
        __self__.SamplesWindow_TableLeft = Listbox(
                __self__.SamplesWindow, 
                height=__self__.SamplesWindow.winfo_height())
        __self__.SamplesWindow_TableRight = Listbox(
                __self__.SamplesWindow, 
                height=__self__.SamplesWindow.winfo_height())
        __self__.SamplesWindow_TableLeft.bind("<MouseWheel>", __self__.scroll_y_L)
        __self__.SamplesWindow_TableRight.bind("<MouseWheel>", __self__.scroll_y_R)
        __self__.SamplesWindow_TableLeft.bind("<Up>", __self__.scroll_up)
        __self__.SamplesWindow_TableLeft.bind("<Down>", __self__.scroll_down)
        __self__.SamplesWindow_TableLeft.bind("<Double-Button-1>", __self__.sample_select)
        __self__.SamplesWindow_TableLeft.bind("<Return>", __self__.sample_select)
        __self__.SamplesWindow_TableLeft.bind("<Button-3>", __self__.sample_popup)
        
        __self__.SamplesWindow_LabelLeft.grid(row=0,column=0)
        __self__.SamplesWindow_LabelRight.grid(row=0,column=1)
        __self__.SamplesWindow_TableLeft.grid(pady=5, row=1,column=0,sticky=N+S)
        __self__.SamplesWindow_TableRight.grid(pady=5, row=1,column=1,sticky=N+S)
        __self__.SamplesWindow_multi = Button(
                __self__.SamplesWindow, 
                text = "Export multiple maps", 
                bd=3, 
                command=__self__.select_multiple)
        __self__.SamplesWindow_ok = Button(
                __self__.SamplesWindow, 
                text = "Validate", 
                bd=3, 
                command=__self__.digestmaps)
        __self__.SamplesWindow_multi.grid(row=2,column=0,sticky=W+E)
        __self__.SamplesWindow_ok.grid(row=2,column=1,sticky=W+E)
        __self__.SamplesWindow_ok.config(state=DISABLED)

        Grid.rowconfigure(__self__.SamplesWindow, 1, weight=1)
        
        #pop-up commands (rigth-click)
        __self__.SamplesWindow.popup = Menu(__self__.SamplesWindow, tearoff=0)
        __self__.SamplesWindow.popup.add_command(
                label="Load",
                command=__self__.sample_select)
        __self__.SamplesWindow.popup.add_command(
                label="Save density map",
                command=__self__.export_density_map)
        __self__.SamplesWindow.popup.add_command(
                label="Open files location",
                command=__self__.open_files_location)
        __self__.SamplesWindow.popup.add_command(
                label="Open output folder",
                command=__self__.open_output_folder)
        __self__.SamplesWindow.popup.add_command(
                label="Remove from database",
                command=__self__.remove_sample)
        __self__.SamplesWindow.popup.add_command(
                label="Clear all maps",
                command=lambda: __self__.sample_select(override=True))

        for key in __self__.samples:
            __self__.SamplesWindow_TableLeft.insert(END,"{}".format(key))
            __self__.SamplesWindow_TableRight.insert(END,"{}".format(__self__.samples[key]))

        place_topright(__self__.master,__self__.SamplesWindow)
        __self__.SamplesWindow.iconbitmap(icon)
        __self__.SamplesWindow_TableRight.config(state=DISABLED)
        __self__.SamplesWindow_TableLeft.focus_set()

    def remove_sample(__self__,e=""):
        try:
            sample = __self__.SamplesWindow_TableLeft.get(ACTIVE)
        except:
            sample = event
        if sample == "" or "Training Data" in sample: return

        d = messagebox.askquestion("Attention!",
        "Are you sure you want to remove sample {} from the list? It will not delete the sample data or the compiled datacube.".format(sample))
        
        if d=="yes":
            try:
                del Constants.USER_DATABASE[sample]["prefix"]
                del Constants.USER_DATABASE[sample]["path"]
                del Constants.USER_DATABASE[sample]["mcacount"]
                del Constants.USER_DATABASE[sample]["indexing"]
                del Constants.USER_DATABASE[sample]["extension"]
                del Constants.USER_DATABASE[sample]
                __self__.list_samples()
            except KeyError:
                messagebox.showinfo("Compiled cube","This sample is not in the database. The Datacube was added from \"XISMuS\\output\" folder. If you don't want to see this sample, remove it from the output folder manually.")
                return
            del __self__.samples[sample]
            del __self__.samples_path[sample]
            del __self__.mcacount[sample]
            del __self__.mca_indexing[sample]
            del __self__.mca_extension[sample]

            try: __self__.summation.master.destroy()
            except: pass
            try: __self__.MPS.master.destroy()
            except: pass
            try: __self__.combined.master.destroy()
            except: pass

            remove_entry_from_database(sample)
            SpecRead.conditional_setup()
            load_cube()
            __self__.write_stat()
            __self__.wipe()
            __self__.list_samples()
            __self__.draw_map()

        else: return

    def select_multiple(__self__):
        """ Toggles the multiple selection mode """

        if __self__.SamplesWindow_multi.config("relief")[-1] == "raised":
            __self__.SamplesWindow_TableLeft.selection_clear(0, END)
            __self__.SamplesWindow_TableLeft.config(selectmode=MULTIPLE)
            __self__.SamplesWindow_multi.config(relief="sunken",fg="red")
            __self__.SamplesWindow_ok.config(state=NORMAL)
        else: 
            __self__.SamplesWindow_TableLeft.selection_clear(0, END)
            __self__.SamplesWindow_TableLeft.config(selectmode=SINGLE)
            __self__.SamplesWindow_multi.config(relief="raised",fg="black")
            __self__.SamplesWindow_ok.config(state=DISABLED)

    def digestmaps(__self__):
        """ Lists all cubes in output folder, matches to the selected 
        samples in Samples List and normalizes all density maps to maximum detected
        value in detected (and compiled) cube maps. Files are saved to the promted 
        folder """

        cube_dict, maps, maxima, packed_maps, cubes = {}, {}, {}, [], []
        for item in __self__.SamplesWindow_TableLeft.curselection():
            cubes.append(__self__.SamplesWindow_TableLeft.get(item))
        if cubes == []: 
            messagebox.showinfo("No Sample!","No sample selected!")
            return 
        _path = os.path.join(SpecRead.__PERSONAL__,"output")
        """ list all packed cubes """
        cube_folders = [name for name in os.listdir(_path) \
                if os.path.isdir(os.path.join(_path,name))]
        for folder in cube_folders:
            for name in os.listdir(os.path.join(_path,folder)):
                if name.endswith(".cube")\
                        and name.split(".cube")[0] in cubes:
                        cube_dict[folder] = name
        for cube in cube_dict: 
            maps[cube] = {}
            cube_file = open(os.path.join(_path,cube,cube_dict[cube]),'rb')
            datacube = pickle.load(cube_file)
            cube_file.close()
            maps[cube]["densemap"] = datacube.densitymap
            maxima["densemap"] = 0
            for element in datacube.check_packed_elements():
                maps[cube][element] = datacube.unpack_element(
                        element.split("_")[0],
                        element.split("_")[1])
                maxima[element] = 0
        for cube in maps:
            packed_maps.append(maps[cube])
        if packed_maps == []:
            no_map = messagebox.showinfo("No Maps!",
                    "No compiled maps are present in the set of samples selected!")
            if no_map == "ok": return
        element_maps = set.intersection(*map(set,packed_maps))
        
        """ get the absolute maximum from all cubes
        this is applicable to SETS OF DATA that have a 
        relation between themselves, for example, when
        working with a larger sample that is composed of several
        datacubes """ 
        
        if element_maps != "":
            __self__.maps_window = Toplevel()
            __self__.maps_window.withdraw()
            icon = ".\\images\\icons\\icon.ico"
            __self__.maps_window.title("Available maps")
            __self__.maps_window.iconbitmap(icon)
            __self__.maps_window.resizable(False, False)
            __self__.maps_window.geometry("240x180")
            __self__.maps_list = Listbox(__self__.maps_window)
            __self__.maps_list.pack(side=TOP, fill=X)
            __self__.maps_list.config(selectmode=MULTIPLE)
            element_maps = sorted(list(element_maps))
            for item in element_maps:
                __self__.maps_list.insert(END,"{}".format(item))
            __self__.ok_btn = Button(__self__.maps_window, text="Export!", bd=3, width=13, \
                    command = lambda: __self__.export_maps(cube, maps, maxima))
            __self__.ok_btn.pack(side=BOTTOM, pady=3)
            place_center(root.SamplesWindow.master, __self__.maps_window)
            __self__.maps_window.deiconify()
            __self__.maps_window.focus_force()
            __self__.maps_window.grab_set()
        else: pass
        
    def export_maps(__self__, cube, maps, maxima):
        selection = []
        for item in __self__.maps_list.curselection():
            selection.append(__self__.maps_list.get(item))
        _path = filedialog.askdirectory(title="Export to")
        if _path != "":
            try: os.mkdir(_path+"\\")
            except: pass
            for cube in maps:
                for image in selection:
                    if maxima[image] < maps[cube][image].max():
                        maxima[image] = maps[cube][image].max()
            for cube in maps:
                for image in selection:
                    norm_map = maps[cube][image]/maxima[image]*255
                    cv2.imwrite(_path+"\\{}_{}.png".format(cube,image),norm_map)
            __self__.select_multiple()
        else: __self__.select_multiple()
        __self__.maps_window.grab_release()
        __self__.maps_window.destroy()

    def list_samples(__self__):
        """ Function invoked by the UI widget. It verifies the exitence
        of any running instance of samples window and call the function which
        draws it accordingly """

        try:
            if __self__.SamplesWindow.state() == 'normal': 
                __self__.SamplesWindow.focus_force()
                __self__.SamplesWindow.delete(0,END)
                for key in __self__.samples:
                    __self__.SamplesWindow_TableLeft.insert(END,"{}".format(key))
                    __self__.SamplesWindow_TableRight.insert(END,"{}".format(\
                            __self__.samples[key]))
                __self__.SamplesWindow_TableLeft.set_focus()
                place_topright(__self__.master,__self__.SamplesWindow)
                pass
            else: __self__.call_listsamples()
        except: __self__.call_listsamples()

    def scroll_y_R(__self__,event):
        """ Right table triggers. Scrolls Left """
        if event.delta == 120: lines = -5
        else: lines = 5
        __self__.SamplesWindow_TableLeft.yview_scroll(lines,"units") 
        return 
    
    def scroll_y_L(__self__,event):
        """ Left table triggers. Scrolls Right """
        if event.delta == 120: lines = -5
        else: lines = 5
        __self__.SamplesWindow_TableRight.yview_scroll(lines,"units") 
        return 

    def scroll_up(__self__,event):
        if __self__.SamplesWindow_TableRight.yview() != __self__.SamplesWindow_TableLeft.yview():
            __self__.SamplesWindow_TableRight.yview_scroll(-1,"units") 

    def scroll_down(__self__,event):
        if __self__.SamplesWindow_TableRight.yview() != __self__.SamplesWindow_TableLeft.yview():
            __self__.SamplesWindow_TableRight.yview_scroll(1,"units") 

    def sample_select(__self__,event="",override=False):
        """ Loads the sample selected from the sample list menu. If the cube is 
        compiled, loads it to memory. If not, the configuration dialog is called """
        
                
        if override  == False:
            # name of selected sample
            try: 
                value = __self__.SamplesWindow_TableLeft.get(ACTIVE)
            except:
                value = event
            if value == "": return
            
            #############################################################
            # WHEN SELECTING ANOTHER ITEM AND A TEMPORARY H5 IS LOADED, #
            # GET RID OF IT                                             #
            #############################################################
            try: #because there could be no datacube loaded previously (MY_DATACUBE = None)
                if any("temp" in x for x in Constants.MY_DATACUBE.datatypes) and \
                        value != Constants.MY_DATACUBE.name:
                    idx = __self__.SamplesWindow_TableLeft.get(0, END).index(
                            Constants.MY_DATACUBE.name)
                    del root.samples[Constants.MY_DATACUBE.name]
                    del root.samples_path[Constants.MY_DATACUBE.name]
                    del root.mcacount[Constants.MY_DATACUBE.name]
                    del root.mca_indexing[Constants.MY_DATACUBE.name]
                    del root.mca_extension[Constants.MY_DATACUBE.name]
                    root.temporaryh5 = "None"
                    gc.collect()
                    __self__.SamplesWindow_TableLeft.delete(idx)
                    __self__.SamplesWindow_TableRight.config(state=NORMAL)
                    __self__.SamplesWindow_TableRight.delete(idx)
                    __self__.SamplesWindow_TableRight.config(state=DISABLED)
                    __self__.SamplesWindow_TableRight.update_idletasks()
                    temp_path = os.path.join(
                        SpecRead.__PERSONAL__,"output",Constants.MY_DATACUBE.name)
                    if os.path.exists(temp_path):
                        shutil.rmtree(temp_path)
            except: pass
            #############################################################

        else: 
            value = __self__.SamplesWindow_TableLeft.get(ACTIVE)
            

            """ If cube clicked is not the one in memory, load it and configure variables """
            try: in_memory = Constants.MY_DATACUBE.name
            except AttributeError: in_memory = None
            if in_memory != value:
                local_cube_path = os.path.join(SpecRead.workpath,"output",value,value+".cube")
                if os.path.exists(local_cube_path):
                    SpecRead.cube_path = os.path.join(
                            SpecRead.workpath,"output",value,value+".cube")
                    load_cube()
                    SpecRead.setup_from_datacube(Constants.MY_DATACUBE,__self__.samples)
                    __self__.SampleVar.set("Sample on memory: "+Constants.SAMPLE_PATH)
            """ ------------------------------------------------------------------------- """
            
            p = messagebox.askquestion("Attention!",
                    "This will remove all elemental maps packed in datacube {}. Are you sure you want to proceed?".format(Constants.MY_DATACUBE.name))
            if p == "yes":
                Constants.MY_DATACUBE.wipe_maps()
            else: return 0

        __self__.master.deiconify()
        __self__.master.focus_set()
        if root.samples[value] == "temp .h5":
            return
        for widget in __self__.master.winfo_children():
            if isinstance(widget, Toplevel): 
                try: 
                    if widget.tagged == True: widget.destroy()
                except:
                    pass
        __self__.toggle_("off")
         
        if __self__.SampleVar.get().split(":")[1].replace(" ","") != value:
            # destroy any open configuration window
            # and all open plot windows
            try: __self__.ConfigDiag.master.destroy()
            except: pass
            try: __self__.summation.master.destroy()
            except: pass
            try: __self__.MPS.master.destroy()
            except: pass
            try: __self__.combined.master.destroy()
            except: pass

            #########################################################################
            # This funcion can be called by the main panel when SamplesWindow       #
            # is destroyed or not yet invoked. To avoid crashes, the function       #
            # attempts to check the multi buttun status (multiple selection on/off  #
            #########################################################################
            
            try:
                if __self__.SamplesWindow_multi["relief"] == "sunken":
                    __self__.select_multiple()
                    return
            except: pass
            
           #########################################################################
        
        """ to avoid unecessarily changing the global variable cube_path, a local version
        is created to check the existance of a cube file for the selected sample. 
        If it exists,then the global variable is changed, the cube is loaded to memory 
        and the aplication load the configuration embedded in the cube file. 
        Config.cfg remains unchanged. If the cube does not exists, 
        the user is promped to config the sample and click ok to compile it.
        Let the user cancel the cofiguration dialog, 
        the global variable cube_path is unchanged. """
        
        local_cube_path = os.path.join(SpecRead.workpath,"output",value,value+".cube")
        if os.path.exists(local_cube_path): 
            SpecRead.cube_path = os.path.join(SpecRead.workpath,"output",value,value+".cube")
            load_cube()
            SpecRead.setup_from_datacube(Constants.MY_DATACUBE,__self__.samples)
            __self__.SampleVar.set("Sample on memory: "+Constants.SAMPLE_PATH)
            __self__.toggle_(toggle="on")    
            __self__.write_stat()   
            __self__.draw_map()
        else: 
            if "Example Data" in value: path="auto"
            else: path=root.samples_path[value]
            SpecRead.conditional_setup(name=value,path=path)
            __self__.call_configure()

    def pop_welcome(__self__):
        """Displays a pop-up window with information on the software"""
        if Constants.WELCOME == True:
            __self__.welcome_window = Welcome(__self__.master)
            __self__.welcome_window.master.grab_set()
            place_center(__self__.master, __self__.welcome_window.master)
        else: pass

    def sample_popup(__self__,event):
        """Call the right-click menu for SampleList"""

        __self__.SamplesWindow_TableLeft.select_clear(0,END)
        idx = __self__.SamplesWindow_TableLeft.nearest(event.y)
        __self__.SamplesWindow_TableLeft.select_set(idx)
        __self__.SamplesWindow_TableLeft.activate(idx)

        name = __self__.SamplesWindow_TableRight.get(idx)
        if "temp" in name:
            __self__.SamplesWindow.popup.entryconfig("Load", state=DISABLED)
            __self__.SamplesWindow.popup.entryconfig("Clear all maps", state=DISABLED)
            __self__.SamplesWindow.popup.entryconfig("Remove from database", state=DISABLED)
            __self__.SamplesWindow.popup.entryconfig("Save density map", state=DISABLED)
        else:
            __self__.SamplesWindow.popup.entryconfig("Load", state=NORMAL)
            __self__.SamplesWindow.popup.entryconfig("Clear all maps", state=NORMAL)
            __self__.SamplesWindow.popup.entryconfig("Remove from database", state=NORMAL)
            __self__.SamplesWindow.popup.entryconfig("Save density map", state=NORMAL)

        try: __self__.SamplesWindow.popup.tk_popup(event.x_root, event.y_root, entry="")
        finally: __self__.SamplesWindow.popup.grab_release()
    
    def draw_map(__self__):
        try: 
            __self__.sample_plot.imshow(Constants.MY_DATACUBE.densitymap, 
                    cmap=Constants.COLORMAP, 
                    vmin=0,
                    vmax=Constants.MY_DATACUBE.densitymap.max(),)
            __self__.plot_canvas.draw()
        except: 
            __self__.sample_plot.imshow(np.ones([20,20]), cmap=Constants.COLORMAP,
                    vmin=0,
                    vmax=1)
            __self__.plot_canvas.draw()
    
    def open_files_location_from_cube(__self__,event=""):
        try:
            value = Constants.MY_DATACUBE.name
        except:
            messagebox.showerror("No datacube!","Please load a datacube first.")
            return
        local_cube_path = os.path.join(SpecRead.workpath,"output",value,value+".cube")
        if os.path.exists(local_cube_path):
            path = Constants.MY_DATACUBE.path
            path = os.path.realpath(path)
            os.startfile(path)
    
    def open_output_folder_from_cube(__self__, event=""):
        try:
            value = Constants.MY_DATACUBE.name
        except:
            messagebox.showerror("No datacube!","Please load a datacube first.")
            return
        path = os.path.join(SpecRead.__PERSONAL__,"output",value)
        if os.path.exists(path):
            path = os.path.realpath(path)
            os.startfile(path)
        else:
            messagebox.showinfo("Directory not found.",
                    "Sample may be uncompiled. Output directory for sample {} not found.".format(value))

    
    def open_files_location(__self__, event=""):
        value = __self__.SamplesWindow_TableLeft.get(ACTIVE)
        local_cube_path = os.path.join(SpecRead.workpath,"output",value,value+".cube")
        path = root.samples_path[value]
        if Constants.MY_DATACUBE == None or Constants.MY_DATACUBE.name != value:
            if os.path.exists(local_cube_path):
                __self__.sample_select(event)
                path = Constants.MY_DATACUBE.path
                path = os.path.realpath(path)
                try: os.startfile(path)
                except FileNotFoundError:
                    messagebox.showinfo("Directory not found.",
                        "Sample files not found! Path {} couldn't be located.".format(path))
            elif os.path.exists(path):
                """if datacube is not compiled, check if mca files are under 
                the selected sample folder chosen by the user"""
                path = os.path.realpath(path)
                try: os.startfile(path)
                except FileNotFoundError:
                    messagebox.showinfo("Directory not found.",
                        "Sample files not found! Path {} couldn't be located.".format(path))
            else:
                messagebox.showinfo("Directory not found.",
                        "Sample files not found! Path {} couldn't be located.".format(path))
        else:
            path = Constants.MY_DATACUBE.path
            path = os.path.realpath(path)
            try: os.startfile(path)
            except FileNotFoundError:
                messagebox.showinfo("Directory not found.",
                    "Sample files not found! Path {} couldn't be located.".format(path))

    def open_output_folder(__self__, event=""):
        try: 
            value = __self__.SamplesWindow_TableLeft.get(ACTIVE)
        except: 
            try:
                value = Constants.MY_DATACUBE.name
            except: 
                messagebox.showerror("No datacube!","Please load a datacube first.")
                return
        path = os.path.join(SpecRead.__PERSONAL__,"output",value)
        if os.path.exists(path):
            path = os.path.realpath(path)
            os.startfile(path)
        else:
            messagebox.showinfo("Directory not found.",
                    "Sample may be uncompiled. Output directory for sample {} not found.".format(value))

    def export_density_map(__self__,event=""):
        try:
            actv = root.SamplesWindow_TableLeft.get(ACTIVE)
            curr = Constants.MY_DATACUBE.name
            if actv == curr:
                pass
            else:
                __self__.sample_select(event)
        finally: 
            try: 
                if  e.cget("text") == "Save density map as . . .":
                    pass
                else:
                    __self__.sample_select(event)
            except: 
                if Constants.MY_DATACUBE == None:
                    messagebox.showerror("No datacube!","Please load a datacube first.")
                    return
            if os.path.exists(SpecRead.cube_path) or hasattr(Constants.MY_DATACUBE,"densitymap"): 
                f = filedialog.asksaveasfile(mode='w', 
                        defaultextension=".png",
                        filetypes=[("Portable Network Graphic", "*.png")],
                        title="Save as...")
            else: 
                return
            if f is None: 
                return
            image = Constants.MY_DATACUBE.densitymap
            factor = Constants.TARGET_RES/max(image.shape)
            newX, newY = int(factor*image.shape[0]),int(factor*image.shape[1])
            if Constants.MY_DATACUBE.config["enhance"]:
                image = cv2.resize(image*255/image.max(),
                        (newY,newX),interpolation=cv2.INTER_CUBIC)
                plt.imsave(f.name, image, cmap=Constants.COLORMAP)
            else:
                image = cv2.resize(image*255/image.max(),
                        (newY,newX),interpolation=cv2.INTER_NEAREST)
                plt.imsave(f.name, image, cmap=Constants.COLORMAP)
            return 0

    def wipe(__self__,e=""):
        try: 
            __self__.ConfigDiag.master.grab_release()
            __self__.ConfigDiag.master.destroy()
        except: pass
        Constants.MY_DATACUBE = None
        load_cube()
        __self__.write_stat()
        __self__.draw_map()
        __self__.toggle_(toggle='off')
        __self__.SampleVar.set("Sample on memory: None")
        try: 
            if __self__.SamplesWindow.state() == "normal": 
                __self__.SamplesWindow.deiconify()
                __self__.SamplesWindow_TableLeft.focus_set()
        except: pass
        
    def refresh_ImageCanvas(__self__,i):
        try: 
            __self__.sample_plot.imshow(__self__.densitymap,
                    cmap=Constants.COLORMAP,
                    label='Counts Map',
                    vmin=0,
                    vmax=__self__.densitymap.max())
        except: 
            __self__.sample_plot.imshow(np.ones([20,20]),
                    vmin=0,
                    vmax=1)
    
    def converter(__self__):
        __self__.converterGUI = Convert_File_Name(__self__.master) 

    def h5loader(__self__):
        def readh5(name):
            with h5py.File(name, "r") as f:
                a_group_key = list(f.keys())[0]
                data = list(f[a_group_key])
                matrix = np.asarray(data, dtype="int32", order="C")
                del data
                gc.collect()
            return matrix

        h5f = filedialog.askopenfilename(parent=__self__.master,
                title="Select h5 file",
                filetypes=(
                    ("H5 Files", "*.h5"),
                    ("All files", "*.*")))
        if h5f == "": return
 
        root.h5path = h5f
        sample_name = str(h5f).split("/")[-1].split(".")[0]

        ##################################
        # Verifies if h5 datacube exists #
        ##################################
        if os.path.exists(os.path.join(
            SpecRead.__PERSONAL__,"output",sample_name,sample_name+".cube")):
            messagebox.showinfo("Cube exists","Datacube for {} already exist!".format(
                sample_name))
            return
        else: 
            ##############################################
            # Verifies if h5 is loaded as a temporary h5 #
            ##############################################
            if sample_name == root.temporaryh5:
                messagebox.showinfo("Info!","Sample {} is already loaded as a temporary h5 file. Select another sample and try again!".format(sample_name))
                return
            ##############################################
        ##################################

        path = str(h5f).split("/")
        path.pop(-1)
        conc_path = ""
        for i in path:
            conc_path += i+"\\"
        conc_path = os.path.abspath(conc_path)
        SpecRead.conditional_setup(name=sample_name,path=conc_path)

        ###############################
        # EXTRACT INFORMATION FROM h5 #
        ###############################
        #NOTE: Attention to root.images_dict, that exists to hold any previously existing
        # images in the h5 file to parse them to the SpecMath.datacube.__init__

        root.images_dict = {}
        Constants.MY_DATACUBE = readh5(h5f)
        img_size = Constants.MY_DATACUBE.shape[0]*Constants.MY_DATACUBE.shape[1]
        specsize = Constants.MY_DATACUBE.shape[2]
        __self__.mcacount[sample_name] = img_size
        __self__.samples[sample_name] = ".h5"
        __self__.samples_path[sample_name] = conc_path
        __self__.mca_indexing[sample_name] = ".h5"
        __self__.mca_extension[sample_name] = ".h5"
        __self__.temporaryh5 = sample_name
        Constants.FIRSTFILE_ABSPATH = h5f
        ###############################

        #3 ask for a sample name and dimension (modified dimension diag)
        try:
            __self__.config_xy = (Constants.MY_DATACUBE.shape[0],Constants.MY_DATACUBE.shape[1])
            __self__.ManualParam = []
        except:
            dimension = (Constants.MY_DATACUBE.shape[0],Constants.MY_DATACUBE.shape[1])
            __self__.master.wait_window(dimension.win)
            if dimension.exit_code == "cancel":
                __self__.wipe()
                return 0
            __self__.ManualParam = []

        # calls the configuration window
        __self__.ConfigDiag = ConfigDiag(__self__.master,matrix=Constants.MY_DATACUBE)
        __self__.ConfigDiag.build_widgets()

    def batch(__self__):
        #1 prompt for files
        file_batch = filedialog.askopenfilenames(parent=__self__.master, 
                title="Select spectra",                        
                filetypes=(
                    ("MCA Files", "*.mca"),
                    ("Text Files", "*.txt"),
                    ("All files", "*.*")))
        if file_batch == "": return
        
        #1.1 get the name of parent directory
        try: sample_name = str(file_batch[0]).split("/")[-2]
        except IndexError: messagebox.showerror("No parent folder!","No parent folder detected. Be sure the spectra files are under a common folder (Hard drives are not parent folders!)")

        #2 setup variables in SpecRead and GUI
        path = str(file_batch[0]).split("/")
        path.pop(-1)
        conc_path = ""
        for i in path:
            conc_path += i+"\\"
        conc_path = os.path.abspath(conc_path)
        SpecRead.conditional_setup(name=sample_name,path=conc_path)
        __self__.mcacount[sample_name] = len(file_batch)
        """ samples dict attribute is always a string, except in this particular case """
        __self__.samples[sample_name] = file_batch
        __self__.samples_path[sample_name] = conc_path
        __self__.mca_indexing[sample_name] = file_batch[0].split(".")[0]
        __self__.mca_extension[sample_name] = "---"
        Constants.FIRSTFILE_ABSPATH = file_batch[0]

        #3 ask for a sample name and dimension (modified dimension diag)
        try: 
            __self__.config_xy = SpecRead.getdimension()
            __self__.ManualParam = []
        except:
            dimension = DimensionDiag(Constants.DIRECTORY)
            __self__.master.wait_window(dimension.win) 
            if dimension.exit_code == "cancel":
                __self__.wipe()
                return 0
            __self__.ManualParam = []
                
        # calls the configuration window
        __self__.ConfigDiag = ConfigDiag(__self__.master,
                matrix=np.zeros([1,1,1],dtype="int32"))
        __self__.ConfigDiag.build_widgets()
        
    def plot_ROI(__self__):
        master = __self__.master
        ROI_plot = PlotWin(master)
        ROI_plot.draw_ROI()

    def plot_calibration_curve(__self__):
        master = __self__.master
        calibration_plot = PlotWin(master)
        calibration_plot.draw_calibration()
    
    def call_summation(__self__):
        master = __self__.master
        __self__.summation = PlotWin(master)
        __self__.summation.draw_spec(
                mode=['summation'],
                display_mode=root.plot_display,
                lines=False)
        spawn_center(__self__.summation.master)
    
    def call_mps(__self__):
        master = __self__.master
        __self__.MPS = PlotWin(master)
        __self__.MPS.draw_spec(
                mode=['mps'],
                display_mode=root.plot_display,
                lines=False)
        spawn_center(__self__.MPS.master)
    
    def call_combined(__self__):
        __self__.combined = PlotWin(__self__.master)
        __self__.combined.draw_spec(
                mode=['summation','mps'],
                display_mode=root.plot_display,
                lines=False)
        spawn_center(__self__.combined.master)
    
    def call_author(__self__):
        try:
            if __self__.AboutWin.master.state() == "normal":
                __self__.AboutWin.master.focus_force()
        except:
            __self__.AboutWin = About(__self__)

    def call_settings(__self__):
        try:
            if __self__.SettingsWin.Settings.winfo_exists() == False:
                __self__.SettingsWin = Settings(__self__)
            else:
                __self__.SettingsWin.Settings.focus_force()
                place_center(__self__.master,__self__.SettingsWin.Settings)
                pass
        except:
            __self__.SettingsWin = Settings(__self__)

    def open_mosaic(__self__):
        CanvasSizeDialog()
    
    def prompt_mosaic_load_file(__self__):
        f = filedialog.askopenfilename(title="Open mosaic",
                    filetypes=[("Mosaic files","*.mosaic")])
        if f == "": return
        else:
            s = open(f,"r") 
            size = [int(i) for i in s.readlines()[0].split("shape:")[-1].split("x")]
            Mosaic_API(size, root, loadfile=f)

    def open_analyzer(__self__):
        API = ImageAnalyzer(__self__.master,Constants.MY_DATACUBE)
        __self__.ImageAnalyzers.append(API) 

    def reconfigure(__self__):
        ReConfigDiag(__self__.master)
        
    def build_widgets(__self__):
        magnifier_icon = PhotoImage(data=ICO_MAGNIFIER)
        __self__.MAG_ICON = magnifier_icon.subsample(1,1)

        # define the frame and layout
        __self__.ButtonsFrame = Frame(__self__.master)
        __self__.ButtonsFrame.grid_propagate(1)
        __self__.ButtonsFrame.grid(row=0, column=0, rowspan=3, columnspan=2,padx=16,sticky="")
        __self__.ImageCanvas = Canvas(__self__.master,
                width=200, height=200,
                bg='black', relief=SUNKEN, bd=5)
        __self__.ImageCanvas.grid(row=3, column=0, rowspan=3, columnspan=2, padx=(8,8),sticky="")
        __self__.ImageCanvas.propagate(1)
        __self__.magnifier = Button(__self__.master,
                image=__self__.MAG_ICON,
                bg="white", bd=1,
                command=__self__.magnify)
        __self__.magnifier.grid(row=5, column=0, sticky=S+W, padx=(11,0), pady=(0,20))
        __self__.DataFrame = Frame(__self__.master).grid(
                padx=16, pady=16, row=0, column=2, rowspan=3, columnspan=3)
        __self__.StatusScroller = Scrollbar(__self__.DataFrame, relief=SUNKEN)
        __self__.StatusBox = Listbox(__self__.DataFrame, 
                yscrollcommand=__self__.StatusScroller.set)
        __self__.StatusBox.grid(
                row=0, 
                column=2, 
                rowspan=3, 
                columnspan=3, 
                sticky=W+E, 
                padx=(16,0))
        __self__.StatusScroller.grid(row=0, column=5, rowspan=3, sticky=N+W+E+S, padx=(0,16))
        __self__.StatusScroller.config(command=__self__.StatusBox.yview) 
        __self__.ConfigFrame = LabelFrame(
                __self__.DataFrame,
                padx=8, pady=8,
                text="Configuration: ")
        __self__.master.columnconfigure(3,weight=1,minsize=4)
        __self__.ConfigFrame.grid(row=3, column=2, rowspan=3, columnspan=4, padx=16,pady=10)
         
        # start matplotlib call inside __self__.ImageCanvas
        blank_image = np.zeros([1,1])
        __self__.plot_canvas = FigureCanvasTkAgg(__self__.sample_figure,__self__.ImageCanvas)
        __self__.plot_canvas.draw()
        __self__.plot_canvas.get_tk_widget().grid(\
                row=3, column=0, rowspan=3, columnspan=2, sticky=E, padx=(3,3), pady=(3,3))
        
        __self__.draw_map()

        #####
        # define the tables which go inside the DataFrame (bottom left corner)
        
        __self__.TableLabel2 = Label(__self__.ConfigFrame,text="KEY")
        __self__.TableLabel3 = Label(__self__.ConfigFrame,text="PACKED")
        __self__.TableLabel2.grid(row=4, column=2)
        __self__.TableLabel3.grid(row=4, column=3, columnspan=2)

        __self__.TableLeft = Listbox(__self__.ConfigFrame)
        __self__.TableLeft.update()
        __self__.TableMiddle = Listbox(
                __self__.ConfigFrame, 
                width=int(__self__.TableLeft.winfo_reqwidth()/3))
        __self__.TableLeft.grid(row=5, column=2, sticky=N+S)
        __self__.TableMiddle.grid(row=5, column=3, columnspan=2, sticky=N+S)
        
        re_configure_icon = PhotoImage(data=ICO_REFRESH)
        __self__.re_configure_icon = re_configure_icon.subsample(1,1)
        __self__.re_configure = Button(
                __self__.ConfigFrame, 
                image=__self__.re_configure_icon, 
                width=32, 
                height=32, 
                command=__self__.reconfigure)
        __self__.re_configure.grid(row=5, column=5, sticky=S,padx=6)
        
        #####
        # define the menu bar

        __self__.MenuBar = Menu(__self__.master,tearoff=0)
        __self__.Toolbox = Menu(__self__.MenuBar,tearoff=0)
        __self__.derived_spectra = Menu(__self__.Toolbox,tearoff=0)

        __self__.MenuBar.add_cascade(label="Toolbox", menu=__self__.Toolbox)
        __self__.MenuBar.add_command(label="Help", 
                command=call_help)
        __self__.MenuBar.add_command(label="About", 
                command=__self__.call_author)
        __self__.derived_spectra.add_command(label="Summation", 
                command=__self__.call_summation)
        __self__.derived_spectra.add_command(label="Maximum Pixel Spectra (MPS)",
                command=__self__.call_mps)
        __self__.derived_spectra.add_command(label="Combined", 
                command=__self__.call_combined)
        __self__.Toolbox.add_command(label="Open samples database . . .", 
                command=__self__.list_samples)
        __self__.Toolbox.add_command(label="Reset sample", 
                command=__self__.reset_sample)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_command(label="Change samples folder . . .", 
                command=prompt_folder)
        __self__.Toolbox.add_command(label="Load file selection . . .",
                command=__self__.batch)
        __self__.Toolbox.add_command(label="Load h5 file . . .",
                command=__self__.h5loader)
        __self__.Toolbox.add_command(label="Convert spectra name . . .",
                command=__self__.converter)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_cascade(label="Derived spectra", menu=__self__.derived_spectra)
        __self__.Toolbox.add_command(label="Check calibration", 
                command=__self__.plot_calibration_curve)
        __self__.Toolbox.add_command(label="Verify calculated ROI", 
                command=__self__.plot_ROI)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_command(label="Map elements", 
                command=__self__.find_elements)
        __self__.Toolbox.add_command(label="Create Mosaic...", 
                command=__self__.open_mosaic)
        __self__.Toolbox.add_command(label="Load Mosaic...", 
                command=__self__.prompt_mosaic_load_file)
        __self__.Toolbox.add_command(label="Image Analyzer . . .", 
                command=__self__.open_analyzer)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_command(label="Settings", command=__self__.call_settings)
        __self__.Toolbox.add_command(label="Exit", command=__self__.root_quit)

        __self__.master.config(menu=__self__.MenuBar)
        
        #####
        # define the buttons which go inside the ButtonsFrame (top left corner)
        
        subx,suby = 1,1 #icon resize factor
        
        # load icons
        ButtonLoad_icon = PhotoImage(data=ICO_LOAD)
        __self__.ButtonLoad_icon = ButtonLoad_icon.subsample(subx,suby)
        ButtonReset_icon = PhotoImage(data=ICO_RESET)
        __self__.ButtonReset_icon = ButtonReset_icon.subsample(subx,suby)
        ImgAnalButton_icon = PhotoImage(data=ICO_IMGANAL)
        __self__.ImgAnalButton_icon = ImgAnalButton_icon.subsample(subx,suby)
        FindElementButton_icon = PhotoImage(data=ICO_RUBIK)
        __self__.FindElementButton_icon = FindElementButton_icon.subsample(subx,suby)
        QuitButton_icon = PhotoImage(data=ICO_QUIT)
        __self__.QuitButton_icon = QuitButton_icon.subsample(subx,suby)
        SettingsButton_icon = PhotoImage(data=ICO_SETTINGS)
        __self__.SettingsButton_icon = SettingsButton_icon.subsample(subx,suby)

        # create buttons
        __self__.ButtonLoad = Button(
                __self__.ButtonsFrame, 
                text="  Database", 
                anchor=W,
                image=__self__.ButtonLoad_icon, 
                bd=3, 
                compound=LEFT, 
                command=__self__.list_samples)
        __self__.ButtonLoad.grid(row=0,column=0, sticky=W+E)

        __self__.ButtonReset = Button(
                __self__.ButtonsFrame, 
                text="  Reset Sample", 
                anchor=W,
                image=__self__.ButtonReset_icon, 
                compound=LEFT, 
                bd=3, 
                command=__self__.reset_sample)
        __self__.ButtonReset.grid(row=0,column=1, sticky=W+E)

        __self__.ImgAnalButton = Button(
                __self__.ButtonsFrame, 
                text="  Image Analyzer", 
                anchor=W,
                image=__self__.ImgAnalButton_icon, 
                compound=LEFT, 
                bd=3, 
                command=__self__.open_analyzer)
        __self__.ImgAnalButton.grid(row=1,column=0, sticky=W+E)

        __self__.FindElementButton = Button(
                __self__.ButtonsFrame, 
                text="  Map Elements", 
                anchor=W,
                image=__self__.FindElementButton_icon, 
                compound=LEFT, 
                bd=3, 
                command=__self__.find_elements)
        __self__.FindElementButton.grid(row=1,column=1, sticky=W+E)

        __self__.QuitButton = Button(
                __self__.ButtonsFrame, 
                text="  Quit", 
                anchor=W,
                image=__self__.QuitButton_icon, 
                compound=LEFT, 
                bd=3, 
                command=__self__.root_quit)
        __self__.QuitButton.grid(row=2,column=1,sticky=W+E)

        __self__.SettingsButton = Button(
                __self__.ButtonsFrame, 
                text="  Settings", 
                anchor=W,
                image=__self__.SettingsButton_icon, 
                compound=LEFT, 
                bd=3, 
                command=__self__.call_settings)
        __self__.SettingsButton.grid(row=2,column=0,sticky=W+E)

        __self__.master.grid_columnconfigure(0,weight=1)
        
        #####

        __self__.SampleVar = StringVar()
        __self__.SampleVar.set("Sample on memory: "+Constants.DIRECTORY)
        __self__.StatusBar = Label(
                __self__.master, 
                textvariable=__self__.SampleVar,
                bd=1, 
                relief=SUNKEN, 
                anchor=W)
        __self__.StatusBar.grid(row=6, column=0, columnspan=6, sticky=W+E)

        __self__.master.protocol("WM_DELETE_WINDOW", __self__.root_quit)

    def magnify(__self__):
        __self__.magnified = PlotWin(__self__.master)
        __self__.magnified.draw_map()
        spawn_center(__self__.magnified.master)
            
    def write_stat(__self__):

        __self__.no_sample = True
        
        __self__.TableMiddle.config(state=NORMAL)
        __self__.TableLeft.config(state=NORMAL)
        __self__.SampleVar.set("Sample on memory: "+Constants.SAMPLE_PATH)
        
        # wipe all text
        __self__.StatusBox.delete(0,END)
        __self__.TableMiddle.delete(0,END)
        __self__.TableLeft.delete(0,END)
        
        if Constants.MY_DATACUBE != None and not os.path.exists(Constants.SAMPLE_PATH): 
            if os.path.exists(Constants.MY_DATACUBE.path):
                files = [f for f in os.listdir(Constants.MY_DATACUBE.path) \
                        if f.lower().endswith(".mca") or f.lower().endswith(".txt")]
                root.mcacount[Constants.DIRECTORY] = len(files)
                __self__.StatusBox.insert(END, "\nSpectra files folder:\n")
                __self__.StatusBox.insert(END,"{0}\n".format(Constants.MY_DATACUBE.path))
                __self__.StatusBox.insert(END,
                        "{0} spectra found!\n".format(root.mcacount[Constants.DIRECTORY]))
                __self__.StatusBox.insert(END, 
                        "\nDatacube loaded with {} spectra packed\n".format(
                            Constants.MY_DATACUBE.img_size))
                __self__.no_sample = False
            else:
                root.mcacount[Constants.DIRECTORY] = Constants.MY_DATACUBE.img_size
                __self__.StatusBox.insert(END, "\nSpectra files folder:\n")
                __self__.StatusBox.insert(END,"{0}\n".format(Constants.MY_DATACUBE.path))
                __self__.StatusBox.insert(END,
                        "Path doesn't exist, continuing with datacube information.")
                __self__.StatusBox.insert(END, 
                        "\nDatacube loaded with {} spectra packed\n".format(
                            Constants.MY_DATACUBE.img_size))
                __self__.no_sample = False

        elif os.path.exists(Constants.SAMPLE_PATH):
            if Constants.MY_DATACUBE != None:
                if os.path.exists(Constants.MY_DATACUBE.path):
                    files = [f for f in os.listdir(Constants.MY_DATACUBE.path) \
                            if f.lower().endswith(".mca") or f.lower().endswith(".txt")]
                    root.mcacount[Constants.DIRECTORY] = len(files)
                    __self__.StatusBox.insert(END, "\nSpectra files folder:\n")
                    __self__.StatusBox.insert(END,"{0}\n".format(Constants.MY_DATACUBE.path))
                    __self__.StatusBox.insert(END,
                            "{0} spectra found!\n".format(root.mcacount[Constants.DIRECTORY]))
                    __self__.StatusBox.insert(END,
                            "\nDatacube loaded with {} spectra packed\n".format(
                                Constants.MY_DATACUBE.img_size))
                    __self__.no_sample = False
                else:
                    root.mcacount[Constants.DIRECTORY] = Constants.MY_DATACUBE.img_size
                    __self__.StatusBox.insert(END, "\nSpectra files folder:\n")
                    __self__.StatusBox.insert(END,"{0}\n".format(Constants.MY_DATACUBE.path))
                    __self__.StatusBox.insert(END,
                            "Path doesn't exist, continuing with datacube information.")
                    __self__.StatusBox.insert(END,
                            "\nDatacube loaded with {} spectra packed\n".format(
                                Constants.MY_DATACUBE.img_size))
                    __self__.no_sample = False

                    if any("h5" in x for x in Constants.MY_DATACUBE.datatypes) and \
                            not os.path.exists(SpecRead.cube_path):
                    
                        ########################################
                        # WRITES THE CONFIGURATION TO SUBPANEL #
                        ########################################
                        values_cube, values_cfg, values_keys = [],[],[]
                        for key in Constants.MY_DATACUBE.config:
                            values_keys.append(str(key))
                            if key == "gain":
                                values_cube.append(str(int(float(
                                    Constants.MY_DATACUBE.config[key])*1000))+" eV")
                            elif key == "bg_settings" and \
                                    Constants.MY_DATACUBE.config[key] == []:
                                values_cube.append("Default values")
                            else:
                                values_cube.append(str(Constants.MY_DATACUBE.config[key]))
                        for item in range(len(values_cube)):
                            __self__.TableLeft.insert(END, "{}".format(values_keys[item]))
                            __self__.TableMiddle.insert(END, "{}".format(values_cube[item]))
                        __self__.no_sample = False
                        ########################################

            else: 
                files = [f for f in os.listdir(Constants.SAMPLE_PATH) \
                            if f.lower().endswith(".mca") or f.lower().endswith(".txt")]
                __self__.StatusBox.insert(END, "\nLooking for spectra files at:\n")
                __self__.StatusBox.insert(END,"{0}\n".format(Constants.SAMPLE_PATH))
                __self__.StatusBox.insert(END, 
                        "\n{} spectra found!\n".format(root.mcacount[Constants.DIRECTORY]))
                __self__.no_sample = False

        if os.path.exists(SpecRead.cube_path):

            cube_stats = os.stat(SpecRead.cube_path)
            cube_size = convert_bytes(cube_stats.st_size)
            __self__.StatusBox.insert(END,
                    "Datacube is compiled. Cube size: {0}".format(cube_size))
            __self__.StatusBox.insert(END,"Verifying packed elements...")
            
            packed_elements = Constants.MY_DATACUBE.check_packed_elements()
            if len(packed_elements) == 0: __self__.StatusBox.insert(END,"None found.")
            else: 
                for element in packed_elements:
                    __self__.StatusBox.insert(END,"Found a map for {0}".format(element))
            __self__.StatusBox.insert(END,"Done.")

            #######################################################################
            # write datacube configuration to panel 9  (see user manual for ref.) #
            #######################################################################

            values_cube, values_cfg, values_keys = [],[],[]
            for key in Constants.MY_DATACUBE.config:
                values_keys.append(str(key))
                if key == "gain":
                    values_cube.append(str(int(float(Constants.MY_DATACUBE.config[key])*1000))+" eV")
                elif key == "bg_settings" and Constants.MY_DATACUBE.config[key] == []:
                    values_cube.append("Default values")
                else:
                    values_cube.append(str(Constants.MY_DATACUBE.config[key]))
            for item in range(len(values_cube)):
                __self__.TableLeft.insert(END, "{}".format(values_keys[item]))
                __self__.TableMiddle.insert(END, "{}".format(values_cube[item]))

            #######################################################################
        
        elif __self__.no_sample == True:
            __self__.StatusBox.insert(END, "No sample configured!") 
            for key in Constants.CONFIG:
                __self__.TableLeft.insert(END,key)

        elif __self__.no_sample == False and root.temporaryh5 == "None": 
            print("Inserting keys")
            __self__.StatusBox.insert(END, "Datacube not compiled.") 
            __self__.StatusBox.insert(END, "Please compile the cube first.")
            for key in Constants.CONFIG:
                __self__.TableLeft.insert(END,key)
        else: pass

        __self__.TableLeft.config(state=DISABLED)
        __self__.TableMiddle.config(state=DISABLED)
        
       
    def reset_sample(__self__):
        
        def repack(__self__, sample):
            logger.warning("Cube {} and its output contents were erased!".format(sample))
            shutil.rmtree(SpecRead.output_path)
            try: x,y,tag_dimension_file = SpecRead.getdimension()
            except OSError as exception:
                tag_dimension_file = False
            if tag_dimension_file == True:
                try: 
                    os.remove(Constants.DIMENSION_FILE)
                    logger.warning("Custom image dimension was deleted.")
                except: raise PermissionError("Can't delete custom dimension file!")

            # clears all open plot windows
            try: __self__.summation.master.destroy()
            except: pass
            try: __self__.MPS.master.destroy()
            except: pass
            try: __self__.combined.master.destroy()
            except: pass

            load_cube()
            __self__.write_stat()
            __self__.toggle_(toggle='off')
            __self__.ResetWindow.grab_release()
            __self__.wipe()
            if __self__.mca_extension[sample] == "---": __self__.samples.pop(sample,None)
            elif __self__.mca_extension[sample] == ".h5": __self__.samples.pop(sample,None)
            __self__.list_samples()
            __self__.draw_map()
            __self__.ResetWindow.destroy()
            return

        if os.path.exists(SpecRead.cube_path):

            # creates dialogue to warn cube exists and promp to repack data
            __self__.ResetWindow = Toplevel(master=__self__.master)
            __self__.ResetWindow.title("Attention!")
            __self__.ResetWindow.resizable(False,False)
            LocalLabel = Label(__self__.ResetWindow, 
                    text="Resetting the sample will erase all files in the OUTPUT folder of sample {}! Are you sure you want to proceed?".format(
                        Constants.DIRECTORY),
                    padx=10, 
                    pady=4, 
                    wraplength=250)
            LocalLabel.pack()
            Erase_ico = PhotoImage(data=ICO_ERASE)
            __self__.Erase_ico = Erase_ico.zoom(2, 2)
            EraseLabel = Label(__self__.ResetWindow, image = __self__.Erase_ico).\
                    pack(side=LEFT, pady=8, padx=16)
            YesButton = Button(
                    __self__.ResetWindow, 
                    text="Yes", 
                    justify=CENTER,
                    command=lambda: repack(
                        __self__,Constants.MY_DATACUBE.config["directory"]),
                    width=10).pack(side=TOP,pady=5)
            NoButton = Button(
                    __self__.ResetWindow, 
                    text="No", 
                    justify=CENTER,
                    command=__self__.ResetWindow.destroy, 
                    width=10).pack(side=TOP, pady=5)
            
            place_center(__self__.master,__self__.ResetWindow)
            icon = os.path.join(os.getcwd(),"images","icons","icon.ico")
            __self__.ResetWindow.iconbitmap(icon)
            __self__.ResetWindow.grab_set()

        else:
            messagebox.showerror("Can't find sample!",
                    "Sample {} could not be located!".format(Constants.DIRECTORY))

    def call_configure(__self__):
        
        """ invokes the configuration dialog """

        try: 
            __self__.config_xy = SpecRead.getdimension()
        except:
            dimension = DimensionDiag(Constants.DIRECTORY)
            __self__.master.wait_window(dimension.win) 
            if dimension.exit_code == "cancel":
                __self__.wipe()
                return 0

        __self__.ManualParam = []
        try: __self__.ConfigDiag.master.destroy()
        except: pass
        __self__.ConfigDiag = ConfigDiag(__self__.master,
                matrix=np.zeros([1,1,1],dtype="int32"))
        __self__.ConfigDiag.build_widgets()
        

class ReConfigDiag:
    def __init__(__self__, master):
        __self__.master = Toplevel(master = master)
        __self__.master.grab_set()
        __self__.master.resizable(False,False)
        __self__.master.title("Cube Configuration")
        __self__.master.bind("<Escape>",__self__.kill)
        __self__.master.bind("<Return>",__self__.kill)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.Frame = Frame(__self__.master,padx=15,pady=15)
        __self__.Labels = Frame(__self__.master,padx=15,pady=15)
        __self__.MergeSettings = LabelFrame(__self__.master,padx=15,pady=15, 
                text="Merged Cube Settings:")
        __self__.MergeSettings.grid(row=1, column=0,columnspan=2)
        __self__.Frame.grid(row=0, column=1)
        __self__.Labels.grid(row=0, column=0)
        __self__.build_widgets()

    def get_version(__self__):
        """ version attribute was implemented in XISMuS 1.3.0,
        any cube prior to this version has no version attribute """

        if hasattr(Constants.MY_DATACUBE,"version"):
            if hasattr(Constants.MY_DATACUBE,"scalable"):
                version = [int(i) for i in Constants.MY_DATACUBE.version.split("v")[-1].split(".")]
                version[0] = version[0]*100
                version[1] = version[1]*10
                version[2] = version[2]*1
                version = sum(version)
                if version >= 130:
                    __self__.scale.config(state=DISABLED)
                    __self__.Label5.config(state=DISABLED)
        else:
            if hasattr(Constants.MY_DATACUBE,"scalable"):
                __self__.scale.config(state=NORMAL)
                __self__.Label5.config(state=NORMAL)
            else:
                __self__.scale.config(state=DISABLED)
                __self__.Label5.config(state=DISABLED)
    
    def build_widgets(__self__):
        Label2 = Label(__self__.Labels, text="Area method:")
        Label3 = Label(__self__.Labels, text="Enhance image?")
        Label4 = Label(__self__.Labels, text="Calculate ratios?")
        __self__.Label5 = Label(__self__.MergeSettings, text="Scale data? (for versions < 1.3)")
        __self__.Label6 = Label(__self__.MergeSettings, text="Re-calculate continuum?")
        
        Label2.grid(row=2,column=0,sticky=W,pady=2)
        Label3.grid(row=3,column=0,sticky=W,pady=2)
        Label4.grid(row=4,column=0,sticky=W,pady=2)
        __self__.Label5.grid(row=0,column=1,sticky=W,pady=2)
        __self__.Label6.grid(row=1,column=1,sticky=W,pady=2)
        
        ConfigDiagEnhanceYes = Label(__self__.Frame, text="Yes")
        ConfigDiagEnhanceYes.grid(row=3,column=1,sticky=E,pady=2)
        ConfigDiagRatioYes = Label(__self__.Frame, text="Yes")
        ConfigDiagRatioYes.grid(row=4,column=1,sticky=E,pady=2)

        __self__.BgstripVar = StringVar()
        __self__.DirectoryVar = StringVar()
        __self__.RatioVar = BooleanVar()
        __self__.EnhanceVar = BooleanVar()
        __self__.MethodVar = StringVar()
        __self__.ScaleVar = BooleanVar()
        __self__.ContVar = BooleanVar()
        __self__.DirectoryVar.set(Constants.MY_DATACUBE.config.get('directory'))
        __self__.BgstripVar.set(Constants.MY_DATACUBE.config.get('bgstrip'))
        __self__.RatioVar.set(Constants.MY_DATACUBE.config.get('ratio'))
        __self__.MethodVar.set(Constants.MY_DATACUBE.config.get('peakmethod'))
        __self__.EnhanceVar.set(Constants.MY_DATACUBE.config.get('enhance'))
        
        __self__.ConfigDiagRatio = Checkbutton(__self__.Frame, variable=__self__.RatioVar)
        
        __self__.ConfigDiagEnhance = Checkbutton(__self__.Frame, variable=__self__.EnhanceVar)
        
        __self__.ConfigDiagMethod = ttk.Combobox(
                __self__.Frame, 
                textvariable=__self__.MethodVar, 
                values=("simple_roi","auto_roi","auto_wizard"),
                state="readonly",
                width=13)
        
        __self__.ConfigDiagMethod.grid(row=2,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagEnhance.grid(row=3,column=0,sticky=E,pady=2)
        __self__.ConfigDiagRatio.grid(row=4,column=0,sticky=E,pady=2)
        
        dimension_text = "Image size = {0} x {1} pixels".format(
                Constants.MY_DATACUBE.dimension[0],
                Constants.MY_DATACUBE.dimension[1])
        img_dimension_display = Label(__self__.master,text=dimension_text)
        img_dimension_display.grid(row=2,column=0,sticky=W,padx=17,pady=2)
        
        __self__.scale = Checkbutton(__self__.MergeSettings, variable=__self__.ScaleVar)
        __self__.cont = Checkbutton(__self__.MergeSettings, variable=__self__.ContVar)
        __self__.scale.grid(row=0,column=0)
        __self__.cont.grid(row=1,column=0)

        ButtonsFrame = Frame(__self__.master)
        ButtonsFrame.grid(row=5,columnspan=2,pady=10,padx=10)
        SaveButton = Button(
                ButtonsFrame, 
                text="Save", 
                justify=CENTER, 
                width=10,
                command=__self__.save)
        SaveButton.grid(row=5,column=0,sticky=S)
        CancelButton = Button(
                ButtonsFrame, 
                text="Cancel", 
                justify=CENTER, 
                width=10,
                command=__self__.kill)
        CancelButton.grid(row=5,column=1,sticky=S)

        if hasattr(Constants.MY_DATACUBE,"scalable"):
            __self__.toggle("on")
            __self__.ScaleVar.set(Constants.MY_DATACUBE.scalable)
        else: __self__.toggle("off")
        __self__.get_version()

        place_center(root.master,__self__.master)
        icon = os.path.join(os.getcwd(),"images","icons","refresh.ico")
        __self__.master.iconbitmap(icon)
        root.master.wait_window(__self__.master)

    def save(__self__):
        Constants.MY_DATACUBE.config["enhance"] = __self__.EnhanceVar.get()
        Constants.MY_DATACUBE.config["peakmethod"] = __self__.MethodVar.get()
        Constants.MY_DATACUBE.config["ratio"] = __self__.RatioVar.get()

        if hasattr(Constants.MY_DATACUBE,"scalable"):

            recalculatedbg = False
            ##############################
            # Reclaculates the bg matrix #
            ##############################

            if __self__.ContVar.get() == True:
                bar = Busy(Constants.MY_DATACUBE.img_size,0)
                bar.update_text("Stripping background")
                Constants.MY_DATACUBE.strip_background(
                        bgstrip=Constants.MY_DATACUBE.config["bgstrip"],
                        recalculating=True,
                        progressbar=bar)
                bar.destroybar()
                recalculatedbg = True

                ##############################

                #####################################
                # Rebuilds all datacube information #
                #####################################

                Constants.MY_DATACUBE.MPS(Constants.MY_DATACUBE.mps)
                Constants.MY_DATACUBE.stacksum()
                Constants.MY_DATACUBE.write_sum()
                Constants.MY_DATACUBE.create_densemap()
                #####################################

            ###############################################################################
            # Apply scaling (if needed) to the densemap to display properly on main panel #
            ###############################################################################


            if recalculatedbg:
                if Constants.MY_DATACUBE.scalable and __self__.ScaleVar.get():
                    Constants.MY_DATACUBE.matrix = Constants.MY_DATACUBE.matrix.astype(
                            "float32")
                    Constants.MY_DATACUBE.densitymap = apply_scaling(
                            Constants.MY_DATACUBE, Constants.MY_DATACUBE.densitymap, 1)
                    Constants.MY_DATACUBE.matrix = Constants.MY_DATACUBE.matrix.astype("int32")
                elif Constants.MY_DATACUBE.scalable and not __self__.ScaleVar.get():
                    Constants.MY_DATACUBE.scalable = __self__.ScaleVar.get()
                    # NOTE: densemap already modified by create_densemap() function #
                    pass
            else:
                if Constants.MY_DATACUBE.scalable == False and __self__.ScaleVar.get():
                    Constants.MY_DATACUBE.scalable = __self__.ScaleVar.get()
                    Constants.MY_DATACUBE.matrix = Constants.MY_DATACUBE.matrix.astype(
                            "float32")
                    Constants.MY_DATACUBE.densitymap = apply_scaling(
                            Constants.MY_DATACUBE,
                            Constants.MY_DATACUBE.densitymap, 1)
                    Constants.MY_DATACUBE.matrix = Constants.MY_DATACUBE.matrix.astype("int32")
                elif Constants.MY_DATACUBE.scalable and not __self__.ScaleVar.get():
                    Constants.MY_DATACUBE.scalable = __self__.ScaleVar.get()
                    Constants.MY_DATACUBE.matrix = Constants.MY_DATACUBE.matrix.astype(
                            "float32")
                    Constants.MY_DATACUBE.densitymap = apply_scaling(
                            Constants.MY_DATACUBE, Constants.MY_DATACUBE.densitymap, -1)
                    Constants.MY_DATACUBE.matrix = Constants.MY_DATACUBE.matrix.astype("int32")

            ###############################################################################

            root.draw_map()

        if "mca" in Constants.MY_DATACUBE.datatypes:
            Constants.MY_DATACUBE.save_cube()
        root.write_stat()
        __self__.kill()

    def toggle(__self__,mode):
        if mode == "on":
            __self__.scale.config(state=NORMAL)
            __self__.cont.config(state=NORMAL)
            __self__.Label5.config(state=NORMAL)
            __self__.Label6.config(state=NORMAL)
        elif mode == "off":
            __self__.scale.config(state=DISABLED)
            __self__.cont.config(state=DISABLED)
            __self__.Label5.config(state=DISABLED)
            __self__.Label6.config(state=DISABLED)

    def kill(__self__):
        __self__.master.destroy()


class ConfigDiag:
    def __init__(__self__, master, matrix=None):
        __self__.master = Toplevel(master = master)
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
        if __self__.CalibVar.get() == 'manual':
            __self__.manual_calib()
        else: __self__.save_config()

    def save_param(__self__):
        EntryParam = [
                [__self__.ch1.get(),__self__.en1.get()],
                [__self__.ch2.get(),__self__.en2.get()],
                [__self__.ch3.get(),__self__.en3.get()],
                [__self__.ch4.get(),__self__.en4.get()]]
        for index in range(len(EntryParam)):
            if EntryParam[index][0] > 0 and EntryParam[index][1] > 0:
                root.ManualParam.append(EntryParam[index])
            elif EntryParam[index][0] < 0 or EntryParam[index][1] < 0:
                messagebox.showerror("Calibration Error",
                        "Can't receive negative values!")
                __self__.CalibDiag.focus_set()
                root.ManualParam = []
                raise ValueError("Manual calibration can't receive negative values!")
        __self__.CalibDiag.grab_release()
        __self__.save_config()
    
    def wipe(__self__,e=""):

        try: 
            __self__.master.grab_release()
            __self__.master.destroy()
        except: pass

        #############################################################
        # WHEN SELECTING ANOTHER ITEM AND A TEMPORARY H5 IS LOADED, #
        # GET RID OF IT                                             #
        #############################################################
        try: #because there could be no datacube loaded previously (MY_DATACUBE = None)
            if Constants.CONFIG["directory"] == root.temporaryh5:

                ##################################################
                # Update status boxes without using write_stat() #
                ##################################################
                root.TableMiddle.config(state=NORMAL)
                root.TableMiddle.delete(0,END)
                root.StatusBox.delete(0,END)
                root.StatusBox.insert(END,
                        "Aborted configuration of {}{}".format(
                            Constants.CONFIG["directory"],root.mca_extension[Constants.CONFIG["directory"]]))
                root.StatusBox.insert(END, 
                        "Spectra count: {}".format(
                            root.mcacount[Constants.CONFIG["directory"]]))
                root.TableMiddle.config(state=DISABLED)
                root.TableMiddle.update_idletasks()
                root.StatusBox.update_idletasks()
                print("Wiped configuration subpanels")
                ##################################################

                del root.samples[Constants.CONFIG["directory"]]
                del root.samples_path[Constants.CONFIG["directory"]]
                del root.mcacount[Constants.CONFIG["directory"]]
                del root.mca_indexing[Constants.CONFIG["directory"]]
                del root.mca_extension[Constants.CONFIG["directory"]]
                root.temporaryh5 = "None"
                gc.collect()
                try:
                    __self__.SamplesWindow_TableRight.config(state=NORMAL)
                    __self__.SamplesWindow_TableRight.delete(temph5_idx)
                    __self__.SamplesWindow_TableLeft.delete(temph5_idx)
                    __self__.SamplesWindow_TableRight.config(state=DISABLED)
                    __self__.SamplesWindow_TableRight.update_idletasks()
                except: pass
                temp_path = os.path.join(
                    SpecRead.__PERSONAL__,"output",Constants.CONFIG["directory"])
                if os.path.exists(temp_path):
                    shutil.rmtree(temp_path)
                Constants.MY_DATACUBE = None
                gc.collect()
                load_cube()
                root.draw_map()
                root.toggle_(toggle="off")
                root.SampleVar.set("Sample on memory: None")
                try:
                    if root.SamplesWindow.state() == "normal":
                        root.SamplesWindow.deiconify()
                        root.SamplesWindow_TableLeft.focus_set()
                except: pass
                return
        except: pass

        Constants.MY_DATACUBE = None
        root.h5path = "None"
        gc.collect()
        if isinstance(root.samples[Constants.CONFIG["directory"]],tuple):
            root.samples.pop(Constants.CONFIG["directory"])
        load_cube()
        root.write_stat()
        root.draw_map()
        root.toggle_(toggle="off")
        root.SampleVar.set("Sample on memory: None")
        try: 
            if root.SamplesWindow.state() == "normal": 
                root.SamplesWindow.deiconify()
                root.SamplesWindow_TableLeft.focus_set()
        except: pass

    def manual_calib(__self__):
        
        __self__.CalibDiag = Toplevel(master = __self__.master)
        __self__.CalibDiag.title("Manual configuration")
        __self__.CalibDiag.resizable(False,False)
        __self__.CalibDiag.protocol("WM_DELETE_WINDOW",__self__.focus_grab)
        __self__.CalibDiag.grab_set()
        icon = ".\\images\\icons\\settings.ico"
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
            Constants.CONFIG['calibration'] = 'manual'
            calibparam = SpecRead.getcalibration()
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
        
        OkButton = Button(ButtonFrame,text="SAVE",command=__self__.save_param).grid(
                row=5,columnspan=2)
        
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

    def focus_grab(__self__):
        __self__.master.focus_set()
        __self__.master.grab_set()

    def save_config(__self__,e=""):

        """ A workaround to always have Training Data in samples list and working, is
        backing up the samples_folder variable, changing it temporarily to compile the 
        Training Data datacube and then set it back so the other samples can be compiled
        properly """

        samples_folder_backup = copy.deepcopy(Constants.SAMPLES_FOLDER)
        if __self__.DirectoryVar.get() == "Training Data 1" or\
                __self__.DirectoryVar.get() == "Training Data 2":
            Constants.SAMPLES_FOLDER = os.path.join(SpecRead.__PERSONAL__,"Example Data")
        
        ##########################################################
            
        configdict = {"directory":__self__.DirectoryVar.get(),
                "bgstrip":__self__.BgstripVar.get(),
                "ratio":__self__.RatioVar.get(),
                "calibration":__self__.CalibVar.get(),
                "enhance":__self__.EnhanceVar.get(),
                "peakmethod":__self__.MethodVar.get(),
                "bg_settings":root.snip_config}
        
        if not os.path.exists(SpecRead.output_path):
            try:
                os.mkdir(SpecRead.output_path)
            except IOError as exception:
                logger.warning("Error {}.".format(exception.__class__.__name__))
                logger.warning("Can't create output folder {}".format(SpecRead.output_path))
                if exception.__class__.__name__ == "FileExistsError": 
                    exists = "Folder already exists!"
                else: exists = None
                messagebox.showerror("{}".format(exception.__class__.__name__),
                        "Cannot create output folder {}\n{}".format(
                            SpecRead.output_path, exists))
                root.write_stat()
                root.draw_map()
                return
            if not os.path.exists(Constants.DIMENSION_FILE):
                dm_file = open(os.path.join(SpecRead.output_path,"colonneXrighe.txt"),"w")
                dm_file.write("righe\t{}\n".format(root.config_xy[0]))
                dm_file.write("colonne\t{}\n".format(root.config_xy[1]))
                dm_file.write(5*"*"+" user input data "+5*"*")
                dm_file.close()
        
        if os.path.exists(root.samples_path[Constants.DIRECTORY])\
                or isinstance(root.samples[configdict["directory"]],tuple):
            Constants.DIRECTORY = configdict["directory"]
            #Constants.SAMPLE_PATH = os.path.join(Constants.SAMPLES_FOLDER, 
            #        Constants.DIRECTORY)
            Constants.SAMPLE_PATH = root.samples_path[configdict["directory"]]
            if not isinstance(root.samples[configdict["directory"]],tuple):
                Constants.FIRSTFILE_ABSPATH = os.path.join(Constants.SAMPLE_PATH,
                    root.samples[configdict["directory"]]+\
                    root.mca_indexing[configdict["directory"]]+\
                    "."+root.mca_extension[configdict["directory"]])

            # reads configuration integrity prior opening config.cfg for writing
            if configdict['calibration'] == 'manual': 
                calibparam = root.ManualParam
                # save_config only passes positive integers forward
                # in the case other data is received as user input, this will be filtered
                # absence of acceptable parameters returns an empty list
                if calibparam == []: 
                    messagebox.showerror("Calibration Error",
                            "No acceptable parameters passed!")
                    __self__.CalibDiag.focus_set()
                    root.ManualParam = []
                    raise ValueError("No acceptable parameters passed!")
                elif len(calibparam) <= 1: 
                    messagebox.showerror("Calibration Error",
                            "Need at least two anchors!")
                    __self__.CalibDiag.focus_set()
                    root.ManualParam = []
                    raise ValueError("Calibration need at least two anchors!")
            else: 
                Constants.CONFIG["calibration"] = "from_source"
                calibparam = SpecRead.getcalibration()

            cfgpath = os.path.join(SpecRead.__PERSONAL__,"bin","config.cfg")
            cfgfile = open(cfgpath,"w+")
            cfgfile.write("<<CONFIG_START>>\r")
            for key in configdict:
                cfgfile.write("{} = {}\r".format(key,configdict[key]))
            cfgfile.write("<<CALIBRATION>>\r")
            for pair in calibparam:
                cfgfile.write("{0}\t{1}\r".format(pair[0],pair[1]))
            cfgfile.write("<<END>>\r")
            cfgfile.close()
            
            SpecRead.setup(root.samples[configdict["directory"]],
                    root.mca_indexing[configdict["directory"]],
                    root.mca_extension[configdict["directory"]])
            __self__.master.grab_release()
            __self__.master.destroy()
            try: __self__.CalibDiag.destroy()
            except: pass
            try: root.ResetWindow.destroy()
            except: pass
             
            call_compilecube()
            load_cube()
            root.write_stat()
            root.draw_map()
            root.toggle_(toggle='on')

        else:
            cfgpath = os.path.join(SpecRead.__PERSONAL__,"bin","config.cfg")
            cfgfile = open(cfgpath,'w+')
            cfgfile.write("<<CONFIG_START>>\r")
            for key in configdict:
                cfgfile.write("{} = {}\r".format(key,configdict[key]))
            cfgfile.write("<<CALIBRATION>>\r")
            
            if configdict['calibration'] == 'manual': 
                calibparam = root.ManualParam
            else: 
                calibparam = [[0,0],[0,0],[0,0]]

            for pair in calibparam:
                cfgfile.write("{0}\t{1}\r".format(pair[0],pair[1]))
            cfgfile.write("<<END>>\r")
            cfgfile.close()
            messagebox.showerror("Directory not found!",
                    "Directory {} not found!\nConfig.cfg saved!".format(
                        configdict['directory']))
            SpecRead.setup(root.samples[configdict["directory"]],
                    root.mca_indexing[configdict["directory"]],
                    root.mca_extension[configdict["directory"]])
            __self__.master.grab_release()
            __self__.master.destroy()
            try: root.ResetWindow.destroy()
            except: pass
            try: __self__.CalibDiag.destroy()
            except: pass
            root.write_stat()
            root.draw_map()
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
        __self__.ConfigDiagRatio = Checkbutton(__self__.Frame, variable=__self__.RatioVar)
        
        __self__.ConfigDiagSetBG = Button(__self__.Frame, text="Set BG",
               width=13+ConfigDiagRatioYes.winfo_width(),command=__self__.call_PeakClipper)
        
        __self__.CalibVar = StringVar()
        __self__.ConfigDiagCalib = ttk.Combobox(
                __self__.Frame, 
                textvariable=__self__.CalibVar, 
                values=("from_source","manual"),
                state="readonly",width=13+ConfigDiagRatioYes.winfo_width())

        __self__.EnhanceVar = BooleanVar()
        
        __self__.MethodVar = StringVar()
        __self__.ConfigDiagMethod = ttk.Combobox(
                __self__.Frame, 
                textvariable=__self__.MethodVar, 
                values=("simple_roi","auto_roi","auto_wizard"),
                state="readonly",
                width=13+ConfigDiagRatioYes.winfo_width())
        
        __self__.DirectoryVar.set(Constants.CONFIG.get('directory'))
        __self__.BgstripVar.set(Constants.CONFIG.get('bgstrip'))
        __self__.RatioVar.set(Constants.CONFIG.get('ratio'))
        __self__.CalibVar.set(Constants.CONFIG.get('calibration'))
        __self__.MethodVar.set(Constants.CONFIG.get('peakmethod'))
        __self__.EnhanceVar.set(Constants.CONFIG.get('enhance'))

        __self__.ConfigDiagBgstrip.grid(row=1,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagSetBG.grid(row=2,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagCalib.grid(row=3,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagMethod.grid(row=6,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagRatio.grid(row=7,column=0,sticky=E,pady=2)
        
        dimension_text = "Image size = {0} x {1} pixels".format(
                root.config_xy[0],root.config_xy[1])
        img_dimension_display = Label(__self__.master,text=dimension_text)
        img_dimension_display.grid(row=1,column=0,sticky=W,padx=17,pady=2)

        ButtonsFrame = Frame(__self__.master)
        ButtonsFrame.grid(row=8,columnspan=2,pady=10,padx=10)
        SaveButton = Button(
                ButtonsFrame, 
                text="Save", 
                justify=CENTER, 
                width=10,
                command=__self__.check_method_and_save)
        SaveButton.grid(row=8,column=0,sticky=S)
        CancelButton = Button(
                ButtonsFrame, 
                text="Cancel", 
                justify=CENTER, 
                width=10,
                command=__self__.wipe)
        CancelButton.grid(row=8,column=1,sticky=S)
        
        place_center(root.master,__self__.master)
        icon = os.path.join(os.getcwd(),"images","icons","settings.ico")
        __self__.master.iconbitmap(icon)
        root.master.wait_window(__self__.master)


class ImgageOperationOutput:
    def __init__(__self__,image,el1,el2,operation,cube_datatypes):
        __self__.image = image
        __self__.master = Toplevel(master=root.master)
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
        __self__.upper.pack(side=TOP, expand=True, fill=BOTH)#, padx=(16,16),pady=(16,16))
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
        __self__.plot.imshow(image, vmin=0, vmax=LEVELS, cmap=Constants.COLORMAP)
        spawn_center(__self__.master)

    def replace_on_cube(__self__,image,element):
        p = messagebox.askquestion("Warning!","You are about to replace {} map in your datacube with the output image. This operation is irreversible. Do you want to proceed?".format(element))
        if p =="yes":
            Constants.MY_DATACUBE.replace_map(image,element)
            return
        else: 
            __self__.master.focus_set()
            return

    def save_image(__self__,image):
        f = filedialog.asksaveasfile(mode='w',
                        defaultextension=".png",
                        filetypes=[("Portable Network Graphic", "*.png")],
                        title="Save as...")
        if f is not None: 
            from ImgMath import write_image
            write_image(image,
                Constants.TARGET_RES,
                f.name,
                enhance=Constants.MY_DATACUBE.config["enhance"],
                save=True)
        else: 
            __self__.master.focus_set()
            return

    def wipe_plot(__self__):
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
        __self__.master.geometry("380x320")
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
        __self__.ok = Button(__self__.master,text="OK",width=13,
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

        from ImgMath import subtract as sub_
        from ImgMath import add as add_

        if __self__.mode == "subtract": 
            operation = "minus"
            output = sub_(__self__.parent.newimage1,
                    __self__.parent.newimage2,norm=True)
        elif __self__.mode == "add":
            operation = "plus"
            output = add_(__self__.parent.newimage1,
                    __self__.parent.newimage2,norm=True)
        else: pass
        if __self__.scaled:
            apply_scaling(__self__.parent.DATACUBE, output, -1)
        ImgageOperationOutput(output,__self__.parent.Map1Var.get(),
                __self__.parent.Map2Var.get(),operation, __self__.parent.DATACUBE.datatypes)
        __self__.master.grab_release()
        __self__.master.destroy()


class PeriodicTable:
    # Creates the periodic table and starts find_elements module from Mapping.py
    def __init__(__self__,parent):
        __self__.master = Toplevel(parent.master)
        __self__.master.tagged = True
        __self__.master.title("Periodic Table of Elements")
        __self__.master.resizable(False,False)
        __self__.master.header = Label(__self__.master, text="Periodic Table of Elements.")
        __self__.master.header.grid(row=0,column=0, columnspan=18)
        __self__.master.body = Frame(__self__.master)
        __self__.master.body.grid(
                row=1,column=0, 
                rowspan=9, columnspan=18,
                padx=(3,3),pady=(3,0))
        __self__.master.footer = Frame(__self__.master)
        __self__.master.footer.grid(row=10,column=0, columnspan=18)
        __self__.cvar1 = DoubleVar()
        __self__.cvar2 = DoubleVar()
        __self__.cvar1.set(0.0)
        __self__.cvar2.set(0.5)
        __self__.draw_buttons() 
        icon = os.path.join(os.getcwd(),"images","icons","rubik.ico")
        place_center(parent.master,__self__.master)
        __self__.master.iconbitmap(icon)
    
    def auto(__self__,elements):

        def reload_cube():
            load_cube()
            __self__.master.grab_release()
            __self__.master.destroy()

        #####################################################################
        # give attribute to avoid lambda function and call this list in run #
        #####################################################################
        __self__.elements = elements
        #####################################################################
        
        #########################################################
        # disable detected elements and change the "run" button #
        #########################################################

        __self__.master.grab_set()
        __self__.master.protocol("WM_DELETE_WINDOW",reload_cube)
        for btn in __self__.master.body.children.values():
                   
            if btn["text"] in elements:
                __self__.add_element(btn)
                btn.config(state=DISABLED)
                btn.config(bg="limegreen")
            if "Custom" in btn["text"]: btn.config(state=DISABLED)
        __self__.low.config(state=DISABLED)
        __self__.high.config(state=DISABLED)

        for btn in __self__.master.footer.children.values():
            if btn["text"] == "Map selected elements!":
                btn.destroy()
                __self__.go = Button(
                        __self__.master.footer, 
                        text="Run wizard!",
                        relief='raised',
                        fg="white",bg="blue",
                        command= __self__.save_and_run_wizard)
                __self__.go.grid(column=7,columnspan=3,pady=(6,3))

        #########################################################

        __self__.master.focus_set()
        
        return 

    def save_and_run_wizard(__self__):
        
        for i in __self__.elements: Constants.FIND_ELEMENT_LIST.remove(i)
        __self__.elements = [ElementList.index(i) for i in Constants.FIND_ELEMENT_LIST]
        logger.info("Elements to add to wizard: {}".format(__self__.elements))
        __self__.master.grab_release()
        __self__.master.destroy()
        start_time = time.time()

        save_path = os.path.join(SpecRead.output_path,"peak_find.png")
        if Constants.MULTICORE == True and \
                Constants.CPUS>1 and \
                Constants.MY_DATACUBE.img_size > 400:
            root.Fitter.locate_peaks(add_list=__self__.elements,path=save_path)
            root.Fitter.launch_workers(
                            Constants.FIT_CYCLES,
                            Constants.SAVE_INTERVAL,
                            Constants.SAVE_FIT_FIGURES)
        else:
            root.Fitter.locate_peaks(add_list=__self__.elements,path=save_path)
            root.Fitter.run_fit()

        root.bar = Busy(1,0)
        root.bar.update_text("Building images...")
        del root.Fitter

        build_images(SpecRead.output_path,bar=root.bar)

        timestamps = open(os.path.join(SpecRead.__BIN__,"timestamps.txt"),"a")
        timestamps.write(
                "\n{4} - {5} WIZARD\n{0} bgtrip={1} enhance={2}\n{3} seconds\n".format(
            __self__.elements,
            Constants.MY_DATACUBE.config["bgstrip"],
            Constants.MY_DATACUBE.config["enhance"],
            time.time()-start_time,
            time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            Constants.MY_DATACUBE.name))
        timestamps.close()

        wipe_list()
        root.toggle_(toggle="on")
        root.MenuBar.entryconfig("Toolbox", state=NORMAL)
        root.ButtonLoad.config(state=NORMAL)
        root.write_stat()
        refresh_plots()

    
    def add_element(__self__,toggle_btn):
        if toggle_btn.config('relief')[-1] == 'sunken':
            toggle_btn.config(relief="raised")
            toggle_btn.config(bg=Constants.DEFAULTBTN_COLOR)
            Constants.FIND_ELEMENT_LIST.remove(toggle_btn.cget("text"))
            refresh_plots()
        else:
            toggle_btn.config(relief="sunken")
            toggle_btn.config(bg="yellow")
            Constants.FIND_ELEMENT_LIST.append(toggle_btn.cget("text"))
            refresh_plots()
    
    def add_custom_element(__self__,toggle_btn):
        if toggle_btn.config('relief')[-1] == 'sunken':
            toggle_btn.config(relief="raised")
            toggle_btn.config(bg=Constants.DEFAULTBTN_COLOR)
            Constants.FIND_ELEMENT_LIST.remove("custom")
            plottables_dict["custom"] = []
            refresh_plots()
        else:
            # setting casual number
            toggle_btn.config(relief="sunken")
            toggle_btn.config(bg="yellow")
            Constants.FIND_ELEMENT_LIST.append("custom")
            plottables_dict["custom"] = [__self__.cvar1.get(),__self__.cvar2.get()]
            refresh_plots()
     
    def save_and_run(__self__,mode=None):
        
        try: cube_status = os.stat(SpecRead.cube_path)
        except: 
            try: cube_status = os.stat(root.h5path)
            except:
                messagebox.showerror("Error","No datacube found! Cannot proceed.")
                return
        mode = Constants.MY_DATACUBE.config["peakmethod"]
        if mode == "auto_wizard": 
            __self__.master.destroy()
            return 0
        if not Constants.FIND_ELEMENT_LIST: 
            __self__.master.destroy()
            messagebox.showinfo("Error", "No element input!")
        else:
            # disabled widgets to avoid user changes sample
            root.toggle_(toggle="off")
            try: root.SamplesWindow.destroy()
            except: pass

            # Sets fano and noise factor 
            if not hasattr(Constants.MY_DATACUBE,"FN"):
                FANO,NOISE = 0.114, 80
                logger.warning("Datacube has no attribute FN, using default FANO and NOISE")
            else:
                FANO, NOISE = Constants.MY_DATACUBE.FN
            FN_set(FANO, NOISE)
            print("These are FANO and NOISE: {} {}".format(FANO,NOISE))

            root.MenuBar.entryconfig("Toolbox", state=DISABLED)
            root.ButtonLoad.config(state=DISABLED)
            for widget in __self__.master.body.winfo_children():
                try: widget.config(state=DISABLED)
                except: pass
            __self__.go.config(state=DISABLED)
            
            cube_size = cube_status.st_size
            sys_mem = dict(virtual_memory()._asdict())
            rnt_mem = [(cube_size*len(Constants.FIND_ELEMENT_LIST)),sys_mem["available"]]
            process_memory = (convert_bytes(rnt_mem[0]),convert_bytes(rnt_mem[1]))
            needed_memory = cube_size*len(Constants.FIND_ELEMENT_LIST)
            
            # multi-core mode
            if Constants.MY_DATACUBE.config["peakmethod"] != "simple_roi":
                if "custom" in Constants.FIND_ELEMENT_LIST: 
                    results = []
                    Constants.FIND_ELEMENT_LIST.remove("custom") 
                    lines = [__self__.cvar1.get(),__self__.cvar2.get()]
                    elmap, ROI = (grab_simple_roi_image(Constants.MY_DATACUBE,lines,\
                            custom_energy=True))
                    results.append((elmap, ROI, "custom"))
                    digest_results(Constants.MY_DATACUBE,results,["custom"])

                if len(Constants.FIND_ELEMENT_LIST) > 2 \
                        and Constants.MY_DATACUBE.img_size > 999\
                        and Constants.MULTICORE == True:
                    
                    max_copies = 0 #as many copies as cores available
                    if needed_memory > root.RAM_limit_value:
                        max_copies = 1
                        while cube_size*max_copies < root.RAM_limit_value:
                            max_copies += 1
                    elif needed_memory > sys_mem["available"]:
                        max_copies = 1
                        while cube_size*max_copies < sys_mem["available"]:
                            max_copies += 1
                    if max_copies == 1:
                        # if only one copy can be made, it's pointless to run multicore
                        MAPS = getpeakmap(Constants.FIND_ELEMENT_LIST,Constants.MY_DATACUBE)
                    else:
                        cuber = Cube_reader(Constants.MY_DATACUBE.matrix,
                                Constants.MY_DATACUBE.energyaxis,
                                Constants.MY_DATACUBE.background,
                                Constants.MY_DATACUBE.config,
                                Constants.FIND_ELEMENT_LIST,
                                max_copies)
                        FANO, NOISE = Constants.MY_DATACUBE.FN
                        TOLERANCE = Constants.SETROI_TOLERANCE
                        results, aborted = cuber.start_workers(FANO, NOISE, TOLERANCE)
                        if not aborted:
                            cuber.p_bar.update_text("Digesting results...")
                            results = sort_results(results,Constants.FIND_ELEMENT_LIST)
                            digest_results(
                                    Constants.MY_DATACUBE,
                                    results,
                                    Constants.FIND_ELEMENT_LIST)
                        cuber.p_bar.destroybar()
                        del cuber

                # single-core mode
                else: 
                    if len(Constants.FIND_ELEMENT_LIST) > 0:
                        MAPS = getpeakmap(Constants.FIND_ELEMENT_LIST,Constants.MY_DATACUBE)
                    else: pass

            else:
                __self__.progress = Busy(len(Constants.FIND_ELEMENT_LIST),0)
                results = []
                partialtimer = time.time()
                iterator = 0
                for element in Constants.FIND_ELEMENT_LIST:
                    iterator += 1
                    __self__.progress.update_text(
                            "Grabbing element {}...".format(element))
                    __self__.progress.updatebar(iterator)

                    if element == "custom":
                        lines = [__self__.cvar1.get(),__self__.cvar2.get()]
                        elmap, ROI = (grab_simple_roi_image(Constants.MY_DATACUBE,lines,\
                                custom_energy=True))
                        results.append((elmap, ROI, "custom"))
                    else:
                        lines = select_lines(element,Constants.MY_DATACUBE.config["ratio"])
                        elmap, ROI = (grab_simple_roi_image(Constants.MY_DATACUBE,lines))
                        results.append((elmap, ROI, element))
                __self__.progress.update_text("Sorting...")
                sort_results(results,Constants.FIND_ELEMENT_LIST)
                __self__.progress.update_text("Digesting maps...")
                digest_results(Constants.MY_DATACUBE,results,Constants.FIND_ELEMENT_LIST)
                logger.info("Finished iteration process for element(s) {0}".format(
                    Constants.FIND_ELEMENT_LIST))
                __self__.progress.destroybar()
                del __self__.progress
                gc.collect()

                timestamp = time.time() - partialtimer
                logger.info("Execution took %s seconds" % (timestamp))
                timestamps = open(os.path.join(SpecRead.__BIN__,"timestamps.txt"),"a")
                timestamps.write("\n{5} - {7}\nbgtrip={1} enhance={2} peakmethod={3}\t\n{6} elements\n{4} seconds\n".format(
                    Constants.FIND_ELEMENT_LIST,
                    Constants.MY_DATACUBE.config["bgstrip"],
                    Constants.MY_DATACUBE.config["enhance"],
                    Constants.MY_DATACUBE.config["peakmethod"],
                    timestamp,
                    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                    len(Constants.FIND_ELEMENT_LIST),
                    Constants.MY_DATACUBE.name))
                logger.info("Finished map acquisition!")

            # reactivate widgets
            wipe_list()
            root.toggle_(toggle="on")
            root.MenuBar.entryconfig("Toolbox", state=NORMAL)
            root.ButtonLoad.config(state=NORMAL)
            root.write_stat()
            refresh_plots()
            gc.collect()

    def draw_buttons(__self__):
        btnsize_w = 3
        btnsize_h = 1
        __self__.H = Button(__self__.master.body, text="H",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.H))
        Constants.DEFAULTBTN_COLOR = __self__.H.cget("background")
        __self__.H.grid(row=0,column=0)
        __self__.He = Button(__self__.master.body, text="He",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.He))
        __self__.He.grid(row=0,column=17)
        __self__.Li = Button(__self__.master.body, text="Li",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Li))
        __self__.Li.grid(row=1,column=0)
        __self__.Be = Button(__self__.master.body, text="Be",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Be))
        __self__.Be.grid(row=1,column=1)
        __self__.B = Button(__self__.master.body, text="B",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.B))
        __self__.B.grid(row=1,column=12)
        __self__.C = Button(__self__.master.body, text="C",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.C))
        __self__.C.grid(row=1,column=13)
        __self__.N = Button(__self__.master.body, text="N",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.N))
        __self__.N.grid(row=1,column=14)
        __self__.O = Button(__self__.master.body, text="O",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.O))
        __self__.O.grid(row=1,column=15)
        __self__.F = Button(__self__.master.body, text="F",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.F))
        __self__.F.grid(row=1,column=16)
        __self__.Ne = Button(__self__.master.body, text="Ne",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ne))
        __self__.Ne.grid(row=1,column=17)
        __self__.Na = Button(__self__.master.body, text="Na",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Na))
        __self__.Na.grid(row=2,column=0)
        __self__.Mg = Button(__self__.master.body, text="Mg",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Mg))
        __self__.Mg.grid(row=2,column=1)
        __self__.Al = Button(__self__.master.body, text="Al",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Al))
        __self__.Al.grid(row=2,column=12)
        __self__.Si = Button(__self__.master.body, text="Si",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Si))
        __self__.Si.grid(row=2,column=13)
        __self__.P = Button(__self__.master.body, text="P",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.P))
        __self__.P.grid(row=2,column=14)
        __self__.S = Button(__self__.master.body, text="S",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.S))
        __self__.S.grid(row=2,column=15)
        __self__.Cl = Button(__self__.master.body, text="Cl",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Cl))
        __self__.Cl.grid(row=2,column=16)
        __self__.Ar = Button(__self__.master.body, text="Ar",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ar))
        __self__.Ar.grid(row=2,column=17)
        
        __self__.K = Button(__self__.master.body, text="K",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.K))
        __self__.K.grid(row=3,column=0)
        __self__.Ca = Button(__self__.master.body, text="Ca",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ca))
        __self__.Ca.grid(row=3,column=1)
        __self__.Sc = Button(__self__.master.body, text="Sc",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Sc))
        __self__.Sc.grid(row=3,column=2)
        __self__.Ti = Button(__self__.master.body, text="Ti",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ti))
        __self__.Ti.grid(row=3,column=3)
        __self__.V = Button(__self__.master.body, text="V",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.V))
        __self__.V.grid(row=3,column=4)
        __self__.Cr = Button(__self__.master.body, text="Cr",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Cr))
        __self__.Cr.grid(row=3,column=5)
        __self__.Mn = Button(__self__.master.body, text="Mn",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Mn))
        __self__.Mn.grid(row=3,column=6)
        __self__.Fe = Button(__self__.master.body, text="Fe",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Fe))
        __self__.Fe.grid(row=3,column=7)
        __self__.Co = Button(__self__.master.body, text="Co",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Co))
        __self__.Co.grid(row=3,column=8)
        __self__.Ni = Button(__self__.master.body, text="Ni",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ni))
        __self__.Ni.grid(row=3,column=9)
        __self__.Cu = Button(__self__.master.body, text="Cu",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Cu))
        __self__.Cu.grid(row=3,column=10)
        __self__.Zn = Button(__self__.master.body, text="Zn",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Zn))
        __self__.Zn.grid(row=3,column=11)
        __self__.Ga = Button(__self__.master.body, text="Ga",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ga))
        __self__.Ga.grid(row=3,column=12)
        __self__.Ge = Button(__self__.master.body, text="Ge",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ge))
        __self__.Ge.grid(row=3,column=13)
        __self__.As = Button(__self__.master.body, text="As",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.As))
        __self__.As.grid(row=3,column=14)
        __self__.Se = Button(__self__.master.body, text="Se",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Se))
        __self__.Se.grid(row=3,column=15)
        __self__.Br = Button(__self__.master.body, text="Br",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Br))
        __self__.Br.grid(row=3,column=16)
        __self__.Kr = Button(__self__.master.body, text="Kr",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Kr))
        __self__.Kr.grid(row=3,column=17)
        
        __self__.Rb = Button(__self__.master.body, text="Rb",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Rb))
        __self__.Rb.grid(row=4,column=0)
        __self__.Sr = Button(__self__.master.body, text="Sr",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Sr))
        __self__.Sr.grid(row=4,column=1)
        __self__.Y = Button(__self__.master.body, text="Y",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Y))
        __self__.Y.grid(row=4,column=2)
        __self__.Zr = Button(__self__.master.body, text="Zr",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Zr))
        __self__.Zr.grid(row=4,column=3)
        __self__.Nb = Button(__self__.master.body, text="Nb",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Nb))
        __self__.Nb.grid(row=4,column=4)
        __self__.Mo = Button(__self__.master.body, text="Mo",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Mo))
        __self__.Mo.grid(row=4,column=5)
        __self__.Tc = Button(__self__.master.body, text="Tc",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Tc))
        __self__.Tc.grid(row=4,column=6)
        __self__.Ru = Button(__self__.master.body, text="Ru",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ru))
        __self__.Ru.grid(row=4,column=7)
        __self__.Rh = Button(__self__.master.body, text="Rh",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Rh))
        __self__.Rh.grid(row=4,column=8)
        __self__.Pd = Button(__self__.master.body, text="Pd",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Pd))
        __self__.Pd.grid(row=4,column=9)
        __self__.Ag = Button(__self__.master.body, text="Ag",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ag))
        __self__.Ag.grid(row=4,column=10)
        __self__.Cd = Button(__self__.master.body, text="Cd",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Cd))
        __self__.Cd.grid(row=4,column=11)
        __self__.In = Button(__self__.master.body, text="In",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.In))
        __self__.In.grid(row=4,column=12)
        __self__.Sn = Button(__self__.master.body, text="Sn",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Sn))
        __self__.Sn.grid(row=4,column=13)
        __self__.Sb = Button(__self__.master.body, text="Sb",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Sb))
        __self__.Sb.grid(row=4,column=14)
        __self__.Te = Button(__self__.master.body, text="Te",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Te))
        __self__.Te.grid(row=4,column=15)
        __self__.I = Button(__self__.master.body, text="I",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.I))
        __self__.I.grid(row=4,column=16)
        __self__.Xe = Button(__self__.master.body, text="Xe",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Xe))
        __self__.Xe.grid(row=4,column=17)
        
        __self__.Cs = Button(__self__.master.body, text="Cs",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Cs))
        __self__.Cs.grid(row=5,column=0)
        __self__.Ba = Button(__self__.master.body, text="Ba",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ba))
        __self__.Ba.grid(row=5,column=1)
        __self__.La = Button(__self__.master.body, text="La",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.La))
        __self__.La.grid(row=5,column=2)
        __self__.Hf = Button(__self__.master.body, text="Hf",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Hf))
        __self__.Hf.grid(row=5,column=3)
        __self__.Ta = Button(__self__.master.body, text="Ta",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ta))
        __self__.Ta.grid(row=5,column=4)
        __self__.W = Button(__self__.master.body, text="W",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.W))
        __self__.W.grid(row=5,column=5)
        __self__.Re = Button(__self__.master.body, text="Re",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Re))
        __self__.Re.grid(row=5,column=6)
        __self__.Os = Button(__self__.master.body, text="Os",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Os))
        __self__.Os.grid(row=5,column=7)
        __self__.Ir = Button(__self__.master.body, text="Ir",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ir))
        __self__.Ir.grid(row=5,column=8)
        __self__.Pt = Button(__self__.master.body, text="Pt",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Pt))
        __self__.Pt.grid(row=5,column=9)
        __self__.Au = Button(__self__.master.body, text="Au",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Au))
        __self__.Au.grid(row=5,column=10)
        __self__.Hg = Button(__self__.master.body, text="Hg",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Hg))
        __self__.Hg.grid(row=5,column=11)
        __self__.Tl = Button(__self__.master.body, text="Tl",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Tl))
        __self__.Tl.grid(row=5,column=12)
        __self__.Pb = Button(__self__.master.body, text="Pb",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Pb))
        __self__.Pb.grid(row=5,column=13)
        __self__.Bi = Button(__self__.master.body, text="Bi",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Bi))
        __self__.Bi.grid(row=5,column=14)
        __self__.Po = Button(__self__.master.body, text="Po",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Po))
        __self__.Po.grid(row=5,column=15)
        __self__.At = Button(__self__.master.body, text="At",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.At))
        __self__.At.grid(row=5,column=16)
        __self__.Rn = Button(__self__.master.body, text="Rn",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Rn))
        __self__.Rn.grid(row=5,column=17)
        
        __self__.Fr = Button(__self__.master.body, text="Fr",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Fr))
        __self__.Fr.grid(row=6,column=0)
        __self__.Ra = Button(__self__.master.body, text="Ra",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ra))
        __self__.Ra.grid(row=6,column=1)
        __self__.Ac = Button(__self__.master.body, text="Ac",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ac))
        __self__.Ac.grid(row=6,column=2)

        __self__.Ce = Button(__self__.master.body, text="Ce",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ce))
        __self__.Ce.grid(row=7,column=4)
        __self__.Pr = Button(__self__.master.body, text="Pr",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Pr))
        __self__.Pr.grid(row=7,column=5)
        __self__.Nd = Button(__self__.master.body, text="Nd",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Nd))
        __self__.Nd.grid(row=7,column=6)
        __self__.Pm = Button(__self__.master.body, text="Pm",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Pm))
        __self__.Pm.grid(row=7,column=7)
        __self__.Sm = Button(__self__.master.body, text="Sm",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Sm))
        __self__.Sm.grid(row=7,column=8)
        __self__.Eu = Button(__self__.master.body, text="Eu",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Eu))
        __self__.Eu.grid(row=7,column=9)
        __self__.Gd = Button(__self__.master.body, text="Gd",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Gd))
        __self__.Gd.grid(row=7,column=10)
        __self__.Tb = Button(__self__.master.body, text="Tb",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Tb))
        __self__.Tb.grid(row=7,column=11)
        __self__.Dy = Button(__self__.master.body, text="Dy",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Dy))
        __self__.Dy.grid(row=7,column=12)
        __self__.Ho = Button(__self__.master.body, text="Ho",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Ho))
        __self__.Ho.grid(row=7,column=13)
        __self__.Er = Button(__self__.master.body, text="Er",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Er))
        __self__.Er.grid(row=7,column=14)
        __self__.Tm = Button(__self__.master.body, text="Tm",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Tm))
        __self__.Tm.grid(row=7,column=15)
        __self__.Yb = Button(__self__.master.body, text="Yb",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Yb))
        __self__.Yb.grid(row=7,column=16)
        __self__.Lu = Button(__self__.master.body, text="Lu",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Lu))
        __self__.Lu.grid(row=7,column=17)

        __self__.Th = Button(__self__.master.body, text="Th",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Th))
        __self__.Th.grid(row=8,column=4)
        __self__.Pa = Button(__self__.master.body, text="Pa",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Pa))
        __self__.Pa.grid(row=8,column=5)
        __self__.U = Button(__self__.master.body, text="U",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.U))
        __self__.U.grid(row=8,column=6)
        __self__.Np = Button(__self__.master.body, text="Np",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Np))
        __self__.Np.grid(row=8,column=7)
        __self__.Pu = Button(__self__.master.body, text="Pu",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Pu))
        __self__.Pu.grid(row=8,column=8)
        __self__.Am = Button(__self__.master.body, text="Am",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Am))
        __self__.Am.grid(row=8,column=9)
        __self__.Cm = Button(__self__.master.body, text="Cm",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Cm))
        __self__.Cm.grid(row=8,column=10)
        __self__.Bk = Button(__self__.master.body, text="Bk",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Bk))
        __self__.Bk.grid(row=8,column=11)
        __self__.Cf = Button(__self__.master.body, text="Cf",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Cf))
        __self__.Cf.grid(row=8,column=12)
        __self__.Es = Button(__self__.master.body, text="Es",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Es))
        __self__.Es.grid(row=8,column=13)
        __self__.Fm = Button(__self__.master.body, text="Fm",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Fm))
        __self__.Fm.grid(row=8,column=14)
        __self__.Md = Button(__self__.master.body, text="Md",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Md))
        __self__.Md.grid(row=8,column=15)
        __self__.No = Button(__self__.master.body, text="No",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.No))
        __self__.No.grid(row=8,column=16)
        __self__.Lr = Button(__self__.master.body, text="Lr",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.Lr))
        __self__.Lr.grid(row=8,column=17)
        __self__.Custom = Button(__self__.master.body, text="Custom",width=2*btnsize_w,height=btnsize_h,relief='raised', fg="blue", command= lambda: __self__.add_custom_element(__self__.Custom))
        __self__.Custom.grid(row=8,column=0,columnspan=2)

        __self__.low = Entry(__self__.master.body, textvariable=__self__.cvar1, width=btnsize_w+1,fg="blue")
        __self__.low.grid(row=9,column=0)
        __self__.high = Entry(__self__.master.body, textvariable=__self__.cvar2, width=btnsize_w+1, fg="red")
        __self__.high.grid(row=9,column=1)
        __self__.clabel = Label(__self__.master.body, text="KeV", width=btnsize_w)
        __self__.clabel.grid(row=9,column=2)

        __self__.go = Button(__self__.master.footer, text="Map selected elements!",relief='raised',fg="red",bg="#da8a67",command= __self__.save_and_run)
        __self__.go.grid(column=7,columnspan=3,pady=(6,3))


#if __name__.endswith('__main__'):         
if __name__ == "__main__":
    import Constants
    optimum_resolution = (1920,1080)
    _init_numpy_mkl()
    del _init_numpy_mkl

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

    # general utilities
    import numpy as np
    import h5py
    import cv2
    import sys, os, copy, pickle, stat, random, base64
    import shutil
    import webbrowser
    from psutil import virtual_memory
    import logging, time
    import gc
    from multiprocessing import freeze_support
    freeze_support()
    
    # matplotlib imports
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    import matplotlib.patches as mpatches
    from matplotlib import style
    style.use('ggplot')
    
    def open_log():
        from SpecRead import __PERSONAL__
        # wipes logfile
        try:
            with open(os.path.join(__PERSONAL__,
                "logfile.log"),'w+') as mylog: mylog.truncate(0)
        except: pass

        # tries to create logfile on user folder
        try: 
            logger = logging.getLogger("logfile")
            logger.setLevel(Constants.LOGLEVEL)
            lHandler = logging.FileHandler(os.path.join(__PERSONAL__,
                "logfile.log"))
            formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
            lHandler.setFormatter(formatter)
            logger.addHandler(lHandler)
            logger.info('*'* 10 + ' LOG START! ' + '*'* 10)
            log_start = "{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            logger.info(log_start)   
        except IOError as exception:
            p = Tk()
            p.iconify()
            messagebox.showerror(
                    exception.__class__.__name__,
                    "Acess denied to folder {}.\nIf error persists, try running the program with administrator rights.".format(os.path.join(__PERSONAL__,"logfile.log")))
            sys.exit(1)
        return 0
    class NavigationToolbar(NavigationToolbar2Tk):
    # only display the buttons we need
        toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        ('Save', 'Save the figure', 'filesave', 'save_figure')
      )
   
    check_screen_resolution(optimum_resolution)
    # internal imports
    open_log()
    logger = logging.getLogger("logfile")
    import SpecRead
    from Mosaic import Mosaic_API
    from ReadConfig import checkout_config, set_settings 
    from ImgMath import LEVELS, apply_scaling, correlate
    from ImgMath import threshold, low_pass, iteractive_median, write_image, stackimages
    from Decoder import *
    from SpecMath import getstackplot, peakstrip
    from SpecMath import FN_reset, FN_set, FN_fit_pseudoinv, FN_fit_gaus
    from SpecMath import datacube as Cube
    from SpecMath import converth5
    from ProgressBar import Busy, BusyManager, create_tooltip
    from EnergyLib import plottables_dict, ElementColors, which_macro, ElementList
    from Mapping import getpeakmap, grab_simple_roi_image, select_lines 
    from Mapping_parallel import Cube_reader, sort_results, digest_results
    from BatchFitter import MultiFit, SingleFit, build_images

    logger.info("Loading GUI...")
    start_up()
    root = MainGUI()
    GUIicon = os.path.join(os.getcwd(),"images","icons","icon.ico")
    root.master.iconbitmap(GUIicon)  
    root_busy = BusyManager(root.master)
    root.master.mainloop()

