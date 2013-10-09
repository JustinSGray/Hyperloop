from XDSM import XDSM

opt = 'Optimization'
dat = 'DataInter'
mda = 'MDA'
anl = 'Analysis'

x = XDSM()

name = 'assembly inputs'
x.addComp(name, anl, name)
name = 'capsule'
x.addComp(name, anl, name)
name = 'tube'
x.addComp(name, anl, name)
name = 'battery'
x.addComp(name, anl, name)
name = 'inlet'
x.addComp(name, anl, name)
name = 'aero'
x.addComp(name, anl, name)
name = 'assembly outputs'
x.addComp(name, anl, name)

x.addDep('inlet', 'assembly inputs', dat, '', stack=True)
x.addDep('aero', 'assembly inputs', dat, '', stack=True)
x.addDep('battery', 'assembly inputs', dat, '', stack=True)
x.addDep('tube', 'assembly inputs', dat, '', stack=True)

x.addDep('inlet', 'capsule', dat, '', stack=True)
x.addDep('battery', 'capsule', dat, '', stack=True)
x.addDep('assembly outputs', 'capsule', dat, '', stack=True)

x.addDep('assembly outputs', 'inlet', dat, '', stack=True)
x.addDep('aero', 'inlet', dat, '', stack=True)

x.addDep('assembly outputs', 'aero', dat, '', stack=True)

x.addDep('assembly outputs', 'battery', dat, '', stack=True)

x.write('pod',True)
