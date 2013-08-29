from math import pi

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float


class BypassDuct(Component): 

    bypass_area = Float(845.5, iotype="in", units="cm**2", desc="required flow area for the fan")
    capsule_area = Float(14850, iotype="in", units="cm**2", desc="amount of area blocked by the passenger capsule")

    duct_radius = Float(.4, iotype="out", units="cm", desc="tip radius for the fan")

    def execute(self): 
        self.duct_radius = ((self.bypass_area+self.capsule_area)/pi)**.5

if __name__ == "__main__": 

    from openmdao.main.api import set_as_top

    f = set_as_top(BypassDuct())
    f.bypass_area = 845.5
    f.capsule_area = 14850
    f.execute()

    print "duct_radius (cm): %f"%f.duct_radius


