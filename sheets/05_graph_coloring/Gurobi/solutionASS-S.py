import gurobipy as gp
import networkx as nx
from gurobipy import GRB

from instances.instances import Instances
from heuristics.heuristics import Heuristics

class GurobiASS:
    def solve_coloring_ASS_gurobi(G: nx.Graph, minimal_heuristic: int, time_limit = 60) -> int:

        vertices = list(G.nodes)
        edges = list(G.edges)
        available_colors = range(minimal_heuristic)

        model = gp.Model()

        model.Params.TimeLimit = time_limit

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

        # add ASS-S specific constraints
        # fix order of colors
        for color in available_colors:
            if color != used_colors[0]:
                model.addConstr(used_colors[color] <= used_colors[color - 1])

        # enforce that 

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

        if model.Status == GRB.OPTIMAL:
            coloring = {}
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