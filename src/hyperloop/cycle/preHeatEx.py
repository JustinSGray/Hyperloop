"""
    preHeatEx.py -  (Run this before heatExchanger2.py)
        Performs inital energy balance for a basic heat exchanger design

     Originally built by Scott Jones in NPSS, ported and augmented by Jeff Chin   

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




class preHeatEx(Component): 
    #inputs
    Mc = Float(288.1, iotype="in", units = 'kg/s', desc='Mass flow rate of cold fluid (water)') 
    Mh = Float(288.1, iotype="in", units = 'kg/s', desc='Mass flow rate of the hot fluid (air)') 
    Cpc = Float(288.1, iotype="in", units = 'J/(kg*K)', desc='Specific Heat of the cold fluid (water)') 
    Cph = Float(288.1, iotype="in", units = 'J/(kg*K)', desc='Specific Heat of the hot fluid (air)') 
    Th_in = Float(791., iotype="in", units = 'K', desc='Temp of air into heat exchanger')     
    Tc_in = Float(288.15, iotype="in", units = 'K', desc='Temp of water into heat exchanger')  

    #outputs
    Th_out = Float(iotype="out", units = 'K', desc='Temp of air out of the heat exchanger')    
    Tc_out = Float(iotype="out", units = 'K', desc='Temp of water out of the heat exchanger') 
    Qreleased = Float(288.1, iotype="out", units = 'W', desc='Energy Released') 


    #intermediate variables
    Qabsorbed= Float(288.1, units = 'W', desc='Energy Absorbed') 
    LMTD = Float(288.1,  desc='Logarathmic Mean Temperature Difference') 
    effectiveness = Float(0.967,  desc='Heat Exchange Effectiveness') 
    MCpMin = Float(288.1, units = 'J/(s*K)', desc='Minimum product of specific heat multiplied by mass flow rate') 
    Qmax= Float(288.1, units = 'W', desc='Max possible heat transfer') 
    firstPass = Bool(True, desc= 'Boolean true if first pass')

    
   def execute(self):
        """Calculate Various Paramters"""
        
        Tc_in = self.Tc_in
        Tc_out = self.Tc_out
        Th_in = self.Th_in
        Th_out = self.Th_out
        Mc = self.Mc
        Mh = self.Mh
        Cph = self.Cph
        Cpc = self.Cpc
        MCpMin = self.MCpMin
        

        # guess exit temperatures     
        if ( firstPass == TRUE ): 
             Tc_out = ( Th_in + Tc_in )/2.
             Th_out = ( Th_in + Tc_in )/2.
             firstPass = FALSE;
        #calculate mdot*Cp min
        MCpMin = Mc*Cpc;
        if ( Mh*Cph < Mc*Cpc ):
            MCpMin = Mh*Cph
        self.Qmax = MCpMin*(Th_in - Tc_in);

        self.Qreleased = Mh*Cph*(Th_in - Th_out);
        self.Qabsorbed = Mc*Cpc*(Tc_out - Tc_in);

        self.LMTD = ( (Th_out - Th_in) + (Tc_out - Tc_in) ) / 
             log( ( Th_out - Tc_in )/( Th_in - Tc_out ) );
        self.Qreal = U*area*LMTD; # or eff = U*area*LMTD/Qmax


 
if __name__ == "__main__":

    from openmdao.main.api import set_as_top
    test = heatExchanger()  
    set_as_top(test)
    print ""
    test.run()
    print  "air:      Tin       Tout         Q      Q\' \n";
    print "    {}    {}    {}    {}".format(HX.Th_in,HX.Th_out,HX.Qreleased, HX.Qmax)

    print 
    print "water:    Tin       Tout         Q      Q\' \n";
    print "    {}    {}    {}    {}".format(HX.Tc_in,HX.Tx_out,HX.Qabsorbed,HX.Qmax)
    print " LMTD = {}  ".format(HX.LMTD)
