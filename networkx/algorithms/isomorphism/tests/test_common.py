import itertools as it

import pytest

import networkx as nx
from networkx.algorithms import isomorphism as iso

graph_classes = [nx.Graph, nx.MultiGraph, nx.DiGraph, nx.MultiDiGraph]

labels_same = ["blue"]
labels_many = [
    "white",
    "red",
    "blue",
    "green",
    "orange",
    "black",
    "purple",
    "yellow",
    "brown",
    "cyan",
    "solarized",
    "pink",
    "none",
]

# Note: vf2pp doesnt use matching functions, instead equality of attrs on Graph
nmatch = iso.categorical_node_match("label", "")
ematch = iso.categorical_edge_match("foo", "")
mematch = iso.categorical_multiedge_match("foo", "")


#### Functions to test (and unify interface)


# vf2pp:
#   vf2pp_all_isomorphisms()
#   vf2pp_isomorphism()
#   vf2pp_is_isomorphic()
# vf2:
#   GraphMatcher gm
#   gm.is_isomorphic()
#   gm.isomorphisms_iter()
#   gm.subgraph_is_isomorphic()
#   gm.subgraph_isomorphisms_iter()
#   gm.subgraph_is_monomorphic()
#   gm.subgraph_monomorphisms_iter()
# ismags:
#   ISMAGS ismags
#   ismags.is_isomorphic()
#   ismags.isomorphisms_iter()
#   ismags.subgraph_is_isomorphic()
#   ismags.subgraph_isomorphisms_iter()
#   ismags.largest_common_subgraph()
#   ismags.analyse_subgraph_symmetry()
#   ismags.find_isomorphisms()          # same as isomorphisms_iter


def ismags_is_iso(G1, G2, node_label=None, edge_label=None, symmetry=False):
    return iso.ISMAGS(G1, G2, node_label, edge_label).is_isomorphic(symmetry)


def ismags_iter(G1, G2, node_label=None, edge_label=None, symmetry=False):
    return iso.ISMAGS(G1, G2, node_label, edge_label).isomorphisms_iter(symmetry)


def ismags_is_SG_iso(G1, G2, node_label=None, edge_label=None, symmetry=False):
    return iso.ISMAGS(G1, G2, node_label, edge_label).subgraph_is_isomorphic(
        symmetry=symmetry
    )


def ismags_subgraph_iter(G1, G2, node_label=None, edge_label=None, symmetry=False):
    gm = iso.ISMAGS(G1, G2, node_label, edge_label)
    return gm.subgraph_isomorphisms_iter(symmetry=symmetry)


def ismags_is_SG_mono(G1, G2, node_label=None, edge_label=None, symmetry=False):
    pytest.xfail("ismags does not handle monomorphism yet")


def ismags_mono_iter(G1, G2, node_label=None, edge_label=None, symmetry=False):
    pytest.xfail("ismags does not handle monomorphism yet")


def vf2_is_iso(G1, G2, node_label=None, edge_label=None, symmetry=False):
    if symmetry:
        pytest.xfail("vf2 does not handle symmetries yet")
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).is_isomorphic()


def vf2_iter(G1, G2, node_label=None, edge_label=None, symmetry=False):
    if symmetry:
        pytest.xfail("vf2 does not handle symmetries yet")
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).isomorphisms_iter()


def vf2_is_SG_iso(G1, G2, node_label=None, edge_label=None, symmetry=False):
    if symmetry:
        pytest.xfail("vf2 does not handle symmetries yet")
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).subgraph_is_isomorphic()


def vf2_subgraph_iter(G1, G2, node_label=None, edge_label=None, symmetry=False):
    if symmetry:
        pytest.xfail("vf2 does not handle symmetries yet")
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).subgraph_isomorphisms_iter()


def vf2_is_SG_mono(G1, G2, node_label=None, edge_label=None, symmetry=False):
    if symmetry:
        pytest.xfail("vf2 does not handle symmetries yet")
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).subgraph_is_monomorphic()


def vf2_mono_iter(G1, G2, node_label=None, edge_label=None, symmetry=False):
    if symmetry:
        pytest.xfail("vf2 does not handle symmetries yet")
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).subgraph_monomorphisms_iter()


def vf2pp_is_iso(G1, G2, node_label=None, edge_label=None, symmetry=False):
    if symmetry:
        pytest.xfail("vf2pp does not handle symmetries yet")
        return nx.vf2pp_is_isomorphic(G1, G2, symmetry=symmetry)
    if node_label is nmatch:
        node_label = "label"
    if edge_label is not None:
        pytest.xfail("vf2pp does not handle edge_labels yet")
        return nx.vf2pp_is_isomorphic(G1, G2, node_label, edge_label=edge_label)
    return nx.vf2pp_is_isomorphic(G1, G2, node_label)


def vf2pp_iter(G1, G2, node_label=None, edge_label=None, symmetry=False):
    if symmetry:
        pytest.xfail("vf2pp does not handle symmetries yet")
        return nx.vf2pp_all_isomorphisms(G1, G2, symmetry=symmetry)
    if node_label is nmatch:
        node_label = "label"
    if edge_label is not None:
        pytest.xfail("vf2pp does not handle edge_labels yet")
        return nx.vf2pp_all_isomorphisms(G1, G2, node_label, edge_label=edge_label)
    return nx.vf2pp_all_isomorphisms(G1, G2, node_label)


def vf2pp_is_SG_iso(G1, G2, node_label=None, edge_label=None, symmetry=False):
    pytest.xfail("vf2pp does not handle subgraph isomorphism yet")


def vf2pp_subgraph_iter(G1, G2, node_label=None, edge_label=None, symmetry=False):
    pytest.xfail("vf2pp does not handle subgraph isomorphism yet")


def vf2pp_is_SG_mono(G1, G2, node_label=None, edge_label=None, symmetry=False):
    pytest.xfail("vf2pp does not handle monomorphism yet")


def vf2pp_mono_iter(G1, G2, node_label=None, edge_label=None, symmetry=False):
    pytest.xfail("vf2pp does not handle monomorphism yet")


is_funcs = {
    "vf2": (vf2_is_iso, vf2_iter),
    "vf2pp": (vf2pp_is_iso, vf2pp_iter),
    "ismags": (ismags_is_iso, ismags_iter),
}
SG_funcs = {
    "vf2_SG": (vf2_is_SG_iso, vf2_subgraph_iter),
    "vf2pp_SG": (vf2pp_is_SG_iso, vf2pp_subgraph_iter),
    "ismags_SG": (ismags_is_SG_iso, ismags_subgraph_iter),
}
mono_funcs = {
    "vf2_mono": (vf2_is_SG_mono, vf2_mono_iter),
    "vf2pp_mono": (vf2pp_is_SG_mono, vf2pp_mono_iter),
    "ismags_mono": (ismags_is_SG_mono, ismags_mono_iter),
}
morphism_funcs = is_funcs | SG_funcs | mono_funcs

is_morphic_funcs = [pytest.param(fn[0], id=id) for id, fn in morphism_funcs.items()]
mono_iters = [pytest.param(fn[1], id=id) for id, fn in mono_funcs.items()]
morphic_and_mapping = [pytest.param(*fns, id=id) for id, fns in morphism_funcs.items()]

is_isomorphic_funcs = [pytest.param(fn[0], id=id) for id, fn in is_funcs.items()]
is_SG_funcs = [pytest.param(fn[0], id=id) for id, fn in SG_funcs.items()]
is_mono_funcs = [pytest.param(fn[0], id=id) for id, fn in mono_funcs.items()]


#### Graph Constructors
## Solo Graphs


def asymm_3triangles_kite():
    G = nx.MultiDiGraph(
        [(1, 2), (1, 3), (1, 4), (2, 3), (3, 2), (2, 6), (3, 4), (1, 5), (2, 5)]
    )
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])
    # for selfloops (node 1, 2 and 3 mapped to selves)
    G.add_edges_from([(1, 1), (2, 2), (3, 3)])

    G.graph["name"] = "asymm_3triangles_kite"
    G.graph["numb_symmetries"] = 1
    G.graph["show"] = r"""
   5-1-4
   |/ \|
 6-2---3
"""
    return G


def asymm_triangle_square_2tails():
    G = nx.MultiDiGraph(
        [(1, 2), (5, 1), (5, 6), (2, 3), (2, 4), (3, 4), (5, 4), (2, 7)]
    )
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])
    G.add_edges_from([(1, 1), (2, 2), (3, 3)])

    G.graph["name"] = "asymm_triangle_square_2tails"
    G.graph["numb_symmetries"] = 1
    G.graph["subgraph_nodes"] = [[2, 3, 4, 7], [1, 4, 5, 6]]
    G.graph["show"] = r"""
  7-2-1
   /| |
  3-4-5-6
"""
    return G


def symm_water_tower():
    G = nx.MultiDiGraph(
        [(1, 2), (1, 3), (1, 4), (2, 3), (3, 2), (2, 6), (4, 3), (3, 7), (1, 5), (5, 2)]
    )
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])
    # for selfloops (node 1 is mapped to itself, nodes 2 and 3 to each other)
    G.add_edges_from([(1, 1), (2, 2), (3, 3)])

    G.graph["name"] = "symm_water_tower"
    G.graph["numb_symmetries"] = 2
    G.graph["mappings"] = [{1: 1, 2: 3, 3: 2, 4: 5, 5: 4, 6: 7, 7: 6}]
    G.graph["show"] = r"""
  5-1-4
  |/ \|    mapping: 1-7 <-> (1, 3, 2, 5, 4, 7, 6)
  2---3
  |   |
  6   7
"""
    return G


def symm_balloon():
    G = nx.MultiDiGraph()
    nx.add_cycle(G, [1, 2, 3])
    nx.add_cycle(G, [2, 3, 4, 5])
    nx.add_cycle(G, [5, 6, 7, 4, 9, 8])
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])
    # for selfloops (node 1 is mapped to itself, nodes 2 and 3 to each other)
    G.add_edges_from([(1, 1), (2, 2), (3, 3)])
    # make directed have mappings too
    nx.add_cycle(G, [8, 9, 4, 7, 6, 5])
    nx.add_cycle(G, [3, 2, 1])

    G.graph["name"] = "symm_balloon"
    G.graph["numb_symmetries"] = 4
    G.graph["numb_directed_symmetries"] = 2
    G.graph["directed_mappings"] = [
        {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 8, 7: 9, 9: 7, 8: 6},
    ]
    G.graph["mappings"] = [
        # {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 9: 9, 8: 8},
        {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 8: 6, 9: 7, 7: 9, 6: 8},
        {1: 1, 3: 2, 2: 3, 5: 4, 4: 5, 9: 6, 8: 7, 6: 9, 7: 8},
        {1: 1, 3: 2, 2: 3, 5: 4, 4: 5, 7: 6, 6: 7, 8: 9, 9: 8},
        # {1: 1, 2: 3, 3: 2, 4: 5, 5: 4, 6: 8, 7: 9, 8: 6, 9: 7},
        # {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 7, 7: 6, 8: 9, 9: 8},
        # {1: 1, 2: 3, 3: 2, 4: 5, 5: 4, 6: 6, 7: 7, 8: 8, 9: 9},
    ]
    G.graph["show"] = r"""
     3---4
    /|  /|\
   / | 9 | 7
  1  | | | |
   \ | 8 | 6
    \|  \|/
     2---5
"""
    return G


def cyclic_ladder_4rungs():
    G = nx.cycle_graph([1, 2, 3, 7, 6, 5, 8, 4], create_using=nx.MultiDiGraph)
    G.add_edges_from([(1, 5), (6, 2), (3, 4), (7, 8), (2, 1)])
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])
    # for selfloops
    G.add_edges_from([(0, 0), (2, 2), (4, 4)])

    G.graph["name"] = "cyclic_ladder_4rungs"
    G.graph["numb_symmetries"] = 4
    G.graph["numb_directed_symmetries"] = 1
    G.graph["directed_mappings"] = []
    G.graph["mappings"] = [
        {1: 1, 4: 2, 3: 3, 7: 7, 8: 6, 5: 5, 6: 8, 2: 4, 0: 0},
        {3: 1, 2: 2, 1: 3, 5: 7, 6: 6, 7: 5, 8: 8, 4: 4, 0: 0},
        {3: 1, 4: 2, 1: 3, 5: 7, 8: 6, 7: 5, 6: 8, 2: 4, 0: 0},
    ]
    G.graph["show"] = r"""
      1
     /|\
    / 2 \
   | / \ |
   5-6 3-4
   | \ / |
    \ 7 /
     \|/
      8
"""
    return G


def cycle6_plus_3_2paths():
    G = nx.cycle_graph(6, create_using=nx.MultiDiGraph)
    nx.add_path(G, [0, 5, 4, 3, 2, 1, 0])  # for directed graphs
    nx.add_path(G, [0, 6, 7])
    nx.add_path(G, [2, 8, 9])
    nx.add_path(G, [4, 10, 11])
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])
    # for selfloops
    G.add_edges_from([(0, 0), (2, 2), (4, 4)])

    G.graph["name"] = "cycle6_plus_3_2paths"
    G.graph["show"] = "6-cycle with 2-paths stuck onto nodes 0, 2, 4"
    G.graph["numb_symmetries"] = 6
    return G


# TODO: add more graphs from test_ismags.py

solo_graphs = [
    asymm_3triangles_kite,
    asymm_triangle_square_2tails,
    symm_water_tower,
    symm_balloon,
    cyclic_ladder_4rungs,
    cycle6_plus_3_2paths,
]


#### Test Functions
## Self-Isomorphism (Symmetry) tests


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("G", solo_graphs)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("iso_ic, iso_iter", morphic_and_mapping)
def test_single_graph(G, Gclass, iso_ic, iso_iter, symmetry):
    G1 = Gclass(G())
    assert iso_ic(G1, G1, symmetry=symmetry)
    assert list(iso_iter(G1, G1, symmetry=symmetry))

    numb_key = "numb_directed_symmetries" if G1.is_directed() else "numb_symmetries"
    sym = G1.graph.get(numb_key, None)
    if sym is not None:
        all_mappings = list(iso_iter(G1, G1, symmetry=symmetry))
        assert len(all_mappings) == (1 if symmetry else sym)

    map_key = "directed_mappings" if G1.is_directed() else "mappings"
    mappings = G1.graph.get(map_key, None)
    if mappings is not None:
        all_mappings = list(iso_iter(G1, G1, symmetry=symmetry))
        if symmetry:
            assert len(all_mappings) == 1
        else:
            assert all(m in all_mappings for m in mappings)
            assert len(all_mappings) == len(mappings) + 1

    G2 = G1.copy()
    G2.remove_edge(2, 2)
    G2.add_edge(6, 6)
    assert not iso_ic(G1, G2, symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("G", solo_graphs)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("iso_ic", is_morphic_funcs)
def test_check_noncomparable_nodes_mappings(G, Gclass, iso_ic, symmetry):
    G1 = Gclass(G())

    N = len(G1)
    numb = 1 if N < 2 else N // 2 if N < 26 else 10
    mapping = dict(enumerate("acdefghijklmnopqrstuvwxyz"[:numb]))
    G2 = nx.relabel_nodes(G1, mapping)

    assert iso_ic(G1, G2, symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("G", solo_graphs)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("iso_ic", is_morphic_funcs)
def test_single_graph_node_and_edge_labels(G, Gclass, iso_ic, symmetry):
    G1 = Gclass(G())
    nm = nmatch
    em = mematch if G1.is_multigraph() else ematch
    nx.set_node_attributes(G1, dict(zip(G1, it.cycle(labels_same))), "label")
    nx.set_edge_attributes(G1, dict(zip(G1.edges, it.cycle(labels_same))), "foo")
    assert iso_ic(G1, G1, node_label=nm, edge_label=None, symmetry=symmetry)
    assert iso_ic(G1, G1, node_label=None, edge_label=em, symmetry=symmetry)
    assert iso_ic(G1, G1, node_label=nm, edge_label=em, symmetry=symmetry)

    G2 = G1.copy()
    node, edge = next(iter(G2)), next(iter(G2.edges))
    G2.nodes[node]["label"] = "magenta"
    G2.edges[edge]["foo"] = "magenta"
    assert iso_ic(G1, G2, node_label=None, edge_label=None, symmetry=symmetry)
    assert not iso_ic(G1, G2, node_label=nm, edge_label=None, symmetry=symmetry)
    assert not iso_ic(G1, G2, node_label=None, edge_label=em, symmetry=symmetry)
    assert not iso_ic(G1, G2, node_label=nm, edge_label=em, symmetry=symmetry)

    nx.set_node_attributes(G1, dict(zip(G1, it.cycle(labels_many))), "label")
    nx.set_edge_attributes(G1, dict(zip(G1.edges, it.cycle(labels_many))), "foo")
    assert iso_ic(G1, G1, node_label=nm, edge_label=None, symmetry=symmetry)
    assert iso_ic(G1, G1, node_label=None, edge_label=em, symmetry=symmetry)
    assert iso_ic(G1, G1, node_label=nm, edge_label=em, symmetry=symmetry)

    G2 = G1.copy()
    # swap two node labels and two edge "foo" values
    nodes, edges = G2.nodes, G2.edges
    node1_d, node2_d = (nodes[n] for n in it.islice(nodes, 2))
    edge1_d, edge2_d = (edges[n] for n in it.islice(edges, 2))
    assert node1_d["label"] != node2_d["label"]
    assert edge1_d["foo"] != edge2_d["foo"]
    node2_d["label"], node1_d["label"] = node1_d["label"], node2_d["label"]
    edge2_d["foo"], edge1_d["foo"] = edge1_d["foo"], edge2_d["foo"]

    assert iso_ic(G1, G2, node_label=None, edge_label=None, symmetry=symmetry)
    assert not iso_ic(G1, G2, node_label=nm, edge_label=None, symmetry=symmetry)
    assert not iso_ic(G1, G2, node_label=None, edge_label=em, symmetry=symmetry)
    assert not iso_ic(G1, G2, node_label=nm, edge_label=em, symmetry=symmetry)


## paired graphs tests


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("iso_ic", is_isomorphic_funcs)
def test_non_isomorphic_same_degree_sequence(iso_ic, symmetry, Gclass):
    G = nx.MultiDiGraph()
    nx.add_cycle(G, [1, 2, 3, 4])
    nx.add_cycle(G, [5, 6, 7, 8])
    G.add_edge(1, 5)
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])
    G.add_edges_from([(1, 1), (3, 3), (6, 6)])

    G1 = G.copy()
    G1.add_edge(4, 8)
    G2 = G.copy()
    G2.add_edge(3, 7)
    # 3rd value is whether isomorphic or not
    assert not iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("iso_ic", is_isomorphic_funcs)
def test_morph_triangle_square_2tails(iso_ic, symmetry, Gclass):
    r"""
    7-2-1
     /| |
    3-4-5-6
    """
    G = asymm_triangle_square_2tails()
    G1 = G.subgraph([2, 3, 4, 7]).copy()
    G2 = G.subgraph([1, 4, 5, 6]).copy()
    assert not iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)

    G1.remove_edge(2, 2)
    G2.add_edge(1, 4)
    assert iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)

    G1.add_edges_from([(3, 7), (4, 7)])
    G2.add_edges_from([(1, 6), (4, 6)])
    assert iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("iso_ic", is_isomorphic_funcs)
def test_morph_3triangles_kite(iso_ic, symmetry, Gclass):
    r"""
      5-1-4
      |/ \|
    6-2---3
    """
    G1 = asymm_3triangles_kite()
    G2 = G1.copy()
    assert iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)
    G2.remove_edges_from([(2, 6)])
    assert not iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)
    G2.add_edges_from([(3, 7)])
    assert not iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)
    G2.remove_node(6)
    assert iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)

    G2.add_edges_from([(5, 5), (5, 5), (1, 1)])
    assert not iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)
    G1.add_edges_from([(4, 4), (4, 4), (1, 1)])
    assert iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)
    G2.remove_edge(1, 4)
    G1.remove_edge(1, 5)
    assert iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)


## Subgraph iso and mono


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("iso_ic", is_SG_funcs + is_mono_funcs)
def test_subgraph_triangle_square_2tails(iso_ic, symmetry, Gclass):
    r"""
    7-2-1
     /| |
    3-4-5-6
    """
    mono = "mono" in iso_ic.__name__
    G = asymm_triangle_square_2tails()

    SG = G.subgraph([2, 3, 4, 7]).copy()
    assert iso_ic(Gclass(G), Gclass(SG), symmetry=symmetry)
    SG.remove_edge(2, 3)

    if "ismags" not in iso_ic.__name__:
        # FIXME: check why fails ismags but not vf2
        assert mono == iso_ic(Gclass(G), Gclass(SG), symmetry=symmetry)

    SG.add_edges_from([(7, 3), (7, 4)])
    assert not iso_ic(Gclass(G), Gclass(SG), symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [False, True])
@pytest.mark.parametrize("iso_ic", is_SG_funcs + is_mono_funcs)
def test_monomorphism_path_in_cycle(iso_ic, symmetry, Gclass):
    G = nx.cycle_graph(14, create_using=nx.MultiDiGraph)
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])
    # for selfloops (node 1, 2 and 3 mapped to selves)
    G.add_edges_from([(1, 1), (2, 2), (3, 3)])

    SG = G.copy()
    SG.remove_edge(13, 0)
    assert G.number_of_edges() == SG.number_of_edges() + 1

    mono = "mono" in iso_ic.__name__
    assert mono == iso_ic(Gclass(G), Gclass(SG), symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("mono_iter", mono_iters)
def test_monomorphism_count_for_path_in_cycle(mono_iter, symmetry, Gclass):
    G = nx.cycle_graph(14, create_using=nx.MultiDiGraph)
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])
    # for selfloops (node 1, 2 and 3 mapped to selves)
    G.add_edges_from([(1, 1), (2, 2), (3, 3)])

    SG = G.copy()
    SG.remove_edge(13, 0)
    assert G.number_of_edges() == SG.number_of_edges() + 1

    G = Gclass(G)
    SG = Gclass(SG)

    mappings = mono_iter(G, SG, symmetry=symmetry)
    assert sum(1 for _ in mappings) == 1 if G.is_directed() else 2

    # switch order of G and SG (bigger cannot be subgraph)
    assert sum(1 for _ in mono_iter(SG, G, symmetry=symmetry)) == 0


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("SG_ic", is_SG_funcs + is_mono_funcs)
def test_subgraph_mono(SG_ic, symmetry, Gclass):
    # wikipedia example
    G = Gclass(["ag", "ah", "ai", "bg", "bh", "bj", "cg", "ci", "cj", "dh", "di", "dj"])
    SG = Gclass(["ag", "cg", "ci", "di", "bg"])
    # check that G is always subgraph morphic to itself
    assert SG_ic(G, G, symmetry=symmetry)

    # true if is_mono, false if is_SG
    assert SG_ic(G, SG, symmetry=symmetry) == ("mono" in SG_ic.__name__)

    # switch order of G and SG (bigger cannot be subgraph)
    assert not SG_ic(SG, G, symmetry=symmetry)

    SG.add_edge("c", "a")
    assert not SG_ic(G, SG, symmetry=symmetry)
