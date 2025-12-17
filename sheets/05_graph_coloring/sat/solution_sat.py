import networkx as nx
from pysat.solvers import Solver as SATSolver

import time

class SAT:
    def solve_coloring_SAT(G: nx.Graph, minimal_heuristic: int, time_limit = 60) -> int:
        
        k = minimal_heuristic
        vertices = list(G.nodes)
        edges = list(G.edges)

        # measure solution time
        init_time = time.time()
        total_runtime = init_time

        # find the smallest number of colors iteratively,
        # start with the given heuristic solution and decrease as long as possible

        while k > 0:

            if total_runtime - init_time > time_limit:
                print("TIMEOUT")
                break

            start = time.time()

            solver = SATSolver("Minicard")

            available_colors = range(k)

            # create variables
            # mapping of vertice-color pairs with variable indices

            node_coloring = {}
            var_counter = 1  # start variable IDs at 1

            for color in available_colors:
                for node in vertices:
                    node_coloring[(node, color)] = var_counter
                    var_counter += 1
                print("SAT COLORS")
        
            # add constraints
            # each vertex gets at least one color --> OR-constraint
            for node in vertices:
                clause = [node_coloring[(node, color)] for color in available_colors]
                solver.add_clause(clause)

            # two adjacent nodes can't share the same color
            for (u, v) in edges:
                for color in available_colors:
                    solver.add_clause([- node_coloring[(u, color)], - node_coloring[(v, color)]])
            
            sol = solver.solve()

            if sol:

                # satisfiability with k colors --> extract solution

                model = solver.get_model()
                model_set = set(model)

                solution = {
                    "objective": None,
                    "coloring": None,
                    "runtime": (total_runtime - init_time)
                }

                coloring = {}
                for node in vertices:
                    for color in available_colors:
                        var = node_coloring[(node, color)]
                        if var in model_set:
                            coloring[node] = color
                            break

                solution["objective"] = k
                solution["coloring"] = coloring

                # try to use smaller k in the next iteration
                k -= 1

                end = time.time()
                print(end - start)
            
                total_runtime += (end - start)

            else:

                # prooving infeasibility of the current number of colors k is very difficult + needs a lot of time
                end = time.time()
                print(end - start)
            
                total_runtime += (end - start)
                break

        print(solution["objective"], "\n")
        print(solution)

        return solution["objective"]

"""    
# test on some instances
G = nx.complete_graph(5)
res = SAT.solve_coloring_SAT(G, 5)
print(res)

G = nx.path_graph(10)
print(SAT.solve_coloring_SAT(G, 10))

G = nx.cycle_graph(5)
print(SAT.solve_coloring_SAT(G, 5))

G = nx.complete_bipartite_graph(5,5)
print(SAT.solve_coloring_SAT(G, 10))

# too difficult
#G = nx.kneser_graph(14, 4)
#print(GurobiASS.solve_coloring_ASS_gurobi(G, 8))
#G = nx.kneser_graph(13, 4)
#print(GurobiASS.solve_coloring_ASS_gurobi(G, 7))

G = nx.kneser_graph(5, 2)
print(SAT.solve_coloring_SAT(G, 10))

G = nx.erdos_renyi_graph(40, 0.5, seed = 42)
print(SAT.solve_coloring_SAT(G, 11))

# timeout --> we know k + 1 is a feasible solution
# but no information about current iteration --> k can also be feasible
G = nx.erdos_renyi_graph(54, 0.5, seed = 42)
print(SAT.solve_coloring_SAT(G, 11))
"""