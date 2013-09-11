from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, VarTree

from pyflowstation.pyflowstation import FlowStation



class Splitter(Component): 
    """Takes a single incoming air stream and splits it into two separate ones"""

    BPR_des = Float(12.47, iotype="in", desc="")
    MNexit1_des = Float(.4, iotype="in", 
        desc="mach number at the design condition for Fl_O1")
    MNexit2_des = Float(.4, iotype="in", 
        desc="mach number at the design condition for Fl_O21`")

    Fl_I = FlowStation(iotype="in", desc="incoming air stream to splitter")
    Fl_O1 = FlowStation(iotype="out", desc="outgoing air stream 1")
    Fl_O2 = FlowStation(iotype="out", desc="outgoing air stream 2")


    def execute(self): 
        pass


if __name__ == "__main__": 
    from openmdao.main.api import set_as_top

    c = set_as_top(Splitter())
    c.run()

