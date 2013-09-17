from openmdao.main.api import Assembly, set_as_top

from pycycle.api import FlowStart, Splitter, Inlet


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


        #Component Connections
        self.connect('tube.Fl_O','tube_bypass.Fl_I')
        self.connect('tube_bypass.Fl_O2', 'inlet.Fl_I')

        #workflow definition
        self.driver.workflow.add('tube')
        self.driver.add_event('tube.design')

        self.driver.workflow.add('tube_bypass')
        self.driver.add_event('tube_bypass.design')

        self.driver.workflow.add('inlet')
        self.driver.add_event('inlet.design')        

        #self.driver.workflow.add()
        #self.driver.add_event()


if __name__ == "__main__": 

    hlc = set_as_top(HyperloopCycle())

    hlc.run()


