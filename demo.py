import casadi as ca

file_path = "neos-860300.pkl"


# Solved with DiveCoefficient: mas76 binkar10_1

import pickle
kwargs = pickle.load(open(file_path,'rb'))


#solver = ca.conic('solver','cbc',{"a":kwargs["a"].sparsity()},{"cbc":{"threads":0},"discrete": kwargs["discrete"],"print_time":True})


solver = ca.conic('solver','highs',{"a":kwargs["a"].sparsity()},{"discrete": kwargs["discrete"],"print_time":True})


sol = solver(lbx=kwargs["lbx"],ubx=kwargs["ubx"],lba=kwargs["lba"],uba=kwargs["uba"],a=kwargs["a"],g=kwargs["g"])

assert sol["cost"]==3201 # See https://plato.asu.edu/ftp/milp_res8/benchmark.cbc.8threads.7200s.res

stats = solver.stats()

print(stats["t_proc_total"],stats["t_wall_total"])
#print(stats[""])
