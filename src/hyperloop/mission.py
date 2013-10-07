import numpy as np

from openmdao.main.api import Component

from openmdao.lib.datatypes.api import Float


#speed profile data from hyperloop alpha proposal
data = np.array([[0,0],
    [12.5, 300],
    [165, 300],
    [182, 555],
    [427, 555],
    [444, 760],
    [1660, 760],
    [1670, 555],
    [1756, 555],
    [1765, 300],
    [2112, 299],
    [2132, 0]])

max_speed = np.max(data[:,1])
data[:,1] /= max_speed #Normalize data

max_time = np.max(data[:,0])
data[:,0] /= max_time #Normalize data

#integrate normalized data to get an average speed fraction relative to the max speed
SPEED_FRAC = np.trapz(data[:,1], data[:,0])


class Mission(Component): 
    """Place holder for real mission analysis. Could consider a 
    pseudospectral optimal control approach""" 

    speed_max = Float(308, iotype="in", units="m/s", desc="Maximum travel speed for the pod")
    tube_length = Float(563270, iotype="in", units="m", desc="length of one trip")

    time = Float(iotype="out", units="s", desc="travel time for a pod to make one trip")


    def execute(self): 
        """this is a *VERY* course approximation that takes the speed profile given in the 
        original proposal as given. It just serves as a place holder for now. It's better 
        than nothing, but a real analysis is needed here""" 

        avg_speed = self.speed_max*SPEED_FRAC
        self.time = self.tube_length/avg_speed

        #print self.itername, self.parent.pod.inlet.area_out, self.parent.compress.W_in, self.parent.kant.W_excess, self.parent.compress.W_in-self.parent.kant.W_excess
        print self.itername, self.parent.compress.W_in, 20*(self.parent.compress.W_in-self.parent.kant.W_excess)


if __name__ == "__main__": 

    from openmdao.main.api import set_as_top

    m = set_as_top(Mission())
    m.run()    





