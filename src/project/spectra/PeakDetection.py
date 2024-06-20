from __future__ import annotations
from time import perf_counter
from pyparsing import Literal
from pandas import DataFrame
from scipy import signal
from scipy.ndimage import gaussian_filter1d
# from scipy.interpolate import interp1d
# import peakutils
import numpy as np
from numpy.matlib import repmat
from project.settings import params
from project.helpers.nearestNumber import nearestnumber

from peakutils.baseline import baseline


class PeakDetector:
    """
    Peak Detection, class which is used to find peaks, both maximas and minimas of a sample,
    peak widths used in integration calculations.
    """

    def __init__(self, name: str, graphData: DataFrame, isImported: bool = False, smoothCoeff: float = 12.0) -> None:
        t1 = perf_counter()
        self.name: str = name
        self.graphData = graphData.copy()
        self.isImported: bool = isImported

        # self.baseline = peakutils.baseline(graphData.iloc[:, 1], 5)
        # self.normalised = DataFrame([graphData.iloc[:, 0], graphData.iloc[:, 1] + self.baseline]).T
        if isImported:
            self.npSmoothGraph = graphData.copy().iloc[:, 1]
        else:
            self.npSmoothGraph = gaussian_filter1d(graphData.iloc[:, 1], smoothCoeff)
        self.npDer = np.gradient(self.npSmoothGraph)
        self.npSecDer = np.gradient(self.npDer, )

        self.smoothGraph = DataFrame([graphData.iloc[:, 0], self.npSmoothGraph]).T
        self.derivative = DataFrame([graphData.iloc[:, 0], self.npDer]).T
        self.secDerivative = DataFrame([graphData.iloc[:, 0], self.npSecDer]).T
        self.infls = np.where(np.diff(np.sign(self.npSecDer)))[0]
        self.flats = np.where(np.diff(np.sign(self.npDer)) < 0)[0]
        self.dips = np.where(np.diff(np.sign(self.npDer)) > 0)[0]
        self.info = None
        self.widths = None
        baselineY = baseline(graphData.iloc[:, 1], 5)

        self.normalised = DataFrame([graphData.iloc[:, 0], graphData.iloc[:, 1] + baselineY]).T
        self.baselineGraph = DataFrame([graphData.iloc[:, 0], baselineY]).T
        self.maximaList: np.ndarray = None
        self.minimaList: np.ndarray = None
        self.maxPeakLimitsX: dict = None
        self.maxPeakLimitsY: dict = None
        self.maxPeakLimitsX2: dict = None
        self.maxPeakLimitsY2: dict = None
        self.minPeakLimitsX: dict = None
        self.minPeakLimitsY: dict = None
        t2 = perf_counter()

        print(f"Elapsed Time - PeakDetector Init - {t2-t1}")

    def definePeakLimits(self, which: Literal['max', 'min'] = 'max'):
        """
        ``definePeakLimits``
        --------------------

        Peak limits is define as the closet of eiher the point of inflection or zero derivative, to the left and right
        of each peak.

        Args:
            which (Literal[&#39;max&#39;, &#39;min&#39;], optional): Whether for maximum or minimum peak.
            Defaults to 'max'.
        """
        t1 = perf_counter()
        peakList = self.maximaList if which == 'max' else self.minimaList
        graphData = self.graphData
        if peakList is None:
            return
        if which == 'max':
            self.maxPeakLimitsX = {}
            self.maxPeakLimitsY = {}
        else:
            self.minPeakLimitsX = {}
            self.minPeakLimitsY = {}

        for peakX in peakList[0]:
            try:
                peakIndex = graphData[graphData.iloc[:, 0] == peakX].index.values.astype(int)
                zerosList = self.dips if which == 'max' else self.flats
                validFlats = zerosList[np.where(zerosList < peakIndex)]
                leftFlat = graphData.iloc[(np.max(validFlats))] if validFlats.size != 0 else [0]

                leftData = graphData[(leftFlat[0] <= graphData[0]) & (graphData[0] <= peakX)]

                leftElbow = self.findElbow(leftData)

                validFlats = zerosList[np.where(zerosList > peakIndex)]

                rightFlat = graphData.iloc[(np.min(validFlats))] if validFlats.size != 0 else [max(graphData[0])]
                rightData = graphData[(peakX <= graphData[0]) & (graphData[0] <= rightFlat[0])]
                rightElbow = self.findElbow(rightData)

                left = leftElbow if leftElbow[0] > leftFlat[0] else leftFlat
                right = rightElbow if rightElbow[0] < rightFlat[0] else rightFlat

                if which == 'max':
                    self.maxPeakLimitsX[peakX] = (left[0], right[0])
                    self.maxPeakLimitsY[peakX] = (left[1], right[1])
                else:
                    self.minPeakLimitsX[peakX] = (left[0], right[0])
                    self.minPeakLimitsY[peakX] = (left[1], right[1])
            except ValueError:
                pass
        t2 = perf_counter()
        print(f"{self.name} - Peak Limits {which} - {t2-t1}")

    def maxima(self, threshold: float = 100) -> tuple[list[float]]:
        """
        ``maxima``
        ----------

        Finds the coordinates of any peak which is found higher than the threshold, within the sample. As well as the
        peak widths.
        Args:

            - ``data`` (DataFrame): Pandas Dataframe with the graph data for the sample.

            - ``threshold`` (float): Threshold for what level peaks should be found from.

        Returns:
            (maxima_list_x, maxima_list_y): Tuple of lists, list of x-coords, list of y-coords.
        """
        x, y = self.graphData.iloc[:, 0], self.graphData.iloc[:, 1]

        # Find peaks
        peaks, _ = signal.find_peaks(np.array(y), threshold, rel_height=1, width=10)

        maxima_list_x = []
        maxima_list_y = []
        for i in peaks:
            peakX = nearestnumber(x, x[i])
            peakY = self.graphData[x == peakX].iloc[0, 1]
            maxima_list_x.append(peakX)
            maxima_list_y.append(peakY)
        self.maximaList = np.array((maxima_list_x, maxima_list_y))

        return (maxima_list_x, maxima_list_y)

    def minima(self) -> tuple[list[float]]:
        """
        ``minima``
        ----------

        Finds the coordinates of the minimas within the selected sample.

        Args:
            ``data`` (DataFrame): Pandas Dataframe with the graph data for the sample.

        Returns:
            (minima_list_x, minima_list_y): Tuple of lists, list of x-coords, list of y-coords.
        """
        x, y = self.graphData.iloc[:, 0], self.graphData.iloc[:, 1] * -1
        # height = -0.9, prominence = 0.003 / 0.1
        minima = signal.find_peaks(y, prominence=params['min_prominence'])[0]

        minima_list_x = []
        minima_list_y = []
        for i in minima:
            peakX = nearestnumber(self.graphData.iloc[:, 0], x[i])
            peakY = self.graphData[self.graphData.iloc[:, 0] == peakX].iloc[0, 1]
            minima_list_x.append(peakX)
            minima_list_y.append(peakY)

        self.minimaList = np.array((minima_list_x, minima_list_y))
        return (minima_list_x, minima_list_y)

    def findElbow(self, data: DataFrame = None) -> tuple[float]:
        """
        ``findElbowPoint``
        ------------------

        Args:
            data (np.ndarray): y data between the peak and a zero derivative

        Returns:
            tuple[float]: y data of the point
        """
        if data is None:
            return
        x, y = data.iloc[:, 0], data.iloc[:, 1]

        nPoints = len(y)
        allCoord = np.vstack((x, y)).T

        firstPoint = allCoord[0]
        lineVec = allCoord[-1] - firstPoint
        lineVecNorm = lineVec / np.sqrt(np.sum(lineVec**2))
        vecFromFirst = allCoord - firstPoint
        scalarProduct = np.sum(vecFromFirst * repmat(lineVecNorm, nPoints, 1), axis=1)
        vecFromFirstParallel = np.outer(scalarProduct, lineVecNorm)
        vecToLine = vecFromFirst - vecFromFirstParallel
        distToLine = np.sqrt(np.sum(vecToLine ** 2, axis=1))
        index = np.argmax(distToLine)

        return data.loc[index + data.first_valid_index()]
