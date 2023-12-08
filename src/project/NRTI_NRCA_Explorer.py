from __future__ import annotations
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.rcsetup
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, LogFormatter

matplotlib.use('QtAgg')

# from matplotlib.backends.backend_qt5agg import (
#     FigureCanvasQTAgg as FigureCanvas,
# )

from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar
)
from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, QModelIndex, QRegularExpression as QRegExp, pyqtSignal
from PyQt6.QtGui import QAction, QCursor, QRegularExpressionValidator as QRegExpValidator, QIcon

from PyQt6.QtWidgets import (
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
    QVBoxLayout,
    QWidget,

)
from copy import deepcopy

from pyparsing import Literal

from element.SpectraDataStructure import SpectraData
from myPyQt.ButtonDelegate import ButtonDelegate
from myPyQt.CustomSortingProxy import CustomSortingProxy
from myPyQt.ExtendedComboBox import ExtendedComboBox
from myPyQt.ExtendedTableModel import ExtendedQTableModel
from myPyQt.InputElementsDialog import InputElementsDialog

from myMatplotlib.CustomFigureCanvas import FigureCanvas
from myMatplotlib.BlittedCursor import BlittedCursor

from helpers.nearestNumber import nearestnumber
from helpers.getRandomColor import getRandomColor
from helpers.getWidgets import getLayoutWidgets


# todo -------------------- Issues/Feature TODO list --------------------
# todo - Add periodic table GUI for selection.
# todo - Maximas after changing threshold wont have correct annotations due to integral and peak widths not calculated
# todo   correctly yet.
# todo - Matplotlib icons
# todo - PyQt5 Unit Testing
# todo - Incorporate multiprocessing and multithreading?
# todo - Fix issues with Maxima not displaying after zoom


# ? Should this ask for the filepath or just be require to be in the format as seen in the repository,
# ? Download the repository and run the program without altering the file structure, will save having
# ? to enter filepaths in console during start up.


# Asking for filepath where the user has saved script
# filepath is where the data and the code has been saved. The sourceFilepath is the path to the latest data folder
# ! Maybe Change back to inputs if required

#  input('Enter the filepath where the latest NRCA code data folder is \n For Example:'
#                         'C://Users/ccj88542/NRCA/Rehana/Latest/main/data: \n')

# print(filepath)
# print(sourceFilepath)

# ! fonts = font_manager.findSystemFonts(
#     fontpaths="C:\\Users\\gzi47552\\Documents\\NRTI-NRCA-Viewing-Database\\src\\fonts")
# ! for font in fonts:
# !    font_manager.fontManager.addfont(font)

matplotlib.rcParamsDefault["path.simplify"] = True
matplotlib.rcParamsDefault["agg.path.chunksize"] = 1000


class ExplorerGUI(QWidget):  # Acts just like QWidget class (like a template)
    """
    ``ExplorerGUI``
    --------------
    Class responsible for creating and manipulating the GUI, used in selecting and graphing the data of elements or
    isotopes within the NRTI/NRCA Explorer.
    """
    resized = pyqtSignal()

    # init constructure for classes
    def __init__(self) -> None:
        """
        Initialisar for ExplorerGUI class
        """
        # Allows for adding more things to the QWidget template
        super(ExplorerGUI, self).__init__()

        self.styleMain = """
        #mainWindow{{
            background-color: {bg_color};
        }}

        *{{
            font-family: 'Roboto Mono';
            font-size: 10pt;
            font-weight: 400;
        }}

        QMenuBar {{
            color: {text_color};
        }}
        QMenuBar::item:selected {{
            color: #000;
        }}

        QCheckBox{{
            color: {text_color};
        }}

        QCheckbox::indicator:checked{{
            image: url(./src/img/checkbox-component-checked.svg);
        }}

        QCheckbox::indicator:unchecked{{
            image: url(./src/img/checkbox-component-unchecked.svg);
        }}

        QComboBox{{
            background-color: #EEE;
            border-radius: 3px;
            font-family: 'Roboto Mono';
            font-size: 10pt;
            font-weight: 400;
        }}

        QMenuBar{{
            background-color: {bg_color};
            color: {text_color};
        }}

        QSplitter::handle:vertical{{
            image: url(./src/img/drag-component.svg);
            height: 11px;
        }}

        QLabel#numPeakLabel, #thresholdLabel, #orderlabel, #compoundLabel, #peakLabel, #gridOptionLabel{{
            font: 11pt 'Roboto Mono';
            color: {text_color};
        }}

        QPushButton#plotEnergyBtn, #plotTOFBtn, #clearBtn, #pdBtn, #compoundBtn{{
            font: 10pt 'Roboto Mono Medium';
            font-weight: 500;
            background-color: #EEE;
            border-radius: 3px;
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

        QCheckBox#gridCheck, #thresholdCheck, #label_check, #orderByIntegral, #orderByPeakW, #peakCheck {{
            font-weight: 500;
        }}

        QCheckBox#grid_check::indicator:unchecked,
                 #thresholdCheck::indicator:unchecked,
                 #label_check::indicator:unchecked,
                 #peakCheck::indicator:unchecked
                 {{
                   image: url(./src/img/checkbox-component-unchecked.svg);
                   color: {text_color};
                 }}

        QCheckBox#grid_check::indicator:checked,
                 #thresholdCheck::indicator:checked,
                 #label_check::indicator:checked,
                 #peakCheck::indicator:checked
                 {{
                     image: url(./src/img/checkbox-component-checked.svg);
                     color: {text_color};
                 }}

        QCheckBox#grid_check:disabled,
                 #thresholdCheck:disabled,
                 #label_check:disabled
                 {{
                     color: #AAA;
                 }}
        QCheckBox#grid_check:enabled,
                 #thresholdCheck:enabled,
                 #label_check:enabled
        {{
            color: {text_color};
        }}

        QDialog {{
            color: {text_color};
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

        QDockWidget{{
            background-color: {bg_color};
            color: {text_color};
        }}

        QDockWidget::title{{
            color: {text_color};
        }}

        QRadioButton:enabled{{
            color: {text_color};
            font-size: 9pt;
            font-weight: 400;
        }}

        QRadioButton::indicator:unchecked{{
            image: url(./src/img/radio-component-unchecked.svg);
            color: #AAA;
        }}
        QRadioButton::indicator:checked{{
            image: url(./src/img/radio-component-checked.svg);
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
                        image: url(./src/img/radio-component-unchecked.svg);
                        color: #AAA;
                    }}

        QRadioButton#orderByIntegral::indicator:checked,
                    #orderByPeakW::indicator:checked
                    {{
                        image: url(./src/img/radio-component-checked.svg);
                        color: {text_color};
                    }}

        QWidget#peakCanvasContainer{{
            margin: 9px;
            background-color: #FFF;
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

        """

        # Setting global variables
        self.selectionName = None
        self.numRows = None

        self.ax = None
        self.axPD = None

        self.plotCount = -1
        self.annotations = []
        self.localHiddenAnnotations = []
        self.plottedSpectra = []
        self.spectraNames = None

        self.gridSettings = {"which": "major", "axis": "both", "color": "#444"}

        self.orderByIntegral = True
        self.spectraData = dict()
        self.elementDataNames = []

        self.compoundData = dict()
        self.isCompound = False

        self.maxPeak = 50
        self.thresholds = dict()
        self.length = {"n-g": 22.804, "n-tot": 23.404}

        self.dir = f"{os.path.dirname(__file__)}\\"
        self.graphDataDir = f"{self.dir}data\\Graph Data\\"
        self.distributionDir = self.dir + "data\\Distribution Information\\"
        thresholdFilepath = self.dir + "data\\threshold_exceptions.txt"
        self.plotFilepath = None

        self.defaultDistributions = dict()
        self.elementDistributions = dict()

        file = pd.read_csv(thresholdFilepath, header=None)

        # Initialise spectra thresholds dict
        for line in file.values:
            symbol = line[0].split(' ')[0]
            self.thresholds[symbol] = (line[0].split(' ')[1].replace('(', ''), line[1].replace(')', ''))

        # Initialise spectra natural abundance / distributions dict
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
        ----------
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
        importAction.triggered.connect(self.importData)

        # * ----------------------------------------------

        # ¦ --------------- MENU BAR - EDIT --------------
        # Creates menu bar and add actions
        editpeakAction = QAction(QIcon("./src/img/edit-component.svg"), "&Edit Peak Limits", self)
        editpeakAction.setShortcut("Ctrl+E")
        editpeakAction.triggered.connect(self.editPeakLimits)

        editThresholdAction = QAction(QIcon("./src/img/edit-component.svg"), "&Edit Threshold", self)
        editThresholdAction.setShortcut("Ctrl+Shift+T")
        editThresholdAction.triggered.connect(self.editThresholdLimit)

        editDistribution = QAction(QIcon("./src/img/edit-component.svg"), "&Edit Distribution", self)
        editDistribution.setShortcut("Ctrl+Shift+D")
        editDistribution.triggered.connect(self.editDistribution)

        editLength = QAction(QIcon("./src/img/edit-component.svg"), "&Edit Length", self)
        editLength.setShortcut("Ctrl+Shift+L")
        editLength.triggered.connect(self.editLength)
        # fileMenu.addAction(saveAction)

        editMenu = menubar.addMenu("&Edit")
        editMenu.addAction(editpeakAction)
        editMenu.addAction(editThresholdAction)
        editMenu.addAction(editDistribution)
        editMenu.addAction(editLength)

        menubarLayout.addWidget(menubar, alignment=Qt.AlignmentFlag.AlignLeft)
        # Adding label which shows number of peaks
        self.peaklabel = QLabel()
        self.peaklabel.setObjectName('numPeakLabel')
        self.peaklabel.setText("")
        self.peaklabel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.peaklabel.setContentsMargins(0, 10, 0, 0)
        menubarLayout.addWidget(self.peaklabel, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Threshold Label
        self.thresholdLabel = QLabel()
        self.thresholdLabel.setObjectName('thresholdLabel')
        self.thresholdLabel.setText("Nothing has been selected")
        self.thresholdLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.thresholdLabel.setContentsMargins(0, 10, 0, 0)

        menubarLayout.addWidget(self.thresholdLabel, alignment=Qt.AlignmentFlag.AlignRight)

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
        self.spectraNames = [None]
        for file in os.listdir(f"{self.graphDataDir}"):
            filename = os.fsdecode(file)
            if ".csv" not in filename[-4:]:
                continue
            filename = filename[:-4]
            self.spectraNames.append(filename)

        # Creating combo box (drop down menu)
        self.combobox = ExtendedComboBox()
        self.combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.combobox.setObjectName("combobox")

        self.combobox.addItems(self.spectraNames)
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

        pointingCursor = QCursor(Qt.CursorShape.PointingHandCursor)

        # ¦ ---------------- Button Group ----------------

        self.btnLayout = QVBoxLayout()

        self.plotEnergyBtn = QPushButton("Plot in Energy", self)
        self.plotEnergyBtn.setObjectName("plotEnergyBtn")
        self.plotEnergyBtn.setCursor(pointingCursor)
        self.plotEnergyBtn.__name__ = "plotEnergyBtn"
        self.plotEnergyBtn.resize(self.plotEnergyBtn.sizeHint())
        self.plotEnergyBtn.setEnabled(False)
        self.btnLayout.addWidget(self.plotEnergyBtn)
        self.plotEnergyBtn.clicked.connect(self.updateGuiData)

        self.plotTOFBtn = QPushButton("Plot in ToF", self)
        self.plotTOFBtn.setCursor(pointingCursor)
        self.plotTOFBtn.setObjectName("plotTOFBtn")
        self.plotTOFBtn.__name__ = "plotToFBtn"
        self.plotTOFBtn.resize(self.plotTOFBtn.sizeHint())
        self.plotTOFBtn.setEnabled(False)
        self.btnLayout.addWidget(self.plotTOFBtn)
        self.plotTOFBtn.clicked.connect(lambda: self.updateGuiData(tof=True))

        self.clearBtn = QPushButton("Clear All", self)
        self.clearBtn.setObjectName("clearBtn")
        self.clearBtn.setCursor(pointingCursor)
        self.clearBtn.__name__ = "clearBtn"
        self.clearBtn.resize(self.clearBtn.sizeHint())
        self.clearBtn.setEnabled(False)
        self.btnLayout.addWidget(self.clearBtn)
        self.clearBtn.clicked.connect(self.clear)

        self.pdBtn = QPushButton("Peak Detection", self)
        self.pdBtn.setObjectName("pdBtn")
        self.pdBtn.setCursor(pointingCursor)
        self.pdBtn.__name__ = "pdBtn"
        self.pdBtn.resize(self.pdBtn.sizeHint())
        self.pdBtn.setEnabled(False)
        self.btnLayout.addWidget(self.pdBtn)
        self.pdBtn.clicked.connect(self.getPeaks)

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
        self.thresholdCheck.setObjectName("thresholdCheck")
        self.thresholdCheck.__name__ = "thresholdCheck"
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
        for file in os.listdir(f"{self.dir}data/Graph Data/Compound Data/"):
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
        self.toolbar = NavigationToolbar(self.canvas, coordinates=True)

        canvasLayout.addWidget(self.toolbar)
        canvasLayout.addWidget(self.canvas)

        # * -----------------------------------------------

        # ¦ -------------------- Table --------------------
        # Adding table to display peak information
        self.table = QTableView()
        self.table.setObjectName('dataTable')
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(200)

        # * -----------------------------------------------

        container = QWidget(self)
        container.setObjectName('mainContainer')
        container.setLayout(canvasLayout)
        container.setMinimumHeight(300)

        splitter = QSplitter()
        splitter.setOrientation(Qt.Orientation.Vertical)
        splitter.addWidget(container)
        splitter.addWidget(self.table)
        splitter.setHandleWidth(10)

        contentLayout = QHBoxLayout()
        contentLayout.addWidget(splitter)
        sidebarLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        mainLayout.addItem(menubarLayout, 0, 0, 1, 50, Qt.AlignmentFlag.AlignTop)
        mainLayout.addItem(sidebarLayout, 1, 0, 1, 1, Qt.AlignmentFlag.AlignTop)
        mainLayout.addItem(contentLayout, 1, 1, 1, 50)
        self.btnLayout.setSpacing(10)
        self.toggleLayout.setSpacing(10)

        sidebarLayout.setSpacing(50)

        # If double-clicking cell, can trigger plot peak

        self.table.doubleClicked.connect(self.plotPeakWindow)

        self.setLayout(mainLayout)  # Generating layout
        self.show()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        """
        ``resizeEvent``
        ---------------
        On resize of connected widget event handler.

        Args:
            event (QtGui.QResizeEvent): Event triggered on resizing.

        Returns:
            ``None``
        """
        self.resized.emit()
        return super(ExplorerGUI, self).resizeEvent(event)

    def adjustCanvas(self) -> None:
        """
        ``adjustCanvas``
        ----------------
        Apply tight layout to figure.
        """
        self.figure.tight_layout()

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        """
        ``dragEnterEvent``
        ------------------
        Handles file drag enter event and verification

        Args:
            ``event`` (QDragEnterEvent): Event triggered on mouse dragging into the window.
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
        ``dropEvent``
        -------------
        Handles the drop event and calls to plot each data file

        Args:
            ``event`` (QDropEvent): PyQtEvent
        """
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            name = filepath.split('/')[-1].split('.')[0]
            self.updateGuiData(False, filepath, True, name)

    def editPeakLimits(self) -> None:
        """
        ``editPeakLimits``
        ------------------
        Edit Peaks opens a dialog window to alter limits of integration for peaks of the selected
        element, recalculating the integral and peak widths to place into the table.
        """
        # Click count to disconnect after two limits have been selected
        if self.plottedSpectra == []:
            QMessageBox.warning(self, "Error", "You have not plotted anything")
            return

        optionsWindow = InputElementsDialog(self, self.styleSheet())

        optionsWindow.elements.addItems(self.spectraData.keys())
        optionsWindow.elements.setMaxVisibleItems(5)

        elementPeaks = ExtendedComboBox()
        elementPeaks.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        firstLimitLayout = QHBoxLayout()
        firstLimitX = QLineEdit()

        firstLimitX.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))
        firstLimitBtn = QPushButton()
        firstLimitBtn.setObjectName("first")
        firstLimitBtn.setIcon(QIcon(".\\src\\img\\add-component.svg"))
        firstLimitLayout.addWidget(firstLimitX)
        firstLimitLayout.addWidget(firstLimitBtn)

        secondLimitLayout = QHBoxLayout()
        secondLimitX = QLineEdit()
        secondLimitX.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))
        secondLimitBtn = QPushButton()
        secondLimitBtn.setObjectName("second")
        secondLimitBtn.setIcon(QIcon(".\\src\\img\\add-component.svg"))
        secondLimitLayout.addWidget(secondLimitX)
        secondLimitLayout.addWidget(secondLimitBtn)

        optionsWindow.inputForm.addRow(QLabel("Peak X-Coord:"), elementPeaks)
        optionsWindow.inputForm.addRow(QLabel("1st Limit X:"), firstLimitLayout)
        optionsWindow.inputForm.addRow(QLabel("2nd Limit X:"), secondLimitLayout)

        applyBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Ok)
        applyBtn.setText("Apply")
        cancelBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)

        optionsWindow.inputForm.setSpacing(5)
        optionsWindow.mainLayout.insertItem(1, optionsWindow.inputForm)

        optionsWindow.setWindowTitle("Edit Peaks for Substance")
        optionsWindow.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        optionsWindow.setLayout(optionsWindow.mainLayout)
        elements = optionsWindow.elements

        ax = self.axPD if self.axPD is not None else self.ax

        def onAccept():

            elementName = elements.itemText(elements.currentIndex() or 0)
            peak = float(elementPeaks.currentText())
            leftLimit = float(firstLimitX.placeholderText() if firstLimitX.text(
            ) == '' else firstLimitX.text())
            rightLimit = float(secondLimitX.placeholderText() if secondLimitX.text(
            ) == '' else secondLimitX.text())

            result = self.spectraData[elementName].peakIntegral(leftLimit, rightLimit)
            print("\n")
            print(f"Peak: {peak}\n")
            print(f"Integral: {result}")
            self.figure.canvas.mpl_disconnect(optionsWindow.motionEvent)
            self.figure.canvas.mpl_disconnect(optionsWindow.buttonPressEvent)
        applyBtn.clicked.connect(onAccept)

        def onClose():
            self.figure.canvas.mpl_disconnect(optionsWindow.motionEvent)
            self.figure.canvas.mpl_disconnect(optionsWindow.buttonPressEvent)
            optionsWindow.close()
        cancelBtn.clicked.connect(onClose)

        def onElementChange(index):

            element = self.spectraData.get(elements.currentText(), False)
            elementPeaks.blockSignals(True)
            firstLimitX.setText(None)
            secondLimitX.setText(None)
            elementPeaks.clear()
            if not element:
                elements.lineEdit().setText(None)
                elements.setCurrentIndex(0)
                return

            if element.maxima[0].size == 0 or element.maxPeakLimitsX == {}:
                elementPeaks.setEnabled(False)
                firstLimitX.setEnabled(False)
                secondLimitX.setEnabled(False)
                applyBtn.setEnabled(False)
                firstLimitBtn.setEnabled(False)
                secondLimitBtn.setEnabled(False)
                elementPeaks.setCurrentText("Null")
                firstLimitX.setPlaceholderText("Null")
                secondLimitX.setPlaceholderText("Null")
                elementPeaks.blockSignals(False)

                return
            elementPeaks.setEnabled(True)
            firstLimitX.setEnabled(True)
            secondLimitX.setEnabled(True)
            firstLimitBtn.setEnabled(True)
            secondLimitBtn.setEnabled(True)
            elementPeaks.addItems([str(peak) for peak in element.maxima[0] if element.maxPeakLimitsX.get(peak, False)])
            elementPeaks.blockSignals(False)

            onPeakChange(elements.currentIndex())

        def onPeakChange(index):

            element = self.spectraData.get(elements.currentText(), False)
            if not element or elementPeaks.currentText() == '':
                elements.lineEdit().setText(None)
                elements.setCurrentIndex(0)
                elementPeaks.setCurrentIndex(0)
                return
            firstLimitX.setText(None)
            secondLimitX.setText(None)
            if element.maxPeakLimitsX == {}:
                elements.setCurrentIndex(0)
                elementPeaks.setCurrentText("Null")
                firstLimitX.setPlaceholderText("Null")
                secondLimitX.setPlaceholderText("Null")
                applyBtn.setEnabled(False)
                return
            applyBtn.setEnabled(True)
            peak = float(elementPeaks.currentText())
            firstLimitX.setPlaceholderText(str(element.maxPeakLimitsX[peak][0]))
            secondLimitX.setPlaceholderText(str(element.maxPeakLimitsX[peak][1]))

            try:
                optionsWindow.blittedCursor.on_remove()
                del optionsWindow.blitterCursor

            except AttributeError:
                pass

        def onLimitChange():

            limitLeft = firstLimitX.placeholderText() if firstLimitX.text(
            ) == '' else firstLimitX.text()
            limitRight = secondLimitX.placeholderText() if secondLimitX.text(
            ) == '' else secondLimitX.text()
            peak = float(elementPeaks.currentText())
            if limitLeft == 'Null' or limitRight == 'Null':
                applyBtn.setEnabled(False)
                return
            if float(limitLeft) > peak or float(limitRight) < peak:
                applyBtn.setEnabled(False)
                return
            try:
                optionsWindow.blittedCursor.on_remove()
                del optionsWindow.blittedCursor

            except AttributeError:
                pass
            for line in ax.get_lines() + ax.texts:
                if 'cursor' in line.get_gid():
                    line.remove()
            applyBtn.setEnabled(True)

        def onLimitSelect(event):
            if not optionsWindow.blittedCursor.valid:
                return
            else:
                if optionsWindow.which == 'first':
                    firstLimitX.setText(f"{round(optionsWindow.blittedCursor.x, 3)}")
                if optionsWindow.which == 'second':
                    secondLimitX.setText(f"{round(optionsWindow.blittedCursor.x, 3)}")

            try:
                optionsWindow.blittedCursor.on_remove()
                del optionsWindow.blittedCursor

            except AttributeError:
                pass
            self.figure.canvas.mpl_disconnect(optionsWindow.motionEvent)
            self.figure.canvas.mpl_disconnect(optionsWindow.buttonPressEvent)

        def connectLimitSelect(btn):
            optionsWindow.which = btn.objectName()
            optionsWindow.blittedCursor = BlittedCursor(ax=ax, axisType='x', which=optionsWindow.which)

            self.figure.canvas.mpl_disconnect(optionsWindow.motionEvent)
            self.figure.canvas.mpl_disconnect(optionsWindow.buttonPressEvent)
            optionsWindow.motionEvent = self.figure.canvas.mpl_connect(
                'motion_notify_event',
                lambda event: optionsWindow.blittedCursor.on_mouse_move(event, float(elementPeaks.currentText())))
            optionsWindow.buttonPressEvent = self.figure.canvas.mpl_connect("button_press_event", onLimitSelect)
        firstLimitBtn.pressed.connect(lambda: connectLimitSelect(firstLimitBtn))
        secondLimitBtn.pressed.connect(lambda: connectLimitSelect(secondLimitBtn))

        optionsWindow.elements.currentIndexChanged.connect(
            lambda: onElementChange(index=optionsWindow.elements.currentIndex()))
        elementPeaks.currentIndexChanged.connect(lambda: onPeakChange(elements.currentIndex()))
        firstLimitX.textChanged.connect(onLimitChange)
        secondLimitX.textChanged.connect(onLimitChange)

        onElementChange(elements.currentIndex())
        optionsWindow.setModal(False)
        optionsWindow.show()

    def editDistribution(self) -> None:
        """
        ``editDistribution``
        --------------------
        Opens a dialog window with options to alter the natural abundance of elements and compounds
        updating the graph data of any relevant plots.
        """

        optionsWindow = InputElementsDialog(self, self.styleSheet())
        optionsWindow.elements.addItems(
            [el for el in self.combobox.getAllItemText() if 'element' in el])
        optionsWindow.elements.addItems(self.compoundCombobox.getAllItemText())

        totalLabel = QLabel()

        applyBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Apply)
        applyBtn.setEnabled(False)
        applyBtn.setText("Apply")
        resetBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Reset)
        cancelBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)

        optionsWindow.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
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

                self.elementDistributions[elementName][title] = dist

            for title, Tof in self.plottedSpectra:

                if elementName == title:
                    title = f"{title}-{'ToF' if Tof else 'Energy'}"

                    self.spectraData[title].distributions = self.elementDistributions[elementName]

                    self.spectraData[title].isDistAltered = True
                    self.spectraData[title].isGraphDrawn = False
                    self.isCompound = self.spectraData[title].isCompound
                    self.selectionName = elementName

                    self.updateGuiData(tof=Tof, distAltered=True)
                    break
        applyBtn.clicked.connect(onAccept)
        cancelBtn.clicked.connect(optionsWindow.reject)

        def onReset():
            onElementChange(index=elements.currentIndex(), reset=True)
            applyBtn.setEnabled(True)
        resetBtn.clicked.connect(onReset)

        def onElementChange(index=0, reset: bool = False):

            elementName = elements.itemText(elements.currentIndex())
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
            totalLabel.setText(f"Total: {round(total, int(acc) - 1)}")
        optionsWindow.elements.setFocus()
        optionsWindow.elements.editTextChanged.connect(lambda: onElementChange(optionsWindow.elements.currentIndex()))

        def onDistributionChange():

            elementName = elements.itemText(elements.currentIndex() or 0)
            if elementName == '':
                return
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

        onElementChange(optionsWindow.elements.currentIndex())
        optionsWindow.setModal(False)
        optionsWindow.show()

    def editThresholdLimit(self) -> None:
        """
        ``editThresholdLimit``
        ----------------------
        Creates a GUI to alter the threshold value for a selected graph, recomputing maximas and
        drawing the relevant annotations
        """
        if self.spectraData == {}:
            return

        optionsWindow = InputElementsDialog(self, self.styleSheet())
        optionsWindow.inputForm.windowTitle = "Threshold Input"

        elements = optionsWindow.elements

        elements.addItems(self.spectraData.keys())

        inputThreshold = QLineEdit()
        inputThreshold.setPlaceholderText(str(self.spectraData[elements.currentText()].threshold))
        inputThreshold.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        optionsWindow.inputForm.addRow(QLabel("Threshold:"), inputThreshold)

        applyBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Apply)
        cancelBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        applyBtn.setEnabled(False)

        optionsWindow.setWindowTitle("Edit Threshold Value")
        optionsWindow.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        optionsWindow.mainLayout.insertItem(1, optionsWindow.inputForm)
        optionsWindow.setLayout(optionsWindow.mainLayout)

        def close():
            optionsWindow.close()
        cancelBtn.clicked.connect(close)

        def onElementChange(index):
            if elements.itemText(index) == '':
                elements.setCurrentIndex(0)
                inputThreshold.setText(None)
                return
            inputThreshold.setPlaceholderText(str(self.spectraData[elements.itemText(index)]))
        elements.editTextChanged.connect(lambda: onElementChange(elements.currentIndex()))

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

            self.spectraData[substance_name].threshold = threshold_value
            self.spectraData[substance_name].updatePeaks()
            self.addTableData()
            self.toggleThreshold()
            self.drawAnnotations(self.spectraData[substance_name])
            for element in self.spectraData.values():
                if element.isMaxDrawn:
                    element.isGraphUpdating = True
                    self.plottingPD(element, True)
                if element.isMinDrawn:
                    element.isGraphUpdating = True
                    self.plottingPD(element, False)
        applyBtn.clicked.connect(onAccept)

        inputThreshold.setFocus()
        optionsWindow.setModal(False)
        optionsWindow.show()

    def editLength(self):

        optionsWindow = QDialog(self)
        optionsWindow.setObjectName("inputWindow")
        mainLayout = QVBoxLayout()
        inputForm = QFormLayout()

        buttonBox = QDialogButtonBox(optionsWindow)
        applyBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Apply)
        applyBtn.setEnabled(False)

        cancelBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)

        mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        optionsWindow.setWindowTitle("Edit Length")
        optionsWindow.setLayout(mainLayout)
        lineEditNG = QLineEdit()
        lineEditNG.setValidator(QRegExpValidator(QRegExp("([0-9]*[.])?[0-9]+")))
        lineEditNG.setPlaceholderText(str(self.length["n-g"]))
        lineEditNTOT = QLineEdit()
        lineEditNTOT.setValidator(QRegExpValidator(QRegExp("([0-9]*[.])?[0-9]+")))
        lineEditNTOT.setPlaceholderText(str(self.length["n-tot"]))

        inputForm.addRow(QLabel("n-g Length:"), lineEditNG)
        inputForm.addRow(QLabel("n-tot Length:"), lineEditNTOT)

        mainLayout.addLayout(inputForm)
        mainLayout.addWidget(buttonBox)

        def onInputChange():
            applyBtn.setEnabled(lineEditNG.text() != '' and lineEditNTOT.text() != '')
        lineEditNG.textEdited.connect(onInputChange)
        lineEditNTOT.textEdited.connect(onInputChange)

        def onCancel():
            optionsWindow.close()
        cancelBtn.clicked.connect(onCancel)

        def onAccept():
            lengthConversion = deepcopy(self.length)

            self.length["n-g"] = float(lineEditNG.text())
            self.length["n-tot"] = float(lineEditNTOT.text())

            lengthConversion["n-g"] = self.length["n-g"] / lengthConversion["n-g"]
            lengthConversion["n-tot"] = self.length["n-tot"] / lengthConversion["n-tot"]
            for spectra in self.spectraData.values():
                spectra.length = self.length
                if spectra.isToF:
                    spectra.graphData = spectra.graphData * \
                        [lengthConversion[spectra.plotType], 1]

                for line in self.ax.lines:
                    if f"{spectra.name}-{'ToF'}" == line.get_label():
                        line.set_xdata(spectra.graphData[0])
                        break

            self.canvas.draw()
        applyBtn.clicked.connect(onAccept)

        optionsWindow.setModal(False)
        optionsWindow.show()

    def gridLineOptions(self):
        """
        ``gridLineOptions``
        -------------------
        Opens a dialog with settings related to the gridlines of the canvas.
        Options include: Which axis to plot gridlines for, which type; major, minor or both ticks, as well as color.
        """

        optionsWindowDialog = QDialog()
        optionsWindowDialog.setStyleSheet(self.styleSheet())
        optionsWindowDialog.setWindowTitle("Gridline Options")
        optionsWindowDialog.setObjectName("optionsDialog")
        mainLayout = QVBoxLayout()
        formLayout = QFormLayout()
        formLayout.setObjectName("inputForm")

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
        gridColorBtn.setStyleSheet(f"""
                                   border: 1px solid #AAA;
                                   background-color:{self.gridSettings['color']};
                                   """)

        gridLineLabel = QLabel("Gridline Options:")
        gridLineLabel.setObjectName("gridOptionLabel")
        axisLabel = QLabel("Axis Options:")
        axisLabel.setObjectName("gridOptionLabel")
        colorLabel = QLabel("Gridline Color:")
        colorLabel.setObjectName("gridOptionLabel")

        formLayout.addRow(gridLineLabel, gridlineGroup)
        formLayout.addRow(axisLabel, axisGroup)
        formLayout.addRow(colorLabel, gridColorBtn)

        buttonBox = QDialogButtonBox()

        onResetBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Reset)
        onAcceptBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Apply)
        onCancelBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)

        mainLayout.addLayout(formLayout)
        mainLayout.addWidget(buttonBox)

        optionsWindowDialog.setLayout(mainLayout)

        def openColorDialog():
            optionsWindowDialog.blockSignals(True)
            gridColorDialog.setModal(True)
            gridColorDialog.show()
        gridColorBtn.clicked.connect(openColorDialog)

        def onColorPick():
            optionsWindowDialog.blockSignals(False)
            gridColorBtn.setStyleSheet(
                f"border: 1px solid #AAA; background-color: {str(gridColorDialog.selectedColor().name())};")
        gridColorDialog.colorSelected.connect(onColorPick)

        def onReset():
            map(lambda btn: btn.setChecked(False),
                getLayoutWidgets(mainLayout, QRadioButton))
            majorRadioBtn.setChecked(True)
            bothAxisRadioBtn.setChecked(True)
            gridColorDialog.setCurrentColor(QtGui.QColor(68, 68, 68, 255))

            gridColorBtn.setStyleSheet(f"border: 1px solid #AAA; background-color:{self.gridSettings['color']};")
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
        ``editMaxPeaks``
        ----------------
        Opens a Dialog window for inputting the max peak label quantity for a selected graph, drawingthe relevant
        annotations.
        """
        if self.spectraData == {}:
            return

        optionsWindow = InputElementsDialog(self, self.styleSheet())
        elements = optionsWindow.elements

        elements.addItems(self.spectraData.keys())

        inputMaxPeaks = QLineEdit()
        inputMaxPeaks.setPlaceholderText(str(self.spectraData[elements.currentText()].numPeaks))
        inputMaxPeaks.setValidator(QRegExpValidator(QRegExp("[0-9]{0,4}")))

        optionsWindow.inputForm.addRow(QLabel("Peak Quantity:"), inputMaxPeaks)

        applyBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Apply)
        cancelBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)

        optionsWindow.setWindowTitle("Displayed Peaks Quantity")
        optionsWindow.mainLayout.insertItem(1, optionsWindow.inputForm)
        optionsWindow.setLayout(optionsWindow.mainLayout)

        def closeWindow():
            optionsWindow.close()
        cancelBtn.clicked.connect(closeWindow)

        def changePeaksText():
            inputMaxPeaks.setPlaceholderText(str(self.spectraData[elements.currentText()].numPeaks))
        elements.activated.connect(changePeaksText)

        def onAccept():
            substance_name = elements.currentText()
            if inputMaxPeaks.text() == '':
                return
            maxPeaks = int(inputMaxPeaks.text())
            self.spectraData[substance_name].maxPeaks = maxPeaks
            self.drawAnnotations(self.spectraData[substance_name])
        applyBtn.clicked.connect(onAccept)

        optionsWindow.setModal(False)
        optionsWindow.show()

    def createCompound(self) -> None:
        """
        ``createCompound``
        ------------------
        Opens a dialog for users to create compounds from weighted combinations of varying elements, this calculates and
        saves the graph data to a file for reuse.
        """

        optionsWindow = InputElementsDialog(self, self.styleSheet())

        elements = optionsWindow.elements

        elements.lineEdit().setPlaceholderText("Select an Isotope / Element")
        elements.addItems([self.combobox.itemText(i)
                           for i in range(self.combobox.count()) if 'element' in self.combobox.itemText(i)])
        # elements.addItems([self.combobox.itemText(i)
        #                    for i in range(self.combobox.count()) if 'element' in self.combobox.itemText(i)])

        totalLabel = QLabel("Total: 0")

        applyBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Apply)
        applyBtn.setText("Create")
        applyBtn.setEnabled(False)

        addBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Yes)
        addBtn.setText("Add")
        addBtn.setEnabled(False)

        resetBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Reset)
        cancelBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)

        optionsWindow.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
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
            weightedGraphData = {name: pd.read_csv(f"{self.graphDataDir}{name}.csv",
                                                   names=['x', 'y'],
                                                   header=None) * [1, dist]
                                 for name, dist in compoundDist.items() if dist != 0}
            newElement = SpectraData(name, None, None, None, None, None, None, None, True)
            newElement.setGraphDataFromDist(weightedGraphData.values())
            newElement.graphData.to_csv(f"{self.graphDataDir}Compound Data\\{name}.csv",
                                        index=False,
                                        header=False)
            pd.DataFrame(compoundDist.items()).to_csv(
                f"{self.dir}data\\Distribution Information\\{name}.csv", index=False, header=False)

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

        def onElementChange(index):

            elementName = elements.itemText(index)
            if elementName == '':
                addBtn.setEnabled(False)
                return
            if elementName in compoundElements.keys():
                addBtn.setEnabled(False)
                return
            addBtn.setEnabled(True)
        elements.editTextChanged.connect(lambda: onElementChange(elements.currentIndex()))

        def onAddRow(index=None):

            elementName = elements.itemText(elements.currentIndex() or 0)
            if elementName == '':
                elements.setCurrentIndex(0)
                return
            if compoundElements == {}:
                compoundMode.append(elementName.split('_')[-1])

                elements.blockSignals(True)
                elementNames = elements.getAllItemText()
                elements.clear()
                elements.addItems([name for name in elementNames if compoundMode[0] in name])
                elements.blockSignals(False)

            totalLabel.setStyleSheet("color: #FFF;")

            sublayout = QHBoxLayout()
            proxyWidget = QWidget()
            newQLineEdit = QLineEdit()
            newQLineEdit.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))

            newQLineEdit.setValidator(QRegExpValidator(
                QRegExp("(0?(\\.[0-9]{1,6})?|1(\\.0{1,6})?)")))
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

            total = round(total, 6)
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
        onElementChange(elements.currentIndex())
        optionsWindow.setModal(False)
        optionsWindow.show()

    def viewDarkStyle(self) -> None:
        """
        ``viewDarkStyle``
        -----------------
        Applies the dark theme to the GUI.
        """
        self.setStyleSheet(self.styleMain.format(bg_color="#202020", text_color="#FFF"))

    def viewLightStyle(self) -> None:
        """
        ``viewLightStyle``
        ------------------
        Applies the light theme to the GUI.
        """
        self.setStyleSheet(self.styleMain.format(bg_color="#968C80", text_color="#FFF"))

    def viewHighContrastStyle(self) -> None:
        """
        ``viewHighContrastStyle``
        -------------------------
        Applies the high contrast theme to the GUI.
        """
        self.setStyleSheet(self.styleMain.format(bg_color="#000", text_color="#FFF"))

    def toggleBtnControls(self, enableAll: bool = False, plotEnergyBtn: bool = False,
                          plotToFBtn: bool = False, clearBtn: bool = False, pdBtn: bool = False) -> None:
        """
        ``toggleBtnControls``
        ---------------------
        Enables and disables the buttons controls, thus only allowing its use when required. ``enableAll`` is done
        before any kwargs have an effect on the buttons. ``enableAll`` defaults to False, True will enable all buttons
        regardless of other kwargs.

        This way you can disable all buttons then make changes to specific buttons.

        Args:
            - ``enableAll`` (bool): Boolean to enable/disable (True/False) all the buttons controls.

            - ``plotEnergyBtn`` (bool): Boolean to enable/disable (True/False) Plot Energy button.

            - ``plotToFBtn`` (bool): Boolean to enable/disable (True/False) Plot ToF button.

            - ``clearBtn`` (bool): Boolean to enable/disable (True/False) Clear button.

            - ``pdBtn`` (bool): Boolean to enable/disable (True/False) Peak Detection button.
        """

        for btn in getLayoutWidgets(self.btnLayout):
            btn.setEnabled(enableAll)

        if enableAll:
            return

        for btn in getLayoutWidgets(self.btnLayout):
            if btn.__name__ == 'plotEnergyBtn':
                btn.setEnabled(plotEnergyBtn)
            if btn.__name__ == 'plotToFBtn':
                btn.setEnabled(plotToFBtn)
            if btn.__name__ == 'clearBtn':
                btn.setEnabled(clearBtn)
            if btn.__name__ == 'pdBtn':
                btn.setEnabled(pdBtn)

    def toggleCheckboxControls(self, enableAll: bool, gridlines: bool = False,
                               peakLimit: bool = False, hidePeakLabels: bool = False) -> None:
        """
        ``toggleCheckboxControls``
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
            if btn.__name__ == 'gridCheck':
                btn.setEnabled(gridlines)
            if btn.__name__ == 'peakCheck':
                btn.setEnabled(hidePeakLabels)
            if btn.__name__ == 'pdCheck':
                btn.setEnabled(peakLimit)

    def plotSelectionProxy(self, index, comboboxName):
        """
        ``plotSelectionProxy``
        ----------------------
        Handles whether the selection made is from the compound list or not, calling resetTableProxy with the combobox
        being used.

        Args:
            - ``index`` (int): Index of selection given from PyQtSignal.

            - ``comboboxName`` (str): Identifier of combobox which made the signal.
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
        ``resetTableProxy``
        -------------------
        Handles setting the data in the table, either displaying the data from a single selection, or returning to the
        previous state of the table.

        Args:
            - ``combobox`` (QComboBox): The Combobox from which the selection was made.
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
                self.selectionName = combobox.currentText()
                self.displayData()
        except AttributeError:
            self.table.setModel(None)

    def displayData(self) -> None:
        """
        ``displayData``
        ---------------
        Will display relevant peak information in the table for the selection made (self.selectionName).
        Once a select is made, the relevant controls are enabled.
        """
        if self.selectionName == "" and self.plotCount > -1:  # Null selection and graphs shown
            self.toggleBtnControls(clearBtn=True)
            return
        elif self.selectionName == "" and self.plotCount == -1:  # Null selection and no graphs shown
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
        split = self.selectionName.split("-")
        if self.selectionName.startswith("e"):
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
            if self.selectionName[-1] == 't':
                self.threshold = self.thresholds[dataSymbol][0]
            else:
                self.threshold = self.thresholds[dataSymbol][1]
        self.thresholdLabel.setText(str(labelInfo))
        # Changing the peak label text
        labelInfo = "Number of peaks: " + str(self.numRows)
        self.peaklabel.setText(str(labelInfo))

    def showTableData(self):
        """
        ``showTableData``
        -----------------
        Read and display the selected substances data within the table.
        """
        # Finding relevant file for peak information
        peakInfoDir = self.dir + "data/Peak information/"

        filepath = None
        for file in os.listdir(peakInfoDir):
            if self.selectionName == file.split(".")[0]:
                filepath = peakInfoDir + file
                break
        try:
            for row in self.table_model.titleRows:
                self.table.setItemDelegateForRow(row, None)
        except AttributeError:
            pass
        try:
            self.table.blockSignals(True)
            file = pd.read_csv(filepath, header=0)
            # Reset any changes to spans before displaying selection data.
            self.table.clearSpans()

            if self.selectionName not in self.plottedSpectra:
                self.numRows = file.shape[0]
            print("Number of peaks: ", self.numRows)
            # Fill Table with data
            tempTableModel = ExtendedQTableModel(file)
            proxy = CustomSortingProxy()
            proxy.setSourceModel(tempTableModel)

            self.table.setModel(proxy)
            self.table.setSortingEnabled(True)
            self.table.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        except ValueError:

            self.table.setModel(None)
            self.numRows = None

    def addTableData(self, reset=False):
        """
        ``addTableData``
        ----------------
        Concatenates the selected spectra table data to the other plotted spectra adding a toggle drop-down title row.

        Args:
            - ``reset`` (bool, optional): Whether to default back to the current state of the table. Defaults to False.
        """
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
        for spectra in self.spectraData.values():
            if spectra.name not in self.elementDataNames:
                table_data = pd.concat([table_data, spectra.tableData], ignore_index=True)
                self.titleRows.append(self.titleRows[-1] + spectra.tableData.shape[0])
                self.elementDataNames.append(spectra.name)

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
        self.table.blockSignals(False)

    def updateGuiData(self, tof: bool = False, filepath: str = None, imported: bool = False, name: str = None,
                      distAltered: bool = False) -> None:
        """
        ``updateGuiData``
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

        """

        # Enable Checkboxes on plotting graphs
        self.toggleCheckboxControls(enableAll=True)
        self.toggleBtnControls(enableAll=True)

        if self.selectionName is None and not imported:
            QMessageBox.warning(self, "Error", "You have not selected anything to plot")
            return
        if imported:
            self.selectionName = name
            self.threshold = 100
        # Checks for adding mutliple graphs for the same selection, energy/tof types.
        if (self.selectionName, tof) in self.plottedSpectra and not distAltered:
            QMessageBox.warning(self, "Warning", "Graph is already plotted")
            return

        if (self.selectionName, tof) not in self.plottedSpectra:
            self.plottedSpectra.append((self.selectionName, tof))
        # Handles number_totpeaks when plotting energy and tof of the same graph

        # # Finds the mode for L0 (length) parameter

        self.titleRows = [0]
        for (element, tof) in self.plottedSpectra:
            title = f"{element}-{'ToF' if tof else 'Energy'}"
            # ¦ -----------------------------------

            if title in self.spectraData.keys():
                if self.spectraData[title].isGraphDrawn:
                    continue
            if self.isCompound:
                self.plotFilepath = f"{self.graphDataDir}Compound Data\\{element}.csv"
            else:
                self.plotFilepath = f"{self.graphDataDir}{element}.csv" if filepath is None else filepath
            peakInfoDir = f"{self.dir}data\\Peak information\\" if filepath is None else None

            try:
                graphData = pd.read_csv(self.plotFilepath, header=None).iloc[:, :2]

            except pd.errors.EmptyDataError:
                QMessageBox.warning(self, "Warning", "Selection has Empty Graph Data")
                self.plottedSpectra.remove((self.selectionName, tof))
                if self.plotCount == -1:
                    self.toggleCheckboxControls(enableAll=False)
                    self.toggleBtnControls(plotEnergyBtn=True, plotToFBtn=True, clearBtn=True, pdBtn=False)
                return
            except FileNotFoundError:
                if self.spectraData.get(element, False):
                    self.spectraData[element].graphData.to_csv(self.plotFilepath, index=False, header=False)
                    graphData = self.compoundData[element].graphData

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

            if self.spectraData.get(title, False):
                for point in self.spectraData[title].annotations:
                    point.remove()

            newSpectra = SpectraData(name=element,
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

            self.spectraData[title] = newSpectra

        redrawMax = False
        redrawMin = False
        if distAltered:
            for line in self.ax.get_lines():
                if newSpectra.name in line.get_label():
                    line.remove()
            try:
                for line in self.axPD.get_lines():
                    if 'max' in line.get_gid():
                        redrawMax = True
                    if 'min' in line.get_gid():
                        redrawMin = True
                    if newSpectra.name in line.get_label() or newSpectra.name in line.get_gid():
                        line.remove()

            except AttributeError:
                pass

        distAltered = False

        self.plot(newSpectra, filepath, imported, name)
        if redrawMax:
            self.plottingPD(newSpectra, True)
        if redrawMin:
            self.plottingPD(newSpectra, False)
        self.addTableData()

        self.canvas.draw()

    def plot(self, spectraData: SpectraData, filepath: str = None, imported: bool = False, name: str = None) -> None:
        """
        ``plot``
        --------
        Will plot the inputted spectraData's spectra to the canvas.

        Args:
            - ``spectraData`` (SpectraData): The spectraData to be plotted

            - ``filepath`` (str, optional): Filepath of imported spectra. Defaults to None.

            - ``imported`` (bool, optional): Whether or not the data has been imported. Defaults to False.

            - ``name`` (str, optional): The name of the imported spectra. Defaults to None.
        """
        if spectraData is None:
            return

        # General Plotting ---------------------------------------------------------------------------------------------
        if self.plotCount < 0:
            self.ax = self.figure.add_subplot(111)
            # Setting scale to be logarithmic

            self.ax.set_yscale("log")
            self.ax.set_xscale("log")
            self.ax.minorticks_on()
            plt.minorticks_on()
            self.ax.xaxis.set_minor_locator(LogLocator(10, 'all'))
            self.ax.xaxis.set_minor_formatter(LogFormatter(10, False, (np.inf, np.inf)))
            self.ax.xaxis.set_tick_params('minor',
                                          size=2,
                                          color="#888",
                                          labelsize=6,
                                          labelrotation=30,
                                          )

        # Allows user to plot in ToF if chosen # -----------------------------------------------------------------------
        if spectraData.isToF and not imported:
            # ! Convert to pandas compatible

            if self.plotCount < 0:
                self.ax.set(
                    xlabel="ToF (uS)", ylabel="Cross section (b)", title=self.selectionName
                )
        else:
            if self.plotCount < 0:
                if spectraData.isToF:
                    self.ax.set(
                        xlabel="Time of Flight (uS)",
                        ylabel="Cross section (b)",
                        title=self.selectionName,
                    )
                else:
                    self.ax.set(
                        xlabel="Energy (eV)",
                        ylabel="Cross section (b)",
                        title=self.selectionName,
                    )
            else:
                self.ax.set(title=None)

        # Plotting -----------------------------------------------------------------------------------------------------

        label = f"{spectraData.name}-ToF" if spectraData.isToF else f"{spectraData.name}-Energy"

        if not spectraData.graphData.empty:
            # if not spectraData.isGraphUpdating:

            self.ax.plot(
                spectraData.graphData.iloc[:, 0],
                spectraData.graphData.iloc[:, 1],
                "-",
                c=spectraData.graphColour,
                alpha=0.6,
                linewidth=0.8,
                label=label,
                gid=spectraData.name if self.selectionName is None else self.selectionName,
            )
            spectraData.isGraphDrawn = True
            # else:
            #     for line in self.ax.lines:
            #         if f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}" == line.get_label():
            #             line.set_data(spectraData.graphData)
            #             self.canvas.draw()
            #             break
            #     try:
            #         for line in self.axPD.lines:
            #             if f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}" == line.get_label():
            #                 line.set_data(spectraData.graphData)
            #                 self.canvas.draw()
            #                 break
            #     except AttributeError:
            #         pass
            spectraData.isGraphUpdating = False
        self.updateLegend()

        # Establishing plot count
        self.plotCount += 1

        self.drawAnnotations(spectraData)
        self.toggleThreshold()

        self.ax.autoscale()  # Tidying up

        self.figure.tight_layout()

        self.canvas.draw()

    def updateLegend(self):
        """
        ``updateLegend``
        ----------------
        Will update the legend to contain all currently plotted spectra and connect the 'pick_event'
        to each legend line to ``hideGraph``.
        """
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
                    legLine.set_pickradius(7)
                    legLine.set_color(self.spectraData[origLine.get_label()].graphColour)
                    legLine.set_alpha(1.0 if origLine.get_visible() else 0.2)

                    self.legOrigLines[legLine] = origLine

    def energyToTOF(self, xData: list[float], length: float) -> list[float]:
        """
        ``energyToTOF``
        ---------------
        Maps all X Values in the given array from energy to TOF

        Args:
            - ``xData`` (list[float]): List of the substances x-coords of its graph data

            - ``length`` (float): Constant value associated to whether the element data is with repsect to n-g or n-tot

        Returns:
            ``list[float]``: Mapped x-coords
        """
        # ! Add a way to change length at runtime per spectra
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
        ``hideGraph``
        -------------
        Function to show or hide the selected graph by clicking the legend.

        Args:
            - ``event`` (pick_event): event on clicking a graphs legend
        """
        # Tells you which plot number you need to deleteLater() labels for

        legline = event.artist
        if self.ax.get_visible():
            axis, legOrigLines = self.ax, self.legOrigLines
        if self.axPD is not None:
            if self.axPD.get_visible():
                axis, legOrigLines = self.axPD, self.legOrigLinesPD

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
        spectraData = self.spectraData[orgline_name]
        spectraData.isGraphHidden = not newVisible
        spectraData.hideAnnotations(self.peakLabelCheck.isChecked())
        for line in axis.lines:
            if line.get_gid() == f"pd_threshold-{orgline_name}":
                line.set_visible(newVisible)
                continue
            if f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-max" in line.get_gid():
                line.set_visible(newVisible)
                continue
            if f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-min" in line.get_gid():
                line.set_visible(newVisible)
                continue

        self.canvas.draw()

    def clear(self) -> None:
        """
        ``clear``
        ---------
        Function will empty all data from the table, all graphs from the plots, along with resetting all data associated
        the table or plot and disables relevant controls.
        """
        try:
            self.figure.clear()
            self.ax.clear()
            self.axPD = None
            self.canvas.draw()
        except AttributeError:
            pass

        self.plotCount = -1
        self.annotations = []
        self.localHiddenAnnotations = []
        self.peaklabel.setText("")
        self.thresholdLabel.setText("")

        self.spectraData = {}
        self.elementDataNames = []
        try:
            for row in self.table_model.titleRows:
                self.table.setItemDelegateForRow(row, None)
        except AttributeError:
            pass

        self.table.setModel(None)

        self.table_model = None
        self.plottedSpectra = []
        self.elementDistributions = deepcopy(self.defaultDistributions)

        self.toggleBtnControls(plotEnergyBtn=True, plotToFBtn=True, clearBtn=True)
        self.toggleCheckboxControls(enableAll=False)

    def toggleGridlines(self, visible: bool,
                        which: Literal["major", "minor", "both"] = "major",
                        axis: Literal["both", "x", "y"] = "both",
                        color="#444") -> None:
        """
        ``toggleGridlines``
        -------------------
        Will toggle visibility of the gridlines on the axis which is currently shown.

        Args:
            - ``visible`` (bool): Whether or not gridlines should be shown.

            - ``which`` (Literal["major", "minor", "both"], optional):
            Whether to show major, minor or both gridline types. Defaults to "major".

            - ``axis`` (Literal["both", "x", "y"], optional):
            Whether or not to show gridlines on x, y, or both. Defaults to "both".

            - ``color`` (str, optional): Gridline Color. Defaults to "#444".
        """
        try:
            self.ax.minorticks_on()
            self.ax.tick_params(which='minor', axis='x')
            self.ax.tick_params(**self.gridSettings)
            self.ax.grid(visible=False, which='both')

            if visible and self.ax.get_visible():
                self.ax.grid(visible=visible, which=which, axis=axis, color=color, alpha=0.2)
            else:
                self.ax.grid(visible=visible, which="both")

            self.axPD.minorticks_on()
            self.axPD.tick_params(which='minor', axis='x')
            self.axPD.tick_params(**self.gridSettings)
            self.axPD.grid(visible=False, which='both')

            if visible and self.axPD.get_visible():
                self.axPD.grid(visible=visible, which=which, axis=axis, color=color, alpha=0.2)
            else:
                self.axPD.grid(visible=visible, which="both")
        except AttributeError:
            pass
        self.canvas.draw()

    def toggleThreshold(self) -> None:
        """
        ``toggleThreshold``
        -------------------
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
            for line in self.axPD.get_lines():
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
            for name, element in self.spectraData.items():
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
                    if self.axPD.get_visible() and (element.isMaxDrawn or element.isMinDrawn):
                        line = self.axPD.axhline(
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
        """
        ``onPeakOrderChange``
        ---------------------
        Handles changing the order of peaks then redrawing the annotations.
        """
        if self.sender().objectName() == "orderByIntegral":
            self.orderByIntegral = self.byIntegralCheck.isChecked()

        if self.sender().objectName() == "orderByPeakW":
            self.orderByIntegral = self.byIntegralCheck.isChecked()

        for element in self.spectraData.values():
            self.drawAnnotations(element)

    def drawAnnotations(self, element: SpectraData) -> None:
        """
        ``drawAnnotations``
        -------------------
        Will plot each numbered annotation in the order of Integral or Peak Width.

        Args:
            - ``element`` (SpectraData): The data for the element your annotating
        """
        self.elementDataNames = []

        if element.isAnnotationsDrawn:
            for anno in element.annotations:
                anno.remove()
            element.annotations.clear()

        if element.maxima.size == 0:
            return

        if element.tableData is not None:
            element.orderAnnotations(self.orderByIntegral)

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
                                                size=7,
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
        ``toggleAnnotations``
        ---------------------
        Toggles visibility of all peak annotations globally.
        """
        for element in self.spectraData.values():
            element.hideAnnotations(self.peakLabelCheck.isChecked())
            element.isAnnotationsHidden = not element.isAnnotationsHidden

        self.canvas.draw()

    def plotPeakWindow(self, index: QModelIndex) -> None:
        """
        ``plotPeakWindow``
        ------------------
        Opens a window displaying the graph about the selected peak within the bounds of integration
        as well as data specific to the peak.

        Args:
            index (QModelIndex): Index object for the selected cell.
        """
        peakWindow = QMainWindow(self)
        # Setting title and geometry
        peakWindow.setWindowTitle("Peak Plotting")
        peakWindow.setGeometry(350, 50, 850, 700)
        peakWindow.setObjectName("mainWindow")
        peakWindow.setStyleSheet(self.styleSheet())
        # Creating a second canvas for singular peak plotting
        peakFigure = plt.figure()
        peakCanvas = FigureCanvas(peakFigure, contextConnect=False)
        toolbar = NavigationToolbar(peakCanvas, self)
        canvasLayout = QVBoxLayout()

        canvasProxyWidget = QWidget()
        canvasProxyWidget.setObjectName("peakCanvasContainer")
        canvasLayout.addWidget(toolbar)
        canvasLayout.addWidget(peakCanvas)

        canvasProxyWidget.setLayout(canvasLayout)

        # Setting up dock for widgets to be used around canvas
        dock = QDockWidget(parent=peakWindow)
        # Creating a widget to contain peak info in dock
        peakInfoWidget = QWidget()

        # Creating layout to display peak info in the widget
        bottomLayout = QVBoxLayout()
        toggleLayout = QHBoxLayout()

        # Adding checkbox to toggle the peak limits on and off
        threshold_check2 = QCheckBox("Integration Limits", peakWindow)
        threshold_check2.resize(threshold_check2.sizeHint())
        threshold_check2.setObjectName("peakCheck")
        threshold_check2.setChecked(True)
        toggleLayout.addWidget(threshold_check2)

        # Adding checkbox to toggle the peak detection limits on and off
        threshold_check3 = QCheckBox("Peak Detection Limits", peakWindow)
        threshold_check3.setObjectName("peakCheck")
        threshold_check3.resize(threshold_check3.sizeHint())
        toggleLayout.addWidget(threshold_check3)
        # Adding to overall layout
        bottomLayout.addLayout(toggleLayout)

        peakTable = QTableView()

        bottomLayout.addWidget(peakTable)

        # Adding label which shows what scale the user picks
        scale_label = QLabel()
        scale_label.setObjectName("peakLabel")
        bottomLayout.addWidget(scale_label)

        # Setting layout within peak info widget
        peakInfoWidget.setLayout(bottomLayout)
        dock.setWidget(peakInfoWidget)  # Adding peak info widget to dock

        peakWindow.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        # Setting canvas as central widget
        peakWindow.setCentralWidget(canvasProxyWidget)

        self.peakAxis = None
        self.peakAxis = peakFigure.add_subplot(111)

        try:
            titleIndex = sorted([rowIndex for rowIndex in self.titleRows if index.row() > rowIndex])[-1]
            elementName = self.table_model.data(self.table_model.index(titleIndex, 0), 0)
            plottedSpectra = [name for name in self.plottedSpectra if elementName in name]
            optionsDialog = InputElementsDialog()
            if len(plottedSpectra) > 1:
                spectraNames = [f"{name}-{'ToF' if tof else 'Energy'}" for name, tof in plottedSpectra]
                optionsDialog.elements.addItems(spectraNames)
                optionsDialog.mainLayout.addWidget(optionsDialog.elements)

                acceptBtn = optionsDialog.buttonBox.addButton(QDialogButtonBox.StandardButton.Ok)

                def onAccept():
                    self.tof = 'ToF' in optionsDialog.elements.currentText()
                    optionsDialog.close()
                acceptBtn.clicked.connect(onAccept)

                optionsDialog.mainLayout.addWidget(optionsDialog.buttonBox)
                optionsDialog.setLayout(optionsDialog.mainLayout)
                optionsDialog.setModal(False)
                optionsDialog.exec_()
            else:
                self.tof = plottedSpectra[0][1]

            elementTitle = f"{elementName}-{'ToF' if self.tof else 'Energy'}"
            element = self.spectraData[elementTitle]
            if element.maxima.size == 0:
                return
            # if element.maxPeakLimitsX == dict():
            maximaX = nearestnumber(element.maxima[0], float(self.table_model.data(
                self.table_model.index(index.row(), 3 if self.tof else 1), 0)))
            maxima = [max for max in element.maxima.T if max[0] == maximaX][0]

            leftLimit, rightLimit = element.maxPeakLimitsX[maxima[0]]

            # else:
            #     leftLimit, rightLimit = element.maxPeakLimitsX[maxima[0]]

        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "No peak limits for this Selection")
        except AttributeError:
            QMessageBox.warning(self, "Warning", "Plot the Graph First")

        rank = [str([ann[0] for ann in element.annotationsOrder.items() if ann[1][0] == maxima[0]][0])]
        limits = [str(element.maxPeakLimitsX[maxima[0]])]
        peakCoords = [f"({maxima[0]}, {maxima[1]})"]
        isoOrigin = [self.table_model.data(self.table_model.index(index.row(), 9), 0)]
        data = {"Peak Number (Rank)": rank,
                "Integration Limits (eV)": limits,
                "Peak Co-ordinates (eV)": peakCoords,
                "Isotopic Origin": isoOrigin}

        tableData = pd.DataFrame(data, index=None)

        peakTable.setModel(ExtendedQTableModel(tableData))

        peakTable.setObjectName('dataTable')
        peakTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        peakTable.setAlternatingRowColors(True)
        peakTable.verticalHeader().setVisible(False)
        peakTable.setMinimumHeight(200)

        graphData = element.graphData[(element.graphData[0] >= leftLimit) & (element.graphData[0] <= rightLimit)]

        def togglePeakLimits() -> None:
            for line in self.peakAxis.get_lines():
                if "PeakWindow-lim" in line.get_gid():
                    line.set_visible(threshold_check2.isChecked())
            self.peakAxis.figure.canvas.draw()
        threshold_check2.clicked.connect(togglePeakLimits)

        def togglePeakThreshold(checked, element) -> None:
            if not threshold_check3.isChecked():
                for line in self.peakAxis.get_lines():
                    if line.get_gid() == f"PeakWindow-Threshold-{element.name}":
                        line.remove()

            else:
                self.peakAxis.axhline(y=element.threshold,
                                      linestyle="--",
                                      color=element.graphColour,
                                      linewidth=0.5,
                                      gid=f"PeakWindow-Threshold-{element.name}")
            self.peakAxis.figure.canvas.draw()
        threshold_check3.clicked.connect(lambda: togglePeakThreshold(threshold_check3.isChecked(), element))

        peakWindow.show()

        self.peakAxis.set_xscale('log')
        self.peakAxis.set_yscale('log')

        self.peakAxis.set(
            xlabel="Energy (eV)", ylabel="Cross section (b)", title=elementTitle
        )

        self.peakAxis.plot(graphData[0],
                           graphData[1],
                           color=element.graphColour,
                           linewidth=0.8,
                           label=elementTitle,
                           gid=f"{elementTitle}-PeakWindow"
                           )

        self.peakAxis.plot(maxima[0],
                           maxima[1],
                           "x",
                           color="black",
                           markersize=3,
                           alpha=0.6,
                           gid=f"{elementTitle}-PeakWindow-max"
                           )

        for i, (peakX, peakY) in enumerate(zip(element.maxPeakLimitsX[maxima[0]], element.maxPeakLimitsY[maxima[0]])):
            self.peakAxis.plot(peakX,
                               peakY,
                               marker=2,
                               color="r",
                               markersize=8,
                               gid=f"{elementTitle}-PeakWindow-lim-{i}")

        self.peakAxis.autoscale()
        peakFigure.tight_layout()
        self.peakAxis.legend(fancybox=True, shadow=True)

    def importData(self) -> None:
        """
        ``importData``
        --------------
        Allows user to select a file on their computer to open and analyse.
        """
        filename = QFileDialog.getOpenFileName(self, "Open file", self.dir, "*.csv *.txt *.dat")
        if filename[0] == '':
            return
        filepath = filename[0]
        getName = filepath.split("/")

        name = getName[-1].split('.')[0]

        if name[-1] == "f":
            self.updateGuiData(True, filepath, True, name)
        else:
            self.updateGuiData(False, filepath, True, name)

    def getPeaks(self) -> None:
        """
        ``getPeaks``
        ------------
        Ask the user for which function to plot the maxima or minima of which element
        then calls the respective function on that element
        """

        mainLayout = QVBoxLayout()
        inputForm = QFormLayout()
        inputForm.setObjectName('inputForm')

        elements = QComboBox()
        elements.setEditable(True)
        elements.addItems(self.spectraData.keys())
        elements.setMaxVisibleItems(5)

        elements.completer().setCompletionMode(
            QCompleter.CompletionMode.UnfilteredPopupCompletion
        )

        elements.completer().setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        elements.completer().setFilterMode(Qt.MatchFlag.MatchContains)

        inputMaxPeaks = QLineEdit()
        inputMaxPeaks.setPlaceholderText(str(self.spectraData[elements.currentText()].threshold))
        inputMaxPeaks.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        inputForm.addRow(QLabel("Spectra:"), elements)
        buttonBox = QDialogButtonBox()
        resetBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Reset)
        resetBtn.setText("Reset")
        maximaBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Yes)
        maximaBtn.setText("Maxima")
        minimaBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.No)
        minimaBtn.setText("Minima")
        cancelBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
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
            self.ax.autoscale(True)
            self.plottingPD(self.spectraData[elements.currentText()], True)
        maximaBtn.clicked.connect(max)

        def min():
            self.plottingPD(self.spectraData[elements.currentText()], False)
        minimaBtn.clicked.connect(min)

        def close():
            inputWindow.close()
        cancelBtn.clicked.connect(close)

        def changePeaksText():
            inputMaxPeaks.setPlaceholderText(str(self.spectraData[elements.currentText()].maxPeaks))
            maxCheck = self.spectraData[elements.currentText()].maxima.size != 0
            minCheck = self.spectraData[elements.currentText()].minima.size != 0

            maximaBtn.setEnabled(maxCheck)
            minimaBtn.setEnabled(minCheck)

            maximaBtn.setToolTip('' if maxCheck else "No Maximas Found")
            minimaBtn.setToolTip('' if minCheck else "No Minimas Found")

        elements.activated.connect(changePeaksText)
        changePeaksText()
        inputWindow.show()

        def ResetPDPlots() -> None:
            try:
                if self.axPD is not None:
                    self.axPD.set_visible(False)
                    self.axPD.clear()
                    self.axPD.remove()
                    self.axPD = None

                self.ax.set_visible(True)
                for element in self.spectraData.values():
                    element.isMaxDrawn = False
                    element.isMinDrawn = False
            except KeyError:
                return
            self.toggleThreshold()
            self.toggleGridlines(self.gridCheck.isChecked(), *self.gridSettings.values())
            self.toolbar.update()
            self.canvas.draw()
        resetBtn.clicked.connect(ResetPDPlots)

    def plottingPD(self, spectraData: SpectraData, isMax: bool) -> None:
        """
        ``plottingPD``
        --------------
        Takes plots the maximas or minimas of the inputted ``spectraData`` based on ``isMax``

        Args:
            - ``spectraData`` (SpectraData): SpectraData Class specifying the element

            - ``isMax`` (bool): Maxima if True else Minima
        """
        if spectraData.isMinDrawn and not isMax and not spectraData.isGraphUpdating:
            return
        if spectraData.isMaxDrawn and isMax and not spectraData.isGraphUpdating:
            return
        if isMax:
            peaksX, peaksY = spectraData.maxima[0], spectraData.maxima[1]

        else:
            peaksX, peaksY = spectraData.minima[0], spectraData.minima[1]

        # ! Add element selection to Peak Detection menu
        # ! Change how points are then plotted
        # Redrawing graph and Peak Detection Limits
        self.ax.set_visible(False)

        if self.axPD is None:
            self.axPD = self.figure.add_subplot(111)

        self.toggleGridlines(self.gridCheck.isChecked(), **self.gridSettings)

        self.axPD.set_visible(True)

        label = f"{spectraData.name}-ToF" if spectraData.isToF else f"{spectraData.name}-Energy"
        if not spectraData.isMaxDrawn and not spectraData.isMinDrawn and not spectraData.isGraphUpdating:
            self.axPD.plot(
                spectraData.graphData[0],
                spectraData.graphData[1],
                "-",
                color=spectraData.graphColour,
                alpha=0.6,
                linewidth=0.8,
                label=label,
                gid=f"{spectraData.name}-PD"
            )
        self.toggleThreshold()
        self.drawAnnotations(spectraData)
        self.axPD.set_xscale("log")
        self.axPD.set_yscale("log")
        self.axPD.set(xlabel="Energy (eV)", ylabel="Cross section (b)", title=str(self.selectionName))

        if isMax:
            title = f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}"
            pdPoints = [
                a for a in self.axPD.get_lines() if "max" in a.get_gid() and title in a.get_gid()
            ]
            pdPointsXY = [(point.get_xdata()[0], point.get_ydata()[0])
                          for point in pdPoints]
            peaks = list(zip(peaksX, peaksY))
            removeIds = []
            for point in pdPoints:
                if "max-p" not in point.get_gid():
                    continue
                xy = (point.get_xdata()[0], point.get_ydata()[0])
                if xy not in peaks and title in point.get_gid():
                    removeIds.append(point.get_gid().split('-')[-1])
            if removeIds != []:
                for point in pdPoints:
                    if point.get_gid().split('-')[-1] in removeIds:
                        point.remove()

            for i, (x, y) in enumerate(zip(peaksX, peaksY)):
                if (x, y) in pdPointsXY:
                    continue
                self.axPD.plot(x,
                               y,
                               "x",
                               color="black",
                               markersize=3,
                               alpha=0.6,
                               gid=f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-max-p-{i}")
                spectraData.isMaxDrawn = True
                if spectraData.maxPeakLimitsX.get(x, False):
                    limitXFirst = spectraData.maxPeakLimitsX[x][0]
                    limitXSecond = spectraData.maxPeakLimitsX[x][1]
                else:
                    continue
                if spectraData.maxPeakLimitsY.get(x, False):
                    limitYFirst = spectraData.maxPeakLimitsY[x][0]
                    limitYSecond = spectraData.maxPeakLimitsY[x][1]
                else:
                    continue

                self.axPD.plot(limitXFirst,
                               limitYFirst,
                               marker=2,
                               color="r",
                               markersize=8,
                               gid=f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-max-limL-{i}")
                self.axPD.plot(limitXSecond,
                               limitYSecond,
                               marker=2,
                               color="r",
                               markersize=8,
                               gid=f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-max-limR-{i}")

        else:
            for x, y in zip(peaksX, peaksY):
                self.axPD.plot(x,
                               y,
                               "x",
                               color="black",
                               markersize=3,
                               alpha=0.6,
                               gid=f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-min")
                spectraData.isMinDrawn = True

        legendPD = self.axPD.legend(fancybox=True, shadow=True)
        self.legOrigLinesPD = {}
        origlines = [line for line in self.axPD.get_lines() if not ('max' in line.get_gid() or 'min' in line.get_gid())]
        for legLine, origLine in zip(legendPD.get_lines(), origlines):
            legLine.set_picker(True)
            legLine.set_linewidth(1.5)
            legLine.set_pickradius(7)
            legLine.set_color(self.spectraData[origLine.get_label()].graphColour)
            legLine.set_alpha(1.0 if origLine.get_visible() else 0.2)
            self.legOrigLinesPD[legLine] = origLine

        self.figure.tight_layout()
        self.toolbar.update()
        self.toolbar.push_current()
        spectraData.isGraphUpdating = False
        self.canvas.draw()


def main() -> None:

    app = QtWidgets.QApplication(sys.argv)
    app.setObjectName('MainWindow')

    # app.setStyle('Fusion')
    QtGui.QFontDatabase.addApplicationFont('src\\fonts\\RobotoMono-Thin.ttf')
    QtGui.QFontDatabase.addApplicationFont('src\\fonts\\RobotoMono-Regular.ttf')
    QtGui.QFontDatabase.addApplicationFont('src\\fonts\\RobotoMono-Medium.ttf')
    Colours = QtGui.QPalette()
    # Colours.setColor(QtGui.QPalette.Window, QtGui.QColor("#393939"))
    # Colours.setColor(QtGui.QPalette.Button, QtGui.QColor("#FFF"))

    app.setWindowIcon(QIcon("./src/img/final_logo.png"))

    _ = ExplorerGUI()
    app.setPalette(Colours)
    app.exec()


if __name__ == "__main__":
    main()
