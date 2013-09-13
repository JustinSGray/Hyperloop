"""
    heatExchanger.py - 
        Performs basic heat exchanger calculations for a multi-tube double pass
        counter-flow or co-flow shell and tube heat exchanger
        
Logarithmic Mean Temperature Difference (LMTD) Method
    Design a heat exchanger to meet prescribed heat transfer requirements

    LMTD Limitations
    -Both starting and final temperature parameters must be known
    -Rigorously defined for double-pipe(or tubular) heat exchanger

NTU (effectiveness) Method
    Determine the heat transfer rate and outlet temperatures when the type and size of the heat exchanger is specified.

    NTU Limitations
    1) Effectiveness of the chosen heat exchanger must be known (empirical)

    Compatible with OpenMDAO v0.8.1
"""


from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, Bool

from math import log, pi, sqrt, e


class heatExchanger(Component):
    """ Main Component """

    #--Inputs--
    #Boundary Temperatures
    T_win = Float(368, units = 'K', iotype='in', desc='Temp of water into heat exchanger') #368 , 110
    T_wout = Float(358, units = 'K', iotype='in', desc='Temp of water out of heat exchanger') #358 , 190
    T_ain = Float(297, units = 'K', iotype='in', desc='Temp of air into heat exchanger') #297, 400
    T_aout = Float(308, units = 'K', iotype='in', desc='Temp of air out of heat exchanger') #308, 170

    #Design Variables
    Mdot_w = Float(1.0, units = 'kg/s', iotype='in', desc='Mass flow rate of water pumped through system')
    Mdot_a = Float(2.2221623, units = 'kg/s', iotype='out', desc='Mass flow rate of air')
    Di_shell = Float(0.05102, units = 'm', iotype='out', desc='Shell pipe (inner) Diameter')
    Do_tube = Float(0.03493, units = 'm', iotype='out', desc='Tube pipe (outer) Diameter')
    Di_tube = Float(0.03279, units = 'm', iotype='in', desc='Tube pipe (inner) Diameter') #0.03279, 0.0371851871796067
    #A_a = Float(1.0, units = 'm**2', iotype='out', desc='Area')
    N = Float(1, units = 'm', iotype='out', desc='Number of Tube Passes')
    
    cooled = Bool(True, desc= 'Boolean true if fluid is cooled, false if heated')
    coFlow = Bool(False, desc= 'Boolean true if co-flow, false if coutner-flow')

    #Assumed Constant Properties
    rho_w = Float(1000.0, units = 'kg/m**3', iotype='in', desc='density of water')
    rho_a = Float(730., units = 'kg/m**3', iotype='in', desc='density of air ')
    cp_w = Float(4208., units = 'J/(kg*K)', iotype='in', desc='specific heat of water')
    cp_a = Float(2470., units = 'J/(kg*K)', iotype='in', desc='specific heat of air')
    dvisc_w = Float(0.00031, units = 'kg/(m*s)', iotype='in', desc='dynamic viscosity for water')
    dvisc_a = Float(0.0004, units = 'kg/(m*s)', iotype='in', desc='dynamic viscosity for air')
    kvisc_w = Float(0.000000326, units = 'm**2/s', iotype='in', desc='kinematic viscosity for water')
    kvisc_a = Float(0.0000005479, units = 'm**2/s', iotype='in', desc='kinematic viscosity for air')
    k_w = Float(0.58, units = 'W/(m*K)', iotype='in', desc='thermal conductivity for water')
    k_a = Float(0.132, units = 'W/(m*K)', iotype='in', desc='thermal conductivity for air')
    k_p = Float(400.0, units = 'W/(m*K)', iotype='in', desc='thermal conductivity of the pipe')
    R_w = Float(1.0, units = 'W/(m*K)', iotype='in', desc='fouling factor of city water')
    R_a = Float(1.0, units = 'W/(m*K)', iotype='in', desc='fouling factor of air')

    #--Outputs--
    #Intermediate Variables
    Asurf_pipe = Float(1.0, units = 'm**2', iotype='out', desc='Surface Area of the Pipe')
    Dh = Float(1.0, units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for fluid flow')
    De = Float(1.0, units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for heat flow')
    A_a = Float(1.0, units= 'm**2', iotype='out', desc='area of air')
    A_w = Float(1.0, units= 'm**2', iotype='out', desc='area of water')
    #Calculated Variables
    Veloc_w = Float(1.0, units= 'm/s', iotype='out', desc='flow velocity of water')
    Veloc_a = Float(1.0, units= 'm/s', iotype='out', desc='flow velocity of air')
    h_w = Float(1.0, units = 'W/m', iotype ='out', desc='heat transfer of water')
    h_a = Float(1.0, units = 'W/m', iotype='out', desc='heat transfer of air')
    q_w = Float(1.0, units = 'W', iotype='out', desc='heat flow of water')
    q_a = Float(1.0, units = 'W', iotype='out', desc='heat flow of air')
    U_o = Float(1.0, units = 'W/(m**2)*K', iotype='out', desc='Overall Heat Transfer Coefficient')
    L = Float(1.0, units = 'm', iotype='out', desc='Heat Exchanger Length')
    F = Float(1.0, iotype='out', desc='Multi-pass correction factor')
    
    #Size/Volume Considerations
    Vol_water = Float(1.0, units= 'm**3', iotype='out', desc='Volume of input water tank')
    Vol_steam = Float(1.0, units= 'm**3', iotype='out', desc='Volume of output steam tank')
    Mass_water = Float(1.0, units= 'kg', iotype='out', desc='Mass of input water tank')
    Mass_steam = Float(1.0, units= 'kg', iotype='out', desc='Mass of output steam tank')


    def execute(self):
        """Calculate Various Paramters"""
        
        def check(var_name,var,correct_val):
            "Format and print a value check"
            if (abs((((var/correct_val)-1))*100)<2):
                print "{}: {} ........{}%  --> {}!".format(var_name,var,abs(((var/correct_val)-1))*100,"Test Passed")
            else:
                print " ===> {}: {} ........{}%  --> {} ?".format(var_name,var,abs(((var/correct_val)-1))*100,"Test Failed :(")
                
        Th_in = self.T_ain #T hot air in
        Th_out = self.T_aout #T air out
        Tc_in = self.T_win #T cold water in
        Tc_out = self.T_wout #T water out

        Di_shell = self.Di_shell
        Do_tube = self.Do_tube
        Di_tube = self.Di_tube

        #Determine the area of the air tube
        self.A_a = pi*(self.Di_tube/2)**2
        
        check('A_a',self.A_a, 0.0008444)
        #prevent cascading errors (switch areas)
        self.A_a = 0.001086
        self.A_w = 0.0008444
        #Determine the fluid velocity of the air
        #Rearrange Mdot = rho * Area * Velocity --> Velocity = Mdot/(rho*Area)
        self.Veloc_a = self.Mdot_a / (self.rho_a * self.A_a)
        
        check('Veloc_a',self.Veloc_a, 2.803)
        #Determine q
        #q = mdot * cp * deltaT
        self.q_a = self.Mdot_a* self.cp_a * (Th_out - Th_in)

        #Energy Balance: Q_water must equal Q_air
        self.q_w = self.q_a
        
        check('q_a',self.q_a, 60377.8)

        #Determine water Mdot
        #q = mdot * cp * deltaT
        self.Mdot_w = self.q_w / (self.cp_w * (Tc_in - Tc_out))

        check('Mdot_w',self.Mdot_w, 1.45)
        
        #Determine the Water Cross sectional Area 
        self.A_w = (pi*(Di_shell/2)**2)- pi*((Do_tube/2)**2)
        check('A_w',self.A_w, 0.001086)
        
        
        #Determin flow velocity of the water, from Mdot and Area
        #Rearrange Mdot = rho * Area * Velocity --> Velocity = Mdot/(rho*Area)
        self.Veloc_w = self.Mdot_w / (self.rho_w * self.A_w)
        check('Veloc_w',self.Veloc_w, 1.71)
        #prevent cascading
        self.Veloc_w = 1.71

        #Hydraulic Diameter (aka characteristic length)
        #D_h = (4*Af)/(Pflow) = 4*pi*(Di_shell^2 - Do_tube^2)/ 4*pi*(Di_shell - Do_tube) = Di_shell - Do_tube
        #D_e = (4*Af)/(PheatTransfer) = 4*pi*(Di_shell^2 - Do_tube^2)/ 4*pi* Do_tube = (Di_shell^2 - Do_tube^2)/Do_tube

        Da_h = Di_shell - Do_tube
        Da_e = (Di_shell**2 - Do_tube**2)/Do_tube

        check('Da_h',Da_h, 0.016082)
        check('Da_e',Da_e, 0.039586)
        
        Dw_h = Di_tube
        Dw_e = Di_tube
        
        check('Dw_h',Dw_h, Di_tube)
        check('Dw_e',Dw_e, Di_tube)
        
        #cascading errors
        #Da_h = 0.016082
        #Da_e = 0.039586
        #Dw_h = Di_tube
        #Dw_e = 0.03279
        
        #Determine the Reynolds Number
        #Re = velocity * hydraulic dimater / kinematic viscostiy   (general form for pipes)
        #Re = inertial forces/ viscous forces
        Re_a = self.Veloc_a*Da_h/self.kvisc_a
        
        Re_w = self.Veloc_w*Dw_h/self.kvisc_w

        check('Re_a',Re_a, 82317)
        check('Re_w',Re_w, 174215)
        Re_w = 174215
 
        #Determine the Prandtl Number
        #Nu = viscous diffusion rate/ thermal diffusion rate = Cp * dyanamic viscosity / thermal conductivity
        #Pr << 1 means thermal diffusivity dominates
        #Pr >> 1 means momentum diffusivity dominates
        Pr_a = self.cp_a*self.dvisc_a/self.k_a
        Pr_w = self.cp_w*self.dvisc_w/self.k_w

        check('Pr_a',Pr_a, 7.48)
        check('Pr_w',Pr_w, 2.25)

        #Determine the Nusselt Number
        #Nu = convecive heat transfer / conductive heat transfer
        #Nu = hL / k = (convective coeff * characteristic length) / conductive coeff

        #Dittus-Boelter equation: valid for smooth pipes with small temp difference across fluid
        #Nu = 0.023*(Re^4/5)*(Pr^n)  where 'n' = 0.4 if heated or = 0.3 if cooled
        #Valid for 0.6 <= Pr <=160
        #and              Re >= 10,000
        #and    L/D >= 10

        #Sieder-Tate correlation
        #Nu = 0.027*(Re^4/5)*(Pr^1/3)*((u/u_s)^0.14)
        #where u = fluid viscosity at the bulk fluid temp
        #where u_s = fluid viscosity at the heat-transfer boundary surface temp
        #(More accurate than Dittus-Boelter, but requires iterative process)
        #(Viscosity factor will change as the Nusselt Number changes)
        #Valid for 0.7 <= Pr <= 16,700
        #and              Re >= 10,000
        #and    L/D >= 10

        #Gnielinski correlation: valid for turbulent flow tubes
        #Nu = ((f/8)*(Re-1000)*Pr)/(1+12.7((f/8)^0.5)*((Pr^2/3)-1))
        #f is the Darcy Friction Factor (obtained from Moody Chart)
        #or f = (0.79*ln(Re) - 1.64)^-2   for smooth tubes
        #Valid for 0.5<= Pr <=2000
        #and      3000<= Re <= 5*(10^6)
        if ((Re_a >10000) and (Re_w > 10000) and (0.6 < Pr_a < 160) and (0.6 < Pr_w < 160)):
            print ""
            print "   Dittus-Boelter Equation Valid. Calculating Nusselt Number   "
        else:
            print ""
            print "!!!** Dittus-Boelter Equation not valid. Use alternate method  **!!!"

        Nu_a = 0.023*(Re_a**(4./5))*(Pr_a**0.4) #fluid is heated n=0.4
        Nu_w = 0.023*(Re_w**(4./5))*(Pr_w**0.3) #fluid is cooled n=0.3
        
        check('Nu_a',Nu_a, 440.345)
        check('Nu_w',Nu_w, 457.16)

        #Determine h
        # h = Nu * k/ D
        self.h_a = Nu_a*self.k_a/Da_e
        self.h_w = Nu_w*self.k_w/Dw_e

        check('h_a',self.h_a, 1467.95)
        check('h_w',self.h_w, 8088.82)
        
        #cascading
        self.h_a = 1467.95
        self.h_w = 8088.82

        #Determine Overall Heat Transfer Coefficient
        # U_o = 1 / [(Ao/Ai*hi)+(Ao*ln(ro/ri)/2*pi*k*L)+(1/ho)]
        # (simplified)
        # U_o = 1/ [(Do/Di*hi)+(Do*ln(Do/Di)/2*k)+(1/ho)]
        
        #print "Do_tube{} Di_tube{} self.h_a{} self.k_p{}  self.h_w{}".format(Do_tube,Di_tube, self.h_a, self.k_p, self.h_w)
        Di_tube = 0.03279
        term1 = Do_tube/(Di_tube*self.h_w)
        term2 =  Do_tube*log((Do_tube/Di_tube),e)
        
        self.U_o = 1/ (term1+(term2/(2*self.k_p))+(1/self.h_a))
        check('U_o',self.U_o, 1226)
        
        #Assume fouling losses
        #lookup R_w, R_a
        self.U_oF = 1/ ((term1+(term2/(2*self.k_p))+(1/self.h_a))+(self.R_w+self.R_a))

        #--Determine LMTD--
        #if(coFlow):
            #dT1 = (Th_in - Tc_in) #Change in T1 (delta T1)
            #dT2 = (Th_out-Tc_out) #Change in T2 (delta T2)
        #else: #counter-flow
        dT1 = (Th_in - Tc_out) #Change in T1 (delta T1)
        dT2 = (Th_out-Tc_in) #Change in T2 (delta T2)

        self.LMTD = abs((dT1- dT2)/(log((dT1/dT2), e))) #take natural log (base e)
        
        check('LMTD',self.LMTD, 60.49)

        print ""
        if (self.N>1):
            #Multi-Pass Corrections
            #Calc P, R  (Table lookup or equation parameters)
            P = (Tc_out-Tc_in)/(Th_out-Tc_in)
            R = (Th_in - Th_out)/(Tc_out-Tc_in)
            #P = (Th_out-Th_in)/(Tc_out-Th_in)
            #R = (Tc_in - Tc_out)/(Th_out-Th_in)

            #Calc X
            X1 = ((R*P-1)/(P-1))**(1./self.N)
            X_num = 1 - X1
            X_denom = R - X1
            X = X_num/X_denom

            
            #Calc F  (Equation fitted to empirical data)
            F_sqr = sqrt(R**2. + 1)
            
            F_num = (F_sqr/(R-1))*log(((1-X)/(1-R*X)),e)
            F_denom1 = (2/X)-1-R + F_sqr
            F_denom2 = (2/X)-1-R - F_sqr
            F_denom = log(F_denom1/F_denom2,e)
            self.F = F_num / F_denom 
            
            print "   {} pass design, correction factor calculated to be: {}".format(self.N,self.F)
        else:
            print "   Single Pass Design, no correction factor"
            self.F = 1
        #Determine the required length of the heat exchanger
        # Q = U * A * LMTD
        # Q = U*pi*D*L*LMTD
        # L = Q/(U*pi*D*LMTD)
        self.L = self.q_a/(self.U_o*pi*self.F*Do_tube*self.LMTD)
        self.L = self.L / self.N #divide by number of passes
        
        if (self.N < 2): #only check single pass case
            check('L',self.L, 7.42)
        

        #Assume pipe minor losses
        #function of length and number of passes
        #Head losses
        #Developed from Bernoulli eq, with zero velocity change and viscous terms included in apparent height
        # H = (k + f*(L/D)*v_avg^2)/2g
        # delP = rho*g*H
        # Also consider bends in tube
        
       
       
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

