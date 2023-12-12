from __future__ import annotations
import numpy as np


def getSpacedElements(array: np.ndarray, numElements: int) -> np.ndarray:
    """
    ``getSpacedElements``
    ---------------------

    Returns an evenly spaced subset of ``numElements`` from the given ``array``.

    Args:
        array (np.ndarray): Input array
        numElements (int): Number of elements to return

    Returns:
        np.ndarray: An evenly distributed subset of ``array``
    """
    return array[np.round(np.linspace(0, array.shape[0] - 1, numElements)).astype(int)]
