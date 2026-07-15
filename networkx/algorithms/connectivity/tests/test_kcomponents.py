# Test for Moody and White k-components algorithm
import pytest

import networkx as nx
from networkx.algorithms import flow
from networkx.algorithms.connectivity.kcomponents import (
    _consolidate,
    _generate_partition,
    _reconstruct_k_components,
    build_k_number_dict,
)

FLOW_FUNCS = (
    flow.boykov_kolmogorov,
    flow.dinitz,
    flow.edmonds_karp,
    flow.preflow_push,
    flow.shortest_augmenting_path,
)


##
# A nice synthetic graph
##
def torrents_and_ferraro_graph():
    # Graph from https://arxiv.org/pdf/1503.04476v1 p.26
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
        # This edge makes the graph biconnected; it's
        # needed because K5s share only one node.
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


def test_directed():
    with pytest.raises(nx.NetworkXNotImplemented):
        G = nx.gnp_random_graph(10, 0.2, directed=True, seed=42)
        nx.k_components(G)


def test_empty_k_components():
    G = nx.empty_graph(5)
    assert nx.k_components(G) == {}


@pytest.mark.parametrize("flow_func", FLOW_FUNCS)
def test_k_components_alternative_flow_func(flow_func):
    G = nx.lollipop_graph(5, 5)
    result = nx.k_components(G, flow_func=flow_func)
    _check_connectivity(G, result)


# Helper function
def _check_connectivity(G, k_components):
    for k, components in k_components.items():
        if k < 3:
            continue
        # check that k-components have node connectivity >= k.
        for component in components:
            C = G.subgraph(component)
            K = nx.node_connectivity(C)
            assert K >= k


def test_torrents_and_ferraro_graph():
    G = torrents_and_ferraro_graph()
    result = nx.k_components(G)
    _check_connectivity(G, result)

    # In this example graph there are 8 3-components, 4 with 15 nodes
    # and 4 with 5 nodes.
    assert len(result[3]) == 8
    assert len([c for c in result[3] if len(c) == 15]) == 4
    assert len([c for c in result[3] if len(c) == 5]) == 4
    # There are also 8 4-components all with 5 nodes.
    assert len(result[4]) == 8
    assert all(len(c) == 5 for c in result[4])


def test_generate_partition_does_not_drop_cutset_nodes():
    # Two icosahedra (5-connected) joined through three connector nodes,
    # plus a fourth node that makes the graph 4-connected. The minimum
    # 3-cutsets of the icosahedron-plus-connectors subproblem are the three
    # connector neighborhoods, and some of their nodes have all their
    # neighbors inside other cutsets. _generate_partition used to remove the
    # union of all cutsets in a single pass, dropping those nodes and losing
    # one of the two 5-components.
    A = nx.icosahedral_graph()
    B = nx.relabel_nodes(nx.icosahedral_graph(), {i: i + 12 for i in range(12)})
    G = nx.union(A, B)
    G.add_edges_from([(24, 0), (24, 1), (24, 2), (24, 12), (24, 13)])
    G.add_edges_from([(25, 3), (25, 4), (25, 5), (25, 14), (25, 15)])
    G.add_edges_from([(26, 6), (26, 7), (26, 8), (26, 16), (26, 17)])
    G.add_edges_from([(27, 9), (27, 10), (27, 20), (27, 21)])
    assert nx.node_connectivity(G) == 4
    result = nx.k_components(G)
    assert sorted(sorted(c) for c in result[5]) == [
        sorted(range(12)),
        sorted(range(12, 24)),
    ]
    # The whole graph is 4-connected, so it is the single k-component at
    # every level from 1 to 4.
    for k in range(1, 5):
        assert sorted(sorted(c) for c in result[k]) == [sorted(range(28))]


def test_reconstruction_does_not_replace_component_by_fragments():
    # A 7-connected graph: the whole graph is the only k-component at every
    # level up to 7. The recursive cuts record lower-connectivity fragments
    # whose union happens to cover all nodes; _reconstruct_k_components used
    # to skip propagating the whole-graph component down to those levels,
    # replacing a genuine k-component by its fragments.
    G = nx.gnp_random_graph(16, 0.6, seed=22070)
    assert nx.node_connectivity(G) == 7
    nodes = sorted(G)
    result = nx.k_components(G)
    for k in range(1, 8):
        assert sorted(sorted(c) for c in result[k]) == [nodes]


@pytest.mark.parametrize(("n", "p"), [(10, 0.6), (50, 0.2)])
def test_random_gnp(n, p):
    G = nx.gnp_random_graph(n, p, seed=42)
    result = nx.k_components(G)
    _check_connectivity(G, result)


@pytest.mark.parametrize(
    "constructor",
    [
        [(5, 8, 0.8), (8, 15, 0.6), (5, 24, 0.2)],
        [(20, 80, 0.8), (80, 180, 0.6)],
    ],
)
def test_shell(constructor):
    G = nx.random_shell_graph(constructor, seed=42)
    result = nx.k_components(G)
    _check_connectivity(G, result)


def test_configuration():
    deg_seq = nx.random_powerlaw_tree_sequence(100, tries=5, seed=72)
    G = nx.Graph(nx.configuration_model(deg_seq))
    G.remove_edges_from(nx.selfloop_edges(G))
    result = nx.k_components(G)
    _check_connectivity(G, result)


def test_karate():
    G = nx.karate_club_graph()
    result = nx.k_components(G)
    _check_connectivity(G, result)


def test_karate_component_number():
    karate_k_num = {
        0: 4,
        1: 4,
        2: 4,
        3: 4,
        4: 3,
        5: 3,
        6: 3,
        7: 4,
        8: 4,
        9: 2,
        10: 3,
        11: 1,
        12: 2,
        13: 4,
        14: 2,
        15: 2,
        16: 2,
        17: 2,
        18: 2,
        19: 3,
        20: 2,
        21: 2,
        22: 2,
        23: 3,
        24: 3,
        25: 3,
        26: 2,
        27: 3,
        28: 3,
        29: 3,
        30: 4,
        31: 3,
        32: 4,
        33: 4,
    }
    G = nx.karate_club_graph()
    k_components = nx.k_components(G)
    k_num = build_k_number_dict(k_components)
    assert karate_k_num == k_num


def test_davis_southern_women():
    G = nx.davis_southern_women_graph()
    result = nx.k_components(G)
    _check_connectivity(G, result)


def test_davis_southern_women_detail_3_and_4():
    solution = {
        3: [
            {
                "Nora Fayette",
                "E10",
                "Myra Liddel",
                "E12",
                "E14",
                "Frances Anderson",
                "Evelyn Jefferson",
                "Ruth DeSand",
                "Helen Lloyd",
                "Eleanor Nye",
                "E9",
                "E8",
                "E5",
                "E4",
                "E7",
                "E6",
                "E1",
                "Verne Sanderson",
                "E3",
                "E2",
                "Theresa Anderson",
                "Pearl Oglethorpe",
                "Katherina Rogers",
                "Brenda Rogers",
                "E13",
                "Charlotte McDowd",
                "Sylvia Avondale",
                "Laura Mandeville",
            }
        ],
        4: [
            {
                "Nora Fayette",
                "E10",
                "Verne Sanderson",
                "E12",
                "Frances Anderson",
                "Evelyn Jefferson",
                "Ruth DeSand",
                "Helen Lloyd",
                "Eleanor Nye",
                "E9",
                "E8",
                "E5",
                "E4",
                "E7",
                "E6",
                "Myra Liddel",
                "E3",
                "Theresa Anderson",
                "Katherina Rogers",
                "Brenda Rogers",
                "Charlotte McDowd",
                "Sylvia Avondale",
                "Laura Mandeville",
            }
        ],
    }
    G = nx.davis_southern_women_graph()
    result = nx.k_components(G)
    for k, components in result.items():
        if k < 3:
            continue
        assert len(components) == len(solution[k])
        for component in components:
            assert component in solution[k]


def test_set_consolidation_rosettacode():
    # Tests from http://rosettacode.org/wiki/Set_consolidation
    def list_of_sets_equal(result, solution):
        assert {frozenset(s) for s in result} == {frozenset(s) for s in solution}

    question = [{"A", "B"}, {"C", "D"}]
    solution = [{"A", "B"}, {"C", "D"}]
    list_of_sets_equal(_consolidate(question, 1), solution)
    question = [{"A", "B"}, {"B", "C"}]
    solution = [{"A", "B", "C"}]
    list_of_sets_equal(_consolidate(question, 1), solution)
    question = [{"A", "B"}, {"C", "D"}, {"D", "B"}]
    solution = [{"A", "C", "B", "D"}]
    list_of_sets_equal(_consolidate(question, 1), solution)
    question = [{"H", "I", "K"}, {"A", "B"}, {"C", "D"}, {"D", "B"}, {"F", "G", "H"}]
    solution = [{"A", "C", "B", "D"}, {"G", "F", "I", "H", "K"}]
    list_of_sets_equal(_consolidate(question, 1), solution)
    question = [
        {"A", "H"},
        {"H", "I", "K"},
        {"A", "B"},
        {"C", "D"},
        {"D", "B"},
        {"F", "G", "H"},
    ]
    solution = [{"A", "C", "B", "D", "G", "F", "I", "H", "K"}]
    list_of_sets_equal(_consolidate(question, 1), solution)
    question = [
        {"H", "I", "K"},
        {"A", "B"},
        {"C", "D"},
        {"D", "B"},
        {"F", "G", "H"},
        {"A", "H"},
    ]
    solution = [{"A", "C", "B", "D", "G", "F", "I", "H", "K"}]
    list_of_sets_equal(_consolidate(question, 1), solution)


def test_reconstruct_k_components_promotes_spanning_component():
    # A (k+1)-level component can span several k-level candidates without
    # being a subset of any of them. It must still be propagated down to
    # level k, where consolidation merges the candidates it bridges; the
    # pre-gh-8734 union-coverage check skipped it and returned the two
    # fragments instead.
    k_comps = {3: [{1, 2, 3, 4}, {4, 5, 6, 7}], 4: [{2, 3, 4, 5, 6}]}
    result = _reconstruct_k_components(k_comps)
    assert result[4] == [{2, 3, 4, 5, 6}]
    assert result[3] == [{1, 2, 3, 4, 5, 6, 7}]
    assert result[2] == [{1, 2, 3, 4, 5, 6, 7}]
    assert result[1] == [{1, 2, 3, 4, 5, 6, 7}]


def test_reconstruct_k_components_drops_nested_candidate():
    # A single _consolidate pass merges on pairwise overlaps of its input
    # sets only. A propagated (k+1)-level component that shares fewer than
    # k nodes with each of two level-k candidates is not merged with
    # either, yet when the two candidates merge with each other it ends up
    # a strict subset of their union. A nested set is never a maximal
    # k-connected subgraph, so reconstruction must drop it.
    A = set(range(1, 9))  # {1..8}
    B = set(range(5, 13))  # {5..12}, shares {5, 6, 7, 8} with A
    c = {2, 3, 4, 9, 10, 11}  # inside A | B, shares only 3 with each
    result = _reconstruct_k_components({4: [A, B], 5: [c]})
    assert result[5] == [c]
    assert result[4] == [A | B]


def test_reconstruct_k_components_no_nested_output():
    # Contract: no level of the returned decomposition contains a
    # component that is a strict subset of another at the same level.
    k_comps = {
        2: [set(range(1, 20)), {30, 31, 32}],
        3: [{1, 2, 3, 4, 5}, {4, 5, 6, 7, 8}, {10, 11, 12, 13}],
        4: [{2, 3, 4, 6, 7, 8}],
    }
    result = _reconstruct_k_components(k_comps)
    for comps in result.values():
        for comp in comps:
            assert not any(comp < other for other in comps)


def test_generate_partition_keeps_cut_adjacent_low_degree_nodes():
    # The Davis Southern Women graph is biconnected with node connectivity
    # 2 and has exactly two minimum cutsets, {E8, E9} and {E9, E11}. Three
    # women attended only two events, both in the cutsets, so removing a
    # cutset separates each of them from the rest of the graph. The
    # expected partition thus has four parts: one per separated woman,
    # holding her and the two events she attended, and one with the other
    # 29 nodes; the parts overlap in the cutsets. The pre-gh-8734 code
    # kept only nodes of degree greater than k outside the cutsets, so it
    # silently dropped the three women.
    G = nx.davis_southern_women_graph()
    k = nx.node_connectivity(G)
    assert k == 2
    cuts = list(nx.all_node_cuts(G, k=k))
    assert {frozenset(cut) for cut in cuts} == {
        frozenset({"E8", "E9"}),
        frozenset({"E9", "E11"}),
    }
    assert set(G["Dorothy Murchison"]) == {"E8", "E9"}
    assert set(G["Flora Price"]) == {"E9", "E11"}
    assert set(G["Olivia Carleton"]) == {"E9", "E11"}
    parts = list(_generate_partition(G, cuts, k))
    assert {frozenset(part) for part in parts} == {
        frozenset({"Dorothy Murchison", "E8", "E9"}),
        frozenset({"Flora Price", "E9", "E11"}),
        frozenset({"Olivia Carleton", "E9", "E11"}),
        frozenset(set(G) - {"Dorothy Murchison", "Flora Price", "Olivia Carleton"}),
    }
    for part in parts:
        assert nx.is_connected(G.subgraph(part))
