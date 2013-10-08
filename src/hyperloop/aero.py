from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float

#put inside pod
class Aero(Component): 
    """Place holder for real aerodynamic calculations of the capsule""" 

    coef_drag = Float(1, iotype="in", desc="capsule drag coefficient")
    area_capsule = Float(18000, iotype="in", units="cm**2", desc="capsule frontal area")
    velocity_capsule = Float(600, iotype="in", units="m/s", desc="capsule frontal area")
    rho = Float(iotype="in", units="kg/m**3", desc="tube air density") 
    gross_thrust = Float(iotype="in", units="N", desc="nozzle gross thrust") 
    
    net_force = Float(iotype="out", desc="Net force with drag considerations", units="N")
    drag = Float(iotype="out", units="N", desc="Drag Force")

    def execute(self): 

        #Drag = 0.5*Cd*rho*Veloc*Area
        self.drag = 0.5*self.coef_drag*self.rho*self.velocity_capsule*self.area_capsule 
        self.net_force = self.gross_thrust - self.drag
