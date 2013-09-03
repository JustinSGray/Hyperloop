from os.path import dirname, join

from openmdao.main.api import Assembly

from openmdao.lib.components.api import GeomComponent
from openmdao.lib.geometry.diamond import GEMParametricGeometry

#hyperloop sizing calculations
import geometry
from geometry.battery import Battery
from geometry.bypass_duct import BypassDuct
from geometry.fan import Fan
from geometry.air_bearing import AirBearing




#ovearll geometry assembly
class Geometry(Assembly): 

    def configure(self): 
        self.add('fan', Fan())
        self.add('bypassDuct', BypassDuct())
        self.add('battery', Battery())
        self.add('air_bearing', AirBearing())

        self.add('geometry_model', GeomComponent())
        self.geometry_model.add('parametric_geometry', GEMParametricGeometry())

        #find the csm model file
        csm_model_file = join(dirname(geometry.__file__),'hyperloop2.csm')
        print csm_model_file
        exit()
        self.geometry_model.parametric_geometry.model_file = csm_model_file

        #print self.geometry_model.list_inputs()



if __name__ == "__main__": 
    from openmdao.main.api import set_as_top
    g = set_as_top(Geometry())
