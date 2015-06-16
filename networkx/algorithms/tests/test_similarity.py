# test_similarity.py - unit tests for the similarity module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.similarity` module."""
import networkx as nx


class TestSimRankSimilarity(object):
    """Unit tests for the
    :func:`~networkx.algorithms.similarity.simrank_similarity` function.

    """

    def test_no_source_no_target(self):
        G = nx.cycle_graph(5)
        nx.simrank_similarity(G)
        assert False, 'Not implemented'

    def test_source_no_target(self):
        G = nx.cycle_graph(5)
        nx.simrank_similarity(G, source=0)
        assert False, 'Not implemented'

    def test_source_and_target(self):
        G = nx.cycle_graph(5)
        nx.simrank_similarity(G, source=0, target=0)
        assert False, 'Not implemented'
