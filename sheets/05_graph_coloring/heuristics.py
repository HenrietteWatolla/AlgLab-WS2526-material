import networkx as nx
from typing import Dict, List
import random

# store coloring in a dict: keys = nodes, values = color indices
Coloring = Dict[int, int]

# helper function: returns smallest index of available colors
def smallest_available_color(used_colors: set[int]) -> int:
    color = 0
    while color in used_colors:
        color += 1
    return color

# greedy --> returns a upper bound for graph coloring
def greedy_coloring(graph: nx.Graph, order: List[int]) -> Coloring:

    coloring: Coloring = {}

    for v in order:
        # store colors already used by the neighbors
        used_colors = {
            coloring[u]
            for u in graph.neighbors(v)
            if u in coloring
        }

        # assign smallest available color to the obtained vertex
        coloring[v] = smallest_available_color(used_colors)

    return coloring

# different node orders
def input_order(graph: nx.Graph) -> List[int]:
    return list(graph.nodes())

def random_order(graph: nx.Graph, seed: int | None = None) -> List[int]:
    nodes = list(graph.nodes())
    randseq = random.Random(seed) # reproducible randomness, seed fix random sequence
    randseq.shuffle(nodes)
    return nodes

def highest_degree_order(graph: nx.Graph) -> List[int]:
    return sorted(
        graph.nodes(),
        key = lambda v: graph.degree(v),
        reverse = True
    )

def multi_start_greedy(graph: nx.Graph, runs: int = 50, seed: int | None = None) -> Coloring:
    best_coloring: Coloring | None = None
    min_colors = float("inf")

    randseq = random.Random(seed)

    # call greedy multiple times with random node order, save smallest found color number
    for i in range(runs):
        order = list(graph.nodes())
        randseq.shuffle(order)

        coloring = greedy_coloring(graph, order)
        k = num_colors(coloring)

        if k < min_colors:
            best_coloring = coloring
            min_colors = k

    return best_coloring

# get saturation degree of vertices
def saturation_degree(graph: nx.Graph, vertex: int, coloring: dict[int, int]) -> int:
    saturation_degree = len({coloring[u] for u in graph.neighbors(vertex) if u in coloring})
    return saturation_degree

# DSATUR --> chooses node next to color dynamically, highest saturation degree first
def dsatur_coloring(graph: nx.Graph) -> dict[int, int]:
    coloring: dict[int, int] = {}
    uncolored = set(graph.nodes())

    # precompute initial degrees
    degree = dict(graph.degree())

    while uncolored:
        # choose vertex with highest saturation degree, break ties by initial degree
        v = max(
            uncolored,
            key = lambda x: (
                saturation_degree(graph, x, coloring),
                degree[x]
            )
        )

        # assign smallest available color
        used_colors = {
            coloring[u]
            for u in graph.neighbors(v)
            if u in coloring
        }
        coloring[v] = smallest_available_color(used_colors)

        uncolored.remove(v)

    return coloring

# count number of used colors
def num_colors(coloring: Coloring) -> int:
    return max(coloring.values()) + 1 if coloring else 0

# test
if __name__ == "__main__":
    for seed in range(5):

        G = erdosThree = nx.erdos_renyi_graph(30, 0.5, seed = 42)

        print(
            seed,
            num_colors(greedy_coloring(G, input_order(G))),
            num_colors(greedy_coloring(G, highest_degree_order(G))),
            num_colors(multi_start_greedy(G, runs=100, seed=seed)),
            num_colors(dsatur_coloring(G))
        )

