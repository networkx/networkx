"""Unit tests for the :mod:`networkx.algorithms.community.utils` module."""

import networkx as nx


def test_is_partition():
    G = nx.empty_graph(3)
    assert nx.community.is_partition(G, [{0, 1}, {2}])
    assert nx.community.is_partition(G, ({0, 1}, {2}))
    assert nx.community.is_partition(G, ([0, 1], [2]))
    assert nx.community.is_partition(G, [[0, 1], [2]])


def test_not_covering():
    G = nx.empty_graph(3)
    assert not nx.community.is_partition(G, [{0}, {1}])


def test_not_disjoint():
    G = nx.empty_graph(3)
    assert not nx.community.is_partition(G, [{0, 1}, {1, 2}])


def test_not_node():
    G = nx.empty_graph(3)
    assert not nx.community.is_partition(G, [{0, 1}, {3}])


def test_is_cover_partition():
    G = nx.path_graph(4)
    assert nx.community.is_cover(G, [{0, 1}, {2, 3}])


def test_is_cover_overlapping():
    G = nx.path_graph(4)
    assert nx.community.is_cover(G, [{0, 1, 2}, {2, 3}])


def test_is_cover_node_in_many_communities():
    G = nx.path_graph(4)
    assert nx.community.is_cover(G, [{0, 1, 2, 3}, {1, 2}, {2, 3}])


def test_is_cover_iterable_inputs():
    G = nx.path_graph(4)
    # Tuple of frozensets (e.g. output of k_clique_communities)
    assert nx.community.is_cover(G, (frozenset({0, 1}), frozenset({2, 3})))
    # Iterator (gets exhausted internally)
    assert nx.community.is_cover(G, iter([{0, 1, 2}, {2, 3}]))


def test_is_cover_missing_node():
    G = nx.path_graph(4)
    assert not nx.community.is_cover(G, [{0, 1, 2}])


def test_is_cover_empty_communities_nonempty_graph():
    G = nx.path_graph(4)
    assert not nx.community.is_cover(G, [])


def test_is_cover_empty_graph_empty_communities():
    assert nx.community.is_cover(nx.Graph(), [])


def test_is_cover_extraneous_nodes_ignored():
    # Nodes appearing in communities that are not in G are ignored,
    # mirroring is_partition's behavior.
    G = nx.path_graph(4)
    assert nx.community.is_cover(G, [{0, 1, 2, 3}, {99}])
