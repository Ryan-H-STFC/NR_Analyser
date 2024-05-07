from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QVBoxLayout
)
from project.myPyQt.ExtendedComboBox import ExtendedComboBox


class InputSpectraDialog(QDialog):

    def __init__(self, parent=None, styleSheet: str = None) -> None:
        super(InputSpectraDialog, self).__init__(parent)
        self.setObjectName('inputWindow')
        if styleSheet is None:
            self.setStyleSheet(f"""
            *{{
                font-family: 'Roboto Mono';
                font-size: 10pt;
                font-weight: 400;
            }}
            #inputWindow{{
                color: {parent.text_color};
                background-color:{parent.bg_color};
            }}
            #inputWindow QLabel{{
                color: {parent.text_color};
            }}
            """)

        self.mainLayout = QVBoxLayout()
        self.inputForm = QFormLayout()

        self.inputForm.setObjectName('inputForm')

        self.spectras = ExtendedComboBox()

        self.buttonBox = QDialogButtonBox()

        self.mainLayout.addWidget(self.spectras)
        self.mainLayout.addWidget(self.buttonBox)
        self.setUpdatesEnabled(True)

        self.motionEvent = None
        self.buttonPressEvent = None
        self.tof = None
