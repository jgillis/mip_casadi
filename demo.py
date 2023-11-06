import casadi as ca
import pandas as pd
import numpy as np




def get_solvers(n_threads):
    yield ("gurobi",{"gurobi":{"threads": n_threads}})
    yield ("cbc",{"cbc":{"threads": n_threads}})
    
    # https://ergo-code.github.io/HiGHS/dev/parallel/: The MIP solver has been written with parallel tree seach in mind, and it is hoped that this will be implemented before the end of 2024. 
    if n_threads==1:
        yield ('highs',{}) # Default serial
    else:
        kSimplexStrategyDualTasks = 2
        kSimplexStrategyDualMulti = 3
        yield ('highs',{"highs": {"simplex_strategy": kSimplexStrategyDualMulti,"simplex_min_concurrency":n_threads,"simplex_max_concurrency":n_threads,"threads": n_threads,"parallel":"on"}})

results = []

for problem in ["fome12","neos-860300"]:
    file_path = problem + ".pkl"

    import pickle
    kwargs = pickle.load(open(file_path,'rb'))
    
    common_options = {"print_time":False}
    if "discrete" in kwargs:
        common_options["discrete"] = kwargs["discrete"]

    for n_threads in [1,2,4,8]:
        for solver_name,solver_options in get_solvers(n_threads):
            options = dict(common_options)
            options.update(solver_options)
            
            
            # Run the solver in a different process (Highs has global state)
            from multiprocessing import Process, Queue
            queue = Queue()
            def task(queue):
                solver = ca.conic('solver',solver_name,{"a":kwargs["a"].sparsity()},options)
                sol = solver(lbx=kwargs["lbx"],ubx=kwargs["ubx"],lba=kwargs["lba"],uba=kwargs["uba"],a=kwargs["a"],g=kwargs["g"])
                if problem=="neos-860300":
                    assert int(np.round(sol["cost"]))==3201 # See https://plato.asu.edu/ftp/milp_res8/benchmark.cbc.8threads.7200s.res
                elif problem=="fome12":
                    assert abs(float(sol["cost"])-4.506558419e+07)<1
                stats = solver.stats()
                queue.put({"t_proc_solver": stats["t_proc_solver"], "t_wall_solver": stats["t_wall_solver"]})
            t = Process(target=task,args=(queue,))
            t.start()
            t.join()
            stats = queue.get()
            
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
