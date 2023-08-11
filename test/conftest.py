import pytest
import pandas as pd
import os


@pytest.fixture(scope="session")
def getElementData():
    filepath = os.path.dirname(os.path.dirname(__file__)) + "\\project"

    # Normal 2 peak dataset
    graphdata1 = pd.read_csv(f"{filepath}\\data\\29-Cu-63_n-g.csv",
                             header=None)
    tabledata1 = pd.read_csv(f"{filepath}\\GUI Files\\Peak information\\29-Cu_n-g.csv",
                             header=None)

    # Large >1000 peak dataset
    graphdata2 = pd.read_csv(f"{filepath}\\data\\element_92-U_n-tot.csv",
                             header=None)
    tabledata2 = pd.read_csv(f"{filepath}\\GUI Files\\Peak information\\element_92-U_n-tot.csv",
                             header=None)
    # Invalid filepath
    try:
        tabledata3 = pd.read_csv(f"{filepath}\\GUI Files\\Peak information\\2-He-4_n-g.csv",
                                 header=None)
    except FileNotFoundError:
        tabledata3 = pd.DataFrame()
    try:
        graphdata3 = pd.read_csv(f"{filepath}\\data\\2-He-4_n-g.csv",
                                 header=None)
    except pd.errors.EmptyDataError:
        graphdata3 = pd.DataFrame()
    return [(tabledata1, graphdata1),
            (tabledata2, graphdata2),
            (graphdata3, tabledata3)]
