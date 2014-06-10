from openmdao.main.api import Assembly, Component
from openmdao.lib.drivers.api import DOEdriver
from openmdao.lib.doegenerators.api import FullFactorial
from openmdao.lib.casehandlers.api import DumpCaseRecorder
from openmdao.lib.datatypes.api import Float

from pycycle.api import (FlowStartStatic, SplitterW, Inlet, Compressor, Duct,
    Nozzle, CycleComponent, HeatExchanger, FlowStationVar, FlowStation)

import numpy as np


class PodSizing(Assembly): 

    #I/O Variables accessible on the boundary of the assembly 
    #NOTE: Some unit conversions to metric also happen here
    Mach_pod = Float(1.0, iotype="in", desc="travel Mach of the pod")
    Mach_throat = Float(1.0, iotype="in", desc="throat Mach in the bypass duct")


    def configure(self):

        #Add Compressor Cycle Components
        tube = self.add('tube', FlowStartStatic())
        tube.W = 10.
        tube.Ps = 0.01436
        tube.Ts = 525.6

        duct1 = self.add('duct1', Duct())
        duct1.Q_dot = 0.0 # no heat exchangers
        duct1.dPqP = 0.0  # no losses
        


        #Inter Component Connections
        self.connect('tube.Fl_O', 'duct1.Fl_I')

        #Input variable pass_throughs to the assembly boundary
        #input -> tube and duct
        self.connect('Mach_pod', 'tube.Mach')
        self.connect('Mach_throat', 'duct1.MNexit_des')


        #driver setup
        design = self.driver
        comp_list = ['tube', 'duct1' ]

        design.workflow.add(comp_list)
        for comp_name in comp_list: #need to put everything in design mode
            design.add_event('%s.design'%comp_name)


if __name__ == "__main__": 
    from math import pi
    from openmdao.main.api import set_as_top

    
    tubeA = []
    throatA = []
    MNpod = []
    MNthroat = []
    AR = []

    hlc = set_as_top(PodSizing())
    for mn in np.arange( 0.10, .91, 0.10 ):
        hlc.Mach_pod = mn
        for mnbyp in np.arange( mn, 1.21, 0.02 ):
            hlc.Mach_throat = mnbyp
            hlc.run()
            MNpod.append( hlc.tube.Fl_O.Mach )
            MNthroat.append( hlc.duct1.Fl_O.Mach )
            tubeA.append( hlc.tube.Fl_O.area )
            throatA.append( hlc.duct1.Fl_O.area )
            AR.append( hlc.duct1.Fl_O.area/hlc.tube.Fl_O.area )
    print MNpod
    print MNthroat
    print tubeA
    print throatA
    print AR    
    #print "tube area:", hlc.tube.Fl_O.area 
    #print "tube Ps", hlc.tube.Fl_O.Ps, hlc.tube.Fl_O.Pt
    #print "tube W", hlc.tube.W
