from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant
from PyQt5.QtGui import QColor


class ExtendedQTableModel(QAbstractTableModel):
    """
        Custom Data Model which allows PyQt5 QTableView to be filled with data 
        using panda dataframes. Useful for much larger files with > 100 rows.
    """

    def __init__(self, data):
        super(ExtendedQTableModel, self).__init__()
        self._data = data
        self.columns = list(data.columns.values)

    def data(self, index, role):
        """
        Used to retrieve data from the data model. Also gives functionality to customise how to handle certain roles regarding data.

        Example: Cells of different data types should coloured differently.

        Args:
            index (QModelIndex): Used to identify the index of a specific cell in the model.
            role (QtRole): Used to describe the type of call being made by Qt, e.g. Qt.DisplayRole tells the model a data retrieval call is being made for displaying.

        Returns:
            QVariant: default Qt item.
            QVariant(bgcolor): QColor used for differentiating rows in the table.
            str(value): The data as string.
        """
        self._data.iloc[index.row(), index.column()]
        row = index.row()
        column = index.column()
        value = self._data.iloc[index.row(), index.column()]
        header_flag: bool = False

        if index.column() == 0:
            try:
                int(value)
                header_flag = False
            except:
                header_flag = True

        if role == Qt.DisplayRole:
            return str(value)
        if role == Qt.BackgroundColorRole:
            if not self._data.columns[index.column()] == "Rank by Integral":
                return QVariant()

            if header_flag:
                bgcolor = QColor(
                    "#B0C0BC") if 'No Peaks' in value else QColor("#C9E4E5")
                return QVariant(bgcolor)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):

        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section]
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return self._data.index[section]
