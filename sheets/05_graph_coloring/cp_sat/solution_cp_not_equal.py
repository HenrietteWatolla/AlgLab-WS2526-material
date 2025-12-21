import networkx as nx
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver

class CP_SAT_NOT_EQUAL:
    def solve_coloring_not_equal_CP_SAT(G: nx.Graph, minimal_heuristic: int, time_limit = 60):

        vertices = list(G.nodes)
        edges = list(G.edges)
        available_colors = range(minimal_heuristic)

        solver = CpSolver()
        solver.parameters.log_search_progress = True
        model = CpModel()

        solver.parameters.max_time_in_seconds = time_limit

        # create variables
        # node v colored in color c --> integer stands for the choosen variable c
        
        node_coloring = {}
        for node in vertices:
            node_coloring[node] = model.NewIntVar(lb = 1, ub = len(available_colors), name = f"color_of_{node}")

        # auxiliary variable
        highest_color_index = model.NewIntVar(lb = 1, ub = len(available_colors), name = "z_max")
        
        # add constraints
        # adjacent nodes can't have the same number
        for (u, v) in edges:
            model.Add(node_coloring[u] != node_coloring[v])

        # z_max constraint
        for node in vertices:
            model.Add(node_coloring[node] <= highest_color_index)

        # obejctive function --> minimizing used colors
        model.Minimize(highest_color_index)

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
                coloring[node] = solver.Value(node_coloring[node])

        solution["status"] = solver.StatusName()
        solution["objective"] = solver.Value(highest_color_index)
        solution["coloring"] = coloring
        solution["LB"] = solver.BestObjectiveBound()

        print(solution["objective"], "\n")
        print(solution)

        return solution

"""
# test on some instances
G = nx.complete_graph(5)
res = CP_SAT_NOT_EQUAL.solve_coloring_not_equal_CP_SAT(G, 5)
print(res)

G = nx.path_graph(10)
print(CP_SAT_NOT_EQUAL.solve_coloring_not_equal_CP_SAT(G, 10))

G = nx.cycle_graph(5)
print(CP_SAT_NOT_EQUAL.solve_coloring_not_equal_CP_SAT(G, 5))

G = nx.complete_bipartite_graph(5,5)
print(CP_SAT_NOT_EQUAL.solve_coloring_not_equal_CP_SAT(G, 10))

# too difficult
#G = nx.kneser_graph(14, 4)
#print(GurobiASS.solve_coloring_ASS_gurobi(G, 8))
#G = nx.kneser_graph(13, 4)
#print(GurobiASS.solve_coloring_ASS_gurobi(G, 7))

G = nx.kneser_graph(5, 2)
print(CP_SAT_NOT_EQUAL.solve_coloring_not_equal_CP_SAT(G, 10))

G = nx.erdos_renyi_graph(54, 0.5, seed = 42)
print(CP_SAT_NOT_EQUAL.solve_coloring_not_equal_CP_SAT(G, 13))
"""