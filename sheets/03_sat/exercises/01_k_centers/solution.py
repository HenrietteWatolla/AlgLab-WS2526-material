import bisect
import logging
import math
from typing import Iterable

import networkx as nx
from pysat.solvers import Gluecard4 as SATSolver

import time


logging.basicConfig(level=logging.INFO)

# Define the node ID type. It is an integer but this helps to make the code more readable.
NodeId = int


class Distances:
    """
    This class provides a convenient interface to query distances between nodes in a graph.
    All distances are precomputed and stored in a dictionary, making lookups efficient.
    """

    def __init__(self, graph: nx.Graph) -> None:
        self.graph = graph
        self._distances = dict(nx.all_pairs_dijkstra_path_length(self.graph))

    def all_vertices(self) -> Iterable[NodeId]:
        """Returns an iterable of all node IDs in the graph."""
        return self._distances.keys()

    def dist(self, u: NodeId, v: NodeId) -> float:
        """Returns the distance between nodes `u` and `v`."""
        return self._distances[u].get(v, math.inf)

    def max_dist(self, centers: Iterable[NodeId]) -> float:
        """Returns the maximum distance from any node to the closest center."""
        return max(min(self.dist(c, u) for c in centers) for u in self.all_vertices())

    def vertices_in_range(self, u: NodeId, limit: float) -> Iterable[NodeId]:
        """Returns an iterable of nodes within `limit` distance from node `u`."""
        return (v for v, d in self._distances[u].items() if d <= limit)

    def sorted_distances(self) -> list[float]:
        """Returns a sorted list of all pairwise distances in the graph."""
        return sorted(
            dist
            for dist_dict in self._distances.values()
            for dist in dist_dict.values()
        )


class KCenterDecisionVariant:
    
    def __init__(self, distances: Distances, k: int) -> None:
        self.distances = distances
        # TODO: Implement me!

        # Solution model
        self.k = k
        self.nodes = list(self.distances.all_vertices())

        # mapping of nodes and variable indices
        self.nodes_map_vars = {node: index for index, node in enumerate(self.nodes, start = 1)}

        self.solver = SATSolver()
        
        #self.vars = [self.nodes_map_vars[node] for node in self.nodes]

        # at most k nodes can be chosen
        self.solver.add_atmost(list(self.nodes_map_vars.values()), k)

        self._infeasible = False
        self._solution: list[NodeId] | None = None
        
    def limit_distance(self, limit: float) -> None:
        """Adds constraints to the SAT solver to ensure coverage within the given distance."""
        logging.info("Limiting to distance: %f", limit)
        # TODO: Implement me!

        self._infeasible = False

        # per vertex at least one chosen center has to be in given limit --> OR-constraint
        for v in self.nodes:
            # find nodes in given distance
            reachable = list(self.distances.vertices_in_range(v, limit))

            # no center can cover v within limit --> instance infeasible
            if not reachable:
                self._infeasible = True
                return
            
            # OR-Constraint
            clause = [self.nodes_map_vars[u] for u in reachable]
            self.solver.add_clause(clause)


    def solve(self) -> list[NodeId] | None:
        """Solves the SAT problem and returns the list of selected nodes, if feasible."""
        # TODO: Implement me!

        if getattr(self, "_infeasible", False):
            return None

        if not self.solver.solve():
            return None
        
        model = self.solver.get_model()
        model_set = set(model)
        chosen_centers = []

        for node, var in self.nodes_map_vars.items():
            if var in model_set:
                chosen_centers.append(node)

        self._solution = chosen_centers
        return self._solution

    def get_solution(self) -> list[NodeId]:
        """Returns the solution if available; raises an error otherwise."""
        if self._solution is None:
            msg = "No solution available. Ensure `solve` is called first."
            raise ValueError(msg)
        return self._solution



class KCentersSolver:
    def __init__(self, graph: nx.Graph) -> None:
        """
        Creates a solver for the k-centers problem on the given networkx graph.
        The graph may not be complete, and edge weights are used to represent distances.
        """
        self.graph = graph

        # TODO: Implement me!
        self.distances = Distances(self.graph)
        self.candidates = self.distances.sorted_distances()
        self.nodes = list(self.distances.all_vertices())

    def solve_heur(self, k: int) -> list[NodeId]:
        """
        Calculate a heuristic solution to the k-centers problem.
        Returns the k selected centers as a list of node IDs.
        """
        # TODO: Implement me!

        # special cases --> no nodes or less than k nodes in graph
        if not self.nodes:
            return []
        if k >= len(self.nodes):
            return list(self.nodes)

        # choose arbitrary node as first center
        centers = []
        centers.append(self.nodes[0])

        # distance from each node to the chosen center
        # start with distance to the first center
        nearest = {v: self.distances.dist(v, centers[0]) for v in self.nodes}

        # choose more centers as long as the cardinality constraint is valid    
        while len(centers) < k:
            # next center is node that is as far away as possible from centers already chosen
            farthest = max(self.nodes, key=lambda u: nearest[u])
            centers.append(farthest)
            # update nearest distances using the new center
            for v in self.nodes:
                d = self.distances.dist(v, farthest)
                if d < nearest[v]:
                    nearest[v] = d

        return centers


    def solve(self, k: int) -> list[NodeId]:
        """
        Calculate the optimal solution to the k-centers problem for the given k.
        Returns the selected centers as a list of node IDs.
        """
        # Start with a heuristic solution --> this is upper bound
        heuristic_centers = self.solve_heur(k)
        upper_bound = self.distances.max_dist(heuristic_centers)

        # TODO: Implement me!

        # candidates in list
        candidates = []
        for c in self.candidates:
            if c < upper_bound:
                candidates.append(c)
        candidates.sort()

        # heuristic solution is best one
        if not candidates:
            return heuristic_centers
        
        # implement binary search, because sequential was not fast enough
        left = 0
        right = len(candidates) - 1

        best_solution = heuristic_centers
        best_value = upper_bound

        # binary search is more efficient here, but just do it to a fitting accuracy
        while left <= (right-(left/100)):
            middle = (left + right) // 2

            # create a fresh decision instance for the middle
            decision = KCenterDecisionVariant(self.distances, k)
            decision.limit_distance(candidates[middle])

            # bottleneck
            sol = decision.solve()

            # test if value is possible
            # --> update best solution + search for smaller distances
            if sol is not None:
                best_solution = sol
                right = middle - 1
            else:
                left = middle + 1
        
        # at one point, go further sequentially
        # --> here this is not necessary anymore, because the accuracy of the binary search solution is already enough
        """
        for c in candidates[left:right+1]:
            decision = KCenterDecisionVariant(self.distances, k)
            decision.limit_distance(c)
            sol = decision.solve()
            # found smallest = best solution
            if sol is not None:
                best_solution = sol
            # not yet feasible
            else:
                break
        """

        return best_solution