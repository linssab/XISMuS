# XISMuS
#### X-Ray fluorescence Imaging Software for Multiple Samples

This software is distributed with a MIT license. Further details can be found [here](../master/LICENSE).\
XISMuS is a dedicated imaging software for X-Ray Fluorescence data (MA-XRF) for Windows OS. The software has been tested on Windows 7 (Ultimate 32-Bit and 64-Bit and Home Premium 64-Bit) and Windows 10. Windows XP is not supported. Be sure to have the latest Visual C++ Redistributable Package when running on *Windows 7*. It can be downloaded directly from Microsoft webpage [here](https://www.microsoft.com/en-us/download/details.aspx?id=40784).\
XISMuS most recent distribution packages can be found here [32-Bit][x86] and here [64-Bit][x64].\
A comprehensive User Guide PDF is provided in [this link][UserGuide].

## Installation
To install XISMuS, simply double-click the executable downloaded from one of the links above (32- or 64-bit depending on your system), carefully read the license agreement and follow the instructions on screen.\
An [update][PATCH] is available. Be sure to download an run it after XISMuS Installation. The update is intended for version v2.x.x onwards. If upgrading from a previous version (v1.x.x), please use the newest installer and only then apply the update. Update v2.2.1 is known for causing the software to freeze when booting in few computers. The new update, v2.3.0, corrects this issue among other stuff.

**Note:** XISMuS uses xraylib version 3.3.0. You can download it for free [here][xraylib]. Be sure to download the corresponding version to your system architecture.<ins> Note: If XISMuS fails to launch due to missing DLL's, please install xraylib.</ins>
If xraylib is not installed, the program may still run, but few methods may not be available.\
Xraylib is used to ensure more precise experimental X-rays data are used. Its absence will cause XISMuS to use its internal database, which may be outdated and may be missing information for low-Z or high-Z elements.

## From Source
If you rather run it from the source, on your local Python environment interpreter, simply fork or clone the repository.

`git clone https://github.com/linssab/XISMuS`

Be sure to have all the required Python modules installed! They are listed in the section below.
You can install the proper corresponding versions using the "requirements.txt" file provided by typing the following command:

`pip install -r .\requirements.txt`

You will have to compile the Cython code, by typing in the following command on your terminal:

`python .\setup_cy.py build_ext --inplace`

You must have a GNU compiler to do so, as `setup_cy.py` will compile the python code in `cy_funcs.pyx` into native C code.
Finally, add `My Documents` content inside your user documents folder.

## As a package
XISMuS Elements module is available as a package.\
To install it, simply type:

`pip install compwizard`

Another module derived from this software is also available: the [xfit][xfit] module.\
The modules can be imported with:

```python-repl=
import Elements
import xfit
```

xfit provides the Spectrum class, for the fitting of X-ray fluorescence spectra.\
For further usage information, check the [compwizard][compwizard] module.

#### Dependencies

To run it within a Python interpreter, we recommend you have Python 3.7 installed and the following packages:
The packages whose versions are mentioned are the stable versions working with XISMuS. Numba, for example, has versions that may raise  issues with opencv and cause JIT funtions to malfunction.
* numpy _v 1.18.1_
* numba _v 0.45.1_
* llvmlite _v 0.31_
* cython (to run setup_cy.py)
* h5py
* opencv-python
* SciPy
* psutil
* pywin32 (for 32-bit system builds)
* matplotlib

You can install the proper corresponding versions using the "requirements.txt" file provided by typing the following command:

`pip install -r .\requirements.txt`


#### xraylib _v 3.3.0_
XISMuS uses xraylib version 3.3.0. You can download it for free [here][xraylib]. Be sure to download the corresponding version to your system architecture. <ins>Note: If XISMuS fails to launch due to missing DLL's, please install xraylib.</ins>
If xraylib is not installed, the program may still run, but few methods may not be available.\
Xraylib is used to ensure more precise experimental X-rays data are used. Its absence will cause XISMuS to use its internal database, which may be outdated and may be missing information for low-Z or high-Z elements.

[xraylib]: http://lvserver.ugent.be/xraylib/
[x64]: https://sourceforge.net/projects/xismus/files/XISMuSx64_2.0.0_Setup.exe/download
[x86]: https://sourceforge.net/projects/xismus/files/XISMuSx86_2.0.0_Setup.exe/download
[PATCH]: https://sourceforge.net/projects/xismus/files/XISMuS-v2.4.3-Update.exe/download
[UserGuide]: https://sourceforge.net/projects/xismus/files/XISMuS_User_Manual_2.4.0.pdf/download
[compwizard]: https://pypi.org/project/compwizard/
[xfit]: https://pypi.org/project/xfit/

## Funding
This project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie-Skłodowska Curie Innovative Training Networks (MSCA-ITN) grant agreement No 766311.<img align="right" src="https://github.com/linssab/XISMuS/blob/master/images/msca_itn.png?raw=true" width="70px"></img>
