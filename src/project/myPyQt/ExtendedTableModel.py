from __future__ import annotations
from PyQt5.QtCore import QAbstractTableModel, Qt

# todo - Add dictionary for row indexes for each section of data associated with each plotted element.


class ExtendedQTableModel(QAbstractTableModel):
    """
    Custom Data Model which allows PyQt5 QTableView to be filled with data
    using panda dataframes. Useful for much larger files with > 100 rows.
    """

    def __init__(self, data):
        super(ExtendedQTableModel, self).__init__()
        self._data = data
        self.columns: list = list(data.columns.values)
        self.titleRows = []

    def data(self, index, role):
        """
        Used to retrieve data from the data model. Also gives functionality to customise how to handle certain roles
        regarding data.

        Example: Cells of different data types should coloured differently.

        Args:
            index (QModelIndex): Used to identify the index of a specific cell in the model.
            role (QtRole): Used to describe the type of call being made by Qt, e.g. Qt.DisplayRole tells the model a
            data retrieval call is being made for displaying.

        Returns:
            QVariant: default Qt item.
            QVariant(bgcolor): QColor used for differentiating rows in the table.
            str(value): The data as string.
        """
        row: int = index.row()
        column: int = index.column()
        value = self._data.iloc[row, column]

        if role == Qt.DisplayRole:
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[section]

    def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
        return super().sort(column, order)
