"""Unit tests for the :mod:`networkx.generators.cographs` module."""

import pytest

import networkx as nx


@pytest.mark.parametrize("n", [3, 4, 5])
@pytest.mark.parametrize("seed", [42, 43])
def test_random_cograph(n, seed):
    """Test the generation of random cographs.

    Parametrized on `seed` to ensure we hit all code branches.
    """
    G = nx.random_cograph(n, seed=seed)

    assert len(G) == 2**n

    # Every connected subgraph of G has diameter <= 2
    if nx.is_connected(G):
        assert nx.diameter(G) <= 2
    else:
        components = nx.connected_components(G)
        for component in components:
            assert nx.diameter(G.subgraph(component)) <= 2
