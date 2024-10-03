import pytest

import networkx as nx

# TODO: test different graph types


def test_karate_club():
    G = nx.karate_club_graph()

    expected = {0, 1, 2, 3, 7, 9, 11, 12, 13, 17, 19, 21}

    # partition = nx.community.lo

    # assert part == partition
