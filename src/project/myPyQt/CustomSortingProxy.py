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
        """Custom Sorting Function, based on which type of data in each column of the table, adjust how the values will
         be sorted. Defaulting to the normal ``QSortFilterProxyModel.lessThan`` results. 

        Args:
            left (QModelIndex): Value on the left of the < operation
            right (QModelIndex): Value on the right of the < operation

        Returns:
            bool: Result of operation
        .. code-block:: text
            left.data() < right.data()
        """
        col = left.column()
        dataLeft = left.data()
        dataRight = right.data()

        if col == 0:
            # Rank of Integral (int)
            return int(dataLeft) < int(dataRight)
        if col in [2, 6]:
            # Rank of ... in format (123) (int)
            return int(dataLeft[1:-1]) < int(dataRight[1:-1])
        if col in [1, 3, 4, 5, 7]:
            # Numerical Data (float)
            return float(dataLeft) < float(dataRight)

        return super(QSortFilterProxyModel, self).lessThan(left, right)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:

        return super().filterAcceptsRow(source_row, source_parent)
