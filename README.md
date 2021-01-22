# XISMuS
#### X-Ray fluorescence Imaging Software for Multiple Samples

This software is distributed with a MIT license. Further details can be found [here](../master/LICENSE)<br>
XISMuS is a dedicated imaging software for X-Ray Fluorescence data (MA-XRF) for Windows OS. The software has been tested on Windows 7 (Ultimate 32-Bit and 64-Bit and Home Premium 64-Bit) and Windows 10. Windows XP is not supported. Be sure to have the latest Visual C++ Redistributable Package when running on *Windows 7*. It can be downloaded directly from Microsoft webpage [here](https://www.microsoft.com/en-us/download/details.aspx?id=40784)<br>
<br>
XISMuS most recent distribution packages can be found here [32-Bit][x86] and here [64-Bit][x64].<br>
A comprehensive User Guide PDF is provided in [this link][UserGuide].
<br>
## Installation
To install XISMuS, simply double-click the executable downloaded from one of the links above (32- or 64-bit depending on your system), carefully read the license agreement and follow the instructions on screen.
<br>
**Note:** XISMuS uses xraylib version 3.3.0. You can download it for free [here][xraylib]. Be sure to download the corresponding version to your system architecture.<ins> Note: If XISMuS fails to launch due to missing DLL's, please install xraylib.</ins><br>
If xraylib is not installed, the program may still run, but auto-wizard imaging method will not be available.<br>
Xraylib is used to ensure more precise experimental X-rays data are used. Its absence will cause XISMuS to use its internal database, which may be outdated and may be missing information for low-Z or high-Z elements.

## From Source
If you rather run it from the source, on your local Python environment interpreter, simply fork or clone the repository.<br>
<br>
`git clone https://github.com/linssab/XISMuS`<br>
<br>
Be sure to have all the required Python modules installed! They are listed in the section below.<br>
You will have to compile the Cython code, by typing in the following command on your terminal:<br>
<br>
`python .\setup_cy.py build_ext --inplace`<br>
<br>
You must have a GNU compiler to do so, as `stupy_cy.py` will compile the python code in `cy_funcs.pyx` into native C code.<br>
Finally, add `My Documents` content inside your user documents folder.<br>

#### Dependencies

To run it within a Python interpreter, we recommend you have Python 3.7 installed and the following packages:<br>
The packages whose versions are mentioned are the stable versions working with XISMuS. Numba, for example, has versions that may raise  issues with opencv and cause JIT funtions to malfunction.<br>
* numpy _v 1.18.1_<br>
* numba _v 0.45.1_<br>
* llvmlite _v 0.31_<br>
* cython (to run setup_cy.py)<br>
* h5py<br>
* opencv-python<br>
* SciPy
* psutil<br>
* pywin32 (for 32-bit system builds)<br>
* matplotlib<br>

#### xraylib _v 3.3.0_
XISMuS uses xraylib version 3.3.0. You can download it for free [here][xraylib]. Be sure to download the corresponding version to your system architecture. <ins>Note: If XISMuS fails to launch due to missing DLL's, please install xraylib.</ins><br>
If xraylib is not installed, the program will still run, but chemical mapping will be limited to few elements.<br>
Xraylib is used to ensure more precise experimental X-rays data are used. Its absence will cause XISMuS to use its internal database, which may be outdated and may be missing information for low-Z or high-Z elements.
<br>

[xraylib]: http://lvserver.ugent.be/xraylib/
[x64]: https://sourceforge.net/projects/xismus/files/XISMuSx64_1.3.2_Setup.exe/download
[x86]: https://sourceforge.net/projects/xismus/files/XISMuSx86_1.3.2_Setup.exe/download
[UserGuide]: https://sourceforge.net/projects/xismus/files/XISMuS_User_Manual_1.3.0.pdf/download

## Funding
This project has received funding from the European Union’s Horizon 2020 research and innovation programme under the Marie-Skłodowska Curie Innovative Training Networks (MSCA-ITN) grant agreement No 766311.<img align="right" src="https://github.com/linssab/XISMuS/blob/master/images/msca_itn.png?raw=true" width="70px"></img>
