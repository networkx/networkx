import pytest

import networkx as nx
from networkx.algorithms.fvs import is_fvs


class TestIsFVS:
    """
    Tests for :func:``
    """

    def test_empty_graph(self):
        G = nx.empty_graph()
        f = set()

        assert is_fvs(G, f)

    def test_graph_with_loop(self):
        G = nx.Graph()
        G.add_edge(1, 1)
        f = set()
        assert not is_fvs(G, f)

        f = {1}
        assert is_fvs(G, f)
