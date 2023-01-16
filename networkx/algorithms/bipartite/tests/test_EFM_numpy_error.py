import networkx as nx
from networkx.algorithms.bipartite.EFM_algorithms import *


class TestEnvyFreeMatching:
    def test_envy_free_matching(self):
        A = nx.complete_bipartite_graph(3, 3)
        # Fails to import numpy when calling envy_free_matching.
        assert envy_free_matching(A) == {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2}
        B = nx.complete_bipartite_graph(3, 3)
        matching = envy_free_matching(B)
        assert matching == {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2}
        C = nx.complete_bipartite_graph(3, 3)
        matching=minimum_weight_envy_free_matching(C)
        assert matching == {0: 3, 1: 4, 2: 5, 3: 0, 4: 1, 5: 2}
