from nose.tools import assert_equal
import networkx as nx


class TestBFS:

    def setUp(self):
        # simple graph
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4)])
        self.G = G

    def test_successor(self):
        assert_equal(dict(nx.bfs_successors(self.G, source=0)),
                     {0: [1], 1: [2, 3], 2: [4]})

    def test_predecessor(self):
        assert_equal(dict(nx.bfs_predecessors(self.G, source=0)),
                     {1: 0, 2: 1, 3: 1, 4: 2})

    def test_bfs_tree(self):
        T = nx.bfs_tree(self.G, source=0)
        assert_equal(sorted(T.nodes()), sorted(self.G.nodes()))
        assert_equal(sorted(T.edges()), [(0, 1), (1, 2), (1, 3), (2, 4)])

    def test_bfs_edges(self):
        edges = nx.bfs_edges(self.G, source=0)
        assert_equal(list(edges), [(0, 1), (1, 2), (1, 3), (2, 4)])

    def test_bfs_edges_reverse(self):
        D = nx.DiGraph()
        D.add_edges_from([(0, 1), (1, 2), (1, 3), (2, 4), (3, 4)])
        edges = nx.bfs_edges(D, source=4, reverse=True)
        assert_equal(list(edges), [(4, 2), (4, 3), (2, 1), (1, 0)])

    def test_bfs_tree_isolates(self):
        G = nx.Graph()
        G.add_node(1)
        G.add_node(2)
        T = nx.bfs_tree(G, source=1)
        assert_equal(sorted(T.nodes()), [1])
        assert_equal(sorted(T.edges()), [])


class TestBreadthLimitedSearch:

    def setUp(self):
        # a tree
        G = nx.Graph()
        nx.add_path(G, [0, 1, 2, 3, 4, 5, 6])
        nx.add_path(G, [2, 7, 8, 9, 10])
        self.G = G
        # a disconnected graph
        D = nx.Graph()
        D.add_edges_from([(0, 1), (2, 3)])
        nx.add_path(D, [2, 7, 8, 9, 10])
        self.D = D

    def bfs_test_successor(self):
        assert_equal(dict(nx.bfs_successors(self.G, source=1, depth_limit=3)),
                     {1: [0, 2], 2: [3, 7], 3: [4], 7: [8]})
        result = {n: sorted(s) for n, s in nx.bfs_successors(self.D, source=7,
                                                             depth_limit=2)}
        assert_equal(result, {8: [9], 2: [3], 7: [2, 8]})

    def bfs_test_predecessor(self):
        assert_equal(dict(nx.bfs_predecessors(self.G, source=1,
                                              depth_limit=3)),
                     {0: 1, 2: 1, 3: 2, 4: 3, 7: 2, 8: 7})
        assert_equal(dict(nx.bfs_predecessors(self.D, source=7,
                                              depth_limit=2)),
                     {2: 7, 3: 2, 8: 7, 9: 8})

    def bfs_test_tree(self):
        T = nx.bfs_tree(self.G, source=3, depth_limit=1)
        assert_equal(sorted(T.edges()), [(3, 2), (3, 4)])

    def bfs_test_edges(self):
        edges = nx.bfs_edges(self.G, source=9, depth_limit=4)
        assert_equal(list(edges), [(9, 8), (9, 10), (8, 7),
                                   (7, 2), (2, 1), (2, 3)])
