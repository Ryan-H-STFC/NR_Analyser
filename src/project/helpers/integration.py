from __future__ import annotations

from pandas import DataFrame
from pyparsing import Literal
from scipy.integrate import trapezoid, simpson

from helpers.nearestNumber import nearestnumber


def integrate_trapz(graphData: DataFrame, leftLimit: float, rightLimit: float) -> float:
    """
    integrate_trapz Integrates the graphdata about the given limits, using the trapezoid rule.

    Args:
        - ``graphData`` (DataFrame): graphs xy data.

        - ``leftLimit`` (float): x-coordinate for the left limit.

        - ``rightLimit`` (float): x-coordinate for the right limit.

    Returns:
        float: Integral value.
    """

    if graphData[(graphData.iloc[:, 0] >= leftLimit) & (graphData.iloc[:, 0] <= rightLimit)].empty:
        left = nearestnumber(graphData.iloc[:, 0], leftLimit)
        right = nearestnumber(graphData.iloc[:, 0], rightLimit)
        graphData = graphData[(graphData.iloc[:, 0] >= left) & (graphData.iloc[:, 0] <= right)]
    else:
        graphData = graphData[(graphData.iloc[:, 0] >= leftLimit) & (graphData.iloc[:, 0] <= rightLimit)]
    peakL = (graphData.iloc[0, 0], graphData.iloc[0, 1])
    peakR = (graphData.iloc[-1, 0], graphData.iloc[-1, 1])

    x, y = graphData.iloc[:, 0], graphData.iloc[:, 1]

    return trapezoid(y, x) - (peakR[0] - peakL[0]) * (peakL[1] + peakR[1]) / 2


def integrate_simps(graphData: DataFrame,
                    leftLimit: tuple[float],
                    rightLimit: tuple[float],
                    which: Literal['max, min'] = 'max') -> float:
    """
    integrate_simps Integrates the graphdata about the given limits, using the simpsons rule.

    Args:
        - ``graphData`` (DataFrame): graphs xy data.

        - ``leftLimit`` (tuple[float]): coordinates for the left limit.

        - ``rightLimit`` (tuple[float]): coordinates for the right limit.

    Returns:
        float: Integral value.
    """

    if graphData[(graphData.iloc[:, 0] >= leftLimit) & (graphData.iloc[:, 0] <= rightLimit)].empty:
        left = nearestnumber(graphData.iloc[:, 0], leftLimit)
        right = nearestnumber(graphData.iloc[:, 0], rightLimit)
        graphData = graphData[(graphData.iloc[:, 0] >= left) & (graphData.iloc[:, 0] <= right)]
    else:
        graphData = graphData[(graphData.iloc[:, 0] >= leftLimit) & (graphData.iloc[:, 0] <= rightLimit)]
    peakL = (graphData.iloc[0, 0], graphData.iloc[0, 1])
    peakR = (graphData.iloc[-1, 0], graphData.iloc[-1, 1])
    if peakL == peakR:
        return 0
    x, y = graphData.iloc[:, 0], graphData.iloc[:, 1]

    result = simpson(y, x)
    excess = (peakR[0] - peakL[0]) * (peakL[1] + peakR[1]) / 2
    if which == 'max':
        if excess >= result:
            mid = nearestnumber(graphData.iloc[:, 0], (rightLimit + leftLimit) / 2)
            mid = (graphData[graphData.iloc[:, 0] == mid].iloc[0, 0], graphData[graphData.iloc[:, 0] == mid].iloc[0, 1])

            return result - ((mid[0] - peakL[0]) * (peakL[1] + mid[1]) + (peakR[0] - mid[0]) * (mid[1] + peakR[1])) / 2
        else:
            return result - excess if which == 'max' else excess - result
    else:
        return excess - result
