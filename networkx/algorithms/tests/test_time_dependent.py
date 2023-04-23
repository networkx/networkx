"""Unit testing for time dependent algorithms."""

import pytest
import networkx as nx

class TestCdIndex:
    def test_extra_nodes(self):
        G = nx.DiGraph()
        G.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
        G.add_edge(1, 2)
        G.add_edge(1, 3)
        G.add_edge(4, 1)
        G.add_edge(5, 1)
        G.add_edge(6, 2)
        G.add_edge(7, 4)

        assert nx.cd_index(G, 1) == 0.67