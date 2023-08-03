# Importing packages and modules to use
import os
import sys
import shutil
import matplotlib.rcsetup
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as sp
from collections import OrderedDict
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas  # Import class from module as FigureCanvas for simplicity
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar  # ""
from PyQt5 import QtGui, QtWidgets  # importing classes from PyQt
from PyQt5.QtCore import Qt, QModelIndex
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QPushButton,
    QCheckBox,
    QComboBox,
    QTableWidget,
    QAction,
    QMenuBar,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QInputDialog,
    QFileDialog,
    QTableWidgetItem,
    QMainWindow,
    QWidget,
    QDockWidget,
    QCompleter,
    QTableView
)

from ExtendedTableModel import ExtendedQTableModel
from PeakDetection import PeakDetection


import time


# todo -------------------- Issues/Feature TODO list --------------------
# todo - Add periodic table GUI for selection.


# ? Should this ask for the filepath or just be require to be in the format as seen in the repository,
# ? Download the repository and run the program without altering the file structure, will save having
# ? to enter filepaths in console during start up.


# Asking for filepath where the user has saved script
# filepath is where the GUI files and the code has been saved. The source_filepath is the path to the latest data folder.
# ! Maybe Change back to inputs if requried
filepath = os.path.dirname(__file__) + "\\"
#  input('Enter the filepath where the latest NRCA code data folder is \n For Example:'
#                         'C://Users/ccj88542/NRCA/Rehana/Latest/main/data: \n')

source_filepath = filepath + "data"

# print(filepath)
# print(source_filepath)

matplotlib.rcParamsDefault['path.simplify'] = False


class DatabaseGUI(QWidget):  # Acts just like QWidget class (like a template)
    """
    Class responsible for creating the GUI used in selecting and graphing the data of numerous isotopes
    within the NRTI/NRCA Database.
    """

    # Establishing signals that will be used later on

    # init constructure for classes
    def __init__(self):
        super(DatabaseGUI, self).__init__()
        """_summary_
        Initialisator for DatabaseGUI class
        """

        # Allows for adding more things to the QWidget template
        super(DatabaseGUI, self).__init__()
        self.initUI()

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
        self.plotted_substances = []
        self.plotted_substances_tof = []
        self.rows = None
        self.table_layout = dict()
        self.arrays = dict()
        self.substance = None
        self.xi = None
        self.yj = None
        self.peaknum = None
        self.interact = None
        self.clickcount = None

        self.hidden_annotations = []
        self.peak_info_isNull = None
        self.graph_data = None
        self.peak_limits_x = dict()
        self.peak_limits_y = dict()
        self.peak_list = None
        self.first_click_x = None
        self.filepath = filepath
        self.data_filepath = source_filepath

    def initUI(self):
        # setting size of GUI and titles etc (Coordinates and size here)
        self.setGeometry(350, 50, 1200, 800)
        self.setWindowTitle('NRTI/NRCA Viewing Database')

        # creates vbox layout so as to arrange things without manually moving
        self.layout = QVBoxLayout()

        self.figure = plt.figure()  # Creating canvas to plot graph on and toolbar
        self.canvas = FigureCanvas(self.figure)

        # Creating actions for file menu
        newAction = QAction('&New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.Clear)

        importAction = QAction('&Import Data', self)
        importAction.setShortcut('Ctrl+I')

        importAction.triggered.connect(self.importdata)

        editpeakAction = QAction('&Edit Peak Limits', self)
        editpeakAction.setShortcut('Ctrl+E')
        editpeakAction.triggered.connect(self.EditPeaks)

        selectlimitsAction = QAction('&Select Limits', self)
        selectlimitsAction.setShortcut('Ctrl+L')
        selectlimitsAction.triggered.connect(self.SelectLimitsOption)

        # Creates menu bar and add actions
        menubar = QMenuBar(self)
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(newAction)
        fileMenu.addAction(importAction)
        # fileMenu.addAction(saveAction)

        editMenu = menubar.addMenu('&Edit')
        editMenu.addAction(editpeakAction)
        editMenu.addAction(selectlimitsAction)

        # helpMenu = menubar.addMenu('&Help')
        # helpMenu.addAction(aboutAction)
        self.layout.addWidget(menubar)  # adds to layout

        # Creating and adding toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar)
        # Adding label which shows number of peaks
        self.peaklabel = QLabel()
        self.peaklabel.setText('')
        self.peaklabel.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.peaklabel)
        # Adding canvas
        self.layout.addWidget(self.canvas)

        # For copying data directory to local directory for plotting later
        # Establishing source and destination directories
        source_directory = source_filepath
        destination_directory = filepath + 'data/'

        # Adding drop down menu in which users
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
        self.combobox.setStyleSheet("""
            QComboBox {
                combobox-popup: 0;
            }
        """)

        self.combobox.addItems(self.substances)

        self.combobox.setEditable(True)
        self.combobox.setInsertPolicy(QComboBox.NoInsert)
        self.combobox.setMaxVisibleItems(15)
        # filterCompleter = QCompleter(self)
        # filterCompleter.set
        self.combobox.completer().setCompletionMode(
            QCompleter.UnfilteredPopupCompletion)

        self.combobox.completer().setCaseSensitivity(Qt.CaseInsensitive)
        self.combobox.completer().setFilterMode(Qt.MatchContains)
        self.layout.addWidget(self.combobox)
        # Upon selecting an option, it records the option
        # and connects to the method 'Select_and_Display'
        self.combobox.activated.connect(self.Select_and_Display)

        # Creating a layout for checkboxes
        self.toggle_layout = QHBoxLayout()

        # Adding checkbox to toggle on and off gridlines for plots
        grid_check = QCheckBox('Grid Lines', self)
        grid_check.setStyleSheet("""
            QCheckbox::hover {
                cursor: pointer;
            }
        """)
        grid_check.__name__ = "gridCheck"
        grid_check.resize(grid_check.sizeHint())
        grid_check.setEnabled(False)
        self.toggle_layout.addWidget(grid_check)
        grid_check.stateChanged.connect(self.Gridlines)

        # Adding checkbox to toggle on and off threshold lines for plots
        self.threshold_check = QCheckBox('Peak Detection Limits', self)
        self.threshold_check.setCursor(QCursor(Qt.PointingHandCursor))
        self.threshold_check.__name__ = "thresholdCheck"
        self.threshold_check.resize(self.threshold_check.sizeHint())
        self.threshold_check.setEnabled(False)
        self.toggle_layout.addWidget(self.threshold_check)
        self.threshold_check.stateChanged.connect(self.Threshold)

        # Adding checkbox to toggle on and off annotations
        self.label_check = QCheckBox('Hide Peak Labels', self)
        self.label_check.setCursor(QCursor(Qt.PointingHandCursor))
        self.label_check.__name__ = "labelCheck"
        self.label_check.resize(self.label_check.sizeHint())
        self.label_check.setEnabled(False)
        self.toggle_layout.addWidget(self.label_check)
        self.label_check.stateChanged.connect(self.Annotations)

        # Adding to overall layout
        self.layout.addLayout(self.toggle_layout)

        # Button layout
        self.btn_layout = QHBoxLayout()

        # Creating a plot in eV (no conversion needed) button
        plot_energy_btn = QPushButton('Plot in Energy', self)
        plot_energy_btn.setCursor(QCursor(Qt.PointingHandCursor))
        plot_energy_btn.__name__ = "plotEnergyBtn"
        plot_energy_btn.resize(plot_energy_btn.sizeHint())
        plot_energy_btn.setEnabled(False)
        self.btn_layout.addWidget(plot_energy_btn)
        plot_energy_btn.clicked.connect(self.Plot)

        # Creating a plot in tof button
        plot_tof_btn = QPushButton('Plot in ToF', self)
        plot_tof_btn.setCursor(QCursor(Qt.PointingHandCursor))
        plot_tof_btn.__name__ = "plotToFBtn"
        plot_tof_btn.resize(plot_tof_btn.sizeHint())
        plot_tof_btn.setEnabled(False)
        self.btn_layout.addWidget(plot_tof_btn)
        plot_tof_btn.clicked.connect(self.PlotToF)

        # Creating a clear result button
        clear_btn = QPushButton('Clear Results', self)
        clear_btn.setCursor(QCursor(Qt.PointingHandCursor))
        clear_btn.__name__ = "clearBtn"
        clear_btn.resize(clear_btn.sizeHint())
        clear_btn.setEnabled(False)
        self.btn_layout.addWidget(clear_btn)
        clear_btn.clicked.connect(self.Clear)

        # Peak detection button
        pd_btn = QPushButton('Peak Detection', self)
        pd_btn.setCursor(QCursor(Qt.PointingHandCursor))
        pd_btn.__name__ = "pdBtn"
        pd_btn.resize(pd_btn.sizeHint())
        pd_btn.setEnabled(False)
        self.btn_layout.addWidget(pd_btn)
        pd_btn.clicked.connect(self.PeakDetection)

        # Adding sub-layout
        self.layout.addLayout(self.btn_layout)

        # Adding table to display peak information
        self.table = QTableView()
        self.table.horizontalHeader()
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        # self.table.horizontalHeader().setSectionResizeMode(QtGui.Stretch)

        # self.table.horizontalHeader().stretchLastSection(True)

        # self.table.setStyleSheet("""
        #     QTableWidget::item[] {
        #         border-left: 1px solid gray;
        #         alternate-background-color:rgba(200, 0, 200, 100)
        #     }
        # """)

        # Allow sorting by column if clicked

        # # Making the table fill the space available
        # header = self.table.horizontalHeader()
        # header.setStretchLastSection(True)
        self.layout.addWidget(self.table)

        # If double-clicking cell, can trigger plot peak
        # self.table.cellDoubleClicked.connect(self.PlotPeakWindow)

        # Threshold Label
        self.threshold_label = QLabel()
        self.threshold_label.setText('Nothing has been selected')
        self.threshold_label.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.threshold_label)

        self.setLayout(self.layout)  # Generating layout
        self.show()

    # Detects what has been selected and displays relevant peak information
    def Select_and_Display(self, index):
        self.data = self.combobox.itemText(index)

        if self.data == '' and self.plot_count > -1:  # Null selection and graphs shown
            self.toggleBtnControls(clearBtn=True)
            return
        elif self.data == '' and self.plot_count == -1:  # Null selection and no graphs shown
            self.toggleBtnControls(enableAll=False)
            self.toggleCheckboxControls(enableAll=False)
            return
        elif self.plot_count != -1:  # Named Selection and graphs shown
            self.toggleBtnControls(enableAll=True)
            self.toggleCheckboxControls(enableAll=True)
        else:   # Named selection and no graphs shown
            self.toggleBtnControls(
                plotEnergyBtn=True, plotToFBtn=True, clearBtn=True)
            self.toggleCheckboxControls(enableAll=False)

        # Getting symbol from substance
        split = self.data.split('-')
        if self.data.startswith('e'):
            data_symbol_sort = split[1]
            data_symbol = data_symbol_sort[:-2]
        else:
            data_symbol = split[1]
        # Finding relevant file for peak information
        peakinfo_directory = self.filepath + 'GUI Files/Peak information/'
        for file in os.listdir(peakinfo_directory):
            if self.data == file.split('.')[0]:
                filepath = peakinfo_directory + file
                break
            else:
                message = 'Sorry, not currently in our peak information database'

        try:

            # start = time.time()
            file = pd.read_csv(filepath, header=0)
            # Reset any changes to spans before displaying selection data.
            self.table.clearSpans()
            # end = time.time()
            # print("Time elapsed : ", end-start)
            if not self.data in self.plotted_substances:
                self.number_rows = file.shape[0]
            print('Number of peaks: ', self.number_rows)
            # Fill Table with data
            self.table_model = ExtendedQTableModel(file)
            self.table.setModel(self.table_model)
            self.peak_info_isNull = False
            # peak_plot_energy_btn = QPushButton(self.table)      # If wanting a button to plot peak
            # peak_plot_energy_btn.setText('Plot')                          # Not sure how to get cell-clicked though
            # peak_plot_energy_btn.clicked.connect(self.PlotPeak)
            # self.table.setCellWidget(row_count,10,peak_plot_energy_btn)

        except:
            QMessageBox.warning(self, 'Error', 'The peak information has not been obtained. \n Contact Rehana'
                                '.Patel@stfc.ac.uk')
            self.peak_info_isNull = True

        # Displaying threshold for chosen substance
        #! ------------ Optimise Reading file ------------
        threshold_directory = self.filepath + 'GUI Files/threshold_exceptions.txt'
        with open(threshold_directory, 'r') as f:
            # * Optimisation for collecting data from a file, some element file have 100's or > 1000 entries.
            file = f.readlines()
        self.thresholds = '100 by default'
        # Checking if the selected substance has a threshold exception
        for i in file:
            sort_limits = i.split(' ')
            symbol = sort_limits[0]
            if str(symbol) == str(data_symbol):
                self.thresholds = str(sort_limits[1]) + str(sort_limits[2])
                break
            else:
                continue

        #! ----------------------------------------------
        # Setting label information based on threshold value
        if self.thresholds == '100 by default':
            label_info = 'Threshold for peak detection for n-tot mode: ' + self.thresholds
        else:
            label_info = 'Threshold for peak detection (n-tot mode, n-g mode): ' + \
                self.thresholds
        self.threshold_label.setText(str(label_info))
        # Changing the peak label text
        label_info = 'Number of peaks: ' + str(self.number_rows)
        self.peaklabel.setText(str(label_info))

    def toggleBtnControls(self, enableAll: bool = False, plotEnergyBtn: bool = False,
                          plotToFBtn: bool = False, clearBtn: bool = False, pdBtn: bool = False):
        """_summary_
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
                               peakLimit: bool = False, hidePeakLabels: bool = False):
        """_summary_
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

    def Plot(self, tof=False, filepath=None, imported=False, name=None):
        """_summary_
            Plots graphs both by energy and time of flight(tof), and fills the table
            with the appropriate data.
        Args:
            tof (bool, optional): Whether to graph for tof or not. Defaults to False. 
            filepath (_type_, optional): Filepath for the selection to graph . Defaults to None.
            imported (bool, optional): Whether or not the selection is from and imported source. Defaults to False.
            name (_type_, optional): The name of the imported selection. Defaults to None.
        """
        # Enable Checkboxes on plotting graphs
        self.toggleCheckboxControls(enableAll=True)
        self.toggleBtnControls(enableAll=True)
        if self.data == None:
            QMessageBox.warning(
                self, 'Error', 'You have not selected anything to plot')
            return
        if imported:
            self.data = name

        # Checks for adding mutliple graphs for the same selection, energy/tof types.
        if not tof and self.data in self.plotted_substances:
            QMessageBox.warning(self, 'Warning', 'Graph is already plotted')
            return
        elif tof and self.data in self.plotted_substances_tof:
            QMessageBox.warning(self, 'Warning', 'Graph is already plotted')
            return

        # Establishing the number of peaks on the graph at any one time and which are due to which plot
        if not imported and self.number_rows != 0:
            if not self.data in self.plotted_substances:
                self.number_totpeaks.append(self.number_rows)

        if tof:
            self.plotted_substances_tof.append(self.data)
        else:
            self.plotted_substances.append(self.data)

        # Re-setting Arrays
        self.x = []
        self.y = []
        # Establishing colours for multiple plots
        # ! Fix issue with adding more than 7 graphs.
        colours = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

        # # print(graph_data)

        # # Getting relevant data file
        # for i in temporary:
        #     # Extracting the raw data from the file without the accompanying info
        #     if i[0] == '1' and i[1] == '.':
        #         start_index = temporary.index(i)
        #         break
        #     else:
        #         continue
        # for i in range(0, start_index):
        #     del temporary[0]
        # for i in temporary:
        #     data = i
        #     sorting = data.split(' ')
        #     self.x.append(sorting[0])
        #     fix_y = sorting[1]
        #     self.y.append(fix_y)
        # self.x = [float(a) for a in self.x]
        # self.y = [float(a) for a in self.y]
        # # Adding to array dictionary for peak plotting later
        # self.arrays[self.data + 'x'] = self.x
        # self.arrays[self.data + 'y'] = self.y

        self.plot_filepath = self.filepath + "data\\" + self.data + ".csv"
        graph_data = pd.read_csv(self.plot_filepath, header=None)
        self.graph_data = graph_data
        # # Finds the mode for L0 (length) parameter
        if self.data[-1] == 't':
            length = 23.404
        else:
            length = 22.804
        # General Plotting ---------------------------------------------------------------------------------------------
        if self.plot_count < 0:
            self.ax = self.figure.add_subplot(111)
            # Setting scale to be logarithmic
            self.ax.set_yscale('log')
            self.ax.set_xscale('log')
        # Allows user to plot in ToF if chosen # -----------------------------------------------------------------------
        if tof and not imported:
            #! Convert to pandas compatible
            self.graph_data[0] = self.EnergytoTOF(
                graph_data[0], length=length)  # !
            if self.plot_count < 0:
                self.ax.set(xlabel='ToF (uS)',
                            ylabel='Cross section (b)', title=self.data)
        else:
            if self.plot_count < 0:
                if tof:
                    self.ax.set(xlabel='Time of Flight (uS)',
                                ylabel='Cross section (b)', title=self.data)
                else:
                    self.ax.set(xlabel='Energy (eV)',
                                ylabel='Cross section (b)', title=self.data)
            else:
                self.ax.set(title=None)
        self.figure.tight_layout()

        # Plotting -----------------------------------------------------------------------------------------------------
        colour = colours[self.plot_count + 1]
        spectra_line = self.ax.plot(
            graph_data.iloc[:, 0], graph_data.iloc[:, 1], '-', color=colour, alpha=0.6, linewidth=0.6, label=self.data, gid=self.data)

        # # Creating a legend to toggle on and off plots--------------------------------------------------------------
        legend = self.ax.legend(fancybox=True, shadow=True, )

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
        plt.connect('pick_event', self.onclick)
        # ------------------------------------------------------------------------------------------------------------

        self.ax.autoscale()  # Tidying up
        self.canvas.draw()
        # Establishing plot count
        self.plot_count += 1

        # Amending the table for more than one plot.
        self.table.reset()
        self.table.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        temp_plotted_substances = list(
            set(self.plotted_substances + self.plotted_substances_tof))

        peakinfo_directory = self.filepath + 'GUI Files/Peak information/'
        end_row = [0]
        table_data = pd.DataFrame()
        #! ---------------------------------------------------------------------------------
        # ? Maybe sort the order in which they are plotted and added to the table.

        for substance in temp_plotted_substances:
            #! Fix issue with adding elements without peak data
            self.peak_filepath = peakinfo_directory + substance + ".csv"
            try:
                graph_data = (pd.read_csv(self.peak_filepath))
                if graph_data.empty:
                    graph_data.loc[-1] = [f"No Peaks for {substance}", *['']*9]
                else:
                    graph_data.loc[-1] = [substance, *['']*9]
                graph_data.index += 1
                graph_data.sort_index(inplace=True)
                end_row.append(end_row[-1] + graph_data.shape[0])
                # Add Title Row into dataframe, Null peak data or not.
                # Merging Tables.
                table_data = pd.concat(
                    [table_data, graph_data], ignore_index=True)
            except:
                continue
        self.table_model = ExtendedQTableModel(table_data)
        self.table.setModel(self.table_model)
        self.table.clearSpans()
        for row in end_row[:-1]:
            self.table.setSpan(row, 0, 1, 10)
        # Adding peak labels
        if self.plot_count < 0:
            self.annotations = []
        try:
            if not tof:
                col_no_1 = 1
            else:
                col_no_1 = 3
            for i in range(0, self.number_rows):
                peak_x_coord = graph_data[1:].iloc[i, col_no_1]
                peak_y_coord = graph_data[1:].iloc[i, 7]

                label_y_coord_adjusted = peak_y_coord + (0.05 * peak_y_coord)
                label_x_coord_adjusted = peak_x_coord - (0.05 * peak_x_coord)

                labels = self.ax.annotate(str(i), xy=(peak_x_coord, peak_y_coord), xycoords='data',
                                          xytext=(label_x_coord_adjusted,
                                                  label_y_coord_adjusted),
                                          textcoords='data')

                self.annotations.append(labels)
            self.ax.draw_artist()
        except:
            print('No peak labels available')

    def onclick(self, event):
        """_summary_
            Function to show or hide the selected graph by clicking the legend.
        Args:
            event (pick_event): event on clicking a graphs legend
        """
        legline = event.artist
        origline = self.graphs[legline]
        origline_index = list(self.graphs.keys()).index(
            legline)  # Tells you which plot number you need to delete labels for
        # Hiding relevant line
        visible = not origline.get_visible()
        origline.set_visible(visible)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled.
        legline.set_alpha(1.0 if visible else 0.2)
        # Hiding relevant labels
        if self.annotations == []:
            self.canvas.draw()
            return  # Exits function if there are no labels to hide
        number_plots = len(self.number_totpeaks)  # Tells you how many plots
        number_labels_before = 0  # Tells you how many labels came before the relevant plot
        for i in range(0, origline_index):
            number_labels_before = number_labels_before + \
                self.number_totpeaks[i]
        final_label = number_labels_before + \
            self.number_totpeaks[origline_index]  # Last label of plot
        for i in range(number_labels_before, final_label):
            annotation = self.annotations[i]

            #! -------------------------------------------------------

            if visible and not self.label_check.isChecked():
                annotation.set_visible(True)
            else:
                annotation.set_visible(False)
                self.hidden_annotations.append(annotation)

        self.canvas.draw()

    def PlotToF(self):
        self.Plot(True)

    def EnergytoTOF(self, x_data, length=None):
        if length == None:
            length = 22.804
        neutron_mass = float(1.68E-27)
        electron_charge = float(1.60E-19)

        # Maps all X Values from energy to TOF
        tof_x = list(map(lambda x: length*1E6 *
                     (0.5*neutron_mass/(x*electron_charge))**0.5, x_data))
        return tof_x

    def Clear(self):

        self.figure.clear()  # Clearing Canvas
        self.canvas.draw()
        self.x = []  # Resetting variables
        self.y = []
        self.plot_count = -1
        self.plotted_substances = []
        self.number_totpeaks = []
        self.annotations = []
        self.peaklabel.setText('')
        self.threshold_label.setText('')

        self.table.setModel(None)

        # Resetting legend
        self.graphs = OrderedDict()

        # Resetting dictionaries
        self.table_layout = dict()
        self.arrays = dict()

        # Resetting plotted graphs arrays
        self.plotted_substances = []
        self.plotted_substances_tof = []

        print("norm " + str(self.plotted_substances))
        print("tof " + str(self.plotted_substances_tof))

        # On clearning graphs disable Checkboxes
        self.toggleCheckboxControls(enableAll=False)

    def Gridlines(self, checked):
        print(checked)
        try:
            if checked:
                self.ax.grid()
                self.canvas.draw()
            else:
                self.ax.grid()
                self.canvas.draw()
        except:
            QMessageBox.warning(
                self, 'Error', 'You have not plotted anything')

    def Threshold(self):
        checked = self.threshold_check.isChecked()
        try:
            if checked:
                # Plotting theshold and limits used
                # Getting the singular y-limits
                threshold_coord_y = 0
                threshold_sorting = self.thresholds.split(',')
                if self.thresholds == '100 by default':
                    threshold_coord_y = 100
                elif self.data[-1] == 't':
                    # sort_limits is set earlier in SelectandDisplay
                    threshold_coord_y_sort = len(threshold_sorting[0])
                    threshold_coord_y = float(
                        threshold_sorting[0][1:threshold_coord_y_sort])
                    print('n-tot mode')
                else:
                    # sort_limits is set earlier in SelectandDisplay
                    threshold_coord_y_sort = len(threshold_sorting[1])
                    # To splice the number from the string correctly regardless of magnitude
                    cutoff = threshold_coord_y_sort - 2
                    threshold_coord_y = float(threshold_sorting[1][0:cutoff])
                    print('n-g mode')
                print('Threshold: ', threshold_coord_y)
                # Creating an array to plot line of coords

                self.figure.add_subplot(self.ax)
                self.ax.axhline(y=threshold_coord_y,
                                linestyle='--', color='black', linewidth=0.5, gid="pd_threshold")
                self.canvas.draw()
            else:
                # Getting rid of the second lines plotted on the graph! (Threshold line)
                for line in self.ax.lines:
                    if line.get_gid() == "pd_threshold":
                        line.remove()
                self.canvas.draw()
                # plt.axhline().remove()
                # plt.draw()
        except:
            QMessageBox.warning(
                self, 'Error', 'You have not plotted anything')

    def Annotations(self, checked):
        #! Comflicting with legend hiding
        checked = self.label_check.isChecked()
        try:
            for i in self.annotations:
                if checked and self.annotations not in self.hidden_annotations:
                    i.set_visible(False)
                else:
                    i.set_visible(True)
            self.ax.draw_artist()
        except:
            print('Nah')

    # ! Not Working <-----------------------------------------------------------------------
    def PlotPeakWindow(self, row_clicked):
        try:
            peakwindow = QMainWindow(self)
            # Setting title and geometry
            peakwindow.setWindowTitle('Peak Plotting')
            peakwindow.setGeometry(350, 50, 850, 700)
            # Creating a second canvas for singular peak plotting
            figure2 = plt.figure()
            self.canvas2 = FigureCanvas(figure2)

            # Setting up dock for widgets to be used around canvas
            dock = QDockWidget('Peak info', peakwindow)
            # Creating a widget to contain peak info in dock
            peak_info_widget = QWidget()

            # Creating layout to display peak info in the widget
            layout2 = QVBoxLayout()
            toggle_layout2 = QHBoxLayout()

            # Adding checkbox to toggle the peak limits on and off
            threshold_check2 = QCheckBox(
                'Peak Detection Limits in X', peakwindow)
            threshold_check2.resize(threshold_check2.sizeHint())
            toggle_layout2.addWidget(threshold_check2)
            threshold_check2.stateChanged.connect(self.PeakLimits)
            # Adding checkbox to toggle the peak detection limits on and off
            threshold_check3 = QCheckBox(
                'Peak Detection Limits in Y', peakwindow)
            threshold_check3.resize(threshold_check3.sizeHint())
            toggle_layout2.addWidget(threshold_check3)
            threshold_check3.stateChanged.connect(self.ThresholdforPeak)
            # Adding to overall layout
            layout2.addLayout(toggle_layout2)

            peak_table = QTableWidget()  # Creating a table to display peak info
            peak_table.setColumnCount(4)
            peak_table.setRowCount(1)
            labels = ['Peak Number (Rank)', 'Peak Limits (Limits of Integration) (eV)', 'Peak Centre Co-ord (eV)',
                      'Isotopic Origin']
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

            peakwindow.addDockWidget(
                Qt.DockWidgetArea.BottomDockWidgetArea, dock)
            # Setting canvas as central widget
            peakwindow.setCentralWidget(self.canvas2)

            self.ax2 = figure2.add_subplot(111)
            # Establishing which row belongs to what substance if multiple ------------------------------------------------
            start_row = 0
            for i in self.plotted_substances:
                index = self.plotted_substances.index(i)
                for j in range(0, index):
                    start_row = start_row + self.number_totpeaks[j] + 1
                end_row = start_row + \
                    self.number_totpeaks[self.plotted_substances.index(i)] + 1
                peak_count = 0
                for j in range(start_row, end_row):
                    self.table_layout[j] = i + '_' + str(peak_count)
                    peak_count += 1
            # Get relevant data for peak
            substance = self.table_layout.get(row_clicked)
            # Getting Singular Peak Arrays with PlotPeak-------------------------------------------------------------------
            # Getting peak limits for relevant substance
            peak_limits = []
            try:
                if self.peak_limits_x == dict():
                    filepath = self.filepath + 'GUI Files/Peak_limits.txt'
                    with open(filepath, 'r') as f:
                        lines = f.readlines()
                        for i in lines:
                            # should have sorting = [name, peak limit 1, peak limit 2]
                            sorting = i.split(' ')
                            if sorting[0] == substance[:-2]:
                                # Slicing the actual numbers out of the string
                                peak_limits.append(sorting[1][1:-1])
                                peak_limits.append(sorting[2][:-2])
                            else:
                                continue
                else:
                    peak_center_coord = self.table.item(row_clicked, 1).text()
                    print(self.peak_limits_x)
                    limit = str(peak_center_coord) + '_first'
                    print(limit)
                    peak_limits.append(
                        self.peak_limits_x[str(peak_center_coord) + '_first'])
                    peak_limits.append(
                        self.peak_limits_x[str(peak_center_coord) + '_second'])

            except:
                QMessageBox.warning(
                    self, 'Error', 'No peak limits for this substance')

            # Getting peak limits for relevant peak
            relevant_limits_index = int(self.substance[-1]) * 2 - 2
            self.first_limit = peak_limits[relevant_limits_index]
            self.second_limit = peak_limits[(relevant_limits_index + 1)]

            # Getting the right arrays to plot the graph
            x = self.arrays.get(substance[:-2] + 'x')
            y = self.arrays.get(substance[:-2] + 'y')

            # Truncating array to just before and after peak limits
            index_first_limit = x.index(float(self.first_limit))
            index_second_limit = x.index(float(self.second_limit))
            self.x_array = x[int(index_first_limit - 10):int(index_second_limit + 10)]
            self.y_array = y[int(index_first_limit - 10):int(index_second_limit + 10)]
            # -------------------------------------------------------------------------------------------------------------
            # Plotting
            # Getting user to choose scale
            scale_list = ['linear', 'log']
            scale, ok = QInputDialog.getText(
                peakwindow, 'Scale', 'Enter Scale as "linear" or "log" : ')
            if ok:
                print(scale)
                if scale not in scale_list:
                    QMessageBox.warning(
                        self, 'Error', 'Not a valid scale option - The default is linear')
                    scale = 'linear'
            else:
                return

            self.ax2.set_xscale(scale)
            self.ax2.set_yscale(scale)
            self.ax2.plot(self.x_array, self.y_array, '.')
            self.ax2.autoscale()
            titlename = self.data + '- Peak: ' + str(int(substance[-1]))
            self.ax2.set(xlabel='Energy (eV)',
                         ylabel='Cross section (b)', title=titlename)

            # Filling in the peak info table information-------------------------------------------------------------------
            rank = self.table.item(row_clicked, 0)
            limits = '(' + str(self.first_limit) + \
                ',' + str(self.second_limit) + ')'
            peak_center_coord = self.table.item(row_clicked, 1)
            isotopic_origin = self.table.item(row_clicked, 9)

            # Setting in table
            peak_table.setItem(0, 0, QTableWidgetItem(rank))
            peak_table.setItem(0, 1, QTableWidgetItem(limits))
            peak_table.setItem(
                0, 2, QTableWidgetItem(peak_center_coord))
            peak_table.setItem(
                0, 3, QTableWidgetItem(isotopic_origin))
            peak_table.resizeRowsToContents()

            # Setting label text
            label_info = 'Selected Scale: ' + scale
            scale_label.setText(label_info)

            peakwindow.show()
        except:
            QMessageBox.warning(
                self, 'Error', 'You need to plot the graph first or select a valid row')

    def PeakLimits(self, checked):
        try:
            if checked:
                # Plotting threshold lines ------------------------------------------------------------------------------------
                number_datappoints = len(self.x_array)
                threshold1_x = [(float(self.first_limit))] * number_datappoints
                max_value_in_y = max(self.y_array)
                min_value_in_y = min(self.y_array)
                threshold1_y = np.linspace(
                    min_value_in_y, max_value_in_y, number_datappoints)
                threshold2_x = [(float(self.second_limit))] * \
                    number_datappoints
                self.ax2.plot(threshold1_x, threshold1_y,
                              '--', color='red', linewidth=1.0)
                self.ax2.plot(threshold2_x, threshold1_y,
                              '--', color='red', linewidth=1.0)
                self.canvas2.draw()
            else:
                # Getting rid of the second plot on the graph (the first limit)
                self.ax2.lines.pop(1)
                # Getting rid of what becomes the second plot on the graph (the second limit)
                self.ax2.lines.pop(1)
                self.canvas2.draw()
        except:
            print('No')

    def ThresholdforPeak(self, checked):
        try:
            if checked:
                # Getting the threshold for the specific substance------------------------------------------------------
                # Getting symbol
                symbol_sorting = self.substance.split('-')
                data_symbol = symbol_sorting[1]
                threshold_directory = self.filepath + 'GUI Files/threshold_exceptions.txt'
                with open(threshold_directory, 'r') as f:
                    file = f.readlines()
                self.thresholds = '100 by default'
                # Checking if the selected substance has a threshold exception
                for i in file:
                    sort_limits = i.split(' ')
                    symbol = sort_limits[0]
                    if str(symbol) == str(data_symbol):
                        self.thresholds = str(
                            sort_limits[1]) + str(sort_limits[2])
                # Plotting ---------------------------------------------------------------------------------------------
                number_data_points = len(self.x_array)
                threshold_sorting = self.thresholds.split(',')
                if self.thresholds == '100 by default':
                    threshold_coord_y = 100
                elif self.data[-1] == 't':
                    # sort_limits is set earlier in SelectandDisplay
                    threshold_coord_y_sort = len(threshold_sorting[0])
                    threshold_coord_y = float(
                        threshold_sorting[0][1:threshold_coord_y_sort])
                    print('n-tot mode')
                else:
                    # sort_limits is set earlier in SelectandDisplay
                    threshold_coord_y_sort = len(threshold_sorting[1])
                    # To splice the number from the string correctly regardless of magnitude
                    cutoff = threshold_coord_y_sort - 2
                    threshold_coord_y = float(threshold_sorting[1][0:cutoff])
                    print('n-g mode')
                # Creating an array to plot line of coords
                threshold_coords_y = [
                    float(threshold_coord_y)] * number_data_points
                threshold_coords_x = self.x_array
                self.ax2.plot(threshold_coords_x, threshold_coords_y,
                              '--', color='black', linewidth=0.5)
                self.canvas2.draw()
            else:
                self.ax2.lines.pop()  # Getting rid of line
                self.canvas2.draw()
        except:
            print('No')
            QMessageBox.warning(self, 'Error',
                                'Trouble getting peak limits for this peak \n Contact Rehana.Patel@stfc.ac.uk')

    def importdata(self):  # Allows user to select a file on their computer to open and analyse
        file_name = QFileDialog.getOpenFileName(
            self, 'Open file', self.filepath)
        filepath = file_name[0]
        get_name = filepath.split('/')
        name = get_name[-1]
        name = name[:-4]
        if name[-1] == 'f':
            self.Plot(True, filepath, True, name)
        else:
            self.Plot(False, filepath, True, name)

# ------------------------ PEAK DETECTION BITS ## ------------------------
    def PeakDetection(self):  # Steps of Peak Detection Put into One Function
        # Ask the user to look for minima or maxima
        typecheck = QMessageBox()
        typecheck.setWindowTitle("What Should I Plot?")
        typecheck.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        buttonY = typecheck.button(QMessageBox.Yes)
        buttonY.setText('Maxima')
        buttonN = typecheck.button(QMessageBox.No)
        buttonN.setText('Minima')
        typecheck.exec_()
        pd = PeakDetection()
        if typecheck.clickedButton().text() == "Maxima":
            x, y = pd.maxima(self.graph_data)
        elif typecheck.clickedButton().text() == "Minima":
            x, y = pd.minima(self.graph_data)
        else:
            return
        # # Plots the peak minima/maxima of the detected peaks
        # self.ax.plot(x, y, 'x', color='black')
        # # Plotting peak limits
        # for i in x:
        #     first_limit = self.peak_limits_x[str(i) + '_first']
        #     second_limit = self.peak_limits_x[str(i) + '_second']
        #     first_limit_y = self.peak_limits_y[str(i) + '_first']
        #     second_limit_y = self.peak_limits_y[str(i) + '_second']
        #     self.ax.plot(first_limit, first_limit_y, 'x', color='r')
        #     self.ax.plot(second_limit, second_limit_y, 'x', color='r')
        # self.canvas.draw()
        self.peak_limits_x = pd.peak_limits_x
        self.peak_limits_y = pd.peak_limits_y
        self.PlottingPD(x, y)

    def PlottingPD(self, peaks_x, peaks_y):
        print('MAXIMA LIST: ', (peaks_x, peaks_y))
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)

        # Redrawing graph and Peak Detection Limits
        self.ax.plot(self.graph_data[0], self.graph_data[1],
                     '-', color='b', alpha=0.6, linewidth=0.6)
        self.Threshold()
        self.ax.set_xscale('log')
        self.ax.set_yscale('log')
        self.ax.set(xlabel='Energy (eV)',
                    ylabel='Cross section (b)', title=str(self.data))
        for i in peaks_x:
            y_index = peaks_x.index(i)
            print('x: ', i, 'y: ', peaks_y[y_index])
            self.ax.plot(i, peaks_y[y_index], 'x', color='black')
            first_limit = self.peak_limits_x[str(i) + '_first']
            second_limit = self.peak_limits_x[str(i) + '_second']
            first_limit_y = self.peak_limits_y[str(i) + '_first']
            second_limit_y = self.peak_limits_y[str(i) + '_second']
            self.ax.plot(first_limit, first_limit_y, 'x', color='r')
            self.ax.plot(second_limit, second_limit_y, 'x', color='r')
        self.figure.tight_layout()
        self.canvas.draw()

    def EditPeaks(self):
        # Click count to disconnect after two limits have been selected
        self.clickcount = 0
        # Ordering peaks
        peak_order = 'Rank by eV    (eV) \n'
        for i in range(0, len(self.peak_list)):
            peak_order = peak_order + \
                str(i) + '    ' + str(self.peak_list[i]) + '\n'
        # Choose which peak they are editing
        self.peaknum, ok = QInputDialog.getText(self, 'Peak Editing',
                                                'Choose which peak to edit by entering its peak '
                                                'number \n (Rank by eV) \n' + peak_order)
        typecheck = QMessageBox.question(self, 'Selecting Peak Limits',
                                         'Do you want to select limits by inputting the coordinates?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        if typecheck == QMessageBox.Yes:
            first_limit_x, ok = QInputDialog.getText(self, 'Peak Limits in X',
                                                     'Enter the first peak limit x-coordinate: ')
            second_limit_x, ok = QInputDialog.getText(self, 'Peak Limits in X',
                                                      'Enter the second peak limit x-coordinate: ')
            # Finding the corresponding y-value
            first_limit_y = self.y[self.x.index(first_limit_x)]
            second_limit_y = self.y[self.x.index(second_limit_x)]
            peak = self.peak_list[int(self.peaknum)]
            self.peak_limits_x[str(peak) + '_first'] = float(first_limit_x)
            self.peak_limits_x[str(peak) + '_second'] = float(second_limit_x)
            self.peak_limits_y[str(peak) + '_first'] = float(first_limit_y)
            self.peak_limits_y[str(peak) + '_second'] = float(second_limit_y)
            print('LIMITS: ', self.peak_limits_x)
            # Re-plotting with new limits
            # getting list of minima/maxima for plotting again
            maxima_x = []
            maxima_y = []
            for i in self.peak_limits_x.keys():
                sorting = i.split('_')
                maxima_x.append(sorting[0])
                index = self.x.index(float(sorting[0]))
                maxima_y.append(self.y[index])
            maxima_x = list(dict.fromkeys(maxima_x))
            maxima_y = list(dict.fromkeys(maxima_y))
            maxima_x_float = []
            for i in maxima_x:
                maxima_x_float.append(float(i))
            self.PlottingPD(maxima_x_float, maxima_y)

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

    def SelectLimitsOption(self):
        # Allowing for selecting coordinates
        self.interact = self.canvas.mpl_connect(
            'button_press_event', self.SelectLimits)

    def SelectLimits(self, event):
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
            first_limit_x = self.nearestnumber(self.x, float(
                self.first_click_x))  # Finding the nearest x-value on the spectrum to where was clicked
            second_limit_x = self.nearestnumber(self.x, float(second_click_x))
            # Finding the corresponding y-value
            first_limit_y = self.y[self.x.index(first_limit_x)]
            second_limit_y = self.y[self.x.index(second_limit_x)]
            # Altering it in dictionary
            self.peak_limits_x[str(peak) + '_first'] = first_limit_x
            self.peak_limits_x[str(peak) + '_second'] = second_limit_x
            self.peak_limits_y[str(peak) + '_first'] = first_limit_y
            self.peak_limits_y[str(peak) + '_second'] = second_limit_y
            print('LIMITS: ', self.peak_limits_x)
            # Re-plotting with new limits
            # getting list of minima/maxima for plotting again
            maxima_x = []
            maxima_y = []
            for i in self.peak_limits_x.keys():
                sorting = i.split('_')
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

    # Finds the closest value in a list to the input target value
    def nearestnumber(self, x, target):
        array = np.asarray(x)
        value_index = (
            np.abs(array - target)).argmin()  # Finds the absolute difference between the value and the target
        # then gives the smallest number in the array and returns it
        return array[value_index]


def getLayoutWidgets(layout):
    """getLayoutWidgets returns a list of widgets from an inputted layout.

    Args:
        layout (PyQt Layout): PyQt Layout Object

    Returns:
        List:QtWidgets: List of widgets within the layout.
    """
    return (layout.itemAt(i).widget() for i in range(layout.count()))


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Changing colour of GUI
    app.setStyle('Fusion')
    Colours = QtGui.QPalette()
    Colours.setColor(QtGui.QPalette.Window, QtGui.QColor(220, 220, 220))
    Colours.setColor(QtGui.QPalette.Button, QtGui.QColor(255, 255, 255))
    Colours.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(0, 0, 0))
    app.setPalette(Colours)
    w = DatabaseGUI()
    app.exec()


if __name__ == "__main__":
    main()
