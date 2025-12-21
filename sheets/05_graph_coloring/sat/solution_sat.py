import networkx as nx
from networkx.algorithms.approximation.clique import large_clique_size
from pysat.solvers import Solver as SATSolver

import time
from multiprocessing import Process, Manager

class SAT:

    def run_solver(G: nx.graph, minimal_heuristic, sol_dict):

        solver = SATSolver("Minicard")
        vertices = list(G.nodes)
        edges = list(G.edges)
        available_colors = range(minimal_heuristic)

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
        
        sol = solver.solve_limited(expect_interrupt = True)
        
        sol_dict["sol"] = sol

        if sol:
            model = solver.get_model()
            sol_dict["model"] = model
            sol_dict["node_coloring"] = node_coloring
            sol_dict["available_colors"] = list(available_colors)

    def solve_coloring_SAT(G: nx.Graph, minimal_heuristic: int, time_limit = 60):

        # measure solution time and interrupt after 60s
        init_time = time.time()

        k = minimal_heuristic

        # wrong runtime for instances with timeout
        solution = {"objective": None, "coloring": None, "runtime": 0}

        # find the smallest number of colors iteratively,
        # start with the given heuristic solution and decrease as long as possible

        while k > 0:
            
            remaining_time = time_limit - (time.time() - init_time)

            if remaining_time <= 0:
                print("TIMEOUT")
                break

            manager = Manager()
            sol_dict = manager.dict()

            p = Process(target = SAT.run_solver, args = (G, k, sol_dict))
            p.start()
            p.join(timeout = remaining_time)

            if p.is_alive():
                p.terminate()
                p.join()
                print("TIMEOUT")
                break

            sol = sol_dict.get("sol", None)

            if sol is None:
                print("TIMEOUT")
                break
            
            elif sol:
                # satisfiable with k colors --> extract solution

                model = sol_dict["model"]
                node_coloring = sol_dict["node_coloring"]
                available_colors = sol_dict["available_colors"]

                coloring = {}
                model_set = set(model)

                for node in G.nodes:
                    for color in available_colors:
                        var = node_coloring[(node, color)]
                        if var in model_set:
                            coloring[node] = color
                            break

                solution["objective"] = k
                solution["coloring"] = coloring
                solution["runtime"] = time.time() - init_time
                solution["LB"] = large_clique_size(G)

                # try to use smaller k in the next iteration
                k -= 1

            else:
                # prooving infeasibility of the current number of colors k is very difficult + needs a lot of time
                break

        print(solution["objective"], "\n")
        print(solution)

        return solution

"""
if __name__ == "__main__":
    # test on some instances
    G = nx.complete_graph(5)
    res = SAT.solve_coloring_SAT(G, 5)

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