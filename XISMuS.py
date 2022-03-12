"""
Copyright (c) 2022 Sergio Augusto Barcellos Lins,
Bories Bremmers & Giovanni Ettore Gigante

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

def update_version():
    import io
    import subprocess
    global latest

    def download_file(destination, URL):
        r = request.Request(URL)
        r.add_header("Cache-Control", "max-age=0")
        r = request.urlopen(r)
        Length = r.getheader('content-length')
        BlockSize = 1000000  # default value
        if Length:
            Length = int(Length)
            BlockSize = max(4096, Length // 20)
        BufferAll = io.BytesIO()
        Size = 0
        bar = Busy(100,0)
        bar.add_cancel_btn()
        bar.update_text("Downloading patch...")
        while True:
            BufferNow = r.read(BlockSize)
            if not BufferNow:
                break
            BufferAll.write(BufferNow)
            Size += len(BufferNow)
            if Length:
                Percent = int((Size / Length)*100)
                try: bar.updatebar(Percent)
                except: 
                    Constants.LOGGER.info("Patch download cancelled.")
                    del r
                    del BufferAll
                    return 0
        f = open(destination, "wb")
        f.write(BufferAll.getvalue())
        f.close()
        bar.destroybar()
        return 1

    def get_version(version):
        version = version.split(".")
        version[0] = int(version[0])*100
        version[1] = int(version[1])*10
        version[2] = int(version[2])*1
        return sum(version)

    def request_version():
        global latest
        try:
            Constants.LOGGER.info("Requesting latest version...")
            package = request.Request("https://xismus.sourceforge.io/__version__.txt")
            package.add_header("Cache-Control","max-age=0")
            version = request.urlopen(package).read().decode("utf-8").replace("v","")
            latest = version
            Constants.LOGGER.info(f"Latest version available: {latest}")
            return 0
        except Exception as exception:
            Constants.LOGGER.info("Failed to connect!")
            Constants.LOGGER.info(f"Exception: {exception}")
            latest = "0.0.0"
            return 1

    def request_patch(version):
        destination = os.path.join(os.path.dirname("__file__"),"patch.exe")
        if get_version(version) > get_version(Constants.VERSION):
            question = messagebox.askyesno("New version available!",
    "There is a new version of XISMuS available. Would you like to update the software?")
            if question == True:
                Constants.LOGGER.info("Connecting to servers...")
                if os.path.exists(destination):
                    Constants.LOGGER.info("Patch file already exists!")
                    try: os.remove(destination)
                    except OSError: 
                        messagebox.showerror("Patch file already exists!",
                            f"A patch file already exists! Remove it manually and try again. File location:\n{destination}")
                        return 0
                try:
                    p = download_file(destination,
                            "https://xismus.sourceforge.io/latest.exe") 
                    if p:
                        Constants.LOGGER.info("Downloaded patch!")
                        return 1
                    else: return 0
                except OSError:
                    messagebox.showerror("Failed to get patch!",
                            "Something went wrong trying to download the patch file!\nBe sure you are running XISMuS with administrator rights.")
                    return 0
        else: 
            return 0
    Constants.LOGGER.info("Attempting to connect to sourceforge servers...")
    t0 = threading.Thread(target=request_version)
    t0.daemon = True
    t0.start()
    t0.join()

    if request_patch(latest):
        patch_path = os.path.abspath(os.path.join(os.path.dirname("__file__"),"patch.exe"))
        patch_path = patch_path.replace(os.sep,"/")
        args = [patch_path]
        try: 
            subprocess.Popen([r"update.exe"] + args, stdout=subprocess.PIPE)
        except:
            messagebox.showerror("Update error!","Failed to launch update.exe! Try updating manually.")
            return
        Constants.ROOT.Constants.ROOT_quit(force=1)

def start_up():
    """ Initializes sp global variables and paths """

    splash.update( "Configuring environment..." )
    sp.conditional_setup()
    Constants.LOGGER.info( "Setting up..." )
    try: load_cube()
    except: pass
    Constants.LOGGER.info( "Done." )
    Constants.FIND_ELEMENT_LIST = []

    database = Samples()
    database.list_all( splash )
    splash.kill()

    Constants.ROOT = MainGUI()
    Constants.ROOT.boot( database )
    Constants.ROOT.busy = BusyManager( Constants.ROOT.master )
    update_version()

def open_log():
    from ReadConfig import __PERSONAL__
    # wipes logfile
    try:
        with open(os.path.join(__PERSONAL__,
            "logfile.log"),'w+') as mylog: mylog.truncate(0)
            
    except: pass

    # tries to create logfile on user folder
    try:
        Constants.LOGGER = logging.getLogger("logfile")
        Constants.LOGGER.setLevel(Constants.LOGLEVEL)
        lHandler = logging.FileHandler(os.path.join(__PERSONAL__,
            "logfile.log"))
        formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(message)s")
        lHandler.setFormatter(formatter)
        Constants.LOGGER.addHandler(lHandler)
        Constants.LOGGER.info('*'* 10 + ' LOG START! ' + '*'* 10)
        log_start = "{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        Constants.LOGGER.info(log_start)
    except IOError as exception:
        p = Tk()
        p.iconbitmap(os.path.join(os.getcwd(),"images","icons","icon.ico"))
        p.iconify()
        messagebox.showerror(
                exception.__class__.__name__,
                "Acess denied to folder {}.\nIf error persists, try running the program with administrator rights.".format(os.path.join(__PERSONAL__,"logfile.log")))
        sys.exit(1)
    return 0

def wipe_list():
    """ Self-explanatory. Clears the global variable and
    destroys the Periodic Table Tk.Toplevel window """
    Constants.FIND_ELEMENT_LIST = []
    refresh_plots() 
    try: Constants.ROOT.find_elements_diag.master.destroy()
    except AttributeError: pass #for auto_wizard method

def openURL(url):
    webbrowser.open(url)

def call_help():
    """ Spawns help dialogue """
    proceed = messagebox.askquestion("Attention!","You are about to be redirected to github webpage.\nDo you want to proceed?")
    if proceed == "yes":
        webbrowser.open("https://github.com/linssab/XISMuS/blob/master/HELP.md")
        return 0
    else:
        return 0

def verify_calibration_parameters(caller, anchors):
    if anchors == []:
        messagebox.showerror("Calibration Error",
                "No acceptable calibration parameters passed!")
        try: caller.master.focus_set()
        except: pass
        raise ValueError("No acceptable calibration parameters passed!")
        return 1
    elif len(anchors) <= 1:
        messagebox.showerror("Calibration Error",
                "Need at least two anchors!")
        try: caller.master.focus_set()
        except: pass
        raise ValueError("Calibration need at least two anchors!")
        return 1
    for index in range(len(anchors)):
        if anchors[index][0] > 0 and anchors[index][1] > 0:
            pass
        elif anchors[index][0] <= 0 or anchors[index][1] <= 0:
            messagebox.showerror("Calibration Error",
                    "Can't receive negative or zero values!")
            raise ValueError("Can't receive negative or zero values!")
            return 1
        ##############################
    return 0

def remove_continuum_data():
    value = Constants.ROOT.SamplesWindow_TableLeft.get(ACTIVE)
    if value != Constants.MY_DATACUBE.name:
        Constants.ROOT.sample_select(force=value)
    if Constants.MY_DATACUBE.matrix.shape != Constants.MY_DATACUBE.background.shape:
        messagebox.showerror("Error","No data to erase! Bgstrip mode already set to None.")
    else: 
        question = messagebox.askyesno("Attention!","Attention, this operation is irreversible. Are you sure you want to proceed?")
        if question:
            Constants.MY_DATACUBE.background = np.zeros([Constants.MY_DATACUBE.matrix.shape[-1]],dtype=np.float32)
            Constants.MY_DATACUBE.sum_bg = np.zeros([Constants.MY_DATACUBE.matrix.shape[-1]],dtype=np.float32)
            Constants.MY_DATACUBE.config["bgstrip"] = "None"
            Constants.MY_DATACUBE.config["bg_settings"] = []
            Constants.MY_DATACUBE.save_cube()
            Constants.ROOT.write_stat()
    return

def upgrade_cube(cube):
    """ pre 1.3 cubes will remain without 'version' attribute. Other cubes will maintain the
    value, plus a string to identify they were updated """

    Constants.LOGGER.warning("Obsolete cube loaded! Updating ...")
    messagebox.showinfo("Update!","Obsolete cube loaded. We will update it to the newest version...")
    attributes = cube.__dict__.keys()

    bar = Busy(len(attributes)-1,0)
    bar.update_text("Updating cube...")
    i=0

    sp.setup_from_datacube(cube,Constants.ROOT.samples)
    specbatch = Cube(["h5","upgrade"],Constants.MY_DATACUBE.config)
    specbatch.__dict__.pop("version")   #remove automatically assigned version
    for atr in attributes:
        bar.updatebar(i)
        if atr != "version":
            specbatch.__dict__[atr] = cube.__dict__[atr]
            Constants.LOGGER.info(f"Assigned {atr} to new cube...")
            i+=1
        elif atr == "version":
            original_version = cube.version.split(" ")[0]
            specbatch.__dict__[atr] = Constants.VERSION
            specbatch.update_info = f"{original_version} -> {Constants.VERSION}"
            i+=1
    if "version" not in attributes: 
        specbatch.update_info = f"pre v1.3 -> {Constants.VERSION}"
        specbatch.fit_fano_and_noise()

    bar.update_text("Writing to disk...")
    specbatch.save_cube()
    load_cube()
    bar.destroybar()

def load_cube():
    """ Loads cube to memory (unpickle). Cube name is passed according to
    latest sp parameters. See setup conditions inside Engine.SpecRead module.
    Returns the datacube object """

    def check_memory():
        sys_mem = dict(virtual_memory()._asdict())
        available_memory = sys_mem["available"]
        cube_stats = os.stat(sp.cube_path)
        cube_size = cube_stats.st_size
        if hasattr(Constants.MY_DATACUBE,"matrix"):
            m_size = Constants.MY_DATACUBE.matrix.itemsize
            b_size = Constants.MY_DATACUBE.background.itemsize
            temp_mem = Constants.MY_DATACUBE.matrix.size * m_size + \
                    Constants.MY_DATACUBE.background.size * b_size
        else: temp_mem = 0
        if cube_size > ( available_memory + temp_mem ):
            #print("Cube",cube_size, "\nAvailable:",available_memory, "\nTemp:",temp_mem)
            Constants.LOGGER.warning(f"Cannot load cube {sp.cube_path}! Not enough RAM!")
            messagebox.showerror("Memory error!",f"No RAM available! Cube size: {convert_bytes(cube_size)}, Memory available: {convert_bytes(available_memory)}.")
            Constants.ROOT.busy.notbusy()
            return 1
        else: return 0

    Constants.LOGGER.debug("Trying to load cube file.")
    Constants.LOGGER.debug(sp.cube_path)
    if os.path.exists(sp.cube_path):
        Constants.ROOT.busy.busy()
        cube_file = open(sp.cube_path,'rb')
        if check_memory():
            raise MemoryError(f"Could not load datacube {sp.cube_path}")
        else: pass
        try: 
            del Constants.MY_DATACUBE
            gc.collect()
        except: 
            pass
        try: Constants.MY_DATACUBE = pickle.load(cube_file)
        except Exception as e: 
            messagebox.showerror("Error",f"Could not unpickle the datacube. Exception:\n{e}")
            return
        cube_file.close()
        if hasattr(Constants.MY_DATACUBE,"version"):
            version = [int(i) for i in Constants.MY_DATACUBE.version.split("v")[-1].split(".")]
            version[0] = version[0]*100
            version[1] = version[1]*10
            version[2] = version[2]*1
            version = sum(version)
            if version < 134:
                upgrade_cube(Constants.MY_DATACUBE)
        elif not hasattr(Constants.MY_DATACUBE,"update_info"): 
            upgrade_cube(Constants.MY_DATACUBE)
        Constants.LOGGER.debug("Loaded cube {} to memory.".format(cube_file))
        Constants.MY_DATACUBE.densitymap = Constants.MY_DATACUBE.densitymap.astype("float32") 
        Constants.ROOT.busy.notbusy()
    elif os.path.exists(os.path.join(sp.output_path,
        "{}.lz".format(Constants.DIRECTORY))):
        lz_file = open(sp.cube_path,'rb')
        data = lz_file.read()
        del Constants.MY_DATACUBE
        Constants.MY_DATACUBE = data
        lz_file.close()
    else:
        Constants.LOGGER.debug("No cube found.")
        Constants.ROOT.toggle_(toggle='Off') 
        pass
    return Constants.MY_DATACUBE

def refresh_plots(exclusive=""):
    """refresh one plot window exclusively or all open windows"""

    if len(Constants.FIND_ELEMENT_LIST) > 0: 
        lines = True
    else: 
        lines = False
    
    ##############################################################
    if exclusive == "mps":
        try:
            Constants.ROOT.MPS.draw_spec(
                mode=['mps'],display_mode=Constants.PLOTSCALE,lines=lines)
            Constants.ROOT.MPS.update_idletasks()
        except: pass
    elif exclusive == "summation":
        try: 
            Constants.ROOT.summation.draw_spec(
                mode=['summation'],display_mode=Constants.PLOTSCALE,lines=lines)
            Constants.ROOT.summation.update_idletasks()
        except: pass
    elif exclusive == "combined":
        try: 
            Constants.ROOT.combined.draw_spec(
                mode=['summation','mps'],display_mode=Constants.PLOTSCALE,lines=lines)
            Constants.ROOT.combined.update_idletasks()
        except: pass
    elif exclusive == "roi_sum":
        for API in Constants.ROOT.ImageAnalyzers: 
            try:
                API.plot.draw_selective_sum(API.DATACUBE,
                        API.sum_spectrum,
                        display_mode = Constants.PLOTSCALE,
                        lines = lines,
                        refresh=True)
                API.plot.master.update_idletasks()
            except: pass
    ##############################################################

    else:
        try:
            Constants.ROOT.MPS.draw_spec(
                mode=['mps'],display_mode=Constants.PLOTSCALE,lines=lines)
            Constants.ROOT.MPS.update_idletasks()
        except: pass
        try: 
            Constants.ROOT.summation.draw_spec(
                mode=['summation'],display_mode=Constants.PLOTSCALE,lines=lines)
            Constants.ROOT.summation.update_idletasks()
        except: pass
        try: 
            Constants.ROOT.combined.draw_spec(
                mode=['summation','mps'],display_mode=Constants.PLOTSCALE,lines=lines)
            Constants.ROOT.combined.update_idletasks()
        except: pass
        for API in Constants.ROOT.ImageAnalyzers:
            try:
                if hasattr(API,"plot"):
                    API.plot.draw_selective_sum(API.DATACUBE,
                            API.sum_spectrum,
                            display_mode = Constants.PLOTSCALE,
                            lines = lines,
                            refresh=True)
                    API.plot.master.update_idletasks()
                if hasattr(API,"IndexNavigator"):
                    if Constants.PLOTSCALE == "-semilogy":
                        mode = "log"
                    else: mode = "linear"
                    API.IndexNavigator.PlotRight.set_yscale(mode)
                    API.IndexNavigator.PlotCanvasR.draw_idle()
            except: pass

def check_screen_resolution(resolution_tuple):
    Constants.LOW_RES = None
    limit_w, limit_h = resolution_tuple[0], resolution_tuple[1]
    w, h = screen_size()

    if w > limit_w or h > limit_h:
        messagebox.showinfo("Info","Your current screen resolution is {}x{}. This program was optmized to work in 1080p resolution. If the windows are too small or if any problems are experienced with buttons and icons, please try lowering your screen resolution and setting the Windows scaling option to 100%.".format(w,h))
    elif w < limit_w and h < limit_h:
        Constants.LOW_RES = "moderate"
        if 800 < w <= 1024 or 600 < h <= 768: Constants.LOW_RES = "high"
        elif w <= 640 or h <= 480: Constants.LOW_RES = "extreme"
        messagebox.showinfo("Info","Your current screen resolution is {}x{}. This program was optmized to work in 1080p resolution. If the windows are too large, off-scale or if any problems are experienced with buttons and icons, please try increasing your screen resolution. Shall problems persist, verify your Windows scaling option.".format(w,h))

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
        _core = os.path.dirname("__file__")
        for _dll in ('mkl_rt', 'libiomp5md', 'mkl_core', 'mkl_intel_thread', 
                     'libmmd', 'libifcoremd', 'libimalloc'):
            try: 
                ctypes.cdll.LoadLibrary(os.path.join(_core,_dll))
                splash.update(f"Loaded {_dll}")
            except:
                splash.update(f"Failed to load {_dll}")
            time.sleep(0.100)
    except Exception:
        pass


class About:
    """ Spawns author information """
    def __init__(__self__):
        __self__.master = Toplevel(master=Constants.ROOT.master)
        __self__.master.title("About")
        __self__.master.resizable(False,False)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.master.bind("<Escape>",__self__.kill)
        __self__.master.iconbitmap( os.path.join(os.getcwd(),"images","icons","icon.ico") )  

        infotext = f"Software version: {Constants.VERSION}\nContact: sergiolins_@outlook.com"

        __self__.winFrame = Frame(__self__.master)
        
        __self__.Info = Label(__self__.winFrame, text=infotext, wraplength=640, anchor=W, justify=LEFT)
        __self__.Link1 = Label(__self__.winFrame, text="Contact via ResearchGate", fg="blue", cursor="hand2", anchor=W)
        __self__.Link2 = Label(__self__.winFrame, text="Go to XISMuS webpage", fg="blue", cursor="hand2", anchor=W)
        __self__.Link1.bind("<Button-1>", __self__.go_to_rs)
        __self__.Link2.bind("<Button-1>", __self__.go_to_web)
        
        __self__.winFrame.grid(row=0, column=0, padx=(16,16),pady=(16,16), sticky="NWSE")
        __self__.Info.grid(row=1, sticky=W)
        __self__.Link1.grid(row=2, sticky=W)
        __self__.Link2.grid(row=3, sticky=W)

        place_center(Constants.ROOT.master,__self__.master)

    def kill(__self__,e=""):
        __self__.master.destroy()

    def go_to_rs(__self__,e=""):
        openURL("https://www.researchgate.net/profile/Sergio_Augusto_Lins")
        __self__.master.destroy()

    def go_to_web(__self__,e=""):
        openURL("https://linssab.github.io/contact")
        __self__.master.destroy()


class CanvasSizeDialog:
    def __init__(__self__, parent):
        __self__.win = Toplevel(master=parent.master)
        __self__.win.bind("<Escape>",__self__.kill)
        __self__.win.withdraw()
        __self__.win.resizable(False,False)
        __self__.win.overrideredirect(True)
        __self__.win.grab_set()


        __self__.diag = ttk.Frame(__self__.win, relief=RIDGE, style="dark.TFrame")
        label0 = ttk.Label(__self__.diag,text="Canvas Size", style="dark.TLabel")
        label1 = ttk.Label(__self__.diag,text="Height (px): ", style="dark.TLabel")
        label2 = ttk.Label(__self__.diag,text="Width (px): ", style="dark.TLabel")

        __self__.x = IntVar()
        __self__.y = IntVar()
        __self__.x.set(100)
        __self__.y.set(100)
        __self__.win.bind("<Return>",__self__.spawn_mosaic)
        
        x_ = ttk.Entry(__self__.diag,textvariable=__self__.x,validate="focusout",
                width=9)
        y_ = ttk.Entry(__self__.diag,textvariable=__self__.y,validate="focusout",
                width=9)

        accept = ttk.Button(__self__.diag,text="Ok", width=10, 
                command=__self__.spawn_mosaic)
        cancel = ttk.Button(__self__.diag,text="Cancel", width=10, 
                command=__self__.kill)
        
        
        label0.grid(row=0,column=0,columnspan=2,pady=(3,0))
        label1.grid(row=1,column=0)
        label2.grid(row=2,column=0)
        __self__.diag.grid()
        x_.grid(row=1,column=1)
        y_.grid(row=2,column=1)
        accept.grid(row=3,column=0,pady=5,sticky=W+E,padx=(10,6))
        cancel.grid(row=3,column=1,pady=5,sticky=W+E,padx=(6,10))
        
        __self__.win.update()
        place_center(parent.master,__self__.win)
        __self__.win.deiconify()
        x_.focus_set()

    def kill(__self__,e=""):
        __self__.win.grab_release()
        __self__.win.destroy()
        Constants.ROOT.master.focus_set()
        del __self__

    def spawn_mosaic(__self__,e=""):
        if __self__.x.get() == 0 or __self__.y.get()==0:
            messagebox.showerror("Ivalid dimension!",
                    "Can't create {}x{} canvas!".format(__self__.x.get(),__self__.y.get()))
            return
        try:
            size = (__self__.x.get(),__self__.y.get())
            __self__.kill()
        except: 
            messagebox.showerror("Ivalid dimension!",
                    "Can't create {}x{} canvas!".format(__self__.x.get(),__self__.y.get()))
            return
        Mosaic_API(size, Constants.ROOT)


class Convert_File_Name:
    def __init__(__self__,parent):
        __self__.master = Toplevel(master=parent.master)
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

        __self__.LeftPane = ttk.LabelFrame(__self__.master, height=250, width=128, text="Input", padding=10)
        __self__.RightPane = ttk.LabelFrame(__self__.master, height=250, text="Output", padding=10)

        __self__.LeftPane.grid(row=0, column=0, sticky=N+W+S+E, padx=(3,2), pady=2)
        __self__.RightPane.grid(row=0, column=1, sticky=N+S, padx=(2,3), pady=2)

        __self__.build_widgets()
        place_center(parent.master,__self__.master)
        __self__.master.grab_set()

    def build_widgets(__self__):
        
        """ Left Pane """
        icon = PhotoImage(data=ICO_LOAD)
        __self__.LoadIco = icon.subsample(1,1)
        __self__.LoadBtn = ttk.Button(__self__.LeftPane, 
                text="Load",
                image=__self__.LoadIco,
                command=__self__.grab_file_list,
                compound=TOP,
                takefocus=False)
        
        """ Right Pane Labels """
        __self__.PrefixLabel = ttk.Label(__self__.RightPane, text="Prefix")
        __self__.StartLabel = ttk.Label(__self__.RightPane, text="Starting No.")
        __self__.WidthLabel = ttk.Label(__self__.RightPane, text="Width (optional)")
        __self__.HeightLabel = ttk.Label(__self__.RightPane, text="Height (optional)")

        """ Right Pane Entries """
        __self__.PrefixEntry = ttk.Entry(__self__.RightPane, 
                textvariable=__self__.prefix,
                width=10)
        __self__.StartEntry = ttk.Entry(__self__.RightPane,
                textvariable=__self__.starting_index,
                width=10)
        __self__.WidthEntry = ttk.Entry(__self__.RightPane,
                textvariable=__self__.width,
                width=10)
        __self__.HeightEntry = ttk.Entry(__self__.RightPane,
                textvariable=__self__.height,
                width=10)
        
        """ Right Pane Buttons """
        icon = PhotoImage(data=ICO_ACCEPT)
        __self__.OkIcon = icon.subsample(1,1)
        __self__.OkBtn = ttk.Button(__self__.RightPane, 
                image=__self__.OkIcon, 
                text= " Convert",
                compound=LEFT,
                command=__self__.start_conversion,
                takefocus=False)

        icon = PhotoImage(data=ICO_REJECT)
        __self__.QuitIcon = icon.subsample(1,1)
        __self__.QuitBtn = ttk.Button(__self__.RightPane, 
                text=" Cancel",
                compound=LEFT,
                image=__self__.QuitIcon,
                command=__self__.kill,
                takefocus=False)
        
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
        Constants.ROOT.master.focus_set()
        __self__.master.destroy()


class Welcome:
    """ Welcome window class. Spawns a window with given texts at the center
    of MainGUI window """

    def __init__(__self__, parent):
        """parent is a Tk window"""
        __self__.h, __self__.w = 400, 240
        __self__.master = Toplevel(master=parent.master)
        __self__.master.attributes("-alpha", 0.0)
        __self__.parent = parent
        __self__.master.iconbitmap(os.path.join(os.getcwd(),"images","icons","icon.ico"))  
        __self__.master.bind("<Return>",__self__.checkout)
        __self__.master.bind("<Escape>",__self__.checkout)
        __self__.font = tkFont.Font(family="Tahoma", size=8)

        __self__.master.resizable(False,False)
        __self__.master.title("Welcome!")

        __self__.page = StringVar()
        __self__.tag = BooleanVar()
        __self__.infotext = StringVar()
        __self__.messages = [
                "Welcome to XISMuS {}\n\
                \nClick the left or right arrows to navigate through this menu.".format(Constants.VERSION),\

                "Getting started: \nSamples automatically located can be found in the righti-most panel. Double-click the name to load it.\nBy default, XISMuS looks for mca files under C:\\Users\\user\\Documents\\XISMuS\\ folder. To change it, click on \"Toolbox\" and select \"Change samples folder\"",

                "Compiling a sample:\nTo compile your data, double click on the sample name inside the \"Samples\" window in the right corner. You will be prompted to configure your sample parameters.\nRight-click the sample or the white canvas in the left for further options."
                ]
        change = __self__.read_log() 
        if change:
            for i in range(len(change)):
                __self__.messages.insert(0,change[len(change)-1-i])
        __self__.current_page = 1
        __self__.page.set("Page {}/{}".format(__self__.current_page,len(__self__.messages)))
        __self__.tag.set(False)
        __self__.infotext.set(__self__.messages[0])
        __self__.build_widgets()
        __self__.master.after(150, __self__.master.attributes, "-alpha", 1.0)

    def build_widgets(__self__):
        __self__.page_counter = Label(
                __self__.master, 
                textvariable=__self__.page, 
                relief=RIDGE)
        __self__.text_frame = Frame(
                __self__.master,
                width=320, height=150)
        __self__.info = Label(__self__.text_frame,
                textvariable=__self__.infotext,
                anchor=CENTER,
                justify=CENTER,
                wraplength=400,
                width=70,
                height=8,
                padx=5,
                bg=Constants.DEFAULTBTN_COLOR, 
                relief=FLAT)
        __self__.info["font"] = __self__.font

        __self__.page_counter.grid(row=0, column=0, sticky=W+E, columnspan=2, pady=3)
        __self__.info.grid(row=0, column=1, sticky=W+E)
        __self__.text_frame.grid(row=1, column=0, sticky=W+E, columnspan=2)

        icon_fw = PhotoImage(data=ICO_NEXT)
        __self__.icon_fw = icon_fw.subsample(1,1)
        icon_bw= PhotoImage(data=ICO_PREVIOUS)
        __self__.icon_bw = icon_bw.subsample(1,1)

        __self__.fw = ttk.Button(
                __self__.text_frame, 
                image=__self__.icon_fw, 
                takefocus=False,
                cursor="hand2",
                command=__self__.next_page) 
        __self__.bw = ttk.Button(
                __self__.text_frame, 
                image=__self__.icon_bw, 
                takefocus=False,
                cursor="hand2",
                command=__self__.previous_page) 

        __self__.fw.grid(row=0, column=2,padx=6)
        __self__.bw.grid(row=0, column=0,padx=6)

        __self__.button_frame = Frame(__self__.master)
        __self__.tag_button = ttk.Checkbutton(__self__.master, 
                takefocus=False,
                text="Do not show me again next time.",
                variable=__self__.tag) 
        __self__.accept = ttk.Button(
                __self__.button_frame, 
                takefocus=False,
                text="Ok", 
                command=__self__.checkout)

        __self__.button_frame.grid(row=3,column=0,columnspan=2)
        __self__.tag_button.grid(row=2, column=0, padx=10)
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
        tot = int(len(lines)/7)
        message,counter,page = [""],0,1
        for i in range(len(lines)):
            line = lines[i]
            counter += 1
            if counter >= 7:
                counter = 0
                #message[page-1] += "\nLog {} of {}".format(page,tot+1)
                message.append("")
                page += 1
            message[page-1] += line
            #if i == len(lines)-1: message[page-1] += "\nLog {} of {}".format(page,tot+1)
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
        inipath = os.path.join(sp.__BIN__,"settings.tag")
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
        __self__.parent.master.focus_set()
        __self__.parent.master.focus_force()
        __self__.master.destroy()


class DimensionDiag():
    """ Creates a pop-up dialog to prompt the datacube dimension
    if no colonneXrighe.txt file is found for the data selected.
    It writes a custom colonneXrighe.txt file to the sample output
    folder, which is deleted if the sample is RESET """

    def __init__(__self__, parent):
        __self__.master = Toplevel(master = parent.master)
        __self__.parent = parent
        __self__.master.withdraw()
        __self__.master.resizable(False,False)
        __self__.master.overrideredirect(True)
        __self__.master.bind("<Escape>",__self__.kill)
        __self__.master.bind("<Return>",__self__.send)

        __self__.exit_code = None
        __self__.master.grab_set()
        __self__.folder = Constants.DIRECTORY

        diag = Frame(__self__.master,relief=RIDGE,bd=3)
        label0 = Label(diag,text="Image size")
        label1 = Label(diag,text="Height: ")
        label2 = Label(diag,text="Width: ")

        __self__.x = StringVar()
        __self__.x.trace("w",__self__.callback_x)
        __self__.y = StringVar()
        __self__.y.trace("w",__self__.callback_y)
        
        __self__.x_ = Entry(diag,textvariable=__self__.x,validate="focusout")
        __self__.y_ = Entry(diag,textvariable=__self__.y,validate="focusout")
        
        accept = Button(diag,text="Ok", width=13, command=__self__.send)

        diag.grid()
        label0.grid(row=0,column=0,columnspan=2)
        label1.grid(row=1,column=0)
        label2.grid(row=2,column=0)
        accept.grid(row=3,column=0,columnspan=2,pady=5)
        __self__.x_.grid(row=1,column=1)
        __self__.y_.grid(row=2,column=1)
        
        __self__.master.update()

        place_center(parent.master,__self__.master)

        __self__.master.deiconify()
        __self__.x_.focus_set()

    def check_values(__self__,x,y):
        x,y = x.get(),y.get()
        if x == "" or y == "": 
            messagebox.showerror("Error!","No input! Please add a value.")
            return
        if x.isdigit(): 
            x=int(x)
            if x > __self__.parent.mcacount[__self__.folder]: x = Constants.ROOT.mcacount[__self__.folder]
            elif x == 0: x = 1
        else: 
            messagebox.showerror("Error!","{} not a number!".format(x))
            return
        if y.isdigit(): 
            y=int(y)
            if y > __self__.parent.mcacount[__self__.folder]: y = Constants.ROOT.mcacount[__self__.folder]
            elif y == 0: y = 1
        else:
            messagebox.showerror("Error!","{} not a number!".format(y))
            return
        while x*y > __self__.parent.mcacount[__self__.folder]:
            if x > y: x-=1
            elif y > x: y-=1
        return x,y
    
    def send(__self__,event=""):
        __self__.parent.config_xy = __self__.check_values(__self__.x,__self__.y)
        if __self__.parent.config_xy == None: return
        __self__.master.grab_release()
        __self__.master.destroy()
        __self__.exit_code = "save"
        return __self__.x.get(),__self__.y.get()

    def callback_x(__self__,name="",index="",mode=""):
        try: 
            value = int(__self__.parent.mcacount[__self__.folder]/int(__self__.x.get()))
            __self__.y.set(value)
        except: 
            pass
    
    def callback_y(__self__,name="",index="",mode=""):
        try: 
            value = int(__self__.parent.mcacount[__self__.folder]/int(__self__.y.get()))
            __self__.x.set(value)
        except:
            pass
    
    def kill(__self__,e):
        __self__.exit_code = "cancel"
        __self__.master.destroy()


class Samples:
    def __init__(__self__):
        __self__.samples_database = {}
        __self__.samples_path = {}
        __self__.mcacount = {}
        __self__.mca_indexing = {}
        __self__.mca_extension = {}

    def kill(__self__):
        __self__.popup.grab_set()
        __self__.popup.destroy()

    def pop_loader(__self__):
        __self__.popup = Toplevel()
        __self__.text = StringVar()
        __self__.text.set("None")
        __self__.popup.resizable(False,False)
        __self__.popup.overrideredirect(True)

        x = __self__.popup.winfo_screenwidth()
        y = __self__.popup.winfo_screenheight()

        __self__.popup.geometry(
                "{}x{}+{}+{}".format(260, 51,
                int((x/2)-80), int((y/2)-23)))

        __self__.outerframe = Frame(
                __self__.popup, 
                relief=RIDGE,
                bd = 3,
                width=260, height=52)
        __self__.popup.label1 = Label(__self__.outerframe, text="Adding to database...")
        __self__.label2 = Label(__self__.outerframe, textvariable = __self__.text)

        __self__.outerframe.grid_propagate(0)
        __self__.outerframe.grid(row=0,column=0,sticky=E+W)
        __self__.label2.grid(row=1,column=0,sticky=W)
        __self__.popup.label1.grid(row=0,column=0,sticky=W)       

        __self__.popup.update_idletasks()
        __self__.popup.grab_set()

    def load_folder_from_database(__self__, folder):
        """ Inserts the database information in the Samples class """
        
        __self__.samples_database[folder] = Constants.USER_DATABASE[folder]["prefix"]
        __self__.samples_path[folder] = Constants.USER_DATABASE[folder]["path"]
        __self__.mcacount[folder] = Constants.USER_DATABASE[folder]["mcacount"]
        __self__.mca_extension[folder] = Constants.USER_DATABASE[folder]["extension"]
        __self__.mca_indexing[folder] = Constants.USER_DATABASE[folder]["indexing"]
        return

    def pre_load_from_database(__self__):
        not_found_samples = []
        for folder in Constants.USER_DATABASE.keys():
            if os.path.exists(Constants.USER_DATABASE[folder]["path"]):
                __self__.load_folder_from_database(folder)
                Constants.LOGGER.info("Loaded {} parameters from database...".format(folder))
                __self__.skip_list.append(folder)
                continue
            else:
                not_found_samples.append(folder)
                Constants.LOGGER.info(
                        "{} path ({}) does not exist. Removed from database...".format(
                            folder,Constants.USER_DATABASE[folder]["path"]))
        Database.remove_entry_from_database(not_found_samples)

    def update_label(__self__, splash=None, text=None):
        if splash:
            text = "Reading\t"+text
            splash.update(text)
        else:
            __self__.text.set(text)
            __self__.label2.update()
            __self__.popup.update_idletasks()

    def list_all(__self__, splash=None):
        __self__.skip_list = []
        Constants.LOGGER.info("Loading sample list...")
        Constants.LOGGER.info("Reading database...")
        Database.load_user_database()
        __self__.pre_load_from_database()
        Constants.LOGGER.info("Done with reading database...")
        indexing = None
        mca_prefix = None
        
        try:
            __self__.update_label(
                    splash=splash,
                    text=f"Reading tree {Constants.SAMPLES_FOLDER}...")
            Constants.LOGGER.info(f"Checking tree {Constants.SAMPLES_FOLDER}")
                        
            """ Lists all possible samples """
            samples = [name for name in os.listdir(Constants.SAMPLES_FOLDER) \
                    if os.path.isdir(os.path.join(Constants.SAMPLES_FOLDER,name)) and \
                    name not in Constants.USER_DATABASE.keys()]
            
            """ Verifies which samples have a compiled datacube in output folder """
            for folder in samples:
                indexing = None
                if os.path.exists(os.path.join(sp.__PERSONAL__,"output",folder)):
                    for name in os.listdir(os.path.join(sp.__PERSONAL__,
                        "output",folder)):
                        if name.lower().endswith(".cube"):
                            __self__.update_label(
                                splash=splash,
                                text=f"Cube for {folder} already compiled, skipping mca\'s")
                            __self__.skip_list.append(name.split(".cube")[0])
                if folder not in __self__.skip_list: 
                    
                    """ Lists the spectra files """            
                    files = [name for name in os.listdir(os.path.join(Constants.SAMPLES_FOLDER,
                        folder)) if name.lower().endswith(".mca") or name.lower().endswith(".txt")]
                    extension = files[:]
                
                else: files = []

                """ If spectra are found, list and get the files prefix, 
                indexing and extension """

                if files != []:
                    if folder not in __self__.skip_list:
                        for item in range(len(files)): 
                            # displays file being read on splash screen
                            __self__.update_label(
                            splash=splash,
                            text=f"{files[item]}")
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
                            Database.write_to_user_database(
                                    folder,
                                    p,
                                    mca_prefix,
                                    len(files),
                                    mca_extension,
                                    indexing)
                            Constants.LOGGER.info(f"Added {folder} to database")
            Constants.LOGGER.info("Done.")

        except IOError as exception:
            if exception.__class__.__name__ == "FileNotFoundError":
                Constants.LOGGER.info("No folder {} found.".format(Constants.SAMPLES_FOLDER))
            elif exception.__class__.__name__ == "PermissionError":
                Constants.LOGGER.info("Cannot load samples. Error {}.".format(
                    exception.__class__.__name__))
                messagebox.showerror(exception.__class__.__name__,
                        "Acess denied to folder {}.\nIf error persists, try running the program with administrator rights.".format(Constants.SAMPLES_FOLDER))
            else: pass

        try:
            """ After trying to look at every folder under the folder selected, 
            priority is given to the actual selected folder """

            local_path = Constants.SAMPLES_FOLDER.split("\\")
            folder = local_path.pop(-1)
            
            # builds new path
            new_path = ""
            for name in local_path:
                new_path = new_path + name + "\\"

            Constants.LOGGER.info(f"Checking {new_path}")

            if os.path.exists(os.path.join(sp.__PERSONAL__,"output",folder)):
                for name in os.listdir(os.path.join(sp.__PERSONAL__,
                    "output")):
                    if name.lower().endswith(".cube"):
                        __self__.update_label(
                        splash=splash,
                        text= f"Cube for {folder} already compiled, skipping mca\'s")
                        __self__.skip_list.append(name.split(".cube")[0])

            files = [name for name in os.listdir(Constants.SAMPLES_FOLDER) \
                    if name.lower().endswith(".mca") or name.lower().endswith(".txt")]
            extension = files[:]
            if files == []: pass
            else:
                if folder not in __self__.skip_list:
                    for item in range(len(files)): 
                        # displays file being read on splash screen
                        __self__.update_label(
                        splash=splash,
                        text= f"{files[item]}")
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
                        Database.write_to_user_database(
                                folder,
                                p,
                                mca_prefix,
                                len(files),
                                mca_extension,
                                indexing)
                        Constants.LOGGER.info(f"Added {folder} to database")
            Constants.LOGGER.info("Done.")
        
        except IOError as exception:
            if exception.__class__.__name__ == "FileNotFoundError":
                Constants.LOGGER.info("No folder {} found.".format(Constants.SAMPLES_FOLDER))
            elif exception.__class__.__name__ == "PermissionError":
                Constants.LOGGER.info("Cannot load samples. Error {}.".format(
                    exception.__class__.__name__))
            else: pass
        
        try:
            """ Try looking for training_data """

            folder = "Example Data"
            new_path = os.path.join(sp.__PERSONAL__,folder)
            Constants.LOGGER.info(f"Checking for TRAINING DATA {new_path}")
            
            if os.path.exists(new_path):
                examples = [folder for folder in os.listdir(new_path) if \
                        os.path.isdir(os.path.join(new_path,folder))]
                for folder in examples:
                    files = [name for name in os.listdir(os.path.join(new_path,folder)) \
                            if name.lower().endswith(".mca") or name.lower().endswith(".txt")]
                    extension = files[:]
                    for item in range(len(files)): 
                        # displays file being read on splash screen
                        __self__.update_label(splash=splash,
                                text=f"{files[item]}")
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
            Constants.LOGGER.info("Done.")
        except: Constants.LOGGER.info("Could not locate Training Data.")

        try:
            """ Verify packed cubes """

            output_folder = os.path.join(sp.__PERSONAL__,"output")
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
                        Constants.LOGGER.info("Datacube {} located. Ignoring mca files".format(folder))
        except IOError as exception:
            if exception.__class__.__name__ == "FileNotFoundError":
                Constants.LOGGER.info("No folder {} found.".format(Constants.SAMPLES_FOLDER))
            elif exception.__class__.__name__ == "PermissionError":
                Constants.LOGGER.info("Cannot load samples. Error {}.".format(
                    exception.__class__.__name__))
            else: pass
        try: __self__.kill()
        except: pass
       

class Settings:        
    def __init__(__self__,parent):
        __self__.master = Toplevel(master=parent.master)
        __self__.master.attributes("-alpha",0.0)
        __self__.parent = parent
        __self__.master.title("Settings")
        __self__.master.resizable(False,False)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill_window)
        __self__.master.bind("<Escape>",__self__.kill_window)
        __self__.master.iconbitmap( os.path.join(os.getcwd(),"images","icons","settings.ico") )
        

        sys_mem = dict(virtual_memory()._asdict())

        __self__.CoreCount = Constants.CPUS
        __self__.GeneralOptions = LabelFrame(__self__.master, text="General options", padx=15, pady=15)
        __self__.PeakOptions = LabelFrame(__self__.master, text="Peakmethod options", padx=15, pady=15)
        __self__.GeneralOptions.grid(row=0,column=0,padx=(15,15),sticky=N+S+W+E)
        __self__.PeakOptions.grid(row=1,column=0,padx=(15,15),sticky=N+S+W+E)
        __self__.RAM_tot = convert_bytes(sys_mem["total"])
        __self__.RAM_free = convert_bytes(sys_mem["available"])

        __self__.build_widgets()
        place_center(parent.master,__self__.master)
        __self__.master.grab_set()
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)

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
        __self__.RAMEntry.set("%.2f"%(float(convert_bytes(Constants.ROOT.RAM_limit_value).split(" ")[0])))
        __self__.RAMUnit.set(convert_bytes(Constants.ROOT.RAM_limit_value).split(" ")[1])
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

        CoreOption = ttk.Checkbutton(__self__.GeneralOptions, 
                variable=__self__.CoreMode,
                text="Yes",
                takefocus=False,
                command=__self__.toggle_multicore)

        CoreCountLabel = Label(__self__.GeneralOptions,
                text="Total number of cores: "+str(__self__.CoreCount),
                relief=GROOVE)
        
        __self__.RAMLabel = Label(__self__.GeneralOptions,text="Limit RAM in Multi-Core? ")

        __self__.RAMUnitLabel = Label(__self__.GeneralOptions, text=__self__.RAMUnit.get())

        __self__.RAMOption = ttk.Checkbutton(__self__.GeneralOptions, 
                variable=__self__.RAMMode,
                text="Yes",
                takefocus=False,
                command=__self__.toggle_ram)

        __self__.RAMEntryBox = Entry(__self__.GeneralOptions, 
                textvariable=__self__.RAMEntry,
                width=10)

        __self__.RAMCountLabel = Label(__self__.GeneralOptions,
                text="Available RAM: "+str(__self__.RAM_free))

        WlcmLabel = Label(__self__.GeneralOptions,text="Welcome message at startup? ")

        WlcmOption = ttk.Checkbutton(__self__.GeneralOptions, 
                takefocus=False,
                text = "Yes",
                variable=__self__.WlcmMode)

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
        ToleranceEntry1 = ttk.Entry(__self__.PeakOptions, 
                textvariable=__self__.TolVar1,
                width=7)

        ToleranceEntry2 = ttk.Entry(__self__.PeakOptions, 
                textvariable=__self__.TolVar2,
                width=7)

        ToleranceEntry3 = ttk.Entry(__self__.PeakOptions, 
                textvariable=__self__.TolVar3,
                width=7)

        # LABELS #
        AutoWizardLabel = Label(__self__.PeakOptions, text="Auto wizard parameters ",relief=GROOVE)
        FitCycles = Label(__self__.PeakOptions, text="Fit cycles/spectrum: ")
        PeakFindTolerance = Label(__self__.PeakOptions, text="Peakfind sensitivity: ")
        ContSupprLabel = Label(__self__.PeakOptions, text="Continuum suppression factor: ")
        PeakCheckTolerance = Label(__self__.PeakOptions, text="Peakfind tolerance: ")
        PeakCheckLabel = Label(__self__.PeakOptions, text="*gain")
        __self__.PlotSaveInterval = Label(__self__.PeakOptions, text="Save plots w/ interval: ")
        PlotSave = Label(__self__.PeakOptions, text="Save fit plots? ")

        # ENTRIES #
        FitCyclesEntry = ttk.Entry(__self__.PeakOptions, 
                textvariable=__self__.CycVar,
                width=13)

        PeakFindEntry = ttk.Entry(__self__.PeakOptions,
                textvariable=__self__.Sensitivity,
                width=13)
    
        ContSupprEntry = ttk.Entry(__self__.PeakOptions,
                textvariable=__self__.ContSuppr,
                width=13)

        PeakCheckEntry = ttk.Entry(__self__.PeakOptions,
                textvariable=__self__.WizTol,
                width=7)

        __self__.PlotSaveIntervalEntry = ttk.Entry(__self__.PeakOptions, 
                textvariable=__self__.PlotSaveVar,
                width=13)

        PlotSaveBool = ttk.Checkbutton(__self__.PeakOptions, 
                takefocus=False,
                text = "Yes",
                variable=__self__.PlotSaveBoolVar,
                command=__self__.toggle_save_plot)

        # BUTTONS #
        ButtonsFrame = Frame(__self__.master, padx=10, pady=10)
        OKButton = ttk.Button(
                ButtonsFrame, 
                text="OK", 
                width=10,
                takefocus=False,
                command=__self__.save_settings)
    
        CancelButton = ttk.Button(
                ButtonsFrame, 
                text="Cancel", 
                width=10,
                takefocus=False,
                command=__self__.kill_window)

        PlotLabel.grid(row=0,column=0,sticky=W)
        PlotOption.grid(row=0,column=1,columnspan=2,sticky=E)
        ColorMapLabel.grid(row=1,column=0,sticky=W)
        ColorMapOption.grid(row=1,column=1,columnspan=2,sticky=E)
        CoreLabel.grid(row=3,column=0,sticky=W)
        CoreOption.grid(row=3,column=1,columnspan=2,sticky=E)
        CoreCountLabel.grid(row=2,column=0,columnspan=12,sticky=N+S+W+E,pady=(10,0))
        __self__.RAMLabel.grid(row=4,column=0,sticky=W)
        __self__.RAMUnitLabel.grid(row=5,column=2,sticky="")
        __self__.RAMOption.grid(row=4,column=1,columnspan=2,sticky=E)
        __self__.RAMEntryBox.grid(row=5,column=1,sticky=E)
        __self__.RAMCountLabel.grid(row=5,column=0,sticky=W)
        WlcmLabel.grid(row=6,column=0,sticky=W)
        WlcmOption.grid(row=6,column=1,columnspan=2,sticky=E)
        ToleranceLabel.grid(row=0,column=0,columnspan=3,sticky=N+S+W+E,pady=(0,10))
        Tolerance1.grid(row=1,column=0,sticky=W)
        Tolerance2.grid(row=2,column=0,sticky=W)
        Tolerance3.grid(row=3,column=0,sticky=W)
        ToleranceEntry1.grid(row=1,column=1,sticky=W)
        ToleranceEntry2.grid(row=2,column=1,sticky=W)
        ToleranceEntry3.grid(row=3,column=1,sticky=W)
        ToleranceDescription1.grid(row=1,column=2,sticky=E)
        ToleranceDescription2.grid(row=2,column=2,sticky=E)
        ToleranceDescription3.grid(row=3,column=2,sticky=E)
        AutoWizardLabel.grid(row=4,column=0,columnspan=3,sticky=N+S+W+E,pady=(10,10))
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
        PlotSaveBool.grid(row=10,column=1,columnspan=2,sticky=E)
        ButtonsFrame.grid(row=4,column=0,columnspan=2)
        OKButton.grid(row=4,column=0)
        CancelButton.grid(row=4,column=1)

        create_tooltip(ContSupprLabel,"Suppresses misleading peaks, usually occasioned by a low peakfind sensitivity.\nHigher values will suppress more peaks.")
        create_tooltip(ContSupprEntry,"Suppresses misleading peaks, usually occasioned by a low peakfind sensitivity.\nHigher values will suppress more peaks.")
        create_tooltip(PeakFindTolerance,"Works best when set closer to the peaks FWHM average.\nLower values usually yield more peaks.")
        create_tooltip(PeakFindEntry,"Works best when set closer to the peaks FWHM average.\nLower values usually yield more peaks.")

        ###########################
        
        __self__.GeneralOptions.grid_columnconfigure(0,weight=1,pad=32)
        __self__.PeakOptions.grid_columnconfigure(0,weight=1,pad=32)

        __self__.toggle_ram()
        __self__.toggle_multicore()
        __self__.toggle_save_plot()
        return

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
        elif __self__.RAMMode.get():
            __self__.RAMMode.set(0)
            __self__.RAMLabel.config(state=DISABLED)
            __self__.RAMOption.config(state=DISABLED)
            __self__.RAMUnitLabel.config(state=DISABLED)
            __self__.RAMEntryBox.config(state=DISABLED)
            __self__.RAMCountLabel.config(state=DISABLED)
        else:
            __self__.RAMLabel.config(state=DISABLED)
            __self__.RAMOption.config(state=DISABLED)
            __self__.RAMUnitLabel.config(state=DISABLED)
            __self__.RAMEntryBox.config(state=DISABLED)
            __self__.RAMCountLabel.config(state=DISABLED)
    
    def write_to_ini(__self__):
        try: 
            inipath = os.path.join(sp.__BIN__,"settings.tag")
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
            Constants.ROOT.master.destroy()

    def kill_window(__self__, e=""):
        try: 
            __self__.master.grab_release()
            __self__.master.destroy()
        except: pass

    def save_settings(__self__):
        Constants.RAM_LIMIT = __self__.RAMMode.get()
        Constants.ROOT.RAM_limit_value = restore_bytes(
                float(__self__.RAMEntry.get()),
                __self__.RAMUnit.get())
        Constants.COLORMAP = __self__.ColorMapMode.get()
        Constants.MULTICORE = __self__.CoreMode.get()
        Constants.PLOTMODE = __self__.PlotMode.get()
        if Constants.PLOTMODE == "Logarithmic": Constants.PLOTSCALE = "-semilogy"
        else: Constants.PLOTSCALE = None

        Constants.WELCOME = __self__.WlcmMode.get()

        Constants.SETROI_TOLERANCE = [__self__.TolVar1.get(),
                __self__.TolVar2.get(),__self__.TolVar3.get()]
        Constants.FIT_CYCLES = int(__self__.CycVar.get())
        Constants.PEAK_TOLERANCE = float(__self__.Sensitivity.get())
        Constants.CONTINUUM_SUPPRESSION = float(__self__.ContSuppr.get())
        Constants.CHECK_TOLERANCE = float(__self__.WizTol.get())
        Constants.SAVE_INTERVAL = int(__self__.PlotSaveVar.get())
        Constants.SAVE_FIT_FIGURES = __self__.PlotSaveBoolVar.get()

        refresh_plots()
        try: __self__.parent.clipper.refresh_plot() 
        except: pass
        __self__.write_to_ini()
        __self__.parent.refresh_all_plots()


class MainGUI:
    def __init__(__self__):
        __self__.master = Tk()
        __self__.master.attributes("-alpha",0.0)
        __self__.master.configure(bg=Constants.DEFAULTBTN_COLOR)
        __self__.master.iconbitmap(os.path.join(os.getcwd(),"images","icons","icon.ico"))
        __self__.master.title("XISMuS {}".format(Constants.VERSION))

    def load_cube(__self__):
        load_cube()

    def boot(__self__, database):
        if Constants.LOW_RES == "extreme": 
            quit = messagebox.showinfo("WARNING",
        "Your screen resolution is too low! XISMuS lowest supported resolution is 800x600.")
            if quit == "ok": sys.exit(1)
        Constants.LOGGER.info("Initializing program...")
        f = open(os.path.join(sp.__BIN__,"settings.tag"),"r")
        for line in f:
            if line.startswith("<welcome>"):
                if line.split("\t")[1] == "True": 
                    Constants.WELCOME = True
                else: 
                    Constants.WELCOME = False
        f.close()
        
        Theme.apply_theme(__self__)
        __self__.find_elements_diag = None
        __self__.ImageAnalyzers = [] 
        __self__.ConfigDiag = None
        __self__.sample_figure = Figure(figsize=(4,3), dpi=75)
        __self__.sample_plot =__self__.sample_figure.add_subplot(111)
        __self__.sample_plot.grid(b=None)
        __self__.sample_plot.axis('off')
        sys_mem = dict(virtual_memory()._asdict())
        inipath = os.path.join(sp.__BIN__,"settings.tag")

        set_settings(inipath)

        __self__.RAM_limit_value = sys_mem["available"]
        
        #####################################################################
        # Spawn splash screen and look for samples under the search folder  #
        # set at folder.ini # It also check the database.dat file to avoid  #
        # reading thousands of files that were read before at some time     #
        #####################################################################

        __self__.SampleLoader = database

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

        __self__.build_widgets()
        __self__.plot_canvas.mpl_connect("button_press_event",__self__.pop)
        __self__.plot_canvas_popup = Menu(__self__.master, tearoff=0)
        __self__.plot_canvas_popup.add_command(
                label="Export as *.h5 . . .",
                command=__self__.h5writer)
        __self__.plot_canvas_popup.add_command(
                label="Save density map as . . .",
                command=__self__.export_density_map)
        __self__.plot_canvas_popup.add_command(
                label="Open files location",
                command=__self__.open_files_location_from_cube)
        __self__.plot_canvas_popup.add_command(
                label="Open output folder",
                command=__self__.open_output_folder_from_cube)
        __self__.plot_canvas_popup.add_command(
                label="Clear all maps",
                command=__self__.wipe_maps)

        __self__.toggle_(toggle='off')
        __self__.master.update_idletasks()
        __self__.master.after( 1000, __self__.master.attributes, "-alpha", 1.0 )
        __self__.master.focus_set()
        __self__.master.focus_force()
        __self__.master.after( 1500, __self__.pop_welcome )
        __self__.master.minsize( __self__.master.winfo_width(), __self__.master.winfo_height() + 150 )
        __self__.master.deiconify()
        __self__.master.state("zoomed")
        return

    def build_widgets(__self__):
        magnifier_icon = PhotoImage(data=ICO_MAGNIFIER)
        __self__.MAG_ICON = magnifier_icon.subsample(1,1)

        # define the frame and layout
        __self__.ButtonsFrame = Frame(__self__.master)
        __self__.ImageCanvas = Canvas(__self__.master,
                width=205, height=205,
                bg='black', relief=SUNKEN, bd=5)
        __self__.ImageCanvas.config(state=DISABLED)

        __self__.magnifier = Button(__self__.master,
                image=__self__.MAG_ICON,
                bg="white", bd=1,
                command=__self__.magnify)

        __self__.DataFrame = ttk.Frame(__self__.master)
        __self__.DataBox = ttk.LabelFrame(__self__.DataFrame, text="Information:", width=320)

        __self__.StatusScroller = ttk.Scrollbar(__self__.DataBox)
        __self__.StatusBox = Listbox(__self__.DataBox, 
                yscrollcommand=__self__.StatusScroller.set,
                bd=0,
                bg=Theme.BG["Listbox"],
                fg=Theme.FG["Listbox"],
                highlightthickness=0)
        __self__.StatusBox.bind("<Double-Button-1>", __self__.load_map_from_click)

        __self__.ConfigFrame = ttk.LabelFrame(
                __self__.DataFrame,
                text="Configuration: ")
         
        # start matplotlib call inside __self__.ImageCanvas
        blank_image = np.zeros([1,1])
        __self__.plot_canvas = FigureCanvasTkAgg(__self__.sample_figure,__self__.ImageCanvas)
        __self__.plot_canvas.draw()
        __self__.draw_map()

        # define the tables which go inside the DataFrame (bottom left corner)
        __self__.TableLabel2 = ttk.Label(__self__.ConfigFrame,text="Value")
        __self__.TableLabel3 = ttk.Label(__self__.ConfigFrame,text="Configuration")
        __self__.TableLeft = Listbox(__self__.ConfigFrame, bd=0,
                highlightthickness=0,
                bg=__self__.master.cget("background"))
        __self__.TableMiddle = Listbox(__self__.ConfigFrame, 
                width=int(__self__.TableLeft.winfo_reqwidth()/3), bd=0, 
                highlightthickness=0,
                bg=__self__.master.cget("background"))
        re_configure_icon = PhotoImage(data=ICO_REFRESH)
        __self__.re_configure_icon = re_configure_icon.subsample(1,1)
        __self__.re_configure = ttk.Button(
                __self__.ConfigFrame, 
                style="main.TButton",
                image=__self__.re_configure_icon, 
                width=32, 
                takefocus=False,
                command=__self__.reconfigure)

        #####
        # define the menu bar

        __self__.MenuBar = Menu(__self__.master,tearoff=0)
        __self__.Toolbox = Menu(__self__.MenuBar,tearoff=0)
        __self__.Extra = Menu(__self__.MenuBar,tearoff=0)
        __self__.derived_spectra = Menu(__self__.Toolbox,tearoff=0)

        __self__.MenuBar.add_cascade(label="Toolbox", menu=__self__.Toolbox)
        __self__.MenuBar.add_cascade(label="Extra", menu=__self__.Extra)
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
        __self__.Toolbox.add_command(label="Export datacube as h5 . . .", 
                command=__self__.h5writer)
        __self__.Toolbox.add_command(label="Reset sample", 
                command=__self__.reset_sample)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_command(label="Change samples folder . . .", 
                command=__self__.prompt_folder)
        __self__.Toolbox.add_command(label="Load file selection . . .",
                command=__self__.load_file_batch)
        __self__.Toolbox.add_command(label="Load h5 file . . .",
                command= lambda: __self__.h5loader(ftype="h5"))
        __self__.Toolbox.add_command(label="Load EDF stack . . .",
                command= lambda: __self__.h5loader(ftype="edf"))
        __self__.Toolbox.add_command(label="Load ftir data [experimental] . . .",
                command= lambda:__self__.load_file_batch(ftir=1))
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
        __self__.Toolbox.add_command(label="Create Mosaic . . .", 
                command=__self__.open_mosaic)
        __self__.Toolbox.add_command(label="Load Mosaic . . .", 
                command=__self__.prompt_mosaic_load_file)
        __self__.Toolbox.add_command(label="Image Analyzer . . .", 
                command=__self__.open_analyzer)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_command(label="Settings", command=__self__.call_settings)
        __self__.Toolbox.add_command(label="Exit", command=__self__.root_quit)
        __self__.Extra.add_command(label="Cube Viewer . . .", command=__self__.cube_viewer)
        __self__.Extra.add_command(label="Differential Attenuation . . .", command=__self__.call_height_mapping)
        __self__.master.config(menu=__self__.MenuBar)
        
        #####
        # define the buttons which go inside the ButtonsFrame (top left corner)
        
        subx,suby = 1,1 #icon resize factor
        
        # load icons
        ButtonLoad_icon = PhotoImage(data=ICO_MOSAIC)
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
        __self__.ButtonLoad = ttk.Button(
                __self__.ButtonsFrame, 
                #text="  Create Mosaic", 
                image=__self__.ButtonLoad_icon, 
                style="main.TButton",
                #compound=LEFT, 
                #width=15,
                command=__self__.open_mosaic)
        __self__.ButtonReset =ttk.Button(
                __self__.ButtonsFrame, 
                #text="  Reset Sample", 
                image=__self__.ButtonReset_icon, 
                style="main.TButton",
                #compound=LEFT, 
                #width=15,
                command=__self__.reset_sample)
        __self__.ImgAnalButton =ttk.Button(
                __self__.ButtonsFrame, 
                #text="  Image Analyzer", 
                image=__self__.ImgAnalButton_icon, 
                style="main.TButton",
                #compound=LEFT, 
                #width=15,
                command=__self__.open_analyzer)
        __self__.FindElementButton =ttk.Button(
                __self__.ButtonsFrame, 
                #text="  Map Elements", 
                image=__self__.FindElementButton_icon, 
                style="main.TButton",
                #compound=LEFT, 
                #width=15,
                command=__self__.find_elements)
        __self__.QuitButton =ttk.Button(
                __self__.ButtonsFrame, 
                #text="  Quit", 
                image=__self__.QuitButton_icon, 
                style="main.TButton",
                #compound=LEFT, 
                #width=15,
                command=__self__.root_quit)
        __self__.SettingsButton =ttk.Button(
                __self__.ButtonsFrame, 
                #text="  Settings", 
                image=__self__.SettingsButton_icon, 
                style="main.TButton",
                #compound=LEFT, 
                #width=15,
                command=__self__.call_settings)
        
        create_tooltip(__self__.ButtonLoad,"Create a new Mosaic (Alt-M)")
        create_tooltip(__self__.ButtonReset,"Reset loaded sample (Alt-R)")
        create_tooltip(__self__.ImgAnalButton,"Open Image Analyzer (Alt-A)")
        create_tooltip(__self__.FindElementButton,"Create maps (Alt-E)")
        create_tooltip(__self__.SettingsButton,"Settings (Alt-S)")
        create_tooltip(__self__.QuitButton,"Exit")

        __self__.master.bind("<Alt-m>",__self__.open_mosaic)
        __self__.master.bind("<Alt-r>",__self__.reset_sample)
        __self__.master.bind("<Alt-a>",__self__.open_analyzer)
        __self__.master.bind("<Alt-e>",__self__.find_elements)
        __self__.master.bind("<Alt-s>",__self__.call_settings)
        #####

        __self__.SampleVar = StringVar()
        __self__.SearchText = StringVar()
        __self__.SearchText.trace("w",__self__.search_samples)

        __self__.SampleVar.set("Sample on memory: "+Constants.DIRECTORY)
        __self__.StatusBar = Label(
                __self__.master, 
                textvariable=__self__.SampleVar,
                bd=1, 
                relief=SUNKEN, 
                anchor=W)
        __self__.master.protocol("WM_DELETE_WINDOW", __self__.root_quit)

        __self__.SamplesWindow = ttk.LabelFrame(__self__.DataFrame, text="Samples")
        __self__.SamplesFilters = ttk.Frame(__self__.SamplesWindow)

        __self__.sort_mode = True
        __self__.SamplesSort = Button(__self__.SamplesFilters, 
                text="Sort A-Z", 
                font=tkFont.Font(family="Tahoma",size=8,underline=1),
                bd=0,
                bg=Theme.BG["Button"],
                fg=Theme.FG["Button"],
                command=__self__.sort_samples)
        __self__.SamplesSearch = ttk.Entry(__self__.SamplesFilters, 
                textvariable=__self__.SearchText, 
                width=27)

        __self__.SampleScroller = ttk.Scrollbar(__self__.SamplesWindow)
        __self__.SamplesWindow_TableLeft = Listbox(
                __self__.SamplesWindow,
                yscrollcommand=__self__.SampleScroller.set,
                height=__self__.SamplesWindow.winfo_height(),
                width=28,
                cursor="hand2",
                bg=Theme.BG["Listbox"],
                fg=Theme.FG["Listbox"],
                bd=1)
        __self__.SamplesWindow_TableRight = Listbox(
                __self__.SamplesWindow,
                height=__self__.SamplesWindow.winfo_height(),
                bd=0)
        __self__.SamplesWindow_multi = Button(
                __self__.SamplesWindow,
                text = "Export multiple maps",
                bd=2,
                bg=Theme.BG["Button"],
                fg=Theme.FG["Button"],
                width=13,
                command=__self__.select_multiple)
        __self__.SamplesWindow_ok = Button(
                __self__.SamplesWindow,
                text = "Validate",
                bd=2,
                bg=Theme.BG["Button"],
                fg=Theme.FG["Button"],
                width=13,
                command=__self__.digestmaps)

        __self__.SamplesWindow_TableLeft.bind("<MouseWheel>", __self__.scroll_y_L)
        __self__.SamplesWindow_TableRight.bind("<MouseWheel>", __self__.scroll_y_R)
        __self__.SamplesWindow_TableLeft.bind("<Up>", __self__.scroll_up)
        __self__.SamplesWindow_TableLeft.bind("<Down>", __self__.scroll_down)
        __self__.SamplesWindow_TableLeft.bind("<Double-Button-1>", __self__.sample_select)
        __self__.SamplesWindow_TableLeft.bind("<Return>", __self__.sample_select)
        __self__.SamplesWindow_TableLeft.bind("<Button-3>", __self__.sample_popup)

        __self__.SamplesWindow_ok.config(state=DISABLED)

        #pop-up commands (rigth-click)
        __self__.SamplesWindow.popup = Menu(__self__.SamplesWindow, tearoff=0)
        __self__.SamplesWindow.popup.add_command(
                label="Load",
                command=__self__.sample_select)
        __self__.SamplesWindow.popup.add_command(
                label="Open files location",
                command=__self__.open_files_location)
        __self__.SamplesWindow.popup.add_command(
                label="Open output folder",
                command=__self__.open_output_folder)
        __self__.SamplesWindow.popup.add_separator()
        __self__.SamplesWindow.popup.add_command(
                label="Delete continuum data",
                command=remove_continuum_data)
        __self__.SamplesWindow.popup.add_command(
                label="Remove from database",
                command=__self__.remove_sample)

        pad = (3,3)
        __self__.ButtonsFrame.grid(row=0, column=0, padx=(32,8+8), pady=(32+8,0), sticky=W)
        __self__.ButtonLoad.grid(row=0,column=0, sticky=W, padx=pad)
        __self__.ButtonReset.grid(row=0,column=1, sticky=W, padx=pad)
        __self__.ImgAnalButton.grid(row=0,column=2, sticky=W, padx=pad)
        __self__.FindElementButton.grid(row=0,column=3, sticky=W, padx=pad)
        __self__.SettingsButton.grid(row=0,column=4, sticky=W, padx=pad)
        __self__.QuitButton.grid(row=0,column=6, sticky=W, padx=pad)

        __self__.ImageCanvas.grid(row=1, column=0, padx=(16+8,8), pady=(32,16),
                sticky=N+W+S+E)
        __self__.magnifier.grid(row=1, column=0, padx=(16+8+3,0), pady=(0,18+1),
                sticky=S+W)

        __self__.DataFrame.grid(row=0, column=1, rowspan=2, 
                padx=(16,8), pady=16, sticky=N+W+E+S)
        __self__.DataBox.grid(row=0, column=0, columnspan=2, 
                padx=16, pady=16, sticky=N+W+E+S)
        __self__.StatusBox.grid(row=0, column=0, sticky=W+E+N+S)
        __self__.StatusScroller.grid(row=0, column=1, sticky=N+S)

        __self__.DataFrame.grid_columnconfigure(0, weight=1, minsize=1)
        __self__.DataBox.grid_columnconfigure(0, weight=1, minsize=1)

        __self__.ConfigFrame.grid(row=1, column=0, columnspan=2, 
                sticky=N+W+E+S, padx=16, pady=(10,0))
        __self__.TableLabel2.grid(row=0, column=0, pady=(3,6))
        __self__.TableLabel3.grid(row=0, column=1, pady=(3,6))
        __self__.TableLeft.grid(row=1, column=0, sticky=N+S, padx=(3,0), pady=(0,3))
        __self__.TableMiddle.grid(row=1, column=1, sticky=N+S, padx=(0,3), pady=(0,3))
        __self__.re_configure.grid(row=1, column=2, sticky=S+W, columnspan=2)
        
        __self__.plot_canvas.get_tk_widget().pack(fill=BOTH, expand=1, padx=3, pady=3)

        __self__.StatusBar.grid(row=3, column=0, columnspan=3, sticky=W+E)

        __self__.SamplesWindow.grid(row=0, column=2, rowspan=2, 
                padx=(8,16+8), pady=(16,0), sticky=N+W+S+E)
        __self__.SamplesFilters.grid(row=0, column=0, columnspan=2, 
                padx=(12,12), pady=(6,0), sticky=N+E+W+S)
        __self__.SamplesFilters.propagate(1)

        __self__.SamplesSort.grid(row=0, column=1, sticky=E)
        __self__.SamplesSearch.grid(row=1, column=0, columnspan=2, padx=(0,20), sticky=E)
        ttk.Label(__self__.SamplesFilters, text="Search").grid(row=0, column=0, sticky=W)
        Button(__self__.SamplesFilters, text="X", 
                font=tkFont.Font(family="Tahoma",weight="bold",size=10), bd=0,
                command=__self__.sort_samples_clear).grid(row=1, column=1, 
                        pady=(0,3), sticky=E)

        __self__.SamplesWindow_TableLeft.grid(row=1, column=0, sticky=N+S, pady=(12,10), 
                padx=(12,0))
        __self__.SampleScroller.grid(row=1, column=1, sticky=N+S, pady=(12,12), padx=(2,12))
        __self__.SamplesWindow_multi.grid(row=2, column=0, columnspan=2, 
                sticky=W+E, pady=(0,2),padx=(12,12))
        __self__.SamplesWindow_ok.grid(row=3, column=0, columnspan=2, 
                sticky=W+E, pady=(2,12),padx=(12,12))
        __self__.SamplesWindow_ok.config(state=DISABLED)

        __self__.ImageCanvas.propagate(1)
        __self__.ButtonsFrame.grid_propagate(1)
        __self__.DataFrame.grid_propagate(1)
        __self__.DataBox.grid_propagate(1)
        __self__.StatusBox.grid_propagate(1)
        __self__.ConfigFrame.grid_propagate(1)
        Grid.rowconfigure(__self__.SamplesWindow, 1, weight=1)
        Grid.rowconfigure(__self__.DataFrame, 0, weight=1)
        Grid.rowconfigure(__self__.DataFrame, 1, weight=1)
        Grid.columnconfigure(__self__.DataFrame, 0, weight=1)
        Grid.columnconfigure(__self__.DataFrame, 1, weight=1)
        Grid.columnconfigure(__self__.SamplesFilters, 0, weight=1)
        Grid.columnconfigure(__self__.SamplesFilters, 1, weight=1)
        Grid.rowconfigure(__self__.DataBox, 0, weight=1)
        Grid.rowconfigure(__self__.ConfigFrame, 1, weight=1)
        Grid.columnconfigure(__self__.ConfigFrame, 0, weight=1)
        Grid.rowconfigure(__self__.TableLeft, 0, weight=1)
        Grid.rowconfigure(__self__.TableMiddle, 0, weight=1)
        __self__.master.grid_columnconfigure(0,weight=2)
        __self__.master.grid_columnconfigure(1,weight=1)
        __self__.master.grid_rowconfigure(1,weight=1)
        __self__.StatusScroller.config(command=__self__.StatusBox.yview)
        __self__.SampleScroller.config(command=__self__.SamplesWindow_TableLeft.yview)

        __self__.SamplesWindow_TableRight.config(state=DISABLED)
        __self__.SamplesWindow_TableLeft.focus_set()

        #writes start-up message:
        hour = int(time.strftime("%H"))
        if 6 <= hour < 12: text=["Good morning, welcome!","Load some data to get started."]
        elif 12 <= hour < 18: text=["Good afternoon!","Load some data to get started."]
        elif 18 <= hour < 23: text=["Good evening!","Load some data to get started."]
        else: text=["Isn't it too late to be looking at data?"]
        text.append("\n")
        for i in text:
            __self__.StatusBox.insert(END, f"{i}")

        __self__.list_samples()
        __self__.StatusBox.focus_set()
        return

    def cube_viewer(__self__):
        if Constants.MY_DATACUBE is None: 
            messagebox.showinfo("No cube!","No datacube is loaded in memory!") 
            return
        path = sp.__PERSONAL__
        __self__.CubeViewer = ImageWindow(__self__, "Cube Viewer", path)

        #If no writing permission is granted, CubeViewer cannot track the user operations
        #with PermissionError, the ImageWindow object fails to spawn and throws an error
        if __self__.CubeViewer.success: 
            __self__.CubeViewer.draw_image(Constants.MY_DATACUBE.densitymap)
            __self__.CubeViewer.create_connection(Constants.MY_DATACUBE)
        else: return

    def call_compilecube(__self__):
        """ Tries to create output folder (name is Constants.CONFIG['directory'])
        and calls SpecMath to compile the data.
        
        If a queued file cannot be read, an error is raised. SpecMath returns the name
        of the file. 
        The funciton is called from the ConfigurationParser.py module """

        try:
            os.mkdir(sp.output_path)
        except IOError as exception:
            Constants.LOGGER.warning("Error {}.".format(exception.__class__.__name__))
            Constants.LOGGER.warning("Can't create output folder {}".format(sp.output_path))

        if os.path.exists(sp.cube_path):
            pass
        else:
            __self__.ButtonLoad.config(state=DISABLED)
            __self__.MenuBar.entryconfig("Toolbox", state=DISABLED)

            ###############################
            # disables the samples window #
            ###############################

            __self__.SamplesWindow_TableLeft.config(state=DISABLED)
            __self__.SamplesWindow_multi.config(state=DISABLED)
            __self__.SamplesWindow_ok.config(state=DISABLED)

            ###############################

            __self__.StatusBox.delete(0,END)
            __self__.StatusBox.insert(END, "\nStarting cube compilation.\n")
            __self__.StatusBox.insert(END, "\nImage size: {} x {}.\n".format(
                __self__.config_xy[0], Constants.ROOT.config_xy[1]))
            __self__.StatusBox.insert(END, "\nSpectra count: {}.\n".format(
                __self__.mcacount[Constants.CONFIG["directory"]]))
            Constants.LOGGER.warning("Starting cube {} compilation!".format(Constants.CONFIG["directory"]))

            ##########################################################################
            # IF LOADING AN H5 FILE, USER CAN COMPILE A DATACUBE OR USE THE H5 AS IS #
            ##########################################################################
            if __self__.mca_extension[Constants.CONFIG["directory"]] == ".h5":
                m = messagebox.askquestion("Attention!",
                        "You can proceed without compiling the H5 file into a datacube, however, it won't be saved to the database nor will be recognized by Mosaic. It is recommended that you COMPILE it into a datacube. To save disk space, you can compress the H5 file later. DO YOU WANT TO CREATE A DATACUBE FILE?")
                dtypes = Constants.MY_DATACUBE.datatypes
                if m == "yes":
                    specbatch = Cube(dtypes,Constants.CONFIG)
                    fail = specbatch.compile_cube()
                    __self__.ButtonLoad.config(state=NORMAL)
                    __self__.MenuBar.entryconfig("Toolbox", state=NORMAL)
                    __self__.temporaryh5 = "None"
                elif m == "no":
                    __self__.busy.busy()
                    Constants.MY_DATACUBE = converth5(dtypes)
                    __self__.samples[Constants.CONFIG["directory"]] = "temp .h5"
                    sp.cube_path = ""
                    __self__.ButtonLoad.config(state=NORMAL)
                    __self__.MenuBar.entryconfig("Toolbox", state=NORMAL)
                    __self__.temporaryh5 = Constants.CONFIG["directory"]
                    __self__.busy.notbusy()

            ##########################################################################

            elif __self__.mca_extension[Constants.CONFIG["directory"]] == ".edf":
                dtypes = Constants.MY_DATACUBE.datatypes
                specbatch = Cube(dtypes,Constants.CONFIG,path=Constants.TEMP_PATH)
                fail = specbatch.compile_cube()
                __self__.ButtonLoad.config(state=NORMAL)
                __self__.MenuBar.entryconfig("Toolbox", state=NORMAL)

            else:

                ############################################################
                # Fills the file pool in case spectra were loaded manually #
                ############################################################

                Constants.FILE_POOL = __self__.samples[Constants.CONFIG["directory"]]

                ############################################################

                if Constants.FTIR_DATA:
                    datatype="ftir"
                else: datatype="mca"
                specbatch = Cube([datatype],Constants.CONFIG)
                fail = specbatch.compile_cube()
                __self__.ButtonLoad.config(state=NORMAL)
                __self__.MenuBar.entryconfig("Toolbox", state=NORMAL)

                ####################################################
                # changes the prefix if sample was loaded manually #
                ####################################################

                if isinstance(Constants.FILE_POOL,tuple):
                    __self__.samples[Constants.CONFIG["directory"]] = \
                    __self__.samples[Constants.CONFIG["directory"]][0].split("/")[-1].split(".")[0]

                ####################################################

                if fail[0] == True:
                    messagebox.showerror("Error!",
                            "Could not read {} file! Aborting compilation".format(fail[1]))
                    shutil.rmtree(sp.output_path)
                    specbatch.progressbar.destroybar()
                    Constants.MY_DATACUBE = None
                    sp.conditional_setup()
                    __self__.SamplesWindow_TableLeft.config(state=NORMAL)
                    __self__.SamplesWindow_multi.config(state=NORMAL)
                    __self__.SamplesWindow_ok.config(state=NORMAL)
                    __self__.list_samples()
                    __self__.toggle_(toggle="off")
                    return

            __self__.SamplesWindow_TableLeft.config(state=NORMAL)
            __self__.SamplesWindow_multi.config(state=NORMAL)
            __self__.SamplesWindow_ok.config(state=NORMAL)
            __self__.toggle_(toggle="on")
            __self__.list_samples()

    def prompt_folder(__self__):
        """ Opens dialogue to change the samples folder """

        folder = filedialog.askdirectory(title="Select the samples folder")
        if folder != "":
            ini_file = open(os.path.join(sp.__BIN__,"folder.ini"),"w")
            ini_file.write(os.path.abspath(folder))
            ini_file.close()
            Constants.SAMPLES_FOLDER = os.path.abspath(folder)
            __self__.refresh_samples()
        else:
            pass
        return 0

    def load_map_from_click(__self__, e=""):
        """ reads the item double clicked and check if it is a map in a cube.
        Displays the image for the user """
        click = __self__.StatusBox.get(ACTIVE)
        listed = Constants.MY_DATACUBE.check_packed_elements()
        for el in listed:
            if el in click:
                image = Constants.MY_DATACUBE.unpack_element( el )
                fullname = Constants.MY_DATACUBE.name + " " + el
                __self__.ClickedMapDisplay = ImageWindow(__self__, fullname, "")
                __self__.ClickedMapDisplay.draw_image(image)
                break
        return
               
    def root_quit(__self__,force=0):
        if force:
            __self__.master.quit()
            del __self__
            gc.collect()
            sys.exit(0)
        r = messagebox.askquestion("Attention","Are you sure you want to exit?")
        if r == "yes":
            for widget in __self__.master.winfo_children():
                #if isinstance(widget, Toplevel):
                try: widget.destroy()
                except: pass
            checkout_config()
            __self__.master.destroy()
            sys.exit(0)
        else: return

    def refresh_all_plots(__self__):
        try:
            __self__.draw_map()
        except: pass
        try:
            for ImgAnal in __self__.ImageAnalyzers:
                try:
                    if hasattr(ImgAnal,"IndexNavigator"):
                        ImgAnal.IndexNavigator.LeftImage.set_cmap(Constants.COLORMAP)
                        ImgAnal.IndexNavigator.PlotCanvasL.draw()
                    ImgAnal.left_image.set_cmap(Constants.COLORMAP)
                    ImgAnal.right_image.set_cmap(Constants.COLORMAP)
                    ImgAnal.canvas1.draw()
                    ImgAnal.canvas2.draw()
                except: pass
        except:
            pass
        return
    
    def toggle_(__self__,toggle='on'):
        if toggle == 'on':
            __self__.master.bind("<Alt-r>",__self__.reset_sample)
            __self__.master.bind("<Alt-a>",__self__.open_analyzer)
            __self__.master.bind("<Alt-e>",__self__.find_elements)
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
            __self__.master.unbind("<Alt-r>")
            __self__.master.unbind("<Alt-a>")
            __self__.master.unbind("<Alt-e>")
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
        if Constants.MY_DATACUBE is not None:
            if any("ftir" in x for x in Constants.MY_DATACUBE.datatypes):
                __self__.master.unbind("<Alt-e>")
                __self__.FindElementButton.state(["disabled"])
                __self__.Toolbox.entryconfig("Map elements",state=DISABLED)
            elif any("temp" in x for x in Constants.MY_DATACUBE.datatypes): 
                __self__.master.unbind("<Alt-r>")
            else:
                __self__.master.bind("<Alt-r>",__self__.reset_sample)
                __self__.master.bind("<Alt-a>",__self__.open_analyzer)
                __self__.FindElementButton.state(["!disabled"])
                __self__.Toolbox.entryconfig("Map elements",state=NORMAL)
        __self__.master.update_idletasks()
    
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
        __self__.list_samples()

    def invoke_wizard(__self__):
        """ This function invokes the auto wizard (BatchFitting)

        --------------------------------------------------------- """

        fit_path = sp.output_path
        
        def call_table(elements):
            __self__.PoolTable = PeriodicTable(Constants.ROOT)
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
                    Constants.ROOT.bar = Busy(1,0)
                    Constants.ROOT.bar.update_text("Building images...")
                    build_images(fit_path,bar=Constants.ROOT.bar)
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
                    Constants.ROOT.Fitter = MultiFit(fit_path)
                else:
                    Constants.ROOT.Fitter = MultiFit(fit_path)
                    Constants.ROOT.Fitter.cores = 1
                if Constants.ROOT.Fitter.bar.KILL: 
                    messagebox.showinfo("ABORTED!","Process aborted by user.")
                    return
                
                save_path = os.path.join(sp.output_path,"peak_find.png")
                __self__.peaks, __self__.matches = Constants.ROOT.Fitter.locate_peaks(path=save_path)

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

                Constants.ROOT.Fitter.bar.destroybar()
                p2 = messagebox.askyesnocancel("Attention!","We have found {} in your sample {}. Do you want to add more elements to the pool?".format(
            message1,Constants.MY_DATACUBE.name))

                if p2 == None:
                    del Constants.ROOT.Fitter
                    return

                elif p2 == True:
                    call_table(elements)
                    return

                elif p2 == False:

                    start_time = time.time()
                    Constants.ROOT.Fitter.launch_workers(
                            Constants.FIT_CYCLES,
                            Constants.SAVE_INTERVAL,
                            Constants.SAVE_FIT_FIGURES)

                    Constants.ROOT.bar = Busy(1,0)
                    Constants.ROOT.bar.update_text("Building images...")
                    build_images(fit_path,bar=Constants.ROOT.bar)
                    del Constants.ROOT.Fitter

                    timestamps = open(os.path.join(sp.__BIN__,"timestamps.txt"),"a")
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

    def find_elements(__self__,e=""):
        mode = Constants.MY_DATACUBE.config["peakmethod"]
        prohibited_methods = ["auto_wizard","fit_approx"]
        if Constants.MY_DATACUBE.config["peakmethod"] in prohibited_methods and\
                any("temp" in x for x in Constants.MY_DATACUBE.datatypes):
                    messagebox.showerror("Error",
                    "Temporarily loaded *.h5 files cannot be fitted! To use this method, reload the corresponding file and try again.")
                    return __self__.master.focus_force()
        elif mode == "auto_wizard":
            __self__.invoke_wizard()
        elif mode == "fit_approx":
            if Constants.SAVE_FIT_FIGURES:
                message = "You have chosen to save the fit outputs. In this case, the approximation of a fit. The saving operation can increase the fitting time considerably. Are you sure you want to proceed?"
            else:
                message = "This operation can take a while depending on the dataset size and cannot be interrupted. Do you want to proceed?"

            question = messagebox.askyesno("Attention!",message)
            if question:
                start_time = time.time()
                __self__.busy.busy()
                if FastFit.fit_and_run() == 0:
                    timestamps = open(os.path.join(sp.__BIN__,"timestamps.txt"),"a")
                    timestamps.write(
                    "\n{4} - {5} APPROX FIT\n{0} bgtrip={1} enhance={2}\n{3} seconds\n".format(
                    Constants.MY_DATACUBE.fit_config["elements"].keys(),
                    Constants.MY_DATACUBE.config["bgstrip"],
                    Constants.MY_DATACUBE.config["enhance"],
                    time.time()-start_time,
                    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                    Constants.MY_DATACUBE.name))
                    timestamps.close()
                __self__.write_stat()
                __self__.busy.notbusy()
            else: return
        else: 
            if mode == "simple_roi":
                messagebox.showinfo("Attention!",
                "Simple roi method does NOT separate peaks. Always verify the Calculated ROI data in the Toolbox menu.")
            try:
                if __self__.find_elements_diag.master.winfo_exists() == False:
                    __self__.find_elements_diag = PeriodicTable(__self__)
                else:
                    __self__.find_elements_diag.master.focus_force()
                    pass
            except:
                __self__.find_elements_diag = PeriodicTable(__self__)
                __self__.find_elements_diag.master.protocol("WM_DELETE_WINDOW",
                        lambda: wipe_list())

    def remove_sample(__self__, e=""):
        try:
            sample = __self__.SamplesWindow_TableLeft.get(ACTIVE)
        except:
            sample = e
        if sample == "" or "Training Data" in sample: 
            messagebox.showinfo("Uh-oh!","It is not possible to remove the Training Data!")
            return

        d = messagebox.askquestion("Attention!",
        "Are you sure you want to remove sample {} from the list? It will not delete the sample data or the compiled datacube.".format(sample))
        
        if d=="yes":
            try:
                Database.remove_entry_from_database([sample])
                __self__.list_samples()
            except KeyError:
                messagebox.showinfo("Compiled cube","This sample is not in the database. The Datacube was added from \"XISMuS\\output\" folder. If you don't want to see this sample, remove it from the output folder manually.")
                return
            del __self__.samples[sample]
            del __self__.samples_path[sample]
            del __self__.mcacount[sample]
            del __self__.mca_indexing[sample]
            del __self__.mca_extension[sample]

            #closes any plot referent to the sample
            try: __self__.summation.master.destroy()
            except: pass
            try: __self__.MPS.master.destroy()
            except: pass
            try: __self__.combined.master.destroy()
            except: pass
            __self__.check_open_analyzers(sample) 

            sp.conditional_setup()
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
            __self__.SamplesWindow_multi.config(relief="raised",fg=Theme.FG["Button"])
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
        _path = os.path.join(sp.__PERSONAL__,"output")
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
            place_center(Constants.ROOT.SamplesWindow.master, __self__.maps_window)
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

        __self__.SamplesWindow_TableLeft.focus_force()
        __self__.SamplesWindow_TableLeft.delete(0,END)
        for key in __self__.samples:
            __self__.SamplesWindow_TableLeft.insert(END,"{}".format(key))
            __self__.SamplesWindow_TableRight.insert(END,"{}".format(\
                    __self__.samples[key]))
        __self__.SamplesWindow_TableLeft.focus_set()

    def sort_samples(__self__, e=""):
        """ Sorts the samples listed in the panel. Only works for the newer interface 2.0,
        where the panel with MCA prefixes does not exist """
        __self__.sort_mode = not __self__.sort_mode
        names = __self__.SamplesWindow_TableLeft.get(0,END)
        names = sorted(names, key=str.casefold, reverse=__self__.sort_mode)
        __self__.SamplesWindow_TableLeft.delete(0,END)
        for name in names:
            __self__.SamplesWindow_TableLeft.insert(END,f"{name}")
        __self__.SamplesWindow_TableLeft.focus_set()

    def sort_samples_clear(__self__, e=""):
        __self__.SearchText.set("")
        __self__.SamplesWindow_TableLeft.delete(0,END)
        names = __self__.samples.keys()
        for name in names:
            __self__.SamplesWindow_TableLeft.insert(END,f"{name}")
        __self__.SamplesWindow_TableLeft.focus_set()

    def search_samples(__self__, var, index, mode):
        __self__.sort_mode = False
        names = __self__.samples.keys()
        __self__.SamplesWindow_TableLeft.delete(0,END)
        search = __self__.SearchText.get().lower()
        results = [name for name in names if name.lower().startswith(search)]
        results = sorted(results)
        for name in results:
            __self__.SamplesWindow_TableLeft.insert(END,f"{name}")

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

    def sample_select(__self__,event="",force=""):
        """ Loads the sample selected from the sample list menu. If the cube is 
        compiled, loads it to memory. If not, the configuration dialog is called """
                
        # name of selected sample
        if force != "": value = force
        else:
            try: 
                value = __self__.SamplesWindow_TableLeft.get(ACTIVE)
            except:
                value = event
            if value == "": return
        
        #############################################################
        # WHEN SELECTING ANOTHER ITEM AND A TEMPORARY H5 IS LOADED, #
        # GET RID OF IT                                             #
        #############################################################
        if Constants.MY_DATACUBE is not None:
            if any("temp" in x for x in Constants.MY_DATACUBE.datatypes) and \
                    value != Constants.MY_DATACUBE.name:
                idx = __self__.SamplesWindow_TableLeft.get(0, END).index(
                        Constants.MY_DATACUBE.name)
                del Constants.ROOT.samples[Constants.MY_DATACUBE.name]
                del Constants.ROOT.samples_path[Constants.MY_DATACUBE.name]
                del Constants.ROOT.mcacount[Constants.MY_DATACUBE.name]
                del Constants.ROOT.mca_indexing[Constants.MY_DATACUBE.name]
                del Constants.ROOT.mca_extension[Constants.MY_DATACUBE.name]
                Constants.ROOT.temporaryh5 = "None"
                gc.collect()
                __self__.SamplesWindow_TableLeft.delete(idx)
                __self__.SamplesWindow_TableRight.config(state=NORMAL)
                __self__.SamplesWindow_TableRight.delete(idx)
                __self__.SamplesWindow_TableRight.config(state=DISABLED)
                __self__.SamplesWindow_TableRight.update_idletasks()
                temp_path = os.path.join(
                    sp.__PERSONAL__,"output",Constants.MY_DATACUBE.name)
                if os.path.exists(temp_path):
                    shutil.rmtree(temp_path)
        #############################################################

        __self__.master.deiconify()
        __self__.master.focus_set()
        if Constants.ROOT.samples[value] == "temp .h5":
            return
        for widget in __self__.master.winfo_children():
            if isinstance(widget, Toplevel): 
                try: 
                    if widget.tagged == True: widget.destroy()
                except:
                    pass
        __self__.toggle_(toggle="off")
         
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
        
        local_cube_path = os.path.join(sp.workpath,"output",value,value+".cube")
        if os.path.exists(local_cube_path): 
            sp.cube_path = os.path.join(sp.workpath,"output",value,value+".cube")
            try: load_cube()
            except: return
            sp.setup_from_datacube(Constants.MY_DATACUBE,__self__.samples)
            __self__.SampleVar.set("Sample on memory: "+Constants.SAMPLE_PATH)
            __self__.toggle_(toggle="on")    
            __self__.write_stat()   
            __self__.draw_map()
        else: 
            if "Example Data" in value: path="auto"
            else: path=Constants.ROOT.samples_path[value]
            sp.conditional_setup(name=value,path=path)
            __self__.call_configure()

    def wipe_maps(__self__,e=""):
        if hasattr(Constants.MY_DATACUBE,"name"):
            pass
        else: 
            messagebox.showerror("No datacube!","Please load a datacube first.")
            return

        p = messagebox.askquestion("Attention!",
                "This will remove all elemental maps packed in datacube {}. Are you sure you want to proceed?".format(Constants.MY_DATACUBE.name))
        if p == "yes":
            __self__.master.config(cursor="watch")
            Constants.MY_DATACUBE.wipe_maps()
            __self__.check_open_analyzers(Constants.MY_DATACUBE.name)
            __self__.write_stat()
            __self__.master.config(cursor="arrow")
        else: return 0

    def check_open_analyzers(__self__, *args):
        """ closes all Image Analyzers open for names passed as argument 
        INPUT: strings;
        OUTPUT: 2D-list;
        """
        alive = []
        killed = []
        for ImgAnal in __self__.ImageAnalyzers:
            alive.append(ImgAnal.DATACUBE.name)
            if ImgAnal.DATACUBE.name in args:
                alive.remove(ImgAnal.DATACUBE.name)
                killed.append(ImgAnal.DATACUBE.name)
                ImgAnal.kill()
        return alive, killed

    def pop_welcome(__self__):
        """Displays a pop-up window with information on the software"""
        if Constants.WELCOME == True:
            __self__.welcome_window = Welcome(__self__)
            place_center(__self__.master, __self__.welcome_window.master)
            __self__.welcome_window.master.grab_set()
        return

    def sample_popup(__self__,event):
        """Call the right-click menu for SampleList"""

        __self__.SamplesWindow_TableLeft.select_clear(0,END)
        idx = __self__.SamplesWindow_TableLeft.nearest(event.y)
        __self__.SamplesWindow_TableLeft.select_set(idx)
        __self__.SamplesWindow_TableLeft.activate(idx)

        name = __self__.SamplesWindow_TableRight.get(idx)
        if "temp" in name:
            __self__.SamplesWindow.popup.entryconfig("Load", state=DISABLED)
            __self__.plot_canvas_popup.entryconfig("Clear all maps", state=DISABLED)
            __self__.plot_canvas_popup.entryconfig("Export as *.h5 . . .", state=DISABLED)
            __self__.SamplesWindow.popup.entryconfig("Remove from database", state=DISABLED)
        else:
            __self__.SamplesWindow.popup.entryconfig("Load", state=NORMAL)
            __self__.plot_canvas_popup.entryconfig("Clear all maps", state=NORMAL)
            __self__.plot_canvas_popup.entryconfig("Export as *.h5 . . .", state=NORMAL)
            __self__.SamplesWindow.popup.entryconfig("Remove from database", state=NORMAL)

        try: __self__.SamplesWindow.popup.tk_popup(event.x_root, event.y_root, entry="")
        finally: __self__.SamplesWindow.popup.grab_release()
    
    def draw_map(__self__):
        try: 
            __self__.sample_plot.imshow(Constants.MY_DATACUBE.densitymap, 
                    cmap=Constants.COLORMAP, 
                    vmin=0,
                    vmax=Constants.MY_DATACUBE.densitymap.max(),)
            __self__.plot_canvas.draw_idle()
        except: 
            __self__.sample_plot.imshow(np.ones([20,20]), cmap=Constants.COLORMAP,
                    vmin=0,
                    vmax=1)
            __self__.plot_canvas.draw_idle()
    
    def open_files_location_from_cube(__self__,event=""):
        try:
            value = Constants.MY_DATACUBE.name
        except:
            messagebox.showerror("No datacube!","Please load a datacube first.")
            return
        local_cube_path = os.path.join(sp.workpath,"output",value,value+".cube")
        if os.path.exists(local_cube_path):
            path = Constants.MY_DATACUBE.path
            path = os.path.realpath(path)
            try: os.startfile(path)
            except: 
                messagebox.showinfo("Directory not found.",
                        "Sample files not found! Path {} couldn't be located.\nRemember that merged Datacubes have no files path. Check the output folder instead.".format(path))
                return
    
    def open_output_folder_from_cube(__self__, event=""):
        try:
            value = Constants.MY_DATACUBE.name
        except:
            messagebox.showerror("No datacube!","Please load a datacube first.")
            return
        path = os.path.join(sp.__PERSONAL__,"output",value)
        if os.path.exists(path):
            path = os.path.realpath(path)
            os.startfile(path)
        else:
            messagebox.showinfo("Directory not found.",
                    "Sample may be uncompiled. Output directory for sample {} not found.".format(value))
    
    def open_files_location(__self__, event=""):
        value = __self__.SamplesWindow_TableLeft.get(ACTIVE)
        local_cube_path = os.path.join(sp.workpath,"output",value,value+".cube")
        path = Constants.ROOT.samples_path[value]
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
        path = os.path.join(sp.__PERSONAL__,"output",value)
        if os.path.exists(path):
            path = os.path.realpath(path)
            os.startfile(path)
        else:
            messagebox.showinfo("Directory not found.",
                    "Sample may be uncompiled. Output directory for sample {} not found.".format(value))

    def export_density_map(__self__,event=""):
        """
        try:
            actv = Constants.ROOT.SamplesWindow_TableLeft.get(ACTIVE)
            curr = Constants.MY_DATACUBE.name
            if actv == curr:
                pass
            else:
                __self__.sample_select(event)
        finally: 
            try: 
                if  event.cget("text") == "Save density map as . . .":
                    pass
                else:
                    __self__.sample_select(event)
            except: 
        """
        if Constants.MY_DATACUBE == None:
            messagebox.showerror("No datacube!","Please load a datacube first.")
            return
        if os.path.exists(sp.cube_path) or hasattr(Constants.MY_DATACUBE,"densitymap"): 
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
        sp.conditional_setup()
        load_cube()
        __self__.write_stat()
        __self__.draw_map()
        __self__.toggle_(toggle='off')
        __self__.SampleVar.set("Sample on memory: None")
        try: 
            if __self__.SamplesWindow.state() == "normal": 
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
        __self__.converterGUI = Convert_File_Name(__self__) 

    def h5writer(__self__):
        spp.write(__self__)

    def h5loader(__self__, ftype=None):
        if ftype is None: return
        else: spp.load(__self__, ftype=ftype)

    def load_file_batch(__self__,**kwargs):
        #1 prompt for files
        if "ftir" in kwargs:
            Constants.FTIR_DATA = 1
            file_batch = filedialog.askopenfilenames(parent=__self__.master,
                title="Select FTIR spectra",
                filetype=[
                    ("Comma Separated Values", "*.csv")])
            if file_batch == "": 
                Constants.FTIR_DATA = 0
                return
        else:
            file_batch = filedialog.askopenfilenames(parent=__self__.master, 
                    title="Select spectra",                        
                    filetypes=(
                        ("MCA files", "*.mca"),
                        ("Text files", "*.txt"),
                        ("All files", "*.*")))
            if file_batch == "": return
        wipe_stats(__self__)
        
        #1.1 get the name of parent directory
        try: sample_name = str(file_batch[0]).split("/")[-2]
        except IndexError: messagebox.showerror("No parent folder!","No parent folder detected. Be sure the spectra files are under a common folder (Hard drives are not parent folders!)")

        #2 setup variables in sp and GUI
        path = str(file_batch[0]).split("/")
        path.pop(-1)
        conc_path = ""
        for i in path:
            conc_path += i+"\\"
        conc_path = os.path.abspath(conc_path)
        sp.conditional_setup(name=sample_name,path=conc_path)
        __self__.mcacount[sample_name] = len(file_batch)
        """ samples dict attribute is always a string, except in this particular case """
        __self__.samples[sample_name] = file_batch
        __self__.samples_path[sample_name] = conc_path
        __self__.mca_indexing[sample_name] = file_batch[0].split(".")[0]
        __self__.mca_extension[sample_name] = "---"
        Constants.FIRSTFILE_ABSPATH = file_batch[0]

        #3 ask for a sample name and dimension (modified dimension diag)
        try: 
            __self__.config_xy = sp.getdimension()
            __self__.ManualParam = []
        except:
            dimension = DimensionDiag(__self__)
            __self__.master.wait_window(dimension.master) 
            if dimension.exit_code == "cancel":
                __self__.wipe()
                return 0
            __self__.ManualParam = []
                
        # calls the configuration window
        __self__.ConfigDiag = ConfigDiag(__self__,
                matrix=np.zeros([1,1,1],dtype="int32"))
        __self__.ConfigDiag.build_widgets()
        
    def plot_ROI(__self__):
        ROI_plot = PlotWin(__self__)
        ROI_plot.draw_ROI()

    def plot_calibration_curve(__self__):
        calibration_plot = PlotWin(__self__)
        calibration_plot.draw_calibration()
    
    def call_summation(__self__):
        __self__.summation = PlotWin(__self__)
        __self__.summation.draw_spec(
                mode=['summation'],
                display_mode=Constants.PLOTSCALE,
                lines=False)
        spawn_center(__self__.summation.master)
    
    def call_mps(__self__):
        __self__.MPS = PlotWin(__self__)
        __self__.MPS.draw_spec(
                mode=['mps'],
                display_mode=Constants.PLOTSCALE,
                lines=False)
        spawn_center(__self__.MPS.master)
    
    def call_combined(__self__):
        __self__.combined = PlotWin(__self__)
        __self__.combined.draw_spec(
                mode=['summation','mps'],
                display_mode=Constants.PLOTSCALE,
                lines=False)
        spawn_center(__self__.combined.master)
    
    def call_author(__self__, e=""):
        try:
            if __self__.AboutWin.master.state() == "normal":
                __self__.AboutWin.master.focus_force()
        except:
            __self__.AboutWin = About()

    def call_settings(__self__,e=""):
        try:
            if __self__.SettingsWin.Settings.winfo_exists() == False:
                __self__.SettingsWin = Settings(__self__)
            else:
                __self__.SettingsWin.Settings.focus_force()
                place_center(__self__.master,__self__.SettingsWin.Settings)
                pass
        except:
            __self__.SettingsWin = Settings(__self__)

    def call_height_mapping(__self__, e=""):
        if Constants.MY_DATACUBE is not None:
            if not hasattr(__self__, "HeighMappingMain"):
                __self__.HeighMappingMain = DifferentialAttenuation.HeighMappingMain( __self__, Constants.MY_DATACUBE )
        else:
            messagebox.showinfo("Uh-oh!", "It appears there is no datacube in memory!")
            return

    def open_mosaic(__self__,e=""):
        CanvasSizeDialog(__self__)
    
    def prompt_mosaic_load_file(__self__):
        f = filedialog.askopenfilename(title="Open mosaic",
                    filetypes=[("Mosaic files","*.mosaic")])
        if f == "": return
        else:
            s = open(f,"r") 
            size = [int(i) for i in s.readlines()[0].split("shape:")[-1].split("x")]
            Mosaic_API(size, Constants.ROOT, loadfile=f)

    def open_analyzer(__self__,e=""):
        API = ImageAnalyzer(__self__,Constants.MY_DATACUBE)
        __self__.ImageAnalyzers.append(API) 

    def reconfigure(__self__):
        ReConfigDiag(__self__.master)
 
    def magnify(__self__):
        __self__.magnified = PlotWin(__self__)
        __self__.magnified.draw_map()
        spawn_center(__self__.magnified.master)
            
    def write_stat(__self__):
        __self__.no_sample = True

        def write_to_subpanel():
            values_cube, values_cfg, values_keys = [],[],[]
            for key in Constants.MY_DATACUBE.config:
                if key == "gain":
                    values_keys.append("Gain")
                    values_cube.append(str(int(float(Constants.MY_DATACUBE.config[key])*1000))+" eV")
                elif key == "bg_settings" and Constants.MY_DATACUBE.config[key] == []:
                    values_keys.append("Bgstrip Settings")
                    values_cube.append("Default values")
                else:
                    values_keys.append(str(key))
                    values_cube.append(str(Constants.MY_DATACUBE.config[key]))
            if hasattr(Constants.MY_DATACUBE,"FN"):
                values_keys.append("Fano")
                values_cube.append(f"{Constants.MY_DATACUBE.FN[0]:.3f}")
                values_keys.append("Noise")
                values_cube.append(f"{Constants.MY_DATACUBE.FN[1]:.3f}")
            for item in range(len(values_cube)):
                __self__.TableLeft.insert(END, "{}".format(values_keys[item]))
                __self__.TableMiddle.insert(END, "{}".format(values_cube[item]))
            return
        
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
                Constants.ROOT.mcacount[Constants.DIRECTORY] = len(files)
                __self__.StatusBox.insert(END, "\nSpectra files folder:\n")
                __self__.StatusBox.insert(END,"{0}\n".format(Constants.MY_DATACUBE.path))
                __self__.StatusBox.insert(END,
                        "{0} spectra found!\n".format(Constants.ROOT.mcacount[Constants.DIRECTORY]))
                __self__.StatusBox.insert(END, 
                        "\nDatacube loaded with {} spectra packed\n".format(
                            Constants.MY_DATACUBE.img_size))
                __self__.no_sample = False
            else:
                Constants.ROOT.mcacount[Constants.DIRECTORY] = Constants.MY_DATACUBE.img_size
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
                    Constants.ROOT.mcacount[Constants.DIRECTORY] = len(files)
                    __self__.StatusBox.insert(END, "\nSpectra files folder:\n")
                    __self__.StatusBox.insert(END,"{0}\n".format(Constants.MY_DATACUBE.path))
                    __self__.StatusBox.insert(END,
                            "{0} spectra found!\n".format(Constants.ROOT.mcacount[Constants.DIRECTORY]))
                    __self__.StatusBox.insert(END,
                            "\nDatacube loaded with {} spectra packed\n".format(
                                Constants.MY_DATACUBE.img_size))
                    __self__.no_sample = False
                else:
                    Constants.ROOT.mcacount[Constants.DIRECTORY] = Constants.MY_DATACUBE.img_size
                    __self__.StatusBox.insert(END, "\nSpectra files folder:\n")
                    __self__.StatusBox.insert(END,"{0}\n".format(Constants.MY_DATACUBE.path))
                    __self__.StatusBox.insert(END,
                            "Path doesn't exist, continuing with datacube information.")
                    __self__.StatusBox.insert(END,
                            "\nDatacube loaded with {} spectra packed\n".format(
                                Constants.MY_DATACUBE.img_size))
                    __self__.no_sample = False

                    if any("h5" in x for x in Constants.MY_DATACUBE.datatypes) and \
                            not os.path.exists(sp.cube_path):
                    
                        ########################################
                        # WRITES THE CONFIGURATION TO SUBPANEL #
                        ########################################
                        write_to_subpanel()
                        __self__.no_sample = False
                        ########################################

            else: 
                try:
                    files = [f for f in os.listdir(Constants.SAMPLE_PATH) \
                                if f.lower().endswith(".mca") or f.lower().endswith(".txt")]
                    __self__.StatusBox.insert(END, "\nLooking for spectra files at:\n")
                    __self__.StatusBox.insert(END,"{0}\n".format(Constants.SAMPLE_PATH))
                    __self__.StatusBox.insert(END, 
                        "\n{} spectra found!\n".format(Constants.ROOT.mcacount[Constants.DIRECTORY]))
                    __self__.no_sample = False
                except: pass

        if os.path.exists(sp.cube_path):
            cube_stats = os.stat(sp.cube_path)
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
            write_to_subpanel()
            #######################################################################
        elif __self__.no_sample == True:
            __self__.StatusBox.insert(END, "No sample configured!") 
            for key in Constants.CONFIG:
                __self__.TableLeft.insert(END,key)
        elif __self__.no_sample == False and Constants.ROOT.temporaryh5 == "None": 
            __self__.StatusBox.insert(END, "Datacube not compiled.") 
            __self__.StatusBox.insert(END, "Please compile the cube first.")
            for key in Constants.CONFIG:
                __self__.TableLeft.insert(END,key)
        else: pass
        __self__.TableLeft.config(state=DISABLED)
        __self__.TableMiddle.config(state=DISABLED)
        return
       
    def reset_sample(__self__,e=""):

        def repack(__self__, sample):
            Constants.LOGGER.warning("Cube {} and its output contents were erased!".format(sample))
            shutil.rmtree(sp.output_path)
            try: x,y,tag_dimension_file = sp.getdimension()
            except OSError as exception:
                tag_dimension_file = False
            if tag_dimension_file == True:
                try: 
                    os.remove(Constants.DIMENSION_FILE)
                    Constants.LOGGER.warning("Custom image dimension was deleted.")
                except: raise PermissionError("Can't delete custom dimension file!")

            # clears all open plot windows
            try: __self__.summation.master.destroy()
            except: pass
            try: __self__.MPS.master.destroy()
            except: pass
            try: __self__.combined.master.destroy()
            except: pass

            __self__.check_open_analyzers(sample) 
            load_cube()
            __self__.write_stat()
            __self__.toggle_(toggle='off')
            __self__.ResetWindow.grab_release()
            __self__.wipe()
            if __self__.mca_extension[sample] == "---": __self__.samples.pop(sample,None)
            elif __self__.mca_extension[sample] == ".h5": __self__.samples.pop(sample,None)
            elif __self__.mca_extension[sample] == ".edf": __self__.samples.pop(sample,None)
            __self__.list_samples()
            __self__.draw_map()
            __self__.ResetWindow.destroy()
            return

        if os.path.exists(sp.cube_path):
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
            EraseLabel = Label(__self__.ResetWindow, image = __self__.Erase_ico).pack(side=LEFT, pady=8, padx=16)
            YesButton = ttk.Button(
                    __self__.ResetWindow, 
                    text="Yes", 
                    command=lambda: repack(
                        __self__,Constants.MY_DATACUBE.name),
                    width=10).pack(side=TOP,pady=5)
            NoButton = ttk.Button(
                    __self__.ResetWindow, 
                    text="No", 
                    command=__self__.ResetWindow.destroy, 
                    width=10).pack(side=TOP, pady=(5,10))
            
            place_center(__self__.master,__self__.ResetWindow)
            icon = os.path.join(os.getcwd(),"images","icons","icon.ico")
            __self__.ResetWindow.iconbitmap(icon)
            __self__.ResetWindow.grab_set()

        else:
            messagebox.showerror("Can't find sample!",
                    "Sample {} could not be located!".format(Constants.MY_DATACUBE.name))

    def call_configure(__self__):
        """ invokes the configuration dialog """

        try: 
            __self__.config_xy = sp.getdimension()
        except:
            dimension = DimensionDiag(__self__)
            __self__.master.wait_window(dimension.master) 
            if dimension.exit_code == "cancel":
                __self__.wipe()
                return 0

        __self__.ManualParam = []
        try: __self__.ConfigDiag.master.destroy()
        except: pass
        __self__.ConfigDiag = ConfigDiag(__self__,
                matrix=np.zeros([1,1,1],dtype="int32"))
        __self__.ConfigDiag.build_widgets()
        

class ReConfigDiag:
    def __init__(__self__, master):
        __self__.master = Toplevel(master = master)
        __self__.master.attributes("-alpha",0.0)
        __self__.master.iconbitmap(os.path.join(os.getcwd(),"images","icons","refresh.ico"))
        __self__.master.resizable(False,False)
        __self__.master.title("Cube Configuration")
        __self__.master.bind("<Escape>",__self__.kill)
        __self__.master.bind("<Return>",__self__.save)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.calibration_params = None
        __self__.Frame = Frame(__self__.master, padx=15, pady=15)
        __self__.MergeSettings = LabelFrame(__self__.master,text="Merged Cube Settings:",padx=15, pady=15)
        __self__.MergeSettings.grid(row=1, column=0, columnspan=2, padx=15, pady=(0,15))
        __self__.Frame.grid(row=0, column=0, padx=15, pady=(0,15))
        __self__.build_widgets()
        place_center(Constants.ROOT.master, __self__.master)
        __self__.master.after(100, __self__.master.attributes, "-alpha", 1.0)
        __self__.master.grab_set()
        return

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

    def check_datatype(__self__):
        if any("ftir" in x for x in Constants.MY_DATACUBE.datatypes):
            __self__.ConfigDiagRatio.state(["disabled"])
            __self__.ConfigDiagMethod.state(["disabled"])
            __self__.ConfigDiagRatio.state(["disabled"])
            __self__.RecalibrateBtn.state(["disabled"])
        else:
            __self__.ConfigDiagRatio.state(["!disabled"])
            __self__.ConfigDiagMethod.state(["!disabled"])
            __self__.ConfigDiagRatio.state(["!disabled"])
            __self__.RecalibrateBtn.state(["!disabled"])
    
    def build_widgets(__self__):
        Label2 = Label(__self__.Frame, text="Area method:")
        Label3 = Label(__self__.Frame, text="Enhance image?")
        Label4 = Label(__self__.Frame, text="Calculate ratios?")
        __self__.Label5 = Label(__self__.MergeSettings, 
                text="Scale data? (for versions < 1.3)")
        __self__.Label6 = Label(__self__.MergeSettings, 
                text="Re-calculate continuum?")
        
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
        
        __self__.ConfigDiagRatio =ttk.Checkbutton(__self__.Frame, 
                takefocus=False,
                text="Yes",
                variable=__self__.RatioVar)
        __self__.ConfigDiagEnhance =ttk.Checkbutton(__self__.Frame, 
                takefocus=False,
                text="Yes",
                variable=__self__.EnhanceVar)
        __self__.ConfigDiagMethod = ttk.Combobox(
                __self__.Frame, 
                textvariable=__self__.MethodVar, 
                values=("simple_roi","auto_roi","auto_wizard","fit_approx"),
                state="readonly",
                width=13)
        
        dimension_text = "Image size = {0} x {1} pixels".format(
                Constants.MY_DATACUBE.dimension[0],
                Constants.MY_DATACUBE.dimension[1])
        img_dimension_display = Label(__self__.master,text=dimension_text)
        
        __self__.scale = ttk.Checkbutton(__self__.MergeSettings, 
                takefocus=False,
                variable=__self__.ScaleVar)
        __self__.cont = ttk.Checkbutton(__self__.MergeSettings, 
                takefocus=False,
                variable=__self__.ContVar)

        __self__.RecalibrateBtn = ttk.Button(__self__.master,
                text="Re-calibrate",
                width=15,
                takefocus=False,
                command=__self__.call_advcalib)

        ButtonsFrame = Frame(__self__.master)
        SaveButton = ttk.Button(
                ButtonsFrame, 
                text="Save", 
                width=10,
                takefocus=False,
                command=__self__.save)
        CancelButton = ttk.Button(
                ButtonsFrame, 
                text="Cancel", 
                width=10,
                takefocus=False,
                command=__self__.kill)

       
        Label2.grid(row=0,sticky=W,pady=2)
        Label3.grid(row=1,sticky=W,pady=2)
        Label4.grid(row=2,sticky=W,pady=2)
        __self__.Label5.grid(row=0,column=1,sticky=W,pady=2)
        __self__.Label6.grid(row=1,column=1,sticky=W,pady=2)
        __self__.ConfigDiagMethod.grid(row=0,column=1,sticky=E,pady=2,padx=(35,0))
        __self__.ConfigDiagEnhance.grid(row=1,column=1,sticky=E,pady=2,padx=(35,0))
        __self__.ConfigDiagRatio.grid(row=2,column=1,sticky=E,pady=2,padx=(35,0))
        __self__.RecalibrateBtn.grid(row=2,column=0,sticky=W,padx=(17,0))
        img_dimension_display.grid(row=3,column=0,sticky=W,padx=17,pady=2)
        __self__.scale.grid(row=0,column=0)
        __self__.cont.grid(row=1,column=0)
        ButtonsFrame.grid(row=4,columnspan=2,pady=10,padx=10)
        SaveButton.grid(row=0,column=0,sticky=S)
        CancelButton.grid(row=0,column=1,sticky=S)

        if hasattr(Constants.MY_DATACUBE,"scalable"):
            __self__.toggle("on")
            __self__.ScaleVar.set(Constants.MY_DATACUBE.scalable)
        else: __self__.toggle("off")
        __self__.get_version()
        __self__.check_datatype()
        return

    def call_advcalib(__self__):
        AdvCalib(__self__,Constants.ROOT,hascube=1) 

    def save(__self__, e=""):
        save_cube = 0   #NOTE: will save if not merged or h5 anyways!!
                        #This is just to avoid saving unnecessarily large merged cubes
                        #Recalibrated cubes will always be saved

        if __self__.calibration_params is not None:
            failed = verify_calibration_parameters(__self__, __self__.calibration_params)
            if not failed:
                Constants.MY_DATACUBE.recalibrate(__self__.calibration_params)
                save_cube = 1
            else: return

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
                    Constants.MY_DATACUBE.densitymap = fast_scaling(
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
                    Constants.MY_DATACUBE.densitymap = fast_scaling(
                            Constants.MY_DATACUBE,
                            Constants.MY_DATACUBE.densitymap, 1)
                    Constants.MY_DATACUBE.matrix = Constants.MY_DATACUBE.matrix.astype("int32")
                elif Constants.MY_DATACUBE.scalable and not __self__.ScaleVar.get():
                    Constants.MY_DATACUBE.scalable = __self__.ScaleVar.get()
                    Constants.MY_DATACUBE.matrix = Constants.MY_DATACUBE.matrix.astype(
                            "float32")
                    Constants.MY_DATACUBE.densitymap = fast_scaling(
                            Constants.MY_DATACUBE, Constants.MY_DATACUBE.densitymap, -1)
                    Constants.MY_DATACUBE.matrix = Constants.MY_DATACUBE.matrix.astype("int32")

            ###############################################################################

            Constants.ROOT.draw_map()

        if "mca" in Constants.MY_DATACUBE.datatypes or save_cube:
            if not "h5-temp" in Constants.MY_DATACUBE.datatypes:
                Constants.MY_DATACUBE.save_cube()
        Constants.ROOT.write_stat()
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

    def kill(__self__, e=""):
        __self__.master.destroy()


class PeriodicTable:
    # Creates the periodic table and starts find_elements module from Mapping.py
    def __init__(__self__, parent):
        __self__.master = Toplevel(master = parent.master)
        __self__.master.attributes("-alpha", 0.0)
        __self__.master.tagged = True
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
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
        place_center(parent.master, __self__.master)
        __self__.master.iconbitmap(icon)
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)
        return
        

    def kill(__self__,e=""):
        wipe_list()
        __self__.master.destroy()
    
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
        Constants.LOGGER.info("Elements to add to wizard: {}".format(__self__.elements))
        __self__.master.grab_release()
        __self__.master.destroy()
        start_time = time.time()

        save_path = os.path.join(sp.output_path,"peak_find.png")
        Constants.ROOT.Fitter.locate_peaks(add_list=__self__.elements,path=save_path)
        Constants.ROOT.Fitter.launch_workers(
                        Constants.FIT_CYCLES,
                        Constants.SAVE_INTERVAL,
                        Constants.SAVE_FIT_FIGURES)
        Constants.ROOT.bar = Busy(1,0)
        Constants.ROOT.bar.update_text("Building images...")
        del Constants.ROOT.Fitter

        build_images(sp.output_path,bar=Constants.ROOT.bar)

        timestamps = open(os.path.join(sp.__BIN__,"timestamps.txt"),"a")
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
        Constants.ROOT.toggle_(toggle="on")
        Constants.ROOT.MenuBar.entryconfig("Toolbox", state=NORMAL)
        Constants.ROOT.ButtonLoad.config(state=NORMAL)
        Constants.ROOT.write_stat()
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
        try: cube_status = os.stat(sp.cube_path)
        except: 
            try: cube_status = os.stat(Constants.ROOT.h5path)
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
            Constants.ROOT.toggle_(toggle="off")

            # Sets fano and noise factor 
            if not hasattr(Constants.MY_DATACUBE,"FN"):
                FANO,NOISE = 0.114, 80
                Constants.LOGGER.warning("Datacube has no attribute FN, using default FANO and NOISE")
            else:
                FANO, NOISE = Constants.MY_DATACUBE.FN
            FN_set(FANO, NOISE)

            Constants.ROOT.MenuBar.entryconfig("Toolbox", state=DISABLED)
            Constants.ROOT.ButtonLoad.config(state=DISABLED)
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
                    elmap, ROI = (grab_simple_roi_image(Constants.MY_DATACUBE,lines,custom_energy=True))
                    results.append((elmap, ROI, "custom"))
                    digest_results(Constants.MY_DATACUBE,results,["custom"])

                if len(Constants.FIND_ELEMENT_LIST) > 2 \
                        and Constants.MY_DATACUBE.img_size > 999\
                        and Constants.MULTICORE == True:
                    
                    max_copies = 0 #as many copies as cores available
                    if needed_memory > Constants.ROOT.RAM_limit_value:
                        max_copies = 1
                        while cube_size*max_copies < Constants.ROOT.RAM_limit_value:
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
                Constants.LOGGER.info("Finished iteration process for element(s) {0}".format(
                    Constants.FIND_ELEMENT_LIST))
                __self__.progress.destroybar()
                del __self__.progress
                gc.collect()

                timestamp = time.time() - partialtimer
                Constants.LOGGER.info("Execution took %s seconds" % (timestamp))
                timestamps = open(os.path.join(sp.__BIN__,"timestamps.txt"),"a")
                timestamps.write("\n{5} - {7}\nbgtrip={1} enhance={2} peakmethod={3}\t\n{6} elements\n{4} seconds\n".format(
                    Constants.FIND_ELEMENT_LIST,
                    Constants.MY_DATACUBE.config["bgstrip"],
                    Constants.MY_DATACUBE.config["enhance"],
                    Constants.MY_DATACUBE.config["peakmethod"],
                    timestamp,
                    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                    len(Constants.FIND_ELEMENT_LIST),
                    Constants.MY_DATACUBE.name))
                Constants.LOGGER.info("Finished map acquisition!")

            # reactivate widgets
            wipe_list()
            Constants.ROOT.toggle_(toggle="on")
            Constants.ROOT.MenuBar.entryconfig("Toolbox", state=NORMAL)
            Constants.ROOT.ButtonLoad.config(state=NORMAL)
            Constants.ROOT.write_stat()
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
        return


if __name__.endswith("__main__"):         
    from multiprocessing import freeze_support
    freeze_support()

    import time
    import Constants
    from Graphics import *
    splash = SplashScreen()

    optimum_resolution = (1920,1080)

    splash.update("Loading MKL libraries...")
    _init_numpy_mkl()

    # tcl/Tk imports
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
    from tkinter import font as tkFont

    # general utilities
    t = 0.050 #50 ms
    splash.update("Importing utilities...")
    time.sleep(t)
    splash.update("Importing utilities... numpy")
    time.sleep(t)
    import numpy as np
    splash.update("Importing utilities... cv2")
    time.sleep(t)
    import cv2
    splash.update("Importing utilities... system")
    time.sleep(t)
    import sys, os, copy, pickle, stat, random, base64
    splash.update("Importing utilities... shutil")
    time.sleep(t)
    import shutil
    splash.update("Importing utilities... webbrowser")
    time.sleep(t)
    import webbrowser
    from urllib import request
    splash.update("Importing utilities... virtual memory")
    time.sleep(t)
    from psutil import virtual_memory
    splash.update("Importing utilities... logging")
    time.sleep(t)
    import logging
    splash.update("Importing utilities... garbage collector")
    time.sleep(t)
    import gc
    
    # matplotlib imports
    splash.update("Importing plot tools...")
    time.sleep(t)
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from matplotlib import style
    style.use('ggplot')

    splash.update("Verifying screen resolution...")
    time.sleep(t)
    check_screen_resolution(optimum_resolution)

    open_log()

    splash.update("Reading configuration...")
    from ReadConfig import checkout_config, set_settings 

    time.sleep(t)
    splash.update("Booting Engine...")
    from Utilities import *
    import Engine.SpecRead as sp
    import Engine.SpecReadPlus as spp
    from Engine import FastFit
    from Engine import Database
    from Engine.ImgMath import LEVELS
    from Engine.SpecMath import converth5, FN_set
    from Engine.SpecMath import datacube as Cube
    from Engine.CBooster import *

    splash.update("Creating elements...")
    time.sleep(t)
    from Elements import *

    splash.update("Preparing GUI...")
    time.sleep(t)
    from GUI import Theme
    from GUI import AdvCalib
    from GUI import Busy, BusyManager, create_tooltip
    from GUI import ImageWindow
    from GUI import DifferentialAttenuation
    from GUI.PlotWindow import PlotWin
    from GUI.ImageAnalyzer import ImageAnalyzer
    from GUI.Mosaic import Mosaic_API
    from GUI.ConfigurationParser import *

    splash.update("Revving Engine...")
    time.sleep(t)
    from Engine.Mapping import getpeakmap, grab_simple_roi_image, select_lines 
    from Engine.MappingParallel import Cube_reader, sort_results, digest_results
    from Engine.BatchFitter import MultiFit, build_images
    import threading

    logger.info("#"*3+" Configuring environment "+"#"*3)
    start_up()
    mainloop()