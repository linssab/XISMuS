VERSION = "1.0.0"

def load_cube(cube=""):
    cube_file = open(os.getcwd()+"\\output\\{}\\{}.cube".format(cube,cube),'rb')
    cube = pickle.load(cube_file)
    cube_file.close()
    return cube

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


class Layer:

    def __init__(__self__,cube,layer,element=""):
        
        """ Inherit properties from Cube parent """

        __self__.name = cube.name
        __self__.matrix = np.zeros([cube.dimension[0],cube.dimension[1],\
                cube.energyaxis.shape[0]],dtype='float64',order='C')
        __self__.bg = np.zeros([cube.dimension[0],cube.dimension[1],\
                cube.energyaxis.shape[0]],dtype='float64',order='C')
        for i in range(__self__.matrix.shape[0]):
            for j in range(__self__.matrix.shape[1]):
                __self__.matrix[i,j] = cube.matrix[i,j]
                __self__.bg[i,j] = cube.background[i,j]
        __self__.calibration = cube.calibration
        __self__.energyaxis = cube.energyaxis
        __self__.config = cube.config
        if element == "": __self__.img = cube.densitymap/cube.densitymap.max()*255
        else: 
            unpacker = element.split("_")
            image = cube.unpack_element(unpacker[0],unpacker[1])
            __self__.img = image/image.max()*255
        
        """ Get rid of 0 values in grayscale image. This is done to
        facilitate detecting if a pixel belongs or not to a Layer """

        for i in range(__self__.img.shape[0]):
            for j in range(__self__.img.shape[1]):
                if __self__.img[i,j] == 0: __self__.img[i,j] = 1
        
        """ Define anchors """

        __self__.start = [0,0]
        __self__.end = [__self__.img.shape[0],__self__.img.shape[1]]

        """ Gives a layer number """

        __self__.layer = layer


class Mosaic:

    def __init__(__self__, size):
        pad = 16
        __self__.master = Tk()
        __self__.master.title("Mosaic v{}".format(VERSION))
        __self__.master.geometry("1024x768")
        __self__.NameVar = StringVar()
        __self__.NameVar.set("New Cube")
        my_dpi = __self__.master.winfo_fpixels("1i")
        __self__.image = np.zeros([size[0],size[1]])
        __self__.layer = {}
        __self__.master.resizable(False,False)
        __self__.layer_count = 0
        __self__.RightPane = Frame(__self__.master,height=768, width=1024-768)
        __self__.LeftPane = Frame(__self__.master,width=768, height=768)
        __self__.RightPane.grid(row=0, column=1, sticky=N+W+E, padx=pad, pady=pad)
        __self__.LeftPane.grid(row=0, column=0)
        __self__.Canvas = Canvas(__self__.LeftPane)
        __self__.Canvas.grid()
        __self__.build_widgets()
        
    def build_widgets(__self__):
        pad = 16
        my_dpi = __self__.master.winfo_fpixels("1i")
        # draw matplotlib canvas
        __self__.map = Figure(figsize=((748-pad)/my_dpi,(748-pad)/my_dpi), dpi=my_dpi)
        __self__.plot1 = __self__.map.add_subplot(111)
        __self__.plot1.axis('off')
        __self__.plot1.grid(b=None)
        __self__.canvas = FigureCanvasTkAgg(__self__.map,__self__.Canvas)
        __self__.canvas.get_tk_widget().pack(fill=BOTH,anchor=N+W)
        __self__.toolbar = NavigationToolbar2Tk(__self__.canvas,__self__.Canvas)
        __self__.toolbar.update()
        __self__.canvas._tkcanvas.pack()

        __self__.canvas.mpl_connect("button_press_event",__self__.on_press)
        __self__.canvas.mpl_connect("motion_notify_event",__self__.on_drag)
        __self__.canvas.mpl_connect("button_release_event",__self__.on_release)
        __self__.press, __self__.move = False, False

        # draw listbox
        up = PhotoImage(file=os.getcwd()+"\\images\\icons\\next.png")
        down = PhotoImage(file=os.getcwd()+"\\images\\icons\\previous.png")
        __self__.icon_up = up.subsample(1,1)
        __self__.icon_down = down.subsample(1,1)

        __self__.layers_list = Listbox(__self__.RightPane, height=10)
        __self__.layer_up = Button(
                __self__.RightPane, 
                image=__self__.icon_up,
                width=32,
                height=32)
        __self__.layer_down = Button(
                __self__.RightPane, 
                image=__self__.icon_down,
                width=32,
                height=32)
        __self__.validate = Button(__self__.RightPane, 
                text="Merge!",
                width=7,
                height=1,
                command=__self__.build_cube)
        __self__.add_layer = Button(
                __self__.RightPane, 
                text="Add",
                width=7,
                height=1,
                command=__self__.add_layer)
        __self__.del_layer = Button(__self__.RightPane, 
                text="Delete",
                width=7,
                height=1)
        __self__.cube_name = Entry(
                __self__.RightPane,
                textvar = __self__.NameVar,
                width=13)
        __self__.cube_name_label = Label(
                __self__.RightPane,
                text = "Cube name: ")

        __self__.layers_list.grid(row=0, column=0, rowspan=4)
        __self__.layer_up.grid(row=0, column=1)
        __self__.layer_down.grid(row=1, column=1)
        __self__.add_layer.grid(row=2, column=1, padx=pad, pady=pad/2)
        __self__.del_layer.grid(row=3, column=1, padx=pad, pady=pad/2)
        __self__.cube_name.grid(row=4, column=1, sticky=W, padx=pad, pady=pad/2)
        __self__.cube_name_label.grid(row=4, column=0, padx=pad, pady=pad/2, sticky=E)
        __self__.validate.grid(row=5, column=0, columnspan=2, pady=pad)

    def on_press(__self__,event):
        __self__.press = True
        try: __self__.x0 = int(event.ydata)
        except: pass
        try: __self__.y0 = int(event.xdata)
        except: pass
        
    def on_drag(__self__,event):
        if __self__.press:
            __self__.move = True
            try: __self__.x1 = int(event.ydata)
            except: pass
            try: __self__.y1 = int(event.xdata)
            except: pass
            # adjust drag pointer to image click position
            try: name = __self__.read_pixels(__self__.x0,__self__.y0)[1].name
            except: return 0
            x_size, y_size = __self__.layer[name].img.shape
            
            # sets new y start
            new_start_y = __self__.y1 - __self__.y0  + __self__.layer[name].start[1]
            #print("New Start Y, previous")
            #print(new_start_y, __self__.layer[name].start[1])
            if new_start_y < 0: __self__.layer[name].start[1] = 0
            elif new_start_y + __self__.layer[name].img.shape[1] > __self__.image.shape[1]: print(new_start_y + __self__.layer[name].img.shape[1], __self__.image.shape[1]) 
            else: 
                __self__.layer[name].start[1] = new_start_y
            
            # sets new x start
            new_start_x = __self__.x1 - __self__.x0  + __self__.layer[name].start[0]
            #print("New Start X, previous")
            #print(new_start_x, __self__.layer[name].start[0])
            if new_start_x < 0: __self__.layer[name].start[0] = 0
            elif new_start_x + __self__.layer[name].img.shape[0] > __self__.image.shape[0]: pass 
            else: 
                __self__.layer[name].start[0] = new_start_x
            print(__self__.layer[name].start)
            
            # sets new y end
            new_end_y = __self__.y1 - __self__.y0  + __self__.layer[name].end[1]
            #print("New End Y, previous")
            #print(new_end_y, __self__.layer[name].end[1])
            if new_start_y < 0: __self__.layer[name].end[1] = __self__.layer[name].img.shape[1]
            elif new_end_y > __self__.image.shape[1]:  __self__.layer[name].end[1] = __self__.image.shape[1]
            else: 
                __self__.layer[name].end[1] = __self__.y1 - __self__.y0  + __self__.layer[name].end[1]

            # sets new x end
            new_end_x = __self__.x1 - __self__.x0  + __self__.layer[name].end[0]
            #print("New End X, previous")
            #print(new_end_x, __self__.layer[name].end[0])
            if new_start_x < 0: __self__.layer[name].end[0] = __self__.layer[name].img.shape[0]
            elif new_end_x > __self__.image.shape[0]: __self__.layer[name].end[0] = __self__.image.shape[0]
            else: 
                __self__.layer[name].end[0] = __self__.x1 - __self__.x0  + __self__.layer[name].end[0]
            print(__self__.layer[name].start, __self__.layer[name].end, __self__.layer[name].name) 
            __self__.build_image(__self__.image.shape)

            #__self__.area1.set_width(__self__.x1 - __self__.x0)
            #__self__.area2.set_width(__self__.x1 - __self__.x0)
            #__self__.area1.set_height(__self__.y1 - __self__.y0)
            #__self__.area2.set_height(__self__.y1 - __self__.y0)
            #__self__.area1.set_xy((__self__.x0,__self__.y0))
            #__self__.area2.set_xy((__self__.x0,__self__.y0))
            #__self__.parent.canvas1.draw()
            #__self__.parent.canvas2.draw()
            #__self__.calculate_area()

    def on_release(__self__,event):
        __self__.press = False
        if __self__.press and not __self__.move:
            __self__.press = False
            __self__.move = False

    def add_layer(__self__):
        _path = os.getcwd()+"\\output\\"
               
        """ list all packed cubes """
        cube_dict = {}
        cube_folders = [name for name in os.listdir(_path) if os.path.isdir(_path+name)]
        for folder in cube_folders:
            for name in os.listdir(_path+folder):
                if name.lower().endswith(".cube"): cube_dict[folder] = name.split(".cube")[0]
        __self__.maps_window = Toplevel()
        __self__.maps_window.withdraw()
        icon = os.getcwd()+"\\images\\icons\\icon.ico"
        __self__.maps_window.title("Available samples")
        __self__.maps_window.iconbitmap(icon)
        __self__.maps_window.resizable(False, False)
        __self__.maps_window.geometry("240x180")
        __self__.maps_list = Listbox(__self__.maps_window)
        __self__.maps_list.pack(side=TOP, fill=X)
        __self__.maps_list.config(selectmode=SINGLE)
        for key in cube_dict:
            item = cube_dict[key]
            __self__.maps_list.insert(END,"{}".format(item))
        __self__.ok_btn = Button(
                __self__.maps_window, 
                text="Import", 
                bd=3, 
                width=13,
                command=__self__.grep_cube)
        __self__.ok_btn.pack(side=BOTTOM, pady=3)
        place_center(__self__.master, __self__.maps_window)
        __self__.maps_window.deiconify()
        __self__.maps_window.focus_force()
        __self__.maps_window.grab_set()
    
    def check_calibration(__self__, cube):
        proceed = True
        candidate = cube.calibration
        for layer in __self__.layer:
            loaded = __self__.layer[layer].calibration
            if loaded != candidate:
                proceed = messagebox.askquestion("Warning!","The cube you are trying to add has a different calibration from the layers already imported. This may cause serious problems when trying to map elements and can yield to results inconsistencies! Are you sure you want to proceed?")
                if proceed == "yes": return True
                else: return False
            else: pass
        return proceed
    
    def check_configuration(__self__, cube):
        proceed, merge_config, divergence = True, "", []
        candidate = cube.config
        for layer in __self__.layer:
            if __self__.layer[layer].layer == 0: 
                zero_config = copy.deepcopy(__self__.layer[layer].config)
            loaded = __self__.layer[layer].config
            for key in loaded:
                if candidate[key] != loaded[key] and key != "directory": 
                    divergence.append(key)
        if divergence != []: 
            zero_config.pop("directory")
            for key in zero_config:
                merge_config = merge_config + str(key) + ": " +str(zero_config[key]) + ", "
            proceed = messagebox.askquestion("Diverging configuration!","The cube you are trying to add has a different configuration from the layers already imported {}!\nDo you want to add it anyways? (Resulting merged cube configuration will be: {})".format(divergence, merge_config))
            if proceed == "yes": return True
            else: return False
        else: return True

    def grep_map(__self__, cube, e=""):
        element = __self__.maps_list.get(ACTIVE)
        if __self__.layer_count == 0: 
            layer_no = 0
            __self__.layer_count += 1
        else: 
            layer_no = __self__.layer_count
            __self__.layer_count += 1
        __self__.layer[cube.name] = Layer(cube,layer_no,element)
        __self__.layers_list.insert(END,"{}_{},{}".format(cube.name,element,layer_no))
        __self__.build_image(__self__.image.shape)
        __self__.maps_window.destroy()

    def grep_cube(__self__, e=""):
        selected_cube = __self__.maps_list.get(ACTIVE)
        cube = load_cube(selected_cube)
        if __self__.layer_count == 0: can_import = True
        else: can_import = __self__.check_calibration(cube)
        if can_import == True and __self__.layer_count > 0: 
            can_import = __self__.check_configuration(cube)
        if can_import == True:
            packed_elements = cube.check_packed_elements()

            if packed_elements != []:
                dialog = messagebox.askquestion("Attention!","There are some element maps packed in this cube. Would you like to import an elemental map instead?")
                if dialog == "yes":
                    __self__.maps_list.delete(0,END)
                    for element in packed_elements: 
                        __self__.maps_list.insert(END,"{}".format(element))
                    __self__.ok_btn.config(text="Import Map")
                    __self__.ok_btn.config(command= lambda: __self__.grep_map(cube))
                else:
                    if __self__.layer_count == 0: 
                        layer_no = 0
                        __self__.layer_count += 1
                    else: 
                        layer_no = __self__.layer_count
                        __self__.layer_count += 1
                    __self__.layer[cube.name] = Layer(cube,layer_no)
                    __self__.layers_list.insert(END,"{},{}".format(cube.name,layer_no))
                    __self__.build_image(__self__.image.shape)
                    __self__.maps_window.destroy()

            elif packed_elements == []:
                if __self__.layer_count == 0: 
                    layer_no = 0
                    __self__.layer_count += 1
                else: 
                    layer_no = __self__.layer_count
                    __self__.layer_count += 1
                __self__.layer[cube.name] = Layer(cube,layer_no)
                __self__.layers_list.insert(END,"{},{}".format(cube.name,layer_no))
                __self__.build_image(__self__.image.shape)
                __self__.maps_window.destroy()

    def read_pixels(__self__,i,j):
        front_layer, top_layer, pixel = 0, 0, 0
        for layer in __self__.layer:
            try:
                x, y = __self__.layer[layer].start
                x_, y_ = __self__.layer[layer].end
                conv_x, conv_y = i-x, j-y
                if x <= i < x_ and y <= j < y_ and __self__.layer[layer].layer >= front_layer:
                    pixel = __self__.layer[layer].img[conv_x,conv_y]
                    front_layer += 1
                    top_layer = __self__.layer[layer]
            except:
                return pixel, top_layer
        return pixel, top_layer
    
    def build_image(__self__, size):
        for i in range(size[0]):
            for j in range(size[1]):
                __self__.image[i,j] = __self__.read_pixels(i,j)[0]
        __self__.plot1.clear()
        __self__.plot1.imshow(__self__.image, cmap='gray')
        __self__.plot1.grid(b=None)
        __self__.canvas.draw()
 
    def pack_spectra(__self__,i,j,void_spectrum):
        front_layer, top_layer, spectrum, bg = 0, 0, void_spectrum, void_spectrum
        for layer in __self__.layer:
            try:
                x, y = __self__.layer[layer].start
                x_, y_ = __self__.layer[layer].end
                conv_x, conv_y = i-x, j-y
                if x <= i < x_ and y <= j < y_ and __self__.layer[layer].layer >= front_layer:
                    spectrum = __self__.layer[layer].matrix[conv_x,conv_y]
                    bg = __self__.layer[layer].bg[conv_x,conv_y]
                    front_layer += 1
                    top_layer = __self__.layer[layer]
            except:
                return spectrum, bg
        return spectrum, bg
    
    def build_cube(__self__):
        start_x, start_y = __self__.image.shape
        end_x, end_y = 0, 0
        for layer in __self__.layer:
            if __self__.layer[layer].start[0] < start_x: 
                start_x = __self__.layer[layer].start[0]
            if __self__.layer[layer].start[1] < start_y:
                start_y = __self__.layer[layer].start[1]
            if __self__.layer[layer].end[0] > end_x: 
                end_x = __self__.layer[layer].end[0]
            if __self__.layer[layer].end[1] > end_y:
                end_y = __self__.layer[layer].end[1]
            specsize = __self__.layer[layer].matrix.shape[2]
        void_spectrum = np.zeros([specsize])
        print(start_x, start_y)
        print(end_x, end_y)
        __self__.merge_matrix = np.zeros([(end_x-start_x)+1,(end_y-start_y)+1,specsize])
        __self__.merge_bg = np.zeros([(end_x-start_x)+1,(end_y-start_y)+1,specsize])
        x=0
        for i in range(start_x, end_x):
            y=0
            for j in range(start_y, end_y):
                __self__.merge_matrix[x,y], __self__.merge_bg[x,y] = \
                        __self__.pack_spectra(i,j,void_spectrum)
                y=y+1
            x=x+1
        layers = list(__self__.layer.keys())

        """ Setup configuration dictionary according to the first loaded layer """

        NAME = __self__.NameVar.get()
        SpecRead.conditional_setup(name=NAME)

        """ Datacube object was not created with merging in mind, therefore some
        workaround had to be done. Main attributes are set externally rather than in the
        __init__ method """
        

        new_cube = Cube(["xrf"],SpecRead.CONFIG,mode="merge",name=NAME)
        new_cube.energyaxis = __self__.layer[layers[0]].energyaxis
        new_cube.dimension = (end_x-start_x), (end_y-start_y)
        new_cube.img_size = new_cube.dimension[0] * new_cube.dimension[1]
        new_cube.matrix = np.zeros([new_cube.dimension[0],new_cube.dimension[1],\
                new_cube.energyaxis.shape[0]],dtype='float64',order='C')
        new_cube.background = np.zeros([new_cube.dimension[0],new_cube.dimension[1],\
                new_cube.energyaxis.shape[0]],dtype='float64',order='C')
        for x in range(new_cube.dimension[0]):
            for y in range(new_cube.dimension[1]):
                new_cube.matrix[x,y] = __self__.merge_matrix[x,y]
                new_cube.background[x,y] = __self__.merge_bg[x,y]
                #print("Assembling {}, {} - Μ{} Β{} Σ{}".format(x,y,
                    #new_cube.matrix[x,y].sum(),
                    #new_cube.background[x,y].sum(),
                    #new_cube.matrix[x,y].sum()-new_cube.background[x,y].sum()))
        new_cube.calibration = __self__.layer[layers[0]].calibration
        new_cube.config = SpecRead.CONFIG
        print(new_cube.config)
        new_cube.digest_merge()
        plt.imshow(new_cube.densitymap)
        plt.show()

   
if __name__.endswith('__main__'):         
    
    optimum_resolution = (1920,1080)

    # tcl/Tk imports
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
     
    # general utilities
    import numpy as np
    import cv2
    import sys, os, copy, pickle, stat, random
    import logging, time
    
    # matplotlib imports
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    from matplotlib import style
    style.use('ggplot')

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

    SpecRead.conditional_setup()
    mosaic_root = Mosaic((400,800))
    mosaic_root.master.mainloop()
