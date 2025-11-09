import math

import networkx as nx
from data_schema import Donation, Solution
from database import TransplantDatabase
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver
import time

class CrossoverTransplantSolver:
    def __init__(self, database: TransplantDatabase) -> None:
        """
        Constructs a new solver instance, using the instance data from the given database instance.
        :param Database database: The organ donor/recipients database.
        """
        self.database = database
        # TODO: Implement me!

        # Init Stuff to work with
        self.recipients = self.database.get_all_recipients()
        self.donors = self.database.get_all_donors()

        self.partners_d = {} #key: recipient, value: partners
        for recipient in self.recipients:
            self.partners_d[recipient] = self.database.get_partner_donors(recipient)

        """
        for recipient in self.recipients:
            
            print("possible donors for recipient ", recipient)
            print(self.database.get_compatible_donors(recipient))
            print("\n")
            print("partners of recipient ", recipient)
            print(self.partners_d[recipient])
            print("\n")
            print("\n")
            print("\n")
        """

        #create graph
        self.graph = CrossoverTransplantSolver.create_graph(self)
        #self.cycles = [tuple(c) for c in nx.simple_cycles(self.graph, length_bound = 3)]

        #print("cycles")
        #print(self.cycles)

        self.solver = CpSolver()
        self.solver.parameters.log_search_progress = True
        self.model = CpModel()
        
        self.edge_to_donor = {}  # key = (u_index, v_index), value = donor
        self.compatibility = CrossoverTransplantSolver.create_adjacency_matrix_from_graph(self)
        self.length_matrix = len(self.compatibility)
        

        # Decision variables: x[i][j] = 1 if donor i donates to recipient j
        self.vars = {}
        for i in range(self.length_matrix):
            for j in range(self.length_matrix):
                if self.compatibility[i][j] == 1:
                    self.vars[i, j] = self.model.NewBoolVar(f"x[{i},{j}]")
        
        #Each donor donates at most once --> at most one outgoing edge per node 
        for i in range(self.length_matrix):
            self.model.Add(
                sum(self.vars[i, j] for j in range(self.length_matrix) 
                    if (i, j) in self.vars) <= 1
            )
        
        #Each recipient receives at most once --> at most one incoming edge per node
        for j in range(self.length_matrix):
            self.model.Add(
                sum(self.vars[i, j] for i in range(self.length_matrix) 
                    if (i, j) in self.vars) <= 1
            )

        #Donor only dontes if partner gets organ in exchange
        for i in range(self.length_matrix):
            outgoing = sum(self.vars[i, j] for j in range(self.length_matrix) if (i, j) in self.vars)
            incoming = sum(self.vars[k, i] for k in range(self.length_matrix) if (k, i) in self.vars)
            self.model.Add(outgoing == incoming)

        self.model.Maximize(sum(self.vars[i, j] for (i, j) in self.vars))


    def create_adjacency_matrix_from_graph(self):    
        n = len(self.graph.nodes)
        nodes = list(self.graph.nodes)
        index = {node: i for i, node in enumerate(nodes)}

        # adjacency matrix (0/1)
        compatibility = [[0]*n for y in range(n)]
        

        for u, v, data in self.graph.edges(data=True):
            ui = index[u]
            vi = index[v]
            compatibility[ui][vi] = 1
            self.edge_to_donor[(ui, vi)] = data['partner_d']
        return compatibility





    def create_graph(self):
        G = nx.DiGraph()
        startTime = time.time()
        for recipient in self.recipients:
            G.add_node(recipient)
        
        acceptable_donors = {}
        possible_donors = {}
        for recipient in self.recipients:

            #get all compatible donors for node v 
            acceptable_donors[recipient] = self.database.get_compatible_donors(recipient) 
            #get all partner donors for node u
            possible_donors[recipient] = self.partners_d[recipient]

        #add edges (u=recipient_start,v=recipient_end) to graph
        for recipient_start in self.recipients:
            for recipient_end in self.recipients:

                #get all compatible donors for node v 
                acceptable_donors_v = set(acceptable_donors[recipient_end])     
                #acceptable_donors_v = acceptable_donors[recipient_end]
                #get all partner donors for node u
                possible_donors_u = set(possible_donors[recipient_start])
                #possible_donors_u = possible_donors[recipient_start]

                #for every acceptable donor check if possible donor is existent for node u, if yes add edge with attr of partner donor
                for x in acceptable_donors_v:
                    if x in possible_donors_u:
                        G.add_edge(recipient_start, recipient_end, partner_d = x)
        EndTime = time.time()
        print("TIME: ", EndTime-startTime)
        return G
    
    def get_graph(self):
        return self.graph

    

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
        result = self.solver.Solve(self.model)

        if result in (OPTIMAL, FEASIBLE):
            donations = [
                Donation(
                    donor=self.edge_to_donor[(i, j)],
                    recipient=self.recipients[j]  
                )
                for (i, j) in self.vars
                if self.solver.Value(self.vars[i, j]) == 1
            ]
            return Solution(donations=donations)

        return Solution(donations=[])