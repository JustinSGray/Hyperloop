"""
    tubeModel.py - 
        Determines the steady state temperature of the hyperloop tube.
        Calculates Q released/absorbed by hyperloop tube due to:
        Internal Convection, Tube Conduction, Ambient Natural Convection, Solar Flux In, Radiation Out
        
    -original calculations from Jeff Berton, ported and extended by Jeff Chin

    Compatible with OpenMDAO v0.8.1
"""
from math import log, pi, sqrt, e

from openmdao.main.api import Assembly, Component
from openmdao.lib.drivers.api import BroydenSolver 
from openmdao.lib.datatypes.api import Float, Bool
from openmdao.main.api import convert_units as cu

from pycycle.api import FlowStationVar


class TubeWallTemp(Component):
    """ Calculates Q released/absorbed by the hyperloop tube """
    #--Inputs--
    #Hyperloop Parameters/Design Variables
    diameter_outer_tube = Float(2.23, units = 'm', iotype='in', desc='tube outer diameter') #7.3ft
    length_tube = Float(482803, units = 'm', iotype='in', desc='Length of entire Hyperloop') #300 miles, 1584000ft
    num_pods = Float(34, units = 'K', iotype='in', desc='Number of Pods in the Tube at a given time') #
    temp_boundary = Float(322.0, units = 'K', iotype='in', desc='Average Temperature of the tube wall') #
    temp_outside_ambient = Float(305.6, units = 'K', iotype='in', desc='Average Temperature of the outside air') #
    nozzle_air = FlowStationVar(iotype="in", desc="air exiting the pod nozzle", copy=None)
    bearing_air = FlowStationVar(iotype="in", desc="air exiting the air bearings", copy=None)
    #constants
    solar_insolation = Float(1000., iotype="in", units = 'W/m**2', desc='solar irradiation at sea level on a clear day') #
    nn_incidence_factor = Float(0.7, iotype="in", desc='Non-normal incidence factor') #
    surface_reflectance = Float(0.5, desc='Solar Reflectance Index') #
    q_per_area_solar = Float(350., units = 'W/m**2', desc='Solar Heat Rate Absorbed per Area') #
    q_total_solar = Float(375989751., iotype="in", units = 'W', desc='Solar Heat Absorbed by Tube') #
    emissivity_tube = Float(0.5, iotype="in", units = 'W', desc='Emmissivity of the Tube') #
    sb_constant = Float(0.00000005670373, iotype="in", units = 'W/((m**2)*(K**4))', desc='Stefan-Boltzmann Constant') #

    #--Outputs--
    area_rad = Float(337486.1, units = 'm**2', iotype='out', desc='Tube Radiating Area') #    
    #Required for Natural Convection Calcs
    GrDelTL3 = Float(1946216.7, units = '1/((ft**3)*F)', iotype='out', desc='Heat Radiated to the outside') #
    Pr = Float(0.707, iotype='out', desc='Prandtl') #
    Gr = Float(12730351223., iotype='out', desc='Grashof #') #
    Ra = Float(8996312085., iotype='out', desc='Rayleigh #') #
    Nu = Float(232.4543713, iotype='out', desc='Nusselt #') #
    k = Float(0.02655, units = 'W/(m*K)', iotype='out', desc='Thermal conductivity') #
    h = Float(0.845464094, units = 'W/((m**2)*K)', iotype='out', desc='Heat Radiated to the outside') #
    area_convection = Float(3374876.115, units = 'W', iotype='out', desc='Convection Area') #
    #Natural Convection
    q_per_area_nat_conv = Float(7.9, units = 'W/(m**2)', iotype='out', desc='Heat Radiated per Area to the outside') #
    total_q_nat_conv = Float(286900419., units = 'W', iotype='out', desc='Total Heat Radiated to the outside via Natural Convection') #
    #Exhausted from Pods
    heat_rate_pod = Float(519763, units = 'W', iotype='out', desc='Heating Due to a Single Pods') #
    total_heat_rate_pods = Float(17671942., units = 'W', iotype='out', desc='Heating Due to a All Pods') #
    #Radiated Out
    q_rad_per_area = Float(31.6, units = 'W/(m**2)', iotype='out', desc='Heat Radiated to the outside') #
    q_rad_tot = Float(106761066.5, units = 'W', iotype='out', desc='Heat Radiated to the outside') #
    #Radiated In
    viewing_angle = Float(1074256, units = 'm**2', iotype='out', desc='Effective Area hit by Sun') #
    #Total Heating
    q_total_out = Float(286900419., units = 'W', iotype='out', desc='Total Heat Released via Radiation and Natural Convection') #
    q_total_in = Float(286900419., units = 'W', iotype='out', desc='Total Heat Absorbed/Added via Pods and Solar Absorption') #
    #Residual (for solver)
    ss_temp_residual = Float(units = 'K', iotype='out', desc='Residual of T_released - T_absorbed')
  
    def execute(self):
        """Calculate Various Paramters"""
        
        bearing_q = cu(self.bearing_air.W,'lbm/s','kg/s') * cu(self.bearing_air.Cp,'Btu/(lbm*degR)','J/(kg*K)') * (cu(self.bearing_air.Tt,'degR','degK') - self.temp_boundary)
        nozzle_q = cu(self.nozzle_air.W,'lbm/s','kg/s') * cu(self.nozzle_air.Cp,'Btu/(lbm*degR)','J/(kg*K)') * (cu(self.nozzle_air.Tt,'degR','degK') - self.temp_boundary)
        #Q = mdot * cp * deltaT 
        self.heat_rate_pod = nozzle_q +bearing_q 
        #Total Q = Q * (number of pods)
        self.total_heat_rate_pods = self.heat_rate_pod*self.num_pods

        #Determine thermal resistance of outside via Natural Convection or forced convection
        if(self.temp_outside_ambient < 400):
            self.GrDelTL3 = 41780000000000000000*((self.temp_outside_ambient)**(-4.639)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        else:
            self.GrDelTL3 = 4985000000000000000*((self.temp_outside_ambient)**(-4.284)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        
        #Prandtl Number
        #Pr = viscous diffusion rate/ thermal diffusion rate = Cp * dyanamic viscosity / thermal conductivity
        #Pr << 1 means thermal diffusivity dominates
        #Pr >> 1 means momentum diffusivity dominates
        if (self.temp_outside_ambient < 400):
            self.Pr = 1.23*(self.temp_outside_ambient**(-0.09685)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        else:
            self.Pr = 0.59*(self.temp_outside_ambient**(0.0239))
        #Grashof Number
        #Relationship between buoyancy and viscosity
        #Laminar = Gr < 10^8
        #Turbulent = Gr > 10^9
        self.Gr = self.GrDelTL3*(self.temp_boundary-self.temp_outside_ambient)*(self.diameter_outer_tube**3)
        #Rayleigh Number 
        #Buoyancy driven flow (natural convection)
        self.Ra = self.Pr * self.Gr
        #Nusselt Number
        #Nu = convecive heat transfer / conductive heat transfer
        if (self.Ra<=10**12): #valid in specific flow regime
            self.Nu = (0.6 + 0.387*self.Ra**(1./6.)/(1 + (0.559/self.Pr)**(9./16.))**(8./27.))**2 #3rd Ed. of Introduction to Heat Transfer by Incropera and DeWitt, equations (9.33) and (9.34) on page 465
        if(self.temp_outside_ambient < 400):
            self.k = 0.0001423*(self.temp_outside_ambient**(0.9138)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        else:
            self.k = 0.0002494*(self.temp_outside_ambient**(0.8152))
        #h = k*Nu/Characteristic Length
        self.h = (self.k * self.Nu)/ self.diameter_outer_tube
        #Convection Area = Surface Area
        self.area_convection = pi * self.length_tube * self.diameter_outer_tube 
        #Determine heat radiated per square meter (Q)
        self.q_per_area_nat_conv = self.h*(self.temp_boundary-self.temp_outside_ambient)
        #Determine total heat radiated over entire tube (Qtotal)
        self.total_q_nat_conv = self.q_per_area_nat_conv * self.area_convection
        #Determine heat incoming via Sun radiation (Incidence Flux)
        #Sun hits an effective rectangular cross section
        self.area_viewing = self.length_tube* self.diameter_outer_tube
        self.q_per_area_solar = (1-self.surface_reflectance)* self.nn_incidence_factor * self.solar_insolation
        self.q_total_solar = self.q_per_area_solar * self.area_viewing
        #Determine heat released via radiation
        #Radiative area = surface area
        self.area_rad = self.area_convection
        #P/A = SB*emmisitivity*(T^4 - To^4)
        self.q_rad_per_area = self.sb_constant*self.emissivity_tube*((self.temp_boundary**4) - (self.temp_outside_ambient**4))
        #P = A * (P/A)
        self.q_rad_tot = self.area_rad * self.q_rad_per_area
        #------------
        #Sum Up
        self.q_total_out = self.q_rad_tot + self.total_q_nat_conv
        self.q_total_in = self.q_total_solar + self.total_heat_rate_pods
        
        self.ss_temp_residual = (self.q_total_out - self.q_total_in)/1e6

#run stand-alone component
if __name__ == "__main__":

    from openmdao.main.api import set_as_top


    class TubeHeatBalance(Assembly):

        def configure(self):

            tm = self.add('tm', TubeWallTemp())
            #tm.bearing_air.setTotalTP()
            driver = self.add('driver',BroydenSolver())
            driver.add_parameter('tm.temp_boundary',low=0.,high=10000.)
            driver.add_constraint('tm.ss_temp_residual=0')

            driver.workflow.add(['tm'])

    test = TubeHeatBalance()
    set_as_top(test)

    #set input values
    test.tm.nozzle_air.setTotalTP(1710, 0.304434211)
    test.tm.nozzle_air.W = 1.08
    test.tm.bearing_air.W = 0.
    test.tm.diameter_outer_tube = 2.22504#, units = 'm', iotype='in', desc='Tube out diameter') #7.3ft
    test.tm.length_tube = 482803.#, units = 'm', iotype='in', desc='Length of entire Hyperloop') #300 miles, 1584000ft
    test.tm.num_pods = 34.#, units = 'K', iotype='in', desc='Number of Pods in the Tube at a given time') #
    test.tm.temp_boundary = 340#, units = 'K', iotype='in', desc='Average Temperature of the tube') #
    test.tm.temp_outside_ambient = 305.6#, units = 'K', iotype='in', desc='Average Temperature of the outside air') #

    test.run()

    print "-----Completed Tube Heat Flux Model Calculations---"
    print ""
    print "CompressQ-{} SolarQ-{} RadQ-{} ConvecQ-{}".format(test.tm.total_heat_rate_pods, test.tm.q_total_solar, test.tm.q_rad_tot, test.tm.total_q_nat_conv )
    print "Equilibrium Wall Temperature: {} K or {} F".format(test.tm.temp_boundary, cu(test.tm.temp_boundary,'degK','degF'))
    print "Ambient Temperature:          {} K or {} F".format(test.tm.temp_outside_ambient, cu(test.tm.temp_outside_ambient,'degK','degF'))
    print "Q Out = {} W  ==>  Q In = {} W ==> Error: {}%".format(test.tm.q_total_out,test.tm.q_total_in,((test.tm.q_total_out-test.tm.q_total_in)/test.tm.q_total_out)*100)