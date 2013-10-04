"""
    heatAssembly.py -  (Assembly running heat calculations)

    Compatible with OpenMDAO v0.8.1
"""

from openmdao.main.api import Assembly , Component
from openmdao.lib.datatypes.api import Float, Bool
from openmdao.lib.drivers.api import BroydenSolver 
from openmdao.main.api import convert_units as cu

from math import log, pi, sqrt, e

class HeatExchanger(Assembly): 

    def configure(self):

        HX = self.add('HX', preHeatEx())
        #heatEx = self.add('heatExchanger', heatExchanger())
        self.connect('Mach_pod', 'compress.Mach_pod')
        self.connect('radius_tube', 'compress.radius_tube')
        self.create_passthrough('compress.Mach_c1_in')

        driver = self.add('driver',BroydenSolver())
        driver.add_parameter('HX.Th_out',low=0.,high=1000.)
        driver.add_parameter('HX.Tc_out',low=0.,high=1000.)
        driver.add_constraint('HX.Qreleased=HX.effectiveness*HX.Qmax')
        driver.add_constraint('HX.Qreleased=HX.Qabsorbed')

        driver.workflow.add(['preHeatEx'])

if __name__=="__main__": 

    from openmdao.main.api import set_as_top
    test = heatExchanger()  
    set_as_top(test)
    test.HX.Mc = .45
    print ""
    test.run()
    print  "air:      Tin       Tout         Q      Q\' \n";
    print "    {}    {}    {}    {}".format(test.HX.Th_in, test.HX.Th_out, test.HX.Qreleased, test.HX.Qmax)

    print 
    print "water:    Tin       Tout         Q      Q\' \n";
    print "    {}    {}    {}    {}".format(test.HX.Tc_in, test.HX.Tx_out, test.HX.Qabsorbed, test.HX.Qmax)
    print " LMTD = {}  ".format(HX.LMTD)