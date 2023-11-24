import pandas as pd
import numpy as np


def getDerivative(graphData: pd.DataFrame, xValue: float) -> float:

    return np.gradient(graphData[1], graphData[0])[graphData[graphData[0] == xValue].index[0]]
