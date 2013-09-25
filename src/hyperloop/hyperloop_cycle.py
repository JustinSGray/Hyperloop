from openmdao.main.api import Assembly, set_as_top, Run_Once, SequentialWorkflow
from openmdao.lib.drivers.api import BroydenSolver, DOEdriver
from openmdao.lib.doegenerators.api import FullFactorial
from openmdao.lib.casehandlers.api import DumpCaseRecorder
from openmdao.lib.datatypes.api import Float

from pycycle.api import (FlowStartStatic, Splitter, Inlet, Compressor, Duct, Splitter,
    Nozzle, )


class HyperloopCycle(Assembly): 

    #I/O Variables accessible on the boundary of the assembly 
    #NOTE: Some unit conversions to metric also happen here
    pod_Mach = Float(1.0, iotype="in", desc="travel Mach of the pod")
    tube_P = Float(99, iotype="in", desc="static pressure in the tube", units="Pa") 
    tube_T = Float(292.1, iotype="in", desc="static temperature in the tube", units="degK")
    tube_radius = Float(111.5, iotype="in", desc="radius of the tube", units="cm")
    c1_entrance_Mach = Float(.6, iotype="in", desc="Mach number at entrance to the first compressor at design conditions")
    c1_PR_des = Float(12.47, iotype="in", desc="pressure ratio of first compressor at design conditions")
    c1_q_dot = Float(0, iotype="in", desc="heat extracted from the flow after the first compressor stage", units="kW")
    c2_PR_des = Float(5, iotype="in", desc="pressure ratio of second compressor at design conditions")
    c2_q_dot = Float(0, iotype="in", desc="heat extracted from the flow after the second compressor stage", units="kW")

    bypass_flow_area = Float(iotype="out", desc="flow area required for the air bypassing the pod", units="cm**2")
    c1_flow_area = Float(iotype="out", desc="flow area required for the first compressor", units="cm**2")
    nozzle_flow_area = Float(iotype="out", desc="flow area required for the nozzle exit", units="cm**2")

    def configure(self):

        MN_DESIGN = 1 #Mach at the design condition

        tube = self.add('tube', FlowStartStatic())
        tube.W = 3.488
        tube.Ps = 0.01436
        tube.Ts = 525.6
        tube.Mach = MN_DESIGN

        tube_bypass = self.add('tube_bypass', Splitter())
        tube_bypass.BPR_des = 2.2285
        tube_bypass.MNexit1_des = MN_DESIGN
        tube_bypass.MNexit2_des = MN_DESIGN

        inlet = self.add('inlet', Inlet())
        inlet.ram_recovery = 1.0
        inlet.MNexit_des = .6

        comp1 = self.add('comp1', Compressor())
        comp1.PR_des = 12.47
        comp1.MNexit_des = .4
        comp1.eff_des = .80

        duct1 = self.add('duct1', Duct())
        duct1.Q_dot = -237
        duct1.dPqP = 0 #no losses

        split = self.add('split', Splitter())
        split.BPR_des = 1.45
        split.MNexit1_des = 1.0
        split.MNexit2_des = 1.0

        nozzle = self.add('nozzle', Nozzle())
        nozzle.dPqP = 0 #no losses

        comp2 = self.add('comp2', Compressor())
        comp2.PR_des = 5.0
        comp2.MNexit_des = .4
        comp2.eff_des = .80

        to_bearings = self.add('to_bearings', Duct())
        to_bearings.Q_dot = -24.138
        to_bearings.dPqP = 0 #no losses

        #Component Connections
        self.connect('tube.Fl_O','tube_bypass.Fl_I')
        self.connect('tube_bypass.Fl_O1', 'inlet.Fl_I')
        self.connect('inlet.Fl_O','comp1.Fl_I')
        self.connect('comp1.Fl_O', 'duct1.Fl_I')
        self.connect('duct1.Fl_O', 'split.Fl_I')
        self.connect('split.Fl_O2', 'nozzle.Fl_I')
        self.connect('tube.Fl_O', 'nozzle.Fl_ref')
        self.connect('split.Fl_O1', 'comp2.Fl_I')
        self.connect('comp2.Fl_O','to_bearings.Fl_I')

        #variable pass_throughs to the assembly boundary
        self.connect('pod_Mach', 'tube.Mach')
        self.connect('c1_entrance_Mach', 'inlet.MNexit_des')
        self.connect('c1_PR_des','comp1.PR_des')
        self.connect('c2_PR_des','comp2.PR_des')

        self.connect('tube_bypass.Fl_O1.area','bypass_flow_area')
        self.connect('inlet.Fl_O.area', 'c1_flow_area')
        self.connect('nozzle.Fl_O.area', 'nozzle_flow_area')

        #driver setup
        design = self.driver
        #design = self.add('driver', BroydenSolver())
        #design.add_parameter('tube.W', low=-1e15, high=1e15)
        #design.add_constraint('tube.Fl_O.area=(3.14159*tube_radius**2)*.394**2') #holds the radius of the tube constant

        comp_list = ['tube','tube_bypass','inlet','comp1',
            'duct1', 'split', 'nozzle', 'comp2', 'to_bearings']

        design.workflow.add(comp_list)
        for comp_name in comp_list: #need to put everything in design mode
            design.add_event('%s.design'%comp_name)


if __name__ == "__main__": 
    from math import pi

    hlc = set_as_top(HyperloopCycle())
    hlc.pod_Mach = 1
    hlc.run()

    print "pwr: ", hlc.comp1.pwr+hlc.comp2.pwr,hlc.comp1.pwr,hlc.comp2.pwr 
    print "tube area:", hlc.tube.Fl_O.area 
    print "tube Ps", hlc.tube.Fl_O.Ps, hlc.tube.Fl_O.Pt
    print "tube W", hlc.tube.W
    print "inlet W", hlc.inlet.Fl_I.W
    print "tube rad: ", (hlc.tube.Fl_O.area/pi)**.5
    print "tube V: ", hlc.tube.Fl_O.Vflow, hlc.tube.Fl_O.Mach

    fs = hlc.tube.Fl_O

    print "Kantrowitz Limit: ", fs.rhot*hlc.tube_bypass.Fl_O1.area*fs.Vflow
    l =  hlc.tube_bypass.Fl_O1.area*fs.Vflow/fs.area
    print "Limit Speed: ", l, l/fs.Vflow 



