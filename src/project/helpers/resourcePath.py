import os
import sys


def resource_path(relative_path: str) -> str:
    """
    ``resource_path``
    -----------------

    Credits:
    - https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file

    Args:
        relative_path (str): Relative path.

    Returns:
        str: resource path used by pyinstaller build.
    """
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
