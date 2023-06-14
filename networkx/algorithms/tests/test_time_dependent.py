"""Unit testing for time dependent algorithms."""

from datetime import datetime

import pytest

import networkx as nx


class TestCdIndex:
    """Unit testing for the cd index function."""

    def test_common_graph(self):
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

    def test_common_graph_with_weights(self):
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
            6: {"time": datetime(1998, 1, 1), "weight": 5},
            7: {"time": datetime(1999, 1, 1), "weight": 2},
            8: {"time": datetime(1999, 1, 1), "weight": 6},
            9: {"time": datetime(1998, 1, 1), "weight": 3},
            10: {"time": datetime(1997, 4, 1), "weight": 10},
        }

        nx.set_node_attributes(G, node_attrs)
        assert nx.cd_index(G, 4, weight="weight") == 0.04

    def test_node_with_no_predecessors(self):
        G = nx.DiGraph()
        G.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        G.add_edge(4, 2)
        G.add_edge(4, 0)
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
            5: {"time": datetime(2005, 1, 1)},
            6: {"time": datetime(2010, 1, 1)},
            7: {"time": datetime(2001, 1, 1)},
            8: {"time": datetime(2020, 1, 1)},
            9: {"time": datetime(2017, 1, 1)},
            10: {"time": datetime(2004, 4, 1)},
        }

        nx.set_node_attributes(G, node_attrs)
        assert nx.cd_index(G, 4) == 0.0

    def test_node_with_no_successors(self):
        G = nx.DiGraph()
        G.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        G.add_edge(8, 2)
        G.add_edge(6, 0)
        G.add_edge(6, 3)
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
        assert nx.cd_index(G, 4) == 1.0

    def test_n_equals_zero(self):
        G = nx.DiGraph()
        G.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        G.add_edge(4, 2)
        G.add_edge(4, 0)
        G.add_edge(4, 3)
        G.add_edge(6, 4)
        G.add_edge(7, 4)
        G.add_edge(8, 4)
        G.add_edge(9, 4)
        G.add_edge(9, 1)
        G.add_edge(10, 4)

        node_attrs = {
            0: {"time": datetime(1992, 1, 1)},
            1: {"time": datetime(1992, 1, 1)},
            2: {"time": datetime(1993, 1, 1)},
            3: {"time": datetime(1993, 1, 1)},
            4: {"time": datetime(1995, 1, 1)},
            5: {"time": datetime(2005, 1, 1)},
            6: {"time": datetime(2010, 1, 1)},
            7: {"time": datetime(2001, 1, 1)},
            8: {"time": datetime(2020, 1, 1)},
            9: {"time": datetime(2017, 1, 1)},
            10: {"time": datetime(2004, 4, 1)},
        }

        nx.set_node_attributes(G, node_attrs)

        with pytest.raises(ValueError, match="The cd index cannot be defined.") as ve:
            nx.cd_index(G, 4)

    def test_node_with_no_time(self):
        G = nx.DiGraph()
        G.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        G.add_edge(8, 2)
        G.add_edge(6, 0)
        G.add_edge(6, 3)
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
            6: {"time": datetime(1998, 1, 1)},
            7: {"time": datetime(1999, 1, 1)},
            8: {"time": datetime(1999, 1, 1)},
            9: {"time": datetime(1998, 1, 1)},
            10: {"time": datetime(1997, 4, 1)},
        }

        nx.set_node_attributes(G, node_attrs)

        with pytest.raises(
            ValueError, match="Not all nodes have a datetime 'time' attribute."
        ) as ve:
            nx.cd_index(G, 4)

    def test_maximally_consolidating(self):
        G = nx.DiGraph()
        G.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        G.add_edge(5, 1)
        G.add_edge(5, 2)
        G.add_edge(5, 3)
        G.add_edge(5, 4)
        G.add_edge(6, 1)
        G.add_edge(6, 5)
        G.add_edge(7, 1)
        G.add_edge(7, 5)
        G.add_edge(8, 2)
        G.add_edge(8, 5)
        G.add_edge(9, 5)
        G.add_edge(9, 3)
        G.add_edge(10, 5)
        G.add_edge(10, 3)
        G.add_edge(10, 4)
        G.add_edge(11, 5)
        G.add_edge(11, 4)

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
            11: {"time": datetime(1998, 5, 1)},
        }

        nx.set_node_attributes(G, node_attrs)

        assert nx.cd_index(G, 5) == -1

    def test_maximally_destabilizing(self):
        G = nx.DiGraph()
        G.add_nodes_from([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
        G.add_edge(5, 1)
        G.add_edge(5, 2)
        G.add_edge(5, 3)
        G.add_edge(5, 4)
        G.add_edge(6, 5)
        G.add_edge(7, 5)
        G.add_edge(8, 5)
        G.add_edge(9, 5)
        G.add_edge(10, 5)
        G.add_edge(11, 5)

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
            11: {"time": datetime(1998, 5, 1)},
        }

        nx.set_node_attributes(G, node_attrs)

        assert nx.cd_index(G, 5) == 1
