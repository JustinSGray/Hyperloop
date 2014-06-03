import numpy as np

from openmdao.main.api import Component

from openmdao.lib.datatypes.api import Float


class Mission(Component): 
    """Place holder for real mission analysis. Could consider a 
    pseudospectral optimal control approach""" 
    #Inputs
    speed_max = Float(308, iotype="in", units="m/s", desc="Maximum travel speed for the pod")
    tube_length = Float(563270, iotype="in", units="m", desc="length of one trip")
    pwr_marg = Float(.3, iotype="in", desc="fractional extra energy requirement")
    pwr_req = Float(420, iotype="in", units="kW", desc="average power requriment for the mission")
    #Outputs
    time = Float(iotype="out", units="s", desc="travel time for a pod to make one trip")
    energy = Float(iotype="out", units="kW*h", desc="total energy storage requirements")

    def execute(self): 
        """this is a *VERY* course approximation that takes the speed profile given in the 
        original proposal as given. It just serves as a place holder for now. It's better 
        than nothing, but a real analysis is needed here""" 

        t1 = (300-0)*1609/(9.81*0.5)/3600; #time needed to accelerate
        t2 = (555-300)*1609/(9.81*0.5)/3600; #time needed to accelerate
        t3 = (self.speed_max-555)*1609/(9.81*0.5)/3600; #time needed to accelerate

        #speed profile data from hyperloop alpha proposal, pg 43
        dataStart = np.array([
            [0,0],
            [t1, 300*1.609],#(300[miles/hour]*1609[meters/mile])/(9.81[meters/second]*0.5)/3600[seconds/hr]
            [167, 300*1.609],
            [167+t2, 555*1.609],#(555-300[miles/hour]*1609[meters/mile])/(9.81[meters/second]*0.5)/3600[seconds/hr]
            [435, 555*1.609],
            [435+t3, self.speed_max]])
        startUp = np.trapz(dataStart[:,1]/3600, dataStart[:,0])*1000 #km covered during start up  Los Angeles Grapevine

        dataEnd = np.array([
            [0,self.speed_max],
            [t3, 555*1.609],
            [t3+100, 555*1.609],
            [t3+100+t2, 300*1.609],
            [t3+100+t2+400, 300*1.609],
            [t3+100+t2+400+t1, 0]])

        windDown = np.trapz(dataEnd[:,1]/3600, dataEnd[:,0])*1000 #km covered during wind down along I-580 to SF
        
        middleLength = self.tube_length - (startUp + windDown)
        middleTime = middleLength / (self.speed_max)

        self.time = middleTime + 435+t3 + t3+100+t2+400+t1

        self.energy = (self.pwr_req*self.time/3600.)*(1+self.pwr_marg) #convert to hours

        print self.itername 
        print " W_i: ", self.parent.compress.W_in, 10*(self.parent.compress.W_in-self.parent.flow_limit.W_excess)
        print "total mission time: ", self.time / 60 , " minutes"
        print " R_tube:  ", self.parent.pod.radius_tube_inner, .01*(self.parent.pod.area_compressor_bypass-self.parent.compress.area_c1_out)
        print " Bearing_Ps:  ", self.parent.compress.c2_PR_des, self.parent.compress.Ps_bearing_residual
        print 

if __name__ == "__main__": 

    from openmdao.main.api import set_as_top

    m = set_as_top(Mission())
    m.run()    





