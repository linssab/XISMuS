Here you can find information on how the code actually handles the data and how it calculates certain values.
To begin with, keep in mind that the input data are always spectra files. These files usually contain information such as the _live time_, _calibration data_ and obviously the _data_ itself.
_SpecRead.py_, as the name suggests, handles the reading process. It extracts the information contained in the spectra files and read essential configuration parameters required to run the algorithm. The configuration is set by the user inside config.cfg file. It is simple and straight forward. 
_SpecMath.py_, _Mapping.py_ and _ImgMath.py_ contains a series of functions to manipulate and handle the data; from simple mathematical operations to the application of more advanced methods such as _SpecFitter.py_ and (until now) basic imaging processing.

## Mapping
This is the "core" of the algorithm. It contains the routines that will calculate and generate the elemental map(s) from the spectra files. So far it can create a single-element map, multi-element map (up to three elements), density map, ratio map and thickness map (the latter two are similar but the data is read in a different manner, e.g. the thickness map is a 3D plot of the surface). How each one is calculated and generated will be explained in the following paragraphs. Further information regarding the **usage** is given in _REAMDME.md_ file.

#### Density map
This routine creates a 2D-matrix, where each element represents the total of _counts_ contained in the pixel-associated spectrum. For a better understanding let's continue with an example: Suppose our data is composed of 600 spectra files representing a scanned area of 24x25 pixels. Assuming the _acquisition time_ of each spectrum is the same, the counts will therefore be direclty proportional to the density of the material measured at that spot.

In order to generate a true image, the matrix must be transformed into a RGBA format. The first step is to normalize our 2D-matrix of total counts, dividing each element for the maximum value of the matrix and then multiplying by 255. The next steps are conducted in a _colorizing_fnc_ function, that will create a RGBA-style matrix turning each pixel (that held one value) into a vector containing now 4 values. **attention: _colorizing_fnc_ function has some known bugs and corrections must yet be done. For now, a false-color map is generated instead of a colorized version. The false-color map is rendered in a yellow-blue scale - a matplotlib default where yeallow means less**
Since we are creating a density map, a grayscale image is enough for visual interpretation (the _colorizing_fnc_ function also handles the elemental maps, which contain colors. Therefore, it was written in a more general way). 
Finally, the grayscale image is produced by associating the pixel-value of our 2D-matrix to each color channel, R, G and B. A is maintained at the value of 255.

#### Elemental maps
Differently from the previous map, the elemental maps must compute the counts contained in a very specific intervals of energy (or channels). Due to the statistical process involved in the acquisition of the data and the count-to-charge ratio, the peaks observed for each XRF line are represented by a gaussian distribution instead of a discrete line.
The typical XRF line energies, jump ration, fluorescence yields, cross-sections and more for each chemical element are calculated and available in open-source libraries as well as in printed XRF handbooks.

The data contained in each spectrum represents the counts per channel. Since the calculated energies for the XRF lines are given in KeV, a calibration curve must be calculated to "convert" the channels to energies.
This calibration curve is calculated following the linear regression method. The parameters are extracted from _config.cfg_ file, which also contains the dimension of the map to be created in lines x rows.

The function that creates the elemental map takes the chemical elements symbols as input in string formatting, e.g. `mapfunction('X','Y')`.
It is up to the algorithm to determine the region of interest (ROI) that represents each of chemical elements the user wants to be found inside the spectrum data. This is made by reading the energy library _EnergyLib.py_ and accessing the theoretical values of lines Kα and Kβ (or Lα and Lβ if the element has an atomic number higher than 50)¹ for element X stored within this library. The same is done for element Y after the map acquisition of element X is complete. 
To save some computing time, Kβ net peak is only searched for and calculated if a Kα peak for the element being looked up was detected in the spectrum currently being read.

_¹If the excitation current used during the acquisition of the spectra was of let's say 30 Kv, there is no way one could observe the K-lines of mercury, for example in the obtained spectra._

##### Peak resolving
With the peak position for line Kα (lookup energy) of element J defined, the algorithm must estimate the ROI to compute the peak net area. Adding to the situation, there is the fact the calibration isn't always perfect (even with a correlation coefficient of 1) and there will always be some slight changes between the observed peak position and the theoretical value. In this case, the observed peak of Au-Lα line for example, could be found somewhere between 9.611 and 9.811 KeV. This interval is a subject of a greater discussion and involves the resolution of the detector, count-to-charge ratio and statistical treatment of data. For the time being, an interval of +1.10  and -1.10 times that of the peak Full Width at Half Maximum (FWHM) centered at the theoretical peak position is defined. This value has proven so far to be reasonable and does the job well.
Since the peaks can be approximated to a gaussian distribution, their width can be estimated. The FWHM is equivalent to 2.3548 * σ, where σ is given by the following equation proposed by Solè et al. 2007:

<img src="https://latex.codecogs.com/gif.latex?\sigma^{2}&space;=&space;\left&space;(\frac{NOISE}{2.3548}&space;\right&space;)^{2}&space;&plus;&space;3.85&space;*&space;FANO&space;*&space;E_{j}" title="\sigma^{2} = \left (\frac{NOISE}{2.3548} \right )^{2} + 3.85 * FANO * E_{j}" />

Ej is the peak energy/characteristic line, NOISE is the electronic contribution to the peak width, FANO is the fano factor and 3.85 is the energy required to produce an electron-hole pair in silicon.

Nonetheless, the algorithm must still verify if the observed peak position matches the theoretical value (obtained from _EnegyLib.py_) in the ROI discussed above. This is done by verifying the maximum y value within the ROI. If y-max corresponds to the theoretical peak position, then the net peak area corresponding to 2 * FWHM is calculated, if not, and if the x value associated to y-max differs up to 1.1 * FWHM from the theoretical one, the code shifts the Kα line position for element J to the new x value and repeats the process one more time. This is called _shift_, which is also a variable that contains the y-max value, x-max value and y-max index inside the ROI array.
If after the second (or third) shift no correspondence is found between the lookup energy and the theoretical value, Kα peak of element J is said to be _False_. Let that be _True_, the algorithm will repeat the process but now for Kβ peak of the same element J. If Kβ results in a _False_ peak, then both peaks are said to be _False_. 
There are more criteria implemented to resolve the peaks, such as signal-to-noise ratio (SNR) evaluation and second differential calculation.

**Attention: The data array provided by _SpecRead.py_ can be modified by _SpecMath.py_ if SNIPBG method is chosen for background estimation for efficiency purposes. Setting it to SNIPBG also means that the data array will be smoothned inside `setROI(lookup,xarray,yarray,svg):` function. This has shown to increase the accuracy of the method. Second differential is still applied over the non-smoothned (RAW) data. The smoothening method applied is a simple Savitsky-Golay filter - 11 points window and 3rd order polynomial approximation. The second differential is smoothned regardless of the background stripping method chosen.**

###### PyMcaFit
It is important to mention that the net peak areas can be calculated in many ways. So far the options `Simple` and `PyMcaFit` are available in config.cfg file. `Simple` means that the area is calculated by summing over the defined ROI. Counts per channel. Corrections for background noise are configured separetely and are independent of the net peak calculation method except from the relation given in the above pragraph. `PyMcaFit` is a bit more complex and therefore requires more processing time. This method fits every spectrum in the batch, spectrum by spectrum according to the input configuration. The fit configuration by now only requires a string of elements as input. FANO, NOISE, calibration, incident energy and angle are set to default values. The elements input in the configuration step must include all elements that may be present within the sample (excluding elements lighter than Z = 12). This method is slower and can yield greater overall errors when compared to `Simple` method, but it will perform better if overlapping of peaks if present. For an unknown sample `PyMcaFit` is preffered.

##### Pixel value
Kα and Kβ net areas being sucessfully calculated, the summed area is then attributed to the pixel in the same way as done for the density map. After iterating over the whole batch of spectra, the 2D-matrix of element J is done. 
Nevertheless, the matrix still needs to be normalized. This must be done in respect to the maximum peak area found within the batch of spectra, in a way each element will be displayed proportionally to the element of greater abundance.

The normalization process follows:
* Stack all spectra and sum them;
* Run the stacked spectra and look for the highest peak;
* Store the energy associated to the most abundant element;
* Run over every spectra calculating the area for the most abundant element;
* Store the highest detected area for the most abundant element;
* Divide the 2D-matrix for the highest detected area value.

Last, the normalized 2D-matrix containing the net areas of element J K-Lines (or L-Lines as aforementioned) must be transformed into a RGBA image. The process follows the same recipe as the one used for the density map with the only difference that this time the element must receive a color so it can be distinguished from a second element in case it has been chosen to be generated as well.

### Heightmap
