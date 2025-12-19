import networkx as nx

class DegreeBasedPreprocessor:
    """
    A preprocessor that removes low-degree vertices from the graph.
    This needs to be a class as it maintains state between the preprocessing and postprocessing steps.
    """
    def __init__(self, graph: nx.Graph):
        self.graph = graph  # the original graph

        # find maximal clique in the graph and use this as lower bound

        self.lower_bound = nx.large_clique_size(graph)

    def preprocess(self) -> nx.Graph:
        """
        Return a preprocessed graph.
        """

        # store the vertex with its neighbors at removal time
        self.stack = []

        # init --> initial node degrees and neighbors
        for v, deg in self.graph.degree():
            print(v, deg)
            self.neighbors = list(self.graph.neighbors(v))

        while True:
            removable = None
            for v in self.graph.nodes:
                if self.graph.degree(v) <= self.lower_bound - 1:
                    removable = v
                    break

            if removable is None:
                break  # no more vertices can be removed

            neighbors = list(self.graph.neighbors(removable))
            self.stack.append((removable, neighbors))
            self.graph.remove_node(removable)


    def postprocess(self, coloring: dict, lower_bound: int) -> tuple[dict, int]:
        """
        Convert a solution for the reduced graph back to the original graph.
        As we are also interested in the lower bound, also pass it through.
        """
        pass