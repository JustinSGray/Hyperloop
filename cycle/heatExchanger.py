"""
    heatExchanger.py - 
        Performs basic heat exchanger calculations for a single pass
        counter-flow shell and tube heat exchanger
        
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

from math import log, pi


class heatExchanger(Component):
    """ Main Component """

    #--Inputs--
    #Boundary Temperatures
    T_win = Float(0.0, units = 'K', iotype='in', desc='Temp of water into heat exchanger')
    T_wout = Float(0.0, units = 'K', iotype='in', desc='Temp of water out of heat exchanger')
    T_ain = Float(0.0, units = 'K', iotype='in', desc='Temp of air into heat exchanger')
    T_aout = Float(0.0, units = 'K', iotype='in', desc='Temp of air out of heat exchanger')

    #Design Variables
    Mdot_w = Float(0.0, units = 'kg/s', iotype='in', desc='Mass flow rate of water pumped through system')
    Mdot_a = Float(0.0, units = 'kg/s', iotype='out', desc='Mass flow rate of air')
    Di_shell = Float(0.0, units = 'm', iotype='out', desc='Shell pipe (inner) Diameter')
    Do_tube = Float(0.0, units = 'm', iotype='out', desc='Tube pipe (outer) Diameter')
    Di_tube = Float(0.0, units = 'm', iotype='out', desc='Tube pipe (inner) Diameter')

    #Assumed Constant Properties
    rho_w = Float(0.0, units = 'kg/m**3', iotype='in', desc='density of water')
    rho_a = Float(0.0, units = 'kg/m**3', iotype='in', desc='density of air ')
    cp_w = Float(0.0, units = 'J/(kg*K)', iotype='in', desc='specific heat of water')
    cp_a = Float(0.0, units = 'J/(kg*K)', iotype='in', desc='specific heat of air')
    dvisc_w = Float(0.0, units = 'kg/(m*s)', iotype='in', desc='dynamic viscosity for water')
    dvis_a = Float(0.0, units = 'kg/(m*s)', iotype='in', desc='dynamic viscosity for air')
    kvisc_w = Float(0.0, units = 'm**2/s', iotype='in', desc='kinematic viscosity for water')
    kvisc_a = Float(0.0, units = 'm**2/s', iotype='in', desc='kinematic viscosity for air')
    k_w = Float(0.0, units = 'W/(m*K)', iotype='in', desc='thermal conductivity for water')
    k_a = Float(0.0, units = 'W/(m*K)', iotype='in', desc='thermal conductivity for air')
    k_p = Float(0.0, units = 'W/(m*K)', iotype='in', desc='thermal conductivity of the pipe')

    #--Outputs--
    #Intermediate Variables
    Asurf_pipe = Float(0.0, units = 'm**2', iotype='out', desc='Surface Area of the Pipe')
    Dh = Float(0.0, units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for fluid flow')
    De = Float(0.0, units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for heat flow')

    #Calculated Variables
    V_w = Float(0.0, units= 'm/s', iotype='out', desc='flow velocity of water')
    V_a = Float(0.0, units= 'm/s', iotype='out', desc='flow velocity of air')
    h_w = Float(0.0, iotype ='out', desc='heat transfer of water')
    h_a = Float(0.0, units = 'W/(m**2)*K', iotype='out', desc='heat transfer of air')
    q_w = Float(0.0, units = 'W', iotype='out', desc='heat flow of water')
    q_a = Float(0.0, units = 'W', iotype='out', desc='heat flow of air')
    
    #Size/Volume Considerations
    Vol_water = Float(0.0, units= 'm**3', iotype='out', desc='Volume of input water tank')
    Vol_steam = Float(0.0, units= 'm**3', iotype='out', desc='Volume of output steam tank')
    Mass_water = Float(0.0, units= 'kg', iotype='out', desc='Mass of input water tank')
    Mass_steam = Float(0.0, units= 'kg', iotype='out', desc='Mass of output steam tank')



    def execute(self):
        """Calculate Various Paramters"""

        #Determine the area of the air tube
        A_a = pi*(self.Di_tube/2)^2
        #Determine the fluid velocity of the air
        #Rearrange Mdot = rho * Area * Velocity --> Velocity = Mdot/(rho*Area)
        Veloc_a = Mdot_a / (rho_a * A_a)


        #Determine q
        #q = mdot * cp * deltaT
        q_a = Mdot_a* cp_a * (T_aout - T_ain)

        #Energy Balance: Q_water must equal Q_air
        q_w = q_a

        #Determine water Mdot
        #q = mdot * cp * deltaT
        Mdot_w = q_w / cp_w * (T_win - T_wout)
        #Determine the flow velocity of the water
        #Rearrange Mdot = rho * Area * Velocity --> Velocity = Mdot/(rho*Area)
        Veloc_w = Mdot_w / (rho_w * A_w)


        #Hydraulic Diameter
        #D_h = (4*Af)/(Pflow) = 4*pi*(Di_shell^2 - Do_tube^2)/ 4*pi*(Di_shell - Do_tube) = Di_shell - Do_tube
        #D_e = (4*Af)/(PheatTransfer) = 4*pi*(Di_shell^2 - Do_tube^2)/ 4*pi* Do_tube = (Di_shell^2 - Do_tube^2)/Do_tube

        Dw_h = self.Di_shell - Do_tube
        Dw_e = (self.Di_shell^2 - self.Do_tube^2)/self.Do_tube

        Da_h = self.Di_shell - Do_tube
        Da_e = (self.Di_shell^2 - self.Do_tube^2)/self.Do_tube

        #Determine the Reynolds Number
        #Re = velocity * hydraulic dimater / kinematic viscostiy   (general form for pipes)
        #Re = inertial forces/ viscous forces
        Re_a = Veloc_a*Da_h/self.kvisc_a
        Re_w = Veloc_w*Dw_h/self.kvisc_w

        
        #Determine the Prandtl Number
        #Nu = viscous diffusion rate/ thermal diffusion rate = Cp * dyanamic viscosity / thermal conductivity
        #Pr << 1 means thermal diffusivity dominates
        #Pr >> 1 means momentum diffusivity dominates
        Pr_a = cp_a*dvis_a/kvisc_a
        Pr_w = cp_w*dvis_w/kvisc_w

        #Determine the Nusselt Number
        #Pr = viscous diffusion rate/ thermal diffusion rate = Cp * dyanamic viscosity / thermal conductivity
        #Pr << 1 means thermal diffusivity dominates
        #Pr >> 1 means momentum diffusivity dominates
        Nu_a = 
        Nu_w = 

        #Determine h
        # h = Nu * k/ D

        h_a
        h_w 



        #Determine Overall Heat Transfer Coefficient
        # eq...


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
        # Q = U * A * LMTD


        #Multi-Pass Corrections
        #lookup table


        #Assume fouling losses
        #lookup

        #Assume pipe minor losses
        #function of length and number of passes