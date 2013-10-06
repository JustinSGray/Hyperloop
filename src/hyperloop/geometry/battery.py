from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float


#NOTE: This is a VERY oversimplified calculation! But it gets us a ballpark figure
class Battery(Component): 

    #energy = Float(160, iotype="in", units="kW*h", desc="total energy requirement for mission")
    time_mission = Float(2100, iotype="in", units="s", desc="pod travel time")
    pwr_req = Float(420, iotype="in", units="kW", desc="average power requriment for the mission")
    pwr_marg = Float(.3, iotype="in", desc="fractional extra energy requirement")
    cross_sectional_area = Float(1.3, iotype="in", units="m**2", desc="available cross section for battery pack")
    
    energy = Float(iotype="out", units="kW*h", desc="total energy storage requirements")
    mass = Float(iotype="out", units="kg", desc="total mass of the batteries")
    volume = Float(iotype="out", units="m**3", desc="total volume of the batteries")
    length = Float(iotype="out", units="m", desc="required length of battery pack")

    def execute(self): 

        #gathered from http://en.wikipedia.org/wiki/Lithium-ion_battery
        specific_energy = .182 #.100-.265 kW*h/kg
        energy_density = 494 #250-739 kW*h/m**3

        self.energy = (self.pwr_req*self.time_mission/3600.)*(1+self.pwr_marg) #convert to hours

        self.mass = self.energy/specific_energy
        self.volume = self.energy/energy_density
        self.length = self.volume/self.cross_sectional_area
        

if __name__ == "__main__": 

    from openmdao.main.api import set_as_top

    comp = set_as_top(Battery())
    comp.run()


    print "mass (Kg): %f"%comp.mass
    print "energy (kW*hr): %f"%comp.energy
    print "volume (m**3): %f"%comp.volume
    print "length (m): %f"%comp.length


