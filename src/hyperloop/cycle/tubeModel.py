"""
    tubeModel.py - 
        Calculates Q released/absorbed by hyperloop tube due to:
        Internal Convection, Tube Conduction, Ambient Natural Convection, Solar Flux In, Radiation Out
        
    -written by Jeff Berton ported and extended by Jeff Chin

    Compatible with OpenMDAO v0.8.1
"""


from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, Bool
from openmdao.main.api import convert_units as cu

from math import log, pi, sqrt, e


class tubeModel(Component):
    """ Main Component """

    #--Inputs--
    #Hyperloop Parameters
    #airTube = Float(0., units = 'kg', iotype='in', desc='Total air in tube') #
    #airRho = Float(0., units = 'kg/m**3', iotype='in', desc='density of air in the tube')
    #tubeID = Float(2.23, units = 'm', iotype='in', desc='Tube inner diameter') #
    tubeOD = Float(2.22504, units = 'm', iotype='in', desc='Tube out diameter') #7.3ft
    tubeLength = Float(482803., units = 'm', iotype='in', desc='Length of entire Hyperloop') #300 miles
    #tubeK = Float(0., units = 'W/(m*K)', iotype='in', desc='thermal conductivity of the tube (conduction)')
    
    #Design Variables
    #podTemp = Float(406.6, units = 'K', iotype='in', desc='Temperature Released by each pod') #
    podMdot = Float(0.49, units = 'kg/s', iotype='in', desc='Amount of air released by each pod') #
    podFreq = Float(34., units = 'K', iotype='in', desc='Number of Pods in the Tube at a given time') #
    podMn = Float(0.91, units = 'K', iotype='in', desc='Pod Mach Number') #
    
    tubeWallTemp = Float(315, units = 'K', iotype='in', desc='Average Temperature of the tube') #
    ambientTemp = Float(305.6, units = 'K', iotype='in', desc='Average Temperature of the outside air') #
    
    compInletTt = Float(367., units = 'K', iotype='in', desc='Compressor Inlet Total Temperature') #
    compInletPt = Float(169., units = 'Pa', iotype='in', desc='Compressor Inlet Total Pressure') #
    
    PR = Float(12.4, iotype='in', desc='Compressor Pressure Ratio') #
    adiabaticEff = Float(0.69, iotype='in', desc='Adiabatic Efficiency of the Compressor') #
    
    #constants
    Solar_constant = Float(1366., units = 'K', iotype='in', desc='Average Temperature of the outside air') #
    Solar_insolation = Float(1000., units = 'K', iotype='in', desc='Average Temperature of the outside air') #
    nnIncidenceF = Float(0.7, iotype='in', desc='Non-normal incidence factor') #
    Surface_reflectance = Float(0.5, iotype='in', desc='Average Temperature of the outside air') #
    solarHeat = Float(350., units = 'W/m**2', iotype='in', desc='Solar Heat Absorbed per Area') #
    solarHeatTotal = Float(0., units = 'W', iotype='in', desc='Solar Heat Absorbed by Tube') #
    tubeEmissivity = Float(0.5, units = 'W', iotype='in', desc='Emmissivity of the Tube') #
    SBconst = Float(0.00000005670373, units = 'W/((m**2)*(K**4))', iotype='in', desc='Stefan-Boltzmann Constant') #
    
    
    #--Outputs--
    
    podCp = Float(1144., units = 'J/(kg*K)', iotype='out', desc='specific heat of hot pod air')
    radArea = Float(337486.1, units = 'm**2', iotype='out', desc='Tube Radiating Area') #
    
    qRad = Float(31.6, units = 'W/(m**2)', iotype='out', desc='Heat Radiated to the outside') #
    qRadTot = Float(106761066.5, units = 'W', iotype='out', desc='Heat Radiated to the outside') #
    
     #tubeCp = Float(1.1221, units = 'J/(kg*K)', iotype='in', desc='specific heat of tube air')
    podQ = Float(519763, units = 'W', iotype='out', desc='Heating Due to a Single Pods') #
    podQTot = Float(17671942., units = 'W', iotype='out', desc='Heating Due to a All Pods') #
    
    
    
    compExitTt = Float(927., units = 'K', iotype='out', desc='Compressor Exit Total Temperature') #
    compExitPt = Float(2099., units = 'Pa', iotype='out', desc='Compressor Exit Total Pressure') #
    
    
    GrDelTL3 = Float(1946216.7., units = '1/((ft**3)*F)', iotype='out', desc='Heat Radiated to the outside') #
    Pr = Float(0.707, iotype='out', desc='Heat Radiated to the outside') #
    Gr = Float(12730351223., iotype='out', desc='Heat Radiated to the outside') #
    Ra = Float(8996312085., iotype='out', desc='Heat Radiated to the outside') #
    Nu = Float(232.4543713, iotype='out', desc='Heat Radiated to the outside') #
    k = Float(0.02655, units = 'W/(m*K)', iotype='out', desc='Heat Radiated to the outside') #
    h = Float(0.845464094, units = 'W/((m**2)*K)', iotype='out', desc='Heat Radiated to the outside') #
    convectionArea = Float(3374876.115, units = 'W', iotype='out', desc='Heat Radiated to the outside') #
    naturalConvection = Float(7.9, units = 'W/(m**2)', iotype='out', desc='Heat Radiated to the outside') #
    naturalConvectionTot = Float(286900419., units = 'W', iotype='out', desc='Heat Radiated to the outside') #
    

    #Intermediate Variables
    #tubeTemp = Float(406.6, units = 'K', iotype='in', desc='Average Temperature of the tube') #
    #surfA_pipe = Float(1.0, units = 'm**2', iotype='out', desc='Surface Area of the Pipe')
    #Dh = Float(1.0, units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for fluid flow')
    #De = Float(1.0, units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for heat flow')

    #Calculated Variables
    #Veloc_a = Float(1.0, units= 'm/s', iotype='out', desc='flow velocity of air')
    #h_a = Float(1.0, units = 'W/m', iotype='out', desc='heat transfer of air (convection)')
    #q_a = Float(1.0, units = 'W', iotype='out', desc='heat flow of air')
    #U_o = Float(1.0, units = 'W/(m**2)*K', iotype='out', desc='Overall Heat Transfer Coefficient')

    

    def execute(self):
        """Calculate Various Paramters"""
        
        def check(var_name,var,correct_val):
            "Format and print a value check"
            if (abs((((var/correct_val)-1))*100)<2):
                print "{}: {} ........{}%  --> {}!".format(var_name,var,abs(((var/correct_val)-1))*100,"Test Passed")
            else:
                print " ===> {}: {} ........{}%  --> {} ?".format(var_name,var,abs(((var/correct_val)-1))*100,"Test Failed :(")
        
        #Determine heat added by pods coming through
        self.compInletTt = self.ambTubeT*(1+0.2*(self.podMn**2))
        
        self.compInletPt = self.ambTubeP*(1+0.2*(self.podMdot**2))**3.5
        
        self.compExitPt = self.compInletPt * self.PR
        
        self.compExitTt = (self.compInletTt*(self.PR)^(1/3.5)-self.compInletTt)/self.adiabaticEff + self.compInletTt
        
        if( compExitTt < 400)
            self.podCp = 990.8*(self.compExitTt**(0.00316))
        else
            self.podCp = 299.4*(self.compExitTt**(0.1962))
            
        self.podQ = self.podCp*self.compExitTt*self.podMdot
        self.podQTot = self.podQ*self.podFreq
        
        #Q = mdot * cp * deltaT
        #Qpod = podMdot * podCp * (podTemp-tubeTemp)
        
        #Determine the thermal resistance of the tube via convection
        #calculate h based on Re, Pr, Nu

        
        #Determine thermal resistance of the tube (conduction)
        #

        #Determine thermal resistance of outside via Natural Convection or forced convection
        if(self.ambientTemp < 400)
            self.GrDelTL3 = 10040000000000000000*(self.ambientTempR**(-4.639))
        else
            self.GrDelTL3 = 972600000000000000*(self.ambientTempR**(-4.284)))
            
        if(self.ambientTemp < 400)
            self.Pr = 1.23*(self.ambientTemp**(-0.09685))
        else
            self.Pr = 0.59*(self.ambientTemp**(0.0239))
            
        self.Gr = GrDelTL3*(tubeWallTemp-ambientTemp)*(tubeOD**3)
        
        self.Ra = self.Pr * self.Gr
        
        self.Nu = (0.6 + 0.387*(self.Ra**(1/6))/(1 + (0.559/self.Pr)**(9/16))**(8/27))**2
        
        if(self.ambientTemp < 400)
            self.k = 0.0001423*(self.ambientTemp**(0.9138))
        else
            self.k = 0.0002494*(self.ambientTemp**(0.8152))
        
        self.h = self.k * self.Nu/self.tubeOD
        
        self.convArea = pi * self.tubeLength * self.tubeOD
        
        self.naturalConvection = self.h*(self.tubeWallTemp-self.ambientTemp)
        
        self.naturalConvectionTot = self.naturalConvection * self.convArea
        #Determine heat incoming via Sun radiation (Incidence Flux)

        self.ViewingArea = self.tubeLength * self.tubeOD
        self.solarHeat = (1-self.Surface_reflectance)* self.nnIncidenceF * self.Solar_insolation
        self.solarHeatTotal = self.solarHeat * self.ViewingArea
        
        #Determine heat released via radiation
        self.radArea = self.convArea
        
        self.qRad = self.SBconst*self.tubeEmissivity*((self.tubeWallTemp**4) - (self.ambientTemp**4))
        self.qRadTot = self.radArea * self.qRad
        

        #------------
        
       
       
#run stand-alone component
if __name__ == "__main__":

    from openmdao.main.api import set_as_top
    test = tubeModel()  
    set_as_top(test)
    print ""
    test.run()
    print "-----Completed tubeModel calculations---"
    print ""
    print "Equilibrium Wall Temperature: {} k".format(tubeWallTemp)
    
