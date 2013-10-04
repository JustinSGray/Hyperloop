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

from openmdao.main.api import Assembly, Component
from openmdao.lib.datatypes.api import Float, Bool
from openmdao.lib.drivers.api import BroydenSolver 
from openmdao.main.api import convert_units as cu

from math import log, pi, sqrt, e




class HeatExchanger(Component): 
    #inputs
    Mc = Float(iotype="in", units = 'kg/s', desc='Mass flow rate of cold fluid (water)') 
    Mh = Float(iotype="in", units = 'kg/s', desc='Mass flow rate of the hot fluid (air)') 
    Cpc = Float(iotype="in", units = 'J/(kg*K)', desc='Specific Heat of the cold fluid (water)') 
    Cph = Float(iotype="in", units = 'J/(kg*K)', desc='Specific Heat of the hot fluid (air)') 
    Th_in = Float(iotype="in", units = 'K', desc='Temp of air into heat exchanger')     
    Tc_in = Float(iotype="in", units = 'K', desc='Temp of water into heat exchanger') 
    #not really inputs  
    Th_out = Float(iotype="in", units = 'K', desc='Temp of air out of the heat exchanger')    
    Tc_out = Float(iotype="in", units = 'K', desc='Temp of water out of the heat exchanger') 
    effectiveness = Float(.9765, iotype="in", desc='Heat Exchange Effectiveness') 



    #outputs
    Qreleased = Float(iotype="out", units = 'W', desc='Energy Released') 
    Qabsorbed= Float(iotype="out", units = 'W', desc='Energy Absorbed') 
    LMTD = Float(iotype="out", desc='Logarathmic Mean Temperature Difference')
    Qmax= Float(iotype="out", units = 'W', desc='Theoretical maximum possible heat transfer') 
 
    residual_qmax = Float(iotype="out", desc='Residual of max*effectiveness') 
    residual_e_balance = Float(iotype="out", desc='Residual of the energy balance')


    #intermediate variables
    MCpMin = Float(units = 'J/(s*K)', desc='Minimum product of specific heat multiplied by mass flow rate') 

    def __init__(self): 
        super(HeatExchanger, self).__init__()


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
        #if ( firstPass == TRUE ): 
        #     Tc_out = ( Th_in + Tc_in )/2.
        #     Th_out = ( Th_in + Tc_in )/2.
        #     firstPass = FALSE;
        #calculate mdot*Cp min
        MCpMin = Mc*Cpc;
        if ( Mh*Cph < Mc*Cpc ):
            MCpMin = Mh*Cph
        self.Qmax = MCpMin*(Th_in - Tc_in);

        self.Qreleased = Mh*Cph*(Th_in - Th_out);
        self.Qabsorbed = Mc*Cpc*(Tc_out - Tc_in);

        self.LMTD = ((Th_out-Th_in)+(Tc_out-Tc_in))/log((Th_out-Tc_in)/(Th_in-Tc_out));

        self.residual_qmax = self.Qreleased-self.effectiveness*self.Qmax

        self.residual_e_balance = self.Qreleased-self.Qabsorbed
 
if __name__ == "__main__":

    from openmdao.main.api import set_as_top
     

    class HeatBalance(Assembly):

        def configure(self):

            hx = self.add('hx', HeatExchanger())
            driver = self.add('driver',BroydenSolver())
            driver.add_parameter('hx.Th_out',low=0.,high=1000.)
            driver.add_parameter('hx.Tc_out',low=0.,high=1000.)
            driver.add_constraint('hx.residual_qmax=0')
            driver.add_constraint('hx.residual_e_balance=0')

            hx.Mh = 0.49
            hx.Cph = 1.006
            hx.Th_in = 791
            hx.Mc = 0.45
            hx.Cpc = 4.186
            hx.Tc_in = 288.15
            effectiveness = 0.9765

            #initial guess
            avg = ( hx.Th_in + hx.Tc_in )/2.
            hx.Tc_out = avg
            hx.Th_out = avg

            driver.workflow.add(['hx'])

    test = HeatBalance()  
    set_as_top(test)
    test.hx.Mc = .45


    #good values: 
    #air:      Tin       Tout         Q      Q' 
    #791.0    299.966975    242.049819343    247.874879
    #water:    Tin       Tout         Q      Q' 
    #288.15    416.647010853    242.049819343    247.874879

    print ""
    test.run()
    print  "air:      Tin       Tout         Q      Q\' \n";
    print "    {}    {}    {}    {}".format(test.hx.Th_in, test.hx.Th_out, test.hx.Qreleased, test.hx.Qmax)

    print 
    print "water:    Tin       Tout         Q      Q\' \n";
    print "    {}    {}    {}    {}".format(test.hx.Tc_in, test.hx.Tc_out, test.hx.Qabsorbed, test.hx.Qmax)
    print " LMTD = {}  ".format(test.hx.LMTD)