"""
    npssCases.py - 
        Contains NPSS component wrappers for the Hyperloop Design case      
"""
#OpenMDAO Imports
from openmdao.main.api import Component, create_io_traits
from openmdao.lib.datatypes.api import Float, Array, File, Slot, VarTree, Str
from npsscomponent import NPSScomponent
#External File Imports
#from designInputs import designInputsTree

class DesignCase(NPSScomponent):
    """This class runs the NPSS Hyperloop Design Case"""
    
    #Key Cycle Design variables
    #tube_Pt = Float(99.0/0.5282, units="Pa", iotype='in')  #tube total pressure
    capsule_MN = Float(1., iotype='in')                    #capsule Mach number
    bearing_Pt = Float(11000., units="Pa", iotype='in')    #air pad total pressure
    Qdot_1 = Float(-250969.3,  iotype='in') #heat out from first heat exchange (convert to watts 1000 BTU/hr --> 293.071 Watts)
    Qdot_2 = Float(-25466.5 ,  iotype='in') #heat out from second heat exchange
    waterPump_PR = Float(8., iotype='in')                  #water pump (heat exchanger) pressure ratio
    capsule_BPR = Float(1.45, iotype='in')                 #nozzle to air bearing BPR
    tube_BPR = Float(2.2285, iotype='in')                  #capsule to tube BPR
    fanFace_MN = Float(0.6, iotype='in')               #Mach number at the fan face

    #Assumed Variables
    delHeatVap_Water = Float(2260, units="kJ/kg", iotype='in')#heat of vaporization for water  (at 1atm)
    bearingWdot = Float(200., units="kg/s", iotype='in')      #bearing air flow rate
    bearingArea =Float(0,  iotype='in')           # total air pad area
    inletBC = Float(5000., iotype='in')                       #inlet boundary condition
    nozzleBC = Float(22572., iotype='in')                     #nozzle boundary condition
    inletArea = Float(5000.,  iotype='in')        #inlet area
    nozzleArea = Float(22572.,iotype='in')      #nozzle area

    #Key Cycle Output variables
    netPower = Float(247., units="kW", iotype='out')        #total energy delta [battery output - (compressor + heat exchanger)]... amount of power released to air as heat
    waterFlowRate = Float(0.39, units="kg/s", iotype='out') #water flow rate in heat exchanger
    
    def __init__(self):
        self.force_execute = True

        includes = [ #include the following directories
            #'-iclodfirst',
            '-I', '.\cycle',
            ]

        myArglist = []
        myArglist.extend(includes)
        myArglist.append('.\cycle\hyper.run') #insert NPSS model here
        
        super(DesignCase, self).__init__(arglist=myArglist) 
        #self.external_files.append(FileMetadata(path=os.path.join(model_dir, 'hyper.run'), input=True, constant=True))

    def configure(self):
        super(DesignCase, self).configure() #this needs to be first
        self.run_command = 'run();'
        #self.reload_flag = 'hyperReload'

        ##generate list of tuples as inputs for every variable in designInputs                     
        #create_io_traits(self, [("designIpnuts." + str(vars), str(vars)) for vars in self.designInputs.list_vars()], iotype='in') #promote NPSS variables and give alias (2nd argument in tuple)
                            #Pass from openMDAO to NPSS

        #varAssign --> NPSS
        #for vars in self.varAssign.designInputsTree.list_vars(): #loop through all file name variables and connect them
        #    self.connect('varAssign.designInputsTree.'+vars,'NPSS.'+vars)

        create_io_traits(self, ["tube.Pt",
                                ], iotype='in')
        create_io_traits(self,[ #(Actual Variable Name, OpenMDAO alias) 
                                #Promote as openMDAO output variables
                                ("nozzle.Fl_O.Pt","nozzle_Pt"),
                                ("nozzle.Fl_O.W","nozzle_W")
                                ], iotype='out')
        
    def execute(self): #trace the NPSS component with print statements before and after execution
        print self.get_pathname(), '--NPSS design execution begins--'
       
        super(DesignCase, self).execute()
                
        print "Nozzle Pt: %s (Pa)" %self.nozzle_Pt
        print "Nozzle W: %s (kg/s)" %self.nozzle_W

        print self.get_pathname(), '--NPSS design execution complete!--'