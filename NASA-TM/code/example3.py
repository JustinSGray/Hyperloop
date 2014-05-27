#Add Solver
solver = self.add('solver',BroydenSolver())
solver.itmax = 50 #max iterations
solver.tol = .001
#Add Parameters and Constraints
solver.add_parameter('compress.W_in',low=-1e15,high=1e15)
solver.add_parameter('compress.c2_PR_des', low=-1e15, high=1e15)
solver.add_parameter(['compress.Ts_tube','flow_limit.Ts_tube',
	'tube_wall_temp.temp_boundary'], low=-1e-15, high=1e15)
solver.add_parameter(['flow_limit.radius_tube', 'pod.radius_tube_inner']
	, low=-1e15, high=1e15)

solver.add_constraint('.01*(compress.W_in-flow_limit.W_excess) = 0')
solver.add_constraint('compress.Ps_bearing_residual=0')
solver.add_constraint('tube_wall_temp.ss_temp_residual=0')
solver.add_constraint('.01*(pod.area_compressor_bypass-compress.area_c1_out)=0')

driver = self.driver
driver.workflow.add('solver')
driver.recorders = [CSVCaseRecorder(filename="hyperloop.csv")]#record only converged
driver.printvars = ['Mach_bypass', 'Mach_pod_max', 'Mach_c1_in', 
					'c1_PR_des', 'pod.radius_inlet_back_outer',
                    'pod.inlet.radius_back_inner', 'flow_limit.radius_tube',
                    'compress.W_in', 'compress.c2_PR_des', 'pod.net_force', 
                    'compress.F_net','compress.pwr_req','pod.energy','mission.time',
                    'compress.speed_max', 'tube_wall_temp.temp_boundary']

#Declare Solver Workflow
solver.workflow.add(['compress','mission','pod','flow_limit','tube_wall_temp'])