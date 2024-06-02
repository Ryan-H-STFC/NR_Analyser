from typing import overload
from PyQt6.QtWidgets import (
    QLabel,
    QWidget,
    QVBoxLayout
)
from PyQt6.QtCore import Qt
from pyparsing import Literal


class ElementCell(QWidget):

    cellLayout: QVBoxLayout

    name: str
    type: str
    nNum: int
    weight: float

    styleSheet: str = """
    QLabel#nNum, QLabel#name, QLabel#weight{
        color: #FFF;
        text-size: 10;
    }
    QLabel#symbol{
        color: #B5B5B5;
        text-size: 16;
    }
    QLabel#name{
        color: #FFF;
        text-size: 10;
    }
    QLabel#weight{
        color: #FFF;
        text-size: 10;
    }
    QWidget#AlkaliMetal {
        background-color: #6c3b01 ;
    }
    QWidget#AlkalineEarthMetal {
        background-color: #846011 ;
    }
    QWidget#Lanthanoid {
        background-color: #402c17 ;
    }
    QWidget#Actinoid {
        background-color: #732e4c ;
    }
    QWidget#TransitionMetal {
        background-color: #711019 ;
    }
    QWidget#Post-transitionMetal {
        background-color: #003666 ;
    }
    QWidget#Metalloid {
        background-color: #015146 ;
    }
    QWidget#ReactiveNon-Metal {
        background-color: #3e6418 ;
    }
    QWidget#Unstable {
        background-color: #222222 ;
    }
    QWidget#NobleGas {
        background-color: #3a2151 ;
    }"""

    @overload
    def __init__(self, symbol: str, info: dict) -> None:
        self.symbol = symbol
        self.nNum = info['nNum']
        self.name = info['name']
        self.weight = info['weight']
        self.type = info['type']

        cellLayout = QVBoxLayout(self)
        nNumLabel = QLabel(text=str(self.nNum))
        nNumLabel.setObjectName("nNum")
        symbolLabel = QLabel(text=symbol)
        symbolLabel.setObjectName("symbol")
        nameLabel = QLabel(text=self.name)
        nameLabel.setObjectName("name")
        weightLabel = QLabel(text=str(self.weight))
        weightLabel.setObjectName("weight")

        cellLayout.addWidget(nNumLabel, Qt.AlignmentFlag.AlignLeft)
        cellLayout.addWidget(symbolLabel, Qt.AlignmentFlag.AlignLeft)
        cellLayout.addWidget(nameLabel, Qt.AlignmentFlag.AlignLeft)
        cellLayout.addWidget(weightLabel, Qt.AlignmentFlag.AlignLeft)

    @overload
    def __init__(self,
                 nNum: str,
                 symbol: str,
                 name: str,
                 weight: float,
                 type: Literal[
                     'Alkali Metal',
                     'Alkaline Earth Metal',
                     'Lanthanoid',
                     'Actinoid',
                     'Transition Metal',
                     'Post-transition Metal',
                     'Metalloid',
                     'Reactive Non-Metal',
                     'Transactinide',
                     'Superactinide'
                     'Noble Gas']
                 ):
        self.nNum - nNum
        self.symbol = symbol
        self.name = name
        self.weight = weight
        self.type = type

        cellLayout = QVBoxLayout(self)
        nNumLabel = QLabel(text=str(nNum))
        nNumLabel.setObjectName("nNum")
        symbolLabel = QLabel(text=symbol)
        symbolLabel.setObjectName("symbol")
        nameLabel = QLabel(text=name)
        nameLabel.setObjectName("name")
        weightLabel = QLabel(text=str(weight))
        weightLabel.setObjectName("weight")

        cellLayout.addWidget(nNumLabel, Qt.AlignmentFlag.AlignLeft)
        cellLayout.addWidget(symbolLabel, Qt.AlignmentFlag.AlignLeft)
        cellLayout.addWidget(nameLabel, Qt.AlignmentFlag.AlignLeft)
        cellLayout.addWidget(weightLabel, Qt.AlignmentFlag.AlignLeft)

        self.setObjectName(type.strip(' '))


ElementCell()
