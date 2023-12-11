from __future__ import annotations
from numpy.random import random


def getRandomColor() -> tuple[float]:
    """
    Returns a random color, with muted extremities.

    ``Red``:  \t(0.1 to 0.9)

    ``Green``:\t(0.2 to 0.7)

    ``Blue`` :\t(0.1 to 0.9)

    Returns:
        tuple[float]: (R,G,B) color.
    """
    return (random() * 0.8 + 0.1,
            random() * 0.5 + 0.2,
            random() * 0.8 + 0.1)
