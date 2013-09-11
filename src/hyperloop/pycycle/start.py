from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, VarTree

from pyflowstation.pyflowstation import FlowStation



class FlowStart(Component): 
    """Flow initialization""" 

    W = Float(1, iotype="in", desc="mass flow rate", units="lbm/s")
    Pt = Float(14.7, iotype="in", desc="total pressure", units="psi")
    Tt = Float(518, iotype="in", desc="total temperature", units="R")
    Mach = Float(.1, iotype="in", desc="Mach Number")

    Fl_O = FlowStation(iotype="out", desc="outgoing flow at the specified conditions")


    def execute(self): 
        self.Fl_O.setDryAir()

        self.Fl_O.setTotalTP(self.Tt, self.Pt)
        self.Fl_O.W = self.W
        self.Fl_O.Mach = self.Mach



if __name__ == "__main__": 
    from openmdao.main.api import set_as_top

    c = set_as_top(FlowStart())

    print c.Fl_O.Pt
    print c.Fl_O.rhot
    print c.Fl_O.area
    print 
    print 
    c.run()

    print c.Fl_O.Pt
    print c.Fl_O.rhot
    print c.Fl_O.area



