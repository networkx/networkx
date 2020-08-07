import networkx as nx

import pytest

numpy = pytest.importorskip("numpy")
npt = pytest.importorskip("numpy.testing")


def test_non_randomness():
    G = nx.karate_club_graph()
    npt.assert_almost_equal(nx.non_randomness(G, 2)[0], 11.7, decimal=2)
    npt.assert_almost_equal(
        nx.non_randomness(G)[0], 7.21, decimal=2
    )  # infers 3 communities
