from __future__ import annotations

import numpy as np


def getSpacedElements(array: np.ndarray, numElements: int) -> np.ndarray:
    return array[np.round(np.linspace(0, array.shape[0] - 1, numElements)).astype(int)]
