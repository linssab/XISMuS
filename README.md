# XISMuS
#### X-Ray fluorescence Imaging Software for Multiple Samples

This software is distributed with a MIT license. Further details can be found [here](../master/LICENSE)<br>
XISMuS is a dedicated imaging software for X-Ray Fluorescence data (MA-XRF) for Windows OS. The software has been tested on Windows 7 (Ultimate 32-Bit and 64-Bit and Home Premium 64-Bit) and Windows 10. Windows XP is not supported. Be sure to have the latest Visual C++ Redistributable Package when running on *Windows 7*. It can be downloaded directly from Microsoft webpage [here](https://www.microsoft.com/en-us/download/details.aspx?id=40784)<br>
<br>
XISMuS most recent distribution packages can be found here [32-Bit][x86] and here [64-Bit][x64]. If you rather compile it yourself, follow the steps below.<br>
<br>
## Installation
No module form distribution is yet available to use with Python; nevertheless, you can clone the repo and compile it into an executable. To do so, simply use the provided setup script:<br>
<br>
`python setup.py build_exe -b "./directory"`<br>
<br>
Be sure to have all the required Python modules installed! They are listed below<br>

## Dependencies
XISMuS requires you to have xraylib version 3.3.0 installed. You can download it for free [here][xraylib]. Be sure to download the corresponding version to your system architecture.<br>
If xraylib is not installed, the program will still run, but chemical mapping will be limited to few elements.<br>
Xraylib is used to ensure more precise experimental X-rays data are used. Its absence will cause XISMuS to use its internal database, which may be outdated and may be missing information for low-Z or high-Z elements.
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
[x64]: https://mega.nz/#!oTJVXYIY!jAJ3u8dL8_ItcH-8jYYzgkcLBibLeWosSU7msBzSZK0
[x86]: https://mega.nz/#!MbY1WKzA!AKqHqlcAQQzaLGkF1BPhasG85U9dA67baJV7gOICo14
