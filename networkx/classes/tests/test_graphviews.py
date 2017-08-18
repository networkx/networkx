from nose.tools import assert_in, assert_not_in, assert_equal
from nose.tools import assert_raises, assert_true, assert_false

import networkx as nx
from networkx.testing import assert_edges_equal

# Note: SubGraph views are not tested here. They have their own testing file


class TestReverseView(object):
    def setup(self):
        self.G = nx.path_graph(9, create_using=nx.DiGraph())
        self.rv = nx.reverse_view(self.G)

    def test_pickle(self):
        import pickle
        rv = self.rv
        prv = pickle.loads(pickle.dumps(rv, -1))
        assert_equal(rv._node, prv._node)
        assert_equal(rv._adj, prv._adj)
        assert_equal(rv.graph, prv.graph)

    def test_contains(self):
        assert_in((2, 3), self.G.edges)
        assert_not_in((3, 2), self.G.edges)
        assert_not_in((2, 3), self.rv.edges)
        assert_in((3, 2), self.rv.edges)

    def test_iter(self):
        expected = sorted(tuple(reversed(e)) for e in self.G.edges)
        assert_equal(sorted(self.rv.edges), expected)

    def test_exceptions(self):
        nxg = nx.graphviews
        assert_raises(nx.NetworkXNotImplemented, nxg.ReverseView, nx.Graph())


class TestMultiReverseView(object):
    def setup(self):
        self.G = nx.path_graph(9, create_using=nx.MultiDiGraph())
        self.G.add_edge(4, 5)
        self.rv = nx.reverse_view(self.G)

    def test_pickle(self):
        import pickle
        rv = self.rv
        prv = pickle.loads(pickle.dumps(rv, -1))
        assert_equal(rv._node, prv._node)
        assert_equal(rv._adj, prv._adj)
        assert_equal(rv.graph, prv.graph)

    def test_contains(self):
        assert_in((2, 3, 0), self.G.edges)
        assert_not_in((3, 2, 0), self.G.edges)
        assert_not_in((2, 3, 0), self.rv.edges)
        assert_in((3, 2, 0), self.rv.edges)
        assert_in((5, 4, 1), self.rv.edges)
        assert_not_in((4, 5, 1), self.rv.edges)

    def test_iter(self):
        expected = sorted((v, u, k) for u, v, k in self.G.edges)
        assert_equal(sorted(self.rv.edges), expected)

    def test_exceptions(self):
        nxg = nx.graphviews
        MG = nx.MultiGraph(self.G)
        assert_raises(nx.NetworkXNotImplemented, nxg.MultiReverseView, MG)


class TestToDirected(object):
    def setup(self):
        self.G = nx.path_graph(9)
        self.dv = nx.to_directed(self.G)
        self.MG = nx.path_graph(9, create_using=nx.MultiGraph())
        self.Mdv = nx.to_directed(self.MG)

    def test_directed(self):
        assert_false(self.G.is_directed())
        assert_true(self.dv.is_directed())

    def test_already_directed(self):
        dd = nx.to_directed(self.dv)
        Mdd = nx.to_directed(self.Mdv)
        assert_edges_equal(dd.edges, self.dv.edges)
        assert_edges_equal(Mdd.edges, self.Mdv.edges)

    def test_pickle(self):
        import pickle
        dv = self.dv
        pdv = pickle.loads(pickle.dumps(dv, -1))
        assert_equal(dv._node, pdv._node)
        assert_equal(dv._succ, pdv._succ)
        assert_equal(dv._pred, pdv._pred)
        assert_equal(dv.graph, pdv.graph)

    def test_contains(self):
        assert_in((2, 3), self.G.edges)
        assert_in((3, 2), self.G.edges)
        assert_in((2, 3), self.dv.edges)
        assert_in((3, 2), self.dv.edges)

    def test_iter(self):
        revd = [tuple(reversed(e)) for e in self.G.edges]
        expected = sorted(list(self.G.edges) + revd)
        assert_equal(sorted(self.dv.edges), expected)

    def test_exceptions(self):
        nxg = nx.graphviews
        assert_raises(nx.NetworkXError, nxg.DiGraphView, self.MG)
        assert_raises(nx.NetworkXError, nxg.MultiDiGraphView, self.G)


class TestToUndirected(object):
    def setup(self):
        self.DG = nx.path_graph(9, create_using=nx.DiGraph())
        self.uv = nx.to_undirected(self.DG)
        self.MDG = nx.path_graph(9, create_using=nx.MultiDiGraph())
        self.Muv = nx.to_undirected(self.MDG)

    def test_directed(self):
        assert_true(self.DG.is_directed())
        assert_false(self.uv.is_directed())

    def test_already_directed(self):
        uu = nx.to_undirected(self.uv)
        Muu = nx.to_undirected(self.Muv)
        assert_edges_equal(uu.edges, self.uv.edges)
        assert_edges_equal(Muu.edges, self.Muv.edges)

    def test_pickle(self):
        import pickle
        uv = self.uv
        puv = pickle.loads(pickle.dumps(uv, -1))
        assert_equal(uv._node, puv._node)
        assert_equal(uv._adj, puv._adj)
        assert_equal(uv.graph, puv.graph)
        assert_true(hasattr(uv, '_graph'))

    def test_contains(self):
        assert_in((2, 3), self.DG.edges)
        assert_not_in((3, 2), self.DG.edges)
        assert_in((2, 3), self.uv.edges)
        assert_in((3, 2), self.uv.edges)

    def test_iter(self):
        expected = sorted(self.DG.edges)
        assert_equal(sorted(self.uv.edges), expected)

    def test_exceptions(self):
        nxg = nx.graphviews
        assert_raises(nx.NetworkXError, nxg.GraphView, self.MDG)
        assert_raises(nx.NetworkXError, nxg.MultiGraphView, self.DG)


class TestChainsOfViews(object):
    def setUp(self):
        self.G = nx.path_graph(9)
        self.DG = nx.path_graph(9, create_using=nx.DiGraph())
        self.Gv = nx.to_undirected(self.DG)
        self.DMG = nx.path_graph(9, create_using=nx.MultiDiGraph())
        self.MGv = nx.to_undirected(self.DMG)

    def test_subgraph_of_subgraph(self):
        SG = nx.induced_subgraph(self.G, [4, 5, 6])
        assert_equal(list(SG), [4, 5, 6])
        SSG = SG.subgraph([6, 7])
        assert_equal(list(SSG), [6])

    def test_subgraph_todirected(self):
        SG = nx.induced_subgraph(self.G, [4, 5, 6])
        SSG = SG.to_directed()
        assert_equal(sorted(SSG), [4, 5, 6])
        assert_equal(sorted(SSG.edges), [(4, 5), (5, 4), (5, 6), (6, 5)])

    def test_subgraph_toundirected(self):
        SG = nx.induced_subgraph(self.G, [4, 5, 6])
        SSG = SG.to_undirected()
        assert_equal(list(SSG), [4, 5, 6])
        assert_equal(sorted(SSG.edges), [(4, 5), (5, 6)])

    def test_reverse_subgraph_toundirected(self):
        G = self.DG.reverse()
        SG = G.subgraph([4, 5, 6])
        SSG = SG.to_undirected()
        assert_equal(list(SSG), [4, 5, 6])
        assert_equal(sorted(SSG.edges), [(4, 5), (5, 6)])

    def test_subgraph_edgesubgraph_toundirected(self):
        G = self.G.copy()
        SG = G.subgraph([4, 5, 6])
        SSG = SG.edge_subgraph([(4, 5), (5, 4)])
        USSG = SSG.to_undirected()
        assert_equal(list(USSG), [4, 5])
        assert_equal(sorted(USSG.edges), [(4, 5)])

    def test_copy_subgraph(self):
        G = self.G.copy()
        SG = G.subgraph([4, 5, 6])
        CSG = SG.copy(as_view=True)
        DCSG = SG.copy(as_view=False)
        assert_equal(CSG.__class__.__name__, 'GraphView')
        assert_equal(DCSG.__class__.__name__, 'Graph')

    def test_copy_disubgraph(self):
        G = self.DG.copy()
        SG = G.subgraph([4, 5, 6])
        CSG = SG.copy(as_view=True)
        DCSG = SG.copy(as_view=False)
        assert_equal(CSG.__class__.__name__, 'DiGraphView')
        assert_equal(DCSG.__class__.__name__, 'DiGraph')

    def test_copy_multidisubgraph(self):
        G = self.DMG.copy()
        SG = G.subgraph([4, 5, 6])
        CSG = SG.copy(as_view=True)
        DCSG = SG.copy(as_view=False)
        assert_equal(CSG.__class__.__name__, 'MultiDiGraphView')
        assert_equal(DCSG.__class__.__name__, 'MultiDiGraph')

    def test_copy_multisubgraph(self):
        G = self.MGv.copy()
        SG = G.subgraph([4, 5, 6])
        CSG = SG.copy(as_view=True)
        DCSG = SG.copy(as_view=False)
        assert_equal(CSG.__class__.__name__, 'MultiGraphView')
        assert_equal(DCSG.__class__.__name__, 'MultiGraph')
