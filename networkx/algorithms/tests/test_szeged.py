# test_c.py - unit tests for the szeged module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.szeged` module."""

import networkx as nx
from networkx import szeged_index


class TestsSzegedIndex(object):
    """Unit tests for computing the Szeged index of a graph."""

    def test_graph_of_size_0(self):
        """Tests that the Szeged index of a graph having no edge is 0.
        """
        n = 10
        g = nx.Graph()
        g.add_nodes_from(list(range(1, n + 1)))
        expected = 0
        actual = szeged_index(g)

        assert expected == actual

    def test_complete_graph(self):
        """Tests that the Szeged index of a complete graph K_n is 0.
        It is trivial, since for any e = xy, w in V(G), d(x,w) = d(y,w) = 1.
        """
        n = 10  # number of edges
        g = nx.complete_graph(n)
        expected = 0
        actual = szeged_index(g)

        assert expected == actual

    def test_bipartite_graph_1(self):
        """Tests that the Szeged index of the complete bipartite K_(n,m) is
        n * m * (n-1) * (m-1). The calculation is from following.
        There are n*m edges in K_(n,m).
        Let e = xy be an edge such that x is in the partition of size n, say A,
        and y is in the partition of size m, say B.
        For any vertex w in B - {y}, it satisfies 1 = d(w,x) < d(w,y) = inf.
        Hence |{w in V(G) : d(w, x) < d(w,y)}| = |B| - 1 = m - 1.
        Similarly, |{w in V(G) : d(w, y) < d(w,x)}| = |A| - 1 = n - 1.
        These equality implies that szeged(K_(n,m)) = n * m * (n-1) * (m-1).

        """
        n = 3
        m = 4
        g = nx.complete_bipartite_graph(n, m)

        expected = n * m * (n - 1) * (m - 1)
        actual = szeged_index(g)

        assert expected == actual

    def test_bipartite_graph_2(self):
        """Tests that the Szeged index of the complete bipartite K_(n,n) is n^2 * (n-1)^2
        It is a special case of K_(n,m).
        """
        n = 10
        g = nx.complete_bipartite_graph(n, n)

        expected = (n ** 2) * ((n - 1) ** 2)
        actual = szeged_index(g)

        assert expected == actual

    def test_path_graph(self):
        """Tests that the Szeged index of the path graph P_n, i.e path of size n, is
        sum([(i-1)*(n-i) for i in [1 ... n]].
        """
        n = 5  # number of edges
        g = nx.path_graph(n + 1)

        expected = sum([(i - 1) * (n - i) for i in range(1, n + 1)])
        actual = szeged_index(g)

        assert expected == actual

    def test_path_graph2(self):
        """Tests that the Szeged index of a graph having two independent paths
        P_n, P_m, i.e disconnected, is
        sum([(i-1)*(n-i) for i in [1 ... n]] + sum([(i-1)*(m-i) for i in [1 ... m]].
        """
        n = 5
        m = 7
        g1 = nx.path_graph(n + 1)
        g2 = nx.path_graph(m + 1)
        g = nx.disjoint_union(g1, g2)
        expected = sum([(i - 1) * (n - i) for i in range(1, n + 1)]) + \
            sum([(i - 1) * (m - i) for i in range(1, m + 1)])
        actual = szeged_index(g)

        assert expected == actual
