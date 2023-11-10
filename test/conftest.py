import pytest
import pandas as pd
import sys
import os

sys.path.append(os.path.abspath("./src/project/"))
sys.path.append(os.path.abspath("./src/project/element"))
sys.path.append(os.path.abspath("./src/project/myPyQt"))

from NRTI_NRCA_Explorer import DatabaseGUI


@pytest.fixture(scope="session")
def app():
    return DatabaseGUI()


@pytest.fixture(scope="session")
def getElementData():

    # Normal 2 peak dataset
    graphdata1 = pd.DataFrame(data=[[1.00E-05, 224.843],
                                    [1.03E-05, 221.41],
                                    [1.06E-05, 218.13],
                                    [1.09E-05, 214.991],
                                    [1.13E-05, 211.984],
                                    [1.16E-05, 209.1]
                                    ])
    tabledata1 = pd.DataFrame(data=[[0, 5.780e+02, (1), 6.872e+01, 6.554e+02, 5.971e+00,
                                     (6), 2.963e+02, (0), ['29-Cu-63_n-g']],
                                    [1, 2.647e+03, (5), 3.212e+01, 2.043e+02, 1.668e+01,
                                     (5), 3.486e+01, (1), ['29-Cu-63_n-g']],
                                    [2, 2.048e+03, (4), 3.651e+01, 1.603e+02, 1.080e+02,
                                     (0), 4.701e+00, (8), ['29-Cu-63_n-g']],
                                    [3, 5.818e+03, (8), 2.166e+01, 9.469e+01, 3.149e+01,
                                     (2), 8.819e+00, (4), ['29-Cu-63_n-g']],
                                    [4, 4.396e+03, (6), 2.492e+01, 7.663e+01, 1.959e+01,
                                     (4), 1.100e+01, (3), ['29-Cu-63_n-g']],
                                    [5, 4.855e+03, (7), 2.371e+01, 6.794e+01, 4.733e+01,
                                     (1), 4.437e+00, (9), ['29-Cu-63_n-g']]
                                    ],
                              columns=['Rank by Integral', 'Energy (eV)', 'Rank by Energy',
                                       'TOF (us)', 'Integral', 'Peak Width',
                                       'Rank by Peak Width', 'Peak Height',
                                       'Rank by Peak Height', 'Relevant Isotope'])

    graphdata2 = pd.DataFrame()
    tabledata2 = pd.DataFrame()

    return [(tabledata1, graphdata1),
            (tabledata2, graphdata2)]
