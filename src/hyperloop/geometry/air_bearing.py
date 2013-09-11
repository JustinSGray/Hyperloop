from math import pi, sin

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, Int


class AirBearing(Component): 

    tube_radius = Float(4, iotype="in", units="m", desc="radius of the tube")
    capsule_mass = Float(15000, iotype="in", units="kg", desc="mass of capsule")
    pressure = Float(9.4, iotype="in", units="kPa", desc="air injection pressure for bearings")
    n_bearings = Int(7, iotype="in", desc="number of rows of bearing pads") 
    sweep_angle = Float(4, iotype="in", units="deg", desc="sweep angle of a single bearing pad on tube wall")

    total_area = Float(iotype="out", units="m**2", desc="total required bearing area")
    area_per_bearing = Float(iotype="out", units="m**2", desc="required area per bearing")
    length_per_bearing = Float(iotype="out", units="m", desc="required length per bearing")
    bearing_width = Float(iotype="out", units="m", desc="lienar width of bearing")

    def execute(self): 

        req_area = self.capsule_mass*9.81/(self.pressure*1000) #convert to Pa from kPa
        req_area *= 1.5 #dirty hack to account for pressure gradient under bearing
        sweep_radians = self.sweep_angle*pi/180
        arc_length = self.tube_radius*sweep_radians

        

        self.total_area = req_area
        self.bearing_width = 2*self.tube_radius*sin(sweep_radians/2)

        #divide by two because there are two parallel skis
        req_total_length = req_area/arc_length/2
        self.length_per_bearing = req_total_length/self.n_bearings/2
        self.area_per_bearing = req_area/self.n_bearings/2


if __name__ == "__main__": 

    from openmdao.main.api import set_as_top

    comp = set_as_top(BearingSizing())
    comp.run()


    print "total_area (m**2): %f"%comp.total_area
    print "area_per_bearing (m**2): %f"%comp.area_per_bearing
    print "length_per_bearing (m): %f"%comp.length_per_bearing
    print "bearing_width (m): %f"%comp.bearing_width


