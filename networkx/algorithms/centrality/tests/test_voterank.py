"""
    Unit tests for VoteRank.
"""


import networkx as nx


class TestVoteRankCentrality:
    # Example Graph present in reference paper
    def test_voterank_centrality_1(self):
        G = nx.Graph()
        G.add_edges_from(
            [
                (7, 8),
                (7, 5),
                (7, 9),
                (5, 0),
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 4),
                (1, 6),
                (2, 6),
                (3, 6),
                (4, 6),
            ]
        )
        assert [0, 7, 6] == nx.voterank(G)

    def test_vote_rank_centrality_1(self):
        G = nx.Graph()
        G.add_edges_from(
            [
                (7, 8),
                (7, 5),
                (7, 9),
                (5, 0),
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 4),
                (1, 6),
                (2, 6),
                (3, 6),
                (4, 6),
            ]
        )
        assert {0: 5, 6: 2.333333333333333, 7: 2.583333333333333} == nx.vote_rank(G)

    # Graph unit test
    def test_voterank_centrality_2(self):
        G = nx.florentine_families_graph()
        d = nx.voterank(G, 4)
        exact = ["Medici", "Strozzi", "Guadagni", "Castellani"]
        assert exact == d

    # Graph unit test
    def test_vote_rank_centrality_2(self):
        G = nx.florentine_families_graph()
        d = nx.vote_rank(G, 4)
        exact = {"Castellani": 1.25, "Guadagni": 2.875, "Medici": 6, "Strozzi": 3.625}
        assert exact == d

    # DiGraph unit test
    def test_voterank_centrality_3(self):
        G = nx.gnc_graph(10, seed=7)
        d = nx.voterank(G, 4)
        exact = [3, 6, 8]
        assert exact == d

    # DiGraph unit test
    def test_vote_rank_centrality_3(self):
        G = nx.gnc_graph(10, seed=7)
        d = nx.vote_rank(G, 4)
        exact = {3: 2, 6: 1.1666666666666665, 8: 1}
        assert exact == d

    # MultiGraph unit test
    def test_voterank_centrality_4(self):
        G = nx.MultiGraph()
        G.add_edges_from(
            [(0, 1), (0, 1), (1, 2), (2, 5), (2, 5), (5, 6), (5, 6), (2, 4), (4, 3)]
        )
        exact = [2, 1, 5, 4]
        assert exact == nx.voterank(G)

    # MultiGraph unit test
    def test_vote_rank_centrality_4(self):
        G = nx.MultiGraph()
        G.add_edges_from(
            [(0, 1), (0, 1), (1, 2), (2, 5), (2, 5), (5, 6), (5, 6), (2, 4), (4, 3)]
        )
        exact = {1: 2, 2: 4, 4: 1, 5: 2}
        assert exact == nx.vote_rank(G)

    # MultiDiGraph unit test
    def test_voterank_centrality_5(self):
        G = nx.MultiDiGraph()
        G.add_edges_from(
            [(0, 1), (0, 1), (1, 2), (2, 5), (2, 5), (5, 6), (5, 6), (2, 4), (4, 3)]
        )
        exact = [2, 0, 5, 4]
        assert exact == nx.voterank(G)

    # MultiDiGraph unit test
    def test_vote_rank_centrality_5(self):
        G = nx.MultiDiGraph()
        G.add_edges_from(
            [(0, 1), (0, 1), (1, 2), (2, 5), (2, 5), (5, 6), (5, 6), (2, 4), (4, 3)]
        )
        exact = {0: 2, 2: 3, 4: 1, 5: 2}
        assert exact == nx.vote_rank(G)
