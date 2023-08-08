"""
    Unit tests for voting based centrality indices.
"""


import networkx as nx


class TestSPAVCentrality:
    def test_spav_1(self):
        G = nx.Graph()
        G.add_edges_from(
            [
                (1, 2),
                (1, 3),
                (1, 4),
                (1, 5),
                (5, 6),
                (6, 7),
                (7, 8),
                (7, 9),
                (8, 10),
                (10, 11),
                (11, 12),
                (11, 2),
            ]
        )
        assert [1, 7, 11] == nx.spav_voting(G, number_of_nodes=3)

    def test_spav_2(self):
        G = nx.Graph()
        G.add_edges_from(
            [
                (1, 2),
                (1, 3),
                (1, 4),
                (1, 5),
                (1, 6),
                (2, 6),
                (3, 6),
                (4, 6),
                (5, 6),
                (7, 6),
                (7, 8),
                (7, 9),
                (10, 6),
                (10, 1),
            ]
        )
        assert [6, 1] == nx.spav_voting(G, number_of_nodes=2)
        assert [6, 7] == nx.spav_voting(
            G, number_of_nodes=2, voting_ability_fn=lambda x: 1 if x == 0 else 0
        )


class TestSAVCentrality:
    def test_sav_1(self):
        G = nx.Graph()
        G.add_edges_from(
            [
                (1, 2),
                (1, 3),
                (1, 4),
                (1, 5),
                (5, 6),
                (6, 7),
                (7, 8),
                (7, 9),
                (8, 10),
                (10, 11),
                (11, 12),
                (11, 2),
            ]
        )
        result = nx.sav_voting(G)
        assert result[1] == 3
        assert result[2] == 1 / 3 + 1 / 4
        assert result[3] == 1 / 4
        assert result[7] == 2
        assert result[10] == 1 / 2 + 1 / 3

    def test_sav_2(self):
        # Graph from reference paper.
        G = nx.Graph()
        G.add_edges_from(
            [
                (0, 1),
                (0, 2),
                (0, 3),
                (0, 4),
                (0, 5),
                (0, 6),
                (0, 7),
                (0, 8),
                (1, 9),
                (9, 10),
                (10, 11),
                (10, 12),
                (10, 13),
                (10, 14),
                (10, 15),
                (10, 16),
                (10, 17),
                (1, 2),
                (2, 3),
                (3, 4),
                (4, 5),
                (5, 6),
                (6, 7),
                (7, 8),
                (8, 1),
            ]
        )
        result = nx.sav_voting(G)
        assert max(result, key=result.get) == 10
        assert result[10] == 7 + 1 / 2
        assert result[0] == 7 * (1 / 3) + 1 / 4
        assert result[1] == 1 / 8 + 2 * (1 / 3) + 1 / 2


class TestCopelandCentrality:
    def test_copeland_no_condorcet_winner(self):
        # Graph from reference paper: Condorcet Paradox.
        G = nx.Graph()
        G.add_edges_from(
            [
                ("A", 1),
                ("A", 2),
                ("A", 3),
                ("A", 4),
                (2, 5),
                (2, 6),
                (2, 7),
                (5, 6),
                (5, 7),
                (5, "C"),
                ("C", "B"),
                ("B", 8),
                ("B", 9),
                ("B", 10),
                ("B", 11),
                (8, 11),
                (9, 11),
                (10, 11),
                (11, 4),
            ]
        )
        result = nx.copeland_voting(G)
        assert result["A"] < 13
        assert result["B"] < 13
        assert result["C"] < 13

    def test_copeland_condorcet_winner_exists(self):
        # Graph from reference paper: Condorcet winner exists, and Copeland chooses it.
        G = nx.Graph()
        G.add_edges_from(
            [
                ("CW", 1),
                ("CW", 2),
                ("CW", 3),
                ("CW", "BW"),
                ("BW", 2),
                ("BW", 4),
                (4, 5),
                (2, "CC"),
                (3, "CC"),
                ("CC", 6),
                ("CC", 7),
                (7, 6),
                (7, 8),
                (7, 9),
                (3, 10),
                (6, 1),
                (10, 9),
                (1, 9),
            ]
        )
        result = nx.copeland_voting(G)
        assert max(result, key=result.get) == "CW"
        assert len([n for n in result if result[n] == result["CW"]]) == 1


class TestBordaCentrality:
    def test_borda(self):
        G = nx.Graph()
        G.add_edges_from(
            [
                ("A", "F"),
                ("A", "B"),
                ("B", "C"),
                ("B", "D"),
                ("C", "D"),
                ("C", "E"),
                ("D", "E"),
            ]
        )
        result = nx.borda_voting(G)
        assert result["A"] == 0
        assert result["B"] == 9
        assert result["C"] == 5
        assert result["D"] == 5
        assert result["E"] == -7
        assert result["F"] == -12
