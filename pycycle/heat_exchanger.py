from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, VarTree

from pyflowstation.pyflowstation import FlowStation, CanteraFlowStation



class HeatExchanger(Component): 
    """Calculates the required mass flow of water given the specified temperatures 
    for water and air and assuming a single pass water-air heat exchanger"""


    air_in = FlowStation(iotype="in", desc="incoming air stream")
    air_out = FlowStation(iotype="out", desc="outgoing air stream")


    def execute(self): 
        pass


if __name__ == "__main__": 
    from openmdao.main.api import set_as_top

    c = set_as_top(Nozzle())
    c.run()
