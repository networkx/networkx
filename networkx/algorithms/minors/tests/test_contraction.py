"""Unit tests for the :mod:`networkx.algorithms.minors.contraction` module."""

import pytest

import networkx as nx
from networkx.utils import arbitrary_element, edges_equal, nodes_equal


def test_quotient_graph_complete_multipartite():
    """Tests that the quotient graph of the complete *n*-partite graph
    under the "same neighbors" node relation is the complete graph on *n*
    nodes.

    """
    G = nx.complete_multipartite_graph(2, 3, 4)
    # Two nodes are equivalent if they are not adjacent but have the same
    # neighbor set.

    def same_neighbors(u, v):
        return u not in G[v] and v not in G[u] and G[u] == G[v]

    expected = nx.complete_graph(3)
    actual = nx.quotient_graph(G, same_neighbors)
    # It won't take too long to run a graph isomorphism algorithm on such
    # small graphs.
    assert nx.is_isomorphic(expected, actual)


def test_quotient_graph_complete_bipartite():
    """Tests that the quotient graph of the complete bipartite graph under
    the "same neighbors" node relation is `K_2`.

    """
    G = nx.complete_bipartite_graph(2, 3)
    # Two nodes are equivalent if they are not adjacent but have the same
    # neighbor set.

    def same_neighbors(u, v):
        return u not in G[v] and v not in G[u] and G[u] == G[v]

    expected = nx.complete_graph(2)
    actual = nx.quotient_graph(G, same_neighbors)
    # It won't take too long to run a graph isomorphism algorithm on such
    # small graphs.
    assert nx.is_isomorphic(expected, actual)


def test_quotient_graph_edge_relation():
    """Tests for specifying an alternate edge relation for the quotient
    graph.

    """
    G = nx.path_graph(5)

    def identity(u, v):
        return u == v

    def same_parity(b, c):
        return arbitrary_element(b) % 2 == arbitrary_element(c) % 2

    actual = nx.quotient_graph(G, identity, same_parity)
    expected = nx.Graph()
    expected.add_edges_from([(0, 2), (0, 4), (2, 4)])
    expected.add_edge(1, 3)
    assert nx.is_isomorphic(actual, expected)


def test_condensation_as_quotient():
    """This tests that the condensation of a graph can be viewed as the
    quotient graph under the "in the same connected component" equivalence
    relation.

    """
    # This example graph comes from the file `test_strongly_connected.py`.
    G = nx.DiGraph()
    G.add_edges_from(
        [
            (1, 2),
            (2, 3),
            (2, 11),
            (2, 12),
            (3, 4),
            (4, 3),
            (4, 5),
            (5, 6),
            (6, 5),
            (6, 7),
            (7, 8),
            (7, 9),
            (7, 10),
            (8, 9),
            (9, 7),
            (10, 6),
            (11, 2),
            (11, 4),
            (11, 6),
            (12, 6),
            (12, 11),
        ]
    )
    scc = list(nx.strongly_connected_components(G))
    C = nx.condensation(G, scc)
    component_of = C.graph["mapping"]
    # Two nodes are equivalent if they are in the same connected component.

    def same_component(u, v):
        return component_of[u] == component_of[v]

    Q = nx.quotient_graph(G, same_component)
    assert nx.is_isomorphic(C, Q)


def test_path():
    G = nx.path_graph(6)
    partition = [{0, 1}, {2, 3}, {4, 5}]
    M = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(M, [0, 1, 2])
    assert edges_equal(M.edges(), [(0, 1), (1, 2)])
    for n in M:
        assert M.nodes[n]["nedges"] == 1
        assert M.nodes[n]["nnodes"] == 2
        assert M.nodes[n]["density"] == 1


def test_path__partition_provided_as_dict_of_lists():
    G = nx.path_graph(6)
    partition = {0: [0, 1], 2: [2, 3], 4: [4, 5]}
    M = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(M, [0, 1, 2])
    assert edges_equal(M.edges(), [(0, 1), (1, 2)])
    for n in M:
        assert M.nodes[n]["nedges"] == 1
        assert M.nodes[n]["nnodes"] == 2
        assert M.nodes[n]["density"] == 1


def test_path__partition_provided_as_dict_of_tuples():
    G = nx.path_graph(6)
    partition = {0: (0, 1), 2: (2, 3), 4: (4, 5)}
    M = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(M, [0, 1, 2])
    assert edges_equal(M.edges(), [(0, 1), (1, 2)])
    for n in M:
        assert M.nodes[n]["nedges"] == 1
        assert M.nodes[n]["nnodes"] == 2
        assert M.nodes[n]["density"] == 1


def test_path__partition_provided_as_dict_of_sets():
    G = nx.path_graph(6)
    partition = {0: {0, 1}, 2: {2, 3}, 4: {4, 5}}
    M = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(M, [0, 1, 2])
    assert edges_equal(M.edges(), [(0, 1), (1, 2)])
    for n in M:
        assert M.nodes[n]["nedges"] == 1
        assert M.nodes[n]["nnodes"] == 2
        assert M.nodes[n]["density"] == 1


def test_multigraph_path():
    G = nx.MultiGraph(nx.path_graph(6))
    partition = [{0, 1}, {2, 3}, {4, 5}]
    M = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(M, [0, 1, 2])
    assert edges_equal(M.edges(), [(0, 1), (1, 2)])
    for n in M:
        assert M.nodes[n]["nedges"] == 1
        assert M.nodes[n]["nnodes"] == 2
        assert M.nodes[n]["density"] == 1


def test_directed_path():
    G = nx.DiGraph()
    nx.add_path(G, range(6))
    partition = [{0, 1}, {2, 3}, {4, 5}]
    M = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(M, [0, 1, 2])
    assert edges_equal(M.edges(), [(0, 1), (1, 2)], directed=True)
    for n in M:
        assert M.nodes[n]["nedges"] == 1
        assert M.nodes[n]["nnodes"] == 2
        assert M.nodes[n]["density"] == 0.5


def test_directed_multigraph_path():
    G = nx.MultiDiGraph()
    nx.add_path(G, range(6))
    partition = [{0, 1}, {2, 3}, {4, 5}]
    M = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(M, [0, 1, 2])
    assert edges_equal(M.edges(), [(0, 1), (1, 2)], directed=True)
    for n in M:
        assert M.nodes[n]["nedges"] == 1
        assert M.nodes[n]["nnodes"] == 2
        assert M.nodes[n]["density"] == 0.5


@pytest.mark.parametrize("graph_type", (nx.DiGraph, nx.MultiDiGraph))
@pytest.mark.parametrize("custom_relation", (False, True))
def test_quotient_graph_directed_weights(graph_type, custom_relation):
    G = graph_type()
    G.add_weighted_edges_from([(0, 2, 2), (1, 3, 5), (2, 0, 11), (3, 1, 17)])
    G.add_edge(0, 1, weight=100)  # An internal edge does not contribute.
    if G.is_multigraph():
        G.add_edge(0, 2, weight=7)
    partition = [{0, 1}, {2, 3}]
    relation = (lambda b, c: True) if custom_relation else None
    Q = nx.quotient_graph(
        G, partition, edge_relation=relation, create_using=nx.DiGraph, relabel=True
    )
    assert Q[0][1]["weight"] == (14 if G.is_multigraph() else 7)
    assert Q[1][0]["weight"] == 28


@pytest.mark.parametrize("graph_type", (nx.MultiGraph, nx.MultiDiGraph))
def test_quotient_graph_parallel_edge_attributes(graph_type):
    G = graph_type()
    G.add_edge(0, 2, key="same", capacity=2, name="first")
    G.add_edge(0, 2, key="other", capacity=3, name="second")
    G.add_edge(1, 3, key="same", capacity=5, name="third")
    G.add_edge(0, 1, capacity=100, name="internal")
    if G.is_directed():
        G.add_edge(2, 0, capacity=11, name="reverse")

    def unused_edge_data(b, c):
        pytest.fail("edge_data must not be called for a multigraph quotient")

    Q = nx.quotient_graph(G, [{0, 1}, {2, 3}], edge_data=unused_edge_data, relabel=True)
    assert sorted((d["name"], d["capacity"]) for d in Q[0][1].values()) == [
        ("first", 2),
        ("second", 3),
        ("third", 5),
    ]
    assert Q.number_of_edges() == (4 if G.is_directed() else 3)
    if G.is_directed():
        assert list(Q[1][0].values()) == [{"capacity": 11, "name": "reverse"}]
    assert G[0][2]["same"] == {"capacity": 2, "name": "first"}


@pytest.mark.parametrize("graph_type", (nx.Graph, nx.MultiGraph))
@pytest.mark.parametrize("target_type", (nx.DiGraph, nx.MultiDiGraph))
def test_quotient_graph_directed_from_undirected(graph_type, target_type):
    G = graph_type()
    G.add_edge(1, 0, weight=2)
    if G.is_multigraph():
        G.add_edge(1, 0, weight=3)
    Q = nx.quotient_graph(G, [{0}, {1}], create_using=target_type, relabel=True)
    assert set(Q.edges()) == {(0, 1), (1, 0)}
    if Q.is_multigraph():
        expected = [2, 3] if G.is_multigraph() else [2]
        assert sorted(d["weight"] for d in Q[0][1].values()) == expected
        assert sorted(d["weight"] for d in Q[1][0].values()) == expected
    else:
        expected = 5 if G.is_multigraph() else 2
        assert Q[0][1]["weight"] == Q[1][0]["weight"] == expected


@pytest.mark.parametrize("graph_type", (nx.DiGraph, nx.MultiDiGraph))
@pytest.mark.parametrize("target_type", (nx.Graph, nx.MultiGraph))
def test_quotient_graph_undirected_from_directed(graph_type, target_type):
    G = graph_type()
    G.add_edge(1, 0, weight=2)
    G.add_edge(0, 1, weight=3)
    G.add_edge(2, 1, weight=7)  # Only the reverse block orientation exists.
    if G.is_multigraph():
        G.add_edge(1, 0, weight=5)
    Q = nx.quotient_graph(G, [{0}, {1}, {2}], create_using=target_type, relabel=True)
    assert set(Q.edges()) == {(0, 1), (1, 2)}
    if Q.is_multigraph():
        expected = [2, 3, 5] if G.is_multigraph() else [2, 3]
        assert sorted(d["weight"] for d in Q[0][1].values()) == expected
        assert list(Q[1][2].values()) == [{"weight": 7}]
    else:
        assert Q[0][1]["weight"] == (10 if G.is_multigraph() else 5)
        assert Q[1][2]["weight"] == 7


def test_overlapping_blocks():
    with pytest.raises(nx.NetworkXException):
        G = nx.path_graph(6)
        partition = [{0, 1, 2}, {2, 3}, {4, 5}]
        nx.quotient_graph(G, partition)


def test_weighted_path():
    G = nx.path_graph(6)
    for i in range(5):
        G[i][i + 1]["w"] = i + 1
    partition = [{0, 1}, {2, 3}, {4, 5}]
    M = nx.quotient_graph(G, partition, weight="w", relabel=True)
    assert nodes_equal(M, [0, 1, 2])
    assert edges_equal(M.edges(), [(0, 1), (1, 2)])
    assert M[0][1]["weight"] == 2
    assert M[1][2]["weight"] == 4
    for n in M:
        assert M.nodes[n]["nedges"] == 1
        assert M.nodes[n]["nnodes"] == 2
        assert M.nodes[n]["density"] == 1


def test_barbell():
    G = nx.barbell_graph(3, 0)
    partition = [{0, 1, 2}, {3, 4, 5}]
    M = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(M, [0, 1])
    assert edges_equal(M.edges(), [(0, 1)])
    for n in M:
        assert M.nodes[n]["nedges"] == 3
        assert M.nodes[n]["nnodes"] == 3
        assert M.nodes[n]["density"] == 1


def test_barbell_plus():
    G = nx.barbell_graph(3, 0)
    # Add an extra edge joining the bells.
    G.add_edge(0, 5)
    partition = [{0, 1, 2}, {3, 4, 5}]
    M = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(M, [0, 1])
    assert edges_equal(M.edges(), [(0, 1)])
    assert M[0][1]["weight"] == 2
    for n in M:
        assert M.nodes[n]["nedges"] == 3
        assert M.nodes[n]["nnodes"] == 3
        assert M.nodes[n]["density"] == 1


def test_blockmodel():
    G = nx.path_graph(6)
    partition = [[0, 1], [2, 3], [4, 5]]
    M = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(M.nodes(), [0, 1, 2])
    assert edges_equal(M.edges(), [(0, 1), (1, 2)])
    for n in M.nodes():
        assert M.nodes[n]["nedges"] == 1
        assert M.nodes[n]["nnodes"] == 2
        assert M.nodes[n]["density"] == 1.0


def test_multigraph_blockmodel():
    G = nx.MultiGraph(nx.path_graph(6))
    partition = [[0, 1], [2, 3], [4, 5]]
    M = nx.quotient_graph(G, partition, create_using=nx.MultiGraph(), relabel=True)
    assert nodes_equal(M.nodes(), [0, 1, 2])
    assert edges_equal(M.edges(), [(0, 1), (1, 2)])
    for n in M.nodes():
        assert M.nodes[n]["nedges"] == 1
        assert M.nodes[n]["nnodes"] == 2
        assert M.nodes[n]["density"] == 1.0


def test_quotient_graph_incomplete_partition():
    G = nx.path_graph(6)
    partition = []
    H = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(H.nodes(), [])
    assert edges_equal(H.edges(), [])

    partition = [[0, 1], [2, 3], [5]]
    H = nx.quotient_graph(G, partition, relabel=True)
    assert nodes_equal(H.nodes(), [0, 1, 2])
    assert edges_equal(H.edges(), [(0, 1)])


@pytest.mark.parametrize("graph_type", (nx.Graph, nx.MultiGraph))
@pytest.mark.parametrize("relabel", (False, True))
def test_quotient_graph_crossing_edges(graph_type, relabel):
    # Node order makes crossing edges appear in both block orientations.
    # Node labels need not be comparable, and zero total weight is still an edge.
    G = graph_type()
    G.add_nodes_from([0, "a", 1, "b", "isolated"])
    G.add_edge(0, "a", cost=2)
    G.add_edge("a", 1, cost=-3)
    G.add_edge(1, "b")
    G.add_edge(0, 1, cost=100)
    G.add_edge("a", "a", cost=100)
    if G.is_multigraph():
        G.add_edge(0, "a", cost=4)
    partition = [{0, 1}, {"a", "b"}, {"isolated"}, set()]
    Q = nx.quotient_graph(
        G, partition, weight="cost", create_using=nx.Graph, relabel=relabel
    )
    blocks = list(range(4)) if relabel else [frozenset(b) for b in partition]
    assert list(Q) == blocks
    assert list(Q.edges(data=True)) == [
        (blocks[0], blocks[1], {"weight": 4 if G.is_multigraph() else 0})
    ]
    for q, b in zip(blocks, partition):
        S = G.subgraph(b)
        assert nodes_equal(Q.nodes[q]["graph"].nodes(data=True), S.nodes(data=True))
        assert edges_equal(Q.nodes[q]["graph"].edges(data=True), S.edges(data=True))
        assert Q.nodes[q]["nnodes"] == len(S)
        assert Q.nodes[q]["nedges"] == S.number_of_edges()
        assert Q.nodes[q]["density"] == nx.density(S)


def test_quotient_graph_callback_order():
    G = nx.Graph()
    G.add_edges_from([(3, 1), (2, 0), (1, 0), (2, 1)])
    partition = [frozenset([n]) for n in range(4)]
    calls = []

    def edge_data(b, c):
        calls.append((b, c))
        # add_edges_from supports attribute keys that are not strings.
        return {0: len(calls)}

    Q = nx.quotient_graph(G, partition, edge_data=edge_data, relabel=True)
    assert calls == [
        (partition[0], partition[1]),
        (partition[0], partition[2]),
        (partition[1], partition[2]),
        (partition[1], partition[3]),
    ]
    assert list(Q.edges(data=True)) == [
        (0, 1, {0: 1}),
        (0, 2, {0: 2}),
        (1, 2, {0: 3}),
        (1, 3, {0: 4}),
    ]


def test_quotient_graph_weight_objects_unchanged():
    np = pytest.importorskip("numpy")
    G = nx.Graph()
    first = np.array([1, 2])
    second = np.array([3, 4])
    G.add_edge(0, 2, weight=first)
    G.add_edge(1, 2, weight=second)
    Q = nx.quotient_graph(G, [{0, 1}, {2}], relabel=True)
    np.testing.assert_array_equal(Q[0][1]["weight"], [4, 6])
    np.testing.assert_array_equal(first, [1, 2])
    np.testing.assert_array_equal(second, [3, 4])


def test_quotient_graph_float_reduction_order():
    G = nx.Graph()
    G.add_nodes_from([2, 0, 1, 3])
    G.add_weighted_edges_from([(0, 3, 1e16), (1, 3, 1), (2, 3, -1e16)])
    b, c = frozenset([0, 1, 2]), frozenset([3])
    # The default reduction visits the nodes in b | c order, which need not
    # match graph insertion order. Retain that order for inexact weights.
    expected = sum(data["weight"] for _, _, data in G.edges(b | c, data=True))
    Q = nx.quotient_graph(G, [b, c], relabel=True)
    assert Q[0][1]["weight"] == expected


def test_quotient_graph_mutating_edge_callback():
    G = nx.Graph([(0, 1), (1, 2)])

    def edge_data(b, c):
        if b == {0} and c == {1}:
            G.remove_edge(1, 2)
        return {}

    # The callback closes over G, so test the native implementation without
    # converting G to a backend graph that the callback cannot access.
    Q = nx.quotient_graph(
        G, [{0}, {1}, {2}], edge_data=edge_data, relabel=True, backend="networkx"
    )
    assert list(Q.edges) == [(0, 1)]


@pytest.mark.parametrize("store_contraction_as", ("contraction", "c", None))
@pytest.mark.parametrize("copy", (True, False))
@pytest.mark.parametrize("selfloops", (True, False))
def test_undirected_node_contraction(store_contraction_as, copy, selfloops):
    """Tests for node contraction in an undirected graph."""
    G = nx.cycle_graph(4)
    actual = nx.contracted_nodes(
        G,
        0,
        1,
        copy=copy,
        self_loops=selfloops,
        store_contraction_as=store_contraction_as,
    )

    expected = nx.cycle_graph(3)
    if selfloops:
        expected.add_edge(0, 0)

    assert nx.is_isomorphic(actual, expected)

    if not copy:
        assert actual is G

    # Test contracted node attributes
    if store_contraction_as is not None:
        assert actual.nodes[0][store_contraction_as] == {1: {}}
    else:
        assert actual.nodes[0] == {}
    # There should be no contracted edges for this case
    assert all(d == {} for _, _, d in actual.edges(data=True))


@pytest.mark.parametrize("store_contraction_as", ("contraction", "c", None))
@pytest.mark.parametrize("copy", (True, False))
@pytest.mark.parametrize("selfloops", (True, False))
def test_directed_node_contraction(store_contraction_as, copy, selfloops):
    """Tests for node contraction in a directed graph."""
    G = nx.DiGraph(nx.cycle_graph(4))
    actual = nx.contracted_nodes(
        G,
        0,
        1,
        copy=copy,
        self_loops=selfloops,
        store_contraction_as=store_contraction_as,
    )

    expected = nx.DiGraph(nx.cycle_graph(3))
    if selfloops:
        expected.add_edge(0, 0)

    assert nx.is_isomorphic(actual, expected)

    if not copy:
        assert actual is G
    # Test contracted node attributes
    if store_contraction_as is not None:
        assert actual.nodes[0][store_contraction_as] == {1: {}}
    else:
        assert actual.nodes[0] == {}
    # Test contracted edge attributes (only relevant if self loops is enabled)
    if selfloops and store_contraction_as:
        assert actual.edges[(0, 0)][store_contraction_as] == {(1, 0): {}}
    else:
        assert all(d == {} for _, _, d in actual.edges(data=True))


@pytest.mark.parametrize("store_contraction_as", ("contraction", "c", None))
@pytest.mark.parametrize("copy", (True, False))
@pytest.mark.parametrize("selfloops", (True, False))
def test_contracted_nodes_multigraph(store_contraction_as, copy, selfloops):
    """Tests that using a MultiGraph creates multiple edges. `store_contraction_as`
    has no effect for multigraphs."""
    G = nx.path_graph(3, create_using=nx.MultiGraph)
    G.add_edges_from([(0, 1), (0, 0), (0, 2)])
    actual = nx.contracted_nodes(
        G,
        0,
        2,
        copy=copy,
        self_loops=selfloops,
        store_contraction_as=store_contraction_as,
    )
    # Two (0, 1) edges from G, another from the contraction of edge (1, 2)
    expected = nx.MultiGraph([(0, 1), (0, 1), (0, 1), (0, 0)])
    # One (0, 0) edge from G, another from the contraction of edge (0, 2), but
    # only if `selfloops` is True
    if selfloops:
        expected.add_edge(0, 0)

    assert edges_equal(actual.edges, expected.edges)
    if not copy:
        assert actual is G


def test_multigraph_keys():
    """Tests that multiedge keys are reset in new graph."""
    G = nx.path_graph(3, create_using=nx.MultiGraph())
    G.add_edge(0, 1, 5)
    G.add_edge(0, 0, 0)
    G.add_edge(0, 2, 5)
    actual = nx.contracted_nodes(G, 0, 2)
    expected = nx.MultiGraph()
    expected.add_edge(0, 1, 0)
    expected.add_edge(0, 1, 5)
    expected.add_edge(0, 1, 2)  # keyed as 2 b/c 2 edges already in G
    expected.add_edge(0, 0, 0)
    expected.add_edge(0, 0, 1)  # this comes from (0, 2, 5)
    assert edges_equal(actual.edges, expected.edges)


@pytest.mark.parametrize("store_contraction_as", ("contraction", "c", None))
@pytest.mark.parametrize("copy", (True, False))
@pytest.mark.parametrize("selfloops", (True, False))
def test_node_attributes(store_contraction_as, copy, selfloops):
    """Tests that node contraction preserves node attributes."""
    G = nx.cycle_graph(4)
    # Add some data to the two nodes being contracted.
    G.nodes[0]["foo"] = "bar"
    G.nodes[1]["baz"] = "xyzzy"
    actual = nx.contracted_nodes(
        G,
        0,
        1,
        copy=copy,
        self_loops=selfloops,
        store_contraction_as=store_contraction_as,
    )
    # We expect that contracting the nodes 0 and 1 in C_4 yields K_3, but
    # with nodes labeled 0, 2, and 3.
    expected = nx.complete_graph(3)
    expected = nx.relabel_nodes(expected, {1: 2, 2: 3})
    expected.nodes[0]["foo"] = "bar"
    # ... and a self-loop (0, 0), if self_loops=True
    if selfloops:
        expected.add_edge(0, 0)

    if store_contraction_as:
        cdict = {1: {"baz": "xyzzy"}}
        expected.nodes[0].update({"foo": "bar", store_contraction_as: cdict})

    assert nx.is_isomorphic(actual, expected)
    assert actual.nodes(data=True) == expected.nodes(data=True)
    if not copy:
        assert actual is G


@pytest.mark.parametrize("store_contraction_as", ("contraction", "c", None))
def test_edge_attributes(store_contraction_as):
    """Tests that node contraction preserves edge attributes."""
    # Shape: src1 --> dest <-- src2
    G = nx.DiGraph([("src1", "dest"), ("src2", "dest")])
    G["src1"]["dest"]["value"] = "src1-->dest"
    G["src2"]["dest"]["value"] = "src2-->dest"

    # New Shape: src1 --> dest
    H = nx.contracted_nodes(
        G, "src1", "src2", store_contraction_as=store_contraction_as
    )
    assert H.edges[("src1", "dest")]["value"] == "src1-->dest"  # Should be unchanged
    if store_contraction_as:
        assert (
            H.edges[("src1", "dest")][store_contraction_as][("src2", "dest")]["value"]
            == "src2-->dest"
        )
    else:
        assert store_contraction_as not in H.edges[("src1", "dest")]

    G = nx.MultiDiGraph(G)
    # New Shape: src1 -(x2)-> dest
    H = nx.contracted_nodes(
        G, "src1", "src2", store_contraction_as=store_contraction_as
    )
    # store_contraction should not affect multigraphs
    assert len(H.edges(("src1", "dest"))) == 2
    assert H.edges[("src1", "dest", 0)]["value"] == "src1-->dest"
    assert H.edges[("src1", "dest", 1)]["value"] == "src2-->dest"


def test_contract_loop_graph():
    """Tests for node contraction when nodes have loops."""
    G = nx.cycle_graph(4)
    G.add_edge(0, 0)
    actual = nx.contracted_nodes(G, 0, 1)
    expected = nx.complete_graph([0, 2, 3])
    expected.add_edge(0, 0)
    assert edges_equal(actual.edges, expected.edges)
    actual = nx.contracted_nodes(G, 1, 0)
    expected = nx.complete_graph([1, 2, 3])
    expected.add_edge(1, 1)
    assert edges_equal(actual.edges, expected.edges)


@pytest.mark.parametrize("store_contraction_as", ("contraction", "c", None))
@pytest.mark.parametrize("copy", (True, False))
@pytest.mark.parametrize("selfloops", (True, False))
def test_undirected_edge_contraction(store_contraction_as, copy, selfloops):
    """Tests for node contraction in an undirected graph."""
    G = nx.cycle_graph(4)
    actual = nx.contracted_edge(
        G,
        (0, 1),
        copy=copy,
        self_loops=selfloops,
        store_contraction_as=store_contraction_as,
    )

    expected = nx.cycle_graph(3)
    if selfloops:
        expected.add_edge(0, 0)

    assert nx.is_isomorphic(actual, expected)

    if not copy:
        assert actual is G

    # Test contracted node attributes
    if store_contraction_as is not None:
        assert actual.nodes[0][store_contraction_as] == {1: {}}
    else:
        assert actual.nodes[0] == {}
    # There should be no contracted edges for this case
    assert all(d == {} for _, _, d in actual.edges(data=True))


@pytest.mark.parametrize("edge", [(0, 1), (0, 1, 0)])
@pytest.mark.parametrize("store_contraction_as", ("contraction", "c", None))
@pytest.mark.parametrize("copy", [True, False])
@pytest.mark.parametrize("selfloops", [True, False])
def test_multigraph_edge_contraction(edge, store_contraction_as, copy, selfloops):
    """Tests for edge contraction in a multigraph"""
    G = nx.cycle_graph(4, create_using=nx.MultiGraph)
    actual = nx.contracted_edge(
        G,
        edge,
        copy=copy,
        self_loops=selfloops,
        store_contraction_as=store_contraction_as,
    )
    expected = nx.relabel_nodes(
        nx.complete_graph(3, create_using=nx.MultiGraph), {0: 0, 1: 2, 2: 3}
    )
    if selfloops:
        expected.add_edge(0, 0)

    assert edges_equal(actual.edges, expected.edges)
    if not copy:
        assert actual is G


def test_nonexistent_edge():
    """Tests that attempting to contract a nonexistent edge raises an
    exception.

    """
    G = nx.cycle_graph(4)
    with pytest.raises(ValueError):
        nx.contracted_edge(G, (0, 2))
