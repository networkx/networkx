import pytest

import networkx as nx
from networkx.algorithms.community import (
    greedy_modularity_communities,
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


def test_generalized_modularity_max_resolution():
    G = nx.karate_club_graph()
    c1 = list(greedy_modularity_communities(G, 1.8))
    c2 = list(naive_greedy_modularity_communities(G, 1.8))
    assert len(c1) == len(c2)
    for cc1, cc2 in zip(c1, c2):
        assert sorted(cc1) == sorted(cc2)
