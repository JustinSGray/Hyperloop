from openmdao.main.api import Assembly, set_as_top, Run_Once, SequentialWorkflow
from openmdao.lib.drivers.api import BroydenSolver, DOEdriver
from openmdao.lib.doegenerators.api import FullFactorial
from openmdao.lib.casehandlers.api import DumpCaseRecorder

from pycycle.api import (FlowStart, Splitter, Inlet, Compressor, Duct, Splitter,
    Nozzle, )


class HyperloopCycle(Assembly): 

    def configure(self): 

        tube = self.add('tube', FlowStart())
        tube.W = 3.488
        tube.Pt = .0272
        tube.Tt = 630.75
        tube.Mach = 1.0

        tube_bypass = self.add('tube_bypass', Splitter())
        tube_bypass.BPR_des = 2.2285
        tube_bypass.MNexit1_des = 1.0
        tube_bypass.MNexit2_des = 1.0

        inlet = self.add('inlet', Inlet())
        inlet.ram_recovery = 1.0
        inlet.MNexit_des = .6

        comp1 = self.add('comp1', Compressor())
        comp1.PR_des = 12.47
        comp1.MNexit_des = .4
        comp1.eff_des = .80

        duct1 = self.add('duct1', Duct())
        duct1.Q_dot = -0
        duct1.dPqP = 0 #no losses

        split = self.add('split', Splitter())
        split.BPR_des = 2.2285
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
        self.connect('tube_bypass.Fl_O2', 'inlet.Fl_I')
        self.connect('inlet.Fl_O','comp1.Fl_I')
        self.connect('comp1.Fl_O', 'duct1.Fl_I')
        self.connect('duct1.Fl_O', 'split.Fl_I')
        self.connect('split.Fl_O2', 'nozzle.Fl_I')
        self.connect('tube.Fl_O', 'nozzle.Fl_ref')
        self.connect('split.Fl_O1', 'comp2.Fl_I')
        self.connect('comp2.Fl_O','to_bearings.Fl_I')


        #driver setup
        #self.driver.workflow = SequentialWorkflow()
        #design = self.add('design', Run_Once())
        design = self.driver

        #workflow definition

        comp_list = ['tube','tube_bypass','inlet','comp1',
            'duct1', 'split', 'nozzle', 'comp2', 'to_bearings']

        design.workflow.add(comp_list)
        for comp_name in comp_list: 
            design.add_event('%s.design'%comp_name)


if __name__ == "__main__": 

    hlc = set_as_top(HyperloopCycle())

    hlc.run()

    print "pwr: ", hlc.comp1.pwr+hlc.comp1.pwr
 

