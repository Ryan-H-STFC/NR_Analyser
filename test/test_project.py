# from project.ExtendedTableModel import ExtendedQTableModel
# from project.PeakDetection import PeakDetection
# import project.Whole_Program
# import tests.conftest
import pytest
from src.project.ElementDataStructure import ElementData


@pytest.fixture
def app():
    # w = project.Whole_Program.DatabaseGUI()
    pass

# ? ElementData Testing


def test_ElementData_init_Normal(getElementData):
    (tableData1, graphData1), _, _ = getElementData
    # Normal
    elementT = ElementData(name="29-Cu-63_n-g", numPeaks=10, tableData=tableData1,
                           graphData=graphData1, isToF=True, annotations=[], graphColour=(0, 0, 0))
    elementF = ElementData(name="29-Cu-63_n-g", numPeaks=10, tableData=tableData1,
                           graphData=graphData1, isToF=False, annotations=[], graphColour=(0, 0, 0))
    return elementT != elementF is True


def test_ElementData_init_Large(getElementData):
    _, (tableData2, graphData2), _ = getElementData
    # >1000 Peaks

    elementT = ElementData(name="element_92-U_n-tot", numPeaks=1169, tableData=tableData2,
                           graphData=graphData2, isToF=True, annotations=[], graphColour=(0, 0, 0))
    elementF = ElementData(name="element_92-U_n-tot", numPeaks=1169, tableData=tableData2,
                           graphData=graphData2, isToF=False, annotations=[], graphColour=(0, 0, 0))
    return elementT != elementF is True


def test_ElementData_init_Null(getElementData):
    _, _, (tableData3, graphData3) = getElementData
    # Null Peak Data
    elementT = ElementData(name="2-He-4_n-g", numPeaks=0, tableData=tableData3,
                           graphData=graphData3, isToF=True, annotations=[], graphColour=(0, 0, 0))
    elementF = ElementData(name="2-He-4_n-g", numPeaks=0, tableData=tableData3,
                           graphData=graphData3, isToF=False, annotations=[], graphColour=(0, 0, 0))
    return elementT != elementF is True

# ? ExtendedTableModel Testing


@pytest.mark.skip(reason="Unfinished Test")
def test_ExtendedTableModel_init():
    pass


# ? Peak Detection Testing

@pytest.mark.skip(reason="Unfinished Test")
def test_PeakDetection_init():
    pass
