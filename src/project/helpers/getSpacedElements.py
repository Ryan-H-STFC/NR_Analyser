import numpy as np


def getSpacedElements(array, numElements):
    return array[np.round(np.linspace(0, array.shape[0] - 1, numElements)).astype(int)]
