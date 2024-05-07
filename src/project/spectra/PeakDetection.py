from __future__ import annotations
from time import perf_counter
from pyparsing import Literal
from pandas import DataFrame
from scipy import signal
from scipy.ndimage import gaussian_filter1d
import numpy as np
from project.settings import params
from project.helpers.fitBoxes import fitBoxes
from project.helpers.getIndex import getIndex
from project.helpers.smooth import smooth
from project.helpers.nearestNumber import nearestnumber


class PeakDetector:
    """
    Peak Detection, class which is used to find peaks, both maximas and minimas of a sample,
    peak widths used in integration calculations.
    """

    def __init__(self, name, graphData, isImported=False, smoothCoeff=12) -> None:
        self.name = name
        self.graphData = graphData.copy()
        self.isImported = isImported

        self.npSmoothGraph = gaussian_filter1d(graphData.iloc[:, 1], smoothCoeff)
        self.npDer = np.gradient(self.npSmoothGraph)
        self.npSecDer = np.gradient(self.npDer)

        self.smoothGraph = DataFrame([graphData.iloc[:, 0], self.npSmoothGraph]).T
        self.derivative = DataFrame([graphData.iloc[:, 0], self.npDer]).T
        self.secDerivative = DataFrame([graphData.iloc[:, 0], self.npSecDer]).T
        self.infls = np.where(np.diff(np.sign(self.npSecDer)))[0]
        self.flats = np.where(np.diff(np.sign(self.npDer)) < 0)[0]
        self.dips = np.where(np.diff(np.sign(self.npDer)) > 0)[0]

        self.maximaList: np.ndarray = None
        self.minimaList: np.ndarray = None
        self.maxPeakLimitsX: dict = None
        self.maxPeakLimitsY: dict = None
        self.minPeakLimitsX: dict = None
        self.minPeakLimitsY: dict = None

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
                validInfls = self.infls[np.where(self.infls < peakIndex)]
                leftInfl = graphData.loc[np.max(validInfls)] if validInfls.size != 0 else [0]
                validFlats = zerosList[np.where(zerosList < peakIndex)]

                leftFlat = graphData.iloc[(np.max(validFlats))] if validFlats.size != 0 else [0]

                left = leftInfl if leftInfl[0] > leftFlat[0] else leftFlat

                validInfls = self.infls[np.where(self.infls > peakIndex)]
                rightInlf = graphData.loc[np.min(validInfls)] if validInfls.size != 0 else [2e7]
                validFlats = zerosList[np.where(zerosList > peakIndex)]
                rightFlat = graphData.iloc[(np.min(validFlats))] if validFlats.size != 0 else [2e7]

                right = rightInlf if rightInlf[0] < rightFlat[0] else rightFlat
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

        maxima = signal.find_peaks(y,
                                   height=threshold,
                                   prominence=1 if self.isImported else params['max_prominence'])[0]

        maxima_list_x = []
        maxima_list_y = []
        for i in maxima:
            peakX = nearestnumber(self.graphData.iloc[:, 0], x[i])
            peakY = self.graphData[self.graphData.iloc[:, 0] == peakX].iloc[0, 1]
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
        minima = signal.find_peaks(y, prominence=0.1 if self.isImported else params['min_prominence'])[0]

        minima_list_x = []
        minima_list_y = []
        for i in minima:
            peakX = nearestnumber(self.graphData.iloc[:, 0], x[i])
            peakY = self.graphData[self.graphData.iloc[:, 0] == peakX].iloc[0, 1]
            minima_list_x.append(peakX)
            minima_list_y.append(peakY)

        self.minimaList = np.array((minima_list_x, minima_list_y))
        return (minima_list_x, minima_list_y)

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
            peakList = self.minimaList.copy()
            peakList[1] = [min * -1 for min in peakList[1]]
        else:
            self.maxPeakLimitsX = {}
            self.maxPeakLimitsY = {}
            peakList = self.maximaList.copy()

        derivative = np.array(
            [(graphData.iloc[i + 1, 1] - graphData.iloc[i, 1]
              ) / (graphData.iloc[i + 1, 0] - graphData.iloc[i, 0])
             for i in range(graphData.shape[0] - 1)])

        indexPosDer = getIndex(np.int32(derivative < 0), 0)
        target = np.hstack((np.ones((indexPosDer)), np.zeros((np.size(derivative) - indexPosDer))))
        derivative = derivative * (
            np.int64(np.abs(derivative) < params['maxleftslope']) * target + (1 - target))
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
        print(f"{self.name} - definePeaks - {which} - Elapsed Time: {t2-t1}")

    def definePeak(self, peak: tuple[float]) -> tuple[tuple[float]]:
        """
        ``definePeak``
        ---------------

        Calculates the limits of integration for a single peak, modified version of ``definePeaks``.

        Credits go to Ivan Alsina Ferrer - https://github.com/ialsina/NRCA-Spectra/tree/main

        Peak Limit Algorithm used with all pre-existing datasets, now reimplemented for use in the GUI with minor
        changes.
        """
        t1 = perf_counter()
        derivative = np.array(
            [(self.graphDataProxy.iloc[i + 1, 1] - self.graphDataProxy.iloc[i, 1]
              ) / (self.graphDataProxy.iloc[i + 1, 0] - self.graphDataProxy.iloc[i, 0])
             for i in range(self.graphDataProxy.shape[0] - 1)])

        indexPosDer = getIndex(np.int32(derivative < 0), 0)
        target = np.hstack((np.ones((indexPosDer)), np.zeros((np.size(derivative) - indexPosDer))))
        derivative = derivative * (np.int64(np.abs(derivative) < params['maxleftslope']) * target + (1 - target))
        smoothDer = smooth(derivative, params['itersmooth'])

        peakIndexes = {peak: (index, self.graphData[self.graphData.iloc[:, 0] == peak].index[0])
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
