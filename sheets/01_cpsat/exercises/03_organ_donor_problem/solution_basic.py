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
        # TODO: Implement me!

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

        # create graph
        self.graph = CrossoverTransplantSolver.create_graph(self)

        self.solver = CpSolver()
        self.solver.parameters.log_search_progress = True
        self.model = CpModel()
        
        # dict with key = (recipient_start, recipient_end), value = donor
        self.edge_to_donor = {}
        self.compatibility = CrossoverTransplantSolver.create_adjacency_matrix_from_graph(self)
        self.length_matrix = len(self.compatibility) # number of lines
        
        # Decision variables: vars[i][j] = 1 if partner of recipient i donates to recipient j --> edge is chosen
        self.vars = {}
        for i in range(self.length_matrix):
            for j in range(self.length_matrix):
                if self.compatibility[i][j] == 1:
                    self.vars[i, j] = self.model.NewBoolVar(f"x[{i},{j}]")
        
        # each donor donates at most once
        # + if recipient has multiple willing donors, only one of them is willing to donate in the final solution
        # --> at most one outgoing edge per node 
        for i in range(self.length_matrix):
            self.model.Add(
                sum(self.vars[i, j] for j in range(self.length_matrix) 
                    if (i, j) in self.vars) <= 1
            )
        
        # each recipient receives at most once --> at most one incoming edge per node
        for j in range(self.length_matrix):
            self.model.Add(
                sum(self.vars[i, j] for i in range(self.length_matrix) 
                    if (i, j) in self.vars) <= 1
            )

        # donor only dontes if partner gets organ in exchange
        # constrainsts above enforce that outgoing = incoming = 0 || 1
        for i in range(self.length_matrix):
            outgoing = sum(self.vars[i, j] for j in range(self.length_matrix) if (i, j) in self.vars)
            incoming = sum(self.vars[k, i] for k in range(self.length_matrix) if (k, i) in self.vars)
            self.model.Add(outgoing == incoming)

        # objective function
        self.model.Maximize(sum(self.vars[i, j] for (i, j) in self.vars))


    def create_adjacency_matrix_from_graph(self):    
        n = len(self.graph.nodes) # number of nodes
        nodes = list(self.graph.nodes)
        # connect node and index
        index = {}
        for i, node in enumerate(nodes):
            index[node] = i

        # adjacency matrix with 0 and 1 (not connected and connected vertices)
        # init with zeros
        compatibility_matrix = []
        for i in range(n):
            compatibility_matrix.append([0] * n)
        
        # change 0 to 1 if vertices are connected and store partner
        for recipient_start, recipient_end, data in self.graph.edges(data = True):
            u = index[recipient_start]
            v = index[recipient_end]
            compatibility_matrix[u][v] = 1
            self.edge_to_donor[(u, v)] = data['partner_d']
        return compatibility_matrix
    
    
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
                        G.add_edge(recipient_start, recipient_end, partner_d = donor)
        return G

    def optimize(self, timelimit: float = math.inf) -> Solution:
        """
        Solves the constraint programming model and returns the optimal solution (if found within time limit).
        :param timelimit: The maximum time limit for the solver.
        :return: A list of Donation objects representing the best solution, or None if no solution was found.
        """
        if timelimit <= 0.0:
            return Solution(donations = [])
        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit

        # TODO: Implement me!
        result = self.solver.Solve(self.model)

        if result in (OPTIMAL, FEASIBLE):
            donations = []
            for (i, j) in self.vars:
                if self.solver.Value(self.vars[i, j]) == 1:
                    donor = self.edge_to_donor[(i, j)]
                    recipient = self.recipients[j]
                    donations.append(Donation(donor = donor, recipient = recipient))
            return Solution(donations = donations)


        return Solution(donations = [])