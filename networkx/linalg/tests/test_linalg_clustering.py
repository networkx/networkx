import networkx as nx
from nose import SkipTest

class TestLinalg_Clustering(object):
    numpy = 1  # nosetests attribute, use nosetests -a 'not numpy' to skip test

    @classmethod
    def setupClass(cls):
        global numpy
        global assert_equal
        global assert_almost_equal
        try:
            import numpy
            from numpy.testing import assert_equal,assert_almost_equal
        except ImportError:
             raise SkipTest('NumPy not available.')
        try:
            import scipy
        except ImportError:
            raise SkipTest('SciPy not available.')

    def test_undirected_unweighted_clustering(self):
        "Testing if the routine gives the same answer as the nx.clustering"
        n = 200
        p = 0.3
        G = nx.fast_gnp_random_graph(n, p, directed=False)
        nx_C = nx.clustering(G)
        linalg_C = nx.linalg.la_clustering(G)

        for key in nx_C:
            nx_c = nx_C[key]
            linalg_c = linalg_C[key]
            assert_almost_equal(nx_c, linalg_c)

    def test_undirected_weighted_clustering(self):
        "Testing if the routine gives the same answer as the nx.clustering"
        n = 200
        p = 0.3
        G = nx.fast_gnp_random_graph(n, p, directed=False)

        for edge in G.edges_iter():
            weight = numpy.random.rand()
            G.add_edge(edge[0], edge[1], weight=weight)

        nx_C = nx.clustering(G, weight='weight')
        linalg_C = nx.linalg.la_clustering(G)

        for key in nx_C:
            nx_c = nx_C[key]
            linalg_c = linalg_C[key]
            assert_almost_equal(nx_c, linalg_c)