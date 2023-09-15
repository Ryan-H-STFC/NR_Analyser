from __future__ import annotations
from dataclasses import dataclass
from pandas import DataFrame, errors
import numpy as np
from numpy import ndarray
from element.PeakDetection import PeakDetector


@dataclass(repr=True)
class ElementData:
    """
    Data class ElementData used to create a structure for each unique element selection and its data. along with
    altered python dunder functions utilised throughout the program.
    """

    name: str
    numPeaks: int
    tableData: DataFrame
    graphData: DataFrame
    graphColour: tuple
    annotations: list
    annotationsOrder: dict
    threshold: float = 100.0
    maxPeaks: int = 50
    maxima: ndarray = None
    minima: ndarray = None

    maxPeakLimitsX: ndarray = None
    maxPeakLimitsY: ndarray = None

    minPeakLimitsX: ndarray = None
    minPeakLimitsY: ndarray = None

    isToF: bool = False
    isImported: bool = False
    isGraphHidden: bool = False
    isGraphDrawn: bool = False
    isMaxDrawn: bool = False
    isMinDrawn: bool = False
    isAnnotationsHidden: bool = False
    isAnnotationsDrawn: bool = False

    def __init__(self,
                 name: str,
                 numPeaks: int,
                 tableData: DataFrame,
                 graphData: DataFrame,
                 graphColour: tuple,
                 isToF: bool,
                 isAnnotationsHidden: bool = False,
                 threshold: float = 100,
                 isImported: bool = False) -> None:

        self.name = name
        self.numPeaks = numPeaks
        self.isToF = isToF
        self.annotations = []
        self.annotationsOrder = {}
        self.isAnnotationsHidden = isAnnotationsHidden
        self.threshold = threshold
        self.isImported = isImported
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
            self.maxPeakLimitsX, self.maxPeakLimitsY = np.array(
                pd.GetMaxPeakLimits()
            )
            self.minima = np.array(pd.minima(graphData))
            self.minPeakLimitsX, self.minPeakLimitsY = np.array(
                pd.GetMinPeakLimits()
            )

        if self.numPeaks is None:
            self.numPeaks = len(self.maxima[0])

    def __eq__(self, other) -> bool:
        if isinstance(other, ElementData):
            return self.name == other.name and self.isToF == other.isToF
        return False

    def __ne__(self, other) -> bool:
        if isinstance(other, ElementData):
            return self.name != other.name or self.isToF != other.isToF

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

    def UpdateMaximas(self) -> None:
        pd = PeakDetector()
        self.maxima = np.array(pd.maxima(self.graphData, self.threshold))
        self.maxPeakLimitsX, self.maxPeakLimitsY = np.array(pd.GetMaxPeakLimits())
        self.numPeaks = len(self.maxima[0])

    def GetPeakLimits(self, max: bool = True) -> tuple[ndarray[float]]:
        if max:
            return (self.maxPeakLimitsX, self.maxPeakLimitsY)
        return (self.minPeakLimitsX, self.minPeakLimitsY)

    def OrderAnnotations(self, byIntegral: bool = True) -> None:
        """
        OrderAnnotations alters the rank value assoicated with each peak in the annotations dictionary
        either ranked by integral or by peak width

        Args:
            byIntegral (bool, optional): Sorted by Integral (True) else by Peak Width (False). Defaults to True.
        """
        self.annotationsOrder.clear()
        if self.numPeaks == 0:
            return
        if self.isImported:
            return

        if self.tableData[1:].empty:
            return

        rankCol = "Rank by Integral" if byIntegral else "Rank by Peak Width"
        compareCol = "TOF (us)" if self.isToF else "Energy (eV)"
        for max_x, max_y in self.maxima.T[0:self.numPeaks]:
            tableMax_x = nearestnumber(self.tableData[compareCol][1:], max_x)

            row = self.tableData[1:].loc[
                (self.tableData[compareCol][1:].astype(float) == tableMax_x)
            ]

            if row.empty:
                index = None
            else:
                index = (
                    row[rankCol].iloc[0]
                    if "(" not in str(row[rankCol].iloc[0])
                    else row[rankCol].iloc[0][1:-1]
                )
            self.annotationsOrder[int(index)] = (max_x, max_y)


def nearestnumber(x: list[float], target: float) -> float:
    """
    Find the closet value in a list to the input target value

    Args:
        x (list[float]): List of x-coords being plotted
        target (float): Value of mouse x-coord

    Returns:
        float: Nearest value in x from target
        None: If searching null list.
    """
    try:
        array = np.asarray(x)
        value_index = (
            np.abs(array - target)
        ).argmin()  # Finds the absolute difference between the value and the target
        # then gives the smallest number in the array and returns it
        return array[value_index]

    except ValueError:
        return None
