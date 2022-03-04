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

import Constants
BG = {}
FG = {}

from tkinter import *
from tkinter import ttk

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

