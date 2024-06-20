from __future__ import annotations


def interpName(name: str = None) -> dict[str | None]:
    """
    ``interName``
    -------------

    Takes in the standard naming format for elements or isotopes and returns a dictionary containing its:
    - zNumber
    - Element Name
    - nNumber
    - mode

    Examples:

    '82-Pb-207_n-g'       ---> {'nNum': '82', 'symbol': 'Pb', 'zNum': '207', 'mode': 'n-g'}
    'element_78-Pt_n-tot' --> {'nNum': '78', 'symbol': 'Pt', 'zNum': None, 'mode': 'n-tot'}

    Args:
        name (str): Standard format name of element or isotope

    Returns:
        dict[str | None]: {'nNum', 'symbol', 'zNum', 'mode'}
    """
    try:

        isoName = name.split('_')[0] if name.count('_') == 1 else name.split('_')[1]
        mode = name.split('_')[-1]

        nNum = isoName.split('-')[0]
        ele = isoName.split('-')[1]
        zNum = isoName.split('-')[2] if isoName.count('-') > 1 else None

        return {
            'nNum': nNum,
            'symbol': ele,
            'zNum': zNum,
            'mode': mode
        }
    except (IndexError, AttributeError):
        return {
            'nNum': None,
            'symbol': None,
            'zNum': None,
            'mode': None
        }


def constructName(info: dict[str]) -> str:
    """
    ``constructName``
    -----------------

    Takes in a dictionary in a standard format given from ``interpName`` and returns its original name.
    - zNumber
    - Element Name
    - nNumber
    - mode

    Examples:

    {'nNum': '82', 'symbol': 'Pb', 'zNum': '207', 'mode': 'n-g'} ---> '82-Pb-207_n-g'
    {'nNum': '78', 'symbol': 'Pt', 'zNum': None, 'mode': 'n-tot'} --> 'element_78-Pt_n-tot'

    Args:
        info (dict[str]): _description_

    Returns:
        str: _description_
    """
    if info['zNum'] is None:
        return f"element_{info['nNum']}-{info['symbol']}_{info['mode']}"
    return f"{info['nNum']}-{info['symbol']}-{info['zNum']}_{info['mode']}"
