from dataclasses import dataclass
from pandas import DataFrame, errors
import numpy as np
from numpy import ndarray
from PeakDetection import PeakDetector


@dataclass(repr=True)
class ElementData:
    """
    Data class ElementData used to create a structure for each unique element selection and its data. along with
    altered python dunder functions utilised throughout the program.
    """

    name: str
    numPeaks: int
    tableData: list
    graphData: list
    graphColour: tuple
    annotations: list
    threshold: float = 100.0
    maxPeaks: int = 50
    maxima: ndarray = None
    minima: ndarray = None

    max_peak_limits_x: ndarray = None
    max_peak_limits_y: ndarray = None

    min_peak_limits_x: ndarray = None
    min_peak_limits_y: ndarray = None

    isToF: bool = False
    isGraphHidden: bool = False
    isAnnotationsHidden: bool = False
    isAnnotationsDrawn: bool = False

    def __init__(self, name: str, numPeaks: int, tableData: DataFrame, graphData: DataFrame,
                 graphColour: tuple, annotations: list, isToF: bool, isAnnotationsHidden: bool = False,
                 threshold: float = 100):
        self.name = name
        self.numPeaks = numPeaks
        self.annotations = annotations
        self.isToF = isToF
        self.isAnnotationsHidden = isAnnotationsHidden
        self.threshold = threshold
        pd = PeakDetector()
        try:
            self.tableData = tableData

        except errors.EmptyDataError:
            self.tableData = DataFrame()

        try:
            self.graphData = graphData

        except errors.EmptyDataError:
            self.graphData = DataFrame()

        self.graphColour = graphColour

        if not self.graphData.empty:
            self.maxima = np.array(pd.maxima(graphData, threshold))
            self.max_peak_limits_x, self.max_peak_limits_y = np.array(pd.GetMaxPeakLimits())
            self.minima = np.array(pd.minima(graphData))
            self.min_peak_limits_x, self.min_peak_limits_y = np.array(pd.GetMinPeakLimits())

        if self.numPeaks is None:
            self.numPeaks = len(self.maxima[0])

    def __eq__(self, other):
        if isinstance(other, ElementData):
            return self.name == other.name and self.isToF == other.isToF
        return False

    def __ne__(self, other):
        if isinstance(other, ElementData):
            return self.name != other.name or self.isToF != other.isToF

    def HideAnnotations(self, globalHide: bool = False):
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

    def UpdateMaximas(self):
        pd = PeakDetector()

        self.maxima = np.array(pd.maxima(self.graphData, self.threshold))
        self.max_peak_limits_x, self.max_peak_limits_y = np.array(pd.GetMaxPeakLimits())
        self.numPeaks = len(self.maxima[0])
