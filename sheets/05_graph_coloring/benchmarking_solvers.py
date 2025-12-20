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
    def solve_all(self):
        # compute solver results for all instances once and store them
        data_rows = []

        # generate all instances only once
        self.all_instances = Instances.generate_test_instances()
        self.graph_classes = Instances.graph_classes()
        self.solvers = {
            #"Gurobi_ASS": lambda G, ub: GurobiASS.solve_coloring_ASS_gurobi(G, ub, 60),
            #"Gurobi_ASS_S": lambda G, ub: GurobiASS_S.solve_coloring_ASS_S_gurobi(G, ub, 60),
            "Gurobi_REP": lambda G, ub: GurobiREP.solve_coloring_REP_gurobi(G, ub, 60),

            #"CP_ASS": lambda G, ub: CP_SAT_ASS.solve_coloring_ASS_CP_SAT(G, ub, 60),
            #"CP_ASS_S": lambda G, ub: CP_SAT_ASS_S.solve_coloring_ASS_S_CP_SAT(G, ub, 60),
            "CP_REP": lambda G, ub: CP_SAT_REP.solve_coloring_REP_CP_SAT(G, ub, 60),
            #"CP_NEQ": lambda G, ub: CP_SAT_NOT_EQUAL.solve_coloring_not_equal_CP_SAT(G, ub, 60),
            #"CP_ALLDIFF": lambda G, ub: CP_SAT_ALL_DIFF.solve_coloring_all_diff_CP_SAT(G, ub, 60),

            #"SAT": lambda G, ub: SAT.solve_coloring_SAT(G, ub, 60),
        }

        for instance_name, G in self.all_instances:
            # compute upper bound once per instance
            ub = min(
                Heuristics.num_colors(Heuristics.dsatur_coloring(G)),
                Heuristics.num_colors(Heuristics.greedy_coloring(G, Heuristics.input_order(G))),
                Heuristics.num_colors(Heuristics.multi_start_greedy(G))
            )

            # run all solvers on the instance
            for solver_name, solver_fn in self.solvers.items():
                result = solver_fn(G, ub)
                data_rows.append({
                    "instance": instance_name,
                    "strategy": solver_name,
                    "metric": result
                })

        # store DataFrame for later plotting
        self.df_results = pd.DataFrame(data_rows)

        print(self.df_results.head(20))

    @classmethod
    def plot_per_graph_class(self):
        # plot performance profiles per graph class
        for class_name, names in self.graph_classes.items():
            df_class = self.df_results[self.df_results["instance"].isin(names)]
            if df_class.empty:
                continue

            Plots.plot_performance_profile(
                data = df_class,
                instance_column = "instance",
                strategy_column = "strategy",
                metric_column = "metric",
                direction = "min",          # smaller number of colors is better upper bound
                comparison = "relative",    # ratio to best-known solution
                highlight_best = True,      # bold dominant heuristic
                title = (f"Performance Profile: {class_name}")
            )

            plt.savefig(f"benchmarking_solvers_{class_name}.png", dpi=300)
            plt.close()

    @classmethod
    def plot_all_instances(self):
        # plot performance profile for all instances together

        Plots.plot_performance_profile(
                data = self.df_results,
                instance_column = "instance",
                strategy_column = "strategy",
                metric_column = "metric",
                direction = "min",          # smaller number of colors is better upper bound
                comparison = "relative",    # ratio to best-known solution
                highlight_best = True,      # bold dominant heuristic
                title = (f"Performance Profile: all instances")
            )

        plt.savefig(f"benchmarking_heuristics_all_instances.png", dpi=300)
        plt.close()

# generate the plots
if __name__ == "__main__":
    
    print("RUN BENCHMARKING OF SOLVERS")

    Benchmarking_Solvers.solve_all()
    Benchmarking_Solvers.plot_per_graph_class()
    Benchmarking_Solvers.plot_all_instances()

# try to do lower bound also directly