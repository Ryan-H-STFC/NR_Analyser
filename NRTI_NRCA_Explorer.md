Module NRTI_NRCA_Explorer
=========================

Functions
---------
    
`main() ‑> None`
:   

Classes
-------

`ExplorerGUI()`
:   ``ExlorerGUI``
    --------------
    Class responsible for creating and manipulating the GUI, used in selecting and graphing the data of elements or
    isotopes within the NRTI/NRCA Database.
    
    Initialisator for ExplorerGUI class

    ### Ancestors (in MRO)

    * PyQt6.QtWidgets.QWidget
    * PyQt6.QtCore.QObject
    * PyQt6.sip.wrapper
    * PyQt6.QtGui.QPaintDevice
    * PyQt6.sip.simplewrapper

    ### Methods

    `addTableData(self, reset=False)`
    :   ``addTableData``
        ----------------
        Concatenates the selected spectras table data to the other plotted spectras adding a toggle drop-down title row.
        
        Args:
            - ``reset`` (bool, optional): Whether to default back to the current state of the table. Defaults to False.

    `adjustCanvas(self) ‑> None`
    :   ``adjustCanvas``
        ----------------
        Apply tight layout to figure.

    `clear(self) ‑> None`
    :   ``clear``
        ---------
        Function will empty all data from the table, all graphs from the plots, along with resetting all data associated
        the table or plot and disables relevent controls.

    `createCompound(self) ‑> None`
    :   ``createCompound``
        ------------------
        Opens a dialog for users to create compounds from weighted combinations of varying elements,
        this calculates and saves the graph data to a file for reuse.

    `displayData(self) ‑> None`
    :   ``displayData``
        ---------------
        Will display relevant peak information in the table for the selection made (self.selectionName).
        Once a select is made, the relevant controls are enabled.

    `dragEnterEvent(self, event: QtGui.QDragEnterEvent) ‑> None`
    :   ``dragEnterEvent``
        ------------------
        Handles file drag enter event and verification
        
        Args:
            ``event`` (QDragEnterEvent): Event triggerd on mouse dragging into the window.

    `drawAnnotations(self, element: SpectraData) ‑> None`
    :   ``drawAnnotations``
        -------------------
        Will plot each numbered annotation in the order of Integral or Peak Width.
        
        Args:
            - ``element`` (SpectraData): The data for the element your annotating

    `dropEvent(self, event: QtGui.QDropEvent) ‑> None`
    :   ``dropEvent``
        -------------
        Handles the drop event and calls to plot each data file
        
        Args:
            ``event`` (QDropEvent): PyQtEvent

    `editDistribution(self) ‑> None`
    :   ``editDistribution``
        --------------------
        Opens a dialog window with options to alter the natural abundence of elements and compounds
        updating the graph data of any relevant plots.

    `editMaxPeaks(self) ‑> None`
    :   ``editMaxPeaks``
        ----------------
        Opens a Dialog window for inputting the max peak label quanitity for a selected graph, drawing
        the relevant annotations.

    `editPeakLimits(self) ‑> None`
    :   ``editPeakLimits``
        ------------------
        Edit Peaks opens a dialog window to alter limits of integration for peaks of the selected
        element, recaluating the integral and peak widths to place into the table.

    `editThresholdLimit(self) ‑> None`
    :   ``editThresholdLimit``
        ----------------------
        Creates a GUI to alter the threshold value for a selected graph, recomputing maximas and
        drawing the relevant annotations

    `energyToTOF(self, xData: list[float], length: float) ‑> list[float]`
    :   ``energyToTOF``
        ---------------
        Maps all X Values in the given array from energy to TOF
        
        Args:
            - ``xData`` (list[float]): List of the substances x-coords of its graph data
        
            - ``length`` (float): Constant value associated to whether the element data is with repsect to n-g or n-tot
        
        Returns:
            ``list[float]``: Mapped x-coords

    `getPeaks(self) ‑> None`
    :   ``getPeaks``
        ------------
        Ask the user for which function to plot the maxima or minima of which element
        then calls the respective function on that element

    `gridLineOptions(self)`
    :   ``gridLineOptions``
        -------------------
        Opens a dialog with settings related to the gridlines of the canvas.
        Options include: Which axis to plot gridlines for, which type; major, minor or both ticks, as well as color.

    `hideGraph(self, event) ‑> None`
    :   ``hideGraph``
        -------------
        Function to show or hide the selected graph by clicking the legend.
        
        Args:
            - ``event`` (pick_event): event on clicking a graphs legend

    `importData(self) ‑> None`
    :   ``importData``
        --------------
        Allows user to select a file on their computer to open and analyse.

    `initUI(self) ‑> None`
    :   ``initUI``
        ----------
        Creates the UI.

    `onPeakOrderChange(self) ‑> None`
    :   ``onPeakOrderChange``
        ---------------------
        Handles changing the order of peaks then redrawing the annotations.

    `plot(self, spectraData: SpectraData, filepath: str = None, imported: bool = False, name: str = None) ‑> None`
    :   ``plot``
        --------
        Will plot the inputted spectraData's spectra to the canvas.
        
        Args:
            - ``spectraData`` (SpectraData): The spectraData to be plotted
        
            - ``filepath`` (str, optional): Filepath of imported spectra. Defaults to None.
        
            - ``imported`` (bool, optional): Whether or not the data has been imported. Defaults to False.
        
            - ``name`` (str, optional): The name of the imported spectra. Defaults to None.

    `plotPeakWindow(self, index: QModelIndex) ‑> None`
    :   ``plotPeakWindow``
        ------------------
        Opens a window displaying the graph about the selected peak within the bounds of integration
        as well as data specific to the peak.
        
        Args:
            index (QModelIndex): Index object for the selected cell.

    `plotSelectionProxy(self, index, comboboxName)`
    :   ``plotSelectionProxy``
        ----------------------
        Handles whether to selection made is from the compound list or not.
        
        Args:
            - index (int): Index of selection given from PyQtSignal.
            - comboboxName (str): Identifier of combobox which made the signal.

    `plottingPD(self, spectraData: SpectraData, isMax: bool) ‑> None`
    :   ``plottingPD``
        --------------
        Takes plots the maximas or minimas of the inputted ``spectraData`` based on ``isMax``
        
        Args:
            - ``spectraData`` (SpectraData): SpectraData Class specifying the element
        
            - ``isMax`` (bool): Maxima if True else Minima

    `resetTableProxy(self, combobox) ‑> None`
    :   ``resetTableProxy``
        -------------------
        Handles setting the data in the table, either displaying the data from a single selection, or returning to the
        previous state of the table.
        
        Args:
            - combobox (QComboBox): The Combobox from which the selection was made.

    `resizeEvent(self, event: QtGui.QResizeEvent) ‑> None`
    :   ``resizeEvent``
        ---------------
        On resize of connected widget event handler.
        
        Args:
            event (QtGui.QResizeEvent): Event triggered on resizing.
        
        Returns:
            ``None``

    `resized(...)`
    :   pyqtSignal(*types, name: str = ..., revision: int = ..., arguments: Sequence = ...) -> PYQT_SIGNAL
        
        types is normally a sequence of individual types.  Each type is either a
        type object or a string that is the name of a C++ type.  Alternatively
        each type could itself be a sequence of types each describing a different
        overloaded signal.
        name is the optional C++ name of the signal.  If it is not specified then
        the name of the class attribute that is bound to the signal is used.
        revision is the optional revision of the signal that is exported to QML.
        If it is not specified then 0 is used.
        arguments is the optional sequence of the names of the signal's arguments.

    `showTableData(self)`
    :   ``showTableData``
        -----------------
        Read and display the selected substances data within the table.

    `toggleAnnotations(self) ‑> None`
    :   ``toggleAnnotations``
        ---------------------
        Toggles visibility of all peak annotations globally.

    `toggleBtnControls(self, enableAll: bool = False, plotEnergyBtn: bool = False, plotToFBtn: bool = False, clearBtn: bool = False, pdBtn: bool = False) ‑> None`
    :   ``toggleBtnControls``
        ---------------------
        Enables and disables the buttons controls, thus only allowing its use when required. ``enableAll`` is done
        before any kwargs have an effect on the buttons. ``enableAll`` defaults to False, True will enable all buttons
        regardless of other kwargs.
        
        This way you can disable all buttons then make changes to specific buttons.
        
        Args:
            - ``enableAll`` (bool): Boolean to enable/disable (True/False) all the buttons controls.
        
            - ``plotEnergyBtn`` (bool): Boolean to enable/disable (True/False) Plot Energy button.
        
            - ``plotToFBtn`` (bool): Boolean to enable/disable (True/False) Plot ToF button.
        
            - ``plotEnergyBtn`` (bool): Boolean to enable/disable (True/False) Plot Energy button.
        
            - ``clearBtn`` (bool): Boolean to enable/disable (True/False) Plot Energy button.
        
            - ``pdBtn`` (bool): Boolean to enable/disable (True/False) Peak Detection button.

    `toggleCheckboxControls(self, enableAll: bool, gridlines: bool = False, peakLimit: bool = False, hidePeakLabels: bool = False) ‑> None`
    :   ``toggleCheckboxControls``
        --------------------------
        Enables and disables the checkboxes controls, thus only allowing its use when required. ``enableAll`` is done
        before any kwargs have an effect on the checkboxes. ``enableAll`` defaults to False, True will enable all
        checkboxes regardless of other kwargs.
        
        This way you can disable all checkboxes then make changes to specific checkboxes.
        
        Args:
            - ``enableAll`` (bool): Boolean to enable/disable (True/False) all the buttons controls.
        
            - ``gridlines`` (bool): Boolean to enable/disable (True/False) Plot Energy button.
        
            - ``peakLimit`` (bool): Boolean to enable/disable (True/False) Plot ToF button.
        
            - ``hidePeakLabels`` (bool): Boolean to enable/disable (True/False) Plot Energy button.

    `toggleGridlines(self, visible: bool, which: "Literal['major', 'minor', 'both']" = 'major', axis: "Literal['both', 'x', 'y']" = 'both', color='#444') ‑> None`
    :   ``toggleGridlines``
        -------------------
        Will toggle visibility of the gridlines on the axis which is currently shown.
        
        Args:
            - ``visible`` (bool): Whether or not gridlines should be shown.
        
            - ``which`` (Literal["major", "minor", "both"], optional):
            Whether to show major, minor or both gridline types. Defaults to "major".
        
            - ``axis`` (Literal["both", "x", "y"], optional):
            Whether or not to show gridlines on x, y, or both. Defaults to "both".
        
            - ``color`` (str, optional): Gridline Color. Defaults to "#444".

    `toggleThreshold(self) ‑> None`
    :   ``toggleThreshold``
        -------------------
        Plots the threshold line for each plotted element at their respective limits.

    `updateGuiData(self, tof: bool = False, filepath: str = None, imported: bool = False, name: str = None, distAltered: bool = False) ‑> None`
    :   ``updateGuiData``
        -----------------
        Will initialise the new element with its peak and graph data, updating the table and plot.
        Handles updates to isotopic distribution.
        Args:
            - ``tof`` (bool, optional): Whether to graph for tof or not. Defaults to False.
        
            - ``filepath`` (string, optional): Filepath for the selection to graph . Defaults to None.
        
            - ``imported`` (bool, optional): Whether the selection imported. Defaults to False.
        
            - ``name`` (string, optional): The name of the imported selection. Defaults to None.
        
            - ``distAltered`` (bool, optional): Whether or not the function is plotted for altered isotope
            distributions. Defaults to False.

    `updateLegend(self)`
    :   ``updateLegend``
        ----------------
        Will update the legend to contain all currently plotted spectras and connect the 'pick_event'
        to each legend line to ``hideGraph``.

    `viewDarkStyle(self) ‑> None`
    :   ``viewDarkStyle``
        -----------------
        Applies the dark theme to the GUI.

    `viewHighContrastStyle(self) ‑> None`
    :   ``viewHighContrastStyle``
        -------------------------
        Applies the high contrast theme to the GUI.

    `viewLightStyle(self) ‑> None`
    :   ``viewLightStyle``
        ------------------
        Applies the light theme to the GUI.