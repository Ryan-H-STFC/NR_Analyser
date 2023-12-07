import sys
import os
from unittest import TestCase, main
from PyQt5 import QtWidgets

sys.path.append(os.path.abspath("./src/project/"))
sys.path.append(os.path.abspath("./src/project/element"))
sys.path.append(os.path.abspath("./src/project/myPyQt"))
from NRTI_NRCA_Explorer import ExplorerGUI

app = QtWidgets.QApplication(sys.argv)


class TestApp(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def test_plot(self):
        app = ExplorerGUI()
        app.combobox.setCurrentIndex(139)
        app.combobox.activated.emit(app.combobox.currentIndex())
        app.plotEnergyBtn.click()
        self.assertIn("29-Cu-63_n-g-Energy", [line.get_label() for line in app.ax.get_lines()])
        self.assertTrue(app.spectraData["29-Cu-63_n-g-Energy"].isGraphDrawn)

    def test_clear(self):
        app = ExplorerGUI()
        app.combobox.setCurrentIndex(5)
        app.combobox.activated.emit(app.combobox.currentIndex())
        app.plotEnergyBtn.click()
        app.clearBtn.click()
        self.assertEqual(app.spectraData, {})
        self.assertEqual(app.elementDataNames, [])
        self.assertEqual(app.plotCount, -1)
        self.assertEqual(app.plottedSpectra, [])
        self.assertEqual(app.ax.get_lines(), [])
        self.assertEqual(app.annotations, [])
        self.assertEqual(app.localHiddenAnnotations, [])
        self.assertEqual(app.elementDistributions, app.defaultDistributions)
        self.assertIsNone(app.table_model)
        self.assertIsNone(app.axPD)

    def test_toggle_states(self):
        app = ExplorerGUI()
        # ¦ Null Selection
        self.assertFalse(app.plotEnergyBtn.isEnabled())
        self.assertFalse(app.plotTOFBtn.isEnabled())
        self.assertFalse(app.clearBtn.isEnabled())
        self.assertFalse(app.pdBtn.isEnabled())
        self.assertFalse(app.gridCheck.isEnabled())
        self.assertFalse(app.thresholdCheck.isEnabled())
        self.assertFalse(app.peakLabelCheck.isEnabled())

        app.combobox.setCurrentIndex(5)
        app.combobox.activated.emit(app.combobox.currentIndex())
        # ¦ Selection Made
        self.assertTrue(app.plotEnergyBtn.isEnabled())
        self.assertTrue(app.plotTOFBtn.isEnabled())
        self.assertTrue(app.clearBtn.isEnabled())
        self.assertFalse(app.pdBtn.isEnabled())
        self.assertFalse(app.gridCheck.isEnabled())
        self.assertFalse(app.thresholdCheck.isEnabled())
        self.assertFalse(app.peakLabelCheck.isEnabled())

        app.plotEnergyBtn.click()
        # ¦ After Plotting
        self.assertTrue(app.plotEnergyBtn.isEnabled())
        self.assertTrue(app.plotTOFBtn.isEnabled())
        self.assertTrue(app.clearBtn.isEnabled())
        self.assertTrue(app.pdBtn.isEnabled())
        self.assertTrue(app.gridCheck.isEnabled())
        self.assertTrue(app.thresholdCheck.isEnabled())
        self.assertTrue(app.peakLabelCheck.isEnabled())


if __name__ == '__main__':
    main(verbosity=1)
