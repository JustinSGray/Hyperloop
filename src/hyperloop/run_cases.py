import numpy as np
import pylab as p

def mvr(assembly):
    machs = []
    tube_r = []
    capsule_r = []

    for m in np.arange(.781,.95, .01):
        hl.Mach_pod_max = m
        hl.run()
        machs.append(m)
        tube_r.append(hl.pod.radius_inlet_back_outer)
        capsule_r.append(hl.flow_limit.radius_tube)

        print machs
        print tube_r
        print capsule_r

def mva(assembly):
    machs = []
    tubeA = []
    podA = []
    areaR = [] #area Ratio --> Tube/Pod


    for m in np.arange(.7,.95, .01):
        assembly.Mach_pod_max = m
        assembly.run()
        machs.append(m)
        tubeA.append(assembly.flow_limit._tube_area)
        podA.append(assembly.flow_limit._inlet_area)
        areaR.append(assembly.flow_limit._tube_area/assembly.flow_limit._inlet_area)
        print machs
        print tubeA
        print podA
        print areaR

def mvb(assembly):

    machs = []
    batt = []
    compE = []
    timeT = []

    for m in np.arange(.7,.95, .01):
        assembly.Mach_pod_max = m
        assembly.run()
        machs.append(m)
        batt.append(assembly.mission.energy)
        compE.append(assembly.mission.pwr_req)
        timeT.append(assembly.mission.time)
        print machs
        print batt
        print compE
        print timeT