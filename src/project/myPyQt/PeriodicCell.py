from __future__ import annotations
from PyQt6.QtGui import QMouseEvent, QResizeEvent
from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QObject, QEvent

classes = {
    '57-71': 'top',
    '79-103': 'middle',
    '6': 'middle',
    '7': 'bottom'
}

colors = {
    'Alkali Metal': '#6c3b01',
    'Alkaline Earth Metal': '#846011',
    'Lanthanoid': '#402c17',
    'Actinoid': '#732e4c',
    'Transition Metal': '#711019',
    'Post-Transition Metal': '#003666',
    'Metalloid': '#015146',
    'Reactive Non-Metal': '#3e6418',
    'Unstable': '#111',
    'Noble Gas': '#3a2151',
    'Filler': '#00b'
}


class ElementCell(QWidget):

    cellLayout: QVBoxLayout

    name: str
    type: str
    nNum: int
    weight: float

    def __init__(self, info: dict, parent) -> None:
        super(QWidget, self).__init__(parent)
        self.table = parent
        self.symbol = info['symbol']
        self.nNum = info['nNum']
        self.name = info['name']
        self.zNum = info['zNum']
        self.weight = info['weight']
        self.type = info['type']
        self.stability = info['stability']
        self.setObjectName(self.type.replace(' ', ''))
        proxyWidget = QWidget(self.table)

        if self.nNum is None:
            proxyWidget.setObjectName('Filler')
        else:
            proxyWidget.setObjectName('cell')
        cellLayout = QVBoxLayout()
        self.nNumLabel = QLabel(text=None if self.nNum is None else str(self.nNum))
        self.symbolLabel = QLabel(text=self.symbol)
        self.nameLabel = QLabel(text=None if self.name is None else self.name)
        self.weightLabel = QLabel(text=None if self.weight is None else str(
            self.weight if self.zNum is None else self.zNum))

        self.nameLabel.setMaximumHeight(10)
        self.nNumLabel.setMaximumHeight(10)
        self.symbolLabel.setMaximumHeight(16)
        self.weightLabel.setMaximumHeight(10)

        self.nameLabel.setObjectName("name")
        self.nNumLabel.setObjectName("nNum")
        self.symbolLabel.setObjectName("symbol")
        self.weightLabel.setObjectName("weight")
        if self.symbol in ['57-71', '79-103', '6', '7']:
            proxyWidget.setProperty('class', classes[self.symbol])

        self.setContentsMargins(0, 0, 0, 0)

        align = Qt.AlignmentFlag.AlignRight if self.nNum is None else Qt.AlignmentFlag.AlignLeft
        cellLayout.addWidget(self.nNumLabel, align)
        cellLayout.addWidget(self.symbolLabel, align)
        cellLayout.addWidget(self.nameLabel, align)
        cellLayout.addWidget(self.weightLabel, align)
        proxyLayout = QVBoxLayout()
        proxyWidget.setLayout(cellLayout)

        proxyLayout.addWidget(proxyWidget)
        proxyLayout.setContentsMargins(0, 0, 0, 0)
        proxyLayout.setSpacing(0)
        self.setLayout(proxyLayout)
        sizePolicy = QSizePolicy()
        sizePolicy.setHorizontalPolicy(QSizePolicy.Policy.Ignored)
        sizePolicy.setVerticalPolicy(QSizePolicy.Policy.Ignored)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(100, 100)

    def mouseReleaseEvent(self, a0: QMouseEvent | None) -> None:
        if self.nNum is None:
            return
        if self.objectName() == 'iso':
            self.table.isoSelect(self)
        else:
            self.table.onSelect(self)
        return super().mouseReleaseEvent(a0)

    def eventFilter(self, obj: QObject | None, event: QEvent | None, ) -> bool:
        if event.type() == QEvent.Type.HoverEnter:
            self.table.onSelect(self)
        if event.type() == QEvent.Type.HoverLeave:
            pass

        return super().eventFilter(obj, event)

    def resizeEvent(self, a0: QResizeEvent | None) -> None:
        height = self.table.window().sizeHint().height() // 9
        color = colors.get(self.type if self.stability else 'Unstable', '#444')
        self.setStyleSheet(f"""
                *{{
                    padding: 0px;
                    margin: 0px;
                }}
                QWidget#cell, QWidget#Filler, #QWidget#iso{{
                    background-color: {color};
                    border: 1px solid #444;
                }}
                QLabel#Filler{{
                    font-size: {max(height // 24, 8)}pt;
                }}
                QWidget#cell:hover, QWidget#iso:hover{{
                    border: 1px solid #FFF;
                }}
                QLabel#nNum, QLabel#name, QLabel#weight{{
                    color: #DEDEDE;
                    font-size: {max(height // 24, 8)}pt;
                    font-weight: 600;
                }}
                QLabel#symbol{{
                    color: #FFF;
                    font-size: {max(height // 15, 12)}pt;
                    font-weight: 800;
                }}
                """)
        self.nameLabel.adjustSize()
        return super().resizeEvent(a0)

    def heightForWidth(self, a0: int) -> int:
        return a0

    def hasHeightForWidth(self) -> bool:
        return True
