from openmdao.main.api import Assembly 
from openmdao.lib.datatypes.api import Float, Int
from openmdao.lib.drivers.api import BroydenSolver 

from hyperloop.api import (TubeLimitFlow, CompressionSystem, TubeWallTemp,
    Pod, Mission)


class HyperloopPod(Assembly): 

    #Inputs
    Mach_pod_max = Float(1.0, iotype="in", desc="travel Mach of the pod")
    Mach_c1_in = Float(.6, iotype="in", desc="Mach number at entrance to the first compressor at design conditions")
    Mach_bypass = Float(.95, iotype="in", desc="Mach in the air passing around the pod")
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa", low=0)     
    solar_heating_factor = Float(.7, iotype="in", 
      desc="Fractional amount of solar radiation to consider in tube temperature calculations", 
      low=0, high=1)
    tube_length = Float(563270, units = 'm', iotype='in', desc='Length of entire Hyperloop') 
    pwr_marg = Float(.3, iotype="in", desc="fractional extra energy requirement")
    speed_max = Float(iotype="in", desc="maximum velocity of the pod", units="m/s")
    hub_to_tip = Float(.4, iotype="in", desc="hub to tip ratio for the compressor")
    c1_PR_des = Float(12.47, iotype="in", desc="pressure ratio of first compressor at design conditions")    
    inlet_wall_thickness = Float(5, iotype="in", units="cm", desc="thickness of the inlet wall")
    coef_drag = Float(2, iotype="in", desc="capsule drag coefficient")
    n_rows = Int(14, iotype="in", desc="number of rows of seats in the pod")
    length_row = Float(150, iotype="in", units="cm", desc="length of each row of seats")



    def configure(self):

        #Add Components
        compress = self.add('compress', CompressionSystem())
        mission = self.add('mission', Mission())
        pod = self.add('pod', Pod())
        flow_limit = self.add('flow_limit', TubeLimitFlow())
        tube_wall_temp = self.add('tube_wall_temp', TubeWallTemp())

        #Boundary Input Connections
        #Hyperloop -> Compress
        self.connect('Mach_pod_max', 'compress.Mach_pod_max')
        self.connect('Ps_tube', 'compress.Ps_tube')
        self.connect('Mach_c1_in','compress.Mach_c1_in') #Design Variable
        self.connect('c1_PR_des', 'compress.c1_PR_des') #Design Variable
        #Hyperloop -> Mission
        self.connect('tube_length', 'mission.tube_length')
        self.connect('pwr_marg','mission.pwr_marg')
        #Hyperloop -> Flow Limit
        self.connect('Mach_pod_max', 'flow_limit.Mach_pod')
        self.connect('Ps_tube', 'flow_limit.Ps_tube')
        self.connect('pod.radius_inlet_back_outer', 'flow_limit.radius_inlet')
        self.connect('Mach_bypass','flow_limit.Mach_bypass')
        #Hyperloop -> Pod
        self.connect('Ps_tube', 'pod.Ps_tube')
        self.connect('hub_to_tip','pod.hub_to_tip')
        self.connect('inlet_wall_thickness','pod.inlet_wall_thickness')
        self.connect('coef_drag','pod.coef_drag')
        self.connect('n_rows','pod.n_rows')
        self.connect('length_row','pod.length_row')
        #Hyperloop -> TubeWallTemp
        self.connect('solar_heating_factor', 'tube_wall_temp.nn_incidence_factor')
        self.connect('tube_length', 'tube_wall_temp.length_tube')

        #Inter-component Connections
        #Compress -> Mission
        self.connect('compress.speed_max', 'mission.speed_max')
        #Compress -> Pod
        self.connect('compress.area_c1_in', 'pod.area_inlet_out')
        self.connect('compress.area_inlet_in', 'pod.area_inlet_in')
        self.connect('compress.rho_air', 'pod.rho_air')
        self.connect('compress.F_net','pod.F_net')
        self.connect('compress.speed_max', 'pod.speed_max')
        #Compress -> TubeWallTemp
        self.connect('compress.nozzle_Fl_O', 'tube_wall_temp.nozzle_air')
        self.connect('compress.bearing_Fl_O', 'tube_wall_temp.bearing_air')
        #Mission -> Pod
        self.connect('mission.time','pod.time_mission')
        self.connect('mission.energy', 'pod.energy')

        #Add Solver
        driver = self.add('driver',BroydenSolver())
        driver.itmax = 50 #max iterations
        driver.tol = .001
        #Add Parameters and Constraints
        driver.add_parameter('compress.W_in',low=-1e15,high=1e15)
        driver.add_parameter('compress.c2_PR_des', low=-1e15, high=1e15)
        driver.add_parameter(['compress.Ts_tube','flow_limit.Ts_tube','tube_wall_temp.temp_boundary'], low=-1e-15, high=1e15)
        driver.add_parameter(['flow_limit.radius_tube', 'pod.radius_tube_inner'], low=-1e15, high=1e15)

        driver.add_constraint('.01*(compress.W_in-flow_limit.W_excess) = 0')
        driver.add_constraint('compress.Ps_bearing_residual=0')
        driver.add_constraint('tube_wall_temp.ss_temp_residual=0')
        driver.add_constraint('.01*(pod.area_compressor_bypass-compress.area_c1_out)=0')

        #Declare Solver Workflow
        driver.workflow.add(['compress','mission','pod','flow_limit','tube_wall_temp'])

if __name__=="__main__": 

    hl = HyperloopPod()
    #design variables
    hl.Mach_bypass = .95
    hl.Mach_pod_max = .8
    hl.Mach_c1_in = .8
    hl.c1_PR_des = 12.5

    hl.compress.W_in = .38 #initial guess
    hl.flow_limit.radius_tube = hl.pod.radius_tube_inner = 209 #initial guess
    hl.compress.Ts_tube = hl.flow_limit.Ts_tube = hl.tube_wall_temp.tubeWallTemp = 322 #initial guess
    
    hl.run()


    print "======================"
    print "Design"
    print "======================"
    print "Mach bypass: ", hl.Mach_bypass
    print "Max Travel Mach: ", hl.Mach_pod_max
    print "Fan Face Mach: ", hl.Mach_c1_in

    print "======================"
    print "Performance"
    print "======================"
    print "radius_inlet_back_outer: ", hl.pod.radius_inlet_back_outer
    print "radius_inlet_back_inner: ", hl.pod.inlet.radius_back_inner
    print "Tube Inner Radius: ", hl.flow_limit.radius_tube
    print "Pod W: ", hl.compress.W_in
    print "bearing Ps: ", hl.compress.duct2.Fl_O.Ps*6894.75729
    print "Pod Net Force: ", hl.pod.net_force
    print "Pod Thrust: ", hl.compress.F_net 
    print "pwr: ", hl.compress.pwr_req
    print "energy: ", hl.pod.energy
    print "travel time: ", hl.mission.time/60
    print "speed:", hl.compress.speed_max
    print "Tube Temp: ", hl.tube_wall_temp.temp_boundary

