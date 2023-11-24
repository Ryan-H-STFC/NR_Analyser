from __future__ import annotations
import numpy as np
from numpy import ndarray
from os import path
import pandas
from pandas import DataFrame, errors

from element.PeakDetection import PeakDetector
from helpers.getSpacedElements import getSpacedElements
from helpers.integration import integrate_simps
from helpers.nearestNumber import nearestnumber


dataFilepath = f"{path.dirname(path.dirname(__file__))}\\data\\Graph Data\\"
peakLimitFilepath = f"{path.dirname(path.dirname(__file__))}\\data\\Peak Limit Information\\"


class ElementData:
    """
    Data class ElementData used to create a structure for each unique element selection and its data. along with
    altered python dunder functions utilised throughout the program.
    """

    name: str
    numPeaks: int
    maxPeaks: int = 50
    tableData: DataFrame
    graphData: DataFrame
    distributions: dict
    defaultDist: dict
    graphColour: tuple

    annotations: list
    annotationsOrder: dict
    threshold: float = 100.0

    maxima: ndarray = None
    minima: ndarray = None

    maxPeakLimitsX: dict
    maxPeakLimitsY: dict
    minPeakLimitsY: dict
    minPeakLimitsX: dict

    isAnnotationsDrawn: bool = False
    isAnnotationsHidden: bool = False
    isCompound: bool = False
    isDistAltered: bool = False
    isGraphDrawn: bool = False
    isGraphHidden: bool = False
    isGraphUpdating: bool = False
    isImported: bool = False
    isMaxDrawn: bool = False
    isMinDrawn: bool = False
    isToF: bool = False

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

        self.tableData = tableData

        if self.tableData is None:
            self.tableData = DataFrame()

        self.graphData = graphData
        if self.defaultDist != self.distributions:
            self.isDistAltered = True
            self.onDistChange()
            self.UpdatePeaks()

        if self.graphData is None:
            self.graphData = DataFrame()

        self.graphColour = graphColour

        length = 23.404 if self.name[-1] == "t" else 22.804

        if self.isToF and not self.graphData.empty:
            graphData[0] = self.energyToTOF(graphData[0], length=length)
            graphData.sort_values(0, ignore_index=True, inplace=True)
        try:
            if not self.graphData.empty and not self.isDistAltered:
                self.maxima = np.array(pd.maxima(graphData, threshold))

                self.minima = np.array(pd.minima(graphData))
        except AttributeError:
            # Case when creating compounds, -> requires use of setGraphDataFromDist before plotting.
            pass
        try:
            name = self.name[8:] if 'element' in self.name else self.name
            limits = pandas.read_csv(f"{peakLimitFilepath}{name}.csv", names=['left', 'right'])
            if self.isToF:
                limits['left'] = self.energyToTOF(limits['left'], length)
                limits['right'] = self.energyToTOF(limits['right'], length)
                limits['left'], limits['right'] = limits['right'], limits['left']

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
            ck = self.name == other.name and self.isToF == other.isToF and self.graphData == other.graphData
            return ck
        return False

    def __ne__(self, other) -> bool:
        if isinstance(other, ElementData):
            return self.name != other.name or self.isToF != other.isToF or self.graphData != other.graphData
        return True

    def energyToTOF(self, xData: float | list[float], length: float | None = None) -> list[float]:
        """
        Maps all X Values from energy to TOF

        Args:
            - ``xData`` (list[float]): List of the substances x-coords of its graph data

            - ``length`` (float, optional): Constant value associated to whether the element data is with repsect to
                                          n-g or n-tot


        Returns:
            list[float]: Mapped x-coords
        """
        if length is None:
            length = 23.404 if self.name[-1] == "t" else 22.804
        neutronMass = float(1.68e-27)
        electronCharge = float(1.60e-19)

        tofX = list(
            map(
                lambda x: length * 1e6 * (0.5 * neutronMass / (x * electronCharge)) ** 0.5,
                xData
            )
        )
        return tofX

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
            return integrate_simps(self.graphData, leftLimit, rightLimit)

    def GetPeakLimits(self, max: bool = True) -> tuple[ndarray[float]]:
        if max:
            return (self.maxPeakLimitsX, self.maxPeakLimitsY)
        return (self.minPeakLimitsX, self.minPeakLimitsY)
