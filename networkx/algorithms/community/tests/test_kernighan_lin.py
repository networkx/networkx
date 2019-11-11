# -*- encoding: utf-8 -*-
"""Unit tests for the :mod:`networkx.algorithms.community.kernighan_lin`
module.

"""
import pytest

import networkx as nx
from networkx.algorithms.community import kernighan_lin_bisection


def assert_partition_equal(x, y):
    assert set(map(frozenset, x)) == set(map(frozenset, y))


def test_partition():
    G = nx.barbell_graph(3, 0)
    C = kernighan_lin_bisection(G)
    assert_partition_equal(C, [{0, 1, 2}, {3, 4, 5}])


def test_seed_argument():
    G = nx.barbell_graph(3, 0)
    C = kernighan_lin_bisection(G, seed=1)
    assert_partition_equal(C, [{0, 1, 2}, {3, 4, 5}])


def test_non_disjoint_partition():
    with pytest.raises(nx.NetworkXError):
        G = nx.barbell_graph(3, 0)
        partition = ({0, 1, 2}, {2, 3, 4, 5})
        kernighan_lin_bisection(G, partition)


def test_too_many_blocks():
    with pytest.raises(nx.NetworkXError):
        G = nx.barbell_graph(3, 0)
        partition = ({0, 1}, {2}, {3, 4, 5})
        kernighan_lin_bisection(G, partition)


def test_multigraph():
    G = nx.cycle_graph(4)
    M = nx.MultiGraph(G.edges())
    M.add_edges_from(G.edges())
    M.remove_edge(1, 2)
    A, B = kernighan_lin_bisection(M)
    assert_partition_equal([A, B], [{0, 1}, {2, 3}])
