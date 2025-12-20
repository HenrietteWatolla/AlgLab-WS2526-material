import networkx as nx
import os

class Instances:

    """
    # used for benchmarking the heuristics
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
        instances.append((f"regular_sudoku_3", nx.sudoku_graph(3)))

        # dense graphs
        for i in range (10, 30):
            number_of_nodes = (i + 1) * 5
            number_of_edges = number_of_nodes * (number_of_nodes - 2) // 2
            instances.append((f"dense_{number_of_nodes}_{number_of_edges}",
                              nx.dense_gnm_random_graph(number_of_nodes, number_of_edges, seed = 42)))
        for i in range(20, 40):
            number_of_nodes = (i + 1) * 5
            number_of_edges = number_of_nodes * (number_of_nodes - 3) // 2
            instances.append((f"dense_{number_of_nodes}_{number_of_edges}",
                              nx.dense_gnm_random_graph(number_of_nodes, number_of_edges, seed = 42)))
        
        # greater instances
        for i in range(100, 110):
            number_of_nodes = (i + 1) * 4
            number_of_edges = number_of_nodes * (number_of_nodes - 3) // 2
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
        """
    
    # used for benchmarking the solvers (due to time constraints less instances)
    @staticmethod
    # store instances in list
    def generate_test_instances():
        instances = []

        # trivial instances
        # complete graphs --> number of vertices = minimal number of colors
        instances.append(("trivial_K23", nx.complete_graph(23)))
        instances.append(("trivial_K100", nx.complete_graph(100)))

        # bipartite graphs --> only two colors necessary
        instances.append(("trivial_bipartite100-150", nx.complete_bipartite_graph(100, 150)))

        # cycle graphs (2 colors for even, 3 colors for odd cycles)
        instances.append(("trivial_cycleEven", nx.cycle_graph(100)))
        instances.append(("trivial_cycleOdd", nx.cycle_graph(101)))

        # paths --> two colors
        instances.append(("trivial_path2", nx.path_graph(103)))

        # non-trivial instances
        # regular graphs

        instances.append((f"regular_20-100-42", nx.random_regular_graph(20, 100, seed = 42)))
        instances.append((f"regular_20-150-30", nx.random_regular_graph(20, 150, seed = 30)))
        instances.append((f"regular_100-200-15", nx.random_regular_graph(100, 200, seed = 15)))
        instances.append((f"regular_110-210-20", nx.random_regular_graph(110, 210, seed = 20)))
        instances.append((f"regular_110-220-17", nx.random_regular_graph(110, 220, seed = 17)))

        instances.append((f"regular_115-230-9", nx.random_regular_graph(115, 230, seed = 9)))
        instances.append((f"regular_120-240-13", nx.random_regular_graph(120, 240, seed = 13)))
        instances.append((f"regular_120-250-4", nx.random_regular_graph(120, 250, seed = 4)))
        instances.append((f"regular_130-260-33", nx.random_regular_graph(130, 260, seed = 33)))
        instances.append((f"regular_130-270-47", nx.random_regular_graph(130, 270, seed = 47)))

        instances.append((f"regular_140-280-29", nx.random_regular_graph(140, 280, seed = 29)))
        instances.append((f"regular_140-290-23", nx.random_regular_graph(140, 290, seed = 23)))
        instances.append((f"regular_150-300-7", nx.random_regular_graph(150, 300, seed = 7)))
        instances.append((f"regular_175-350-19", nx.random_regular_graph(175, 350, seed = 19)))

        # sudoku graph
        instances.append((f"regular_sudoku_3", nx.sudoku_graph(3)))

        # dense graphs

        instances.append((f"dense_200-10000-42", nx.dense_gnm_random_graph(200, 10000, seed = 42)))
        instances.append((f"dense_210-10000-30", nx.dense_gnm_random_graph(210, 10000, seed = 30)))
        instances.append((f"dense_220-10000-15", nx.dense_gnm_random_graph(220, 10000, seed = 15)))
        instances.append((f"dense_230-10000-20", nx.dense_gnm_random_graph(230, 10000, seed = 20)))
        instances.append((f"dense_240-10000-17", nx.dense_gnm_random_graph(240, 10000, seed = 17)))

        instances.append((f"dense_250-10000-9", nx.dense_gnm_random_graph(250, 10000, seed = 9)))
        instances.append((f"dense_260-10000-13", nx.dense_gnm_random_graph(260, 10000, seed = 13)))
        instances.append((f"dense_270-10000-4", nx.dense_gnm_random_graph(270, 10000, seed = 4)))
        instances.append((f"dense_280-10000-33", nx.dense_gnm_random_graph(280, 10000, seed = 33)))
        instances.append((f"dense_290-15000-47", nx.dense_gnm_random_graph(290, 15000, seed = 47)))

        instances.append((f"dense_300-15000-29", nx.dense_gnm_random_graph(300, 15000, seed = 29)))
        instances.append((f"dense_350-16000-23", nx.dense_gnm_random_graph(350, 16000, seed = 23)))
        instances.append((f"dense_400-20000-7", nx.dense_gnm_random_graph(400, 20000, seed = 7)))
        instances.append((f"dense_450-22000-19", nx.dense_gnm_random_graph(450, 22000, seed = 19)))
        instances.append((f"dense_450-30000-25", nx.dense_gnm_random_graph(450, 30000, seed = 25)))

        # erdos_renyi_graphs (random)
        # erdos_renyi_graph(number of nodes, probability that an edge between two nodes exist, seed that garantee same graph for same input)
        # some overlap to other instance classes
        instances.append(("erdos30-0.1-42", nx.erdos_renyi_graph(30, 0.1, seed = 42)))
        instances.append(("erdos30-0.3-42", nx.erdos_renyi_graph(30, 0.3, seed = 42)))
        instances.append(("erdos30-0.5-42", nx.erdos_renyi_graph(30, 0.5, seed = 42)))
        instances.append(("erdos30-0.7-42", nx.erdos_renyi_graph(30, 0.7, seed = 42)))
        instances.append(("dense_erdos30-0.9-42", nx.erdos_renyi_graph(30, 0.9, seed = 42)))

        instances.append(("erdos55-0.5-10", nx.erdos_renyi_graph(55, 0.5, seed = 10)))
        instances.append(("erdos75-0.5-13", nx.erdos_renyi_graph(75, 0.5, seed = 13)))
        instances.append(("erdos100-0.1-23", nx.erdos_renyi_graph(100, 0.1, seed = 23)))
        instances.append(("erdos150-0.3-27", nx.erdos_renyi_graph(150, 0.3, seed = 27)))
        instances.append(("erdos200-0.1-35", nx.erdos_renyi_graph(200, 0.1, seed = 35)))

        instances.append(("erdos250-0.3-39", nx.erdos_renyi_graph(250, 0.3, seed = 39)))
        instances.append(("erdos300-0.4-42", nx.erdos_renyi_graph(300, 0.4, seed = 42)))
        instances.append(("erdos350-0.1-17", nx.erdos_renyi_graph(350, 0.1, seed = 17)))
        instances.append(("erdos400-0.05-29", nx.erdos_renyi_graph(400, 0.05, seed = 29)))
        instances.append(("erdos500-0.02-36", nx.erdos_renyi_graph(500, 0.02, seed = 36)))

        # erdos and dense graphs
        instances.append(("dense_erdos55-0.9-17", nx.erdos_renyi_graph(55, 0.9, seed = 17)))
        instances.append(("dense_erdos55-0.95-19", nx.erdos_renyi_graph(55, 0.95, seed = 19)))
        instances.append(("dense_erdos55-0.96-21", nx.erdos_renyi_graph(55, 0.96, seed = 21)))
        instances.append(("dense_erdos55-0.97-27", nx.erdos_renyi_graph(55, 0.97, seed = 27)))
        instances.append(("dense_erdos55-0.98-33", nx.erdos_renyi_graph(55, 0.98, seed = 33)))

        instances.append(("dense_erdos55-0.99-35", nx.erdos_renyi_graph(55, 0.99, seed = 35)))
        instances.append(("dense_erdos60-0.9-37", nx.erdos_renyi_graph(60, 0.9, seed = 37)))
        instances.append(("dense_erdos65-0.9-41", nx.erdos_renyi_graph(65, 0.9, seed = 41)))
        instances.append(("dense_erdos70-0.9-42", nx.erdos_renyi_graph(70, 0.9, seed = 42)))
        instances.append(("dense_erdos75-0.9-53", nx.erdos_renyi_graph(75, 0.9, seed = 53)))

        # barabasi_albert_graph (random) --> sequentielly adding of nodes with degree m
        # barabasi_alber_graph(number of nodes, edges added per new node, seed)
        # --> nodes with high degree --> DSATUR much better
        instances.append(("barabasi50-5-42", nx.barabasi_albert_graph(50, 5, seed = 42)))
        instances.append(("barabasi50-30-17", nx.barabasi_albert_graph(50, 30, seed = 17)))
        instances.append(("barabasi50-45-29", nx.barabasi_albert_graph(50, 45, seed = 29)))

        instances.append(("barabasi75-15-42", nx.barabasi_albert_graph(75, 15, seed = 42)))
        instances.append(("barabasi75-40-13", nx.barabasi_albert_graph(75, 40, seed = 13)))
        instances.append(("barabasi75-50-38", nx.barabasi_albert_graph(75, 50, seed = 38)))

        instances.append(("barabasi100-10-42", nx.barabasi_albert_graph(100, 10, seed = 42)))
        instances.append(("barabasi100-20-19", nx.barabasi_albert_graph(100, 20, seed = 19)))
        instances.append(("barabasi150-15-42", nx.barabasi_albert_graph(150, 15, seed = 42)))
        instances.append(("barabasi150-25-33", nx.barabasi_albert_graph(150, 25, seed = 33)))

        instances.append(("barabasi200-7-17", nx.barabasi_albert_graph(200, 7, seed = 17)))
        instances.append(("barabasi200-13-29", nx.barabasi_albert_graph(200, 13, seed = 29)))
        instances.append(("barabasi250-7-15", nx.barabasi_albert_graph(250, 7, seed = 15)))
        instances.append(("barabasi250-33-39", nx.barabasi_albert_graph(250, 33, seed = 39)))
        instances.append(("barabasi300-100-42", nx.barabasi_albert_graph(300, 100, seed = 42)))
        
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
        instances.append(("kneser15-3", nx.kneser_graph(15, 3)))

        # add dimacs instances
        instances.extend(Instances.load_dimacs_instances())

        return instances

    # load DIMACS instances
    def load_dimacs_col(filepath):
        G = nx.Graph()

        with open(filepath) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("c"):
                    continue

                if line.startswith("p"):
                    i, i, n, i = line.split()
                    G.add_nodes_from(range(1, int(n) + 1))

                elif line.startswith("e"):
                    i, u, v = line.split()
                    G.add_edge(int(u), int(v))
        return G
    
    # get the dimacs instances

    @staticmethod
    def load_dimacs_instances():

        base_dir = os.path.dirname(os.path.abspath(__file__))
        dimacs_dir = os.path.join(base_dir, "..", "dimacs")

        dimacs_files = [

            # mycielski (high chromatic, triangle-free)
            "myciel3.col", "myciel4.col", "myciel5.col",
            "myciel6.col", "myciel7.col",

            # queens graphs (structured and symmetric)
            "queen5_5.col", "queen6_6.col", "queen7_7.col",
            "queen8_8.col", "queen9_9.col", "queen10_10.col",

            # leighton graphs (classic communication networks)
            "le450_5a.col", "le450_5b.col",
            "le450_15a.col", "le450_15b.col",

            # miles graphs
            "miles250.col", "miles500.col",
        ]

        instances = []
        for file in dimacs_files:
            path = os.path.join(dimacs_dir, file)
            G = Instances.load_dimacs_col(path)
            name = file.replace(".col", "")
            instances.append((f"DIMACS_{name}", G))

        return instances


    @staticmethod
    def graph_classes():
        instances = Instances.generate_test_instances()
        classes = {
            "trivial": [name for name, i in instances if "trivial" in name],
            "regular": [name for name, i in instances if "regular" in name],
            "dense": [name for name, i in instances if "dense" in name],
            "erdos_renyi": [name for name, i in instances if "erdos" in name],
            "barabasi": [name for name, i in instances if "barabasi" in name],
            "kneser": [name for name, i in instances if "kneser" in name or "petersenGraph" in name],
            "dimacs": [name for name, _ in instances if name.startswith("DIMACS_")]
        }
        return classes
    
if __name__ == "__main__":
    print("RUN GETTING INSTANCES")
    instances = Instances.generate_test_instances()
    print(len(instances))

    for name, G in instances:
        assert G.number_of_nodes() > 0, name
    for cls, names in Instances.graph_classes().items():
        print(cls, len(names))
