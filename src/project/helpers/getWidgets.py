from pyparsing import Generator
from PyQt5.QtWidgets import QWidget


def getLayoutWidgets(layout, widgetType: type = None) -> Generator[QWidget, None, None]:
    """
    ``getLayoutWidgets`` returns a list of widgets from an inputted layout. Will return specific widgets of a specified 
    type using ``widgetType``

    Args:
        ``layout`` (PyQt Layout): PyQt Layout Object
        ``widgetType``(type): Specified type of widgets to find within layout
    Returns:
        List:QtWidgets: List of widgets within the layout
    """
    if layout is None:
        return
    if widgetType is None:
        return [layout.itemAt(i).widget() for i in range(layout.count())]

    return [layout.itemAt(i).widget() for i in range(layout.count())
            if type(layout.itemAt(i).widget()) == widgetType]
