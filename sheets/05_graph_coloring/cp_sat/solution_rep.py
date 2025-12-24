import networkx as nx
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver

class CP_SAT_REP:
    def solve_coloring_REP_CP_SAT(G: nx.Graph, minimal_heuristic = int | None, time_limit = 60):

        vertices = sorted(G.nodes) # sorted to ensure that smallest index node is used as representant of class
        edges = list(G.edges)

        solver = CpSolver()
        solver.parameters.log_search_progress = True
        model = CpModel()

        solver.parameters.max_time_in_seconds = time_limit

        # create variables
        # nodes v, w are colored with the same color (1) --> w is representant of v
        same_color = {}
        for v in vertices:
            for w in vertices:
                # ordering to choose smallest possible representant
                if w <= v and w not in G.neighbors(v):
                    same_color[(v, w)] = model.NewBoolVar(f"same_color{v}_{w}")
        
        # add constraints
        # each vertex must choose exactly one representative
        for v in vertices:
            model.Add(sum(same_color[(v, w)]
                                for w in vertices
                                if (v, w) in same_color)
                                == 1
                            )

        # two adjacent nodes can't choose the same representant
        # + if v selects w as its representative, then w must itself be marked as representative

        for (v, w) in same_color:
            model.Add(
                same_color[(v, w)] <= same_color[(w, w)]
            )

        for (u, v) in edges:
            for w in vertices:
                # w can only be a valid representative for wether u or v
                if (((u, w) in same_color) and ((v, w) in same_color)):
                    model.Add(
                        same_color[(u, w)] + same_color[(v, w)] <= same_color[(w, w)]
                    )

        # objective function --> minimizing used colors
        # this is equal to minimize nodes that are representatives of themselves
        model.Minimize(sum(same_color[(v, v)] for v in vertices))

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

            # get node classes
            representatives = [
                w for w in vertices
                if solver.Value(same_color[(w, w)]) == 1
            ]

            # one color index per representant
            rep_to_color = {rep: i for i, rep in enumerate(representatives)}

            # assign colors to vertices
            for v in vertices:
                for w in vertices:
                    if (v, w) in same_color and solver.Value(same_color[(v, w)]) == 1:
                        coloring[v] = rep_to_color[w]
                        break

        solution["status"] = solver.StatusName()
        solution["objective"] = sum(1 for v in vertices if solver.Value(same_color[(v, v)]) == 1)
        solution["coloring"] = coloring
        solution["LB"] = solver.BestObjectiveBound()

        print(solution)

        return solution