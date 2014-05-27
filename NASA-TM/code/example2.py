def configure(self):

    #Add Components
    compress = self.add('compress', CompressionSystem())
    mission = self.add('mission', Mission())
    pod = self.add('pod', Pod())
    flow_limit = self.add('flow_limit', TubeLimitFlow())
    tube_wall_temp = self.add('tube_wall_temp', TubeWallTemp())

    #Boundary Input Connections
    #Hyperloop -> Compress
    self.connect('Mach_pod_max', 'compress.Mach_pod_max')
    self.connect('Mach_c1_in','compress.Mach_c1_in') #Design Variable
    #Hyperloop -> Mission
    self.connect('tube_length', 'mission.tube_length')
    self.connect('pwr_marg','mission.pwr_marg')
    #Hyperloop -> Pod
    #...

    #Inter-component Connections
    #Compress -> Mission
    self.connect('compress.speed_max', 'mission.speed_max')
    #Compress -> Pod
    self.connect('compress.area_c1_in', 'pod.area_inlet_out')
    self.connect('compress.area_inlet_in', 'pod.area_inlet_in')

    #.. Add Boundary outputs...so on and so forth