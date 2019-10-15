# Copyright 2014 "cheebee7i".
# Copyright 2014 "alexbrc".
# Copyright 2014 Jeffrey Finkelstein <jeffrey.finkelstein@gmail.com>.
"""Unit tests for the :mod:`networkx.generators.expanders` module.

"""

import networkx as nx
from networkx import adjacency_matrix
from networkx import number_of_nodes
from networkx.generators.expanders import chordal_cycle_graph
from networkx.generators.expanders import margulis_gabber_galil_graph

import pytest


def test_margulis_gabber_galil_graph():
    for n in 2, 3, 5, 6, 10:
        g = margulis_gabber_galil_graph(n)
        assert number_of_nodes(g) == n * n
        for node in g:
            assert g.degree(node) == 8
            assert len(node) == 2
            for i in node:
                assert int(i) == i
                assert 0 <= i < n

    np = pytest.importorskip("numpy")
    scipy = pytest.importorskip("scipy")
    scipy.linalg = pytest.importorskip("scipy.linalg")
    # Eigenvalues are already sorted using the scipy eigvalsh,
    # but the implementation in numpy does not guarantee order.
    w = sorted(scipy.linalg.eigvalsh(adjacency_matrix(g).A))
    assert w[-2] < 5 * np.sqrt(2)


def test_chordal_cycle_graph():
    """Test for the :func:`networkx.chordal_cycle_graph` function."""
    primes = [3, 5, 7, 11]
    for p in primes:
        G = chordal_cycle_graph(p)
        assert len(G) == p
        # TODO The second largest eigenvalue should be smaller than a constant,
        # independent of the number of nodes in the graph:
        #
        #     eigs = sorted(scipy.linalg.eigvalsh(adjacency_matrix(G).A))
        #     assert_less(eigs[-2], ...)
        #


def test_margulis_gabber_galil_graph_badinput():
    pytest.raises(nx.NetworkXError, margulis_gabber_galil_graph, 3,
                  nx.DiGraph())
    pytest.raises(nx.NetworkXError, margulis_gabber_galil_graph, 3,
                  nx.Graph())
