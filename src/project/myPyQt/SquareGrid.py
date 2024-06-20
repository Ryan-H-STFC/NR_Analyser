from __future__ import annotations

from PyQt6.QtWidgets import (
    QGridLayout,
    QWidget
)


class SquareGrid(QGridLayout):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, a0: int) -> int:
        return a0
