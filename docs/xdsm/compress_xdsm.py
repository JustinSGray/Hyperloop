from XDSM import XDSM

opt = 'Optimization'
dat = 'DataInter'
mda = 'MDA'
anl = 'Analysis'

x = XDSM()

names = ['assembly inputs', 'tube', 'inlet' , 'comp1', 'duct1', 'split', 'nozzle', 
         'comp2', 'duct2', 'perf', 'assembly outputs']
for name in names: 
    x.addComp(name, anl, name)

x.addDep('tube', 'assembly inputs', dat, '', stack=True)
x.addDep('inlet', 'assembly inputs', dat, '', stack=True)
x.addDep('comp1', 'assembly inputs', dat, '', stack=True)
x.addDep('split', 'assembly inputs', dat, '', stack=True)
x.addDep('comp2', 'assembly inputs', dat, '', stack=True)
x.addDep('perf', 'assembly inputs', dat, '', stack=True)

x.addDep('inlet', 'tube', dat, '', stack=True)
x.addDep('comp1', 'inlet', dat, '', stack=True)
x.addDep('duct1', 'comp1', dat, '', stack=True)
x.addDep('split', 'duct1', dat, '', stack=True)
x.addDep('nozzle', 'split', dat, '', stack=True)
x.addDep('comp2', 'split', dat, '', stack=True)
x.addDep('duct2', 'comp2', dat, '', stack=True)
x.addDep('perf', 'nozzle', dat, '', stack=True)
x.addDep('perf', 'comp2', dat, '', stack=True)
x.addDep('comp2', 'perf', dat, '', stack=True)
x.addDep('perf', 'inlet', dat, '', stack=True)
x.addDep('perf', 'comp1', dat, '', stack=True)


x.addDep('assembly outputs', 'tube', dat, '', stack=True)
x.addDep('assembly outputs', 'inlet', dat, '', stack=True)
x.addDep('assembly outputs', 'comp1', dat, '', stack=True)
x.addDep('assembly outputs', 'duct2', dat, '', stack=True)
x.addDep('assembly outputs', 'perf', dat, '', stack=True)

x.write('compress',True)
