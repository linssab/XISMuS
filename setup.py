import cx_Freeze
import sys
import os
from CoreGUI import VERSION

import scipy
import numba
import llvmlite

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')
mkls_path = r"C:\Users\sergi\Miniconda3\Library\bin" 
lib = []
lib.append((os.path.join(mkls_path,"libiomp5md.dll"), ".\\MKLs\\libiomp5md.dll"))
lib.append((os.path.join(mkls_path,"libmmd.dll"), ".\\MKLs\\libmmd.dll"))
lib.append((os.path.join(mkls_path,"libifcoremd.dll"), ".\\MKLs\\libifcoremd.dll")) 
lib.append((os.path.join(mkls_path,"libimalloc.dll"), ".\\MKLs\\libimalloc.dll"))

mkls_ = [(os.path.join(mkls_path, mkl),".\\MKLs\\"+mkl) for mkl in os.listdir(mkls_path) if mkl.lower().startswith("mkl")]
for lib_file in lib: mkls_.append((lib_file))

includefiles_list=[(".\\images\\icons\\erase.png",".\\images\\icons\\erase.png"),\
                (".\\images\\icons\\img_anal.png",".\\images\\icons\\img_anal.png"),\
                (".\\images\\icons\\img_anal.ico",".\\images\\icons\\img_anal.ico"),\
                (".\\images\\icons\\load.png",".\\images\\icons\\load.png"),\
                (".\\images\\icons\\plot.ico",".\\images\\icons\\plot.ico"),\
                (".\\images\\icons\\quit.png",".\\images\\icons\\quit.png"),\
                (".\\images\\icons\\reset.png",".\\images\\icons\\reset.png"),\
                (".\\images\\icons\\refresh.png",".\\images\\icons\\refresh.png"),\
                (".\\images\\icons\\refresh.ico",".\\images\\icons\\refresh.ico"),\
                (".\\images\\icons\\rubik.png",".\\images\\icons\\rubik.png"),\
                (".\\images\\icons\\rubik.ico",".\\images\\icons\\rubik.ico"),\
                (".\\images\\icons\\settings.png",".\\images\\icons\\settings.png"),\
                (".\\images\\icons\\settings.ico",".\\images\\icons\\settings.ico"),\
                (".\\images\\icons\\export_1.png",".\\images\\icons\\export_1.png"),\
                (".\\images\\icons\\export_2.png",".\\images\\icons\\export_2.png"),\
                (".\\images\\icons\\next.png",".\\images\\icons\\next.png"),\
                (".\\images\\icons\\previous.png",".\\images\\icons\\previous.png"),\
                (".\\images\\icons\\export_merge.png",".\\images\\icons\\export_merge.png"),\
                (".\\images\\icons\\icon.ico",".\\images\\icons\\icon.ico"),\
                (".\\images\\splash.png",".\\images\\splash.png"),\
                (".\\images\\no_data.png",".\\images\\no_data.png"),\
                (".\\output.ini",".\\output\\output.ini"),\
                (".\\folder.ini",".\\folder.ini"),\
                ".\\config.cfg",\
                ".\\logfile.log",\
                ".\\settings.tag",\
                ".\\fitconfigGUI.cfg",
                (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'), 
                    os.path.join('lib', 'tcl86t.dll')),
                (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'), 
                    os.path.join('lib', 'tk86t.dll'))]
for mkl in mkls_: includefiles_list.append(mkl)

training_data = [item for item in os.listdir("C:\\samples\\misure\\") if \
        item.lower().endswith(".mca") or item.lower().endswith(".txt")]

for item in training_data:
    path = "C:\\samples\\misure\\"+item
    new_path = ".\\training_data\\"+item
    includefiles_list.append((path,new_path))

with open(".\\folder.ini","w+") as inifile:
    inifile.write(".\\training_data\\")

with open(".\\config.cfg","w+") as cfgfile:
    configdict = {'directory': None,'bgstrip':"SNIPBG",\
                'ratio':True,'thickratio':0,\
                'calibration':"from_source",'enhance':True,\
                'peakmethod':"simple_roi",'bg_settings':[]}
    calibparam = [[1,1],[2,2]] 

    cfgfile.write("<<CONFIG_START>>\r")
    for key in configdict:
        cfgfile.write("{} = {}\r".format(key,configdict[key]))
    cfgfile.write("<<CALIBRATION>>\r")
    for pair in calibparam:
        cfgfile.write("{0}\t{1}\r".format(pair[0],pair[1]))
    cfgfile.write("<<END>>\r")

with open(".\\logfile.log","w+") as logfile:
    logfile.write(" ")

scipy_path = os.path.dirname(scipy.__file__)
numba_path = os.path.dirname(numba.__file__)
includefiles_list.append(scipy_path)
includefiles_list.append(numba_path)
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

#executables = [cx_Freeze.Executable("CoreGUI.py", targetName="XISMuS", icon="C:\\Users\\sergi\\github\\xrfscanner\\images\\icons\\icon.ico", base="Win32GUI")]
executables = [cx_Freeze.Executable("CoreGUI.py", targetName="XISMuS", icon="C:\\Users\\sergi\\github\\xrfscanner\\images\\icons\\icon.ico")]

cx_Freeze.setup(
        name = "XISMuS",
        options = {"build_exe":{\
                "packages":["llvmlite","tkinter","cv2","math","pickle","logging",\
                "xraylib","matplotlib"],\
                #"mpl_toolkits"],\
                
                "includes":["numpy","tkinter"],
                 
                "include_files":includefiles_list}},
                version = VERSION,
                executables = executables
        )
