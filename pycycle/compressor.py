from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, VarTree

from pyflowstation.pyflowstation import FlowStation, CanteraFlowStation



class Compressor(Component): 

    PR_des = Float(12.47, iotype="in", desc="Pressure ratio at design conditions")
    MNexit_des = Float(.4, iotype="in", desc="mach number at the compressor exit at design conditions")

    Fl_I = FlowStation(iotype="in", desc="incoming air stream to compressor")
    Fl_O = FlowStation(iotype="out", desc="outgoing air stream from compressor")


    def execute(self): 
        pass


if __name__ == "__main__": 
    from openmdao.main.api import set_as_top

    c = set_as_top(Compressor())
    c.run()



