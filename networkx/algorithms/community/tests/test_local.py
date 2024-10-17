import pytest

import networkx as nx

# TODO: test different graph types


def test_karate_club():
    G = nx.karate_club_graph()

    community = nx.community.clauset(G, 16)

    expected = {0, 4, 5, 6, 10, 11, 16}

    assert community == expected
