from openmdao.main.api import Assembly, Component
from openmdao.lib.drivers.api import DOEdriver
from openmdao.lib.doegenerators.api import FullFactorial
from openmdao.lib.casehandlers.api import DumpCaseRecorder
from openmdao.lib.datatypes.api import Float

from pycycle.api import (FlowStartStatic, SplitterW, Inlet, Compressor, Duct,
    Nozzle, CycleComponent, HeatExchanger, FlowStation)




class PwrSum(CycleComponent): 

    C1_pwr = Float(0, iotype='in', units='hp')
    C2_pwr = Float(0, iotype='in', units='hp')

    pwr = Float(0, iotype='out', units='hp')

    def execute(self): 

        self.pwr = self.C1_pwr + self.C2_pwr



class CompressionSystem(Assembly): 

    #I/O Variables accessible on the boundary of the assembly 
    #NOTE: Some unit conversions to metric also happen here
    Mach_pod_max = Float(1.0, iotype="in", desc="Maximum travel Mach of the pod")
    W_in = Float(.69, iotype="in", desc="mass flow rate into the compression system", units="kg/s")
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa") 
    Ts_tube = Float(292.1, iotype="in", desc="static temperature in the tube", units="degK")
    radius_tube = Float(111.5, iotype="in", desc="radius of the tube", units="cm")
    Mach_c1_in = Float(.6, iotype="in", desc="Mach number at entrance to the first compressor at design conditions")
    c1_PR_des = Float(12.47, iotype="in", desc="pressure ratio of first compressor at design conditions")
    c2_PR_des = Float(5, iotype="in", desc="pressure ratio of second compressor at design conditions")

    nozzle_Fl_O = FlowStation(iotype="out", desc="flow exiting the nozzle", copy=None)
    bearing_Fl_O = FlowStation(iotype="out", desc="flow exiting the bearings", copy=None)

    speed_max = Float(iotype="out", desc="maximum velocity of the pod", units="m/s")
    area_c1_in = Float(iotype="out", desc="flow area required for the first compressor", units="cm**2")
    area_inlet_in = Float(iotype="out", desc="flow area required for the first compressor", units="cm**2")
    nozzle_flow_area = Float(iotype="out", desc="flow area required for the nozzle exit", units="cm**2")
    pwr_req = Float(iotype="out", desc="pwr required to drivr the compression system", units="kW")

    def configure(self):

      

        tube = self.add('tube', FlowStartStatic())
        #tube.W = 1.521
        tube.Ps = 0.01436
        tube.Ts = 525.6

        inlet = self.add('inlet', Inlet())
        inlet.ram_recovery = 1.0
        #inlet.MNexit_des = .6

        comp1 = self.add('comp1', Compressor())
        comp1.PR_des = 12.47
        comp1.MNexit_des = .4
        comp1.eff_des = .80

        duct1 = self.add('duct1', Duct())
        duct1.Q_dot = 0# no heat exchangers
        duct1.dPqP = 0 #no losses

        split = self.add('split', SplitterW())
        split.W1_des = .44
        split.MNexit1_des = 1.0
        split.MNexit2_des = 1.0

        nozzle = self.add('nozzle', Nozzle())
        nozzle.dPqP = 0 #no losses

        comp2 = self.add('comp2', Compressor())
        comp2.PR_des = 5.0
        comp2.MNexit_des = .4
        comp2.eff_des = .80

        duct2 = self.add('duct2', Duct()) #to bearings
        duct2.Q_dot = 0 #no heat exchangers
        duct2.dPqP = 0 #no losses

        pwr_sum = self.add('pwr_sum', PwrSum())

        #Inter Component Connections
        self.connect('tube.Fl_O', 'inlet.Fl_I')
        self.connect('inlet.Fl_O','comp1.Fl_I')
        self.connect('comp1.Fl_O', 'duct1.Fl_I')
        self.connect('duct1.Fl_O', 'split.Fl_I')
        self.connect('split.Fl_O2', 'nozzle.Fl_I')
        self.connect('tube.Fl_O', 'nozzle.Fl_ref')
        self.connect('split.Fl_O1', 'comp2.Fl_I')
        self.connect('comp2.Fl_O','duct2.Fl_I')
        self.connect('comp1.pwr','pwr_sum.C1_pwr')
        self.connect('comp2.pwr','pwr_sum.C2_pwr')

        #variable pass_throughs to the assembly boundary
        self.connect('Mach_pod_max', 'tube.Mach')
        self.connect('Mach_c1_in', 'inlet.MNexit_des')
        self.connect('c1_PR_des','comp1.PR_des')
        self.connect('c2_PR_des','comp2.PR_des')
        self.connect('nozzle.Fl_O', 'nozzle_Fl_O')
        self.connect('duct2.Fl_O', 'bearing_Fl_O')
        self.connect('inlet.Fl_O.area', 'area_c1_in')
        self.connect('tube.Fl_O.area', 'area_inlet_in')
        self.connect('nozzle.Fl_O.area', 'nozzle_flow_area')
        self.connect('pwr_sum.pwr', 'pwr_req') 
        self.connect('tube.Fl_O.Vflow', 'speed_max')

        #driver setup
        design = self.driver
        comp_list = ['tube','inlet','comp1',
            'duct1', 'split', 'nozzle', 'comp2', 'duct2', 'pwr_sum']

        design.workflow.add(comp_list)
        for comp_name in comp_list: #need to put everything in design mode
            design.add_event('%s.design'%comp_name)


if __name__ == "__main__": 
    from math import pi
    from openmdao.main.api import set_as_top

    hlc = set_as_top(CompressionSystem())
    hlc.Mach_pod_max = 1
    hlc.run()

    print "pwr: ", hlc.comp1.pwr+hlc.comp2.pwr,hlc.comp1.pwr,hlc.comp2.pwr 
    print "tube area:", hlc.tube.Fl_O.area 
    print "tube Ps", hlc.tube.Fl_O.Ps, hlc.tube.Fl_O.Pt
    print "tube Rhos", hlc.tube.Fl_O.rhos
    print "tube W", hlc.tube.W
    print "inlet W", hlc.inlet.Fl_I.W
    print "tube rad: ", (hlc.tube.Fl_O.area/pi)**.5
    print "tube V: ", hlc.tube.Fl_O.Vflow, hlc.tube.Fl_O.Mach

    fs = hlc.tube.Fl_O




