import networkx as nx
from networkx.algorithms.approximation.steinertree import steiner_tree
from networkx.utils import edges_equal


class TestSteinerTree:
    @classmethod
    def setup_class(cls):
        G = nx.Graph()
        G.add_edge(1, 2, weight=10)
        G.add_edge(2, 3, weight=10)
        G.add_edge(3, 4, weight=10)
        G.add_edge(4, 5, weight=10)
        G.add_edge(5, 6, weight=10)
        G.add_edge(2, 7, weight=1)
        G.add_edge(7, 5, weight=1)
        cls.G = G
        cls.term_nodes = [1, 2, 3, 4, 5]


    def test_steiner_tree(self):
        S = steiner_tree(self.G, self.term_nodes)
        expected_steiner_tree = [
            (1, 2, {"weight": 10}),
            (2, 3, {"weight": 10}),
            (2, 7, {"weight": 1}),
            (3, 4, {"weight": 10}),
            (5, 7, {"weight": 1}),
        ]
        assert edges_equal(list(S.edges(data=True)), expected_steiner_tree)

    def test_multigraph_steiner_tree(self):
        G = nx.MultiGraph()
        G.add_edges_from(
            [
                (1, 2, 0, {"weight": 1}),
                (2, 3, 0, {"weight": 999}),
                (2, 3, 1, {"weight": 1}),
                (3, 4, 0, {"weight": 1}),
                (3, 5, 0, {"weight": 1}),
            ]
        )
        terminal_nodes = [2, 4, 5]
        expected_edges = [
            (2, 3, 1, {"weight": 1}),  # edge with key 1 has lower weight
            (3, 4, 0, {"weight": 1}),
            (3, 5, 0, {"weight": 1}),
        ]
        T = steiner_tree(G, terminal_nodes)
        assert edges_equal(T.edges(data=True, keys=True), expected_edges)
