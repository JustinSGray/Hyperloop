from openmdao.main.api import Assembly 
from openmdao.lib.datatypes.api import Float, Int
from openmdao.lib.drivers.api import BroydenSolver
from openmdao.lib.casehandlers.api import CSVCaseRecorder


#from hyperloop.api import (TubeLimitFlow, CompressionSystem, TubeWallTemp, Pod)
from cycle.compression_system import CompressionSystem
from tube_wall_temp import TubeWallTemp
from geometry.pod import Pod
from aero import Aero
from tube_limit_flow import TubeLimitFlow
from mission import Mission
from run_cases import mva, mvr, mvb


class HyperloopPod(Assembly): 

    #Design Variables
    Mach_pod_max = Float(1.0, iotype="in", desc="travel Mach of the pod")
    Mach_c1_in = Float(.6, iotype="in", desc="Mach number at entrance to the first compressor at design conditions")
    Mach_bypass = Float(.95, iotype="in", desc="Mach in the air passing around the pod")
    c1_PR_des = Float(12.47, iotype="in", desc="pressure ratio of first compressor at design conditions")    
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa", low=0)     

    #Parameters
    solar_heating_factor = Float(.7, iotype="in", 
      desc="Fractional amount of solar radiation to consider in tube temperature calculations", 
      low=0, high=1)
    tube_length = Float(563270, units = 'm', iotype='in', desc='Length of entire Hyperloop') 
    pwr_marg = Float(.3, iotype="in", desc="fractional extra energy requirement")
    hub_to_tip = Float(.4, iotype="in", desc="hub to tip ratio for the compressor")
    coef_drag = Float(2, iotype="in", desc="capsule drag coefficient")
    n_rows = Int(14, iotype="in", desc="number of rows of seats in the pod")
    length_row = Float(150, iotype="in", units="cm", desc="length of each row of seats")

    #outputs
    radius_tube_outer = Float(0, iotype="out", desc="final outer travel tube radius")
    temp_boundary = Float(0, iotype="out", desc="final equilibirum tube wall temperature")
   
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
        self.create_passthrough('compress.compressor_adiabatic_eff')

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
        self.connect('coef_drag','pod.coef_drag')
        self.connect('n_rows','pod.n_rows')
        self.connect('length_row','pod.length_row')
        self.connect('pod.radius_tube_outer', 'radius_tube_outer')


        #Hyperloop -> TubeWallTemp
        self.connect('solar_heating_factor', 'tube_wall_temp.nn_incidence_factor')
        self.connect('tube_length', 'tube_wall_temp.length_tube')
        self.create_passthrough('tube_wall_temp.temp_outside_ambient')
        self.create_passthrough('tube_wall_temp.solar_insolation')
        self.create_passthrough('tube_wall_temp.surface_reflectance')
        self.create_passthrough('tube_wall_temp.num_pods')
        self.create_passthrough('tube_wall_temp.emissivity_tube')
        self.create_passthrough('tube_wall_temp.Nu_multiplier')
        self.connect('tube_wall_temp.temp_boundary', 'temp_boundary')


        #Inter-component Connections
        #Compress -> Mission
        self.connect('compress.speed_max', 'mission.speed_max')
        self.connect('compress.pwr_req', 'mission.pwr_req')
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
        #Pod -> TubeWallTemp
        #self.connect('pod.radius_tube_outer', 'tube_wall_temp.radius_outer_tube')

        #Add Solver
        solver = self.add('solver',BroydenSolver())
        solver.itmax = 50 #max iterations
        solver.tol = .001
        #Add Parameters and Constraints
        solver.add_parameter('compress.W_in',low=-1e15,high=1e15)
        solver.add_parameter('compress.c2_PR_des', low=-1e15, high=1e15)
        solver.add_parameter(['compress.Ts_tube','flow_limit.Ts_tube','tube_wall_temp.temp_boundary'], low=-1e-15, high=1e15)
        solver.add_parameter(['flow_limit.radius_tube', 'pod.radius_tube_inner'], low=-1e15, high=1e15)

        solver.add_constraint('.01*(compress.W_in-flow_limit.W_excess) = 0')
        solver.add_constraint('compress.Ps_bearing_residual=0')
        solver.add_constraint('tube_wall_temp.ss_temp_residual=0')
        solver.add_constraint('.01*(pod.area_compressor_bypass-compress.area_c1_out)=0')

        driver = self.driver
        driver.workflow.add('solver')
        #driver.recorders = [CSVCaseRecorder(filename="hyperloop_data.csv")] #record only converged
        #driver.printvars = ['Mach_bypass', 'Mach_pod_max', 'Mach_c1_in', 'c1_PR_des', 'pod.radius_inlet_back_outer',
        #                    'pod.inlet.radius_back_inner', 'flow_limit.radius_tube', 'compress.W_in', 'compress.c2_PR_des',
        #                    'pod.net_force', 'compress.F_net', 'compress.pwr_req', 'pod.energy', 'mission.time',
        #                    'compress.speed_max', 'tube_wall_temp.temp_boundary']

        #Declare Solver Workflow
        solver.workflow.add(['compress','mission','pod','flow_limit','tube_wall_temp'])

if __name__=="__main__": 
    from collections import OrderedDict
    import numpy as np

    hl = HyperloopPod()
    #design variables
    hl.Mach_bypass = .95
    hl.Mach_pod_max = .8
    hl.Mach_c1_in = .65
    hl.c1_PR_des = 13

    #initial guesses
    # hl.compress.W_in = .35
    # hl.flow_limit.radius_tube = hl.pod.radius_tube_inner = 178
    # hl.compress.Ts_tube = hl.flow_limit.Ts_tube = hl.tube_wall_temp.tubeWallTemp = 322 
    # hl.compress.c2_PR_des = 5 

    hl.compress.W_in = .38
    hl.flow_limit.radius_tube = hl.pod.radius_tube_inner = 243
    hl.compress.Ts_tube = hl.flow_limit.Ts_tube = hl.tube_wall_temp.tubeWallTemp = 322.28
    hl.compress.c2_PR_des = 8.72

    #mvr(hl) #mach vs radius

    #mva(hl) #mach vs area ratio

    #mvb(hl) #mach vs battery/comp/missionTime

    hl.run()

    def pretty_print(data): 
        for label,value in data.iteritems(): 
            print '%s: %.2f'%(label,value)


    design_data = OrderedDict([
        ('Mach bypass', hl.Mach_bypass), 
        ('Max Travel Mach', hl.Mach_pod_max), 
        ('Fan Face Mach', hl.Mach_c1_in),
        ('C1 PR', hl.c1_PR_des)
    ])

    output_data = OrderedDict([
        ('Radius Inlet Outer',  hl.pod.radius_inlet_back_outer), 
        ('Radius Inlet Inner',  hl.pod.inlet.radius_back_inner), 
        ('Tube Inner Radius', hl.flow_limit.radius_tube),
        ('Pod W', hl.compress.W_in),
        ('Compressor C2 PR', hl.compress.c2_PR_des), 
        ('Pod Net Force', hl.pod.net_force), 
        ('Pod Thrust', hl.compress.F_net), 
        ('Pod Power', hl.compress.pwr_req), 
        ('Total Energy', hl.pod.energy), 
        ('Travel time', hl.mission.time), 
        ('Max Speed', hl.compress.speed_max), 
        ('Equilibirum Tube Temp', hl.tube_wall_temp.temp_boundary)
    ])

    

    print "======================"
    print "Design"
    print "======================"
    pretty_print(design_data)

    print "======================"
    print "Performance"
    print "======================"
    pretty_print(output_data)

    hl.flow_limit.radius_tube = hl.pod.radius_tube_inner = 242
    hl.run()

    design_data = OrderedDict([
        ('Mach bypass', hl.Mach_bypass), 
        ('Max Travel Mach', hl.Mach_pod_max), 
        ('Fan Face Mach', hl.Mach_c1_in),
        ('C1 PR', hl.c1_PR_des)
    ])

    output_data = OrderedDict([
        ('Radius Inlet Outer',  hl.pod.radius_inlet_back_outer), 
        ('Radius Inlet Inner',  hl.pod.inlet.radius_back_inner), 
        ('Tube Inner Radius', hl.flow_limit.radius_tube),
        ('Pod W', hl.compress.W_in),
        ('Compressor C2 PR', hl.compress.c2_PR_des), 
        ('Pod Net Force', hl.pod.net_force), 
        ('Pod Thrust', hl.compress.F_net), 
        ('Pod Power', hl.compress.pwr_req), 
        ('Total Energy', hl.pod.energy), 
        ('Travel time', hl.mission.time), 
        ('Max Speed', hl.compress.speed_max), 
        ('Equilibirum Tube Temp', hl.tube_wall_temp.temp_boundary)
    ])

    print "======================"
    print "Design"
    print "======================"
    pretty_print(design_data)

    print "======================"
    print "Performance"
    print "======================"
    pretty_print(output_data)

