#################################################################
#                                                               #
#          Mosaic API Module                                    #
#                        version: 1.1.0 - Mar - 2020            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

VERSION = "1.1.0"
global layers_dict
layers_dict = {}

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
from Decoder import *

# matplotlib imports
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib import style
style.use('ggplot')

# internal imports
import SpecRead
from ReadConfig import checkout_config
from ImgMath import LEVELS
from ImgMath import threshold, low_pass, iteractive_median, write_image, stackimages
from SpecMath import getstackplot, correlate, peakstrip, Busy
from SpecMath import datacube as Cube
from EnergyLib import plottables_dict
from Mapping import getpeakmap, grab_simple_roi_image, select_lines 
from Mapping_parallel import Cube_reader, sort_results, digest_results
import cy_funcs

def load_cube(cube=""):
    cube_file = open(os.path.join(SpecRead.__PERSONAL__,
        "output",cube,"{}.cube".format(cube)),"rb")
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

def convert_layers_to_dict(MosaicAPI_obj):
    new_dict = {}
    for layer in MosaicAPI_obj.layer:
        new_dict[MosaicAPI_obj.layer[layer].name] = {
                "start":MosaicAPI_obj.layer[layer].start,
                "end":MosaicAPI_obj.layer[layer].end,
                "img":MosaicAPI_obj.layer[layer].img,
                "layer":MosaicAPI_obj.layer[layer].layer
                }
    return new_dict

class NavigationToolbar(NavigationToolbar2Tk):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar2Tk.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom')]

class Layer:

    def __init__(__self__,cube,layer,element=""):
        
        """ Inherit properties from Cube parent """

        __self__.name = cube.name
        __self__.matrix = np.zeros([cube.dimension[0],cube.dimension[1],\
                cube.energyaxis.shape[0]],dtype='float32',order='C')
        __self__.bg = np.zeros([cube.dimension[0],cube.dimension[1],\
                cube.energyaxis.shape[0]],dtype='float32',order='C')
        for i in range(__self__.matrix.shape[0]):
            for j in range(__self__.matrix.shape[1]):
                __self__.matrix[i,j] = cube.matrix[i,j]
                __self__.bg[i,j] = cube.background[i,j]
        __self__.calibration = cube.calibration
        __self__.energyaxis = cube.energyaxis
        __self__.config = cube.config
        if element == "": 
            __self__.img = cube.densitymap/cube.densitymap.max()*255
            __self__.img = __self__.img.astype("int32")
        else: 
            unpacker = element.split("_")
            image = cube.unpack_element(unpacker[0],unpacker[1])
            __self__.img = image/image.max()*255
            __self__.img = __self__.img.astype("int32")
        
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
        
        

class Mosaic_API:

    def __init__(__self__, size):
        pad = 16
        zbar = 35
        __self__.master = Toplevel()
        __self__.master.grab_set()
        __self__.master.attributes("-alpha",0.0)
        icon = os.getcwd()+"\\images\\icons\\icon.ico"
        __self__.master.iconbitmap(icon)
        __self__.master.title("Mosaic v{}".format(VERSION))
        __self__.master.geometry("1024x768")
        __self__.master.protocol("WM_DELETE_WINDOW",__self__.kill)
        __self__.NameVar = StringVar()
        __self__.NameVar.set("New Cube")
        my_dpi = __self__.master.winfo_fpixels("1i")
        __self__.image = np.zeros([size[0],size[1]],dtype="int")+59
        __self__.layer = {}
        __self__.master.resizable(True,True)
        __self__.master.minsize(1024,768)
        __self__.layer_count = 0
        __self__.layer_numbering = {}

        # create panels
        __self__.RightPane = Frame(__self__.master,
                height=768, width=1024-768-2*pad)
        __self__.LeftPane = Frame(__self__.master,
                height=768-zbar, 
                width=768-2*pad)
        __self__.LeftPane.pack(side=LEFT,
                fill=BOTH,
                anchor=N, 
                padx=(0,pad),
                expand=True)
        __self__.RightPane.pack(side=RIGHT,
                fill=BOTH,
                anchor=N, 
                padx=(pad,pad), 
                pady=pad,
                expand=False)

        # allocates the canvas and toolbar spaces
        __self__.Canvas = Canvas(__self__.LeftPane, 
                height=768-zbar-2,
                width=768-2-2*pad,
                bg="#3b3b38") 
        __self__.Canvas.pack(side=TOP,expand=True,fill=BOTH)
        __self__.barframe = Frame(__self__.LeftPane,
                height=zbar,
                width=768-2*pad)
        __self__.barframe.pack(side=BOTTOM,expand=False,fill=BOTH,anchor=N)
        __self__.master.columnconfigure(0,weight=0)
        __self__.master.columnconfigure(1,weight=1)
        __self__.master.rowconfigure(0, weight=1)
        __self__.master.rowconfigure(1, weight=1)
        __self__.build_widgets()
    
    def build_widgets(__self__):
        pad = 16
        zbar = 35
        my_dpi = __self__.master.winfo_fpixels("1i")
        # draw matplotlib canvas
        __self__.map = plt.figure(
                figsize=(round(768-2*pad)/my_dpi,round(768-zbar)/my_dpi), 
                dpi=my_dpi)
        __self__.map.set_facecolor("#3b3b38")
        __self__.im_plot = plt.imshow(__self__.image, cmap="gray",vmin=0, vmax=255)
        __self__.map.subplots_adjust(
                top=0.99,
                bottom=0.01,
                left=0.01,
                right=0.99)
        __self__.axs = plt.gca()
        __self__.axs.axis("on")
        __self__.axs.get_yaxis().set_visible(False)
        __self__.axs.get_xaxis().set_visible(False)
        __self__.axs.spines["top"].set_color("#3b3b38")
        __self__.axs.spines["bottom"].set_color("#3b3b38")
        __self__.axs.spines["left"].set_color("#3b3b38")
        __self__.axs.spines["right"].set_color("#3b3b38")
        __self__.axs.grid(b=None)

        __self__.canvas = FigureCanvasTkAgg(__self__.map,__self__.Canvas)
        __self__.canvas.draw()
        __self__.mpl_canvas = __self__.canvas.get_tk_widget()
        __self__.mpl_canvas.pack(fill=BOTH,anchor=N+W,expand=True)
        __self__.toolbar = NavigationToolbar(__self__.canvas,__self__.barframe)
        __self__.toolbar.update()
        __self__.canvas._tkcanvas.pack()
        
        # redefines backend callback to prevent moving the layers while zooming and panning
        press_zoom = NavigationToolbar2Tk.press_zoom
        press_pan = NavigationToolbar2Tk.press_pan
        def new_press_zoom(self, *args, **kwargs):
            __self__.press, __self__.move = False, False
            press_zoom(self,*args,**kwargs)
        def new_press_pan(self, *args, **kwargs):
            __self__.press, __self__.move = False, False
            press_pan(self,*args,**kwargs)
        NavigationToolbar2Tk.press_zoom = new_press_zoom
        NavigationToolbar2Tk.press_pan = new_press_pan

        __self__.canvas.mpl_connect("button_press_event",__self__.on_press)
        __self__.canvas.mpl_connect("motion_notify_event",__self__.on_drag)
        __self__.canvas.mpl_connect("button_release_event",__self__.on_release)
        __self__.press, __self__.move = False, False

        # draw listbox
        up = PhotoImage(data=ICO_UP)
        down = PhotoImage(data=ICO_DOWN)
        cw = PhotoImage(data=ICO_CW)
        ccw = PhotoImage(data=ICO_CCW)
        __self__.icon_up = up.subsample(1,1)
        __self__.icon_down = down.subsample(1,1)
        __self__.icon_cw = cw.subsample(1,1)
        __self__.icon_ccw = ccw.subsample(1,1)
        
        # container for the buttons
        __self__.container = Frame(__self__.RightPane,width=64,height=64)

        __self__.layers_list = Listbox(__self__.RightPane, height=10)
        __self__.layer_up = Button(
                __self__.container, 
                image=__self__.icon_up,
                width=32,
                height=32,
                command=__self__.move_layer_up)
        __self__.layer_down = Button(
                __self__.container, 
                image=__self__.icon_down,
                width=32,
                height=32,
                command=__self__.move_layer_down)
        __self__.rotate_cw = Button(
                __self__.container, 
                image=__self__.icon_cw,
                width=32,
                height=32,
                command= lambda: __self__.rotate(1))
        __self__.rotate_ccw = Button(
                __self__.container, 
                image=__self__.icon_ccw,
                width=32,
                height=32,
                command= lambda: __self__.rotate(0))

        __self__.validate = Button(__self__.RightPane, 
                text="Merge!",
                width=7,
                height=1,
                command=__self__.build_cube)
        __self__.add_layer = Button(
                __self__.RightPane, 
                text="Add",
                width=10,
                height=1,
                command=__self__.add_layer)
        __self__.del_layer = Button(__self__.RightPane, 
                text="Delete",
                width=10,
                height=1,
                command=__self__.remove_layer)
        __self__.cube_name = Entry(
                __self__.RightPane,
                textvar = __self__.NameVar,
                width=13)
        __self__.cube_name_label = Label(
                __self__.RightPane,
                text = "Cube name: ")

        __self__.layers_list.grid(row=0, column=0, rowspan=4)
        __self__.container.grid(row=0,column=1)
        __self__.layer_up.grid(row=0, column=0)
        __self__.layer_down.grid(row=0, column=1)
        __self__.rotate_ccw.grid(row=1, column=0)
        __self__.rotate_cw.grid(row=1, column=1)
        __self__.add_layer.grid(row=2, column=1, padx=pad)
        __self__.del_layer.grid(row=3, column=1, padx=pad)
        __self__.cube_name.grid(row=4, column=1, sticky=W, padx=pad, pady=pad/2)
        __self__.cube_name_label.grid(row=4, column=0, padx=pad, pady=pad/2, sticky=E)
        __self__.validate.grid(row=5, column=0, columnspan=2, pady=pad)
        
        __self__.master.after(200,__self__.master.attributes,"-alpha",1.0)
        __self__.canvas.draw()

    def rotate(__self__,direction,e=""):
        global layers_dict
        active_layer = __self__.layers_list.curselection()
        if active_layer == (): return
        else: 
            active_layer = __self__.layers_list.get(active_layer).split(",")[0]
            active_layer = active_layer.split("_")[0]
        layer = __self__.layer[active_layer]
        if direction == 1:
            #cv2.rotate(layer.matrix, cv2.ROTATE_90_CLOCKWISE)
            #cv2.rotate(layer.bg, cv2.ROTATE_90_CLOCKWISE)
            img = layer.img[:]
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
            end = [layer.start[0]+img.shape[0],layer.start[1]+img.shape[1]]
            for i in range(len(end)):
                if end[i] > __self__.image.shape[i]:
                    return
            layer.img, layer.end = img, end
            layer.matrix = np.rot90(layer.matrix,3)
            layer.bg = np.rot90(layer.bg,3)

        elif direction == 0:
            img = layer.img[:]
            img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            end = [layer.start[0]+img.shape[0],layer.start[1]+img.shape[1]]
            for i in range(len(end)):
                if end[i] > __self__.image.shape[i]:
                    return
            layer.img, layer.end = img, end
            layer.matrix = np.rot90(layer.matrix)
            layer.bg = np.rot90(layer.bg)
        layers_dict = convert_layers_to_dict(__self__)
        __self__.build_image(__self__.image.shape)

    def on_press(__self__,event):
        __self__.press = True
        try: __self__.x0 = int(event.ydata)
        except: pass
        try: __self__.y0 = int(event.xdata)
        except: pass
        
    def on_drag(__self__,event):
        if __self__.press:
            __self__.move = True
            __self__.x1 = int(event.ydata)
            __self__.y1 = int(event.xdata)
            
            # adjust drag pointer to image click position
            try: name = __self__.read_pixels(__self__.x0,__self__.y0)[1].name
            except: return 0
            
            # sets new y start
            new_start_y = __self__.y1 - __self__.y0  + __self__.layer[name].start[1]
            if new_start_y < 0: 
                __self__.layer[name].start[1] = 0
            elif new_start_y + __self__.layer[name].img.shape[1] > __self__.image.shape[1]: 
                pass
            else: 
                __self__.layer[name].start[1] = new_start_y
            
            # sets new x start
            new_start_x = __self__.x1 - __self__.x0  + __self__.layer[name].start[0]
            if new_start_x < 0: 
                __self__.layer[name].start[0] = 0
            elif new_start_x + __self__.layer[name].img.shape[0] > __self__.image.shape[0]: 
                pass 
            else: 
                __self__.layer[name].start[0] = new_start_x
            
            # sets new y end
            new_end_y = __self__.y1 - __self__.y0  + __self__.layer[name].end[1]
            if new_start_y < 0: 
                __self__.layer[name].end[1] = __self__.layer[name].img.shape[1]
            elif new_end_y > __self__.image.shape[1]:
                __self__.layer[name].end[1] = __self__.image.shape[1]
            else: 
                __self__.layer[name].end[1] = \
                        __self__.y1 - __self__.y0  + __self__.layer[name].end[1]

            # sets new x end
            new_end_x = __self__.x1 - __self__.x0  + __self__.layer[name].end[0]
            if new_start_x < 0: 
                __self__.layer[name].end[0] = __self__.layer[name].img.shape[0]
            elif new_end_x > __self__.image.shape[0]: 
                __self__.layer[name].end[0] = __self__.image.shape[0]
            else: 
                __self__.layer[name].end[0] = \
                        __self__.x1 - __self__.x0  + __self__.layer[name].end[0]
             
            __self__.build_image(__self__.image.shape)
            __self__.x0 = __self__.x1
            __self__.y0 = __self__.y1

    def on_release(__self__,event):
        __self__.press = False
        if __self__.press and not __self__.move:
            __self__.press = False
            __self__.move = False

    def add_layer(__self__):
        _path = os.path.join(SpecRead.__PERSONAL__,"output")
               
        """ list all packed cubes """
        cube_dict = {}
        cube_folders = [name for name in os.listdir(_path) if os.path.isdir(
            os.path.join(_path,name))]
        for folder in cube_folders:
            for name in os.listdir(os.path.join(_path,folder)):
                if name.lower().endswith(".cube"): cube_dict[folder] = name.split(".cube")[0]
        __self__.maps_window = Toplevel()
        __self__.maps_window.withdraw()
        __self__.maps_window.bind("<Escape>",__self__.refocus)
        __self__.maps_window.protocol("WM_DELETE_WINDOW",__self__.refocus)
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

    def remove_layer(__self__,e=""):
        active_layer = __self__.layers_list.curselection()
        if active_layer == (): return
        else: 
            active_layer_name = __self__.layers_list.get(active_layer).split(",")[0]
            __self__.layers_list.delete(active_layer)
            __self__.layer.pop(active_layer_name)
            __self__.reorder_layers()
            __self__.build_image(__self__.image.shape)
            __self__.layer_count -= 1

    def reorder_layers(__self__):
        global layers_dict
        llist = __self__.layers_list.get(0,END)
        __self__.layer_numbering = {}
        for entry in llist:
            idx = __self__.layers_list.get(0,END).index(entry)
            layer_name, el_map = entry.split(",",1)
            __self__.layers_list.delete(idx)
            __self__.layer[layer_name].layer = idx
            __self__.layer_numbering[idx] = layer_name
            element = el_map.split(",")[0]
            if len(element) > 3: 
                __self__.layers_list.insert(idx,"{},{},{}".format(layer_name,element,idx))
            else:
                __self__.layers_list.insert(idx,"{},{}".format(layer_name,idx))
        layers_dict = convert_layers_to_dict(__self__)

    def move_layer_up(__self__):
        active_layer_idx = __self__.layers_list.curselection()
        if active_layer_idx == (): return
        else:
            active_layer_idx = active_layer_idx[0]
            active_layer_entry = __self__.layers_list.get(active_layer_idx).split(",",1)[0]
            active_layer_name = active_layer_entry.split(",")[0]
            if active_layer_idx > 0:
                previous_layer = __self__.layers_list.get(active_layer_idx-1)
                previous_layer_idx = active_layer_idx-1
                previous_layer_entry = previous_layer.split(",",1)[0]
                previous_layer_name = previous_layer_entry.split(",")[0]
                __self__.layers_list.delete(active_layer_idx)
                __self__.layers_list.delete(previous_layer_idx)
                __self__.layers_list.insert(active_layer_idx-1,
                        "{},{}".format(active_layer_name,
                            active_layer_idx-1))
                __self__.layers_list.insert(previous_layer_idx+1,
                        "{},{}".format(previous_layer_name,
                            previous_layer_idx+1))
            else: return
            __self__.reorder_layers()
            __self__.build_image(__self__.image.shape)
    
    def move_layer_down(__self__):
        active_layer_idx = __self__.layers_list.curselection()
        if active_layer_idx == (): return
        else:
            active_layer_idx = active_layer_idx[0]
            active_layer_entry = __self__.layers_list.get(active_layer_idx).split(",",1)[0]
            active_layer_name = active_layer_entry.split(",")[0]
            if active_layer_idx+1 < __self__.layers_list.size():
                next_layer = __self__.layers_list.get(active_layer_idx+1)
                next_layer_idx = active_layer_idx+1
                next_layer_entry = next_layer.split(",",1)[0]
                next_layer_name = next_layer_entry.split(",")[0]
                __self__.layers_list.delete(next_layer_idx)
                __self__.layers_list.delete(active_layer_idx)
                __self__.layers_list.insert(active_layer_idx,
                        "{},{}".format(next_layer_name,
                            active_layer_idx))
                __self__.layers_list.insert(next_layer_idx,
                        "{},{}".format(active_layer_name,
                            next_layer_idx))
            else: return
            __self__.reorder_layers()
            __self__.build_image(__self__.image.shape)

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
                __self__.zero_config = copy.deepcopy(__self__.layer[layer].config)
            loaded = __self__.layer[layer].config
            for key in loaded:
                if candidate[key] != loaded[key] and key != "directory": 
                    divergence.append(key)
        if divergence != []: 
            __self__.zero_config.pop("directory")
            for key in __self__.zero_config:
                merge_config = merge_config+str(key)+": "+str(__self__.zero_config[key])+", "
            proceed = messagebox.askquestion("Diverging configuration!","The cube you are trying to add has a different configuration from the layers already imported {}!\nDo you want to add it anyways? (Resulting merged cube configuration will be: {})".format(divergence, merge_config))
            if proceed == "yes": return True
            else: return False
        else: return True

    def grep_map(__self__, cube, e=""):
        global layers_dict
        element = __self__.maps_list.get(ACTIVE)
        if __self__.layer_count == 0: 
            layer_no = 0
            __self__.layer_count += 1
        else: 
            layer_no = __self__.layer_count
            __self__.layer_count += 1
        __self__.layer_numbering[__self__.layer_count] = cube.name
        __self__.layer[cube.name] = Layer(cube,layer_no,element)
        __self__.layers_list.insert(END,"{},{},{}".format(cube.name,element,layer_no))
        layers_dict = convert_layers_to_dict(__self__)
        __self__.build_image(__self__.image.shape)
        __self__.maps_window.destroy()
        __self__.refocus()


    def grep_cube(__self__, e=""):
        global layers_dict
        selected_cube = __self__.maps_list.get(ACTIVE)
        cube = load_cube(selected_cube)
        if __self__.layer.__contains__(selected_cube):
            messagebox.showinfo("Cube already imported!",
                    "Cabn't add same cube twice!")
            __self__.refocus()
            return
        elif __self__.layer_count == 0: can_import = True
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
                    __self__.layer_numbering[__self__.layer_count] = cube.name
                    __self__.layer[cube.name] = Layer(cube,layer_no)
                    __self__.layers_list.insert(END,"{},{}".format(cube.name,layer_no))
                    layers_dict = convert_layers_to_dict(__self__)
                    __self__.build_image(__self__.image.shape)
                    __self__.maps_window.destroy()
                    __self__.refocus()


            elif packed_elements == []:
                if __self__.layer_count == 0: 
                    layer_no = 0
                    __self__.layer_count += 1
                else: 
                    layer_no = __self__.layer_count
                    __self__.layer_count += 1
                __self__.layer_numbering[__self__.layer_count] = cube.name
                __self__.layer[cube.name] = Layer(cube,layer_no)
                __self__.layers_list.insert(END,"{},{}".format(cube.name,layer_no))
                layers_dict = convert_layers_to_dict(__self__)
                __self__.build_image(__self__.image.shape)
                __self__.maps_window.destroy()
                __self__.refocus()

            else: return
    
    def get_toplayer(__self__,i,j):
        layer = __self__.layer_numbering[__self__.layer_count]
        # convert canvas coordinates to datacube coordinates
        x, y = __self__.layer[layer].start
        x_, y_ = __self__.layer[layer].end
        conv_x, conv_y = i-x, j-y
        if x <= i < x_ and y <= j < y_: #verifies if pixels belongs to the datacube
            return  __self__.layer[layer].name
        else: return ""

    def read_pixels(__self__,i,j):
        front_layer, top_layer, pixel = -1, 0, 59
        for layer in __self__.layer:
            try:
                x, y = __self__.layer[layer].start
                x_, y_ = __self__.layer[layer].end
                conv_x, conv_y = i-x, j-y
                if x <= i < x_ and y <= j < y_ \
                        and __self__.layer[layer].layer > front_layer:
                    pixel = __self__.layer[layer].img[conv_x,conv_y]
                    top_layer = __self__.layer[layer]
                    front_layer = top_layer.layer
            except:
                return pixel, top_layer
        return pixel, top_layer
    
    def build_image(__self__, size):
        global layers_dict
        __self__.image = cy_funcs.cy_build_image(
                __self__.image, 
                np.asarray(__self__.image.shape),
                layers_dict)
        __self__.im_plot.set_data(__self__.image)
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
        if __self__.layer == {}:
            messagebox.showerror("No Layers!",
                    "Please add cubes to canvas before trying to compile a new cube!")
            return
        start_x, start_y = __self__.image.shape
        end_x, end_y = 0, 0
        for layer in __self__.layer:
            if __self__.layer[layer].start[0] <= start_x: 
                start_x = __self__.layer[layer].start[0]
            if __self__.layer[layer].start[1] <= start_y:
                start_y = __self__.layer[layer].start[1]
            if __self__.layer[layer].end[0] >= end_x: 
                end_x = __self__.layer[layer].end[0]
            if __self__.layer[layer].end[1] >= end_y:
                end_y = __self__.layer[layer].end[1]
            specsize = __self__.layer[layer].matrix.shape[2]
        void_spectrum = np.zeros([specsize])
        __self__.merge_matrix = np.zeros([(end_x-start_x),(end_y-start_y),specsize],
                dtype="float32")
        __self__.merge_bg = np.zeros([(end_x-start_x),(end_y-start_y),specsize],
                dtype="float32")
        __self__.progress_bar = Busy((end_x-start_x)*(end_y-start_y),0)
        __self__.progress_bar.update_text("Packing...")
        x, iteration = 0,0
        for i in range(start_x, end_x):
            y=0
            for j in range(start_y, end_y):
                iteration += 1
                __self__.progress_bar.updatebar(iteration)
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
        
        __self__.progress_bar.update_text("Building cube...")
        __self__.progress_bar.updatebar(0)
        new_cube = Cube(["xrf"],SpecRead.CONFIG,mode="merge",name=NAME)
        new_cube.energyaxis = __self__.layer[layers[0]].energyaxis
        new_cube.dimension = (end_x-start_x), (end_y-start_y)
        __self__.progress_bar.progress["maximum"] = \
                new_cube.dimension[0]*new_cube.dimension[1]
        new_cube.img_size = new_cube.dimension[0] * new_cube.dimension[1]
        new_cube.matrix = np.zeros([new_cube.dimension[0],new_cube.dimension[1],\
                new_cube.energyaxis.shape[0]],dtype='float32',order='C')
        new_cube.background = np.zeros([new_cube.dimension[0],new_cube.dimension[1],\
                new_cube.energyaxis.shape[0]],dtype='float32',order='C')
        new_cube.matrix = __self__.merge_matrix
        new_cube.background = __self__.merge_bg
        new_cube.calibration = __self__.layer[layers[0]].calibration
        new_cube.config = SpecRead.CONFIG
        __self__.progress_bar.update_text("Digesting...")
        new_cube.digest_merge(bar=__self__.progress_bar)
        __self__.progress_bar.destroybar()

    def refocus(__self__,e=""):
        try: __self__.maps_window.destroy()
        except: pass
        __self__.master.grab_set()
        __self__.master.focus_set()

    def kill(__self__,e=""):
        __self__.master.grab_release()
        __self__.master.destroy()

   
if __name__.endswith('__main__'):         
    
    """ This is an independent module, which can be run separately from CoreGUI.py """

    optimum_resolution = (1920,1080)

    
    SpecRead.conditional_setup()
    mosaic_root = Mosaic_API((500,500))
    mosaic_root.master.mainloop()
