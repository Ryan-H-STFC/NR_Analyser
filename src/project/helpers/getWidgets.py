from pyparsing import Generator
from PyQt5.QtWidgets import QWidget


def getLayoutWidgets(layout) -> Generator[QWidget, None, None]:
    """
    getLayoutWidgets returns a list of widgets from an inputted layout.

    Args:
        layout (PyQt Layout): PyQt Layout Object

    Returns:
        List:QtWidgets: List of widgets within the layout.
    """
    return (layout.itemAt(i).widget() for i in range(layout.count()))
