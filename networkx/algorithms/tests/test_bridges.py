# test_bridges.py - unit tests for bridge-finding algorithms
#
# Copyright 2004-2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for bridge-finding algorithms."""
from unittest import TestCase

import networkx as nx


class TestBridges(TestCase):
    """Unit tests for the bridge-finding function."""

    def test_single_bridge(self):
        edges = [
            # DFS tree edges.
            (1, 2), (2, 3), (3, 4), (3, 5), (5, 6), (6, 7), (7, 8), (5, 9),
            (9, 10),
            # Nontree edges.
            (1, 3), (1, 4), (2, 5), (5, 10), (6, 8)
        ]
        G = nx.Graph(edges)
        source = 1
        bridges = list(nx.bridges(G, source))
        self.assertEqual(bridges, [(5, 6)])

    def test_barbell_graph(self):
        # The (3, 0) barbell graph has two triangles joined by a single edge.
        G = nx.barbell_graph(3, 0)
        source = 0
        bridges = list(nx.bridges(G, source))
        self.assertEqual(bridges, [(2, 3)])
