"""
heat_exchanger_sizing.py -  (This one is for water and air)
    Performs basic heat exchanger calculations for a multi-tube double pass
    counter-flow or co-flow shell and tube heat exchanger
        
Logarithmic Mean Temperature Difference (LMTD) Method
Design a heat exchanger to meet prescribed heat transfer requirements

LMTD Limitations
  -Both starting and final temperature parameters must be known
  -Temperature change across cannot be so large that Cp changes significantly
  -Rigorously defined for double-pipe(or tubular) heat exchanger

Compatible with OpenMDAO v0.8.1
"""
from openmdao.main.api import Component
from openmdao.lib.datatypes.api import Float, Bool
from openmdao.main.api import convert_units as cu
from math import log, pi, sqrt, e

#Assumed Constant Water Properties
#http://www.engineeringtoolbox.com/air-properties-d_156.html air @300C
rho_w = 1000.0#, units = 'kg/m**3', desc='density of water')
cp_w = 4186.#, units = 'J/(kg*K)', desc='specific heat of water')
dvisc_w = 0.00031#, units = 'kg/(m*s)', desc='dynamic viscosity for water')
kvisc_w = 0.000000326#, units = 'm**2/s', desc='kinematic viscosity for water')
#Assumed fouling factors
R_w = 1.0#, units = 'W/(m*K)', desc='fouling factor of city water')
R_a = 1.0#, units = 'W/(m*K)', desc='fouling factor of air')
#Conductivity properties
k_w = 0.58#, units = 'W/(m*K)', iotype='in', desc='thermal conductivity for water')
k_a = 0.0454#, units = 'W/(m*K)', iotype='in', desc='thermal conductivity for air')
k_p = 400.0#, units = 'W/(m*K)', iotype='in', desc='thermal conductivity of the pipe')

class HeatExchangerSizing(Component):
    """ Main Component """

    #--Inputs--
    T_win = Float(units = 'K', iotype='in', desc='Temp of water into heat exchanger') #368 , 110
    T_wout = Float(units = 'K', iotype='in', desc='Temp of water out of heat exchanger') #358 , 190
    T_ain = Float(units = 'K', iotype='in', desc='Temp of air into heat exchanger') #297, 400
    T_aout = Float(units = 'K', iotype='in', desc='Temp of air out of heat exchanger') #308, 170
    Mdot_a = Float(units = 'kg/s', iotype='in', desc='Mass flow rate of air')

    #Heat Exchanger Physical Design Variables
    Di_shell = Float(0.05102, units = 'm', iotype='in', desc='Shell pipe (inner) Diameter')
    Do_tube = Float(0.03493, units = 'm', iotype='in', desc='Tube pipe (outer) Diameter')
    Di_tube = Float(0.03279, units = 'm', iotype='in', desc='Tube pipe (inner) Diameter') #0.03279, 0.0371851871796067
    N = Float(1, units = 'm', iotype='in', desc='Number of Tube Passes')
    
    cooled = Bool(True, desc= 'Boolean true if fluid is cooled, false if heated')
    coFlow = Bool(False, desc= 'Boolean true if co-flow, false if coutner-flow')

    #Assumed Constant Properties of air (should come in from flow station)
    rho_a = Float(0.616, units = 'kg/m**3', iotype='in', desc='density of air ')
    cp_a = Float(1006., units = 'J/(kg*K)', iotype='in', desc='specific heat of air')
    dvisc_a = Float(0.00002, units = 'kg/(m*s)', iotype='in', desc='dynamic viscosity for air')
    kvisc_a = Float(0.00001568, units = 'm**2/s', iotype='in', desc='kinematic viscosity for air')
    

    #--Outputs--
    #Calculated Variables
    Asurf_pipe = Float(units = 'm**2', iotype='out', desc='Surface Area of the Pipe')
    Da_h = Float(units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for fluid flow')
    Da_e = Float(units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for heat flow')
    Dw_h = Float(units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for fluid flow')
    Dw_e = Float(units= 'm', iotype='out', desc='Hyrdraulic Diameter of the shell (annulus) for heat flow')

    A_a = Float(units= 'm**2', iotype='out', desc='cross sectional area of air')
    A_w = Float(units= 'm**2', iotype='out', desc='cross sectional area of water')
    Veloc_w = Float(units= 'm/s', iotype='out', desc='flow velocity of water')
    Veloc_a = Float(units= 'm/s', iotype='out', desc='flow velocity of air')
    Re_a = Float(iotype='out', desc='Reynolds Number of air')
    Re_w = Float(iotype='out', desc='Reynolds Number of water')
    Pr_a = Float(iotype='out', desc='Prandtl Number of air')
    Pr_w = Float(iotype='out', desc='Prandtl Number of water')
    Nu_a = Float(iotype='out', desc='Nusselt Number of air')
    Nu_w  = Float(iotype='out', desc='Nusselt Number of water') 
    h_w = Float(units = 'W/m', iotype ='out', desc='heat transfer of water')
    h_a = Float(units = 'W/m', iotype='out', desc='heat transfer of air')
    q_w = Float(units = 'W', iotype='out', desc='heat flow of water')
    q_a = Float(units = 'W', iotype='out', desc='heat flow of air')
    F = Float(iotype='out', desc='Multi-pass correction factor')

    #Most Interesting Outputs
    Mdot_w = Float(1.0, units = 'kg/s', iotype='in', desc='Mass flow rate of water pumped through system')
    U_o = Float(1.0, units = 'W/(m**2)*K', iotype='out', desc='Overall Heat Transfer Coefficient')
    L = Float(1.0, units = 'm', iotype='out', desc='Heat Exchanger Length')
    
    #Size/Volume Considerations
    #Vol_water = Float(1.0, units= 'm**3', iotype='out', desc='Volume of input water tank')
    #Vol_steam = Float(1.0, units= 'm**3', iotype='out', desc='Volume of output steam tank')
    #Mass_water = Float(1.0, units= 'kg', iotype='out', desc='Mass of input water tank')
    #Mass_steam = Float(1.0, units= 'kg', iotype='out', desc='Mass of output steam tank')


    def execute(self):
        """Calculate Various Paramters"""
             
        Th_in = self.T_ain #T hot air in
        Th_out = self.T_aout #T air out
        Tc_in = self.T_win #T cold water in
        Tc_out = self.T_wout #T water out

        Di_shell = self.Di_shell
        Do_tube = self.Do_tube
        Di_tube = self.Di_tube

        #Determine the cross sectional area of the air tube
        self.A_a = pi*(self.Di_tube/2)**2

        #prevent cascading errors (switch areas)
        #self.A_a = 0.001086
        #self.A_w = 0.0008444
        #Determine the fluid velocity of the air
        #Rearrange Mdot = rho * Area * Velocity --> Velocity = Mdot/(rho*Area)
        self.Veloc_a = self.Mdot_a / (self.rho_a * self.A_a)
        
        #Determine q
        #q = mdot * cp * deltaT
        self.q_a = self.Mdot_a* self.cp_a * -(Th_out - Th_in)

        #Energy Balance: Q_water must equal Q_air
        self.q_w = self.q_a

        #Determine water Mdot
        #q = mdot * cp * deltaT
        self.Mdot_w = self.q_w / (cp_w * -(Tc_in - Tc_out))
        
        #Determine the Water Cross sectional Area 
        self.A_w = (pi*(Di_shell/2)**2)- pi*((Do_tube/2)**2)

        #Determin flow velocity of the water, from Mdot and Area
        #Rearrange Mdot = rho * Area * Velocity --> Velocity = Mdot/(rho*Area)
        self.Veloc_w = self.Mdot_w / (rho_w * self.A_w)
        
        #prevent cascading
        #self.Veloc_w = 1.71

        #Hydraulic Diameter (aka characteristic length)
        #D_h = (4*Af)/(Pflow) = 4*pi*(Di_shell^2 - Do_tube^2)/ 4*pi*(Di_shell - Do_tube) = Di_shell - Do_tube
        #D_e = (4*Af)/(PheatTransfer) = 4*pi*(Di_shell^2 - Do_tube^2)/ 4*pi* Do_tube = (Di_shell^2 - Do_tube^2)/Do_tube

        self.Da_h = Di_shell - Do_tube
        self.Da_e = (Di_shell**2 - Do_tube**2)/Do_tube
        self.Dw_h = Di_tube
        self.Dw_e = Di_tube
        
        #cascading errors
        #Da_h = 0.016082
        #Da_e = 0.039586
        #Dw_h = Di_tube
        #Dw_e = 0.03279
        
        #Determine the Reynolds Number
        #Re = velocity * hydraulic dimater / kinematic viscostiy   (general form for pipes)
        #Re = inertial forces/ viscous forces
        self.Re_a = self.Veloc_a*self.Da_h/self.kvisc_a
        
        self.Re_w = self.Veloc_w*self.Dw_h/kvisc_w

        #Re_w = 174215
 
        #Determine the Prandtl Number
        #Pr = viscous diffusion rate/ thermal diffusion rate = Cp * dyanamic viscosity / thermal conductivity
        #Pr << 1 means thermal diffusivity dominates
        #Pr >> 1 means momentum diffusivity dominates
        self.Pr_a = self.cp_a*self.dvisc_a/k_a
        self.Pr_w = cp_w*dvisc_w/k_w

        #Override Pr calculation based on better information @ 300 degree C 
        self.Pr_a = 0.68 #http://www.engineeringtoolbox.com/air-properties-d_156.html

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
        if ((self.Re_a >10000) and (self.Re_w > 10000) and (0.6 < self.Pr_a < 160) and (0.6 < self.Pr_w < 160)):
            print ""
            print "   Dittus-Boelter Equation Valid. Calculating Nusselt Number   "
        else:
            print ""
            print "!!!** Dittus-Boelter Equation not valid. Use alternate method  **!!!"

        self.Nu_a = 0.023*(self.Re_a**(4./5))*(self.Pr_a**0.4) #fluid is heated n=0.4
        self.Nu_w = 0.023*(self.Re_w**(4./5))*(self.Pr_w**0.3) #fluid is cooled n=0.3

        #Determine h
        # h = Nu * k/ D
        self.h_a = self.Nu_a*k_a/self.Da_e
        self.h_w = self.Nu_w*k_w/self.Dw_e

        #cascading
        #self.h_a = 1467.95
        #self.h_w = 8088.82

        #Determine Overall Heat Transfer Coefficient
        # U_o = 1 / [(Ao/Ai*hi)+(Ao*ln(ro/ri)/2*pi*k*L)+(1/ho)]
        # (simplified)
        # U_o = 1/ [(Do/Di*hi)+(Do*ln(Do/Di)/2*k)+(1/ho)]
        
        #print "Do_tube{} Di_tube{} self.h_a{} self.k_p{}  self.h_w{}".format(Do_tube,Di_tube, self.h_a, self.k_p, self.h_w)
        #Di_tube = 0.03279
        term1 = Do_tube/(Di_tube*self.h_w)
        term2 =  Do_tube*log((Do_tube/Di_tube),e)
        
        self.U_o = 1/ (term1+(term2/(2*k_p))+(1/self.h_a))

        #Assume fouling losses
        #lookup R_w, R_a
        self.U_oF = 1/ ((term1+(term2/(2*k_p))+(1/self.h_a))+(R_w+R_a))

        #--Determine LMTD--
        #if(coFlow):
            #dT1 = (Th_in - Tc_in) #Change in T1 (delta T1)
            #dT2 = (Th_out-Tc_out) #Change in T2 (delta T2)
        #else: #counter-flow
        dT1 = (Th_in - Tc_out) #Change in T1 (delta T1)
        dT2 = (Th_out-Tc_in) #Change in T2 (delta T2)

        self.LMTD = abs((dT1- dT2)/(log((dT1/dT2), e))) #take natural log (base e)

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
        
        #Assume pipe minor losses
        #function of length and number of passes
        #Head losses
        #Developed from Bernoulli eq, with zero velocity change and viscous terms included in apparent height
        # H = (k + f*(L/D)*v_avg^2)/2g
        # delP = rho*g*H
        # Also consider bends in tube
        

#run stand-alone component
if __name__ == "__main__":

    #this function is used for crude value comparisons (to test each calculation step versus a verified problem)
    def check(var_name,var,correct_val):
        #check('<variable_name>',<variable>,<correct value>)
        "Format and print the results of a value comparison, (crude tests for verification purposes)"
        error = (correct_val - var)/correct_val
        if (abs(error*100)<2): #determine percent error, if greater than 1%
            print "{}: {} ........{}%  --> {}!".format(var_name,var,abs(error)*100,"Test Passed")
        else: #comparison fails, print error output
            print " ===> {}: {} ........{}%  --> {} ?".format(var_name,var,abs(error)*100,"Test Failed :(")


    from openmdao.main.api import set_as_top
    test = HeatExchangerSizing()  
    set_as_top(test)
    print ""

    test.T_win = 288.1
    test.T_wout = 406.6
    test.T_ain = 791.
    test.T_aout = 338.4
    test.Mdot_a = 0.49
    test.N = 1

    test.run()

    #crude unit testing
    check('A_a',test.A_a, 0.0008444)
    check('Veloc_a',test.Veloc_a, 941.)
    check('q_a',test.q_a, 223104.)
    check('Mdot_w',test.Mdot_w, 0.449)
    check('A_w',test.A_w, 0.001086)
    check('Veloc_w',test.Veloc_w, 0.414)
    check('Da_h',test.Da_h, 0.016082)
    check('Da_e',test.Da_e, 0.039586)
    check('Dw_h',test.Dw_h, test.Di_tube)
    check('Dw_e',test.Dw_e, test.Di_tube)
    check('Re_a',test.Re_a, 966613)
    check('Re_w',test.Re_w, 41650)
    check('Pr_a',test.Pr_a, 0.68)
    check('Pr_w',test.Pr_w, 2.25)
    check('Nu_a',test.Nu_a, 1210.)
    check('Nu_w',test.Nu_w, 145.)
    check('h_a',test.h_a, 1387.989)
    check('h_w',test.h_w, 2570.589)
    check('U_o',test.U_o, 879.019)
    check('LMTD',test.LMTD, 164.28)
    if (test.N < 2): #only check single pass case
        check('L',test.L, 14.078)

    print "-----Completed Heat Exchanger Sizing---"
    print ""
    print "Heat Exchanger Length: {} meters, with {} tube pass(es)".format(test.L/2,test.N)
    
    #sqrt(#passes * tube area * packing factor)
    #assumes shell magically becomes rectangular but keeps packing factor
    packing_factor =  (test.A_a/(test.A_a + test.A_w)) + 1
    x = cu(((test.N * pi*((test.Do_tube/2)**2)*packing_factor)**0.5),'m','ft')
    y = 2*x #height of a double pass
 
    tot_vol = x*y * cu(test.L,'m','ft')
    
    print "Heat Exchanger Dimensions: {}ft (Length) x {}ft (Width) x {}ft (Height)".format(cu(test.L,'m','ft')/2,x,y)
    print "Heat Exchanger Volume: {} ft^3".format( tot_vol)