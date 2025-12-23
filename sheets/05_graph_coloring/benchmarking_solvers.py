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

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Benchmarking_Solvers:

    output_file = "benchmark_results_preprocessing.csv"

    def_results = None

    @classmethod
    def solve_all(cls, preprocessing = False):

        if os.path.exists(Benchmarking_Solvers.output_file):
            cls.df_results = pd.read_csv(Benchmarking_Solvers.output_file)
            completed = set(
                zip(cls.df_results["instance"], cls.df_results["strategy"])
            )
            write_header = False
        else:
            cls.df_results = pd.DataFrame()
            completed = set()
            write_header = True

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

        instance_counter = 0

        # compute solver results for all instances once and store them
        for instance_name, G in cls.all_instances:

            # track instance number
            instance_counter += 1

            # compute upper bound once per instance
            ub = min(
                Heuristics.num_colors(Heuristics.dsatur_coloring(G)),
                Heuristics.num_colors(Heuristics.greedy_coloring(G, Heuristics.input_order(G))),
                Heuristics.num_colors(Heuristics.multi_start_greedy(G))
            )

            # run all solvers on the instance
            for solver_name, solver_fn in active_solvers.items():

                # skip already solven instances
                if (instance_name, solver_name) in completed:
                    continue

                print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA ", instance_counter, solver_name)

                result = solver_fn(G, ub)

                lower_bound = result["LB"]
                best_solution = result["objective"]
                
                row = ({
                    "instance": instance_name,
                    "strategy": solver_name,
                    "objective": best_solution,
                    "LB": lower_bound,
                    "instance_number": instance_counter
                })

                # write row immediately to CSV if memory runs out of space and interrupts solving process
                df_row = pd.DataFrame([row])

                df_row.to_csv(
                    Benchmarking_Solvers.output_file,
                    mode = "a", # append mode
                    header = write_header,
                    index = False
                )

                write_header = False
                completed.add((instance_name, solver_name))

        # store DataFrame and load it for later plotting

        Benchmarking_Solvers.df_results = pd.read_csv(Benchmarking_Solvers.output_file)
        print("DONE. Rows:", len(Benchmarking_Solvers.df_results))
        print("QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ", Benchmarking_Solvers.df_results.head(36))
        

    @classmethod
    def plot_per_graph_class_objective(cls):
        # plot performance profiles per graph class
        for class_name, names in cls.graph_classes.items():
            df_class = cls.df_results[cls.df_results["instance"].isin(names)]
            if df_class.empty:
                continue

            Plots.plot_performance_profile(
                data = df_class,
                instance_column = "instance",
                strategy_column = "strategy",
                metric_column = "objective",
                direction = "min",          # smaller number of colors is better upper bound
                comparison = "absolute",    # ratio to best-known solution
                highlight_best = True,      # bold dominant solver
                title = (f"Performance Profile: best solution found for {class_name} with preprocessing")
            )

            plt.savefig(f"benchmarking_solvers_best_solution_found_{class_name}_pre_absolute.png", dpi=300)
            plt.close()

    @classmethod
    def plot_all_instances_objective(cls):
        # plot performance profile for all instances together

        df_class = cls.df_results
                                  
        Plots.plot_performance_profile(
                data = df_class,
                instance_column = "instance",
                strategy_column = "strategy",
                metric_column = "objective",
                direction = "min",          # smaller number of colors is better upper bound
                comparison = "absolute",    # ratio to best-known solution
                highlight_best = True,      # bold dominant solver
                title = (f"Performance Profile: best solution found for all instances with preprocessing")
            )

        plt.savefig(f"benchmarking_solvers_best_solution_found_all_instances_pre_absolute.png", dpi=300)
        plt.close()

    @classmethod
    def plot_per_graph_class_lower_bound(cls):
        # plot performance profiles per graph class
        for class_name, names in cls.graph_classes.items():
            df_class = cls.df_results[cls.df_results["instance"].isin(names)]
            if df_class.empty:
                continue

            Plots.plot_performance_profile(
                data = df_class,
                instance_column = "instance",
                strategy_column = "strategy",
                metric_column = "LB",
                direction = "max",          # greater number of colors is better lower bound
                comparison = "absolute",    # ratio to best-known solution
                highlight_best = True,      # bold dominant solver
                title = (f"Performance Profile: lower bound for {class_name} with preprocessing")
            )

            plt.savefig(f"benchmarking_solvers_lower_bound_{class_name}_pre_absolute.png", dpi=300)
            plt.close()

    @classmethod
    def plot_all_instances_lower_bound(cls):
        # plot performance profile for all instances together

        df_class = cls.df_results
        
        Plots.plot_performance_profile(
                data = df_class,
                instance_column = "instance",
                strategy_column = "strategy",
                metric_column = "LB",
                direction = "max",          # greater number of colors is better lower bound
                comparison = "absolute",    # ratio to best-known solution
                highlight_best = True,      # bold dominant solver
                title = (f"Performance Profile: lower bound for all instances with preprocessing")
            )

        plt.savefig(f"benchmarking_solvers_lower_bound_all_instances_pre_absolute.png", dpi=300)
        plt.close()
    
    # preprocessing = pipeline (solver remains untouched)
    def solve_with_preprocessing(solver_fn):
        def wrapped_solver(G, ub):
            pre = DegreeBasedPreprocessor(G.copy())
            G_reduced = pre.preprocess()

            # solve reduced graph
            result = solver_fn(G_reduced, ub)

            # reconstruct solution
            coloring, ub, lb = pre.postprocess(
                result["coloring"],
                result["LB"]
            )

            result["coloring"] = coloring
            result["best_bound"] = lb
            return result

        return wrapped_solver

# generate the plots
if __name__ == "__main__":
    
    print("RUN BENCHMARKING OF SOLVERS")
    
    """
    # no preprocessing
    Benchmarking_Solvers.solve_all(preprocessing = False)
    Benchmarking_Solvers.plot_per_graph_class_objective()
    Benchmarking_Solvers.plot_all_instances_objective()
    Benchmarking_Solvers.plot_per_graph_class_lower_bound()
    Benchmarking_Solvers.plot_all_instances_lower_bound()
    """
    
    # with preprocessing
    Benchmarking_Solvers.solve_all(preprocessing = True)
    Benchmarking_Solvers.plot_per_graph_class_objective()
    Benchmarking_Solvers.plot_all_instances_objective()
    Benchmarking_Solvers.plot_per_graph_class_lower_bound()
    Benchmarking_Solvers.plot_all_instances_lower_bound()