# test_christofides.py - unit tests for the approximation.christofides module
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.approximation.christofides`
module.

"""

from nose.tools import assert_true
from nose.tools import raises
import random

import networkx as nx

class TestChristofides(object):
    """Unit tests for the
    :func:`~networkx.algorithms.approximation.christofides` function.

    """

    @raises(nx.NetworkXError)
    def test_exception(self):
        G = nx.complete_graph(10)
        G.remove_edge(0, 1)
        nx.christofides(G)

    def test_hamiltonian(self):
        for _ in range(100):
            G = nx.complete_graph(20)
            for (u, v) in G.edges():
                G.edges[u,v]['weight'] = random.randint(0,10)
            H = nx.Graph()
            H.add_edges_from(nx.christofides(G))
            H.remove_edges_from(nx.find_cycle(H))
            assert_true(len(H.edges)==0)
