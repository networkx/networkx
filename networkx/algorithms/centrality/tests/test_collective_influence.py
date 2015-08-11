# coding: utf-8
"""
    Unit tests for collective influence.
"""
from nose.tools import *
import networkx as nx

class TestCollectiveInfluence(object):
    def __init__(self):
        # Sample network taken from Figure 1 in letter:
        # István A. Kovács & Albert-László Barabási
        # Network science: Destruction perfected
        # Nature 524, 38–39 (06 August 2015)
        # doi: 10.1038/524038a
        edges = [
            (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
            (2, 7), (2, 8), (2, 9), (2, 10),
            (3, 4), (3, 8), (3, 19),
            (7, 8), (7, 11), (7, 13),
            (8, 26),
            (11, 14), (11, 12),
            (12, 15), (12, 19), (12, 29),
            (13, 22),
            (14, 16), (14, 17), (14, 18), (14, 15),
            (17, 18),
            (19, 20), (19, 21),
            (20, 21), (20, 22), (20, 23), (20, 24),
            (21, 22), (21, 23), (21, 25),
            (22, 26), (22, 27), (22, 28),
            (26, 29),
            (27, 28),
            (29, 30),
        ]
        self.G = nx.Graph(edges)

    def test_collective_influence_1(self):
        collective_influence = nx.collective_influence(self.G)
        assert_equal(collective_influence[7],  63)
        assert_equal(collective_influence[22], 60)
