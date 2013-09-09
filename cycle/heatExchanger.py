"""
    heatExchanger.py - 
        Performs basic heat exchanger calculations for a single pass
        counter-flow heat exchanger
        
Logarithmic Mean Temperature Difference (LMTD) Method
    Design a heat exchanger to meet prescribed heat transfer requirements

    LMTD Limitations
    1) Restricted to single pass heat exchanger
    - Multipass exchangers can be designed using empirical correction factor ‘F’
    2) Both starting and final temperature parameters must be known

NTU (effectiveness) Method
    Determine the heat transfer rate and outlet temperatures when the type and size of the heat exchanger is specified.

    NTU Limitations
    1) Effectiveness of the chosen heat exchanger must be known (empirical)

    Compatible with OpenMDAO v0.8.1
"""


from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float

from math import log


class heatExchanger(Component):
    """ Main Component """

    #--Inputs--
    #Boundary Temperatures
    T_win = Float(0.0, iotype='in', desc='Temp of water into heat exchanger')
    T_wout = Float(0.0, iotype='in', desc='Temp of water out of heat exchanger')
    T_ain = Float(0.0, iotype='in', desc='Temp of air into heat exchanger')
    T_aout = Float(0.0, iotype='in', desc='Temp of air out of heat exchanger')

    #Design Variables
    Mdot_w = = Float(0.0, iotype='in', desc='Mass flow rate of water pumped through system')
    Ao_pipe = Float(0.0, iotype='out', desc='Shell pipe (Outer) Area')
    Ai_pipe = Float(0.0, iotype='out', desc='Tube pipe (Inner) Area')

    #Assumed Constant Properties
    rho_w = Float(0.0, iotype='in', desc='density of water')
    rho_a = Float(0.0, iotype='in', desc='density of air ')
    cp_w = Float(0.0, iotype='in', desc='specific heat of water')
    cp_a = Float(0.0, iotype='in', desc='specific heat of air')
    dvisc_w = Float(0.0, iotype='in', desc='dynamic viscosity for water')
    dvis_a = Float(0.0, iotype='in', desc='dynamic viscosity for air')
    kvisc_w = Float(0.0, iotype='in', desc='kinematic viscosity for water')
    kvisc_a = Float(0.0, iotype='in', desc='kinematic viscosity for air')
    k_w = Float(0.0, iotype='in', desc='thermal conductivity for water')
    k_a = Float(0.0, iotype='in', desc='thermal conductivity for air')
    k_p = Float(0.0, iotype='in', desc='thermal conductivity of the pipe')

    #--Outputs--
    #Intermediate Variables
    Asurf_pipe = Float(0.0, iotype='out', desc='Surface Area of the Pipe')


    #Calculated Variables
    V_w = Float(0.0, iotype='out', desc='flow velocity of water')
    V_a = Float(0.0, iotype='out', desc='flow velocity of air')
    W_w = Float(0.0, iotype='out', desc='mass flow of water')
    W_a = Float(0.0, iotype='out', desc='mass flow of air')
    h_w = Float(0.0, iotype='out', desc='heat transfer of water')
    h_a = Float(0.0, iotype='out', desc='heat transfer of air')
    q_w = Float(0.0, iotype='out', desc='heat flow of water')
    q_a = Float(0.0, iotype='out', desc='heat flow of air')
    
    #Size/Volume Considerations
    V_water = Float(0.0, iotype='out', desc='Volume of input water tank')
    V_steam = Float(0.0, iotype='out', desc='Volume of output steam tank')
    M_water = Float(0.0, iotype='out', desc='Mass of input water tank')
    M_steam = Float(0.0, iotype='out', desc='Mass of output steam tank')



    def execute(self):
        """Calculate Various Paramters
        """

        #Determine amount of heat that needs to be transferred
        #Q_water must equal Q_air
        #Q = Mdot * Cp * delta T



        #Determine the flow rate of the water
        # Mdot = rho * Area * Volume


        #Determine Hyrdraulic Diameters



        #Determine Overall Heat Transfer Coefficient
        #1) Calculate Reynolds Number
        #2) Calculate Prandtl Number
        #3) Calculate Nusselt Number


        #Determine LMTD
        LMTD = self.LMTD #Log Mean Temp Diff
        Th_in = self.T_ain
        Tc_in = self.T_win
        Th_out = self.T_aout
        Tc_out = self.T_wout

        dT1 = (Th_out - Th_in) #Change in T1 (delta T1)
        dT2 = (Tc_out-Tc_in) #Change in T2 (delta T2)

        self.LMTD = (dT1 - dT2)/(log(dT1/(dT2), e)) #take natural log (base e)



        #Determine the required length of the heat exchanger



        #Assume fouling losses



        #Assume pipe minor losses