# test_matching.py - unit tests for bipartite matching algorithms
#
# Copyright 2015 Jeffrey Finkelstein <jeffrey.finkelstein@gmail.com>.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.bipartite.matching` module."""
import itertools

import networkx as nx

from networkx.algorithms.bipartite.matching import eppstein_matching
from networkx.algorithms.bipartite.matching import hopcroft_karp_matching
from networkx.algorithms.bipartite.matching import maximum_matching
from networkx.algorithms.bipartite.matching import to_vertex_cover


class TestMatching():
    """Tests for bipartite matching algorithms."""

    def setup(self):
        """Creates a bipartite graph for use in testing matching algorithms.

        The bipartite graph has a maximum cardinality matching that leaves
        vertex 1 and vertex 10 unmatched. The first six numbers are the left
        vertices and the next six numbers are the right vertices.

        """
        edges = [(0, 7), (0, 8), (2, 6), (2, 9), (3, 8), (4, 8), (4, 9),
                 (5, 11)]
        self.graph = nx.Graph()
        self.graph.add_nodes_from(range(12))
        self.graph.add_edges_from(edges)

    def check_match(self, matching):
        """Asserts that the matching is what we expect from the bipartite graph
        constructed in the :meth:`setup` fixture.

        """
        # For the sake of brevity, rename `matching` to `M`.
        M = matching
        matched_vertices = frozenset(itertools.chain(*M.items()))
        # Assert that the maximum number of vertices (10) is matched.
        assert matched_vertices == frozenset(range(12)) - {1, 10}
        # Assert that no vertex appears in two edges, or in other words, that
        # the matching (u, v) and (v, u) both appear in the matching
        # dictionary.
        assert all(u == M[M[u]] for u in range(12) if u in M)

    def check_vertex_cover(self, vertices):
        """Asserts that the given set of vertices is the vertex cover we
        expected from the bipartite graph constructed in the :meth:`setup`
        fixture.

        """
        # By Konig's theorem, the number of edges in a maximum matching equals
        # the number of vertices in a minimum vertex cover.
        assert len(vertices) == 5
        # Assert that the set is truly a vertex cover.
        for (u, v) in self.graph.edges():
            assert u in vertices or v in vertices
        # TODO Assert that the vertices are the correct ones.

    def test_eppstein_matching(self):
        """Tests that David Eppstein's implementation of the Hopcroft--Karp
        algorithm produces a maximum cardinality matching.

        """
        self.check_match(eppstein_matching(self.graph))

    def test_hopcroft_karp_matching(self):
        """Tests that the Hopcroft--Karp algorithm produces a maximum
        cardinality matching in a bipartite graph.

        """
        self.check_match(hopcroft_karp_matching(self.graph))

    def test_to_vertex_cover(self):
        """Test for converting a maximum matching to a minimum vertex cover."""
        matching = maximum_matching(self.graph)
        vertex_cover = to_vertex_cover(self.graph, matching)
        self.check_vertex_cover(vertex_cover)
