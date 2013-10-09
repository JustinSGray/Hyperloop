from XDSM import XDSM

opt = 'Optimization'
dat = 'DataInter'
mda = 'MDA'
anl = 'Analysis'

x = XDSM()
#x.addComp('driver', mda, 'Solver')
x.addComp('assembly inputs', anl, 'assembly inputs')
x.addComp('compress', anl, 'compress')
x.addComp('mission', anl, 'mission')
x.addComp('pod', anl, 'pod')
x.addComp('flow_limit', anl, 'flow\_limit')
x.addComp('tube_wall_temp', anl, 'tube\_wall\_temp')

x.addDep('mission', 'compress', dat, '', stack=True)
x.addDep('pod', 'compress', dat, '', stack=True)
x.addDep('pod', 'mission', dat, '', stack=True)
x.addDep('flow_limit', 'pod', dat, '', stack=True)
x.addDep('tube_wall_temp', 'compress', dat, '', stack=True)

#reverse couplings
x.addDep('compress', 'flow_limit', dat, '', stack=True)
x.addDep('compress', 'tube_wall_temp', dat, '', stack=True)
x.addDep('compress', 'pod', dat, '', stack=True)

#assembly inputs
x.addDep('compress', 'assembly inputs', dat, '', stack=True)
x.addDep('mission', 'assembly inputs', dat, '', stack=True)
x.addDep('flow_limit', 'assembly inputs', dat, '', stack=True)
x.addDep('tube_wall_temp', 'assembly inputs', dat, '', stack=True)
x.addDep('pod', 'assembly inputs', dat, '', stack=True)


#x.addDep('compress','driver', dat, '$W_{in}$')


x.write('hyperloop',True)
