# Jordi Torrents
# Test for k-cutsets
import itertools

import pytest

import networkx as nx
from networkx.algorithms import flow
from networkx.algorithms.connectivity.kcutsets import _is_separating_set

MAX_CUTSETS_TO_TEST = 100

flow_funcs = [
    flow.boykov_kolmogorov,
    flow.dinitz,
    flow.edmonds_karp,
    flow.preflow_push,
    flow.shortest_augmenting_path,
]


##
# Some nice synthetic graphs
##
def graph_example_1():
    G = nx.convert_node_labels_to_integers(
        nx.grid_graph([5, 5]), label_attribute="labels"
    )
    rlabels = nx.get_node_attributes(G, "labels")
    labels = {v: k for k, v in rlabels.items()}

    for nodes in [
        (labels[(0, 0)], labels[(1, 0)]),
        (labels[(0, 4)], labels[(1, 4)]),
        (labels[(3, 0)], labels[(4, 0)]),
        (labels[(3, 4)], labels[(4, 4)]),
    ]:
        new_node = G.order() + 1
        # Petersen graph is triconnected
        P = nx.petersen_graph()
        G = nx.disjoint_union(G, P)
        # Add two edges between the grid and P
        G.add_edge(new_node + 1, nodes[0])
        G.add_edge(new_node, nodes[1])
        # K5 is 4-connected
        K = nx.complete_graph(5)
        G = nx.disjoint_union(G, K)
        # Add three edges between P and K5
        G.add_edge(new_node + 2, new_node + 11)
        G.add_edge(new_node + 3, new_node + 12)
        G.add_edge(new_node + 4, new_node + 13)
        # Add another K5 sharing a node
        G = nx.disjoint_union(G, K)
        nbrs = G[new_node + 10]
        G.remove_node(new_node + 10)
        for nbr in nbrs:
            G.add_edge(new_node + 17, nbr)
        G.add_edge(new_node + 16, new_node + 5)
    return G


def torrents_and_ferraro_graph():
    G = nx.convert_node_labels_to_integers(
        nx.grid_graph([5, 5]), label_attribute="labels"
    )
    rlabels = nx.get_node_attributes(G, "labels")
    labels = {v: k for k, v in rlabels.items()}

    for nodes in [(labels[(0, 4)], labels[(1, 4)]), (labels[(3, 4)], labels[(4, 4)])]:
        new_node = G.order() + 1
        # Petersen graph is triconnected
        P = nx.petersen_graph()
        G = nx.disjoint_union(G, P)
        # Add two edges between the grid and P
        G.add_edge(new_node + 1, nodes[0])
        G.add_edge(new_node, nodes[1])
        # K5 is 4-connected
        K = nx.complete_graph(5)
        G = nx.disjoint_union(G, K)
        # Add three edges between P and K5
        G.add_edge(new_node + 2, new_node + 11)
        G.add_edge(new_node + 3, new_node + 12)
        G.add_edge(new_node + 4, new_node + 13)
        # Add another K5 sharing a node
        G = nx.disjoint_union(G, K)
        nbrs = G[new_node + 10]
        G.remove_node(new_node + 10)
        for nbr in nbrs:
            G.add_edge(new_node + 17, nbr)
        # Commenting this makes the graph not biconnected !!
        # This stupid mistake make one reviewer very angry :P
        G.add_edge(new_node + 16, new_node + 8)

    for nodes in [(labels[(0, 0)], labels[(1, 0)]), (labels[(3, 0)], labels[(4, 0)])]:
        new_node = G.order() + 1
        # Petersen graph is triconnected
        P = nx.petersen_graph()
        G = nx.disjoint_union(G, P)
        # Add two edges between the grid and P
        G.add_edge(new_node + 1, nodes[0])
        G.add_edge(new_node, nodes[1])
        # K5 is 4-connected
        K = nx.complete_graph(5)
        G = nx.disjoint_union(G, K)
        # Add three edges between P and K5
        G.add_edge(new_node + 2, new_node + 11)
        G.add_edge(new_node + 3, new_node + 12)
        G.add_edge(new_node + 4, new_node + 13)
        # Add another K5 sharing two nodes
        G = nx.disjoint_union(G, K)
        nbrs = G[new_node + 10]
        G.remove_node(new_node + 10)
        for nbr in nbrs:
            G.add_edge(new_node + 17, nbr)
        nbrs2 = G[new_node + 9]
        G.remove_node(new_node + 9)
        for nbr in nbrs2:
            G.add_edge(new_node + 18, nbr)
    return G


# Helper function
def _check_separating_sets(G):
    for cc in nx.connected_components(G):
        if len(cc) < 3:
            continue
        Gc = G.subgraph(cc)
        node_conn = nx.node_connectivity(Gc)
        all_cuts = nx.all_node_cuts(Gc)
        # Only test a limited number of cut sets to reduce test time.
        for cut in itertools.islice(all_cuts, MAX_CUTSETS_TO_TEST):
            assert node_conn == len(cut)
            assert not nx.is_connected(nx.restricted_view(G, cut, []))


def test_torrents_and_ferraro_graph():
    G = torrents_and_ferraro_graph()
    _check_separating_sets(G)


def test_example_1():
    G = graph_example_1()
    _check_separating_sets(G)


def test_random_gnp():
    G = nx.gnp_random_graph(100, 0.1, seed=42)
    _check_separating_sets(G)


def test_shell():
    constructor = [(20, 80, 0.8), (80, 180, 0.6)]
    G = nx.random_shell_graph(constructor, seed=42)
    _check_separating_sets(G)


def test_configuration():
    deg_seq = nx.random_powerlaw_tree_sequence(100, tries=5, seed=72)
    G = nx.Graph(nx.configuration_model(deg_seq))
    G.remove_edges_from(nx.selfloop_edges(G))
    _check_separating_sets(G)


def test_karate():
    G = nx.karate_club_graph()
    _check_separating_sets(G)


def _generate_no_biconnected(max_attempts=50):
    attempts = 0
    while True:
        G = nx.fast_gnp_random_graph(100, 0.0575, seed=42)
        if nx.is_connected(G) and not nx.is_biconnected(G):
            attempts = 0
            yield G
        else:
            if attempts >= max_attempts:
                msg = f"Tried {attempts} times: no suitable Graph."
                raise Exception(msg)
            else:
                attempts += 1


def test_articulation_points():
    Ggen = _generate_no_biconnected()
    for i in range(1):  # change 1 to 3 or more for more realizations.
        G = next(Ggen)
        articulation_points = [{a} for a in nx.articulation_points(G)]
        for cut in nx.all_node_cuts(G):
            assert cut in articulation_points


def test_grid_2d_graph():
    # All minimum node cuts of a 2d grid
    # are the four pairs of nodes that are
    # neighbors of the four corner nodes.
    G = nx.grid_2d_graph(5, 5)
    solution = [{(0, 1), (1, 0)}, {(3, 0), (4, 1)}, {(3, 4), (4, 3)}, {(0, 3), (1, 4)}]
    for cut in nx.all_node_cuts(G):
        assert cut in solution


def test_disconnected_graph():
    G = nx.fast_gnp_random_graph(100, 0.01, seed=42)
    cuts = nx.all_node_cuts(G)
    pytest.raises(nx.NetworkXError, next, cuts)


@pytest.mark.parametrize("G", [nx.grid_2d_graph(4, 4), nx.cycle_graph(5)])
@pytest.mark.parametrize("flow_func", flow_funcs)
def test_alternative_flow_functions(G, flow_func):
    node_conn = nx.node_connectivity(G)
    all_cuts = nx.all_node_cuts(G, flow_func=flow_func)
    # Only test a limited number of cut sets to reduce test time.
    for cut in itertools.islice(all_cuts, MAX_CUTSETS_TO_TEST):
        assert node_conn == len(cut)
        assert not nx.is_connected(nx.restricted_view(G, cut, []))


def test_is_separating_set_complete_graph():
    G = nx.complete_graph(5)
    assert _is_separating_set(G, {0, 1, 2, 3})


def test_is_separating_set():
    for i in [5, 10, 15]:
        G = nx.star_graph(i)
        max_degree_node = max(G, key=G.degree)
        assert _is_separating_set(G, {max_degree_node})


def test_non_repeated_cuts():
    # The algorithm was repeating the cut {0, 1} for the giant biconnected
    # component of the Karate club graph.
    K = nx.karate_club_graph()
    bcc = max(list(nx.biconnected_components(K)), key=len)
    G = K.subgraph(bcc)
    solution = [{32, 33}, {2, 33}, {0, 3}, {0, 1}, {29, 33}]
    cuts = list(nx.all_node_cuts(G))
    assert len(solution) == len(cuts)
    for cut in cuts:
        assert cut in solution


def test_cycle_graph():
    G = nx.cycle_graph(5)
    solution = [{0, 2}, {0, 3}, {1, 3}, {1, 4}, {2, 4}]
    cuts = list(nx.all_node_cuts(G))
    assert len(solution) == len(cuts)
    for cut in cuts:
        assert cut in solution


def test_complete_graph():
    G = nx.complete_graph(5)
    assert nx.node_connectivity(G) == 4
    assert list(nx.all_node_cuts(G)) == []


def test_all_node_cuts_simple_case():
    G = nx.complete_graph(5)
    G.remove_edges_from([(0, 1), (3, 4)])
    expected = [{0, 1, 2}, {2, 3, 4}]
    actual = list(nx.all_node_cuts(G))
    assert len(actual) == len(expected)
    for cut in actual:
        assert cut in expected


def _two_blobs(blob_size, separator_size):
    """Two cliques joined only through a separator of non adjacent nodes.

    The connectivity is `separator_size` and the separator is the only
    minimum cut, while every pair of nodes inside a blob is far more
    connected than that. That is the shape that makes the pre-filter fire.
    """
    G = nx.Graph()
    for prefix in "ab":
        blob = [f"{prefix}{i}" for i in range(blob_size)]
        G.add_edges_from(itertools.combinations(blob, 2))
    for i in range(separator_size):
        for prefix in "ab":
            G.add_edges_from((f"s{i}", f"{prefix}{j}") for j in range(blob_size))
    return G


@pytest.mark.parametrize(
    "G",
    [
        nx.karate_club_graph(),
        nx.florentine_families_graph(),
        _two_blobs(4, 2),
        _two_blobs(5, 3),
    ],
)
def test_all_node_cuts_is_complete_under_the_prefilter(G):
    """The approximate pre-filter must not drop a minimum cut.

    A pair of nodes whose approximate local node connectivity exceeds `k`
    cannot yield a cut of cardinality `k`, so `all_node_cuts` skips its
    maximum flow computation. These are graphs where that skip does fire,
    unlike the regular graphs elsewhere in this file, and the enumeration is
    checked against brute force over every `k`-subset of nodes.
    """
    k = nx.node_connectivity(G)
    expected = {
        frozenset(candidate)
        for candidate in itertools.combinations(G, k)
        if not nx.is_connected(nx.restricted_view(G, candidate, []))
    }
    assert expected, "the fixture has no minimum cut to find"
    assert {frozenset(cut) for cut in nx.all_node_cuts(G)} == expected


def test_all_node_cuts_sap():
    """Non-slow test for `all_node_cuts` using the shortest augmenting path flow."""
    G = nx.cycle_graph(5)
    node_conn = nx.node_connectivity(G)
    all_cuts = nx.all_node_cuts(G, flow_func=flow.shortest_augmenting_path)
    # Only test a limited number of cut sets to reduce test time.
    for cut in itertools.islice(all_cuts, MAX_CUTSETS_TO_TEST):
        assert node_conn == len(cut)
        assert not nx.is_connected(nx.restricted_view(G, cut, []))
