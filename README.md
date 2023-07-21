# NRTI/NRCA-Viewing-Database


## **Installing and Starting the Application**

Download the repository. The following python packages are required for the script to run:
* matplotlib
* numppy
* os
* shutil
* PyQt5

Download the repository and save it in a suitable filepath on your computer. Please keep the directory paths the same else the program will not run. You will be asked for the filepath upon running the application.
You will also be asked for the filepath to the data folder from the most recent version of the NRCA code. This can be found on the ndw1901 computer at 'NRCA/Rehana/Latest_NRCA_Code/data'.

Open in PyCharm or the interpreter of your choosing and run the script.

## **Purpose**

It takes the data stored in the NRCA analysis code and provides the user with a physical interface to analyse the data. This allows the user to plot multiple graphs and analyse spectra via the program. Note: It is directly linked to the data directory used to store information in the NRCA database and so is updated as data files are added to the database. However, peak information is not currently automatically updated so any new data files will have no peak information for the user to see unless manually updated.

## **Overview of GUI**


![image](https://user-images.githubusercontent.com/109808872/210983210-82bace49-ad6a-44ef-a0b8-0d61b5f87797.png)


## **Features**

* Import and plot data
* Compare spectra with the ability to hide and show different spectra within the plot
* Provide automated peak detection feature for quick analysis upon importing of data or selecting data
* Edit peak limits
* Provide further information about a singular peak selected from a spectrum
* Save and export plots
* Be accessible and straightforward in installation and use


**Note** : You cannot alter limits or any data within this program.

## **Bugs to be fixed soon**

* Adding mulitple of the same graph.
* Limiting number of graphs to avoid crashing.
* Toggling Peak Line throws unnecessary error. 'checked' variable may be the issue.
* Disable buttons which require a selected isotope, to avoid 'no graph selected' errors.
* Peak Detection - Do not allow multiple reads for peak data if it is already displayed.

## **Improvements Coming Soon**

* Put code into MVP (Model, View, Presenter) format
* Allow Sorting by any column in table.
* Simplify entering filepath, simple splash window asking to select the relavent folders.
* Add search for isotope selection, and scroll bar.

## **Accessibility**

A new colour scheme has been implemented than that seen in the picture above to provide high-contrast for those who are perhaps colour blind.
