import pytest

import networkx as nx
from networkx.algorithms.community import (
    greedy_modularity_communities,
    modularity,
    naive_greedy_modularity_communities,
)


@pytest.mark.parametrize(
    "func", (greedy_modularity_communities, naive_greedy_modularity_communities)
)
def test_modularity_communities(func):
    G = nx.karate_club_graph()

    john_a = frozenset(
        [8, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
    )
    mr_hi = frozenset([0, 4, 5, 6, 10, 11, 16, 19])
    overlap = frozenset([1, 2, 3, 7, 9, 12, 13, 17, 21])
    expected = {john_a, overlap, mr_hi}

    assert set(func(G)) == expected


def test_modularity_communities_weighted():
    G = nx.balanced_tree(2, 3)
    for (a, b) in G.edges:
        if ((a == 1) or (a == 2)) and (b != 0):
            G[a][b]["weight"] = 10.0
        else:
            G[a][b]["weight"] = 1.0

    expected = [{0, 1, 3, 4, 7, 8, 9, 10}, {2, 5, 6, 11, 12, 13, 14}]

    assert greedy_modularity_communities(G, weight="weight") == expected


def test_resolution_parameter_impact():
    G = nx.barbell_graph(5, 3)

    gamma = 1
    expected = [frozenset(range(5)), frozenset(range(8, 13)), frozenset(range(5, 8))]
    assert greedy_modularity_communities(G, resolution=gamma) == expected
    assert naive_greedy_modularity_communities(G, resolution=gamma) == expected

    gamma = 2.5
    expected = [{0, 1, 2, 3}, {9, 10, 11, 12}, {5, 6, 7}, {4}, {8}]
    assert greedy_modularity_communities(G, resolution=gamma) == expected
    assert naive_greedy_modularity_communities(G, resolution=gamma) == expected

    gamma = 0.3
    expected = [frozenset(range(8)), frozenset(range(8, 13))]
    assert greedy_modularity_communities(G, resolution=gamma) == expected
    assert naive_greedy_modularity_communities(G, resolution=gamma) == expected
