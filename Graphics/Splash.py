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

def screen_size():
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)   


class SplashScreen:
    def __init__(__self__):
        from .Decoder import IMG_SPLASH
        BG = "red"
        __self__.master = Tk()
        __self__.master.resizable(False,False)
        __self__.master.configure(bg=BG)
        __self__.master.wm_attributes("-transparent", BG)
        scr_w, scr_h = screen_size()
        w, h = 787, 526
        __self__.master.geometry(f"{w}x{h}+{int((scr_w/2)-w/2)}+{int((scr_h/2)-h/2)}")
        __self__.master.overrideredirect(True)
        __self__.master.withdraw()

        __self__.text = StringVar()
        __self__.text.set("Start")
        __self__.master.grid_rowconfigure(0,weight=10)
        __self__.master.grid_rowconfigure(1,weight=1)
        __self__.master.grid_columnconfigure(0,weight=1)
        __self__.master.grid_columnconfigure(1,weight=1)
        __self__.master_image = PhotoImage(data=IMG_SPLASH)

        __self__.canvas = Canvas(__self__.master, 
                height=h,
                width=w,
                highlightthickness=0,
                bd=0,
                bg=BG)
        pad = 10
        __self__.canvas.create_image(int(w/2),int(h/2),image=__self__.master_image)
        __self__.label2 = __self__.canvas.create_text(
                119+pad,382+pad,text=__self__.text,
                font=("Tahoma",12),
                fill="white",
                anchor=W)
        __self__.canvas.grid(row=0,column=0,columnspan=3)

        __self__.master.update()
        __self__.master.update_idletasks()
        __self__.master.wm_attributes("-topmost",True)
        __self__.master.wm_attributes("-disabled",True)
        __self__.master.deiconify()

    def update(__self__,text):
        __self__.text.set(text)
        __self__.canvas.itemconfigure(__self__.label2, text=text)
        __self__.master.update()

    def kill(__self__):
        __self__.master.destroy()


