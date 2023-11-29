import numpy as np


def getIndex(arr, elements, single_as_int=True):
    """Given an array and an element of it, gives back the index array where the element is found.
    Works for ordered iterables, too. Then it gives back an array of indices.
    inputs:
        - arr (np.ndarray):
            numpy array to be searched in
        - elements (int, float, list, tuple, np.ndarray):
            single element or list/tuple/array of elements to search in arr
        - single_as_int (bool):
            True: if the output is a single value, it is given as int
            False: if the output is a single value, it is given as an array of shape (1,)
    outputs:
        - outp (int/array)
            index/indices of elements in arr
    Warnings:
        - if the element occurs more than once in the array, the first indexs is returned.
        - if the element doesn't belong to the array, returns None"""
    outp = None
    if type(elements) in [int, float, np.float_]:
        elements = np.array([elements])
    if type(elements) in [list, tuple]:
        elements = np.array(elements)
    outp = np.array([np.nonzero(arr == el)[0][0] for el in elements])
    if outp is not None and np.size(outp) == 1 and single_as_int:
        outp = outp[0]
    return outp
