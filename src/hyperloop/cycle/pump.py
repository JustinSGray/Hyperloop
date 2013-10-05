from scipy.interpolate import interp1d

from openmdao.main.api import Component

from openmdao.lib.datatypes.api import Float


class Pump(Component): 
    """Calculate the power requirement for a water pump given flow conditions""" 

    Pt_out = Float(1000, iotype="in", units="kPa", desc="Pump output pressure")
    Pt_in = Float(100, iotype="in", units="kPa", desc="Pump input pressure")
    Tt = Float(288, iotype="in", units="K", desc="water temperature at the pump inlet")
    W = Float(.5, iotype="in", units="kg/s", desc="liquid flow rate")
    eff = Float(.8, iotype="in", desc="")

    pwr_req = Float(iotype="out", units="kW", desc="power required to drive the pump")


    def __init__(self): 
        super(Pump, self).__init__()

        _temps = [273.15,  277.15,  283.15,  293.15,  303.15,  313.15,  323.15, 333.15,  343.15,  353.15,  363.15,  373.15] #degrees K
        _rhos =  [999.8,1000,999.7,998.2,995.7,992.2,988.1,983.2,977.8,971.8,965.3,958.4] #kg/m**3

        self._rho = interp1d(_temps, _rhos)

    def execute(self): 
        _rho = self._rho(self.Tt)
        self.pwr_req = self.W/_rho*(self.Pt_out-self.Pt_in)

if __name__ == "__main__":
    from openmdao.main.api import set_as_top

    p = set_as_top(Pump())

    p.run()

    print p.pwr_req