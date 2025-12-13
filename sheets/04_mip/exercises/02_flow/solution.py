import logging

import gurobipy as gp
import networkx as nx
from data_schema import Instance, Solution
from gurobipy import GRB
    
class MiningRoutingSolver:
    def __init__(self, instance: Instance) -> None:
        self.instance = instance
        self.budget = instance.budget
        logging.info("Creating model ...")
        logging.info(
            "Instance has %d locations, %d mines, %d tunnels, and a budget of %.2f",
            len(instance.locations),
            len(instance.mines),
            len(instance.tunnels),
            instance.budget,
        )
        # TODO: Implement me!
        self._model = gp.Model()

        # get parameters
        w_tunnels = []
        for t in instance.tunnels:
            w_tunnels.append([t.source, t.target, t.throughput_per_hour, t.reinforcement_costs])
        w_mines = {m.location: m.ore_per_hour for m in instance.mines.values()}
        elevator = instance.elevator_location

        # build graph
        self.graph = nx.Graph()
        self.graph.add_node(elevator)
        for loc, prod in w_mines.items():
            self.graph.add_node(loc)
        for source, target, throughput, costs in w_tunnels:
            self.graph.add_edge(source, target)

        # create variables, consider both tunnel directions
        # number of ores transported along this direction
        self.mine_flow = {}
        # tunnel is used or not, considering the direction
        self.used_tunnel_directed = {}
        for source, target, throughput, costs in w_tunnels:
            self.mine_flow[(source, target)] = self._model.addVar(
                vtype = GRB.CONTINUOUS, name = f"flow_{source}_{target}", lb = 0.0, ub = throughput
            )
            self.mine_flow[(target, source)] = self._model.addVar(
                vtype = GRB.CONTINUOUS, name = f"flow_{target}_{source}", lb = 0.0, ub = throughput
            )
            self.used_tunnel_directed[(source, target)] = self._model.addVar(
                vtype = GRB.BINARY, name = f"tunnel_{source}_{target}"
            )
            self.used_tunnel_directed[(target, source)] = self._model.addVar(
                vtype = GRB.BINARY, name = f"tunnel_{target}_{source}"
            )

        # add constraints
        # only one direction can be used at once
        for source, target, throughput, costs in w_tunnels:
            self._model.addConstr(
                (self.used_tunnel_directed[(source, target)] + self.used_tunnel_directed[(target, source)] <= 1)
            )
            # dont exceed maximal throughput of the tunnels
            self._model.addConstr(
                (self.mine_flow[(source, target)] <= throughput * self.used_tunnel_directed[(source, target)])
            )
            self._model.addConstr(
                (self.mine_flow[(target, source)] <= throughput * self.used_tunnel_directed[(target, source)])
            )

        # budget constraint
        self._model.addConstr(
                (gp.quicksum(costs * (self.used_tunnel_directed[(source, target)] + self.used_tunnel_directed[(target, source)])
                    for source, target, throughput, costs in w_tunnels) <= instance.budget)
        )
        
        # flow constraint --> at least incoming ore, at most +mine's capacity has to exit a mine
        mine_neighbors = {loc: set(self.graph.neighbors(loc)) for loc, prod in w_mines.items()}

        for loc, prod in w_mines.items():
            outflow = gp.quicksum(self.mine_flow[(loc, v)] for v in mine_neighbors[loc])
            inflow = gp.quicksum(self.mine_flow[(v, loc)] for v in mine_neighbors[loc])
            self._model.addConstr(outflow - inflow <= prod)
        
        # elevator eats up ore completely
        elevator_neighbors = set(self.graph.neighbors(elevator))
        elevator_in = gp.quicksum(self.mine_flow[(v, elevator)] for v in elevator_neighbors)
        elevator_out = gp.quicksum(self.mine_flow[(elevator, v)] for v in elevator_neighbors)
        self._model.addConstr(elevator_out == 0)

        # obejctive function --> maximize incoming ore at the elevator
        self._model.setObjective(elevator_in, GRB.MAXIMIZE)

    def solve(self) -> Solution:
        """
        Calculate the optimal solution to the problem.
        Returns the "flow" as a list of tuples, each tuple with two entries:
            - The *directed* edge tuple. Both entries in the edge should be ints, representing the ids of locations.
            - The throughput/utilization of the edge, in goods per hour
        """
        # TODO: implement me!
        logging.info("Solving model...")

        self._model.optimize()

        solution_flows = []
        # collect all flow variables with positive value
        for (source, target), var in self.mine_flow.items():
            val = var.X
            if val > 0:
                solution_flows.append(((source, target), float(val)))

        return Solution(flow = solution_flows)