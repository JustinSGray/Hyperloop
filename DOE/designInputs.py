"""
    designInputs.py - 
        Input Variables = designInputsTree, mechVarsTree, noiseVarsTree, envelopeVarsTree
        Output Variables = flopsTree, anoppTree
        
        Contains top level design variables and default values for the NPSS cycle model
"""

#OpenMDAO Imports
from openmdao.main.api import VariableTree
from openmdao.lib.datatypes.api import Float, Array, Str
#numpy
from numpy import array
import numpy
from numpy import float as numpy_float


class designInputsTree(VariableTree):
    """Default design variables."""
    #Key Cycle Design variables
    tube_Pt = Float(99.0/0.5282, units="Pa", iotype='out')  #tube total pressure
    capsule_MN = Float(1., iotype='out')     				#capsule Mach number
    bearing_Pt = Float(11000., units="Pa", iotype='out')    #air pad total pressure
    Qdot_1 = Float(-250969.3, units="BTU/hr", iotype='out') #heat out from first heat exchange (convert to watts 1000 BTU/hr --> 293.071 Watts)
    Qdot_2 = Float(-25466.5 , units="BTU/hr", iotype='out') #heat out from second heat exchange
    waterPump_PR = Float(2300., iotype='out') 			    #water pump (heat exchanger) pressure ratio
    capsule_BPR = Float(1.45, iotype='out') 			    #nozzle to air bearing BPR
	tube_BPR = Float(2.2285, iotype='out')			        #capsule to tube BPR
    fanFace_MN = Float(2200., iotype='out')   		        #Mach number at the fan face
	
    #Key Cycle Output variables
    netPower = Float(247., units="kW", iotype='out')        #total energy delta [battery output - (compressor + heat exchanger)]... amount of power released to air as heat
    waterFlowRate = Float(0.39, units="kg/s", iotype='out') #water flow rate in heat exchanger
	
    #Assumed Variables
    delHeatVap_Water = Float(2260, units="kJ/kg", iotype='out')#heat of vaporization for water  (at 1atm)
    bearingWdot = Float(200., units="kg/s", iotype='out')   #bearing air flow rate
    bearingArea =Float(0, units="m^2", iotype='out')        # total air pad area
    inletBC = Float(5000., iotype='out')       			    #inlet boundary condition
    nozzleBC = Float(22572., iotype='out')   			    #nozzle boundary condition
	inletArea = Float(5000., units="m^2", iotype='out')     #inlet area
    nozzleArea = Float(22572., units="m^2", iotype='out')   #nozzle area