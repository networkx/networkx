import pytest

np = pytest.importorskip("numpy")

import networkx as nx

from .base_test import BaseTestAttributeMixing, BaseTestDegreeMixing


class TestDegreeMixingCorrelation(BaseTestDegreeMixing):
    def test_degree_assortativity_undirected(self):
        r = nx.degree_assortativity_coefficient(self.P4)
        np.testing.assert_almost_equal(r, -1.0 / 2, decimal=4)

    def test_degree_assortativity_directed(self):
        r = nx.degree_assortativity_coefficient(self.D)
        np.testing.assert_almost_equal(r, -0.57735, decimal=4)

    def test_degree_assortativity_directed2(self):
        """Test degree assortativity for a directed graph where the set of
        in/out degree does not equal the total degree."""
        r = nx.degree_assortativity_coefficient(self.D2)
        np.testing.assert_almost_equal(r, 0.14852, decimal=4)

    def test_degree_assortativity_multigraph(self):
        r = nx.degree_assortativity_coefficient(self.M)
        np.testing.assert_almost_equal(r, -1.0 / 7.0, decimal=4)

    def test_degree_assortativity_weighted(self):
        r = nx.degree_assortativity_coefficient(self.W, weight="weight")
        np.testing.assert_almost_equal(r, -0.1429, decimal=4)

    def test_degree_assortativity_double_star(self):
        r = nx.degree_assortativity_coefficient(self.DS)
        np.testing.assert_almost_equal(r, -0.9339, decimal=4)


class TestAttributeMixingCorrelation(BaseTestAttributeMixing):
    def test_attribute_assortativity_undirected(self):
        r = nx.discrete_assortativity_coefficient(self.G, "fish")
        assert r == 6.0 / 22.0

    def test_attribute_assortativity_directed(self):
        r = nx.discrete_assortativity_coefficient(self.D, "fish")
        assert r == 1.0 / 3.0

    def test_attribute_assortativity_multigraph(self):
        r = nx.discrete_assortativity_coefficient(self.M, "fish")
        assert r == 1.0

    def test_attribute_assortativity_negative(self):
        r = nx.scalar_assortativity_coefficient(self.N, "margin")
        np.testing.assert_almost_equal(r, -0.2903, decimal=4)

    def test_attribute_assortativity_float(self):
        r = nx.scalar_assortativity_coefficient(self.F, "margin")
        np.testing.assert_almost_equal(r, -0.1429, decimal=4)

    def test_attribute_assortativity_mixed(self):
        r = nx.scalar_assortativity_coefficient(self.K, "margin")
        np.testing.assert_almost_equal(r, 0.4340, decimal=4)
