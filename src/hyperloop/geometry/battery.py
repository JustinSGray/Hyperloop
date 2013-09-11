from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float


#NOTE: This is a VERY oversimplified calculation! But it gets us a ballpark figure
class Battery(Component): 

    energy = Float(160, iotype="in", units="kW*h", desc="total energy requirement for mission")
    cross_sectional_area = Float(1.3, iotype="in", units="m**2", desc="available cross section for battery pack")
    
    mass = Float(iotype="out", units="kg", desc="total mass of the batteries")
    volume = Float(iotype="out", units="m**3", desc="total volume of the batteries")
    length = Float(iotype="out", units="m", desc="required length of battery pack")

    def execute(self): 

        #gathered from http://en.wikipedia.org/wiki/Lithium-ion_battery
        specific_energy = .182 #.100-.265 kW*h/kg
        energy_density = 494 #250-739 kW*h/m**3

        self.mass = self.energy/specific_energy
        self.volume = self.energy/energy_density
        self.length = self.volume/self.cross_sectional_area
        


if __name__ == "__main__": 

    from openmdao.main.api import set_as_top

    comp = set_as_top(Battery())
    comp.run()


    print "mass (Kg): %f"%comp.mass
    print "volume (m**3): %f"%comp.volume
    print "length (m): %f"%comp.length


