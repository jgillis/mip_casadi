import casadi as ca
import pandas as pd
import numpy as np
import pickle
from multiprocessing import Process, Queue, freeze_support

def get_solvers(n_threads):
    yield ("gurobi", {"gurobi": {"threads": n_threads}})
    yield ("cbc", {"cbc": {"threads": n_threads}})
    
    # https://ergo-code.github.io/HiGHS/dev/parallel/
    if n_threads == 1:
        yield ('highs', {})  # Default serial
    else:
        kSimplexStrategyDualTasks = 2
        kSimplexStrategyDualMulti = 3
        yield ('highs', {
            "highs": {
                "simplex_strategy": kSimplexStrategyDualMulti,
                "simplex_min_concurrency": n_threads,
                "simplex_max_concurrency": n_threads,
                "threads": n_threads,
                "parallel": "on"
            }
        })

def task(queue, solver_name, solver_options, kwargs, problem):
    solver = ca.conic('solver', solver_name, {"a": kwargs["a"].sparsity()}, solver_options)
    sol = solver(lbx=kwargs["lbx"], ubx=kwargs["ubx"], lba=kwargs["lba"], uba=kwargs["uba"], a=kwargs["a"], g=kwargs["g"])
    if problem == "neos-860300":
        assert int(np.round(sol["cost"])) == 3201  # See https://plato.asu.edu/ftp/milp_res8/benchmark.cbc.8threads.7200s.res
    elif problem == "fome12":
        assert abs(float(sol["cost"]) - 4.506558419e+07) < 1
    stats = solver.stats()
    queue.put({"t_proc_solver": stats["t_proc_solver"], "t_wall_solver": stats["t_wall_solver"]})

def main():
    results = []

    for problem in ["fome12", "neos-860300"]:
        file_path = problem + ".pkl"

        kwargs = pickle.load(open(file_path, 'rb'))

        common_options = {"print_time": False}
        if "discrete" in kwargs:
            common_options["discrete"] = kwargs["discrete"]

        for n_threads in [1, 2, 4, 8]:
            for solver_name, solver_options in get_solvers(n_threads):
                options = dict(common_options)
                options.update(solver_options)

                # Run the solver in a different process (Highs has global state)
                queue = Queue()
                t = Process(target=task, args=(queue, solver_name, options, kwargs, problem))
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

    results_df.set_index(['solver', 'threads','problem'], inplace=True)

    # Get unique problems and solvers
    unique_problems = results_df.index.get_level_values('problem').unique()
    unique_solvers = results_df.index.get_level_values('solver').unique()

    # Dictionary to store the restructured data for each problem
    restructured_dfs = {}

    # Create a multi-level index for the rows
    multi_index = pd.MultiIndex.from_product([unique_solvers, ['wall', 'proc']], names=['solver', 'type'])

    for problem in unique_problems:
        # Create a temporary list to hold the data
        temp_data = []
        for solver in unique_solvers:
            for measure in ['wall', 'proc']:
                # Extract the series for the current solver and measure
                data_series = results_df.xs((solver, problem), level=('solver', 'problem'))[measure]
                temp_data.append(data_series.values)
        
        # Create a DataFrame from the temp_data with the new multi-level row index
        # and columns as the sorted unique threads
        problem_df = pd.DataFrame(temp_data, index=multi_index, columns=sorted(results_df.index.get_level_values('threads').unique()))

        # Store the DataFrame in the dictionary
        restructured_dfs[problem] = problem_df

    # Now you can print the DataFrames in the desired format
    for problem, df in restructured_dfs.items():
        print(f"\n{problem}\n")
        print(df)


# This is the important part for Windows compatibility:
if __name__ == '__main__':
    freeze_support()
    main()

