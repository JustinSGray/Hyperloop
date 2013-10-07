from XDSM import XDSM

opt = 'Optimization'
dat = 'DataInter'
mda = 'MDA'
anl = 'Analysis'

x = XDSM()
#x.addComp('driver', mda, 'Solver')
x.addComp('compress', anl, 'Compression')
x.addComp('mission', anl, 'Mission')
x.addComp('pod', anl, 'Pod Geom.')
x.addComp('flow_limit', anl, 'Tube Flow Limit')
x.addComp('tube_wall_temp', anl, 'Tube Wall Temp')

x.addDep('mission', 'compress', dat, '', stack=True)
x.addDep('pod', 'compress', dat, '', stack=True)
x.addDep('pod', 'mission', dat, '', stack=True)
x.addDep('flow_limit', 'pod', dat, '', stack=True)
x.addDep('tube_wall_temp', 'compress', dat, '', stack=True)

#reverse couplings
x.addDep('compress', 'flow_limit', dat, '', stack=True)
x.addDep('compress', 'tube_wall_temp', dat, '', stack=True)
x.addDep('compress', 'pod', dat, '', stack=True)

#x.addDep('compress','driver', dat, '$W_{in}$')


x.write('hyperloop',True)
