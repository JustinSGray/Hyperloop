from os.path import dirname, join

from openmdao.main.api import Assembly

from openmdao.lib.components.api import GeomComponent
from openmdao.lib.datatypes.api import Float

#hyperloop sizing calculations
from inlet import InletGeom 
from battery import Battery
from passenger_capsule import PassengerCapsule
from tube_structure import TubeStructural
from aero import Aero


#overall geometry assembly
class Pod(Assembly): 

    area_inlet_in = Float(iotype="in", units="cm**2", desc="flow area required at the front of the inlet")
    area_inlet_out = Float(iotype="in", units="cm**2", desc="flow area required at the back of the inlet")
    time_mission = Float(iotype="in", units="s", desc="travel time for a single trip")
    radius_tube_inner = Float(iotype="in", units="cm", desc="inner tube radius")
    rho_air = Float(iotype="in", units="cm", desc="air density (aero calcs)")

    radius_inlet_outer = Float(iotype="out", units="cm", desc="outer radius of the inlet")
    area_compressor_bypass = Float(iotype="out", units="cm**2", desc="area available to move compressed air around the passenger capsule")
    radius_tube_outer = Float(iotype="out", units="cm", desc="outer radius of tube")

    def configure(self): 

        #Add Components
        capsule = self.add('capsule', PassengerCapsule())
        tube = self.add('tube', TubeStructural())
        inlet = self.add('inlet', InletGeom())
        battery = self.add('battery', Battery())
        aero = self.add('aero',Aero())
        
        #Boundary Inputs
        #Pod->Inlet
        self.connect('area_inlet_in','inlet.area_in')
        self.connect('area_inlet_out','inlet.area_out')
        #Pod->Tube
        self.connect('radius_tube_inner', 'tube.radius_inner')
        #Pod -> Battery
        self.connect('time_mission','battery.time_mission')
        self.create_passthrough('battery.pwr_req')
        #Pod -> Aero
        self.connect('rho_air','aero.rho_air')

        #Inter Component Connections
        #Capsule -> Inlet
        self.connect('capsule.area_cross_section','inlet.area_passenger_capsule')
        #Capsule -> Battery
        self.connect('capsule.area_cross_section','battery.area_cross_section')

        #Boundary Outputs
        #Tube->Pod
        self.connect('tube.radius_outer','radius_tube_outer')
        #Inlet->Pod
        self.connect('inlet.radius_outer', 'radius_inlet_outer')
        self.connect('inlet.area_bypass', 'area_compressor_bypass')
        
        self.create_passthrough('capsule.area_cross_section')
        self.create_passthrough('battery.energy') 
        self.create_passthrough('aero.drag')  #not currently used, eventually passed to mission

        #Declare Workflow
        self.driver.workflow.add(['capsule','tube','inlet','battery','aero'])

    def run(self,*args,**kwargs): 
        super(Assembly, self).run(*args,**kwargs)


if __name__ == "__main__": 
    from openmdao.main.api import set_as_top
    g = set_as_top(Pod())
