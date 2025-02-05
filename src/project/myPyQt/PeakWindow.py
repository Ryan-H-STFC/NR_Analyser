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

    def __init__(self, parent: QWidget | None = ..., flags: Qt.WindowType = ..., index: QModelIndex = None, ) -> None:
        super().__init__(parent, flags)
        # Setting title and geometry
        self.setWindowTitle("Peak Plotting")
        self.setGeometry(350, 50, 1000, 800)
        self.setObjectName("mainWindow")
        self.setStyleSheet(parent.styleSheet())
        # Creating a second canvas for singular peak plotting
        peakFigure = plt.figure()
        peakCanvas = peakFigure.canvas
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
            spectraName = parent.table_model.data(parent.table_model.index(titleIndex, 0), 0)
            plottedSpectra = [name for name in parent.plottedSpectra if spectraName in name]
            optionsDialog = InputSpectraDialog(parent=parent, styleSheet=parent.styleSheet())
            if len(plottedSpectra) > 1:
                spectraNames = [f"{name}-{'ToF' if tof else 'Energy'}" for name, tof in plottedSpectra]
                optionsDialog.spectras.addItems(spectraNames)
                optionsDialog.mainLayout.addWidget(optionsDialog.spectras)

                acceptBtn = optionsDialog.buttonBox.addButton(QDialogButtonBox.StandardButton.Ok)

                def onAccept():
                    self.tof = 'ToF' in optionsDialog.spectras.currentText()
                    optionsDialog.close()
                acceptBtn.clicked.connect(onAccept)

                optionsDialog.mainLayout.addWidget(optionsDialog.buttonBox)
                optionsDialog.setLayout(optionsDialog.mainLayout)
                optionsDialog.setModal(False)
                optionsDialog.exec()
            else:
                self.tof = plottedSpectra[0][1]

            spectraTitle = f"{spectraName}-{'ToF' if self.tof else 'Energy'}"
            spectra = parent.spectraData[spectraTitle]
            which = 'max' if parent.maxTableOptionRadio.isChecked() else 'min'
            if which == 'max':
                if spectra.maxima.size == 0:
                    return
                # if spectra.maxPeakLimitsX == dict():
                peakX = nearestnumber(spectra.maxima[:, 0], float(parent.table_model.data(
                    parent.table_model.index(index.row(), 1), 0)))
                peakY = nearestnumber(spectra.maxima[:, 1], float(parent.table_model.data(
                    parent.table_model.index(index.row(), 6), 0)))
                limitsX = spectra.maxPeakLimitsX[peakX]
                limitsY = spectra.maxPeakLimitsY[peakX]

            else:
                if spectra.minima.size == 0:
                    return
                peakX = nearestnumber(spectra.minima[:, 0], float(parent.table_model.data(
                    parent.table_model.index(index.row(), 1), 0)))
                peakY = nearestnumber(spectra.minima[:, 1], float(parent.table_model.data(
                    parent.table_model.index(index.row(), 6), 0)))

                limitsX = spectra.minPeakLimitsX[peakX]
                limitsY = spectra.minPeakLimitsY[peakX]

            leftLimit, rightLimit = limitsX
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "No peak limits for this Selection")
        except AttributeError:
            QMessageBox.warning(self, "Warning", "Plot the Graph First")
        tableData = spectra.maxTableData if which == 'max' else spectra.minTableData
        rank = tableData[
            tableData["TOF (us)" if spectra.isToF else "Energy (eV)"] == float(f"{peakX:.6g}")
        ]["Rank by Integral"].iloc[0]

        limits = [f"({limitsX[0]:.6g}, {limitsX[1]:.6g})"]
        peakCoords = [f"({peakX:.6g}, {peakY:.6g})"]
        isoOrigin = [parent.table_model.data(parent.table_model.index(index.row(), 9), 0)]
        data = {"Peak Number (Integral Rank)": rank,
                f"Integration Limits {'(us)' if spectra.isToF else '(eV)'}": limits,
                f"Peak Co-ordinates {'(us)' if spectra.isToF else '(eV)'}": peakCoords,
                "Isotopic Origin": isoOrigin}

        tableData = pd.DataFrame(data, index=None)

        peakTable.setModel(ExtendedQTableModel(tableData, parent))

        peakTable.setObjectName('dataTable')
        peakTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        peakTable.setAlternatingRowColors(True)
        peakTable.verticalHeader().setVisible(False)
        peakTable.setMinimumHeight(200)

        graphData = spectra.graphData[(spectra.graphData[0] >= leftLimit) & (spectra.graphData[0] <= rightLimit)]

        self.limitsCheck.clicked.connect(self.togglePeakLimits)
        self.thresholdCheck.clicked.connect(lambda: self.togglePeakThreshold(spectra))

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

        self.peakAxis.set_title(spectraTitle,
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
                           color=spectra.graphColour,
                           linewidth=0.8,
                           label=spectraTitle,
                           gid=f"{spectraTitle}-PeakWindow"
                           )

        self.peakAxis.plot(peakX,
                           peakY,
                           "x",
                           color="black",
                           markersize=3,
                           alpha=0.6,
                           gid=f"{spectraTitle}-PeakWindow-max"
                           )

        for i, (limX, limY) in enumerate(zip(limitsX, limitsY)):
            self.peakAxis.plot(limX,
                               limY,
                               marker=2,
                               color="r",
                               markersize=8,
                               gid=f"{spectraTitle}-PeakWindow-lim-{i}")

        self.peakAxis.legend(fancybox=True, shadow=True)
        self.peakAxis.autoscale()

    def togglePeakThreshold(self, spectra) -> None:
        if not self.thresholdCheck.isChecked():
            for line in self.peakAxis.get_lines():
                if line.get_gid() == f"PeakWindow-Threshold-{spectra.name}":
                    line.remove()

        else:
            self.peakAxis.axhline(y=spectra.threshold,
                                  linestyle="--",
                                  color=spectra.graphColour,
                                  linewidth=0.5,
                                  gid=f"PeakWindow-Threshold-{spectra.name}")
        self.peakAxis.figure.canvas.draw()

    def togglePeakLimits(self) -> None:
        for line in self.peakAxis.get_lines():
            if "PeakWindow-lim" in line.get_gid():
                line.set_visible(self.limitsCheck.isChecked())
        self.peakAxis.figure.canvas.draw()
