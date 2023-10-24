import pytest
import sys
import os

sys.path.append(os.path.abspath("./src/project/"))
sys.path.append(os.path.abspath("./src/project/element"))
sys.path.append(os.path.abspath("./src/project/myPyQt"))
sys.path.append(os.path.abspath("./src/project/helpers"))
sys.path.append(os.path.abspath("./src/project/myMatplotlib"))
from ElementDataStructure import ElementData


@pytest.fixture
def app():
    # w = project.Whole_Program.DatabaseGUI()
    pass


# ? ElementData Testing


def test_ElementData_init_Normal(getElementData):
    (tableData1, graphData1), _ = getElementData
    # Normal
    elementT = ElementData(
        name="29-Cu-63_n-g",
        numPeaks=10,
        tableData=tableData1,
        graphData=graphData1,
        graphColour=(0, 0, 0),
        isToF=True,
        distributions=None,
        defaultDist=None
    )
    elementF = ElementData(
        name="29-Cu-63_n-g",
        numPeaks=10,
        tableData=tableData1,
        graphData=graphData1,
        isToF=False,
        graphColour=(0, 0, 0),
        distributions=None,
        defaultDist=None
    )
    return elementT != elementF is True


def test_ElementData_init_Null(getElementData):
    _, (tableData2, graphData2) = getElementData
    # Null Peak Data
    elementT = ElementData(
        name="2-He-4_n-g",
        numPeaks=0,
        tableData=tableData2,
        graphData=graphData2,
        isToF=True,
        graphColour=(0, 0, 0),
        distributions=None,
        defaultDist=None
    )
    elementF = ElementData(
        name="2-He-4_n-g",
        numPeaks=0,
        tableData=tableData2,
        graphData=graphData2,
        isToF=False,
        graphColour=(0, 0, 0),
        distributions=None,
        defaultDist=None
    )
    return elementT != elementF is True


# ? ExtendedTableModel Testing


@pytest.mark.skip(reason="Unfinished Test")
def test_ExtendedTableModel_init():
    pass


# ? Peak Detection Testing


@pytest.mark.skip(reason="Unfinished Test")
def test_PeakDetection_init():
    pass
