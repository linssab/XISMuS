#################################################################
#                                                               #
#          GUI Theme                                            #
#                        version: 2.0.0 - Feb - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import Constants

try:
    from tkinter import *
    from tkinter import ttk
    from tkinter import font as tkFont
except:
    from Tkinter import *
    from Tkinter import ttk
    import tkFont

def apply_theme(TkWin):
    default = Constants.DEFAULTBTN_COLOR
    dark = "#A0A1A1"
    system = TkWin.master.cget("background")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TCheckbutton", focuscolor=system)
    style.configure("TCheckbutton", background=default)
    style.map("TCheckbutton", background=[("disabled",default),("active",default)])
    style.configure('TButton', focuscolor="#D3D3D3")
    style.configure('TButton', background=system)
    style.configure('main.TButton', background=system, 
            anchor=W, relief=RAISED, bd=3)
    style.configure("green.Horizontal.TProgressbar", foreground="red", background="red")
    style.configure("TFrame", background=system)
    style.configure("TLabelframe", background=system, foreground="black")
    style.configure("TLabelframe.Label", background=system, foreground="black", 
            font=("Tahoma",10,"bold"))
    style.configure("TLabel", background=system)
    style.configure("dark.TFrame", background=dark)
    style.configure("dark.TLabel", background=dark)
    style.configure("dark.TLabelframe", background=dark)
