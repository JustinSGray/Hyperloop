from openmdao.main.api import Assembly 
from openmdao.lib.datatypes.api import Float
from openmdao.lib.drivers.api import BroydenSolver 

from hyperloop.api import (TubeLimitFlow, CompressionSystem, TubeWallTemp,
    Pod, Mission)


class HyperloopPod(Assembly): 

    Mach_pod_max = Float(1.0, iotype="in", desc="travel Mach of the pod")
    #radius_tube = Float(111.5 , iotype="in", units="cm", desc="required radius for the tube")
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa", low=0)     
    SolarHeatingFactor = Float(.7, iotype="in", 
      desc="Fractional amount of solar radiation to consider in tube temperature calculations", 
      low=0, high=1)

    tube_length = Float(563270, units = 'm', iotype='in', desc='Length of entire Hyperloop') 


    def configure(self):

        #Add Components
        compress = self.add('compress', CompressionSystem())
        mission = self.add('mission', Mission())
        pod = self.add('pod', Pod())
        flow_limit = self.add('flow_limit', TubeLimitFlow())
        tube_wall_temp = self.add('tube_wall_temp', TubeWallTemp())

        #Boundary Inputs
        #Hyperloop -> Compress
        self.connect('Mach_pod_max', 'compress.Mach_pod_max')
        self.connect('Ps_tube', 'compress.Ps_tube')
        self.create_passthrough('compress.Mach_c1_in') #Design Variable
        #Hyperloop -> Mission
        self.connect('tube_length', 'mission.tube_length')
        #Hyperloop -> Flow Limit
        self.connect('Mach_pod_max', 'flow_limit.Mach_pod')
        self.connect('Ps_tube', 'flow_limit.Ps_tube')
        self.connect('pod.radius_inlet_outer', 'flow_limit.radius_inlet')
        self.create_passthrough('flow_limit.Mach_bypass')
        #Hyperloop -> TubeWallTemp
        self.connect('SolarHeatingFactor', 'tube_wall_temp.nn_incidence_factor')
        self.connect('tube_length', 'tube_wall_temp.length_tube')

        #Inter-component Connections
        #Compress -> Mission
        self.connect('compress.speed_max', 'mission.speed_max')
        #Compress -> Pod
        self.connect('compress.area_c1_in', 'pod.area_inlet_out')
        self.connect('compress.area_inlet_in', 'pod.area_inlet_in')
        self.connect('compress.pwr_req','pod.pwr_req')
        self.connect('compress.rho_air', 'pod.rho_air')
        #Compress -> TubeWallTemp
        self.connect('compress.nozzle_Fl_O', 'tube_wall_temp.nozzle_air')
        self.connect('compress.bearing_Fl_O', 'tube_wall_temp.bearing_air')
        #Mission -> Pod
        self.connect('mission.time','pod.time_mission')

        #Add Solver
        driver = self.add('driver',BroydenSolver())
        driver.itmax = 50 #max iterations
        driver.tol = .0001
        #Add Parameters and Constraints
        driver.add_parameter('compress.W_in',low=-1e15,high=1e15)
        driver.add_parameter(['compress.Ts_tube','flow_limit.Ts_tube','tube_wall_temp.temp_tube_wall'], low=-1e-15, high=1e15)
        driver.add_parameter(['compress.radius_tube','flow_limit.radius_tube', 'pod.radius_tube_inner'], low=-1e15, high=1e15)
        driver.add_constraint('10*(compress.W_in-flow_limit.W_excess) = 0')
        driver.add_constraint('tube_wall_temp.ss_temp_residual=0')
        driver.add_constraint('.01*(pod.area_compressor_bypass-compress.area_c1_out)=0')
        #Declare Solver Workflow
        driver.workflow.add(['compress','mission','pod','flow_limit','tube_wall_temp'])

if __name__=="__main__": 

    hl = HyperloopPod()
    hl.Mach_bypass = .9
    hl.Mach_pod_max = .85
    hl.compress.W_in = .5 #initial guess
    hl.compress.radius_tube = hl.flow_limit.radius_tube = 300 #initial guess
    hl.Mach_c1_in = .7
    hl.compress.Ts_tube = hl.flow_limit.Ts_tube = hl.tube_wall_temp.tubeWallTemp = 322 #initial guess
    hl.run()


    print "======================"
    print "Design"
    print "======================"
    print "Mach bypass: ", hl.Mach_bypass
    print "Max Travel Mach: ", hl.Mach_pod_max
    print "Tube Inner Radius: ", hl.flow_limit.radius_tube
    print "Fan Face Mach: ", hl.Mach_c1_in

    print "======================"
    print "Performance"
    print "======================"
    print "inlet_radius: ", hl.flow_limit.radius_inlet
    print "Pod W: ", hl.compress.W_in
    print "bearing W: ", hl.compress.W_bearing_in
    print "pwr: ", hl.compress.pwr_req
    print "energy: ", hl.pod.energy
    print "travel time: ", hl.mission.time/60
    print "speed:", hl.compress.speed_max
    print "Tube Temp: ", hl.tube_wall_temp.temp_tube_wall

