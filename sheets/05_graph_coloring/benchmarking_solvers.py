from heuristics.heuristics import Heuristics
from instances.instances import Instances
from plot_generation import Plots

from cp_sat.solution_ass import CP_SAT_ASS
from cp_sat.solution_ass_s import CP_SAT_ASS_S
from cp_sat.solution_cp_all_diff import CP_SAT_ALL_DIFF
from cp_sat.solution_cp_not_equal import CP_SAT_NOT_EQUAL
from cp_sat.solution_rep import CP_SAT_REP

from gurobi.solution_rep import GurobiREP
from gurobi.solution_ass import GurobiASS
from gurobi.solution_ass_s import GurobiASS_S

from sat.solution_sat import SAT

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Benchmarking_Solvers:

    @classmethod
    def plot_per_graph_class(cls):
        for class_name, names in Instances.graph_classes().items():
            data_rows = []

            for instance_name, G in cls.all_instances:
                if instance_name not in names:
                    continue  # skip instances not in this class
                for solver_name, solver_fn in cls.solvers.items():
                    ub = min(
                        Heuristics.num_colors(Heuristics.dsatur_coloring(G)),
                        Heuristics.num_colors(Heuristics.greedy_coloring(G, Heuristics.input_order(G))),
                        Heuristics.num_colors(Heuristics.multi_start_greedy(G))
                    )
                    result = solver_fn(G, ub)
                    data_rows.append({
                        "instance": instance_name,
                        "strategy": solver_name,
                        "metric": result
                    })

            df_class = pd.DataFrame(data_rows)

            # test
            print(df_class.head(20))

            Plots.plot_performance_profile(
                data = df_class,
                instance_column = "instance",
                strategy_column = "strategy",
                metric_column = "metric",
                direction = "min",          # smaller number of colors is better upper bound
                comparison = "absolute",    # ratio to best-known solution
                highlight_best = True,      # bold dominant heuristic
                title = (f"Performance Profile: {class_name}")
            )

            plt.savefig(f"benchmarking_solvers_{class_name}.png", dpi=300)
            plt.close()

    @classmethod
    def plot_all_instances(cls):
        data_rows = []
        for i, (instance_name, G) in enumerate(Instances.generate_test_instances()):

            for solver_name, solver_fn in cls.solvers.items():
                ub = min(
                    Heuristics.num_colors(Heuristics.dsatur_coloring(G)),
                    Heuristics.num_colors(Heuristics.greedy_coloring(G, Heuristics.input_order(G))),
                    Heuristics.num_colors(Heuristics.multi_start_greedy(G))
                )
                result = solver_fn(G, ub)
                data_rows.append({
                    "instance": instance_name,
                    "strategy": solver_name,
                    "metric": result
                })
        
        df_class = pd.DataFrame(data_rows)

        print(df_class.head(40))

        Plots.plot_performance_profile(
                data = df_class,
                instance_column = "instance",
                strategy_column = "strategy",
                metric_column = "metric",
                direction = "min",          # smaller number of colors is better upper bound
                comparison = "absolute",    # ratio to best-known solution
                highlight_best = True,      # bold dominant heuristic
                title = (f"Performance Profile: all instances")
            )

        plt.savefig(f"benchmarking_heuristics_all_instances.png", dpi=300)
        plt.close()

# generate the plots
if __name__ == "__main__":

    all_instances = list(Instances.generate_test_instances())

    solvers = {
        "Gurobi_ASS": lambda G, ub: GurobiASS.solve_coloring_ASS_gurobi(G, ub, 60),
        "Gurobi_ASS_S": lambda G, ub: GurobiASS_S.solve_coloring_ASS_S_gurobi(G, ub, 60),
        "Gurobi_REP": lambda G, ub: GurobiREP.solve_coloring_REP_gurobi(G, ub, 60),

        "CP_ASS": lambda G, ub: CP_SAT_ASS.solve_coloring_ASS_CP_SAT(G, ub, 60),
        "CP_ASS_S": lambda G, ub: CP_SAT_ASS_S.solve_coloring_ASS_S_CP_SAT(G, ub, 60),
        "CP_REP": lambda G, ub: CP_SAT_REP.solve_coloring_REP_CP_SAT(G, ub, 60),
        "CP_NEQ": lambda G, ub: CP_SAT_NOT_EQUAL.solve_coloring_not_equal_CP_SAT(G, ub, 60),
        "CP_ALLDIFF": lambda G, ub: CP_SAT_ALL_DIFF.solve_coloring_all_diff_CP_SAT(G, ub, 60),

        "SAT": lambda G, ub: SAT.solve_coloring_SAT(G, ub, 60),
    }
    
    print("RUN BENCHMARKING OF SOLVERS")
    Benchmarking_Solvers.plot_per_graph_class()
    Benchmarking_Solvers.plot_all_instances()

# try to do lower bound also directly