from nose.tools import assert_in, assert_not_in, assert_equal
from nose.tools import assert_raises, assert_true, assert_false
import networkx as nx


class test_reverse_view(object):
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


class test_multi_reverse_view(object):
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


class test_to_directed(object):
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


class test_to_undirected(object):
    def setup(self):
        self.G = nx.path_graph(9)
        self.G = nx.path_graph(9, create_using=nx.DiGraph())
        self.dv = nx.to_undirected(self.G)
        self.MG = nx.path_graph(9, create_using=nx.MultiDiGraph())
        self.Mdv = nx.to_undirected(self.MG)

    def test_directed(self):
        assert_true(self.G.is_directed())
        assert_false(self.dv.is_directed())

    def test_already_directed(self):
        dd = nx.to_undirected(self.dv)
        Mdd = nx.to_undirected(self.Mdv)

    def test_pickle(self):
        import pickle
        dv = self.dv
        pdv = pickle.loads(pickle.dumps(dv, -1))
        assert_equal(dv._node, pdv._node)
        assert_equal(dv._adj, pdv._adj)
        assert_equal(dv.graph, pdv.graph)

    def test_contains(self):
        assert_in((2, 3), self.G.edges)
        assert_not_in((3, 2), self.G.edges)
        assert_in((2, 3), self.dv.edges)
        assert_in((3, 2), self.dv.edges)

    def test_iter(self):
        expected = sorted(self.G.edges)
        assert_equal(sorted(self.dv.edges), expected)
