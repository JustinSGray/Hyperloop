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
    airTube = Float(0., units = 'kg', iotype='in', desc='Total air in tube') #
    airRho = Float(0., units = 'kg/m**3', iotype='in', desc='density of air in the tube')
    tubeID = Float(2.23, units = 'm', iotype='in', desc='Tube inner diameter') #
    tubeOD = Float(2.33, units = 'm', iotype='in', desc='Tube out diameter') #
    tubeLength = Float(0., units = 'm', iotype='in', desc='Length of entire Hyperloop') #
    tubeK = Float(0., units = 'W/(m*K)', iotype='in', desc='thermal conductivity of the tube (conduction)')
    podCp = Float(1006., units = 'J/(kg*K)', iotype='in', desc='specific heat of hot pod air')
    tubeCp = Float(1.1221, units = 'J/(kg*K)', iotype='in', desc='specific heat of tube air')
    
    #Design Variables
    podTemp = Float(406.6, units = 'K', iotype='in', desc='Temperature Released by each pod') #
    podMdot = Float(406.6, units = 'kg/s', iotype='in', desc='Amount of air released by each pod') #
    podFreq = Float(406.6, units = 'K', iotype='in', desc='Frequency Pods travel down tube') #
    
    
    tubeWallTemp = Float(406.6, units = 'K', iotype='in', desc='Average Temperature of the tube') #
    ambientTemp = Float(406.6, units = 'K', iotype='in', desc='Average Temperature of the outside air') #
    Solar_constant = Float(1366., units = 'K', iotype='in', desc='Average Temperature of the outside air') #
    Solar_insolation = Float(1000., units = 'K', iotype='in', desc='Average Temperature of the outside air') #
    nnIncidenceF = Float(0.7, iotype='in', desc='Non-normal incidence factor') #
    Surface_reflectance = Float(0.5, iotype='in', desc='Average Temperature of the outside air') #
    solarHeat = Float(350., units = 'W/m**2', iotype='in', desc='Solar Heat Absorbed per Area') #
    solarHeatTotal = Float(0., units = 'W', iotype='in', desc='Solar Heat Absorbed by Tube') #
    
    SBconst = Float(0., units = 'W', iotype='in', desc='Stefan-Boltzmann Constant') #
    radArea = Float(0., units = 'W', iotype='in', desc='Tube Radiating Area') #
    tubeEmissivity = Float(0., units = 'W', iotype='in', desc='Emmissivity of the Tube') #
    qRad = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    qRadTot = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    
    
    GrDelTL3 = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    Pr = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    Gr = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    Ra = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    Nu = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    k = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    h = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    convectionArea = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    naturalConvection = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    naturalConvectionTot = Float(0., units = 'W', iotype='in', desc='Heat Radiated to the outside') #
    
    
    
    #--Outputs--
    #Intermediate Variables
    #tubeTemp = Float(406.6, units = 'K', iotype='in', desc='Average Temperature of the tube') #
    Asurf_pipe = Float(1.0, units = 'm**2', iotype='out', desc='Surface Area of the Pipe')
    Dh = Float(1.0, units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for fluid flow')
    De = Float(1.0, units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for heat flow')

    #Calculated Variables
    Veloc_a = Float(1.0, units= 'm/s', iotype='out', desc='flow velocity of air')
    h_a = Float(1.0, units = 'W/m', iotype='out', desc='heat transfer of air (convection)')
    q_a = Float(1.0, units = 'W', iotype='out', desc='heat flow of air')
    U_o = Float(1.0, units = 'W/(m**2)*K', iotype='out', desc='Overall Heat Transfer Coefficient')

    

    def execute(self):
        """Calculate Various Paramters"""
        
        def check(var_name,var,correct_val):
            "Format and print a value check"
            if (abs((((var/correct_val)-1))*100)<2):
                print "{}: {} ........{}%  --> {}!".format(var_name,var,abs(((var/correct_val)-1))*100,"Test Passed")
            else:
                print " ===> {}: {} ........{}%  --> {} ?".format(var_name,var,abs(((var/correct_val)-1))*100,"Test Failed :(")
        
        #Determine heat added by pods coming through
        Mach
        
        compInletTt = ambTubeT*(1+0.2*(Mach**2))
        
        
        compInletPt = ambTubeP*(1+0.2*(podMdot**2))**3.5
        
        compExitPt = compInletPt * PR
        
        compExitTt = (compInletTt*(PR)^(1/3.5)-compInletTt)/adEff + compInletTt
        
        if( compExitTt < 400)
            cp = 990.8*(compExitTt**(0.00316))
        else
            cp = 299.4*(compExitTt**(0.1962))
            
        singleCapsule = cp*compExitTt*podMdot
        allCapsules = singleCapsule*podFreq
        
        #Q = mdot * cp * deltaT
        Qpod = podMdot * podCp * (podTemp-tubeTemp)
        
        #Determine the thermal resistance of the tube via convection
        #calculate h based on Re, Pr, Nu

        
        #Determine thermal resistance of the tube (conduction)
        #

        #Determine thermal resistance of outside via Natural Convection or forced convection
        if(ambT < 400)
            GrDelTL3 = 10040000000000000000*(ambTR**(-4.639))
        else
            GrDelTL3 = 972600000000000000*(ambTR**(-4.284)))
            
        if(ambT < 400)
            Pr = 1.23*(ambT**(-0.09685))
        else
            Pr = 0.59*(ambT**(0.0239))
            
        Gr = GrDelTL3*(tubeWallTemp-ambientTemp)*(tubeOD**3)
        
        Ra = Pr * Gr
        
        Nu = (0.6 + 0.387*(Ra**(1/6))/(1 + (0.559/Pr)**(9/16))**(8/27))**2
        
        if(ambT < 400)
            k = 0.0001423*(ambT**(0.9138))
        else
            k = 0.0002494*(ambT**(0.8152))
        
        h = k * Nu/tubeOD
        
        convArea = pi * tubeLength * tubeOD
        
        naturalConvection = h*(tubeWallTemp-ambientTemp)
        
        naturalConvectionTot = naturalConvection * convArea
        #Determine heat incoming via Sun radiation (Incidence Flux)

        ViewingArea = tubeLength * tubeOD
        solarHeat = (1-Surface_reflectance)* nnIncidenceF * Solar_insolation
        solarHeatTotal = solarHeat * ViewingArea
        
        #Determine heat released via radiation
        radArea = convArea
        
        qRad = SBconst*tubeEmissivity*((tubeWallTemp**4) - (ambientTemp**4))
        qRadTot = radArea * qRad
        
        
        
        
        #------------
        
       
       
#run stand-alone component
if __name__ == "__main__":

    from openmdao.main.api import set_as_top
    test = heatExchanger()  
    set_as_top(test)
    print ""
    test.run()
    print "-----Completed Heat Exchanger Sizing---"
    print ""
    print "Heat Exchanger Length: {} meters, with {} tube pass(es)".format(test.L/2,test.N)
    
    m2ft = 3.28084 #meter to feet conversion
    
    #sqrt(#passes * tube area * packing factor)
    #assumes shell magically becomes rectangular but keeps packing factor
    packing_factor =  (test.A_a/(test.A_a + test.A_w)) + 1
    x = ((test.N * pi*((test.Do_tube/2)**2)*packing_factor)**0.5)*m2ft
    y = 2*x #height of a double pass
 
    tot_vol = (x*(y) * (test.L *m2ft))
    
    print "Heat Exchanger Dimensions: {}ft (Length) x {}ft (Width) x {}ft (Height)".format((test.L/2)*m2ft,x,y)
    print "Heat Exchanger Volume: {} ft^3".format( tot_vol)

