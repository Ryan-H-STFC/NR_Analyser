from __future__ import annotations
import numpy as np
from numpy import ndarray
from os import path
import pandas
from pandas import DataFrame, errors

from element.PeakDetection import PeakDetector
from helpers.getSpacedElements import getSpacedElements
from helpers.integration import integrate_trapz, integrate_simps
from helpers.nearestNumber import nearestnumber
from helpers.timeme import timeme

dataFilepath = f"{path.dirname(path.dirname(__file__))}\\data\\Graph Data\\"
peakLimitFilepath = f"{path.dirname(path.dirname(__file__))}\\data\\Peak Limit Information\\"


class ElementData:
    """
    Data class ElementData used to create a structure for each unique element selection and its data. along with
    altered python dunder functions utilised throughout the program.
    """

    name: str
    numPeaks: int
    tableData: DataFrame
    graphData: DataFrame
    distributions: dict
    defaultDist: dict
    graphColour: tuple

    annotations: list
    annotationsOrder: dict
    threshold: float = 100.0
    maxPeaks: int = 50

    maxima: ndarray = None
    minima: ndarray = None

    maxPeakLimitsX: dict
    maxPeakLimitsY: dict
    minPeakLimitsY: dict
    minPeakLimitsX: dict

    isToF: bool = False
    isImported: bool = False
    isGraphHidden: bool = False
    isGraphDrawn: bool = False
    isGraphUpdating: bool = False
    isDistAltered: bool = False
    isMaxDrawn: bool = False
    isMinDrawn: bool = False
    isAnnotationsHidden: bool = False
    isAnnotationsDrawn: bool = False
    isCompound: bool = False

    def __init__(self,
                 name: str,
                 numPeaks: int,
                 tableData: DataFrame,
                 graphData: DataFrame,
                 graphColour: tuple,
                 isToF: bool,
                 distributions: dict,
                 defaultDist: dict,
                 isCompound: bool = False,
                 isAnnotationsHidden: bool = False,
                 threshold: float = 100,
                 isImported: bool = False) -> None:

        self.name = name
        self.numPeaks = numPeaks
        self.isToF = isToF
        self.distributions = distributions
        self.defaultDist = defaultDist
        self.isCompound = isCompound
        self.annotations = []
        self.annotationsOrder = {}
        self.maxPeakLimitsX = {}
        self.maxPeakLimitsY = {}

        self.isAnnotationsHidden = isAnnotationsHidden
        self.threshold = threshold
        self.isImported = isImported
        pd = PeakDetector()
        try:
            self.tableData = tableData

        except errors.EmptyDataError:
            self.tableData = DataFrame()

        try:
            self.graphData = graphData
            if self.defaultDist != self.distributions:
                self.isDistAltered = True
                self.onDistChange()
                self.UpdatePeaks()

        except errors.EmptyDataError:
            self.graphData = DataFrame()

        try:
            if not self.graphData.empty and not self.isDistAltered:
                self.maxima = np.array(pd.maxima(graphData, threshold))

                self.minima = np.array(pd.minima(graphData))
        except AttributeError:
            # Case when creating compounds, -> requires use of setGraphDataFromDist before plotting.
            pass
        self.graphColour = graphColour

        try:
            name = self.name[8:] if 'element' in self.name else self.name
            limits = pandas.read_csv(f"{peakLimitFilepath}{name}.csv", names=['left', 'right'], header=None)
            for max in self.maxima[0]:
                lim = limits[(limits['left'] < max) & (limits['right'] > max)]
                if lim.empty:
                    continue
                self.maxPeakLimitsX[max] = (lim['left'].iloc[0], lim['right'].iloc[0])
                leftLimit = nearestnumber(graphData[0], lim['left'].iloc[0])
                rightLimit = nearestnumber(graphData[0], lim['right'].iloc[0])
                self.maxPeakLimitsY[max] = (graphData[graphData[0] == leftLimit].iloc[0, 1],
                                            graphData[graphData[0] == rightLimit].iloc[0, 1])

        except ValueError:
            # Catches invalid maximas produced by scipy.signal.find_peaks
            pass
        except FileNotFoundError:
            pass
            # ! Figure out how to replicate peak limits programmatically
            # if self.isToF:
            #     maxPeakWidths = {max: width for max, width in list(zip(
            #         self.tableData["TOF (us)"].iloc[1:], self.tableData["Peak Width"].iloc[1:]))}
            # else:
            #     maxPeakWidths = {max: width for max, width in list(zip(
            #         self.tableData["Energy (eV)"].iloc[1:], self.tableData["Peak Width"].iloc[1:]))}

            # if not self.tableData.empty:
            #     self.maxPeakLimitsX = {
            #         round(max, 1): (max - width / 2, max + width / 2) for max, width in maxPeakWidths.items()
            #     }

        if self.numPeaks is None:
            self.numPeaks = None if self.maxima is None else len(self.maxima[0])

    def __eq__(self, other) -> bool:
        if isinstance(other, ElementData):
            return self.name == other.name and self.isToF == other.isToF
        return False

    def __ne__(self, other) -> bool:
        if isinstance(other, ElementData):
            return self.name != other.name or self.isToF != other.isToF

    def _getGraphDataFromDist(self, graphData: ndarray[float]) -> ndarray[float]:
        """
        ``getGraphDataFromDist`` Will return interpolated y-values for the given graphData over the total domain.

        Args:
            ``graphData`` (ndarray[float]): x-value.

        Returns:
            float: Interpolated y-values for graphData over the given domain.
        """
        return np.interp(self.graphDataX, graphData.iloc[:, 0], graphData.iloc[:, 1])

    @timeme
    def onDistChange(self) -> None:
        """
        ``onDistChange`` Will retrieve an elements the corresponding isotopes graphData appling the weights specified in
        the menu.
        """
        if not self.isDistAltered and not ('element' in self.name or 'compound' in self.name):
            return

        self.weightedIsoGraphData = {name: pandas.read_csv(f"""{dataFilepath}{name.strip('_n-g')}_{
            self.name.split('_')[-1]}.csv""",
                                                           names=['x', 'y'],
                                                           header=None) * [1, dist]
                                     for name, dist in self.distributions.items() if dist != 0}
        self.setGraphDataFromDist(self.weightedIsoGraphData.values())

    def setGraphDataFromDist(self, weightedGraphData: list[DataFrame]) -> None:
        """
        ``setGraphDataFromDist`` Given a list of graphData return a sum of its merged date.
        By merging the x-data either retrieve or linearly interplote for each graphData in the list to produce a y-value
        for the new x-domain. Then sum the resulting y-values inplace and setting the graphData of the instance.


        Args:
            ``weightedGraphData`` (list[DataFrame]): List of graph data for each element or isotope to be summed.
        """

        graphDataX = []
        peakD = PeakDetector()
        for graphData in weightedGraphData:

            graphDataX += peakD.maxima(graphData, 0)[0] if self.maxima is None else list(self.maxima[0])
            graphDataX += peakD.minima(graphData)[0] if self.minima is None else list(self.minima[0])
            graphDataX = list(getSpacedElements(np.array(graphData.iloc[:, 0]),
                                                graphData.shape[0] // 2)) + graphDataX
        self.graphDataX = np.unique(graphDataX)

        isoY = np.zeros(shape=(len(weightedGraphData), self.graphDataX.shape[0]))

        # coreCount = cpu_count()
        # p = Pool(processes=coreCount)
        for i, graphData in enumerate(weightedGraphData):
            isoY[i] = np.interp(self.graphDataX, graphData.iloc[:, 0], graphData.iloc[:, 1])
        # isoY = np.array(p.map(self._getGraphDataFromDist, list(weightedGraphData.values()), coreCount))
        # p.close()
        # p.join()
        self.graphData = pandas.DataFrame(sorted(zip(self.graphDataX, np.sum(isoY, axis=0))))

    def UpdatePeaks(self) -> None:
        """
        ``UpdatePeaks`` recalulates maxima coordinates and updates associated variables.
        Used when threshold values have been altered.
        """
        peakD = PeakDetector()
        self.maxima = np.array(peakD.maxima(self.graphData, self.threshold))
        self.maxPeakLimitsX, self.maxPeakLimitsY = np.array(peakD.GetMaxPeakLimits())
        self.numPeaks = len(self.maxima[0])

        self.minima = np.array(peakD.minima(self.graphData))

    def HideAnnotations(self, globalHide: bool = False) -> None:
        """
        HideAnnotations will only hide if 'Hide Peak Label' is checked, or the graph is hidden,
        otherwise it will show the annotation.

        Args:
            globalHide (bool, optional): Wheher or not the 'Hide Peak Label' is checked or not. Defaults to False.
        """
        if self.annotations == []:
            return

        boolCheck = not (globalHide or self.isGraphHidden)
        for point in self.annotations:
            point.set_visible(boolCheck)
        self.isAnnotationsHidden = boolCheck

    def OrderAnnotations(self, byIntegral: bool = True) -> None:
        """
        ``OrderAnnotations`` alters the rank value assoicated with each peak in the annotations dictionary
        either ranked by integral or by peak width

        Args:
            ``byIntegral`` (bool, optional): Sorted by Integral (True) else by Peak Width (False). Defaults to True.
        """
        self.annotationsOrder.clear()
        if self.numPeaks == 0:
            return
        if self.isImported:
            return

        if self.tableData[1:].empty:
            return

        rankCol = "Rank by Integral" if byIntegral else "Rank by Peak Width"
        xCol = "TOF (us)" if self.isToF else "Energy (eV)"
        yCol = "Peak Height"
        for i in range(self.numPeaks):
            if byIntegral:
                row = self.tableData[1:].loc[
                    (self.tableData[rankCol][1:] == i)
                ]
            else:
                row = self.tableData[1:].loc[
                    (self.tableData[rankCol][1:] == f'({i})')
                ]

            if row.empty:
                continue
            else:
                max_x = nearestnumber(self.maxima[0], row[xCol].iloc[0])
                max_y = nearestnumber(self.maxima[1], row[yCol].iloc[0])
            self.annotationsOrder[i] = (max_x, max_y)

    def PeakIntegral(self, leftLimit: float, rightLimit: float) -> float:
        if "element" in self.name:
            isoGraphData = {name: pandas.read_csv(f"{dataFilepath}{name}_{self.name.split('_')[-1]}.csv",
                                                  names=['x', 'y'],
                                                  header=None)
                            for name, dist in self.distributions.items() if dist != 0}

            integrals = []
            for name, graphData in isoGraphData.items():
                # regionGraphData = graphData[(graphData['x'] >= leftLimit) & (graphData['x'] <= rightLimit)]
                integrals.append(integrate_simps(graphData, leftLimit, rightLimit) * self.distributions[name])

            return sum(integrals)
        else:
            # regionGraphData = self.graphData[(graphData['x'] >= leftLimit) & (graphData['x'] <= rightLimit)]
            return np.mean([integrate_simps(self.graphData, leftLimit, rightLimit),
                            integrate_trapz(self.graphData, leftLimit, rightLimit)])

    def GetPeakLimits(self, max: bool = True) -> tuple[ndarray[float]]:
        if max:
            return (self.maxPeakLimitsX, self.maxPeakLimitsY)
        return (self.minPeakLimitsX, self.minPeakLimitsY)
