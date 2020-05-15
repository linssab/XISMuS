from tkinter import *
from tkinter import ttk


class Busy:
    
    """ Progress bar class. """
    
    def __init__(__self__,max_,min_):
        __self__.master = Toplevel()
        __self__.master.resizable(False,False)
        __self__.master.overrideredirect(True)
        x = __self__.master.winfo_screenwidth()
        y = __self__.master.winfo_screenheight()
        win_x = __self__.master.winfo_width()
        win_y = __self__.master.winfo_height()
        __self__.master.geometry('{}x{}+{}+{}'.format(166, 49,\
                int((x/2)-80), int((y/2)-23)))
        __self__.outerframe = Frame(__self__.master, bd=3, relief=RIDGE)
        __self__.outerframe.grid(row=0,column=0)
        __self__.master.label = Label(__self__.outerframe, text="Packing spectra...")
        __self__.master.label.grid(row=0,column=0)       
        __self__.master.body = Frame(__self__.outerframe)        
        __self__.master.body.grid(row=1,column=0)
        __self__.progress = ttk.Progressbar(__self__.master.body, orient="horizontal",length=160, mode="determinate",maximum=max_)
        __self__.progress.grid(row=0,column=0)
        __self__.master.grab_set()

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


class ReadProgress:
    
    def __init__(__self__,max_,min_):
        __self__.master = Toplevel()
        __self__.master.resizable(False,False)
        __self__.master.overrideredirect(True)
        x = __self__.master.winfo_screenwidth()
        y = __self__.master.winfo_screenheight()
        win_x = __self__.master.winfo_width()
        win_y = __self__.master.winfo_height()
        __self__.master.geometry('{}x{}+{}+{}'.format(166, 71,\
                int((x/2)-80), int((y/2)-35)))
        __self__.outerframe = Frame(__self__.master, bd=3, relief=RIDGE)
        __self__.outerframe.grid(row=0, column=0)
        __self__.master.label = Label(__self__.outerframe, text="Reading spectra...").\
                grid(row=0,column=0) 
        __self__.master.body = Frame(__self__.outerframe)        
        __self__.master.body.grid(row=1,column=0)
        __self__.progress = ttk.Progressbar(__self__.master.body, orient="horizontal",length=160, mode="determinate",maximum=max_)
        __self__.progress.grid(row=0,column=0)
        __self__.spec = Label(__self__.master.body, text="")       
        __self__.spec.grid(row=2,column=0)

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
        __self__.master = Tk()
        __self__.parent = parent
        __self__.master.resizable(False,False)
        __self__.master.overrideredirect(True)
        __self__.speed = speed
        __self__.idx = 0
        spawn_x = __self__.master.winfo_screenwidth()
        spawn_y = __self__.master.winfo_screenheight()
        win_x = __self__.master.winfo_width()
        win_y = __self__.master.winfo_height()
        __self__.master.geometry('{}x{}+{}+{}'.format(x, y,\
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

