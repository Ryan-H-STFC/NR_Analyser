import sys
import os
from unittest import TestCase, main


sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath("./src/"))
sys.path.append(os.path.abspath("./src/project/"))
sys.path.append(os.path.abspath("./src/project/spectra"))
sys.path.append(os.path.abspath("./src/project/myPyQt"))

from project.helpers.getRandomColor import getRandomColor
from project.helpers.interpName import interpName


class TestHelpers(TestCase):

    def test_getRandomColor(self):
        self.assertTrue(isinstance(getRandomColor(), tuple))
        self.assertTrue(len(getRandomColor()) == 3)
        self.assertTrue(0.1 <= getRandomColor()[0] <= 0.9)
        self.assertTrue(0.2 <= getRandomColor()[1] <= 0.7)
        self.assertTrue(0.1 <= getRandomColor()[2] <= 0.9)

    def test_interpName(self):

        self.assertTrue(isinstance(interpName('82-Pb-207_n-g'), dict))
        self.assertTrue(isinstance(interpName('element_82-Pb_n-tot'), dict))
        self.assertTrue(isinstance(interpName('80-Hg-198_n-tot'), dict))
        self.assertTrue(isinstance(interpName('element_78-Pt_n-tot'), dict))
        self.assertTrue(isinstance(interpName('70-Yb-168_n-tot'), dict))
        self.assertTrue(interpName() is None)
        self.assertTrue(interpName('') is None)
        self.assertTrue(interpName(True) is None)
        self.assertTrue(interpName(0.45324) is None)
        self.assertTrue(interpName(222) is None)
        self.assertTrue(interpName('hbdfv -df0=f-12   \n\t  dn1klv dfs-=fa s-df=a') is None)


if __name__ == '__main__':
    main()
