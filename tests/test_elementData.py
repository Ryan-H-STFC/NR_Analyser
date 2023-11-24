import sys
import os
import pandas as pd
from pandas.testing import assert_frame_equal
from unittest import TestCase, main


sys.path.append(os.path.abspath("./src/project/"))
sys.path.append(os.path.abspath("./src/project/element"))
sys.path.append(os.path.abspath("./src/project/myPyQt"))
from ElementDataStructure import ElementData


filepath = f"{os.path.dirname(os.path.dirname(__file__))}"


class TestElemenetData(TestCase):

    graphData = pd.read_csv(
        f"{filepath}/src/project/data/Graph Data/element_29-Cu_n-g.csv",
        header=None
    )

    tableData = pd.read_csv(
        f"{filepath}/src/project/data/Peak information/29-Cu-63_n-g.csv",
        header=None
    )

    elementGraphData = pd.read_csv(
        f"{filepath}/src/project/data/Graph Data/element_48-Cd_n-g.csv",
        header=None)

    elementTableData = pd.read_csv(
        f"{filepath}/src/project/data/Peak Information/element_48-Cd_n-g.csv",
        header=None)

    def test_ElementData_init_Normal(self):

        # Normal
        elementT = ElementData(
            name="29-Cu-63_n-g",
            numPeaks=10,
            tableData=self.tableData,
            graphData=self.graphData,
            graphColour=(0, 0, 0),
            isToF=True,
            distributions={"29-Cu-63": 0.691500, "29-Cu-65": 0.308500},
            defaultDist={"29-Cu-63": 0.691500, "29-Cu-65": 0.308500}
        )
        elementF = ElementData(
            name="29-Cu-63_n-g",
            numPeaks=10,
            tableData=self.tableData,
            graphData=self.graphData,
            isToF=False,
            graphColour=(0, 0, 0),
            distributions={"29-Cu-63": 0.691500, "29-Cu-65": 0.308500},
            defaultDist={"29-Cu-63": 0.691500, "29-Cu-65": 0.308500}
        )
        self.assertNotEqual(elementT, elementF)

    def test_ElementData_init_Null(self):

        # Null Peak Data
        elementT = ElementData(
            name="2-He-4_n-g",
            numPeaks=None,
            tableData=None,
            graphData=None,
            isToF=True,
            graphColour=(0, 0, 0),
            distributions=None,
            defaultDist=None
        )
        elementF = ElementData(
            name="2-He-4_n-g",
            numPeaks=None,
            tableData=None,
            graphData=None,
            isToF=False,
            graphColour=(0, 0, 0),
            distributions=None,
            defaultDist=None
        )
        self.assertFalse(elementT == elementF)
        self.assertTrue(elementT != elementF)
        self.assertFalse(elementT == "Other Type")
        self.assertTrue(elementT != "Other Type")

    def test_ElementData_init_Dist(self):

        element = ElementData(
            name="29-Cu-63_n-g",
            numPeaks=10,
            tableData=self.tableData,
            graphData=self.graphData,
            isToF=False,
            graphColour=(0, 0, 0),
            distributions={"29-Cu-63": 0.5, "29-Cu-65": 0.5},
            defaultDist={"29-Cu-63": 0.691500, "29-Cu-65": 0.308500}
        )

        self.assertNotEqual(element.graphData.shape, self.graphData.shape)

    def test_ElementData_energyToTOF(self):
        element = ElementData(
            name="29-Cu-63_n-g",
            numPeaks=10,
            tableData=self.tableData.copy(),
            graphData=self.graphData.copy(),
            isToF=False,
            graphColour=(0, 0, 0),
            distributions={"29-Cu-63": 0.691500, "29-Cu-65": 0.308500},
            defaultDist={"29-Cu-63": 0.691500, "29-Cu-65": 0.308500}
        )
        element.graphData[0] = element.energyToTOF(element.graphData[0], 23.404)
        self.assertFalse(all(element.graphData[0] == self.graphData[0]))
        element.graphData = self.graphData.copy()

        element.graphData[0] = element.energyToTOF(element.graphData[0], None)
        self.assertFalse(all(element.graphData[0] == self.graphData[0]))


if __name__ == '__main__':
    main()
