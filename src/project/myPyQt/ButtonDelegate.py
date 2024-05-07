from PyQt6 import QtCore
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QItemDelegate,
    QPushButton,
    QStyle,
    QStyleOptionButton,
    QApplication
)
from project.settings import params


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
            opt.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Sunken
        else:
            opt.state = QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Raised
        QApplication.style().drawControl(QStyle.ControlElement.CE_PushButton, opt, painter)
        painter.restore()

    def editorEvent(self, event, model, option, index):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            # store the position that is clicked
            self._pressed = (index.row(), index.column())
            return True
        elif event.type() == QtCore.QEvent.Type.MouseButtonRelease:
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
        color = "#7D9797" if "No Peak" in index.data() else "#507373"
        button.setStyleSheet(f"""background-color: {color};
                             border-radius: 0px;
                             color: #FFF;
                             """)
        if "No Peak" not in index.data():
            button.setIcon(QIcon(f"{params['dir_img']}expand-down-component.svg"))
            button.toggled.connect(lambda: self.collapseTableRows(button.isChecked(), index.row(), button))
        return button

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def collapseTableRows(self, collapse: bool, row: int, button):
        rowCount = self.tableModel.rowCount(0)
        titleRowIndex = self.tableModel.titleRows.index(row)
        endRow = rowCount if titleRowIndex == -1 else self.tableModel.titleRows[titleRowIndex + 1]
        interval = range(row + 1, endRow)
        if collapse:
            button.setIcon(QIcon(f"{params['dir_img']}expand-up-component.svg"))
            for i in interval:
                self.tableView.hideRow(i)
        else:
            button.setIcon(QIcon(f"{params['dir_img']}expand-down-component.svg"))
            for i in interval:
                self.tableView.showRow(i)
