from nose.tools import assert_equal, assert_not_equal, \
        assert_true, assert_false, assert_raises

import networkx as nx


class test_graphview(object):
    hide_edges_filter = staticmethod(nx.filters.hide_edges)
    show_edges_filter = staticmethod(nx.filters.show_edges)

    def setUp(self):
        self.gview = nx.SubGraph
        self.G = nx.path_graph(9)
        self.hide_edges_w_hide_nodes = {(3, 4), (4, 5), (5, 6)}

    def test_hidden_nodes(self):
        hide_nodes = [4, 5, 111]
        nodes_gone = nx.filters.hide_nodes(hide_nodes)
        G = self.gview(self.G, filter_node=nodes_gone)
        assert_equal(self.G.nodes - G.nodes, {4, 5})
        assert_equal(self.G.edges - G.edges, self.hide_edges_w_hide_nodes)
        if G.is_directed():
            assert_equal(list(G[3]), [])
            assert_equal(list(G[2]), [3])
        else:
            assert_equal(list(G[3]), [2])
            assert_equal(set(G[2]), {1, 3})
        assert_raises(KeyError, G.__getitem__, 4)
        assert_raises(KeyError, G.__getitem__, 112)
        assert_raises(KeyError, G.__getitem__, 111)
        assert_equal(G.degree(3), 3 if G.is_multigraph() else 1)
        assert_equal(G.size(), 7 if G.is_multigraph() else 5)

    def test_hidden_edges(self):
        self.hide_edges = [(2, 3), (8, 7), (222, 223)]
        self.edges_gone = self.hide_edges_filter(self.hide_edges)
        G = self.gview(self.G, filter_edge=self.edges_gone)
        assert_equal(self.G.nodes, G.nodes)
        if G.is_directed():
            assert_equal(self.G.edges - G.edges, {(2, 3)})
            assert_equal(list(G[2]), [])
            assert_equal(list(G.pred[3]), [])
            assert_equal(list(G.pred[2]), [1])
            assert_equal(G.size(), 7)
        else:
            assert_equal(self.G.edges - G.edges, {(2, 3), (7, 8)})
            assert_equal(list(G[2]), [1])
            assert_equal(G.size(), 6)
        assert_equal(list(G[3]), [4])
        assert_raises(KeyError, G.__getitem__, 221)
        assert_raises(KeyError, G.__getitem__, 222)
        assert_equal(G.degree(3), 1)

    def test_shown_node(self):
        self.induced_subgraph = nx.filters.show_nodes([2, 3, 111])
        G = self.gview(self.G, filter_node=self.induced_subgraph)
        assert_equal(set(G.nodes), {2, 3})
        if G.is_directed():
            assert_equal(list(G[3]), [])
        else:
            assert_equal(list(G[3]), [2])
        assert_equal(list(G[2]), [3])
        assert_raises(KeyError, G.__getitem__, 4)
        assert_raises(KeyError, G.__getitem__, 112)
        assert_raises(KeyError, G.__getitem__, 111)
        assert_equal(G.degree(3), 3 if G.is_multigraph() else 1)
        assert_equal(G.size(), 3 if G.is_multigraph() else 1)

    def test_shown_edges(self):
        show_edges = [(2, 3), (8, 7), (222, 223)]
        edge_subgraph = self.show_edges_filter(show_edges)
        G = self.gview(self.G, filter_edge=edge_subgraph)
        assert_equal(self.G.nodes, G.nodes)
        if G.is_directed():
            assert_equal(G.edges, {(2, 3)})
            assert_equal(list(G[3]), [])
            assert_equal(list(G[2]), [3])
            assert_equal(list(G.pred[3]), [2])
            assert_equal(list(G.pred[2]), [])
            assert_equal(G.size(), 1)
        else:
            assert_equal(G.edges, {(2, 3), (7, 8)})
            assert_equal(list(G[3]), [2])
            assert_equal(list(G[2]), [3])
            assert_equal(G.size(), 2)
        assert_raises(KeyError, G.__getitem__, 221)
        assert_raises(KeyError, G.__getitem__, 222)
        assert_equal(G.degree(3), 1)


class test_digraphview(test_graphview):
    hide_edges_filter = staticmethod(nx.filters.hide_diedges)
    show_edges_filter = staticmethod(nx.filters.show_diedges)

    def setUp(self):
        self.gview = nx.DiSubGraph
        self.G = nx.path_graph(9, create_using=nx.DiGraph())
        self.hide_edges_w_hide_nodes = {(3, 4), (4, 5), (5, 6)}

    def test_inoutedges(self):
        hide_edges = [(2, 3), (8, 7), (222, 223)]
        edges_gone = nx.filters.hide_diedges(hide_edges)
        hide_nodes = [4, 5, 111]
        nodes_gone = nx.filters.hide_nodes(hide_nodes)
        G = self.gview(self.G, nodes_gone, edges_gone)

        excluded = {(2, 3), (3, 4), (4, 5), (5, 6)}
        assert_equal(self.G.in_edges - G.in_edges, excluded)
        assert_equal(self.G.out_edges - G.out_edges, excluded)

    def test_pred(self):
        hide_edges = [(2, 3), (8, 7), (222, 223)]
        edges_gone = nx.filters.hide_diedges(hide_edges)
        hide_nodes = [4, 5, 111]
        nodes_gone = nx.filters.hide_nodes(hide_nodes)
        G = self.gview(self.G, nodes_gone, edges_gone)

        assert_equal(list(G.pred[2]), [1])
        assert_equal(list(G.pred[6]), [])

    def test_inout_degree(self):
        hide_edges = [(2, 3), (8, 7), (222, 223)]
        edges_gone = nx.filters.hide_diedges(hide_edges)
        hide_nodes = [4, 5, 111]
        nodes_gone = nx.filters.hide_nodes(hide_nodes)
        G = self.gview(self.G, nodes_gone, edges_gone)

        assert_equal(G.degree(2), 1)
        assert_equal(G.out_degree(2), 0)
        assert_equal(G.in_degree(2), 1)
        assert_equal(G.size(), 4)


# multigraph
class test_multigraphview(test_graphview):
    gview = nx.MultiSubGraph
    graph = nx.MultiGraph
    hide_edges_filter = staticmethod(nx.filters.hide_multiedges)
    show_edges_filter = staticmethod(nx.filters.show_multiedges)

    def setUp(self):
        self.G = nx.path_graph(9, create_using=self.graph())
        multiedges = {(2, 3, 4), (2, 3, 5)}
        self.G.add_edges_from(multiedges)
        self.hide_edges_w_hide_nodes = {(3, 4, 0), (4, 5, 0), (5, 6, 0)}

    def test_hidden_edges(self):
        hide_edges = [(2, 3, 4), (2, 3, 3), (8, 7, 0), (222, 223, 0)]
        edges_gone = self.hide_edges_filter(hide_edges)
        G = self.gview(self.G, filter_edge=edges_gone)
        assert_equal(self.G.nodes, G.nodes)
        if G.is_directed():
            assert_equal(self.G.edges - G.edges, {(2, 3, 4)})
            assert_equal(list(G[3]), [4])
            assert_equal(list(G[2]), [3])
            assert_equal(list(G.pred[3]), [2])  # only one 2 but two edges
            assert_equal(list(G.pred[2]), [1])
            assert_equal(G.size(), 9)
        else:
            assert_equal(self.G.edges - G.edges, {(2, 3, 4), (7, 8, 0)})
            assert_equal(list(G[3]), [2, 4])
            assert_equal(list(G[2]), [1, 3])
            assert_equal(G.size(), 8)
        assert_equal(G.degree(3), 3)
        assert_raises(KeyError, G.__getitem__, 221)
        assert_raises(KeyError, G.__getitem__, 222)

    def test_shown_edges(self):
        show_edges = [(2, 3, 4), (2, 3, 3), (8, 7, 0), (222, 223, 0)]
        edge_subgraph = self.show_edges_filter(show_edges)
        G = self.gview(self.G, filter_edge=edge_subgraph)
        assert_equal(self.G.nodes, G.nodes)
        if G.is_directed():
            assert_equal(G.edges, {(2, 3, 4)})
            assert_equal(list(G[3]), [])
            assert_equal(list(G.pred[3]), [2])
            assert_equal(list(G.pred[2]), [])
            assert_equal(G.size(), 1)
        else:
            assert_equal(G.edges, {(2, 3, 4), (7, 8, 0)})
            assert_equal(G.size(), 2)
            assert_equal(list(G[3]), [2])
        assert_equal(G.degree(3), 1)
        assert_equal(list(G[2]), [3])
        assert_raises(KeyError, G.__getitem__, 221)
        assert_raises(KeyError, G.__getitem__, 222)


# multidigraph
class test_multidigraphview(test_multigraphview):
    gview = nx.MultiDiSubGraph
    graph = nx.MultiDiGraph
    hide_edges_filter = staticmethod(nx.filters.hide_multidiedges)
    show_edges_filter = staticmethod(nx.filters.show_multidiedges)
