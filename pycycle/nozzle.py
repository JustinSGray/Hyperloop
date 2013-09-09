from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, VarTree

from pyflowstation.pyflowstation import FlowStation, CanteraFlowStation



class Nozzle(Component): 
    """Calculates the gross thrust for a convergent-divergent nozzle, assuming an ideally expanded
    exit condition"""

    Fl_reference = FlowStation(iotype="in", desc="Flowstation with reference exit conditions")

    Fl_I = FlowStation(iotype="in", desc="incoming air stream to compressor")
    Fl_O = FlowStation(iotype="out", desc="outgoing air stream from compressor")


    def execute(self): 
        pass


if __name__ == "__main__": 
    from openmdao.main.api import set_as_top

    c = set_as_top(Nozzle())
    c.run()
