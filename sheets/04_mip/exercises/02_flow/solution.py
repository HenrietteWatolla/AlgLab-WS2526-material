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
        locations = set(instance.locations)
        elevator = instance.elevator_location

        # create variables, consider both tunnel directions
        # number of ores transported along this direction
        self.mine_flow = {}
        # tunnel is used or not, considering the direction
        self.used_tunnel_directed = {}
        for source, target, throughput, costs in w_tunnels:
            # both directions necessary?
            self.mine_flow[(source, target)] = self._model.addVar(vtype = GRB.CONTINUOUS, name = f"flow_{source}_{target}", lb = 0)
            self.mine_flow[(target, source)] = self._model.addVar(vtype = GRB.CONTINUOUS, name = f"flow_{target}_{source}", lb = 0)
            self.used_tunnel_directed[(source, target)] = self._model.addVar(vtype = GRB.BINARY, name = f"tunnel_{source}_{target}")
            self.used_tunnel_directed[(target, source)] = self._model.addVar(vtype = GRB.BINARY, name = f"tunnel_{target}_{source}")

        # add constraints
        big_M = max(1.0, sum(w_mines.values()))
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
            # flow and usage of tunnels must be connected (if tunnel unused --> flow must be 0)
            # use Big M
            self._model.addConstr(
                self.used_tunnel_directed[(source, target)] * big_M >= self.mine_flow[(source, target)]
            )
            self._model.addConstr(
                self.used_tunnel_directed[(target, source)] * big_M >= self.mine_flow[(target, source)]
            )

        # budget constraint
        self._model.addConstr(
                (gp.quicksum((costs * (self.used_tunnel_directed[(source, target)] + self.used_tunnel_directed[(target, source)]))
                    for source, target, throughput, costs in w_tunnels) <= instance.budget)
            )
        # flow constraint --> at least incoming ore, at most +mine's capacity has to exit a mine
        for loc, prod in w_mines.items():
            outflow = gp.quicksum(self.mine_flow[(loc, v)] for (u, v, t, c) in w_tunnels if u == loc)
            inflow = gp.quicksum(self.mine_flow[(u, loc)] for (u, v, t, c) in w_tunnels if v == loc)
            self._model.addConstr(outflow - inflow <= prod)
            self._model.addConstr(outflow >= inflow)
        print("flow out ", outflow, "flow_in ", inflow, "mine capacity ", prod, "\n")

        # flow conservation at intermediate nodes
        mine_locations = set(w_mines.keys())
        intermediate = locations - mine_locations - {elevator}
        for node in intermediate:
            outflow = gp.quicksum(self.flow[(node, v)] for (u, v, t, c) in w_tunnels if u == node)
            inflow = gp.quicksum(self.flow[(u, node)] for (u, v, t, c) in w_tunnels if v == node)
            self._model.addConstr(inflow == outflow)
        
        # elevator eats up ore completely
        elevator_out = gp.quicksum(self.mine_flow[(elevator, v)] for (u, v, t, c) in w_tunnels if u == elevator)
        elevator_in = gp.quicksum(self.mine_flow[(u, elevator)] for (u, v, t, c) in w_tunnels if v == elevator)
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

        # debugging
        if self._model.Status == GRB.OPTIMAL:
            print("Objective: ", self._model.ObjVal)

        # compute used tunnels --> in solution no tunnels are used, WHY?
        used = []
        for (u, v), var in self.used_tunnel_directed.items():
            val = var.X
            if val is not None and val > 0:
                used.append((u, v))
        print("Opened directed edges: ", used)

        solution_flows = []
        print("solution count", self._model.SolCount)
        print("mine flow entries ", self.mine_flow.items())
        if self._model.status == GRB.OPTIMAL:
            # collect all flow variables with positive value
            print("solution ", self.mine_flow.items())
            for (source, target), var in self.mine_flow.items():
                val = var.X
                print("VALUE ", val, "\n")
                if val > 0:
                    solution_flows.append(((source, target), float(val)))
        print("solution ", solution_flows)

        return Solution(flow = solution_flows)