#################################################################
#                                                               #
#          Graphical Interface and Core file                    #
#                        version: 0.0.1α                        #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################
global MY_DATACUBE, FIND_ELEMENT_LIST
MY_DATACUBE, FIND_ELEMENT_LIST = None, None

def start_up():
    SpecRead.conditional_setup()
    logging.info("Setting up...")
    try: load_cube()
    except: pass
    logging.info("Done.")
    global FIND_ELEMENT_LIST
    FIND_ELEMENT_LIST = []


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
    #window2.deiconify()

def spawn_center(window):
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    
    w_width = window.winfo_width()
    w_height = window.winfo_height()

    window.geometry("{}x{}+{}+{}".format(w_width,w_height,\
            int((width/2)-(w_width/2)),int((height/2)-(w_height/2))))

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

def call_author():
    AuthorWin = Toplevel(master=root.master)
    AuthorWin.title("Author")
    AuthorWin.resizable(False,False)
    infotext="Author: Sergio Lins\nSoftware version: {0}\nContact: sergio.lins@roma3.infn.it".format(VERSION)
    winFrame = Frame(AuthorWin)
    winFrame.pack(padx=(16,16),pady=(16,16))
    Info = Label(winFrame,text=infotext, wraplength=640, anchor=W, justify=LEFT)
    Info.pack()

def open_analyzer():
    ImgAnalyzer = ImageAnalyzer(root.master)

def call_compilecube():
    
    try: os.mkdir(SpecRead.output_path)
    except: 
        #print("Cannot create folder {}".format(SpecRead.output_path))
        pass
    
    if os.path.exists(SpecRead.cube_path): 
        pass
    else:
        #try: 
        specbatch = Cube(['xrf'],SpecRead.CONFIG)
        specbatch.compile_cube()
        #except:
        #    ErrorMessage("Can't find sample {}!".format(SpecRead.DIRECTORY))

def prompt_folder():
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


class Annotator:

    def __init__(__self__,datacube,application):
        __self__.datacube = datacube
        __self__.element1 = application.Map1Var.get()
        __self__.element2 = application.Map2Var.get()
        __self__.plot1 = application.plot1
        __self__.plot2 = application.plot2
        __self__.canvas1 = application.canvas1
        __self__.canvas2 = application.canvas2
        __self__.figure1 = application.figure1
        __self__.figure2 = application.figure2
        __self__.roibox1 = application.roibox1
        __self__.roibox2 = application.roibox2
        __self__.ratebox = application.ratebox
        __self__.area1 = Rectangle((0,0),1,1,fill=False,snap=True,color="red",linewidth=3)
        __self__.area2 = Rectangle((0,0),1,1,fill=False,snap=True,color="red",linewidth=3)
        __self__.x0 = None
        __self__.y0 = None
        __self__.x1 = None
        __self__.y1 = None
        __self__.plot1.add_patch(__self__.area1)
        __self__.plot2.add_patch(__self__.area2)
        __self__.canvas1.mpl_connect("button_press_event",__self__.on_press)
        __self__.canvas1.mpl_connect("motion_notify_event",__self__.on_drag)
        __self__.canvas1.mpl_connect("button_release_event",__self__.on_release)
        __self__.canvas2.mpl_connect("button_press_event",__self__.on_press)
        __self__.canvas2.mpl_connect("motion_notify_event",__self__.on_drag)
        __self__.canvas2.mpl_connect("button_release_event",__self__.on_release)
        __self__.press, __self__.move = False, False

    def refresh_annotator(__self__,application):
        __self__.element1 = application.Map1Var.get()
        __self__.element2 = application.Map2Var.get()
        __self__.area1.remove()
        __self__.area2.remove()
        __self__.canvas1.draw()
        __self__.canvas2.draw()
        __self__.plot1 = application.plot1
        __self__.plot2 = application.plot2
        __self__.canvas1 = application.canvas1
        __self__.canvas2 = application.canvas2
        __self__.figure1 = application.figure1
        __self__.figure2 = application.figure2
        __self__.plot1.add_patch(__self__.area1)
        __self__.plot2.add_patch(__self__.area2)
        __self__.canvas1.mpl_connect("button_press_event",__self__.on_press)
        __self__.canvas1.mpl_connect("motion_notify_event",__self__.on_drag)
        __self__.canvas1.mpl_connect("button_release_event",__self__.on_release)
        __self__.canvas2.mpl_connect("button_press_event",__self__.on_press)
        __self__.canvas2.mpl_connect("motion_notify_event",__self__.on_drag)
        __self__.canvas2.mpl_connect("button_release_event",__self__.on_release)

    def wipe_annotator(__self__,application):
        __self__.area1.remove()
        __self__.area2.remove()
        __self__.canvas1.draw()
        __self__.canvas2.draw()
        __self__.roibox1["text"] = "Roi 1: None"
        __self__.roibox2["text"] = "Roi 2: None"
        __self__.ratebox["text"] = "Ratio: None"

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
            __self__.canvas1.draw()
            __self__.canvas2.draw()
            __self__.calculate_area()

    def on_release(__self__,event):
        __self__.press = False
        if __self__.press and not __self__.move:
            __self__.press = False
            __self__.move = False

    def calculate_area(__self__):
        __self__.area1_sum = 0
        __self__.area2_sum = 0
        unpacker1 = __self__.element1.split("_")
        unpacker2 = __self__.element2.split("_")
        
        # unpacks raw image, notice no normalization is done to match LEVELS levels of gray
        image1 = __self__.datacube.unpack_element(unpacker1[0],unpacker1[1])
        image2 = __self__.datacube.unpack_element(unpacker2[0],unpacker2[1])
        
        x_ = [__self__.x0,__self__.x1]
        y_ = [__self__.y0,__self__.y1]
        x_.sort()
        y_.sort()
        for x in range(y_[0],y_[1]):
            for y in range(x_[0],x_[1]):
                __self__.area1_sum += image1[x][y]
                __self__.area2_sum += image2[x][y]
        __self__.roibox1["text"] = "Roi 1: {}".format(int(__self__.area1_sum))
        __self__.roibox2["text"] = "Roi 2: {}".format(int(__self__.area2_sum))
        if __self__.area2_sum > 0:
            __self__.ratebox["text"] = "Ratio: {:.2f}".format(__self__.area1_sum/__self__.area2_sum)


class ImageAnalyzer:


    def __init__(__self__,parent):

        global MY_DATACUBE
        
        __self__.packed_elements = MY_DATACUBE.check_packed_elements()
        __self__.master = Toplevel(master=parent)
        #__self__.master.bind("<Configure>", __self__.resize)
        __self__.master.title("Image Analyzer v1.01a")
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
        __self__.sliders.pack(side=BOTTOM)
        __self__.buttons = Frame(__self__.sliders,padx=30)
        __self__.buttons.grid(row=0,column=0,rowspan=4)
        
        __self__.Map1Var = StringVar()
        __self__.Map1Counts = StringVar()
        __self__.Map1Counts.set("Select an element")
        __self__.Map2Var = StringVar()
        __self__.Map2Counts = StringVar()
        __self__.Map2Counts.set("Select an element")
        
        try:
            __self__.ElementalMap1 = np.zeros([MY_DATACUBE.dimension[0],MY_DATACUBE.dimension[1]])
            __self__.ElementalMap2 = np.zeros([MY_DATACUBE.dimension[0],MY_DATACUBE.dimension[1]])
        except:
            __self__.ElementalMap1 = np.zeros([1,1])
            __self__.ElementalMap2 = np.zeros([1,1])
        

        __self__.Map1Label = Label(__self__.sampler, textvariable=__self__.Map1Counts,width=30)
        __self__.Map1Label.grid(row=0, column=0, columnspan=3, sticky=W)
        __self__.Map1Combo = ttk.Combobox(__self__.sampler, textvariable=__self__.Map1Var,\
                values=__self__.packed_elements,width=5)
        __self__.Map1Combo.grid(row=0,column=3, sticky=W,padx=(16,16),pady=(8,4))
        
        __self__.Map2Label = Label(__self__.sampler, textvariable=__self__.Map2Counts,width=30)
        __self__.Map2Label.grid(row=0, column=5, columnspan=3, sticky=E)
        __self__.Map2Combo = ttk.Combobox(__self__.sampler, textvariable=__self__.Map2Var,\
                values=__self__.packed_elements,width=5)
        __self__.Map2Combo.grid(row=0,column=4, sticky=E,padx=(16,16),pady=(8,4))
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
        __self__.correlate = Button(__self__.buttons,text="Correlate maps",\
                command=__self__.get_correlation,width=15)
        __self__.correlate.grid(row=3,column=0)
        __self__.annotate = Button(__self__.buttons,text="Set ROI",\
                command=__self__.toggle_annotator,relief="raised",width=15)
        __self__.annotate.grid(row=4,column=0)

        # Disable sliders
        __self__.T1Slider.config(state=DISABLED)
        __self__.T2Slider.config(state=DISABLED)
        __self__.LP1Slider.config(state=DISABLED)
        __self__.LP2Slider.config(state=DISABLED)
        
        __self__.draw_image1(0)
        __self__.draw_image2(0)
    
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
            __self__.annotator = Annotator(MY_DATACUBE,__self__) 
        else:
            __self__.annotate.config(relief="raised")
            # the easiest way to recover the default color button is pointing to an existing button
            # that never changes its color
            __self__.annotate.config(bg=__self__.correlate.cget("background"))
            __self__.annotator.wipe_annotator(__self__)
            del __self__.annotator
        

 
    def update_sample1(__self__,event):
        global MY_DATACUBE
        label1 = "Maximum net counts: {}".format(int(MY_DATACUBE.max_counts[__self__.Map1Var.get()]))
        __self__.Map1Counts.set(label1)
        unpacker = __self__.Map1Var.get()
        unpacker = unpacker.split("_")
        __self__.ElementalMap1 = MY_DATACUBE.unpack_element(unpacker[0],unpacker[1])
        __self__.ElementalMap1 = __self__.ElementalMap1/__self__.ElementalMap1.max()*LEVELS
        __self__.draw_image1(0)
        try: __self__.annotator.refresh_annotator(__self__)
        except: pass
     
    def update_sample2(__self__,event):
        global MY_DATACUBE
        label2 = "Maximum net counts: {}".format(int(MY_DATACUBE.max_counts[__self__.Map2Var.get()]))
        __self__.Map2Counts.set(label2)
        unpacker = __self__.Map2Var.get()
        unpacker = unpacker.split("_")
        __self__.ElementalMap2 = MY_DATACUBE.unpack_element(unpacker[0],unpacker[1])
        __self__.ElementalMap2 = __self__.ElementalMap2/__self__.ElementalMap2.max()*LEVELS
        __self__.draw_image2(0)
        try: __self__.annotator.refresh_annotator(__self__)
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
            __self__.annotator.wipe_annotator(__self__)
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
            __self__.annotator.wipe_annotator(__self__)
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


class PlotWin:

    global MY_DATACUBE

    def __init__(__self__,master):
        plot_font = {'fontname':'Times New Roman','fontsize':10}
        __self__.master = Toplevel(master=master)
        __self__.master.title("Plot")
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
    
    def wipe_plot(__self__):
        __self__.plot.clear()
        __self__.master.destroy()
        del __self__

    def resize(__self__, event):
        #__self__.master.update_idletasks()
        wi = __self__.upper.winfo_width()
        hi = __self__.upper.winfo_height()
        wi_t = __self__.lower.winfo_width()
        hi_t = __self__.lower.winfo_height()
        __self__.mplCanvas.config(width=wi, height=hi)
        #__self__.canvas._tkcanvas.config(width=wi, height=hi)
        #__self__.canvas.draw()

    def draw_calibration(__self__):
        plot_font = {'fontname':'Times New Roman','fontsize':10}
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

    def draw_spec(__self__,mode,display_mode='-semilog',lines=False):
        if __self__.master.winfo_exists() == True:
            global FIND_ELEMENT_LIST
            __self__.plot.clear()
            plot_font = {'fontname':'Times New Roman','fontsize':10}
            if display_mode == '-semilog':
                __self__.plot.set_title('{0}'.format(SpecRead.DIRECTORY),**plot_font)
                __self__.plot.set_ylabel("Counts")
                for option in mode:
                    __self__.plotdata = getstackplot(MY_DATACUBE,option)
                    __self__.plotdata = __self__.plotdata/__self__.plotdata.max()
                    __self__.plot.semilogy(MY_DATACUBE.energyaxis,__self__.plotdata,label=str(option))
                if lines==True:
                    for element in FIND_ELEMENT_LIST:
                        energies = plottables_dict[element]
                        __self__.plot.plot((energies,energies),(0,__self__.plotdata.max()),'k--')

                __self__.plot.set_xlabel("Energy (KeV)")
                __self__.plot.legend()
            else:
                for option in mode:
                    __self__.plotdata = getstackplot(MY_DATACUBE,option)
                    __self__.plotdata = __self__.plotdata/__self__.plotdata.max()
                    __self__.plot.plot(MY_DATACUBE.energyaxis,__self__.plotdata,label=str(option))
                if lines==True:
                    for element in FIND_ELEMENT_LIST:
                        energies = plottables_dict[element]
                        __self__.plot.plot((energies,energies),(0,__self__.plotdata.max()),'k--')

                __self__.plot.set_xlabel("Energy (KeV)")
                __self__.plot.legend()
            __self__.canvas.draw()
    
    def draw_ROI(__self__):
        global MY_DATACUBE
        for element in MY_DATACUBE.ROI:
            __self__.plotdata = MY_DATACUBE.ROI[element]
            if MY_DATACUBE.max_counts[element+"_a"] == 0:
                try: net = (MY_DATACUBE.max_counts[element+"_b"],"Beta")
                except: net = (MY_DATACUBE.max_counts[element+"_a"],"Alpha")
            else: net = (MY_DATACUBE.max_counts[element+"_a"],"Alpha")
            roi_label = element + " Max net: {} in {}".format(int(net[0]),net[1])
            __self__.plot.semilogy(MY_DATACUBE.energyaxis,__self__.plotdata,label=roi_label)
        __self__.plot.semilogy(MY_DATACUBE.energyaxis,MY_DATACUBE.sum,label="Sum spectrum")
        __self__.plot.semilogy(MY_DATACUBE.energyaxis,MY_DATACUBE.sum_bg,label="Background")
        __self__.plot.legend()
        place_topleft(__self__.master.master,__self__.master)

    def draw_correlation(__self__,corr,labels):
        plot_font = {'fontname':'Times New Roman','fontsize':10}
        __self__.plot.set_title('{0}'.format(SpecRead.DIRECTORY),**plot_font)
        __self__.plot.set_xlabel(labels[0])
        __self__.plot.set_ylabel(labels[1])
        __self__.plot.scatter(corr[0],corr[1])
        place_topleft(__self__.master.master,__self__.master)

class Samples:

    def __init__(__self__):
        __self__.samples_database = {}

    def splash_screen(__self__,parent):
        __self__.splash = Toplevel(parent.master)
        __self__.splash.resizable(False,False)
        __self__.splash.configure(bg="#DCDCDC")
        __self__.splash.geometry("640x480")
        __self__.splash.overrideredirect(True)
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

    def splash_kill(__self__):
        __self__.splash.destroy()

    def list_all(__self__):
        logging.info("Loading sample list...")
        samples = [name for name in os.listdir(SpecRead.samples_folder) \
                if os.path.isdir(SpecRead.samples_folder+name)]
        for folder in samples:
            files = [name for name in os.listdir(SpecRead.samples_folder+folder)]
            for item in range(len(files)): 
                __self__.filequeue.set("{}".format(files[item]))
                __self__.label2.update()
                __self__.splash.update_idletasks()
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
        __self__.splash_kill()

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

    def __init__(__self__):
        logging.info("Initializing program...")
        __self__.master = Tk()
        __self__.master.withdraw() 
        
        samples = Samples()
        samples.splash_screen(__self__)
        __self__.master.after(100,samples.list_all())
        __self__.samples = samples.samples_database
        __self__.find_elements_diag = None
        
        __self__.master.title("Piratininga SM {}".format(VERSION))
        __self__.master.resizable(False,False)
        __self__.sample_figure = Figure(figsize=(3,2), dpi=100)
        __self__.sample_plot =__self__.sample_figure.add_subplot(111)
        __self__.sample_plot.grid(b=None)
        __self__.sample_plot.axis('off')
        mapfont = {'fontname':'Times New Roman','fontsize':10}
        __self__.sample_plot.set_title('Sample Counts Map',**mapfont)
        __self__.build_widgets()
        __self__.toggle_(toggle='off')
        __self__.master.deiconify()
        
       
    def root_quit(__self__):
        for widget in __self__.master.winfo_children():
            if isinstance(widget, Toplevel):
                widget.destroy()
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

    def find_elements(__self__):
        try:
            if __self__.find_elements_diag.master.winfo_exists() == False:
                __self__.find_elements_diag = PeriodicTable(__self__)
                __self__.find_elements_diag.master.protocol("WM_DELETE_WINDOW",\
                        lambda: wipe_list())
            else:
                __self__.find_elements_diag.master.focus_force()
                pass
        except:
            __self__.find_elements_diag = PeriodicTable(__self__)
            __self__.find_elements_diag.master.protocol("WM_DELETE_WINDOW",\
                    lambda: wipe_list())
        
        
    def call_listsamples(__self__):
        __self__.SamplesWindow = Toplevel(master=__self__.master)
        __self__.SamplesWindow.title("Sample List")
        __self__.SamplesWindow.resizable(False,False) 
        __self__.SamplesWindow_LabelLeft = Label(__self__.SamplesWindow, text="FOLDER")
        __self__.SamplesWindow_LabelRight = Label(__self__.SamplesWindow, text="MCA PREFIX")
        __self__.SamplesWindow_TableLeft = Listbox(__self__.SamplesWindow, height=40)
        __self__.SamplesWindow_TableLeft.bind('<Double-Button-1>', __self__.sample_select)
        __self__.SamplesWindow_TableRight = Listbox(__self__.SamplesWindow, height=40)
        
        __self__.SamplesWindow_LabelLeft.grid(row=0,column=0)
        __self__.SamplesWindow_LabelRight.grid(row=0,column=1)
        __self__.SamplesWindow_TableLeft.grid(pady=5, row=1,column=0)
        __self__.SamplesWindow_TableRight.grid(pady=5, row=1,column=1)
       
        for key in __self__.samples:
            __self__.SamplesWindow_TableLeft.insert(END,"{}".format(key))
            __self__.SamplesWindow_TableRight.insert(END,"{}".format(__self__.samples[key]))
        place_topleft(__self__.master,__self__.SamplesWindow)

    def list_samples(__self__):
        try:
            if __self__.SamplesWindow.state() == 'normal': 
                __self__.SamplesWindow.focus_force()
                place_topleft(__self__.master,__self__.SamplesWindow)
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
            SpecRead.setup_from_datacube(MY_DATACUBE,__self__.samples)
            __self__.SampleVar.set("Sample on memory: "+SpecRead.selected_sample_folder)
            __self__.toggle_(toggle='on')    
            __self__.write_stat()   
            __self__.draw_map()

        else: 
            SpecRead.conditional_setup(name=value)
            __self__.call_configure()
            __self__.master.wait_window(__self__.ConfigDiag)
    
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
        __self__.summation.draw_spec(mode=['summation'],display_mode='-semilog',lines=False)
        place_topleft(__self__.master,__self__.summation.master)
    
    def call_mps(__self__):
        master = __self__.master
        __self__.MPS = PlotWin(master)
        __self__.MPS.draw_spec(mode=['mps'],display_mode='-semilog',lines=False)
        place_topleft(__self__.master,__self__.MPS.master)
    
    def call_combined(__self__):
        master = __self__.master
        __self__.combined = PlotWin(master)
        __self__.combined.draw_spec(mode=['summation','mps'],display_mode='-semilog',lines=False)
        place_topleft(__self__.master,__self__.combined.master)

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
        __self__.Toolbox.add_command(label="Set samples folder . . .", command=doNothing)
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
                image=__self__.SettingsButton_icon, compound=LEFT, bd=3, command=doNothing)
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
            shutil.rmtree(SpecRead.output_path)
            #os.remove(SpecRead.cube_path)
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


class PeriodicTable:

    # Creates the periodic table and starts find_elements module from Mapping.py

    def __init__(__self__,parent):
        __self__.master = Toplevel(parent.master)
        __self__.master.title("Periodic Table of Elements")
        __self__.master.resizable(False,False)
        __self__.master.header = Label(__self__.master, text="Periodic Table of Elements.")
        __self__.master.header.grid(row=0,column=0, columnspan=18)
        __self__.master.body = Frame(__self__.master)
        __self__.master.body.grid(row=1,column=0, rowspan=9, columnspan=18,padx=(3,3),pady=(3,0))
        __self__.master.footer = Frame(__self__.master)
        __self__.master.footer.grid(row=10,column=0, columnspan=18)

        __self__.draw_buttons() 
    
    def refresh_plots(__self__):
        global FIND_ELEMENT_LIST
        if len(FIND_ELEMENT_LIST) > 0: 
            lines = True
        else: 
            lines = False
        
        try:
            root.MPS.draw_spec(\
                mode=['mps'],display_mode='-semilog',lines=lines)
            root.MPS.update_idletasks()
        except: pass
        try: 
            root.summation.draw_spec(\
                mode=['summation'],display_mode='-semilog',lines=lines)
            root.summation.update_idletasks()
        except: pass
        try: 
            root.combined.draw_spec(\
                mode=['mps','summation'],display_mode='-semilog',lines=lines)
            root.combined.update_idletasks()
        except: pass
        
        try: root.find_elements_diag.master.focus_force()
        except: pass
        return np.nan

    def add_element(__self__,toggle_btn):
        global DEFAULTBTN_COLOR
        global FIND_ELEMENT_LIST
        if toggle_btn.config('relief')[-1] == 'sunken':
            toggle_btn.config(relief="raised")
            toggle_btn.config(bg=DEFAULTBTN_COLOR)
            FIND_ELEMENT_LIST.remove(toggle_btn.cget("text"))
            __self__.refresh_plots()
        else:
            toggle_btn.config(relief="sunken")
            toggle_btn.config(bg="yellow")
            FIND_ELEMENT_LIST.append(toggle_btn.cget("text"))
            __self__.refresh_plots()
       
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
            
            if cube_size*(len(FIND_ELEMENT_LIST)) > sys_mem["available"]:
                logging.warning("Non-fatal MEMORY ERROR! Memony size needed for cube copies not available!")
                messagebox.showerror("Memory Error!","Multiprocessing copies the datacube to for each running instance.\nMemory needed: {}\nMemory available: {}\nProcess will follow in a single instance and may take a while.".format(process_memory[0],process_memory[1]))   

            # multi-core mode
            if len(FIND_ELEMENT_LIST) > 2 and MY_DATACUBE.img_size > 1200\
                    and cube_size*len(FIND_ELEMENT_LIST) < sys_mem["available"]:
                cuber = Cube_reader(MY_DATACUBE,FIND_ELEMENT_LIST)
                results = cuber.start_workers()
                results = sort_results(results,FIND_ELEMENT_LIST)
                digest_results(MY_DATACUBE,results,FIND_ELEMENT_LIST)
 
            # single-core mode
            else: 
                MAPS = getpeakmap(FIND_ELEMENT_LIST,MY_DATACUBE)
                #ImgMath.split_and_save(MY_DATACUBE,MAPS,FIND_ELEMENT_LIST)
                


            # reactivate widgets
            wipe_list()
            root.toggle_(toggle="on")
            root.MenuBar.entryconfig("Toolbox", state=NORMAL)
            root.ButtonLoad.config(state=NORMAL)
            root.write_stat()
            __self__.refresh_plots()

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

              
if __name__ == "__main__":
    import logging
    from multiprocessing import freeze_support
    freeze_support()
    logging.basicConfig(format = '%(asctime)s\t%(levelname)s\t%(message)s',\
            filename = 'logfile.log',level = logging.DEBUG)
    with open('logfile.log','w+') as mylog: mylog.truncate(0)
    logging.info('*'* 10 + ' LOG START! ' + '*'* 10)

    VERSION = "0.0.1α"
    optimum_resolution = (1920,1080)

    # tcl/Tk imports
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox

    # general utilities
    import numpy as np
    import sys, os, copy, pickle
    from psutil import virtual_memory

    # matplotlib imports
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    from matplotlib import style
    style.use('ggplot')
    
    check_screen_resolution(optimum_resolution)
    # internal imports
    import SpecRead
    from ImgMath import LEVELS
    from ImgMath import threshold, low_pass, iteractive_median
    from SpecMath import getstackplot, correlate
    from SpecMath import datacube as Cube
    from EnergyLib import plottables_dict
    from Mapping import getpeakmap
    from Mapping_parallel import Cube_reader, sort_results, digest_results

    logging.info("Loading GUI...")
    start_up()
    root = MainGUI()
    root.master.mainloop()

