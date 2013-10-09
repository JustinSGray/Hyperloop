.. _`Usage`:

==============================
Usage Example
==============================

To use the hyperloop model, you want to run the file ``src\hyperloop\hyperloop_sim.py`` 
in the hyperloop repository. If you have already done that and you're ready to go, then 
you need not read any farther in this section. We're going to explain whats going on in
this file next. 

The file starts out with some library imports and the i/o definition of the HyperloopPod assembly. 

.. code:: 

    from openmdao.main.api import Assembly 
    from openmdao.lib.datatypes.api import Float, Int
    from openmdao.lib.drivers.api import BroydenSolver
    from openmdao.lib.casehandlers.api import CSVCaseRecorder


    from hyperloop.api import (TubeLimitFlow, CompressionSystem, TubeWallTemp,
        Pod, Mission)


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

        #Outputs
        #would go here if they existed for this assembly
        #var_name = Float(default_val, iotype="out", ...)

Next is the configure method, which is used to wire up the assembly components like the diagrams 
we show in the model layout section.

First we add an instance of each component class, then connect variables to and from each component.

.. code::

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
        self.connect('Mach_c1_in','compress.Mach_c1_in') #Design Variable
        #Hyperloop -> Mission
        self.connect('tube_length', 'mission.tube_length')
        self.connect('pwr_marg','mission.pwr_marg')
        #Hyperloop -> Pod
        #... 

        #Inter-component Connections
        #Compress -> Mission
        self.connect('compress.speed_max', 'mission.speed_max')
        #Compress -> Pod
        self.connect('compress.area_c1_in', 'pod.area_inlet_out')
        self.connect('compress.area_inlet_in', 'pod.area_inlet_in')

        #.. Add Boundary outputs...so on and so forth


Since assemblies often require iteration and convergence, a solver is then added. Each added 
parameter gives the solver variables to vary, until all declared constraints are satisfied.


.. code::

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
        driver.recorders = [CSVCaseRecorder(filename="hyperloop_data.csv")] #record only converged
        driver.printvars = ['Mach_bypass', 'Mach_pod_max', 'Mach_c1_in', 'c1_PR_des', 'pod.radius_inlet_back_outer',
                            'pod.inlet.radius_back_inner', 'flow_limit.radius_tube', 'compress.W_in', 'compress.c2_PR_des',
                            'pod.net_force', 'compress.F_net', 'compress.pwr_req', 'pod.energy', 'mission.time',
                            'compress.speed_max', 'tube_wall_temp.temp_boundary']

        #Declare Solver Workflow
        solver.workflow.add(['compress','mission','pod','flow_limit','tube_wall_temp'])

The final '''if __name__=="__main__":''' section works the same as you might see it in any 
other python script. This trick allows the user to set up conditional inputs and
parameters for the file to run by itself, rather than in conjunction with the rest of the 
optimization. Running stand-alone is much more convenient when initially building a component
and debugging.


.. code::

    if __name__=="__main__": 
        from collections import OrderedDict

        hl = HyperloopPod()
        #design variables
        hl.Mach_bypass = .95
        hl.Mach_pod_max = .7
        hl.Mach_c1_in = .65
        hl.c1_PR_des = 13

        #initial guesses
        hl.compress.W_in = .46 
        hl.flow_limit.radius_tube = hl.pod.radius_tube_inner = 324 
        hl.compress.Ts_tube = hl.flow_limit.Ts_tube = hl.tube_wall_temp.tubeWallTemp = 322 
        hl.compress.c2_PR_des = 5 
        
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

        def pretty_print(data): 
            for label,value in data.iteritems(): 
                print '%s: %.2f'%(label,value)


        print "======================"
        print "Design"
        print "======================"
        pretty_print(design_data)

        print "======================"
        print "Performance"
        print "======================"
        pretty_print(output_data)
