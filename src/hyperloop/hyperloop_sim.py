from openmdao.main.api import Assembly 
from openmdao.lib.datatypes.api import Float

from hyperloop.api import KantrowitzLimit

class Hyperloop(Assembly): 

    Mach_pod = Float(1.0, iotype="in", desc="travel Mach of the pod")
    
    def configure(self):

