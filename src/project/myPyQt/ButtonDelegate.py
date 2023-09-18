from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QItemDelegate,
    QPushButton,
    QStyle,
    QStyleOptionButton,
    QApplication
)


class ButtonDelegate(QItemDelegate):

    def __init__(self, parent=None, tableView=None, tableModel=None):
        super(ButtonDelegate, self).__init__(parent)
        self._pressed = None
        self.tableView = tableView
        self.tableModel = tableModel

    def paint(self, painter, option, index):
        painter.save()
        opt = QStyleOptionButton()
        opt.text = str(index.data())
        opt.rect = option.rect
        opt.palette = option.palette
        if self._pressed and self._pressed == (index.row(), index.column()):
            opt.state = QStyle.State_Enabled | QStyle.State_Sunken
        else:
            opt.state = QStyle.State_Enabled | QStyle.State_Raised
        QApplication.style().drawControl(QStyle.CE_PushButton, opt, painter)
        painter.restore()

    def editorEvent(self, event, model, option, index):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            # store the position that is clicked
            self._pressed = (index.row(), index.column())
            return True
        elif event.type() == QtCore.QEvent.MouseButtonRelease:
            if self._pressed == (index.row(), index.column()):
                # we are at the same place, so emit
                self.commitData(self.sender())
            elif self._pressed:
                # different place.
                # force a repaint on the pressed cell by emitting a dataChanged
                # Note: This is probably not the best idea
                # but I've yet to find a better solution.
                oldIndex = index.model().index(*self._pressed)
                self._pressed = None
                index.model().dataChanged.emit(oldIndex, oldIndex)
            self._pressed = None
            return True
        else:
            # for all other cases, default action will be fine
            return super(ButtonDelegate, self).editorEvent(event, model, option, index)

    def createEditor(self, parent, option, index):
        button = QPushButton(parent)
        button.setCheckable(True)
        button.setObjectName("tableCollapseBtn")
        button.setText(index.data())
        button.setIcon(QIcon("./src/img/expand-down-component.svg"))
        color = "#B0C0BC" if "No Peak" in index.data() else "#759395"
        button.setStyleSheet(f"background-color: {color};")
        button.toggled.connect(lambda: self.CollapseTableRows(button.isChecked(), index.row(), button))
        return button

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def CollapseTableRows(self, collapse: bool, row: int, button):
        rowCount = self.tableModel.rowCount(0)
        titleRowIndex = self.tableModel.titleRows.index(row)
        endRow = rowCount if titleRowIndex == -1 else self.tableModel.titleRows[titleRowIndex + 1]
        interval = range(row + 1, endRow)
        if collapse:
            button.setIcon(QIcon("./src/img/expand-up-component.svg"))
            for i in interval:
                self.tableView.hideRow(i)
        else:
            button.setIcon(QIcon("./src/img/expand-down-component.svg"))
            for i in interval:
                self.tableView.showRow(i)
