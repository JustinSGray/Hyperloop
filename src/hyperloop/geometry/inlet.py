from math import pi

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float


class InletGeom(Component): 

    inlet_wall_thickness = Float(5, iotype="in", units="cm", desc="thickness of the inlet wall")
    area_in = Float(iotype="in", units="cm**2", desc="flow area required at the front of the inlet")
    area_out = Float(iotype="in", units="cm**2", desc="flow area required at the back of the inlet")

    radius_inner = Float(iotype="out", units="cm", desc="inner radius of the inlet")
    radius_outer = Float(iotype="out", units="cm", desc="outer radius of the inlet")
    blockage_area = Float(iotype="out", units="cm", desc="total area blocked by the inlet")

    def execute(self): 
        self.radius_inner = (self.area_out/pi)**.5
        self.radius_outer = self.radius_inner+self.inlet_wall_thickness
        self.blockage = pi*(self.radius_outer)**2


if __name__ == "__main__": 

    from openmdao.main.api import set_as_top

    f = set_as_top(BypassDuct())
    f.execute()

    print "tube_radius (cm): %f"%f.tube_radius


