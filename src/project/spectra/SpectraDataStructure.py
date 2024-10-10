from __future__ import annotations
import numpy as np
from numpy import ndarray
from pyparsing import Literal
from scipy.interpolate import interp1d
import pandas
from pandas import DataFrame
from decimal import Decimal, getcontext
import concurrent.futures

from project.spectra.PeakDetection import PeakDetector
from project.helpers.getSpacedElements import getSpacedElements
from project.helpers.integration import integrate_simps
from project.helpers.nearestNumber import nearestnumber
from project.helpers.resourcePath import resource_path
from project.helpers.smartRound import smart_round
from project.spectra.Integrator import IsotopeIntegrator
from time import perf_counter
from project.settings import params


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
    maxAnnotationOrder: dict
    minAnnotationOrder: dict
    threshold: dict[float] = {'n-tot': 100.0, 'n-g': 100}
    length: dict[float] = None

    maxima: ndarray = None
    minima: ndarray = None

    peakList: ndarray = None

    maxPeakLimitsX: dict
    maxPeakLimitsY: dict
    minPeakLimitsX: dict
    minPeakLimitsY: dict

    isAnnotationsDrawn: bool = False
    whichAnnotationsDrawn: Literal['max', 'min'] = 'max'
    isAnnotationsHidden: bool = False
    isCompound: bool = False
    distChanging: bool = False
    isGraphDrawn: bool = False
    isGraphHidden: bool = False
    isUpdating: bool = False
    isImported: bool = False
    isMaxDrawn: bool = False
    isMinDrawn: bool = False
    isToF: bool = False

    def __init__(self,
                 name: str,
                 numPeaks: int,
                 tableDataMax: DataFrame,
                 tableDataMin: DataFrame,
                 graphData: DataFrame,
                 graphColour: tuple,
                 isToF: bool,
                 distributions: dict,
                 defaultDist: dict,
                 distChanging: bool = False,
                 isCompound: bool = False,
                 isAnnotationsHidden: bool = False,
                 thresholds: float = 100,
                 length: dict[float] = params['length'],
                 isImported: bool = False,
                 updatingDatabase: bool = False) -> None:

        t1 = perf_counter()

        t3 = perf_counter()
        self.name: str = name
        self.plotType: str = 'n-tot' if 'tot' in self.name else 'n-g'
        self.numPeaks: int = numPeaks
        self.distributions: dict[float] = distributions
        self.defaultDist: dict[float] = defaultDist
        self.distChanging: bool = distChanging
        self.isToF: bool = isToF
        self.isAnnotationsHidden: bool = isAnnotationsHidden
        self.isCompound: bool = isCompound
        self.isImported: bool = isImported
        self.annotations: list = []
        self.maxAnnotationOrder: dict[int] = {}
        self.minAnnotationOrder: dict[int] = {}
        self.maxPeakLimitsX: dict[tuple[float]] = {}
        self.maxPeakLimitsY: dict[tuple[float]] = {}
        self.minPeakLimitsX: dict[tuple[float]] = {}
        self.minPeakLimitsY: dict[tuple[float]] = {}

        self.thresholds: dict[float] = thresholds if isinstance(
            thresholds, dict) else {'n-tot': thresholds[0], 'n-g': thresholds[1]} if isinstance(
                thresholds, tuple) else {'n-tot': 100, 'n-g': 100}
        if self.thresholds is not None:
            self.threshold: float = self.thresholds[self.plotType]
        self.length: dict[float] = length

        self.tableData: DataFrame = DataFrame()
        self.maxTableData: DataFrame = tableDataMax
        self.minTableData: DataFrame = tableDataMin
        dataChanged: bool = isCompound or distChanging

        if self.maxTableData is None:
            self.maxTableData = DataFrame()
        if self.minTableData is None:
            self.minTableData = DataFrame()

        self.graphData: DataFrame = graphData
        if self.graphData is None:
            self.graphData = DataFrame()
        else:
            self.graphData.drop_duplicates(0, inplace=True)
            self.graphData.dropna(inplace=True)
            self.graphData.reset_index(drop=True, inplace=True)

        self.graphColour = graphColour

        if self.length is None:
            self.length = {"n-g": 22.804, "n-tot": 23.404}

        if distChanging:
            self.onDistChange()

        if self.isToF and not self.graphData.empty and not distChanging:
            self.graphData[0] = self.energyToTOF(graphData[0], length=self.length)
        if self.graphData.empty:
            self.peakDetector = None
        else:
            self.graphData.sort_values(0, ignore_index=True, inplace=True)

            self.peakDetector: PeakDetector = PeakDetector(self.name, self.graphData, self.isImported,
                                                           smoothCoeff=1 if self.isImported else 12)
        t4 = perf_counter()

        print(f"Elapsed Time - Start Init - {t4 - t3}")
        t3 = perf_counter()
        try:
            if self.peakDetector is not None:
                self.maxima = np.array(self.peakDetector.maxima(self.threshold))
                self.minima = np.array(self.peakDetector.minima())
        except AttributeError:
            # Case when creating compounds, -> requires use of setGraphDataFromDist before plotting.
            pass
        t4 = perf_counter()
        print(f"Elapsed Time - Peak Detector - {t4 - t3}")
        # Grab Peak Limits for max from file, otherwise calculate
        t3 = perf_counter()
        try:
            if updatingDatabase or dataChanged:
                raise FileNotFoundError
            if not self.distChanging:
                name = self.name[8:] if 'element' in self.name else self.name
                maxLimits = pandas.read_csv(resource_path(
                    f"{peakLimitFilepath}{name}_max.csv"), names=['left', 'right'])
                if self.isToF:
                    # Convert Limit coords to TOF
                    maxLimits['left'] = self.energyToTOF(maxLimits['left'], self.length)
                    maxLimits['right'] = self.energyToTOF(maxLimits['right'], self.length)
                    maxLimits['left'], maxLimits['right'] = maxLimits['right'], maxLimits['left']

                for peak in self.maxima[0]:
                    lim = maxLimits[(maxLimits['left'] < peak) & (maxLimits['right'] > peak)]
                    if lim.empty:
                        continue
                    self.maxPeakLimitsX[peak] = (lim['left'].iloc[0], lim['right'].iloc[0])
                    leftLimit = nearestnumber(graphData[0], lim['left'].iloc[0])
                    rightLimit = nearestnumber(graphData[0], lim['right'].iloc[0])
                    interpGraphData = interp1d(graphData[0], graphData[1])
                    self.maxPeakLimitsY[peak] = (float(interpGraphData(leftLimit)), float(interpGraphData(rightLimit)))
            else:
                raise FileNotFoundError

        except ValueError:
            # Catches invalid maximas produced by scipy.signal.find_peaks
            pass
        except FileNotFoundError:
            if self.maxima is not None:
                if self.maxima.size != 0:

                    self.peakDetector.definePeakLimits(which='max')
                    self.maxPeakLimitsX = self.peakDetector.maxPeakLimitsX.copy()
                    self.maxPeakLimitsY = self.peakDetector.maxPeakLimitsY.copy()
                    self.recalculateAllPeakData(which='max')
        t4 = perf_counter()
        print(f"Elapsed Time - Max Peak Limits - {t4 - t3}")
        t3 = perf_counter()
        try:
            if updatingDatabase:
                raise FileNotFoundError
            if not distChanging:
                minLimits = pandas.read_csv(resource_path(
                    f"{peakLimitFilepath}{name}_min.csv"), names=['left', 'right'])
                if self.isToF:
                    minLimits['left'] = self.energyToTOF(minLimits['left'], self.length)
                    minLimits['right'] = self.energyToTOF(minLimits['right'], self.length)
                    minLimits['left'], minLimits['right'] = minLimits['right'], minLimits['left']
                interpGraphData = interp1d(graphData[0], graphData[1])
                for peak in self.minima[0]:
                    lim = minLimits[(minLimits['left'] < peak) & (minLimits['right'] > peak)]
                    if lim.empty:
                        continue
                    self.minPeakLimitsX[peak] = (lim['left'].iloc[0], lim['right'].iloc[0])
                    leftLimit = nearestnumber(graphData[0], lim['left'].iloc[0])
                    rightLimit = nearestnumber(graphData[0], lim['right'].iloc[0])

                    self.minPeakLimitsY[peak] = (float(interpGraphData(leftLimit)), float(interpGraphData(rightLimit)))
            else:
                raise FileNotFoundError
        except ValueError:
            pass
        except FileNotFoundError:

            if self.minima is not None:
                if self.minima.size != 0:

                    self.peakDetector.definePeakLimits(which='min')
                    self.minPeakLimitsX = self.peakDetector.minPeakLimitsX.copy()
                    self.minPeakLimitsY = self.peakDetector.minPeakLimitsY.copy()
                    self.recalculateAllPeakData(which='min')

        t4 = perf_counter()
        print(f"Elapsed Time - Max Peak Limits - {t4 - t3}")

        if self.numPeaks is None:
            self.numPeaks = None if self.maxima is None else len(self.maxima[0])
        self.changePeakTableData()

        t2 = perf_counter()
        self.isUpdating = False
        print(f"Elapsed Time - {self.name} Init - {t2 - t1}")

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

        # Set the decimal context to avoid precision errors
        getcontext().prec = 50

        neutronMass = Decimal('1.68e-27')
        electronCharge = Decimal('1.60e-19')
        xData = Decimal(str(xData))  # Convert xData to Decimal
        length = Decimal(str(length))  # Convert length to Decimal

        # Perform calculations using Decimal
        result = length * Decimal('1e6') * (Decimal('0.5') * neutronMass / (xData * electronCharge)) ** Decimal('0.5')

        # Convert the result back to float before returning
        return float(result)

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

        # Set the decimal context to avoid precision errors
        getcontext().prec = 50

        neutronMass = Decimal('1.68e-27')
        electronCharge = Decimal('1.60e-19')  # Corrected electronCharge value
        xData = Decimal(str(xData))  # Convert xData to Decimal
        length = Decimal(str(length))  # Convert length to Decimal

        # Perform calculations using Decimal
        result = (length ** 2 * Decimal('1e12') * neutronMass) / (Decimal('2') * electronCharge * xData ** 2)

        # Convert the result back to float before returning
        return float(result)

    def updatePeaks(self, which: Literal['max', 'min', 'both'], newGraphData: bool = False) -> None:
        """
        ``updatePeaks``
        ---------------

        Recalculates maxima coordinates and updates associated variables.
        Used when threshold values have been altered.

        Args:
            which (Literal[&#39;max&#39;, &#39;min&#39;, &#39;both&#39;]): Update maximas or minimas or both.
        """
        t1 = perf_counter()
        if newGraphData:
            self.peakDetector: PeakDetector = PeakDetector(self.name, self.graphData, self.isImported,
                                                           smoothCoeff=1 if self.isImported else 12)
        self.maxima = np.array(self.peakDetector.maxima(self.threshold))
        self.minima = np.array(self.peakDetector.minima())

        self.numPeaks = len(self.maxima[0])
        if which in ['max', 'both']:
            self.peakDetector.definePeakLimits(which='max')
            self.maxPeakLimitsX = self.peakDetector.maxPeakLimitsX
            self.maxPeakLimitsY = self.peakDetector.maxPeakLimitsY
            self.recalculateAllPeakData(which='max')

        if which in ['min', 'both']:
            self.peakDetector.definePeakLimits(which='min')
            self.minPeakLimitsX = self.peakDetector.minPeakLimitsX
            self.minPeakLimitsY = self.peakDetector.minPeakLimitsY
            self.recalculateAllPeakData(which='min')
        t2 = perf_counter()
        print(f"{self.name} - updatePeaks {which} - Elapsed Time: {t2 - t1}")

    def onDistChange(self) -> None:
        """
        ``onDistChange``
        ----------------

        Will retrieve an elements corresponding isotope graphData appling the weights specified in
        the menu.
        """
        if not self.distChanging and not ('element' in self.name or 'compound' in self.name):
            return
        plotType = "n-tot" if 'n-tot' in self.name else "n-g"
        self.weightedIsoGraphData = {name: pandas.read_csv(resource_path(
            f"{params['dir_graphData']}{name}{'' if self.isCompound else '_' + plotType}.csv"),
            header=None) * [1, dist]
            for name, dist in self.distributions.items() if dist != 0}

        self.setGraphDataFromDist(self.weightedIsoGraphData)

    def setGraphDataFromDist(self, weightedGraphData: dict[DataFrame]) -> None:
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
        for name, graphData in weightedGraphData.items():
            peakD = PeakDetector(name, graphData)
            graphDataX += peakD.maxima(self.threshold)[0] if self.maxima is None else list(self.maxima[0])
            graphDataX += peakD.minima()[0] if self.minima is None else list(self.minima[0])
            graphDataX = list(getSpacedElements(np.array(graphData.iloc[:, 0]),
                                                graphData.shape[0] // 2)) + graphDataX
        self.graphDataX = np.unique(graphDataX)

        isoY = np.zeros(shape=(len(weightedGraphData), self.graphDataX.shape[0]))

        for i, graphData in enumerate(weightedGraphData.values()):
            isoY[i] = np.interp(self.graphDataX, graphData.iloc[:, 0], graphData.iloc[:, 1])

        self.graphData = pandas.DataFrame(sorted(zip(self.graphDataX, np.sum(isoY, axis=0))))
        if self.isToF:
            self.graphData[0] = self.energyToTOF(self.graphData[0], length=self.length)
            self.graphData.sort_values(0, ignore_index=True, inplace=True)

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

    def orderAnnotations(self, which: Literal['max', 'min'] = 'max', byIntegral: bool = True) -> None:
        """
        ``orderAnnotations``
        --------------------

        Alters the rank value associated with each peak in the annotations dictionary
        either ranked by integral or by peak width

        Args:
            - ``byIntegral`` (bool, optional): Sorted by Integral (True) else by Peak Width (False). Defaults to True.
        """
        if which == 'max':
            self.maxAnnotationOrder.clear()
        else:
            self.minAnnotationOrder.clear()

        if self.maxima.size == 0 and which == 'max':
            return
        if self.minima.size == 0 and which == 'min':
            return

        tableData = self.maxTableData if which == 'max' else self.minTableData
        peaks = self.maxima if which == 'max' else self.minima
        numPeaks = self.maxima.shape[1] if which == 'max' else self.minima.shape[1]
        if tableData[1:].empty:
            return

        rankCol = "Rank by Integral" if byIntegral else "Rank by Peak Width"
        xCol = "TOF (us)" if self.isToF else "Energy (eV)"
        yCol = "Peak Height"
        for i in range(numPeaks):
            if byIntegral:
                row = tableData[1:].loc[
                    (tableData[rankCol][1:] == i)
                ]
            else:
                row = tableData[1:].loc[
                    (tableData[rankCol][1:] == f'({i})')
                ]

            if row.empty:
                continue
            else:
                peakX = nearestnumber(peaks[0], row[xCol].iloc[0])
                peakY = nearestnumber(peaks[1], row[yCol].iloc[0])

            if which == 'max':
                self.maxAnnotationOrder[i] = (float(f"{peakX:.6g}"), float(f"{peakY:.6g}"))
            else:
                self.minAnnotationOrder[i] = (float(f"{peakX:.6g}"), float(f"{peakY:.6g}"))

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
            integrator = IsotopeIntegrator(self)
            return integrator.peak_integral(leftLimit, rightLimit, which)
        else:
            if leftLimit == rightLimit:
                return (0, 'none')
            return (integrate_simps(self.graphData, leftLimit, rightLimit, which), 'none')

    def recalculatePeakData(self, peak: float, which: Literal['max', 'min'] = 'max') -> None:
        """
        ``recalculatePeakData``
        -----------------------

        Recalculates peak data and rankings for a change on a single peak.

        Args:
            which (Literal[&#39;max&#39;, &#39;min&#39;], optional): Max or Min table data. Defaults to 'max'.
        """
        columns = [
            "Rank by Integral",
            "TOF (us)" if self.isToF else "Energy (eV)",
            "Rank by " + ("TOF" if self.isToF else "Energy"),
            "Integral",
            "Peak Width",
            "Rank by Peak Width",
            "Peak Height",
            "Rank by Peak Height",
            "Relevant Isotope"
        ]
        if which == 'max' and self.maxima.size == 0 or which == 'min' and self.minima.size == 0:
            self.tableData = pandas.DataFrame([[f"No Peak Data for {self.name}", *[""] * 9]], columns=columns)
            return

        if which == 'max':
            table = self.maxTableData
            peakList = self.maxima
            peakLimitsX = self.maxPeakLimitsX
        else:
            table = self.minTableData
            peakList = self.minima
            peakLimitsX = self.minPeakLimitsX

        integral = self.peakIntegral(peakLimitsX[peak][0], peakLimitsX[peak][1], which=which)
        column = 'TOF (us)' if self.isToF else "Energy (eV)"
        intColumn = "Integral"
        table.loc[table[column] == float(f"{peak:.6g}"), intColumn] = float(f"{integral[0]:.6g}")

        integrals = {peak: (table.loc[table[column] == float(f"{peak:.6g}"), "Integral"].iloc[0],
                            table.loc[table[column] == float(f"{peak:.6g}"), 'Relevant Isotope'].iloc[0])
                     for peak in peakLimitsX.keys()}

        integralRanks = {peak: i for i, peak in enumerate(dict(
            sorted(integrals.items(), key=lambda item: item[1], reverse=True)).keys())}

        peakHeightRank = {peak: i for i, peak in enumerate(
            sorted(peakList[1], key=lambda item: item, reverse=True))}

        peakWidth = {peak: peakLimitsX[peak][1] - peakLimitsX[peak][0]
                     for peak in peakLimitsX.keys()}

        peakWidthRank = {peak: i for i, peak in enumerate(dict(
            sorted(peakWidth.items(), key=lambda item: item[1], reverse=True)).keys())}
        t1 = perf_counter()
        tableDataTemp = [
            [
                integralRanks[x],                                                           # Rank by Integral
                float(np.format_float_positional(x, 6, fractional=False)),                  # Value
                f"({np.where(peakList[0] == x)[0][0]})",                                    # Rank by Value
                float(np.format_float_positional(integrals[x][0], 6, fractional=False)),    # Integral
                float(np.format_float_positional(peakWidth[x], 6, fractional=False)),       # Peak Width
                f"({peakWidthRank[x]})",                                                    # Rank by Peak Width
                float(np.format_float_positional(y, 6, fractional=False)),                  # Peak Height
                f"({peakHeightRank[y]})",                                                   # Rank by Peak Height
                integrals[x][1]                                                             # Relevant Isotope
            ]
            for x, y in [peak for peak in peakList.T if peak[0] in integralRanks.keys()]]

        t2 = perf_counter()
        print(f"Table Data Creation - {t2 - t1}")
        tableDataTemp = sorted(tableDataTemp, key=lambda item: item[0])

        if which == 'max':
            self.maxTableData = pandas.DataFrame(tableDataTemp, columns=columns)
            self.maxTableData.loc[-1] = [f"{self.name}", *[""] * 8]
            self.maxTableData.index += 1
            self.maxTableData.sort_index(inplace=True)
        else:
            self.minTableData = pandas.DataFrame(tableDataTemp, columns=columns)
            self.minTableData.loc[-1] = [f"{self.name}", *[""] * 8]
            self.minTableData.index += 1
            self.minTableData.sort_index(inplace=True)
        self.changePeakTableData(which=which)
        self.orderAnnotations(which=which)

    def recalculateAllPeakData(self, which: Literal['max', 'min'] = 'max') -> None:
        """
        ``recalculatePeakData``
        -----------------------

        Loops over the existing peaks of the instance and calculates the data associated with each. Updating the table
        data.
        """
        columns = [
            "Rank by Integral",
            "TOF (us)" if self.isToF else "Energy (eV)",
            "Rank by " + ("TOF" if self.isToF else "Energy"),
            "Integral",
            "Peak Width",
            "Rank by Peak Width",
            "Peak Height",
            "Rank by Peak Height",
            "Relevant Isotope"
        ]
        if (which == 'max' and self.maxPeakLimitsX == {}) or (which == 'min' and self.minPeakLimitsX == {}):
            self.tableData = pandas.DataFrame([[f"No Peak Data for {self.name}", *[""] * 8]], columns=columns)

            if which == 'max':
                self.maxTableData = self.tableData.copy()
            else:
                self.minTableData = self.tableData.copy()

            return

        if which == 'max':
            peakList = self.maxima
            peakLimitsX = self.maxPeakLimitsX
        else:
            peakList = self.minima
            peakLimitsX = self.minPeakLimitsX
        t1 = perf_counter()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(
                self.peakIntegral,
                peakLimitsX[peak][0],
                peakLimitsX[peak][1],
                which=which): peak for peak in peakLimitsX.keys()}
            integrals = {peak: future.result() for future, peak in futures.items()}

        t2 = perf_counter()
        print(f"Integral Calc - {t2 - t1}")
        t1 = perf_counter()
        integralRanks = {peak: i for i, peak in enumerate(dict(
            sorted(integrals.items(), key=lambda item: item[1], reverse=True)).keys())}

        t2 = perf_counter()
        print(f"Integral Ranks Calc - {t2 - t1}")
        t1 = perf_counter()

        peakHeightRank = {peak: i for i, peak in enumerate(
            sorted(peakList[1], key=lambda item: item, reverse=True))}
        t2 = perf_counter()
        print(f"Peak Height Rank Calc - {t2 - t1}")
        t1 = perf_counter()

        peakWidth = {peak: peakLimitsX[peak][1] - peakLimitsX[peak][0]
                     for peak in peakLimitsX.keys()}
        t2 = perf_counter()
        print(f"Peak Width Calc - {t2 - t1}")
        t1 = perf_counter()

        peakWidthRank = {peak: i for i, peak in enumerate(dict(
            sorted(peakWidth.items(), key=lambda item: item[1], reverse=True)).keys())}
        t2 = perf_counter()
        print(f"Peak Width Rank Calc - {t2 - t1}")
        t1 = perf_counter()

        tableDataTemp = [
            [
                integralRanks[x],                                                           # Rank by Integral
                float(np.format_float_positional(x, 6, fractional=False)),                  # Value
                f"({np.where(peakList[0] == x)[0][0]})",                                    # Rank by Value
                float(np.format_float_positional(integrals[x][0], 6, fractional=False)),    # Integral
                float(np.format_float_positional(peakWidth[x], 6, fractional=False)),       # Peak Width
                f"({peakWidthRank[x]})",                                                    # Rank by Peak Width
                float(np.format_float_positional(y, 6, fractional=False)),                  # Peak Height
                f"({peakHeightRank[y]})",                                                   # Rank by Peak Height
                integrals[x][1]                                                             # Relevant Isotope
            ]
            for x, y in [peak for peak in peakList.T if peak[0] in integralRanks.keys()]]

        t2 = perf_counter()
        print(f"Table Data Creation - {t2 - t1}")
        tableDataTemp = sorted(tableDataTemp, key=lambda item: item[0])

        if which == 'max':
            self.maxTableData = pandas.DataFrame(tableDataTemp, columns=columns)
            self.maxTableData.loc[-1] = [f"{self.name}", *[""] * 8]
            self.maxTableData.index += 1
            self.maxTableData.sort_index(inplace=True)
        else:
            self.minTableData = pandas.DataFrame(tableDataTemp, columns=columns)
            self.minTableData.loc[-1] = [f"{self.name}", *[""] * 8]
            self.minTableData.index += 1
            self.minTableData.sort_index(inplace=True)
        self.changePeakTableData(which=which)

        t2 = perf_counter()

        print(f"{self.name} - TableData {which} - Elapsed Time: {t2 - t1}")

    def changePeakTableData(self, which: Literal['max', 'min'] = 'max') -> None:
        """
        ``changePeakTableData``
        -----------------------

        Args:
            which (Literal[&#39;max&#39;, &#39;min&#39;], optional): Which peak table to set as currently active.
            Defaults to 'max'.
        """
        self.tableData = self.maxTableData.copy() if which == 'max' else self.minTableData.copy()
