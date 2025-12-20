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

from preprocessing import DegreeBasedPreprocessor

import networkx as nx

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Benchmarking_Solvers:

    @classmethod
    def solve_all(cls, preprocessing = False):
        # compute solver results for all instances once and store them
        data_rows = []

        # generate all instances only once
        cls.all_instances = Instances.generate_test_instances()
        cls.graph_classes = Instances.graph_classes()

        cls.solvers = {

            "Gurobi_ASS": lambda G, ub: GurobiASS.solve_coloring_ASS_gurobi(G, ub, 60),
            "Gurobi_ASS_S": lambda G, ub: GurobiASS_S.solve_coloring_ASS_S_gurobi(G, ub, 60),
            "Gurobi_REP": lambda G, ub: GurobiREP.solve_coloring_REP_gurobi(G, ub, 60),

            "CP_ASS": lambda G, ub: CP_SAT_ASS.solve_coloring_ASS_CP_SAT(G, ub, 60),
            "CP_ASS_S": lambda G, ub: CP_SAT_ASS_S.solve_coloring_ASS_S_CP_SAT(G, ub, 60),
            "CP_REP": lambda G, ub: CP_SAT_REP.solve_coloring_REP_CP_SAT(G, ub, 60),
            "CP_NEQ": lambda G, ub: CP_SAT_NOT_EQUAL.solve_coloring_not_equal_CP_SAT(G, ub, 60),
            "CP_ALLDIFF": lambda G, ub: CP_SAT_ALL_DIFF.solve_coloring_all_diff_CP_SAT(G, ub, 60),

            "SAT": lambda G, ub: SAT.solve_coloring_SAT(G, ub, 60)
        }

        cls.solvers_with_preprocessing = {
            
            "Gurobi_ASS-PRE": Benchmarking_Solvers.solve_with_preprocessing(
                lambda G, ub: GurobiASS.solve_coloring_ASS_gurobi(G, ub, 60)),

            "Gurobi_ASS_S+PRE": Benchmarking_Solvers.solve_with_preprocessing(
                lambda G, ub: GurobiASS_S.solve_coloring_ASS_S_gurobi(G, ub, 60)),

            "Gurobi_REP+PRE": Benchmarking_Solvers.solve_with_preprocessing(
                lambda G, ub: GurobiREP.solve_coloring_REP_gurobi(G, ub, 60)),

            "CP_ASS+PRE": Benchmarking_Solvers.solve_with_preprocessing(
                lambda G, ub: CP_SAT_ASS.solve_coloring_ASS_CP_SAT(G, ub, 60)),

            "CP_ASS_S+PRE": Benchmarking_Solvers.solve_with_preprocessing(
                lambda G, ub: CP_SAT_ASS_S.solve_coloring_ASS_S_CP_SAT(G, ub, 60)),

            "CP_REP+PRE": Benchmarking_Solvers.solve_with_preprocessing(
                lambda G, ub: CP_SAT_REP.solve_coloring_REP_CP_SAT(G, ub, 60)),
            
            "CP_NEQ+PRE": Benchmarking_Solvers.solve_with_preprocessing(
                lambda G, ub: CP_SAT_NOT_EQUAL.solve_coloring_not_equal_CP_SAT(G, ub, 60)),

            "CP_ALLDIFF+PRE": Benchmarking_Solvers.solve_with_preprocessing(
                lambda G, ub: CP_SAT_ALL_DIFF.solve_coloring_all_diff_CP_SAT(G, ub, 60)),

            "SAT+PRE": Benchmarking_Solvers.solve_with_preprocessing(
                lambda G, ub: SAT.solve_coloring_SAT(G, ub, 60))
        }

        if preprocessing:
            active_solvers = cls.solvers_with_preprocessing
        else:
            active_solvers = cls.solvers

        for instance_name, G in cls.all_instances:
            # compute upper bound once per instance
            ub = min(
                Heuristics.num_colors(Heuristics.dsatur_coloring(G)),
                Heuristics.num_colors(Heuristics.greedy_coloring(G, Heuristics.input_order(G))),
                Heuristics.num_colors(Heuristics.multi_start_greedy(G))
            )

            clique_lb = nx.large_clique_size(G)

            # run all solvers on the instance
            for solver_name, solver_fn in active_solvers.items():
                result = solver_fn(G, ub)
                data_rows.append({
                    "instance": instance_name,
                    "strategy": solver_name,
                    "UB": result["objective"],
                    "LB": clique_lb,
                    "runtime": result["runtime"]
                })

        # store DataFrame for later plotting
        cls.df_results = pd.DataFrame(data_rows)
        print("DONE. Rows:", len(cls.df_results))

        print(cls.df_results.head(20))

    @classmethod
    def plot_per_graph_class(cls):
        # plot performance profiles per graph class
        for class_name, names in cls.graph_classes.items():
            df_class = cls.df_results[cls.df_results["instance"].isin(names)]
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
    def plot_all_instances(cls):
        # plot performance profile for all instances together

        Plots.plot_performance_profile(
                data = cls.df_results,
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
    
    # preprocessing = pipeline (solver remains untouched)
    def solve_with_preprocessing(solver_fn):
        def wrapped_solver(G, ub):
            pre = DegreeBasedPreprocessor(G.copy())
            G_reduced = pre.preprocess()

            # solve reduced graph
            result = solver_fn(G_reduced, ub)

            # reconstruct solution
            coloring, lb = pre.postprocess(
                result["coloring"],
                result.get("best_bound", 0)
            )

            result["coloring"] = coloring
            result["best_bound"] = lb
            return result

        return wrapped_solver

# generate the plots
if __name__ == "__main__":
    
    print("RUN BENCHMARKING OF SOLVERS")

    # no preprocessing
    Benchmarking_Solvers.solve_all(preprocessing = False)
    Benchmarking_Solvers.plot_per_graph_class()
    Benchmarking_Solvers.plot_all_instances()

    # preprocessing
    Benchmarking_Solvers.solve_all(preprocessing = True)
    Benchmarking_Solvers.plot_per_graph_class()
    Benchmarking_Solvers.plot_all_instances()