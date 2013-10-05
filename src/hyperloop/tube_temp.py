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
    tubeOD = Float(units = 'm', iotype='in', desc='Tube out diameter') #7.3ft
    tubeLength = Float(units = 'm', iotype='in', desc='Length of entire Hyperloop') #300 miles, 1584000ft
    #podMdot = Float(units = 'kg/s', iotype='in', desc='Amount of air released by each pod') #
    podFreq = Float(units = 'K', iotype='in', desc='Number of Pods in the Tube at a given time') #
    #podMN = Float(units = 'K', iotype='in', desc='Pod Mach Number') #
    tubeWallTemp = Float(units = 'K', iotype='in', desc='Average Temperature of the tube') #
    #tubeAmbientPressure = Float(units = 'Pa', iotype='in', desc='Average Temperature of the tube') #
    ambientTemp = Float(units = 'K', iotype='in', desc='Average Temperature of the outside air') #
    #compInletTt = Float(units = 'K', iotype='in', desc='Compressor Inlet Total Temperature') #
    #compInletPt = Float(units = 'Pa', iotype='in', desc='Compressor Inlet Total Pressure') #
    #PR = Float(iotype='in', desc='Compressor Pressure Ratio') #
    #adiabaticEff = Float(iotype='in', desc='Adiabatic Efficiency of the Compressor') #
    #compExitTt = Float(927., units = 'K', iotype='in', desc='Compressor Exit Total Temperature') 
    podCp = Float(1144., units = 'J/(kg*K)', iotype='in', desc='specific heat of hot pod air')

    nozzle_air = FlowStation(iotype="in", desc="air exiting the pod nozzle", copy=None)
    bearing_air = FlowStation(iotype="in", desc="air exiting the air bearings", copy=None)


    #constants
    #Solar_constant = Float(1366., units = 'K', desc='Flux Density of incoming solar radiation') #
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
    
    #compExitPt = Float(2099., units = 'Pa', iotype='out', desc='Compressor Exit Total Pressure') #
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
        
        #Determine heat added by pods coming through
        #Tt = Ts * (1 + [(gam-1)/2]*(MN^2)
        #self.compInletTt = self.tubeWallTemp*(1+((self.gammaAir-1)/2)*(self.podMN**2))
        #Pt = Ps * (Tt/Ts)^(gam/gam-1)
        #self.compInletPt = self.tubeAmbientPressure*(1+((self.gammaAir-1)/2)*(self.podMN**2))**(self.gammaAir/(self.gammaAir-1))
        #Pt_exit = Pt_inlet * PR
        #self.compExitPt = self.compInletPt * self.PR
        #Tt_exit = Tt_inlet + ([Tt_inlet * PR^(gam-1/gam)]-Tt_inlet)/adiabatic_efficiency
        #self.compExitTt = self.compInletTt + (self.compInletTt*(self.PR)**((self.gammaAir-1)/self.gammaAir)-self.compInletTt)/self.adiabaticEff
        
        #if (self.compExitTt < 400):
        #    self.podCp = 990.8*(self.compExitTt**(0.00316)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        #else:
        #    self.podCp = 299.4*(self.compExitTt**(0.1962)) #SI units
        bearing_q = cu(bearing_air.W,'lbm/s','W/(m**2)') * cu(bearing_air.Cp,'Btu/(lbm*degR)','J/(kg*K)') * (cu(bearing_air.Tt,'degR','degK') - self.tubeWallTemp)
        nozzle_q = cu(nozzle_air.W,'lbm/s','W/(m**2)') * cu(nozzle_air.Cp,'Btu/(lbm*degR)','J/(kg*K)') * (cu(nozzle_air.Tt,'degR','degK') - self.tubeWallTemp)
        #Q = mdot * cp * deltaT 
        self.podQ = nozzle_q #+bearing_q 
        #Total Q = Q * (number of pods)
        self.podQTot = self.podQ*self.podFreq

        #Determine the thermal resistance of the tube via convection
        #calculate h based on Re, Pr, Nu
        #Determine thermal resistance of the tube (conduction)
        #
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
        else:
            print "Flow Regime Not Valid"
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
        
        self.ssTemp_residual = self.Qout - self.Qin
#run stand-alone component
if __name__ == "__main__":

    #crude value comparison for testing
    def check(var_name,var,correct_val):
        #check('<variable_name>',<variable>,<correct value>)
        "Format and print the results of a value comparison, (crude tests for verification purposes)"
        error = (correct_val - var)/correct_val
        if (abs(error*100)<3): #determine percent error, if greater than 1%
            print "{}: {} ........{}%  --> {}!".format(var_name,var,abs(error)*100,"Test Passed")
        else: #comparison fails, print error output
            print " ===> {}: {} ........{}%  --> {} ?".format(var_name,var,abs(error)*100,"Test Failed :(")


    from openmdao.main.api import set_as_top

    class TubeHeatBalance(Assembly):

        def configure(self):

            tm = self.add('tm', TubeTemp())
            #tm.bearing_air.setTotalTP()
            driver = self.add('driver',BroydenSolver())
            driver.add_parameter('tm.tubeWallTemp',low=0.,high=10000.)
            driver.add_constraint('tm.ssTemp_residual=0')

            

            driver.workflow.add(['tm'])

    test = TubeHeatBalance()
    set_as_top(test)

    #set input values
    test.tm.nozzle_air.setTotalTP(1710, 0.304434211)
    test.tm.nozzle_air.W = 1.08
    test.tm.tubeOD = 2.22504#, units = 'm', iotype='in', desc='Tube out diameter') #7.3ft
    test.tm.tubeLength = 482803.#, units = 'm', iotype='in', desc='Length of entire Hyperloop') #300 miles, 1584000ft
    #test.tm.podMdot = 0.49#, units = 'kg/s', iotype='in', desc='Amount of air released by each pod') #
    test.tm.podFreq = 34.#, units = 'K', iotype='in', desc='Number of Pods in the Tube at a given time') #
    #test.tm.podMN = 0.91#, units = 'K', iotype='in', desc='Pod Mach Number') #
    test.tm.tubeWallTemp = 322.361#, units = 'K', iotype='in', desc='Average Temperature of the tube') #
    #test.tm.tubeAmbientPressure = 99.#, units = 'Pa', iotype='in', desc='Average Temperature of the tube') #
    test.tm.ambientTemp = 305.6#, units = 'K', iotype='in', desc='Average Temperature of the outside air') #
    #test.tm.compInletTt = 367.#, units = 'K', iotype='in', desc='Compressor Inlet Total Temperature') #
    #test.tm.compInletPt = 169.#, units = 'Pa', iotype='in', desc='Compressor Inlet Total Pressure') #
    #test.tm.PR = 12.4#, iotype='in', desc='Compressor Pressure Ratio') #
    #test.tm.adiabaticEff = 0.69#, iotype='in', desc='Adiabatic Efficiency of the Compressor') #

    print ""
    test.run()

    #perform crude value comparison (calculation verification)
    check('compInletTt',test.tm.compInletTt,375.96)
    check('podCp',test.tm.podCp,1144.)
    check('compInletPt',test.tm.compInletPt,169.)
    check('compExitPt',test.tm.compExitPt,2099.)
    check('compExitTt',test.tm.compExitTt,950.)
    check('podQ',test.tm.podQ,353244.)
    check('podQTot',test.tm.podQTot,12010290.)
    check('GrDelTL3',test.tm.GrDelTL3,123775609)
    check('Pr',test.tm.Pr,0.707)
    check('Gr',test.tm.Gr,23163846280.)
    check('Ra',test.tm.Ra,16369476896.)
    check('Nu',test.tm.Nu,281.6714) #http://www.egr.msu.edu/~somerton/Nusselt/ii/ii_a/ii_a_3/ii_a_3_a.html
    check('k',test.tm.k,0.02655)
    check('h',test.tm.h,3.3611)
    check('convArea',test.tm.convArea,3374876)
    check('naturalConvection',test.tm.naturalConvection,57.10)
    check('naturalConvectionTot',test.tm.naturalConvectionTot,192710349)
    check('ViewingArea',test.tm.ViewingArea,1074256.)
    check('solarHeat',test.tm.solarHeat,350.)
    check('solarHeatTotal',test.tm.solarHeatTotal,375989751.)
    check('radArea',test.tm.radArea,3374876.115)
    check('qRad',test.tm.qRad,59.7)
    check('qRadTot',test.tm.qRadTot,201533208)
    check('Qout',test.tm.Qout,394673364.)

    print "-----Completed Tube Heat Flux Model Calculations---"
    print ""
    print "Equilibrium Wall Temperature: {} K or {} F".format(test.tubeWallTemp, cu(test.tubeWallTemp,'degK','degF'))
    print "Ambient Temperature:          {} K or {} F".format(test.ambientTemp, cu(test.ambientTemp,'degK','degF'))
    print "Q Out = {} W  ==>  Q In = {} W ==> Error: {}%".format(test.Qout,test.Qin,((test.Qout-test.Qin)/test.Qout)*100)