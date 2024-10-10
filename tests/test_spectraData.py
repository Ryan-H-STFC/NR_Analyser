import sys
import os
import pandas as pd
from unittest import TestCase, main


sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath("./src/"))
sys.path.append(os.path.abspath("./src/project/"))
sys.path.append(os.path.abspath("./src/project/spectra"))
sys.path.append(os.path.abspath("./src/project/myPyQt"))
from project.spectra.SpectraDataStructure import SpectraData

filepath = f"{os.path.dirname(__file__)}"


class TestSpectraData(TestCase):

    graphData = pd.read_csv(
        f"{filepath}/test_data/graphData/element_29-Cu_n-g.csv",
        header=None
    )

    tableData = pd.read_csv(
        f"{filepath}/test_data/tableData/29-Cu_n-g_tableData_max.csv",
        header=None
    )

    graphData2 = pd.read_csv(
        f"{filepath}/test_data/graphData/element_48-Cd_n-g.csv",
        header=None)

    tableData2 = pd.read_csv(
        f"{filepath}/test_data/tableData/48-Cd_n-g_tableData_max.csv",
        header=None)

    def test_ElementData_init_Normal(self):

        # Normal
        elementT = SpectraData(
            name="element_29-Cu-63_n-g",
            numPeaks=10,
            tableDataMax=self.tableData,
            tableDataMin=None,
            graphData=self.graphData,
            graphColour=(0, 0, 0),
            isToF=False,
            distributions={"29-Cu-63": 0.691500, "29-Cu-65": 0.308500},
            defaultDist={"29-Cu-63": 0.691500, "29-Cu-65": 0.308500}
        )
        elementF = SpectraData(
            name="element_29-Cu-63_n-g",
            numPeaks=10,
            tableDataMax=self.tableData,
            tableDataMin=None,
            graphData=self.graphData,
            isToF=True,
            graphColour=(0, 0, 0),
            distributions={"29-Cu-63": 0.691500, "29-Cu-65": 0.308500},
            defaultDist={"29-Cu-63": 0.691500, "29-Cu-65": 0.308500}
        )
        self.assertNotEqual(elementT, elementF)

    def test_ElementData_init_Null(self):

        # Null Peak Data
        elementT = SpectraData(
            name="2-He-4_n-g",
            numPeaks=None,
            tableDataMax=None,
            tableDataMin=None,
            graphData=None,
            isToF=True,
            graphColour=(0, 0, 0),
            distributions=None,
            defaultDist=None
        )
        elementF = SpectraData(
            name="2-He-4_n-g",
            numPeaks=None,
            tableDataMax=None,
            tableDataMin=None,
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

        element = SpectraData(
            name="element_48-Cd_n-g",
            numPeaks=10,
            tableDataMax=self.tableData2,
            tableDataMin=None,
            graphData=self.graphData2,
            isToF=False,
            graphColour=(0, 0, 0),
            distributions={"48-Cd-106": 0.5,
                           "48-Cd-108": 0.5,
                           },
            defaultDist={"48-Cd-106": 0.014972,
                         "48-Cd-108": 0.010660,
                         "48-Cd-110": 0.149599,
                         "48-Cd-111": 0.153312,
                         "48-Cd-112": 0.289017,
                         "48-Cd-113": 0.146365,
                         "48-Cd-114": 0.146365,
                         "48-Cd-116": 0.089711
                         }
        )

        self.assertNotEqual(element.graphData.shape, self.graphData.shape)

    def test_ElementData_energyToTOF(self):
        element = SpectraData(
            name="element_48-Cd_n-g",
            numPeaks=10,
            tableDataMax=self.tableData2.copy(),
            tableDataMin=None,
            graphData=self.graphData2.copy(),
            isToF=False,
            graphColour=(0, 0, 0),
            distributions={"48-Cd-106": 0.014972,
                           "48-Cd-108": 0.010660,
                           "48-Cd-110": 0.149599,
                           "48-Cd-111": 0.153312,
                           "48-Cd-112": 0.289017,
                           "48-Cd-113": 0.146365,
                           "48-Cd-114": 0.146365,
                           "48-Cd-116": 0.089711},
            defaultDist={"48-Cd-106": 0.014972,
                         "48-Cd-108": 0.010660,
                         "48-Cd-110": 0.149599,
                         "48-Cd-111": 0.153312,
                         "48-Cd-112": 0.289017,
                         "48-Cd-113": 0.146365,
                         "48-Cd-114": 0.146365,
                         "48-Cd-116": 0.089711}
        )
        element.graphData[0] = element.energyToTOF(element.graphData[0], 23.404)
        print(f"{self.graphData2.shape}, {element.graphData.shape}")
        self.assertFalse(element.graphData.equals(self.graphData2))
        element.graphData = self.graphData.copy()

        element.graphData[0] = element.energyToTOF(element.graphData[0], None)
        self.assertFalse(element.graphData.equals(self.graphData2))


if __name__ == '__main__':
    main()
