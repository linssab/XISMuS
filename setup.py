import cx_Freeze
import sys, shutil
import os, opcode
from CoreGUI import VERSION
from win32com.shell import shell, shellcon
docs = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL, None, 0)
__PERSONAL__ = os.path.join(docs,"XISMuS")
__BIN__ = os.path.join(__PERSONAL__,"bin")
AUTHOR = "Sergio Augusto Barcellos Lins"
__ICON__ = os.path.join(os.getcwd(),"images","icons","icon.ico")

import numba
import llvmlite
import mpl_toolkits

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

includefiles_list=[
                (".\\images\\icons\\img_anal.ico",".\\images\\icons\\img_anal.ico"),
                (".\\images\\icons\\plot.ico",".\\images\\icons\\plot.ico"),
                (".\\images\\icons\\refresh.ico",".\\images\\icons\\refresh.ico"),
                (".\\images\\icons\\rubik.ico",".\\images\\icons\\rubik.ico"),
                (".\\images\\icons\\settings.ico",".\\images\\icons\\settings.ico"),
                (".\\images\\icons\\icon.ico",".\\images\\icons\\icon.ico"),
                (".\\images\\icons\\icons.tz",".\\images\\icons\\icons.tz"),
                (".\\images\\utils.tz",".\\images\\utils.tz"),
                (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'), 
                    os.path.join('lib', 'tcl86t.dll')),
                (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'), 
                    os.path.join('lib', 'tk86t.dll'))
                ]


mkls_path = os.path.join(os.path.dirname(os.path.dirname(os.__file__)),"Library","bin")

lib = []
if os.path.exists(os.path.join(mkls_path,"libiomp5md.dll")):
    lib.append((os.path.join(mkls_path,"libiomp5md.dll"), ".\\MKLs\\libiomp5md.dll"))
if os.path.exists(os.path.join(mkls_path,"libmmd.dll")):
    lib.append((os.path.join(mkls_path,"libmmd.dll"), ".\\MKLs\\libmmd.dll"))
if os.path.exists(os.path.join(mkls_path,"libifcoremd.dll")):
    lib.append((os.path.join(mkls_path,"libifcoremd.dll"), ".\\MKLs\\libifcoremd.dll")) 
if os.path.exists(os.path.join(mkls_path,"libimalloc.dll")):
    lib.append((os.path.join(mkls_path,"libimalloc.dll"), ".\\MKLs\\libimalloc.dll"))

mkls_ = [(os.path.join(mkls_path, mkl),".\\MKLs\\"+mkl) for mkl in os.listdir(mkls_path) if mkl.lower().startswith("mkl")]
for lib_file in lib: mkls_.append((lib_file))
for mkl in mkls_: includefiles_list.append(mkl)

with open(".\\folder.ini","w+") as inifile:
    inifile.write(os.path.join(__PERSONAL__,"Example Data"))

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
doc_files = [
    (".\\output.ini",os.path.join(__PERSONAL__,"output","output.ini")),
    (".\\folder.ini",os.path.join(__BIN__,"folder.ini")),
    (".\\config.cfg",os.path.join(__BIN__,"config.cfg")),
    (".\\logfile.log",os.path.join(__PERSONAL__,"logfile.log")),
    (".\\settings.tag",os.path.join(__BIN__,"settings.tag"))
    ]
try:
    os.mkdir(__BIN__)
except: print("Can't create folder {}".format(__BIN__))
try:
    os.mkdir(os.path.join(__PERSONAL__,"output"))
except: print("Can't create folder {}".format(os.path.join(__PERSONAL__,"output")))
try: 
    os.mkdir(__PERSONAL__)
    os.mkdir(__BIN__)
    os.mkdir(os.path.join(__PERSONAL__,"output"))
except: 
    print("{} folder tree already exists! Overwriting files.".format(__PERSONAL__))
for pair in doc_files:
    print(pair)
    shutil.copy(pair[0],pair[1])
    
###########################################################################

""" USE IF NEEDED
numba_path = os.path.dirname(numba.__file__)
llvmlite_path = os.path.dirname(llvmlite.__file__)
includefiles_list.append(numba_path)
includefiles_list.append(llvmlite_path)
"""
mpl_path = os.path.dirname(mpl_toolkits.__file__)
includefiles_list.append((mpl_path,".\\lib\\"))

for item in includefiles_list:
    print(item)

def load_sqlite3(finder, module):

    """In Windows, the sqlite3 module requires an additional dll sqlite3.dll to
       be present in the build directory."""
    if sys.platform == "win32":
        dll_name = "sqlite3.dll"
        dll_path = os.path.join(sys.base_prefix, "DLLs", dll_name)
        finder.IncludeFiles(dll_path, dll_name)

""" Creates an executable that opens the prompt (cmd) """
#executables = [cx_Freeze.Executable("CoreGUI.py", targetName="XISMuS", icon="C:\\Users\\sergi\\github\\xrfscanner\\images\\icons\\icon.ico")]

target = cx_Freeze.Executable(
        script="CoreGUI.py", 
        targetName="XISMuS.exe", 
        base="Win32GUI",
        icon=__ICON__)

options= {
            "packages":["tkinter","cv2","xraylib","matplotlib","numpy","llvmlite", "numba"],
            "includes":[],
            "excludes":[],
            "include_files":includefiles_list
            }

cx_Freeze.setup(
        name = "XISMuS",
        options = {"build_exe":options},
        version = VERSION,
        author = AUTHOR,
        author_email = "sergio.lins@roma3.infn.it",
        description = "X-Ray Imaging Software for Multiple Samples.",
        executables = [target]
        )

