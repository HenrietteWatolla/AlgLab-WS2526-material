import math

import networkx as nx
from data_schema import Donation, Solution
from database import TransplantDatabase
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver

class CrossoverTransplantSolver:

    def __init__(self, database: TransplantDatabase) -> None:
        """
        Constructs a new solver instance, using the instance data from the given database instance.
        :param Database database: The organ donor/recipients database.
        """
        self.database = database
        # Init Stuff to work with
        recipients = self.database.get_all_recipients()
        donors = self.database.get_all_donors()
 
        # create dictionaries for fast access
        compatible_donors_per_recipient = {}
        partner_of_recipients = {}
        print("a!!!!!!!!!!!!!!!!!!")
        for recipient in recipients:
            compatible_donors_per_recipient[recipient] = self.database.get_compatible_donors(recipient)
            partner_of_recipients[recipient] = self.database.get_partner_donors(recipient)
        compatible_recipients_per_donor = {}
        partner_of_donors = {}
        print("b!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        for donor in donors:
            compatible_recipients_per_donor[donor] = self.database.get_compatible_recipients(donor)
            partner_of_donors[donor] = self.database.get_partner_recipient(donor)
        print("c!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(partner_of_donors)
        # print(partner_of_recipients)

        # build directed graph
        def build_directed_graph(database: TransplantDatabase) -> nx.DiGraph:
            # Build a directed NetworkX graph from the TransplantDatabase so we can identifiy cycles.
            G = nx.DiGraph()

            # Add all recipients as nodes in the graph
            for recipient in recipients:
                G.add_node(recipient)
            print("ea!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            # Add directed edges to the graph --> one per compatible donation
            for recipient1 in recipients:
                for partner in partner_of_recipients[recipient1]:
                    for recipient2 in compatible_recipients_per_donor[partner]:
                        G.add_edge(recipient1, recipient2, partner = partner)
            print("eb!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            return G
        
        print("d!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # TODO: Implement me!
        #self.items = datab.items
        #self.capacities = instance.capacities
        self.model = CpModel()
        #self.solver = CpSolver()

        self.solver = CpSolver()
        self.solver.parameters.log_search_progress = True

        print("e!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        self.directed_graph = build_directed_graph(database)
        print("w")
        self.circles = [tuple(c) for c in nx.simple_cycles(self.directed_graph, length_bound = 5)]
        # self.circles_list = list(nx.simple_cycles(self.directed_graph, length_bound = 2))
        print("x")
        # Variables --> one per recipient, connected to the cycle of donation
        # self.circles = [c for c in nx.simple_cycles(self.directed_graph) if len(c) <= 5]
        print(len(recipients))
        print(self.circles)
        self.vars = {}
        print("f!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        for circle in self.circles:
            for recipient in recipients:
                self.vars[recipient, circle] = self.model.new_bool_var(f"{recipient},{circle}")
        print("g!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Constraints
        # choosing of cycles
        # donor is willing to donate only if their associated recipient receives an organ in exchange
        # --> outgoing edge from the node leads to ingoing edge for the same node
        # --> use one node of the cycle, use all
        # only one of multiple willing donors will donate in the final solution --> per node at most one outgoing edge
        self.vars_cycles = {}
        for circle in range(len(self.circles)):
            self.vars_cycles[circle] = self.model.new_bool_var("choosen cycles")
        print("h!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        #for circle in circles:
        #    for recipient in recipients:
                # choose one node of the cycle leads to choosing complete cycle --> 1 <= 1
        #        self.model.Add(self.vars[recipient, circle] <= self.vars_cycles[circle]) ###Fehler Hier!
        for node in range(len(recipients)):
            self.model.Add(sum(self.vars_cycles[circle] for circle in self.circles if node in circle) <= 1)

        print("i!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # donor can only donate once
        for donor in donors:
            recipient = self.database.get_partner_recipient(donor)
            self.model.Add(sum(self.vars[recipient, circle] for circle in self.circles) <= 1)
        print("j!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # recipient can receive only one organ
        for recipient in recipients:
            self.model.Add(sum(self.vars[recipient, circle] for circle in self.circles) <= 1)
        print("k!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Objective function
        self.model.maximize(sum(self.vars[recipient, circle] for recipient in recipients for circle in self.circles))
        print("l!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    def optimize(self, timelimit: float = math.inf) -> Solution:
        """
        Solves the constraint programming model and returns the optimal solution (if found within time limit).
        :param timelimit: The maximum time limit for the solver.
        :return: A list of Donation objects representing the best solution, or None if no solution was found.
        """
        if timelimit <= 0.0:
            return Solution(donations=[])
        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit
        # TODO: Implement me!
        status = self.solver.solve(self.model)
        print("m!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        if status in (OPTIMAL, FEASIBLE):
            # create one empty list
            donations = []
            circles = self.circles
            for circle_idx, circle in enumerate(circles):
                if self.solver.value(self.vars_cycles[circle_idx]) == 1:
                    
                # print(self.directed_graph.edges.data())
                # if self.solver.value(self.vars[recipient, circle]) == 1:
                    for recipient in range(len(circle)):
                        recipient1 = circle[recipient]
                        recipient2 = circle[(recipient + 1) % len(circle)] # mod cycle length --> read whole cycle one time
                        donor = self.directed_graph[recipient1, recipient2]['partner']
                        donations.append(Donation(donor = donor, recipient = recipient2))
                        print(donations)

            return Solution(donations = donations)
        else:
            # no solution found --> return empty solution
            return Solution(donations = [])
