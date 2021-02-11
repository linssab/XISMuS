try:
    from tkinter import *
except:
    from Tkinter import *

def screen_size():
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)   


class SplashScreen:
    def __init__(__self__):
        from .Decoder import IMG_SPLASH
        __self__.master = Tk()
        __self__.master.resizable(False,False)
        __self__.master.configure(bg="#DCDCDC")
        w, h = screen_size()
        __self__.master.geometry(f"640x400+{int(w/2)-320}+{int(h/2)-200}")
        __self__.master.overrideredirect(True)
        __self__.master.withdraw()

        __self__.text = StringVar()
        __self__.text.set(" ")
        __self__.master.grid_rowconfigure(0,weight=10)
        __self__.master.grid_rowconfigure(1,weight=1)
        __self__.master.grid_columnconfigure(0,weight=1)
        __self__.master.grid_columnconfigure(1,weight=1)
        __self__.master_image = PhotoImage(data=IMG_SPLASH)

        __self__.canvas = Label(__self__.master, 
                image = __self__.master_image,
                height=374)
        __self__.canvas.grid(row=0,column=0,columnspan=2)
        __self__.footer = Frame(__self__.master, bg="#DCDCDC")
        __self__.label1 = Label(__self__.footer, text="Loading...\t",bg="#DCDCDC")
        __self__.label2 = Label(__self__.footer, textvariable = __self__.text,bg="#DCDCDC")

        __self__.footer.grid(row=1,column=0,columnspan=2,sticky=W+E)
        __self__.label1.grid(row=0,column=0,sticky=W)
        __self__.label2.grid(row=0,column=1)

        __self__.master.update()
        __self__.master.update_idletasks()
        __self__.master.wm_attributes("-topmost",True)
        __self__.master.wm_attributes("-disabled",True)
        __self__.master.deiconify()

    def update(__self__,text):
        __self__.text.set(text)
        __self__.label2.update()

    def kill(__self__):
        __self__.master.destroy()


