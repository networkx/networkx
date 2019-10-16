import pytest
numpy = pytest.importorskip('numpy')
npt = pytest.importorskip('numpy.testing')
scipy = pytest.importorskip('scipy')

import networkx as nx
from networkx.generators.degree_seq import havel_hakimi_graph


class TestSpectrum(object):

    @classmethod
    def setup_class(cls):
        deg = [3, 2, 2, 1, 0]
        cls.G = havel_hakimi_graph(deg)
        cls.P = nx.path_graph(3)
        cls.WG = nx.Graph((u, v, {'weight': 0.5, 'other': 0.3})
                           for (u, v) in cls.G.edges())
        cls.WG.add_node(4)
        cls.DG = nx.DiGraph()
        nx.add_path(cls.DG, [0, 1, 2])

    def test_laplacian_spectrum(self):
        "Laplacian eigenvalues"
        evals = numpy.array([0, 0, 1, 3, 4])
        e = sorted(nx.laplacian_spectrum(self.G))
        npt.assert_almost_equal(e, evals)
        e = sorted(nx.laplacian_spectrum(self.WG, weight=None))
        npt.assert_almost_equal(e, evals)
        e = sorted(nx.laplacian_spectrum(self.WG))
        npt.assert_almost_equal(e, 0.5 * evals)
        e = sorted(nx.laplacian_spectrum(self.WG, weight='other'))
        npt.assert_almost_equal(e, 0.3 * evals)

    def test_normalized_laplacian_spectrum(self):
        "Normalized Laplacian eigenvalues"
        evals = numpy.array([0, 0, 0.7712864461218, 1.5, 1.7287135538781])
        e = sorted(nx.normalized_laplacian_spectrum(self.G))
        npt.assert_almost_equal(e, evals)
        e = sorted(nx.normalized_laplacian_spectrum(self.WG, weight=None))
        npt.assert_almost_equal(e, evals)
        e = sorted(nx.normalized_laplacian_spectrum(self.WG))
        npt.assert_almost_equal(e, evals)
        e = sorted(nx.normalized_laplacian_spectrum(self.WG, weight='other'))
        npt.assert_almost_equal(e, evals)


    def test_adjacency_spectrum(self):
        "Adjacency eigenvalues"
        evals = numpy.array([-numpy.sqrt(2), 0, numpy.sqrt(2)])
        e = sorted(nx.adjacency_spectrum(self.P))
        npt.assert_almost_equal(e, evals)

    def test_modularity_spectrum(self):
        "Modularity eigenvalues"
        evals = numpy.array([-1.5, 0., 0.])
        e = sorted(nx.modularity_spectrum(self.P))
        npt.assert_almost_equal(e, evals)
        # Directed modularity eigenvalues
        evals = numpy.array([-0.5, 0., 0.])
        e = sorted(nx.modularity_spectrum(self.DG))
        npt.assert_almost_equal(e, evals)

    def test_bethe_hessian_spectrum(self):
        "Bethe Hessian eigenvalues"
        evals = numpy.array([0.5 * (9 - numpy.sqrt(33)), 4,
                             0.5 * (9 + numpy.sqrt(33))])
        e = sorted(nx.bethe_hessian_spectrum(self.P, r=2))
        npt.assert_almost_equal(e, evals)
        # Collapses back to Laplacian:
        e1 = sorted(nx.bethe_hessian_spectrum(self.P, r=1))
        e2 = sorted(nx.laplacian_spectrum(self.P))
        npt.assert_almost_equal(e1, e2)
