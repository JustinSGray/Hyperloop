from math import pi

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float


class FanSizing(Component): 

    hub_to_tip = Float(.4, iotype="in", desc="hub to tip ratio for the fan")
    flow_area = Float(.4, iotype="in", units="cm**2", desc="required flow area for the fan")

    tip_radius = Float(.4, iotype="out", units="cm", desc="tip radius for the fan")
    hub_radius = Float(.4, iotype="out", units="cm", desc="hub radius for the fan")

    def execute(self): 
        self.tip_radius = (self.flow_area/(pi)*1/(1-self.hub_to_tip**2))**.5
        self.hub_radius = self.hub_to_tip*self.tip_radius

if __name__ == "__main__": 

    from openmdao.main.api import set_as_top

    f = set_as_top(FanSizing())
    f.hub_to_tip = .4
    f.flow_area = 14400
    f.execute()

    print "tip_radius (cm): %f"%f.tip_radius
    print "hub_radius (cm): %f"%f.hub_radius


