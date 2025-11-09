import math
from collections import defaultdict

import networkx as nx
from data_schema import Donation, Solution
from database import TransplantDatabase
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver
import time

class CycleLimitingCrossoverTransplantSolver:
    def __init__(self, database: TransplantDatabase) -> None:
        """
        Constructs a new solver instance, using the instance data from the given database instance.
        :param Database database: The organ donor/recipients database.
        """

        time4_start = time.time()
        self.database = database
        # Init Stuff to work with
        self.recipients = self.database.get_all_recipients()
        self.donors = self.database.get_all_donors()

        # dict with key = recipient, value = partners
        self.partners = {}
        # dict with key = recipient, value = compatible donors
        self.compatible_donors = {}
        for recipient in self.recipients:
            self.partners[recipient] = self.database.get_partner_donors(recipient)
            # get all compatible donors for each recipient
            self.compatible_donors[recipient] = self.database.get_compatible_donors(recipient)
        time4_end = time.time()
        print("TIME!!!!!!!!!INITIALIZATION!", time4_end-time4_start)
        # create graph
        time_start1 = time.time()
        self.graph = CycleLimitingCrossoverTransplantSolver.create_graph(self)
        time_end1 = time.time()
        print("TIME!!!!!Create_Graph!!!!", time_end1-time_start1)
        # TODO: Implement me!

        
        self.solver = CpSolver()
        self.solver.parameters.log_search_progress = True
        self.model = CpModel()

        time_start = time.time()
        self.transplantation_cycles = [tuple(c) for c in nx.simple_cycles(self.graph, length_bound = 3)]
        time_end = time.time()
        print("TIME!!!!find Cycles!!", time_end-time_start)
        # Variables --> choose cycle or not
        time_start3 = time.time()
        self.vars_cycles = {}

        timex = time.time()
        for circle in self.transplantation_cycles:
            self.vars_cycles[circle] = self.model.new_bool_var("cc") # choosen cycles
        timey = time.time()
        print("TIME circle Vars", timey-timex)
        # Constraints
        #for node in range(len(recipients)):
         #   self.model.Add(sum(self.vars_cycles[circle] for circle in self.circles if node in circle) <= 1)

        # each donor donates at most once
        # + if recipient has multiple willing donors, only one of them is willing to donate in the final solution
        # --> at most one outgoing edge per node
        # recipient can receive only one organ
        # --> represent everything here

        timec = time.time()
        recipient_in_cycles = defaultdict(list)
        for c in self.transplantation_cycles:
            for r in c:
                recipient_in_cycles[r].append(self.vars_cycles[c])
        #for recipient in self.recipients:
        #    self.model.Add(sum(self.vars_cycles[c] for c in self.transplantation_cycles if recipient in c) <= 1)
        #above is unoptimize takes ~20seconds, new variateion takes 0.3 seconds
        for r, vars_for_r in recipient_in_cycles.items():
            self.model.AddAtMostOne(vars_for_r)
        
        timecc = time.time()
        print("TIME add constraint", timecc-timec)

        # Objective function
        timej = time.time()
        self.model.Maximize(sum(len(c) * self.vars_cycles[c] for c in self.transplantation_cycles))
        timejj = time.time()
        print("TIME Objective funktion", timejj-timej)
        time_end3 = time.time()
        print("TIME!!!!create vars!!!!!!", time_end3-time_start3)
    
    def create_graph(self):
        G = nx.DiGraph()

        # add vertices
        for recipient in self.recipients:
            G.add_node(recipient) 

        # add edges (recipient_start, recipient_end) to graph
        for recipient_start in self.recipients:
            for recipient_end in self.recipients:
                # get all compatible donors for recipient_end
                compatible_donors_end = set(self.compatible_donors[recipient_end]) # access to sets faster because of hashing
                # get all partner donors for recipient_start
                possible_donors_start = set(self.partners[recipient_start])

                # for every to recipient_end acceptable donor check if possible donor is existent for recipient_start,
                # if so, add edge with attr of partner donor
                for donor in compatible_donors_end:
                    if donor in possible_donors_start:
                        G.add_edge(recipient_start, recipient_end, p = donor)
        return G


    def optimize(self, timelimit: float = math.inf) -> Solution:
        if timelimit <= 0.0:
            return Solution(donations=[])
        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit
        time2_start = time.time()
        # TODO: Implement me!
        status = self.solver.solve(self.model)
        if status in (OPTIMAL, FEASIBLE):
            # create one empty list
            donations = []
            circles = self.transplantation_cycles

            for circle in circles:
                if self.solver.Value(self.vars_cycles[circle]) == 1:
                    
                # print(self.directed_graph.edges.data())
                # if self.solver.value(self.vars[recipient, circle]) == 1:
                    for recipient in range(len(circle)):
                        recipient1 = circle[recipient]
                        recipient2 = circle[(recipient + 1) % len(circle)] # mod cycle length --> read whole cycle one time
                        donor = self.graph[recipient1][recipient2]['p']
                        donations.append(Donation(donor = donor, recipient = recipient2))
            time2_end = time.time()
            print("TIME!!!OPTIMIZE!!!", time2_end-time2_start)
            return Solution(donations = donations)
        else:
            # no solution found --> return empty solution
            return Solution(donations = [])