"""
Implement the Dantzig-Fulkerson-Johnson formulation for the TSP.
"""

import logging
import typing

import gurobipy as gp
import networkx as nx
from gurobipy import GRB


class GurobiTspRelaxationSolver:
    """
    IMPLEMENT ME!
    """

    def __init__(self, G: nx.Graph, k: int = 2):
        """
        G is a weighted networkx graph, where the weight of an edge is stored in the
        "weight" attribute. It is strictly positive.
        """
        self.graph = G
        self.k = k
        assert (
            G.number_of_edges() == G.number_of_nodes() * (G.number_of_nodes() - 1) / 2
        ), "Invalid graph"
        assert all(
            weight > 0
            for _, _, weight in G.edges.data("weight", default=None)  # type: ignore[attr-defined]
        ), "Invalid graph"
        assert k in {1, 2}, "Invalid k"
        logging.info("Creating model ...")
        logging.info(
            "Graph has %d nodes and %d edges", G.number_of_nodes(), G.number_of_edges()
        )
        logging.info("Implementing subtour elimination with >= %d", k)
        self._model = gp.Model()
        # TODO: Implement me! --> use most from previous task

        # create continuous variables for every edge (0 <= x <= 1)
        # consider ordering, because of non directed graph to avoid several variables for the same edge
        edges = G.edges()
        self._vars = {}
        for (u, v) in edges:
            x, y = (u, v) if u < v else (v, u)
            self._vars[(x, y)] = self._model.addVar(vtype = GRB.CONTINUOUS, name = f"edge_{u}_{v}", lb = 0, ub = 1)

        # objective function --> minimize total costs of the tour
        self._model.setObjective(gp.quicksum(self._vars[(u, v) if u < v else (v, u)] * G[u][v]["weight"]
                                             for u, v in edges), GRB.MINIMIZE)

        # find incident edges per vertex
        neighbors = {node: [] for node in G.nodes()}
        for (u, v) in self._vars.keys():
            neighbors[u].append((u, v))
            neighbors[v].append((u, v))

        # degree constraint
        for v in G.nodes():
            self._model.addConstr(
                (gp.quicksum(self._vars[edge] for edge in neighbors[v]) == 2)
            )

    def get_lower_bound(self) -> float:
        """
        Return the current lower bound.
        """
        # TODO: Implement me!
        # use value of Linear Relaxation as lower bound
        return self._model.ObjVal

    def get_solution(self) -> typing.Optional[nx.Graph]:
        """
        Return the current solution as a graph.

        The solution should be a networkx Graph were the
        fractional value of the edge is stored in the "x" attribute.
        You do not have to add edges with x=0.

        ```python
        graph = nx.Graph()
        graph.add_edge(0, 1, x=0.5)
        graph.add_edge(1, 2, x=1.0)
        ```
        """
        # TODO: Implement me!
        return self._sol_graph

    def get_objective(self) -> typing.Optional[float]:
        """
        Return the objective value of the last solution.
        """
        # TODO: Implement me!
        if self._model.status == GRB.OPTIMAL:
            return self._model.ObjVal

    def solve(self) -> None:
        """
        Solve the model. After solving the model, the solution, its objective value,
        and the lower bounds should be available via the corresponding methods.
        """
        logging.info("Solving model ...")
        # Set parameters for the solver.
        self._model.Params.LogToConsole = 1

        # TODO: Implement me!

        while True:

            # optimize model initially
            self._model.optimize()

            # build graph from solution values >= 0.01
            selected_graph = nx.Graph()
            selected_graph.add_nodes_from(self.graph.nodes())
            for edge, var in self._vars.items():
                value = var.X  # value in current best solution
                if value >= 0.01:
                    (u, v) = edge
                    selected_graph.add_edge(u, v, x = value)

            # identify subtours
            components = list(nx.connected_components(selected_graph))
            # only one connected component --> single hamiltonian cycle
            if (len(components) == 1):
                self._sol_graph = selected_graph
                return None
            
            # for every subtour, add subour elimination constraints iteratively
            for comp in components:
                edges_leaving = []
                for v in comp:
                    for w in self.graph.nodes():
                        if w not in comp:
                            e = (v, w) if v < w else (w, v)
                            if e in self._vars:
                                edges_leaving.append(e)
                if edges_leaving:
                    self._model.addConstr(gp.quicksum(self._vars[e] for e in edges_leaving) >= self.k)