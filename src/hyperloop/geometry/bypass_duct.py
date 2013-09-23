from math import pi

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float


class Tube(Component): 


    bypass_flow_area = Float(845.5, iotype="in", units="cm**2", desc="required flow area for the fan")
    c1_flow_area = Float(14850, iotype="in", units="cm**2", desc="amount of area blocked by the passenger capsule")
    inlet_wall_thickness = Float(5, iotype="in", units="cm", desc="thickness of the inlet wall")

    inlet_radius = Float(iotype="out", units="cm", desc="radius of the inlet at it's largest point")
    tube_radius = Float(iotype="out", units="cm", desc="required radius for the tube")

    def execute(self): 
        c1_rad = (self.c1_flow_area/pi)**.5 
        blockage = pi*(c1_rad+self.inlet_wall_thickness)**2
        self.tube_radius = ((self.bypass_area+blockage)/pi)**.5

if __name__ == "__main__": 

    from openmdao.main.api import set_as_top

    f = set_as_top(BypassDuct())
    f.bypass_area = 845.5
    f.capsule_area = 14850
    f.execute()

    print "tube_radius (cm): %f"%f.tube_radius


