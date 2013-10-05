"""
    tubeModel.py - 
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

from pycycle.api import FlowStation


class TubeTemp(Component):
    """ Main Component """

    #--Inputs--
    #Hyperloop Parameters/Design Variables
    tubeOD = Float(2.23, units = 'm', iotype='in', desc='Tube out diameter') #7.3ft
    tubeLength = Float(482803, units = 'm', iotype='in', desc='Length of entire Hyperloop') #300 miles, 1584000ft
    podFreq = Float(34, units = 'K', iotype='in', desc='Number of Pods in the Tube at a given time') #
    tubeWallTemp = Float(322.0, units = 'K', iotype='in', desc='Average Temperature of the tube') #
    ambientTemp = Float(305.6, units = 'K', iotype='in', desc='Average Temperature of the outside air') #
    podCp = Float(1144., units = 'J/(kg*K)', iotype='in', desc='specific heat of hot pod air')

    nozzle_air = FlowStation(iotype="in", desc="air exiting the pod nozzle", copy=None)
    bearing_air = FlowStation(iotype="in", desc="air exiting the air bearings", copy=None)


    #constants
    Solar_insolation = Float(1000., units = 'W/m**2', desc='solar irradiation at sea level on a clear day') #
    nnIncidenceF = Float(0.7, desc='Non-normal incidence factor') #
    Surface_reflectance = Float(0.5, desc='Solar Reflectance Index') #
    solarHeat = Float(350., units = 'W/m**2', desc='Solar Heat Absorbed per Area') #
    solarHeatTotal = Float(375989751., units = 'W', desc='Solar Heat Absorbed by Tube') #
    tubeEmissivity = Float(0.5, units = 'W', desc='Emmissivity of the Tube') #
    SBconst = Float(0.00000005670373, units = 'W/((m**2)*(K**4))', desc='Stefan-Boltzmann Constant') #
    gammaAir = Float(1.4, desc='Heat Capacity of Air') #
    

    #--Outputs--
    #Intermediate Values
    radArea = Float(337486.1, units = 'm**2', iotype='out', desc='Tube Radiating Area') #
    
    #Required for Natural Convection Calcs
    GrDelTL3 = Float(1946216.7, units = '1/((ft**3)*F)', iotype='out', desc='Heat Radiated to the outside') #
    Pr = Float(0.707, iotype='out', desc='Heat Radiated to the outside') #
    Gr = Float(12730351223., iotype='out', desc='Heat Radiated to the outside') #
    Ra = Float(8996312085., iotype='out', desc='Heat Radiated to the outside') #
    Nu = Float(232.4543713, iotype='out', desc='Heat Radiated to the outside') #
    k = Float(0.02655, units = 'W/(m*K)', iotype='out', desc='Heat Radiated to the outside') #
    h = Float(0.845464094, units = 'W/((m**2)*K)', iotype='out', desc='Heat Radiated to the outside') #
    convectionArea = Float(3374876.115, units = 'W', iotype='out', desc='Heat Radiated to the outside') #

    #Exhausted from Pods
    podQ = Float(519763, units = 'W', iotype='out', desc='Heating Due to a Single Pods') #
    podQTot = Float(17671942., units = 'W', iotype='out', desc='Heating Due to a All Pods') #
    #Radiated Out
    qRad = Float(31.6, units = 'W/(m**2)', iotype='out', desc='Heat Radiated to the outside') #
    qRadTot = Float(106761066.5, units = 'W', iotype='out', desc='Heat Radiated to the outside') #
    Qout = Float(286900419., units = 'W', iotype='out', desc='Total Heat Released via Radiation and Natural Convection') #
    #Radiated In
    viewingAngle = Float(1074256, units = 'm**2', iotype='out', desc='Effective Area hit by Sun') #
    Qin = Float(286900419., units = 'W', iotype='out', desc='Total Heat Absorbed/Added via Pods and Solar Absorption') #
    #Natural Convection
    naturalConvection = Float(7.9, units = 'W/(m**2)', iotype='out', desc='Heat Radiated to the outside') #
    naturalConvectionTot = Float(286900419., units = 'W', iotype='out', desc='Heat Radiated to the outside') #

    ssTemp_residual = Float(units = 'K', iotype='out', desc='Residual of T_released - T_absorbed')
  
    def execute(self):
        """Calculate Various Paramters"""
        
        bearing_q = cu(self.bearing_air.W,'lbm/s','kg/s') * cu(self.bearing_air.Cp,'Btu/(lbm*degR)','J/(kg*K)') * (cu(self.bearing_air.Tt,'degR','degK') - self.tubeWallTemp)
        nozzle_q = cu(self.nozzle_air.W,'lbm/s','kg/s') * cu(self.nozzle_air.Cp,'Btu/(lbm*degR)','J/(kg*K)') * (cu(self.nozzle_air.Tt,'degR','degK') - self.tubeWallTemp)
        #Q = mdot * cp * deltaT 
        self.podQ = nozzle_q +bearing_q 
        #Total Q = Q * (number of pods)
        self.podQTot = self.podQ*self.podFreq

        #Determine thermal resistance of outside via Natural Convection or forced convection
        if(self.ambientTemp < 400):
            self.GrDelTL3 = 41780000000000000000*((self.ambientTemp)**(-4.639)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        else:
            self.GrDelTL3 = 4985000000000000000*((self.ambientTemp)**(-4.284)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        
        #Prandtl Number
        #Pr = viscous diffusion rate/ thermal diffusion rate = Cp * dyanamic viscosity / thermal conductivity
        #Pr << 1 means thermal diffusivity dominates
        #Pr >> 1 means momentum diffusivity dominates
        if (self.ambientTemp < 400):
            self.Pr = 1.23*(self.ambientTemp**(-0.09685)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        else:
            self.Pr = 0.59*(self.ambientTemp**(0.0239))
        #Grashof Number
        #Relationship between buoyancy and viscosity
        #Laminar = Gr < 10^8
        #Turbulent = Gr > 10^9
        self.Gr = self.GrDelTL3*(self.tubeWallTemp-self.ambientTemp)*(self.tubeOD**3)
        #Rayleigh Number 
        #Buoyancy driven flow (natural convection)
        self.Ra = self.Pr * self.Gr
        #Nusselt Number
        #Nu = convecive heat transfer / conductive heat transfer
        if (self.Ra<=10**12): #valid in specific flow regime
            self.Nu = (0.6 + 0.387*self.Ra**(1./6.)/(1 + (0.559/self.Pr)**(9./16.))**(8./27.))**2 #3rd Ed. of Introduction to Heat Transfer by Incropera and DeWitt, equations (9.33) and (9.34) on page 465
        if(self.ambientTemp < 400):
            self.k = 0.0001423*(self.ambientTemp**(0.9138)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        else:
            self.k = 0.0002494*(self.ambientTemp**(0.8152))
        #h = k*Nu/Characteristic Length
        self.h = (self.k * self.Nu)/ self.tubeOD
        #Convection Area = Surface Area
        self.convArea = pi * self.tubeLength * self.tubeOD 
        #Determine heat radiated per square meter (Q)
        self.naturalConvection = self.h*(self.tubeWallTemp-self.ambientTemp)
        #Determine total heat radiated over entire tube (Qtotal)
        self.naturalConvectionTot = self.naturalConvection * self.convArea
        #Determine heat incoming via Sun radiation (Incidence Flux)
        #Sun hits an effective rectangular cross section
        self.ViewingArea = self.tubeLength* self.tubeOD
        self.solarHeat = (1-self.Surface_reflectance)* self.nnIncidenceF * self.Solar_insolation
        self.solarHeatTotal = self.solarHeat * self.ViewingArea
        #Determine heat released via radiation
        #Radiative area = surface area
        self.radArea = self.convArea
        #P/A = SB*emmisitivity*(T^4 - To^4)
        self.qRad = self.SBconst*self.tubeEmissivity*((self.tubeWallTemp**4) - (self.ambientTemp**4))
        #P = A * (P/A)
        self.qRadTot = self.radArea * self.qRad
        #------------
        #Sum Up
        self.Qout = self.qRadTot + self.naturalConvectionTot
        self.Qin = self.solarHeatTotal + self.podQTot
        
        self.ssTemp_residual = (self.Qout - self.Qin)/1e6

#run stand-alone component
if __name__ == "__main__":

    from openmdao.main.api import set_as_top
    from openmdao.lib.drivers.newton_krylov import NewtonKyrlovSolver


    class TubeHeatBalance(Assembly):

        def configure(self):

            tm = self.add('tm', TubeTemp())
            #tm.bearing_air.setTotalTP()
            driver = self.add('driver',NewtonKyrlovSolver())
            driver.add_parameter('tm.tubeWallTemp',low=0.,high=10000.)
            driver.add_constraint('tm.ssTemp_residual=0')

            

            driver.workflow.add(['tm'])

    test = TubeHeatBalance()
    set_as_top(test)

    #set input values
    test.tm.nozzle_air.setTotalTP(1710, 0.304434211)
    test.tm.nozzle_air.W = 1.08
    test.tm.bearing_air.W = 0.
    test.tm.tubeOD = 2.22504#, units = 'm', iotype='in', desc='Tube out diameter') #7.3ft
    test.tm.tubeLength = 482803.#, units = 'm', iotype='in', desc='Length of entire Hyperloop') #300 miles, 1584000ft
    test.tm.podFreq = 34.#, units = 'K', iotype='in', desc='Number of Pods in the Tube at a given time') #
    test.tm.tubeWallTemp = 320#, units = 'K', iotype='in', desc='Average Temperature of the tube') #
    test.tm.ambientTemp = 305.6#, units = 'K', iotype='in', desc='Average Temperature of the outside air') #

    test.run()


    print "-----Completed Tube Heat Flux Model Calculations---"
    print ""
    print "Equilibrium Wall Temperature: {} K or {} F".format(test.tm.tubeWallTemp, cu(test.tm.tubeWallTemp,'degK','degF'))
    print "Ambient Temperature:          {} K or {} F".format(test.tm.ambientTemp, cu(test.tm.ambientTemp,'degK','degF'))
    print "Q Out = {} W  ==>  Q In = {} W ==> Error: {}%".format(test.tm.Qout,test.tm.Qin,((test.tm.Qout-test.tm.Qin)/test.tm.Qout)*100)