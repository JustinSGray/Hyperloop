"""
    preHeatEx.py -  (Run this before heatExchanger2.py)
        Performs inital energy balance for a basic heat exchanger design

NTU (effectiveness) Method
    Determine the heat transfer rate and outlet temperatures when the type and size of the heat exchanger is specified.

    NTU Limitations
    1) Effectiveness of the chosen heat exchanger must be known (empirical)

    Compatible with OpenMDAO v0.8.1
"""

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, Bool
from openmdao.main.api import convert_units as cu

from math import log, pi, sqrt, e

Mc = Float(288.1, units = 'kg/s', desc='Mass flow rate of cold fluid (water)') 
Mh = Float(288.1, units = 'kg/s', desc='Mass flow rate of the hot fluid (air)') 
Cpc = Float(288.1, units = 'J/(kg*K)', desc='Specific Heat of the cold fluid (water)') 
Cph = Float(288.1, units = 'J/(kg*K)', desc='Specific Heat of the hot fluid (air)') 
Th_in = Float(288.1, units = 'K', desc='Temp of air into heat exchanger') 
Th_out = Float(288.1, units = 'K', desc='Temp of air out of the heat exchanger') 

Qreleased = Float(288.1, units = 'W', desc='Energy Released') 
Qabsorbed= Float(288.1, units = 'W', desc='Energy Absorbed') 
U = Float(288.1, units = 'K', desc='') 
area = Float(288.1, units = 'm**2', desc='not currently used') 
LMTD = Float(288.1,  desc='Logarathmic Mean Temperature Difference') 
effectiveness = Float(288.1,  desc='Heat Exchange Effectiveness') 

MCpMin = Float(288.1, units = 'J/(s*K)', desc='Minimum product of specific heat multiplied by mass flow rate') 
Qmax= Float(288.1, units = 'W', desc='Max possible heat transfer') 
Qreal = Float(288.1, units = 'W', desc='Temp of water into heat exchanger') 
firstPass = Bool(True, desc= 'Boolean true if first pass')

   def execute(self):
        """Calculate Various Paramters"""
             



if __name__ == "__main__":

    from openmdao.main.api import set_as_top
    test = heatExchanger()  
    set_as_top(test)
    print ""
    test.run()
    print "-----Completed Heat Exchanger Sizing---"
    print ""
    print "Heat Exchanger Length: {} meters, with {} tube pass(es)".format(test.L/2,test.N)