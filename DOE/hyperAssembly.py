"""
    hyperAssembly.py - 
        In support of the open-source Hyperloop transit project

		This openMDAO assembly wraps NPSS and runs a basic DOE
		
		-hyperAssembly.py		[top level DOE assembly]
		-npssCases.py			[NPSS component wrapper]
		-designInputs.py		[design input variable tree]
		-./cycle/				[folder containing NPSS model]
			-hyper.run			[model and run commands]
			-hyper.view_page	[output viewer]
			-hyper.viewOut		[actual ouptut]

    Compatible with OpenMDAO v0.8.1
	Compatible with NPSS v25D2_VC10??
"""
#Python Imports
import os.path
import os
from os import mkdir
from subprocess import call
#OpenMDAO Imports
from openmdao.main.api import Assembly, Component, VariableTree, set_as_top, create_io_traits
from openmdao.lib.drivers.api import DOEdriver
from openmdao.lib.doegenerators.api import FullFactorial
from openmdao.lib.casehandlers.api import ListCaseRecorder, CSVCaseRecorder, DumpCaseRecorder
from openmdao.lib.datatypes.api import Float, Array, File, Slot, VarTree
from npsscomponent import NPSScomponent
#External File Imports
from designInputs import designInputsTree
from npssCases import DesignCase
        
class varAssign(Component):
    """variable assignment"""
	
    designInputs = VarTree(designInputsTree(), iotype='in') 
    def __init__(self):
        super(varAssign, self).__init__() 
        #Do Nothing
    
    def execute(self):
        #override variable values here
		#redirect files
		#unit conversions?
        self.folderTree.DOE_myOutdirectoryL0= "OutputDOE"
        if not os.path.exists(self.folderTree.DOE_myOutdirectoryL0):
            os.mkdir(self.folderTree.DOE_myOutdirectoryL0)
        
        self.folderTree.DOE_myOutfileName = os.sep+ "VCE_"+str(self.designInputs.T3_opLimit)+"_"+str(self.designInputs.FanPR_des)+"_"+str(self.designInputs.OPR_des)+"_"+str(self.designInputs.T4_des)+"_"+str(self.designInputs.VCEBPR_des)
        self.folderTree.DOE_myOutdirectoryL1=self.folderTree.DOE_myOutdirectoryL0 + os.sep + "Outfolder_"+str(self.designInputs.T3_opLimit)+"_"+str(self.designInputs.VCEBPR_des)
        self.folderTree.DOE_myOutdirectoryL2=self.folderTree.DOE_myOutdirectoryL1+self.folderTree.DOE_myOutfileName 
        self.fileTree.FLOPSformatName =pth+"_FLOPSeng.txt"
        self.fileTree.indepPageName=pth+"_indeps.output"
        self.fileTree.noisePageName=pth+"_Noise.output"
        self.fileTree.ESTformatName=pth+"_NoiseEST.output"
        self.fileTree.WATEPageName=pth+"_WATE.output" 
        self.fileTree.WATEDiskName=pth+"_diskpage.output"
        self.fileTree.WATEVSPName=pth+"_VSP.xml"
        self.fileTree.WATECostName=pth+"_AutodataCost.output"
        self.fileTree.myOutfileName=  self.folderTree.DOE_myOutfileName + os.sep
        self.fileTree.myOutdirectoryL2=  self.folderTree.DOE_myOutdirectoryL2
		
class hyperTop(Assembly):
    """ Hyperloop Top level Assembly. """
    
    def configure(self):
        super(VCE_top, self).configure()
        #--------------------------Component Setup-----------------------------------
        self.add('varAssign',varAssign()) #variable Assignment imported from designInputs.py
        self.add('NPSS', DesignCase()) #imported from npssCases.py

        #---------------------------DOE Setup----------------------------------------
        self.add('driver',DOEdriver())
        self.driver.add_parameter(('varAssign.designInputs.T3_opLimit','NPSS_MDP.T3_opLimit'), low=1960., high=1960.) #low=1760., high=1960.)
        self.driver.add_parameter(('varAssign.designInputs.FanPR_des','NPSS_MDP.FanPR_des'), low=3.7, high=3.7) #low=2.8, high=4.6
        self.driver.add_parameter(('varAssign.designInputs.OPR_des','NPSS_MDP.OPR_des'), low=45., high=45.) #low=36., high=48.
        self.driver.add_parameter(('varAssign.designInputs.T4_des','NPSS_MDP.T4_opLimit'), low=3560., high=3560.) #low=2910., high=3510
        
        self.driver.DOEgenerator = FullFactorial(num_levels=1)#7

        #------------------------Case Recorders Setup--------------------------------
        #outfile = open('test_jeff.txt','w')
        #self.driver.recorders = [CSVCaseRecorder(filename='DOEoutdata.csv'), DumpCaseRecorder(outfile)] 
        ##other options DBCase,ListCaseRecorder
        
        #self.driver.printvars = ['designInputs.*']
        #self.driver.recorders[0].num_backups = 0   #save backup copies of previous runs (dated)
        
        #-------------------------- Assembly Setup ----------------------------------
        # Assembly Workflow
        self.driver.workflow.add(['varAssign','NPSS_MDP','flopsWrap','anoppWrap'])#,'NPSS_CycleDeck'])

        ## Assembly Connections
        #varAssign --> NPSS
        for vars in self.varAssign.designInputsTree.list_vars(): #loop through all file name variables and connect them
            self.connect('varAssign.designInputsTree.'+vars,'NPSS.'+vars)
        
        #--------------------------------------------------------------------------
        #    Workflow        
        # ____________            ____________  
        #|            |          |            |
        #| Var Assign | -------> |    NPSS    |
        #|____________|			 |____________|
        #           
        #--------------------------------------------------------------------------
if __name__ == '__main__':
    
    top = hyperTop()
    
    top.run()
    
    print 'EIFile read from: ' + top.varAssign.fileTree.FLOPSformatName
    print 'Range: ' + str(top.flopsWrap.range)

    #for case in top.driver.recorders[0].get_iterator():
    #    print "T3_opLimit: %f"%(case['designInputs.T3_opLimit'])
    


