import networkx as nx

import pytest

np = pytest.importorskip("numpy")


def test_non_randomness():
    G = nx.karate_club_graph()
    np.testing.assert_almost_equal(nx.non_randomness(G, 2)[0], 11.7, decimal=2)
    np.testing.assert_almost_equal(
        nx.non_randomness(G)[0], 7.21, decimal=2
    )  # infers 3 communities
