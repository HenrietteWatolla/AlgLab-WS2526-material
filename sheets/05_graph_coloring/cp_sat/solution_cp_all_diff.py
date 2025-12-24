import networkx as nx
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver

class CP_SAT_ALL_DIFF:
    def solve_coloring_all_diff_CP_SAT(G: nx.Graph, minimal_heuristic: int, time_limit = 60):

        vertices = list(G.nodes)
        edges = list(G.edges)
        available_colors = range(minimal_heuristic)

        # use for AllDiff Constraint
        # filter because the number of cliques can be exponential
        max_used_cliques = len(vertices) // 20
        MIN_SIZE = 7

        cliques = [
            c for c in nx.find_cliques(G)
            if len(c) >= MIN_SIZE
        ][:max_used_cliques]


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

        # strengthen the model by AllDifferent constraints on subsets of vertices that form cliques
        for clique in cliques:
            model.AddAllDifferent([node_coloring[v] for v in clique])

        # objective function --> minimizing used colors
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

        print(solution)

        return solution