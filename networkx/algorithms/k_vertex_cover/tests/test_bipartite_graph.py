import networkx as nx
from networkx.algorithms import bipartite
from networkx.algorithms.k_vertex_cover.test_helper_functions import (
    check_vertex_cover,
)


class TestBipartiteGraph:
    def test_vertex_cover(self):
        G = nx.path_graph(5)
        self.check(G)

        G = nx.path_graph(6)
        self.check(G)

        G = nx.complete_bipartite_graph(5, 6)
        self.check(G)

        G = bipartite.random_graph(3, 6, 0.2)
        self.check(G)

    def check(self, G):
        for k in range(len(G) + 1):
            check_vertex_cover(G, k)


if __name__ == "__main__":
    test_class = TestBipartiteGraph()
    test_class.test_vertex_cover()
