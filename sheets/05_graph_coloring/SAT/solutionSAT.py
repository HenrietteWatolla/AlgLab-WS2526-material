import networkx as nx
from pysat.solvers import Solver as SATSolver

import time

class SAT:
    def solve_coloring_SAT(G: nx.Graph, minimal_heuristic: int, time_limit = 60) -> int:
        
        k = minimal_heuristic
        vertices = list(G.nodes)
        edges = list(G.edges)
        available_colors = range(minimal_heuristic)

        # find the smallest number of colors iteratively,
        # start with the given heuristic solution and decrease as long as possible

        while k > 0:
            solver = SATSolver("Minicard")

            # create variables
            # mapping of vertice-color pairs with variable indices

            node_coloring = {}
            var_counter = 1  # start variable IDs at 1

            for color in available_colors:
                for node in vertices:
                    node_coloring[(node, color)] = var_counter
                    var_counter += 1
        
            # add constraints
            # each vertex gets at least one color --> OR-constraint
            for node in vertices:
                clause = [node_coloring[(node, color)] for color in available_colors]
                solver.add_clause(clause)

            # two adjacent nodes can't share the same color
            for (u, v) in edges:
                for color in available_colors:
                    solver.add_clause([- node_coloring[(u, color)], - node_coloring[(v, color)]])

            # remove colors c used with c >= k
            for v in vertices:
                for color in range(k, minimal_heuristic):
                    solver.add_clause([-node_coloring[(v, color)]])
            
            # measure solution time
            start = time.time()
            sol = solver.solve()
            end = time.time()

            runtime = end - start

            if sol:

                # satisfiability with k colors --> extract solution
                solution = {
                "objective": None,
                "coloring": None,
                "runtime": runtime
                }

                coloring = {}
                for node in vertices:
                    for color in available_colors:
                        if node_coloring[(node, color)] > 0:
                            coloring[node] = color

                solution["objective"] = k
                solution["coloring"] = coloring

                # try to use smaller k in the next iteration
                k -= 1

            else:
                break

        print(solution["objective"], "\n")
        print(solution)

        return solution["objective"]
    
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

G = nx.erdos_renyi_graph(54, 0.5, seed = 42)
print(SAT.solve_coloring_SAT(G, 11))
