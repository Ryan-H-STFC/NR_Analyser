from dataclasses import dataclass
from PeakDetection import PeakDetection
from pandas import DataFrame, errors


@dataclass(repr=True)
class ElementData:
    """
    Data class ElementData used to create a structure for each unique element
    selection and its data. along with altered python dunder functions utilised
    throughout the program.
    """

    _name: str
    _numPeaks: int
    _tableData: list
    _graphData: list
    _annotations: list
    _maxima: list = None
    _minima: list = None

    _isToF: bool = False
    isGraphHidden: bool = False
    isAnnotationsHidden: bool = False

    def __init__(self, name: str, numPeaks: int, tableData: DataFrame, graphData: DataFrame,
                 annotations: list, isToF: bool, isAnnotationsHidden: bool = False):
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

        if not self._graphData.empty:
            self._maxima = pd.maxima(graphData)
            self._minima = pd.minima(graphData)

    def __eq__(self, other):
        if isinstance(other, ElementData):
            return self._name == other._name and self._isToF == other._isToF
        return False

    def __ne__(self, other):
        if isinstance(other, ElementData):
            return self._name != other._name or self._isToF != other._isToF
