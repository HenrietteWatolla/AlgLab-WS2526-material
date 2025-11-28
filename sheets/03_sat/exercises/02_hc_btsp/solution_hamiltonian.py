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
        
        for v in graph.nodes():
            # get neighbors of the node
            neighbors = [self.var(v, w) for w in graph.neighbors(v)]
            no_neighbors = [-x for x in neighbors]
            # degree constraint
            self.solver.add_atmost(neighbors, 2)
            self.solver.add_atmost(no_neighbors, len(neighbors)-2)

    # function for fast access to the variables
    def var(self, v, w):
        return self.edge_map_vars[(min(v, w), max(v, w))]

    def solve(self) -> list[tuple[int, int]] | None:
        """
        Solves the Hamiltonian Cycle Problem. If a HC is found,
        its edges are returned as a list.
        If the graph has no HC, 'None' is returned.
        """
        # TODO: Implement me!

        # use the SAT-solver to find subtour that already accepts degree constraint
        while True:
            model = self.solver.solve()
            # no solution that accepts degree constraint
            if not model:
                return None
            
            model = self.solver.get_model()
            # get chosen edges --> only positive literals represent chosen edges
            chosen_edges = []
            for (v, w), var in self.edge_map_vars.items():
                if model[var - 1] > 0:
                    chosen_edges.append((v, w))

            # build graph from chosen edges
            self.subtour_graph = nx.Graph()
            self.subtour_graph.add_edges_from(chosen_edges)
            self.components = list(nx.connected_components(self.subtour_graph))

            # only one component --> this is the hamiltonian cycle
            if (len(self.components)) == 1 and (len(self.subtour_graph.nodes()) == len(self.graph.nodes())):
                return list(self.subtour_graph.edges())

            # more than one component --> add subtour elimination constraint iteratively
            # --> don't consider every possible subset of nodes at once --> exponential
            # better: add them incrementally (DFJ)
            for component in self.components:
                # find all edges that leaving the component
                edges_leaving = [
                    (v, w)
                    for v in component
                    for w in self.graph.nodes()
                    if w not in component and self.graph.has_edge(v, w)
                ]

                # isolated component --> the found subtours can't get connected
                if not edges_leaving:
                    return None
                
                # disjunctive clause --> at least one of the leaving edges must be chosen
                clause = ([self.var(v,w) for (v,w) in edges_leaving])
                self.solver.add_clause(clause)