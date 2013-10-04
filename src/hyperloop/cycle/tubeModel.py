"""
    tubeModel.py - 
        Calculates Q released/absorbed by hyperloop tube due to:
        Internal Convection, Tube Conduction, Ambient Natural Convection, Solar Flux In, Radiation Out
        
    -original calculations from Jeff Berton, ported and extended by Jeff Chin

    Compatible with OpenMDAO v0.8.1
"""


from openmdao.main.api import Component, convert_units
from openmdao.lib.datatypes.api import Float, Bool
from openmdao.main.api import convert_units as cu

from math import log, pi, sqrt, e


def check(var_name,var,correct_val):
    #check('<variable_name>',<variable>,<correct value>)
    "Format and print the results of a value comparison, (crude tests for verification purposes)"
    error = (correct_val - var)/correct_val
    if (abs(error*100)<3): #determine percent error, if greater than 1%
        print "{}: {} ........{}%  --> {}!".format(var_name,var,abs(error)*100,"Test Passed")
    else: #comparison fails, print error output
        print " ===> {}: {} ........{}%  --> {} ?".format(var_name,var,abs(error)*100,"Test Failed :(")


class tubeModel(Component):
    """ Main Component """

    #--Inputs--
    #Hyperloop Parameters/Design Variables
    #airTube = Float(0., units = 'kg', iotype='in', desc='Total air in tube') #
    #airRho = Float(0., units = 'kg/m**3', iotype='in', desc='density of air in the tube')
    #tubeID = Float(2.23, units = 'm', iotype='in', desc='Tube inner diameter') #
    tubeOD = Float(2.22504, units = 'm', iotype='in', desc='Tube out diameter') #7.3ft
    tubeLength = Float(482803., units = 'm', iotype='in', desc='Length of entire Hyperloop') #300 miles, 1584000ft
    #tubeK = Float(0., units = 'W/(m*K)', iotype='in', desc='thermal conductivity of the tube (conduction)')
    #podTemp = Float(406.6, units = 'K', iotype='in', desc='Temperature Released by each pod') #
    podMdot = Float(0.49, units = 'kg/s', iotype='in', desc='Amount of air released by each pod') #
    podFreq = Float(34., units = 'K', iotype='in', desc='Number of Pods in the Tube at a given time') #
    podMN = Float(0.91, units = 'K', iotype='in', desc='Pod Mach Number') #
    tubeWallTemp = Float(322.361, units = 'K', iotype='in', desc='Average Temperature of the tube') #
    tubeAmbientPressure = Float(99., units = 'Pa', iotype='in', desc='Average Temperature of the tube') #
    ambientTemp = Float(305.6, units = 'K', iotype='in', desc='Average Temperature of the outside air') #
    compInletTt = Float(367., units = 'K', iotype='in', desc='Compressor Inlet Total Temperature') #
    compInletPt = Float(169., units = 'Pa', iotype='in', desc='Compressor Inlet Total Pressure') #
    PR = Float(12.4, iotype='in', desc='Compressor Pressure Ratio') #
    adiabaticEff = Float(0.69, iotype='in', desc='Adiabatic Efficiency of the Compressor') #

    #constants
    Solar_constant = Float(1366., units = 'K', desc='Average Temperature of the outside air') #
    Solar_insolation = Float(1000., units = 'K', desc='Average Temperature of the outside air') #
    nnIncidenceF = Float(0.7, desc='Non-normal incidence factor') #
    Surface_reflectance = Float(0.5, desc='Solar Reflectance Index') #
    solarHeat = Float(350., units = 'W/m**2', desc='Solar Heat Absorbed per Area') #
    solarHeatTotal = Float(375989751., units = 'W', desc='Solar Heat Absorbed by Tube') #
    tubeEmissivity = Float(0.5, units = 'W', desc='Emmissivity of the Tube') #
    SBconst = Float(0.00000005670373, units = 'W/((m**2)*(K**4))', desc='Stefan-Boltzmann Constant') #
    gammaAir = Float(1.4, desc='Heat Capacity of Air') #
    
    #Intermediate Values
    podCp = Float(1144., units = 'J/(kg*K)', iotype='out', desc='specific heat of hot pod air')
    #tubeCp = Float(1.1221, units = 'J/(kg*K)', iotype='in', desc='specific heat of tube air')
    radArea = Float(337486.1, units = 'm**2', iotype='out', desc='Tube Radiating Area') #
    compExitTt = Float(927., units = 'K', iotype='out', desc='Compressor Exit Total Temperature') #
    compExitPt = Float(2099., units = 'Pa', iotype='out', desc='Compressor Exit Total Pressure') #
    #Required for Natural Convection Calcs
    GrDelTL3 = Float(1946216.7, units = '1/((ft**3)*F)', iotype='out', desc='Heat Radiated to the outside') #
    Pr = Float(0.707, iotype='out', desc='Heat Radiated to the outside') #
    Gr = Float(12730351223., iotype='out', desc='Heat Radiated to the outside') #
    Ra = Float(8996312085., iotype='out', desc='Heat Radiated to the outside') #
    Nu = Float(232.4543713, iotype='out', desc='Heat Radiated to the outside') #
    k = Float(0.02655, units = 'W/(m*K)', iotype='out', desc='Heat Radiated to the outside') #
    h = Float(0.845464094, units = 'W/((m**2)*K)', iotype='out', desc='Heat Radiated to the outside') #
    convectionArea = Float(3374876.115, units = 'W', iotype='out', desc='Heat Radiated to the outside') #
    #tubeTemp = Float(406.6, units = 'K', iotype='in', desc='Average Temperature of the tube') #
    #surfA_pipe = Float(1.0, units = 'm**2', iotype='out', desc='Surface Area of the Pipe')
    #Dh = Float(1.0, units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for fluid flow')
    #De = Float(1.0, units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for heat flow')

    #Calculated Variables
    #Veloc_a = Float(1.0, units= 'm/s', iotype='out', desc='flow velocity of air')
    #h_a = Float(1.0, units = 'W/m', iotype='out', desc='heat transfer of air (convection)')
    #q_a = Float(1.0, units = 'W', iotype='out', desc='heat flow of air')
    #U_o = Float(1.0, units = 'W/(m**2)*K', iotype='out', desc='Overall Heat Transfer Coefficient')
    
    #--Outputs--
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
  
    def execute(self):
        """Calculate Various Paramters"""
        
        #Determine heat added by pods coming through
        #Tt = Ts * (1 + [(gam-1)/2]*(MN^2)
        self.compInletTt = self.tubeWallTemp*(1+((self.gammaAir-1)/2)*(self.podMN**2))
        check('compInletTt',self.compInletTt,375.96)
        #Pt = Ps * (Tt/Ts)^(gam/gam-1)
        self.compInletPt = self.tubeAmbientPressure*(1+((self.gammaAir-1)/2)*(self.podMN**2))**(self.gammaAir/(self.gammaAir-1))
        check('compInletPt',self.compInletPt,169.)
        #Pt_exit = Pt_inlet * PR
        self.compExitPt = self.compInletPt * self.PR
        check('compExitPt',self.compExitPt,2099.)
        #Tt_exit = Tt_inlet + ([Tt_inlet * PR^(gam-1/gam)]-Tt_inlet)/adiabatic_efficiency
        self.compExitTt = self.compInletTt + (self.compInletTt*(self.PR)**((self.gammaAir-1)/self.gammaAir)-self.compInletTt)/self.adiabaticEff
        check('compExitTt',self.compExitTt,950.)
        
        if (self.compExitTt < 400):
            self.podCp = 990.8*(self.compExitTt**(0.00316)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        else:
            self.podCp = 299.4*(self.compExitTt**(0.1962)) #SI units
        check('podCp',self.podCp,1144.)
        #Q = mdot * cp * deltaT 
        self.podQ = self.podMdot * self.podCp * (self.compExitTt-self.tubeWallTemp)
        check('podQ',self.podQ,353244.)
        #Total Q = Q * (number of pods)
        self.podQTot = self.podQ*self.podFreq
        check('podQTot',self.podQTot,12010290.)

        #Determine the thermal resistance of the tube via convection
        #calculate h based on Re, Pr, Nu

        
        #Determine thermal resistance of the tube (conduction)
        #
        
        #Determine thermal resistance of outside via Natural Convection or forced convection
        if(self.ambientTemp < 400):
            self.GrDelTL3 = 41780000000000000000*((self.ambientTemp)**(-4.639)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        else:
            self.GrDelTL3 = 4985000000000000000*((self.ambientTemp)**(-4.284)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        check('GrDelTL3',self.GrDelTL3,123775609)
        #Prandtl Number
        #Pr = viscous diffusion rate/ thermal diffusion rate = Cp * dyanamic viscosity / thermal conductivity
        #Pr << 1 means thermal diffusivity dominates
        #Pr >> 1 means momentum diffusivity dominates
        if (self.ambientTemp < 400):
            self.Pr = 1.23*(self.ambientTemp**(-0.09685)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        else:
            self.Pr = 0.59*(self.ambientTemp**(0.0239))
        check('Pr',self.Pr,0.707)
        #Grashof Number
        #Relationship between buoyancy and viscosity
        #Laminar = Gr < 10^8
        #Turbulent = Gr > 10^9
        self.Gr = self.GrDelTL3*(self.tubeWallTemp-self.ambientTemp)*(self.tubeOD**3)
        check('Gr',self.Gr,23163846280.)
        #Rayleigh Number 
        #Buoyancy driven flow (natural convection)
        self.Ra = self.Pr * self.Gr
        check('Ra',self.Ra,16369476896.)
        #Nusselt Number
        #Nu = convecive heat transfer / conductive heat transfer
        if (self.Ra<=10**12): #valid in specific flow regime
            self.Nu = (0.6 + 0.387*self.Ra**(1./6.)/(1 + (0.559/self.Pr)**(9./16.))**(8./27.))**2 #3rd Ed. of Introduction to Heat Transfer by Incropera and DeWitt, equations (9.33) and (9.34) on page 465
            check('Nu',self.Nu,281.6714) #http://www.egr.msu.edu/~somerton/Nusselt/ii/ii_a/ii_a_3/ii_a_3_a.html
        else:
            print "Flow Regime Not Valid"
        
        if(self.ambientTemp < 400):
            self.k = 0.0001423*(self.ambientTemp**(0.9138)) #SI units (https://mdao.grc.nasa.gov/publications/Berton-Thesis.pdf pg51)
        else:
            self.k = 0.0002494*(self.ambientTemp**(0.8152))
        check('k',self.k,0.02655)
        
        #h = k*Nu/Characteristic Length
        self.h = (self.k * self.Nu)/ self.tubeOD
        check('h',self.h,3.3611)
        #Convection Area = Surface Area
        self.convArea = pi * self.tubeLength * self.tubeOD 
        check('convArea',self.convArea,3374876)
        #Determine heat radiated per square meter (Q)
        self.naturalConvection = self.h*(self.tubeWallTemp-self.ambientTemp)
        check('naturalConvection',self.naturalConvection,57.10)
        #Determine total heat radiated over entire tube (Qtotal)
        self.naturalConvectionTot = self.naturalConvection * self.convArea
        check('naturalConvectionTot',self.naturalConvectionTot,192710349)
        
        #Determine heat incoming via Sun radiation (Incidence Flux)
        #Sun hits an effective rectangular cross section
        self.ViewingArea = self.tubeLength* self.tubeOD
        check('ViewingArea',self.ViewingArea,1074256.)
        
        self.solarHeat = (1-self.Surface_reflectance)* self.nnIncidenceF * self.Solar_insolation
        check('solarHeat',self.solarHeat,350.)
        
        self.solarHeatTotal = self.solarHeat * self.ViewingArea
        check('solarHeatTotal',self.solarHeatTotal,375989751.)
        
        #Determine heat released via radiation
        #Radiative area = surface area
        self.radArea = self.convArea
        check('radArea',self.radArea,3374876.115)
        #P/A = SB*emmisitivity*(T^4 - To^4)
        self.qRad = self.SBconst*self.tubeEmissivity*((self.tubeWallTemp**4) - (self.ambientTemp**4))
        check('qRad',self.qRad,59.7)
        #P = A * (P/A)
        self.qRadTot = self.radArea * self.qRad
        check('qRadTot',self.qRadTot,201533208)
        
        #------------
        #Sum Up
        self.Qout = self.qRadTot + self.naturalConvectionTot
        self.Qin = self.solarHeatTotal + self.podQTot
        check('Qout',self.Qout,394673364.)
       
#run stand-alone component
if __name__ == "__main__":

    from openmdao.main.api import set_as_top
    test = tubeModel()  
    set_as_top(test)
    print ""
    test.run()
    print "-----Completed Tube Heat Flux Model Calculations---"
    print ""
    print "Equilibrium Wall Temperature: {} K or {} F".format(test.tubeWallTemp, convert_units(test.tubeWallTemp,'degK','degF'))
    print "Ambient Temperature:          {} K or {} F".format(test.ambientTemp, convert_units(test.ambientTemp,'degK','degF'))
    print "Q Out = {} W  ==>  Q In = {} W ==> Error: {}%".format(test.Qout,test.Qin,((test.Qout-test.Qin)/test.Qout)*100)
    
