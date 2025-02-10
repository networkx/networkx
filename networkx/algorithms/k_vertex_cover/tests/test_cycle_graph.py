import networkx as nx
from networkx.algorithms.k_vertex_cover.test_helper_functions import (
    check_vertex_cover,
)


class TestCycleGraph:
    def test_vertex_cover(self):
        G = nx.cycle_graph(4)
        self.check(G)

        G = nx.cycle_graph(5)
        self.check(G)

    def check(self, G):
        for k in range(len(G) + 1):
            check_vertex_cover(G, k)


if __name__ == "__main__":
    test_class = TestCycleGraph()
    test_class.test_vertex_cover()
