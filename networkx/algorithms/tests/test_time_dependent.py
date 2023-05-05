"""Unit testing for time dependent algorithms."""

from datetime import datetime

import pytest

import networkx as nx


class TestCdIndex:
    """Unit testing for the cd index function."""

    def test_russellfunk(self):
        G = nx.DiGraph()
        G.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        G.add_edge(4, 2)
        G.add_edge(4, 0)
        G.add_edge(4, 1)
        G.add_edge(4, 3)
        G.add_edge(5, 2)
        G.add_edge(6, 2)
        G.add_edge(6, 4)
        G.add_edge(7, 4)
        G.add_edge(8, 4)
        G.add_edge(9, 4)
        G.add_edge(9, 1)
        G.add_edge(9, 3)
        G.add_edge(10, 4)

        node_attrs = {
            0: {"time": datetime(1992, 1, 1)},
            1: {"time": datetime(1992, 1, 1)},
            2: {"time": datetime(1993, 1, 1)},
            3: {"time": datetime(1993, 1, 1)},
            4: {"time": datetime(1995, 1, 1)},
            5: {"time": datetime(1997, 1, 1)},
            6: {"time": datetime(1998, 1, 1)},
            7: {"time": datetime(1999, 1, 1)},
            8: {"time": datetime(1999, 1, 1)},
            9: {"time": datetime(1998, 1, 1)},
            10: {"time": datetime(1997, 4, 1)},
        }

        nx.set_node_attributes(G, node_attrs)

        assert nx.cd_index(G, 4) == 0.17

    def test_russellfunk_with_weights(self):
        G = nx.DiGraph()
        G.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        G.add_edge(4, 2)
        G.add_edge(4, 0)
        G.add_edge(4, 1)
        G.add_edge(4, 3)
        G.add_edge(5, 2)
        G.add_edge(6, 2)
        G.add_edge(6, 4)
        G.add_edge(7, 4)
        G.add_edge(8, 4)
        G.add_edge(9, 4)
        G.add_edge(9, 1)
        G.add_edge(9, 3)
        G.add_edge(10, 4)

        node_attrs = {
            0: {"time": datetime(1992, 1, 1)},
            1: {"time": datetime(1992, 1, 1)},
            2: {"time": datetime(1993, 1, 1)},
            3: {"time": datetime(1993, 1, 1)},
            4: {"time": datetime(1995, 1, 1)},
            5: {"time": datetime(1997, 1, 1)},
            6: {"time": datetime(1998, 1, 1)},
            7: {"time": datetime(1999, 1, 1)},
            8: {"time": datetime(1999, 1, 1)},
            9: {"time": datetime(1998, 1, 1)},
            10: {"time": datetime(1997, 4, 1)},
        }

        nx.set_node_attributes(G, node_attrs)
        w = [5, 2, 6, 3, 10]
        assert nx.cd_index(G, 4, weight=w) == 0.04
