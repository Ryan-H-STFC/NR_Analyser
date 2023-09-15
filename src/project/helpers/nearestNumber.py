import numpy as np


def nearestnumber(x: list[float], target: float) -> float:
    """
    Find the closet value in a list the the input target value

    Args:
        x (list[float]): List of x-coords being plotted
        target (float): Value of mouse x-coord

    Returns:
        float: Nearest value in x from target
    """
    array = np.asarray(x)
    value_index = (
        np.abs(array - target)
    ).argmin()  # Finds the absolute difference between the value and the target
    # then gives the smallest number in the array and returns it
    return array[value_index]
