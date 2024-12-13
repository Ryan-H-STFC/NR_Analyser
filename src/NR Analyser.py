from __future__ import annotations
import os
import sys
from time import perf_counter
from copy import deepcopy

import matplotlib.axes
import matplotlib.figure
import matplotlib.legend
import matplotlib.style
import matplotlib.rcsetup
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, LogFormatterSciNotation

matplotlib.use("QtAgg")
matplotlib.style.use("fast")
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import pandas as pd

from PyQt6 import QtGui, QtWidgets
from PyQt6.QtCore import Qt, QModelIndex, QRegularExpression as QRegExp, pyqtSignal
from PyQt6.QtGui import (
    QAction,
    QCursor,
    QRegularExpressionValidator as QRegExpValidator,
    QIcon,
)
from PyQt6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QCompleter,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QScrollBar,
    QSizePolicy,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)
from pyparsing import Literal
from scipy.interpolate import interp1d


from project.spectra.SpectraDataStructure import SpectraData

from project.myPyQt.ButtonDelegate import ButtonDelegate
from project.myPyQt.CustomSortingProxy import CustomSortingProxy
from project.myPyQt.ExtendedComboBox import ExtendedComboBox
from project.myPyQt.ExtendedTableModel import ExtendedQTableModel
from project.myPyQt.InputSpectraDialog import InputSpectraDialog
from project.myPyQt.PeakWindow import PeakWindow
from project.myPyQt.PeriodicTable import QtPeriodicTable

from project.myMatplotlib.BlittedCursor import BlittedCursor
from project.myMatplotlib.CustomFigureCanvas import FigureCanvas

from project.helpers.getRandomColor import getRandomColor
from project.helpers.getWidgets import getLayoutWidgets
from project.helpers.resourcePath import resource_path
from project.helpers.interpName import interpName
from project.settings import params


# todo ------------------------------------------- Issue / Feature TODO list -------------------------------------------

# todo - Matplotlib icons.

# todo - clearBtn confirmation Dialog

# todo - imports on non ideal data formats

# todo - Look into update checks for installer and Inno Setup Wizard

# todo - Optimsiations for Spectra Data init

# todo - Table sorting by column

# todo - Option to correct for flux distribution (Mulitply by roughly constant wave)

# todo - Option to change flux file

# todo - Change periodic table colors to fit

# todo - DOCUMENTATION

# ! todo - Create a reset controls function to properly enable or disable functions when errors occur

# * Energy Log scales

# * TOF linear scales


# ? Should this ask for the filepath or just be require to be in the format as seen in the repository,
# ? Download the repository and run the program without altering the file structure, will save having
# ? to enter filepaths in console during start up.


# Asking for filepath where the user has saved script
# filepath is where the data and the code has been saved. The sourceFilepath is the path to the latest data folder
# ! Maybe Change back to inputs if required
#  input('Enter the filepath where the latest NRCA code data folder is \n For Example:'
#                         'C://Users/ccj88542/NRCA/Rehana/Latest/main/data: \n')


class ExplorerGUI(QWidget):  # Acts just like QWidget class (like a template)
    """
    ``ExplorerGUI``
    --------------
    Class responsible for creating and manipulating the GUI, used in selecting and graphing the data of elements or
    isotopes within the NR Analyser.
    """

    resized = pyqtSignal()

    # init constructure for classes
    def __init__(self) -> None:
        """
        Initialisar for ExplorerGUI class
        """
        # Allows for adding more things to the QWidget template
        super(ExplorerGUI, self).__init__()
        self.defaultParams = params.copy()
        self.checkBoxChecked = resource_path(
            f"{params['dir_img']}checkbox-component-checked.svg"
        )
        self.checkBoxUnchecked = resource_path(
            f"{params['dir_img']}checkbox-component-unchecked.svg"
        )
        self.drag = resource_path(f"{params['dir_img']}drag-component.svg")
        self.radioUnchecked = resource_path(
            f"{params['dir_img']}radio-component-unchecked.svg"
        )
        self.radioChecked = resource_path(
            f"{params['dir_img']}radio-component-checked.svg"
        )
        self.expandDown = resource_path(f"{params['dir_img']}expand-down-component.svg")
        self.expandUp = resource_path(f"{params['dir_img']}expand-up-component.svg")
        self.bg_color = "#202020"
        self.text_color = "#FFF"

        # Setting glo bal variables
        self.selectionName: str = None
        self.numRows: int = None

        self.ax: matplotlib.axes.Axes = None
        self.axPD: matplotlib.axes.Axes = None

        self.plotCount: int = -1
        self.annotations: list[matplotlib.text.Annotations] = []
        self.localHiddenAnnotations: list[matplotlib.text.Annotations] = []
        self.plottedSpectra: list[tuple[str, bool]] = []
        self.spectraNames: list[str] = None

        self.orderByIntegral: bool = True
        self.spectraData: dict[str, SpectraData] = dict()
        self.elementDataNames: list[str] = []

        self.compoundData: dict[SpectraData] = dict()
        self.isCompound: bool = False

        self.gridSettings: dict[str] = params["grid_settings"]
        self.maxPeak: int = params["max_annotations"]
        self.length: dict[float] = params["length"]

        self.dir: str = params["dir_project"]
        self.graphDataDir: str = params["dir_graphData"]
        self.distributionDir: str = params["dir_distribution"]
        self.plotFilepath: str = None

        self.defaultDistributions: dict[dict[float]] = dict()
        self.elementDistributions: dict[dict[float]] = dict()

        self.thresholds: dict[tuple[float, float]] = params["threshold_exceptions"]

        # Initialise spectra natural abundance / distributions dict
        dist_filePaths: list[str] = [
            f for f in os.listdir(self.distributionDir) if f.endswith(".csv")
        ]
        for filepath in dist_filePaths:
            name = filepath[:-4]
            dist = pd.read_csv(
                resource_path(f"{self.distributionDir}{filepath}"), header=None
            )
            self.defaultDistributions[name] = dict({d[0]: d[1] for d in dist.values})

        self.elementDistributions = deepcopy(self.defaultDistributions)

        self.setStyleSheet(self.setStyleTo("dark"))
        self.initUI()

    def initUI(self) -> None:
        """
        ``initUI``
        ----------
        Creates the UI.
        """
        self.setObjectName("mainWindow")
        self.setGeometry(
            50,
            50,
            12 * self.screen().availableGeometry().width() // 18,
            self.screen().availableGeometry().height() // 2,
        )
        self.setWindowTitle("NR Analyser")
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

        newAction = QAction(
            QIcon(resource_path(f"{params['dir_img']}add-component.svg")), "&New", self
        )
        newAction.setShortcut("Ctrl+N")
        newAction.triggered.connect(self.clear)

        importAction = QAction(
            QIcon(resource_path(f"{params['dir_img']}upload-component.svg")),
            "&Import Data",
            self,
        )
        importAction.setShortcut("Ctrl+I")
        importAction.triggered.connect(lambda: self.importData(None))

        exportAction = QAction(
            QIcon(resource_path(f"{params['dir_img']}export-component.svg")),
            "&Export Data",
            self,
        )
        exportAction.setShortcut("Ctrl+S")
        exportAction.triggered.connect(self.exportData)

        fileMenu = menubar.addMenu("&File")
        fileMenu.addAction(newAction)
        fileMenu.addAction(importAction)
        fileMenu.addAction(exportAction)

        # * ----------------------------------------------

        # ¦ --------------- MENU BAR - EDIT --------------
        # Creates menu bar and add actions
        editpeakAction = QAction(
            QIcon(resource_path(f"{params['dir_img']}edit-component.svg")),
            "&Edit Peak Limits",
            self,
        )
        editpeakAction.setShortcut("Ctrl+E")
        editpeakAction.triggered.connect(self.editPeakLimits)

        editThresholdAction = QAction(
            QIcon(resource_path(f"{params['dir_img']}edit-component.svg")),
            "&Edit Threshold",
            self,
        )
        editThresholdAction.setShortcut("Ctrl+Shift+T")
        editThresholdAction.triggered.connect(self.editThresholdLimit)

        editDistribution = QAction(
            QIcon(resource_path(f"{params['dir_img']}edit-component.svg")),
            "&Edit Distribution",
            self,
        )
        editDistribution.setShortcut("Ctrl+Shift+D")
        editDistribution.triggered.connect(self.editDistribution)

        editLength = QAction(
            QIcon(resource_path(f"{params['dir_img']}edit-component.svg")),
            "&Edit Length",
            self,
        )
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
        self.peaklabel.setObjectName("numPeakLabel")
        self.peaklabel.setText("")
        self.peaklabel.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.peaklabel.setContentsMargins(0, 10, 0, 0)
        menubarLayout.addWidget(self.peaklabel, alignment=Qt.AlignmentFlag.AlignVCenter)
        # Threshold Label
        self.thresholdLabel = QLabel()
        self.thresholdLabel.setObjectName("thresholdLabel")
        self.thresholdLabel.setText("Nothing has been selected")
        self.thresholdLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.thresholdLabel.setContentsMargins(0, 10, 0, 0)

        menubarLayout.addWidget(
            self.thresholdLabel, alignment=Qt.AlignmentFlag.AlignRight
        )

        # * ----------------------------------------------

        # ¦ --------------- MENU BAR - VIEW --------------

        viewMenu = menubar.addMenu("&View")
        appearenceMenu = viewMenu.addMenu("Appearence")

        defaultAppearence = QAction(
            QIcon(resource_path(f"{params['dir_img']}changeAppearence-component.svg")),
            "&Dark Theme",
            self,
        )
        defaultAppearence.setShortcut("Ctrl+Shift+1")
        defaultAppearence.triggered.connect(self.viewDarkStyle)

        windowsAppearence = QAction(
            QIcon(resource_path(f"{params['dir_img']}changeAppearence-component.svg")),
            "&Light Theme",
            self,
        )
        windowsAppearence.setShortcut("Ctrl+Shift+2")
        windowsAppearence.triggered.connect(self.viewLightStyle)

        highContrastAppearence = QAction(
            QIcon(resource_path(f"{params['dir_img']}changeAppearence-component.svg")),
            "&High Contrast",
            self,
        )
        highContrastAppearence.setShortcut("Ctrl+Shift+3")
        highContrastAppearence.triggered.connect(self.viewHighContrastStyle)

        appearenceMenu.addAction(defaultAppearence)
        appearenceMenu.addAction(windowsAppearence)
        appearenceMenu.addAction(highContrastAppearence)

        # * ----------------------------------------------

        # ¦ ------------- MENU BAR - OPTIONS -------------

        optionsMenu = menubar.addMenu("&Options")

        gridlineOptions = QAction(
            QIcon(resource_path(f"{params['dir_img']}grid-component.svg")),
            "&Grid Line Settings",
            self,
        )
        gridlineOptions.setShortcut("Ctrl+Shift+G")
        gridlineOptions.triggered.connect(self.gridLineOptions)

        maxPeaksOption = QAction(
            QIcon(resource_path(f"{params['dir_img']}edit-component.svg")),
            "&Max Peak Quantity",
            self,
        )
        maxPeaksOption.setShortcut("Ctrl+Shift+Q")
        maxPeaksOption.triggered.connect(self.editMaxPeaks)

        settingsMenu = QAction(
            QIcon(f"{params['dir_img']}settings.svg"), "&Settings", self
        )
        settingsMenu.triggered.connect(self.settingsMenu)

        optionsMenu.addAction(gridlineOptions)
        optionsMenu.addAction(maxPeaksOption)
        optionsMenu.addAction(settingsMenu)

        # * ----------------------------------------------

        # ¦ --------------- Combobox Group ---------------

        # For copying data directory to local directory for plotting later
        # Establishing source and destination directories

        # Creating a list of substances stored in the NRCA database data directory
        self.spectraNames = [None]
        for file in os.listdir(resource_path(f"{self.graphDataDir}")):
            filename = os.fsdecode(file)
            if ".csv" not in filename[-4:]:
                continue
            filename = filename[:-4]
            self.spectraNames.append(filename)

        # Creating combo box (drop down menu)
        self.combobox = ExtendedComboBox(self)
        self.combobox.view().setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.combobox.setObjectName("combobox")

        self.combobox.addItems(self.spectraNames)
        self.combobox.lineEdit().setPlaceholderText("Select an Isotope / Element")

        sidebarLayout.addWidget(self.combobox)
        periodicTableBtn = QPushButton("Periodic Table", self)
        periodicTableBtn.setIcon(QIcon(f"{params['dir_img']}periodic-table.svg"))

        periodicTableBtn.clicked.connect(self.openPeriodicTable)
        sidebarLayout.addWidget(periodicTableBtn)

        # Upon selecting an option, it records the option
        # and connects to the method 'plotSelectionProxy'
        self.combobox.editTextChanged.connect(
            lambda: self.plotSelectionProxy(
                index=self.combobox.currentIndex(),
                comboboxName=self.combobox.objectName(),
            )
        )

        # * ----------------------------------------------

        pointingCursor = QCursor(Qt.CursorShape.PointingHandCursor)

        # ¦ ---------------- Button Group ----------------

        self.btnLayout = QVBoxLayout()

        self.btnTopLayout = QVBoxLayout()
        self.btnTopLayout.setSpacing(10)
        self.plotEnergyBtn = QPushButton("Plot in Energy", self)
        self.plotEnergyBtn.setObjectName("plotEnergyBtn")
        self.plotEnergyBtn.setCursor(pointingCursor)
        self.plotEnergyBtn.__name__ = "plotEnergyBtn"
        self.plotEnergyBtn.resize(self.plotEnergyBtn.sizeHint())
        self.plotEnergyBtn.setEnabled(False)
        self.btnTopLayout.addWidget(self.plotEnergyBtn)
        self.plotEnergyBtn.clicked.connect(self.updateGuiData)

        self.plotTOFBtn = QPushButton("Plot in ToF", self)
        self.plotTOFBtn.setCursor(pointingCursor)
        self.plotTOFBtn.setObjectName("plotTOFBtn")
        self.plotTOFBtn.__name__ = "plotToFBtn"
        self.plotTOFBtn.resize(self.plotTOFBtn.sizeHint())
        self.plotTOFBtn.setEnabled(False)
        self.btnTopLayout.addWidget(self.plotTOFBtn)
        self.plotTOFBtn.clicked.connect(lambda: self.updateGuiData(tof=True))

        self.pdBtn = QPushButton("Peak Detection", self)
        self.pdBtn.setObjectName("pdBtn")
        self.pdBtn.setCursor(pointingCursor)
        self.pdBtn.__name__ = "pdBtn"
        self.pdBtn.resize(self.pdBtn.sizeHint())
        self.pdBtn.setEnabled(False)
        self.pdBtn.clicked.connect(self.getPeaks)

        self.clearBtn = QPushButton("Clear All", self)
        self.clearBtn.setObjectName("clearBtn")
        self.clearBtn.setCursor(pointingCursor)
        self.clearBtn.__name__ = "clearBtn"
        self.clearBtn.resize(self.clearBtn.sizeHint())
        self.clearBtn.setEnabled(False)
        self.clearBtn.clicked.connect(self.clear)

        self.btnLayout.addItem(self.btnTopLayout)
        self.btnLayout.addSpacing(15)
        self.btnLayout.addWidget(self.pdBtn)
        self.btnLayout.addSpacing(15)
        self.btnLayout.addWidget(self.clearBtn)

        sidebarLayout.addLayout(self.btnLayout)

        # * ----------------------------------------------

        # ¦ --------------- Checkbox Group ---------------

        self.toggleLayout = QVBoxLayout()
        self.toggleLayout.setObjectName("toggleLayout")

        self.gridCheck = QCheckBox("Grid Lines", self)
        self.gridCheck.setCursor(pointingCursor)
        self.gridCheck.setObjectName("grid_check")
        self.gridCheck.__name__ = "gridCheck"

        self.gridCheck.setEnabled(False)
        self.toggleLayout.addWidget(self.gridCheck)
        self.gridCheck.stateChanged.connect(
            lambda: self.toggleGridlines(
                self.gridCheck.isChecked(), **self.gridSettings
            )
        )

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
        peakOrderLabel.setObjectName("orderlabel")

        peakOrderButtonGroup = QButtonGroup(self)
        peakOrderButtonGroup.setObjectName("peakOrderButtonGroup")
        self.byIntegralCheck = QRadioButton("By Integral")
        self.byIntegralCheck.setObjectName("orderByIntegral")
        self.byIntegralCheck.setChecked(True)
        self.byIntegralCheck.clicked.connect(self.onPeakOrderChange)
        self.byPeakWidthCheck = QRadioButton("By Peak Width")
        self.byPeakWidthCheck.setObjectName("orderByPeakW")
        self.byPeakWidthCheck.clicked.connect(self.onPeakOrderChange)

        peakOrderButtonGroup.addButton(self.byIntegralCheck)
        peakOrderButtonGroup.addButton(self.byPeakWidthCheck)

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
        compoundCreaterBtn.setCursor(pointingCursor)
        compoundCreaterBtn.clicked.connect(self.createCompound)
        self.compoundCombobox = ExtendedComboBox()
        self.compoundCombobox.lineEdit().setPlaceholderText("Select a Compound")
        self.compoundCombobox.setObjectName("compoundComboBox")
        self.compoundCombobox.editTextChanged.connect(
            lambda: self.plotSelectionProxy(
                index=self.compoundCombobox.currentIndex(),
                comboboxName=self.compoundCombobox.objectName(),
            )
        )
        self.compoundCombobox.setMaximumWidth(250)
        self.compoundNames = [None]
        for file in os.listdir(resource_path(params["dir_compoundGraphData"])):
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

        # ¦ ----------- Peak Table Option Group -----------

        peakTableOptionLayout = QVBoxLayout()
        peakTableOptionLayout.setSpacing(5)
        peakTableOptionRadioLayout = QHBoxLayout()
        peakTableOptionLayout.setSpacing(5)

        peakTableOptionButtonGroup = QButtonGroup(self)
        peakTableOptionButtonGroup.setObjectName("peakTableOptionButtonGroup")

        peakTableOptionLabel = QLabel("Display Data")
        peakTableOptionLabel.setObjectName("tableTypeLabel")
        self.maxTableOptionRadio = QRadioButton("Maxima")
        self.maxTableOptionRadio.setChecked(True)
        self.maxTableOptionRadio.clicked.connect(self.onPeakTableOptionChange)
        self.minTableOptionRadio = QRadioButton("Minima")
        self.minTableOptionRadio.clicked.connect(self.onPeakTableOptionChange)

        peakTableOptionButtonGroup.addButton(self.maxTableOptionRadio)
        peakTableOptionButtonGroup.addButton(self.minTableOptionRadio)

        peakTableOptionRadioLayout.addWidget(self.maxTableOptionRadio)
        peakTableOptionRadioLayout.addWidget(self.minTableOptionRadio)
        peakTableOptionLayout.addWidget(peakTableOptionLabel)
        peakTableOptionLayout.addLayout(peakTableOptionRadioLayout)

        sidebarLayout.addLayout(peakTableOptionLayout)
        # * -----------------------------------------------

        # ¦ ----------------- Plot Canvas -----------------
        self.figure = plt.figure()  # Creating canvas to plot graph on and toolbar
        self.canvas = FigureCanvas(self.figure, self, contextConnect=True)

        self.canvas.__name__ = "canvas"
        self.canvas.mpl_connect("pick_event", self.hideGraph)
        self.toolbar = NavigationToolbar(self.canvas, parent=self, coordinates=True)

        canvasLayout.addWidget(self.toolbar)
        canvasLayout.addWidget(self.canvas)

        # * -----------------------------------------------

        # ¦ -------------------- Table --------------------

        self.table = QTableView()
        self.table.setObjectName("dataTable")
        self.table.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(200)

        # * -----------------------------------------------

        container = QWidget(self)
        container.setObjectName("mainContainer")
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
        self.setAcceptDrops(True)

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

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent) -> None:
        """
        ``dragEnterEvent``
        ------------------
        Handles file drag enter event and verification

        Args:
            ``event`` (QDragEnterEvent): Event triggered on mouse dragging into the window.
        """
        try:
            if event.mimeData().hasUrls():
                for file in event.mimeData().urls():
                    filepath = file.toLocalFile()
                    if any(
                        [ext for ext in [".csv", ".txt", ".dat"] if ext in filepath]
                    ):
                        event.acceptProposedAction()
                    else:
                        event.ignore()
            else:
                event.ignore()
        except AttributeError:
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
            self.importData(filepath)

    def adjustCanvas(self) -> None:
        """
        ``adjustCanvas``
        ----------------
        Apply tight layout to figure.
        """
        self.figure.tight_layout()

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

        optionsWindow = InputSpectraDialog(self, self.styleSheet())

        optionsWindow.spectras.addItems(self.spectraData.keys())
        optionsWindow.spectras.setMaxVisibleItems(5)

        spectraPeaks = ExtendedComboBox()
        spectraPeaks.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        peakOptionLayout = QHBoxLayout()
        maxOptionRadio = QRadioButton()
        maxOptionRadio.setText("Maxima")
        minOptionRadio = QRadioButton()
        minOptionRadio.setText("Minima")
        peakOptionLayout.addWidget(maxOptionRadio)
        peakOptionLayout.addWidget(minOptionRadio)
        maxOptionRadio.setChecked(True)

        firstLimitLayout = QHBoxLayout()
        firstLimitX = QLineEdit()

        firstLimitX.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))
        firstLimitBtn = QPushButton()
        firstLimitBtn.setObjectName("first")
        firstLimitBtn.setIcon(
            QIcon(resource_path(f"{params['dir_img']}add-component.svg"))
        )
        firstLimitLayout.addWidget(firstLimitX)
        firstLimitLayout.addWidget(firstLimitBtn)

        secondLimitLayout = QHBoxLayout()
        secondLimitX = QLineEdit()
        secondLimitX.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))
        secondLimitBtn = QPushButton()
        secondLimitBtn.setObjectName("second")
        secondLimitBtn.setIcon(
            QIcon(resource_path(f"{params['dir_img']}add-component.svg"))
        )
        secondLimitLayout.addWidget(secondLimitX)
        secondLimitLayout.addWidget(secondLimitBtn)

        optionsWindow.inputForm.addItem(peakOptionLayout)
        optionsWindow.inputForm.addRow(QLabel("Peak X-Coord:"), spectraPeaks)
        optionsWindow.inputForm.addRow(QLabel("1st Limit X:"), firstLimitLayout)
        optionsWindow.inputForm.addRow(QLabel("2nd Limit X:"), secondLimitLayout)

        applyBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Ok)
        applyBtn.setText("Apply")
        cancelBtn = optionsWindow.buttonBox.addButton(
            QDialogButtonBox.StandardButton.Cancel
        )

        optionsWindow.inputForm.setSpacing(5)
        optionsWindow.mainLayout.insertItem(1, optionsWindow.inputForm)

        optionsWindow.setWindowTitle("Edit Peaks for Substance")
        optionsWindow.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        optionsWindow.setLayout(optionsWindow.mainLayout)

        ax: matplotlib.axes.Axes = self.axPD if self.axPD is not None else self.ax

        spectras = optionsWindow.spectras

        def drawPeakData(
            peak: tuple[float] = None,
            removeAll: bool = False,
        ):
            spectraName: str = spectras.itemText(spectras.currentIndex() or 0)
            spectra: SpectraData = self.spectraData[spectraName]
            which = "max" if maxOptionRadio.isChecked() else "min"
            peakList = spectra.maxima if which == "max" else spectra.minima
            whichLim = (
                "both"
                if firstLimitX.text() and secondLimitX.text()
                else "left"
                if firstLimitX.text()
                else "right"
                if secondLimitX.text()
                else None
            )
            ax: matplotlib.axes.Axes = self.axPD if self.axPD is not None else self.ax
            for line in [line for line in ax.lines if "peakEdit" in line.get_gid()]:
                if removeAll:
                    line.remove()

                elif str(peak[0]) in line.get_gid():
                    line.remove()

            if removeAll:
                self.figure.canvas.draw()
                return
            if not spectra.whichAnnotationsDrawn == which:
                self.drawAnnotations(spectra, which)
            xLims, yLims = (
                (spectra.maxPeakLimitsX, spectra.maxPeakLimitsY)
                if maxOptionRadio.isChecked()
                else (spectra.minPeakLimitsX, spectra.minPeakLimitsY)
            )
            leftLim, rightLim = list(zip(xLims[peak[0]], yLims[peak[0]]))
            index = np.where(peakList[:, 0] == peak[0])[0][0]
            if whichLim is not None:
                for line in [
                    line
                    for line in ax.lines
                    if f"{which}-limL-{index}" in line.get_gid() or f"{which}-limR-{index}" in line.get_gid()
                ]:
                    if whichLim in ["left", "both"] and "limL" in line.get_gid():
                        line.set_data([leftLim[0]], [leftLim[1]])

                    elif whichLim in ["right", "both"] and "limR" in line.get_gid():
                        line.set_data([rightLim[0]], [rightLim[1]])

            ax.plot(
                peak[0],
                peak[1],
                "x",
                color="black",
                markersize=3,
                alpha=0.6,
                gid=f"peakEdit-{peak[0]}-peak",
            )
            ax.axline(
                leftLim,
                rightLim,
                linestyle="--",
                color="r",
                linewidth=1.0,
                gid=f"peakEdit-{peak[0]}-midLine",
            )

            ax.axvline(
                x=leftLim[0],
                linestyle="--",
                color="r",
                linewidth=1.0,
                gid=f"peakEdit-{peak[0]}-leftLine",
            )
            ax.axvline(
                x=rightLim[0],
                linestyle="--",
                color="r",
                linewidth=1.0,
                gid=f"peakEdit-{peak[0]}-rightLim",
            )
            self.toolbar.push_current()

            ax.set_xlim(
                left=(lambda x: x if x > 0 else 0.001)(
                    leftLim[0] - 0.1 * (rightLim[0] - leftLim[0])
                ),
                right=rightLim[0] + 0.05 * (rightLim[0] - leftLim[0]),
            )
            ax.set_ylim(
                bottom=(
                    min(leftLim[1], rightLim[1]) if maxOptionRadio.isChecked() else peak[1]
                ) * 0.8,
                top=(
                    peak[1]
                    if maxOptionRadio.isChecked()
                    else max(leftLim[1], rightLim[1])
                ) * 1.2,
            )
            self.figure.canvas.draw()

        def onAccept():
            drawPeakData(removeAll=True)
            spectraName: str = spectras.itemText(spectras.currentIndex() or 0)
            spectra: SpectraData = self.spectraData[spectraName]
            which: str = "max" if maxOptionRadio.isChecked() else "min"
            peakList = spectra.maxima if maxOptionRadio.isChecked() else spectra.minima
            peakX: float = float(spectraPeaks.currentText())
            peakY = peakList[:, 1][np.where(peakList[:, 0] == peakX)[0][0]]
            leftLimitX = float(
                firstLimitX.placeholderText()
                if firstLimitX.text() == ""
                else firstLimitX.text()
            )

            rightLimitX = float(
                secondLimitX.placeholderText()
                if secondLimitX.text() == ""
                else secondLimitX.text()
            )

            interpGraphData = interp1d(spectra.graphData[0], spectra.graphData[1])
            leftLimitY = float(interpGraphData(leftLimitX))
            rightLimitY = float(interpGraphData(rightLimitX))

            if which == "max":
                spectra.maxPeakLimitsX[peakX] = (leftLimitX, rightLimitX)
                spectra.maxPeakLimitsY[peakX] = (leftLimitY, rightLimitY)

            else:
                spectra.minPeakLimitsX[peakX] = (leftLimitX, rightLimitX)
                spectra.minPeakLimitsY[peakX] = (leftLimitY, rightLimitY)

            drawPeakData((peakX, peakY))

            self.figure.canvas.mpl_disconnect(optionsWindow.motionEvent)
            self.figure.canvas.mpl_disconnect(optionsWindow.buttonPressEvent)
            spectra.recalculatePeakData(peakX, which=which)
            spectra.orderAnnotations(
                which=which, byIntegral=self.byIntegralCheck.isChecked()
            )
            self.addTableData(reset=True)

        applyBtn.clicked.connect(onAccept)

        def onClose():
            drawPeakData(removeAll=True)
            self.figure.canvas.mpl_disconnect(optionsWindow.motionEvent)
            self.figure.canvas.mpl_disconnect(optionsWindow.buttonPressEvent)
            optionsWindow.close()

        optionsWindow.finished.connect(onClose)
        cancelBtn.clicked.connect(onClose)

        def onPeakOptionChange():
            spectras.blockSignals(True)
            spectraPeaks.blockSignals(True)
            maxOptionRadio.blockSignals(True)
            minOptionRadio.blockSignals(True)
            spectra: SpectraData = self.spectraData.get(spectras.currentText(), False)

            if not spectra:
                spectras.lineEdit().setText(None)
                spectras.setCurrentIndex(0)
                return
            if (
                maxOptionRadio.isChecked() and (spectra.maxima.shape[0] == 0 or spectra.maxPeakLimitsX == {})
            ) or (
                minOptionRadio.isChecked() and (spectra.minima.shape[0] == 0 or spectra.minPeakLimitsX == {})
            ):
                spectraPeaks.setEnabled(False)
                firstLimitX.setEnabled(False)
                secondLimitX.setEnabled(False)
                applyBtn.setEnabled(False)
                applyBtn.setToolTip("No peaks detected.")
                firstLimitBtn.setEnabled(False)
                secondLimitBtn.setEnabled(False)
                spectraPeaks.setCurrentText("Null")
                firstLimitX.setPlaceholderText("Null")
                secondLimitX.setPlaceholderText("Null")
                spectraPeaks.blockSignals(False)
                maxOptionRadio.blockSignals(False)
                minOptionRadio.blockSignals(False)
                return

            spectraPeaks.setEnabled(True)
            firstLimitX.setEnabled(True)
            secondLimitX.setEnabled(True)
            firstLimitX.setText(None)
            secondLimitX.setText(None)
            firstLimitBtn.setEnabled(True)
            secondLimitBtn.setEnabled(True)
            applyBtn.setEnabled(True)
            applyBtn.setToolTip(None)

            peakList = spectra.maxima if maxOptionRadio.isChecked() else spectra.minima
            peakLimits = (
                (spectra.maxPeakLimitsX, spectra.maxPeakLimitsY)
                if maxOptionRadio.isChecked()
                else (spectra.minPeakLimitsX, spectra.minPeakLimitsY)
            )
            spectraPeaks.clear()

            spectraPeaks.addItems(
                [str(peak) for peak in peakList[:, 0] if peakLimits[0].get(peak, False)]
            )
            peakX = float(spectraPeaks.currentText())
            peakY = peakList[:, 1][np.where(peakList[:, 0] == peakX)[0][0]]
            peakIndex = spectra.graphData[spectra.graphData[0] == peakX].index[0]

            zerosList = (
                spectra.peakDetector.dips
                if maxOptionRadio.isChecked()
                else spectra.peakDetector.peaks
            )
            validFlats = zerosList[np.where(zerosList < peakX)]

            left = 0 if validFlats.size == 0 else max(validFlats)

            validFlats = zerosList[np.where(zerosList > peakX)]
            right = max(zerosList) if validFlats.size == 0 else min(validFlats)

            firstLimitX.setPlaceholderText(str(left))
            secondLimitX.setPlaceholderText(str(right))

            drawPeakData(removeAll=True)
            drawPeakData((peakX, peakY))

            spectras.blockSignals(False)
            spectraPeaks.blockSignals(False)
            maxOptionRadio.blockSignals(False)
            minOptionRadio.blockSignals(False)

        maxOptionRadio.clicked.connect(onPeakOptionChange)
        minOptionRadio.clicked.connect(onPeakOptionChange)

        def onElementChange(index):
            spectras.blockSignals(True)
            spectraPeaks.blockSignals(True)
            maxOptionRadio.blockSignals(True)
            minOptionRadio.blockSignals(True)
            firstLimitX.setText(None)
            secondLimitX.setText(None)
            spectra = self.spectraData.get(spectras.currentText(), False)

            spectraPeaks.clear()
            if not spectra:
                spectras.lineEdit().setText(None)
                spectras.setCurrentIndex(0)
                return

            if (
                maxOptionRadio.isChecked() and (spectra.maxima.shape[0] == 0 or spectra.maxPeakLimitsX == {})
            ) or (
                minOptionRadio.isChecked() and (spectra.minima.shape[0] == 0 or spectra.minPeakLimitsX == {})
            ):
                spectraPeaks.setEnabled(False)
                firstLimitX.setEnabled(False)
                secondLimitX.setEnabled(False)
                applyBtn.setEnabled(False)
                applyBtn.setToolTip("No peaks detected.")
                firstLimitBtn.setEnabled(False)
                secondLimitBtn.setEnabled(False)
                spectraPeaks.setCurrentText("Null")
                firstLimitX.setPlaceholderText("Null")
                secondLimitX.setPlaceholderText("Null")
                spectraPeaks.blockSignals(False)
                maxOptionRadio.blockSignals(False)
                minOptionRadio.blockSignals(False)
                return

            spectraPeaks.setEnabled(True)
            firstLimitX.setEnabled(True)
            secondLimitX.setEnabled(True)
            firstLimitBtn.setEnabled(True)
            secondLimitBtn.setEnabled(True)
            applyBtn.setEnabled(True)
            applyBtn.setToolTip(None)

            spectraPeaks.clear()
            if maxOptionRadio.isChecked():
                spectraPeaks.addItems(
                    [
                        str(peak)
                        for peak in spectra.maxima[:, 0]
                        if spectra.maxPeakLimitsX.get(peak, False)
                    ]
                )
            else:
                spectraPeaks.addItems(
                    [
                        str(peak)
                        for peak in spectra.minima[:, 0]
                        if spectra.minPeakLimitsX.get(peak, False)
                    ]
                )

            spectras.blockSignals(False)
            spectraPeaks.blockSignals(False)
            maxOptionRadio.blockSignals(False)
            minOptionRadio.blockSignals(False)

            onPeakChange(spectras.currentIndex())

        spectras.currentIndexChanged.connect(
            lambda: onElementChange(index=spectras.currentIndex())
        )

        def onPeakChange(index):
            spectras.blockSignals(True)
            spectraPeaks.blockSignals(True)
            maxOptionRadio.blockSignals(True)
            minOptionRadio.blockSignals(True)

            spectra = self.spectraData.get(spectras.currentText(), False)
            if not spectra or spectraPeaks.currentText() == "":
                spectras.lineEdit().setText(None)
                spectras.setCurrentIndex(0)
                spectraPeaks.setCurrentIndex(0)
                return

            firstLimitX.setText(None)
            secondLimitX.setText(None)
            if (
                maxOptionRadio.isChecked() and (spectra.maxima.shape[0] == 0 or spectra.maxPeakLimitsX == {})
            ) or (
                minOptionRadio.isChecked() and (spectra.minima.shape[0] == 0 or spectra.minPeakLimitsX == {})
            ):
                spectras.setCurrentIndex(0)
                spectraPeaks.setCurrentText("Null")
                firstLimitX.setPlaceholderText("Null")
                secondLimitX.setPlaceholderText("Null")
                applyBtn.setEnabled(False)
                applyBtn.setToolTip("No peaks detected.")
                return

            spectraPeaks.setEnabled(True)
            firstLimitX.setEnabled(True)
            secondLimitX.setEnabled(True)
            firstLimitBtn.setEnabled(True)
            secondLimitBtn.setEnabled(True)
            applyBtn.setEnabled(True)
            applyBtn.setToolTip(None)

            peakX = float(spectraPeaks.currentText())
            peakList = spectra.maxima if maxOptionRadio.isChecked() else spectra.minima

            if maxOptionRadio.isChecked():
                firstLimitX.setPlaceholderText(str(spectra.maxPeakLimitsX[peakX][0]))
                secondLimitX.setPlaceholderText(str(spectra.maxPeakLimitsX[peakX][1]))

            else:
                firstLimitX.setPlaceholderText(str(spectra.minPeakLimitsX[peakX][0]))
                secondLimitX.setPlaceholderText(str(spectra.minPeakLimitsX[peakX][1]))

            try:
                optionsWindow.blittedCursor.on_remove()
                del optionsWindow.blitterCursor

            except AttributeError:
                pass

            peakY = peakList[:, 1][np.where(peakList[:, 0] == peakX)[0][0]]
            peakIndex = spectra.graphData[spectra.graphData[0] == peakX].index[0]

            zerosList = (
                spectra.peakDetector.dips
                if maxOptionRadio.isChecked()
                else spectra.peakDetector.peaks
            )
            validFlats = zerosList[np.where(zerosList < peakIndex)]

            left = (
                spectra.graphData.iloc[(np.where(np.max(validFlats)))]
                if validFlats.size != 0
                else spectra.graphData.iloc[0]
            ).to_numpy()
            left = (float(left[:, 0]), float(left[:, 1]))

            validFlats = zerosList[np.where(zerosList > peakIndex)]
            right = (
                spectra.graphData.iloc[(np.where(np.min(validFlats)))]
                if validFlats.size != 0
                else spectra.graphData.iloc[-1]
            ).to_numpy()
            right = (float(right[:, 0]), float(right[:, 1]))

            drawPeakData(removeAll=True)
            drawPeakData((peakX, peakY))

            spectras.blockSignals(False)
            spectraPeaks.blockSignals(False)
            maxOptionRadio.blockSignals(False)
            minOptionRadio.blockSignals(False)

        spectraPeaks.currentIndexChanged.connect(
            lambda: onPeakChange(spectras.currentIndex())
        )

        def onLimitChange(which: Literal["left", "right"]):
            spectra: SpectraData = self.spectraData.get(spectras.currentText(), False)
            leftlimit: str = (
                firstLimitX.placeholderText()
                if firstLimitX.text() == ""
                else firstLimitX.text()
            )
            rightLimit: str = (
                secondLimitX.placeholderText()
                if secondLimitX.text() == ""
                else secondLimitX.text()
            )
            peakX: float = float(spectraPeaks.currentText())
            if leftlimit == "Null" or rightLimit == "Null":
                applyBtn.setEnabled(False)
                applyBtn.setToolTip("Limits cannot be Null.")
                return
            if float(leftlimit) > peakX or float(rightLimit) < peakX:
                applyBtn.setEnabled(False)
                applyBtn.setToolTip("Invalid integral region.")
                return
            if (
                float(leftlimit) < spectra.graphData[0].min() or float(rightLimit) > spectra.graphData[0].max()
            ):
                applyBtn.setEnabled(False)
                applyBtn.setToolTip("Limits exceed maximum or minimum of spectra.")
                return
            try:
                optionsWindow.blittedCursor.on_remove()
                del optionsWindow.blittedCursor

            except AttributeError:
                pass
            for line in ax.get_lines() + ax.texts:
                if "cursor" in line.get_gid():
                    line.remove()
            applyBtn.setEnabled(True)
            applyBtn.setToolTip(None)

        firstLimitX.textChanged.connect(lambda: onLimitChange(which="left"))
        secondLimitX.textChanged.connect(lambda: onLimitChange(which="right"))

        def onLimitSelect(event):
            if not optionsWindow.blittedCursor.valid:
                return
            else:
                if optionsWindow.which == "first":
                    firstLimitX.setText(f"{round(optionsWindow.blittedCursor.x, 3)}")
                if optionsWindow.which == "second":
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
            optionsWindow.blittedCursor = BlittedCursor(
                ax=ax, axisType="both", which=optionsWindow.which
            )

            self.figure.canvas.mpl_disconnect(optionsWindow.motionEvent)
            self.figure.canvas.mpl_disconnect(optionsWindow.buttonPressEvent)
            optionsWindow.motionEvent = self.figure.canvas.mpl_connect(
                "motion_notify_event",
                lambda event: optionsWindow.blittedCursor.on_mouse_move(
                    event, float(spectraPeaks.currentText())
                ),
            )
            optionsWindow.buttonPressEvent = self.figure.canvas.mpl_connect(
                "button_press_event", onLimitSelect
            )

        firstLimitBtn.pressed.connect(lambda: connectLimitSelect(firstLimitBtn))
        secondLimitBtn.pressed.connect(lambda: connectLimitSelect(secondLimitBtn))

        onElementChange(spectras.currentIndex())
        optionsWindow.setModal(False)
        optionsWindow.show()

    def editDistribution(self) -> None:
        """
        ``editDistribution``
        --------------------
        Opens a dialog window with options to alter the natural abundance of elements and compounds
        updating the graph data of any relevant plots.
        """

        optionsWindow = InputSpectraDialog(self, self.styleSheet())
        optionsWindow.spectras.addItems(
            [el for el in self.combobox.getAllItemText() if "element" in el]
        )
        optionsWindow.spectras.addItems(self.compoundCombobox.getAllItemText())

        totalLabel = QLabel()

        applyBtn = optionsWindow.buttonBox.addButton(
            QDialogButtonBox.StandardButton.Apply
        )
        applyBtn.setEnabled(False)
        applyBtn.setText("Apply")
        resetBtn = optionsWindow.buttonBox.addButton(
            QDialogButtonBox.StandardButton.Reset
        )
        cancelBtn = optionsWindow.buttonBox.addButton(
            QDialogButtonBox.StandardButton.Cancel
        )

        optionsWindow.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        optionsWindow.setWindowTitle("Edit Distribution")
        optionsWindow.setLayout(optionsWindow.mainLayout)

        optionsWindow.mainLayout.insertWidget(
            len(optionsWindow.children()) - 2, totalLabel
        )

        spectras = optionsWindow.spectras

        def onAccept():
            spectraName = spectras.itemText(spectras.currentIndex() or 0)
            if spectraName == "":
                return
            for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget):
                title = widget.findChild(QLabel).text()[:-1]
                if widget.findChild(QLineEdit).text() == "":
                    dist = float(widget.findChild(QLineEdit).placeholderText())
                else:
                    dist = float(widget.findChild(QLineEdit).text())

                self.elementDistributions[spectraName][title] = dist

            for title, Tof in self.plottedSpectra:
                if spectraName == title:
                    title = f"{title}-{'ToF' if Tof else 'Energy'}"
                    spectra: SpectraData = self.spectraData[title]
                    spectra.distributions = self.elementDistributions[spectraName]

                    spectra.distChanging = True
                    spectra.isUpdating = True
                    spectra.isGraphDrawn = False
                    self.isCompound = spectra.isCompound
                    self.selectionName = spectraName

                    self.updateGuiData(tof=Tof, distAltered=True)
                    self.addTableData(reset=True)
                    self.updateLabels(title)

        applyBtn.clicked.connect(onAccept)
        cancelBtn.clicked.connect(optionsWindow.reject)

        def onReset():
            onElementChange(index=spectras.currentIndex(), reset=True)
            applyBtn.setEnabled(True)

        resetBtn.clicked.connect(onReset)

        def onElementChange(index=0, reset: bool = False):
            spectraName = spectras.itemText(spectras.currentIndex())
            if spectraName == "":
                spectras.setCurrentIndex(0)
                return
            totalLabel.setStyleSheet(f"color: {self.text_color};")
            for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget):
                if widget.objectName() == "isotopeDistribution":
                    optionsWindow.mainLayout.removeWidget(widget)
                    widget.deleteLater()

            total = 0
            acc = str(
                max(
                    [
                        len(str(a)) - 2
                        for a in self.defaultDistributions[spectraName].values()
                    ] + [2]
                )
            )
            if reset:
                items = self.defaultDistributions
            else:
                items = self.elementDistributions
            for i, (name, dist) in enumerate(items[spectraName].items()):
                total += dist
                sublayout = QHBoxLayout()
                proxyWidget = QWidget()
                newQLineEdit = QLineEdit()

                newQLineEdit.setValidator(
                    QRegExpValidator(
                        QRegExp(
                            "(0?(\\.[0-9]{1," + acc + "})?|1(\\.0{1," + acc + "})?)"
                        )
                    )
                )
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

        optionsWindow.spectras.setFocus()
        optionsWindow.spectras.editTextChanged.connect(
            lambda: onElementChange(optionsWindow.spectras.currentIndex())
        )

        def onDistributionChange():
            spectraName = spectras.itemText(spectras.currentIndex() or 0)
            if spectraName == "":
                return
            total: float = 0
            acc = min(
                [
                    len(str(a)) - 2
                    for a in self.defaultDistributions[spectraName].values()
                ]
            )
            for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget):
                lineEdit = widget.findChild(QLineEdit)
                distribution = (
                    lineEdit.placeholderText()
                    if lineEdit.text() == ""
                    else lineEdit.text()
                )
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

        onElementChange(optionsWindow.spectras.currentIndex())
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

        optionsWindow = InputSpectraDialog(self, self.styleSheet())
        optionsWindow.inputForm.windowTitle = "Threshold Input"

        spectras = optionsWindow.spectras

        spectras.addItems(self.spectraData.keys())

        inputThreshold = QLineEdit()
        inputThreshold.setPlaceholderText(
            str(self.spectraData[spectras.currentText()].threshold)
        )
        inputThreshold.setValidator(
            QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+"))
        )

        optionsWindow.inputForm.addRow(QLabel("Threshold:"), inputThreshold)

        applyBtn = optionsWindow.buttonBox.addButton(
            QDialogButtonBox.StandardButton.Apply
        )
        cancelBtn = optionsWindow.buttonBox.addButton(
            QDialogButtonBox.StandardButton.Cancel
        )
        applyBtn.setEnabled(False)

        optionsWindow.setWindowTitle("Edit Threshold Value")
        optionsWindow.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)

        optionsWindow.mainLayout.insertItem(1, optionsWindow.inputForm)
        optionsWindow.setLayout(optionsWindow.mainLayout)

        def close():
            optionsWindow.close()

        cancelBtn.clicked.connect(close)

        def onElementChange(index):
            if spectras.itemText(index) == "":
                spectras.setCurrentIndex(0)
                inputThreshold.setText(None)
                return
            inputThreshold.setPlaceholderText(
                str(self.spectraData[spectras.itemText(index)].threshold)
            )

        spectras.editTextChanged.connect(
            lambda: onElementChange(spectras.currentIndex())
        )

        def onThresholdTextChange():
            if inputThreshold.text() == "":
                applyBtn.setEnabled(False)
            else:
                applyBtn.setEnabled(True)

        inputThreshold.textChanged.connect(onThresholdTextChange)

        def onAccept():
            spectraName = spectras.currentText()
            if inputThreshold.text() == "":
                return
            threshold_value = float(inputThreshold.text())
            spectra: SpectraData = self.spectraData[spectraName]
            spectra.thresholds[spectra.plotType] = threshold_value
            spectra.threshold = threshold_value
            spectra.peakDetector.threshold = threshold_value
            self.threshold = threshold_value
            self.numRows = spectra.numPeaks
            spectra.updatePeaks(which="max")
            self.addTableData()
            self.toggleThreshold()
            self.plotDerivatives(spectra)
            self.drawAnnotations(
                spectra, which="max" if self.maxTableOptionRadio.isChecked() else "min"
            )
            for spectra in self.spectraData.values():
                if spectra.isMaxDrawn:
                    spectra.isUpdating = True
                    self.plottingPD(spectra, True)
                if spectra.isMinDrawn:
                    spectra.isUpdating = True
                    self.plottingPD(spectra, False)
            self.updateLabels(spectraName)

        applyBtn.clicked.connect(onAccept)

        inputThreshold.setFocus()
        optionsWindow.setModal(False)
        optionsWindow.show()

    def editLength(self) -> None:
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
            applyBtn.setEnabled(lineEditNG.text() != "" and lineEditNTOT.text() != "")

        lineEditNG.textEdited.connect(onInputChange)
        lineEditNTOT.textEdited.connect(onInputChange)

        def onCancel():
            optionsWindow.close()

        cancelBtn.clicked.connect(onCancel)

        def onAccept():
            lengthConversion = deepcopy(self.length)

            self.length["n-g"] = float(lineEditNG.text())
            self.length["n-tot"] = float(lineEditNTOT.text())
            params["length"] = self.length

            lengthConversion["n-g"] = self.length["n-g"] / lengthConversion["n-g"]
            lengthConversion["n-tot"] = self.length["n-tot"] / lengthConversion["n-tot"]
            for spectra in self.spectraData.values():
                spectra.length = self.length
                if spectra.isToF and not spectra.isImported:
                    spectra.graphData = spectra.graphData * [
                        lengthConversion[spectra.plotType],
                        1,
                    ]

                spectra.updatePeaks("both", True)
                spectra.orderAnnotations("max")
                spectra.orderAnnotations("min")

                for line in self.ax.lines:
                    if f"{spectra.name}-{'ToF'}" == line.get_label():
                        line.set_xdata(spectra.graphData[0])
                        break

                self.drawAnnotations(
                    spectra=spectra,
                    which="max" if self.maxTableOptionRadio.isChecked() else "min",
                )
            self.canvas.draw()

        applyBtn.clicked.connect(onAccept)

        optionsWindow.setModal(False)
        optionsWindow.show()

    def settingsMenu(self) -> None:
        """
        ``settingsMenu``
        ----------------

        Opens a dialog allowing the user to edit settings related to different functionality within the program.
        """
        settingsDialog = QDialog(self)
        settingsDialog.setWindowTitle("Settings")
        settingsDialog.setObjectName("settings")
        settingsDialog.setMinimumSize(600, 820)
        settingsDialog.setStyleSheet(self.setStyleTo(self.currentStyle))
        mainLayout = QVBoxLayout()
        formLayout = QGridLayout()
        formLayout.setObjectName("settings")
        scrollArea = QScrollArea()

        scrollArea.setWidgetResizable(True)
        scrollArea.setVerticalScrollBar(QScrollBar())
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollArea.setMinimumHeight(100)
        inputs = []
        for i, (key, value) in enumerate(params.items()):
            rowLayout = QHBoxLayout()
            rowLayout.setObjectName("row")
            rowTitleLabel = QLabel(key)
            inputLineEdit = QLineEdit()
            inputLineEdit.setObjectName(key)
            if isinstance(value, dict):
                subContentLayout = QVBoxLayout()
                for subKey, subValue in value.items():
                    subRowTitleLabel = QLabel(subKey)
                    subRowContentLayout = QHBoxLayout()
                    subRowContentLayout.setObjectName("row")
                    subInputLineEdit = QLineEdit()
                    subInputLineEdit.setObjectName(f"{key}>{subKey}")
                    subInputLineEdit.setPlaceholderText(str(subValue))
                    if isinstance(subValue, float):
                        subInputLineEdit.setValidator(
                            QRegExpValidator(QRegExp(r"([0-9]*[.])?[0-9]+"))
                        )
                    elif isinstance(subValue, int):
                        subInputLineEdit.setValidator(
                            QRegExpValidator(QRegExp(r"([0-9]*)+"))
                        )
                    elif key == "threshold_exceptions":
                        subInputLineEdit.setValidator(
                            QRegExpValidator(
                                QRegExp(r"\((\d+(\.\d+)?),(\d+(\.\d+)?)\)")
                            )
                        )

                    subRowContentLayout.addWidget(subRowTitleLabel)
                    if "grid" in key:
                        comboBox = QComboBox()
                        comboBox.setEditText(subValue)
                        comboBox.setMinimumSize(150, 40)
                        comboBox.setObjectName(f"{key}>{subKey}")
                        if subKey == "which":
                            comboBox.addItems(["major", "minor", "both"])
                            subRowContentLayout.addWidget(
                                comboBox, alignment=Qt.AlignmentFlag.AlignLeft
                            )
                            inputs.append(comboBox)
                        elif subKey == "axis":
                            comboBox.addItems(["x", "y", "both"])
                            subRowContentLayout.addWidget(
                                comboBox, alignment=Qt.AlignmentFlag.AlignLeft
                            )
                            inputs.append(comboBox)
                        else:
                            colorDialog = QColorDialog()
                            colorDialog.setCurrentColor(QtGui.QColor(subValue))
                            colorDialog.setObjectName(f"{key}>{subKey}")
                            subRowContentLayout.addWidget(
                                colorDialog, alignment=Qt.AlignmentFlag.AlignLeft
                            )

                            inputs.append(colorDialog)
                    else:
                        subRowContentLayout.addWidget(
                            subInputLineEdit, alignment=Qt.AlignmentFlag.AlignLeft
                        )
                        inputs.append(subInputLineEdit)
                    subContentLayout.addLayout(subRowContentLayout)
                rowLayout.addLayout(subContentLayout)

            else:
                inputLineEdit.setPlaceholderText(str(value))
                if type(value) is float or "prominence" in key:
                    inputLineEdit.setObjectName(f"{key}-float")
                    inputLineEdit.setValidator(
                        QRegExpValidator(QRegExp("([0-9]*[.])?[0-9]+"))
                    )
                    rowLayout.addWidget(
                        inputLineEdit, alignment=Qt.AlignmentFlag.AlignLeft
                    )
                    inputs.append(inputLineEdit)

                if type(value) is int:
                    inputLineEdit.setObjectName(f"{key}-int")
                    inputLineEdit.setValidator(QRegExpValidator(QRegExp("([0-9]*)+")))
                    rowLayout.addWidget(
                        inputLineEdit, alignment=Qt.AlignmentFlag.AlignLeft
                    )
                    inputs.append(inputLineEdit)

                if type(value) is bool:
                    comboBox = QComboBox()
                    comboBox.addItems(["False", "True"])
                    comboBox.setCurrentIndex(value)
                    comboBox.setMinimumSize(150, 40)
                    comboBox.setObjectName(f"{key}-bool")
                    rowLayout.addWidget(comboBox, alignment=Qt.AlignmentFlag.AlignLeft)
                    inputs.append(comboBox)

                if type(value) is list:
                    comboBox = QComboBox()
                    comboBox.addItems(value)
                    comboBox.setCurrentIndex(0)
                    comboBox.setMinimumSize(150, 40)
                    comboBox.setObjectName(f"{key}-str")
                    rowLayout.addWidget(comboBox, alignment=Qt.AlignmentFlag.AlignLeft)
                    inputs.append(comboBox)

                if "dir" in key:
                    continue
                    # dirLabel = QLabel(value)
                    # dirLabel.setObjectName(f'{key}-str')

                    # fileDialogButton = QPushButton()
                    # fileDialogButton.setFixedWidth(40)
                    # fileDialogButton.clicked.connect(lambda: handleFileChange(dirLabel))
                    # rowLayout.addWidget(dirLabel)
                    # inputs.append(dirLabel)
                    # rowLayout.addWidget(fileDialogButton, alignment=Qt.AlignmentFlag.AlignRight)
            formLayout.addWidget(
                rowTitleLabel, i, 0, alignment=Qt.AlignmentFlag.AlignTop
            )
            formLayout.addLayout(rowLayout, i, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        buttonBox = QDialogButtonBox()

        onResetBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Reset)
        onAcceptBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Yes)
        onAcceptBtn.setText("Accept")
        onCancelBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)

        def handleFileChange(label: QLineEdit) -> None:
            label.setText(QFileDialog.getExistingDirectory(self, "Select a Folder"))

        def onAccept() -> None:
            # ! Work out assignment to nested dictionary
            newLength = {}
            newThresholds = {}
            newGridSettings = {}
            for key in params.keys():
                newInputs = [input for input in inputs if key in input.objectName()]
                for input in newInputs:
                    if isinstance(input, QComboBox):
                        value = input.currentText()
                    elif isinstance(input, QColorDialog):
                        value = input.currentColor().name()
                    else:
                        value = (
                            input.text() if input.text() else input.placeholderText()
                        )
                    if (
                        ">" in input.objectName()
                    ):  # Handling dictionary assignment within params
                        dicKey, dicSubKey = input.objectName().split(">")
                        if dicKey == "length":
                            newLength[dicSubKey] = float(value)
                        elif dicKey == "threshold_exceptions":
                            newThresholds[dicSubKey] = (
                                float(value[1:-1].split(",")[0]),
                                float(value[1:-1].split(",")[1]),
                            )
                        elif dicKey == "grid_settings":
                            newGridSettings[dicSubKey] = value
                    elif isinstance(input, (QLineEdit, QLabel, QComboBox)):
                        params[key] = (
                            float(value)
                            if "float" in input.objectName()
                            else int(value)
                            if "int" in input.objectName()
                            else bool(True if "True" in input.currentText() else False)
                            if "bool" in input.objectName()
                            else value
                        )

            params["length"] = newLength
            params["threshold_exceptions"] = newThresholds
            params["grid_settings"] = newGridSettings

        onAcceptBtn.clicked.connect(onAccept)

        def onReset() -> None:
            for key, value in self.defaultParams.items():
                params[key] = value

        onResetBtn.clicked.connect(onReset)

        def onCancel():
            settingsDialog.close()

        onCancelBtn.clicked.connect(onCancel)
        viewport = QWidget()
        viewport.setObjectName("viewport")
        viewport.setLayout(formLayout)
        scrollArea.setWidget(viewport)
        scrollArea.setObjectName("settingsMenu")
        mainLayout.addWidget(scrollArea)
        mainLayout.addWidget(buttonBox)
        viewport.setStyleSheet(self.styleSheet())
        settingsDialog.setLayout(mainLayout)
        settingsDialog.setModal(False)

        settingsDialog.exec()

    def gridLineOptions(self) -> None:
        """
        ``gridLineOptions``
        -------------------
        Opens a dialog with settings related to the gridlines of the canvas.
        Options include: Which axis to plot gridlines for, which type; major, minor or both ticks, as well as color.
        """

        optionsWindowDialog = QDialog(self)
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
                f"border: 1px solid #AAA; background-color: {str(gridColorDialog.selectedColor().name())};"
            )

        gridColorDialog.colorSelected.connect(onColorPick)

        def onReset():
            map(
                lambda btn: btn.setChecked(False),
                getLayoutWidgets(mainLayout, QRadioButton),
            )
            majorRadioBtn.setChecked(True)
            bothAxisRadioBtn.setChecked(True)
            gridColorDialog.setCurrentColor(QtGui.QColor(68, 68, 68, 255))

            gridColorBtn.setStyleSheet(
                f"border: 1px solid #AAA; background-color:{self.gridSettings['color']};"
            )
            self.toggleGridlines(
                self.gridCheck.isChecked(), *self.gridSettings.values()
            )

        onResetBtn.clicked.connect(onReset)

        def onAccept():
            self.gridSettings = {
                "which": [
                    radio.text().lower()
                    for radio in getLayoutWidgets(gridlineLayout)
                    if radio.isChecked()
                ][0],
                "axis": [
                    radio.text().lower()
                    for radio in getLayoutWidgets(axisLayout)
                    if radio.isChecked()
                ][0],
                "color": gridColorDialog.currentColor().name(),
            }
            self.toggleGridlines(
                self.gridCheck.isChecked(), *self.gridSettings.values()
            )

        onAcceptBtn.clicked.connect(onAccept)

        def onCancel():
            optionsWindowDialog.close()

        onCancelBtn.clicked.connect(onCancel)

        optionsWindowDialog.setModal(False)

        optionsWindowDialog.show()

    def editMaxPeaks(self) -> None:
        """
        ``editMaxPeaks``
        ----------------
        Opens a Dialog window for inputting the max peak label quantity for a selected graph, drawingthe relevant
        annotations.
        """
        if self.spectraData == {}:
            return

        optionsWindow = InputSpectraDialog(self, self.styleSheet())
        spectras = optionsWindow.spectras

        spectras.addItems(self.spectraData.keys())

        inputMaxPeaks = QLineEdit()
        inputMaxPeaks.setPlaceholderText(
            str(self.spectraData[spectras.currentText()].numPeaks)
        )
        inputMaxPeaks.setValidator(QRegExpValidator(QRegExp("[0-9]{0,4}")))

        optionsWindow.inputForm.addRow(QLabel("Peak Quantity:"), inputMaxPeaks)

        applyBtn = optionsWindow.buttonBox.addButton(
            QDialogButtonBox.StandardButton.Apply
        )
        cancelBtn = optionsWindow.buttonBox.addButton(
            QDialogButtonBox.StandardButton.Cancel
        )

        optionsWindow.setWindowTitle("Displayed Peaks Quantity")
        optionsWindow.mainLayout.insertItem(1, optionsWindow.inputForm)
        optionsWindow.setLayout(optionsWindow.mainLayout)

        def closeWindow():
            optionsWindow.close()

        cancelBtn.clicked.connect(closeWindow)

        def changePeaksText():
            inputMaxPeaks.setPlaceholderText(
                str(self.spectraData[spectras.currentText()].numPeaks)
            )

        spectras.activated.connect(changePeaksText)

        def onAccept():
            substance_name = spectras.currentText()
            if inputMaxPeaks.text() == "":
                return
            maxPeaks = int(inputMaxPeaks.text())
            self.spectraData[substance_name].maxPeaks = maxPeaks
            self.drawAnnotations(
                self.spectraData[substance_name],
                which="max" if self.maxTableOptionRadio.isChecked() else "min",
            )

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

        optionsWindow = InputSpectraDialog(self, self.styleSheet())
        nameLineEdit = QLineEdit()
        nameLineEdit.setPlaceholderText("Enter Name")

        optionsWindow.mainLayout.insertWidget(0, nameLineEdit)
        spectras = optionsWindow.spectras

        spectras.lineEdit().setPlaceholderText("Select an Isotope / Element")
        spectras.addItems(
            [
                self.combobox.itemText(i)
                for i in range(self.combobox.count())
                if "element" in self.combobox.itemText(i)
            ]
        )

        totalLabel = QLabel("Total: 0")

        applyBtn = optionsWindow.buttonBox.addButton(
            QDialogButtonBox.StandardButton.Apply
        )
        applyBtn.setText("Create")
        applyBtn.setEnabled(False)

        addBtn = optionsWindow.buttonBox.addButton(QDialogButtonBox.StandardButton.Yes)
        addBtn.setText("Add")
        addBtn.setEnabled(False)

        resetBtn = optionsWindow.buttonBox.addButton(
            QDialogButtonBox.StandardButton.Reset
        )
        cancelBtn = optionsWindow.buttonBox.addButton(
            QDialogButtonBox.StandardButton.Cancel
        )

        optionsWindow.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        optionsWindow.setWindowTitle("Compound Creater")
        optionsWindow.setLayout(optionsWindow.mainLayout)

        optionsWindow.mainLayout.insertWidget(
            len(optionsWindow.children()) - 2, totalLabel
        )

        compoundElements = {}
        compoundMode = []

        def onAccept():
            applyBtn.setEnabled(False)
            compoundDist = {
                widget.findChild(QLabel).text()[:-1].replace('element_', '').replace('_n-tot', '').replace('_n-g', ''):
                    float(widget.findChild(QLineEdit).text()
                          )
                for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget)
            }

            if nameLineEdit.text() == "":
                QMessageBox.warning(self, "Warning", "Enter a name")
                applyBtn.setEnabled(True)
                return
            plotType = "n-tot" if "n-tot" in str(compoundDist.keys()) else "n-g"
            weightedGraphData = {
                name: pd.read_csv(
                    resource_path(f"{self.graphDataDir}element_{name}_{plotType}.csv"), header=None
                ) * [1, dist]
                for name, dist in compoundDist.items()
                if dist != 0
            }
            name = f"compound_{nameLineEdit.text()}_{plotType}"
            newElement = SpectraData(
                name,
                None,
                None,
                None,
                None,
                None,
                None,
                compoundDist,
                compoundDist,
                isCompound=True,
            )
            newElement.setGraphDataFromDist(weightedGraphData)
            newElement.graphData.to_csv(
                f"{self.graphDataDir}Compound Data\\{name}.csv",
                index=False,
                header=False,
            )
            pd.DataFrame(compoundDist.items()).to_csv(
                f"{self.dir}data\\Distribution Information\\{name}.csv",
                index=False,
                header=False,
            )

            self.compoundNames.append(name)
            self.compoundCombobox.clear()
            self.compoundCombobox.addItems(self.compoundNames)
            self.defaultDistributions[name] = compoundDist
            self.elementDistributions[name] = deepcopy(compoundDist)

        applyBtn.clicked.connect(onAccept)
        cancelBtn.clicked.connect(optionsWindow.reject)

        def onReset():
            spectras.lineEdit().clear()
            spectras.clear()
            spectras.addItems(
                [
                    self.combobox.itemText(i)
                    for i in range(self.combobox.count())
                    if "element" in self.combobox.itemText(i)
                ]
            )
            totalLabel.setText("Total: 0")
            onRemove()

        resetBtn.clicked.connect(onReset)

        def onElementChange(index):
            spectraName = spectras.itemText(index)
            if spectraName == "":
                addBtn.setEnabled(False)
                return
            if spectraName in compoundElements.keys():
                addBtn.setEnabled(False)
                return
            addBtn.setEnabled(True)

        spectras.editTextChanged.connect(
            lambda: onElementChange(spectras.currentIndex())
        )

        def onAddRow(index=None):
            spectraName = spectras.itemText(spectras.currentIndex() or 0)
            if spectraName == "":
                spectras.setCurrentIndex(0)
                return
            if compoundElements == {}:
                compoundMode.append(spectraName.split("_")[-1])

                optionsWindow.spectras.blockSignals(True)
                spectraNames = spectras.getAllItemText()
                spectras.clear()
                spectras.addItems(
                    [name for name in spectraNames if compoundMode[0] in name]
                )
                optionsWindow.spectras.blockSignals(False)

            totalLabel.setStyleSheet("color: #FFF;")

            sublayout = QHBoxLayout()
            proxyWidget = QWidget()
            newQLineEdit = QLineEdit()
            newQLineEdit.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
            )

            newQLineEdit.setValidator(
                QRegExpValidator(QRegExp("(0?(\\.[0-9]{1,6})?|1(\\.0{1,6})?)"))
            )
            newQLineEdit.setPlaceholderText("0")
            title = QLabel(f"{spectraName}:")
            removeBtn = QPushButton()
            removeBtn.setIcon(
                QIcon(resource_path(f"{params['dir_img']}delete-component.svg"))
            )
            removeBtn.setObjectName("compoundDelBtn")
            removeBtn.clicked.connect(lambda: onRemove(spectraName))
            index = len(optionsWindow.children())
            sublayout.addWidget(title)
            sublayout.addWidget(newQLineEdit)
            sublayout.addWidget(removeBtn)
            sublayout.setSpacing(1)
            proxyWidget.setLayout(sublayout)
            proxyWidget.setFixedHeight(38)
            proxyWidget.setObjectName(f"{spectraName}-RowWidget")
            newQLineEdit.textChanged.connect(onDistributionChange)
            optionsWindow.mainLayout.insertWidget(index - 3, proxyWidget)
            optionsWindow.updateGeometry()

            compoundElements[spectraName] = 0
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

            if (
                spectras.itemText(spectras.currentIndex() or 0)
                not in compoundElements.keys()
            ):
                addBtn.setEnabled(True)

        def onDistributionChange():
            total = 0
            for widget in getLayoutWidgets(optionsWindow.mainLayout, QWidget):
                lineEdit = widget.findChild(QLineEdit)
                distribution = (
                    lineEdit.placeholderText()
                    if lineEdit.text() == ""
                    else lineEdit.text()
                )
                if distribution == ".":
                    continue
                else:
                    total += float(distribution)

            compoundDist = {
                widget.findChild(QLabel).text()[:-1]: float(
                    widget.findChild(QLineEdit).text()
                )
                if widget.findChild(QLineEdit).text() not in ["", "."]
                else float(widget.findChild(QLineEdit).placeholderText())
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

        spectras.setFocus()
        onElementChange(spectras.currentIndex())
        optionsWindow.setModal(False)
        optionsWindow.show()

    def setStyleTo(self, style: Literal["dark", "light", "contrast"] = "dark") -> str:  # noqa: F821
        self.currentStyle = style
        if style == "dark":
            self.bg_color = "#202020"
            self.text_color = "#FFF"
        elif style == "light":
            self.bg_color = "#968C80"
            self.text_color = "#FFF"
        elif style == "contrast":
            self.bg_color = "#000"
            self.text_color = "#FFF"
        return f"""
        #mainWindow{{
            background-color: {self.bg_color};
        }}

        #settings{{
            background-color: {self.bg_color};
            color: {self.text_color};
        }}

        *{{
            font-family: 'Roboto Mono';
            font-size: 10pt;
            font-weight: 400;
        }}

        QMenuBar {{
            color: {self.text_color};
        }}
        QMenuBar::item:selected {{
            color: #000;
        }}

        QCheckBox{{
            color: {self.text_color};
        }}

        QCheckbox::indicator:checked{{
            image: url({self.checkBoxChecked});
        }}

        QCheckbox::indicator:unchecked{{
            image: url({self.checkBoxChecked});
        }}

        QComboBox{{
            background-color: #EEE;
            border-radius: 3px;
            font-family: 'Roboto Mono';
            font-size: 10pt;
            font-weight: 400;
        }}
        QCombobox QAbstractItemView {{
            min-width: 1000px;
        }}

        QMenuBar{{
            background-color: {self.bg_color};
            color: {self.text_color};
        }}

        QSplitter::handle:vertical{{
            image: url({self.drag});
            height: 11px;
        }}

        QLabel#numPeakLabel,
              #thresholdLabel,
              #orderlabel,
              #compoundLabel,
              #peakLabel,
              #tableTypeLabel,
              #gridOptionLabel{{
            font: 12pt 'Roboto Mono Medium';
            color: {self.text_color};
        }}
        QLineEdit#dir{{
            direction: left;
            text-overflow: ellipsis;
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
                   #compoundBtn:enabled
                   {{
                       color: #000;
                    }}

        QCheckBox#gridCheck,
                 #thresholdCheck,
                 #label_check,
                 #orderByIntegral,
                 #orderByPeakW,
                 #peakCheck,
                 #limitCheck,
                 #tableCheck,
                 #graphCheck
                 {{
                    font-weight: 500;
                 }}

        QCheckBox#grid_check::indicator:unchecked,
                 #thresholdCheck::indicator:unchecked,
                 #label_check::indicator:unchecked,
                 #peakCheck::indicator:unchecked,
                 #limitCheck::indicator:unchecked,
                 #tableCheck::indicator:unchecked,
                 #graphCheck::indicator:unchecked
                 {{
                   image: url({self.checkBoxUnchecked});
                   color: {self.text_color};
                 }}

        QCheckBox#grid_check::indicator:checked,
                 #thresholdCheck::indicator:checked,
                 #label_check::indicator:checked,
                 #peakCheck::indicator:checked,
                 #limitCheck::indicator:checked,
                 #tableCheck::indicator:checked,
                 #graphCheck::indicator:checked
                 {{
                     image: url({self.checkBoxChecked});
                     color: {self.text_color};
                 }}

        QCheckBox#grid_check:disabled,
                 #thresholdCheck:disabled,
                 #label_check:disabled,
                 #limitCheck:disabled,
                 #tableCheck:disabled,
                 #graphCheck:disbaled
                 {{
                     color: #AAA;
                 }}
        QCheckBox#grid_check:enabled,
                 #thresholdCheck:enabled,
                 #label_check:enabled,
                 #limitCheck:enabled,
                 #tableCheck:enabled,
                 #graphCheck:enabled
                 {{
                     color: {self.text_color};
                 }}

        QDialog {{
            color: {self.text_color};
            background-color: {self.bg_color};
        }}
        QDialog#inputWindow, QDialog#optionsWindow
        {{
            color: {self.text_color};
            background-color: {self.bg_color};
        }}

        QDialog#inputWindow QLabel, QDialog#optionsWindow QLabel{{
            color: {self.text_color};
        }}

        QDialog#optionsDialog QCombobox, QDialog#optionsWindow QComboBox{{
            background-color: {self.text_color};
        }}

        QDockWidget{{
            background-color: {self.bg_color};
            color: {self.text_color};
        }}

        QDockWidget::title{{
            color: {self.text_color};
        }}
        QGridLayout#settings{{
            color: {self.text_color};
            background-color: {self.bg_color};
        }}
        QGridLayout#inputForm{{
            color: {self.text_color};
            border: 1px solid #AAA;
            background-color: {self.bg_color};
        }}
        QRadioButton:enabled{{
            color: {self.text_color};
            font-size: 9pt;
            font-weight: 400;
        }}

        QRadioButton::indicator:unchecked{{
            image: url({self.radioUnchecked});
            color: #AAA;
        }}
        QRadioButton::indicator:checked{{
            image: url({self.radioChecked});
            color: {self.text_color};
        }}

        QRadioButton#orderByIntegral:enabled,
                    #orderByPeakW:enabled
                    {{
                        color: {self.text_color};
                    }}
        QRadioButton#orderByIntegral::indicator:unchecked,
                    #orderByPeakW::indicator:unchecked
                    {{
                        image: url({self.radioUnchecked});
                        color: #AAA;
                    }}

        QRadioButton#orderByIntegral::indicator:checked,
                    #orderByPeakW::indicator:checked
                    {{
                        image: url({self.radioChecked});
                        color: {self.text_color};
                    }}

        QWidget#peakCanvasContainer{{
            margin: 9px;
            background-color: #FFF;
        }}

        QWidget#mainContainer {{
            background-color: {self.text_color};
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
            image: url({self.expandDown});
        }}

        QHeaderView::up-arrow{{
            image: url({self.expandUp});
        }}

        QTableView#dataTable {{
            font-size: 8pt;
            border-style: none;
        }}

        QMessageBox QLabel{{
            color: {self.text_color};
        }}
        #periodicTable{{
            color: {self.text_color};
            background-color: {self.bg_color};
        }}
        #periodicTable QLabel{{
            color: {self.text_color};
            font-weight: 800;
            font-size: 12pt;
        }}
        """

    def viewDarkStyle(self) -> None:
        """
        ``viewDarkStyle``
        -----------------
        Applies the dark theme to the GUI.
        """

        self.setStyleSheet(self.setStyleTo("dark"))

    def viewLightStyle(self) -> None:
        """
        ``viewLightStyle``
        ------------------
        Applies the light theme to the GUI.
        """
        self.setStyleSheet(self.setStyleTo("light"))

    def viewHighContrastStyle(self) -> None:
        """
        ``viewHighContrastStyle``
        -------------------------
        Applies the high contrast theme to the GUI.
        """
        self.setStyleSheet(self.setStyleTo("contrast"))

    def toggleBtnControls(
        self,
        enableAll: bool = False,
        plotEnergyBtn: bool = False,
        plotToFBtn: bool = False,
        clearBtn: bool = False,
        pdBtn: bool = False,
    ) -> None:
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

        for btn in getLayoutWidgets(self.btnLayout, QPushButton) + getLayoutWidgets(
            self.btnTopLayout, QPushButton
        ):
            btn.setEnabled(enableAll)

        if enableAll:
            return

        for btn in getLayoutWidgets(self.btnLayout, QPushButton) + getLayoutWidgets(
            self.btnTopLayout, QPushButton
        ):
            if btn.__name__ == "plotEnergyBtn":
                btn.setEnabled(plotEnergyBtn)
            if btn.__name__ == "plotToFBtn":
                btn.setEnabled(plotToFBtn)
            if btn.__name__ == "clearBtn":
                btn.setEnabled(clearBtn)
            if btn.__name__ == "pdBtn":
                btn.setEnabled(pdBtn)

    def toggleCheckboxControls(
        self,
        enableAll: bool,
        gridlines: bool = False,
        peakLimit: bool = False,
        hidePeakLabels: bool = False,
    ) -> None:
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
            if btn.__name__ == "gridCheck":
                btn.setEnabled(gridlines)
            if btn.__name__ == "peakCheck":
                btn.setEnabled(hidePeakLabels)
            if btn.__name__ == "pdCheck":
                btn.setEnabled(peakLimit)

    def plotSelectionProxy(self, index: int, comboboxName: str):
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

    def resetTableProxy(self, combobox: QComboBox) -> None:
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
            self.selectionName = combobox.currentText()
            if combobox.currentText() == "" and self.table_model is not None:
                self.table.setSortingEnabled(False)
                proxy = CustomSortingProxy()
                proxy.setSourceModel(self.table_model)

                self.table.setModel(proxy)
                self.table_model.titleRows = self.titleRows
                self.table.setModel(self.table_model)
                self.table.clearSpans()
                for row in self.titleRows[:-1]:
                    self.table.setSpan(row, 0, 1, 10)
                    self.table.setItemDelegateForRow(
                        row, ButtonDelegate(self, self.table, self.table_model)
                    )
                    self.table.openPersistentEditor(self.table_model.index(row, 0))
                self.table.setSortingEnabled(True)

            elif combobox.currentText() in substanceNames:
                self.displayData()
        except AttributeError:
            self.table.setModel(None)

    def updateLabels(self, name: str = None) -> None:
        numPeaks = self.numRows
        try:
            if name is None:
                raise KeyError
            self.thresholds = self.spectraData[name].thresholds
        except KeyError:
            self.thresholds = params["threshold_exceptions"].get(
                interpName(self.selectionName)["symbol"], (100, 100)
            )

            # Setting label information based on threshold value
        try:
            labelInfo = f"""Threshold for peak detection (n-tot mode, n-g mode): ({
                self.thresholds[0]},{self.thresholds[1]})"""
        except KeyError:
            labelInfo = f"""Threshold for peak detection (n-tot mode, n-g mode): ({
                self.thresholds['n-tot']},{self.thresholds['n-g']})"""

        self.thresholdLabel.setText(str(labelInfo))
        # Changing the peak label text
        if name is not None:
            numPeaks = str(self.spectraData[name].peakDetector.numPeaks
                           if self.maxTableOptionRadio.isChecked()
                           else self.spectraData[name].peakDetector.numDips)
        else:
            numPeaks = 'None'
        self.peaklabel.setText(f"Number of Peaks: {numPeaks}")

    def displayData(self) -> None:
        """
        ``displayData``
        ---------------
        Will display relevant peak information in the table for the selection made (self.selectionName).
        Once a select is made, the relevant controls are enabled.
        """
        if self.selectionName is None:
            return
        if (
            self.selectionName == "" and self.plotCount > -1
        ):  # Null selection and graphs shown
            self.toggleBtnControls(clearBtn=True)
            return
        elif (
            self.selectionName == "" and self.plotCount == -1
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

        self.showTableData()

        self.updateLabels()

    def showTableData(self):
        """
        ``showTableData``
        -----------------
        Read and display the selected substances data within the table.
        """
        # Finding relevant file for peak information
        filepath = None
        for file in os.listdir(params["dir_peakInfo"]):
            if self.selectionName.replace("element_", "") in file:
                filepath = resource_path(f"""{
                    params['dir_peakInfo']
                }{file[:-7]}{'max' if self.maxTableOptionRadio.isChecked() else 'min'}.csv""")
                break

        try:
            for row in self.table_model.titleRows:
                self.table.setItemDelegateForRow(row, None)
        except AttributeError:
            pass
        try:
            if filepath is None:
                raise ValueError

            self.table.blockSignals(True)
            file = pd.read_csv(resource_path(filepath), header=0)
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

        except (ValueError, FileNotFoundError):
            self.table.setModel(None)
            self.numRows = None

    def addTableData(self, reset: bool = False):
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
            for row in self.table_model.titleRows[:-1]:
                self.table.setItemDelegateForRow(row, None)
        except AttributeError:
            pass
        self.table.setModel(None)
        self.table_model = None
        self.table.setSortingEnabled(False)
        self.titleRows = [0]
        dataInTable = []
        # ! ---------------------------------------------------------------------------------
        # ? Maybe sort the order in which they are plotted and added to the table.
        for spectra in self.spectraData.values():
            if spectra.name in dataInTable:
                continue
            table_data = pd.concat(
                [
                    table_data,
                    spectra.maxTableData
                    if self.maxTableOptionRadio.isChecked()
                    else spectra.minTableData,
                ],
                ignore_index=True,
            )
            self.titleRows.append(self.titleRows[-1] + spectra.tableData.shape[0])
            dataInTable.append(spectra.name)
            self.elementDataNames.append(spectra.name)

        self.table_model = ExtendedQTableModel(table_data, parent=self)

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
            self.table.setItemDelegateForRow(
                row, ButtonDelegate(self, self.table, self.table_model)
            )
            self.table.openPersistentEditor(self.table_model.index(row, 0))
        self.table.blockSignals(False)

    def updateGuiData(
        self,
        tof: bool = False,
        filepath: str = None,
        imported: bool = False,
        name: str = None,
        distAltered: bool = False,
    ) -> None:
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

        if (
            self.combobox.currentIndex() == 0 and self.compoundCombobox.currentIndex() == 0
        ):
            self.toggleBtnControls(
                enableAll=True, plotEnergyBtn=False, plotToFBtn=False
            )

        if self.selectionName is None and not imported:
            QMessageBox.warning(self, "Error", "You have not selected anything to plot")
            return
        if imported:
            self.selectionName = name
        if (
            interpName(self.selectionName)["symbol"] is None and not imported and "compound" not in self.selectionName
        ):
            QMessageBox.warning(self, "Warning", "Graph is already plotted")
            self.toggleCheckboxControls(enableAll=False)
            return
        # Checks for adding mutliple graphs for the same selection, energy/tof types.
        if (self.selectionName, tof) in self.plottedSpectra and not distAltered:
            QMessageBox.warning(self, "Warning", "Graph is already plotted")
            return

        if (self.selectionName, tof) not in self.plottedSpectra:
            self.plottedSpectra.append((self.selectionName, tof))

        self.titleRows = [0]

        for spectraName, tof in self.plottedSpectra:
            title = f"{spectraName}-{'ToF' if tof else 'Energy'}"
            # ¦ -----------------------------------

            if title in self.spectraData.keys():
                if self.spectraData[title].isGraphDrawn:
                    continue
            if "compound" in spectraName:
                self.plotFilepath = (
                    f"{params['dir_compoundGraphData']}{spectraName}.csv"
                )
            else:
                self.plotFilepath = (
                    f"{self.graphDataDir}{spectraName}.csv"
                    if filepath is None
                    else filepath
                )
            peakInfoDir = (
                f"{self.dir}data\\Peak information\\" if filepath is None else None
            )

            try:
                graphData = pd.read_csv(
                    resource_path(self.plotFilepath), header=None
                ).iloc[:, :2]

            except pd.errors.EmptyDataError:
                QMessageBox.warning(self, "Warning", "Selection has Empty Graph Data")
                self.plottedSpectra.remove((self.selectionName, tof))
                if self.plotCount == -1:
                    self.toggleCheckboxControls(enableAll=False)
                    self.toggleBtnControls(
                        plotEnergyBtn=True, plotToFBtn=True, clearBtn=True, pdBtn=False
                    )
                return
            except FileNotFoundError:
                if self.spectraData.get(spectraName, False):
                    self.spectraData[spectraName].graphData.to_csv(
                        self.plotFilepath, index=False, header=False
                    )

                    graphData = self.spectraData[spectraName].graphData
            try:
                graphData = graphData[~graphData[0].str.contains("#")].astype(float)
                if graphData.select_dtypes(np.number).empty:
                    QMessageBox.warning(self, "Wanring", "Data Format Invalid")
                    self.plottedSpectra.remove((self.selectionName, tof))
                    return
            except AttributeError:
                pass
            except ValueError:
                QMessageBox.warning(self, "Warning", "Invalid Format - Requires (x,y)")
                self.plottedSpectra.remove((self.selectionName, tof))
                if self.plotCount == -1:
                    self.toggleCheckboxControls(enableAll=False)
                return

            try:
                elementTableDataMax = pd.read_csv(
                    resource_path(
                        f"{peakInfoDir}{'TOF' if tof else 'Energy'}/{spectraName.replace(
                            'element_', '')}_tableData_max.csv"
                    )
                )
            except FileNotFoundError:
                elementTableDataMax = pd.DataFrame(
                    columns=[
                        "Rank by Integral",
                        "TOF (us)" if tof else "Energy (eV)",
                        "Rank by " + ("TOF" if tof else "Energy"),
                        "Integral",
                        "Peak Width",
                        "Rank by Peak Width",
                        "Peak Height",
                        "Rank by Peak Height",
                        "Relevant Isotope",
                    ]
                )
            # Title Rows
            if elementTableDataMax.empty:
                elementTableDataMax.loc[-1] = [
                    f"No Peak Data for {spectraName}",
                    *[""] * 8,
                ]

            else:
                elementTableDataMax.loc[-1] = [spectraName, *[""] * 8]
            elementTableDataMax.index += 1
            elementTableDataMax.sort_index(inplace=True)
            try:
                elementTableDataMin = pd.read_csv(
                    resource_path(
                        f"{peakInfoDir}{'TOF' if tof else 'Energy'}/{spectraName.replace(
                            'element_', '')}_tableData_min.csv"
                    )
                )
            except FileNotFoundError:
                elementTableDataMin = pd.DataFrame(
                    columns=[
                        "Rank by Integral",
                        "TOF (us)" if tof else "Energy (eV)",
                        "Rank by " + ("TOF" if tof else "Energy"),
                        "Integral",
                        "Peak Width",
                        "Rank by Peak Width",
                        "Peak Height",
                        "Rank by Peak Height",
                        "Relevant Isotope",
                    ]
                )
            # Title Rows
            if elementTableDataMin.empty:
                elementTableDataMin.loc[-1] = [
                    f"No Peak Data for {spectraName}",
                    *[""] * 8,
                ]

            else:
                elementTableDataMin.loc[-1] = [spectraName, *[""] * 8]
            elementTableDataMin.index += 1
            elementTableDataMin.sort_index(inplace=True)

            if self.spectraData.get(title, False):
                for point in self.spectraData[title].annotations:
                    point.remove()
            symbol = interpName(spectraName)["symbol"]
            thresholds = params["threshold_exceptions"].get(
                symbol, {"n-tot": 100, "n-g": 100}
            )
            newSpectra = SpectraData(
                name=spectraName,
                numPeaks=self.numRows,
                tableDataMax=elementTableDataMax,
                tableDataMin=elementTableDataMin,
                graphData=graphData,
                graphColour=getRandomColor(),
                isToF=tof,
                distributions=self.elementDistributions.get(spectraName, None),
                defaultDist=self.defaultDistributions.get(spectraName, None),
                distChanging=distAltered,
                isCompound="compound" in spectraName,
                isAnnotationsHidden=self.peakLabelCheck.isChecked(),
                thresholds=thresholds,
                length=params["length"],
                isImported=imported,
                updatingDatabase=params["updating_database"],
            )

            self.spectraData[title] = newSpectra

        redrawMax = False
        redrawMin = False
        if distAltered:
            title = f"{newSpectra.name}-{'ToF' if tof else 'Energy'}"
            for line in self.ax.get_lines():
                if title in line.get_label():
                    line.remove()
            try:
                for line in self.axPD.get_lines():
                    if "max" in line.get_gid():
                        redrawMax = True
                    if "min" in line.get_gid():
                        redrawMin = True
                    if title in line.get_label() or title in line.get_gid():
                        line.remove()

            except AttributeError:
                pass

        distAltered = False

        self.plot(newSpectra, filepath, imported, name)
        if redrawMax:
            self.plottingPD(newSpectra, True)
        if redrawMin:
            self.plottingPD(newSpectra, False)

        self.onPeakTableOptionChange()
        self.updateLabels(title)

        self.canvas.draw()

    def plot(
        self,
        spectraData: SpectraData,
        filepath: str = None,
        imported: bool = False,
        name: str = None,
    ) -> None:
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

            self.ax.set_xscale("log")
            self.ax.set_yscale("log")
            self.ax.xaxis.set_minor_locator(LogLocator(10, "all"))
            self.ax.xaxis.set_minor_formatter(
                LogFormatterSciNotation(10, False, (np.inf, np.inf))
            )
            self.ax.minorticks_on()
            plt.minorticks_on()
            self.ax.xaxis.set_tick_params("major", size=12, color="#888", labelsize=9)
            self.ax.xaxis.set_tick_params(
                "minor",
                size=4,
                color="#888",
                labelsize=6,
                labelrotation=45,
            )

        # Allows user to plot in ToF if chosen # -----------------------------------------------------------------------
        if spectraData.isToF and not imported:
            # ! Convert to pandas compatible

            if self.plotCount < 0:
                self.ax.set(
                    xlabel="ToF (uS)",
                    ylabel="Cross section (b)",
                    title=self.selectionName,
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

        label = f"{spectraData.name}{'-ToF' if spectraData.isToF else '-Energy'}"

        if not spectraData.graphData.empty:
            self.ax.plot(
                spectraData.graphData.iloc[:, 0],
                spectraData.graphData.iloc[:, 1],
                "-",
                c=spectraData.graphColour,
                alpha=0.6,
                linewidth=1.0,
                label=label,
                gid=spectraData.name
                if self.selectionName is None
                else self.selectionName,
            )
            spectraData.isGraphDrawn = True

            spectraData.isUpdating = False

        # Establishing plot count
        self.plotCount += 1

        # Plot derivatives, check settings debug section to customise.

        self.plotDerivatives(spectraData)

        self.updateLegend()
        self.toggleThreshold()

        self.ax.autoscale()  # Tidying up

        self.figure.tight_layout()
        self.canvas.draw()

    def plotDerivatives(self, spectraData: SpectraData) -> None:
        """
        ``plotDerivatives``
        -------------------

        Use to plot the the x-coord for zeros of the first and second derivatives as well as the smoothed graph data
        its based on.

        Check settings.py in Debug settings to enable and disable each plot.
        - params['show_smoothed']
        - params['show_first_der']
        - params['show_second_der']

        Args:
            spectraData (SpectraData): Which spectra to plot for.
        """
        if all([not params['show_smoothed'], not params['show_first_der'], not params['show_second_der']]):
            return
        if spectraData is None:
            return
        if spectraData.maxPeakLimitsX != {}:
            left, right = (
                list(spectraData.maxPeakLimitsX.values())[0][0],
                list(spectraData.maxPeakLimitsX.values())[-1][1],
            )
            left, right = (
                spectraData.graphData[
                    spectraData.graphData.iloc[:, 0] == left
                ].index.values.astype(int),
                spectraData.graphData[
                    spectraData.graphData.iloc[:, 0] == right
                ].index.values.astype(int),
            )
        else:
            left = 1e-5
            right = 2e7
        ax: matplotlib.axes.Axes = self.axPD if self.axPD is not None else self.ax

        for line in [
            line
            for line in ax.get_lines()
            if "Der" in line.get_gid() and spectraData.name in line.get_gid()
        ]:
            line.remove()
        smoothGraph = spectraData.peakDetector.smoothGraph
        graphData = spectraData.peakDetector.secDerivative
        label = f"{spectraData.name}-{"ToF" if spectraData.isToF else "Energy"}"
        if params["show_smoothed"]:
            ax.plot(
                smoothGraph.iloc[:, 0],
                smoothGraph.iloc[:, 1],
                "-",
                alpha=0.6,
                color="#00F",
                linewidth=1.0,
                label=f"{label}-Smoothed",
                gid=f"{label}-Smoothed-Der",
            )
            self.plottedSpectra.append((f"{label}-Smoothed", spectraData.isToF))

        if params["show_first_der"]:
            dips = spectraData.peakDetector.dips
            flats = spectraData.peakDetector.peaks
            for x in graphData.iloc[flats[np.where(flats < right)]].iloc[:, 0]:
                ax.axvline(
                    x,
                    color="#00ff00aa",
                    linewidth=0.7,
                    alpha=0.8,
                    gid=f"{label}-{x}-Flats-Der",
                )

            for x in graphData.iloc[dips[np.where(dips < right)]].iloc[:, 0]:
                ax.axvline(
                    x,
                    color="#F0F",
                    linewidth=0.7,
                    alpha=0.8,
                    gid=f"{label}-{x}-Dips-Der",
                )

        if params["show_second_der"]:
            infls = spectraData.peakDetector.infls
            for x in graphData.iloc[
                infls[np.where((infls > left) & (infls < right))]
            ].iloc[:, 0]:
                ax.axvline(
                    x,
                    color="#00F",
                    linewidth=0.7,
                    alpha=0.8,
                    gid=f"{label}-{x}-Inflection-Der",
                )
        if params["show_smoothed"]:
            ax.plot(
                spectraData.peakDetector.normalised.iloc[:, 0],
                spectraData.peakDetector.normalised.iloc[:, 1],
                label=f"{label}-normal",
                gid=f"{label}-normal-Der",
            )
            ax.plot(
                spectraData.peakDetector.baselineGraph.iloc[:, 0],
                spectraData.peakDetector.baselineGraph.iloc[:, 1],
                label=f"{label}-baseline",
                gid=f"{label}-baseline-Der",
            )
            self.plottedSpectra.append((f"{label}-normal", spectraData.isToF))
            self.plottedSpectra.append((f"{label}-baseline", spectraData.isToF))

        # widths, h_eval, left_ips, right_ips = spectraData.peakDetector.widths
        # ax.hlines(h_eval, left_ips, right_ips, color='green', linewidth=1.5)

    def updateLegend(self):
        """
        ``updateLegend``
        ----------------
        Will update the legend to contain all currently plotted spectra and connect the 'pick_event'
        to each legend line to ``hideGraph``.
        """
        # Creating a legend to toggle on and off plots--------------------------------------------------------------

        legend: matplotlib.legend.DraggableLegend = self.ax.legend(
            fancybox=True, shadow=True, loc="upper right", draggable=True
        )

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
                    colour = (
                        self.spectraData.get(origLine.get_label()).graphColour
                        if self.spectraData.get(origLine.get_label())
                        else getRandomColor()
                    )
                    legLine.set_color(colour)
                    legLine.set_alpha(1.0 if origLine.get_visible() else 0.2)

                    self.legOrigLines[legLine] = origLine

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
        if self.spectraData.get(orgline_name, False):
            spectraData = self.spectraData[orgline_name]
            spectraData.isGraphHidden = not newVisible
            spectraData.hideAnnotations(self.peakLabelCheck.isChecked())
            for line in axis.lines:
                if line.get_gid() == f"pd_threshold-{orgline_name}":
                    line.set_visible(newVisible)
                    continue
                if (
                    f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-max"
                    in line.get_gid()
                ):
                    line.set_visible(newVisible)
                    continue
                if (
                    f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-min"
                    in line.get_gid()
                ):
                    line.set_visible(newVisible)
                    continue
                if spectraData.name in line.get_gid() and "Der" in line.get_gid():
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
        if self.combobox.currentIndex() == 0:
            self.toggleBtnControls(enableAll=False)
        else:
            self.toggleBtnControls(plotEnergyBtn=True, plotToFBtn=True, clearBtn=True)
        self.toggleCheckboxControls(enableAll=False)

    def toggleGridlines(
        self,
        visible: bool,
        which: Literal["major", "minor", "both"] = "major",
        axis: Literal["both", "x", "y"] = "both",
        color="#888",
    ) -> None:
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
            self.ax.tick_params(which="minor", axis="x")
            self.ax.tick_params(**self.gridSettings)
            self.ax.grid(visible=False, which="both", linewidth=1.1, color=color)

            if visible and self.ax.get_visible():
                self.ax.grid(
                    visible=visible, which=which, axis=axis, color=color, alpha=0.2
                )
            else:
                self.ax.grid(visible=visible, which="both")

            self.axPD.minorticks_on()
            self.axPD.tick_params(which="minor", axis="x")
            self.axPD.tick_params(**self.gridSettings)
            self.axPD.grid(visible=False, which="both")

            if visible and self.axPD.get_visible():
                self.axPD.grid(
                    visible=visible, which=which, axis=axis, color=color, alpha=0.2
                )
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
                        gid=f"pd_threshold-{name}",
                    )
                try:
                    if self.axPD.get_visible() and (
                        element.isMaxDrawn or element.isMinDrawn
                    ):
                        line = self.axPD.axhline(
                            y=element.threshold,
                            linestyle="--",
                            color=element.graphColour,
                            linewidth=0.5,
                            gid=f"pd_threshold-{name}",
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
            self.drawAnnotations(
                element, which="max" if self.maxTableOptionRadio.isChecked() else "min"
            )

    def onPeakTableOptionChange(self) -> None:
        which = "max" if self.maxTableOptionRadio.isChecked() else "min"
        if self.selectionName in [
            spectra.name for spectra in self.spectraData.values()
        ]:
            for spectra in self.spectraData.values():

                spectra.changePeakTableData(which)
                self.drawAnnotations(spectra=spectra, which=which)

            self.addTableData(True)
        else:
            self.displayData()

    def drawAnnotations(
        self, spectra: SpectraData, which: Literal["max", "min"] = "max"
    ) -> None:
        """
        ``drawAnnotations``
        -------------------
        Will plot each numbered annotation in the order of Integral or Peak Width.

        Args:
            - ``spectra`` (SpectraData): The data for the spectra your annotating
        """
        self.elementDataNames = []
        spectra.whichAnnotationsDrawn = which
        gid = f"annotation-{spectra.name}-{'ToF' if spectra.isToF else 'Energy'}"
        if spectra.isAnnotationsDrawn:
            for anno in spectra.annotations:
                anno.remove()
            spectra.annotations.clear()

        if spectra.maxima.size == 0 and which == "max":
            self.canvas.draw()
            return
        if spectra.minima.size == 0 and which == "min":
            self.canvas.draw()
            return

        if spectra.tableData is not None:
            spectra.orderAnnotations(which=which, byIntegral=self.orderByIntegral)

        if which == "max":
            xy = spectra.maxAnnotationOrder
        else:
            xy = spectra.minAnnotationOrder
        if spectra.distChanging:
            maxDraw = len(xy)
        else:
            maxDraw = (
                spectra.maxima.shape[0] if which == "max" else spectra.minima.shape[0]
            )
            maxDraw = spectra.maxPeaks if maxDraw > spectra.maxPeaks else maxDraw
        t1 = perf_counter()
        if len(xy) != 0:
            spectra.annotations = [
                self.ax.annotate(
                    text=f"{i}",
                    xy=xy[i],
                    xytext=xy[i],
                    xycoords="data",
                    textcoords="data",
                    va="center",
                    size=7,
                    gid=gid,
                    annotation_clip=True,
                    alpha=0.8,
                )
                for i in (range(0, maxDraw) if type(xy) is np.ndarray else xy.keys())
                if i < maxDraw
            ]

        t2 = perf_counter()
        print(f"Elapsed Time - {which} Annotations - {t2 - t1}")
        if spectra.isGraphHidden or self.peakLabelCheck.isChecked():
            for annotation in spectra.annotations:
                annotation.set_visible(False)
            spectra.isAnnotationsHidden = True
        spectra.isAnnotationsDrawn = True
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

        peakWindow = PeakWindow(self, self.windowType(), index)
        peakWindow.show()

    def importData(self, filepath: str = None) -> None:
        """
        ``importData``
        --------------
        Allows user to select a file on their computer to open and analyse.
        """

        if filepath is None:
            filename = QFileDialog.getOpenFileName(
                self, "Open file", self.dir, "*.csv *.txt *.dat"
            )
            if filename[0] == "":
                return
            filepath = filename[0]
        getName = filepath.split("/")

        name = getName[-1].split(".")[0]

        optionsWindow = QDialog(self)
        optionsWindow.setWindowTitle(name)
        mainLayout = QVBoxLayout()

        buttonBox = QDialogButtonBox()

        cancelButton = buttonBox.addButton(QDialogButtonBox.StandardButton.Cancel)
        tofButton = buttonBox.addButton(QDialogButtonBox.StandardButton.Apply)
        tofButton.setObjectName("tof")
        energyButton = buttonBox.addButton(QDialogButtonBox.StandardButton.Apply)
        energyButton.setObjectName("energy")

        tofButton.setText("ToF (us)")
        energyButton.setText("Energy (eV)")

        mainLayout.addWidget(buttonBox)
        optionsWindow.setLayout(mainLayout)

        def onClose():
            optionsWindow.close()

        cancelButton.clicked.connect(onClose)

        def onAccept(tof: bool):
            self.updateGuiData(tof, filepath, True, name)
            optionsWindow.close()

        tofButton.clicked.connect(lambda: onAccept(True))
        energyButton.clicked.connect(lambda: onAccept(False))

        optionsWindow.setModal(False)
        optionsWindow.show()

    def exportData(self):
        if len(self.spectraData) == 0:
            return

        optionsWindow = InputSpectraDialog(self, self.styleSheet())
        optionsWindow.inputForm.windowTitle = "Export Menu"

        spectras = optionsWindow.spectras
        spectras.addItems(self.spectraData.keys())

        optionsWindow.setObjectName("inputWindow")
        mainLayout = QVBoxLayout()
        inputForm = QFormLayout()

        buttonBox = QDialogButtonBox(optionsWindow)
        saveBtn = buttonBox.addButton(QDialogButtonBox.StandardButton.Apply)
        saveBtn.setText("Save")

        mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        optionsWindow.setWindowTitle("Export")
        optionsWindow.setLayout(mainLayout)

        row = QHBoxLayout()
        row.setSpacing(8)

        graphDataBox = QHBoxLayout()
        graphDataBox.setSpacing(5)
        graphDataLabel = QLabel("Graph Data")
        graphDataCheck = QCheckBox()
        graphDataCheck.setObjectName("graphCheck")

        graphDataBox.addWidget(graphDataLabel)
        graphDataBox.addWidget(graphDataCheck)

        tableDataBox = QHBoxLayout()
        tableDataBox.setSpacing(5)
        tableDataLabel = QLabel("Table Data")
        tableDataCheck = QCheckBox()
        tableDataCheck.setObjectName("tableCheck")

        tableDataBox.addWidget(tableDataLabel)
        tableDataBox.addWidget(tableDataCheck)

        limitDataBox = QHBoxLayout()
        limitDataBox.setSpacing(5)
        limitDataLabel = QLabel("Peak Limits Data")
        limitDataCheck = QCheckBox()
        limitDataCheck.setObjectName("limitCheck")

        limitDataBox.addWidget(limitDataLabel)
        limitDataBox.addWidget(limitDataCheck)

        row.addItem(graphDataBox)
        row.addItem(tableDataBox)
        row.addItem(limitDataBox)

        rowWidget = QWidget()
        rowWidget.setObjectName("row")
        rowWidget.setLayout(row)
        inputForm.addRow(rowWidget)

        mainLayout.addWidget(spectras)
        mainLayout.addLayout(inputForm)
        mainLayout.addWidget(buttonBox)

        def onAccept():
            exportDir = QFileDialog.getExistingDirectory(self, "Select Folder")
            if exportDir == "":
                return
            name = spectras.currentText()
            row = getLayoutWidgets(inputForm, QWidget)[0]
            saveGraph = row.findChild(QCheckBox, "graphCheck").isChecked()
            saveTable = row.findChild(QCheckBox, "tableCheck").isChecked()
            saveLimit = row.findChild(QCheckBox, "limitCheck").isChecked()
            spec = self.spectraData[name]
            if saveGraph:
                spec.graphData[1:].to_csv(
                    f'{exportDir}/{name.replace("ToF (us)" if spec.isToF else "Energy (eV)", "")}_graphData.csv',
                    index=False,
                    header=False,
                )
            if saveTable:
                if not spec.maxTableData[1:].empty:
                    spec.maxTableData[1:].to_csv(
                        f'{exportDir}/{name.replace("ToF (us)" if spec.isToF else "Energy (eV)", "")}_table_max.csv',
                        index=False,
                    )
                if not spec.minTableData[1:].empty:
                    spec.minTableData[1:].to_csv(
                        f'{exportDir}/{name.replace("ToF (us)" if spec.isToF else "Energy (eV)", "")}_table_min.csv',
                        index=False,
                    )

            if saveLimit:
                pd.DataFrame(spec.maxPeakLimitsX.values()).to_csv(
                    f'{exportDir}/{name.replace("ToF (us)" if spec.isToF else "Energy (eV)", "")}_peakLim_max.csv',
                    header=False,
                    index=False,
                )
                pd.DataFrame(spec.minPeakLimitsX.values()).to_csv(
                    f'{exportDir}/{name.replace("ToF (us)" if spec.isToF else "Energy (eV)", "")}_peakLim_min.csv',
                    header=False,
                    index=False,
                )

            QMessageBox.warning(self, "warning", "Save Complete")

        saveBtn.clicked.connect(onAccept)

        optionsWindow.setModal(False)
        optionsWindow.show()

    def getPeaks(self) -> None:
        """
        ``getPeaks``
        ------------
        Ask the user for which function to plot the maxima or minima of which element then calls the respective function
        on that element
        """

        mainLayout = QVBoxLayout()
        inputForm = QFormLayout()
        inputForm.setObjectName("inputForm")

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
        inputMaxPeaks.setPlaceholderText(
            str(self.spectraData[elements.currentText()].threshold)
        )
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
            inputMaxPeaks.setPlaceholderText(
                str(self.spectraData[elements.currentText()].maxPeaks)
            )
            maxCheck = self.spectraData[elements.currentText()].maxima.size != 0
            minCheck = self.spectraData[elements.currentText()].minima.size != 0

            maximaBtn.setEnabled(maxCheck)
            minimaBtn.setEnabled(minCheck)

            maximaBtn.setToolTip("" if maxCheck else "No Maximas Found")
            minimaBtn.setToolTip("" if minCheck else "No Minimas Found")

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
            self.toggleGridlines(
                self.gridCheck.isChecked(), *self.gridSettings.values()
            )
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
        if spectraData.isMinDrawn and not isMax and not spectraData.isUpdating:
            return
        if spectraData.isMaxDrawn and isMax and not spectraData.isUpdating:
            return
        if isMax:
            peaksX, peaksY = spectraData.maxima[:, 0], spectraData.maxima[:, 1]
            self.maxTableOptionRadio.setChecked(True)
            self.minTableOptionRadio.setChecked(False)

        else:
            peaksX, peaksY = spectraData.minima[:, 0], spectraData.minima[:, 1]
            self.maxTableOptionRadio.setChecked(False)
            self.minTableOptionRadio.setChecked(True)

        # ! Add element selection to Peak Detection menu
        # ! Change how points are then plotted
        # Redrawing graph and Peak Detection Limits
        self.onPeakTableOptionChange()
        self.addTableData(reset=True)
        self.ax.set_visible(False)
        if self.axPD is None:
            self.axPD = self.figure.add_subplot(111)
            if spectraData.isToF:
                self.axPD.set(
                    xlabel="Time of Flight (uS)",
                    ylabel="Cross section (b)",
                    title=spectraData.name,
                )
            else:
                self.axPD.set(
                    xlabel="Energy (eV)",
                    ylabel="Cross section (b)",
                    title=spectraData.name,
                )

            self.axPD.set_yscale("log")
            self.axPD.set_xscale("log")
            self.axPD.minorticks_on()
            plt.minorticks_on()
            self.axPD.xaxis.set_minor_locator(LogLocator(10, "all"))
            self.axPD.xaxis.set_minor_formatter(
                LogFormatterSciNotation(10, False, (np.inf, np.inf))
            )
            self.axPD.xaxis.set_tick_params("major", size=12, color="#888", labelsize=9)
            self.axPD.xaxis.set_tick_params(
                "minor",
                size=4,
                color="#888",
                labelsize=6,
                labelrotation=45,
            )

        self.toggleGridlines(self.gridCheck.isChecked(), **self.gridSettings)
        self.toggleThreshold()
        self.axPD.set_visible(True)

        label = (
            f"{spectraData.name}-ToF"
            if spectraData.isToF
            else f"{spectraData.name}-Energy"
        )
        if (
            not spectraData.isMaxDrawn and not spectraData.isMinDrawn and not spectraData.isUpdating
        ):
            self.axPD.plot(
                spectraData.graphData[0],
                spectraData.graphData[1],
                "-",
                color=spectraData.graphColour,
                alpha=0.6,
                linewidth=1.0,
                label=label,
                gid=f"{spectraData.name}-PD",
            )
        self.toggleThreshold()
        self.drawAnnotations(
            spectraData, which="max" if self.maxTableOptionRadio.isChecked() else "min"
        )

        if isMax:
            title = f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}"
            pdPoints = [
                a
                for a in self.axPD.get_lines()
                if "max" in a.get_gid() and title in a.get_gid()
            ]
            pdPointsXY = [
                (point.get_xdata()[0], point.get_ydata()[0]) for point in pdPoints
            ]
            peaks = list(zip(peaksX, peaksY))
            removeIds = []
            for point in pdPoints:
                if "max-p" not in point.get_gid():
                    continue
                xy = (point.get_xdata()[0], point.get_ydata()[0])
                if xy not in peaks and title in point.get_gid():
                    removeIds.append(point.get_gid().split("-")[-1])
            if removeIds != []:
                for point in pdPoints:
                    if point.get_gid().split("-")[-1] in removeIds:
                        point.remove()

            # Plot Maxima / minima points and its integration limits

            for i, (x, y) in enumerate(zip(peaksX, peaksY)):
                if (x, y) in pdPointsXY:
                    continue
                self.axPD.plot(
                    x,
                    y,
                    "x",
                    color="black",
                    markersize=3,
                    alpha=0.6,
                    gid=f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-max-p-{i}",
                )
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

                self.axPD.plot(
                    limitXFirst,
                    limitYFirst,
                    marker=2,
                    color="r",
                    markersize=8,
                    gid=f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-max-limL-{i}",
                )
                self.axPD.plot(
                    limitXSecond,
                    limitYSecond,
                    marker=2,
                    color="r",
                    markersize=8,
                    gid=f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-max-limR-{i}",
                )

        else:
            for i, (x, y) in enumerate(zip(peaksX, peaksY)):
                self.axPD.plot(
                    x,
                    y,
                    "x",
                    color="black",
                    markersize=3,
                    alpha=0.6,
                    gid=f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-min-p-{i}",
                )
                spectraData.isMinDrawn = True
                if spectraData.minPeakLimitsX.get(x, False):
                    limitXFirst = spectraData.minPeakLimitsX[x][0]
                    limitXSecond = spectraData.minPeakLimitsX[x][1]
                else:
                    continue
                if spectraData.minPeakLimitsY.get(x, False):
                    limitYFirst = spectraData.minPeakLimitsY[x][0]
                    limitYSecond = spectraData.minPeakLimitsY[x][1]
                else:
                    continue

                self.axPD.plot(
                    limitXFirst,
                    limitYFirst,
                    marker=2,
                    color="r",
                    markersize=8,
                    gid=f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-min-limL-{i}",
                )
                self.axPD.plot(
                    limitXSecond,
                    limitYSecond,
                    marker=2,
                    color="r",
                    markersize=8,
                    gid=f"{spectraData.name}-{'ToF' if spectraData.isToF else 'Energy'}-min-limR-{i}",
                )

        legendPD: matplotlib.legend.DraggableLegend = self.axPD.legend(
            fancybox=True, shadow=True, draggable=True
        )
        self.legOrigLinesPD = {}
        origlines = [
            line
            for line in self.axPD.get_lines()
            if not ("max" in line.get_gid() or "min" in line.get_gid())
        ]
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
        spectraData.isUpdating = False
        self.canvas.draw()

    def openPeriodicTable(self) -> None:
        self.periodicTable = QtPeriodicTable(self)
        self.periodicTable.show()


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    app.setObjectName("MainWindow")

    QtGui.QFontDatabase.addApplicationFont(
        resource_path(f"{params['dir_fonts']}RobotoMono-Thin.ttf")
    )
    QtGui.QFontDatabase.addApplicationFont(
        resource_path(f"{params['dir_fonts']}RobotoMono-Regular.ttf")
    )
    QtGui.QFontDatabase.addApplicationFont(
        resource_path(f"{params['dir_fonts']}RobotoMono-Medium.ttf")
    )

    app.setWindowIcon(QIcon(resource_path(f"{params['dir_img']}final_logo.png")))

    _ = ExplorerGUI()
    app.exec()


if __name__ == "__main__":
    main()
