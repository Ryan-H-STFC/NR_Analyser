from scipy.integrate import trapezoid, simpson

from pandas import DataFrame


def integrate_trapz(graphData: DataFrame):
    x, y = graphData.iloc[:, 0], graphData.iloc[:, 1]

    return trapezoid(y, x)


def integrate_simps(graphData: DataFrame):
    x, y = graphData.iloc[:, 0], graphData.iloc[:, 1]

    return simpson(y, x)
