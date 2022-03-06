import networkx as nx
from itertools import permutations


class GraphBenchmark:
    def setup(self):
        self.nodes = list(range(1, 1000))
        self.edges = list()
        self.subgraph_nodes = list(range(1, 100))
        self.subgraph_nodes_large = list(range(1, 900))
        self.G = nx.Graph()

    # Create a Graph object
    def time_graph_create(self):
        _ = nx.Graph()
    # Add multiple nodes
    def time_add_nodes_from(self):
        self.G.add_nodes_from(self.nodes)

    # Add multiple edges
    def time_add_edges_from(self):
        self.G.add_edges_from(self.edges)

    # remove_nodes_from
    def time_remove_nodes_from(self):
        self.G.remove_nodes_from(self.nodes)

    # remove_edges_from
    def time_remove_edges_from(self):
        self.G.remove_edges_from(self.edges)

    # copy
    def time_copy(self):
        _ = self.G.copy()

    def time_to_directed(self):
        _ = self.G.to_directed()

    def time_to_undirected(self):
        _ = self.G.to_undirected()

    def time_subgraph(self):
        _ = self.G.subgraph(self.subgraph_nodes).copy()

    def time_subgraph_large(self):
        _ = self.G.subgraph(self.subgraph_nodes_large).copy()

