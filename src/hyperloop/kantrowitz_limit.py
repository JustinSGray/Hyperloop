from math import pi
import numpy as np

import pylab as p

from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float

from pycycle.flowstation import CanteraFlowStation, secant

class KantrowitzLimit(Component): 
    """finds the Kantrowitz limit velocity for a body traveling through a tube"""

    tube_radius = Float(111.5 , iotype="in", units="cm", desc="required radius for the tube")    
    inlet_radius = Float(73.7, iotype="in", units="cm", desc="radius of the inlet at it's largest point")
    pod_radius = Float()
    Ps = Float(99, iotype="in", desc="static pressure in the tube", units="Pa") 
    Ts = Float(292.1, iotype="in", desc="static temperature in the tube", units="degK")

    limit_speed = Float(iotype="out", desc="pod travel speed where flow choking occurs", units="m/s")
    limit_Mach = Float(iotype="out", desc="pod travel Mach number where flow choking occurs")
    def execute(self):

    	fs_tube = CanteraFlowStation()
        fs_kant = CanteraFlowStation()

        MN = []
        W_tube = []
        W_kant = []

        tube_rad = self.tube_radius*0.0328084 #convert to ft
        inlet_rad = self.inlet_radius*0.0328084

        tube_area = pi*(tube_rad**2) #ft**2
        bypass_area = pi*(tube_rad**2-inlet_rad**2)

        area_ratio_target = tube_area/bypass_area

        def f(m_guess): 
            fs_tube.setStaticTsPsMN(self.Ts*1.8, self.Ps*0.000145037738, m_guess)
            gam = fs_tube.gamt
            g_exp = (gam+1)/(2*(gam-1))
            ar = ((gam+1)/2)**(-1*g_exp)*((1+ (gam-1)/2*m_guess**2)**g_exp)/m_guess
            return ar - area_ratio_target

        self.limit_Mach = secant(f, .1, x_min=0, x_max=1)
        self.limit_speed = fs_tube.Vflow*0.3048 #convert to meters

        

        for m in np.arange(.1,1.1,.1): 
            MN.append(m)
            fs_tube.setStaticTsPsMN(self.Ts*1.8, self.Ps*0.000145037738, m)

            w_tube = fs_tube.rhos*fs_tube.Vflow*tube_area
            fs_tube.W = w_tube
            #W_tube.append(w_tube*0.45359237)
            W_tube.append(w_tube)
           
            fs_tube.W = w_tube
            fs_tube.Mach = 1

            #print fs_tube.area, (bypass_area*144)
            #exit()

            def f(w_guess):
                fs_tube.W = w_guess
                return fs_tube.area - (bypass_area*144) #convert to inch**2

            w_kant = secant(f, w_tube, x_min=0.)
            #print w_kant, w_tube, fs_tube.area, bypass_area*144
            #print w_kant, w_tube
            #W_kant.append(w_kant*0.45359237)
            W_kant.append(w_kant)

        self.MN = MN
        self.W_kant = W_kant
        self.W_tube = W_tube
            

    def plot_data(self):
        p.plot(self.MN,self.W_tube, label="Required Tube Flow", lw=5)
        p.plot(self.MN,self.W_kant, label="Kantrowitz Limit",   lw=5)
        p.legend(loc="best")
        p.xlabel('Pod Mach Number')
        p.ylabel('Mass Flow Rate (kg/sec)')
        p.title('Kantrowitz Limit Flow')
        p.show()

        


if __name__ == "__main__": 

    from openmdao.main.api import set_as_top
    comp = set_as_top(KantrowitzLimit())
    #comp.tube_radius = 200
    comp.run()
    print comp.limit_speed, comp.limit_Mach
    #print comp.MN[-1]
    #print comp.W_tube[-1]
    #print comp.W_kant[-1]
    print "excess mass flow at Mach %1.1f: %f"%(comp.MN[-1], comp.W_tube[-1]-comp.W_kant[-1])
    #comp.plot_data()