
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

    '82-Pb-207_n-g'       -> {'zNum': '82', 'symbol': 'Pb', 'nNum': '207', 'mode': 'n-g'}
    'element_78-Pt_n-tot' -> {'zNum': '78', 'symbol': 'Pt', 'nNum': None, 'mode': 'n-tot'}

    Args:
        name (str): Standard format name of element or isotope

    Returns:
        dict[str | None]: {'zNum', 'symbol', 'nNum', 'mode'}
    """
    try:

        isoName = name.split('_')[0] if name.count('_') == 1 else name.split('_')[1]
        mode = name.split('_')[-1]

        zNum = isoName.split('-')[0]
        ele = isoName.split('-')[1]
        nNum = isoName.split('-')[2] if isoName.count('-') > 1 else None

        return {'zNum': zNum,
                'symbol': ele,
                'nNum': nNum,
                'mode': mode
                }
    except (IndexError, AttributeError):
        return {'zNum': None,
                'symbol': None,
                'nNum': None,
                'mode': None
                }
