# XISMuS Tutorial
Here we will guide you, step-by-step, on how to use XISMuS.<br>
You will learn:<br>
<br>
**X [Quick-Guide](#quick)<br>**
<br>
**1.  [How to load a sample](#loadingSample)<br>**
**2.  [How to configure a sample](#configureSample)<br>**
**3.  [How to change the configuration](#reconfigure)<br>**
**4.  [How to verify the compiled data](#output)<br>**
**5.  [How to save the sample global image](#saveImage)**<br>
**6.  [How to verify the derived spectra](#derivedSpectra)<br>**
**7.  [How to map elements](#mapping)<br>**
**8.  [How to export the maps](#export)<br>**

## Getting started
This tutorial makes use of the Example Data provided with the distribution packages.
If your are running it from source, be sure to have some data you can use. The Example Data provided is proprietary, 
so please do not (re)distribute it by other means other than the distribution packages provided in the 
**[release section](https://github.com/linssab/XISMuS/releases)** 
before prior communication or authorisation from the owners.<br>
___

## Loading Sample <a name="loadingSample"></a>

### Automatic detection
XISMuS automatically looks for *.mca files inside the **samples folder** and its first degree child directories. 
By default the sampels folder it set to ```../My Documents/XISMuS/Example Data```.<br>
When launching the software from a fresh start, the Example Data should be automatically identified. 
To change the samples folder, click on the ```"Toolbox"``` dropdown menu and then select "Change samples folder...".<br>
There are other ways to load your data, even if XISMuS does not recognize the spectra batch name structure. 
For that, please refer to the User Manual also available for download separately 
**[here](https://sourceforge.net/projects/xismus/files/XISMuS_User_Manual_2.4.0.pdf/download)**.<br>

### EDF and Hierarchical Data Format datasets
To load ***.edf** batches or ***.h5** files, click the corresponding option under the ```"Toolbox"``` dropdown menu.
For the *.edf batch, select all files from the batch. H5 files give you the option to avoid saving a datacube to disk,
saving space. This, however, limits the software functionalities and XISMuS will not save your progress as you use the
software. We highly reccomend you choose to create a datacube when working with *.h5 files. You can always erase the
datacube later by clicking the ```"Reset"``` button on the main panel.<br>

### Loading from the Samples panel
Every sample detected by the software (valid only for *.mca batches) will remain in the Samples panel, located on the right.
To compile one sample, that is, to read all spectra files and pack them into a datacube, simply double-click the name of the
sample in the Samples panel. The name of the sample is always inherited from the parent folder.<br>
In the image below you will see the Example Data, named as "Training Data 1" and "Training Data 2". Double-click any
of them to bring up the configuration panel.<br>
If you're loading data other than the Example Data provided, a dimension dialog will display instead; 
asking for the image dimensions. In this case, enter the values and hit "Return" to validate and proceed 
to the configuration panel. To close it and go back to the Main Panel, hit "Escape" on your keyboard.<br>

<p align="center">
    <a href="https://imgbb.com/"><img src="https://i.ibb.co/qxzBGzT/samples.png" alt="samples" border="0"></a>
</p>

___

## Configuring the sample <a name="configureSample"></a>
Configuring your sample is straightforward. 
There are few options to choose from the configuration panel as shown in the image below. 
All options are explained in more detail in the User Manual.<br>
Double-click one of the Example Datasets provided in the Samples panel on your right to bring up the configuration panel.
From the options available, we will focus on the following three:
**Background strip mode**, **Netpeak area method** and **Calibration**. 
<p align="center">
    <a href="https://imgbb.com/"><img src="https://i.ibb.co/8bmM8Xm/reconfig.png" alt="configuration-panel" border="0"></a>
</p>

___

**Background strip mode** will allow you to select the background estimation method (useful for high [signal-to-noise ratio](https://www.sciencedirect.com/topics/chemistry/signal-to-noise-ratio) data) and the latter will  allow you to select the peak searching method.<br> 
> **_NOTE:_**  If the background contained in your data can be disregarded, leave this option set to ```"None"```. 
The continuum contribution (background) is stored as another matrix in the datacube, hence it consumes as much disk space and memory as the data itself.

If you choose the **SNIPBG** method, it is possible to configure few parameters. If you ignore setting them or insert invalid values, the default values will be used: Sav-gol and clipping windows of 5, sav-gol order of 3 and 24  iterations. 
Further information on the SNIPBG method can be found in this 
**[reference](https://www.crcpress.com/Handbook-of-X-Ray-Spectrometry/Grieken-Markowicz/p/book/9780824706005)**.<br>
For now, leave this option to "SNIPBG".
___

From the options available within **Netpeak area method**, we advise checking the User Manual for a better understanding 
of their functioning and main differences.<br>
In short, *simple_roi* is the fastest imaging mode, as it just slices the datacube. It is the best approach for a first
understanding of your dataset. *Auto_roi*, on the other hand, can be considerably slower. It works in a very similar way,
but it verifies each and every spectrum in the datacube for the existence of a peak and (re)adjusts the peak center; 
while *simple_roi* simply slices the data in the same energy/channel interval.<br>
*Auto-wizard* and *fit_approx* requires that **xraylib** is installed. The first method is completely automatic; 
it identifies possible elements within the dataset and fits each and every spectrum with a gaussian approximation. 
This is the best method for separating overlapping peaks, it is also the slowest method. *Fit-approx* is the most 
advanced option, and it requires you set some parameters beforehand, from within the ```Image Analyzer``` panel.<br>
We will leave the *simple_roi* option selected for now.
___

The **calibration** field provides you with 3 options: *from_source*, *simple*, and *advanced*.<br>
If your data has some built-in calibration values (energy-channel pairs), check the first option. 
If the parameters cannot be retrieved with the program, then select *simple* or *advanced* methods.<br>
The *simple* option allows you to enter manually the enery-channel pairs, while the *advanced* option will 
randomly sample 200 spectra from the dataset and show you their sum, so you can click the identified 
peaks and assign energy values to them.<br>
In our case, we will select the *from_source* option.<br>

When ready, click "Save" and wait for the data to be compiled.<br>
At the end of the process, an image should appear at the Front Panel and the subpanels on the top- and bottom-right parts should be updated.<br>
___

## Changing compiled sample configuration <a name="reconfigure"></a>
If calculating the netpeak area for both alpha and beta macros is getting confusing, not needed any longer,
or if the output images are too chunky or too smooth, or even if the images are presenting too many dead pixels, 
you can change/tweak few configuration parameters to what is more suitable. This can be done by clicking the small 
rubik's cube icon in the bottom-right part of the front panel.<br>
You will immediately notice there is one extra option not available in the configuration phase: *Enhance image*.
This option is usually toggled by default, it affects the exported images and the density map zoom image 
(when clicking the magnifier icon in the bottom-left panel). 
Leaving it ON will create smoother images, while leaving it OFF will produce chunkier images. For now, leave this option toggled.<br>
The other options you are already familiar with, so change them if needed.<br>

The background/continuum estimation method cannot be changed. In any case, it is possible to **remove** 
the background data by right-clicking the sample name in the Samples panel. 
To use another background estimation method, you need to recompile the data. 
This can be done by resetting the sample and double-clicking the sample's name after.<br>
___

## Verifying and accessing the compiled data <a name="output"></a>
You can direclty access the corresponding output folder of each sample through the "Samples" panel 
(as shown [here](#loadingSample)).<br>
Rick-click your sample name to bring up the pop-up menu and click on ```"open output folder"```. 
In the new explorer window you will notice that there are already some files in there, the compiled *.cube file 
and the sum spectrum of your sample in *.txt and *.mca formats.<br>
Calculated images, fitted spectra plots, and other data generated by XISMuS will be stored in these folders.<br>
___

## Save sample image <a name="saveImage"></a>
Few extra option are available by right-clicking the sample image (densitymap) shown in the lower-left panel. 
As shown in the image below.

<p align="center">
    <a href="https://imgbb.com/"><img src="https://i.ibb.co/hfjTkpF/Captura-de-tela-2022-03-22-152339.png" alt="Right-click panel" border="0" height="auto" width="250" display="flex"></a>
</p>

To save the image shown in the panel, simple select ```"Save density map as..."``` option. 
The "Enhanced" version of the image, if the "Enchance image?" option is toggled in the 
[Re-configure panel](#reconfigure), can be viewed by clicking the magnifier icon
in the lower-left corner of the panel. 
To save this version of the image, click the floppy disk icon.<br>
Try now saving the densitymap by right-clicking the image and then try saving the enhanced version of the image
accessible through the magnifier icon.<br>
___

## Derived spectra <a name="derivedSpectra"></a>
The first thing to start analyzing your data is accessing the derived spectra. 
They will give you a first hint on what chemical elements may be present in the entirety of the sample. 
The derived spectra can be accessed under the ```"Toolbox"``` dropdown menu. 
You will notice there are 3 options available: Summation, MPS and combined. 
For now, click on ```"Summation"``` to bring up the summation spectrum. 
> **_NOTE:_** The summation spectrum is also available in the output folder as a *.txt and *.mca files.<br>

<p align="center">
    <a href="https://ibb.co/JrnCxdp"><img src="https://i.ibb.co/7rvbgzp/combined.png" alt="combined" border="0"></a>
</p>

In the plot window you can pan, zoom and save the plot image by using the toolbar in the bottom.<br>
<ins>You can keep this plot window open when mapping elements!</ins> If you are using *simple_roi*, *auto_roi*, or *auto_wizard* methods, 
the elements selected will be displayed in the derived spectrum window. 
This is a very handy way to check if the elements you are selecting in the Periodic Table make sense.<br>
___

## Mapping elements <a name="mapping"></a>
You must have a compiled sample in memory in order to start mapping any chemical element. 
If there is no sample loaded, double-click any of the Example Datasets provided in the Samples panel. 
If you followed the previous steps, they should be compiled by now; if not, 
the [configuration panel](#configureSample) will be broguht instead.<br>
You know a sample is compiled and loaded when there is an image in the bottom-left frame in the front panel 
or by checking the status bar in the very bottom of the front panel.<br>
Now click on ```"Map elements"``` button (atom icon).
This will bring up the periodic table of elements if you are using *simple_roi* or *auto_roi* methods.<br>
Now simply select the elements you want to look for and hit ```"Map selected elements!"```. 
If you have any derived spectrum plot open, the theoretical position of the selected element's peaks will show 
up in the plot, so you can verify its presence before mapping them.<br>
Depending on the method chosen in the configuration step and the software settings, the mapping operation may 
take a while.<br>

The calculated regions can be checked through the ```"Toolbox"``` dropdown menu by clicking 
```"Verify calculated ROI"```. The created elemental maps can be viewed by accessing the "Image Analyzer" window.<br>
Try mapping Fe, Cu, Ag and Au elements.<br>
___

### Mapping a custom energy range
You may have notice a button labelled ```"Custom"``` in the periodic table of elements. 
Instead of looking for elements only, it may be useful to look for a specific energy range instead. 
To do so, simply type the lower and higher limits and toggle the "Custom" button to enable it. 
If any derived spectrum plot is open, the lower and higher limits will be shown as well.<br>
___

## Exporting images <a name="export"></a>
Whenever a chemical element is mapped, the raw images are automatically saved under the [output folder](#output).
You can merge and filter them in the ```"Image Analyzer"``` window.
Threshold filters (high-pass or low-pass) can be toggled. In addition, it is possible to use an iterative smooth
filter. The filtering level is adjusted by sliding the bars. To adjust the threshold bars, the filter option must be first
toggled. Each image shown, left and right, can be filtered separately.<br>
It is also possible to add or subtract one image from another. 
In these operations, the filter levels toggled will be applied!<br>

To export the images displayed in the screen, click ```"Export"```. The export dialogue will show up:<br>

<p align="center">
    <a href="https://imgbb.com/"><img src="https://i.ibb.co/Q7gNhbQ/export-dialogue.png" alt="export-dialogue" border="0" width=300 title="Export Dialogue"></a><br>
</p>

To export the image on the left or right as they are shown, click "1" or "2" respectively. To merge both images into one, click "Merge".
It is also possible to export each image shown in Image Analyzer by right-clicking the corresponding image.

## Quick guide <a name="quick"></a>
This section will guide you from loading the Example Data provided to exporting a combined map. Follow the instructions below:<br>
+ Double-click "Training Data 2";<br>
+ Input the following configuration parameters:<br>
    - Background strip mode: SNIPBG<br>
    - Calibration: from_source<br>
    - Netpeak area method: auto_roi<br>
    - Calculate ratios: No<br>
    - Before proceeding, click "Set BG";<br>
+ Input the following parameters:<br>
    - Sav_gol window: 5<br>
    - Sav-gol order: 3<br>
    - Clipping window: 5<br>
    - Number of iterations: 24<br>
    - Click "Save"<br>
    - Click "Save" again in the previous configuration panel;<br>
+ Open the "Toolbox" dropdown menu, navigate to "Derived spectra" and click "Summation";<br>
+ Back at the front panel, click "Map elements";<br>
+ Select "Cu", "Ag" and "Au". Notice the lines that appear in the derived spectrum plot window. Click "Map selected elements!" and wait for the data to be compiled;<br>
+ Back at the front panel, click "Image Analyzer";<br>
+ Select the elements you wish in the uppermost dropdown menus;<br>
+ Filter the images if needed by activating and dragging the slider in the bottom part of the window. When ready, click "Export";<br>
+ To export the individual images shown in the left and right panels, click "1" or "2" respectively. To merge them into an RGBA image, click "merge".<br>
