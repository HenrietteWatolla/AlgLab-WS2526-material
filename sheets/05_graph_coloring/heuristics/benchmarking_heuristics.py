from heuristics.heuristics import Heuristics
from instances.instances import Instances
from plot_generation import Plots

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class Benchmarking_Heuristics:

    heuristics = {
        "greedy": lambda G: Heuristics.greedy_coloring(G, Heuristics.input_order(G)),
        "multi_greedy": lambda G: Heuristics.multi_start_greedy(G, runs = 50, seed = 42),
        "dsatur": Heuristics.dsatur_coloring
    }

    all_instances = Instances.generate_test_instances()

    @classmethod
    def plot_per_graph_class(cls):
        for class_name, names in Instances.graph_classes().items():
            data_rows = []

            for instance_name, G in cls.all_instances:
                if instance_name not in names:
                    continue  # skip instances not in this class
                for h_name, f in cls.heuristics.items():
                    coloring = f(G)
                    data_rows.append({
                        "instance": instance_name,
                        "strategy": h_name,
                        "metric": Heuristics.num_colors(coloring)
                    })

            df_class = pd.DataFrame(data_rows)

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

            plt.savefig(f"benchmarking_heuristics_{class_name}.png", dpi=300)
            plt.close()

    @classmethod
    def plot_all_instances(cls):
        data_rows = []
        for i, (instance_name, G) in enumerate(Instances.generate_test_instances()):
            instance_id = instance_name
            for heuristic_name, f in cls.heuristics.items():
                coloring = f(G)
                data_rows.append({
                    "instance": instance_id,
                    "strategy": heuristic_name,
                    "metric": Heuristics.num_colors(coloring)
                })
        
        df = pd.DataFrame(data_rows)

        print(df.head(40))

        Plots.plot_performance_profile(
                data = df,
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
    print("RUN BENCHMARKING OF HEURISTICS")
    Benchmarking_Heuristics.plot_all_instances()
    Benchmarking_Heuristics.plot_per_graph_class()