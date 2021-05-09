#################################################################
#                                                               #
#          App Windows utilities                                #
#                        version: 2.4.0 - May - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################
import Constants
# tcl/Tk imports
try:
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox
    from tkinter import filedialog
    from tkinter import font as tkFont
except:
    from Tkinter import *
    from Tkinter import ttk
    from Tkinter import messagebox
    from Tkinter import filedialog
    import tkFont

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
        window2.geometry("{}x{}+{}+{}".format(width2, height2, x, y))
        window2.deiconify()
    elif Constants.LOW_RES == "high":
        width = window2.winfo_screenwidth()
        height = window2.winfo_screenheight()
        w_width = window2.winfo_width()
        w_height = window2.winfo_height()
        window2.geometry("{}x{}+{}+{}".format(w_width,w_height,\
                int((width/2)-(w_width/2)),int((height/2)-(w_height/2))))
        window2.deiconify()

def spawn_center(window):
    """ Spawns the window on center of screen. There are known issues
    with multiple monitors, specially of different dpi """

    width = window.winfo_screenwidth()
    height = window.winfo_screenheight()
    
    w_width = window.winfo_width()
    w_height = window.winfo_height()

    window.geometry("{}x{}+{}+{}".format(w_width,w_height,\
            int((width/2)-(w_width/2)),int((height/2)-(w_height/2))))
    window.focus_force() 

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
    win_height = height + titlebar_height + frm_width
    height2 = window2.winfo_height()

    w_user, h_user = screen_size()   

    x = window1.winfo_rootx() + (int(win_width/2)) - (int(width2/2))
    y = window1.winfo_rooty() - titlebar_height + (int(height/2)) - (int(height2/2))
    
    if y < 0 or y + height2 > h_user: spawn_center(window2)
    elif x > w_user or x + width2 > w_user or x < 0: spawn_center(window2)
    else:
        window2.geometry('{}x{}+{}+{}'.format(width2, height2, x, y))
        window2.deiconify()
        window2.focus_force()
    return
