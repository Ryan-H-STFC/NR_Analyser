from __future__ import annotations
import os
import sys
import shutil
import matplotlib.rcsetup
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import OrderedDict
from itertools import islice
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
)
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar
)
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QRegExp

from PyQt5.QtGui import QCursor, QRegExpValidator, QIcon
from PyQt5.QtWidgets import (
    QAction,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QDockWidget,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSplitter,
    QTableView,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)

from element.ElementDataStructure import ElementData
from myPyQt.ExtendedTableModel import ExtendedQTableModel
from myPyQt.CustomSortingProxy import CustomSortingProxy
from myPyQt.ButtonDelegate import ButtonDelegate
from helpers.integration import integrate_simps, integrate_trapz
from helpers.nearestNumber import nearestnumber
from helpers.getWidgets import getLayoutWidgets


# todo -------------------- Issues/Feature TODO list --------------------
# todo - Add periodic table GUI for selection.
# todo - Maximas are broken
# todo - Matplotlib icons


# ? Should this ask for the filepath or just be require to be in the format as seen in the repository,
# ? Download the repository and run the program without altering the file structure, will save having
# ? to enter filepaths in console during start up.


# Asking for filepath where the user has saved script
# filepath is where the GUI files and the code has been saved. The sourceFilepath is the path to the latest data folder
# ! Maybe Change back to inputs if requried
filepath = os.path.dirname(__file__) + "\\"
#  input('Enter the filepath where the latest NRCA code data folder is \n For Example:'
#                         'C://Users/ccj88542/NRCA/Rehana/Latest/main/data: \n')

sourceFilepath = filepath + "data"

# print(filepath)
# print(sourceFilepath)

# ! fonts = font_manager.findSystemFonts(
#     fontpaths="C:\\Users\\gzi47552\\Documents\\NRTI-NRCA-Viewing-Database\\src\\fonts")
# ! for font in fonts:
# !    font_manager.fontManager.addfont(font)
# ! matplotlib.rcParams["font.family"] = 'Roboto Mono'

matplotlib.rcParamsDefault["path.simplify"] = False


class DatabaseGUI(QWidget):  # Acts just like QWidget class (like a template)
    """
    Class responsible for creating and manipulating the GUI used in selecting and graphing the data of numerous isotopes
    within the NRTI/NRCA Database.
    """

    # init constructure for classes
    def __init__(self) -> None:
        """
        Initialisator for DatabaseGUI class
        """
        # Allows for adding more things to the QWidget template
        super(DatabaseGUI, self).__init__()
        self.initUI()
        self.setAcceptDrops(True)

        # Setting global variables
        self.data = None
        self.x = []  # ! Depreciated
        self.y = []  # ! Depreciated
        self.xArray = []
        self.yArray = []
        self.thresholds = None
        self.numRows = None
        self.numTotPeaks = []

        self.ax = None
        self.ax2 = None
        self.canvas2 = None
        self.plotFilepath = None
        self.firstLimit = None
        self.secondLimit = None
        self.plotCount = -1
        self.graphs = OrderedDict()
        self.annotations = []
        self.localHiddenAnnotations = []
        self.plottedSubstances = []
        self.rows = None
        self.tableLayout = dict()
        self.arrays = dict()
        self.substance = None
        self.xi = None
        self.yj = None
        self.peaknum = None
        self.interact = None
        self.clickcount = None

        self.peakInfoIsNull = None
        self.graphData = None
        self.peakLimitsX = dict()
        self.peakLimitsY = dict()
        self.peakList = None
        self.orderByIntegral = True
        self.firstClickX = None
        self.filepath = filepath
        self.dataFilepath = sourceFilepath
        self.elementData = dict()
        self.elementDataNames = []
        self.maxPeak = 50
        self.threshold = 100

    def initUI(self) -> None:
        """
        Creates the UI.
        """
        self.setObjectName('mainWindow')
        self.setGeometry(350, 50, 1600, 900)
        self.setWindowTitle("NRTI/NRCA Viewing Database")

        mainLayout = QGridLayout()

        menubarLayout = QHBoxLayout()
        menubarLayout.setContentsMargins(0, 0, 0, 0)
        sidebarLayout = QVBoxLayout()
        sidebarLayout.setContentsMargins(0, 0, 0, 0)

        canvasLayout = QVBoxLayout()
        canvasLayout.setContentsMargins(0, 0, 0, 0)

        # * ----------------------------------------------

        # ¦ -------------- MENU BAR - FILE ---------------
        # Creating actions for file menu
        newAction = QAction(QIcon("./src/img/add-component.svg"), "&New", self)
        newAction.setShortcut("Ctrl+N")
        newAction.triggered.connect(self.Clear)

        importAction = QAction(QIcon("./src/img/upload-component.svg"), "&Import Data", self)
        importAction.setShortcut("Ctrl+I")

        importAction.triggered.connect(self.importdata)

        editpeakAction = QAction(QIcon("./src/img/edit-component.svg"), "&Edit Peak Limits", self)
        editpeakAction.setShortcut("Ctrl+E")
        editpeakAction.triggered.connect(self.EditPeaks)

        selectlimitsAction = QAction(QIcon("./src/img/select-component.svg"), "&Select Limits", self)
        selectlimitsAction.setShortcut("Ctrl+L")
        selectlimitsAction.triggered.connect(self.SelectLimitsOption)

        editThresholdAction = QAction(QIcon("./src/img/edit-component.svg"), "&Edit Threshold", self)
        editThresholdAction.setShortcut("Ctrl+Shift+T")
        editThresholdAction.triggered.connect(self.editThresholdLimit)

        editMaxPeaks = QAction(QIcon("./src/img/edit-component.svg"), "&Edit Peak Quantity", self)
        editMaxPeaks.setShortcut("Ctrl+Shift+Q")
        editMaxPeaks.triggered.connect(self.editMaxPeaks)

        # * ----------------------------------------------

        # ¦ -------------- MENU BAR - EDIT ---------------
        # Creates menu bar and add actions
        menubar = QMenuBar(self)
        menubar.setObjectName("menubar")
        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(newAction)
        fileMenu.addAction(importAction)
        # fileMenu.addAction(saveAction)

        editMenu = menubar.addMenu("&Edit")
        editMenu.addAction(editpeakAction)
        editMenu.addAction(selectlimitsAction)
        editMenu.addAction(editThresholdAction)
        editMenu.addAction(editMaxPeaks)
        # helpMenu = menubar.addMenu('&Help')
        # helpMenu.addAction(aboutAction)
        menubarLayout.addWidget(menubar, alignment=Qt.AlignLeft)
        # Adding label which shows number of peaks
        self.peaklabel = QLabel()
        self.peaklabel.setObjectName('numPeakLabel')
        self.peaklabel.setText("")
        self.peaklabel.setAlignment(Qt.AlignVCenter)

        self.peaklabel.setContentsMargins(0, 10, 0, 0)
        menubarLayout.addWidget(self.peaklabel, alignment=Qt.AlignVCenter)
        # Threshold Label
        self.thresholdLabel = QLabel()
        self.thresholdLabel.setObjectName('thresholdLabel')
        self.thresholdLabel.setText("Nothing has been selected")
        self.thresholdLabel.setAlignment(Qt.AlignRight)
        self.thresholdLabel.setContentsMargins(0, 10, 0, 0)

        menubarLayout.addWidget(self.thresholdLabel, alignment=Qt.AlignRight)

        # * ----------------------------------------------

        # ¦ --------------- Combobox Group ---------------
        # For copying data directory to local directory for plotting later
        # Establishing source and destination directories
        sourceDir = sourceFilepath
        destinationDir = filepath + "data/"

        # Creating a list of substances stored in the NRCA database data directory
        self.substances = [None]
        for file in os.listdir(sourceDir):
            filename = os.fsdecode(file)
            filename = filename[:-4]
            self.substances.append(filename)
            source = sourceDir + file
            destination = destinationDir + file
            if os.path.isfile(source):
                shutil.copy(source, destination)

        # Creating combo box (drop down menu)
        self.combobox = QComboBox()
        self.combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.combobox.setObjectName("combobox")
        self.combobox.addItems(self.substances)
        self.combobox.setEditable(True)

        self.combobox.setInsertPolicy(QComboBox.NoInsert)
        self.combobox.setMaxVisibleItems(15)
        # filterCompleter = QCompleter(self)
        # filterCompleter.set
        self.combobox.completer().setCompletionMode(
            QCompleter.UnfilteredPopupCompletion
        )

        self.combobox.completer().setCaseSensitivity(Qt.CaseInsensitive)
        self.combobox.completer().setFilterMode(Qt.MatchContains)

        sidebarLayout.addWidget(self.combobox)
        # Upon selecting an option, it records the option
        # and connects to the method 'Select_and_Display'
        self.combobox.activated.connect(self.Select_and_Display)

        # * ----------------------------------------------

        pointingCursor = QCursor(Qt.PointingHandCursor)

        # ¦ ---------------- Button Group ----------------
        self.btnLayout = QVBoxLayout()

        plotEnergyBtn = QPushButton("Plot in Energy", self)
        plotEnergyBtn.setObjectName("plotEnergyBtn")
        plotEnergyBtn.setCursor(pointingCursor)
        plotEnergyBtn.__name__ = "plotEnergyBtn"
        plotEnergyBtn.resize(plotEnergyBtn.sizeHint())
        plotEnergyBtn.setEnabled(False)
        self.btnLayout.addWidget(plotEnergyBtn)
        plotEnergyBtn.clicked.connect(self.Plot)

        plotTOFBtn = QPushButton("Plot in ToF", self)
        plotTOFBtn.setCursor(pointingCursor)
        plotTOFBtn.setObjectName("plotTOFBtn")
        plotTOFBtn.__name__ = "plotToFBtn"
        plotTOFBtn.resize(plotTOFBtn.sizeHint())
        plotTOFBtn.setEnabled(False)
        self.btnLayout.addWidget(plotTOFBtn)
        plotTOFBtn.clicked.connect(self.PlotToF)

        clearBtn = QPushButton("Clear Results", self)
        clearBtn.setObjectName("clearBtn")
        clearBtn.setCursor(pointingCursor)
        clearBtn.__name__ = "clearBtn"
        clearBtn.resize(clearBtn.sizeHint())
        clearBtn.setEnabled(False)
        self.btnLayout.addWidget(clearBtn)
        clearBtn.clicked.connect(self.Clear)

        pdBtn = QPushButton("Peak Detection", self)
        pdBtn.setObjectName("pdBtn")
        pdBtn.setCursor(pointingCursor)
        pdBtn.__name__ = "pdBtn"
        pdBtn.resize(pdBtn.sizeHint())
        pdBtn.setEnabled(False)
        self.btnLayout.addWidget(pdBtn)
        pdBtn.clicked.connect(self.GetPeaks)

        sidebarLayout.addLayout(self.btnLayout)

        # * ----------------------------------------------

        # ¦ --------------- Checkbox Group ---------------
        self.toggleLayout = QVBoxLayout()
        self.toggleLayout.setObjectName('toggleLayout')

        gridCheck = QCheckBox("Grid Lines", self)
        gridCheck.setCursor(pointingCursor)
        gridCheck.setObjectName("gridCheck")
        gridCheck.__name__ = "gridCheck"

        gridCheck.setEnabled(False)
        self.toggleLayout.addWidget(gridCheck)
        gridCheck.stateChanged.connect(self.Gridlines)

        self.threshold_check = QCheckBox("Peak Detection Limits", self)
        self.threshold_check.setCursor(pointingCursor)
        self.threshold_check.setObjectName("threshold_check")
        self.threshold_check.__name__ = "thresholdCheck"
        self.threshold_check.setEnabled(False)
        self.toggleLayout.addWidget(self.threshold_check)
        self.threshold_check.stateChanged.connect(self.Threshold)

        self.peakLabelCheck = QCheckBox("Hide Peak Labels", self)
        self.peakLabelCheck.setCursor(pointingCursor)
        self.peakLabelCheck.setObjectName("label_check")
        self.peakLabelCheck.__name__ = "labelCheck"
        self.peakLabelCheck.setEnabled(False)
        self.toggleLayout.addWidget(self.peakLabelCheck)
        self.peakLabelCheck.stateChanged.connect(self.ToggleAnnotations)

        sidebarLayout.addLayout(self.toggleLayout)

        # * ------------------------------------------------

        # ¦ --------------- Peak Order Group ---------------
        peakOrderLayout = QVBoxLayout()
        peakOrderLayout.setSpacing(5)
        peakCheckLayout = QHBoxLayout()
        peakCheckLayout.setSpacing(5)
        peakOrderLabel = QLabel(self, text="Peak Order")
        peakOrderLabel.setObjectName('orderlabel')

        radioBtnGroup = QGroupBox()
        self.byIntegralCheck = QRadioButton(radioBtnGroup, text="By Integral")
        self.byIntegralCheck.setObjectName('orderByIntegral')
        self.byIntegralCheck.setChecked(True)
        self.byIntegralCheck.clicked.connect(self.PeakOrderChanged)
        self.byPeakWidthCheck = QRadioButton(radioBtnGroup, text="By Peak Width")
        self.byPeakWidthCheck.setObjectName('orderByPeakW')
        self.byPeakWidthCheck.clicked.connect(self.PeakOrderChanged)

        peakCheckLayout.addWidget(self.byIntegralCheck)
        peakCheckLayout.addWidget(self.byPeakWidthCheck)

        peakOrderLayout.addWidget(peakOrderLabel)
        peakOrderLayout.addItem(peakCheckLayout)

        sidebarLayout.addLayout(peakOrderLayout)

        # * -----------------------------------------------

        # ¦ ---------------- Plot Canvas ------------------
        self.figure = plt.figure()  # Creating canvas to plot graph on and toolbar
        self.canvas = FigureCanvas(self.figure)
        self.canvas.__name__ = "canvas"

        self.toolbar = NavigationToolbar(self.canvas, self)
        canvasLayout.addWidget(self.toolbar)
        canvasLayout.addWidget(self.canvas)

        # * -----------------------------------------------

        # ¦ -------------------- Table --------------------
        # Adding table to display peak information
        self.table = QTableView()
        self.table.setObjectName('dataTable')
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(200)

        # * -----------------------------------------------

        container = QWidget(self)
        container.setObjectName('mainContainer')
        container.setLayout(canvasLayout)
        container.setMinimumHeight(300)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(container)
        splitter.addWidget(self.table)
        splitter.setHandleWidth(10)
        splitter.splitterMoved.connect(self.figure.tight_layout)

        contentLayout = QHBoxLayout()
        contentLayout.addWidget(splitter)
        sidebarLayout.setAlignment(Qt.AlignTop)

        mainLayout.addItem(menubarLayout, 0, 0, 1, 6, Qt.AlignTop)
        mainLayout.addItem(sidebarLayout, 1, 0, 1, 1, Qt.AlignTop)
        mainLayout.addItem(contentLayout, 1, 1, 1, 6)
        self.btnLayout.setSpacing(10)
        self.toggleLayout.setSpacing(10)

        sidebarLayout.setSpacing(50)

        # If double-clicking cell, can trigger plot peak

        # self.table.cellDoubleClicked.connect(self.PlotPeakWindow)

        self.setLayout(mainLayout)  # Generating layout
        self.show()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        """
        dragEnterEvent handles file drag enter event and verification

        Args:
            event (QDragEnterEvent): PyQtEvent
        """
        if event.mimeData().hasUrls():
            for file in event.mimeData().urls():
                filepath = file.toLocalFile()
                if any([ext for ext in ['.csv', '.txt', '.dat'] if ext in filepath]):
                    event.acceptProposedAction()
                else:
                    event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        """
        dropEvent handles the drop event and calls to plot each data file

        Args:
            event (QDropEvent): PyQtEvent
        """
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            name = filepath.split('/')[-1].split('.')[0]
            self.Plot(False, filepath, True, name)

    def editThresholdLimit(self) -> None:
        if self.elementData == {}:
            return

        mainLayout = QVBoxLayout()
        inputFormGroupBox = QGroupBox()
        inputForm = QFormLayout()
        inputForm.windowTitle = "Threshold Input"

        elements = QComboBox()
        elements.addItems(self.elementData.keys())

        input_threshold = QLineEdit()
        input_threshold.setPlaceholderText(str(self.elementData[elements.currentText()].threshold))
        input_threshold.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        inputForm.addRow(QLabel("Substance:"), elements)
        inputForm.addRow(QLabel("Threshold:"), input_threshold)
        inputFormGroupBox.setLayout(inputForm)
        buttonBox = QDialogButtonBox()
        buttonOk = buttonBox.addButton(QDialogButtonBox.Ok)

        mainLayout.addWidget(inputFormGroupBox)
        mainLayout.addWidget(buttonBox)

        inputWindow = QDialog()
        inputWindow.setObjectName('thresholdLimit')

        inputWindow.setWindowTitle("Edit Threshold Value")
        inputWindow.setLayout(mainLayout)

        def close():
            inputWindow.close()
        buttonOk.clicked.connect(close)

        def changeThresholdText():
            input_threshold.setPlaceholderText(str(self.elementData[elements.currentText()].threshold))
        elements.currentTextChanged.connect(changeThresholdText)

        inputWindow.exec_()

        substance_name = elements.currentText()
        if input_threshold.text() == '':
            return
        threshold_value = float(input_threshold.text())

        self.elementData[substance_name].threshold = threshold_value
        self.elementData[substance_name].UpdateMaximas()
        self.Threshold()
        self.DrawAnnotations(self.elementData[substance_name])

    def editMaxPeaks(self) -> None:
        if self.elementData == {}:
            return

        mainLayout = QVBoxLayout()
        inputFormGroupBox = QGroupBox()
        inputForm = QFormLayout()
        inputForm.windowTitle = "Threshold Input"

        elements = QComboBox()
        elements.addItems(self.elementData.keys())

        inputMaxPeaks = QLineEdit()
        inputMaxPeaks.setPlaceholderText(str(self.elementData[elements.currentText()].numPeaks))
        inputMaxPeaks.setValidator(QRegExpValidator(QRegExp("[0-9]{0,4}")))

        inputForm.addRow(QLabel("Substance:"), elements)
        inputForm.addRow(QLabel("Peak Quantity:"), inputMaxPeaks)
        inputFormGroupBox.setLayout(inputForm)
        buttonBox = QDialogButtonBox()
        okButton = buttonBox.addButton(QDialogButtonBox.Ok)

        mainLayout.addWidget(inputFormGroupBox)
        mainLayout.addWidget(buttonBox)

        inputWindow = QDialog()
        inputWindow.setObjectName('maxPeaks')
        inputWindow.setWindowTitle("Displayed Peaks Quantity")
        inputWindow.setLayout(mainLayout)

        def closeWindow():
            inputWindow.close()
        okButton.clicked.connect(closeWindow)

        def changePeaksText():
            inputMaxPeaks.setPlaceholderText(str(self.elementData[elements.currentText()].numPeaks))
        elements.currentTextChanged.connect(changePeaksText)

        inputWindow.exec_()

        substance_name = elements.currentText()
        if inputMaxPeaks.text() == '':
            return
        maxPeaks = int(inputMaxPeaks.text())
        self.elementData[substance_name].maxPeaks = maxPeaks
        self.DrawAnnotations(self.elementData[substance_name])

    def Select_and_Display(self, index) -> None:
        """
        Select_and_Display detects what has been selected and displays relevant peak information in the table.
        Once a select is made, the relevant controls are enabled.

        Args:
            index (int): Index of the selected item within the combobox.
        """
        self.data = self.combobox.itemText(index)

        if self.data == "" and self.plotCount > -1:  # Null selection and graphs shown
            self.toggleBtnControls(clearBtn=True)
            return
        elif (
            self.data == "" and self.plotCount == -1
        ):  # Null selection and no graphs shown
            self.toggleBtnControls(enableAll=False)
            self.toggleCheckboxControls(enableAll=False)
            return
        elif self.plotCount != -1:  # Named Selection and graphs shown
            self.toggleBtnControls(enableAll=True)
            self.toggleCheckboxControls(enableAll=True)
        else:  # Named selection and no graphs shown
            self.toggleBtnControls(plotEnergyBtn=True, plotToFBtn=True, clearBtn=True)
            self.toggleCheckboxControls(enableAll=False)

        # Getting symbol from substance
        split = self.data.split("-")
        if self.data.startswith("e"):
            dataSymbolSort = split[1]
            dataSymbol = dataSymbolSort[:-2]
        else:
            dataSymbol = split[1]
        # Finding relevant file for peak information
        peakInfoDir = self.filepath + "GUI Files/Peak information/"
        filepath = None
        for file in os.listdir(peakInfoDir):
            if self.data == file.split(".")[0]:
                filepath = peakInfoDir + file
                break

        try:
            file = pd.read_csv(filepath, header=0)
            # start = time.time()
            # Reset any changes to spans before displaying selection data.
            self.table.clearSpans()
            # end = time.time()
            # print("Time elapsed : ", end-start)
            if self.data not in self.plottedSubstances:
                self.numRows = file.shape[0]
            print("Number of peaks: ", self.numRows)
            # Fill Table with data
            if self.table_model is not None:
                for row in self.table_model.titleRows:
                    self.table.setItemDelegateForRow(row, None)
            self.table_model = ExtendedQTableModel(file)
            proxy = CustomSortingProxy()
            proxy.setSourceModel(self.table_model)

            self.table.setModel(proxy)
            self.table.setSortingEnabled(True)
            self.peakInfoIsNull = False
            # peak_plotEnergyBtn = QPushButton(self.table)      # If wanting a button to plot peak
            # peak_plotEnergyBtn.setText('Plot')         # Not sure how to get cell-clicked though
            # peak_plotEnergyBtn.clicked.connect(self.PlotPeak)
            # self.table.setCellWidget(row_count,10,peak_plotEnergyBtn)
        except AttributeError:
            pass
        except ValueError:
            QMessageBox.warning(
                self,
                "Error",
                "The peak information has not been obtained. \n Contact Rehana"
                ".Patel@stfc.ac.uk",
            )
            self.peakInfoIsNull = True
            self.numRows = None

        # Displaying threshold for chosen substance
        # ! ------------ Optimise Reading file ------------
        thresholdDir = self.filepath + "GUI Files/threshold_exceptions.txt"
        with open(thresholdDir, "r") as f:
            # * Optimisation for collecting data from a file,
            # * some element file have 100's or >1000 entries.
            file = f.readlines()
        self.thresholds = "100 by default"
        # Checking if the selected substance has a threshold exception
        for i in file:
            sortLimits = i.replace('\n', '').split(" ")
            symbol = sortLimits[0]
            if str(symbol) == str(dataSymbol):
                self.thresholds = str(sortLimits[1]) + str(sortLimits[2])
                break
            else:
                continue

        # ! ----------------------------------------------
        # Setting label information based on threshold value
        if self.thresholds == "100 by default":
            labelInfo = (
                "Threshold for peak detection for n-tot mode: " + self.thresholds
            )
            self.threshold = 100
        else:
            labelInfo = (
                "Threshold for peak detection (n-tot mode, n-g mode): " + self.thresholds
            )
            if self.data[-1] == 't':
                self.threshold = sortLimits[1][1:-1]
            else:
                self.threshold = sortLimits[2][:-1]
        self.thresholdLabel.setText(str(labelInfo))
        # Changing the peak label text
        labelInfo = "Number of peaks: " + str(self.numRows)
        self.peaklabel.setText(str(labelInfo))

    def toggleBtnControls(self, enableAll: bool = False, plotEnergyBtn: bool = False,
                          plotToFBtn: bool = False, clearBtn: bool = False, pdBtn: bool = False) -> None:
        """
        toggleBtnControls enables and disables the buttons controls, thus only allowing its
        use when required. enableAll is done before any kwargs have an effect on the buttons.
        enableAll defaults to False, True will enable all buttons regardless of other kwargs.
        This way you can disable all buttons then make changes to specific buttons.

        Args:
            enableAll (bool): Boolean to enable/disable (True/False) all the buttons controls.
            plotEnergyBtn (bool): Boolean to enable/disable (True/False) Plot Energy button.
            plotToFBtn (bool): Boolean to enable/disable (True/False) Plot ToF button.
            plotEnergyBtn (bool): Boolean to enable/disable (True/False) Plot Energy button.
            clearBtn (bool): Boolean to enable/disable (True/False) Plot Energy button.
            pdBtn (bool): Boolean to enable/disable (True/False) Peak Detection button.
        """

        for btn in getLayoutWidgets(self.btnLayout):
            btn.setEnabled(enableAll)

        if enableAll:
            return

        for btn in getLayoutWidgets(self.btnLayout):
            match btn.__name__:
                case "plotEnergyBtn":
                    btn.setEnabled(plotEnergyBtn)
                case "plotToFBtn":
                    btn.setEnabled(plotToFBtn)
                case "clearBtn":
                    btn.setEnabled(clearBtn)
                case "pdBtn":
                    btn.setEnabled(pdBtn)

    def toggleCheckboxControls(self, enableAll: bool, gridlines: bool = False,
                               peakLimit: bool = False, hidePeakLabels: bool = False) -> None:
        """
        toggleCheckboxControls enables and disables the checkboxes controls, thus only allowing its
        use when required. enableAll is done before any kwargs have an effect on the checkboxes.
        enableAll defaults to False, True will enable all checkboxes regardless of other kwargs.
        This way you can disable all checkboxes then make changes to specific checkboxes.

        Args:
            enableAll (bool): Boolean to enable/disable (True/False) all the buttons controls.
            gridlines (bool): Boolean to enable/disable (True/False) Plot Energy button.
            peakLimit (bool): Boolean to enable/disable (True/False) Plot ToF button.
            hidePeakLabels (bool): Boolean to enable/disable (True/False) Plot Energy button.
        """

        for btn in getLayoutWidgets(self.toggleLayout):
            if enableAll:  # Enable All then return
                btn.setEnabled(True)

            else:  # Otherwise disable all and apply kwargs
                btn.setEnabled(False)
                btn.setChecked(False)

        if enableAll:
            return

        for btn in getLayoutWidgets(self.toggleLayout):
            match btn.__name__:
                case "gridCheck":
                    btn.setEnabled(gridlines)
                case "peakCheck":
                    btn.setEnabled(peakLimit)
                case "pdCheck":
                    btn.setEnabled(hidePeakLabels)

    def Plot(self, tof=False, filepath=None, imported=False, name=None) -> None:
        """
        Plots graphs both by energy and time of flight(tof), and fills the table
        with the appropriate data.

        Args:
            tof (bool, optional): Whether to graph for tof or not. Defaults to False.
            filepath (string, optional): Filepath for the selection to graph . Defaults to None.
            imported (bool, optional): Whether the selection imported. Defaults to False.
            name (string, optional): The name of the imported selection. Defaults to None.
        """
        # Enable Checkboxes on plotting graphs
        self.toggleCheckboxControls(enableAll=True)
        self.toggleBtnControls(enableAll=True)

        if self.data is None and not imported:
            QMessageBox.warning(self, "Error", "You have not selected anything to plot")
            return
        if imported:
            self.data = name
        # Checks for adding mutliple graphs for the same selection, energy/tof types.
        if (self.data, tof) in self.plottedSubstances:
            QMessageBox.warning(self, "Warning", "Graph is already plotted")
            return

        # Establishing the number of peaks on the graph at one time, and their type
        if not imported and self.numRows != 0:
            if self.data not in self.plottedSubstances:
                self.numTotPeaks.append(self.numRows)

        # ! Handle Element Creation here.

        self.plottedSubstances.append((self.data, tof))
        # Handles number_totpeaks when plotting energy and tof of the same graph
        self.numTotPeaks.append(self.numRows)

        # # Finds the mode for L0 (length) parameter
        if self.data[-1] == "t":
            length = 23.404
        else:
            length = 22.804

        self.titleRows = [0]

        for (substance, tof) in self.plottedSubstances:
            title = f"{substance}-{'ToF' if tof else 'Energy'}"
            if title in self.elementData.keys():
                if self.elementData[title].isGraphDrawn:
                    continue
            self.plotFilepath = f"{self.filepath}data\\{substance}.csv" if filepath is None else filepath
            peakInfoDir = f"{self.filepath}GUI Files/Peak information/" if filepath is None else None

            graphData = pd.read_csv(self.plotFilepath, header=None)
            self.graphData = graphData

            if tof:
                graphData[0] = self.EnergytoTOF(graphData[0], length=length)

            try:
                elementTableData = pd.read_csv(f"{peakInfoDir}{substance}.csv")
            except FileNotFoundError:
                elementTableData = pd.DataFrame(
                    columns=[
                        "Rank by Integral",
                        "Energy (eV)",
                        "Rank by Energy",
                        "TOF (us)",
                        "Integral",
                        "Peak Width",
                        "Rank by Peak Width",
                        "Peak Height",
                        "Rank by Peak Height",
                        "Relevant Isotope"
                    ])
            # Title Rows
            if elementTableData.empty:
                elementTableData.loc[-1] = [f"No Peak Data for {substance}", *[""] * 9]

            else:
                elementTableData.loc[-1] = [substance, *[""] * 9]
            elementTableData.index += 1
            elementTableData.sort_index(inplace=True)
            colour = (np.random.random() * 0.8 + 0.1,
                      np.random.random() * 0.5 + 0.2,
                      np.random.random() * 0.8 + 0.1)
            if title not in self.elementData.keys():
                newElement = ElementData(name=substance,
                                         numPeaks=self.numRows,
                                         tableData=elementTableData,
                                         graphData=graphData,
                                         graphColour=colour,
                                         isToF=tof,
                                         isAnnotationsHidden=self.peakLabelCheck.isChecked(),
                                         threshold=float(self.threshold),
                                         isImported=imported)
                self.elementData[title] = newElement
        # Re-setting Arrays
        self.x = []
        self.y = []
        # Establishing colours for multiple plots
        # ! Fix issue with adding more than 7 graphs.

        # # print(graphData)

        # General Plotting ---------------------------------------------------------------------------------------------
        if self.plotCount < 0:
            self.ax = self.figure.add_subplot(111)
            # Setting scale to be logarithmic
            self.ax.set_yscale("log")
            self.ax.set_xscale("log")
        # Allows user to plot in ToF if chosen # -----------------------------------------------------------------------
        if tof and not imported:
            # ! Convert to pandas compatible

            if self.plotCount < 0:
                self.ax.set(
                    xlabel="ToF (uS)", ylabel="Cross section (b)", title=self.data
                )
        else:
            if self.plotCount < 0:
                if tof:
                    self.ax.set(
                        xlabel="Time of Flight (uS)",
                        ylabel="Cross section (b)",
                        title=self.data,
                    )
                else:
                    self.ax.set(
                        xlabel="Energy (eV)",
                        ylabel="Cross section (b)",
                        title=self.data,
                    )
            else:
                self.ax.set(title=None)

        # Plotting -----------------------------------------------------------------------------------------------------

        spectraLine = self.ax.plot(
            graphData.iloc[:, 0],
            graphData.iloc[:, 1],
            "-",
            c=colour,
            alpha=0.6,
            linewidth=0.8,
            label=f"{self.data}-ToF" if newElement.isToF else f"{self.data}-Energy",
            gid=self.data,
        )
        newElement.isGraphDrawn = True

        # Creating a legend to toggle on and off plots----------------------------------------------------------------
        legend = self.ax.legend(fancybox=True, shadow=True)

        # Amending dictionary of plotted lines - maps legend line to original line and allows for picking
        spectraLegend = legend.get_lines()  # Gets the 'ID' of lines ( I think)
        for i in spectraLegend:
            i.set_picker(True)
            i.set_pickradius(5)  # Makes it easier to click on legend line

        # Dictionary has legend line mapped to spectraLine but needs to be updated for multiple plots
        legend_line = spectraLegend[-1]
        self.graphs[legend_line] = spectraLine[0]

        # Updating for multiple plots
        dictionary_keys = []
        for key in self.graphs:
            dictionary_keys.append(key)
        count = 0
        for i in spectraLegend:
            self.graphs[i] = self.graphs.pop(dictionary_keys[count])
            count = count + 1
        plt.connect("pick_event", self.HideGraph)
        # ------------------------------------------------------------------------------------------------------------

        # Establishing plot count
        self.plotCount += 1
        self.canvas.draw()

        # Amending the table for more than one plot.
        self.table.reset()
        self.table.sortByColumn(-1, Qt.SortOrder.AscendingOrder)

        table_data = pd.DataFrame()
        # ! ---------------------------------------------------------------------------------
        # ? Maybe sort the order in which they are plotted and added to the table.
        for substance in self.elementData.values():
            if substance.name not in self.elementDataNames:
                table_data = pd.concat([table_data, substance.tableData], ignore_index=True)
                self.titleRows.append(self.titleRows[-1] + substance.tableData.shape[0])
                self.elementDataNames.append(substance.name)

        self.DrawAnnotations(self.elementData.get(f"{self.data}-ToF" if newElement.isToF else f"{self.data}-Energy"))
        self.Threshold()
        self.ax.autoscale()  # Tidying up

        self.figure.tight_layout()

        self.table_model = ExtendedQTableModel(table_data)
        self.table_model.titleRows = self.titleRows
        self.table.setModel(self.table_model)
        self.table.setSortingEnabled(False)
        self.table.clearSpans()
        for row in self.titleRows[:-1]:
            self.table.setSpan(row, 0, 1, 10)
            self.table.setItemDelegateForRow(row, ButtonDelegate(self, self.table, self.table_model))
            self.table.openPersistentEditor(self.table_model.index(row, 0))

        self.canvas.draw()

    def PlotToF(self) -> None:
        self.Plot(True)

    def EnergytoTOF(self, xData: list[float], length: float) -> list[float]:
        """
        Maps all X Values from energy to TOF

        Args:
            xData (list[float]): List of the substances x-coords of its graph data
            length (float): Constant value associated to whether the substance data is with repsect to n-g or n-tot

        Returns:
            list[float]: Mapped x-coords
        """
        if length is None:
            length = 22.804
        neutronMass = float(1.68e-27)
        electronCharge = float(1.60e-19)

        tofX = list(
            map(
                lambda x: length * 1e6 * (0.5 * neutronMass / (x * electronCharge)) ** 0.5,
                xData
            )
        )
        return tofX

    def HideGraph(self, event) -> None:
        """
        Function to show or hide the selected graph by clicking the legend.

        Args:
            event (pick_event): event on clicking a graphs legend
        """
        # Tells you which plot number you need to delete labels for
        legline = event.artist
        graphLine = self.graphs[legline]
        orgline_name = graphLine._label
        # Hiding relevant line
        visible = not graphLine.get_visible()
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled.
        legline.set_alpha(1.0 if visible else 0.2)
        graphLine.set_visible(visible)
        # Hiding relevant labels

        self.elementData[orgline_name].isGraphHidden = not visible
        self.elementData[orgline_name].HideAnnotations(self.peakLabelCheck.isChecked())
        for line in self.ax.lines:
            if line.get_gid() == f"pd_threshold-{orgline_name}":
                line.set_visible(visible)
        self.canvas.draw()

    def Clear(self) -> None:
        """
        Clear Function will empty all data from the table, all graphs from the plots,
        along with resetting all data associated the table or plot and disables relevent controls.
        """

        self.figure.clear()
        self.canvas.draw()
        self.x = []
        self.y = []
        self.plotCount = -1
        self.numTotPeaks = []
        self.annotations = []
        self.localHiddenAnnotations = []
        self.peaklabel.setText("")
        self.thresholdLabel.setText("")
        self.elementData = {}
        self.elementDataNames = []
        for row in self.table_model.titleRows:
            self.table.setItemDelegateForRow(row, None)
        self.table.setModel(None)
        self.graphs = OrderedDict()
        self.tableLayout = dict()
        self.arrays = dict()
        self.plottedSubstances = []

        self.toggleBtnControls(plotEnergyBtn=True, plotToFBtn=True, clearBtn=True)
        self.toggleCheckboxControls(enableAll=False)

    def Gridlines(self, checked: bool) -> None:
        """
        Toggles the gridlines on the plot

        Args:
            checked (_type_): _description_
        """
        try:
            if checked:
                self.ax.grid()
                self.canvas.draw()
            else:
                self.ax.grid()
                self.canvas.draw()
        except Exception:
            QMessageBox.warning(self, "Error", "You have not plotted anything")

    def Threshold(self) -> None:
        """
        Plots the threshold line for each plotted substance at their respective limits.
        """
        checked = self.threshold_check.isChecked()
        for line in self.ax.lines:
            if line is None:
                continue
            if line.get_gid() is None:
                continue
            if "pd_threshold" in line.get_gid():
                line.remove()
        self.canvas.draw()
        if checked:
            for name, substance in self.elementData.items():
                self.figure.add_subplot(self.ax)
                line = self.ax.axhline(
                    y=substance.threshold,
                    linestyle="--",
                    color=substance.graphColour,
                    linewidth=0.5,
                    gid=f"pd_threshold-{name}"
                )
                if substance.isGraphHidden:
                    line.set_visible(False)

                self.canvas.draw()

    def PeakOrderChanged(self) -> None:
        if self.sender().objectName() == "orderByIntegral":
            self.orderByIntegral = self.byIntegralCheck.isChecked()

        if self.sender().objectName() == "orderByPeakW":
            self.orderByIntegral = self.byIntegralCheck.isChecked()

        for element in self.elementData.values():
            self.DrawAnnotations(element)

    def DrawAnnotations(self, element: ElementData) -> None:
        """
        DrawAnnotations will plot each numbered annotation in the order of Integral or Peak Width

        Args:
            element (ElementData): The data for the element your annotating
        """
        self.elementDataNames = []

        if element.isAnnotationsDrawn:
            for anno in element.annotations:
                anno.remove()
            element.annotations.clear()
        if element.maxima.size == 0:
            return
        element.OrderAnnotations(self.orderByIntegral)
        gid = f"annotation-{element.name}-" + "ToF" if element.isToF else "Energy"
        maxDraw = element.maxPeaks if element.maxPeaks < element.numPeaks else element.numPeaks
        xy = element.maxima.T if element.annotationsOrder == {} else element.annotationsOrder
        element.annotations = [self.ax.annotate(text=f'{i}',
                                                xy=xy[i],
                                                xytext=xy[i],
                                                xycoords="data",
                                                textcoords="data",
                                                va="center",
                                                size=6,
                                                gid=gid,
                                                annotation_clip=True,
                                                )
                               for i in
                               (range(0, maxDraw) if type(xy) == np.ndarray else xy.keys())
                               if i <= maxDraw]
        if element.isGraphHidden or self.peakLabelCheck.isChecked():
            for annotation in element.annotations:
                annotation.set_visible(False)
            element.isAnnotationsHidden = True
        element.isAnnotationsDrawn = True
        self.canvas.draw()

    def ToggleAnnotations(self) -> None:
        """
        Function Annotations shows & hides all peak annotations globally.
        """
        for substance in self.elementData.values():
            substance.HideAnnotations(self.peakLabelCheck.isChecked())
            substance.isAnnotationsHidden = not substance.isAnnotationsHidden
        self.canvas.draw()

    # ! Not Working <-----------------------------------------------------------------------
    def PlotPeakWindow(self, row_clicked) -> None:
        try:
            peakwindow = QMainWindow(self)
            # Setting title and geometry
            peakwindow.setWindowTitle("Peak Plotting")
            peakwindow.setGeometry(350, 50, 850, 700)
            # Creating a second canvas for singular peak plotting
            figure2 = plt.figure()
            self.canvas2 = FigureCanvas(figure2)

            # Setting up dock for widgets to be used around canvas
            dock = QDockWidget("Peak info", peakwindow)
            # Creating a widget to contain peak info in dock
            peak_info_widget = QWidget()

            # Creating layout to display peak info in the widget
            layout2 = QVBoxLayout()
            toggle_layout2 = QHBoxLayout()

            # Adding checkbox to toggle the peak limits on and off
            threshold_check2 = QCheckBox("Peak Detection Limits in X", peakwindow)
            threshold_check2.resize(threshold_check2.sizeHint())
            toggle_layout2.addWidget(threshold_check2)
            threshold_check2.stateChanged.connect(self.PeakLimits)
            # Adding checkbox to toggle the peak detection limits on and off
            threshold_check3 = QCheckBox("Peak Detection Limits in Y", peakwindow)
            threshold_check3.resize(threshold_check3.sizeHint())
            toggle_layout2.addWidget(threshold_check3)
            threshold_check3.stateChanged.connect(self.ThresholdforPeak)
            # Adding to overall layout
            layout2.addLayout(toggle_layout2)

            peak_table = QTableView()  # Creating a table to display peak info
            peak_table.setColumnCount(4)
            peak_table.setRowCount(1)
            labels = [
                "Peak Number (Rank)",
                "Peak Limits (Limits of Integration) (eV)",
                "Peak Centre Co-ord (eV)",
                "Isotopic Origin",
            ]
            peak_table.setHorizontalHeaderLabels(labels)
            peak_table.resizeColumnsToContents()
            # Making the table fill the space available
            header = peak_table.horizontalHeader()
            header.setStretchLastSection(True)
            layout2.addWidget(peak_table)

            # Adding label which shows what scale the user picks
            scale_label = QLabel()
            layout2.addWidget(scale_label)

            # Setting layout within peak info widget
            peak_info_widget.setLayout(layout2)
            dock.setWidget(peak_info_widget)  # Adding peak info widget to dock

            peakwindow.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
            # Setting canvas as central widget
            peakwindow.setCentralWidget(self.canvas2)

            self.ax2 = figure2.add_subplot(111)
            # Establishing which row belongs to what substance if multiple --------------------------------------------
            start_row = 0
            for i in self.plottedSubstances:
                index = self.plottedSubstances.index(i)
                for j in range(0, index):
                    start_row = start_row + self.numTotPeaks[j] + 1
                titleRows = (
                    start_row + self.numTotPeaks[self.plottedSubstances.index(i)] + 1
                )
                peak_count = 0
                for j in range(start_row, titleRows):
                    self.tableLayout[j] = i + "_" + str(peak_count)
                    peak_count += 1
            # Get relevant data for peak
            substance = self.tableLayout.get(row_clicked)
            # Getting Singular Peak Arrays with PlotPeak---------------------------------------------------------------
            # Getting peak limits for relevant substance
            peakLimits = []
            try:
                if self.peakLimitsX == dict():
                    filepath = self.filepath + "GUI Files/Peak_limits.txt"
                    with open(filepath, "r") as f:
                        lines = f.readlines()
                        for i in lines:
                            # should have sorting = [name, peak limit 1, peak limit 2]
                            sorting = i.split(" ")
                            if sorting[0] == substance[:-2]:
                                # Slicing the actual numbers out of the string
                                peakLimits.append(sorting[1][1:-1])
                                peakLimits.append(sorting[2][:-2])
                            else:
                                continue
                else:
                    peak_center_coord = self.table.item(row_clicked, 1).text()
                    print(self.peakLimitsX)
                    limit = str(peak_center_coord) + "_first"
                    print(limit)
                    peakLimits.append(
                        self.peakLimitsX[str(peak_center_coord) + "_first"]
                    )
                    peakLimits.append(
                        self.peakLimitsX[str(peak_center_coord) + "_second"]
                    )

            except Exception:
                QMessageBox.warning(self, "Error", "No peak limits for this substance")

            # Getting peak limits for relevant peak
            limitsIndex = int(self.substance[-1]) * 2 - 2
            self.firstLimit = peakLimits[limitsIndex]
            self.secondLimit = peakLimits[(limitsIndex + 1)]

            # Getting the right arrays to plot the graph
            x = self.arrays.get(substance[:-2] + "x")
            y = self.arrays.get(substance[:-2] + "y")

            # Truncating array to just before and after peak limits
            firstLimitIndex = x.index(float(self.firstLimit))
            secondLimitIndex = x.index(float(self.secondLimit))
            self.xArray = x[int(firstLimitIndex - 10): int(secondLimitIndex + 10)]
            self.yArray = y[int(firstLimitIndex - 10): int(secondLimitIndex + 10)]

            # ---------------------------------------------------------------------------------------------------------
            # Plotting
            # Getting user to choose scale
            scaleList = ["linear", "log"]
            scale, ok = QInputDialog.getText(
                peakwindow, "Scale", 'Enter Scale as "linear" or "log" : '
            )
            if ok:
                print(scale)
                if scale not in scaleList:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "Not a valid scale option - The default is linear",
                    )
                    scale = "linear"
            else:
                return

            self.ax2.set_xscale(scale)
            self.ax2.set_yscale(scale)
            self.ax2.plot(self.xArray, self.yArray, ".")
            self.ax2.autoscale()
            titlename = self.data + "- Peak: " + str(int(substance[-1]))
            self.ax2.set(
                xlabel="Energy (eV)", ylabel="Cross section (b)", title=titlename
            )

            # Filling in the peak info table information----------------------------------------------------------------
            rank = self.table.item(row_clicked, 0)
            limits = "(" + str(self.firstLimit) + "," + str(self.secondLimit) + ")"
            peak_center_coord = self.table.item(row_clicked, 1)
            isotopic_origin = self.table.item(row_clicked, 9)

            # Setting in table
            peak_table.setItem(0, 0, QTableWidgetItem(rank))
            peak_table.setItem(0, 1, QTableWidgetItem(limits))
            peak_table.setItem(0, 2, QTableWidgetItem(peak_center_coord))
            peak_table.setItem(0, 3, QTableWidgetItem(isotopic_origin))
            peak_table.resizeRowsToContents()

            # Setting label text
            labelInfo = "Selected Scale: " + scale
            scale_label.setText(labelInfo)

            peakwindow.show()
        except Exception:
            QMessageBox.warning(
                self, "Error", "You need to plot the graph first or select a valid row"
            )

    def PeakLimits(self, checked) -> None:
        try:
            if checked:
                # Plotting threshold lines ----------------------------------------------------------------------------
                number_datappoints = len(self.xArray)
                threshold1_x = [(float(self.firstLimit))] * number_datappoints
                max_value_in_y = max(self.yArray)
                min_value_in_y = min(self.yArray)
                threshold1_y = np.linspace(
                    min_value_in_y, max_value_in_y, number_datappoints
                )
                threshold2_x = [(float(self.secondLimit))] * number_datappoints
                self.ax2.plot(
                    threshold1_x, threshold1_y, "--", color="red", linewidth=1.0
                )
                self.ax2.plot(
                    threshold2_x, threshold1_y, "--", color="red", linewidth=1.0
                )
                self.canvas2.draw()
            else:
                # Getting rid of the second plot on the graph (the first limit)
                self.ax2.lines.pop(1)
                # Getting rid of what becomes the second plot on the graph (the second limit)
                self.ax2.lines.pop(1)
                self.canvas2.draw()
        except Exception:
            print("No")

    def ThresholdforPeak(self, checked) -> None:
        try:
            if checked:
                # Getting the threshold for the specific substance------------------------------------------------------
                # Getting symbol
                symbol_sorting = self.substance.split("-")
                dataSymbol = symbol_sorting[1]
                thresholdDir = (
                    self.filepath + "GUI Files/threshold_exceptions.txt"
                )
                with open(thresholdDir, "r") as f:
                    file = f.readlines()
                self.thresholds = "100 by default"
                # Checking if the selected substance has a threshold exception
                for i in file:
                    sortLimits = i.split(" ")
                    symbol = sortLimits[0]
                    if str(symbol) == str(dataSymbol):
                        self.thresholds = str(sortLimits[1]) + str(sortLimits[2])
                # Plotting ---------------------------------------------------------------------------------------------
                number_data_points = len(self.xArray)
                threshold_sorting = self.thresholds.split(",")
                if self.thresholds == "100 by default":
                    threshold_coord_y = 100
                elif self.data[-1] == "t":
                    # sortLimits is set earlier in SelectandDisplay
                    threshold_coord_y_sort = len(threshold_sorting[0])
                    threshold_coord_y = float(
                        threshold_sorting[0][1:threshold_coord_y_sort]
                    )
                    print("n-tot mode")
                else:
                    # sortLimits is set earlier in SelectandDisplay
                    threshold_coord_y_sort = len(threshold_sorting[1])
                    # To splice the number from the string correctly regardless of magnitude
                    cutoff = threshold_coord_y_sort - 2
                    threshold_coord_y = float(threshold_sorting[1][0:cutoff])
                    print("n-g mode")
                # Creating an array to plot line of coords
                threshold_coords_y = [float(threshold_coord_y)] * number_data_points
                threshold_coords_x = self.xArray
                self.ax2.plot(
                    threshold_coords_x,
                    threshold_coords_y,
                    "--",
                    color="black",
                    linewidth=0.5,
                )
                self.canvas2.draw()
            else:
                self.ax2.lines.pop()  # Getting rid of line
                self.canvas2.draw()
        except Exception:
            print("No")
            QMessageBox.warning(self, "Error",
                                "Trouble getting peak limits for this peak \n Contact Rehana.Patel@stfc.ac.uk")

    def importdata(self) -> None:
        """
        Allows user to select a file on their computer to open and analyse.
        """
        filename = QFileDialog.getOpenFileName(self, "Open file", self.filepath)
        if filename[0] == '':
            return
        filepath = filename[0]
        getName = filepath.split("/")

        name = getName[-1].split('.')[0]

        if name[-1] == "f":
            self.Plot(True, filepath, True, name)
        else:
            self.Plot(False, filepath, True, name)

    # ------------------------ PEAK DETECTION BITS ## ------------------------
    def GetPeaks(self) -> None:
        """
        Ask the user for which function to plot the maxima or minima of which substance
        then calls the respective function on that substance
        """

        mainLayout = QVBoxLayout()
        inputForm = QFormLayout()
        inputForm.setObjectName('inputForm')

        elements = QComboBox()
        elements.setEditable(True)
        elements.addItems(self.elementData.keys())
        elements.setMaxVisibleItems(5)

        elements.completer().setCompletionMode(
            QCompleter.UnfilteredPopupCompletion
        )

        elements.completer().setCaseSensitivity(Qt.CaseInsensitive)
        elements.completer().setFilterMode(Qt.MatchContains)

        inputMaxPeaks = QLineEdit()
        inputMaxPeaks.setPlaceholderText(str(self.elementData[elements.currentText()].threshold))
        inputMaxPeaks.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        inputForm.addRow(QLabel("Substance:"), elements)
        buttonBox = QDialogButtonBox()
        resetBtn = buttonBox.addButton(QDialogButtonBox.Reset)
        resetBtn.setText("Reset")
        maximaBtn = buttonBox.addButton(QDialogButtonBox.Yes)
        maximaBtn.setText("Maxima")
        minimaBtn = buttonBox.addButton(QDialogButtonBox.No)
        minimaBtn.setText("Minima")
        cancelBtn = buttonBox.addButton(QDialogButtonBox.Cancel)
        cancelBtn.setText("Cancel")

        inputForm.setSpacing(5)
        mainLayout.addItem(inputForm)
        mainLayout.addWidget(buttonBox)

        inputWindow = QDialog(self)
        inputWindow.setModal(True)

        inputWindow.setWindowTitle("What Should I Plot?")
        inputWindow.setLayout(mainLayout)

        def max():
            self.PlottingPD(self.elementData[elements.currentText()], True)
        maximaBtn.clicked.connect(max)

        def min():
            self.PlottingPD(self.elementData[elements.currentText()], False)
        minimaBtn.clicked.connect(min)

        def close():
            inputWindow.close()
        cancelBtn.clicked.connect(close)

        def changePeaksText():
            inputMaxPeaks.setPlaceholderText(str(self.elementData[elements.currentText()].maxPeaks))
            maxCheck = self.elementData[elements.currentText()].maxima.size != 0
            minCheck = self.elementData[elements.currentText()].minima.size != 0

            maximaBtn.setEnabled(maxCheck)
            minimaBtn.setEnabled(minCheck)

            maximaBtn.setToolTip('' if maxCheck else "No Maximas Found")
            minimaBtn.setToolTip('' if minCheck else "No Minimas Found")

        elements.activated.connect(changePeaksText)
        changePeaksText()
        inputWindow.show()

        def ResetPDPlots() -> None:
            try:
                if self.ax2 is not None:
                    self.ax2.set_visible(False)
                    self.ax2.clear()
                    self.ax2.remove()
                    self.ax2 = None

                self.ax.set_visible(True)
                for element in self.elementData.values():
                    element.isMaxDrawn = False
                    element.isMinDrawn = False
            except KeyError:
                return
            self.canvas.draw()
        resetBtn.clicked.connect(ResetPDPlots)

    def PlottingPD(self, elementData: ElementData, isMax: bool) -> None:

        if isMax and elementData.isMaxDrawn:
            return
        if not isMax and elementData.isMinDrawn:
            return

        if isMax:
            peaksX, peaksY = elementData.maxima[0], elementData.maxima[1]

        else:
            peaksX, peaksY = elementData.minima[0], elementData.minima[1]

        # ! Add substance selection to Peak Detection menu
        # ! Change how points are then plotted
        # Redrawing graph and Peak Detection Limits
        self.ax.set_visible(False)

        if self.ax2 is None:
            self.ax2 = self.figure.add_subplot(111)

        if not elementData.isMaxDrawn and not elementData.isMinDrawn:
            self.ax2.plot(
                elementData.graphData[0],
                elementData.graphData[1],
                "-",
                color=elementData.graphColour,
                alpha=0.6,
                linewidth=0.6,
            )
        self.Threshold()
        self.ax2.set_xscale("log")
        self.ax2.set_yscale("log")
        self.ax2.set(
            xlabel="Energy (eV)", ylabel="Cross section (b)", title=str(self.data)
        )
        if isMax:
            for x, y in zip(peaksX, peaksY):
                self.ax2.plot(x, y, "x", color="black", markersize=4)
                limitXFirst = elementData.maxPeakLimitsX[f"{x}_first"]
                limitYFirst = elementData.maxPeakLimitsY[f"{x}_first"]
                limitXSecond = elementData.maxPeakLimitsX[f"{x}_second"]
                limitYSecond = elementData.maxPeakLimitsY[f"{x}_second"]
                self.ax2.plot(limitXFirst, limitYFirst, marker=2, color="r",
                              markersize=8, gid=f"{self.data}-first_limit")
                self.ax2.plot(limitXSecond, limitYSecond, marker=2, color="r",
                              markersize=8, gid=f"{self.data}-second_limit")
                elementData.isMaxDrawn = True
        else:
            for x, y in zip(peaksX, peaksY):
                self.ax2.plot(x, y, "x", color="black", markersize=4)
                elementData.isMinDrawn = True

                # limitXFirst = elementData.minPeakLimitsX[f"{x}_first"]
                # limitYFirst = elementData.minPeakLimitsY[f"{x}_first"]
                # limitXSecond = elementData.minPeakLimitsX[f"{x}_second"]
                # limitYSecond = elementData.minPeakLimitsY[f"{x}_second"]
                # self.ax2.plot(limitXFirst, limitYFirst, 0, color="r", markersize=8)
                # self.ax2.plot(limitXSecond, limitYSecond, 0, color="r", markersize=8)
        self.figure.tight_layout()
        self.canvas.draw()

    def EditPeaks(self) -> None:
        # Click count to disconnect after two limits have been selected
        if self.plottedSubstances == []:
            QMessageBox.warning(self, "Error", "You have not plotted anything")
            return

        mainLayout = QVBoxLayout()
        inputForm = QFormLayout()
        inputForm.setObjectName('inputForm')

        elements = QComboBox()
        elements.addItems(self.elementData.keys())
        elementPeaks = QComboBox()
        elementPeaks.setMaxVisibleItems(5)

        firstLimitX = QLineEdit()
        firstLimitX.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        secondLimitX = QLineEdit()
        secondLimitX.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        inputForm.addRow(QLabel("Substance:"), elements)
        inputForm.addRow(QLabel("Peak X-Coord:"), elementPeaks)
        inputForm.addRow(QLabel("1st Limit X:"), firstLimitX)
        inputForm.addRow(QLabel("2nd Limit X:"), secondLimitX)

        buttonBox = QDialogButtonBox()
        maximaBtn = buttonBox.addButton(QDialogButtonBox.Yes)
        maximaBtn.setText("Apply")

        cancelBtn = buttonBox.addButton(QDialogButtonBox.Cancel)
        cancelBtn.setText("Cancel")

        inputForm.setSpacing(5)
        mainLayout.addItem(inputForm)
        mainLayout.addWidget(buttonBox)

        inputWindow = QDialog(self)
        inputWindow.setObjectName('editPeaks')

        inputWindow.setModal(True)
        inputWindow.setWindowTitle("Edit Peaks for Substance")
        inputWindow.setLayout(mainLayout)

        def onAccept():
            element = self.elementData[elements.currentText()]
            peak = float(elementPeaks.currentText())
            left = element.maxPeakLimitsX[f"{peak}_first"]
            right = element.maxPeakLimitsX[f"{peak}_second"]
            graphData = element.graphData[(element.graphData[0] >= left) & (element.graphData[0] <= right)]
            simps = integrate_simps(graphData)
            trapz = integrate_trapz(graphData)

            tableMax_x = nearestnumber(element.tableData["Energy (eV)"][1:], peak)

            row = element.tableData[1:].loc[
                (element.tableData["Energy (eV)"][1:].astype(float) == tableMax_x)
            ]
            integral = row["Integral"].iloc[0]

            print(f"Peak: {peak} has bound co-ords ({left},{graphData.iloc[0, 1]}, ({right},{graphData.iloc[-1, 1]})")

            print(f"Simps: {simps}, Trapz {trapz}")

            print(f"Peak: {peak}. Simps has error {abs(integral-simps)}")

            print(f"Peak: {peak}. Trapz has error {abs(integral-trapz)}")

        maximaBtn.clicked.connect(onAccept)
        cancelBtn.clicked.connect(inputWindow.reject)

        def onElementChange():
            element = self.elementData[elements.currentText()]
            elementPeaks.currentIndexChanged.disconnect(onPeakChange)
            elementPeaks.clear()
            if element.maxima[0].size == 0:
                elementPeaks.setEnabled(False)
                firstLimitX.setEnabled(False)
                secondLimitX.setEnabled(False)
                elementPeaks.addItem("Null")
                firstLimitX.setPlaceholderText("Null")
                secondLimitX.setPlaceholderText("Null")
                elementPeaks.currentIndexChanged.connect(onPeakChange)
                return
            elementPeaks.setEnabled(True)
            firstLimitX.setEnabled(True)
            secondLimitX.setEnabled(True)
            elementPeaks.addItems([str(peak) for peak in element.maxima[0]])
            elementPeaks.currentIndexChanged.connect(onPeakChange)
            onPeakChange()

        def onPeakChange():
            element = self.elementData[elements.currentText()]

            peak = elementPeaks.currentText()
            firstLimitX.setPlaceholderText(str(element.maxPeakLimitsX[f"{peak}_first"]))
            secondLimitX.setPlaceholderText(str(element.maxPeakLimitsX[f"{peak}_second"]))

        elements.currentIndexChanged.connect(onElementChange)
        elementPeaks.currentIndexChanged.connect(onPeakChange)
        onElementChange()
        inputWindow.show()

        # ? self.clickcount = 0
        # ? # Ordering peaks
        # ? peak_order = "Rank by eV    (eV) \n"
        # ? for i in range(0, len(self.peakList)):
        # ?     peak_order += str(i) + "    " + str(self.peakList[i]) + "\n"
        # ? # Choose which peak they are editing
        # ? self.peaknum, ok = QInputDialog.getText(self,
        # ?                                         "Peak Editing",
        # ?                                         "Choose which peak to edit by entering its peak "
        # ?                                         "number \n (Rank by eV) \n" + peak_order)
        # ? typecheck = QMessageBox.question(self,
        # ?                                  "Selecting Peak Limits",
        # ?                                  "Do you want to select limits by inputting the coordinates?",
        # ?                                  QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        # ? if typecheck == QMessageBox.Yes:
        # ?     firstLimitX, ok = QInputDialog.getText(
        # ?         self, "Peak Limits in X", "Enter the first peak limit x-coordinate: "
        # ?     )
        # ?     secondLimitX, ok = QInputDialog.getText(
        # ?         self, "Peak Limits in X", "Enter the second peak limit x-coordinate: "
        # ?     )
        # ?     # Finding the corresponding y-value
        # ?     first_limit_y = self.y[self.x.index(firstLimitX)]
        # ?     second_limit_y = self.y[self.x.index(secondLimitX)]
        # ?     peak = self.peakList[int(self.peaknum)]
        # ?     self.peakLimitsX[str(peak) + "_first"] = float(firstLimitX)
        # ?     self.peakLimitsX[str(peak) + "_second"] = float(secondLimitX)
        # ?     self.peakLimitsY[str(peak) + "_first"] = float(first_limit_y)
        # ?     self.peakLimitsY[str(peak) + "_second"] = float(second_limit_y)
        # ?     print("LIMITS: ", self.peakLimitsX)
        # ?     # Re-plotting with new limits
        # ?     # getting list of minima/maxima for plotting again
        # ?     maxima_x = []
        # ?     maxima_y = []
        # ?     for i in self.peakLimitsX.keys():
        # ?         sorting = i.split("_")
        # ?         maxima_x.append(sorting[0])
        # ?         index = self.x.index(float(sorting[0]))
        # ?         maxima_y.append(self.y[index])
        # ?     maxima_x = list(dict.fromkeys(maxima_x))
        # ?     maxima_y = list(dict.fromkeys(maxima_y))
        # ?     maxima_x_float = []
        # ?     for i in maxima_x:
        # ?         maxima_x_float.append(float(i))
        # ?     self.PlottingPD(maxima_x_float, maxima_y)

        # Plotting the individual peak
        # peak = self.peakList[int(self.peaknum)]
        # first_limit_i = self.x.index(self.peakLimitsX[str(peak) + '_first'])
        # second_limit_i = self.x.index(self.peakLimitsX[str(peak) + '_second'])
        # x = self.x[first_limit_i-50:second_limit_i+50]
        # y = self.y[first_limit_i-50:second_limit_i+50]
        # # Clearing the figure
        # self.figure.clear()
        # self.ax = self.figure.add_subplot(111)
        # self.ax.plot(x, y, '-', color='b')
        # self.ax.set(xlabel='eV', ylabel = 'Cross section', title='Peak ' + str(self.peaknum))
        # self.canvas.draw()
        # # Allowing for selecting coordinates
        # self.interact = self.canvas.mpl_connect('button_press_event', self.SelectLimits)

    def SelectLimitsOption(self) -> None:
        # Allowing for selecting coordinates
        if self.plottedSubstances == []:
            QMessageBox.warning(self, "Error", "You have not plotted anything")
            return
        self.interact = self.canvas.mpl_connect("button_press_event", self.SelectLimits)

    def SelectLimits(self, event) -> None:
        if self.clickcount is None:
            self.clickcount = 0
        self.xi, self.yj = event.xdata, event.ydata
        self.clickcount = self.clickcount + 1
        print(self.clickcount)
        # if self.clickcount >= 2:
        #     self.canvas.mpl_disconnect(self.interact)
        print(self.xi, self.yj)
        # Taking note of which coordinates are picked
        peak = self.peakList[int(self.peaknum)]
        if self.clickcount == 1:
            self.firstClickX = self.xi
        if self.clickcount == 2:
            second_click_x = self.xi
            firstLimitX = self.nearestnumber(
                self.x, float(self.firstClickX)
            )  # Finding the nearest x-value on the spectrum to where was clicked
            secondLimitX = self.nearestnumber(self.x, float(second_click_x))
            # Finding the corresponding y-value
            first_limit_y = self.y[self.x.index(firstLimitX)]
            second_limit_y = self.y[self.x.index(secondLimitX)]
            # Altering it in dictionary
            self.peakLimitsX[str(peak) + "_first"] = firstLimitX
            self.peakLimitsX[str(peak) + "_second"] = secondLimitX
            self.peakLimitsY[str(peak) + "_first"] = first_limit_y
            self.peakLimitsY[str(peak) + "_second"] = second_limit_y
            print("LIMITS: ", self.peakLimitsX)
            # Re-plotting with new limits
            # getting list of minima/maxima for plotting again
            maxima_x = []
            maxima_y = []
            for i in self.peakLimitsX.keys():
                sorting = i.split("_")
                maxima_x.append(sorting[0])
                index = self.x.index(float(sorting[0]))
                maxima_y.append(self.y[index])
            maxima_x = list(dict.fromkeys(maxima_x))
            maxima_y = list(dict.fromkeys(maxima_y))
            maxima_x_float = []
            for i in maxima_x:
                maxima_x_float.append(float(i))
            print(maxima_x_float)
            self.PlottingPD(maxima_x_float, maxima_y)
        # Disconnecting clicking
        self.canvas.mpl_disconnect(self.interact)


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    app.setObjectName('MainWindow')

    app.setStyle('Fusion')
    QtGui.QFontDatabase.addApplicationFont('src\\fonts\\RobotoMono-Thin.ttf')
    QtGui.QFontDatabase.addApplicationFont('src\\fonts\\RobotoMono-Regular.ttf')
    QtGui.QFontDatabase.addApplicationFont('src\\fonts\\RobotoMono-Medium.ttf')
    Colours = QtGui.QPalette()
    Colours.setColor(QtGui.QPalette.Window, QtGui.QColor("#4D4D4D"))
    # Colours.setColor(QtGui.QPalette.Button, QtGui.QColor("#FFF"))

    app.setWindowIcon(QIcon("./src/img/final_logo.png"))

    app.setStyleSheet(
        """
        *{
            font-family: 'Roboto Mono';
            font-size: 10pt;
            font-weight: 400;
        }
        QMenuBar{
            background-color: #4D4D4D;
            color: #FFF;
        }
        QAction {
            background-color: #4D4D4D;
            color: #FFF;
        }
        QSplitter::handle:vertical{
            image: url(./src/img/drag-component.svg);
            height: 11px;
        }
        QLabel#numPeakLabel, #thresholdLabel, #orderlabel{
            font: 10pt 'Roboto Mono';
            color: #FFF;
        }

        QPushButton#plotEnergyBtn, #plotTOFBtn, #clearBtn, #pdBtn {
            font: 10pt 'Roboto Mono Medium';
            font-weight: 500;
        }
        QPushButton#plotEnergyBtn:disabled, #plotTOFBtn:disabled, #clearBtn:disabled, #pdBtn:disabled {
            color: #AAA;
        }
        QPushButton#plotEnergyBtn:enabled, #plotTOFBtn:enabled, #clearBtn:enabled, #pdBtn:enabled {
            color: #000;
        }

        QCheckBox#gridCheck, #threshold_check, #label_check, #orderByIntegral, #orderByPeakW {
            font-weight: 500;
        }
        QCheckBox#gridCheck::indicator:unchecked,
                 #threshold_check::indicator:unchecked,
                 #label_check::indicator:unchecked,
                 #orderByIntegral::indicator:unchecked,
                 #orderByPeakW::indicator:unchecked
                 {
                   image: url(./src/img/checkbox-component-unchecked.svg);
                   color: #FFF
                 }
        QCheckBox#gridCheck::indicator:checked,
                 #threshold_check::indicator:checked,
                 #label_check::indicator:checked,
                 #orderByIntegral::indicator:checked,
                 #orderByPeakW::indicator:checked
                 {
                     image: url(./src/img/checkbox-component-checked.svg);
                     color: #FFF
                 }
        QCheckBox#gridCheck:disabled,
                 #threshold_check:disabled,
                 #label_check:disabled,
                 #orderByIntegral:disabled,
                 #orderByPeakW:disabled
                 {
                     color: #888;
                 }
        QCheckBox#gridCheck:enabled,
                 #threshold_check:enabled,
                 #label_check:enabled
        {
            color: #FFF;
        }
        QRadioButton#orderByIntegral:enabled,
                    #orderByPeakW:enabled
                    {
                        color: #FFF;
                    }
        QRadioButton#orderByIntegral::indicator:unchecked,
                    #orderByPeakW::indicator:unchecked
                    {
                        image: url(./src/img/radio-component-unchecked);
                        color: #888;
                    }
        QRadioButton#orderByIntegral::indicator:checked,
                    #orderByPeakW::indicator:checked
                    {
                        image: url(./src/img/radio-component-checked);
                        color: #FFF;
                    }
        QWidget#mainContainer {
            background-color: white;
        }
        QHeaderView {
            font-size: 7.5pt;
        }
        QHeaderView::section:horizontal{
            border-top: 1px solid #000;
            border-bottom: 1px solid #000;
        }
        QHeaderView::section:horizontal:!last{
            border-right: 1px solid #000;
        }
        
        QHeaderView::down-arrow{
            image: url(./src/img/expand-down-component.svg)
        }
        QHeaderView::up-arrow{
            image: url(./src/img/expand-up-component.svg)
        }
        QTableView#dataTable {
            font-size: 8pt;
            border-style: none;
        }
        QDialog{
            background-color: #4D4D4D;
            color: white;
        }
        QDialog#maxPeaks QLabel, #editPeaks QLabel, #thresholdLimit QLabel{
            color: white;
        }
    """
    )

    _ = DatabaseGUI()
    app.setPalette(Colours)
    app.exec()


if __name__ == "__main__":
    main()
