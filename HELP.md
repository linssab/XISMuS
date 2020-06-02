# XISMuS Tutorial
Here we will guide you, step-by-step on how to use XISMuS.<br>
You will learn:<br>
<br>
**X [Quick-Guide](#quick)<br>**
<br>
**1.  [How to load a sample](#loadingSample)<br>**
**2.  [How to configure a sample](#configureSample)<br>**
**3.  [How to change the configuration](#reconfigure)<br>**
**4.  [How to verify the compiled data](#output)<br>**
**5.  [How to verify the derived spectra](#derivedSpectra)<br>**
**6.  [How to map elements](#mapping)<br>**
**7.  [How to export the maps](#export)<br>**

## Getting started
This tutorial makes use of the Example Data provided with the distribution packages. If your are running it from source, be sure to have some data at hand. The data provided is porprietary, so please do not distribute it by other means other than the distribution packages provided in the **[release section](https://github.com/linssab/XISMuS/releases)** before prior communication.<br>

## Loading Sample <a name="loadingSample"></a>

#### Automatic detection
XISMuS automatically looks for *.mca and *.txt files inside the **samples folder**. By default, it is "../My Documents/XISMuS/Example Data". When launching it from a fresh start, the Example Data should be automatically identified. If, not, click on the "Toolbox" dropdown menu and select "Change samples folder...", this will change the default lookup folder. There are other ways to load your data, even if XISMuS doesn't recognize the spectra name structure. For that, please refer to the User Manual also available for download separately **[here](https://mega.nz/file/Ebon0YhS#u6HiWwlbOa4AkEte6UxvEtB18btDiK97Au8xIToAToU)**.<br>

#### Selecting from list
To load a sample and compile it (configure and create its *.cube file), click on "Load Sample". The "Sample List" panel below should come up showing the two example data provided.<br>
Double click "Training Data 1" and the configurational panel will show up. If you're loading data other than the example data provided, a dimension dialog will display instead; asking for the image dimensions. In this case, enter the values and hit "Return" to validate and proceed to the configuration panel. To close it and go back to the main panel, hit "Escape"<br>
<a href="https://imgbb.com/"><img src="https://i.ibb.co/5cCTLWy/sample-list.png" alt="sample-list" border="0" height=250 title="Sample List"></a><a href="https://imgbb.com/"><img src="https://i.ibb.co/JxKb08x/dimension.png" alt="dimension" border="0" title="Dimension Prompt"></a><br>

## Configuring the sample <a name="configureSample"></a>
Configuring your sample is straightforward. There are few options to choose from the configuration panel as shown in the image below. All options are explained in more detail in the User Manual. For now, we'll focus in the basic options that most impact performance and results: **Background strip mode** and **Netpeak area method**. The former will allow you to select the background estimation method (useful for high [signal-to-noise ratio](https://www.sciencedirect.com/topics/chemistry/signal-to-noise-ratio) data) and the latter will  allow you to select the peak searching method.<br> 
From the options available in Netpeak area method, auto_roi is considerably slower as it verifies each spectrum for the existence of a peak, while simple_roi simply slices the data according to the element assigned. As always, refer to the User Manual for further information.<br>
<a href="https://imgbb.com/"><img src="https://i.ibb.co/26PqWjb/configuration-panel.png" alt="configuration-panel" border="0" title="Configuration Panel" height=250></a><br>
You can configure SNIPBG parameters, but failing to set new valid values or not setting them at all, will force the default values to be used, which are: Sav-gol and clipping windows of 5, sav-gol order of 3 and 24  iterations. Further information on the SNIPBG method can be found in this **[reference](https://www.crcpress.com/Handbook-of-X-Ray-Spectrometry/Grieken-Markowicz/p/book/9780824706005)**.<br>
When ready, click "Save" and wait for the data to be compiled.<br>
At the end of the process, an image should appear at the Front Panel and the subpanels on the top- and bottom-right parts should be updated.<br>

## Changing compiled sample configuration <a name="reconfigure"></a>
If calculating the netpeak area for both alpha and beta macros is getting confusing or is not needed any longer or if the output images are too chunky or too smooth, or even if the images are presenting too many dead pixels, you can change/tweak few configuration parameters to what is more suitable. This can be done by clicking the small rubik's cube icon in the bottom-right part of the front panel.<br>
You will immediately see some options that were not available in the configuration panel before. For now ignore thickratio option, it it only there to be used in the future updates with extended functionalities. As for the other option, "enhance", will change how the exported images look. Leaving it ON will create smoother images, while leaving it OFF will produce chunkier images.<br>
The other options you are already familiar with, so change them accordingly. Background estimation method cannot be changed unless you reset the sample by clicking the corresponding front panel button. After resetting the sample you'll have to recompile the data.<br>

## Verifying and accessing the compiled data <a name="output"></a>
After saving the configuration parameters, your sample must now be compiled. You can direclty access the corresponding output folder for that sample through the "Sample List" panel (as shown [here](#loadingSample)), by clicking the "Load Sample" button in the front panel.<br>
Rick-click your sample name to bring up the pop-up menu. Click on "open output folder". In the new explorer window you will notice that there are already some files in there, the compiled *.cube file and the sum spectrum of your sample in *.txt and *.mca formats.<br>
The sample image displayed in the bottom-left part of the front panel can be saved as a *.png file through the "Sample List" menu as well.<br>

## Derived spectra <a name="derivedSpectra"></a>
The first thing to start analyzing your data is accessing the derived spectra. They will give you a first hint of what chemical elements may be present in the entirety of the sample. The derived spectra can be accessed under the "Toolbox" dropdown menu. You will notice there are 3 options available: Summation, MPS and combined. For now, click on "Summation" to bring up the summation spectrum. <ins>Note: The summation spectrum is also available in the output folder as a *.txt and *.mca file.</ins><br>
<a href="https://imgbb.com/"><img src="https://i.ibb.co/t4xnDyT/Untitled.png" alt="Summation Plot" border="0" height=300 title="Derived spectrum (Summation)"></a><br>
In the plot window you can pan, zoom and save the plot image by using the toolbar in the bottom.<br>
Keep this plot window open when mapping elements!<br>

## Mapping elements <a name="mapping"></a>
You must have a compiled sample in memory in order to start mapping any chemical element. If there is no sample loaded, open the "Sample List" menu and double-click "Training Data 1", which should be compiled by now if you followed the previous steps. If not, the [configuration panel](#configureSample) will be broguht instead.<br>
You know a sample is compiled and loaded when there is an image in the bottom-left part of the front panel or by checking the status bar in the very bottom of the front panel.<br>
Now click on "Map elements" button. This will bring up the periodic table of elements. Simply select the elements you want to look for and hit "Map selected elements!". If you have any derived spectrum plot open, the theoretical position of the selected element's peaks will show up in the plot, so you can verify its presence before start mapping.<br>
Depending on the method chosen in the configuration step and the software settings, mapping operation may take a while.<br>
The calculated regions can be checked through the "Toolbox" dropdown menu by clicking "Verify calculated ROI". The created elemental maps can be viewed by accessing the "Image Analyzer" window.<br>
Try mapping Fe, Cu, Ag and Au elements.<br>
<br>
#### Mapping a custom energy range
You may have notice a button labelled "Custom" in the periodic table of elements. Instead of looking for elements only, it may be useful to look for a specific energy range instead. To do so, simply type the lower and higher limits and click the "Custom" button to enable it. If any derived spectrum plot is open, the lower and higher limits will be shown as well.<br>

## Exporting images <a name="export"></a>
Whenever a chemical element is mapped, the output images are automatically saved under the [output folder](#output). However, you can merge and filter them in the "Image Analyzer" window. There are few filters available, use them according to need. To export the images displayed in the screen, click "Export". The export dialogue will show up:<br>
<a href="https://imgbb.com/"><img src="https://i.ibb.co/Q7gNhbQ/export-dialogue.png" alt="export-dialogue" border="0" width=300 title="Export Dialogue"></a><br>
To export the image on the left or right as they are shown, click "1" or "2" respectively. To merge both images into one, click "Merge".

## Quick guide <a name="quick"></a>
This section will guide you from loading the Example Data provided to exporting a combined map. Follow the instructions below:<br>
+ Click on "Load Sample" located in the front panel;<br>
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
