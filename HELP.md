# XISMuS Tutorial
Here we will guide you, step-by-step on how to use XISMuS.<br>
You will learn:<br>
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
XISMuS automatically looks for *.mca and *.txt files inside the **samples folder**. By default, it is "../My Documents/XISMuS/Example Data". When launching it from a fresh start, the Example Data should be automatically identified. If, not, click on the "Toolbox" dropdown menu and select "Change samples folder...". There are other ways to load your data, even if XISMuS doesn't recognize the spectra name structure. For that, please refer to the User Manual also available for download separately **[here](https://mega.nz/#!UHRUEYYQ!7PeijTr0P63wUXZQJ9U1xAGyFaLE-8mpyvUEKX50EME)**.<br>
To load a sample and compile it (configure and create its *.cube file), click on "Load Sample". The panel below should come up showing the two example data provided.<br>
<br>
<a href="https://imgbb.com/"><img src="https://i.ibb.co/5cCTLWy/sample-list.png" alt="sample-list" border="0" height=250 title="Sample List"></a>
<br>
Double click "Training Data 1" and the configurational panel will show up. If you're loading data other than the example data provided, a dimension dialog will display instead; asking for the image dimensions. In this case, enter the values and hit "Return" to validate and proceed to the configuration panel. To close it and go back to the main panel, hit "Escape"<br>

## Configuring the sample <a name="configureSample"></a>
Configuring your sample is straightforward. There are few options to choose from the configuration panel as shown in the image below. All options are explained in more detail in the User Manual. For now, we'll focus in the basic options that most impact performance and results: **Background strip mode** and **Netpeak area method**. The former will allow you to select the background estimation method (useful for high [signal-to-noise ratio](https://www.sciencedirect.com/topics/chemistry/signal-to-noise-ratio) data) and the latter will  allow you to select the peak searching method.<br> 
From the options available in Netpeak area method, auto_roi is considerably slower as it verifies each spectrum for the existence of a peak, while simple_roi simply slices the data according to the element assigned. As always, refer to the User Manual for further information.<br>
<a href="https://imgbb.com/"><img src="https://i.ibb.co/26PqWjb/configuration-panel.png" alt="configuration-panel" border="0" title="Configuration Panel" height=250></a><br>
You can configure SNIPBG parameters, but failing to set new valid values or not setting them at all, will force the default values to be used, which are: Sav-gol and clipping windows of 5, sav-gol order of 3 and 24  iterations. Further information on the SNIPBG method can be found in this **[reference](https://www.crcpress.com/Handbook-of-X-Ray-Spectrometry/Grieken-Markowicz/p/book/9780824706005)**.<br>
When ready, click "Save" and wait for the data to be compiled.<br>
At the end of the process, an image should appear at the Front Panel and the subpanels on the top- and bottom-right parts should be updated.<br>

## Changing compiled sample configuration <a name="reconfigure"></a>

## Verifying and accessing the compiled data <a name="output"></a>

## Derived spectra <a name="derivedSpectra"></a>

## Mapping elements <a name="mapping"></a>

## Exporting images <a name="export"></a>

