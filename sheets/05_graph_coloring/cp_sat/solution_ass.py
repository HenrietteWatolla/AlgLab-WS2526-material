import networkx as nx
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver

class CP_SAT_ASS:
    def solve_coloring_ASS_CP_SAT(G: nx.Graph, minimal_heuristic: int, time_limit = 60):

        vertices = list(G.nodes)
        edges = list(G.edges)
        available_colors = range(minimal_heuristic)

        solver = CpSolver()
        solver.parameters.log_search_progress = True
        model = CpModel()

        solver.parameters.max_time_in_seconds = time_limit

        # create variables
        # node v colored in color c
        node_coloring = {}

        # color used (1) or not (0)
        used_colors = {}
        for color in available_colors:
            used_colors[color] = model.NewBoolVar(f"color_{color}")
            for node in vertices:
                node_coloring[(node, color)] = model.NewBoolVar(f"node_{node}_color{color}")
        
        # add constraints
        # each vertex gets exactly one color
        for v in vertices:
            model.Add(sum(node_coloring[(v, color)] for color in available_colors) == 1)

        # two adjacent nodes can't share the same color
        for (u, v) in edges:
            for color in available_colors:
                model.Add(node_coloring[(u, color)] + node_coloring[(v, color)] <= 1)

        # connect vertex-color assignment with color usage
        for v in vertices:
            for color in available_colors:
                model.AddImplication(node_coloring[(v, color)], used_colors[color])

        # obejctive function --> minimizing used colors
        model.Minimize(sum(used_colors[color] for color in available_colors))

        # solve the model
        result = solver.Solve(model)

        solution = {
            "status": None,
            "objective": None,
            "coloring": None,
            "LB": None,
            "runtime": solver.WallTime()
        }

        coloring = {}
        
        # extract solution
        if result in (OPTIMAL, FEASIBLE):

            for node in vertices:
                for color in available_colors:

                    if solver.Value(node_coloring[node, color]) == 1:
                        coloring[node] = color
                        break
        
        solution["status"] = solver.StatusName()
        solution["objective"] = sum(1 for color in available_colors if solver.Value(used_colors[color]) == 1)
        solution["coloring"] = coloring
        solution["LB"] = solver.BestObjectiveBound()

        print(solution)

        return solution