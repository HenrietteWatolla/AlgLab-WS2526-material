import gurobipy as gp
import networkx as nx
from gurobipy import GRB

class GurobiASS:
    def solve_coloring_ASS_gurobi(G: nx.Graph, minimal_heuristic: int, time_limit = 60):

        vertices = list(G.nodes)
        edges = list(G.edges)
        available_colors = range(minimal_heuristic)

        model = gp.Model()

        model.Params.TimeLimit = time_limit

        """
        self.heuristics = {
            "greedy": lambda G: Heuristics.greedy_coloring(G, Heuristics.input_order(G)),
            "multi_greedy": lambda G: Heuristics.multi_start_greedy(G, runs = 50, seed = 42),
            "dsatur": Heuristics.dsatur_coloring
        }

        # get instances --> one solving model per instance
        for graph in Instances.generate_test_instances():
            

            # find best upper bound
            self.best_upper_bound = min(Heuristics.num_colors(heuristic) for heuristic in self.heuristics.items())
            print("INIT upper bound ", self.best_upper_bound)
        """

        # create variables
        # node v colored in color c
        
        node_coloring = {}
        # color used (1) or not (0)
        used_colors = {}
        for color in available_colors:
            used_colors[color] = model.addVar(vtype = GRB.BINARY, name = f"color_{color}")
            for node in vertices:
                node_coloring[(node, color)] = model.addVar(vtype = GRB.BINARY, name = f"node_{node}_color{color}")
        
        # add constraints
        # each vertex gets exactly one color
        for v in vertices:
            model.addConstr(gp.quicksum(node_coloring[(v, color)] for color in available_colors) == 1)

        # two adjacent nodes can't share the same color
        for (u, v) in edges:
            for color in available_colors:
                model.addConstr(node_coloring[(u, color)] + node_coloring[(v, color)] <= 1)

        # connect vertex-color assignment with color usage
        for v in vertices:
            for color in available_colors:
                model.addConstr(node_coloring[(v, color)] <= used_colors[color])

        # obejctive function --> minimizing used colors
        model.setObjective(gp.quicksum(used_colors[color] for color in available_colors), GRB.MINIMIZE)

        # solve the model
        model.optimize()

        # extract solution

        solution = {
            "status": model.Status,
            "objective": None,
            "coloring": None,
            "runtime": model.Runtime
        }

        coloring = {}
        if model.SolCount > 0:
            for node in vertices:
                for color in available_colors:
                    if node_coloring[(node, color)].X > 0.5:
                        coloring[node] = color
                        break

        solution["objective"] = sum(1 for color in available_colors if used_colors[color].X > 0.5)
        solution["coloring"] = coloring

        print(solution["objective"], "\n")
        print(solution)

        return solution["objective"]

"""
G = nx.complete_graph(5)
res = GurobiASS.solve_coloring_ASS_gurobi(G, 5)
print(res)

G = nx.path_graph(10)
print(GurobiASS.solve_coloring_ASS_gurobi(G, 10))

G = nx.cycle_graph(5)
print(GurobiASS.solve_coloring_ASS_gurobi(G, 5))

G = nx.complete_bipartite_graph(5,5)
print(GurobiASS.solve_coloring_ASS_gurobi(G, 10))

# too difficult
#G = nx.kneser_graph(14, 4)
#print(GurobiASS.solve_coloring_ASS_gurobi(G, 8))
#G = nx.kneser_graph(13, 4)
#print(GurobiASS.solve_coloring_ASS_gurobi(G, 7))

G = nx.kneser_graph(5, 2)
print(GurobiASS.solve_coloring_ASS_gurobi(G, 10))

G = nx.erdos_renyi_graph(54, 0.5, seed = 42)
print(GurobiASS.solve_coloring_ASS_gurobi(G, 13))
"""