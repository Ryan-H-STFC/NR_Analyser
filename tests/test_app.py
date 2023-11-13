from unittest import TestCase, main
import sys
import os
from PyQt5 import QtWidgets

sys.path.append(os.path.abspath("./src/project/"))
sys.path.append(os.path.abspath("./src/project/element"))
sys.path.append(os.path.abspath("./src/project/myPyQt"))
from NRTI_NRCA_Explorer import DatabaseGUI


app = QtWidgets.QApplication(sys.argv)


class TestApp(TestCase):

    def test_plot(self):

        app = DatabaseGUI()
        app.combobox.setCurrentIndex(139)
        app.combobox.activated.emit(app.combobox.currentIndex())
        app.plotEnergyBtn.click()
        self.assertIn("29-Cu-63_n-g-Energy", [line.get_label() for line in app.ax.get_lines()])

    def test_clear(self):
        app = DatabaseGUI()
        app.combobox.setCurrentIndex(5)
        app.combobox.activated.emit(app.combobox.currentIndex())
        app.plotEnergyBtn.click()
        app.clearBtn.click()
        self.assertEqual(app.elementData, {})
        self.assertEqual(app.elementDataNames, [])
        self.assertEqual(app.plotCount, -1)
        self.assertEqual(app.plottedSubstances, [])
        self.assertEqual(app.ax.get_lines(), [])
        self.assertEqual(app.numTotPeaks, [])
        self.assertEqual(app.annotations, [])
        self.assertEqual(app.localHiddenAnnotations, [])
        self.assertEqual(app.elementDistributions, app.defaultDistributions)
        self.assertIsNone(app.table_model)
        self.assertIsNone(app.ax2)


if __name__ == '__main__':
    main(verbosity=0)
