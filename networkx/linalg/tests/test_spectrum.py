import pytest

import networkx as nx

np = pytest.importorskip("numpy")
pytest.importorskip("scipy")


class TestSpectrum:
    @classmethod
    def setup_class(cls):
        deg = [3, 2, 2, 1, 0]
        cls.G = nx.havel_hakimi_graph(deg)
        cls.P = nx.path_graph(3)
        cls.WG = nx.Graph(
            (u, v, {"weight": 0.5, "other": 0.3}) for (u, v) in cls.G.edges()
        )
        cls.WG.add_node(4)
        cls.DG = nx.DiGraph()
        nx.add_path(cls.DG, [0, 1, 2])

    def test_laplacian_spectrum(self):
        "Laplacian eigenvalues"
        evals = np.array([0, 0, 1, 3, 4])
        e = sorted(nx.laplacian_spectrum(self.G))
        assert np.allclose(e, evals, atol=1.5e-7, rtol=0)
        e = sorted(nx.laplacian_spectrum(self.WG, weight=None))
        assert np.allclose(e, evals, atol=1.5e-7, rtol=0)
        e = sorted(nx.laplacian_spectrum(self.WG))
        assert np.allclose(e, 0.5 * evals, atol=1.5e-7, rtol=0)
        e = sorted(nx.laplacian_spectrum(self.WG, weight="other"))
        assert np.allclose(e, 0.3 * evals, atol=1.5e-7, rtol=0)

    def test_normalized_laplacian_spectrum(self):
        "Normalized Laplacian eigenvalues"
        evals = np.array([0, 0, 0.7712864461218, 1.5, 1.7287135538781])
        e = sorted(nx.normalized_laplacian_spectrum(self.G))
        assert np.allclose(e, evals, atol=1.5e-7, rtol=0)
        e = sorted(nx.normalized_laplacian_spectrum(self.WG, weight=None))
        assert np.allclose(e, evals, atol=1.5e-7, rtol=0)
        e = sorted(nx.normalized_laplacian_spectrum(self.WG))
        assert np.allclose(e, evals, atol=1.5e-7, rtol=0)
        e = sorted(nx.normalized_laplacian_spectrum(self.WG, weight="other"))
        assert np.allclose(e, evals, atol=1.5e-7, rtol=0)

    def test_adjacency_spectrum(self):
        "Adjacency eigenvalues"
        evals = np.array([-np.sqrt(2), 0, np.sqrt(2)])
        e = sorted(nx.adjacency_spectrum(self.P))
        assert np.allclose(e, evals, atol=1.5e-7, rtol=0)

    def test_modularity_spectrum(self):
        "Modularity eigenvalues"
        evals = np.array([-1.5, 0.0, 0.0])
        e = sorted(nx.modularity_spectrum(self.P))
        assert np.allclose(e, evals, atol=1.5e-7, rtol=0)
        # Directed modularity eigenvalues
        evals = np.array([-0.5, 0.0, 0.0])
        e = sorted(nx.modularity_spectrum(self.DG))
        assert np.allclose(e, evals, atol=1.5e-7, rtol=0)

    def test_bethe_hessian_spectrum(self):
        "Bethe Hessian eigenvalues"
        evals = np.array([0.5 * (9 - np.sqrt(33)), 4, 0.5 * (9 + np.sqrt(33))])
        e = sorted(nx.bethe_hessian_spectrum(self.P, r=2))
        assert np.allclose(e, evals, atol=1.5e-7, rtol=0)
        # Collapses back to Laplacian:
        e1 = sorted(nx.bethe_hessian_spectrum(self.P, r=1))
        e2 = sorted(nx.laplacian_spectrum(self.P))
        assert np.allclose(e1, e2, atol=1.5e-7, rtol=0)
