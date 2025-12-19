import networkx as nx

class Instances:
    @staticmethod
    # store instances in list
    def generate_test_instances():
        instances = []

        # trivial instances
        # complete graphs --> number of vertices = minimal number of colors
        instances.append(("trivial_K3", nx.complete_graph(3)))
        instances.append(("trivial_K4", nx.complete_graph(4)))
        instances.append(("trivial_K23", nx.complete_graph(23)))

        # bipartite graphs --> only two colors necessary
        instances.append(("trivial_bipartite3-5", nx.complete_bipartite_graph(3, 5)))
        instances.append(("trivial_bipartite1-7", nx.complete_bipartite_graph(1, 7)))
        instances.append(("trivial_bipartite9-4", nx.complete_bipartite_graph(9, 4)))

        # cycle graphs (2 colors for even, 3 colors for odd cycles)
        instances.append(("trivial_cycleEven", nx.cycle_graph(24)))
        instances.append(("trivial_cycleOdd", nx.cycle_graph(25)))

        # paths --> two colors
        instances.append(("trivial_path1", nx.path_graph(19)))
        instances.append(("trivial_path2", nx.path_graph(35)))

        # non-trivial instances
        # regular graphs
        for i in range(45):
            number_of_nodes = (i + 1) * 4
            degree = i + 1
            instances.append((f"regular_{number_of_nodes}_{degree}", nx.random_regular_graph(degree, number_of_nodes, seed = 42)))

            degree = 2 * (i + 1)
            instances.append((f"regular_{number_of_nodes}_{degree}", nx.random_regular_graph(degree, number_of_nodes, seed = 42)))
        
        # sudoku graphs
        for i in range(5):
            grid_size = i + 1
            instances.append((f"regular_sudoku_{grid_size}", nx.sudoku_graph([grid_size])))

        # dense graphs
        for i in range (10, 30):
            number_of_nodes = (i + 1) * 5
            number_of_edges = number_of_nodes * (number_of_nodes - 2) / 2
            instances.append((f"dense_{number_of_nodes}_{number_of_edges}",
                              nx.dense_gnm_random_graph(number_of_nodes, number_of_edges, seed = 42)))
        for i in range(20, 40):
            number_of_nodes = (i + 1) * 5
            number_of_edges = number_of_nodes * (number_of_nodes - 3) / 2
            instances.append((f"dense_{number_of_nodes}_{number_of_edges}",
                              nx.dense_gnm_random_graph(number_of_nodes, number_of_edges, seed = 42)))
        
        # greater instances
        for i in range(100, 110):
            number_of_nodes = (i + 1) * 4
            number_of_edges = number_of_nodes * (number_of_nodes - 3) / 2
            instances.append((f"dense_{number_of_nodes}_{number_of_edges}",
                              nx.dense_gnm_random_graph(number_of_nodes, number_of_edges, seed = 42)))

        # erdos_renyi_graphs (random)
        # erdos_renyi_graph(number of nodes, probability that an edge between two nodes exist, seed that garantee same graph for same input)
        # some overlap to other instance classes
        instances.append(("erdos30-0.1", nx.erdos_renyi_graph(30, 0.1, seed = 42)))
        instances.append(("erdos30-0.3", nx.erdos_renyi_graph(30, 0.3, seed = 42)))
        instances.append(("erdos30-0.5", nx.erdos_renyi_graph(30, 0.5, seed = 42)))
        instances.append(("erdos30-0.7", nx.erdos_renyi_graph(30, 0.7, seed = 42)))
        instances.append(("complete_erdos30-1", nx.erdos_renyi_graph(30, 1, seed = 42)))

        instances.append(("erdos55-0.5", nx.erdos_renyi_graph(55, 0.5, seed = 42)))
        instances.append(("erdos75-0.5", nx.erdos_renyi_graph(75, 0.5, seed = 42)))
        instances.append(("erdos100-0.1", nx.erdos_renyi_graph(100, 0.1, seed = 42)))
        instances.append(("erdos150-0.3", nx.erdos_renyi_graph(150, 0.3, seed = 42)))
        instances.append(("erdos200-0.1", nx.erdos_renyi_graph(200, 0.1, seed = 42)))

        instances.append(("erdos250-0.3", nx.erdos_renyi_graph(250, 0.3, seed = 42)))
        instances.append(("erdos300-0.4", nx.erdos_renyi_graph(300, 0.4, seed = 42)))
        instances.append(("erdos350-0.1", nx.erdos_renyi_graph(350, 0.1, seed = 42)))
        instances.append(("erdos400-0.05", nx.erdos_renyi_graph(400, 0.05, seed = 42)))
        instances.append(("erdos500-0.02", nx.erdos_renyi_graph(500, 0.02, seed = 42)))

        # erdos and dense graphs
        instances.append(("dense_erdos55-0.9", nx.erdos_renyi_graph(55, 0.9, seed = 42)))
        instances.append(("dense_erdos55-0.95", nx.erdos_renyi_graph(55, 0.95, seed = 42)))
        instances.append(("dense_erdos55-0.96", nx.erdos_renyi_graph(55, 0.96, seed = 42)))
        instances.append(("dense_erdos55-0.97", nx.erdos_renyi_graph(55, 0.97, seed = 42)))
        instances.append(("dense_erdos55-0.98", nx.erdos_renyi_graph(55, 0.98, seed = 42)))
        instances.append(("dense_erdos55-0.99", nx.erdos_renyi_graph(55, 0.99, seed = 42)))
        
        instances.append(("dense_erdos60-0.9", nx.erdos_renyi_graph(60, 0.9, seed = 42)))
        instances.append(("dense_erdos65-0.9", nx.erdos_renyi_graph(65, 0.9, seed = 42)))
        instances.append(("dense_erdos70-0.9", nx.erdos_renyi_graph(70, 0.9, seed = 42)))
        instances.append(("dense_erdos75-0.9", nx.erdos_renyi_graph(75, 0.9, seed = 42)))

        # barabasi_albert_graph (random) --> sequentielly adding of nodes with degree m
        # barabasi_alber_graph(number of nodes, edges added per new node, seed)
        # --> nodes with high degree --> DSATUR much better
        instances.append(("barabasi50-5", nx.barabasi_albert_graph(50, 5, seed = 42)))
        instances.append(("barabasi50-7", nx.barabasi_albert_graph(50, 7, seed = 42)))
        instances.append(("barabasi50-10", nx.barabasi_albert_graph(50, 10, seed = 42)))
        instances.append(("barabasi50-15", nx.barabasi_albert_graph(50, 15, seed = 42)))
        instances.append(("barabasi50-25", nx.barabasi_albert_graph(50, 25, seed = 42)))
        instances.append(("barabasi50-35", nx.barabasi_albert_graph(50, 35, seed = 42)))
        instances.append(("barabasi50-45", nx.barabasi_albert_graph(50, 45, seed = 42)))

        instances.append(("barabasi75-15", nx.barabasi_albert_graph(75, 15, seed = 42)))
        instances.append(("barabasi75-25", nx.barabasi_albert_graph(75, 25, seed = 42)))
        instances.append(("barabasi75-40", nx.barabasi_albert_graph(75, 40, seed = 42)))
        instances.append(("barabasi75-50", nx.barabasi_albert_graph(75, 50, seed = 42)))

        instances.append(("barabasi100-10", nx.barabasi_albert_graph(100, 10, seed = 42)))
        instances.append(("barabasi100-20", nx.barabasi_albert_graph(100, 20, seed = 42)))

        instances.append(("barabasi150-15", nx.barabasi_albert_graph(150, 15, seed = 42)))
        instances.append(("barabasi150-25", nx.barabasi_albert_graph(150, 25, seed = 42)))

        instances.append(("barabasi200-7", nx.barabasi_albert_graph(200, 7, seed = 42)))
        instances.append(("barabasi200-13", nx.barabasi_albert_graph(200, 13, seed = 42)))

        instances.append(("barabasi250-7", nx.barabasi_albert_graph(250, 7, seed = 42)))
        instances.append(("barabasi250-10", nx.barabasi_albert_graph(250, 10, seed = 42)))

        instances.append(("barabasi300-10", nx.barabasi_albert_graph(300, 10, seed = 42)))
        
        # kneser graph (classic, n > k > 0) --> highly symmetric, challenging for greedy
        # vertices = all subsets of n with exact k elements, edges = connections between disjoint subsets
        instances.append(("petersenGraph", nx.kneser_graph(5, 2)))
        instances.append(("kneser5-3", nx.kneser_graph(5, 3)))
        instances.append(("kneser5-4", nx.kneser_graph(5, 4)))

        instances.append(("kneser7-2", nx.kneser_graph(7, 2)))
        instances.append(("kneser7-3", nx.kneser_graph(7, 3)))
        instances.append(("kneser7-5", nx.kneser_graph(7, 5)))

        instances.append(("kneser9-3", nx.kneser_graph(9, 3)))
        instances.append(("kneser9-4", nx.kneser_graph(9, 4)))
        instances.append(("kneser9-5", nx.kneser_graph(9, 5)))
        instances.append(("kneser9-6", nx.kneser_graph(9, 6)))
        instances.append(("kneser9-7", nx.kneser_graph(9, 7)))

        instances.append(("kneser10-3", nx.kneser_graph(10, 3)))
        instances.append(("kneser10-5", nx.kneser_graph(10, 5)))
        instances.append(("kneser10-7", nx.kneser_graph(10, 7)))

        instances.append(("kneser13-4", nx.kneser_graph(13, 4)))
        instances.append(("kneser13-5", nx.kneser_graph(13, 5)))

        instances.append(("kneser14-4", nx.kneser_graph(14, 4)))
        instances.append(("kneser14-5", nx.kneser_graph(14, 5)))

        instances.append(("kneser15-2", nx.kneser_graph(15, 2)))
        instances.append(("kneser15-4", nx.kneser_graph(15, 3)))

        return instances

    @staticmethod
    def graph_classes():
        instances = Instances.generate_test_instances()
        classes = {
            "trivial": [name for name, i in instances if "trivial" in name],
            "regular": [name for name, i in instances if "regular" in name],
            "dense": [name for name, i in instances if "dense" in name],
            "erdos_renyi": [name for name, _ in instances if "erdos" in name],
            "barabasi": [name for name, _ in instances if "barabasi" in name],
            "kneser": [name for name, _ in instances if "kneser" in name or "petersenGraph" in name]
        }
        return classes