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
        w_mines = []
        for m in instance.mines.values():
            w_mines.append([m.location, m.ore_per_hour])

        # create variables, consider both tunnel directions
        # number of ores transported along this direction
        self.mine_flow = {}
        # tunnel is used or not, considering the direction
        used_tunnel_directed = {}
        for t in w_tunnels:
            self.mine_flow[(t[0], t[1])] = self._model.addVar(vtype = GRB.INTEGER, name = f"flow_{t[0]}_{t[1]}", lb = 0)
            self.mine_flow[(t[1], t[0])] = self._model.addVar(vtype = GRB.INTEGER, name = f"flow_{t[1]}_{t[0]}", lb = 0)
            used_tunnel_directed[(t[0], t[1])] = self._model.addVar(vtype = GRB.BINARY, name = f"tunnel_{t[0]}_{t[1]}")
            used_tunnel_directed[(t[1], t[0])] = self._model.addVar(vtype = GRB.BINARY, name = f"tunnel_{t[1]}_{t[0]}")

        # add constraints
        # only one direction can be used at once
        for source, target, throughput, costs in w_tunnels:
            self._model.addConstr(
                (used_tunnel_directed[(source, target)] + used_tunnel_directed[(target, source)] <= 1)
            )
            # dont exceed maximal throughput of the tunnels
            self._model.addConstr(
                (self.mine_flow[(source, target)] <= throughput * used_tunnel_directed[(source, target)])
            )
            self._model.addConstr(
                (self.mine_flow[(target, source)] <= throughput * used_tunnel_directed[(target, source)])
            )

        # budget constraint
        self._model.addConstr(
                (gp.quicksum(costs * (used_tunnel_directed[(source, target)] + used_tunnel_directed[(target, source)])
                    for source, target, throughput, costs in w_tunnels) <= instance.budget)
            )
        # flow constraint --> at least incoming ore, at most +mine's capacity has to exit a mine
        for mine in w_mines:
            flow_out = gp.LinExpr()
            flow_in = gp.LinExpr()
            for source, target, throughput, costs in w_tunnels:
                if source == mine[0]:
                    flow_out = flow_out + self.mine_flow[(source, target)]
                if target == mine[0]:
                    flow_in = flow_in + self.mine_flow[(target, source)]
            self._model.addConstr((flow_out - flow_in <= mine[1]))
            print("flow out ", flow_out, "flow_in ", flow_in, "mine capacity ", mine[1], "\n")
        
        # elevator eat up ore completely
        center = instance.elevator_location
        flow_out_elevator = gp.LinExpr()
        flow_in_elevator = gp.LinExpr()
        for source, target, throughput, costs in w_tunnels:
            if source == center:
                flow_out_elevator = flow_out_elevator + self.mine_flow[(source, target)]
            if target == center:
                flow_in_elevator = flow_in_elevator + self.mine_flow[(target, source)]
        self._model.addConstr(flow_out_elevator == 0)

        # obejctive function --> maximize incoming ore at the elevator
        self._model.setObjective(flow_in_elevator, GRB.MAXIMIZE)

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
        if self._model.status == GRB.OPTIMAL:
            # collect all flow variables with positive value
            solution_flows = []
            print("solution ", self.mine_flow.items())
            for (source, target), var in self.mine_flow.items():
                if var.X > 0:
                    flow_value = var.X
                    solution_flows.append(((source, target), flow_value))
        return Solution(flow = solution_flows)