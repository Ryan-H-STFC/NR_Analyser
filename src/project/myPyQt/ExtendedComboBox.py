from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QComboBox, QCompleter, QSizePolicy
from PyQt5.QtCore import Qt, QSortFilterProxyModel


class ExtendedComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ExtendedComboBox, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.pFilterModel.setSourceModel(self.model())

        self.completer = QCompleter(self.pFilterModel, self)
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        self.lineEdit().textEdited[str].connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.onCompleterActivated)
        self.completer.popup().setStyleSheet("font-family: 'Roboto Mono'; font-size: 10pt; font-weight: 400;")

        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred))

    def onCompleterActivated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            self.activated[str].emit(self.itemText(index))

    def setModel(self, model):
        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if e.key() == 16777220:
            proxyIndex = self.pFilterModel.index(0, 0)
            index = self.pFilterModel.mapToSource(proxyIndex)
            self.setCurrentIndex(index.row())

        return super(ExtendedComboBox, self).keyPressEvent(e)

    def getAllItemText(self):
        return [self.itemText(i) for i in range(self.count())]
