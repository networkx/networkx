#!/usr/bin/env python
import pytest
np = pytest.importorskip('numpy')
npt = pytest.importorskip('numpy.testing')
scipy = pytest.importorskip('scipy')


import networkx as nx
from .base_test import BaseTestAttributeMixing, BaseTestDegreeMixing
from networkx.algorithms.assortativity.correlation import attribute_ac


class TestDegreeMixingCorrelation(BaseTestDegreeMixing):

    def test_degree_assortativity_undirected(self):
        r = nx.degree_assortativity_coefficient(self.P4)
        npt.assert_almost_equal(r, -1.0 / 2, decimal=4)

    def test_degree_assortativity_directed(self):
        r = nx.degree_assortativity_coefficient(self.D)
        npt.assert_almost_equal(r, -0.57735, decimal=4)

    def test_degree_assortativity_multigraph(self):
        r = nx.degree_assortativity_coefficient(self.M)
        npt.assert_almost_equal(r, -1.0 / 7.0, decimal=4)

    def test_degree_pearson_assortativity_undirected(self):
        r = nx.degree_pearson_correlation_coefficient(self.P4)
        npt.assert_almost_equal(r, -1.0 / 2, decimal=4)

    def test_degree_pearson_assortativity_directed(self):
        r = nx.degree_pearson_correlation_coefficient(self.D)
        npt.assert_almost_equal(r, -0.57735, decimal=4)

    def test_degree_pearson_assortativity_multigraph(self):
        r = nx.degree_pearson_correlation_coefficient(self.M)
        npt.assert_almost_equal(r, -1.0 / 7.0, decimal=4)


class TestAttributeMixingCorrelation(BaseTestAttributeMixing):

    def test_attribute_assortativity_undirected(self):
        r = nx.attribute_assortativity_coefficient(self.G, 'fish')
        assert r == 6.0 / 22.0

    def test_attribute_assortativity_directed(self):
        r = nx.attribute_assortativity_coefficient(self.D, 'fish')
        assert r == 1.0 / 3.0

    def test_attribute_assortativity_multigraph(self):
        r = nx.attribute_assortativity_coefficient(self.M, 'fish')
        assert r == 1.0

    def test_attribute_assortativity_coefficient(self):
        # from "Mixing patterns in networks"
        a = np.array([[0.258, 0.016, 0.035, 0.013],
                      [0.012, 0.157, 0.058, 0.019],
                      [0.013, 0.023, 0.306, 0.035],
                      [0.005, 0.007, 0.024, 0.016]])
        r = attribute_ac(a)
        npt.assert_almost_equal(r, 0.623, decimal=3)

    def test_attribute_assortativity_coefficient2(self):
        a = np.array([[0.18, 0.02, 0.01, 0.03],
                      [0.02, 0.20, 0.03, 0.02],
                      [0.01, 0.03, 0.16, 0.01],
                      [0.03, 0.02, 0.01, 0.22]])

        r = attribute_ac(a)
        npt.assert_almost_equal(r, 0.68, decimal=2)

    def test_attribute_assortativity(self):
        a = np.array([[50, 50, 0], [50, 50, 0], [0, 0, 2]])
        r = attribute_ac(a)
        npt.assert_almost_equal(r, 0.029, decimal=3)
