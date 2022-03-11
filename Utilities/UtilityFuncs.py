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
import Constants
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

def screen_size():
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def maximize_window(window,e=""):
    if window.alt == False: return
    else:
        if window.master.state()=="zoomed":
            window.master.state("normal")
        else: 
            window.master.state("zoomed")

def place_topright(window1,window2):
    w_user, h_user = screen_size()
    
    # adapted from: https://stackoverflow.com/questions/3352918/
    """ Places window2 next to window1 top-right end """ 
    
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

    if x + width2 > w_user or y + height2 > h_user: 
        place_center(window1,window2) 
        return 1 
    if Constants.LOW_RES == None:
        window2.geometry(f"{width2}x{height2}+{x}+{y}")
    elif Constants.LOW_RES == "high":
        width = window2.winfo_screenwidth()
        height = window2.winfo_screenheight()
        w_width = window2.winfo_width()
        w_height = window2.winfo_height()
        window2.geometry(f"{w_width}x{w_height}+{int( ( width / 2 ) - ( w_width / 2 ) )}+{int( ( height / 2 ) - ( w_height / 2 ) )}")

def spawn_center(window):
    """ Spawns the window on center of screen. There are known issues
    with multiple monitors, specially of different dpi """
    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    w_width = window.winfo_width()
    w_height = window.winfo_height()
    window.geometry(f"+{int( ( width / 2 ) - ( w_width / 2 ) )}+{int( ( height / 2 ) - ( w_height / 2 ) )}")
    return

def place_center(window1,window2):
    """ Places window2 on center of window1 """

    window1.update_idletasks()
    window2.update_idletasks()
    width = window1.winfo_width()
    frm_width = window1.winfo_rootx() - window1.winfo_x()
    win_width = width + (2 * frm_width)
    width2 = window2.winfo_width()
    height = window1.winfo_height()
    titlebar_height = window1.winfo_rooty() - window1.winfo_y()
    height2 = window2.winfo_height()
    w_user, h_user = screen_size()   
    x = window1.winfo_rootx() + (int(win_width/2)) - (int(width2/2))
    y = window1.winfo_rooty() - titlebar_height + (int(height/2)) - (int(height2/2))
    if y < 0 or y + height2 > h_user: spawn_center(window2)
    elif x > w_user or x + width2 > w_user or x < 0: spawn_center(window2)
    else:
        window2.geometry(f"+{x}+{y}")
        window2.focus_force()
    return

# only display the buttons we need
class NavigationToolbar(NavigationToolbar2Tk):
    toolitems = (
    ('Home', 'Reset original view', 'home', 'home'),
    ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
    ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
    ('Save', 'Save the figure', 'filesave', 'save_figure')
  )

def convert_bytes(num):
    """ Obtained from https://stackoverflow.com/questions/210408 """

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0
        
def restore_bytes(num,unit):
    """ Reverse operation of convert_bytes function """

    units = ['KB', 'MB', 'GB', 'TB']
    for x in units:
        if unit == x:
            return num * (1024**(units.index(x)+1))

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

    def __init__(__self__, widget, wraplength=160):
        __self__.widget = widget
        __self__.tipwindow = None
        __self__.id = None
        __self__.x = __self__.y = 0
        __self__.wraplength = wraplength

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
                      font=("tahoma", "8", "normal"), wraplength=__self__.wraplength)
        label.pack(ipadx=1)

    def hidetip(__self__):
        tw = __self__.tipwindow
        __self__.tipwindow = None
        if tw:
            tw.destroy()

