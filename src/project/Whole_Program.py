from __future__ import annotations
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.rcsetup
import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import (
#     FigureCanvasQTAgg as FigureCanvas,
# )
from matplotlib.ticker import AutoMinorLocator
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar
)
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QRegExp, pyqtSignal
from PyQt5.QtGui import QCursor, QRegExpValidator, QIcon

from PyQt5.QtWidgets import (
    QAction,
    QCheckBox,
    QColorDialog,
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
    QLayout,
    QLineEdit,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSplitter,
    QTableView,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,

)
from copy import deepcopy

from pyparsing import Literal

from element.ElementDataStructure import ElementData
from myPyQt.ButtonDelegate import ButtonDelegate
from myPyQt.CustomSortingProxy import CustomSortingProxy
from myPyQt.ExtendedComboBox import ExtendedComboBox
from myPyQt.ExtendedTableModel import ExtendedQTableModel
from myPyQt.InputElementsDialog import InputElementsDialog

from myMatplotlib.CustomFigureCanvas import FigureCanvas

from helpers.nearestNumber import nearestnumber
from helpers.getRandomColor import getRandomColor
from helpers.getWidgets import getLayoutWidgets


# todo -------------------- Issues/Feature TODO list --------------------
# todo - Add periodic table GUI for selection.
# todo - Maximas after changing threshold wont have correct annotations due to integral and peak widths not calculated
# todo   correctly yet.
# todo - Matplotlib icons
# todo - PyQt5 Unit Testing
# todo - Incorporate multiprocessing and multithreading
# todo - Fix issues with Maxima not displaying after zoom


# ? Should this ask for the filepath or just be require to be in the format as seen in the repository,
# ? Download the repository and run the program without altering the file structure, will save having
# ? to enter filepaths in console during start up.


# Asking for filepath where the user has saved script
# filepath is where the data and the code has been saved. The sourceFilepath is the path to the latest data folder
# ! Maybe Change back to inputs if requried

#  input('Enter the filepath where the latest NRCA code data folder is \n For Example:'
#                         'C://Users/ccj88542/NRCA/Rehana/Latest/main/data: \n')

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
    Class responsible for creating and manipulating the GUI, used in selecting and graphing the data of elements or
    isotopes within the NRTI/NRCA Database.
    """
    resized = pyqtSignal()

    # init constructure for classes
    def __init__(self) -> None:
        """
        Initialisator for DatabaseGUI class
        """
        # Allows for adding more things to the QWidget template
        super(DatabaseGUI, self).__init__()

        self.styleWindows = "Fusion"

        self.styleMain = """
        #mainWindow{{
            background-color: {bg_color};
        }}
        *{{
            font-family: 'Roboto Mono';
            font-size: 10pt;
            font-weight: 400;
        }}
        QMenuBar{{
            background-color: {bg_color};
            color: {text_color};
        }}
        QComboBox{{
            font-family: 'Roboto Mono';
            font-size: 10pt;
            font-weight: 400;
        }}
        QAction {{
            background-color: {bg_color};
            color: {text_color};
        }}
        QSplitter::handle:vertical{{
            image: url(./src/img/drag-component.svg);
            height: 11px;
        }}
        QLabel#numPeakLabel, #thresholdLabel, #orderlabel, #compoundLabel{{
            font: 10pt 'Roboto Mono';
            color: {text_color};
        }}

        QPushButton#plotEnergyBtn, #plotTOFBtn, #clearBtn, #pdBtn, #compoundBtn{{
            font: 10pt 'Roboto Mono Medium';
            font-weight: 500;
        }}
        QPushButton#plotEnergyBtn:disabled,
                   #plotTOFBtn:disabled,
                   #clearBtn:disabled,
                   #pdBtn:disabled,
                   #compoundBtn:disabled{{
            color: #AAA;
        }}
        QPushButton#plotEnergyBtn:enabled,
                   #plotTOFBtn:enabled,
                   #clearBtn:enabled,
                   #pdBtn:enabled,
                   #compoundBtn:enabled {{
            color: #000;
        }}

        QCheckBox#gridCheck, #threshold_check, #label_check, #orderByIntegral, #orderByPeakW {{
            font-weight: 500;
        }}
        QCheckBox#grid_check::indicator:unchecked,
                 #threshold_check::indicator:unchecked,
                 #label_check::indicator:unchecked
                 {{
                   image: url(./src/img/checkbox-component-unchecked.svg);
                   color: {text_color};
                 }}
        QCheckBox#grid_check::indicator:checked,
                 #threshold_check::indicator:checked,
                 #label_check::indicator:checked
                 {{
                     image: url(./src/img/checkbox-component-checked.svg);
                     color: {text_color};
                 }}
        QCheckBox#grid_check:disabled,
                 #threshold_check:disabled,
                 #label_check:disabled
                 {{
                     color: #AAA;
                 }}
        QCheckBox#grid_check:enabled,
                 #threshold_check:enabled,
                 #label_check:enabled
        {{
            color: {text_color};
        }}
        QRadioButton#orderByIntegral:enabled,
                    #orderByPeakW:enabled
                    {{
                        color: {text_color};
                    }}
        QRadioButton#orderByIntegral::indicator:unchecked,
                    #orderByPeakW::indicator:unchecked
                    {{
                        image: url(./src/img/radio-component-unchecked);
                        color: #AAA;
                    }}
        QRadioButton#orderByIntegral::indicator:checked,
                    #orderByPeakW::indicator:checked
                    {{
                        image: url(./src/img/radio-component-checked);
                        color: {text_color};
                    }}

        QWidget#mainContainer {{
            background-color: {text_color};
        }}
        QHeaderView {{
            font-size: 7.5pt;
        }}
        QHeaderView::section:horizontal{{
            border-top: 1px solid #000;
            border-bottom: 1px solid #000;
        }}
        QHeaderView::section:horizontal:!last{{
            border-right: 1px solid #000;
        }}

        QHeaderView::down-arrow{{
            image: url(./src/img/expand-down-component.svg);
        }}
        QHeaderView::up-arrow{{
            image: url(./src/img/expand-up-component.svg);
        }}
        QTableView#dataTable {{
            font-size: 8pt;
            border-style: none;
        }}

        QMessageBox QLabel{{
            color: {text_color};
        }}
        QDialog {{
            background-color: {bg_color};
        }}
        QDialog#inputWindow
        {{
            color: {text_color};
            background-color: {bg_color};
        }}
        QDialog#inputWindow QLabel{{
            color: {text_color};
        }}
        QDialog#optionsDialog QCombobox{{
            background-color: {text_color};
        }}
        """

        # Setting global variables
        self.data = None
        self.x = []  # ! Depreciated
        self.y = []  # ! Depreciated
        self.xArray = []
        self.yArray = []
        self.numRows = None
        self.numTotPeaks = []

        self.ax = None
        self.ax2 = None
        self.canvas2 = None
        self.plotFilepath = None
        self.firstLimit = None
        self.secondLimit = None
        self.plotCount = -1
        self.graphs = dict()
        self.annotations = []
        self.localHiddenAnnotations = []
        self.plottedSubstances = []
        self.rows = None
        self.tableLayout = dict()
        self.arrays = dict()
        self.selectionName = None
        self.xi = None
        self.yj = None
        self.peaknum = None
        self.interact = None
        self.clickcount = None
        self.gridSettings = {"which": "major", "axis": "both", "color": "#444"}

        self.peakInfoIsNull = None
        self.graphData = None
        self.peakLimitsX = dict()
        self.peakLimitsY = dict()
        self.peakList = None
        self.orderByIntegral = True
        self.firstClickX = None
        self.filepath = f"{os.path.dirname(__file__)}\\"
        self.dataFilepath = f"{self.filepath}data\\Graph Data\\"
        self.elementData = dict()
        self.elementDataNames = []
        self.compoundData = dict()
        self.isCompound = False

        self.maxPeak = 50
        self.thresholds = dict()

        self.distributionDir = self.filepath + "data\\Distribution Information\\"
        self.defaultDistributions = dict()
        self.elementDistributions = dict()

        thresholdFilepath = self.filepath + "data\\threshold_exceptions.txt"

        file = pd.read_csv(thresholdFilepath, header=None)

        for line in file.values:
            symbol = line[0].split(' ')[0]
            self.thresholds[symbol] = (line[0].split(' ')[1].replace('(', ''), line[1].replace(')', ''))

        dist_filePaths = [f for f in os.listdir(self.distributionDir) if f.endswith(".csv")]
        for filepath in dist_filePaths:
            name = filepath[:-4]
            dist = pd.read_csv(f"{self.distributionDir}{filepath}", header=None)
            self.defaultDistributions[name] = dict({d[0]: d[1] for d in dist.values})

        self.elementDistributions = deepcopy(self.defaultDistributions)

        self.setStyleSheet(self.styleMain.format(bg_color="#202020", text_color="#FFF"))
        self.initUI()
        self.setAcceptDrops(True)

    def initUI(self) -> None:
        """
        ``initUI``
        Creates the UI.
        """
        self.setObjectName('mainWindow')
        self.setGeometry(350, 50, 1600, 900)
        self.setWindowTitle("NRTI/NRCA Viewing Database")
        self.resized.connect(self.adjustCanvas)

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
        menubar = QMenuBar(self)
        menubar.setObjectName("menubar")

        newAction = QAction(QIcon("./src/img/add-component.svg"), "&New", self)
        newAction.setShortcut("Ctrl+N")
        newAction.triggered.connect(self.clear)

        importAction = QAction(QIcon("./src/img/upload-component.svg"), "&Import Data", self)
        importAction.setShortcut("Ctrl+I")

        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(newAction)
        fileMenu.addAction(importAction)
        importAction.triggered.connect(self.importdata)

        # * ----------------------------------------------

        # ¦ --------------- MENU BAR - EDIT --------------
        # Creates menu bar and add actions
        editpeakAction = QAction(QIcon("./src/img/edit-component.svg"), "&Edit Peak Limits", self)
        editpeakAction.setShortcut("Ctrl+E")
        editpeakAction.triggered.connect(self.editPeakLimits)

        selectlimitsAction = QAction(QIcon("./src/img/select-component.svg"), "&Select Limits", self)
        selectlimitsAction.setShortcut("Ctrl+L")
        # ! selectlimitsAction.triggered.connect(self.connectClickLimits)

        editThresholdAction = QAction(QIcon("./src/img/edit-component.svg"), "&Edit Threshold", self)
        editThresholdAction.setShortcut("Ctrl+Shift+T")
        editThresholdAction.triggered.connect(self.editThresholdLimit)

        editDistribution = QAction(QIcon("./src/img/edit-component.svg"), "&Edit Distribution", self)
        editDistribution.setShortcut("Ctrl+Shift+D")
        editDistribution.triggered.connect(self.editDistribution)
        # fileMenu.addAction(saveAction)

        editMenu = menubar.addMenu("&Edit")
        editMenu.addAction(editpeakAction)
        editMenu.addAction(selectlimitsAction)
        editMenu.addAction(editThresholdAction)
        editMenu.addAction(editDistribution)

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

        # ¦ --------------- MENU BAR - VIEW --------------

        viewMenu = menubar.addMenu("&View")
        appearenceMenu = viewMenu.addMenu("Appearence")

        defaultAppearence = QAction(QIcon("./src/img/changeAppearence-component.svg"), "&Dark Theme", self)
        defaultAppearence.setShortcut("Ctrl+Shift+1")
        defaultAppearence.triggered.connect(self.viewDarkStyle)

        windowsAppearence = QAction(QIcon("./src/img/changeAppearence-component.svg"), "&Light Theme", self)
        windowsAppearence.setShortcut("Ctrl+Shift+2")
        windowsAppearence.triggered.connect(self.viewLightStyle)

        highContrastAppearence = QAction(QIcon("./src/img/changeAppearence-component.svg"), "&High Contrast", self)
        highContrastAppearence.setShortcut("Ctrl+Shift+3")
        highContrastAppearence.triggered.connect(self.viewHighContrastStyle)

        appearenceMenu.addAction(defaultAppearence)
        appearenceMenu.addAction(windowsAppearence)
        appearenceMenu.addAction(highContrastAppearence)

        # * ----------------------------------------------

        # ¦ ------------- MENU BAR - OPTIONS -------------

        optionsMenu = menubar.addMenu("&Options")

        gridlineOptions = QAction(QIcon("./src/img/grid-component.svg"), "&Grid Line Settings", self)
        gridlineOptions.setShortcut("Ctrl+Shift+G")
        gridlineOptions.triggered.connect(self.gridLineOptions)

        maxPeaksOption = QAction(QIcon("./src/img/edit-component.svg"), "&Max Peak Quantity", self)
        maxPeaksOption.setShortcut("Ctrl+Shift+Q")
        maxPeaksOption.triggered.connect(self.editMaxPeaks)

        optionsMenu.addAction(gridlineOptions)
        optionsMenu.addAction(maxPeaksOption)

        # * ----------------------------------------------

        # ¦ --------------- Combobox Group ---------------
        # For copying data directory to local directory for plotting later
        # Establishing source and destination directories

        # Creating a list of substances stored in the NRCA database data directory
        self.selectionName = [None]
        for file in os.listdir(f"{self.filepath}data\\Graph Data\\"):
            filename = os.fsdecode(file)
            if ".csv" not in filename[-4:]:
                continue
            filename = filename[:-4]
            self.selectionName.append(filename)

        # Creating combo box (drop down menu)
        self.combobox = ExtendedComboBox()
        self.combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.combobox.setObjectName("combobox")

        self.combobox.addItems(self.selectionName)
        # self.combobox.setEditable(True)
        self.combobox.lineEdit().setPlaceholderText("Select an Isotope / Element")
        # self.combobox.setInsertPolicy(QComboBox.NoInsert)
        # self.combobox.setMaxVisibleItems(15)

        # completer = CustomQCompleter(self.combobox)
        # completer.setCompletionMode(QCompleter.PopupCompletion)
        # completer.setModel(self.combobox.model())

        # self.combobox.setCompleter(completer)

        sidebarLayout.addWidget(self.combobox)

        # Upon selecting an option, it records the option
        # and connects to the method 'displayData'
        self.combobox.editTextChanged.connect(lambda: self.plotSelectionProxy(
            index=self.combobox.currentIndex(),
            comboboxName=self.combobox.objectName()
        ))

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
        plotEnergyBtn.clicked.connect(self.updateGuiData)

        plotTOFBtn = QPushButton("Plot in ToF", self)
        plotTOFBtn.setCursor(pointingCursor)
        plotTOFBtn.setObjectName("plotTOFBtn")
        plotTOFBtn.__name__ = "plotToFBtn"
        plotTOFBtn.resize(plotTOFBtn.sizeHint())
        plotTOFBtn.setEnabled(False)
        self.btnLayout.addWidget(plotTOFBtn)
        plotTOFBtn.clicked.connect(lambda: self.updateGuiData(tof=True))

        clearBtn = QPushButton("Clear All", self)
        clearBtn.setObjectName("clearBtn")
        clearBtn.setCursor(pointingCursor)
        clearBtn.__name__ = "clearBtn"
        clearBtn.resize(clearBtn.sizeHint())
        clearBtn.setEnabled(False)
        self.btnLayout.addWidget(clearBtn)
        clearBtn.clicked.connect(self.clear)

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

        self.gridCheck = QCheckBox("Grid Lines", self)
        self.gridCheck.setCursor(pointingCursor)
        self.gridCheck.setObjectName("grid_check")
        self.gridCheck.__name__ = "gridCheck"

        self.gridCheck.setEnabled(False)
        self.toggleLayout.addWidget(self.gridCheck)
        self.gridCheck.stateChanged.connect(lambda: self.toggleGridlines(self.gridCheck.isChecked(),
                                                                         **self.gridSettings))

        self.thresholdCheck = QCheckBox("Peak Detection Limits", self)
        self.thresholdCheck.setCursor(pointingCursor)
        self.thresholdCheck.setObjectName("threshold_check")
        self.thresholdCheck.__name__ = "threshold_check"
        self.thresholdCheck.setEnabled(False)
        self.toggleLayout.addWidget(self.thresholdCheck)
        self.thresholdCheck.stateChanged.connect(self.toggleThreshold)

        self.peakLabelCheck = QCheckBox("Hide Peak Labels", self)
        self.peakLabelCheck.setCursor(pointingCursor)
        self.peakLabelCheck.setObjectName("label_check")
        self.peakLabelCheck.__name__ = "labelCheck"
        self.peakLabelCheck.setEnabled(False)
        self.toggleLayout.addWidget(self.peakLabelCheck)
        self.peakLabelCheck.stateChanged.connect(self.toggleAnnotations)

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
        self.byIntegralCheck.clicked.connect(self.onPeakOrderChange)
        self.byPeakWidthCheck = QRadioButton(radioBtnGroup, text="By Peak Width")
        self.byPeakWidthCheck.setObjectName('orderByPeakW')
        self.byPeakWidthCheck.clicked.connect(self.onPeakOrderChange)

        peakCheckLayout.addWidget(self.byIntegralCheck)
        peakCheckLayout.addWidget(self.byPeakWidthCheck)

        peakOrderLayout.addWidget(peakOrderLabel)
        peakOrderLayout.addItem(peakCheckLayout)

        sidebarLayout.addLayout(peakOrderLayout)

        # * -----------------------------------------------

        # ¦ ----------- Compound Creater Group ------------

        compoundCreaterLayout = QVBoxLayout()
        compoundCreaterLayout.setSpacing(5)
        compoundLabel = QLabel(self, text="Compound Creation")
        compoundLabel.setObjectName("compoundLabel")
        compoundCreaterBtn = QPushButton("Create Compound", self)
        compoundCreaterBtn.setObjectName("compoundBtn")
        compoundCreaterBtn.clicked.connect(self.createCompound)
        self.compoundCombobox = ExtendedComboBox()
        self.compoundCombobox.lineEdit().setPlaceholderText("Select a Compound")
        self.compoundCombobox.setObjectName("compoundComboBox")
        self.compoundCombobox.editTextChanged.connect(lambda: self.plotSelectionProxy(
            index=self.compoundCombobox.currentIndex(),
            comboboxName=self.compoundCombobox.objectName()
        ))
        self.compoundNames = [None]
        for file in os.listdir(f"{self.filepath}data\\Graph Data\\Compound Data\\"):
            filename = os.fsdecode(file)
            if ".csv" not in filename[-4:]:
                continue
            filename = filename[:-4]
            self.compoundNames.append(filename)
        self.compoundCombobox.addItems(self.compoundNames)
        compoundCreaterLayout.addWidget(compoundLabel)
        compoundCreaterLayout.addWidget(compoundCreaterBtn)
        compoundCreaterLayout.addWidget(self.compoundCombobox)

        sidebarLayout.addLayout(compoundCreaterLayout)

        # * -----------------------------------------------

        # ¦ ----------------- Plot Canvas -----------------
        self.figure = plt.figure()  # Creating canvas to plot graph on and toolbar
        self.canvas = FigureCanvas(self.figure, self)
        self.canvas.__name__ = "canvas"
        self.canvas.mpl_connect('pick_event', self.hideGraph)
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

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        """
        ``resizeEvent`` On resize of connected widget event handler.

        Args:
            event (QtGui.QResizeEvent): _description_

        Returns:
            ``None``
        """
        self.resized.emit()
        return super(DatabaseGUI, self).resizeEvent(event)

    def adjustCanvas(self) -> None:
        """
        ``adjustCanvas`` Apply tight layout to figure.
        """
        self.figure.tight_layout()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        """
        ``dragEnterEvent`` handles file drag enter event and verification

        Args:
            ``event`` (QDragEnterEvent): Event triggerd on mouse dragging into the window.
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
        ``dropEvent`` handles the drop event and calls to plot each data file

        Args:
            ``event`` (QDropEvent): PyQtEvent
        """
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            name = filepath.split('/')[-1].split('.')[0]
            self.updateGuiData(False, filepath, True, name)

    def editPeakLimits(self) -> None:
        """
        ``editPeakLimits`` Edit Peaks opens a dialog window to alter limits of integration for peaks of the selected element, recaluating
        the integral and peak widths to place into the table.
        """
        # Click count to disconnect after two limits have been selected
        if self.plottedSubstances == []:
            QMessageBox.warning(self, "Error", "You have not plotted anything")
            return

        optionsWindow = InputElementsDialog(self, self.styleSheet())

        optionsWindow.elements.addItems(self.elementData.keys())
        optionsWindow.elements.setMaxVisibleItems(5)

        elementPeaks = ExtendedComboBox()

        firstLimitX = QLineEdit()
        firstLimitX.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        secondLimitX = QLineEdit()
        secondLimitX.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        optionsWindow.inputForm.addRow(QLabel("Peak X-Coord:"), elementPeaks)
        optionsWindow.inputForm.addRow(QLabel("1st Limit X:"), firstLimitX)
        optionsWindow.inputForm.addRow(QLabel("2nd Limit X:"), secondLimitX)

        maximaBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Ok)
        maximaBtn.setText("Apply")
        cancelBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Cancel)

        optionsWindow.inputForm.setSpacing(5)
        optionsWindow.mainLayout.insertItem(1, optionsWindow.inputForm)

        optionsWindow.setWindowTitle("Edit Peaks for Substance")
        optionsWindow.mainLayout.setSizeConstraint(QLayout.SetFixedSize)
        optionsWindow.setLayout(optionsWindow.mainLayout)
        elements = optionsWindow.elements

        def onAccept():

            elementName = elements.itemText(elements.currentIndex() or 0)
            element = self.elementData[elementName]
            peak = float(elementPeaks.currentText())
            leftLimit = float(firstLimitX.placeholderText() if firstLimitX.text(
            ) == '' else firstLimitX.text())
            rightLimit = float(secondLimitX.placeholderText() if secondLimitX.text(
            ) == '' else secondLimitX.text())

            tableMax_x = nearestnumber(element.tableData["Energy (eV)"][1:], peak)

            row = element.tableData[1:].loc[
                (element.tableData["Energy (eV)"][1:].astype(float) == tableMax_x)
            ]
            integral = row["Integral"].iloc[0]

            result = self.elementData[elementName].PeakIntegral(leftLimit, rightLimit)

            print(f"Peak: {peak}\n")
            print(f"Integral: {integral}\t-\tEstimate: {result}")
        maximaBtn.clicked.connect(onAccept)
        cancelBtn.clicked.connect(optionsWindow.reject)

        def onElementChange():

            element = self.elementData[elements.currentText()]
            elementPeaks.currentIndexChanged.disconnect(onPeakChange)

            elementPeaks.clear()
            if element.maxima[0].size == 0 or element.maxPeakLimitsX == {}:
                elementPeaks.setEnabled(False)
                firstLimitX.setEnabled(False)
                secondLimitX.setEnabled(False)
                maximaBtn.setEnabled(False)
                elementPeaks.setCurrentText("Null")
                firstLimitX.setPlaceholderText("Null")
                secondLimitX.setPlaceholderText("Null")
                elementPeaks.currentIndexChanged.connect(onPeakChange)
                return
            elementPeaks.setEnabled(True)
            firstLimitX.setEnabled(True)
            secondLimitX.setEnabled(True)
            elementPeaks.addItems([str(peak) for peak in element.maxima[0] if element.maxPeakLimitsX.get(peak, False)])
            elementPeaks.currentIndexChanged.connect(onPeakChange)

            onPeakChange()

        def onPeakChange():

            element = self.elementData[elements.currentText()]

            if element.maxPeakLimitsX == {}:
                elementPeaks.setCurrentText("Null")
                firstLimitX.setPlaceholderText("Null")
                secondLimitX.setPlaceholderText("Null")
                maximaBtn.setEnabled(False)
                return
            peak = float(elementPeaks.currentText())
            firstLimitX.setPlaceholderText(str(element.maxPeakLimitsX[peak][0]))
            secondLimitX.setPlaceholderText(str(element.maxPeakLimitsX[peak][1]))

        def onLimitChange():
            limitLeft = firstLimitX.placeholderText() if firstLimitX.text(
            ) == '' else firstLimitX.text()
            limitRight = secondLimitX.placeholderText() if secondLimitX.text(
            ) == '' else secondLimitX.text()
            peak = float(elementPeaks.currentText())
            if limitLeft == 'Null' or limitRight == 'Null':
                maximaBtn.setEnabled(False)
                return
            if float(limitLeft) > peak or float(limitRight) < peak:
                maximaBtn.setEnabled(False)
                return
            maximaBtn.setEnabled(True)
        optionsWindow.elements.currentIndexChanged.connect(onElementChange)
        elementPeaks.currentIndexChanged.connect(onPeakChange)
        firstLimitX.textChanged.connect(onLimitChange)
        secondLimitX.textChanged.connect(onLimitChange)

        onElementChange()
        optionsWindow.setModal(False)
        optionsWindow.show()

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
        # self.interact = self.canvas.mpl_connect('button_press_event', self.selectLimits)

    def editDistribution(self) -> None:
        """
        ``editDistribution`` Opens a dialog window with options to alter the natural abundence of elements and compounds
        updating the graph data of any relevant plots.
        """

        optionsWindow = InputElementsDialog(self, self.styleSheet())
        optionsWindow.elements.addItems(
            [el for el in self.combobox.getAllItemText() if 'element' in el])
        optionsWindow.elements.addItems(self.compoundCombobox.getAllItemText())

        totalLabel = QLabel()

        applyBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Apply)
        applyBtn.setEnabled(False)
        applyBtn.setText("Apply")
        resetBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Reset)
        cancelBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Cancel)

        optionsWindow.mainLayout.setSizeConstraint(QLayout.SetFixedSize)
        optionsWindow.setWindowTitle("Edit Distribution")
        optionsWindow.setLayout(optionsWindow.mainLayout)

        optionsWindow.mainLayout.insertWidget(len(optionsWindow.children()) - 2, totalLabel)

        elements = optionsWindow.elements

        def onAccept():

            elementName = elements.itemText(elements.currentIndex() or 0)
            if elementName == '':
                return
            for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget):

                title = widget.findChild(QLabel).text()[:-1]
                if widget.findChild(QLineEdit).text() == '':
                    dist = float(widget.findChild(QLineEdit).placeholderText())
                else:
                    dist = float(widget.findChild(QLineEdit).text())
                # fadeEffect = QtWidgets.QGraphicsColorizeEffect(widget.findChild(QLineEdit))
                # fadeEffect.setColor(QColor(76, 143, 38))

                # fadeAnim = QPropertyAnimation(fadeEffect, b"color")
                # fadeAnim.setStartValue("QLineEdit{ color: rgb(76, 143, 38);}")
                # fadeAnim.setKeyValueAt(0.5, "QLineEdit { color: rgb(120, 143, 108);}")
                # fadeAnim.setEndValue("QLineEdit { color: rgb(255, 255, 255);}")

                # fadeAnim.setDuration(1000)
                # fadeAnim.setLoopCount(1)

                self.elementDistributions[elementName][title] = dist

            for title, Tof in self.plottedSubstances:

                if elementName == title:
                    title = f"{title}-{'ToF' if Tof else 'Energy'}"

                    self.elementData[title].distributions = self.elementDistributions[elementName]

                    self.elementData[title].isDistAltered = True
                    self.elementData[title].isGraphDrawn = False
                    self.isCompound = self.elementData[title].isCompound
                    self.data = elementName

                    # if self.elementData[title].distributions == self.elementData[title].defaultDist:
                    #     self.Plot(tof=Tof)
                    # else:
                    self.updateGuiData(tof=Tof, distAltered=True)
                    break

            # fadeAnim.start(QAbstractAnimation.DeleteWhenStopped)
        applyBtn.clicked.connect(onAccept)
        cancelBtn.clicked.connect(optionsWindow.reject)

        def onReset():
            onElementChange(reset=True)
            applyBtn.setEnabled(True)
        resetBtn.clicked.connect(onReset)

        def onElementChange(index=None, reset: bool = False):

            elementName = elements.itemText(elements.currentIndex() or 0)
            if elementName == '':
                elements.setCurrentIndex(0)
                return
            totalLabel.setStyleSheet("color: {text_color};")
            for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget):
                if widget.objectName() == "isotopeDistribution":
                    optionsWindow.mainLayout.removeWidget(widget)
                    widget.deleteLater()

            total = 0
            acc = str(max([len(str(a)) - 2 for a in self.defaultDistributions[elementName].values()] + [2]))
            if reset:
                items = self.defaultDistributions
            else:
                items = self.elementDistributions
            for i, (name, dist) in enumerate(items[elementName].items()):
                total += dist
                sublayout = QHBoxLayout()
                proxyWidget = QWidget()
                newQLineEdit = QLineEdit()

                newQLineEdit.setValidator(QRegExpValidator(
                    QRegExp("(0?(\\.[0-9]{1," + acc + "})?|1(\\.0{1," + acc + "})?)")))
                newQLineEdit.setPlaceholderText(str(dist))
                title = QLabel(f"{name}:")

                sublayout.addWidget(title)
                sublayout.addWidget(newQLineEdit)
                sublayout.setSpacing(1)
                proxyWidget.setLayout(sublayout)
                proxyWidget.setFixedHeight(38)
                proxyWidget.setObjectName("isotopeDistribution")
                newQLineEdit.textChanged.connect(onDistributionChange)
                optionsWindow.mainLayout.insertWidget(i + 1, proxyWidget)
            optionsWindow.updateGeometry()
            totalLabel.setText(f"Total: {round(total, int(acc)-1)}")
        optionsWindow.elements.setFocus()
        optionsWindow.elements.currentIndexChanged.connect(onElementChange)

        def onDistributionChange():

            elementName = elements.itemText(elements.currentIndex() or 0)
            total: float = 0
            acc = min([len(str(a)) - 2 for a in self.defaultDistributions[elementName].values()])
            for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget):
                lineEdit = widget.findChild(QLineEdit)
                distribution = lineEdit.placeholderText() if lineEdit.text() == '' else lineEdit.text()
                if distribution == ".":
                    continue
                total += float(distribution)
            total = round(total, acc)
            totalLabel.setText(f"Total: {total}")
            applyBtn.setEnabled(False)
            if total < 1:
                totalLabel.setStyleSheet("color: #FFF;")
            elif total > 1:
                totalLabel.setStyleSheet("color: #F00;")
            else:
                totalLabel.setStyleSheet("color: #0F0;")
                applyBtn.setEnabled(True)

        onElementChange()
        optionsWindow.setModal(False)
        optionsWindow.show()

    # def connectClickLimits(self) -> None:
    #     # Allowing for selecting coordinates
    #     if self.plottedSubstances == []:
    #         QMessageBox.warning(self, "Error", "You have not plotted anything")
    #         return
    #     self.interact = self.canvas.mpl_connect("button_press_event", self.selectLimits)

    def selectLimits(self, event) -> None:
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

    def editThresholdLimit(self) -> None:
        """
        ``editThresholdLimit`` Creates a GUI to alter the threshold value for a selected graph, recomputing maximas and
        drawing the relevant annotations
        """
        if self.elementData == {}:
            return

        optionsWindow = InputElementsDialog(self, self.styleSheet())
        optionsWindow.inputForm.windowTitle = "Threshold Input"

        elements = optionsWindow.elements

        elements.addItems(self.elementData.keys())

        inputThreshold = QLineEdit()
        inputThreshold.setPlaceholderText(str(self.elementData[elements.currentText()].threshold))
        inputThreshold.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        optionsWindow.inputForm.addRow(QLabel("Threshold:"), inputThreshold)

        applyBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Apply)
        cancelBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Cancel)
        applyBtn.setEnabled(False)

        optionsWindow.setWindowTitle("Edit Threshold Value")
        optionsWindow.mainLayout.setSizeConstraint(QLayout.SetFixedSize)

        optionsWindow.mainLayout.insertItem(1, optionsWindow.inputForm)
        optionsWindow.setLayout(optionsWindow.mainLayout)

        def close():
            optionsWindow.close()
        cancelBtn.clicked.connect(close)

        def onElementChange():
            inputThreshold.setPlaceholderText(str(self.elementData[elements.currentText()].threshold))
        elements.currentTextChanged.connect(onElementChange)

        def onThresholdTextChange():
            if inputThreshold.text() == '':
                applyBtn.setEnabled(False)
            else:
                applyBtn.setEnabled(True)
        inputThreshold.textChanged.connect(onThresholdTextChange)

        def onAccept():
            substance_name = elements.currentText()
            if inputThreshold.text() == '':
                return
            threshold_value = float(inputThreshold.text())

            self.elementData[substance_name].threshold = threshold_value
            self.elementData[substance_name].UpdatePeaks()
            self.toggleThreshold()
            self.drawAnnotations(self.elementData[substance_name])
            for element in self.elementData.values():
                if element.isMaxDrawn:
                    self.PlottingPD(element, True)
                if element.isMinDrawn:
                    self.PlottingPD(element, False)
        applyBtn.clicked.connect(onAccept)

        optionsWindow.setModal(False)
        optionsWindow.show()

    def gridLineOptions(self):
        """
        ``gridLineOptions`` Opens a dialog with settings related to the gridlines of the canvas.
        Options include: Which axis to plot gridlines for, which type; major, minor or both ticks, as well as color.
        """

        optionsWindowDialog = QDialog()
        optionsWindowDialog.setWindowTitle("Gridline Options")
        mainLayout = QVBoxLayout()
        formLayout = QFormLayout()

        gridlineLayout = QHBoxLayout()
        gridlineGroup = QGroupBox()

        majorRadioBtn = QRadioButton(text="Major")
        majorRadioBtn.setObjectName("gridline")
        majorRadioBtn.setChecked(True)
        minorRadioBtn = QRadioButton(text="Minor")
        minorRadioBtn.setObjectName("gridline")
        bothRadioBtn = QRadioButton(text="Both")
        bothRadioBtn.setObjectName("gridline")

        gridlineLayout.addWidget(majorRadioBtn)
        gridlineLayout.addWidget(minorRadioBtn)
        gridlineLayout.addWidget(bothRadioBtn)

        gridlineGroup.setLayout(gridlineLayout)

        axisLayout = QHBoxLayout()
        axisGroup = QGroupBox()

        xAxisRadioBtn = QRadioButton(text="X")
        xAxisRadioBtn.setObjectName("axis")
        yAxisRadioBtn = QRadioButton(text="Y")
        yAxisRadioBtn.setObjectName("axis")
        bothAxisRadioBtn = QRadioButton(text="Both")
        bothAxisRadioBtn.setObjectName("axis")
        bothAxisRadioBtn.setChecked(True)

        axisLayout.addWidget(xAxisRadioBtn)
        axisLayout.addWidget(yAxisRadioBtn)
        axisLayout.addWidget(bothAxisRadioBtn)

        axisGroup.setLayout(axisLayout)

        gridColorDialog = QColorDialog()
        gridColorDialog.setCurrentColor(QtGui.QColor(self.gridSettings["color"]))
        gridColorBtn = QPushButton()
        gridColorBtn.setStyleSheet(f"margin: 5px; background-color: {self.gridSettings['color']};")

        formLayout.addRow(QLabel("Gridline Options:"), gridlineGroup)
        formLayout.addRow(QLabel("Axis Options:"), axisGroup)
        formLayout.addRow(QLabel("Gridline Color:"), gridColorBtn)

        buttonBox = QDialogButtonBox()

        onResetBtn = buttonBox.addButton(QDialogButtonBox.Reset)
        onAcceptBtn = buttonBox.addButton(QDialogButtonBox.Apply)
        onCancelBtn = buttonBox.addButton(QDialogButtonBox.Cancel)

        mainLayout.addLayout(formLayout)
        mainLayout.addWidget(buttonBox)

        optionsWindowDialog.setLayout(mainLayout)

        # map(lambda radio: radio.g.connect(lambda: onRadioCheck("axis", radio)),
        #     getLayoutWidgets(axisLayout, QRadioButton))
        # map(lambda radio: radio.clicked.connect(lambda: onRadioCheck("gridline", radio)),
        #     getLayoutWidgets(gridlineLayout, QRadioButton))

        # def onRadioCheck(group: str, radio: QRadioButton):
        #     radioBtns = getLayoutWidgets(QRadioButton)
        #     map(lambda radio: radio.setChecked(False),
        #         [radio for radio in radioBtns if radio.objectName() == group])
        #     radio.setChecked(True)

        def openColorDialog():
            optionsWindowDialog.blockSignals(True)
            gridColorDialog.setModal(True)
            gridColorDialog.show()
        gridColorBtn.clicked.connect(openColorDialog)

        def onColorPick():
            optionsWindowDialog.blockSignals(False)
            gridColorBtn.setStyleSheet(
                f"margin: 5px; background-color: {str(gridColorDialog.selectedColor().name())};")
        gridColorDialog.colorSelected.connect(onColorPick)

        def onReset():
            map(lambda btn: btn.setChecked(False),
                getLayoutWidgets(mainLayout, QRadioButton))
            majorRadioBtn.setChecked(True)
            bothAxisRadioBtn.setChecked(True)
            gridColorDialog.setCurrentColor(QtGui.QColor(255, 0, 0))
            self.toggleGridlines(self.gridCheck.isChecked(), *self.gridSettings.values())
        onResetBtn.clicked.connect(onReset)

        def onAccept():
            self.gridSettings = {"which": [radio.text().lower()
                                           for radio in getLayoutWidgets(gridlineLayout) if radio.isChecked()][0],
                                 "axis": [radio.text().lower()
                                          for radio in getLayoutWidgets(axisLayout) if radio.isChecked()][0],
                                 "color": gridColorDialog.currentColor().name()}
            self.toggleGridlines(self.gridCheck.isChecked(), *self.gridSettings.values())
        onAcceptBtn.clicked.connect(onAccept)

        def onCancel():
            optionsWindowDialog.close()
        onCancelBtn.clicked.connect(onCancel)

        optionsWindowDialog.setModal(False)
        optionsWindowDialog.setUpdatesEnabled(True)
        optionsWindowDialog.blockSignals(True)
        optionsWindowDialog.show()
        optionsWindowDialog.blockSignals(False)

    def editMaxPeaks(self) -> None:
        """
        ``editMaxPeaks`` Creates a GUI element for inputting the max peak label quanitity for a selected graph, drawing
        the relevant annotations.
        """
        if self.elementData == {}:
            return

        optionsWindow = InputElementsDialog(self, self.styleSheet())
        elements = optionsWindow.elements

        elements.addItems(self.elementData.keys())

        inputMaxPeaks = QLineEdit()
        inputMaxPeaks.setPlaceholderText(str(self.elementData[elements.currentText()].numPeaks))
        inputMaxPeaks.setValidator(QRegExpValidator(QRegExp("[0-9]{0,4}")))

        optionsWindow.inputForm.addRow(QLabel("Peak Quantity:"), inputMaxPeaks)

        applyBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Apply)
        cancelBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Cancel)

        optionsWindow.setWindowTitle("Displayed Peaks Quantity")
        optionsWindow.mainLayout.insertItem(1, optionsWindow.inputForm)
        optionsWindow.setLayout(optionsWindow.mainLayout)

        def closeWindow():
            optionsWindow.close()
        cancelBtn.clicked.connect(closeWindow)

        def changePeaksText():
            inputMaxPeaks.setPlaceholderText(str(self.elementData[elements.currentText()].numPeaks))
        elements.activated.connect(changePeaksText)

        def onAccept():
            substance_name = elements.currentText()
            if inputMaxPeaks.text() == '':
                return
            maxPeaks = int(inputMaxPeaks.text())
            self.elementData[substance_name].maxPeaks = maxPeaks
            self.drawAnnotations(self.elementData[substance_name])
        applyBtn.clicked.connect(onAccept)

        optionsWindow.setModal(False)
        optionsWindow.show()

    def createCompound(self) -> None:
        """
        ``createCompound`` Opens a dialog for users to create compounds from weighted combinations of varying elements,
        this calculates and saves the graph data to a file for reuse.
        """

        optionsWindow = InputElementsDialog(self, self.styleSheet())

        elements = optionsWindow.elements

        elements.lineEdit().setPlaceholderText("Select an Isotope / Element")
        elements.addItems([self.combobox.itemText(i)
                           for i in range(self.combobox.count()) if 'element' in self.combobox.itemText(i)])

        totalLabel = QLabel("Total: 0")

        applyBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Apply)
        applyBtn.setText("Create")
        applyBtn.setEnabled(False)

        addBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Yes)
        addBtn.setText("Add")
        addBtn.setEnabled(False)

        resetBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Reset)
        cancelBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.Cancel)

        optionsWindow.mainLayout.setSizeConstraint(QLayout.SetFixedSize)
        optionsWindow.setWindowTitle("Compound Creater")
        optionsWindow.setLayout(optionsWindow.mainLayout)

        optionsWindow.mainLayout.insertWidget(len(optionsWindow.children()) - 2, totalLabel)

        compoundElements = {}
        compoundMode = []

        def onAccept():
            applyBtn.setEnabled(False)
            compoundDist = {
                widget.findChild(QLabel).text()[:-1]: float(widget.findChild(QLineEdit).text())
                for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget)
            }
            name = f"""compound_{'-'.join([f'{name.split("-", 1)[1].split("_")[0]}[{str(dist)}]'
                                            for name, dist in compoundDist.items()])}_{compoundMode[0]}"""
            weightedGraphData = {name: pd.read_csv(f"{self.dataFilepath}{name}.csv",
                                                   names=['x', 'y'],
                                                   header=None) * [1, dist]
                                 for name, dist in compoundDist.items() if dist != 0}
            newElement = ElementData(name, None, None, None, None, None, None, None, True)
            newElement.setGraphDataFromDist(weightedGraphData.values())
            newElement.graphData.to_csv(f"{self.filepath}data\\Graph Data\\Compound Data\\{name}.csv",
                                        index=False,
                                        header=False)
            pd.DataFrame(compoundDist.items()).to_csv(
                f"{self.filepath}data\\Distribution Information\\{name}.csv", index=False, header=False)

            self.compoundNames.append(name)
            self.compoundCombobox.clear()
            self.compoundCombobox.addItems(self.compoundNames)
            self.defaultDistributions[name] = compoundDist
            self.elementDistributions[name] = deepcopy(compoundDist)
        applyBtn.clicked.connect(onAccept)
        cancelBtn.clicked.connect(optionsWindow.reject)

        def onReset():
            elements.lineEdit().clear()
            elements.clear()
            elements.addItems([self.combobox.itemText(i)
                               for i in range(self.combobox.count()) if 'element' in self.combobox.itemText(i)])
            totalLabel.setText("Total: 0")
            onRemove()
        resetBtn.clicked.connect(onReset)

        def onElementChange():

            elementName = elements.itemText(elements.currentIndex() or 0)
            if elementName == '':
                addBtn.setEnabled(False)
                return
            if elementName in compoundElements.keys():
                addBtn.setEnabled(False)
                return
            addBtn.setEnabled(True)
        elements.currentIndexChanged.connect(onElementChange)

        def onAddRow(index=None):

            elementName = elements.itemText(elements.currentIndex() or 0)
            if elementName == '':
                elements.setCurrentIndex(0)
                return
            if compoundElements == {}:
                compoundMode.append(elementName.split('_')[-1])

                elements.currentIndexChanged.disconnect()
                elementNames = elements.getAllItemText()
                elements.clear()
                elements.addItems([name for name in elementNames if compoundMode[0] in name])
                elements.currentIndexChanged.connect(onElementChange)

            totalLabel.setStyleSheet("color: #FFF;")

            sublayout = QHBoxLayout()
            proxyWidget = QWidget()
            newQLineEdit = QLineEdit()
            newQLineEdit.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum))

            newQLineEdit.setValidator(QRegExpValidator(
                QRegExp("(0?(\\.[0-9]{1,4})?|1(\\.0{1,4})?)")))
            newQLineEdit.setPlaceholderText("0")
            title = QLabel(f"{elementName}:")
            removeBtn = QPushButton()
            removeBtn.setIcon(QIcon(".\\src\\img\\delete-component.svg"))
            removeBtn.setObjectName("compoundDelBtn")
            removeBtn.clicked.connect(lambda: onRemove(elementName))
            index = len(optionsWindow.children())
            sublayout.addWidget(title)
            sublayout.addWidget(newQLineEdit)
            sublayout.addWidget(removeBtn)
            sublayout.setSpacing(1)
            proxyWidget.setLayout(sublayout)
            proxyWidget.setFixedHeight(38)
            proxyWidget.setObjectName(f"{elementName}-RowWidget")
            newQLineEdit.textChanged.connect(onDistributionChange)
            optionsWindow.mainLayout.insertWidget(index - 3, proxyWidget)
            optionsWindow.updateGeometry()

            compoundElements[elementName] = 0
            onDistributionChange()
            addBtn.setEnabled(False)
        addBtn.clicked.connect(onAddRow)

        def onRemove(name: str = None):

            if name is None:
                for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget):
                    if "RowWidget" in widget.objectName():
                        optionsWindow.mainLayout.removeWidget(widget)
                        widget.deleteLater()
                compoundMode.clear()
                compoundElements.clear()
                applyBtn.setEnabled(False)
                return
            for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget):
                if widget.objectName() == f"{name}-RowWidget":
                    optionsWindow.mainLayout.removeWidget(widget)
                    widget.deleteLater()
                compoundElements.pop(name, None)
            onDistributionChange()

            if elements.itemText(elements.currentIndex() or 0) not in compoundElements.keys():
                addBtn.setEnabled(True)

        def onDistributionChange():

            total = 0
            for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget):
                lineEdit = widget.findChild(QLineEdit)
                distribution = lineEdit.placeholderText() if lineEdit.text() == '' else lineEdit.text()
                if distribution == ".":
                    continue
                total += float(distribution)

            total = round(total, 4)
            totalLabel.setText(f"Total: {total}")
            applyBtn.setEnabled(False)
            if total < 1:
                totalLabel.setStyleSheet("color: #FFF;")
            elif total > 1:
                totalLabel.setStyleSheet("color: #F00;")
            else:
                totalLabel.setStyleSheet("color: #0F0;")
                applyBtn.setEnabled(True)

            compoundDist = {
                widget.findChild(QLabel).text()[:-1]: float(widget.findChild(QLineEdit).text()) if widget.findChild(
                    QLineEdit).text() != '' else float(widget.findChild(QLineEdit).placeholderText())
                for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget)
            }
            name = f"""compound_{'-'.join([f'{name.split("-", 1)[1].split("_")[0]}[{str(dist)}]'
                                            for name, dist in compoundDist.items()])}"""
            if name in self.compoundNames:
                applyBtn.setEnabled(False)
                applyBtn.setToolTip("Compound Already Exists")
            else:
                applyBtn.setEnabled(True)
                applyBtn.setToolTip(None)

        elements.setFocus()
        onElementChange()
        optionsWindow.setModal(False)
        optionsWindow.show()

    def viewDarkStyle(self) -> None:
        """
        ``viewDarkStyle`` Applies the dark theme to the GUI.
        """
        self.setStyleSheet(self.styleMain.format(bg_color="#202020", text_color="#FFF"))

    def viewLightStyle(self) -> None:
        """
        ``viewLightStyle`` Applies the light theme to the GUI.
        """
        self.setStyleSheet(self.styleMain.format(bg_color="#968C80", text_color="#FFF"))

    def viewHighContrastStyle(self) -> None:
        """
        ``viewHighContrastStyle`` Applies the high contrast theme to the GUI.
        """
        self.setStyleSheet(self.styleMain.format(bg_color="#000", text_color="#FFF"))

    def toggleBtnControls(self, enableAll: bool = False, plotEnergyBtn: bool = False,
                          plotToFBtn: bool = False, clearBtn: bool = False, pdBtn: bool = False) -> None:
        """
        ``toggleBtnControls`` enables and disables the buttons controls, thus only allowing its
        use when required. enableAll is done before any kwargs have an effect on the buttons.
        enableAll defaults to False, True will enable all buttons regardless of other kwargs.
        This way you can disable all buttons then make changes to specific buttons.

        Args:
            ``enableAll`` (bool): Boolean to enable/disable (True/False) all the buttons controls.

            ``plotEnergyBtn`` (bool): Boolean to enable/disable (True/False) Plot Energy button.

            ``plotToFBtn`` (bool): Boolean to enable/disable (True/False) Plot ToF button.

            ``plotEnergyBtn`` (bool): Boolean to enable/disable (True/False) Plot Energy button.

            ``clearBtn`` (bool): Boolean to enable/disable (True/False) Plot Energy button.

            ``pdBtn`` (bool): Boolean to enable/disable (True/False) Peak Detection button.
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
        ``toggleCheckboxControls`` enables and disables the checkboxes controls, thus only allowing its
        use when required. enableAll is done before any kwargs have an effect on the checkboxes.
        enableAll defaults to False, True will enable all checkboxes regardless of other kwargs.
        This way you can disable all checkboxes then make changes to specific checkboxes.

        Args:
            ``enableAll`` (bool): Boolean to enable/disable (True/False) all the buttons controls.

            ``gridlines`` (bool): Boolean to enable/disable (True/False) Plot Energy button.

            ``peakLimit`` (bool): Boolean to enable/disable (True/False) Plot ToF button.

            ``hidePeakLabels`` (bool): Boolean to enable/disable (True/False) Plot Energy button.

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
                case "self.gridCheck":
                    btn.setEnabled(gridlines)
                case "peakCheck":
                    btn.setEnabled(peakLimit)
                case "pdCheck":
                    btn.setEnabled(hidePeakLabels)

    def plotSelectionProxy(self, index, comboboxName):
        """
        ``plotSelectionProxy`` Handles whether to selection made is from the compound list or not.

        Args:
            index (int): Index of selection given from PyQtSignal
            comboboxName (str): Identifier of combobox which made the signal.
        """

        self.combobox.blockSignals(True)
        self.compoundCombobox.blockSignals(True)

        if comboboxName == "compoundComboBox":
            self.combobox.setCurrentIndex(0)
            self.isCompound = True
            combobox = self.compoundCombobox
        if comboboxName == "combobox":
            self.compoundCombobox.setCurrentIndex(0)
            self.isCompound = False
            combobox = self.combobox

        self.combobox.blockSignals(False)
        self.compoundCombobox.blockSignals(False)
        self.resetTableProxy(combobox)

    def resetTableProxy(self, combobox) -> None:
        """
        ``resetTableProxy`` Handles setting the data in the table, either displaying the data from a single selection,
        or returning to the previous state of the table.

        Args:
            combobox (QComboBox): The Combobox from which the selection was made.
        """
        substanceNames = combobox.getAllItemText()
        try:
            if combobox.currentText() == '' and self.table_model is not None:
                self.table.setSortingEnabled(False)
                proxy = CustomSortingProxy()
                proxy.setSourceModel(self.table_model)

                self.table.setModel(proxy)
                self.table_model.titleRows = self.titleRows
                self.table.setModel(self.table_model)
                self.table.clearSpans()
                for row in self.titleRows[:-1]:
                    self.table.setSpan(row, 0, 1, 10)
                    self.table.setItemDelegateForRow(row, ButtonDelegate(self, self.table, self.table_model))
                    self.table.openPersistentEditor(self.table_model.index(row, 0))
                self.table.setSortingEnabled(True)

            elif combobox.currentText() in substanceNames:
                self.data = combobox.currentText()
                self.displayData()
        except AttributeError:
            self.table.setModel(None)

    def displayData(self) -> None:
        """
        ``displayData`` Will display relevant peak information in the table for the selection made (self.data).
        Once a select is made, the relevant controls are enabled.
        """

        if self.data == "" and self.plotCount > -1:  # Null selection and graphs shown
            self.toggleBtnControls(clearBtn=True)
            return
        elif self.data == "" and self.plotCount == -1:  # Null selection and no graphs shown
            self.toggleBtnControls(enableAll=False)
            self.toggleCheckboxControls(enableAll=False)
            return
        elif self.plotCount != -1:  # Named Selection and graphs shown
            self.toggleBtnControls(enableAll=True)
            self.toggleCheckboxControls(enableAll=True)
        else:  # Named selection and no graphs shown
            self.toggleBtnControls(plotEnergyBtn=True, plotToFBtn=True, clearBtn=True)
            self.toggleCheckboxControls(enableAll=False)

        # Getting symbol from element
        split = self.data.split("-")
        if self.data.startswith("e"):
            dataSymbolSort = split[1]
            dataSymbol = dataSymbolSort[:-2]
        else:
            dataSymbol = split[1]

        self.showTableData()

        self.threshold = self.thresholds.get(dataSymbol, 100)
        # Setting label information based on threshold value
        if self.threshold == 100:
            labelInfo = (
                "Threshold for peak detection for n-tot mode: 100"
            )

        else:
            labelInfo = (
                "Threshold for peak detection (n-tot mode, n-g mode): " + f"({self.threshold[0]},{self.threshold[1]})"
            )
            if self.data[-1] == 't':
                self.threshold = self.thresholds[dataSymbol][0]
            else:
                self.threshold = self.thresholds[dataSymbol][1]
        self.thresholdLabel.setText(str(labelInfo))
        # Changing the peak label text
        labelInfo = "Number of peaks: " + str(self.numRows)
        self.peaklabel.setText(str(labelInfo))

    def showTableData(self):
        """
        ``showTableData`` Read and display the selected substances data within the table.
        """
        # Finding relevant file for peak information
        peakInfoDir = self.filepath + "data/Peak information/"
        filepath = None
        for file in os.listdir(peakInfoDir):
            if self.data == file.split(".")[0]:
                filepath = peakInfoDir + file
                break
        try:
            for row in self.table_model.titleRows:
                self.table.setItemDelegateForRow(row, None)
        except AttributeError:
            pass
        try:
            file = pd.read_csv(filepath, header=0)
            # Reset any changes to spans before displaying selection data.
            self.table.clearSpans()

            if self.data not in self.plottedSubstances:
                self.numRows = file.shape[0]
            print("Number of peaks: ", self.numRows)
            # Fill Table with data
            tempTableModel = ExtendedQTableModel(file)
            proxy = CustomSortingProxy()
            proxy.setSourceModel(tempTableModel)

            self.table.setModel(proxy)
            self.table.setSortingEnabled(True)
            self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)
            self.peakInfoIsNull = False
            # if self.table_model is not None:

            # peak_plotEnergyBtn = QPushButton(self.table)      # If wanting a button to plot peak
            # peak_plotEnergyBtn.setText('Plot')         # Not sure how to get cell-clicked though
            # peak_plotEnergyBtn.clicked.connect(self.PlotPeak)
            # self.table.setCellWidget(row_count,10,peak_plotEnergyBtn)

        except ValueError:

            self.table.setModel(None)
            self.peakInfoIsNull = True
            self.numRows = None

    def addTableData(self, reset=False):
        # Amending the table for more than one plot.
        self.table.reset()
        self.table.sortByColumn(-1, Qt.SortOrder.AscendingOrder)

        table_data = pd.DataFrame()
        try:
            self.table_model.beginResetModel()
            self.table_model.endResetModel()
        except AttributeError:
            pass
        self.table.setModel(None)
        self.table_model = None
        self.table.setSortingEnabled(False)
        self.titleRows = [0]
        # ! ---------------------------------------------------------------------------------
        # ? Maybe sort the order in which they are plotted and added to the table.
        for element in self.elementData.values():
            if element.name not in self.elementDataNames:
                table_data = pd.concat([table_data, element.tableData], ignore_index=True)
                self.titleRows.append(self.titleRows[-1] + element.tableData.shape[0])
                self.elementDataNames.append(element.name)

        self.table_model = ExtendedQTableModel(table_data)

        proxy = CustomSortingProxy()
        proxy.setSourceModel(self.table_model)

        self.table.setModel(proxy)
        self.table.setSortingEnabled(True)
        self.table_model.titleRows = self.titleRows
        self.table.setModel(self.table_model)
        self.table.setSortingEnabled(True)
        self.table.clearSpans()
        for row in self.titleRows[:-1]:
            self.table.setSpan(row, 0, 1, 10)
            self.table.setItemDelegateForRow(row, ButtonDelegate(self, self.table, self.table_model))
            self.table.openPersistentEditor(self.table_model.index(row, 0))

    def updateGuiData(self, tof: bool = False, filepath: str = None, imported: bool = False, name: str = None,
                      distAltered: bool = False) -> None:
        """
        ``updateGuiData`` Will initialise the new element with its peak and graph data, updating the table and plot.
        Handles updates to isotopic distribution.
        Args:
            ``tof`` (bool, optional): Whether to graph for tof or not. Defaults to False.

            ``filepath`` (string, optional): Filepath for the selection to graph . Defaults to None.

            ``imported`` (bool, optional): Whether the selection imported. Defaults to False.

            ``name`` (string, optional): The name of the imported selection. Defaults to None.

            ``distAltered`` (bool, optional): Whether or not the function is plotted for altered isotope distributions.
            Defaults to False.

        """

        # Enable Checkboxes on plotting graphs
        self.toggleCheckboxControls(enableAll=True)
        self.toggleBtnControls(enableAll=True)

        if self.data is None and not imported:
            QMessageBox.warning(self, "Error", "You have not selected anything to plot")
            return
        if imported:
            self.data = name
            self.threshold = 100
        # Checks for adding mutliple graphs for the same selection, energy/tof types.
        if (self.data, tof) in self.plottedSubstances and not distAltered:
            QMessageBox.warning(self, "Warning", "Graph is already plotted")
            return

        # Establishing the number of peaks on the graph at one time, and their type
        if not imported and self.numRows != 0:
            if self.data not in self.plottedSubstances:
                self.numTotPeaks.append(self.numRows)

        if (self.data, tof) not in self.plottedSubstances:
            self.plottedSubstances.append((self.data, tof))
        # Handles number_totpeaks when plotting energy and tof of the same graph
        self.numTotPeaks.append(self.numRows)

        # # Finds the mode for L0 (length) parameter
        if self.data[-1] == "t":
            length = 23.404
        else:
            length = 22.804

        self.titleRows = [0]
        for (element, tof) in self.plottedSubstances:
            title = f"{element}-{'ToF' if tof else 'Energy'}"
            # ¦ -----------------------------------

            if title in self.elementData.keys():
                if self.elementData[title].isGraphDrawn:
                    continue
            if self.isCompound:
                self.plotFilepath = f"{self.filepath}data\\Graph Data\\Compound Data\\{element}.csv"
            else:
                self.plotFilepath = f"{self.filepath}data\\Graph Data\\{element}.csv" if filepath is None else filepath
            peakInfoDir = f"{self.filepath}data\\Peak information\\" if filepath is None else None

            try:
                graphData = pd.read_csv(self.plotFilepath, header=None)

            except pd.errors.EmptyDataError:
                QMessageBox.warning(self, "Warning", "Selection has Empty Graph Data")
                self.plottedSubstances.remove((self.data, tof))
                if self.plotCount == -1:
                    self.toggleCheckboxControls(enableAll=False)
                    self.toggleBtnControls(plotEnergyBtn=True, plotToFBtn=True, clearBtn=True, pdBtn=False)
                    return
            except FileNotFoundError:
                if self.elementData.get(element, False):
                    self.elementData[element].graphData.to_csv(self.plotFilepath, index=False, header=False)
                    graphData = self.compoundData[element].graphData

            if tof and not graphData.empty:
                graphData[0] = self.energyToTOF(graphData[0], length=length)

            try:
                elementTableData = pd.read_csv(f"{peakInfoDir}{element}.csv")
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
                elementTableData.loc[-1] = [f"No Peak Data for {element}", *[""] * 9]

            else:
                elementTableData.loc[-1] = [element, *[""] * 9]
            elementTableData.index += 1
            elementTableData.sort_index(inplace=True)

            if self.elementData.get(title, False):
                for point in self.elementData[title].annotations:
                    point.remove()

            newElement = ElementData(name=element,
                                     numPeaks=self.numRows,
                                     tableData=elementTableData,
                                     graphData=graphData,
                                     graphColour=getRandomColor(),
                                     isToF=tof,
                                     distributions=self.elementDistributions.get(element, None),
                                     defaultDist=self.defaultDistributions.get(element, None),
                                     isCompound=self.isCompound,
                                     isAnnotationsHidden=self.peakLabelCheck.isChecked(),
                                     threshold=float(self.threshold or 100),
                                     isImported=imported)

            self.elementData[title] = newElement

        if distAltered:
            for line in self.ax.get_lines():
                if newElement.name in line.get_label():
                    line.remove()

        distAltered = False

        self.plot(newElement, filepath, imported, name)
        self.addTableData()

        self.canvas.draw()

    def plot(self, elementData: ElementData, filepath: str = None, imported: bool = False, name: str = None) -> None:
        if elementData is None:
            return
        # Re-setting Arrays
        self.x = []
        self.y = []
        # Establishing colours for multiple plots

        # General Plotting ---------------------------------------------------------------------------------------------
        if self.plotCount < 0:
            self.ax = self.figure.add_subplot(111)
            # Setting scale to be logarithmic
            self.ax.set_yscale("log")
            self.ax.set_xscale("log")
            self.ax.minorticks_on()
            self.ax.xaxis.set_tick_params('both', bottom=True)

        # Allows user to plot in ToF if chosen # -----------------------------------------------------------------------
        if elementData.isToF and not imported:
            # ! Convert to pandas compatible

            if self.plotCount < 0:
                self.ax.set(
                    xlabel="ToF (uS)", ylabel="Cross section (b)", title=self.data
                )
        else:
            if self.plotCount < 0:
                if elementData.isToF:
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

        label = f"{elementData.name}-ToF" if elementData.isToF else f"{elementData.name}-Energy"

        if not elementData.graphData.empty:

            self.ax.plot(
                elementData.graphData.iloc[:, 0],
                elementData.graphData.iloc[:, 1],
                "-",
                c=elementData.graphColour,
                alpha=0.6,
                linewidth=0.8,
                label=label,
                gid=elementData.name if self.data is None else self.data,
            )
            elementData.isGraphDrawn = True

            self.updateLegend()

            # Establishing plot count
            self.plotCount += 1

            self.drawAnnotations(elementData)
            self.toggleThreshold()
            self.ax.autoscale()  # Tidying up

            self.figure.tight_layout()

        self.canvas.draw()

    def updateLegend(self):
        # Creating a legend to toggle on and off plots--------------------------------------------------------------

        legend = self.ax.legend(fancybox=True, shadow=True)

        if len(self.ax.get_lines()) == 0:
            self.clear()
            return
        # Amending dictionary of plotted lines - maps legend line to original line and allows for picking
        self.legOrigLines = {}
        for legLine in legend.get_lines():
            for origLine in self.ax.get_lines():
                if origLine.get_label() == legLine.get_label():
                    legLine.set_picker(True)
                    legLine.set_linewidth(1.5)
                    legLine.set_pickradius(1.5)
                    legLine.set_color(self.elementData[origLine.get_label()].graphColour)
                    legLine.set_alpha(1.0 if origLine.get_visible() else 0.2)

                    self.legOrigLines[legLine] = origLine

    def energyToTOF(self, xData: list[float], length: float) -> list[float]:
        """
        Maps all X Values from energy to TOF

        Args:
            ``xData`` (list[float]): List of the substances x-coords of its graph data

            ``length`` (float): Constant value associated to whether the element data is with repsect to n-g or n-tot


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

    def hideGraph(self, event) -> None:
        """
        Function to show or hide the selected graph by clicking the legend.

        Args:
            ``event`` (pick_event): event on clicking a graphs legend
        """
        # Tells you which plot number you need to deleteLater() labels for

        legline = event.artist
        if self.ax.get_visible():
            axis, legOrigLines = self.ax, self.legOrigLines
        if self.ax2 is not None:
            if self.ax2.get_visible():
                axis, legOrigLines = self.ax2, self.legOrigLinesPD

        if legline not in legOrigLines:
            return
        origLine = legOrigLines[legline]
        orgline_name = legline.get_label()
        # Hiding relevant line
        newVisible = not origLine.get_visible()
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled.
        legline.set_alpha(1.0 if newVisible else 0.2)
        origLine.set_visible(newVisible)
        # Hiding relevant labels
        elementData = self.elementData[orgline_name]
        elementData.isGraphHidden = not newVisible
        elementData.HideAnnotations(self.peakLabelCheck.isChecked())
        for line in axis.lines:
            if line.get_gid() == f"pd_threshold-{orgline_name}":
                line.set_visible(newVisible)
                continue
            if f"{elementData.name}-{'ToF' if elementData.isToF else 'Energy'}-max" in line.get_gid():
                line.set_visible(newVisible)
                continue
            if f"{elementData.name}-{'ToF' if elementData.isToF else 'Energy'}-min" in line.get_gid():
                line.set_visible(newVisible)
                continue

        self.canvas.draw()

    def clear(self) -> None:
        """
        clear Function will empty all data from the table, all graphs from the plots,
        along with resetting all data associated the table or plot and disables relevent controls.
        """

        self.figure.clear()
        self.ax.clear()
        self.ax2 = None
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
        try:
            for row in self.table_model.titleRows:
                self.table.setItemDelegateForRow(row, None)
        except AttributeError:
            pass
        self.table.setModel(None)
        self.graphs = dict()
        self.tableLayout = dict()
        self.table_model = None
        self.arrays = dict()
        self.plottedSubstances = []
        self.elementDistributions = deepcopy(self.defaultDistributions)

        self.toggleBtnControls(plotEnergyBtn=True, plotToFBtn=True, clearBtn=True)
        self.toggleCheckboxControls(enableAll=False)

    def toggleGridlines(self, visible: bool,
                        which: Literal["major", "minor", "both"] = "major",
                        axis: Literal["both", "x", "y"] = "both",
                        color="#444") -> None:
        """
        ``toggleGridlines`` Will toggle visibility of the gridlines on the axis which is currently shown.


        Args:
            ``visible`` (bool): Whether or not gridlines should be shown.

            ``which`` (Literal["major", "minor", "both"], optional):
            Whether to show major, minor or both gridline types. Defaults to "major".

            ``axis`` (Literal["both", "x", "y"], optional):
            Whether or not to show gridlines on x, y, or both. Defaults to "both".

            ``color`` (str, optional): Gridline Color. Defaults to "#444".
        """
        try:
            # if self.gridSettings["which"] == "major":
            #     plt.minorticks_off()
            #     self.ax.minorticks_off()
            # else:
            #     plt.minorticks_on()
            #     self.ax.minorticks_on()
            self.ax.minorticks_on()

            self.ax.tick_params(which='minor', axis='x')
            self.ax.tick_params(**self.gridSettings)
            self.ax.grid(visible=False, which='both')
            if visible and self.ax.get_visible():
                self.ax.grid(visible=visible, which=which, axis=axis, color=color, alpha=0.2)
            else:
                self.ax.grid(visible=visible, which="both")
            if visible and self.ax2.get_visible():
                self.ax2.grid(visible=visible, which=which, axis=axis, color=color, alpha=0.2)
            else:
                self.ax.grid(visible=visible, which="both")
        except AttributeError:
            pass
        self.canvas.draw()

    def toggleThreshold(self) -> None:
        """
        Plots the threshold line for each plotted element at their respective limits.
        """
        checked = self.thresholdCheck.isChecked()

        for line in self.ax.get_lines():
            if line is None:
                continue
            if line.get_gid() is None:
                continue
            if "pd_threshold" in line.get_gid():
                line.remove()
        try:
            for line in self.ax2.get_lines():
                if line is None:
                    continue
                if line.get_gid() is None:
                    continue
                if "pd_threshold" in line.get_gid():
                    line.remove()
        except AttributeError:
            pass
        self.canvas.draw()
        if checked:
            for name, element in self.elementData.items():
                self.figure.add_subplot(self.ax)
                if self.ax.get_visible():
                    line = self.ax.axhline(
                        y=element.threshold,
                        linestyle="--",
                        color=element.graphColour,
                        linewidth=0.5,
                        gid=f"pd_threshold-{name}"
                    )
                try:
                    if self.ax2.get_visible() and (element.isMaxDrawn or element.isMinDrawn):
                        line = self.ax2.axhline(
                            y=element.threshold,
                            linestyle="--",
                            color=element.graphColour,
                            linewidth=0.5,
                            gid=f"pd_threshold-{name}"
                        )
                except AttributeError:
                    pass
                if element.isGraphHidden:
                    line.set_visible(False)

                self.canvas.draw()

    def onPeakOrderChange(self) -> None:
        if self.sender().objectName() == "orderByIntegral":
            self.orderByIntegral = self.byIntegralCheck.isChecked()

        if self.sender().objectName() == "orderByPeakW":
            self.orderByIntegral = self.byIntegralCheck.isChecked()

        for element in self.elementData.values():
            self.drawAnnotations(element)

    def drawAnnotations(self, element: ElementData) -> None:
        """
        ``drawAnnotations`` will plot each numbered annotation in the order of Integral or Peak Width

        Args:
            ``element`` (ElementData): The data for the element your annotating
        """
        self.elementDataNames = []

        if element.isAnnotationsDrawn:
            for anno in element.annotations:
                anno.remove()
            element.annotations.clear()

        if element.maxima.size == 0:
            return

        if element.tableData is not None:
            element.OrderAnnotations(self.orderByIntegral)

        gid = f"annotation-{element.name}-" + "ToF" if element.isToF else "Energy"
        xy = element.maxima.T if element.annotationsOrder == {} or element.isDistAltered else element.annotationsOrder
        if element.isDistAltered:
            maxDraw = len(xy)
        else:
            maxDraw = element.maxPeaks if element.maxPeaks < element.numPeaks else element.numPeaks
        element.annotations = [self.ax.annotate(text=f'{i}',
                                                xy=xy[i],
                                                xytext=xy[i],
                                                xycoords="data",
                                                textcoords="data",
                                                va="center",
                                                size=6,
                                                gid=gid,
                                                annotation_clip=True,
                                                alpha=0.8
                                                )
                               for i in
                               (range(0, maxDraw) if type(xy) is np.ndarray else xy.keys())
                               if i < maxDraw]
        if element.isGraphHidden or self.peakLabelCheck.isChecked():
            for annotation in element.annotations:
                annotation.set_visible(False)
            element.isAnnotationsHidden = True
        element.isAnnotationsDrawn = True
        self.canvas.draw()

    def toggleAnnotations(self) -> None:
        """
        Function Annotations shows & hides all peak annotations globally.
        """
        for element in self.elementData.values():
            element.HideAnnotations(self.peakLabelCheck.isChecked())
            element.isAnnotationsHidden = not element.isAnnotationsHidden

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
            # Establishing which row belongs to what element if multiple --------------------------------------------
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
            element = self.tableLayout.get(row_clicked)
            # Getting Singular Peak Arrays with PlotPeak---------------------------------------------------------------
            # Getting peak limits for relevant element
            peakLimits = []
            try:
                if self.peakLimitsX == dict():
                    # ! filepath = self.filepath + "data/Peak_limits.txt"
                    with open(filepath, "r") as f:
                        lines = f.readlines()
                        for i in lines:
                            # should have sorting = [name, peak limit 1, peak limit 2]
                            sorting = i.split(" ")
                            if sorting[0] == element[:-2]:
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
                QMessageBox.warning(self, "Error", "No peak limits for this Selection")

            # Getting peak limits for relevant peak
            limitsIndex = int(self.element[-1]) * 2 - 2
            self.firstLimit = peakLimits[limitsIndex]
            self.secondLimit = peakLimits[(limitsIndex + 1)]

            # Getting the right arrays to plot the graph
            x = self.arrays.get(element[:-2] + "x")
            y = self.arrays.get(element[:-2] + "y")

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
            titlename = self.data + "- Peak: " + str(int(element[-1]))
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
            raise NotImplementedError
        #     if checked:
        #         # Getting the threshold for the specific element------------------------------------------------------
        #         # Getting symbol
        #         symbol_sorting = self.element.split("-")
        #         dataSymbol = symbol_sorting[1]
        #         thresholdFilepath = (
        #             self.filepath + "data/threshold_exceptions.txt"
        #         )
        #         with open(thresholdFilepath, "r") as f:
        #             file = f.readlines()
        #         # ! self.thresholds = "100 by default"
        #         # Checking if the selected element has a threshold exception
        #         for i in file:
        #             sortLimits = i.split(" ")
        #             symbol = sortLimits[0]
        #             if str(symbol) == str(dataSymbol):
        #                 self.thresholds = str(sortLimits[1]) + str(sortLimits[2])
        #         # Plotting ---------------------------------------------------------------------------------------------
        #         number_data_points = len(self.xArray)
        #         threshold_sorting = self.thresholds.split(",")
        #         if self.thresholds == "100 by default":
        #             threshold_coord_y = 100
        #         elif self.data[-1] == "t":
        #             # sortLimits is set earlier in SelectandDisplay
        #             threshold_coord_y_sort = len(threshold_sorting[0])
        #             threshold_coord_y = float(
        #                 threshold_sorting[0][1:threshold_coord_y_sort]
        #             )
        #             print("n-tot mode")
        #         else:
        #             # sortLimits is set earlier in SelectandDisplay
        #             threshold_coord_y_sort = len(threshold_sorting[1])
        #             # To splice the number from the string correctly regardless of magnitude
        #             cutoff = threshold_coord_y_sort - 2
        #             threshold_coord_y = float(threshold_sorting[1][0:cutoff])
        #             print("n-g mode")
        #         # Creating an array to plot line of coords
        #         threshold_coords_y = [float(threshold_coord_y)] * number_data_points
        #         threshold_coords_x = self.xArray
        #         self.ax2.plot(
        #             threshold_coords_x,
        #             threshold_coords_y,
        #             "--",
        #             color="black",
        #             linewidth=0.5,
        #         )
        #         self.canvas2.draw()
        #     else:
        #         self.ax2.lines.pop()  # Getting rid of line
        #         self.canvas2.draw()
        except FileNotFoundError:
            QMessageBox.warning(self, "Error",
                                "Trouble getting peak limits for this peak \n Contact Ryan.Horrell@stfc.ac.uk")
        except NotImplementedError:
            print("Function 'ThresholdforPeak' Not Yet Implemented.")

    # ! ------------------------------------------------------------------------------------

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
            self.updateGuiData(True, filepath, True, name)
        else:
            self.updateGuiData(False, filepath, True, name)

    # ------------------------ PEAK DETECTION BITS ## ------------------------
    def GetPeaks(self) -> None:
        """
        Ask the user for which function to plot the maxima or minima of which element
        then calls the respective function on that element
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
        inputWindow.setObjectName("inputWindow")
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
            self.toggleThreshold()
            self.toggleGridlines(self.gridCheck.isChecked(), *self.gridSettings.values())
            self.toolbar.update()
            self.canvas.draw()
        resetBtn.clicked.connect(ResetPDPlots)

    def PlottingPD(self, elementData: ElementData, isMax: bool) -> None:
        """
        ``PlottingPD`` takes plots the maximas or minimas of the inputted ``elementData`` based on ``isMax``

        Args:
            ``elementData`` (ElementData): ElementData Class specifying the element

            ``isMax`` (bool): Maxima if True else Minima
        """
        if elementData.isMinDrawn and not isMax:
            return
        if elementData.isMaxDrawn and isMax:
            return
        if isMax:
            peaksX, peaksY = elementData.maxima[0], elementData.maxima[1]

        else:
            peaksX, peaksY = elementData.minima[0], elementData.minima[1]

        # ! Add element selection to Peak Detection menu
        # ! Change how points are then plotted
        # Redrawing graph and Peak Detection Limits
        self.ax.set_visible(False)

        if self.ax2 is None:
            self.ax2 = self.figure.add_subplot(111)

        self.toggleGridlines(self.gridCheck.isChecked(), **self.gridSettings)

        self.ax2.set_visible(True)
        label = f"{elementData.name}-ToF" if elementData.isToF else f"{elementData.name}-Energy"
        if not elementData.isMaxDrawn and not elementData.isMinDrawn:
            self.ax2.plot(
                elementData.graphData[0],
                elementData.graphData[1],
                "-",
                color=elementData.graphColour,
                alpha=0.6,
                linewidth=0.8,
                label=label,
                gid=f"{elementData.name}-PD"
            )
        self.toggleThreshold()
        self.drawAnnotations(elementData)
        self.ax2.set_xscale("log")
        self.ax2.set_yscale("log")
        self.ax2.set(xlabel="Energy (eV)", ylabel="Cross section (b)", title=str(self.data))

        if isMax:
            pdPoints = [
                a for a in self.ax2.get_lines() if "max" in a.get_gid() and elementData.name in a.get_gid()
            ]
            pdPointsXY = [(point.get_xdata()[0], point.get_ydata()[0])
                          for point in pdPoints]
            peaks = list(zip(peaksX, peaksY))
            removeIds = []
            for point in pdPoints:
                if "max-p" not in point.get_gid():
                    continue
                xy = (point.get_xdata()[0], point.get_ydata()[0])
                if xy not in peaks:
                    removeIds.append(point.get_gid().split('-')[-1])
            if removeIds != []:
                for point in pdPoints:
                    for id in removeIds:
                        if id == point.get_gid().split('-')[-1]:
                            point.remove()
                            break

            for i, (x, y) in enumerate(zip(peaksX, peaksY)):
                if (x, y) in pdPointsXY:
                    continue
                self.ax2.plot(x,
                              y,
                              "x",
                              color="black",
                              markersize=3,
                              alpha=0.6,
                              gid=f"{elementData.name}-{'ToF' if elementData.isToF else 'Energy'}-max-p-{i}")
                elementData.isMaxDrawn = True
                if elementData.maxPeakLimitsX.get(x, False):
                    limitXFirst = elementData.maxPeakLimitsX[x][0]
                    limitXSecond = elementData.maxPeakLimitsX[x][1]
                else:
                    continue
                if elementData.maxPeakLimitsY.get(x, False):
                    limitYFirst = elementData.maxPeakLimitsY[x][0]
                    limitYSecond = elementData.maxPeakLimitsY[x][1]
                else:
                    continue

                self.ax2.plot(limitXFirst,
                              limitYFirst,
                              marker=2,
                              color="r",
                              markersize=8,
                              gid=f"{elementData.name}-{'ToF' if elementData.isToF else 'Energy'}-max-limL-{i}")
                self.ax2.plot(limitXSecond,
                              limitYSecond,
                              marker=2,
                              color="r",
                              markersize=8,
                              gid=f"{elementData.name}-{'ToF' if elementData.isToF else 'Energy'}-max-limR-{i}")

        else:
            for x, y in zip(peaksX, peaksY):
                self.ax2.plot(x,
                              y,
                              "x",
                              color="black",
                              markersize=3,
                              alpha=0.6,
                              gid=f"{elementData.name}-{'ToF' if elementData.isToF else 'Energy'}-min")
                elementData.isMinDrawn = True

                # limitXFirst = elementData.minPeakLimitsX[f"{x}_first"]
                # limitYFirst = elementData.minPeakLimitsY[f"{x}_first"]
                # limitXSecond = elementData.minPeakLimitsX[f"{x}_second"]
                # limitYSecond = elementData.minPeakLimitsY[f"{x}_second"]
                # self.ax2.plot(limitXFirst, limitYFirst, 0, color="r", markersize=8)
                # self.ax2.plot(limitXSecond, limitYSecond, 0, color="r", markersize=8)
        legendPD = self.ax2.legend(fancybox=True, shadow=True)
        self.legOrigLinesPD = {}
        origlines = [line for line in self.ax2.get_lines() if not ('max' in line.get_gid() or 'min' in line.get_gid())]
        for legline, origline in zip(legendPD.get_lines(), origlines):
            legline.set_picker(True)
            legline.set_pickradius(7)
            legline.set_color(origline.get_color())
            self.legOrigLinesPD[legline] = origline

        self.figure.tight_layout()
        self.toolbar.update()
        self.toolbar.push_current()
        self.canvas.draw()


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    app.setObjectName('MainWindow')

    app.setStyle('Fusion')
    QtGui.QFontDatabase.addApplicationFont('src\\fonts\\RobotoMono-Thin.ttf')
    QtGui.QFontDatabase.addApplicationFont('src\\fonts\\RobotoMono-Regular.ttf')
    QtGui.QFontDatabase.addApplicationFont('src\\fonts\\RobotoMono-Medium.ttf')
    Colours = QtGui.QPalette()
    # Colours.setColor(QtGui.QPalette.Window, QtGui.QColor("#393939"))
    # Colours.setColor(QtGui.QPalette.Button, QtGui.QColor("#FFF"))

    app.setWindowIcon(QIcon("./src/img/final_logo.png"))

    _ = DatabaseGUI()
    app.setPalette(Colours)
    app.exec()


if __name__ == "__main__":
    main()
