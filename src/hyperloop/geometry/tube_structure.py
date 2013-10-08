from openmdao.main.api import Component

from openmdao.lib.datatypes.api import Float

THICKNESS_RATIO = .23/111.5 #uses ratio given on page 27 or original proposal


class TubeStructural(Component): 
    """Place holder for real structural calculations to size the tube wall Thickness""" 
    #Inputs
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa")
    radius_inner = Float(300, iotype="in", units="cm", desc="inner radius of tube")
    #Outputs
    radius_outer = Float(300.6, iotype="out", units="cm", desc="outer radius of tube")

    def execute(self): 

        thickness = self.radius_inner*THICKNESS_RATIO
        self.radius_outer = self.radius_inner + thickness




