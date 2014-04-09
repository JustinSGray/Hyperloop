from openmdao.main.api import Assembly
from openmdao.lib.datatypes.api import Float, Int
from openmdao.lib.drivers.api import BroydenSolver
from openmdao.lib.casehandlers.api import CSVCaseRecorder


from hyperloop.api import (TubeLimitFlow, CompressionSystem, TubeWallTemp,
    Pod, Mission)


class HyperloopPod(Assembly):

    #Design Variables
    Mach_pod_max = Float(1.0, iotype="in", desc="travel Mach of the pod")
    Mach_c1_in = Float(.6, iotype="in", desc="Mach number at entrance to the first \
        compressor at design conditions")
    Mach_bypass = Float(.95, iotype="in", desc="Mach in the air passing around the pod")
    c1_PR_des = Float(12.47, iotype="in", desc="pressure ratio of first compressor at \
        design conditions")
    Ps_tube = Float(99, iotype="in", desc="static pressure in the tube", units="Pa", 
        low=0)

    #Parameters
    solar_heating_factor = Float(.7, iotype="in",
      desc="Fractional amount of solar radiation to consider in tube temperature \
      calculations", low=0, high=1)
    tube_length = Float(563270, units = 'm', iotype='in', desc='Length of entire\
     Hyperloop')
    pwr_marg = Float(.3, iotype="in", desc="fractional extra energy requirement")
    hub_to_tip = Float(.4, iotype="in", desc="hub to tip ratio for the compressor")
    coef_drag = Float(2, iotype="in", desc="capsule drag coefficient")
    n_rows = Int(14, iotype="in", desc="number of rows of seats in the pod")
    length_row = Float(150, iotype="in", units="cm", desc="length of each row of seats")

    #Outputs
    #would go here if they existed for this assembly
    #var_name = Float(default_val, iotype="out", ...)