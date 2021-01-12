import networkx as nx
from networkx.algorithms.community import (
    greedy_modularity_communities,
    naive_greedy_modularity_communities,
)


class TestCNM:
    def setup(self):
        self.G = nx.karate_club_graph()

    def _check_communities(self, expected):
        communities = set(greedy_modularity_communities(self.G))
        assert communities == expected

    def test_karate_club(self):
        john_a = frozenset(
            [8, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        )
        mr_hi = frozenset([0, 4, 5, 6, 10, 11, 16, 19])
        overlap = frozenset([1, 2, 3, 7, 9, 12, 13, 17, 21])
        self._check_communities({john_a, overlap, mr_hi})


class TestNaive:
    def setup(self):
        self.G = nx.karate_club_graph()

    def _check_communities(self, expected):
        communities = set(naive_greedy_modularity_communities(self.G))
        assert communities == expected

    def test_karate_club(self):
        john_a = frozenset(
            [8, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
        )
        mr_hi = frozenset([0, 4, 5, 6, 10, 11, 16, 19])
        overlap = frozenset([1, 2, 3, 7, 9, 12, 13, 17, 21])
        self._check_communities({john_a, overlap, mr_hi})
