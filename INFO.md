Here you can find information on how the code actually handles the data and how it calculates certain values.
To begin with, keep in mind that the input data are always spectra files. These files can contain information such as the _live time_, _calibration data_ and most importantly: our _data_.
_SpecRead.py_, as the name suggests, handles the reading process. It extracts the information contained in the spectra files.
_SpecMath.py_ contains a series of function to manipulate the data.

## Mapping
This is the core of the code. This file contains the routines that will calculate and generate the elemental map(s) from the spectra files. So far it can create a single-element map, multi-element map (up to two elements), density map and ratio map. How each one is calculated and generated will be explained in the following paragraphs. Further information regarding the **usage** is given in _REAMDME.md_ file.

#### Density map
This routine creates a 2D-matrix, where each element represents the total of _counts_ contained in the pixel-associated spectrum. For a better understandment let's continue with an example: Suppose our data is composed of 600 spectra files representing a scanned area of 24x25 pixels. Assuming the _acquisition time_ of each spectrum is the same, the counts will therefore be direclty proportional to the density of the measured spot.

In order to generate a true image, the matrix must be transformed into a RGBA format. The first step is to normalize our 2D-matrix of total counts, dividing each element for the maximum value of the matrix and then multiplying by 255. The next steps are conducted in a _colorizing_ function, that will create a RGBA-style matrix turning each pixel in a vector with 4 elements. 
Since we are creating a density map, a grayscale image is enough for visual interpretation (the _colorizing_ function also handles the elemental maps, which contain colors. Therefore, it was written in a more general way). 
Finally, the grayscale image is produced by associating the pixel-value of our 2D-matrix to each color channel, R, G and B. A is maintained at the value of 255.

#### Element maps
Differently from the previous map, the elemental maps must compute the counts contained in a very specific interval of energy (or channels). Due to the statistical process involved in the acquisition of the data and the count-to-charge ratio, the peaks observed for each XRF line are represented by a gaussian distribution instead of a discrete line.
The typical XRF line energies, jump ration, fluorescence yields, cross-sections and more for each chemical element are calculated and available in open-source libraries as well as in printed XRF handbooks.
The data contained in each spectrum represents the counts per channel. Since the calculated energies for the XRF lines are given in KeV, a calibration curve must be calculated to "convert" the channels to energies.

The calibration curve is calculated following the linear regression method. The parameters are extracted from _config.cfg_ file, which also contains the dimension of the map to be created in linex x rows.

The function that creates the elemental map takes the chemical elements symbols as strings as input, e.g. `mapfunction('Au','Ag')`.
It is up to the code to determine the region of interest (ROI) that represents each of chemical elements the user wants to be found. This is made by reading the energies library and accessing the theoretical value of line x1 for element x. So far the code only takes into consideration the most probable line, Κα or Lα according to the element. If the excitation current used during the acquisition of the spectra was of 30 Kv, there is no way one could observe the K-lines of mercury, for example in the obtained spectra. 

With the peak position for line x1 of element x defined, the code must estimate an interval to compute the area. Adding to the situation, there is the fact the calibration isn't always perfect, even with a correlation coefficient of 1, creating slight changes in the observed peak position. In this case, the observed peak of Au-Lα line for example, could be somewhere between 9.611 and 9.811 KeV. This interval is a subject of a greater discussion and involves the resolution of the detector and statistical treatment of data. For the time being, an interval of 200 eV is set. This value is reasonable and does the job well.

To compute the interval, the code first calculates the width of peak throught an FWHM approach. Since the peaks can be approximated to a gaussian distribution, their width can be estimated. The FWHM is equivalent to 2.3548 * σ, where σ is given by the following equation proposed by Solè et al. 2007:

<img src="https://latex.codecogs.com/gif.latex?\sigma^{2}&space;=&space;\left&space;(\frac{NOISE}{2.3548}&space;\right&space;)^{2}&space;&plus;&space;3.85&space;*&space;FANO&space;*&space;E_{j}" title="\sigma^{2} = \left (\frac{NOISE}{2.3548} \right )^{2} + 3.85 * FANO * E_{j}" />

Ej is the peak position, NOISE is the electronic contribution to the peak width, FANO is the fano factor and 3.85 is the energy required to produce an electron-hole pair in silicon.

The code will verify if the observed peak position matches the theoretical value in the range from (Ej - FWHM) to (Ej + FWHM). This is done by verifying the maximum y value in this range. If max y corresponds to the theoretical peak position, the code calculates the peak area corresponding to 2 * FWHM, if not, and if the x value associated to y max differs up to +- 60 eV from the theoretical one, the code shifts the x1 line value for element x to the new x and calculates the peak area. Keep in mind that **by now no background subtration method has been implemented!**

The calculated area is then attributed to the pixel in the same way as for the density map. After iterating over the whole batch of spectra, the 2D-matrix of element x is done. Nevertheless, this matrix needs to be normalized. This normalization must be done in respect to the maximum peak area found in the batch of spectra, in a way each element will be displayed proportionally to the element in greater abundance.

The normalization process follows:
* Stack all spectra and sum them;
* Run the stacked spectra and look for the highest peak;
* Store the energy associated to the most abundant element;
* Run over every spectra calculating the area for the most abundant element;
* Store the highest detected area for the most abundant element;
* Divide the 2D-matrix for the highest detected area value.

Last, the normalized 2D-matrix containing the areas of the x1 energy peaks of element x must be transformed into a RGBA image. The process is the same as the one used for the density map with the only difference that this time the element must receive a color so it can be distinguished from a second element in case it has been chosen to be generated as well.

If a _multi-element_ map is chosen, the process iterates over for the second element. With both RGBA images, now each image containing the peak areas for line x1 of element x and y1 for element y together with the color of each element, respectively, the program must overlay both images.
By now the overlaying is made with the use of cv2 library.
