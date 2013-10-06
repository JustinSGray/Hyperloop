from os.path import dirname, join

from openmdao.main.api import Assembly

from openmdao.lib.components.api import GeomComponent
from openmdao.lib.datatypes.api import Float

#hyperloop sizing calculations
from inlet import InletGeom


#ovearll geometry assembly
class Pod(Assembly): 

    area_inlet_in = Float(iotype="in", units="cm**2", desc="flow area required at the front of the inlet")
    area_inlet_out = Float(iotype="in", units="cm**2", desc="flow area required at the back of the inlet")
    
    radius_inlet_outer = Float(iotype="out", units="cm", desc="outer radius of the inlet")

    def configure(self): 

        inlet = self.add('inlet', InletGeom())
        self.connect('area_inlet_in','inlet.area_in')
        self.connect('area_inlet_out','inlet.area_out')
        self.connect('inlet.radius_outer', 'radius_inlet_outer',)
        self.driver.workflow.add('inlet')

    def run(self,*args,**kwargs): 
        super(Assembly, self).run(*args,**kwargs)


if __name__ == "__main__": 
    from openmdao.main.api import set_as_top
    g = set_as_top(Pod())
