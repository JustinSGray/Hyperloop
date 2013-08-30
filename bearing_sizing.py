from math import pi

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, Int


class BearingSizing(Component): 

    tube_radius = Float(4, iotype="in", units="m", desc="radius of the tube")
    capsule_mass = Float(15000, iotype="in", units="kg", desc="mass of capsule")
    pressure = Float(9.4, iotype="in", units="kPa", desc="air injection pressure for bearings")
    n_bearings = Int(6, iotype="in", desc="number of independent bearing pads") 
    sweep_angle = Float(20, iotype="in", units="deg", desc="sweep angle of a single bearing pad on tube wall")

    total_area = Float(iotype="out", units="m**2", desc="total required bearing area")
    area_per_bearing = Float(iotype="out", units="m**2", desc="required area per bearing")
    length_per_bearing = Float(iotype="out", units="m", desc="required length per bearing")

    def execute(self): 

        req_area = self.capsule_mass*9.81/(self.pressure*1000) #convert to Pa from kPa
        req_area *= 1.5 #dirty hack to account for pressure gradient under bearing
        
        arc_length = self.tube_radius*self.sweep_angle*pi/180

        req_total_length = req_area/arc_length

        self.total_area = req_area
        self.length_per_bearing = req_total_length/self.n_bearings
        self.area_per_bearing = req_area/self.n_bearings

if __name__ == "__main__": 

    from openmdao.main.api import set_as_top

    comp = set_as_top(BearingSizing())
    comp.run()


    print "total_area (m**2): %f"%comp.total_area
    print "area_per_bearing (m**2): %f"%comp.area_per_bearing
    print "length_per_bearing (m): %f"%comp.length_per_bearing


