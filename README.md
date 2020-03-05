# XISMuS
#### X-Ray fluorescence Imaging Software for Multiple Samples

This software is distributed with a MIT license. Further details can be found [here](../master/LICENSE)<br>
XISMuS is a dedicated imaging software for X-Ray Fluorescence data (MA-XRF) for Windows OS. The software has been tested on Windows 7 and Windows 10. Be sure to have the latest Visual C++ Redistributable Package when running on *Windows 7*. It can be downloaded from Microsoft webpage [here](https://www.microsoft.com/en-us/download/details.aspx?id=40784) <br>
<br>
XISMuS most recent distribution package can be found [here](https://www.google.com/). If you rather compile it yourself, follow the steps below.<br>
<br>
## Installation
No module form distribution is yet available to use with Python; nevertheless, you can clone the repo and compile it into an executable. To do so, simply use the provided setup script:<br>
<br>
`python setup.py build`<br>
<br>
Be sure to have all the required Python modules installed! They are listed below<br>

## Dependencies
XISMuS requires you to have xraylib version 3.3.0 (or superior) installed. You can download it for free [here][xraylib].<br>
If xraylib is not installed, the program will still run, but with some limited functionalities and errors are prone to happen.<br>
Xraylib is used to extract precise x-rays physics data. Its absence will cause XISMuS to use its internal database, which may be outdated.
<br>
To run it within a Python interpreter, we recommend you have Python 3.7 installed and the following packages:<br>
The packages whose versions are mentioned are the stable versions working with XISMuS. Numba, for example, has some issues with cx_freeze and may cause JIT funtions to malfunction.<br>
* numpy _v 1.18.1_<br>
* numba _v 0.45.1_<br>
* llvmlite _v 0.31_<br>
* opencv<br>
* psutil<br>
* multiprocessing<br>
* matplotlib
* cx_Freeze _v 6.0_ (for compiling the software)<br>

[xraylib]: http://lvserver.ugent.be/xraylib/xraylib-3.3.0-win64.exe
