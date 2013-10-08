from math import pi

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float


class InletGeom(Component): 
    """Calculates the dimentions for the inlet and compressor entrance"""
    #Inputs
    inlet_wall_thickness = Float(5, iotype="in", units="cm", desc="thickness of the inlet wall")
    area_in = Float(iotype="in", units="cm**2", desc="flow area required at the front of the inlet")
    area_out = Float(iotype="in", units="cm**2", desc="flow area required at the back of the inlet")
    hub_to_tip = Float(.4, iotype="in", desc="hub to tip ratio for the compressor")
    area_passenger_capsule = Float(14000, iotype="in", units="cm**2", desc="cross sectional area of the passenger capsule")
    #Outputs
    radius_back_inner = Float(iotype="out", units="cm", desc="inner radius of back of the inlet")
    radius_back_outer = Float(iotype="out", units="cm", desc="outer radius of back of the inlet")
    area_bypass = Float(iotype="out", units="cm**2", desc="available area to move bypass air around the passenger capsule")
    area_frontal = Float(iotype="out", units="cm**2", desc="total capsule frontal area")


    def execute(self): 
        self.radius_back_inner = (self.area_out/pi/(1-self.hub_to_tip**2))**.5
        self.radius_back_outer = self.radius_back_inner+self.inlet_wall_thickness
        self.area_bypass = pi*(self.radius_back_inner)**2 - self.area_passenger_capsule
        self.area_frontal = pi*(self.radius_back_outer)**2

if __name__ == "__main__": 

    from openmdao.main.api import set_as_top

    f = set_as_top(BypassDuct())
    f.execute()

    print "tube_radius (cm): %f"%f.tube_radius


