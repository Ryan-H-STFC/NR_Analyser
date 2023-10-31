from __future__ import annotations


def supremum(x: list[float], target: float) -> float | None:
    """
    ``supremum`` Finds the supremum of ``target`` for a given list ``x``.

    Args:
        ``x`` (list[float]): List to search.

        ``target`` (float): Value to find supremum for.

    Returns:
        float | None: The Supremum for the given target values. None if ``x`` is empty or not of type list[float].
    """
    try:
        return x[x < target].max()
    except ValueError:
        return None


def infimum(x: list[float], target: float) -> float | None:
    """
    ``infimum`` Finds the infimum of ``target`` for a given list ``x``.

    Args:
        ``x`` (list[float]): List to search.

        ``target`` (float): Value to find infimum for.

    Returns:
        float | None: The Infimum for the given target values. None if ``x`` is empty or not of type list[float].
    """
    try:
        return x[x > target].min()
    except ValueError | TypeError:
        return None


def linInterpY(data, x: float) -> float | None:
    try:
        GLB = infimum(data['x'], x)  # X1
        LUB = supremum(data['x'], x)  # X2

        GLB_Y = float(data.loc[data['x'] == GLB]['y'].iloc[0])  # Y1
        LUB_Y = float(data.loc[data['x'] == LUB]['y'].iloc[0])  # Y2

        return (LUB_Y - GLB_Y) / (LUB - GLB) * (x - GLB) + GLB_Y

    except TypeError:
        return float(data['y'].iloc[-1])

    except ValueError:
        # data.empty == True
        return None
