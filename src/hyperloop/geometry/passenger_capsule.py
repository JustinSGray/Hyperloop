from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, Int

class PassengerCapsule(Component): 
    """Place holder component for passenger capsule sizing and structural analysis.
    Currently, just assume the baseline shape from the original proposal""" 
    #Inputs
    n_rows = Int(14, iotype="in", desc="number of rows of seats in the pod")
    length_row = Float(150, iotype="in", units="cm", desc="length of each row of seats")
    #Outputs
    length_capsule = Float(iotype="out", units="cm", desc="overall length of the passenger capsule")
    area_cross_section = Float(iotype="out", units="cm**2", desc="cross sectional area of the passenger capsule")

    def execute(self):
        self.length_capsule = 1.1*self.n_rows*self.length_row #10% fudge factor
        self.area_cross_section = 14000 # page 15 of the original proposal
