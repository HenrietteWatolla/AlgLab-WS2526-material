import networkx as nx

class Instances:
    @staticmethod
    # store instances in list
    def generate_test_instances():
        instances = []

        # complete graphs --> number of vertices = minimal number of colors
        instances.append(("K3", nx.complete_graph(3)))
        instances.append(("K4", nx.complete_graph(4)))
        instances.append(("K23", nx.complete_graph(23)))

        # bipartite graphs --> only two colors necessary
        instances.append(("bipartite3-5", nx.complete_bipartite_graph(3, 5)))
        instances.append(("bipartite1-7", nx.complete_bipartite_graph(1, 7)))
        instances.append(("bipartite9-4", nx.complete_bipartite_graph(9, 4)))

        # cycle graphs (2 colors for even, 3 colors for odd cycles)
        instances.append(("cycleEven", nx.cycle_graph(24)))
        instances.append(("cycleOdd", nx.cycle_graph(25)))

        # paths --> two colors
        instances.append(("path1", nx.path_graph(19)))
        instances.append(("path2", nx.path_graph(35)))

        # erdos_renyi_graphs (random)
        # erdos_renyi_graph(number of nodes, probability that an edge between two nodes exist, seed that garantee same graph for same input)
        instances.append(("erdos30-0.1-42", nx.erdos_renyi_graph(30, 0.1, seed = 42)))
        instances.append(("erdos30-0.3-42", nx.erdos_renyi_graph(30, 0.3, seed = 42)))
        instances.append(("erdos30-0.5-42", nx.erdos_renyi_graph(30, 0.5, seed = 42)))
        instances.append(("erdos30-0.7-42", nx.erdos_renyi_graph(30, 0.7, seed = 42)))
        #instances.append(("erdos30-0.5-13", nx.erdos_renyi_graph(30, 0.5, seed = 13)))
        #instances.append(("erdos30-0.5-33", nx.erdos_renyi_graph(30, 0.5, seed = 33)))
        #instances.append(("erdos30-2-1", nx.erdos_renyi_graph(30, 1, seed = 1)))
        #instances.append(("erdos55-0.9-42", nx.erdos_renyi_graph(55, 0.9, seed = 42)))
        #instances.append(("erdos100-2-42", nx.erdos_renyi_graph(100, 0.1, seed = 42)))
        #instances.append(("erdos150-5-42", nx.erdos_renyi_graph(150, 0.3, seed = 42)))

        # barabasi_albert_graph (random) --> sequentielly adding of nodes with degree m
        # barabasi_alber_graph(number of nodes, edges added per new node, seed)
        # --> nodes with high degree --> DSATUR much better
        instances.append(("barabasi50-2-42", nx.barabasi_albert_graph(50, 2, seed = 42)))
        instances.append(("barabasi50-3-42", nx.barabasi_albert_graph(50, 3, seed = 42)))
        instances.append(("barabasi50-4-42", nx.barabasi_albert_graph(50, 4, seed = 42)))
        instances.append(("barabasi50-10-42", nx.barabasi_albert_graph(50, 10, seed = 42)))
        #instances.append(("barabasi100-10-13", nx.barabasi_albert_graph(100, 10, seed = 13)))
        #instances.append(("barabasi100-10-20", nx.barabasi_albert_graph(100, 10, seed = 20)))
        #instances.append(("barabasi100-10-42", nx.barabasi_albert_graph(100, 10, seed = 42)))
        #instances.append(("barabasi100-10-55", nx.barabasi_albert_graph(100, 10, seed = 55)))
        #instances.append(("barabasi100-25-55", nx.barabasi_albert_graph(100, 25, seed = 55)))
        #instances.append(("barabasi150-33-66", nx.barabasi_albert_graph(150, 33, seed = 66)))

        # kneser graph (classic, n > k > 0) --> highly symmetric, challenging for greedy
        instances.append(("petersenGraph", nx.kneser_graph(5, 2)))
        instances.append(("kneser9-4", nx.kneser_graph(9, 4)))
        instances.append(("kneser10-3", nx.kneser_graph(10, 3)))
        instances.append(("kneser10-5", nx.kneser_graph(10, 5)))
        #instances.append(("kneser13-4", nx.kneser_graph(13, 4)))
        #instances.append(("kneser13-5", nx.kneser_graph(13, 5)))
        #instances.append(("kneser14-4", nx.kneser_graph(14, 4)))
        #instances.append(("kneser14-5", nx.kneser_graph(14, 5)))
        #instances.append(("kneser15-2", nx.kneser_graph(15, 2)))
        #instances.append(("kneser15-4", nx.kneser_graph(15, 4)))
        # boss level
        #instances.append(("kneser15-5", nx.kneser_graph(15, 5)))

        return instances

    @staticmethod
    def graph_classes():
        instances = Instances.generate_test_instances()
        classes = {
            "complete": [name for name, _ in instances if "K" in name],
            "bipartite": [name for name, _ in instances if "bipartite" in name],
            "cycle": [name for name, _ in instances if "cycle" in name],
            "path": [name for name, _ in instances if "path" in name],
            "erdos_renyi": [name for name, _ in instances if "erdos" in name],
            "barabasi": [name for name, _ in instances if "barabasi" in name],
            "kneser": [name for name, _ in instances if "kneser" in name or "petersenGraph" in name]
        }
        return classes