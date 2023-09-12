from __future__ import annotations
from PyQt5.QtCore import QModelIndex, QSortFilterProxyModel


class CustomSortingProxy(QSortFilterProxyModel):
    """
    Custom Sorting Proxy, allows the columns of the table to be sorted based on the type of its data.

    Args:
        QSortFilterProxyModel (Class): Parent Class which CustomSorting Proxy
    """
    def __init__(self):
        super(QSortFilterProxyModel, self).__init__()

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        col = left.column()
        dataLeft = left.data()
        dataRight = right.data()

        match (col):
            case 0:
                # Rank of Integral (int)
                dataLeft = int(dataLeft)
                dataRight = int(dataRight)
            case 2 | 6:
                # Rank of ... in format (123) (int)
                dataLeft = int(dataLeft[1:-1])
                dataRight = int(dataRight[1:-1])
            case 1 | 3 | 4 | 5 | 7:
                # Numerical Data (float)
                dataLeft = float(dataLeft)
                dataRight = float(dataRight)

        return dataLeft < dataRight
