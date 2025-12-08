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

        #print("sources ", w_tunnels, "\n")
        #print("mines ", w_mines)

        # create variables, consider both tunnel directions
        # number of ores transported along this direction
        flow_variables = {}
        # tunnel is used or not
        usage_variables = {}
        for t in w_tunnels:
            flow_variables[(t[0], t[1])] = self._model.addVar(vtype = GRB.INTEGER, name = f"flow_{t[0]}_{t[1]}", lb = 0)
            flow_variables[(t[1], t[0])] = self._model.addVar(vtype = GRB.INTEGER, name = f"flow_{t[1]}_{t[0]}", lb = 0)
            usage_variables[(t[0], t[1])] = self._model.addVar(vtype = GRB.BINARY, name = f"tunnel_{t[0]}_{t[1]}")
            usage_variables[(t[1], t[0])] = self._model.addVar(vtype = GRB.BINARY, name = f"tunnel_{t[1]}_{t[0]}")

        # add constraints
        # only one direction can be used at once
        for source, target, throughput, costs in w_tunnels:
            self._model.addConstr(
                (usage_variables[(source, target)] + usage_variables[(target, source)] <= 1)
            )
            # dont exceed maximal throughput of the tunnels
            self._model.addConstr(
                (flow_variables[(source, target)] <= throughput * usage_variables[(source, target)])
            )
            self._model.addConstr(
                (flow_variables[(target, source)] <= throughput * usage_variables[(target, source)])
            )
        # budget constraint
        self._model.addConstr(
                (gp.quicksum(costs * (usage_variables[(source, target)] + usage_variables[(target, source)])
                    for source, target, throughput, costs in w_tunnels) <= instance.budget)
            )

        # obejctive function

    def solve(self) -> Solution:
        """
        Calculate the optimal solution to the problem.
        Returns the "flow" as a list of tuples, each tuple with two entries:
            - The *directed* edge tuple. Both entries in the edge should be ints, representing the ids of locations.
            - The throughput/utilization of the edge, in goods per hour
        """
        # TODO: implement me!
        logging.info("Solving model...")
