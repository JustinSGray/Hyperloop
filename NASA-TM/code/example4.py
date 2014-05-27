if __name__=="__main__":
    from collections import OrderedDict

    hl = HyperloopPod()
    #design variables
    hl.Mach_bypass = .95
    hl.Mach_pod_max = .7
    hl.Mach_c1_in = .65
    hl.c1_PR_des = 13

    #initial guesses
    hl.compress.W_in = .46
    hl.flow_limit.radius_tube = hl.pod.radius_tube_inner = 324
    hl.compress.Ts_tube = hl.flow_limit.Ts_tube \
        = hl.tube_wall_temp.tubeWallTemp = 322
    hl.compress.c2_PR_des = 5

    hl.run()

    design_data = OrderedDict([
        ('Mach bypass', hl.Mach_bypass),
        ('Max Travel Mach', hl.Mach_pod_max),
        ('Fan Face Mach', hl.Mach_c1_in),
        ('C1 PR', hl.c1_PR_des)
    ])

    output_data = OrderedDict([
        ('Radius Inlet Outer',  hl.pod.radius_inlet_back_outer),
        ('Radius Inlet Inner',  hl.pod.inlet.radius_back_inner),
        ('Tube Inner Radius', hl.flow_limit.radius_tube),
        ('Pod W', hl.compress.W_in),
        ('Compressor C2 PR', hl.compress.c2_PR_des),
        ('Pod Net Force', hl.pod.net_force),
        ('Pod Thrust', hl.compress.F_net),
        ('Pod Power', hl.compress.pwr_req),
        ('Total Energy', hl.pod.energy),
        ('Travel time', hl.mission.time),
        ('Max Speed', hl.compress.speed_max),
        ('Equilibirum Tube Temp', hl.tube_wall_temp.temp_boundary)
    ])

    def pretty_print(data):
        for label,value in data.iteritems():
            print '%s: %.2f'%(label,value)


    print "======================"
    print "Design"
    print "======================"
    pretty_print(design_data)

    print "======================"
    print "Performance"
    print "======================"
    pretty_print(output_data)