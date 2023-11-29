import numpy as np


def fitBoxes(array, dboxes):
    """Forces all the y values of an array to be fit within a made-up mesh of a certain amount of points.
    This amount of points is actually given by as a density, so that num_points = (y_max - y_min)*density
    inputs:
        -array: (np.ndarray):
            numpy array to fit
        - dboxes:
            density of points/boxes
    outputs:
        -fitted data as an array of the same shape, box width"""
    try:
        b0 = np.min(array)
        b1 = np.max(array)
        nboxes = dboxes * (b1 - b0)
        norm = (array - b0) / (b1 - b0)
        fitn = np.around(norm * (nboxes - 1)) / (nboxes - 1)
        fit = (b1 - b0) * fitn + b0
        return fit, (b1 - b0) / (2 * nboxes)
    except Exception:
        return None, None
