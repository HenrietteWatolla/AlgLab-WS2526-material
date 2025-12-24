import networkx as nx
from networkx.algorithms.approximation import large_clique_size

class DegreeBasedPreprocessor:
    """
    A preprocessor that removes low-degree vertices from the graph.
    This needs to be a class as it maintains state between the preprocessing and postprocessing steps.
    """
    def __init__(self, graph: nx.Graph):
        self.original_graph = graph  # the original graph

        # find maximal clique in the graph and use this as lower bound
        self.lower_bound = large_clique_size(graph)
        self.stack = []  # store vertex with its neighbors at removal time

    def preprocess(self) -> nx.Graph:
        """
        Return a preprocessed graph.
        """
        G = self.original_graph.copy()

        changed = True
        while changed:
            changed = False
            for v in list(G.nodes()):
                
                # find vertices with low degree and delete them
                if G.degree(v) <= self.lower_bound - 1:
                    neighbors = list(G.neighbors(v))
                    self.stack.append((v, neighbors))
                    G.remove_node(v)
                    changed = True
                    break  # restart iteration after modification

        self.reduced_graph = G
        return G

    def postprocess(self, coloring: dict, lower_bound: int) -> tuple[dict, int, int]:
        """
        Convert a solution for the reduced graph back to the original graph.
        As we are also interested in the lower bound, also pass it through.
        """

        coloring = coloring.copy()

        # reinsert vertices in reverse removal order
        while self.stack:
            v, neighbors = self.stack.pop()

            used_colors = {
                coloring[u]
                for u in self.original_graph.neighbors(v) # work on original graph to realize the current drawing
                if u in coloring
            }

            # assign smallest available color
            color = 0
            while color in used_colors:
                color += 1

            coloring[v] = color

        # number of used colors
        num_colors = max(coloring.values()) + 1 if coloring else 0

        lower_bound = max(lower_bound, self.lower_bound)

        return coloring, num_colors, lower_bound
