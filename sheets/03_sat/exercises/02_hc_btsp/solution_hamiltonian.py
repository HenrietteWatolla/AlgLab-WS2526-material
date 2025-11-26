import itertools

import networkx as nx
from pysat.solvers import Solver as SATSolver


class HamiltonianCycleModel:
    def __init__(self, graph: nx.Graph) -> None:
        self.graph = graph
        self.solver = SATSolver("Minicard")
        self.assumptions = []
        # TODO: Implement me!

        # mapping of edges and variable indices
        self.edge_map_vars = {}
        self.var_counter = 1  # start variable IDs at 1
        for v, w in self.graph.edges():
            key = (min(v, w), max(v, w))
            self.edge_map_vars[key] = self.var_counter
            self.var_counter += 1
        
        # function for fast access to the variables
        def var(v, w):
            return self.edge_map_vars[(min(v, w), max(v, w))]
        
        # get neighbors of the nodes
        self.neighbors = [var(v, w) for w in graph.neighbors(v)]
        self.no_neighbors = [-x for x in self.neighbors]
        
        # degree constraint
        self.solver.add_atmost(self.neighbors, 2)
        self.solver.add_atmost(self.no_neighbors, len(self.neighbors)-2)

        # subtour elimination constraint
        # --> dont consider every possible subset of nodes at once --> exponential
        # better: add them incrementally (DFJ)
        for component in nx.connected_components(self.graph):
            # find all edges that leaving the component
            edges_leaving = [
                (v, w)
                for v in component
                for w in self.graph.nodes()
                if w not in component and self.graph.has_edge(v, w)
            ]
            # disjunctive clause --> at least one of the leaving edges must be chosen
            self.solver.add_clause([var(v,w) for (v,w) in edges_leaving])


        self.subgraphs = [self.graph.subgraph(c).copy() for c in nx.connected_components(self.graph)]


    def solve(self) -> list[tuple[int, int]] | None:
        """
        Solves the Hamiltonian Cycle Problem. If a HC is found,
        its edges are returned as a list.
        If the graph has no HC, 'None' is returned.
        """
        # TODO: Implement me!

        # special case: graph is not connected
        if len(self.subgraphs) > 1:
            return None