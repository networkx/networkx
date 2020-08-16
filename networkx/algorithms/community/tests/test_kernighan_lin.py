"""Unit tests for the :mod:`networkx.algorithms.community.kernighan_lin`
module.

"""
import pytest

import networkx as nx
from networkx.algorithms.community import kernighan_lin_bisection
from itertools import permutations


def assert_partition_equal(x, y):
    assert set(map(frozenset, x)) == set(map(frozenset, y))


def test_partition():
    G = nx.barbell_graph(3, 0)
    C = kernighan_lin_bisection(G)
    assert_partition_equal(C, [{0, 1, 2}, {3, 4, 5}])


def test_partition_argument():
    G = nx.barbell_graph(3, 0)
    partition = [{0, 1, 2}, {3, 4, 5}]
    C = kernighan_lin_bisection(G, partition)
    assert_partition_equal(C, partition)


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
    for labels in permutations(range(4)):
        mapping = dict(zip(M, labels))
        A, B = kernighan_lin_bisection(nx.relabel_nodes(M, mapping), seed=0)
        assert_partition_equal(
            [A, B], [{mapping[0], mapping[1]}, {mapping[2], mapping[3]}]
        )
