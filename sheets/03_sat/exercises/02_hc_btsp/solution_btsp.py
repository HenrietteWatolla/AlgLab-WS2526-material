import math
from enum import Enum

import networkx as nx
from _timer import Timer
from solution_hamiltonian import HamiltonianCycleModel
import time

class SearchStrategy(Enum):
    """
    Different search strategies for the solver.
    """

    SEQUENTIAL_UP = 1  # Try smallest possible k first.
    SEQUENTIAL_DOWN = 2  # Try any improvement.
    BINARY_SEARCH = 3  # Try a binary search for the optimal k.

    def __str__(self):
        return self.name.title()

    @staticmethod
    def from_str(s: str):
        return SearchStrategy[s.upper()]


class BottleneckTSPSolver:
    def __init__(self, graph: nx.Graph) -> None:
        """
        Creates a solver for the Bottleneck Traveling Salesman Problem on the given networkx graph.
        You can assume that the input graph is complete, so all nodes are neighbors.
        The distance between two neighboring nodes is a numeric value (int / float), saved as
        an edge data parameter called "weight".
        There are multiple ways to access this data, and networkx also implements
        several algorithms that automatically make use of this value.
        Check the networkx documentation for more information!
        """
        self.graph = graph
        # TODO: Implement me!
        # only edge weights can give a valid solution for maximal single traveling time
        self.candidates = [self.graph.edges[e]["weight"] for e in self.graph.edges()]
        self.candidates.sort()

    def lower_bound(self) -> float:
        # TODO: Implement me!
        # exact as many edges as nodes in the graph are used for hamiltonian cycle
        # --> lower bound is at least n'th smallest edge weight
        nodes = len(self.graph.nodes())
        self.minimal_index = nodes - 1
        return self.candidates[self.minimal_index]

    def optimize_bottleneck(
        self,
        time_limit: float = math.inf,
        search_strategy: SearchStrategy = SearchStrategy.BINARY_SEARCH,
    ) -> list[tuple[int, int]] | None:
        """
        Find the optimal bottleneck tsp tour.
        """
        self.timer = Timer(time_limit)
        # TODO: Implement me!

        # init binary search
        left = (len(self.graph.nodes())) - 1
        right = len(self.candidates) - 1
        shortest_edge_weight = self.candidates[len(self.candidates) - 1]
        best_solution = None

        # binary search
        while left <= right:
            middle = (left + right) // 2
            candidate_weight = self.candidates[middle]
            
            # build subgraph with edges <= candidate_weight only
            self.subgraph = nx.Graph()
            for v, w, data in self.graph.edges(data = True):
                if data["weight"] <= candidate_weight:
                    self.subgraph.add_edge(v, w)
            
            model = HamiltonianCycleModel(self.subgraph)
                    
            # try to find Hamiltonian cycle in builded subgraph
            solution = model.solve()

            if solution is not None:
                # Hamiltonian cycle exists
                best_solution = solution
                shortest_edge_weight = candidate_weight
                # try smaller edge weight, because hamiltonian cycle could be possible with less edges
                right = middle - 1
            else:
                # more (heavier) edges necessary to make a hamiltonian cycle possible
                left = middle + 1
                
        return best_solution