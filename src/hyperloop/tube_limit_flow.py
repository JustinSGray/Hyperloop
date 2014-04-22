from math import pi
import numpy as np

import pylab as p

from openmdao.main.api import Component
from openmdao.main.api import convert_units as cu
from openmdao.lib.datatypes.api import Float

from pycycle.flowstation import FlowStation, secant

class TubeLimitFlow(Component): 
    """Finds the limit velocity for a body traveling through a tube"""
    #Inputs
    radius_tube = Float(111.5 , iotype="in", units="cm", desc="required radius for the tube")    
    radius_inlet = Float(73.7, iotype="in", units="cm", desc="radius of the inlet at it's largest point")
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa") 
    Ts_tube = Float(292.1, iotype="in", desc="static temperature in the tube", units="degK")
    Mach_pod = Float(1.0, iotype="in", desc="travel Mach of the pod")
    Mach_bypass = Float(.95, iotype="in", desc="Mach in the air passing around the pod")
    #Outputs
    limit_speed = Float(iotype="out", desc="pod travel speed where flow choking occurs", units="m/s")
    limit_Mach = Float(iotype="out", desc="pod travel Mach number where flow choking occurs")
    W_excess = Float(iotype="out", desc="excess tube mass flow above the Kantrowitz limit", units="kg/s")
    W_tube = Float(iotype="out", desc="Tube demand flow", units="kg/s")
    W_kant = Float(iotype="out", desc="Kantrowitz limit flow", units="kg/s")
    #mu_air = Float(iotype="out", desc="dynamic viscosity of air", units="Pa*s")

    def execute(self):

    	fs_tube = self.fs_tube = FlowStation()

        tube_rad = cu(self.radius_tube,'cm','ft') #convert to ft
        inlet_rad = cu(self.radius_inlet,'cm','ft')
        #A = pi(r^2) 
        self._tube_area  = pi*(tube_rad**2) #ft**2
        self._inlet_area  = pi*(inlet_rad**2) #ft**2
        self._bypass_area = self._tube_area - self._inlet_area

        self._Ts = cu(self.Ts_tube,'degK','degR') #convert to R
        self._Ps = cu(self.Ps_tube,'Pa','psi') #convert to psi

        area_ratio_target = self._tube_area/self._bypass_area

        #iterate over pod speed until the area ratio = A_tube / A_bypass
        def f(m_guess): 
            fs_tube.setStaticTsPsMN(self._Ts, self._Ps , m_guess) #set the static conditions iteratively until correct (Ts, Ps are known)
            gam = fs_tube.gamt
            g_exp = (gam+1)/(2*(gam-1))
            ar = ((gam+1)/2)**(-1*g_exp)*((1+ (gam-1)/2*m_guess**2)**g_exp)/m_guess
            return ar - area_ratio_target
        #Solve for Mach where AR = AR_target
        self.limit_Mach = secant(f, .3, x_min=0, x_max=1) #value not actually needed, fs_tube contains necessary flow information
        self.limit_speed = cu(fs_tube.Vflow,'ft','m') #convert to meters/second
        
        #excess mass flow calculation
        fs_tube.setStaticTsPsMN(self._Ts, self._Ps, self.Mach_pod)
        self.W_tube = cu(fs_tube.rhos*fs_tube.Vflow*self._tube_area,'lbm','kg') #convert to kg/sec

        fs_tube.Mach = self.Mach_bypass #Kantrowitz flow is at these total conditions, but with Mach 1
        self.W_kant = cu(fs_tube.rhos*fs_tube.Vflow*self._bypass_area,'lbm','kg') #convert to kg/sec
        #print "test", fs_tube.rhos, fs_tube.Vflow, self._bypass_area, self.W_kant

        self.W_excess = self.W_tube - self.W_kant

        #self.mu_air = self.fs_tube.mu/0.671968975


def plot_data(comp, c='b'):
    """utility function to make the Kantrowitz Limit Plot""" 

    MN = []
    W_tube = []
    W_kant = []

    for m in np.arange(.1,1.1,.1): 
        comp.Mach_pod = m
        comp.run()
        #print comp.radius_tube, comp.Mach_pod, comp.W_tube, comp.W_kant, comp.W_excess

        MN.append(m)
        W_kant.append(comp.W_kant)
        W_tube.append(comp.W_tube)

    fig = p.plot(MN,W_tube, '-', label="%3.1f Req."%(comp._tube_area/comp._inlet_area), lw=3, c=c)
    p.plot(MN,W_kant, '--', label="%3.1f Limit"%(comp._tube_area/comp._inlet_area),   lw=3, c=c)
    #p.legend(loc="best")
    p.tick_params(axis='both', which='major', labelsize=15)
    p.xlabel('Pod Mach Number', fontsize=18)
    p.ylabel('Flow Rate (kg/sec)', fontsize=18)
    p.title('Tube Flow Limits for Three Area Ratios', fontsize=20)

    return fig

    #print np.array(W_tube)- np.array(W_kant)


if __name__ == "__main__": 

    from openmdao.main.api import set_as_top
    comp = set_as_top(TubeLimitFlow())
    comp.radius_tube = 100
    comp.run()
    #print comp.Mach_pod, comp.W_tube, comp.W_kant, comp.W_excess
    #print comp.MN[-1]
    #print comp.W_tube[-1]
    #print comp.W_kant[-1]
    plot_data(comp,c='b')

    comp.radius_tube = 150
    plot_data(comp,c='g')

    comp.radius_tube = 200
    plot_data(comp,c='r')

    p.legend(loc="best")
    
    p.gcf().set_size_inches(11,5.5)
    p.gcf().savefig('test2png.png',dpi=130)
    p.show()