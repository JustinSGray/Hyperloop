from openmdao.main.api import Assembly 
from openmdao.lib.datatypes.api import Float
from openmdao.lib.drivers.api import BroydenSolver 

from hyperloop.api import KantrowitzLimit, CompressionSystem, InletGeom, Battery

class HyperloopPod(Assembly): 

    Mach_pod = Float(1.0, iotype="in", desc="travel Mach of the pod")
    radius_tube = Float(111.5 , iotype="in", units="cm", desc="required radius for the tube")
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa") 
    Ts_tube = Float(292.1, iotype="in", desc="static temperature in the tube", units="degK")


    def configure(self):

        compress = self.add('compress', CompressionSystem())
        self.connect('Mach_pod', 'compress.Mach_pod')
        self.connect('radius_tube', 'compress.radius_tube')
        self.connect('Ps_tube', 'compress.Ps_tube')
        self.connect('Ts_tube', 'compress.Ts_tube')
        self.create_passthrough('compress.Mach_c1_in')
        self.create_passthrough('compress.pwr_req')


        inlet_geom = self.add('inlet_geom', InletGeom())
        self.connect('compress.area_c1_in', 'inlet_geom.area_inlet')

        kant = self.add('kant', KantrowitzLimit())
        self.connect('Mach_pod', 'kant.Mach_pod')
        self.connect('radius_tube', 'kant.radius_tube')
        self.connect('Ps_tube', 'kant.Ps_tube')
        self.connect('Ts_tube', 'kant.Ts_tube')
        self.connect('inlet_geom.radius_outer', 'kant.radius_inlet')

        battery = self.add('battery', Battery())
        self.connect('compress.pwr_req','battery.pwr_req')
        self.create_passthrough('battery.energy')

        driver = self.add('driver',BroydenSolver())
        driver.add_parameter('compress.W_in',low=-1e15,high=1e15)
        driver.add_constraint('compress.W_in=kant.W_excess')

        driver.workflow.add(['compress','inlet_geom','kant','battery'])


if __name__=="__main__": 

    hl = HyperloopPod()
    hl.Mach_pod = .9
    hl.run()

    print "pwr: ", hl.pwr_req
    print "energy: ", hl.energy
    print "W: ", hl.compress.W_in
    print "C1.Fl_O.Pt: ", hl.compress.comp1.Fl_O.Pt




    



