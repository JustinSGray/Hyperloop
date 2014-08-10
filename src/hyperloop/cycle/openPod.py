from openmdao.main.api import Assembly, Component
#from openmdao.lib.drivers.api import DOEdriver
from openmdao.lib.drivers.api import BroydenSolver
#from openmdao.lib.doegenerators.api import FullFactorial
#from openmdao.lib.casehandlers.api import DumpCaseRecorder
from openmdao.lib.datatypes.api import Float

from pycycle.api import (FlowStartStatic, SplitterBPR, Inlet, Compressor, Duct,
    Nozzle, CycleComponent, HeatExchanger, FlowStationVar, FlowStation)

import numpy as np

#class AreaCalc(Component):
#BPR can't be equal to 2

class CompressionSystem(Assembly): 

    #I/O Variables accessible on the boundary of the assembly 
    #NOTE: Some unit conversions to metric also happen here
    Mach_pod = Float(1.0, iotype="in", desc="travel Mach of the pod") #this gets overwritten
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa") 
    Ts_tube = Float(292.1, iotype="in", desc="static temperature in the tube", units="degK") #524 R
    A_pax = Float(14000, iotype="in", units="cm**2", desc="cross sectional area of the passenger capsule")
    #W_in = Float(.69, iotype="in", desc="mass flow rate into the compression system", units="kg/s")
    #BPR = Float(1, iotype="in", desc="bypass ratio")

    PR_des = Float(12.47, iotype="in", desc="pressure ratio of the compressor at design conditions")
    blockage_factor = Float(0.9, iotype="in", desc="ratio of the diffused area to the pod area")
    Mach_c1_in = Float(.65, iotype="in", desc="Mach number at entrance to the compressor at design conditions")

    #Mach_throat = Float(1.0, iotype="in", desc="throat Mach in the bypass duct")
    #A_diff = Float(iotype="out", desc="flow area required for the input to the first compressor", units="cm**2")
    A_tube = Float(iotype="out", desc="Tube Area", units="cm**2")
    A_tubeB = Float(iotype="out", desc="Tube Area minus TubeC", units="cm**2")
    A_tubeC = Float(iotype="out", desc="Area at the front of the diffuser", units="cm**2")
    A_diff = Float(iotype="out", desc="Area at tge back of the diffuser", units="cm**2")
    A_byp = Float(iotype="out", desc="Area bypassing the pod", units="cm**2")
    A_compressed = Float(iotype="out", desc="Area compressed throught the pod", units="cm**2")
    A_pod = Float(iotype="out", desc="Total pod area", units="cm**2")

    def configure(self):

        #Add Compressor Cycle Components
        start = self.add('start', FlowStartStatic())
        start.W = 3 #2.65451
        start.Pt = 0.02 # 0.02
        start.Tt = 305 # 550R

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
        #comp1.PR_des = 12.47  #(input above)
        #comp1.MNexit_des = .4
        comp1.eff_des = .90

        bypass_duct = self.add('bypass_duct', Duct()) #bypassed around pod
        bypass_duct.MNexit_des = 1.
        bypass_duct.Q_dot = 0.0 # no heat exchangers
        bypass_duct.dPqP = 0.0  # no losses

        int_duct = self.add('int_duct', Duct()) #compressed duct through pod
        int_duct.Q_dot = 0.0 # no heat exchangers
        int_duct.dPqP = 0.0  # no losses


        #Inter Component Connections
        self.connect('start.Fl_O', 'tube.Fl_I')
        self.connect('tube.Fl_O','split.Fl_I')
        #first flow path (through pod)
        self.connect('split.Fl_O1', 'inlet.Fl_I')
        self.connect('inlet.Fl_O', 'comp1.Fl_I')
        self.connect('comp1.Fl_O', 'int_duct.Fl_I')
        #second flow path (around pod)
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
        self.connect('Mach_c1_in', 'inlet.MNexit_des') #intake pre_exec block
        #Input -> C1
        self.connect('Mach_c1_in', 'comp1.MNexit_des') #cmp25 pre_exec block

        #Outputs (save to different names for debugging)
        self.connect('tube.Fl_O.area','A_tube') 
        self.connect('split.Fl_O2.area','A_tubeB') 
        self.connect('split.Fl_O1.area','A_tubeC') 
        self.connect('inlet.Fl_O.area','A_diff')
        self.connect('bypass_duct.Fl_O.area','A_byp')
        self.connect('comp1.Fl_O.area','A_compressed')
        self.connect('inlet.Fl_O.area/ blockage_factor','A_pod')

        #driver setup
        design = self.add('driver',BroydenSolver())
        comp_list = ['start','tube','split','inlet','comp1',
            'bypass_duct', 'int_duct']

        design.workflow.add(comp_list)
        for comp_name in comp_list: #need to put everything in design mode
            design.add_event('%s.design'%comp_name)


        #Add Solver
        #solver = self.add('solver',BroydenSolver())
        design.itmax = 50 #max iterations
        design.tol = .001

        #design.workflow.add('solver')  

        design.add_parameter('start.W',low=0.001,high=100)
        design.add_parameter('split.BPR', low=.1, high=10)
        #design.add_parameter('start')

        #design.add_constraint('split.BPR = 1.69752/0.95698')
        design.add_constraint('(inlet.Fl_O.area - comp1.Fl_O.area-2170.00434)/10000 = 0')
        design.add_constraint('(split.Fl_O2.area + split.Fl_O1.area -(bypass_duct.Fl_O.area + inlet.Fl_O.area/ blockage_factor))/1000= 0') #dep_Amatch


if __name__ == "__main__": 
    from math import pi
    from openmdao.main.api import set_as_top

    tube_A = []
    m_pod = []

    hlc = set_as_top(CompressionSystem())

    for mn in np.arange( 0.6, .92, 0.01 ):
        hlc.Mach_pod = mn

        if mn < hlc.Mach_c1_in:
            hlc.Mach_c1_in = mn
        hlc.run()
        tube_A.append(hlc.tube.Fl_O.area*0.00064516) #inches^2 to m^2
        m_pod.append(hlc.Mach_pod)

    print tube_A
    print m_pod    
    #print ""
    #print "Tube Ps = ", hlc.start.Ps
    #print "Tube Ts = ", hlc.start.Ts 
    #print "W = ", hlc.start.W
    #print "split W1 = ", hlc.split.Fl_O1.W
    #print "split W2 = ", hlc.split.Fl_O2.W
    #print "comp1.W = ", hlc.comp1.Fl_O.W
    #print ""

    #print "A_tube = ", hlc.A_tube
    #print "A_tubeB  = ", hlc.A_tubeB
    #print "A_tubeC = ", hlc.A_tubeC
    #print "A_byp = ", hlc.A_byp
    #print "hlc.A_diff/hlc.blockage_factor = ", (hlc.A_diff/hlc.blockage_factor)
    #print "A_compressed = ", hlc.A_compressed
    #print "A_pod = ", hlc.A_pod
    #print "A_pax = ", hlc.A_pax
    #print "BPR = ", hlc.split.BPR 
    

    #print "tube Mach = ", hlc.tube.Fl_O.Mach
    #print "split1 Mach = ", hlc.split.Fl_O1.Mach
    #print "split2 Mach = ", hlc.split.Fl_O2.Mach
    #print "inlet Mach = ", hlc.inlet.Fl_O.Mach
    #print "comp1 Mach = ", hlc.comp1.Fl_O.Mach
    #print "bypass_duct Mach = ", hlc.bypass_duct.Fl_O.Mach

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
    print ""
    #print "pwr: ", hlc.comp1.pwr+hlc.comp2.pwr,hlc.comp1.pwr,hlc.comp2.pwr 




