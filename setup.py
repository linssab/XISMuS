import cx_Freeze
import sys
import os

import scipy
import numba
import llvmlite

includefiles_list=[(".\\images\\icons\\erase.png",".\\images\\icons\\erase.png"),\
                (".\\images\\icons\\img_anal.png",".\\images\\icons\\img_anal.png"),\
                (".\\images\\icons\\img_anal.ico",".\\images\\icons\\img_anal.ico"),\
                (".\\images\\icons\\load.png",".\\images\\icons\\load.png"),\
                (".\\images\\icons\\plot.ico",".\\images\\icons\\plot.ico"),\
                (".\\images\\icons\\quit.png",".\\images\\icons\\quit.png"),\
                (".\\images\\icons\\reset.png",".\\images\\icons\\reset.png"),\
                (".\\images\\icons\\rubik.png",".\\images\\icons\\rubik.png"),\
                (".\\images\\icons\\rubik.ico",".\\images\\icons\\rubik.ico"),\
                (".\\images\\icons\\settings.png",".\\images\\icons\\settings.png"),\
                (".\\images\\icons\\settings.ico",".\\images\\icons\\settings.ico"),\
                (".\\images\\icons\\export_1.png",".\\images\\icons\\export_1.png"),\
                (".\\images\\icons\\export_2.png",".\\images\\icons\\export_2.png"),\
                (".\\images\\icons\\export_merge.png",".\\images\\icons\\export_merge.png"),\
                (".\\images\\icons\\icon.ico",".\\images\\icons\\icon.ico"),\
                (".\\images\\splash.png",".\\images\\splash.png"),\
                (".\\images\\no_data.png",".\\images\\no_data.png"),\
                (".\\output.ini",".\\output\\output.ini"),\
                (".\\folder.ini",".\\folder.ini"),\
                ".\\config.cfg",\
                ".\\settings.tag",\
                ".\\fitconfigGUI.cfg"]

scipy_path = os.path.dirname(scipy.__file__)
numba_path = os.path.dirname(numba.__file__)
includefiles_list.append(scipy_path)
includefiles_list.append(numba_path)
#includefiles_list.append(r'C:\\Users\\sergi\\Miniconda3\\lib\\site-packages\\numba')
includefiles_list.append(r"C:\Users\sergi\Miniconda3\Lib\site-packages\mpl_toolkits")

for item in includefiles_list:
    print(item)

def load_sqlite3(finder, module):

    """In Windows, the sqlite3 module requires an additional dll sqlite3.dll to
       be present in the build directory."""
    if sys.platform == "win32":
        dll_name = "sqlite3.dll"
        dll_path = os.path.join(sys.base_prefix, "DLLs", dll_name)
        finder.IncludeFiles(dll_path, dll_name)

#executables = [cx_Freeze.Executable("CoreGUI.py", icon="C:\\Users\\sergi\\github\\xrfscanner\\images\\icons\\icon.ico", base="Win32GUI")]
executables = [cx_Freeze.Executable("CoreGUI.py",icon="C:\\Users\\sergi\\github\\xrfscanner\\images\\icons\\icon.ico")]

cx_Freeze.setup(
        name = "Piratininga SM",
        options = {"build_exe":{\
                "packages":["llvmlite","Tkinter","cv2","math","pickle","logging",\
                "xraylib","matplotlib"],\
                #"mpl_toolkits"],\
                
                "includes":["numpy","Tkinter"],
                 
                "include_files":includefiles_list}},
                version = "0.0.1",
                executables = executables
        )
