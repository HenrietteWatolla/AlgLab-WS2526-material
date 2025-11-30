"""
Implement the Dantzig-Fulkerson-Johnson formulation for the TSP.
"""

import logging
import typing

import gurobipy as gp
import networkx as nx
from gurobipy import GRB


class GurobiTspSolver:
    """
    IMPLEMENT ME!
    """

    def __init__(self, G: nx.Graph, k: int = 2):
        """
        G is a weighted networkx graph, where the weight of an edge is stored in the
        "weight" attribute. It is strictly positive.
        """
        self.graph = G
        assert (
            G.number_of_edges() == G.number_of_nodes() * (G.number_of_nodes() - 1) / 2
        ), "Invalid graph"
        assert all(
            weight > 0
            for _, _, weight in G.edges.data("weight", default=None)  # type: ignore[attr-defined]
        ), "Invalid graph"
        assert k in {1, 2}, "Invalid k"
        self.k = k
        logging.info("Creating model ...")
        logging.info(
            "Graph has %d nodes and %d edges", G.number_of_nodes(), G.number_of_edges()
        )
        logging.info("Implementing subtour elimination with >= %d", k)
        self._model = gp.Model()
        # TODO: Implement me!

        # create bool variable for every edge
        # consider ordering, because of non directed graph to avoid several variables for the same edge
        edges = G.edges()
        self._vars = {}
        for (u, v) in edges:
            x, y = (u, v) if u < v else (v, u)
            self._vars[(x, y)] = self._model.addVar(vtype = GRB.BINARY, name = f"edge_{u}_{v}")

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
        return self._model.ObjBound

    def get_solution(self) -> typing.Optional[nx.Graph]:
        """
        Return the current solution as a graph.
        """
        # TODO: Implement me!
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", self._sol_graph)
        print("nodes ", self._sol_graph.nodes(), "edges ", self._sol_graph.edges())
        return self._sol_graph

    def get_objective(self) -> typing.Optional[float]:
        """
        Return the objective value of the last solution.
        """
        # TODO: Implement me!
        if self._model.SolCount > 0:
            return self._model.ObjVal
        return None

    def solve(self, time_limit: float, opt_tol: float = 0.001) -> None:
        """
        Solve the model. After solving the model, the solution, its objective value,
        and the lower bounds should be available via the corresponding methods.
        """
        logging.info("Solving model ...")
        # Set parameters for the solver.
        self._model.Params.LogToConsole = 1
        self._model.Params.TimeLimit = time_limit
        self._model.Params.LazyConstraints = 1
        self._model.Params.MIPGap = (
            opt_tol  # https://www.gurobi.com/documentation/11.0/refman/mipgap.html
        )

        # ...
        # TODO: Implement me!

        # subour elimination constraints added iteratively via callback
        def callback(model, where):

            print("where", where)
            if where == gp.GRB.Callback.MIPSOL:

                ("WHY I CANT GET HERE?????????????????????????????")
                #solution = self._model.cbGetSolution
                solution = model.cbGetSolution(self._vars)

                # build graph from solution values > 0.5
                selected_graph = nx.Graph()
                selected_graph.add_nodes_from(self.graph.nodes())
                for (u, v), val in solution.items():
                    if val >= 0.5:
                        selected_graph.add_edge(u,v)

                # find subtours
                components = list(nx.connected_components(selected_graph))
                print("comp8888888888888888888888888888888888888888888888888888888888888888888888888888onents ", components)
                # only one connected component --> single hamiltonian cycle
                if (len(components) == 1):
                    return

                # for every strict subset of set of vertices, add subour elimination constraint
                for comp in components:
                    edges_leaving = []
                    for v in comp:
                        for w in self.graph.nodes():
                            if w not in comp:
                                # sorted tuple (v, w)
                                e = (v, w) if v < w else (w, v)
                                if e in self._vars:
                                    edges_leaving.append(e)

                    # isolated component --> the found subtours can't get connected
                    if not edges_leaving:
                        continue

                    # lazy constraint --> enforce that at least 2 edges leave the component
                    if edges_leaving:
                        model.cbLazy(gp.quicksum(self._vars[e] for e in edges_leaving) >= 2)

        self._model.optimize(callback)  # pass callback with the solve call

        # build current best solution
        sol_graph = nx.Graph()
        sol_graph.add_nodes_from(self.graph.nodes())
        for edge, var in self._vars.items():
            value = var.X  # value in current best solution
            if value >= 0.5:
                (u, v) = edge
                sol_graph.add_edge(u, v, weight = self.graph[u][v]["weight"])
        
        # after optimization get solution, its objective value and the lower bound
        if self._model.status == GRB.OPTIMAL:
            self._sol_graph = sol_graph
            return None
        if self._model.SolCount > 0:
           self._model.optimize(callback)