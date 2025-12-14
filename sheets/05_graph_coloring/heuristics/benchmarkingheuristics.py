from heuristics.heuristics import Heuristics
from instances.instances import Instances
from plot_generation import Plots

import pandas as pd

data_rows = []
heuristics = {
    "greedy": lambda G: Heuristics.greedy_coloring(G, Heuristics.input_order(G)),
    "degree_order": lambda G: Heuristics.greedy_coloring(G, Heuristics.highest_degree_order(G)),
    "multi_greedy": lambda G: Heuristics.multi_start_greedy(G, runs = 50, seed = 42),
    "dsatur": Heuristics.dsatur_coloring
}

for i, (name, G) in enumerate(Instances.generate_test_instances()):
    instance_id = name
    for name, f in heuristics.items():
        coloring = f(G)
        data_rows.append({
            "instance": instance_id,
            "strategy": name,
            "metric": Heuristics.num_colors(coloring)
        })

df = pd.DataFrame(data_rows)

Plots.plot_performance_profile(
    data=df,
    instance_column="instance",
    strategy_column="strategy",
    metric_column="metric",
    direction="min",          # smaller number of colors is better
    comparison="relative",    # ratio to best-known solution
    highlight_best=True,      # optional: bold the dominant heuristic
    title="Performance Profile of Graph Coloring Heuristics"
)