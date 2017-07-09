from nose.tools import assert_equal, assert_not_equal, \
        assert_true, assert_false, assert_raises

import networkx as nx


class test_graphview(object):
    def setUp(self):
        self.G = nx.path_graph(9)
        self.gview = nx.GraphView
        self.hide_nodes = [4, 5, 111]
        self.hide_edges = [(2, 3), (8, 7), (222, 223)]
        self.out_nodes = {4, 5}
        self.out_edges = {(3, 4), (4, 5), (5, 6)}

    def test_hidden_nodes(self):
        G = self.gview(self.G, self.hide_nodes, [])
        assert_equal(self.G.nodes - G.nodes, self.out_nodes)
        assert_equal(self.G.edges - G.edges, self.out_edges)
        if G.is_directed():
            assert_equal(list(G[3]), [])
            assert_equal(list(G[2]), [3])
        else:
            assert_equal(list(G[3]), [2])
            assert_equal(set(G[2]), {1, 3})
        assert_raises(KeyError, G.__getitem__, 4)
        assert_raises(KeyError, G.__getitem__, 112)
        assert_raises(KeyError, G.__getitem__, 111)
        assert_equal(G.degree(3), 1)
        assert_equal(G.size(), 5)

    def test_hidden_edges(self):
        G = self.gview(self.G, [], self.hide_edges)
        assert_equal(self.G.nodes, G.nodes)
        if G.is_directed():
            assert_equal(self.G.edges - G.edges, {(2, 3)})
            assert_equal(list(G[3]), [4])
            assert_equal(list(G[2]), [])
            assert_equal(list(G.pred[3]), [])
            assert_equal(list(G.pred[2]), [1])
            assert_equal(G.size(), 7)
        else:
            assert_equal(self.G.edges - G.edges, {(2, 3), (7, 8)})
            assert_equal(list(G[3]), [4])
            assert_equal(list(G[2]), [1])
            assert_equal(G.size(), 6)
        assert_raises(KeyError, G.__getitem__, 221)
        assert_raises(KeyError, G.__getitem__, 222)
        assert_equal(G.degree(3), 1)


class test_digraphview(test_graphview):
    def setUp(self):
        self.G = nx.path_graph(9, create_using=nx.DiGraph())
        self.gview = nx.DiGraphView
        self.hide_nodes = [4, 5, 111]
        self.hide_edges = [(2, 3), (8, 7), (222, 223)]
        self.out_nodes = {4, 5}
        self.out_edges = {(3, 4), (4, 5), (5, 6)}

    def test_inoutedges(self):
        G = self.gview(self.G, self.hide_nodes, self.hide_edges)
        excluded = {(2, 3), (3, 4), (4, 5), (5, 6)}
        assert_equal(self.G.in_edges - G.in_edges, excluded)
        assert_equal(self.G.out_edges - G.out_edges, excluded)

    def test_pred(self):
        G = self.gview(self.G, self.hide_nodes, self.hide_edges)
        assert_equal(list(G.pred[2]), [1])
        assert_equal(list(G.pred[6]), [])

    def test_inout_degree(self):
        G = self.gview(self.G, self.hide_nodes, self.hide_edges)
        assert_equal(G.degree(2), 1)
        assert_equal(G.out_degree(2), 0)
        assert_equal(G.in_degree(2), 1)
        assert_equal(G.size(), 4)


# multigraph
class test_multigraphview(test_graphview):
    def setUp(self):
        self.G = nx.path_graph(9, create_using=nx.MultiGraph())
        multiedges = {(2, 3, 4), (2, 3, 5)}
        self.G.add_edges_from(multiedges)
        self.gview = nx.MultiGraphView
        self.hide_nodes = [4, 5, 111]
        self.hide_edges = [(2, 3, 4), (2, 3, 3), (8, 7, 0), (222, 223, 0)]
        self.out_nodes = {4, 5}
        self.out_edges = multiedges | {(3, 4, 0), (4, 5, 0), (5, 6, 0)}

    def test_hidden_edges(self):
        G = self.gview(self.G, [], self.hide_edges)
        assert_equal(self.G.nodes, G.nodes)
        if G.is_directed():
            assert_equal(self.G.edges - G.edges, {(2, 3, 4)})
            assert_equal(list(G[3]), [4])
            assert_equal(list(G[2]), [3])
            assert_equal(list(G.pred[3]), [2])  # only one 2 but two edges
            assert_equal(list(G.pred[2]), [1])
            assert_equal(G.size(), 9)
            assert_equal(G.degree(3), 3)
        else:
            assert_equal(self.G.edges - G.edges, {(2, 3, 4), (7, 8, 0)})
            assert_equal(list(G[3]), [2, 4])
            assert_equal(list(G[2]), [1, 3])
            assert_equal(G.size(), 8)
            assert_equal(G.degree(3), 3)
        assert_raises(KeyError, G.__getitem__, 221)
        assert_raises(KeyError, G.__getitem__, 222)


# multidigraph
class test_multidigraphview(test_multigraphview):
    def setUp(self):
        self.G = nx.path_graph(9, create_using=nx.MultiDiGraph())
        multiedges = {(2, 3, 4), (2, 3, 5)}
        self.G.add_edges_from(multiedges)
        self.gview = nx.MultiDiGraphView
        self.hide_nodes = [4, 5, 111]
        self.hide_edges = [(2, 3, 4), (2, 3, 3), (8, 7, 0), (222, 223, 0)]
        self.out_nodes = {4, 5}
        self.out_edges = multiedges | {(3, 4, 0), (4, 5, 0), (5, 6, 0)}
