# test_schultz.py - unit tests for the schultz module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
# Authors: Jangwon Yie(kleinaberoho10@gmail.com)

"""Unit tests for the :mod:`networkx.algorithms.schultz` module."""

import networkx as nx
from networkx.algorithms.schultz import schultz_index_first, schultz_index_second


class TestsSchultzIndex(object):
    """Unit tests for computing the Schultz index of a graph."""

    def test_disconnected_graph(self):
        n = 4
        g = nx.Graph()
        g.add_nodes_from(list(range(1, n + 1)))
        expected = float('inf')

        g.add_edge(1, 2)
        g.add_edge(3, 4)

        actual_1 = schultz_index_first(g)
        actual_2 = schultz_index_second(g)

        assert expected == actual_1
        assert expected == actual_2

    def test_complete_bipartite_graph_1(self):
        n = 3
        m = 3
        cbg = nx.complete_bipartite_graph(n, m)

        expected_1 = n * m * (n + m) + 2 * n * (n - 1) * m + 2 * m * (m - 1) * n
        actual_1 = schultz_index_first(cbg)

        expected_2 = n * m * (n * m) + n * (n - 1) * m * m + m * (m - 1) * n * n
        actual_2 = schultz_index_second(cbg)

        assert expected_1 == actual_1
        assert expected_2 == actual_2

    def test_complete_bipartite_graph_2(self):
        n = 2
        m = 5
        cbg = nx.complete_bipartite_graph(n, m)

        expected_1 = n * m * (n + m) + 2 * n * (n - 1) * m + 2 * m * (m - 1) * n
        actual_1 = schultz_index_first(cbg)

        expected_2 = n * m * (n * m) + n * (n - 1) * m * m + m * (m - 1) * n * n
        actual_2 = schultz_index_second(cbg)

        assert expected_1 == actual_1
        assert expected_2 == actual_2

    def test_complete_graph(self):
        n = 5
        cg = nx.complete_graph(n)

        expected_1 = n * (n - 1) * (n - 1)
        actual_1 = schultz_index_first(cg)

        assert expected_1 == actual_1

        expected_2 = n * (n - 1) * (n - 1) * (n - 1) / 2
        actual_2 = schultz_index_second(cg)

        assert expected_2 == actual_2

    def test_odd_cycle_graph(self):
        k = 5
        n = 2 * k + 1
        ocg = nx.cycle_graph(n)

        expected_1 = 2 * n * k * (k + 1)
        actual_1 = schultz_index_first(ocg)

        expected_2 = 2 * n * k * (k + 1)
        actual_2 = schultz_index_second(ocg)

        assert expected_1 == actual_1
        assert expected_2 == actual_2
