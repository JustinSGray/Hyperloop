from openmdao.main.api import Assembly 
from openmdao.lib.datatypes.api import Float
from openmdao.lib.drivers.api import BroydenSolver 
from openmdao.lib.drivers.newton_krylov import NewtonKyrlovSolver

from hyperloop.api import (KantrowitzLimit, CompressionSystem, InletGeom, Battery, TubeWall,
    Pod)


class HyperloopPod(Assembly): 

    Mach_pod = Float(1.0, iotype="in", desc="travel Mach of the pod")
    radius_tube = Float(111.5 , iotype="in", units="cm", desc="required radius for the tube")
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa", low=0)     
    SolarHeatingFactor = Float(.7, iotype="in", 
      desc="Fractional amount of solar radiation to consider in tube temperature calculations", 
      low=0, high=1)


    def configure(self):

        compress = self.add('compress', CompressionSystem())
        self.connect('Mach_pod', 'compress.Mach_pod')
        self.connect('radius_tube', 'compress.radius_tube')
        self.connect('Ps_tube', 'compress.Ps_tube')
        self.create_passthrough('compress.Mach_c1_in')
        self.create_passthrough('compress.pwr_req')


        pod = self.add('pod', Pod())
        self.connect('compress.area_c1_in', 'pod.area_inlet_out')
        self.connect('compress.area_inlet_in', 'pod.area_inlet_in')

        kant = self.add('kant', KantrowitzLimit())
        self.connect('Mach_pod', 'kant.Mach_pod')
        self.connect('radius_tube', 'kant.radius_tube')
        self.connect('Ps_tube', 'kant.Ps_tube')
        self.connect('pod.radius_inlet_outer', 'kant.radius_inlet')

        battery = self.add('battery', Battery())
        self.connect('compress.pwr_req','battery.pwr_req')
        self.create_passthrough('battery.energy')

        tube_wall = self.add('tube_wall', TubeWall())
        self.connect('compress.nozzle_Fl_O', 'tube_wall.nozzle_air')
        self.connect('compress.bearing_Fl_O', 'tube_wall.bearing_air')
        self.connect('SolarHeatingFactor', 'tube_wall.nnIncidenceF')

        driver = self.add('driver',BroydenSolver())
        driver.add_parameter('compress.W_in',low=-1e15,high=1e15)
        driver.add_constraint('compress.W_in=kant.W_excess')

        driver.add_parameter(['compress.Ts_tube','kant.Ts_tube','tube_wall.tubeWallTemp'], low=-1e-15, high=1e15)
        driver.add_constraint('tube_wall.ssTemp_residual=0')

        driver.workflow.add(['compress','pod','kant','battery','tube_wall'])


if __name__=="__main__": 

    hl = HyperloopPod()
    hl.Mach_pod = .9
    hl.compress.Ts_tube = hl.kant.Ts_tube = hl.tube_wall.tubeWallTemp = 322
    hl.run()

    print "pwr: ", hl.pwr_req
    print "energy: ", hl.energy
    print "W: ", hl.compress.W_in
    print "radius_inlet_outer: ", hl.pod.radius_inlet_outer
    print "Tube Temp: ", hl.tube_wall.tubeWallTemp




    



