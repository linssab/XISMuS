#################################################################
#                                                               #
#          GUI Theme                                            #
#                        version: 2.0.0 - Feb - 2021            #
# @author: Sergio Lins               sergio.lins@roma3.infn.it  #
#################################################################

import Constants
BG = {}
FG = {}

try:
    from tkinter import *
    from tkinter import ttk
    from tkinter import font as tkFont
except:
    from Tkinter import *
    from Tkinter import ttk
    import tkFont

def apply_theme(root):
    default = Constants.DEFAULTBTN_COLOR

    system00 = "#A0A1A1"
    system01 = default

    style = ttk.Style()
    style.theme_use("clam")

    root.master.configure(bg=system01)
    BG["Listbox"] = "white"   
    BG["Button"] = system01   
    FG["Listbox"] = "black"
    FG["Button"] = "black"

    style.configure("TCheckbutton", focuscolor=system01)
    style.configure("TCheckbutton", background=system01)
    style.map("TCheckbutton", background=[("disabled",system01),("active",system01)])
    style.configure('TButton', focuscolor="#D3D3D3")
    style.configure('TButton', background=system01)
    style.configure('main.TButton', background=system01, 
            anchor=W, relief=RAISED, bd=3)

    style.configure("red.Horizontal.TProgressbar", foreground="red", background="red")

    style.configure("TLabel", background=system01)
    style.configure("TFrame", background=system01)
    style.configure("TLabelframe", background=system01, foreground="black")
    style.configure("TLabelframe.Label", background=system01, foreground="black", 
            font=("Tahoma",10,"bold"))

    style.configure("dark.TFrame", background=system00)
    style.configure("dark.TLabel", background=system00)
    style.configure("dark.TLabelframe", background=system00)
    return style

def apply_theme_dark(root):
    default = Constants.DEFAULTBTN_COLOR

    system00 = "#0E1013"
    system01 = "#17181B"
    system02 = "#202124"
    system03 = "#282A2D"
    system04 = "#2E3134"
    system05 = "#3C4043"
    system06 = "#5F6368"

    foreground00 = "#80868B"
    foreground01 = "#9AA0A6"
    foreground02 = "#BDC1C6"
    foreground03 = "#DADCE0"
    foreground04 = "#E8EAED"
    foreground05 = "#F1F3F4"
    foreground06 = "#F8F9FA"

    style = ttk.Style()
    style.theme_use("clam")

    root.master.configure(bg=system04)
    BG["Listbox"] = system05
    BG["Button"] = system04
    FG["Listbox"] = foreground01
    FG["Button"] = foreground06

    style.configure("TCheckbutton", focuscolor=system06)
    style.configure("TCheckbutton", background=system04)
    style.map("TCheckbutton", background=[("disabled",system04),("active",system04)])

    style.configure('TButton', 
            focuscolor=system05,
            background=system04, 
            foreground=foreground05)
    style.configure('main.TButton', 
            focuscolor=system05,
            background=system04,
            foreground=foreground05,
            anchor=W, 
            relief=RAISED, 
            bd=3)

    style.configure("red.Horizontal.TProgressbar", foreground="red", background="red")

    style.configure("TFrame", background=system04)
    style.configure("TLabel", background=system04)
    style.configure("TLabelframe", background=system04, foreground=foreground05)
    style.configure("TLabelframe.Label", background=system04, foreground=foreground05,
            font=("Tahoma",10,"bold"))

    style.configure("dark.TFrame", background=system01)
    style.configure("dark.TLabel", background=system01)
    style.configure("dark.TLabelframe", background=system01)

    style.map("TButton",
            foreground=[("active",foreground05),("pressed",foreground06)],
            background=[("active",system05),("pressed",system06)])
    style.map("main.TButton",
            foreground=[("active",foreground05),("pressed",foreground06)],
            background=[("active",system05),("pressed",system06)])
    return style

