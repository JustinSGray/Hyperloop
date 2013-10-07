from os.path import dirname, join

from openmdao.main.api import Assembly

from openmdao.lib.components.api import GeomComponent
from openmdao.lib.datatypes.api import Float

#hyperloop sizing calculations
from inlet import InletGeom 
from battery import Battery
from passenger_capsule import PassengerCapsule


#ovearll geometry assembly
class Pod(Assembly): 

    area_inlet_in = Float(iotype="in", units="cm**2", desc="flow area required at the front of the inlet")
    area_inlet_out = Float(iotype="in", units="cm**2", desc="flow area required at the back of the inlet")
    time_mission = Float(iotype="in", units="s", desc="travel time for a single trip")

    radius_inlet_outer = Float(iotype="out", units="cm", desc="outer radius of the inlet")
    area_compressor_bypass = Float(iotype="out", units="cm**2", desc="area available to move compressed air around the passenger capsule")

    def configure(self): 


        capsule = self.add('capsule', PassengerCapsule())
        self.create_passthrough('capsule.area_cross_section')
        self.driver.workflow.add('capsule')

        inlet = self.add('inlet', InletGeom())
        self.connect('area_inlet_in','inlet.area_in')
        self.connect('area_inlet_out','inlet.area_out')
        self.connect('capsule.area_cross_section','inlet.area_passenger_capsule')
        self.connect('inlet.radius_outer', 'radius_inlet_outer')
        self.connect('inlet.area_bypass', 'area_compressor_bypass')
        self.driver.workflow.add('inlet')


        battery = self.add('battery', Battery())
        self.create_passthrough('battery.pwr_req')
        self.create_passthrough('battery.energy')
        self.connect('time_mission','battery.time_mission')
        self.connect('capsule.area_cross_section','battery.area_cross_section')
        self.driver.workflow.add('battery')



    def run(self,*args,**kwargs): 
        super(Assembly, self).run(*args,**kwargs)


if __name__ == "__main__": 
    from openmdao.main.api import set_as_top
    g = set_as_top(Pod())
