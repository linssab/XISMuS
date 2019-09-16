import cx_Freeze
import sys
import os

import scipy
import numba
import llvmlite

includefiles_list=[(".\\images\\icons\\erase.png",".\\images\\icons\\erase.png"),\
                (".\\images\\icons\\img_anal.png",".\\images\\icons\\img_anal.png"),\
                (".\\images\\icons\\quit.png",".\\images\\icons\\quit.png"),\
                (".\\images\\icons\\reset.png",".\\images\\icons\\reset.png"),\
                (".\\images\\icons\\load.png",".\\images\\icons\\load.png"),\
                (".\\images\\icons\\settings.png",".\\images\\icons\\settings.png"),\
                (".\\output.ini",".\\output\\output.ini"),\
                ".\\config.cfg",\
                ".\\fitconfigGUI.cfg"]
scipy_path = os.path.dirname(scipy.__file__)
numba_path = os.path.dirname(numba.__file__)
ll_path = os.path.dirname(llvmlite.__file__)
includefiles_list.append(scipy_path)
includefiles_list.append(numba_path)
includefiles_list.append(r'C:\\Users\\sergi\\Miniconda3\\lib\\site-packages\\numba')
includefiles_list.append(ll_path)
for item in includefiles_list:
    print(item)

def load_sqlite3(finder, module):

    """In Windows, the sqlite3 module requires an additional dll sqlite3.dll to
       be present in the build directory."""
    if sys.platform == "win32":
        dll_name = "sqlite3.dll"
        dll_path = os.path.join(sys.base_prefix, "DLLs", dll_name)
        finder.IncludeFiles(dll_path, dll_name)

executables = [cx_Freeze.Executable("CoreGUI.py", base="Win32GUI")]
#executables = [cx_Freeze.Executable("CoreGUI.py")]

cx_Freeze.setup(
        name = "Piratininga SM",
        options = {"build_exe":{\
                "packages":["llvmlite","tkinter","cv2","math","pickle","logging",\
                "xraylib","matplotlib","mpl_toolkits"],\
                
                "includes":["numpy"],
                
                "include_files":includefiles_list}},
                version = "0.0.1",
                executables = executables
        )
