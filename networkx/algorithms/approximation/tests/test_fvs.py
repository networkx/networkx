# test_fvs.py - unit tests for the approximate feedback vertex set algorithm
#
# Copyright 2004-2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the approximate feedback vertex set algorithm."""
from itertools import chain
from itertools import cycle
from itertools import islice
from unittest import TestCase

import networkx as nx
from networkx.algorithms.approximation.fvs import min_feedback_vertex_set
from networkx.algorithms.approximation.fvs import paths_of_degree_2
from networkx.algorithms.approximation.fvs import semidisjoint_cycles
from networkx.testing.utils import assert_edges_equal


def cycles(seq):
    """Yields cyclic permutations of the given sequence.

    For example::

        >>> list(cycles('abc'))
        [('a', 'b', 'c'), ('b', 'c', 'a'), ('c', 'a', 'b')]

    """
    # Create a list to ensure there is a __len__ method.
    seq = list(seq)
    n = len(seq)
    cycled_seq = cycle(seq)
    for x in seq:
        yield tuple(islice(cycled_seq, n))
        next(cycled_seq)


def cyclic_equals(seq1, seq2, symmetric=True):
    """Decide whether two sequences are equal up to cyclic permutations.

    For example::

        >>> cyclic_equals('xyz', 'zxy')
        True
        >>> cyclic_equals('xyz', 'zyx')
        False

    If `symmetric` is True, then reflections are considered in addition
    to cycles:

        >>> cyclic_equals('xyz', 'yxz', symmetric=True)
        True
        >>> cyclic_equals('abcd', 'acbd', symmetric=True)
        False

    """
    # Cast seq2 to a tuple since `cycles()` yields tuples.
    seq2 = tuple(seq2)
    all_cycles = chain(cycles(seq1), cycles(reversed(seq1)))
    return any(x == seq2 for x in all_cycles)


class TestPathsOfDegree2(TestCase):

    def test_paths(self):
        G = nx.cycle_graph(5)
        G.add_edge(0, 5)
        paths = list(paths_of_degree_2(G))
        self.assertEqual(len(paths), 1)
        path = paths[0]
        self.assertTrue(cyclic_equals(path, [1, 2, 3, 4]))


class TestSemidisjointCycles(TestCase):

    def test_cycle(self):
        G = nx.cycle_graph(3)
        cycles = list(semidisjoint_cycles(G))
        self.assertEqual(len(cycles), 1)
        cycle = cycles[0]
        self.assertTrue(cyclic_equals(cycle, [0, 1, 2]))

    def test_joined_cycles(self):
        G = nx.Graph([(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)])
        cycles = semidisjoint_cycles(G)
        cycle1, cycle2 = cycles
        if 0 in cycle2:
            cycle1, cycle2 = cycle2, cycle1
        self.assertTrue(cyclic_equals(cycle1, [0, 1, 2]))
        self.assertTrue(cyclic_equals(cycle2, [3, 4, 5]))

    def test_no_cycles(self):
        G = nx.path_graph(3)
        with self.assertRaises(StopIteration):
            next(semidisjoint_cycles(G))


class TestApproxMinFVS(TestCase):

    def assertIsFVS(self, G, fvs):
        self.assertTrue(nx.is_forest(G.subgraph(set(G) - fvs)))

    def test_is_feedback_vertex_set(self):
        G = nx.gnp_random_graph(200, 0.75)
        fvs = min_feedback_vertex_set(G)
        self.assertIsFVS(G, fvs)

    def test_cycle_graph(self):
        G = nx.cycle_graph(5)
        fvs = min_feedback_vertex_set(G)
        self.assertIsFVS(G, fvs)
