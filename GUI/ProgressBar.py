"""
Copyright (c) 2020 Sergio Augusto Barcellos Lins & Giovanni Ettore Gigante

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

from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os, time
import shutil
import threading
import Constants


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
        
        __self__.outerframe = ttk.Frame(__self__.master, relief=RIDGE, style="dark.TFrame")
        __self__.master.body = ttk.Frame(__self__.outerframe, style="dark.TFrame")
        __self__.master.label = ttk.Label(__self__.outerframe, 
                text="Packing spectra...",
                style="dark.TLabel")
        __self__.progress = ttk.Progressbar(__self__.master.body, 
                orient="horizontal",length=160, 
                mode="determinate",
                style="red.Horizontal.TProgressbar",
                maximum=max_)

        __self__.master.label.grid(row=0,column=0, pady=(3,0))       
        __self__.progress.grid(row=0,column=0)
        __self__.outerframe.grid(row=0,column=0)
        __self__.master.body.grid(row=1,column=0,padx=(6,6),pady=(6,6))

        if grab: 
            __self__.master.focus_set()
            __self__.master.focus_force()
            __self__.master.grab_set()
        __self__.set_size()

    def set_size(__self__):
        __self__.master.update()
        __self__.master.body.update_idletasks()
        __self__.outerframe.update_idletasks()

        x = __self__.master.winfo_screenwidth()
        y = __self__.master.winfo_screenheight()
        win_x = __self__.master.winfo_width()
        win_y = __self__.master.winfo_height()
        try: btn_y = __self__.abort_btn.winfo_height() + 6 #pady = 3
        except: btn_y = 0
        __self__.master.geometry('{}x{}+{}+{}'.format(win_x, win_y + btn_y,
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

    def add_cancel_btn(__self__):
        def cancel():
            __self__.KILL = 1
            __self__.destroybar()
            return
        __self__.abort_btn = ttk.Button(__self__.outerframe,
                text="Cancel",
                width=7,
                command=cancel)
        __self__.abort_btn.grid(row=2,column=0,pady=3)
        __self__.set_size()

    def add_abort(__self__,workers=None,multiprocess=Constants.MULTICORE,mode=None):
        __self__.mode=mode
        __self__.workers = workers
        __self__.multiprocess = multiprocess
        __self__.abort_btn = ttk.Button(__self__.outerframe,
                text="Abort",
                width=7,
                command=__self__.abort)
        __self__.abort_btn.grid(row=2,column=0,pady=3)
        __self__.set_size()

    def abort(__self__):
        import pickle, os
        import Constants
        import Engine.SpecRead as sp
        
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

        cube_file = open(sp.cube_path,'rb')
        del Constants.MY_DATACUBE
        Constants.MY_DATACUBE = pickle.load(cube_file)
        cube_file.close()

        fit_path = sp.output_path
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
                style="red.Horizontal.TProgressbar",
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
        __self__.alive = True
        __self__.idx = 0
        GIF = os.path.join(os.path.dirname(__file__),"wheel.gif")
        spawn_x = __self__.master.winfo_screenwidth()
        spawn_y = __self__.master.winfo_screenheight()
        win_x = __self__.master.winfo_width()
        win_y = __self__.master.winfo_height()
        __self__.master.geometry('{}x{}+{}+{}'.format(x, y,
                int((spawn_x/2)-x/2), int((spawn_y/2)-y/2)))
        __self__.gif = [PhotoImage(file=GIF,format = 'gif -index %i' %(i),
            master = __self__.master) for i in range(8)]
        __self__.image = ttk.Label(__self__.master,
                text="Thinking...", image=__self__.gif[__self__.idx],
                compound=BOTTOM)
        __self__.image.grid(row=0,column=0)       
        __self__.master.grab_set()
        if auto == True: 
            __self__.master.after(
                    __self__.speed,
                    threading.Thread(target=__self__.update_frame).start()
                    )

    def update_frame(__self__):
        while __self__.alive:
            __self__.idx += 1
            if __self__.idx >= 8: __self__.idx = 0
            __self__.frame = __self__.gif[__self__.idx]
            __self__.image.configure(image=__self__.frame)
            __self__.master.update()
            time.sleep(__self__.speed)

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

