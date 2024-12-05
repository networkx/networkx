import networkx as nx
from networkx.algorithms.k_vertex_cover.test_helper_functions import (
    check_vertex_cover,
)
from networkx.generators import random_graphs


class TestRandomGraph:
    def test_vertex_cover(self):
        G = random_graphs.erdos_renyi_graph(5, 0.3)
        self.check(G)

        G = random_graphs.erdos_renyi_graph(4, 0.5)
        self.check(G)

        G = random_graphs.erdos_renyi_graph(5, 0.7)
        self.check(G)

    def check(self, G):
        for k in range(len(G) + 1):
            check_vertex_cover(G, k)


if __name__ == "__main__":
    test_class = TestRandomGraph()
    test_class.test_vertex_cover()
