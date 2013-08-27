"""
    npssCases.py - 
        Contains NPSS component wrappers for the Hyperloop Design case
        
"""
#OpenMDAO Imports
from openmdao.main.api import Component, create_io_traits
from openmdao.lib.datatypes.api import Float, Array, File, Slot
from npsscomponent import NPSScomponent
#External File Imports
from designInputs import designInputsTree

class DesignCase(NPSScomponent):
    """This class runs the NPSS Hyperloop Design Case"""
    
    #totWt = Float(iotype='out') #total engine weight (bareWt + wtacc)
    #bareWt = Float(iotype='out')
    
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
        create_io_traits(self, [("designInputs.tube_Pt","tube_Pt"),
                                ("designInputs.capsule_MN","capsule_MN"),
                                ("designInputs.bearing_Pt","bearing_Pt"),
                                ("designInputs.waterPump_PR","waterPump_PR")
								], iotype='in')
        create_io_traits(self,[ #(Actual Variable Name, OpenMDAO alias) 
                                #Promote as openMDAO output variables
                                ("nozzle.Fl_O.Pt","nozzle_Pt"),
								("nozzle.Fl_O.W","nozzle_W")
                                ], iotype='out')
        
    def execute(self): #trace the NPSS component with print statements before and after execution
        print self.get_pathname(), '--NPSS design execution begins--'
       
        super(DesignCase, self).execute()
        
        #self.bareWt = (self.inletWt - self.engMountWt)
        #self.weng = (self.bareWt+self.wtacc)
        
        print "Total Power: %s (kW)" %self.V1
        print "Water Flow Rate: %s (kg/s)" %self.waterFlowRate

        print self.get_pathname(), '--NPSS design execution complete!--'