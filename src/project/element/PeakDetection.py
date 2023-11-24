from __future__ import annotations
from pandas import DataFrame
import scipy as sp


class PeakDetector:
    """
    Peak Detection, class which is used to find peaks, both maximas and minimas of a sample,
    peak widths used in integration calculations.
    """

    def __init__(self) -> None:
        self.maxPeakLimitsX = None
        self.maxPeakLimitsY = None
        self.minPeakLimitsX = None
        self.minPeakLimitsY = None
        self.peak_list = None

    def maxima(self, data: DataFrame, threshold: float = 100) -> tuple[list[float]]:
        """
        ``maxima`` finds the coordinates of any peak which is found higher than the threshold, within the sample.
        As well as the peak widths.
        Args:
            ``self`` (PeakDetector): PeakDetector Instance.

            ``data`` (DataFrame): Pandas Dataframe with the graph data for the sample.

            ``threshold`` (float): Threshold for what level peaks should be found from.

        Returns:
            (maxima_list_x, maxima_list_y): Tuple of lists, list of x-coords, list of y-coords.
        """
        x, y = data.iloc[:, 0], data.iloc[:, 1]
        maxima, _ = sp.signal.find_peaks(y, height=threshold)

        width = sp.signal.peak_widths(y, maxima, rel_height=1, wlen=110)
        # Extracting maxima coordinates
        maxima_list_x: list[float] = []
        maxima_list_y = []
        maxima = maxima.tolist()
        for i in maxima:
            maxima_list_x.append(x[i])  # Get list of maxima # !
            maxima_list_y.append(y[i])
        # Extracting peak width coordinates
        self.maxPeakLimitsX = {}  # Re-setting if used before
        self.maxPeakLimitsY = {}
        first_limits = width[2].tolist()
        second_limits = width[3].tolist()
        # Refining peak limits
        # first_limits, second_limits = self.PeakLimitsCheck(first_limits, second_limits, maxima)
        # print("FL", first_limits)
        for i in first_limits:
            index = first_limits.index(i)
            peak = maxima_list_x[index]
            # ! Loss of Accuracy? check how indexing is done
            coordinate = x[round(i)]
            # Finding the y- value for corresponding limits
            coordinate_index = x.loc[x == coordinate].index[0]
            self.maxPeakLimitsX[f"{peak}_first"] = coordinate
            self.maxPeakLimitsY[f"{peak}_first"] = y[coordinate_index]
        for i in second_limits:
            index = second_limits.index(i)
            peak = maxima_list_x[index]
            coordinate = x[round(i)]
            # Finding the y- value for corresponding limits
            coordinate_index = x.loc[x == coordinate].index[0]
            self.maxPeakLimitsX[f"{peak}_second"] = coordinate
            self.maxPeakLimitsY[f"{peak}_second"] = y[coordinate_index]
        # print("Peak limits x: ", self.maxPeakLimitsX)
        # print("Peak limits y: ", self.maxPeakLimitsY)
        self.peak_list = maxima_list_x
        return (maxima_list_x, maxima_list_y)

    def minima(self, data: DataFrame) -> tuple[list[float]]:
        """
        ``minima`` finds the coordinates of the minimas within the selected sample.

        Args:
            ``self`` (PeakDetector): PeakDetector Instance.
            ``data`` (DataFrame): Pandas Dataframe with the graph data for the sample.

        Returns:
            (minima_list_x, minima_list_y): Tuple of lists, list of x-coords, list of y-coords.
        """
        x = data.iloc[:, 0]
        y = (lambda data: -1 * data.iloc[:, 1])(data)
        minima, _ = sp.signal.find_peaks(y, height=-0.90, prominence=0.0035)
        width = sp.signal.peak_widths(y, minima, rel_height=1, wlen=300)
        # Extracting peak center coordinates
        minima_list_x = []
        minima_list_y = []
        minima = minima.tolist()
        for i in minima:
            minima_list_x.append(x[i])
            minima_list_y.append(y[i])
        # Extracting peak width coordinates
        self.minPeakLimitsX = dict()  # Resetting if used before
        self.minPeakLimitsY = dict()
        first_limits = width[2].tolist()
        second_limits = width[3].tolist()
        for i in first_limits:
            index = first_limits.index(i)
            peak = minima_list_x[index]
            coordinate = x[round(i)]
            # Finding the y- value for corresponding limits
            coordinate_index = x.loc[x == coordinate].index[0]

            self.minPeakLimitsX[f"{peak}_first"] = coordinate
            self.minPeakLimitsY[f"{peak}_first"] = y[coordinate_index]
        for i in second_limits:
            index = second_limits.index(i)
            peak = minima_list_x[index]
            coordinate = x[round(i)]
            # Finding the y- value for corresponding limits
            coordinate_index = x.loc[x == coordinate].index[0]
            self.minPeakLimitsX[f"{peak}_second"] = coordinate
            self.minPeakLimitsY[f"{peak}_second"] = y[coordinate_index]

        minima_list_y = list(map(lambda val: -1 * val, minima_list_y))
        return minima_list_x, minima_list_y

    def GetMaxPeakLimits(self) -> tuple[dict[str]]:
        return self.maxPeakLimitsX, self.maxPeakLimitsY

    def GetMinPeakLimits(self) -> tuple[dict[str]]:
        return self.minPeakLimitsX, self.minPeakLimitsY
