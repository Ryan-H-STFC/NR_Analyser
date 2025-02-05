from __future__ import annotations
from time import perf_counter
from pyparsing import Literal
from pandas import DataFrame
from scipy import signal

from scipy.ndimage import gaussian_filter
# from scipy.interpolate import interp1d

from findpeaks import findpeaks
from findpeaks.interpolate import interpolate_line1d, interpolate_line2d
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

    def __init__(self, name: str,
                 graphData: DataFrame,
                 threshold: float = 100.0,
                 isImported: bool = False
                 ) -> None:
        t1 = perf_counter()
        self.name: str = name
        self.graphData: DataFrame = graphData.copy()
        self.threshold: float = threshold
        self.isImported: bool = isImported

        self.interp = np.array(interpolate_line2d(graphData.iloc[:, 0], graphData.iloc[:, 1], interpol=3, window=3))

        if isImported:
            fp = findpeaks(lookahead=75, interpolate=10, denoise='lee_sigma', params={'delta': 0,
                                                                                      'window': 3})
            fp.plot()
            interp = interpolate_line1d(graphData.iloc[:, 0], 10 if isImported else None)
            results = fp.fit(graphData.iloc[:, 1], interp)['df_interp']
            graphData = DataFrame([results['x'], results['y']]).T

            peakIndexes = results[results['peak'] == True].index.to_numpy()
            dipIndexes = results[results['valley'] == True].index.to_numpy()
            self.prominences = signal.peak_prominences(graphData.iloc[:, 1] * -1, dipIndexes)
            data = self.graphData.copy().to_numpy()
            dipsX = [nearestnumber(self.graphData.iloc[:, 0], x) for x in graphData.loc[dipIndexes].iloc[:, 0]]
            self.dips = data[np.in1d(data[:, 0], dipsX)]

            peakX = [nearestnumber(self.graphData.iloc[:, 0], x) for x in graphData.loc[peakIndexes].iloc[:, 0]]
            self.peaks = data[np.in1d(data[:, 0], peakX)]
        else:
            peakIndexes, info = signal.find_peaks(graphData.iloc[:, 1],
                                                  height=0,
                                                  distance=10 if isImported else None,
                                                  prominence=(params['prominence_min'],
                                                              params['prominence_max']))
            self.dips = np.array(graphData.loc[np.unique([info['left_bases'], info['right_bases']])])
            # self.dips = np.array(graphData.loc[results['df'][results['df']['valley'] == True]['x']])
            self.peaks = np.array(graphData.loc[peakIndexes])
            self.prominences = info['prominences']

        self.npDer = np.gradient(self.interp[1])
        self.npSecDer = np.gradient(self.npDer)

        self.smoothGraph = DataFrame([self.interp[0], self.interp[1]]).T
        self.derivative = DataFrame([self.interp[0], self.npDer]).T
        self.secDerivative = DataFrame([self.interp[0], self.npSecDer]).T
        self.infls = np.where(np.diff(np.sign(self.npSecDer)))[0]

        baselineY = baseline(graphData.iloc[:, 1], 5)

        self.normalised = DataFrame([graphData.iloc[:, 0], graphData.iloc[:, 1] + baselineY]).T
        self.baselineGraph = DataFrame([graphData.iloc[:, 0], baselineY]).T
        self.maximaList: np.ndarray = self.maxima(self.threshold)
        self.minimaList: np.ndarray = self.minima()
        self.maxPeakLimitsX: dict = None
        self.maxPeakLimitsY: dict = None
        self.minPeakLimitsX: dict = None
        self.minPeakLimitsY: dict = None

        self.numPeaks = self.maximaList.shape[0]
        t2 = perf_counter()

        print(f"Elapsed Time - PeakDetector Init - {t2 - t1}")

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
        peakList = self.peaks if which == 'max' else self.dips
        graphData = self.graphData
        if peakList is None:
            return
        if which == 'max':
            self.maxPeakLimitsX = {}
            self.maxPeakLimitsY = {}
        else:
            self.minPeakLimitsX = {}
            self.minPeakLimitsY = {}
        for peakX in peakList[:, 0]:
            try:
                zerosList = self.dips if which == 'max' else self.peaks
                validFlats = zerosList[np.where(zerosList[:, 0] < peakX)]
                leftFlat = np.max(validFlats, axis=0) if validFlats.size != 0 else [min(graphData[0])]

                leftData = self.interp[:, *np.where((leftFlat[0] <= self.interp[0]) & (self.interp[0] <= peakX))]

                leftElbow = self.findElbow(leftData)

                validFlats = zerosList[np.where(zerosList[:, 0] > peakX)]

                rightFlat = np.min(validFlats, axis=0) if validFlats.size != 0 else [max(graphData[0])]
                rightData = self.interp[:, *np.where((peakX <= self.interp[0]) & (self.interp[0] <= rightFlat[0]))]
                rightElbow = self.findElbow(rightData)

                if params['limits_from_first_der'] or self.isImported:

                    left = self.graphData[self.graphData[0] == leftFlat[0]].to_numpy()
                    right = self.graphData[self.graphData[0] == rightFlat[0]].to_numpy()
                else:

                    left = np.array([leftElbow])
                    right = np.array([rightElbow])

                if which == 'max':
                    self.maxPeakLimitsX[peakX] = (left[0, 0], right[0, 0])
                    self.maxPeakLimitsY[peakX] = (left[0, 1], right[0, 1])
                else:
                    self.minPeakLimitsX[peakX] = (left[0, 0], right[0, 0])
                    self.minPeakLimitsY[peakX] = (left[0, 1], right[0, 1])
            except (ValueError, IndexError):
                pass
        t2 = perf_counter()
        print(f"{self.name} - Peak Limits {which} - {t2 - t1}")

    def maxima(self, threshold: float = 100, useInterp: bool = False) -> np.ndarray:
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
        # self.peaks = np.array(
        #     self.graphData.loc[signal.find_peaks(self.graphData.iloc[:, 1],
        #                                          height=0,
        #                                          prominence=(params['peak_prominence_min'],
        #                                                      params['peak_prominence_max'])
        #                                          )[0]])
        peaks = self.peaks[self.peaks[:, 1] >= threshold]

        maxima_list_x = []
        maxima_list_y = []
        for i, peak in enumerate(peaks):
            if not (self.prominences[i] >= params['prominence_min'] and self.prominences[i] <= params['prominence_max']):
                continue
            if useInterp:
                maxima_list_x.append(peak[0])
                maxima_list_y.append(peak[1])
            else:
                maxima_list_x.append(nearestnumber(self.graphData[0], peak[0]))
                maxima_list_y.append(nearestnumber(self.graphData[1], peak[1]))
        self.maximaList = np.array([maxima_list_x, maxima_list_y]).T
        self.numPeaks = self.maximaList.shape[0]
        return self.maximaList

    def minima(self, useInterp: bool = False) -> np.ndarray:
        """
        ``minima``
        ----------

        Finds the coordinates of the minimas within the selected sample.

        Args:
            ``data`` (DataFrame): Pandas Dataframe with the graph data for the sample.

        Returns:
            (minima_list_x, minima_list_y): Tuple of lists, list of x-coords, list of y-coords.
        """

        x, y = self.graphData[0], self.graphData[1]

        minima_list_x = []
        minima_list_y = []
        for i in range(self.dips.shape[0]):
            if useInterp:
                minima_list_x.append(x[i])
                minima_list_y.append(y[i])
            else:
                minima_list_x.append(nearestnumber(self.graphData[0], x[i]))
                minima_list_y.append(nearestnumber(self.graphData[1], y[i]))

        self.minimaList = np.array([minima_list_x, minima_list_y]).T
        self.numDips = self.minimaList.shape[0]

        return self.minimaList

    def findElbow(self, data: np.ndarray = None) -> tuple[float]:
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
        x, y = data

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

        return data[:, index]
