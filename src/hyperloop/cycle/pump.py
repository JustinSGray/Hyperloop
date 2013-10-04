from openmdao.main.api import Component

from openmdao.lib.datatypes.api import Float


class Pump(Component): 
    """Calculate the power requirement for a liquid pump given flow conditions""" 

    Pt_out = Float(100, iotype="in", units="kPa", desc="Pump output pressure")
    Pt_in = Float(100, iotype="in", units="kPa", desc="Pump output pressure")
    Pt_out = Float(100, iotype="in", units="kPa", desc="Pump output pressure")
