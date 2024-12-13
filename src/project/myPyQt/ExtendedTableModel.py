from __future__ import annotations
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtWidgets import QTableView
from pandas import DataFrame, concat

from project.myPyQt.CustomSortingProxy import CustomSortingProxy

# todo - Add dictionary for row indexes for each section of data associated with each plotted element.


class ExtendedQTableModel(QAbstractTableModel):
    """
    Custom Data Model which allows PyQt5 QTableView to be filled with data
    using panda dataframes. Useful for much larger files.
    """

    def __init__(self, data, parent=None):
        super(ExtendedQTableModel, self).__init__()
        self._data: DataFrame = data
        self.gui = parent
        self.columns: list[str] = list(data.columns.values)
        # self.titleRows: list[int] = list(data.loc[data['Integral'] == ''].index)
        # self.titleRows.append(data.shape[0])
        # self.splitData = [data.iloc[self.titleRows[n]:self.titleRows[n + 1]] for n in range(len(self.titleRows) - 1)]

    def data(self, index: QModelIndex, role: Qt.ItemDataRole):
        """
        Used to retrieve data from the data model. Also gives functionality to customise how to handle certain roles
        regarding data.

        Example: Cells of different data types should coloured differently.

        Args:
            index (QModelIndex): Used to identify the index of a specific cell in the model.
            role (Qt.ItemDataRole): Used to describe the type of call being made by Qt, e.g. Qt.DisplayRole tells the
            model a data retrieval call is being made for displaying.

        Returns:
            QVariant: default Qt item.
            QVariant(bgcolor): QColor used for differentiating rows in the table.
            str(value): The data as string.
        """
        row: int = index.row()
        column: int = index.column()
        value = self._data.iloc[row, column]

        if role == Qt.ItemDataRole.DisplayRole:
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.columns[section]
        if orientation == Qt.Orientation.Vertical and role == Qt.ItemDataRole.DisplayRole:
            return self._data.index[section]

    # def sort(self, column: int, order: Qt.SortOrder = ...) -> None:
    #     proxy = CustomSortingProxy()
    #     proxy.setSourceModel(self)
    #     proxy.sort(column, order)
    #     self.gui.table.setModel(self)
    #     # if column == -1:
    #     #     return super().sort(column, order)
    #     # sortedData = []
    #     # for data in self.splitData:

    #     #     sortedData.append(concat([
    #     #         data[0:1],
    #     #         data[1:].sort_values(
    #     #             by=self.columns[column], ascending=not order.value, ignore_index=True)],
    #     #         ignore_index=True))

    #     # concat(sortedData, ignore_index=True)
