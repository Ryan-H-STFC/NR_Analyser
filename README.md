# NR Analyser

![Tests](https://github.com/Ryan-H-STFC/NRTI-NRCA_Explorer/actions/workflows/test.yml/badge.svg)

## **Installing and Starting the Application**

Open the releases tab on this repository and download the latest edition of the program.

or,

Download this repository into your chosen IDE and run from the 'NR Analyser.py' file.

## **Purpose**

Provides a GUI interface to plot and analyse data taken from the ENDF/B-VIII database. Both n-g the gamma emission and n-tot total cross section of neutron capture and emission, are available and built into this program, the user can import x-y data from experiments and use all the same features.


## **Overview of GUI**

![NTRI_NRCA_empty](https://github.com/Ryan-H-STFC/NRTI-NRCA-Viewing-Database/assets/139995913/d2209566-3280-49b3-a4bb-8b2a4591ca00)
![NTRI_NRCA_filled](https://github.com/Ryan-H-STFC/NRTI-NRCA-Viewing-Database/assets/139995913/d0a7a709-b6db-49d7-a9fb-7adcce2667c3)

## **Features**

* Import and plot data
* Provide automated peak detection feature for quick analysis upon importing of data or selecting data
* Edit peak limits invidually or choose from a blanket algorithm using nearest zero derivative, or elbow point (recommended).
* Provide further information about a singular peak selected from a spectrum
* Create compounds of varying compositions
* Save and export data from plots
* Simple search for element or isotope
* Periodic table menu to select the isotope or element of your choice
* Changing the natural compositions of elements, and created compounds.

Peak Integration Limit Algorithm:

Using either the nearest zero derivative or, by default, the elbow point to find suitable limits of integration
- Allowing for experiemental data to be analysed throughtout the program.
- Changing threshold, natural abundance of elements, creating compounds, etc, can all be analysed and data updated accordingly.
  
## **Bugs to be fixed soon**

Check the issues tab, make note on that tab if you have any bugs or ideas.

## **Improvements Coming Soon**

* Improved performance with data calculations, large calculations may take up to a few minutes on slow machines.
  
## **Accessibility**

A new colour schemes has been implemented than that seen in the picture above to provide high-contrast for those who are perhaps colour blind or otherwise visually impaired.
