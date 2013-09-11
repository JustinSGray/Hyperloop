from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, VarTree

from pyflowstation.pyflowstation import FlowStation, CanteraFlowStation



class Inlet(Component): 
    """The inlet takes in air at a given flow rate and mach number, and diffuses it down 
    to a slower mach number and larger area"""

    ram_recovery = Float(1.000, iotype="in", desc="fraction of the total pressure retained")
    MNexit_des = Float(.6, iotype="in", desc="mach number at the exit of the inlet")

    Fl_I = FlowStation(iotype="in", desc="incoming air stream to compressor")
    Fl_O = FlowStation(iotype="out", desc="outgoing air stream from compressor")


    def execute(self): 
        pass


if __name__ == "__main__": 
    from openmdao.main.api import set_as_top

    c = set_as_top(Inlet())
    c.run()
