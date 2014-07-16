from nose.tools import *

import networkx as nx
edge_dfs = nx.algorithms.edge_dfs
FORWARD = nx.algorithms.edgedfs.FORWARD
REVERSE = nx.algorithms.edgedfs.REVERSE

class TestEdgeDFS(object):
    def setUp(self):
        self.nodes = [0, 1, 2, 3]
        self.edges = [(0, 1), (1, 0), (1, 0), (2, 1), (3, 1)]

    def test_empty(self):
        G = nx.Graph()
        edges = list(edge_dfs(G))
        assert_equal(edges, [])

    def test_graph(self):
        G = nx.Graph(self.edges)
        x = list(edge_dfs(G, self.nodes))
        x_ = [(0, 1), (1, 2), (1, 3)]
        assert_equal(x, x_)

    def test_digraph(self):
        G = nx.DiGraph(self.edges)
        x = list(edge_dfs(G, self.nodes))
        x_= [(0, 1), (1, 0), (2, 1), (3, 1)]
        assert_equal(x, x_)

    def test_digraph_rev(self):
        G = nx.DiGraph(self.edges)
        x = list(edge_dfs(G, self.nodes, orientation='reverse'))
        x_= [(1, 0, REVERSE), (0, 1, REVERSE),
             (2, 1, REVERSE), (3, 1, REVERSE)]
        assert_equal(x, x_)

    def test_multigraph(self):
        G = nx.MultiGraph(self.edges)
        x = list(edge_dfs(G, self.nodes))
        x_ = [(0, 1, 0), (1, 0, 1), (0, 1, 2), (1, 2, 0), (1, 3, 0)]
        assert_equal(x, x_)

    def test_multidigraph(self):
        G = nx.MultiDiGraph(self.edges)
        x = list(edge_dfs(G, self.nodes))
        x_ = [(0, 1, 0), (1, 0, 0), (1, 0, 1), (2, 1, 0), (3, 1, 0)]
        assert_equal(x, x_)

    def test_multidigraph_rev(self):
        G = nx.MultiDiGraph(self.edges)
        x = list(edge_dfs(G, self.nodes, orientation='reverse'))
        x_ = [(1, 0, 0, REVERSE),
              (1, 0, 1, REVERSE),
              (0, 1, 0, REVERSE),
              (2, 1, 0, REVERSE),
              (3, 1, 0, REVERSE)]
        assert_equal(x, x_)

    def test_digraph_ignore(self):
        G = nx.DiGraph(self.edges)
        x = list(edge_dfs(G, self.nodes, orientation='ignore'))
        x_ = [(0, 1, FORWARD), (1, 0, FORWARD),
              (2, 1, REVERSE), (3, 1, REVERSE)]
        assert_equal(x, x_)

    def test_multidigraph_ignore(self):
        G = nx.MultiDiGraph(self.edges)
        x = list(edge_dfs(G, self.nodes, orientation='ignore'))
        x_ = [(0, 1, 0, FORWARD), (1, 0, 0, FORWARD),
              (1, 0, 1, REVERSE), (2, 1, 0, REVERSE),
              (3, 1, 0, REVERSE)]
        assert_equal(x, x_)


