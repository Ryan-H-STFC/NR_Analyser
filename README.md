# NR Analyser

![Tests](https://github.com/Ryan-H-STFC/NRTI-NRCA_Explorer/actions/workflows/test.yml/badge.svg)

## **Installing and Starting the Application**

Download the repository. The following python packages are required for the script to run:
* matplotlib
* numpy
* pandas
* scipy
* PyQt6

Download the repository and save it in a suitable filepath on your computer. Please keep the directory paths the same else the program will not run. You will be asked for the filepath upon running the application.
You will also be asked for the filepath to the data folder from the most recent version of the NRCA code. This can be found on the ndw1901 computer at 'NRCA/Rehana/Latest_NRCA_Code/data'.

Open in PyCharm or the interpreter of your choosing and run the script.

## **Purpose**

It takes the data stored in the NRCA analysis code and provides the user with a physical interface to analyse the data. This allows the user to plot multiple graphs and analyse spectra via the program. Note: It is directly linked to the data directory used to store information in the NRCA database and so is updated as data files are added to the database. However, peak information is not currently automatically updated so any new data files will have no peak information for the user to see unless manually updated.

## **Overview of GUI**

![NTRI_NRCA_empty](https://github.com/Ryan-H-STFC/NRTI-NRCA-Viewing-Database/assets/139995913/d2209566-3280-49b3-a4bb-8b2a4591ca00)
![NTRI_NRCA_filled](https://github.com/Ryan-H-STFC/NRTI-NRCA-Viewing-Database/assets/139995913/d0a7a709-b6db-49d7-a9fb-7adcce2667c3)

## **Features**

* Import and plot data
* Compare spectra with the ability to hide and show different spectra within the plot
* Provide automated peak detection feature for quick analysis upon importing of data or selecting data
* Edit peak limits
* Provide further information about a singular peak selected from a spectrum
* Save and export plots
* Be accessible and straightforward in installation and use
* Simple search for element selection

Peak Integration Limit Algorithm:
- More accurate data collection
- Allowing for experiemental data to be analysed throughtout the program.
- Changing threshold, natural abundance of elements, creating compounds, etc, will all be able to be analysed and data updated accordingly.
  
**Note** : You cannot alter limits or any data within this program.

## **Bugs to be fixed soon**

## **Improvements Coming Soon**

## **Accessibility**

A new colour schemes has been implemented than that seen in the picture above to provide high-contrast for those who are perhaps colour blind.
