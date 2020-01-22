#################################################################
#                                                               #
#          Graphical Interface and Core file                    #
#                        version: 0.0.2α                        #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

global MY_DATACUBE, FIND_ELEMENT_LIST
MY_DATACUBE, FIND_ELEMENT_LIST = None, None

VERSION = "0.0.2α"

def read_license():
    import uuid
    sysid = str(uuid.UUID(int=uuid.getnode()))
    with open("sysid.id","wb") as idfile:
        b_sysid = sysid.encode("utf-8")
        idfile.write(b_sysid)
    return sysid

def start_up():
    #license = read_license()
    #if license not in authorized:
    #    license_error(VERSION)
    # ------------------------------------------------------------

    SpecRead.conditional_setup()
    logging.info("Setting up...")
    try: load_cube()
    except: pass
    logging.info("Done.")
    global FIND_ELEMENT_LIST
    global snip_config
    # snip BG parameters are written as global variables and this is horrible
    # changes to be made in the future
    FIND_ELEMENT_LIST = []
    snip_config = None

def wipe_list():
    global FIND_ELEMENT_LIST
    FIND_ELEMENT_LIST = []
    root.find_elements_diag.master.destroy()

def place_topleft(window1,window2):
    
    # adapted from: https://stackoverflow.com/questions/3352918/
    
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
    window2.geometry('{}x{}+{}+{}'.format(width2, height2, x, y))
    window2.deiconify()

def place_center(window1,window2):
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
    
    x = window1.winfo_rootx() + (int(win_width/2)) - (int(width2/2))
    y = window1.winfo_rooty() - titlebar_height + (int(height/2)) - (int(height2/2))
    window2.geometry('{}x{}+{}+{}'.format(width2, height2, x, y))
    window2.deiconify()
    window2.focus_force()

def spawn_center(window):
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    
    w_width = window.winfo_width()
    w_height = window.winfo_height()

    window.geometry("{}x{}+{}+{}".format(w_width,w_height,\
            int((width/2)-(w_width/2)),int((height/2)-(w_height/2))))
    window.focus_force() 

def convert_bytes(num):
    """
    Obtained from https://stackoverflow.com/questions/210408
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
        
def restore_bytes(num,unit):
    units = ['KB', 'MB', 'GB', 'TB']
    for x in units:
        if unit == x:
            return num * (1024**(units.index(x)+1))

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
    try:
        if root.HelpWindow.state() == "normal":
            root.HelpWindow.focus_force()
        else:
            root.HelpWindow = Toplevel(master=root.master)
            root.HelpWindow.title("Help")
            root.HelpWindow.resizable(False,False)
            HelpText = "There is going to be something here soon."
            HelpLabel = Label(root.HelpWindow, text=HelpText, wraplength=640, anchor=W, justify=LEFT)
            HelpLabel.grid(sticky=W)
            place_center(root.master, root.HelpWindow)
    except: 
            root.HelpWindow = Toplevel(master=root.master)
            root.HelpWindow.title("Help")
            root.HelpWindow.resizable(False,False)
            HelpText = "There is going to be something here soon."
            HelpLabel = Label(root.HelpWindow, text=HelpText, wraplength=640, anchor=W, justify=LEFT)
            HelpLabel.grid(sticky=W)
            place_center(root.master, root.HelpWindow)


def call_author():
    try:
        if root.AuthorWin.state() == "normal":
            root.AuthorWin.focus_force()
        else:
            root.AuthorWin = Toplevel(master=root.master)
            root.AuthorWin.title("Author")
            root.AuthorWin.resizable(False,False)
            icon = os.getcwd()+"\\images\\icons\\icon.ico"
            root.AuthorWin.iconbitmap(icon)  
            infotext="Author: Sergio Lins\nSoftware version: {0}\nContact: sergio.lins@roma3.infn.it".format(VERSION)
            winFrame = Frame(root.AuthorWin)
            winFrame.pack(padx=(16,16),pady=(16,16))
            Info = Label(winFrame,text=infotext, wraplength=640, anchor=W, justify=LEFT)
            Info.pack()
            place_center(root.master,root.AuthorWin)
    except:
            root.AuthorWin = Toplevel(master=root.master)
            root.AuthorWin.title("Author")
            root.AuthorWin.resizable(False,False)
            icon = os.getcwd()+"\\images\\icons\\icon.ico"
            root.AuthorWin.iconbitmap(icon)  
            infotext="Author: Sergio Lins\nSoftware version: {0}\nContact: sergio.lins@roma3.infn.it".format(VERSION)
            winFrame = Frame(root.AuthorWin)
            winFrame.pack(padx=(16,16),pady=(16,16))
            Info = Label(winFrame,text=infotext, wraplength=640, anchor=W, justify=LEFT)
            Info.pack()
            place_center(root.master,root.AuthorWin)


def open_analyzer():
    global MY_DATACUBE
    API = ImageAnalyzer(root.master,MY_DATACUBE)
    root.ImageAnalyzers.append(API) 

def call_compilecube():
    try: os.mkdir(SpecRead.output_path)
    except IOError as exception:
        logging.warning("Error {}.".format(exception.__class__.__name__))
        logging.warning("Can't create output folder {}".format(SpecRead.output_path))
    
    if os.path.exists(SpecRead.cube_path): 
        pass
    else:
        root.ButtonLoad.config(state=DISABLED)
        root.MenuBar.entryconfig("Toolbox", state=DISABLED)
        try: root.SamplesWindow.destroy()
        except: pass
        logging.warning("Starting cube {} compilation!".format(SpecRead.CONFIG["directory"]))
        specbatch = Cube(['xrf'],SpecRead.CONFIG)
        fail = specbatch.compile_cube()
        root.ButtonLoad.config(state=NORMAL)
        root.MenuBar.entryconfig("Toolbox", state=NORMAL)
        if fail[0] == True:
            messagebox.showerror("EOF Error!","Could not read {} file!".format(fail[1]))

def prompt_folder():
    folder = filedialog.askdirectory()
    if folder != "":
        ini_file = open(os.getcwd() + "\\folder.ini","w")
        folder = folder.replace("/","\\")
        ini_file.write(folder+"\\")
        ini_file.close()
        SpecRead.samples_folder = folder+"\\"
        root.refresh_samples()
    else:
        pass
    return 0

def call_heightmap():
    return 0

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


class Welcome:

    def __init__(__self__,parent):
        """parent is a Tk window"""
        __self__.h, __self__.w = 400, 240
        __self__.master = Toplevel(master=parent)
        icon = os.getcwd()+"\\images\\icons\\icon.ico"
        __self__.master.iconbitmap(icon)  

        __self__.master.resizable(False,False)
        __self__.master.title("Welcome!")
        __self__.page = StringVar()
        __self__.tag = BooleanVar()
        __self__.infotext = StringVar()
        __self__.messages = ["Welcome to Piratininga Sample Manager v.0.0.2.\n\nClick the left or right arrows to navigate.",\
                "Getting started:\nClick \"Load Sample\" to open the \"Sample List\" window.\nBy default, Piratininga SM looks for mca files under C:\\Samples\\ folder. To change it, click on \"Toolbox\" and select \"Change samples folder\"\nSelect the folder that contains the folder with your data.\nPiratininga SM also manages your samples, so if any sample is already compiled, it will appear in the list.","Compiling a sample:\nTo compile your data, double click on the sample name inside the \"Samples List\" window in the right corner. You will be prompted to configure your sample parameters.\nTo save the \"sample counts map\", right-click the sample name in the \"Samples List\" window and select \"Save density map\"."]
        __self__.current_page = 1
        __self__.page.set("Page {}/{}".format(__self__.current_page,len(__self__.messages)))
        __self__.tag.set(False)
        __self__.infotext.set(__self__.messages[0])

        __self__.build_widgets()

    def build_widgets(__self__):
        __self__.page_counter = Label(__self__.master, textvariable=__self__.page)
        __self__.page_counter.grid(row=0, column=0, sticky=W+E, columnspan=2, pady=3)
        
        __self__.text_frame = Frame(__self__.master, width=320, height=150)
        __self__.text_frame.grid(row=1, column=0, sticky=W+E, columnspan=2)
        __self__.info = Label(__self__.text_frame,
                textvariable=__self__.infotext,
                anchor=CENTER,
                justify=CENTER,
                wraplength=400,
                width=70,
                height=7,
                padx=5)
        __self__.info.grid(row=0, column=1, sticky=W+E)
        icon_fw = PhotoImage(file=os.getcwd()+"\\images\\icons\\next.png")
        __self__.icon_fw = icon_fw.subsample(1,1)
        icon_bw= PhotoImage(file=os.getcwd()+"\\images\\icons\\previous.png")
        __self__.icon_bw = icon_bw.subsample(1,1)
        __self__.fw = Button(__self__.text_frame, image=__self__.icon_fw, command=__self__.next_page, width=32,height=32)
        __self__.fw.grid(row=0, column=2)
        __self__.bw = Button(__self__.text_frame, image=__self__.icon_bw, command=__self__.previous_page, width=32, height=32)
        __self__.bw.grid(row=0, column=0)

        __self__.button_frame = Frame(__self__.master)
        __self__.button_frame.grid(row=3,column=0,columnspan=2)
        
        __self__.tag_button = Checkbutton(__self__.master, variable=__self__.tag) 
        __self__.tag_button.grid(row=2, column=0, padx=10)
        
        __self__.tag_label = Label(__self__.master, text="Don't show me again on startup.")
        __self__.tag_label.grid(row=2, column=1, sticky=W)

        __self__.accept = Button(__self__.button_frame, text="Ok", width=13, command=__self__.checkout)
        __self__.accept.grid(pady=10)
        
        for i in range(5):
            __self__.master.columnconfigure(i, weight=0)
            __self__.master.rowconfigure(i, weight=0)
        __self__.master.columnconfigure(1, weight=1)
        
    def next_page(__self__):
        if __self__.current_page+1 <= len(__self__.messages):
            __self__.current_page +=1
            text = __self__.current_page-1
            __self__.infotext.set(__self__.messages[text])
            __self__.page.set("Page {}/{}".format(__self__.current_page,len(__self__.messages)))
            __self__.info.update()
        else: pass
        
    def previous_page(__self__):
        if __self__.current_page-1 >= 1:
            __self__.current_page -=1
            text = __self__.current_page-1
            __self__.infotext.set(__self__.messages[text])
            __self__.page.set("Page {}/{}".format(__self__.current_page,len(__self__.messages)))
            __self__.info.update()
        else: pass

    def checkout(__self__):
        checker = True
        if __self__.tag.get() == True:
            root.checker = False
            checker = False
        inipath = os.getcwd() + "\settings.tag"
        ini = open(inipath,'w+')
        ini.write("{}\n".format(SpecRead.samples_folder))
        ini.write("<MultiCore>\t{}\n".format(root.MultiCore))
        ini.write("<PlotMode>\t{}\n".format(root.PlotMode))
        ini.write("<RAMLimit>\t{}\n".format(root.RAM_limit))
        ini.write("<welcome>\t{}".format(checker))
        ini.close()
        __self__.master.destroy()


class export_diag():

    """Creates a dialog to export ImageAnalyzer class images"""

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
        icon1 = PhotoImage(file=os.getcwd()+"\\images\\icons\\export_1.png")
        icon2 = PhotoImage(file=os.getcwd()+"\\images\\icons\\export_2.png")
        icon3 = PhotoImage(file=os.getcwd()+"\\images\\icons\\export_merge.png")
        __self__.icon1 = icon1.subsample(1,1)
        __self__.icon2 = icon2.subsample(1,1)
        __self__.icon3 = icon3.subsample(1,1)
        size_x, size_y = 64,64
        __self__.Button1 = Button(__self__.Frame, image=__self__.icon1, bd=3, command=lambda:__self__.export(tag=1), width=size_x, height=size_y)
        __self__.Button2 = Button(__self__.Frame, image=__self__.icon2, bd=3, command=lambda:__self__.export(tag=2), width=size_x, height=size_y)
        __self__.Button3 = Button(__self__.Frame, image=__self__.icon3, bd=3, command=__self__.merge, width=size_x, height=size_y)

        __self__.Button1.grid(row=0,column=0,padx=32)
        __self__.Button2.grid(row=0,column=1,padx=32)
        __self__.Button3.grid(row=0,column=2,padx=32)
        
        __self__.master.update()

        place_center(__self__.parent.master,__self__.master)
        __self__.master.deiconify()
        __self__.master.focus_set()
        icon = os.getcwd()+"\\images\\icons\\img_anal.ico"
        __self__.master.iconbitmap(icon)


    def export(__self__,tag=0):
        try:
            if tag == 1: 
                f = filedialog.asksaveasfile(mode='w', defaultextension=".png")
                if f is None: 
                    return
                write_image(__self__.parent.newimage1,1024,f.name)
            elif tag == 2: 
                f = filedialog.asksaveasfile(mode='w', defaultextension=".png")
                if f is None: 
                    return
                write_image(__self__.parent.newimage2,1024,f.name)
            else: pass
        except PermissionError as exception: 
            messagebox.showerror("Error!",exception.__class__.__name__)
            return
        __self__.kill()

    def merge(__self__):
        stack = stackimages(__self__.parent.newimage1,__self__.parent.newimage2)
        f = filedialog.asksaveasfile(mode='w', defaultextension=".png")
        if f is None: 
            return
        write_image(stack,1024,f.name)
        __self__.kill()

    def kill(__self__,e=""):
        __self__.master.grab_release()
        __self__.parent.master.focus_force()
        __self__.master.destroy()


class dimension_diag():

    """Creates a pop-up dialog to prompt the datacube dimension
    if no colonneXrighe.txt file is found for the data selected.
    It writes a custom colonneXrighe.txt file to the sample output
    folder, which is deleted if the sample is RESET"""

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
        if x.isdigit(): 
            x=int(x)
            if x > root.mcacount[__self__.folder]: x = root.mcacount[__self__.folder]
            elif x == 0: x = 1
        else: x=1
        if y.isdigit(): 
            y=int(y)
            if y > root.mcacount[__self__.folder]: y = root.mcacount[__self__.folder]
            elif y == 0: y = 1
        else: y=1
        while x*y > root.mcacount[__self__.folder]:
            if x > y: x-=1
            elif y > x: y-=1
        return x,y
    
    def send(__self__,event=""):
        root.config_xy = __self__.check_values(__self__.x,__self__.y)
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
        __self__.win.destroy()


class PeakClipper:

    """Creates a dialog to set-up SNIPBG parameters"""
    
    def __init__(__self__,parent):
        __self__.master = Toplevel(parent)
        __self__.master.tagged = True
        __self__.parent = parent
        #__self__.master.withdraw()
        __self__.master.resizable(False,False)
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.master.bind("<Escape>",__self__.kill)
        __self__.frame1 = Frame(__self__.master,height=320,width=240)
        __self__.frame2 = Frame(__self__.master)
        __self__.frame3 = Frame(__self__.master)
        __self__.frame1.grid(row=0,rowspan=2,column=0)
        __self__.frame2.grid(row=0,column=1,padx=15)
        __self__.frame3.grid(row=1,column=1,padx=15,pady=15)

        __self__.savgol = IntVar()
        __self__.order = IntVar()
        __self__.window = IntVar()
        __self__.iter = IntVar()
        
        __self__.build_widgets()

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
        __self__.mplCanvas.pack()
        __self__.canvas._tkcanvas.pack()

        # frame 2 (top-right)
        __self__.randomize = Button(__self__.frame2, text="Pick random spectrum",\
                command=__self__.random_sample, justify=CENTER)
        __self__.label_savgol = Label(__self__.frame2, text="Sav-gol window: ")
        __self__.label_order = Label(__self__.frame2, text="Sav-gol order: ")
        __self__.label_window = Label(__self__.frame2, text= "Clipping window: ")
        __self__.label_iter = Label(__self__.frame2, text="Number of iterations: ")
        __self__.entry_savgol = Entry(__self__.frame2,textvariable=__self__.savgol,width=15)
        __self__.entry_order = Entry(__self__.frame2,textvariable=__self__.order,width=15)
        __self__.entry_window = Entry(__self__.frame2,textvariable=__self__.window,width=15)
        __self__.entry_iter = Entry(__self__.frame2,textvariable=__self__.iter,width=15)

        __self__.randomize.grid(row=0,column=0,columnspan=2,pady=15)
        __self__.label_savgol.grid(row=1,column=0)
        __self__.label_order.grid(row=2,column=0)
        __self__.label_window.grid(row=3,column=0)
        __self__.label_iter.grid(row=4,column=0)
        __self__.entry_savgol.grid(row=1,column=1,sticky=E)
        __self__.entry_order.grid(row=2,column=1,sticky=E)
        __self__.entry_window.grid(row=3,column=1,sticky=E)
        __self__.entry_iter.grid(row=4,column=1,sticky=E)

        # frame 3 (lower-right)
        __self__.button_try = Button(__self__.frame3,text="Try",width=10,\
                justify=CENTER,command=__self__.refresh_plot)
        __self__.button_save = Button(__self__.frame3, text="Save",width=10,\
                justify=CENTER,command=__self__.save)
        __self__.button_cancel = Button(__self__.frame3, text="Cancel",width=10,\
                justify=CENTER,command=__self__.kill)

        __self__.button_try.grid(row=0,column=0)
        __self__.button_save.grid(row=0,column=1)
        __self__.button_cancel.grid(row=1,column=0,columnspan=2)
        
        __self__.master.update()
        place_center(__self__.parent,__self__.master)
        #__self__.master.deiconify()
        __self__.master.focus_set()
        icon = os.getcwd()+"\\images\\icons\\settings.ico"
        __self__.master.iconbitmap(icon)
        __self__.random_sample()

    
    def stripbg(__self__):
        savgol = __self__.savgol.get()
        order = __self__.order.get()
        window = __self__.window.get()
        cycles = __self__.iter.get()
        background = peakstrip(__self__.spectrum,cycles,window,savgol,order)
        return background

    def refresh_plot(__self__):
        __self__.plot.clear()
        folder = SpecRead.CONFIG.get('directory')
        if root.PlotMode == "Linear":
            __self__.plot.set_ylabel("Counts")
            __self__.plot.set_xlabel("Channels")
            __self__.plot.plot(__self__.spectrum,color="blue",\
                    label=(root.samples[folder] + "_{0}.{1}".format(__self__.sample,root.mca_extension[folder])))
            try: 
                background = __self__.stripbg()
                __self__.plot.plot(background, label="Background",color="yellow")
            except: pass
            __self__.plot.set_ylim(bottom=0)
        else:
            __self__.plot.set_ylabel("Counts")
            __self__.plot.set_xlabel("Channels")
            __self__.plot.semilogy(__self__.spectrum,color="blue",\
                    label=(root.samples[folder] + "_{0}.{1}".format(__self__.sample,root.mca_extension[folder])))
            try: 
                background = __self__.stripbg()
                __self__.plot.plot(background, label="Background",color="yellow")
            except: pass
            __self__.plot.set_ylim(bottom=10e-2)
            __self__.plot.set_ylim(top=1.10*__self__.spectrum.max())

        __self__.plot.legend()
        __self__.canvas.draw()

    def random_sample(__self__):
        folder = SpecRead.CONFIG.get('directory')
        spec_no = root.mcacount[folder]
        __self__.sample = random.randint(1,spec_no)
        mca = SpecRead.selected_sample_folder + \
                root.samples[folder] + "_{0}.{1}".format(__self__.sample,root.mca_extension[folder])
        __self__.spectrum = SpecRead.getdata(mca)
        if isinstance(__self__.spectrum,np.ndarray):
            __self__.refresh_plot() 
        else:
            messagebox.showerror("EOF Error!","Could not read {} file!".\
                    format(__self__.spectrum))

    def save(__self__):
        global snip_config
        snip_config = __self__.iter.get(),__self__.window.get(),__self__.savgol.get(),__self__.order.get()
        proceed = __self__.verify_values(snip_config)
        if proceed == True: __self__.kill()
        else: messagebox.showerror("Value Error", "Parameters not valid. No negative or zero values are valid. Sav-gol window must be odd and greater than Sav-gol order.")

    def kill(__self__, event=""):
        __self__.master.grab_release()
        root.ConfigDiag.grab_set()
        __self__.master.destroy()
        return 0
    
    def verify_values(__self__,snip):
        if snip[0] <= 0 or snip[1] <= 0: return False
        if int(snip[2]%2) == 0: return False
        if snip[3] > snip[2]: return False
        else: return True


class Annotator:

    """Creates an annotator to select areas on matplotlib canvases"""

    def __init__(__self__,parent):
      
        __self__.parent = parent
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
        __self__.parent.canvas1.mpl_connect("button_press_event",__self__.on_press)
        __self__.parent.canvas1.mpl_connect("motion_notify_event",__self__.on_drag)
        __self__.parent.canvas1.mpl_connect("button_release_event",__self__.on_release)
        __self__.parent.canvas2.mpl_connect("button_press_event",__self__.on_press)
        __self__.parent.canvas2.mpl_connect("motion_notify_event",__self__.on_drag)
        __self__.parent.canvas2.mpl_connect("button_release_event",__self__.on_release)

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

    def refresh_roi_plot(__self__):
        global FIND_ELEMENT_LIST
        if len(FIND_ELEMENT_LIST) > 0: 
            lines = True
        else: 
            lines = False
        __self__.parent.plot.draw_selective_sum(__self__.parent.DATACUBE,\
                __self__.parent.sum_spectrum,
                display_mode = root.plot_display,
                lines = lines)

    def on_press(__self__,event):
        __self__.press = True
        try: __self__.x0 = int(event.xdata)
        except: pass
        try: __self__.y0 = int(event.ydata)
        except: pass

    def on_drag(__self__,event):
        if __self__.press:
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

            """Create local method to avoid using the global refresh!!!"""
            __self__.refresh_roi_plot()

    def on_release(__self__,event):
        __self__.press = False
        if __self__.press and not __self__.move:
            __self__.press = False
            __self__.move = False

    def calculate_area(__self__):
        __self__.area1_sum = 0
        __self__.area2_sum = 0
        __self__.parent.sum_spectrum = np.ones([__self__.parent.DATACUBE.sum.shape[0]])
        unpacker1 = __self__.element1.split("_")
        unpacker2 = __self__.element2.split("_")
        
        # unpacks raw image, notice no normalization is done to match LEVELS levels of gray
        image1 = __self__.parent.DATACUBE.unpack_element(unpacker1[0],unpacker1[1])
        image2 = __self__.parent.DATACUBE.unpack_element(unpacker2[0],unpacker2[1])
        
        x_ = [__self__.x0,__self__.x1]
        y_ = [__self__.y0,__self__.y1]
        x_.sort()
        y_.sort()
        for x in range(y_[0],y_[1]):
            for y in range(x_[0],x_[1]):
                __self__.area1_sum += image1[x][y]
                __self__.area2_sum += image2[x][y]
                __self__.parent.sum_spectrum += __self__.parent.DATACUBE.matrix[x][y]
        __self__.roibox1["text"] = "Roi 1: {}".format(int(__self__.area1_sum))
        __self__.roibox2["text"] = "Roi 2: {}".format(int(__self__.area2_sum))
        if __self__.area2_sum > 0:
            __self__.ratebox["text"] = \
                    "Ratio: {:.2f}".format(__self__.area1_sum/__self__.area2_sum)


class ImageAnalyzer:

    def __init__(__self__,parent,datacube):
        
        __self__.DATACUBE = datacube
        __self__.packed_elements = __self__.DATACUBE.check_packed_elements()
        __self__.master = Toplevel(master=parent)
        __self__.master.tagged = False
        #__self__.master.bind("<Configure>", __self__.resize)
        __self__.master.title("Image Analyzer v1.0.0")
        __self__.master.resizable(False,False)
        __self__.sampler = Frame(__self__.master)
        __self__.sampler.pack(side=TOP,anchor=CENTER)
        __self__.SampleFrame = Frame(__self__.master)
        __self__.SampleFrame.pack(side=TOP)
        __self__.LeftCanvas = Canvas(__self__.SampleFrame)
        __self__.LeftCanvas.pack(side=LEFT)
        __self__.RightCanvas = Canvas(__self__.SampleFrame)
        __self__.RightCanvas.pack(side=RIGHT)
        __self__.sliders = Frame(__self__.master)
        __self__.sliders.pack(side=BOTTOM,fill=X)
        __self__.buttons = Frame(__self__.sliders)
        __self__.buttons.grid(row=0,column=0,rowspan=4,columnspan=2,padx=(60,30),sticky=W)
        
        __self__.Map1Var = StringVar()
        __self__.Map1Counts = StringVar()
        __self__.Map1Counts.set("Select an element")
        __self__.Map2Var = StringVar()
        __self__.Map2Counts = StringVar()
        __self__.Map2Counts.set("Select an element")
        
        try:
            __self__.ElementalMap1 = np.zeros([__self__.DATACUBE.dimension[0],\
                    __self__.DATACUBE.dimension[1]])
            __self__.ElementalMap2 = np.zeros([__self__.DATACUBE.dimension[0],\
                    __self__.DATACUBE.dimension[1]])
        except:
            __self__.ElementalMap1 = np.zeros([1,1])
            __self__.ElementalMap2 = np.zeros([1,1])
        
        # map 1
        __self__.Map1Label = Label(__self__.sampler, textvariable=__self__.Map1Counts,width=30)
        __self__.Map1Label.grid(row=0, column=0, columnspan=3, sticky=W)
        __self__.Map1Combo = ttk.Combobox(__self__.sampler, textvariable=__self__.Map1Var,\
                values=__self__.packed_elements,width=5,state="readonly")
        __self__.Map1Combo.grid(row=0,column=3, sticky=W,padx=(16,16),pady=(8,4))
        __self__.Map1Combo.bind("<<ComboboxSelected>>", __self__.update_sample1)
        
        # map 2
        __self__.Map2Label = Label(__self__.sampler, textvariable=__self__.Map2Counts,width=30)
        __self__.Map2Label.grid(row=0, column=5, columnspan=3, sticky=E)
        __self__.Map2Combo = ttk.Combobox(__self__.sampler, textvariable=__self__.Map2Var,\
                values=__self__.packed_elements,width=5,state="readonly")
        __self__.Map2Combo.grid(row=0,column=4, sticky=E,padx=(16,16),pady=(8,4))
        __self__.Map2Combo.bind("<<ComboboxSelected>>", __self__.update_sample2)

        # matplotlib canvases
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
                command=__self__.switchLP1T1).grid(row=0,column=2)
        __self__.LP1check = BooleanVar()
        __self__.LP1check.set(False)
        __self__.LP1 = Checkbutton(__self__.sliders, variable=__self__.LP1check, \
                command=__self__.switchT1LP1).grid(row=1,column=2)
        __self__.S1check = BooleanVar()
        __self__.S1check.set(False)
        __self__.S1 = Checkbutton(__self__.sliders, variable=__self__.S1check).grid(row=2,column=2)
       
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

        # slider for image 1
        __self__.T1Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=LEVELS, \
                command=__self__.draw_image1)
        __self__.T1Slider.grid(row=0,column=4)
        __self__.LP1Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=LEVELS, \
                command=__self__.draw_image1)
        __self__.LP1Slider.grid(row=1,column=4)
        __self__.S1Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=7, \
                command=__self__.draw_image1)
        __self__.S1Slider.grid(row=2,column=4)

        # image controls Threshold, LowPass and Smooth
        __self__.T2check = BooleanVar()
        __self__.T2check.set(False)
        __self__.T2 = Checkbutton(__self__.sliders, variable=__self__.T2check, \
                command=__self__.switchLP2T2).grid(row=0,column=6)
        __self__.LP2check = BooleanVar()
        __self__.LP2check.set(0)
        __self__.LP2 = Checkbutton(__self__.sliders, variable=__self__.LP2check, \
                command=__self__.switchT2LP2).grid(row=1,column=6)
        __self__.S2check = BooleanVar()
        __self__.S2check.set(0)
        __self__.S2 = Checkbutton(__self__.sliders, variable=__self__.S2check).grid(row=2,column=6)
               
        # slider for image 2
        __self__.T2Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=LEVELS, \
                command=__self__.draw_image2)
        __self__.T2Slider.grid(row=0,column=8)
        __self__.LP2Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=LEVELS, \
                command=__self__.draw_image2)
        __self__.LP2Slider.grid(row=1,column=8)
        __self__.S2Slider = Scale(__self__.sliders, orient='horizontal', from_=0, to=7, \
                command=__self__.draw_image2)
        __self__.S2Slider.grid(row=2,column=8)
    
        # buttons
        __self__.roibox1 = Label(__self__.buttons,text="Roi 1: None") 
        __self__.roibox1.grid(row=0,column=0,columnspan=2)
        __self__.roibox2 = Label(__self__.buttons,text="Roi 2: None") 
        __self__.roibox2.grid(row=1,column=0,columnspan=2)
        __self__.ratebox = Label(__self__.buttons,text="Ratio: None") 
        __self__.ratebox.grid(row=2,column=0,columnspan=2)
        
        __self__.annotate = Button(__self__.buttons,text="Set ROI",\
                command=__self__.toggle_annotator,relief="raised",width=14)
        __self__.annotate.grid(row=4,column=0,columnspan=2)
        __self__.correlate = Button(__self__.buttons,text="Correlate",\
                command=__self__.get_correlation,width=round(__self__.annotate.winfo_width()/2))
        __self__.correlate.grid(row=3,column=0)
        __self__.export = Button(__self__.buttons,text="Export",\
                command=__self__.export_maps,width=round(__self__.annotate.winfo_width()/2))
        __self__.export.grid(row=3,column=1)
        
        # Disable sliders
        __self__.T1Slider.config(state=DISABLED)
        __self__.T2Slider.config(state=DISABLED)
        __self__.LP1Slider.config(state=DISABLED)
        __self__.LP2Slider.config(state=DISABLED)
        
        __self__.draw_image1(0)
        __self__.draw_image2(0)
        
        icon = os.getcwd()+"\\images\\icons\\img_anal.ico"
        __self__.master.iconbitmap(icon)  
        
        # presents a first image. displays a "no data image if no packed element exists"
        try: 
            try: __self__.Map1Combo.current(0)
            except: pass
            try: __self__.Map2Combo.current(1)
            except: 
                try: __self__.Map2Combo.current(0)
                except: pass
            if __self__.ElementalMap1.max() == 0:
                __self__.ElementalMap1 = np.array(plt.imread(os.getcwd()+"\\images\\no_data.png"))
                __self__.draw_image1(0)
            if __self__.ElementalMap2.max() == 0:
                __self__.ElementalMap2 = np.array(plt.imread(os.getcwd()+"\\images\\no_data.png"))
                __self__.draw_image2(0)
            __self__.update_sample1(None)
            __self__.update_sample2(None)
        except: 
            pass
    
    def resize(__self__, event):
        wi = __self__.LeftCanvas.winfo_width()
        hi = __self__.LeftCanvas.winfo_height()
        wi_t = __self__.RightCanvas.winfo_width()
        hi_t = __self__.RightCanvas.winfo_height()

    def toggle_annotator(__self__):
        """
        passes the current datacube, so if the user changes it, for the current ImgAnal api open when
        using the annotation function, the cube is still the one loaded when ImgAnal was opened
        the api is passed as argument so the annotator knows where to draw
        """
        if __self__.annotate.config("relief")[-1] == "raised":
            __self__.annotate.config(relief="sunken")
            __self__.annotate.config(bg="yellow")
            __self__.annotator = Annotator(__self__) 
            __self__.plot = PlotWin(__self__.master)
            __self__.plot.draw_selective_sum(__self__.DATACUBE,
                    __self__.DATACUBE.sum,
                    root.plot_display)
        else:
            __self__.annotate.config(relief="raised")
            # the easiest way to recover the default color button is pointing to an existing button
            # that never changes its color
            __self__.annotate.config(bg=__self__.correlate.cget("background"))
            __self__.annotator.wipe_annotator()
            del __self__.annotator
 
    def update_sample1(__self__,event):
        label1 = "Maximum net counts: {}".format(int(__self__.DATACUBE.max_counts[__self__.Map1Var.get()]))
        __self__.Map1Counts.set(label1)
        unpacker = __self__.Map1Var.get()
        unpacker = unpacker.split("_")
        __self__.ElementalMap1 = __self__.DATACUBE.unpack_element(unpacker[0],unpacker[1])
        __self__.ElementalMap1 = __self__.ElementalMap1/__self__.ElementalMap1.max()*LEVELS
        __self__.draw_image1(0)
        try: __self__.annotator.refresh_annotator()
        except: pass
     
    def update_sample2(__self__,event):
        label2 = "Maximum net counts: {}".format(int(__self__.DATACUBE.max_counts[__self__.Map2Var.get()]))
        __self__.Map2Counts.set(label2)
        unpacker = __self__.Map2Var.get()
        unpacker = unpacker.split("_")
        __self__.ElementalMap2 = __self__.DATACUBE.unpack_element(unpacker[0],unpacker[1])
        __self__.ElementalMap2 = __self__.ElementalMap2/__self__.ElementalMap2.max()*LEVELS
        __self__.draw_image2(0)
        try: __self__.annotator.refresh_annotator()
        except: pass
    
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
            del __self__.annotator
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
            del __self__.annotator
        except: pass
         
        return image   
    
    # the Sliders are the widgets that calls draw_image functions
    # they always pass their respective values as argument when using command
    # argument i is there just to make it work. The value passed doesn't change a thing

    def draw_image1(__self__,i):
        __self__.CACHEMAP1 = copy.deepcopy(__self__.ElementalMap1)
        __self__.newimage1 = __self__.transform1(__self__.CACHEMAP1)
        __self__.CACHEMAP1
        __self__.plot1.clear()
        __self__.plot1.imshow(__self__.newimage1, cmap='gray')
        __self__.plot1.grid(b=None)
        __self__.canvas1.draw()
    
    def draw_image2(__self__,i):
        __self__.CACHEMAP2 = copy.deepcopy(__self__.ElementalMap2)
        __self__.newimage2 = __self__.transform2(__self__.CACHEMAP2)
        __self__.CACHEMAP2 = None
        __self__.plot2.clear()
        __self__.plot2.imshow(__self__.newimage2, cmap='gray')
        __self__.plot2.grid(b=None)
        __self__.canvas2.draw()

    def get_correlation(__self__):
        labels = __self__.Map1Var.get(),__self__.Map2Var.get()
        corr = correlate(__self__.newimage1,__self__.newimage2)

        # this step is necessary to make a proper correlation between the two
        # displayed images. Transforming them only cuts the desired signals,
        # therefore the gray levels remain the same. The image looks brighter when
        # displayed because matplot adjust the axes maxima and minima when plotting
        try: 
            corr[0] = corr[0]/corr[0].max()*LEVELS
            corr[1] = corr[1]/corr[1].max()*LEVELS
        
            corr_plot = PlotWin(__self__.master)
            corr_plot.draw_correlation(corr,labels)
        except:
            pass

    def export_maps(__self__):
        export = export_diag(__self__)
        return 0


class PlotWin:

    global MY_DATACUBE

    def __init__(__self__,master):
        plot_font = {'fontname':'Arial','fontsize':10}
        __self__.master = Toplevel(master=master)
        __self__.master.title("Plot")
        __self__.master.tagged = None
        __self__.master.minsize(width=600,height=480)
        __self__.master.configure(bg='white')
        __self__.master.resizable(True,True) 
        __self__.upper = Canvas(__self__.master)
        __self__.upper.config(bg='white')
        __self__.upper.pack(side=TOP, expand=True, fill=BOTH, padx=(16,16),pady=(16,16))
        __self__.lower = Canvas(__self__.master,height=35)
        __self__.lower.pack(side=TOP, anchor=N, fill=BOTH)
        __self__.master.bind("<Configure>", __self__.resize)
        
        __self__.figure = Figure(figsize=(5,4), dpi=75)
        __self__.plot = __self__.figure.add_subplot(111)
        __self__.plot.grid(which='both',axis='both')
        __self__.plot.axis('On')
        __self__.canvas = FigureCanvasTkAgg(__self__.figure,__self__.upper)
        __self__.canvas.draw()
        __self__.mplCanvas = __self__.canvas.get_tk_widget()
        __self__.mplCanvas.pack()
        __self__.toolbar = NavigationToolbar2Tk(__self__.canvas,__self__.lower)
        __self__.toolbar.update()
        __self__.canvas._tkcanvas.pack()
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.wipe_plot)
        icon = os.getcwd()+"\\images\\icons\\plot.ico"
        __self__.master.iconbitmap(icon)
    
    def wipe_plot(__self__):

        """clears and destroy plot"""

        __self__.plot.clear()
        __self__.master.destroy()
        del __self__

    def resize(__self__, event):
        wi = __self__.upper.winfo_width()
        hi = __self__.upper.winfo_height()
        wi_t = __self__.lower.winfo_width()
        hi_t = __self__.lower.winfo_height()
        __self__.mplCanvas.config(width=wi, height=hi)

    def draw_calibration(__self__):
        __self__.master.tagged = True
        plot_font = {'fontname':'Arial','fontsize':10}
        __self__.plotdata = MY_DATACUBE.energyaxis
        channels = np.arange(1,__self__.plotdata.shape[0]+1)
        anchors = MY_DATACUBE.calibration
        __self__.plot.set_title('{0} Calibration curve'.format(SpecRead.DIRECTORY),**plot_font)
        __self__.plot.plot(channels,__self__.plotdata,label="Calibration curve")
        for pair in anchors:
            __self__.plot.plot(pair[0],pair[1], marker='+',mew=1,ms=10,label="{0}".format(pair))
        __self__.plot.set_ylabel("Energy (KeV)")
        __self__.plot.set_xlabel("Channel")
        __self__.plot.legend()
        place_topleft(__self__.master.master,__self__.master)

    def draw_spec(__self__,mode,display_mode=None,lines=False):
        __self__.master.tagged = False
        if __self__.master.winfo_exists() == True:
            global FIND_ELEMENT_LIST
            __self__.plot.clear()
            plot_font = {'fontname':'Arial','fontsize':10}
            colors = ["blue","red","green"]
            if display_mode == '-semilog':
                __self__.plot.set_ylabel("Counts")
                i = 0
                for option in mode:
                    __self__.plotdata = getstackplot(MY_DATACUBE,option)
                    __self__.plotdata = __self__.plotdata/__self__.plotdata.max()
                    __self__.plot.semilogy(MY_DATACUBE.energyaxis,__self__.plotdata,\
                            label=str(option),color=colors[i])
                    i+=1
                if lines==True:
                    __self__.master.tagged = True
                    for element in FIND_ELEMENT_LIST:
                        if element == "custom":
                            energies = plottables_dict[element]
                            __self__.plot.plot((energies[0],energies[0]),\
                                    (0,__self__.plotdata.max()),'k--',color="cornflowerblue",\
                                    label="Custom Low")
                            __self__.plot.plot((energies[1],energies[1]),\
                                    (0,__self__.plotdata.max()),'k--',color="tomato",\
                                    label="Custom High")
                        else:
                            energies = plottables_dict[element]
                            __self__.plot.plot((energies,energies),\
                                    (0,__self__.plotdata.max()),'k--')

                __self__.plot.set_title('{0} {1}'.format(SpecRead.DIRECTORY,mode),**plot_font)
                __self__.plot.set_xlabel("Energy (KeV)")
                __self__.plot.legend()
            else:
                i = 0
                for option in mode:
                    __self__.plotdata = getstackplot(MY_DATACUBE,option)
                    __self__.plotdata = __self__.plotdata/__self__.plotdata.max()
                    __self__.plot.plot(MY_DATACUBE.energyaxis,__self__.plotdata,\
                            label=str(option),color=colors[i])
                    i+=1
                if lines==True:
                    __self__.master.tagged = True
                    for element in FIND_ELEMENT_LIST:
                        if element == "custom":
                            energies = plottables_dict[element]
                            __self__.plot.plot((energies[0],energies[0]),\
                                    (0,__self__.plotdata.max()),'k--',color="cornflowerblue",\
                                    label="Custom Low")
                            __self__.plot.plot((energies[1],energies[1]),\
                                    (0,__self__.plotdata.max()),'k--',color="tomato",\
                                    label="Custom High")
                        else:
                            energies = plottables_dict[element]
                            __self__.plot.plot((energies,energies),\
                                    (0,__self__.plotdata.max()),'k--')

                __self__.plot.set_title('{0} {1}'.format(SpecRead.DIRECTORY,mode),**plot_font)
                __self__.plot.set_xlabel("Energy (KeV)")
                __self__.plot.legend()

            __self__.canvas.draw()
    
    def draw_ROI(__self__):
        __self__.master.tagged = True
        global MY_DATACUBE
        for element in MY_DATACUBE.ROI:
            __self__.plotdata = MY_DATACUBE.ROI[element]
            if MY_DATACUBE.max_counts[element+"_a"] == 0:
                try: net = (MY_DATACUBE.max_counts[element+"_b"],"Beta")
                except: net = (MY_DATACUBE.max_counts[element+"_a"],"Alpha")
            else: net = (MY_DATACUBE.max_counts[element+"_a"],"Alpha")
            roi_label = element + " Max net: {} in {}".format(int(net[0]),net[1])
            __self__.plot.semilogy(MY_DATACUBE.energyaxis,__self__.plotdata,label=roi_label)
        __self__.plot.semilogy(MY_DATACUBE.energyaxis,MY_DATACUBE.sum,label="Sum spectrum",color="blue")
        __self__.plot.legend()
        place_topleft(__self__.master.master,__self__.master)

    def draw_correlation(__self__,corr,labels):
        plot_font = {'fontname':'Times New Roman','fontsize':10}
        __self__.plot.set_title('{0}'.format(SpecRead.DIRECTORY),**plot_font)
        __self__.plot.set_xlabel(labels[0])
        __self__.plot.set_ylabel(labels[1])
        __self__.plot.scatter(corr[0],corr[1])
        place_topleft(__self__.master.master,__self__.master)

    def draw_selective_sum(__self__,DATACUBE,y_data,display_mode=None,lines=False):
        global FIND_ELEMENT_LIST
        __self__.plot.clear()
        plot_font = {'fontname':'Arial','fontsize':10}
        colors = ["blue","red","green"]
        __self__.plot.set_title('{0}'.format(DATACUBE.name),**plot_font)
        __self__.plot.set_ylabel("Counts")

        if display_mode == '-semilog':
            __self__.plotdata = y_data
            __self__.plot.semilogy(DATACUBE.energyaxis,__self__.plotdata,\
                    label="ROI Sum",color=colors[0])
            if lines==True:
                __self__.master.tagged = True
                for element in FIND_ELEMENT_LIST:
                    if element == "custom":
                        energies = plottables_dict[element]
                        __self__.plot.plot((energies[0],energies[0]),\
                                (0,__self__.plotdata.max()),'k--',color="cornflowerblue",\
                                label="Custom Low")
                        __self__.plot.plot((energies[1],energies[1]),\
                                (0,__self__.plotdata.max()),'k--',color="tomato",\
                                label="Custom High")
                    else:
                        energies = plottables_dict[element]
                        __self__.plot.plot((energies,energies),\
                                (0,__self__.plotdata.max()),'k--')
            __self__.plot.set_xlabel("Energy (KeV)")
            __self__.plot.legend()
        else:
            __self__.plotdata = y_data
            __self__.plot.plot(DATACUBE.energyaxis,__self__.plotdata,\
                    label="ROI Sum",color=colors[0])
            if lines==True:
                __self__.master.tagged = True
                for element in FIND_ELEMENT_LIST:
                    if element == "custom":
                        energies = plottables_dict[element]
                        __self__.plot.plot((energies[0],energies[0]),\
                                (0,__self__.plotdata.max()),'k--',color="cornflowerblue",\
                                label="Custom Low")
                        __self__.plot.plot((energies[1],energies[1]),\
                                (0,__self__.plotdata.max()),'k--',color="tomato",\
                                label="Custom High")
                    else:
                        energies = plottables_dict[element]
                        __self__.plot.plot((energies,energies),\
                                (0,__self__.plotdata.max()),'k--')
            __self__.plot.set_xlabel("Energy (KeV)")
            __self__.plot.legend()
        __self__.canvas.draw()


class Samples:

    def __init__(__self__):
        __self__.samples_database = {}
        __self__.mcacount = {}
        __self__.mca_extension = {}

    def splash_screen(__self__,parent):
        __self__.splash = Toplevel(parent.master)
        __self__.splash.resizable(False,False)
        __self__.splash.configure(bg="#DCDCDC")
        __self__.splash.geometry("640x480")
        __self__.splash.overrideredirect(True)
        __self__.splash.withdraw()
        __self__.splash.grid_rowconfigure(0,weight=10)
        __self__.splash.grid_rowconfigure(1,weight=1)
        __self__.splash.grid_columnconfigure(0,weight=1)
        __self__.splash.grid_columnconfigure(1,weight=1)
        __self__.splash_image = PhotoImage(file=os.getcwd()+"\\images\\splash.png")
        __self__.canvas = Label(__self__.splash, image = __self__.splash_image,bg="white")
        __self__.canvas.grid(row=0,column=0,columnspan=2)
        __self__.filequeue = StringVar()
        __self__.filequeue.set(" ")
        __self__.bar = Frame(__self__.splash,bg="#DCDCDC")
        __self__.bar.grid(row=1,column=0,columnspan=2,sticky=W+E)
        __self__.label1 = Label(__self__.bar, text="Reading samples files...\t",bg="#DCDCDC")
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
            __self__.popup.destroy()
        except:
            pass

    def pop_loader(__self__):
        __self__.popup = Toplevel(master=root.master)
        __self__.popup.resizable(False,False)
        __self__.popup.overrideredirect(True)
        x = __self__.popup.winfo_screenwidth()
        y = __self__.popup.winfo_screenheight()
        __self__.popup.geometry('{}x{}+{}+{}'.format(166, 51,\
                int((x/2)-80), int((y/2)-23)))
        __self__.outerframe = Frame(__self__.popup, bd=3, relief=RIDGE,\
                width=166, height=52)
        __self__.outerframe.grid(row=0,column=0,sticky=E+W)
        __self__.outerframe.grid_propagate(0)
        __self__.popup.label1 = Label(__self__.outerframe, text="Reading samples...")
        __self__.popup.label1.grid(row=0,column=0,sticky=W)       
        __self__.label2 = Label(__self__.outerframe, textvariable = __self__.filequeue)
        __self__.label2.grid(row=1,column=0,sticky=W)

    def list_all(__self__):
        logging.info("Loading sample list...")
        try:
            mca_prefix = None
            __self__.samples_database = {}

            samples = [name for name in os.listdir(SpecRead.samples_folder) \
                    if os.path.isdir(SpecRead.samples_folder+name)]
            for folder in samples:
                files = [name for name in os.listdir(SpecRead.samples_folder+folder) \
                        if name.lower().endswith('.mca') or name.lower().endswith(".txt")]
                extension = files[:]
                if files == []: pass
                else:
                    for item in range(len(files)): 
                        # displays file being read on splash screen
                        __self__.filequeue.set("{}".format(files[item]))
                        __self__.label2.update()
                        try: __self__.splash.update_idletasks()
                        except: __self__.popup.update_idletasks()
                        finally: pass
                        try:
                            files[item], extension[item] = \
                                    files[item].split("_",1)[0], files[item].split(".",1)[1]
                        except: pass
                    counter = dict((x,files.count(x)) for x in files)
                    counter_ext = dict((x,extension.count(x)) for x in extension)
                    
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
                        __self__.mcacount[folder] = len(files)
                        __self__.mca_extension[folder] = mca_extension
            
            output_folder = os.getcwd()+"\output\\"
            outputs = [folder for folder in os.listdir(output_folder) \
                    if os.path.isdir(output_folder + folder)]
            for folder in outputs:
                cubes = [cube for cube in os.listdir(output_folder + folder) \
                        if cube.lower().endswith('.cube')]
                if folder not in __self__.samples_database: 
                    if cubes != []: 
                        # sampes_database keys hold the mca prefixes
                        __self__.samples_database[folder] = "---"
                        __self__.mcacount[folder] = 0
                        __self__.mca_extension[folder] = "---"

        except IOError as exception:
            __self__.splash_kill()
            if exception.__class__.__name__ == "FileNotFoundError":
                logging.info("No folder {} found.".format(SpecRead.samples_folder))
            elif exception.__class__.__name__ == "PermissionError":
                logging.info("Cannot load samples. Error {}.".format(exception.__class__.__name__))
                messagebox.showerror(exception.__class__.__name__,"Acess denied to folder {}.\nIf error persists, try running the program with administrator rights.".format(SpecRead.samples_folder))
            else: pass
        __self__.splash_kill()
       

class Settings:        
        
    def __init__(__self__,parent):
        __self__.Settings = Toplevel(master=parent.master)
        __self__.Settings.resizable(False,False)
        __self__.CoreCount = cpu_count()
        __self__.ScreenFrame = Frame(__self__.Settings,padx=15,pady=15)
        __self__.ScreenFrame.grid(row=0,column=1)
        __self__.TextFrame = Frame(__self__.Settings,padx=15,pady=15)
        __self__.TextFrame.grid(row=0,column=0)
        sys_mem = dict(virtual_memory()._asdict())
        __self__.RAM_tot = convert_bytes(sys_mem["total"])
        __self__.RAM_free = convert_bytes(sys_mem["available"])
        __self__.build_widgets()
        __self__.Settings.title("Settings")
        icon = os.getcwd()+"\\images\\icons\\settings.ico"
        __self__.Settings.iconbitmap(icon)  
        __self__.Settings.protocol("WM_DELETE_WINDOW",__self__.kill_window)
        place_center(root.master,__self__.Settings)
        __self__.Settings.grab_set()

    def build_widgets(__self__):
        __self__.PlotMode = StringVar()
        __self__.CoreMode = BooleanVar()
        __self__.RAMMode = BooleanVar()
        __self__.RAMEntry = DoubleVar()
        __self__.RAMUnit = StringVar()
        __self__.WlcmMode = BooleanVar()
        
        __self__.PlotMode.set(root.PlotMode)
        __self__.CoreMode.set(root.MultiCore)
        __self__.RAMMode.set(root.RAM_limit)
        __self__.RAMEntry.set('%.2f'%(float(convert_bytes(root.RAM_limit_value).split(" ")[0])))
        __self__.RAMUnit.set(convert_bytes(root.RAM_limit_value).split(" ")[1])
        __self__.WlcmMode.set(root.checker)
        
        PlotLabel = Label(__self__.TextFrame,text="Plot mode: ")
        PlotLabel.grid(row=0,column=0,sticky=W)
        PlotOption = ttk.Combobox(__self__.ScreenFrame, textvariable=__self__.PlotMode, values=("Linear","Logarithmic"),width=13,state="readonly")
        PlotOption.grid(row=0,column=0,columnspan=3,sticky=E)
        
        CoreLabel = Label(__self__.TextFrame,text="Enable multi-core processing? ")
        CoreLabel.grid(row=1,column=0,sticky=W)
        CoreOption = Checkbutton(__self__.ScreenFrame, variable=__self__.CoreMode,pady=3)
        CoreOption.grid(row=1,rowspan=2,column=0,columnspan=2,sticky=E)
        CoreOptionText = Label(__self__.ScreenFrame, text="Yes",pady=3)
        CoreOptionText.grid(row=1,rowspan=2,column=2,sticky=E)
        CoreCountLabel = Label(__self__.TextFrame,text="Total number of cores: "+str(__self__.CoreCount))
        CoreCountLabel.grid(row=2,column=0,sticky=W)
        
        RAMLabel = Label(__self__.TextFrame,text="Limit RAM usage for multi-core? ")
        RAMLabel.grid(row=3,column=0,sticky=W)
        RAMUnit = Label(__self__.ScreenFrame, text=__self__.RAMUnit.get())
        RAMUnit.grid(row=4,column=2,sticky=W)
        RAMOption = Checkbutton(__self__.ScreenFrame, variable=__self__.RAMMode)
        RAMOption.grid(row=3,column=0,columnspan=2,sticky=E)
        RAMOptionText = Label(__self__.ScreenFrame, text="Yes")
        RAMOptionText.grid(row=3,column=2,sticky=E)
        __self__.RAMEntryBox = Entry(__self__.ScreenFrame, textvariable=__self__.RAMEntry,width=13-RAMUnit.winfo_width())
        __self__.RAMEntryBox.grid(row=4,column=0,columnspan=2,sticky=W)
        RAMCountLabel = Label(__self__.TextFrame,text="Available RAM: "+str(__self__.RAM_free))
        RAMCountLabel.grid(row=4,column=0,sticky=W)


        WlcmLabel = Label(__self__.TextFrame,text="Display welcome message at startup? ")
        WlcmLabel.grid(row=5,column=0,sticky=W)
        WlcmOption = Checkbutton(__self__.ScreenFrame, variable=__self__.WlcmMode)
        WlcmOption.grid(row=5,column=0,columnspan=2,sticky=E)
        WlcmOptionText = Label(__self__.ScreenFrame, text="Yes")
        WlcmOptionText.grid(row=5,column=2,sticky=E)
        
        __self__.ScreenFrame.grid_columnconfigure(1,pad=8)
        
        ButtonsFrame = Frame(__self__.Settings, padx=10, pady=10)
        ButtonsFrame.grid(row=3,column=0,columnspan=2)
        OKButton = Button(ButtonsFrame, text="OK", justify=CENTER,width=10,command=__self__.save_settings)
        OKButton.grid(row=3,column=0)
        CancelButton = Button(ButtonsFrame, text="Cancel", justify=CENTER,width=10,command=__self__.kill_window)
        CancelButton.grid(row=3,column=1)
    
    def write_to_ini(__self__):
        try: 
            inipath = os.getcwd() + "\settings.tag"
            ini = open(inipath,'w+')
            ini.write("{}\n".format(SpecRead.samples_folder))
            ini.write("<MultiCore>\t{}\n".format(root.MultiCore))
            ini.write("<PlotMode>\t{}\n".format(root.PlotMode))
            ini.write("<RAMLimit>\t{}\n".format(root.RAM_limit))
            ini.write("<welcome>\t{}".format(root.checker))
            ini.close()
            __self__.kill_window()
        except: 
            messagebox.showerror("Error","File inifile.ini not found.")
            root.master.destroy()

    def kill_window(__self__):
        try: 
            del root.SettingsWin 
            __self__.Settings.grab_release()
            __self__.Settings.destroy()
        except: pass

    def save_settings(__self__):
        root.RAM_limit = __self__.RAMMode.get()
        root.RAM_limit_value = restore_bytes(float(__self__.RAMEntry.get()),__self__.RAMUnit.get())
        root.MultiCore = __self__.CoreMode.get()
        root.PlotMode = __self__.PlotMode.get()
        root.checker = __self__.WlcmMode.get()
        if root.PlotMode == "Logarithmic": root.plot_display = "-semilog"
        if root.PlotMode == "Linear": root.plot_display = None

        refresh_plots()
        try: root.clipper.refresh_plot() 
        except: pass
        __self__.write_to_ini()


def grab_GUI_config(inifile):
    CoreMode,PlotMode,RAMMode = None, None, None
    ini = open(inifile,"r")
    for line in ini:
        line = line.replace("\n","")
        line = line.replace("\r","")
        if line.split("\t")[0] == "<MultiCore>": CoreMode = bool(line.split("\t")[1])
        if line.split("\t")[0] == "<PlotMode>": PlotMode = str(line.split("\t")[1])
        if line.split("\t")[0] == "<RAMLimit>": RAMMode = bool(line.split("\t")[1])
        if line.split("\t")[0] == "<welcome>": WlcmMode = bool(line.split("\t")[1])
    ini.close() 
    return CoreMode, PlotMode, RAMMode


class MainGUI:
    
    # *** Methods *** #
    
    # root_quit()
    # find_elements()
    # list_samples()
    # call_listsamples()
    # sample_select(event)
    # build_widgets()
    # write_stat()
    # reset_sample()
    # call_configure()
    # call_settings()
    # refresh_samples()
    # toggle_
    # wipe()

    def __init__(__self__):
        logging.info("Initializing program...")
        f = open(os.getcwd()+"\\settings.tag","r")
        for line in f:
            if line.startswith("<welcome>"):
                if line.split("\t")[1] == "True": __self__.checker = True
                else: __self__.checker = False
        f.close()
        __self__.master = Tk()
        __self__.master.withdraw() 
        __self__.SampleLoader = Samples()
        __self__.SampleLoader.splash_screen(__self__)
        __self__.master.after(200,__self__.SampleLoader.list_all())
        __self__.samples = __self__.SampleLoader.samples_database
        __self__.mcacount = __self__.SampleLoader.mcacount
        __self__.mca_extension = __self__.SampleLoader.mca_extension
        __self__.find_elements_diag = None
        __self__.ImageAnalyzers = []
        
        __self__.master.title("Piratininga SM {}".format(VERSION))
        __self__.master.resizable(False,False)
        __self__.sample_figure = Figure(figsize=(3,2), dpi=100)
        __self__.sample_plot =__self__.sample_figure.add_subplot(111)
        __self__.sample_plot.grid(b=None)
        __self__.sample_plot.axis('off')
        mapfont = {'fontname':'Arial','fontsize':10}
        __self__.sample_plot.set_title('Sample Counts Map',**mapfont)

        sys_mem = dict(virtual_memory()._asdict())
        inipath = os.getcwd()+"\settings.tag"
        __self__.MultiCore, __self__.PlotMode, __self__.RAM_limit = grab_GUI_config(inipath)
        __self__.RAM_limit_value = sys_mem["available"]
        if __self__.PlotMode == "Logarithmic": __self__.plot_display = "-semilog"
        if __self__.PlotMode == "Linear": __self__.plot_display = None
        
        __self__.build_widgets()
        __self__.toggle_(toggle='off')
        __self__.master.deiconify()
        __self__.pop_welcome()
               
    def root_quit(__self__):
        for widget in __self__.master.winfo_children():
            if isinstance(widget, Toplevel):
                widget.destroy()
        checkout_config()
        __self__.master.destroy()
        sys.exit()
    
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
            __self__.Toolbox.entryconfig("Height-mapping",state=NORMAL)
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
            __self__.Toolbox.entryconfig("Height-mapping",state=DISABLED)

    def refresh_samples(__self__):
        __self__.SampleLoader.pop_loader()
        __self__.SampleLoader.list_all()
        __self__.samples = __self__.SampleLoader.samples_database
        try: 
            __self__.SamplesWindow.destroy()
            __self__.list_samples()
        except: __self__.list_samples()

    def find_elements(__self__):
        try:
            if __self__.find_elements_diag.master.winfo_exists() == False:
                __self__.find_elements_diag = PeriodicTable(__self__)
                __self__.find_elements_diag.master.protocol("WM_DELETE_WINDOW",\
                        lambda: wipe_list())
            else:
                __self__.find_elements_diag.master.focus_force()
                place_center(__self__.master,__self__.find_elements_diag.master)
                pass
        except:
            __self__.find_elements_diag = PeriodicTable(__self__)
            __self__.find_elements_diag.master.protocol("WM_DELETE_WINDOW",\
                    lambda: wipe_list())
        
    def call_listsamples(__self__):

        """ Draws the sample list window """

        __self__.SamplesWindow = Toplevel(master=__self__.master, name="samples list")
        __self__.SamplesWindow.tagged = False
        __self__.SamplesWindow.title("Sample List")
        icon = os.getcwd()+"\\images\\icons\\icon.ico"
        __self__.SamplesWindow.resizable(False,True) 
        __self__.SamplesWindow.minsize(0,320)
        __self__.SamplesWindow_LabelLeft = Label(__self__.SamplesWindow, text="FOLDER")
        __self__.SamplesWindow_LabelRight = Label(__self__.SamplesWindow, text="MCA PREFIX")
        __self__.SamplesWindow_TableLeft = Listbox(__self__.SamplesWindow, height=__self__.SamplesWindow.winfo_height())
        __self__.SamplesWindow_TableRight = Listbox(__self__.SamplesWindow, height=__self__.SamplesWindow.winfo_height())
        __self__.SamplesWindow_TableLeft.bind("<Double-Button-1>", __self__.sample_select)
        __self__.SamplesWindow_TableLeft.bind("<Return>", __self__.sample_select)
        __self__.SamplesWindow_TableLeft.bind("<Button-3>", __self__.sample_popup)
        
        __self__.SamplesWindow_LabelLeft.grid(row=0,column=0)
        __self__.SamplesWindow_LabelRight.grid(row=0,column=1)
        __self__.SamplesWindow_TableLeft.grid(pady=5, row=1,column=0,sticky=N+S)
        __self__.SamplesWindow_TableRight.grid(pady=5, row=1,column=1,sticky=N+S)

        Grid.rowconfigure(__self__.SamplesWindow, 1, weight=1)
   
        __self__.SamplesWindow.popup = Menu(__self__.SamplesWindow, tearoff=0)
        __self__.SamplesWindow.popup.add_command(label="Load",command=__self__.sample_select)
        __self__.SamplesWindow.popup.add_command(label="Save density map",command=__self__.export_density_map)
        __self__.SamplesWindow.popup.add_command(label="Open files location",command=__self__.open_files_location)
        __self__.SamplesWindow.popup.add_command(label="Open output folder",command=__self__.open_output_folder)

        for key in __self__.samples:
            __self__.SamplesWindow_TableLeft.insert(END,"{}".format(key))
            __self__.SamplesWindow_TableRight.insert(END,"{}".format(__self__.samples[key]))

        place_topleft(__self__.master,__self__.SamplesWindow)
        __self__.SamplesWindow.iconbitmap(icon)
        __self__.SamplesWindow_TableRight.config(state=DISABLED)
        __self__.SamplesWindow_TableLeft.focus_set()

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
                place_topleft(__self__.master,__self__.SamplesWindow)
                pass
            else: __self__.call_listsamples()
        except: __self__.call_listsamples()
    
    def sample_select(__self__,event=""):
    
        """ Loads the sample selected from the sample list menu. If the cube is 
        compiled, loads it to memory. If not, the configuration dialog is called """

        __self__.master.deiconify()
        __self__.master.focus_set()
        for widget in __self__.master.winfo_children():
            if isinstance(widget, Toplevel): 
                try: 
                    if widget.tagged == True: widget.destroy()
                except:
                    pass
        __self__.toggle_('off')
        
        # destroy any open configuration window
        try: __self__.ConfigDiag.destroy()
        except: pass

        #index = int(event.widget.curselection()[0])
        #value = event.widget.get(index)
        value = __self__.SamplesWindow_TableLeft.get(ACTIVE)
        
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
            SpecRead.setup_from_datacube(MY_DATACUBE,__self__.samples)
            __self__.SampleVar.set("Sample on memory: "+SpecRead.selected_sample_folder)
            __self__.toggle_(toggle='on')    
            __self__.write_stat()   
            __self__.draw_map()
        else: 
            SpecRead.conditional_setup(name=value)
            __self__.call_configure()

    def pop_welcome(__self__):
        
        """Displays a pop-up window with information on the software"""
        if __self__.checker == True:
            __self__.welcome_window = Welcome(__self__.master)
            __self__.welcome_window.master.grab_set()
            place_center(__self__.master, __self__.welcome_window.master)
        else: pass

    def sample_popup(__self__,event):

        """Call SamplesWindow method to pop a loading screen
        while it reads the mca files in the newly selected folder"""

        __self__.SamplesWindow_TableLeft.select_clear(0,END)
        idx = __self__.SamplesWindow_TableLeft.nearest(event.y)
        __self__.SamplesWindow_TableLeft.select_set(idx)
        __self__.SamplesWindow_TableLeft.activate(idx)
        try: __self__.SamplesWindow.popup.tk_popup(event.x_root, event.y_root, entry="")
        finally: __self__.SamplesWindow.popup.grab_release()
    
    def draw_map(__self__):
        global MY_DATACUBE
        try: 
            __self__.sample_plot.imshow(MY_DATACUBE.densitymap, cmap='jet')
            __self__.plot_canvas.draw()
        except: 
            blank = np.zeros([20,20])
            __self__.sample_plot.imshow(blank, cmap='jet')
            __self__.plot_canvas.draw()
    
    def open_files_location(__self__, event=""):
        value = __self__.SamplesWindow_TableLeft.get(ACTIVE)
        path = SpecRead.samples_folder + value + "\\"
        local_cube_path = SpecRead.workpath+'\output\\'+value+'\\'+value+'.cube'
        if os.path.exists(local_cube_path):
            global MY_DATACUBE
            __self__.sample_select(event)
            path = MY_DATACUBE.root
            path = os.path.realpath(path)
            os.startfile(path)
        elif os.path.exists(path):
            """if datacube is not compiled, check if mca files are under 
            the selected sample folder chosen by the user"""
            path = os.path.realpath(path)
            os.startfile(path)
        else:
            messagebox.showinfo("Directory not found.","Sample files not found! Path {} couldn't be located.".format(path))

    def open_output_folder(__self__, event=""):
        value = __self__.SamplesWindow_TableLeft.get(ACTIVE)
        path = os.getcwd()+"\\output\\"+value
        if os.path.exists(path):
            path = os.path.realpath(path)
            os.startfile(path)
        else:
            messagebox.showinfo("Directory not found.","Sample may be uncompiled. Output directory for sample {} not found.".format(value))

    def export_density_map(__self__,event=""):
        global MY_DATACUBE
        __self__.sample_select(event)
        if os.path.exists(SpecRead.cube_path): 
            f = filedialog.asksaveasfile(mode='w', defaultextension=".png")
        else: 
            return
        if f is None: 
            return
        __self__.sample_figure.savefig(f.name, format="png",dpi=600) 
        return 0

    def wipe(__self__,e=""):
        try: 
            __self__.ConfigDiag.grab_release()
            __self__.ConfigDiag.destroy()
        except: logging.warning("Tried to destroy ConfigDiag before calling it for the \
                first time")
        global MY_DATACUBE
        MY_DATACUBE = None
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
            __self__.sample_plot.imshow(__self__.densitymap,cmap='jet',label='Counts Map')
        except: 
            __self__.sample_plot.imshow(np.zeros([20,20]))
    
        
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
        __self__.summation.draw_spec(mode=['summation'],display_mode=root.plot_display,lines=False)
        place_topleft(__self__.master,__self__.summation.master)
    
    def call_mps(__self__):
        master = __self__.master
        __self__.MPS = PlotWin(master)
        __self__.MPS.draw_spec(mode=['mps'],display_mode=root.plot_display,lines=False)
        place_topleft(__self__.master,__self__.MPS.master)
    
    def call_combined(__self__):
        master = __self__.master
        __self__.combined = PlotWin(master)
        __self__.combined.draw_spec(mode=['summation','mps'],display_mode=root.plot_display,lines=False)
        place_topleft(__self__.master,__self__.combined.master)

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
        __self__.MenuBar.add_command(label="Author", command=call_author)
        __self__.derived_spectra.add_command(label="Summation", command=__self__.call_summation)
        __self__.derived_spectra.add_command(label="Maximum Pixel Spectra (MPS)", \
                command=__self__.call_mps)
        __self__.derived_spectra.add_command(label="Combined", command=__self__.call_combined)
        __self__.Toolbox.add_command(label="Change samples folder . . .", command=prompt_folder)
        __self__.Toolbox.add_command(label="Load sample", command=__self__.list_samples)
        __self__.Toolbox.add_command(label="Reset sample", command=__self__.reset_sample)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_cascade(label="Derived spectra", menu=__self__.derived_spectra)
        __self__.Toolbox.add_command(label="Check calibration", command=__self__.plot_calibration_curve)
        __self__.Toolbox.add_command(label="Verify calculated ROI", command=__self__.plot_ROI)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_command(label="Map elements", command=__self__.find_elements)
        __self__.Toolbox.add_command(label="Height-mapping", command=doNothing)
        __self__.Toolbox.add_command(label="Image Analyzer . . .", command=open_analyzer)
        __self__.Toolbox.add_separator()
        __self__.Toolbox.add_command(label="Settings", command=__self__.call_settings)
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
        FindElementButton_icon = PhotoImage(file = os.getcwd()+'\images\icons\\rubik.png')
        __self__.FindElementButton_icon = FindElementButton_icon.subsample(subx,suby)
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
        __self__.FindElementButton = Button(__self__.ButtonsFrame, text="  Map Elements", anchor=W,\
                image=__self__.FindElementButton_icon, compound=LEFT, bd=3, command=__self__.find_elements)
        __self__.FindElementButton.grid(row=1,column=1, sticky=W+E)
        __self__.QuitButton = Button(__self__.ButtonsFrame, text="  Quit", anchor=W,\
                image=__self__.QuitButton_icon, compound=LEFT, bd=3, command=__self__.root_quit)
        __self__.QuitButton.grid(row=2,column=1,sticky=W+E)
        __self__.SettingsButton = Button(__self__.ButtonsFrame, text="  Settings", anchor=W,\
                image=__self__.SettingsButton_icon, compound=LEFT, bd=3, command=__self__.call_settings)
        __self__.SettingsButton.grid(row=2,column=0,sticky=W+E)
        
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
        __self__.SampleVar.set("Sample on memory: "+SpecRead.DIRECTORY)
        
        # wipe all text
        __self__.StatusBox.delete(0,END)
        __self__.TableRight.delete(0,END)
        __self__.TableMiddle.delete(0,END)
        __self__.TableLeft.delete(0,END)

        if os.path.exists(SpecRead.selected_sample_folder):
            __self__.StatusBox.insert(\
                    END, "\nLooking for spectra files at: {0}\n".format(SpecRead.selected_sample_folder))
            __self__.StatusBox.insert(END, "\n{} spectra found!\n".format(root.mcacount[SpecRead.DIRECTORY]))
            __self__.no_sample = False
        else: 
            __self__.StatusBox.insert(\
                    END, "\nLooking for spectra files at: {0}\n".format(SpecRead.selected_sample_folder))
            __self__.StatusBox.insert(END, "\nSpetra for sample {} not found!\n".format(SpecRead.DIRECTORY))
            __self__.StatusBox.insert(END, "\nUsing compiled cube data.\n")
            __self__.no_sample = True

        if os.path.exists(SpecRead.cube_path):
            cube_stats = os.stat(SpecRead.cube_path)
            cube_size = convert_bytes(cube_stats.st_size)
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
        
        def repack(__self__, sample):
            logging.warning("Cube {} and its output contents were erased!".\
                    format(sample))
            shutil.rmtree(SpecRead.output_path)
            try: x,y,tag_dimension_file = SpecRead.getdimension()
            except OSError as exception:
                tag_dimension_file = False
            if tag_dimension_file == True:
                try: 
                    os.remove(SpecRead.dimension_file)
                    logging.warning("Custom image dimension was deleted.")
                except: raise PermissionError("Can't delete custom dimension file!")
            load_cube()
            __self__.write_stat()
            __self__.toggle_(toggle='off')
            __self__.ResetWindow.grab_release()
            __self__.wipe()
            if __self__.mca_extension[sample] == "---": __self__.samples.pop(sample,None)
            __self__.list_samples()
            __self__.draw_map()
            __self__.ResetWindow.destroy()

        if os.path.exists(SpecRead.cube_path):
            # creates dialogue to warn cube exists and promp to repack data
            __self__.ResetWindow = Toplevel(master=__self__.master)
            __self__.ResetWindow.title("Attention!")
            __self__.ResetWindow.resizable(False,False)
            LocalLabel = Label(__self__.ResetWindow, text=\
                    "Resetting the sample will erase all files in the OUTPUT folder of sample {}! Are you sure you want to proceed?".\
                    format(SpecRead.DIRECTORY),padx=10, pady=4, wraplength=250)
            LocalLabel.pack()
            Erase_ico = PhotoImage(file = os.getcwd()+'\images\icons\erase.png')
            __self__.Erase_ico = Erase_ico.zoom(2, 2)
            EraseLabel = Label(__self__.ResetWindow, image = __self__.Erase_ico).\
                    pack(side=LEFT, pady=8, padx=16)
            YesButton = Button(__self__.ResetWindow, text="Yes", justify=CENTER,\
                    command=lambda: repack(__self__,MY_DATACUBE.config["directory"]), \
                    width=10, bd=3).pack(side=TOP,pady=5)
            NoButton = Button(__self__.ResetWindow, text="No", justify=CENTER,\
                    command=__self__.ResetWindow.destroy, width=10, bd=3).pack(side=TOP, pady=5)
            
            place_center(__self__.master,__self__.ResetWindow)
            icon = os.getcwd()+"\\images\\icons\\icon.ico"
            __self__.ResetWindow.iconbitmap(icon)
            __self__.ResetWindow.grab_set()

        else:
            ErrorMessage("Can't find sample {}!".format(SpecRead.DIRECTORY))

    def call_configure(__self__):
        if not os.path.exists(SpecRead.dimension_file):
            dimension = dimension_diag(SpecRead.DIRECTORY)
            __self__.master.wait_window(dimension.win) 
            if dimension.exit_code == "cancel":
                __self__.wipe()
                return 0
        else:
            __self__.config_xy = SpecRead.getdimension()

        __self__.ManualParam = []

        def manual_calib():
            
            def save_param():
                EntryParam = [\
                        [ch1.get(),en1.get()],\
                        [ch2.get(),en2.get()],\
                        [ch3.get(),en3.get()],\
                        [ch4.get(),en4.get()]]
                for index in range(len(EntryParam)):
                    if EntryParam[index][0] > 0 and EntryParam[index][1] > 0:
                        __self__.ManualParam.append(EntryParam[index])
                    elif EntryParam[index][0] < 0 or EntryParam[index][1] < 0:
                        messagebox.showerror("Calibration Error",\
                                "Can't receive negative values!")
                        __self__.ManualParam = []
                        raise ValueError("Manual calibration can't receive negative values!")
                save_config()

            CalibDiag = Toplevel(master = __self__.ConfigDiag)
            CalibDiag.title("Manual configuration")
            CalibDiag.resizable(False,False)
            icon = os.getcwd()+"\\images\\icons\\settings.ico"
            CalibDiag.iconbitmap(icon)
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
                # gets calibration parameters read while performing last 
                # setup or conditional setup and fills entries
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
            
            OkButton = Button(ButtonFrame,text="SAVE",command=save_param).\
                    grid(row=5,columnspan=2)
            
            place_center(__self__.ConfigDiag,CalibDiag)
        
        def check_method_and_save():
            if CalibVar.get() == 'manual':
                manual_calib()
            else: save_config()
        
        def call_PeakClipper(__self__):
            __self__.ConfigDiag.grab_release()
            __self__.clipper = PeakClipper(root.master)
            __self__.clipper.master.grab_set()

        def save_config():
            global snip_config
            configdict = {'directory':DirectoryVar.get(),'bgstrip':BgstripVar.get(),\
                    'ratio':RatioVar.get(),'thickratio':ThickVar.get(),\
                    'calibration':CalibVar.get(),'enhance':EnhanceVar.get(),\
                    'peakmethod':MethodVar.get(),'bg_settings':snip_config}
            
            if not os.path.exists(SpecRead.dimension_file):
                os.mkdir(SpecRead.output_path)
                dm_file = open(SpecRead.output_path + "colonneXrighe.txt","w")
                dm_file.write("righe\t{}\n".format(__self__.config_xy[0]))
                dm_file.write("colonne\t{}\n".format(__self__.config_xy[1]))
                dm_file.write(5*"*"+" user input data "+5*"*")
                dm_file.close()

            if os.path.exists(SpecRead.samples_folder + configdict['directory'] + '\\'):
                
                SpecRead.DIRECTORY = configdict["directory"] + '\\'
                SpecRead.selected_sample_folder = \
                        SpecRead.samples_folder + SpecRead.DIRECTORY+'\\'
                SpecRead.FIRSTFILE_ABSPATH = SpecRead.findprefix()

                # reads configuration integrity prior opening config.cfg for writing
                if configdict['calibration'] == 'manual': 
                    calibparam = __self__.ManualParam
                    # save_config only passes positive integers forward
                    # in the case other data is received as user input, this will be filtered
                    # absence of acceptable parameters returns an empty list
                    if calibparam == []: 
                        messagebox.showerror("Calibration Error",\
                                "No acceptable parameters passed!")
                        __self__.ManualParam = []
                        raise ValueError("No acceptable parameters passed!")
                    elif len(calibparam) <= 1: 
                        messagebox.showerror("Calibration Error",\
                                "Need at least two anchors!")
                        __self__.ManualParam = []
                        raise ValueError("Calibration need at least two anchors!")
                else: 
                    SpecRead.CONFIG["calibration"] = "from_source"
                    calibparam = SpecRead.getcalibration()

                cfgpath = os.getcwd() + "\config.cfg"
                cfgfile = open(cfgpath,"w+")
                cfgfile.write("<<CONFIG_START>>\r")
                for key in configdict:
                    cfgfile.write("{} = {}\r".format(key,configdict[key]))
                cfgfile.write("<<CALIBRATION>>\r")
                for pair in calibparam:
                    cfgfile.write("{0}\t{1}\r".format(pair[0],pair[1]))
                cfgfile.write("<<END>>\r")
                cfgfile.close()
                
                SpecRead.setup()
                __self__.ConfigDiag.grab_release()
                __self__.ConfigDiag.destroy()
                try: 
                    __self__.ResetWindow.destroy()
                    CalibDiag.destroy()
                except: pass
                 
                call_compilecube()
                load_cube()
                __self__.write_stat()
                __self__.draw_map()
                __self__.toggle_(toggle='on')

            else:
                
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
                ErrorMessage("Directory {} not found!\nConfig.cfg saved!".\
                        format(configdict['directory']))
                
                SpecRead.setup()
                __self__.ConfigDiag.grab_release()
                __self__.ConfigDiag.destroy()
                try: 
                    __self__.ResetWindow.destroy()
                    CalibDiag.destroy()
                except: pass
                __self__.write_stat()
                __self__.draw_map()
       
        __self__.ConfigDiag = Toplevel(master = __self__.master)
        __self__.ConfigDiag.grab_set()
        __self__.ConfigDiag.resizable(False,False)
        __self__.ConfigDiag.title("Configuration")
        __self__.ConfigDiag.bind("<Escape>",__self__.wipe)
        __self__.ConfigDiag.protocol("WM_DELETE_WINDOW",__self__.wipe)
        __self__.ConfigDiagFrame = Frame(__self__.ConfigDiag,padx=15,pady=15)
        __self__.ConfigDiagLabels = Frame(__self__.ConfigDiag,padx=15,pady=15)
        __self__.ConfigDiagFrame.grid(row=0, column=1)
        __self__.ConfigDiagLabels.grid(row=0, column=0)

        #Label1 = Label(__self__.ConfigDiagLabels, text="Sample directory:")
        Label2 = Label(__self__.ConfigDiagLabels, text="Background strip mode:")
        Label3 = Label(__self__.ConfigDiagLabels, text="Configure BG strip:")
        Label4 = Label(__self__.ConfigDiagLabels, text="Calibration:")
        #Label5 = Label(__self__.ConfigDiagLabels, text="Thick ratio:")
        #Label6 = Label(__self__.ConfigDiagLabels, text="Enhance image?")
        Label7 = Label(__self__.ConfigDiagLabels, text="Netpeak area method:")
        Label8 = Label(__self__.ConfigDiagLabels, text="Calculate ratios?")
        
        #Label1.grid(row=0,column=0,sticky=W,pady=2)
        Label2.grid(row=1,column=0,sticky=W,pady=2)
        Label3.grid(row=2,column=0,sticky=W,pady=2)
        Label4.grid(row=3,column=0,sticky=W,pady=2)
        #Label5.grid(row=4,column=0,sticky=W,pady=2)
        #Label6.grid(row=5,column=0,sticky=W,pady=2)
        Label7.grid(row=6,column=0,sticky=W,pady=2)
        Label8.grid(row=7,column=0,sticky=W,pady=2)
        
        ConfigDiagRatioYes = Label(__self__.ConfigDiagFrame, text="Yes")
        ConfigDiagRatioYes.grid(row=7,column=1,sticky=E,pady=2)
        ConfigDiagEnhanceYes = Label(__self__.ConfigDiagFrame, text="Yes")
        ConfigDiagEnhanceYes.grid(row=6,column=1,sticky=E,pady=2)
        
        BgstripVar = StringVar()
        __self__.ConfigDiagBgstrip = ttk.Combobox(__self__.ConfigDiagFrame, textvariable=BgstripVar, values=("None","SNIPBG"),state="readonly",width=13+ConfigDiagRatioYes.winfo_width())
        
        DirectoryVar = StringVar()
        #__self__.ConfigDiagDirectory = Entry(__self__.ConfigDiagFrame,textvariable=DirectoryVar,width=__self__.ConfigDiagBgstrip.winfo_width())
        
        RatioVar = BooleanVar()
        __self__.ConfigDiagRatio = Checkbutton(__self__.ConfigDiagFrame, variable=RatioVar)
        
        ThickVar = DoubleVar()
        #__self__.ConfigDiagThick = Entry(__self__.ConfigDiagFrame, textvariable=ThickVar,width=13)
        __self__.ConfigDiagSetBG = Button(__self__.ConfigDiagFrame, text="Set BG",\
               width=13+ConfigDiagRatioYes.winfo_width(),command=lambda: call_PeakClipper(__self__))
        
        CalibVar = StringVar()
        __self__.ConfigDiagCalib = ttk.Combobox(__self__.ConfigDiagFrame, textvariable=CalibVar, values=("from_source","manual"),\
                state="readonly",width=13+ConfigDiagRatioYes.winfo_width())

        EnhanceVar = BooleanVar()
        #__self__.ConfigDiagEnhance = Checkbutton(__self__.ConfigDiagFrame, variable=EnhanceVar)
        
        MethodVar = StringVar()
        __self__.ConfigDiagMethod = ttk.Combobox(__self__.ConfigDiagFrame, textvariable=MethodVar, values=("simple_roi","auto_roi"),\
                state="readonly",width=13+ConfigDiagRatioYes.winfo_width())
        
        DirectoryVar.set(SpecRead.CONFIG.get('directory'))
        BgstripVar.set(SpecRead.CONFIG.get('bgstrip'))
        RatioVar.set(SpecRead.CONFIG.get('ratio'))
        ThickVar.set(SpecRead.CONFIG.get('thickratio'))
        CalibVar.set(SpecRead.CONFIG.get('calibration'))
        MethodVar.set(SpecRead.CONFIG.get('peakmethod'))
        EnhanceVar.set(SpecRead.CONFIG.get('enhance'))

        #__self__.ConfigDiagDirectory.grid(row=0,column=1,sticky=E)
        __self__.ConfigDiagBgstrip.grid(row=1,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagSetBG.grid(row=2,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagCalib.grid(row=3,column=0,columnspan=2,sticky=E,pady=2)
        #__self__.ConfigDiagThick.grid(row=4,column=0,columnspan=2,sticky=E,pady=2)
        #__self__.ConfigDiagEnhance.grid(row=5,column=0,sticky=E,pady=2)
        __self__.ConfigDiagMethod.grid(row=6,column=0,columnspan=2,sticky=E,pady=2)
        __self__.ConfigDiagRatio.grid(row=7,column=0,sticky=E,pady=2)
        
        dimension_text = "Image size = {0} x {1} pixels"\
                .format(__self__.config_xy[0],__self__.config_xy[1])
        img_dimension_display = Label(__self__.ConfigDiag,text=dimension_text)
        img_dimension_display.grid(row=1,column=0,sticky=W,padx=17,pady=2)

        ButtonsFrame = Frame(__self__.ConfigDiag)
        ButtonsFrame.grid(row=8,columnspan=2,pady=10,padx=10)
        SaveButton = Button(ButtonsFrame, text="Save", justify=CENTER, width=10,\
                command=check_method_and_save)
        SaveButton.grid(row=8,column=0,sticky=S)
        CancelButton = Button(ButtonsFrame, text="Cancel", justify=CENTER, width=10,\
                command=__self__.wipe)
        CancelButton.grid(row=8,column=1,sticky=S)
        
        place_center(root.master,__self__.ConfigDiag)
        icon = os.getcwd()+"\\images\\icons\\settings.ico"
        __self__.ConfigDiag.iconbitmap(icon)
        __self__.master.wait_window(__self__.ConfigDiag)

        return 0

def refresh_plots(exclusive=""):

    """refresh one plot window exclusively or all open windows"""

    global FIND_ELEMENT_LIST
    if len(FIND_ELEMENT_LIST) > 0: 
        lines = True
    else: 
        lines = False
    
    if exclusive == "mps":
        try:
            root.MPS.draw_spec(\
                mode=['mps'],display_mode=root.plot_display,lines=lines)
            root.MPS.update_idletasks()
        except: pass
    elif exclusive == "summation":
        try: 
            root.summation.draw_spec(\
                mode=['summation'],display_mode=root.plot_display,lines=lines)
            root.summation.update_idletasks()
        except: pass
    elif exclusive == "combined":
        try: 
            root.combined.draw_spec(\
                mode=['summation','mps'],display_mode=root.plot_display,lines=lines)
            root.combined.update_idletasks()
        except: pass
    elif exclusive == "roi_sum":
        for API in root.ImageAnalyzers: 
            try:
                API.plot.draw_selective_sum(API.DATACUBE,
                        API.sum_spectrum,\
                        display_mode = root.plot_display,
                        lines = lines)
                API.plot.master.update_idletasks()
            except: pass
    else:
        try:
            root.MPS.draw_spec(\
                mode=['mps'],display_mode=root.plot_display,lines=lines)
            root.MPS.update_idletasks()
        except: pass
        try: 
            root.summation.draw_spec(\
                mode=['summation'],display_mode=root.plot_display,lines=lines)
            root.summation.update_idletasks()
        except: pass
        try: 
            root.combined.draw_spec(\
                mode=['summation','mps'],display_mode=root.plot_display,lines=lines)
            root.combined.update_idletasks()
        except: pass
        for API in root.ImageAnalyzers:
            try :
                API.plot.draw_selective_sum(API.DATACUBE,
                        API.sum_spectrum,\
                        display_mode = root.plot_display,
                        lines = lines)
                API.plot.master.update_idletasks()
            except: pass

    try: root.find_elements_diag.master.focus_force()
    except: pass


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
        __self__.master.body.grid(row=1,column=0, rowspan=9, columnspan=18,padx=(3,3),pady=(3,0))
        __self__.master.footer = Frame(__self__.master)
        __self__.master.footer.grid(row=10,column=0, columnspan=18)
        __self__.cvar1 = DoubleVar()
        __self__.cvar2 = DoubleVar()
        __self__.cvar1.set(0.0)
        __self__.cvar2.set(0.5)
        __self__.draw_buttons() 
        icon = os.getcwd()+"\\images\\icons\\rubik.ico"
        place_center(parent.master,__self__.master)
        __self__.master.iconbitmap(icon)

    
    def add_element(__self__,toggle_btn):
        global DEFAULTBTN_COLOR
        global FIND_ELEMENT_LIST
        if toggle_btn.config('relief')[-1] == 'sunken':
            toggle_btn.config(relief="raised")
            toggle_btn.config(bg=DEFAULTBTN_COLOR)
            FIND_ELEMENT_LIST.remove(toggle_btn.cget("text"))
            refresh_plots()
        else:
            toggle_btn.config(relief="sunken")
            toggle_btn.config(bg="yellow")
            FIND_ELEMENT_LIST.append(toggle_btn.cget("text"))
            refresh_plots()
    
    def add_custom_element(__self__,toggle_btn):
        global DEFAULTBTN_COLOR
        global FIND_ELEMENT_LIST
        if toggle_btn.config('relief')[-1] == 'sunken':
            toggle_btn.config(relief="raised")
            toggle_btn.config(bg=DEFAULTBTN_COLOR)
            FIND_ELEMENT_LIST.remove("custom")
            plottables_dict["custom"] = []
            refresh_plots()
        else:
            # setting casual number
            toggle_btn.config(relief="sunken")
            toggle_btn.config(bg="yellow")
            FIND_ELEMENT_LIST.append("custom")
            plottables_dict["custom"] = [__self__.cvar1.get(),__self__.cvar2.get()]
            refresh_plots()
     
       
    def save_and_run(__self__):
        
        if not FIND_ELEMENT_LIST: 
            __self__.master.destroy()
            messagebox.showinfo("Error", "No element input!")
        else:
            # disabled widgets to avoid user changes sample
            root.toggle_(toggle="off")
            root.SamplesWindow.destroy()
            
            root.MenuBar.entryconfig("Toolbox", state=DISABLED)
            root.ButtonLoad.config(state=DISABLED)
            for widget in __self__.master.body.winfo_children():
                try: widget.config(state=DISABLED)
                except: pass
            __self__.go.config(state=DISABLED)
            
            cube_status = os.stat(SpecRead.cube_path)
            cube_size = cube_status.st_size
            sys_mem = dict(virtual_memory()._asdict())
            rnt_mem = [(cube_size*len(FIND_ELEMENT_LIST)),sys_mem["available"]]
            process_memory = (convert_bytes(rnt_mem[0]),convert_bytes(rnt_mem[1]))
            needed_memory = cube_size*len(FIND_ELEMENT_LIST)
            
            if cube_size*(len(FIND_ELEMENT_LIST)) > sys_mem["available"]:
                logging.warning("Non-fatal MEMORY ERROR! Memony size needed for cube copies not available!")
                messagebox.showerror("Memory Error!","Multiprocessing copies the datacube for each running instance.\nMemory needed: {}\nMemory available: {}\nProcess will follow in a single instance and may take a while.".format(process_memory[0],process_memory[1]))   

            # multi-core mode
            if MY_DATACUBE.config["peakmethod"] != "simple_roi":
                if "custom" in FIND_ELEMENT_LIST: 
                    results = []
                    FIND_ELEMENT_LIST.remove("custom") 
                    lines = [__self__.cvar1.get(),__self__.cvar2.get()]
                    elmap, ROI = (grab_simple_roi_image(MY_DATACUBE,lines,\
                            custom_energy=True))
                    results.append((elmap, ROI, "custom"))
                    digest_results(MY_DATACUBE,results,["custom"])

                if len(FIND_ELEMENT_LIST) > 2 and MY_DATACUBE.img_size > 999\
                        and needed_memory < sys_mem["available"] and\
                        needed_memory < root.RAM_limit_value and root.MultiCore == True:
                    
                    cuber = Cube_reader(MY_DATACUBE,FIND_ELEMENT_LIST)
                    results = cuber.start_workers()
                    cuber.p_bar.update_text("Digesting results...")
                    results = sort_results(results,FIND_ELEMENT_LIST)
                    digest_results(MY_DATACUBE,results,FIND_ELEMENT_LIST)
                    cuber.p_bar.destroybar()

                # single-core mode
                else: 
                    if len(FIND_ELEMENT_LIST) > 0:
                        MAPS = getpeakmap(FIND_ELEMENT_LIST,MY_DATACUBE)
                    else: pass
            
            else:
                results = []
                for element in FIND_ELEMENT_LIST:
                    if element == "custom":
                        lines = [__self__.cvar1.get(),__self__.cvar2.get()]
                        elmap, ROI = (grab_simple_roi_image(MY_DATACUBE,lines,\
                                custom_energy=True))
                        results.append((elmap, ROI, "custom"))
                    else:
                        lines = select_lines(element,MY_DATACUBE.config["ratio"])
                        elmap, ROI = (grab_simple_roi_image(MY_DATACUBE,lines))
                        results.append((elmap, ROI, element))
                sort_results(results,FIND_ELEMENT_LIST)
                digest_results(MY_DATACUBE,results,FIND_ELEMENT_LIST)

            # reactivate widgets
            wipe_list()
            root.toggle_(toggle="on")
            root.MenuBar.entryconfig("Toolbox", state=NORMAL)
            root.ButtonLoad.config(state=NORMAL)
            root.write_stat()
            refresh_plots()

    def draw_buttons(__self__):
        btnsize_w = 3
        btnsize_h = 1
        __self__.H = Button(__self__.master.body, text="H",width=btnsize_w,height=btnsize_h,relief='raised',command= lambda: __self__.add_element(__self__.H))
        global DEFAULTBTN_COLOR
        DEFAULTBTN_COLOR = __self__.H.cget("background")
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

def check_screen_resolution(resolution_tuple):
    pop = Tk()
    pop.withdraw()
    limit_w, limit_h = resolution_tuple[0], resolution_tuple[1]
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    if w > limit_w or h > limit_h:
        messagebox.showinfo("Info","Your current screen resolution is {}x{}. This program was optmized to work in 1080p resolution. If the windows are too small or if any problems are experienced with buttons and icons, please try lowering your screen resolution and setting the Windows scaling option to 100%.".format(w,h))
    pop.destroy()

def license_error(version):
    pop = Tk()
    pop.withdraw()
    messagebox.showerror("License error!","Even though this is an open source software, this is a beta UNRELEASED version made by the author. To run this specific version of the software your machine has to be authorized beforehand. This is done to avoid an unexperienced user of producing biased or wrong information with this current unreleased version {0}, which contains known bugs. Further information can be provided upon contacting the author: sergio.lins@roma3.infn.it".format(version))
    pop.destroy()
    raise PermissionError("Machine unauthorized")

if __name__.endswith('__main__'):         
    
    optimum_resolution = (1920,1080)

    # tcl/Tk imports
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
     
    # general utilities
    import numpy as np
    import sys, os, copy, pickle, stat, random
    import shutil
    from psutil import virtual_memory
    from psutil import cpu_count
    import logging, time
    from multiprocessing import freeze_support
    freeze_support()
    
    # matplotlib imports
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    from matplotlib import style
    style.use('ggplot')

    # tries to create logfile on exe folder
    try: 
        logging.basicConfig(format = '%(asctime)s\t%(levelname)s\t%(message)s',\
            filename = 'logfile.log',level = logging.INFO)
        with open('logfile.log','w+') as mylog: mylog.truncate(0)
        logging.info('*'* 10 + ' LOG START! ' + '*'* 10)
        log_start = "{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        logging.info(log_start)   
    except IOError as exception:
        p = Tk()
        p.iconify()
        messagebox.showerror(exception.__class__.__name__,"Acess denied to folder {}.\nIf error persists, try running the program with administrator rights.".format(os.getcwd()))
        #sys.exit()
    
    check_screen_resolution(optimum_resolution)
    # internal imports
    import SpecRead
    from ReadConfig import checkout_config
    from ImgMath import LEVELS
    from ImgMath import threshold, low_pass, iteractive_median, write_image, stackimages
    from SpecMath import getstackplot, correlate, peakstrip
    from SpecMath import datacube as Cube
    from EnergyLib import plottables_dict
    from Mapping import getpeakmap, grab_simple_roi_image, select_lines 
    from Mapping_parallel import Cube_reader, sort_results, digest_results

    logging.info("Loading GUI...")
    start_up()
    root = MainGUI()
    GUIicon = os.getcwd()+"\\images\\icons\\icon.ico"
    root.master.iconbitmap(GUIicon)  
    root.master.mainloop()

