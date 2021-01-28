
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
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TCheckbutton", focuscolor=TkWin.master.cget("background"))
    style.configure("TCheckbutton", background=default)
    style.map("TCheckbutton", background=[("disabled",default),("active",default)])
    style.configure('TButton', focuscolor="#D3D3D3")
    style.configure('TButton', background=TkWin.master.cget("background"))
    style.configure('main.TButton', background=TkWin.master.cget("background"), 
            anchor=W, relief=RAISED, bd=3)
    style.configure("green.Horizontal.TProgressbar", foreground="red", background="red")
