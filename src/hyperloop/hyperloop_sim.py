from openmdao.main.api import Assembly 
from openmdao.lib.datatypes.api import Float

from hyperloop.api import KantrowitzLimit, CompressionSystem, InletGeom

class Hyperloop(Assembly): 

    Mach_pod = Float(1.0, iotype="in", desc="travel Mach of the pod")
    radius_tube = Float(111.5 , iotype="in", units="cm", desc="required radius for the tube")
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa") 
    Ts_tube = Float(292.1, iotype="in", desc="static temperature in the tube", units="degK")

    def configure(self):

        kant = self.add('kant', KantrowitzLimit())

        self.connect('Mach_pod', 'kant.Mach_pod')
        self.connect('radius_tube', 'kant.radius_tube')
        self.connect('Ps_tube', 'kant.Ps_tube')
        self.connect('Ts_tube', 'kant.Ts_tube')

        compress = self.add('compress', CompressionSystem())
        self.connect('Mach_pod', 'compress.Mach_pod')
        self.connect('radius_tube', 'compress.radius_tube')
        self.connect('Ps_tube', 'compress.Ps_tube')
        self.connect('Ts_tube', 'compress.Ts_tube')
        self.create_passthrough('compress.Mach_c1_in')

        inlet_geom = self.add('inlet_geom', InletGeom())
        self.connect('compress.area_c1_in', 'inlet_geom.area_inlet')
        self.connect('inlet_geom.radius_outer','kant.radius_inlet')




