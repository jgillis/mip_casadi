import casadi as ca
import pandas as pd
import numpy as np




def get_solvers(n_threads):
    #yield ("gurobi",{"gurobi":{"threads": n_threads}})
    yield ("cbc",{"cbc":{"threads": n_threads}})
    
    kSimplexStrategyDualTasks = 2
    yield ('highs',{"highs": {"simplex_strategy": kSimplexStrategyDualTasks,"simplex_min_concurrency":n_threads,"simplex_max_concurrency":n_threads,"threads": n_threads,"parallel":"on"}})

results = []

for problem in ["neos-860300","fome12"]:
    file_path = problem + ".pkl"

    import pickle
    kwargs = pickle.load(open(file_path,'rb'))
    
    common_options = {"discrete": kwargs["discrete"],"print_time":False}

    for n_threads in [1,2,4,8]:
        for solver_name,solver_options in get_solvers(n_threads):
            options = dict(common_options)
            options.update(solver_options)
            
            solver = ca.conic('solver',solver_name,{"a":kwargs["a"].sparsity()},options)
            
            sol = solver(lbx=kwargs["lbx"],ubx=kwargs["ubx"],lba=kwargs["lba"],uba=kwargs["uba"],a=kwargs["a"],g=kwargs["g"])
            
            assert int(np.round(sol["cost"]))==3201 # See https://plato.asu.edu/ftp/milp_res8/benchmark.cbc.8threads.7200s.res
            
            stats = solver.stats()
            print(stats)
            
            results.append({
                "solver": solver_name,
                "threads": n_threads,
                "proc": stats['t_proc_solver'],
                "wall": stats['t_wall_solver'],
                "problem": problem
            })

results_df = pd.DataFrame(results)

results_df.set_index(['solver', 'threads'], inplace=True)

print(results_df)
