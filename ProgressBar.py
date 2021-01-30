#################################################################
#                                                               #
#          PROGRESS BARS AND LOADING MODULE                     #
#                        version: 1.3.2 - Jan - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

from tkinter import *
from tkinter import ttk
import logging
import Constants
logger = logging.getLogger("logfile")
logger.info("Importing module BatchFitter.py...")

def create_tooltip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

class ToolTip(object):
    """ taken from https://stackoverflow.com/questions/20399243/display-message-when-hovering-over-something-with-mouse-cursor-in-python """

    def __init__(__self__, widget):
        __self__.widget = widget
        __self__.tipwindow = None
        __self__.id = None
        __self__.x = __self__.y = 0

    def showtip(__self__, text):
        "Display text in tooltip window"
        __self__.text = text
        if __self__.tipwindow or not __self__.text:
            return
        x, y, cx, cy = __self__.widget.bbox("insert")
        x = x + __self__.widget.winfo_rootx() + 57
        y = y + cy + __self__.widget.winfo_rooty() +27
        __self__.tipwindow = tw = Toplevel(__self__.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(tw, text=__self__.text, justify=LEFT,
                      background="#ffffe0", relief=SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(__self__):
        tw = __self__.tipwindow
        __self__.tipwindow = None
        if tw:
            tw.destroy()


class BusyManager:
    def __init__(__self__, widget):
        __self__.toplevel = widget.winfo_toplevel()
        __self__.widgets = {}

    def busy(__self__, widget=None):

    # attach busy cursor to toplevel, plus all windows
    # that define their own cursor.

        if widget is None:
            w = __self__.toplevel # myself
        else:
            w = widget

        if not str(w) in __self__.widgets:
            try:
                # attach cursor to this widget
                cursor = w.cget("cursor")
                if cursor != "watch":
                    __self__.widgets[str(w)] = (w, cursor)
                    w.config(cursor="watch")
            except TclError:
                pass

        for w in w.children.values():
            __self__.busy(w)

    def notbusy(__self__):
        for w, cursor in __self__.widgets.values():
            try:
                w.config(cursor=cursor)
            except TclError:
                pass
        __self__.widgets = {}


class Busy:
    """ Progress bar class. """
    
    def __init__(__self__,max_,min_,grab=True):
        __self__.master = Toplevel()
        __self__.master.attributes("-alpha",0.0)
        __self__.make_abortion = False
        __self__.master.resizable(False,False)
        __self__.master.overrideredirect(True)
        
        __self__.btnz = Frame(__self__.master)
        __self__.btnz.grid(row=1,column=0)
        __self__.outerframe = Frame(__self__.master, bd=3, relief=RIDGE)
        __self__.outerframe.grid(row=0,column=0)
        __self__.master.label = Label(__self__.outerframe, text="Packing spectra...")
        __self__.master.label.grid(row=0,column=0)       
        __self__.master.body = Frame(__self__.outerframe)        
        __self__.master.body.grid(row=1,column=0)
        __self__.progress = ttk.Progressbar(__self__.master.body, 
                orient="horizontal",length=160, 
                mode="determinate",
                style="green.Horizontal.TProgressbar",
                maximum=max_)
        __self__.progress.grid(row=0,column=0)
        if grab: __self__.master.grab_set()
        __self__.set_size()

    def set_size(__self__,th=-1):
        # NOTE: th is just a horrible workaround to rounding te size of the window
        # when adding the 'abort' button, window is a pixel shorter, when not, it is a 
        # pixel longer. So, without the button, a pixel is removed, when adding it, one
        # is added. It is a horrible workaround, but it works

        __self__.master.update()
        __self__.master.update_idletasks()

        x = __self__.master.winfo_screenwidth()
        y = __self__.master.winfo_screenheight()
        win_x = __self__.master.winfo_width()
        win_y = __self__.master.winfo_height()
        __self__.master.geometry('{}x{}+{}+{}'.format(win_x, win_y+th,
                round((x/2)-win_x/2), round((y/2)-win_y/2)))
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)

    def updatebar(__self__,value):

        """ update bar progress. Value is the progress literal value. The maximum value is 
        defined according to the amount of spectra to be read. """

        __self__.progress["value"] = value
        __self__.progress.update()

    def update_text(__self__,text):

        """ update text displayed on bar """

        __self__.master.label["text"] = text
        __self__.master.update()

    def destroybar(__self__):

        """ Destroys the bar window """

        __self__.master.grab_release()
        __self__.master.destroy()
        del __self__

    def interrupt(__self__,mca,timeout):

        """ In case of read failure, progress is interrupted """

        __self__.progress["maximum"] = timeout
        __self__.updatebar(timeout)
        __self__.update_text("Failed to read mca!")
        for i in range(timeout):
            __self__.updatebar(timeout-i)
            time.sleep(1)
        __self__.destroybar()

    def add_abort(__self__,workers=None,multiprocess=Constants.MULTICORE,mode=None):
        __self__.mode=mode
        __self__.workers = workers
        __self__.multiprocess = multiprocess
        __self__.master.geometry("{}x{}".format(166,81))
        __self__.abort_btn = ttk.Button(__self__.outerframe,
                text="Abort",
                width=7,
                command=__self__.abort)
        __self__.abort_btn.grid(row=2,column=0,pady=3)
        __self__.btnz.update()
        __self__.set_size(th=1)

    def abort(__self__):

        import pickle, os
        import Constants
        import SpecRead
        
        def verify_existing_fit_chunks():
            frames = [npy for npy in os.listdir(
                fit_path) if npy.lower().endswith(".npy")]
            if frames == []:
                return 0
            else: 
                return frames

        __self__.make_abortion = True
        __self__.abort_btn.config(state=DISABLED)
        messagebox.showinfo("ABORTED!","The process was aborted by the user.")

        cube_file = open(SpecRead.cube_path,'rb')
        del Constants.MY_DATACUBE
        Constants.MY_DATACUBE = pickle.load(cube_file)
        cube_file.close()

        fit_path = SpecRead.output_path
        if __self__.mode=="auto_wizard": 
            frames = verify_existing_fit_chunks()
            try: shutil.rmtree(os.path.join(fit_path,"Fit Plots"))
            except: pass
            for chunk in frames:
                try: os.remove(os.path.join(fit_path,chunk))
                except: pass

        return 

    def toggle_abort(__self__,state):
        if state=="on": __self__.abort_btn.config(state=NORMAL)
        elif state=="off": __self__.abort_btn.config(state=DISABLED)


class ReadProgress:
    def __init__(__self__,max_,min_):
        __self__.master = Toplevel()
        __self__.master.attributes("-alpha",0.0)
        __self__.master.resizable(False,False)
        __self__.master.overrideredirect(True)

        __self__.outerframe = Frame(__self__.master, bd=3, relief=RIDGE)
        __self__.outerframe.grid(row=0, column=0)
        __self__.master.label = Label(__self__.outerframe, text="Reading spectra...").\
                grid(row=0,column=0) 
        __self__.master.body = Frame(__self__.outerframe)        
        __self__.master.body.grid(row=1,column=0)
        __self__.progress = ttk.Progressbar(__self__.master.body, 
                orient="horizontal",
                length=160, 
                style="green.Horizontal.TProgressbar",
                mode="determinate",
                maximum=max_)
        __self__.progress.grid(row=0,column=0)
        __self__.spec = Label(__self__.master.body, text="")       
        __self__.spec.grid(row=2,column=0)
        
        __self__.master.update()
        x = __self__.master.winfo_screenwidth()
        y = __self__.master.winfo_screenheight()
        win_x = __self__.master.winfo_width()
        win_y = __self__.master.winfo_height()
        __self__.master.geometry('{}x{}+{}+{}'.format(win_x, win_y,
                int((x/2)-win_x/2), int((y/2)-win_y/2)))
        __self__.master.after(100,__self__.master.attributes,"-alpha",1.0)

    def updatebar(__self__,value):
        if value == __self__.progress["maximum"]-1: 
            __self__.master.destroy()
        else:
            __self__.progress["value"] = value
            __self__.progress.update()
            __self__.spec["text"] = "Spec {0} of {1}".format(value,__self__.progress["maximum"])
            __self__.spec.update()


class ThinkingWheel:
    def __init__(__self__,speed,x,y,auto=True,parent=None):
        if parent == None: auto = False
        __self__.master = Toplevel()
        __self__.parent = parent
        __self__.master.resizable(False,False)
        __self__.master.overrideredirect(True)
        __self__.speed = speed
        __self__.idx = 0
        spawn_x = __self__.master.winfo_screenwidth()
        spawn_y = __self__.master.winfo_screenheight()
        win_x = __self__.master.winfo_width()
        win_y = __self__.master.winfo_height()
        __self__.master.geometry('{}x{}+{}+{}'.format(x, y,
                int((spawn_x/2)-x/2), int((spawn_y/2)-y/2)))
        __self__.gif = [PhotoImage(file="./tnk.gif",format = 'gif -index %i' %(i),
            master = __self__.master) for i in range(8)]
        __self__.image = Label(__self__.master,
                text="Thinking...", image=__self__.gif[__self__.idx],
                compound=BOTTOM)
        __self__.image.grid(row=0,column=0)       
        __self__.master.grab_set()
        if auto == True: __self__.master.after(__self__.speed,__self__.update_frame)

    def update_frame(__self__):
        __self__.idx += 1
        if __self__.idx >= 8: __self__.idx = 0
        __self__.frame = __self__.gif[__self__.idx]
        __self__.image.configure(image=__self__.frame)
        __self__.parent.after(__self__.speed, __self__.update_frame)
        __self__.master.update()

    def next_frame(__self__):
        __self__.idx += 1
        if __self__.idx >= 8: __self__.idx = 0
        __self__.frame = __self__.gif[__self__.idx]
        __self__.image.configure(image=__self__.frame)
        __self__.master.update()

    def kill(__self__):
        __self__.master.grab_release()
        __self__.master.destroy()
        del __self__

