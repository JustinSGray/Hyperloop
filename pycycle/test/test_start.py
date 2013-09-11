
import unittest

from openmdao.main.api import set_as_top

import start

class StartTestCase(unittest.TestCase):

    def test_start(self): 
        start = set_as_top(start.FlowStart())

        start.W = 1.582
        start.Pt = 99
        start.Tt = 292
        start.Mach = 1.0

        start.run()

        self.assertAlmostEqual(start.Fl_O.W, 1.582)
        self.assertAlmostEqual(start.Fl_O.Pt, 187.43)
        self.assertAlmostEqual(start.Fl_O.Tt, 292)
        self.assertAlmostEqual(start.Fl_O.rhos, 0.001181)
        self.assertAlmostEqual(start.Fl_O.Mach, 1.00)
        self.assertAlmostEqual(start.Fl_O.Area, 39100.5)

        
if __name__ == "__main__":
    unittest.main()
    