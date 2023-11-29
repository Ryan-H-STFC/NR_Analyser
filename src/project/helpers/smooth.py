import numpy as np


def smooth(arr: np.ndarray, it: int):
    """
    ``smooth``
    ----------
    Smooths an array. If it has two axes, (x being 0th and y being 1st row), y axes is smoothed.
    The smoothing mesh can be outlined as {1 2 1}/4
    inputs:
        - arr: (np.ndarray):
            numpy array to smooth.
        -it: (int)
            number of iterations
    outputs:
        - smoothed array"""
    if not isinstance(it, int):
        return
    if len(np.shape(arr)) > 1:
        arr0 = np.copy(arr)[1]
    else:
        arr0 = np.copy(arr)
    for j in range(it):
        temp = [0.]
        for i in range(1, np.size(arr0) - 1):
            temp.append((arr0[i - 1] + 2 * arr0[i] + arr0[i + 1]) / 4)
        temp.append(0.)
        arr0 = np.copy(np.array(temp))
    if len(np.shape(arr)) > 1 and np.shape(arr)[0] > 1:
        arr0 = [arr[0], arr0]
        for i in range(2, np.shape(arr)[0]):
            arr0.append(arr[i])
    return np.array(arr0)
