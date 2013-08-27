"""
    hyperAssembly.py - 
        In support of the open-source Hyperloop transit project

        This openMDAO assembly wraps NPSS and runs a basic DOE
        
        -hyperAssembly.py       [top level DOE assembly]
        -npssCases.py           [NPSS component wrapper]
        -./cycle/               [folder containing NPSS model]
            -hyper.run          [model and run commands]
            -hyper.view_page    [output viewer]
            -hyper.viewOut      [actual ouptut]

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
from openmdao.lib.datatypes.api import Float, Array, File, Slot, VarTree, Str
from npsscomponent import NPSScomponent
#External File Imports
from npssCases import DesignCase

class hyperTop(Assembly):
    """ Hyperloop Top level Assembly. """
    
    def configure(self):
        super(hyperTop, self).configure()
        #--------------------------Component Setup-----------------------------------
        
        self.add('NPSS', DesignCase()) #imported from npssCases.py

        #---------------------------DOE Setup----------------------------------------
        self.add('driver',DOEdriver())
        self.driver.add_parameter('NPSS.tube_Pt', low=99.0/0.5282, high=300.) #low=1760., high=1960.)
        self.driver.add_parameter('NPSS.capsule_MN', low=0.6, high=1.) #low=1760., high=1960.)
        self.driver.add_parameter('NPSS.bearing_Pt', low=11000., high=12000.) #low=1760., high=1960.)
        
        self.driver.DOEgenerator = FullFactorial(num_levels=1)

        #------------------------Case Recorders Setup--------------------------------
        #outfile = open('test_jeff.txt','w')
        #self.driver.recorders = [CSVCaseRecorder(filename='DOEoutdata.csv'), DumpCaseRecorder(outfile)] 
        ##other options DBCase,ListCaseRecorder
        
        #self.driver.printvars = ['designInputs.*']
        #self.driver.recorders[0].num_backups = 0   #save backup copies of previous runs (dated)
        
        #-------------------------- Assembly Setup ----------------------------------
        # Assembly Workflow
        self.driver.workflow.add(['NPSS'])#

        # Assembly Connections

        
if __name__ == '__main__':
    
    top = hyperTop()
    top.run()
    
    print 'Total Power to Air: ' + str(top.NPSS.netPower)
    print 'Water Flow Rate: ' + str(top.NPSS.waterFlowRate)

    #for case in top.driver.recorders[0].get_iterator():
    #    print "T3_opLimit: %f"%(case['designInputs.T3_opLimit'])
    


