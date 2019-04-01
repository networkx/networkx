"""
    Unit tests for VoteRank.
"""

from nose.tools import assert_equal

import networkx as nx


class TestVoteRankCentrality:
    def test_voterank_centrality_1(self):
        G = nx.Graph()
        G.add_edges_from([(7, 8), (7, 5), (7, 9), (5, 0), (0, 1), (0, 2),
                          (0, 3), (0, 4), (1, 6), (2, 6), (3, 6), (4, 6)])
        assert_equal([0, 7, 6], nx.voterank(G))

    def test_voterank_centrality_2(self):
        G = nx.florentine_families_graph()
        d = nx.voterank(G, 4)
        exact = ['Medici', 'Strozzi', 'Guadagni', 'Castellani']
        assert_equal(exact, d)
