from __future__ import annotations
import numpy as np
from numpy import ndarray
from pyparsing import Literal
from scipy.interpolate import interp1d
import pandas
from pandas import DataFrame
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor
from concurrent import futures
from more_itertools import grouper

from spectra.PeakDetection import PeakDetector
from helpers.getSpacedElements import getSpacedElements
from helpers.fitBoxes import fitBoxes
from helpers.getIndex import getIndex
from helpers.integration import integrate_simps
from helpers.nearestNumber import nearestnumber
from helpers.smooth import smooth
from helpers.splitProcessing import splitProcess
from time import perf_counter
from settings import params


dataFilepath = params['dir_graphData']
peakLimitFilepath = params['dir_peakLimitInfo']


class SpectraData:
    """
    Class SpectraData used to create a structure for each unique element selection and its data. along with
    altered python dunder functions utilised throughout the program.
    """

    name: str
    numPeaks: int
    maxPeaks: int = 50
    tableData: DataFrame
    maxTableData: DataFrame
    minTableData: DataFrame
    graphData: DataFrame
    graphDataProxy: DataFrame
    distributions: dict
    defaultDist: dict
    graphColour: tuple
    plotType: str

    annotations: list
    annotationsOrder: dict
    threshold: float = 100.0
    length: dict[float] = None

    maxima: ndarray = None
    minima: ndarray = None

    peakList: ndarray = None

    maxPeakLimitsX: dict
    maxPeakLimitsY: dict
    minPeakLimitsX: dict
    minPeakLimitsY: dict

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
                 length: dict[float] = params['length'],
                 isImported: bool = False) -> None:

        t1 = perf_counter()

        self.name = name
        self.plotType = 'n-tot' if 'tot' in self.name else 'n-g'
        self.numPeaks = numPeaks
        self.isToF = isToF
        self.distributions = distributions
        self.defaultDist = defaultDist
        self.isCompound = isCompound
        self.annotations = []
        self.annotationsOrder = {}
        self.maxPeakLimitsX = {}
        self.maxPeakLimitsY = {}
        self.minPeakLimitsX = {}
        self.minPeakLimitsY = {}

        self.isAnnotationsHidden = isAnnotationsHidden
        self.threshold = threshold
        self.length = length
        self.isImported = isImported
        pd = PeakDetector()

        self.tableData = tableData
        self.maxTableData = tableData.copy()

        if self.tableData is None:
            self.tableData = DataFrame()

        self.graphData = graphData

        if self.graphData is None:
            self.graphData = DataFrame()

        self.graphColour = graphColour

        if self.length is None:
            self.length = {"n-g": 22.804, "n-tot": 23.404}

        if self.isToF and not self.graphData.empty:
            graphData[0] = self.energyToTOF(graphData[0], length=self.length)
            graphData.sort_values(0, ignore_index=True, inplace=True)
        if self.defaultDist != self.distributions:
            self.isDistAltered = True
            self.onDistChange()
            self.updatePeaks(which='both')
        try:
            if not self.graphData.empty and not self.isDistAltered:
                self.maxima = np.array(pd.maxima(graphData, threshold))

                self.minima = np.array(pd.minima(graphData))
        except AttributeError:
            # Case when creating compounds, -> requires use of setGraphDataFromDist before plotting.
            pass

        # Grab Peak Limits for max from file, otherwise calculate
        try:
            if not self.isDistAltered:
                name = self.name[8:] if 'element' in self.name else self.name
                maxLimits = pandas.read_csv(f"{peakLimitFilepath}{name}_max.csv", names=['left', 'right'])

                if self.isToF:
                    # Convert Limit coords to TOF
                    maxLimits['left'] = self.energyToTOF(maxLimits['left'], self.length)
                    maxLimits['right'] = self.energyToTOF(maxLimits['right'], self.length)
                    maxLimits['left'], maxLimits['right'] = maxLimits['right'], maxLimits['left']

                for max in self.maxima[0]:
                    lim = maxLimits[(maxLimits['left'] < max) & (maxLimits['right'] > max)]
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
            # if self.maxima.shape[1] < 100:
            if self.maxima is not None:
                if self.maxima.size != 0:

                    self.definePeaks(which='max')
                    self.recalculatePeakData()
            # else:
            #     if self.maxima is not None and not self.maxima.size == 0:
            #         self.peakList = self.maxima.copy()
            #         self.graphDataProxy = self.graphData.copy()
            #         # results = splitProcess(self.definePeak, [(peak[0], peak[1]) for peak in self.maxima.T], chunks=8)
            #         # for result in results.get():
            #         #     print(result)
            #         executor = ProcessPoolExecutor()
            #         future = [executor.submit(self.definePeak, group)
            #                   for group in grouper([(peak[0], peak[1]) for peak in self.maxima.T], 8)]
            #         results = futures.wait(future)
            #         for result in results:
            #             print(result)
            #         self.recalculatePeakData()

       # Grab Peak Limits for Min, otherwise calculate

        try:
            minLimits = pandas.read_csv(f"{peakLimitFilepath}{name}_min.csv", names=['left', 'right'])

            if self.isToF:
                minLimits['left'] = self.energyToTOF(minLimits['left'], self.length)
                minLimits['right'] = self.energyToTOF(minLimits['right'], self.length)
                minLimits['left'], minLimits['right'] = minLimits['right'], minLimits['left']
            for min in self.minima[0]:
                lim = minLimits[(minLimits['left'] < max) & (minLimits['right'] > max)]
                if lim.empty:
                    continue
                self.minPeakLimitsX[min] = (lim['left'].iloc[0], lim['right'].iloc[0])
                leftLimit = nearestnumber(graphData[0], lim['left'].iloc[0])
                rightLimit = nearestnumber(graphData[0], lim['right'].iloc[0])

                self.maxPeakLimitsY[max] = (graphData[graphData[0] == leftLimit].iloc[0, 1],
                                            graphData[graphData[0] == rightLimit].iloc[0, 1])
        except ValueError:
            pass
        except FileNotFoundError:

            # if self.minima.shape[1] < 100:
            if self.minima is not None:
                if self.minima.size != 0:

                    self.definePeaks(which='min')
                    self.recalculatePeakData()
            # else:
            #     if self.minima is not None and not self.minima.size == 0:
            #         self.peakList = self.minima.copy()
            #         self.graphDataProxy = self.graphData.copy()
            #         self.graphDataProxy.iloc[:, 1] = self.graphDataProxy.iloc[:, 1] * -1
            #         results = splitProcess(self.definePeak, [(peak[0], peak[1]) for peak in self.minima.T], 'min', 8)
            #         for result in results:
            #             print(result)
            #         self.recalculatePeakData(which='min')

        if self.numPeaks is None:
            self.numPeaks = None if self.maxima is None else len(self.maxima[0])

        t2 = perf_counter()

        print(f"init - Elapsed Time: {t2-t1}")

    def __eq__(self, other) -> bool:
        """
        Returns whether or not a SpectraData instance is equal to another, based on its name TOF state and graph data.

        Args:
            - ``other`` (Any): Object on the right-hand side of the equal to comparison. Although returns False if not
            of type SpectraData.

        Returns:
            bool: Whether or not the two SpectraData Objects are equal.
        """
        if isinstance(other, SpectraData):
            ck = self.name == other.name and self.isToF == other.isToF and self.graphData == other.graphData
            return ck
        return False

    def __ne__(self, other) -> bool:
        """
        Returns whether or not two SpectraData objects are not equal, based on the names, TOF state and graph data.

        Args:
            - ``other`` (Any): Object on the right-hand side of the equal to comparison.

        Returns:
            bool: Whether or not two instances are not equal to one another.
        """
        if isinstance(other, SpectraData):
            return self.name != other.name or self.isToF != other.isToF or self.graphData != other.graphData
        return True

    def energyToTOF(self,
                    xData: float | list[float],
                    length: dict[float] = {"n-g": 22.804, "n-tot": 23.404}) -> list[float]:
        """
        ``energyToTOF``
        ---------------

        Maps all X Values from energy to TOF

        Args:
            - ``xData`` (list[float]): List of the substances x-coords of its graph data

        Returns:
            list[float]: Mapped x-coords
        """
        if self.length is not None:
            length = self.length
        neutronMass = float(1.68e-27)
        electronCharge = float(1.60e-19)

        tofX = list(
            map(
                lambda x: length[self.plotType] * 1e6 * (0.5 * neutronMass / (x * electronCharge)) ** 0.5,
                xData
            )
        )
        return tofX

    def e2TOF(self, xData: float, length: dict[float] = params['length']) -> float:
        """
        ``e2TOF``
        -------

        Converts a single X Value from energy to TOF

        Args:
            - ``xData`` (float): Energy-Value.

            - ``length`` (dict[float], optional): Constant value associated with the plotType.
                                                Defaults to params['length'].

        Returns:
            float: Mapped x-coord
        """
        if self.length is not None:
            length = self.length[self.plotType]
        neutronMass = float(1.68e-27)
        electronCharge = float(1.60e-19)

        return length * 1e6 * (0.5 * neutronMass / (xData * electronCharge)) ** 0.5

    def tof2e(self, xData: float, length: dict[float] = params['length']) -> float:
        """
        ``tof2e``
        ---------

        Converts a single X Value from TOF to energy

        Args:
            - ``xData`` (float): TOF-Value

            - ``length`` (dict[float], optional): Constant value associated with the plotType.
                                                Defaults to params['length'].

        Returns:
            float: Mapped x-coord
        """
        if self.length is not None:
            length = self.length[self.plotType]
        neutronMass = float(1.68e-27)
        electronCharge = float(1.68e-19)

        return (length ** 2 * 1e12 * neutronMass) / (2 * electronCharge * xData ** 2)

    def updatePeaks(self, which: Literal['max', 'min', 'both']) -> None:
        """
        ``updatePeaks``
        ---------------

        Recalculates maxima coordinates and updates associated variables.
        Used when threshold values have been altered.
        """
        peakD = PeakDetector()
        self.maxima = np.array(peakD.maxima(self.graphData, self.threshold))
        self.minima = np.array(peakD.minima(self.graphData))

        self.numPeaks = len(self.maxima[0])
        if which == 'both':
            self.definePeaks(which='max')
            self.definePeaks(which='min')
            self.recalculatePeakData(which='min')
        else:
            self.definePeaks(which=which)
            self.recalculatePeakData(which=which)

    def onDistChange(self) -> None:
        """
        ``onDistChange``
        ----------------

        Will retrieve an elements corresponding isotope graphData appling the weights specified in
        the menu.
        """
        if not self.isDistAltered and not ('element' in self.name or 'compound' in self.name):
            return
        plotType = "n-tot" if 'n-tot' in self.name else "n-g"
        self.weightedIsoGraphData = {name: pandas.read_csv(
            f"{params['dir_graphData']}{name}{'' if self.isCompound else '_'+plotType}.csv",
            names=['x', 'y'],
            header=None) * [1, dist]
            for name, dist in self.distributions.items() if dist != 0}
        self.setGraphDataFromDist(self.weightedIsoGraphData.values())

    def setGraphDataFromDist(self, weightedGraphData: list[DataFrame]) -> None:
        """
        ``setGraphDataFromDist``
        ------------------------

        Given a list of graphData return a sum of its merged date. By merging the x-data either retrieve or linearly
        interpolate for each graphData in the list to produce a y-value for the new x-domain. Then sum the resulting
        y-values in-place and setting the graphData of the instance.

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
        if self.isToF:
            self.graphData[0] = self.energyToTOF(self.graphData[0], self.length)

    def hideAnnotations(self, globalHide: bool = False) -> None:
        """
        ``hideAnnotations``
        -------------------

        Will only hide if 'Hide Peak Label' is checked, or the graph is hidden,
        otherwise it will show the annotation.

        Args:
            - ``globalHide`` (bool, optional): Whether or not the 'Hide Peak Label' is checked or not.
            Defaults to False.
        """
        if self.annotations == []:
            return

        boolCheck = not (globalHide or self.isGraphHidden)
        for point in self.annotations:
            point.set_visible(boolCheck)
        self.isAnnotationsHidden = boolCheck

    def orderAnnotations(self, byIntegral: bool = True) -> None:
        """
        ``orderAnnotations``
        --------------------

        Alters the rank value associated with each peak in the annotations dictionary
        either ranked by integral or by peak width

        Args:
            - ``byIntegral`` (bool, optional): Sorted by Integral (True) else by Peak Width (False). Defaults to True.
        """
        self.annotationsOrder.clear()
        if self.numPeaks == 0:
            return
        if self.isImported:
            return

        if self.maxTableData[1:].empty:
            return

        rankCol = "Rank by Integral" if byIntegral else "Rank by Peak Width"
        xCol = "TOF (us)" if self.isToF else "Energy (eV)"
        yCol = "Peak Height"
        for i in range(self.numPeaks):
            if byIntegral:
                row = self.maxTableData[1:].loc[
                    (self.maxTableData[rankCol][1:] == i)
                ]
            else:
                row = self.maxTableData[1:].loc[
                    (self.maxTableData[rankCol][1:] == f'({i})')
                ]

            if row.empty:
                continue
            else:
                max_x = nearestnumber(self.maxima[0], row[xCol].iloc[0])
                max_y = nearestnumber(self.maxima[1], row[yCol].iloc[0])
            self.annotationsOrder[i] = (max_x, max_y)

    def peakIntegral(self, leftLimit: float, rightLimit: float,
                     which: Literal['max', 'min'] = 'max') -> tuple[float, str]:
        """
        ``peakIntegral``
        ----------------

        Calculates the integral of a peak within the region specificed by the limits, uses the simpson rule and removes
        a trapezium created between the axis and the coordinates of the limits.

        Args:
            - ``leftLimit`` (float): X-Coord of the left limit of integration

            - ``rightLimit`` (float): X-Coord of the right limit of integration

            - ``which`` (Literal): Whether getting integral of max or min

        Returns:
            tuple[float, str]: (Integral Value, Relevant Isotope)
        """
        if "element" in self.name:
            isoGraphData = {name: pandas.read_csv(f"{dataFilepath}{name}_{self.name.split('_')[-1]}.csv",
                                                  names=['x', 'y'],
                                                  header=None)
                            for name, dist in self.distributions.items() if dist != 0}

            if self.isToF:
                for name, graphData in isoGraphData.items():
                    graphData['x'] = self.energyToTOF(graphData['x'], self.length)
                    graphData.sort_values('x', ignore_index=True, inplace=True)
                    isoGraphData[name] = graphData
            integrals = dict()
            for name, graphData in isoGraphData.items():

                graphDataInterp = interp1d(graphData.iloc[:, 0], graphData.iloc[:, 1])
                xRange = np.arange(leftLimit, rightLimit, (rightLimit - leftLimit) / 100)
                integrals[name] = integrate_simps(DataFrame(list(zip(xRange, graphDataInterp(xRange))),
                                                            columns=['x', 'y']),
                                                  leftLimit,
                                                  rightLimit,
                                                  which=which) * self.distributions[name]

            return (sum(integrals.values()), f"['{max(integrals, key=integrals.get)}_{self.plotType}']")
        else:
            return (integrate_simps(self.graphData, leftLimit, rightLimit, which), 'none')

    def definePeaks(self, which: Literal['max', 'min'] = 'max') -> None:
        """
        ``definePeaks``
        ---------------

        Calculates the limits of integration for peaks.

        Credits go to Ivan Alsina Ferrer - https://github.com/ialsina/NRCA-Spectra/tree/main

        Peak Limit Algorithm used with all pre-existing datasets, now reimplemented for use in the GUI with minor
        changes.
        """
        t1 = perf_counter()
        graphData = self.graphData.copy()
        if which == 'min':
            self.minPeakLimitsX = {}
            self.minPeakLimitsY = {}
            graphData[1] = graphData[1].apply(lambda y: y * -1)
            peakList = self.minima.copy()
            peakList[1] = [min * -1 for min in peakList[1]]
        else:
            self.maxPeakLimitsX = {}
            self.maxPeakLimitsY = {}
            peakList = self.maxima.copy()

        derivative = np.array(
            [(graphData.iloc[i + 1, 1] - graphData.iloc[i, 1]
              ) / (graphData.iloc[i + 1, 0] - graphData.iloc[i, 0])
             for i in range(graphData.shape[0] - 1)])

        indexPosDer = getIndex(np.int32(derivative < 0), 0)
        target = np.hstack((np.ones((indexPosDer)), np.zeros((np.size(derivative) - indexPosDer))))
        derivative = derivative * (np.int64(np.abs(derivative) < params['maxleftslope']) * target + (1 - target))
        smoothDer = smooth(derivative, params['itersmooth'])

        peakIndexes = [graphData[graphData[0] == max].index[0] for max in peakList[0]]
        for i, max in enumerate(peakList[0]):
            # Number of points at the left of the current peak
            nleft = peakIndexes[i]
            # Number of points at the right of the current peak
            nright = np.shape(graphData)[0] - nleft - 1
            if np.size(peakList > 1):
                if i == 0 or i == np.size(peakList[0]) - 1:
                    prange = min(params['prangemax'], nleft, nright)
                else:
                    indexPrev = peakIndexes[i - 1]
                    indexNext = peakIndexes[i + 1]
                    prange = min(params['prangemax'], indexNext - indexPrev, nleft, nright)
            elif np.size(peakList) == 1:
                prange = min(params['prangemax'], nleft, nright)
            else:
                prange = 0

            peakIndex = peakIndexes[i]
            derRegion = smoothDer[peakIndex - prange: peakIndex + prange + 1]
            for i in range(1, 10):
                fit, boxwidth = fitBoxes(derRegion, params['dboxes'] * i)
                temp1, temp2 = np.unique(fit, return_counts=True)
                if not (temp2 == 1).all():
                    break
            outerslope = temp1[np.argmax(temp2)]
            if abs(outerslope) > params['maxouterslope']:
                outerslope = 0
            limsX = []
            limsY = []
            for sign in [-1, 1]:
                decreasing, increasing, lock = False, False, False
                derMax = None
                for i in range(peakIndex, peakIndex + sign * (prange + 1), sign):
                    if i + sign == smoothDer.shape[0]:
                        break
                    decreasing = smoothDer[i + sign] < smoothDer[i]
                    increasing = smoothDer[i + sign] > smoothDer[i]
                    if not lock:
                        if (decreasing if sign == -1 else increasing):
                            lock = True
                            derMax = smoothDer[np.max(np.where(np.isfinite(smoothDer)))]
                            if derMax == outerslope:
                                # raise Exception('Non-standing slope', prange)
                                continue
                    if lock:
                        if (smoothDer[peakIndex] == np.inf) or (smoothDer[peakIndex + sign] == np.nan):
                            limsX.append(graphData.iloc[peakIndex + sign, 0])
                            limsY.append(graphData.iloc[peakIndex + sign, 1])
                            break
                        if abs((derivative[i] - outerslope) / (derMax - outerslope)) <= params['slopedrop']:
                            limsX.append(graphData.iloc[i, 0])
                            limsY.append(graphData.iloc[i, 1])
                            break
                        if smoothDer[i + sign] * smoothDer[i] <= 0:
                            if i == peakIndex:
                                limsX.append(graphData.iloc[i + sign, 0])
                                limsY.append(graphData.iloc[i + sign, 1])
                            else:
                                limsX.append(graphData.iloc[i, 0])
                                limsY.append(graphData.iloc[i, 1])
                            break
                        if i == peakIndex + sign * (prange):
                            limsX.append(graphData.iloc[i, 0])
                            limsY.append(graphData.iloc[i, 1])
                            break

            try:

                lims = sorted(list(zip(limsX, limsY)), key=lambda item: item[0])
                if which == 'max':
                    self.maxPeakLimitsX[max] = (lims[0][0], lims[1][0])
                    self.maxPeakLimitsY[max] = (lims[0][1], lims[1][1])
                if which == 'min':
                    self.minPeakLimitsX[max] = (lims[0][0], lims[1][0])
                    self.minPeakLimitsY[max] = (lims[0][1] * -1, lims[1][1] * -1)

            except IndexError:
                # indexL = peakIndex - (peakIndex - (prange + 1)) // 3
                # indexR = peakIndex + (peakIndex - (prange + 1)) // 3
                # if which == 'max':
                #     self.maxPeakLimitsX[max] = (graphData.iloc[indexL, 0], graphData.iloc[indexR, 0])
                #     self.maxPeakLimitsY[max] = (graphData.iloc[indexL, 1], graphData.iloc[indexR, 1])
                # if which == 'min':
                #     self.minPeakLimitsX[max] = (graphData.iloc[indexL, 0], graphData.iloc[indexR, 0])
                #     self.minPeakLimitsY[max] = (graphData.iloc[indexL, 1] * -1, graphData.iloc[indexR, 1] * -1)
                print(max)
        t2 = perf_counter()
        print(f"Elapsed Time: {t2-t1} - {which}")

    def definePeak(self, peak: tuple[float]) -> tuple[tuple[float]]:
        t1 = perf_counter()
        derivative = np.array(
            [(self.graphDataProxy.iloc[i + 1, 1] - self.graphDataProxy.iloc[i, 1]
              ) / (self.graphDataProxy.iloc[i + 1, 0] - self.graphDataProxy.iloc[i, 0])
             for i in range(self.graphDataProxy.shape[0] - 1)])

        indexPosDer = getIndex(np.int32(derivative < 0), 0)
        target = np.hstack((np.ones((indexPosDer)), np.zeros((np.size(derivative) - indexPosDer))))
        derivative = derivative * (np.int64(np.abs(derivative) < params['maxleftslope']) * target + (1 - target))
        smoothDer = smooth(derivative, params['itersmooth'])

        peakIndexes = {peak: (index, self.graphData[self.graphData[0] == peak].index[0])
                       for index, peak in enumerate(self.peakList[0])}

        # Number of points at the left of the current peak
        nleft = peakIndexes[peak[0]][1]
        # Number of points at the right of the current peak
        nright = np.shape(self.graphDataProxy)[0] - nleft - 1
        peakEnum = peakIndexes[peak[0]][0]
        peakIndex = peakIndexes[peak[0]][1]
        if np.size(self.peakList > 1):
            if peakIndexes[peak[0]][0] == 0 or peakIndexes[peak[0]][0] == np.size(self.peakList[0]) - 1:
                prange = min(params['prangemax'], nleft, nright)
            else:
                indexPrev = [index[1] for index in peakIndexes.values() if index[0] == peakEnum - 1][0]
                indexNext = [index[1] for index in peakIndexes.values() if index[0] == peakEnum + 1][0]
                prange = min(params['prangemax'], indexNext - indexPrev, nleft, nright)
        elif np.size(self.peakList) == 1:
            prange = min(params['prangemax'], nleft, nright)
        else:
            prange = 0

        derRegion = smoothDer[peakIndex - prange: peakIndex + prange + 1]
        for i in range(1, 10):
            fit, boxwidth = fitBoxes(derRegion, params['dboxes'] * i)
            temp1, temp2 = np.unique(fit, return_counts=True)
            if not (temp2 == 1).all():
                break
        outerslope = temp1[np.argmax(temp2)]
        if abs(outerslope) > params['maxouterslope']:
            outerslope = 0
        limsX = []
        limsY = []
        for sign in [-1, 1]:
            decreasing, increasing, lock = False, False, False
            derMax = None
            for i in range(peakIndex, peakIndex + sign * (prange + 1), sign):
                if i + sign == smoothDer.shape[0]:
                    break
                decreasing = smoothDer[i + sign] < smoothDer[i]
                increasing = smoothDer[i + sign] > smoothDer[i]
                if not lock:
                    if (decreasing if sign == -1 else increasing):
                        lock = True
                        derMax = smoothDer[np.max(np.where(np.isfinite(smoothDer)))]
                        if derMax == outerslope:
                            # raise Exception('Non-standing slope', prange)
                            continue
                if lock:
                    if (smoothDer[peakIndex] == np.inf) or (smoothDer[peakIndex + sign] == np.nan):
                        limsX.append(self.graphDataProxy.iloc[peakIndex + sign, 0])
                        limsY.append(self.graphDataProxy.iloc[peakIndex + sign, 1])
                        break
                    if abs((derivative[i] - outerslope) / (derMax - outerslope)) <= params['slopedrop']:
                        limsX.append(self.graphDataProxy.iloc[i, 0])
                        limsY.append(self.graphDataProxy.iloc[i, 1])
                        break
                    if smoothDer[i + sign] * smoothDer[i] <= 0:
                        if i == peakIndex:
                            limsX.append(self.graphDataProxy.iloc[i + sign, 0])
                            limsY.append(self.graphDataProxy.iloc[i + sign, 1])
                        else:
                            limsX.append(self.graphDataProxy.iloc[i, 0])
                            limsY.append(self.graphDataProxy.iloc[i, 1])
                        break
                    if i == peakIndex + sign * (prange):
                        limsX.append(self.graphDataProxy.iloc[i, 0])
                        limsY.append(self.graphDataProxy.iloc[i, 1])
                        break
        t2 = perf_counter()
        print(f"{peak}, {peakIndex} - Elapsed Time: {t2-t1}")

    def recalculatePeakData(self, which: Literal['max', 'min'] = 'max') -> None:
        """
        ``recalculatePeakData``
        -----------------------

        Loops over the existing peaks of the instance and calculates the data associated with each. Updating the table
        data.
        """
        t1 = perf_counter()
        if which == 'max' and self.maxima.size == 0 or which == 'min' and self.minima.size == 0:
            self.tableData = pandas.DataFrame([[f"No Peak Data for {self.name}", *[""] * 9]],
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
            return
        if which == 'max':
            peakList = self.maxima
            peakLimitsX = self.maxPeakLimitsX
        else:
            peakList = self.minima
            peakLimitsX = self.minPeakLimitsX

        integrals = {peak: self.peakIntegral(peakLimitsX[peak][0], peakLimitsX[peak][1], which=which)
                     for peak in peakLimitsX.keys()}
        integralRanks = {peak: i for i, peak in enumerate(dict(
            sorted(integrals.items(), key=lambda item: item[1], reverse=True)).keys())}

        peakHeightRank = {peak: i for i, peak in enumerate(
            sorted(peakList[1], key=lambda item: item, reverse=True))}

        peakWidth = {peak: peakLimitsX[peak][1] - peakLimitsX[peak][0]
                     for peak in peakLimitsX.keys()}

        peakWidthRank = {peak: i for i, peak in enumerate(dict(
            sorted(peakWidth.items(), key=lambda item: item[1], reverse=True)).keys())}

        if self.isToF:
            tableDataTemp = [
                [
                    integralRanks[peakCoords[0]],                            # Rank by Integral
                    float(f"{self.e2TOF(peakCoords[0]):.5g}"),               # Energy (eV)
                    f"({np.where(peakList[0] == peakCoords[0])[0][0]})",     # Rank by Energy
                    float(f"{peakCoords[0]:.5g}"),                           # TOF (us)
                    float(f"{integrals[peakCoords[0]][0]:.5g}"),             # Integral
                    float(f"{peakWidth[peakCoords[0]]:.5g}"),                # Peak Width
                    f"({peakWidthRank[peakCoords[0]]})",                     # Rank by Peak Width
                    float(f"{peakCoords[1]:.5g}"),                           # Peak Height
                    f"({peakHeightRank[peakCoords[1]]:.5g})",                # Rank by Peak Height
                    integrals[peakCoords[0]][1]                              # Relevant Isotope
                ]
                for peakCoords in [peak for peak in peakList.T if peak[0] in integralRanks.keys()]]
        else:
            tableDataTemp = [
                [
                    integralRanks[peakCoords[0]],                            # Rank by Integral
                    float(f"{peakCoords[0]:.5g}"),                           # Energy (eV)
                    f"({np.where(peakList[0] == peakCoords[0])[0][0]})",     # Rank by Energy
                    float(f"{self.e2TOF(peakCoords[0]):.5g}"),               # TOF (us)
                    float(f"{integrals[peakCoords[0]][0]:.5g}"),             # Integral
                    float(f"{peakWidth[peakCoords[0]]:.5g}"),                # Peak Width
                    f"({peakWidthRank[peakCoords[0]]})",                     # Rank by Peak Width
                    float(f"{peakCoords[1]:.5g}"),                           # Peak Height
                    f"({peakHeightRank[peakCoords[1]]:.5g})",                # Rank by Peak Height
                    integrals[peakCoords[0]][1]                              # Relevant Isotope
                ]
                for peakCoords in [peak for peak in peakList.T if peak[0] in integralRanks.keys()]]
        tableDataTemp = sorted(tableDataTemp, key=lambda item: item[0])

        if which == 'max':
            self.maxTableData = pandas.DataFrame(tableDataTemp,
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
            self.tableData = self.maxTableData.copy()
            self.maxTableData.loc[-1] = [f"{self.name}", *[""] * 9]
            self.maxTableData.index += 1
            self.maxTableData.sort_index(inplace=True)
        else:
            self.minTableData = pandas.DataFrame(tableDataTemp,
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
            self.tableData = self.minTableData.copy()
            self.minTableData.loc[-1] = [f"{self.name}", *[""] * 9]
            self.minTableData.index += 1
            self.minTableData.sort_index(inplace=True)
        self.tableData.loc[-1] = [f"{self.name}", *[""] * 9]
        self.tableData.index += 1
        self.tableData.sort_index(inplace=True)

        t2 = perf_counter()

        print(f"TableData {which} - Elapsed Time: {t2-t1}")
