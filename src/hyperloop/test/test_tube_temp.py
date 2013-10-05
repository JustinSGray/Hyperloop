import unittest

from openmdao.main.api import set_as_top, Assembly
from openmdao.util.testutil import assert_rel_error
from openmdao.lib.drivers.api import BroydenSolver
from hyperloop.tube_temp import TubeTemp


class TubeHeatBalance(Assembly):

    def configure(self):

        tm = self.add('tm', TubeTemp())
        #tm.bearing_air.setTotalTP()
        driver = self.add('driver',BroydenSolver())
        driver.add_parameter('tm.tubeWallTemp',low=0.,high=10000.)
        driver.add_constraint('tm.ssTemp_residual=0')
        driver.workflow.add(['tm'])


class TubeTempTestCase(unittest.TestCase):
    
    def test_tube_temp(self): 
        
        test = set_as_top(TubeHeatBalance())
        #set input values
        test.tm.nozzle_air.setTotalTP(1710, 0.304434211)
        test.tm.nozzle_air.W = 1.08
        test.tm.bearing_air.W = 0.
        test.tm.tubeOD = 2.22504#, units = 'm', iotype='in', desc='Tube out diameter') #7.3ft
        test.tm.tubeLength = 482803.#, units = 'm', iotype='in', desc='Length of entire Hyperloop') #300 miles, 1584000ft
        test.tm.podFreq = 34.#, units = 'K', iotype='in', desc='Number of Pods in the Tube at a given time') #
        test.tm.tubeWallTemp = 322.361#, units = 'K', iotype='in', desc='Average Temperature of the tube') #
        test.tm.ambientTemp = 305.6#, units = 'K', iotype='in', desc='Average Temperature of the outside air') #

        test.run()
        assert_rel_error(self,test.tm.podQ, 353244., 0.02)
        assert_rel_error(self,test.tm.podQTot,12010290., 0.02)
        assert_rel_error(self,test.tm.GrDelTL3,123775609, 0.02)
        assert_rel_error(self,test.tm.Pr,0.707, 0.02)
        assert_rel_error(self,test.tm.Gr,23163846280., 0.02)
        assert_rel_error(self,test.tm.Ra,16369476896., 0.02)
        assert_rel_error(self,test.tm.Nu,281.6714, 0.02) #http://www.egr.msu.edu/~somerton/Nusselt/ii/ii_a/ii_a_3/ii_a_3_a.html
        assert_rel_error(self,test.tm.k,0.02655, 0.02)
        assert_rel_error(self,test.tm.h,3.3611, 0.02)
        assert_rel_error(self,test.tm.convArea,3374876, 0.02)
        assert_rel_error(self,test.tm.naturalConvection,57.10, 0.02)
        assert_rel_error(self,test.tm.naturalConvectionTot,192710349, 0.02)
        assert_rel_error(self,test.tm.ViewingArea,1074256., 0.02)
        assert_rel_error(self,test.tm.solarHeat,350., 0.02)
        assert_rel_error(self,test.tm.solarHeatTotal,375989751., 0.02)
        assert_rel_error(self,test.tm.radArea,3374876.115, 0.02)
        assert_rel_error(self,test.tm.qRad,59.7, 0.02)
        assert_rel_error(self,test.tm.qRadTot,201533208, 0.02)
        assert_rel_error(self,test.tm.Qout,394673364., 0.02)


if __name__ == "__main__":
    unittest.main()