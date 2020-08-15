import pytest


import networkx
from networkx.testing import almost_equal

# Example from
# A. Langville and C. Meyer, "A survey of eigenvector methods of web
# information retrieval."  http://citeseer.ist.psu.edu/713792.html


class TestHITS:
    @classmethod
    def setup_class(cls):

        G = networkx.DiGraph()

        edges = [(1, 3), (1, 5), (2, 1), (3, 5), (5, 4), (5, 3), (6, 5)]

        G.add_edges_from(edges, weight=1)
        cls.G = G
        cls.G.a = dict(
            zip(sorted(G), [0.000000, 0.000000, 0.366025, 0.133975, 0.500000, 0.000000])
        )
        cls.G.h = dict(
            zip(sorted(G), [0.366025, 0.000000, 0.211325, 0.000000, 0.211325, 0.211325])
        )

    def test_hits(self):
        G = self.G
        h, a = networkx.hits(G, tol=1.0e-08)
        for n in G:
            assert almost_equal(h[n], G.h[n], places=4)
        for n in G:
            assert almost_equal(a[n], G.a[n], places=4)

    def test_hits_nstart(self):
        G = self.G
        nstart = {i: 1.0 / 2 for i in G}
        h, a = networkx.hits(G, nstart=nstart)

    def test_hits_numpy(self):
        numpy = pytest.importorskip("numpy")
        G = self.G
        h, a = networkx.hits_numpy(G)
        for n in G:
            assert almost_equal(h[n], G.h[n], places=4)
        for n in G:
            assert almost_equal(a[n], G.a[n], places=4)

    def test_hits_scipy(self):
        sp = pytest.importorskip("scipy")
        G = self.G
        h, a = networkx.hits_scipy(G, tol=1.0e-08)
        for n in G:
            assert almost_equal(h[n], G.h[n], places=4)
        for n in G:
            assert almost_equal(a[n], G.a[n], places=4)

    def test_empty(self):
        numpy = pytest.importorskip("numpy")
        G = networkx.Graph()
        assert networkx.hits(G) == ({}, {})
        assert networkx.hits_numpy(G) == ({}, {})
        assert networkx.authority_matrix(G).shape == (0, 0)
        assert networkx.hub_matrix(G).shape == (0, 0)

    def test_empty_scipy(self):
        scipy = pytest.importorskip("scipy")
        G = networkx.Graph()
        assert networkx.hits_scipy(G) == ({}, {})

    def test_hits_not_convergent(self):
        with pytest.raises(networkx.PowerIterationFailedConvergence):
            G = self.G
            networkx.hits(G, max_iter=0)
