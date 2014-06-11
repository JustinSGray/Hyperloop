from openmdao.main.api import Assembly, Component
#from openmdao.lib.drivers.api import DOEdriver
from openmdao.lib.drivers.api import BroydenSolver
#from openmdao.lib.doegenerators.api import FullFactorial
#from openmdao.lib.casehandlers.api import DumpCaseRecorder
from openmdao.lib.datatypes.api import Float

from pycycle.api import (FlowStartStatic, SplitterBPR, Inlet, Compressor, Duct,
    Nozzle, CycleComponent, HeatExchanger, FlowStationVar, FlowStation)


#class AreaCalc(Component):
#BPR can't be equal to 2

class CompressionSystem(Assembly): 

    #I/O Variables accessible on the boundary of the assembly 
    #NOTE: Some unit conversions to metric also happen here
    Mach_pod = Float(1.0, iotype="in", desc="travel Mach of the pod")
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa") 
    Ts_tube = Float(292.1, iotype="in", desc="static temperature in the tube", units="degK")
    W_in = Float(.69, iotype="in", desc="mass flow rate into the compression system", units="kg/s")
    A_pax = Float(14000, iotype="in", units="cm**2", desc="cross sectional area of the passenger capsule")
    #BPR = Float(1, iotype="in", desc="bypass ratio")

    PR_des = Float(12.47, iotype="in", desc="pressure ratio of the compressor at design conditions")
    blockage_factor = Float(1, iotype="in", desc="ratio of the diffused area to the pod area")
    Mach_c1_in = Float(.6, iotype="in", desc="Mach number at entrance to the compressor at design conditions")

    #Mach_throat = Float(1.0, iotype="in", desc="throat Mach in the bypass duct")
    #A_diff = Float(iotype="out", desc="flow area required for the input to the first compressor", units="cm**2")
    A_tube = Float(iotype="out", desc="flow area required for the output to the first compressor", units="cm**2")
    A_tubeB = Float(iotype="out", desc="flow area required for the output to the first compressor", units="cm**2")
    A_tubeC = Float(iotype="out", desc="flow area required for the output to the first compressor", units="cm**2")
    A_diff = Float(iotype="out", desc="flow area required for the output to the first compressor", units="cm**2")
    A_byp = Float(iotype="out", desc="flow area required for the output to the first compressor", units="cm**2")
    A_compressed = Float(iotype="out", desc="flow area required for the output to the first compressor", units="cm**2")
    A_pod = Float(iotype="out", desc="flow area required for the output to the first compressor", units="cm**2")

    def configure(self):

        #Add Compressor Cycle Components
        start = self.add('start', FlowStartStatic())
        start.W = 10.
        #start.Ps = 0.01436
        #start.Ts = 525.6

        tube = self.add('tube', Duct())
        tube.Q_dot = 0.0 # no heat exchangers
        tube.dPqP = 0.0  # no losses

        split = self.add('split', SplitterBPR()) #change this class def in pycycle
        #split.BPR = 1.
        #split.MNexit1_des = 1.0
        #split.MNexit2_des = 1.0

        inlet = self.add('inlet', Duct())
        inlet.Q_dot = 0.0 # no heat exchangers
        inlet.dPqP = 0.0  # no losses

        comp1 = self.add('comp1', Compressor())
        #comp1.PR_des = 12.47
        #comp1.MNexit_des = .4
        comp1.eff_des = .80

        bypass_duct = self.add('bypass_duct', Duct())
        bypass_duct.MNexit_des = 1.
        bypass_duct.Q_dot = 0.0 # no heat exchangers
        bypass_duct.dPqP = 0.0  # no losses

        int_duct = self.add('int_duct', Duct())
        int_duct.Q_dot = 0.0 # no heat exchangers
        int_duct.dPqP = 0.0  # no losses


        #Inter Component Connections
        self.connect('start.Fl_O', 'tube.Fl_I')
        self.connect('tube.Fl_O','split.Fl_I')
        #first flow path
        self.connect('split.Fl_O1', 'inlet.Fl_I')
        self.connect('inlet.Fl_O', 'comp1.Fl_I')
        self.connect('comp1.Fl_O', 'int_duct.Fl_I')
        #second flow path
        self.connect('split.Fl_O2', 'bypass_duct.Fl_I')
        

        #Input variable pass_throughs to the assembly boundary
        #Input -> start
        #self.connect('W_in', 'start.W')
        self.connect('Ts_tube','start.Ts')
        self.connect('Ps_tube', 'start.Ps')
        self.connect('Mach_pod', 'start.Mach')
        #Input -> tube
        self.connect('Mach_pod', 'tube.MNexit_des')
        #Input -> split
        #self.connect('BPR', 'split.BPR')
        self.connect('Mach_pod', 'split.MNexit1_des')
        self.connect('Mach_pod', 'split.MNexit2_des')
        #Input -> Inlet
        self.connect('Mach_c1_in', 'inlet.MNexit_des')
        #Input -> C1
        self.connect('Mach_c1_in', 'comp1.MNexit_des')

        #Outputs
        self.connect('tube.Fl_O.area','A_tube') 
        self.connect('split.Fl_O2.area','A_tubeB') 
        self.connect('split.Fl_O1.area','A_tubeC') 
        self.connect('inlet.Fl_O.area','A_diff')
        self.connect('bypass_duct.Fl_O.area','A_byp')
        self.connect('comp1.Fl_O.area','A_compressed')
        self.connect('inlet.Fl_O.area/ blockage_factor','A_pod')

        #driver setup
        design = self.driver
        comp_list = ['start','tube','split','inlet','comp1',
            'bypass_duct', 'int_duct']

        design.workflow.add(comp_list)
        for comp_name in comp_list: #need to put everything in design mode
            design.add_event('%s.design'%comp_name)


        #Add Solver
        solver = self.add('solver',BroydenSolver())
        solver.itmax = 50 #max iterations
        solver.tol = .001

        design.workflow.add('solver')  

        solver.add_parameter('start.W',low=0.001,high=100)
        solver.add_parameter('split.BPR', low=.1, high=10)

        #solver.add_constraint('W_in = 0.1')
        solver.add_constraint('A_diff - A_compressed = A_pax')
        solver.add_constraint('A_tubeB + A_tubeC = A_byp + A_pod')


if __name__ == "__main__": 
    from math import pi
    from openmdao.main.api import set_as_top

    hlc = set_as_top(CompressionSystem())
    hlc.Mach_pod = 0.7;
    hlc.run()

    print "A_tube = ", hlc.A_tube
    print "A_tubeB  = ", hlc.A_tubeB 
    print "A_tubeC = ", hlc.A_tubeC
    print "A_byp = ", hlc.A_byp
    print "hlc.A_diff/hlc.blockage_factor = ", hlc.A_diff/hlc.blockage_factor
    print "A_compressed = ", hlc.A_compressed
    print "A_pod = ", hlc.A_pod
    print "A_pax = ", hlc.A_pax
    print "BPR = ", hlc.split.BPR
    print "W = ", hlc.W_in, start.W

    print "tube Mach = ", hlc.tube.Fl_O.Mach
    print "split1 Mach = ", hlc.split.Fl_O1.Mach
    print "split2 Mach = ", hlc.split.Fl_O2.Mach
    print "inlet Mach = ", hlc.inlet.Fl_O.Mach
    print "comp1 Mach = ", hlc.comp1.Fl_O.Mach
    print "bypass_duct Mach = ", hlc.bypass_duct.Fl_O.Mach

    print "--- Test ---"
    print "A_tube = A_tubeC + A_tubeB"
    print hlc.A_tube, " = ", hlc.A_tubeC + hlc.A_tubeB
    print ""
    print "A_byp + A_pod =  A_tube"
    print hlc.A_byp + hlc.A_pod, " = ", hlc.A_tube
    print ""
    print "A_pax + A_compressed = A_diff"
    print hlc.A_pax + hlc.A_compressed, " = ", hlc.A_diff
    print ""
    print "A_pod * blockage_factor = A_diff"
    print hlc.A_pod * hlc.blockage_factor, " = ", hlc.A_diff

    #print "pwr: ", hlc.comp1.pwr+hlc.comp2.pwr,hlc.comp1.pwr,hlc.comp2.pwr 




