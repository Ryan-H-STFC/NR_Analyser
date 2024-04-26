from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QDockWidget,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTableView,
    QWidget,
    QVBoxLayout
)
from matplotlib.backends.backend_qt5agg import (
    NavigationToolbar2QT as NavigationToolbar
)
from matplotlib.ticker import LogLocator, LogFormatterSciNotation
import matplotlib.pyplot as plt
import matplotlib.rcsetup
import numpy as np
import pandas as pd

from project.helpers.nearestNumber import nearestnumber
from project.myMatplotlib.CustomFigureCanvas import FigureCanvas
from project.myPyQt.ExtendedTableModel import ExtendedQTableModel
from project.myPyQt.InputSpectraDialog import InputSpectraDialog

matplotlib.use("QtAgg")

matplotlib.rcParams['figure.subplot.top'] = 0.927
matplotlib.rcParams['figure.subplot.bottom'] = 0.192
matplotlib.rcParams['figure.subplot.left'] = 0.066
matplotlib.rcParams['figure.subplot.right'] = 0.985
matplotlib.rcParams['figure.subplot.hspace'] = 0.2
matplotlib.rcParams['figure.subplot.wspace'] = 0.2


class PeakWindow(QMainWindow):

    def __init__(self, parent: QWidget | None = ..., flags: Qt.WindowType = ..., index: QModelIndex = None) -> None:
        super().__init__(parent, flags)
        # Setting title and geometry
        self.setWindowTitle("Peak Plotting")
        self.setGeometry(350, 50, 1000, 800)
        self.setObjectName("mainWindow")
        self.setStyleSheet(parent.styleSheet())
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
        dock = QDockWidget(parent=self)
        # Creating a widget to contain peak info in dock
        peakInfoWidget = QWidget()

        # Creating layout to display peak info in the widget
        bottomLayout = QVBoxLayout()
        toggleLayout = QHBoxLayout()

        # Adding checkbox to toggle the peak limits on and off
        self.limitsCheck = QCheckBox("Integration Limits", self)
        self.limitsCheck.resize(self.limitsCheck.sizeHint())
        self.limitsCheck.setObjectName("peakCheck")
        self.limitsCheck.setChecked(True)
        toggleLayout.addWidget(self.limitsCheck)

        # Adding checkbox to toggle the peak detection limits on and off
        self.thresholdCheck = QCheckBox("Peak Detection Limits", self)
        self.thresholdCheck.setObjectName("peakCheck")
        self.thresholdCheck.resize(self.thresholdCheck.sizeHint())
        toggleLayout.addWidget(self.thresholdCheck)
        # Adding to overall layout
        bottomLayout.addLayout(toggleLayout)

        peakTable = QTableView()

        bottomLayout.addWidget(peakTable)

        # Adding label which shows what scale the user picks
        scaleLabel = QLabel()
        scaleLabel.setObjectName("peakLabel")
        bottomLayout.addWidget(scaleLabel)

        # Setting layout within peak info widget
        peakInfoWidget.setLayout(bottomLayout)
        dock.setWidget(peakInfoWidget)  # Adding peak info widget to dock

        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, dock)
        # Setting canvas as central widget
        self.setCentralWidget(canvasProxyWidget)

        self.peakAxis = None
        self.peakAxis = peakFigure.add_subplot(111)

        try:
            titleIndex = sorted([rowIndex for rowIndex in parent.titleRows if index.row() > rowIndex])[-1]
            elementName = parent.table_model.data(parent.table_model.index(titleIndex, 0), 0)
            plottedSpectra = [name for name in parent.plottedSpectra if elementName in name]
            optionsDialog = InputSpectraDialog()
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
                optionsDialog.exec()
            else:
                self.tof = plottedSpectra[0][1]

            elementTitle = f"{elementName}-{'ToF' if self.tof else 'Energy'}"
            element = parent.spectraData[elementTitle]
            which = 'max' if parent.maxTableOptionRadio.isChecked() else 'min'
            if which == 'max':
                if element.maxima.size == 0:
                    return
                # if element.maxPeakLimitsX == dict():
                peakX = nearestnumber(element.maxima[0], float(parent.table_model.data(
                    parent.table_model.index(index.row(), 3 if self.tof else 1), 0)))
                peak = [max for max in element.maxima.T if max[0] == peakX][0]
                limitsX = element.maxPeakLimitsX[peak[0]]
                limitsY = element.maxPeakLimitsY[peak[0]]

            else:
                if element.minima.size == 0:
                    return
                peakX = nearestnumber(element.minima[0], float(parent.table_model.data(
                    parent.table_model.index(index.row(), 3 if self.tof else 1), 0)))
                peak = [min for min in element.minima.T if min[0] == peakX][0]
                limitsX = element.minPeakLimitsX[peak[0]]
                limitsY = element.minPeakLimitsY[peak[0]]

            leftLimit, rightLimit = limitsX
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "No peak limits for this Selection")
        except AttributeError:
            QMessageBox.warning(self, "Warning", "Plot the Graph First")
        tableData = element.maxTableData if which == 'max' else element.minTableData
        rank = tableData[
            tableData["TOF (us)" if element.isToF else "Energy (eV)"] == float(f"{peak[0]:.6g}")
        ]["Rank by Integral"].iloc[0]

        limits = [f"({limitsX[0]:.6g}, {limitsX[1]:.6g})"]
        peakCoords = [f"({peak[0]:.6g}, {peak[1]:.6g})"]
        isoOrigin = [parent.table_model.data(parent.table_model.index(index.row(), 9), 0)]
        data = {"Peak Number (Integral Rank)": rank,
                f"Integration Limits {'(us)' if element.isToF else '(eV)'}": limits,
                f"Peak Co-ordinates {'(us)' if element.isToF else '(eV)'}": peakCoords,
                "Isotopic Origin": isoOrigin}

        tableData = pd.DataFrame(data, index=None)

        peakTable.setModel(ExtendedQTableModel(tableData))

        peakTable.setObjectName('dataTable')
        peakTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        peakTable.setAlternatingRowColors(True)
        peakTable.verticalHeader().setVisible(False)
        peakTable.setMinimumHeight(200)

        graphData = element.graphData[(element.graphData[0] >= leftLimit) & (element.graphData[0] <= rightLimit)]

        self.limitsCheck.clicked.connect(self.togglePeakLimits)
        self.thresholdCheck.clicked.connect(lambda: self.togglePeakThreshold(element))

        self.peakAxis.set_xscale('log')
        self.peakAxis.set_yscale('log')

        self.peakAxis.minorticks_on()
        plt.minorticks_on()
        self.peakAxis.xaxis.set_minor_locator(LogLocator(10, 'all'))
        self.peakAxis.xaxis.set_minor_formatter(LogFormatterSciNotation(10, False, (np.inf, np.inf)))
        self.peakAxis.xaxis.set_tick_params('major',
                                            size=6,
                                            color="#888",
                                            labelsize=8
                                            )
        self.peakAxis.xaxis.set_tick_params('minor',
                                            size=4,
                                            color="#888",
                                            labelsize=6,
                                            labelrotation=45,
                                            )
        self.peakAxis.yaxis.set_tick_params('major',
                                            size=6,
                                            color="#888",
                                            labelsize=8
                                            )
        self.peakAxis.yaxis.set_tick_params('minor',
                                            size=4,
                                            color="#888",
                                            labelsize=6,
                                            )

        self.peakAxis.set_title(elementTitle,
                                fontsize='small'
                                )
        self.peakAxis.set_xlabel("Energy (eV)",
                                 fontsize='small'
                                 )
        self.peakAxis.set_ylabel("Cross Section (b)",
                                 fontsize='small'
                                 )

        self.peakAxis.plot(graphData[0],
                           graphData[1],
                           color=element.graphColour,
                           linewidth=0.8,
                           label=elementTitle,
                           gid=f"{elementTitle}-PeakWindow"
                           )

        self.peakAxis.plot(peak[0],
                           peak[1],
                           "x",
                           color="black",
                           markersize=3,
                           alpha=0.6,
                           gid=f"{elementTitle}-PeakWindow-max"
                           )

        for i, (peakX, peakY) in enumerate(zip(limitsX, limitsY)):
            self.peakAxis.plot(peakX,
                               peakY,
                               marker=2,
                               color="r",
                               markersize=8,
                               gid=f"{elementTitle}-PeakWindow-lim-{i}")

        self.peakAxis.legend(fancybox=True, shadow=True)
        self.peakAxis.autoscale()

    def togglePeakThreshold(self, element) -> None:
        if not self.thresholdCheck.isChecked():
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

    def togglePeakLimits(self) -> None:
        for line in self.peakAxis.get_lines():
            if "PeakWindow-lim" in line.get_gid():
                line.set_visible(self.limitsCheck.isChecked())
        self.peakAxis.figure.canvas.draw()
