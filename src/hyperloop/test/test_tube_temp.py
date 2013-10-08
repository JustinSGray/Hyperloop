import unittest

from openmdao.main.api import set_as_top, Assembly
from openmdao.util.testutil import assert_rel_error
from openmdao.lib.drivers.api import BroydenSolver
from hyperloop.tube_wall_temp import TubeWallTemp


class TubeHeatBalance(Assembly):

    def configure(self):

        tm = self.add('tm', TubeWallTemp())
        #tm.bearing_air.setTotalTP()
        driver = self.add('driver',BroydenSolver())
        driver.add_parameter('tm.temp_boundary',low=0.,high=10000.)
        driver.add_constraint('tm.ss_temp_residual=0')
        driver.workflow.add(['tm'])


class TubeWallTestCase(unittest.TestCase):
    
    def test_tube_temp(self): 
        
        test = set_as_top(TubeHeatBalance())
        #set input values
        test.tm.nozzle_air.setTotalTP(1710, 0.304434211)
        test.tm.nozzle_air.W = 1.08
        test.tm.bearing_air.W = 0.
        test.tm.diameter_outer_tube = 2.22504#, units = 'm', iotype='in', desc='Tube out diameter') #7.3ft
        test.tm.length_tube = 482803.#, units = 'm', iotype='in', desc='Length of entire Hyperloop') #300 miles, 1584000ft
        test.tm.num_pods = 34.#, units = 'K', iotype='in', desc='Number of Pods in the Tube at a given time') #
        test.tm.temp_boundary = 322.361#, units = 'K', iotype='in', desc='Average Temperature of the tube') #
        test.tm.temp_outside_ambient = 305.6#, units = 'K', iotype='in', desc='Average Temperature of the outside air') #

        test.run()
        assert_rel_error(self,test.tm.heat_rate_pod, 353244., 0.02)
        assert_rel_error(self,test.tm.total_heat_rate_pods,12010290., 0.02)
        assert_rel_error(self,test.tm.GrDelTL3,123775609, 0.02)
        assert_rel_error(self,test.tm.Pr,0.707, 0.02)
        assert_rel_error(self,test.tm.Gr,23163846280., 0.02)
        assert_rel_error(self,test.tm.Ra,16369476896., 0.02)
        assert_rel_error(self,test.tm.Nu,281.6714, 0.02) #http://www.egr.msu.edu/~somerton/Nusselt/ii/ii_a/ii_a_3/ii_a_3_a.html
        assert_rel_error(self,test.tm.k,0.02655, 0.02)
        assert_rel_error(self,test.tm.h,3.3611, 0.02)
        assert_rel_error(self,test.tm.area_convection,3374876, 0.02)
        assert_rel_error(self,test.tm.q_per_area_nat_conv,57.10, 0.02)
        assert_rel_error(self,test.tm.total_q_nat_conv,192710349, 0.02)
        assert_rel_error(self,test.tm.area_viewing,1074256., 0.02)
        assert_rel_error(self,test.tm.q_per_area_solar,350., 0.02)
        assert_rel_error(self,test.tm.q_total_solar,375989751., 0.02)
        assert_rel_error(self,test.tm.area_rad,3374876.115, 0.02)
        assert_rel_error(self,test.tm.q_rad_per_area,59.7, 0.02)
        assert_rel_error(self,test.tm.q_rad_tot,201533208, 0.02)
        assert_rel_error(self,test.tm.q_total_out,394673364., 0.02)


if __name__ == "__main__":
    unittest.main()