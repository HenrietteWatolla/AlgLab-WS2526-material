import gurobipy as gp
import networkx as nx
from gurobipy import GRB

class GurobiREP:
    def solve_coloring_REP_gurobi(G: nx.Graph, minimal_heuristic: int | None, time_limit = 60):

        vertices = sorted(G.nodes) # sorted to ensure that smallest index node is used as representant of class
        edges = list(G.edges)

        model = gp.Model()

        model.Params.TimeLimit = time_limit

        # create variables
        # nodes v, w are colored with the same color (1) --> w is representant of v
        same_color = {}

        # representative ones
        for w in vertices:
            same_color[(w, w)] = model.addVar(vtype = GRB.BINARY, name = f"same_color{w}_{w}")

        # non-representative variables
        for v in vertices:
            for w in vertices:
                # ordering to choose smallest possible representant
                if w < v and w not in G.neighbors(v):
                    same_color[(v, w)] = model.addVar(vtype = GRB.BINARY, name = f"same_color{v}_{w}")

        # add constraints
        # each vertex must choose exactly one representative
        for v in vertices:
            model.addConstr(gp.quicksum(same_color[(v, w)]
                                for w in vertices
                                if (v, w) in same_color)
                                == 1
                            )

        # two adjacent nodes can't choose the same representant
        # + if v selects w as its representative, then w must itself be marked as representative

        for (v, w) in same_color:
            model.addConstr(
                same_color[(v, w)] <= same_color[(w, w)]
            )

        for (u, v) in edges:
            for w in vertices:
                # w can only be a valid representative for wether u or v
                if (((u, w) in same_color) and ((v, w) in same_color)):
                    model.addConstr(
                        same_color[(u, w)] + same_color[(v, w)] <= same_color[(w, w)]
                    )

        # objective function --> minimizing used colors, this is equal to minimize nodes that are representatives of themselves
        model.setObjective(gp.quicksum(same_color[(v, v)] for v in vertices), GRB.MINIMIZE)

        # solve the model
        model.optimize()

        # extract solution
        solution = {
            "status": model.Status,
            "objective": None,
            "coloring": None,
            "LB": None,
            "runtime": model.Runtime
        }

        if model.SolCount > 0:

            coloring = {}

            # get node classes
            representatives = [
                w for w in vertices
                if same_color[(w, w)].X > 0.5
            ]

            # one color index per representant
            rep_to_color = {rep: i for i, rep in enumerate(representatives)}

            # assign colors to vertices
            for v in vertices:
                for w in vertices:
                    if (v, w) in same_color and same_color[(v, w)].X > 0.5:
                        coloring[v] = rep_to_color[w]
                        break

            solution["objective"] = model.ObjVal
            solution["LB"] = model.ObjBound
            solution["coloring"] = coloring

            print(solution)

            return solution
        
        else:
            # no feasible solution found within time limit --> return heuristic solution

            solution["objective"] = minimal_heuristic
            solution["best_bound"] = model.ObjBound

            print(solution)

            return solution