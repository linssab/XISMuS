# XISMuS
#### X-Ray fluorescence Imaging Software for Multiple Samples

This software is distributed with an MIT license. Further details can be found [here](../master/LICENSE)<br>
XISMuS is a dedicated imaging software for X-Ray Fluorescence data (MA-XRF) for Windows OS. This software had been tested on Windows 7 and Windows 10. <br>
The most recent distribution can be found [here](https://www.google.com/). To compile it from source, follow the steps below.<br>
<br>
## Installation
No package form distribution is yet available to use with Python; nevertheless, you can clone the repo and compile it from source. To do so, simply use the provided setup script:<br>
<br>
`python setup.py build`<br>
<br>
Be sure to have all the required Python packages installed!<br>
Alternatively, the most recent installation executable is available [in this link](https://www.google.com/).<br>

## Dependencies
XISMuS requires you to have xraylib version 3.3.0 (or superior) installed. You can download it for free [here][xraylib].<br>
If xraylib is not installed, the program will still run, but with some limited functionalities and errors are prone to happen.<br>
<br>
To run it within a Python interpreter, we recommend you have Python 3.7 installed and the following packages:<br>
* numpy<br>
* numba<br>
* scipy<br>
* cv2<br>
* psutil<br>
* multiprocessing<br>
* tkinter (for the Graphical User Interface)<br>

[xraylib]: http://lvserver.ugent.be/xraylib/xraylib-3.3.0-win64.exe
