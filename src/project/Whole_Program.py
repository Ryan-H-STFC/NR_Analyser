import os
import sys
import shutil
import matplotlib.rcsetup
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import OrderedDict
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
    QTableView,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget
)
from pyparsing import Generator

from ElementDataStructure import ElementData
from ExtendedTableModel import ExtendedQTableModel
from CustomSortingProxy import CustomSortingProxy

# todo -------------------- Issues/Feature TODO list --------------------
# todo - Add periodic table GUI for selection.
# todo - Maximas are broken
# todo - Matplotlib icons


# ? Should this ask for the filepath or just be require to be in the format as seen in the repository,
# ? Download the repository and run the program without altering the file structure, will save having
# ? to enter filepaths in console during start up.


# Asking for filepath where the user has saved script
# filepath is where the GUI files and the code has been saved. The source_filepath is the path to the latest data folder
# ! Maybe Change back to inputs if requried
filepath = os.path.dirname(__file__) + "\\"
#  input('Enter the filepath where the latest NRCA code data folder is \n For Example:'
#                         'C://Users/ccj88542/NRCA/Rehana/Latest/main/data: \n')

source_filepath = filepath + "data"

# print(filepath)
# print(source_filepath)

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
        """_summary_
        Initialisator for DatabaseGUI class
        """
        # Allows for adding more things to the QWidget template
        super(DatabaseGUI, self).__init__()
        self.initUI()
        self.setAcceptDrops(True)
        
        # Setting global variables
        self.data = None
        self.x = []
        self.y = []
        self.x_array = []
        self.y_array = []
        self.thresholds = None
        self.number_rows = None
        self.number_totpeaks = []

        self.ax = None
        self.ax2 = None
        self.canvas2 = None
        self.plot_filepath = None
        self.first_limit = None
        self.second_limit = None
        self.plot_count = -1
        self.graphs = OrderedDict()
        self.annotations = []
        self.local_hidden_annotations = []
        self.plotted_substances = []
        self.rows = None
        self.table_layout = dict()
        self.arrays = dict()
        self.substance = None
        self.xi = None
        self.yj = None
        self.peaknum = None
        self.interact = None
        self.clickcount = None

        self.peak_info_isNull = None
        self.graph_data = None
        self.peak_limits_x = dict()
        self.peak_limits_y = dict()
        self.peak_list = None
        self.orderByIntegral = True
        self.first_click_x = None
        self.filepath = filepath
        self.data_filepath = source_filepath
        self.element_data = dict()
        self.element_data_names = []
        self.maxPeak = 50
        self.threshold = 100

    def initUI(self) -> None:
        """
        Creates the UI.
        """
        self.setObjectName('mainWindow')
        self.setGeometry(350, 50, 1600, 900)
        self.setWindowTitle("NRTI/NRCA Viewing Database")

        main_layout = QGridLayout()

        menubar_layout = QHBoxLayout()
        sidebar_layout = QVBoxLayout()
        content_layout = QVBoxLayout()

        # * ----------------------------------------------

        # * -------------- MENU BAR - FILE ---------------
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

        # * -------------- MENU BAR - EDIT ---------------
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
        menubar_layout.addWidget(menubar, alignment=Qt.AlignLeft)
        # Adding label which shows number of peaks
        self.peaklabel = QLabel()
        self.peaklabel.setObjectName('numPeakLabel')
        self.peaklabel.setText("")
        self.peaklabel.setAlignment(Qt.AlignVCenter)

        self.peaklabel.setContentsMargins(0, 10, 0, 0)
        menubar_layout.addWidget(self.peaklabel, alignment=Qt.AlignVCenter)
        # Threshold Label
        self.threshold_label = QLabel()
        self.threshold_label.setObjectName('thresholdLabel')
        self.threshold_label.setText("Nothing has been selected")
        self.threshold_label.setAlignment(Qt.AlignRight)
        self.threshold_label.setContentsMargins(0, 10, 0, 0)

        menubar_layout.addWidget(self.threshold_label, alignment=Qt.AlignRight)

        # * ----------------------------------------------

        # * --------------- Combobox Group ---------------
        # For copying data directory to local directory for plotting later
        # Establishing source and destination directories
        source_directory = source_filepath
        destination_directory = filepath + "data/"

        # Creating a list of substances stored in the NRCA database data directory
        self.substances = [None]
        for file in os.listdir(source_directory):
            filename = os.fsdecode(file)
            filename = filename[:-4]
            self.substances.append(filename)
            source = source_directory + file
            destination = destination_directory + file
            if os.path.isfile(source):
                shutil.copy(source, destination)

        # Creating combo box (drop down menu)
        self.combobox = QComboBox()
        self.combobox.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.combobox.setObjectName("combobox")
        self.combobox.addItems(self.substances)
        self.combobox.setEditable(True)
        self.combobox.setPlaceholderText("Select substance")
        self.combobox.setInsertPolicy(QComboBox.NoInsert)
        self.combobox.setMaxVisibleItems(15)
        # filterCompleter = QCompleter(self)
        # filterCompleter.set
        self.combobox.completer().setCompletionMode(
            QCompleter.UnfilteredPopupCompletion
        )

        self.combobox.completer().setCaseSensitivity(Qt.CaseInsensitive)
        self.combobox.completer().setFilterMode(Qt.MatchContains)

        sidebar_layout.addWidget(self.combobox)
        # Upon selecting an option, it records the option
        # and connects to the method 'Select_and_Display'
        self.combobox.activated.connect(self.Select_and_Display)

        # * ----------------------------------------------

        pointing_cursor = QCursor(Qt.PointingHandCursor)

        # * ---------------- Button Group ----------------
        self.btn_layout = QVBoxLayout()

        plot_energy_btn = QPushButton("Plot in Energy", self)
        plot_energy_btn.setObjectName("plot_energy_btn")
        plot_energy_btn.setCursor(pointing_cursor)
        plot_energy_btn.__name__ = "plotEnergyBtn"
        plot_energy_btn.resize(plot_energy_btn.sizeHint())
        plot_energy_btn.setEnabled(False)
        self.btn_layout.addWidget(plot_energy_btn)
        plot_energy_btn.clicked.connect(self.Plot)

        plot_tof_btn = QPushButton("Plot in ToF", self)
        plot_tof_btn.setCursor(pointing_cursor)
        plot_tof_btn.setObjectName("plot_tof_btn")
        plot_tof_btn.__name__ = "plotToFBtn"
        plot_tof_btn.resize(plot_tof_btn.sizeHint())
        plot_tof_btn.setEnabled(False)
        self.btn_layout.addWidget(plot_tof_btn)
        plot_tof_btn.clicked.connect(self.PlotToF)

        clear_btn = QPushButton("Clear Results", self)
        clear_btn.setObjectName("clear_btn")
        clear_btn.setCursor(pointing_cursor)
        clear_btn.__name__ = "clearBtn"
        clear_btn.resize(clear_btn.sizeHint())
        clear_btn.setEnabled(False)
        self.btn_layout.addWidget(clear_btn)
        clear_btn.clicked.connect(self.Clear)

        pd_btn = QPushButton("Peak Detection", self)
        pd_btn.setObjectName("pd_btn")
        pd_btn.setCursor(pointing_cursor)
        pd_btn.__name__ = "pdBtn"
        pd_btn.resize(pd_btn.sizeHint())
        pd_btn.setEnabled(False)
        self.btn_layout.addWidget(pd_btn)
        pd_btn.clicked.connect(self.GetPeaks)

        sidebar_layout.addLayout(self.btn_layout)

        # * ----------------------------------------------

        # * --------------- Checkbox Group ---------------
        self.toggle_layout = QVBoxLayout()
        self.toggle_layout.setObjectName('toggleLayout')

        grid_check = QCheckBox("Grid Lines", self)
        grid_check.setCursor(pointing_cursor)
        grid_check.setObjectName("grid_check")
        grid_check.__name__ = "gridCheck"

        grid_check.setEnabled(False)
        self.toggle_layout.addWidget(grid_check)
        grid_check.stateChanged.connect(self.Gridlines)

        self.threshold_check = QCheckBox("Peak Detection Limits", self)
        self.threshold_check.setCursor(pointing_cursor)
        self.threshold_check.setObjectName("threshold_check")
        self.threshold_check.__name__ = "thresholdCheck"
        self.threshold_check.setEnabled(False)
        self.toggle_layout.addWidget(self.threshold_check)
        self.threshold_check.stateChanged.connect(self.Threshold)

        self.label_check = QCheckBox("Hide Peak Labels", self)
        self.label_check.setCursor(pointing_cursor)
        self.label_check.setObjectName("label_check")
        self.label_check.__name__ = "labelCheck"
        self.label_check.setEnabled(False)
        self.toggle_layout.addWidget(self.label_check)
        self.label_check.stateChanged.connect(self.ToggleAnnotations)

        sidebar_layout.addLayout(self.toggle_layout)

        # * ------------------------------------------------

        # * --------------- Peak Order Group ---------------
        peak_order_layout = QVBoxLayout()
        peak_order_layout.setSpacing(5)
        peak_check_layout = QHBoxLayout()
        peak_check_layout.setSpacing(5)
        peak_order_label = QLabel(self, text="Peak Order")
        peak_order_label.setObjectName('orderlabel')
        self.byIntegral_check = QCheckBox(self, text="By Integral")
        self.byIntegral_check.setObjectName('orderByIntegral')
        self.byIntegral_check.setChecked(True)
        self.byIntegral_check.clicked.connect(self.PeakOrderChanged)
        self.byPeakWidth_check = QCheckBox(self, text="By Peak Width")
        self.byPeakWidth_check.setObjectName('orderByPeakW')
        self.byPeakWidth_check.clicked.connect(self.PeakOrderChanged)
        peak_check_layout.addWidget(self.byIntegral_check)
        peak_check_layout.addWidget(self.byPeakWidth_check)

        peak_order_layout.addWidget(peak_order_label)
        peak_order_layout.addItem(peak_check_layout)

        sidebar_layout.addLayout(peak_order_layout)

        # * -----------------------------------------------

        # * ---------------- Plot Canvas ------------------
        self.figure = plt.figure()  # Creating canvas to plot graph on and toolbar
        self.canvas = FigureCanvas(self.figure)
        self.canvas.__name__ = "canvas"

        self.toolbar = NavigationToolbar(self.canvas, self)
        content_layout.addWidget(self.toolbar)
        content_layout.addWidget(self.canvas)
        container = QWidget(self)
        container.setObjectName('mainContainer')
        container.setLayout(content_layout)
        # * -----------------------------------------------

        # * -------------------- Table --------------------
        # Adding table to display peak information
        self.table = QTableView()
        self.table.setObjectName('dataTable')
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        content_layout.addWidget(self.table)

        sidebar_layout.setAlignment(Qt.AlignTop)

        main_layout.addItem(menubar_layout, 0, 0, 1, 2, Qt.AlignTop)
        main_layout.addItem(sidebar_layout, 1, 0, 1, 1, Qt.AlignTop)
        main_layout.addWidget(container, 1, 1)
        self.btn_layout.setSpacing(10)
        self.toggle_layout.setSpacing(10)

        sidebar_layout.setSpacing(50)
        content_layout.setStretch(0, 1)

        # If double-clicking cell, can trigger plot peak

        # self.table.cellDoubleClicked.connect(self.PlotPeakWindow)

        self.setLayout(main_layout)  # Generating layout
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
        if self.element_data == {}:
            return

        mainLayout = QVBoxLayout()
        input_formGroupBox = QGroupBox()
        input_form = QFormLayout()
        input_form.windowTitle = "Threshold Input"

        elements = QComboBox()
        elements.addItems(self.element_data.keys())

        input_threshold = QLineEdit()
        input_threshold.setPlaceholderText(str(self.element_data[elements.currentText()].threshold))
        input_threshold.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        input_form.addRow(QLabel("Substance:"), elements)
        input_form.addRow(QLabel("Threshold:"), input_threshold)
        input_formGroupBox.setLayout(input_form)
        buttonBox = QDialogButtonBox()
        buttonOk = buttonBox.addButton(QDialogButtonBox.Ok)

        mainLayout.addWidget(input_formGroupBox)
        mainLayout.addWidget(buttonBox)

        input_window = QDialog()
        input_window.setObjectName('thresholdLimit')

        input_window.setWindowTitle("Edit Threshold Value")
        input_window.setLayout(mainLayout)

        def close():
            input_window.close()
        buttonOk.clicked.connect(close)

        def changeThresholdText():
            input_threshold.setPlaceholderText(str(self.element_data[elements.currentText()].threshold))
        elements.currentTextChanged.connect(changeThresholdText)

        input_window.exec_()

        substance_name = elements.currentText()
        if input_threshold.text() == '':
            return
        threshold_value = float(input_threshold.text())

        self.element_data[substance_name].threshold = threshold_value
        self.element_data[substance_name].UpdateMaximas()
        self.Threshold()
        self.DrawAnnotations(self.element_data[substance_name])

    def editMaxPeaks(self) -> None:
        if self.element_data == {}:
            return

        mainLayout = QVBoxLayout()
        input_formGroupBox = QGroupBox()
        input_form = QFormLayout()
        input_form.windowTitle = "Threshold Input"

        elements = QComboBox()
        elements.addItems(self.element_data.keys())

        input_maxPeaks = QLineEdit()
        input_maxPeaks.setPlaceholderText(str(self.element_data[elements.currentText()].numPeaks))
        input_maxPeaks.setValidator(QRegExpValidator(QRegExp("[0-9]{0,4}")))

        input_form.addRow(QLabel("Substance:"), elements)
        input_form.addRow(QLabel("Peak Quantity:"), input_maxPeaks)
        input_formGroupBox.setLayout(input_form)
        buttonBox = QDialogButtonBox()
        okButton = buttonBox.addButton(QDialogButtonBox.Ok)

        mainLayout.addWidget(input_formGroupBox)
        mainLayout.addWidget(buttonBox)

        input_window = QDialog()
        input_window.setObjectName('maxPeaks')
        input_window.setWindowTitle("Displayed Peaks Quantity")
        input_window.setLayout(mainLayout)

        def closeWindow():
            input_window.close()
        okButton.clicked.connect(closeWindow)

        def changePeaksText():
            input_maxPeaks.setPlaceholderText(str(self.element_data[elements.currentText()].numPeaks))
        elements.currentTextChanged.connect(changePeaksText)

        input_window.exec_()

        substance_name = elements.currentText()
        if input_maxPeaks.text() == '':
            return
        maxPeaks = int(input_maxPeaks.text())
        self.element_data[substance_name].maxPeaks = maxPeaks
        self.DrawAnnotations(self.element_data[substance_name])

    def Select_and_Display(self, index) -> None:
        """
        Select_and_Display detects what has been selected and displays relevant peak information in the table.
        Once a select is made, the relevant controls are enabled.

        Args:
            index (int): Index of the selected item within the combobox.
        """
        self.data = self.combobox.itemText(index)

        if self.data == "" and self.plot_count > -1:  # Null selection and graphs shown
            self.toggleBtnControls(clearBtn=True)
            return
        elif (
            self.data == "" and self.plot_count == -1
        ):  # Null selection and no graphs shown
            self.toggleBtnControls(enableAll=False)
            self.toggleCheckboxControls(enableAll=False)
            return
        elif self.plot_count != -1:  # Named Selection and graphs shown
            self.toggleBtnControls(enableAll=True)
            self.toggleCheckboxControls(enableAll=True)
        else:  # Named selection and no graphs shown
            self.toggleBtnControls(plotEnergyBtn=True, plotToFBtn=True, clearBtn=True)
            self.toggleCheckboxControls(enableAll=False)

        # Getting symbol from substance
        split = self.data.split("-")
        if self.data.startswith("e"):
            data_symbol_sort = split[1]
            data_symbol = data_symbol_sort[:-2]
        else:
            data_symbol = split[1]
        # Finding relevant file for peak information
        peakinfo_directory = self.filepath + "GUI Files/Peak information/"
        filepath = None
        for file in os.listdir(peakinfo_directory):
            if self.data == file.split(".")[0]:
                filepath = peakinfo_directory + file
                break

        try:
            file = pd.read_csv(filepath, header=0)
            # start = time.time()
            # Reset any changes to spans before displaying selection data.
            self.table.clearSpans()
            # end = time.time()
            # print("Time elapsed : ", end-start)
            if self.data not in self.plotted_substances:
                self.number_rows = file.shape[0]
            print("Number of peaks: ", self.number_rows)
            # Fill Table with data
            self.table_model = ExtendedQTableModel(file)
            proxy = CustomSortingProxy()
            proxy.setSourceModel(self.table_model)

            self.table.setModel(proxy)
            self.table.setSortingEnabled(True)
            self.peak_info_isNull = False
            # peak_plot_energy_btn = QPushButton(self.table)      # If wanting a button to plot peak
            # peak_plot_energy_btn.setText('Plot')         # Not sure how to get cell-clicked though
            # peak_plot_energy_btn.clicked.connect(self.PlotPeak)
            # self.table.setCellWidget(row_count,10,peak_plot_energy_btn)

        except ValueError:
            QMessageBox.warning(
                self,
                "Error",
                "The peak information has not been obtained. \n Contact Rehana"
                ".Patel@stfc.ac.uk",
            )
            self.peak_info_isNull = True

        # Displaying threshold for chosen substance
        # ! ------------ Optimise Reading file ------------
        threshold_directory = self.filepath + "GUI Files/threshold_exceptions.txt"
        with open(threshold_directory, "r") as f:
            # * Optimisation for collecting data from a file,
            # * some element file have 100's or >1000 entries.
            file = f.readlines()
        self.thresholds = "100 by default"
        # Checking if the selected substance has a threshold exception
        for i in file:
            sort_limits = i.replace('\n', '').split(" ")
            symbol = sort_limits[0]
            if str(symbol) == str(data_symbol):
                self.thresholds = str(sort_limits[1]) + str(sort_limits[2])
                break
            else:
                continue

        # ! ----------------------------------------------
        # Setting label information based on threshold value
        if self.thresholds == "100 by default":
            label_info = (
                "Threshold for peak detection for n-tot mode: " + self.thresholds
            )
            self.threshold = 100
        else:
            label_info = (
                "Threshold for peak detection (n-tot mode, n-g mode): " + self.thresholds
            )
            if self.data[-1] == 't':
                self.threshold = sort_limits[1][1:-1]
            else:
                self.threshold = sort_limits[2][:-1]
        self.threshold_label.setText(str(label_info))
        # Changing the peak label text
        label_info = "Number of peaks: " + str(self.number_rows)
        self.peaklabel.setText(str(label_info))

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

        for btn in getLayoutWidgets(self.btn_layout):
            if enableAll:  # Enable All then return
                btn.setEnabled(True)
            else:  # Otherwise disable all and apply kwargs
                btn.setEnabled(False)

        if enableAll:
            return

        for btn in getLayoutWidgets(self.btn_layout):
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

        for btn in getLayoutWidgets(self.toggle_layout):
            if enableAll:  # Enable All then return
                btn.setEnabled(True)

            else:  # Otherwise disable all and apply kwargs
                btn.setEnabled(False)
                btn.setChecked(False)

        if enableAll:
            return

        for btn in getLayoutWidgets(self.toggle_layout):
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
        if (self.data, tof) in self.plotted_substances:
            QMessageBox.warning(self, "Warning", "Graph is already plotted")
            return

        # Establishing the number of peaks on the graph at one time, and their type
        if not imported and self.number_rows != 0:
            if self.data not in self.plotted_substances:
                self.number_totpeaks.append(self.number_rows)

        # ! Handle Element Creation here.

        self.plotted_substances.append((self.data, tof))
        # Handles number_totpeaks when plotting energy and tof of the same graph
        self.number_totpeaks.append(self.number_rows)

        # # Finds the mode for L0 (length) parameter
        if self.data[-1] == "t":
            length = 23.404
        else:
            length = 22.804

        end_row = [0]

        for (substance, tof) in self.plotted_substances:
            title = f"{substance}-{'ToF' if tof else 'Energy'}"
            if title in self.element_data.keys():
                if self.element_data[title].isGraphDrawn:
                    continue
            self.plot_filepath = f"{self.filepath}data\\{substance}.csv" if filepath is None else filepath
            peakinfo_directory = f"{self.filepath}GUI Files/Peak information/" if filepath is None else None

            graph_data = pd.read_csv(self.plot_filepath, header=None)
            self.graph_data = graph_data

            if tof:
                graph_data[0] = self.EnergytoTOF(graph_data[0], length=length)

            try:
                element_table_data = pd.read_csv(f"{peakinfo_directory}{substance}.csv")
            except FileNotFoundError:
                element_table_data = pd.DataFrame(
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
            if element_table_data.empty:
                element_table_data.loc[-1] = [f"No Peak Data for {substance}", *[""] * 9]
            else:
                element_table_data.loc[-1] = [substance, *[""] * 9]
            element_table_data.index += 1
            element_table_data.sort_index(inplace=True)
            colour = (np.random.random() * 0.8 + 0.1,
                      np.random.random() * 0.5 + 0.2,
                      np.random.random() * 0.8 + 0.1)
            if title not in self.element_data.keys():
                newElement = ElementData(name=substance,
                                         numPeaks=self.number_rows,
                                         tableData=element_table_data,
                                         graphData=graph_data,
                                         graphColour=colour,
                                         isToF=tof,
                                         isAnnotationsHidden=self.label_check.isChecked(),
                                         threshold=float(self.threshold),
                                         isImported=imported)
                self.element_data[title] = newElement
        # Re-setting Arrays
        self.x = []
        self.y = []
        # Establishing colours for multiple plots
        # ! Fix issue with adding more than 7 graphs.

        # # print(graph_data)

        # General Plotting ---------------------------------------------------------------------------------------------
        if self.plot_count < 0:
            self.ax = self.figure.add_subplot(111)
            # Setting scale to be logarithmic
            self.ax.set_yscale("log")
            self.ax.set_xscale("log")
        # Allows user to plot in ToF if chosen # -----------------------------------------------------------------------
        if tof and not imported:
            # ! Convert to pandas compatible

            if self.plot_count < 0:
                self.ax.set(
                    xlabel="ToF (uS)", ylabel="Cross section (b)", title=self.data
                )
        else:
            if self.plot_count < 0:
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

        spectra_line = self.ax.plot(
            graph_data.iloc[:, 0],
            graph_data.iloc[:, 1],
            "-",
            c=colour,
            alpha=0.6,
            linewidth=0.8,
            label=f"{self.data}-ToF" if newElement.isToF else f"{self.data}-Energy",
            gid=self.data,
        )
        newElement.isGraphDrawn = True

        # Creating a legend to toggle on and off plots----------------------------------------------------------------
        legend = self.ax.legend(
            fancybox=True,
            shadow=True,
        )

        # Amending dictionary of plotted lines - maps legend line to original line and allows for picking
        spectra_legend = legend.get_lines()  # Gets the 'ID' of lines ( I think)
        for i in spectra_legend:
            i.set_picker(True)
            i.set_pickradius(5)  # Makes it easier to click on legend line

        # Dictionary has legend line mapped to spectra_line but needs to be updated for multiple plots
        legend_line = spectra_legend[-1]
        self.graphs[legend_line] = spectra_line[0]

        # Updating for multiple plots
        dictionary_keys = []
        for key in self.graphs:
            dictionary_keys.append(key)
        count = 0
        for i in spectra_legend:
            self.graphs[i] = self.graphs.pop(dictionary_keys[count])
            count = count + 1
        plt.connect("pick_event", self.HideGraph)
        # ------------------------------------------------------------------------------------------------------------

        # Establishing plot count
        self.plot_count += 1
        self.canvas.draw()

        # Amending the table for more than one plot.
        self.table.reset()
        self.table.sortByColumn(-1, Qt.SortOrder.AscendingOrder)

        table_data = pd.DataFrame()
        # ! ---------------------------------------------------------------------------------
        # ? Maybe sort the order in which they are plotted and added to the table.
        for substance in self.element_data.values():
            if substance.name not in self.element_data_names:
                table_data = pd.concat([table_data, substance.tableData], ignore_index=True)
                end_row.append(end_row[-1] + substance.tableData.shape[0])
                self.element_data_names.append(substance.name)

        self.DrawAnnotations(self.element_data.get(f"{self.data}-ToF" if newElement.isToF else f"{self.data}-Energy"))
        self.Threshold()
        self.ax.autoscale()  # Tidying up

        self.figure.tight_layout()

        self.table_model = ExtendedQTableModel(table_data)
        self.table.setModel(self.table_model)
        self.table.setSortingEnabled(False)
        self.table.clearSpans()
        for row in end_row[:-1]:
            self.table.setSpan(row, 0, 1, 10)

        self.canvas.draw()

    def HideGraph(self, event) -> None:
        """
        Function to show or hide the selected graph by clicking the legend.

        Args:
            event (pick_event): event on clicking a graphs legend
        """
        # Tells you which plot number you need to delete labels for
        legline = event.artist
        orgline = self.graphs[legline]
        orgline_name = orgline._label
        # Hiding relevant line
        visible = not orgline.get_visible()
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled.
        legline.set_alpha(1.0 if visible else 0.2)
        orgline.set_visible(visible)
        # Hiding relevant labels

        self.element_data[orgline_name].isGraphHidden = not visible
        self.element_data[orgline_name].HideAnnotations(self.label_check.isChecked())
        for line in self.ax.lines:
            if line.get_gid() == f"pd_threshold-{orgline_name}":
                line.set_visible(visible)
        self.canvas.draw()

    def PlotToF(self) -> None:
        self.Plot(True)

    def EnergytoTOF(self, x_data: list[float], length: float) -> list[float]:
        """
        Maps all X Values from energy to TOF

        Args:
            x_data (list[float]): List of the substances x-coords of its graph data
            length (float): Constant value associated to whether the substance data is with repsect to n-g or n-tot

        Returns:
            list[float]: Mapped x-coords
        """
        if length is None:
            length = 22.804
        neutron_mass = float(1.68e-27)
        electron_charge = float(1.60e-19)

        tof_x = list(
            map(
                lambda x: length * 1e6 * (0.5 * neutron_mass / (x * electron_charge)) ** 0.5,
                x_data
            )
        )
        return tof_x

    def Clear(self) -> None:
        """
        Clear Function will empty all data from the table, all graphs from the plots,
        along with resetting all data associated the table or plot and disables relevent controls.
        """

        self.figure.clear()
        self.canvas.draw()
        self.x = []
        self.y = []
        self.plot_count = -1
        self.number_totpeaks = []
        self.annotations = []
        self.local_hidden_annotations = []
        self.peaklabel.setText("")
        self.threshold_label.setText("")
        self.element_data = {}
        self.element_data_names = []
        self.table.setModel(None)
        self.graphs = OrderedDict()
        self.table_layout = dict()
        self.arrays = dict()
        self.plotted_substances = []

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
            for name, substance in self.element_data.items():
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
            self.byPeakWidth_check.setChecked(not self.byPeakWidth_check.isChecked())
            self.orderByIntegral = self.byIntegral_check.isChecked()

        if self.sender().objectName() == "orderByPeakW":
            self.byIntegral_check.setChecked(not self.byIntegral_check.isChecked())
            self.orderByIntegral = self.byIntegral_check.isChecked()

        for element in self.element_data.values():
            self.DrawAnnotations(element)

    def DrawAnnotations(self, element: ElementData) -> None:
        """
        DrawAnnotations will plot each numbered annotation in the order of Integral or Peak Width

        Args:
            element (ElementData): The data for the element your annotating
        """
        self.element_data_names = []

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
                                                size=6,
                                                gid=gid,
                                                annotation_clip=True
                                                )
                               for i in range(maxDraw)]

        if element.isGraphHidden or self.label_check.isChecked():
            for annotation in element.annotations:
                annotation.set_visible(False)
            element.isAnnotationsHidden = True
        element.isAnnotationsDrawn = True
        self.canvas.draw()

    def ToggleAnnotations(self) -> None:
        """
        Function Annotations shows & hides all peak annotations globally.
        """
        for substance in self.element_data.values():
            substance.HideAnnotations(self.label_check.isChecked())
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
            for i in self.plotted_substances:
                index = self.plotted_substances.index(i)
                for j in range(0, index):
                    start_row = start_row + self.number_totpeaks[j] + 1
                end_row = (
                    start_row + self.number_totpeaks[self.plotted_substances.index(i)] + 1
                )
                peak_count = 0
                for j in range(start_row, end_row):
                    self.table_layout[j] = i + "_" + str(peak_count)
                    peak_count += 1
            # Get relevant data for peak
            substance = self.table_layout.get(row_clicked)
            # Getting Singular Peak Arrays with PlotPeak---------------------------------------------------------------
            # Getting peak limits for relevant substance
            peak_limits = []
            try:
                if self.peak_limits_x == dict():
                    filepath = self.filepath + "GUI Files/Peak_limits.txt"
                    with open(filepath, "r") as f:
                        lines = f.readlines()
                        for i in lines:
                            # should have sorting = [name, peak limit 1, peak limit 2]
                            sorting = i.split(" ")
                            if sorting[0] == substance[:-2]:
                                # Slicing the actual numbers out of the string
                                peak_limits.append(sorting[1][1:-1])
                                peak_limits.append(sorting[2][:-2])
                            else:
                                continue
                else:
                    peak_center_coord = self.table.item(row_clicked, 1).text()
                    print(self.peak_limits_x)
                    limit = str(peak_center_coord) + "_first"
                    print(limit)
                    peak_limits.append(
                        self.peak_limits_x[str(peak_center_coord) + "_first"]
                    )
                    peak_limits.append(
                        self.peak_limits_x[str(peak_center_coord) + "_second"]
                    )

            except Exception:
                QMessageBox.warning(self, "Error", "No peak limits for this substance")

            # Getting peak limits for relevant peak
            relevant_limits_index = int(self.substance[-1]) * 2 - 2
            self.first_limit = peak_limits[relevant_limits_index]
            self.second_limit = peak_limits[(relevant_limits_index + 1)]

            # Getting the right arrays to plot the graph
            x = self.arrays.get(substance[:-2] + "x")
            y = self.arrays.get(substance[:-2] + "y")

            # Truncating array to just before and after peak limits
            index_first_limit = x.index(float(self.first_limit))
            index_second_limit = x.index(float(self.second_limit))
            self.x_array = x[int(index_first_limit - 10): int(index_second_limit + 10)]
            self.y_array = y[int(index_first_limit - 10): int(index_second_limit + 10)]

            # ---------------------------------------------------------------------------------------------------------
            # Plotting
            # Getting user to choose scale
            scale_list = ["linear", "log"]
            scale, ok = QInputDialog.getText(
                peakwindow, "Scale", 'Enter Scale as "linear" or "log" : '
            )
            if ok:
                print(scale)
                if scale not in scale_list:
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
            self.ax2.plot(self.x_array, self.y_array, ".")
            self.ax2.autoscale()
            titlename = self.data + "- Peak: " + str(int(substance[-1]))
            self.ax2.set(
                xlabel="Energy (eV)", ylabel="Cross section (b)", title=titlename
            )

            # Filling in the peak info table information----------------------------------------------------------------
            rank = self.table.item(row_clicked, 0)
            limits = "(" + str(self.first_limit) + "," + str(self.second_limit) + ")"
            peak_center_coord = self.table.item(row_clicked, 1)
            isotopic_origin = self.table.item(row_clicked, 9)

            # Setting in table
            peak_table.setItem(0, 0, QTableWidgetItem(rank))
            peak_table.setItem(0, 1, QTableWidgetItem(limits))
            peak_table.setItem(0, 2, QTableWidgetItem(peak_center_coord))
            peak_table.setItem(0, 3, QTableWidgetItem(isotopic_origin))
            peak_table.resizeRowsToContents()

            # Setting label text
            label_info = "Selected Scale: " + scale
            scale_label.setText(label_info)

            peakwindow.show()
        except Exception:
            QMessageBox.warning(
                self, "Error", "You need to plot the graph first or select a valid row"
            )

    def PeakLimits(self, checked) -> None:
        try:
            if checked:
                # Plotting threshold lines ----------------------------------------------------------------------------
                number_datappoints = len(self.x_array)
                threshold1_x = [(float(self.first_limit))] * number_datappoints
                max_value_in_y = max(self.y_array)
                min_value_in_y = min(self.y_array)
                threshold1_y = np.linspace(
                    min_value_in_y, max_value_in_y, number_datappoints
                )
                threshold2_x = [(float(self.second_limit))] * number_datappoints
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
                data_symbol = symbol_sorting[1]
                threshold_directory = (
                    self.filepath + "GUI Files/threshold_exceptions.txt"
                )
                with open(threshold_directory, "r") as f:
                    file = f.readlines()
                self.thresholds = "100 by default"
                # Checking if the selected substance has a threshold exception
                for i in file:
                    sort_limits = i.split(" ")
                    symbol = sort_limits[0]
                    if str(symbol) == str(data_symbol):
                        self.thresholds = str(sort_limits[1]) + str(sort_limits[2])
                # Plotting ---------------------------------------------------------------------------------------------
                number_data_points = len(self.x_array)
                threshold_sorting = self.thresholds.split(",")
                if self.thresholds == "100 by default":
                    threshold_coord_y = 100
                elif self.data[-1] == "t":
                    # sort_limits is set earlier in SelectandDisplay
                    threshold_coord_y_sort = len(threshold_sorting[0])
                    threshold_coord_y = float(
                        threshold_sorting[0][1:threshold_coord_y_sort]
                    )
                    print("n-tot mode")
                else:
                    # sort_limits is set earlier in SelectandDisplay
                    threshold_coord_y_sort = len(threshold_sorting[1])
                    # To splice the number from the string correctly regardless of magnitude
                    cutoff = threshold_coord_y_sort - 2
                    threshold_coord_y = float(threshold_sorting[1][0:cutoff])
                    print("n-g mode")
                # Creating an array to plot line of coords
                threshold_coords_y = [float(threshold_coord_y)] * number_data_points
                threshold_coords_x = self.x_array
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
        file_name = QFileDialog.getOpenFileName(self, "Open file", self.filepath)
        if file_name[0] == '':
            return
        filepath = file_name[0]
        get_name = filepath.split("/")

        name = get_name[-1].split('.')[0]

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
        input_form = QFormLayout()
        input_form.setObjectName('inputForm')

        elements = QComboBox()
        elements.addItems(self.element_data.keys())
        elements.setMaxVisibleItems(5)

        input_maxPeaks = QLineEdit()
        input_maxPeaks.setPlaceholderText(str(self.element_data[elements.currentText()].threshold))
        input_maxPeaks.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        input_form.addRow(QLabel("Substance:"), elements)
        buttonBox = QDialogButtonBox()
        buttonR = buttonBox.addButton(QDialogButtonBox.Reset)
        buttonR.setText("Reset")
        buttonY = buttonBox.addButton(QDialogButtonBox.Yes)
        buttonY.setText("Maxima")
        buttonN = buttonBox.addButton(QDialogButtonBox.No)
        buttonN.setText("Minima")
        buttonCancel = buttonBox.addButton(QDialogButtonBox.Cancel)
        buttonCancel.setText("Cancel")
        input_form.setSpacing(5)
        mainLayout.addItem(input_form)
        mainLayout.addWidget(buttonBox)

        input_window = QDialog(self)
        input_window.setModal(True)

        input_window.setWindowTitle("What Should I Plot?")
        input_window.setLayout(mainLayout)

        def max():
            self.PlottingPD(self.element_data[elements.currentText()], True)
        buttonY.clicked.connect(max)

        def min():
            self.PlottingPD(self.element_data[elements.currentText()], False)
        buttonN.clicked.connect(min)

        def close():
            input_window.close()
        buttonCancel.clicked.connect(close)

        def changePeaksText():
            input_maxPeaks.setPlaceholderText(str(self.element_data[elements.currentText()].maxPeaks))
        elements.currentTextChanged.connect(changePeaksText)

        input_window.show()

        def ResetPDPlots() -> None:
            try:
                if self.ax2 is not None:
                    self.ax2.set_visible(False)
                    self.ax2 = None
                self.ax.set_visible(True)
                for element in self.element_data.values():
                    element.isMaxDrawn = False
                    element.isMinDrawn = False
            except KeyError:
                return
        buttonR.clicked.connect(ResetPDPlots)

    def PlottingPD(self, element_data: ElementData, isMax: bool) -> None:

        if isMax and element_data.isMaxDrawn:
            return
        if not isMax and element_data.isMinDrawn:
            return

        if isMax:
            peaks_x, peaks_y = element_data.maxima[0], element_data.maxima[1]

        else:
            peaks_x, peaks_y = element_data.minima[0], element_data.minima[1]

        # ! Add substance selection to Peak Detection menu
        # ! Change how points are then plotted
        # Redrawing graph and Peak Detection Limits
        self.ax.set_visible(False)

        if self.ax2 is None:
            self.ax2 = self.figure.add_subplot(111)

        if not element_data.isMaxDrawn and not element_data.isMinDrawn:
            self.ax2.plot(
                element_data.graphData[0],
                element_data.graphData[1],
                "-",
                color=element_data.graphColour,
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
            for x, y in zip(peaks_x, peaks_y):
                self.ax2.plot(x, y, "x", color="black", markersize=4)
                limit_x_first = element_data.max_peak_limits_x[str(x) + "_first"]
                limit_y_first = element_data.max_peak_limits_y[str(x) + "_first"]
                limit_x_second = element_data.max_peak_limits_x[str(x) + "_second"]
                limit_y_second = element_data.max_peak_limits_y[str(x) + "_second"]
                self.ax2.plot(limit_x_first, limit_y_first, marker=2, color="r", markersize=8)
                self.ax2.plot(limit_x_second, limit_y_second, marker=2, color="r", markersize=8)
                element_data.isMaxDrawn = True
        else:
            for x, y in zip(peaks_x, peaks_y):
                self.ax2.plot(x, y, "x", color="black")
                element_data.isMinDrawn = True

                # limit_x_first = element_data.min_peak_limits_x[str(x) + "_first"]
                # limit_y_first = element_data.min_peak_limits_y[str(x) + "_first"]
                # limit_x_second = element_data.min_peak_limits_x[str(x) + "_second"]
                # limit_y_second = element_data.min_peak_limits_y[str(x) + "_second"]
                # self.ax2.plot(limit_x_first, limit_y_first, 0, color="r", markersize=8)
                # self.ax2.plot(limit_x_second, limit_y_second, 0, color="r", markersize=8)
        self.figure.tight_layout()
        self.canvas.draw()

    def EditPeaks(self) -> None:
        # Click count to disconnect after two limits have been selected
        if self.plotted_substances == []:
            QMessageBox.warning(self, "Error", "You have not plotted anything")
            return

        mainLayout = QVBoxLayout()
        input_form = QFormLayout()
        input_form.setObjectName('inputForm')

        elements = QComboBox()
        elements.addItems(self.element_data.keys())
        element_peaks = QComboBox()
        element_peaks.setMaxVisibleItems(5)

        first_limit_x = QLineEdit()
        first_limit_x.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        second_limit_x = QLineEdit()
        second_limit_x.setValidator(QRegExpValidator(QRegExp("[+-]?([0-9]*[.])?[0-9]+")))

        input_form.addRow(QLabel("Substance:"), elements)
        input_form.addRow(QLabel("Peak X-Coord:"), element_peaks)
        input_form.addRow(QLabel("1st Limit X:"), first_limit_x)
        input_form.addRow(QLabel("2nd Limit X:"), second_limit_x)

        buttonBox = QDialogButtonBox()
        buttonY = buttonBox.addButton(QDialogButtonBox.Yes)
        buttonY.setText("Apply")

        buttonCancel = buttonBox.addButton(QDialogButtonBox.Cancel)
        buttonCancel.setText("Cancel")

        input_form.setSpacing(5)
        mainLayout.addItem(input_form)
        mainLayout.addWidget(buttonBox)

        input_window = QDialog(self)
        input_window.setObjectName('editPeaks')

        input_window.setModal(True)
        input_window.setWindowTitle("Edit Peaks for Substance")
        input_window.setLayout(mainLayout)

        buttonY.clicked.connect(input_window.accept)
        buttonCancel.clicked.connect(input_window.reject)

        def onElementChange():
            element = self.element_data[elements.currentText()]
            element_peaks.currentIndexChanged.disconnect(onPeakChange)
            element_peaks.clear()
            if element.maxima[0].size == 0:
                element_peaks.setEnabled(False)
                first_limit_x.setEnabled(False)
                second_limit_x.setEnabled(False)
                element_peaks.addItem("Null")
                first_limit_x.setPlaceholderText("Null")
                second_limit_x.setPlaceholderText("Null")
                element_peaks.currentIndexChanged.connect(onPeakChange)
                return
            element_peaks.setEnabled(True)
            first_limit_x.setEnabled(True)
            second_limit_x.setEnabled(True)
            element_peaks.addItems([str(peak) for peak in element.maxima[0]])               
            element_peaks.currentIndexChanged.connect(onPeakChange)
            onPeakChange()

        def onPeakChange():
            element = self.element_data[elements.currentText()]

            peak = element_peaks.currentText()
            first_limit_x.setPlaceholderText(str(element.max_peak_limits_x[f"{peak}_first"]))
            second_limit_x.setPlaceholderText(str(element.max_peak_limits_x[f"{peak}_second"]))

        elements.currentIndexChanged.connect(onElementChange)
        element_peaks.currentIndexChanged.connect(onPeakChange)
        onElementChange()
        input_window.show()

        # ? self.clickcount = 0
        # ? # Ordering peaks
        # ? peak_order = "Rank by eV    (eV) \n"
        # ? for i in range(0, len(self.peak_list)):
        # ?     peak_order += str(i) + "    " + str(self.peak_list[i]) + "\n"
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
        # ?     first_limit_x, ok = QInputDialog.getText(
        # ?         self, "Peak Limits in X", "Enter the first peak limit x-coordinate: "
        # ?     )
        # ?     second_limit_x, ok = QInputDialog.getText(
        # ?         self, "Peak Limits in X", "Enter the second peak limit x-coordinate: "
        # ?     )
        # ?     # Finding the corresponding y-value
        # ?     first_limit_y = self.y[self.x.index(first_limit_x)]
        # ?     second_limit_y = self.y[self.x.index(second_limit_x)]
        # ?     peak = self.peak_list[int(self.peaknum)]
        # ?     self.peak_limits_x[str(peak) + "_first"] = float(first_limit_x)
        # ?     self.peak_limits_x[str(peak) + "_second"] = float(second_limit_x)
        # ?     self.peak_limits_y[str(peak) + "_first"] = float(first_limit_y)
        # ?     self.peak_limits_y[str(peak) + "_second"] = float(second_limit_y)
        # ?     print("LIMITS: ", self.peak_limits_x)
        # ?     # Re-plotting with new limits
        # ?     # getting list of minima/maxima for plotting again
        # ?     maxima_x = []
        # ?     maxima_y = []
        # ?     for i in self.peak_limits_x.keys():
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
        # peak = self.peak_list[int(self.peaknum)]
        # first_limit_i = self.x.index(self.peak_limits_x[str(peak) + '_first'])
        # second_limit_i = self.x.index(self.peak_limits_x[str(peak) + '_second'])
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
        if self.plotted_substances == []:
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
        peak = self.peak_list[int(self.peaknum)]
        if self.clickcount == 1:
            self.first_click_x = self.xi
        if self.clickcount == 2:
            second_click_x = self.xi
            first_limit_x = self.nearestnumber(
                self.x, float(self.first_click_x)
            )  # Finding the nearest x-value on the spectrum to where was clicked
            second_limit_x = self.nearestnumber(self.x, float(second_click_x))
            # Finding the corresponding y-value
            first_limit_y = self.y[self.x.index(first_limit_x)]
            second_limit_y = self.y[self.x.index(second_limit_x)]
            # Altering it in dictionary
            self.peak_limits_x[str(peak) + "_first"] = first_limit_x
            self.peak_limits_x[str(peak) + "_second"] = second_limit_x
            self.peak_limits_y[str(peak) + "_first"] = first_limit_y
            self.peak_limits_y[str(peak) + "_second"] = second_limit_y
            print("LIMITS: ", self.peak_limits_x)
            # Re-plotting with new limits
            # getting list of minima/maxima for plotting again
            maxima_x = []
            maxima_y = []
            for i in self.peak_limits_x.keys():
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


def nearestnumber(x: list[float], target: float) -> float:
    """
    Find the closet value in a list the the input target value

    Args:
        x (list[float]): List of x-coords being plotted
        target (float): Value of mouse x-coord

    Returns:
        float: Nearest value in x from target
    """
    array = np.asarray(x)
    value_index = (
        np.abs(array - target)
    ).argmin()  # Finds the absolute difference between the value and the target
    # then gives the smallest number in the array and returns it
    return array[value_index]


def getLayoutWidgets(layout) -> Generator[QWidget, None, None]:
    """
    getLayoutWidgets returns a list of widgets from an inputted layout.

    Args:
        layout (PyQt Layout): PyQt Layout Object

    Returns:
        List:QtWidgets: List of widgets within the layout.
    """
    return (layout.itemAt(i).widget() for i in range(layout.count()))


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
        QLabel#numPeakLabel, #thresholdLabel, #orderlabel{
            font: 10pt 'Roboto Mono';
            color: #FFF;
        }

        QPushButton#plot_energy_btn, #plot_tof_btn, #clear_btn, #pd_btn {
            font: 10pt 'Roboto Mono Medium';
            font-weight: 500;
        }
        QPushButton#plot_energy_btn:disabled, #plot_tof_btn:disabled, #clear_btn:disabled, #pd_btn:disabled {
            color: #AAA;
        }
        QPushButton#plot_energy_btn:enabled, #plot_tof_btn:enabled, #clear_btn:enabled, #pd_btn:enabled {
            color: #000;
        }

        QCheckBox#grid_check, #threshold_check, #label_check, #orderByIntegral, #orderByPeakW {
            font-weight: 500;
        }
        QCheckBox#grid_check::indicator:unchecked,
                 #threshold_check::indicator:unchecked,
                 #label_check::indicator:unchecked,
                 #orderByIntegral::indicator:unchecked,
                 #orderByPeakW::indicator:unchecked {
            image: url(./src/img/checkbox-component-unchecked.svg);
            color: #FFF
        }
        QCheckBox#grid_check::indicator:checked,
                 #threshold_check::indicator:checked,
                 #label_check::indicator:checked,
                 #orderByIntegral::indicator:checked,
                #orderByPeakW::indicator:checked{
            image: url(./src/img/checkbox-component-checked.svg);
            color: #FFF
        }
        QCheckBox#grid_check:disabled,
                 #threshold_check:disabled,
                 #label_check:disabled,
                 #orderByIntegral:disabled,
                 #orderByPeakW:disabled
        {
            color: #888;
        }
        QCheckBox#grid_check:enabled,
                 #threshold_check:enabled,
                 #label_check:enabled,
                 #orderByIntegral:enabled,
                 #orderByPeakW:enabled{
            color: #FFF;
        }
        QWidget#mainContainer {
            border: 1px solid #4D4D4D;
            padding: 0;
            background: white;

        }
        QHeaderView {
            font-size: 7.5pt;
        }
        QTableView#dataTable {
            font-size: 8pt;
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
