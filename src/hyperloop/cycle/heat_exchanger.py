"""
Originally built by Scott Jones in NPSS, ported and augmented by Jeff Chin   

NTU (effectiveness) Method
Determine the heat transfer rate and outlet temperatures when the type and size of the heat exchanger is specified.

NTU Limitations
1) Effectiveness of the chosen heat exchanger must be known (empirical)

"""

from math import log, pi, sqrt, e

from openmdao.main.api import Assembly, Component
from openmdao.lib.datatypes.api import Float, Bool
from openmdao.lib.drivers.api import BroydenSolver 
from openmdao.main.api import convert_units as cu

from pycycle.api import FlowStationVar, FlowStation, CycleComponent


class HeatExchanger(CycleComponent): 
    """Calculates required Q to reach perscribed temperatures for a water-to-air heat exchanger"""

    #inputs
    W_cold = Float(0.45, iotype="in", units = 'kg/s', desc='Mass flow rate of cold fluid (water)') 
    #Wh = Float(iotype="in", units = 'kg/s', desc='Mass flow rate of the hot fluid (air)') 
    Cp_cold = Float(4186, iotype="in", units = 'J/(kg*K)', desc='Specific Heat of the cold fluid (water)') 
    #Cp_hot = Float(iotype="in", units = 'J/(kg*K)', desc='Specific Heat of the hot fluid (air)') 
    #T_hot_in = Float(iotype="in", units = 'K', desc='Temp of air into heat exchanger')     
    T_cold_in = Float(288.1, iotype="in", units = 'K', desc='Temp of water into heat exchanger') 
    effectiveness = Float(.9765, iotype="in", desc='Heat Exchange Effectiveness') 
    MNexit_des = Float(.6, iotype="in", desc="mach number at the exit of heat exchanger")
    #State Vars
    T_hot_out = Float(338.4, iotype="in", units = 'K', desc='Temp of air out of the heat exchanger')    
    T_cold_out = Float(iotype="in", units = 'K', desc='Temp of water out of the heat exchanger') 
    

    Fl_I = FlowStationVar(iotype="in", desc="incoming air stream to heat exchanger", copy=None)

    #outputs
    Qreleased = Float(iotype="out", units = 'W', desc='Energy Released') 
    Qabsorbed= Float(iotype="out", units = 'W', desc='Energy Absorbed') 
    LMTD = Float(iotype="out", desc='Logarathmic Mean Temperature Difference')
    Qmax= Float(iotype="out", units = 'W', desc='Theoretical maximum possible heat transfer') 
 
    residual_qmax = Float(iotype="out", desc='Residual of max*effectiveness') 
    residual_e_balance = Float(iotype="out", desc='Residual of the energy balance')

    Fl_O = FlowStationVar(iotype="out", desc="outgoing air stream from heat exchanger", copy=None)

    def execute(self):
        """Calculate Various Paramters"""

        Fl_I = self.Fl_I
        Fl_O = self.Fl_O

        T_cold_in = self.T_cold_in
        T_cold_out = self.T_cold_out
        T_hot_in = self.Fl_I.Tt*.555555556 # R to K
        T_hot_out = self.T_hot_out
        W_cold = self.W_cold
        Wh = Fl_I.W
        Cp_hot = Fl_I.Cp/2.388459e-1 #BTU/lbm-C to Kj/kg-k
        Cp_cold = self.Cp_cold
        
        W_coldCpMin = W_cold*Cp_cold;
        if ( Wh*Cp_hot < W_cold*Cp_cold ):
            W_coldCpMin = Wh*Cp_hot
        self.Qmax = W_coldCpMin*(T_hot_in - T_cold_in);

        self.Qreleased = Wh*Cp_hot*(T_hot_in - T_hot_out);
        self.Qabsorbed = W_cold*Cp_cold*(T_cold_out - T_cold_in);

        self.LMTD = ((T_hot_out-T_hot_in)+(T_cold_out-T_cold_in))/log((T_hot_out-T_cold_in)/(T_hot_in-T_cold_out))

        self.residual_qmax = (self.Qreleased-self.effectiveness*self.Qmax)/100

        self.residual_e_balance = (self.Qreleased-self.Qabsorbed)/100

        Fl_O.setTotalTP(T_hot_out*1.8, Fl_I.Pt)
        Fl_O.W = Fl_I.W
        if self.run_design: 
            Fl_O.Mach = self.MNexit_des  
            self._exit_area_des = Fl_O.area
        else: 
            Fl_O.area = self._exit_area_des
 
if __name__ == "__main__":

    from openmdao.main.api import set_as_top
     

    class HeatBalance(Assembly):

        def configure(self):

            hx = self.add('hx', HeatExchanger())
            driver = self.add('driver',BroydenSolver())
            driver.add_parameter('hx.T_hot_out',low=0.,high=1000.)
            driver.add_parameter('hx.T_cold_out',low=0.,high=1000.)
            driver.add_constraint('hx.residual_qmax=0')
            driver.add_constraint('hx.residual_e_balance=0')

            #hx.Wh = 0.49
            #hx.Cp_hot = 1.006
            #hx.T_hot_in = 791
            fs = FlowStation()
            fs.setTotalTP(1423.8, 0.302712118187) #R, psi
            fs.W = .49
            hx.Fl_I = fs
            hx.W_cold = 0.45
            hx.Cp_cold = 4.186
            hx.T_cold_in = 288.15
            effectiveness = 0.9765

            #initial guess
            avg = ( hx.Fl_I.Tt*.555555556 + hx.T_cold_in )/2.
            hx.T_cold_out = avg
            hx.T_hot_out = avg  

            driver.workflow.add(['hx'])

    test = HeatBalance()  
    set_as_top(test)
    test.hx.design = True


    #good values: 
    #air:      Tin       Tout         Q      Q' 
    #791.0    299.966975    242.049819343    247.874879
    #water:    Tin       Tout         Q      Q' 
    #288.15    416.647010853    242.049819343    247.874879

    print ""
    test.run()
    print  "air:      Tin       Tout         Q      Q\' \n";
    print "    {}    {}    {}    {}".format(test.hx.Fl_I.Tt*.555555556, test.hx.T_hot_out, test.hx.Qreleased, test.hx.Qmax)

    print 
    print "water:    Tin       Tout         Q      Q\' \n";
    print "    {}    {}    {}    {}".format(test.hx.T_cold_in, test.hx.T_cold_out, test.hx.Qabsorbed, test.hx.Qmax)
    print " LMTD = {}  ".format(test.hx.LMTD)