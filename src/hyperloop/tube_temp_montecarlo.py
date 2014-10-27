import os
import time

import numpy as np

from openmdao.main.api import Assembly
from openmdao.lib.drivers.api import CaseIteratorDriver
from openmdao.lib.casehandlers.api import BSONCaseRecorder

from hyperloop_sim import HyperloopPod

class HyperloopMonteCarlo(Assembly): 

    def configure(self): 

        driver = self.add('driver', CaseIteratorDriver())
        self.add('hyperloop', HyperloopPod())

        driver.add_parameter('hyperloop.temp_outside_ambient')
        driver.add_parameter('hyperloop.solar_insolation')
        driver.add_parameter('hyperloop.surface_reflectance')
        driver.add_parameter('hyperloop.num_pods')
        driver.add_parameter('hyperloop.emissivity_tube')
        driver.add_parameter('hyperloop.Nu_multiplier')
        driver.add_parameter('hyperloop.compressor_adiabatic_eff')

        driver.add_response('hyperloop.temp_boundary')
        driver.add_response('hyperloop.radius_tube_outer')

        N_SAMPLES = 10
        driver.case_inputs.hyperloop.temp_outside_ambient = np.random.normal(305,10,N_SAMPLES)        
        driver.case_inputs.hyperloop.solar_insolation = np.random.triangular(200,1000,1000,N_SAMPLES); #left, mode, right, samples
        driver.case_inputs.hyperloop.surface_reflectance = np.random.triangular(0.5,0.7,1,N_SAMPLES);
        driver.case_inputs.hyperloop.num_pods = np.random.normal(34,2,N_SAMPLES);
        driver.case_inputs.hyperloop.emissivity_tube = np.random.triangular(0.4,0.4,0.9,N_SAMPLES);
        driver.case_inputs.hyperloop.Nu_multiplier = np.random.triangular(0.9,1,3,N_SAMPLES);
        driver.case_inputs.hyperloop.compressor_adiabatic_eff = np.random.triangular(0.6,0.69,0.8,N_SAMPLES);

        # driver.case_inputs.hyperloop.temp_outside_ambient = np.random.normal(305,10,N_SAMPLES)        
        # driver.case_inputs.hyperloop.solar_insolation = np.random.triangular(500,1000,1000,N_SAMPLES); #left, mode, right, samples
        # driver.case_inputs.hyperloop.surface_reflectance = np.random.triangular(0.7,0.85,1,N_SAMPLES);
        # driver.case_inputs.hyperloop.num_pods = np.random.normal(34,2,N_SAMPLES);
        # driver.case_inputs.hyperloop.emissivity_tube = np.random.triangular(0.4,0.4,0.6,N_SAMPLES);
        # driver.case_inputs.hyperloop.Nu_multiplier = np.random.triangular(0.9,1,3,N_SAMPLES);
        # driver.case_inputs.hyperloop.compressor_adiabatic_eff = np.random.triangular(0.6,0.69,0.8,N_SAMPLES);



        timestamp = time.strftime("%Y%m%d%H%M%S")
        self.recorders = [BSONCaseRecorder('therm_mc_%s.bson'%timestamp)]



if __name__ == "__main__": 

    hl_mc = HyperloopMonteCarlo()

    #parameters
    hl_mc.hyperloop.Mach_bypass = .95
    hl_mc.hyperloop.Mach_pod_max = .8
    hl_mc.hyperloop.Mach_c1_in = .65
    hl_mc.hyperloop.c1_PR_des = 13

    #initial guesses
    hl_mc.hyperloop.compress.W_in = .38
    hl_mc.hyperloop.flow_limit.radius_tube = hl_mc.hyperloop.pod.radius_tube_inner = 243
    hl_mc.hyperloop.compress.Ts_tube = hl_mc.hyperloop.flow_limit.Ts_tube = hl_mc.hyperloop.tube_wall_temp.tubeWallTemp = 322.28
    hl_mc.hyperloop.compress.c2_PR_des = 8.72

    #initial run to converge things
    hl_mc.run()


