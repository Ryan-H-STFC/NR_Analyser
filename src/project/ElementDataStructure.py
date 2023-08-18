from dataclasses import dataclass
from pandas import DataFrame, errors
import numpy as np
from PeakDetection import PeakDetection


@dataclass(repr=True)
class ElementData:
    """
    Data class ElementData used to create a structure for each unique element selection and its data. along with
    altered python dunder functions utilised throughout the program.
    """

    _name: str
    _numPeaks: int
    _tableData: list
    _graphData: list
    _graphColour: tuple
    _annotations: list
    _maxima: list = None
    _minima: list = None

    max_peak_limits_x: dict = None
    max_peak_limits_y: dict = None

    min_peak_limits_x: dict = None
    min_peak_limits_y: dict = None
    _isToF: bool = False
    isGraphHidden: bool = False
    isAnnotationsHidden: bool = False
    isAnnotationsDrawn: bool = False

    def __init__(self, name: str, numPeaks: int, tableData: DataFrame, graphData: DataFrame,
                 graphColour: tuple, annotations: list, isToF: bool, isAnnotationsHidden: bool = False):
        self._name = name
        self._numPeaks = numPeaks
        self._annotations = annotations
        self._isToF = isToF
        self.isAnnotationsHidden = isAnnotationsHidden
        pd = PeakDetection()
        try:
            self._tableData = tableData

        except errors.EmptyDataError:
            self._tableData = DataFrame()

        try:
            self._graphData = graphData

        except errors.EmptyDataError:
            self._graphData = DataFrame()

        self._graphColour = graphColour

        if not self._graphData.empty:
            self._maxima = np.array(pd.maxima(graphData))
            self.max_peak_limits_x, self.max_peak_limits_y = np.array(pd.GetMaxPeakLimits())
            self._minima = np.array(pd.minima(graphData))
            self.min_peak_limits_x, self.min_peak_limits_y = np.array(pd.GetMinPeakLimits())

    def __eq__(self, other):
        if isinstance(other, ElementData):
            return self._name == other._name and self._isToF == other._isToF
        return False

    def __ne__(self, other):
        if isinstance(other, ElementData):
            return self._name != other._name or self._isToF != other._isToF

    def HideAnnotations(self, globalHide: bool = False):
        """
        HideAnnotations will only hide if 'Hide Peak Label' is checked, or the graph is hidden,
        otherwise it will show the annotation.

        Args:
            globalHide (bool, optional): Wheher or not the 'Hide Peak Label' is checked or not. Defaults to False.
        """
        if self._annotations == []:
            return

        boolCheck = not (globalHide or self.isGraphHidden)
        for point in self._annotations:
            point.set_visible(boolCheck)
        self.isAnnotationsHidden = boolCheck
