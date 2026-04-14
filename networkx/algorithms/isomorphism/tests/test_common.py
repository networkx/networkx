import itertools as it

import pytest

import networkx as nx
from networkx.algorithms import isomorphism as iso

graph_classes = [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]

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
#   vf2pp_all_subgraph_isomorphisms()
#   vf2pp_subgraph_isomorphism()
#   vf2pp_subgraph_is_isomorphic()
#   vf2pp_all_monomorphisms()
#   vf2pp_monomorphism()
#   vf2pp_is_monomorphic()
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
    if symmetry:
        pytest.xfail("vf2pp does not handle symmetries yet")
        return nx.vf2pp_all_isomorphisms(G1, G2, symmetry=symmetry)
    if node_label is nmatch:
        node_label = "label"
    if edge_label is not None:
        pytest.xfail("vf2pp does not handle edge_labels yet")
        return nx.vf2pp_all_isomorphisms(G1, G2, node_label, edge_label=edge_label)
    try:
        mapping = next(nx.vf2pp_all_subgraph_isomorphisms(G1, G2, node_label))
        return True
    except StopIteration:
        return False


def vf2pp_subgraph_iter(G1, G2, node_label=None, edge_label=None, symmetry=False):
    if symmetry:
        pytest.xfail("vf2pp does not handle symmetries yet")
        return nx.vf2pp_all_subgraph_isomorphisms(G1, G2, symmetry=symmetry)
    if node_label is nmatch:
        node_label = "label"
    if edge_label is not None:
        pytest.xfail("vf2pp does not handle edge_labels yet")
        return nx.vf2pp_all_subgraph_isomorphisms(G1, G2, node_label, edge_label)
    return nx.vf2pp_all_subgraph_isomorphisms(G1, G2, node_label)


def vf2pp_is_SG_mono(G1, G2, node_label=None, edge_label=None, symmetry=False):
    if symmetry:
        pytest.xfail("vf2pp does not handle symmetries yet")
        try:
            next(nx.vf2pp_all_monomorphisms(G1, G2, node_label, symmetry=symmetry))
            return True
        except StopIteration:
            return False
    if node_label is nmatch:
        node_label = "label"
    if edge_label is not None:
        pytest.xfail("vf2pp does not handle edge_labels yet")
        try:
            next(nx.vf2pp_all_monomorphisms(G1, G2, node_label, edge_label))
            return True
        except StopIteration:
            return False
    try:
        mapping = next(nx.vf2pp_all_monomorphisms(G1, G2, node_label))
        return True
    except StopIteration:
        return False


def vf2pp_mono_iter(G1, G2, node_label=None, edge_label=None, symmetry=False):
    if symmetry:
        pytest.xfail("vf2pp does not handle symmetries yet")
        return nx.vf2pp_all_monomorphisms(G1, G2, symmetry=symmetry)
    if node_label is nmatch:
        node_label = "label"
    if edge_label is not None:
        pytest.xfail("vf2pp does not handle edge_labels yet")
        return nx.vf2pp_all_monomorphisms(G1, G2, node_label, edge_label)
    return nx.vf2pp_all_monomorphisms(G1, G2, node_label)


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

is_iso_funcs = [pytest.param(fn[0], id=id) for id, fn in is_funcs.items()]
is_SG_funcs = [pytest.param(fn[0], id=id) for id, fn in SG_funcs.items()]
is_mono_funcs = [pytest.param(fn[0], id=id) for id, fn in mono_funcs.items()]


#### Graph Constructors
## Solo Graphs


def asymm_3triangles_kite():
    G = nx.MultiDiGraph(
        [(1, 2), (1, 3), (1, 4), (2, 3), (3, 2), (2, 6), (3, 4), (1, 5), (2, 5)]
    )
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges()) if i % 2 == 0])
    # for selfloops (node 1, 2 and 3 mapped to selves)
    G.add_edges_from([(1, 1), (2, 2), (3, 3)])

    G.graph["name"] = "asymm_3triangles_kite"
    G.graph["numb_symmetries"] = {g: 1 for g in graph_classes}
    G.graph["mappings"] = {
        nx.Graph: [  # USG  (undirected simple graph)
            {1:1, 2:2, 3:3, 4:4, 6:6, 5:5},
        ],
        nx.DiGraph: [  # DSG  (undirected simple graph)
            {1:1, 2:2, 3:3, 4:4, 6:6, 5:5},
        ],
        nx.MultiGraph: [  # UMG  (undirected multi graph)
            {1:1, 2:2, 3:3, 4:4, 6:6, 5:5},
        ],
        nx.MultiDiGraph: [  # DMG  (directed multi graph)
            {1:1, 2:2, 3:3, 4:4, 6:6, 5:5},
        ],
    }  # fmt: skip
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
    G.add_edges_from([e for i, e in enumerate(G.edges()) if i % 2 == 0])
    G.add_edges_from([(1, 1), (2, 2), (3, 3)])

    G.graph["name"] = "asymm_triangle_square_2tails"
    G.graph["numb_symmetries"] = {g: 1 for g in graph_classes}
    G.graph["subgraph_nodes"] = [[2, 3, 4, 7], [1, 4, 5, 6]]
    G.graph["mappings"] = {
        nx.Graph: [  # USG  (undirected simple graph)
            {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7},
        ],
        nx.DiGraph: [  # DSG  (undirected simple graph)
            {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7},
        ],
        nx.MultiGraph: [  # UMG  (undirected multi graph)
            {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7},
        ],
        nx.MultiDiGraph: [  # DMG  (directed multi graph)
            {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7},
        ],
    }  # fmt: skip
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
    G.add_edges_from([e for i, e in enumerate(G.edges()) if i % 2 == 0])
    # for selfloops (node 1 is mapped to itself, nodes 2 and 3 to each other)
    G.add_edges_from([(1, 1), (2, 2), (3, 3)])

    G.graph["name"] = "symm_water_tower"
    G.graph["numb_symmetries"] = dict(zip(graph_classes, (2, 2, 1, 1)))
    G.graph["mappings"] = {
        nx.Graph: [  # USG  (undirected simple graph)
            {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7},
            {1:1, 3:2, 2:3, 4:5, 5:4, 6:7, 7:6},
        ],
        nx.DiGraph: [  # DSG  (undirected simple graph)
            {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7},
            {1:1, 3:2, 2:3, 4:5, 5:4, 6:7, 7:6},
        ],
        nx.MultiGraph: [  # UMG  (undirected multi graph)
            {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7},
        ],
        nx.MultiDiGraph: [  # DMG  (directed multi graph)
            {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7},
        ],
    }  # fmt: skip
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
    G.add_edges_from([(6, 7)])
    # for selfloops (node 1 is mapped to itself, nodes 2 and 3 to each other)
    G.add_edges_from([(1, 1), (2, 2), (3, 3)])
    # make directed have mappings too
    nx.add_cycle(G, [8, 9, 4, 7, 6, 5])
    nx.add_cycle(G, [3, 2, 1])

    G.graph["name"] = "symm_balloon"
    G.graph["numb_symmetries"] = dict(zip(graph_classes, (4, 2, 2, 1)))
    G.graph["mappings"] = {
        nx.Graph: [  # USG  (undirected simple graph)
          {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 9:9, 8:8},
          {1:1, 2:2, 3:3, 4:4, 5:5, 8:6, 9:7, 7:9, 6:8},
          {1:1, 3:2, 2:3, 5:4, 4:5, 9:6, 8:7, 6:9, 7:8},
          {1:1, 3:2, 2:3, 5:4, 4:5, 7:6, 6:7, 8:9, 9:8},
        ],
        nx.DiGraph: [  # DSG  (undirected simple graph)
          {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 9:9, 8:8},
          {1:1, 2:2, 3:3, 4:4, 5:5, 8:6, 9:7, 7:9, 6:8},
        ],
        nx.MultiGraph: [  # UMG  (undirected multi graph)
          {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 9:9, 8:8},
          {1:1, 3:2, 2:3, 5:4, 4:5, 7:6, 6:7, 8:9, 9:8},
        ],
        nx.MultiDiGraph: [  # DMG  (directed multi graph)
          {1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 9:9, 8:8},
        ],
    }  # fmt: skip
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
    G.add_edges_from([e for i, e in enumerate(G.edges()) if i % 2 == 0])
    # for selfloops
    G.add_edges_from([(0, 0), (2, 2), (4, 4)])

    G.graph["name"] = "cyclic_ladder_4rungs"
    G.graph["numb_symmetries"] = dict(zip(graph_classes, (4, 1, 1, 1)))
    G.graph["mappings"] = {
        nx.Graph: [
          {1:1, 2:2, 3:3, 7:7, 6:6, 5:5, 8:8, 4:4, 0:0},
          {1:1, 4:2, 3:3, 7:7, 8:6, 5:5, 6:8, 2:4, 0:0},
          {3:1, 2:2, 1:3, 5:7, 6:6, 7:5, 8:8, 4:4, 0:0},
          {3:1, 4:2, 1:3, 5:7, 8:6, 7:5, 6:8, 2:4, 0:0},
        ],
        nx.DiGraph: [
          {1:1, 2:2, 3:3, 7:7, 6:6, 5:5, 8:8, 4:4, 0:0},
        ],
        nx.MultiGraph: [
          {1:1, 2:2, 3:3, 7:7, 6:6, 5:5, 8:8, 4:4, 0:0},
        ],
        nx.MultiDiGraph: [
          {1:1, 2:2, 3:3, 7:7, 6:6, 5:5, 8:8, 4:4, 0:0},
        ],
    }  # fmt: skip
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
    G.add_edges_from([e for i, e in enumerate(G.edges()) if i % 2 == 0])
    # for selfloops
    G.add_edges_from([(0, 0), (2, 2), (4, 4)])

    G.graph["name"] = "cycle6_plus_3_2paths"
    G.graph["numb_symmetries"] = dict(zip(graph_classes, (6, 6, 1, 1)))
    G.graph["mappings"] = {
      nx.Graph: [
        {0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11:11},
        {0:0, 5:1, 4:2, 3:3, 2:4, 1:5, 6:6, 7:7, 10:8, 11:9, 8:10, 9:11},
        {2:0, 1:1, 0:2, 5:3, 4:4, 3:5, 8:6, 9:7, 6:8, 7:9, 10:10, 11:11},
        {2:0, 3:1, 4:2, 5:3, 0:4, 1:5, 8:6, 9:7, 10:8, 11:9, 6:10, 7:11},
        {4:0, 3:1, 2:2, 1:3, 0:4, 5:5, 10:6, 11:7, 8:8, 9:9, 6:10, 7:11},
        {4:0, 5:1, 0:2, 1:3, 2:4, 3:5, 10:6, 11:7, 6:8, 7:9, 8:10, 9:11},
      ],
      nx.DiGraph: [
        {0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11:11},
        {0:0, 5:1, 4:2, 3:3, 2:4, 1:5, 6:6, 7:7, 10:8, 11:9, 8:10, 9:11},
        {2:0, 1:1, 0:2, 5:3, 4:4, 3:5, 8:6, 9:7, 6:8, 7:9, 10:10, 11:11},
        {2:0, 3:1, 4:2, 5:3, 0:4, 1:5, 8:6, 9:7, 10:8, 11:9, 6:10, 7:11},
        {4:0, 3:1, 2:2, 1:3, 0:4, 5:5, 10:6, 11:7, 8:8, 9:9, 6:10, 7:11},
        {4:0, 5:1, 0:2, 1:3, 2:4, 3:5, 10:6, 11:7, 6:8, 7:9, 8:10, 9:11},
      ],
      nx.MultiGraph: [
        {0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11:11},
        ],
      nx.MultiDiGraph: [
        {0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11:11},
      ],
    }  # fmt: skip
    G.graph["show"] = r"""
          0-6-7
         / \
        1   5
        |   |
    8-9-2   4-10-11
         \ /
          3
"""
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

    all_mappings = list(iso_iter(G1, G1, symmetry=symmetry))

    sym = G1.graph.get("numb_symmetries", None)
    mappings = G1.graph.get("mappings", None)

    if sym is not None or mappings is not None:
        if symmetry:
            assert len(all_mappings) == 1
            return
        g_type = G1.__class__
        if sym is not None:
            assert len(all_mappings) == sym[g_type]
        if mappings is not None:
            list_of_maps = mappings[g_type]
            assert len(all_mappings) == len(list_of_maps)
            assert all(m in all_mappings for m in list_of_maps)

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
    edge1_d, edge2_d = (edges[e] for e in it.islice(edges, 2))
    assert node1_d["label"] != node2_d["label"]
    assert edge1_d["foo"] != edge2_d["foo"]
    node2_d["label"], node1_d["label"] = node1_d["label"], node2_d["label"]
    edge2_d["foo"], edge1_d["foo"] = edge1_d["foo"], edge2_d["foo"]
    if G2.is_multigraph():
        e1, e2 = it.islice(edges, 2)
        if e1[:2] == e2[:2]:
            # test case where two multiedges on same nodes can swap labels
            assert iso_ic(G1, G2, node_label=None, edge_label=em, symmetry=symmetry)
            # now swap two edges without same nodes
            edge2_d["foo"], edge1_d["foo"] = edge1_d["foo"], edge2_d["foo"]
            e_iter = it.islice(edges, 2, None)
            e2 = next(e_iter)
            while e1[:2] == e2[:2]:
                e2 = next(e_iter)
            edge2_d = edges[e2]
            edge2_d["foo"], edge1_d["foo"] = edge1_d["foo"], edge2_d["foo"]
    # dont select first two to ensure not multiedges with same nodes
    edge1_d, edge2_d = (edges[e] for e in it.islice(edges, 0, 3, 2))

    assert iso_ic(G1, G2, node_label=None, edge_label=None, symmetry=symmetry)
    assert not iso_ic(G1, G2, node_label=nm, edge_label=None, symmetry=symmetry)
    assert not iso_ic(G1, G2, node_label=None, edge_label=em, symmetry=symmetry)
    assert not iso_ic(G1, G2, node_label=nm, edge_label=em, symmetry=symmetry)


## paired graphs tests


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("iso_ic", is_iso_funcs)
def test_non_isomorphic_same_degree_sequence(iso_ic, symmetry, Gclass):
    G = nx.MultiDiGraph()
    nx.add_cycle(G, [1, 2, 3, 4])
    nx.add_cycle(G, [5, 6, 7, 8])
    G.add_edge(1, 5)
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges()) if i % 2 == 0])
    G.add_edges_from([(1, 1), (3, 3), (6, 6)])

    G1 = G.copy()
    G1.add_edge(4, 8)
    G2 = G.copy()
    G2.add_edge(3, 7)
    # 3rd value is whether isomorphic or not
    assert not iso_ic(Gclass(G1), Gclass(G2), symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("iso_ic", is_iso_funcs)
def test_morph_triangle_square_2tails(iso_ic, symmetry, Gclass):
    r"""
    7-2-1
     /| |
    3-4-5-6
    """
    G = Gclass(asymm_triangle_square_2tails())
    G1 = G.subgraph([2, 3, 4, 7]).copy()
    G2 = G.subgraph([1, 4, 5, 6]).copy()
    assert not iso_ic(G1, G2, symmetry=symmetry)

    G1.remove_edge(2, 2)
    G1.add_edge(2, 3)  # adjust multiedge to match 1-5 multiedge
    G2.add_edge(1, 4)
    assert iso_ic(G1, G2, symmetry=symmetry)

    G1.add_edges_from([(3, 7), (4, 7)])
    G2.add_edges_from([(1, 6), (4, 6)])
    assert iso_ic(G1, G2, symmetry=symmetry)
    # check todirected version (creates a symmetry in a DiGraph)
    if G1.is_directed():
        G1d = G1.to_undirected().to_directed()
        G2d = G2.to_undirected().to_directed()
        assert iso_ic(G1d, G2d, symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("iso_ic", is_iso_funcs)
def test_morph_3triangles_kite(iso_ic, symmetry, Gclass):
    r"""
      5-1-4
      |/ \|
    6-2---3
    """
    G1 = Gclass(asymm_3triangles_kite())
    G2 = G1.copy()
    simplegraph = not G1.is_multigraph()
    assert iso_ic(G1, G2, symmetry=symmetry)
    G2.remove_edges_from([(2, 6)])
    assert not iso_ic(G1, G2, symmetry=symmetry)
    G2.add_edges_from([(3, 7)])
    assert not iso_ic(G1, G2, symmetry=symmetry)
    G2.remove_node(6)
    assert iso_ic(G1, G2, symmetry=symmetry) == simplegraph

    G2.add_edges_from([(5, 5), (5, 5), (1, 1)])
    assert not iso_ic(G1, G2, symmetry=symmetry)
    G1.add_edges_from([(4, 4), (4, 4), (1, 1)])
    assert iso_ic(G1, G2, symmetry=symmetry) == simplegraph
    G2.remove_edge(1, 4)
    G1.remove_edge(1, 5)
    assert iso_ic(G1, G2, symmetry=symmetry) == simplegraph


## Subgraph iso and mono


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("iso_ic", is_SG_funcs + is_mono_funcs)
def test_subgraph_triangle_square_2tails(iso_ic, symmetry, Gclass):
    r"""
    7-2-1
     /| |
    3-4-5-6 multiedges on the square (1, 2), (2, 4), (5, 1), (5, 4)
    """
    mono = "mono" in iso_ic.__name__
    FG = asymm_triangle_square_2tails()

    SG = FG.subgraph([2, 3, 4, 7]).copy()
    assert iso_ic(Gclass(FG), Gclass(SG), symmetry=symmetry)

    SG.remove_edge(2, 3)
    assert mono == iso_ic(Gclass(FG), Gclass(SG), symmetry=symmetry)

    SG.add_edges_from([(7, 3), (7, 4)])
    assert not iso_ic(Gclass(FG), Gclass(SG), symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [False, True])
@pytest.mark.parametrize("iso_ic", is_SG_funcs + is_mono_funcs)
def test_monomorphism_path_in_cycle(iso_ic, symmetry, Gclass):
    FG = nx.cycle_graph(14, create_using=nx.MultiDiGraph)
    # for multiedges
    FG.add_edges_from([e for i, e in enumerate(FG.edges()) if i % 2 == 0])
    # for selfloops (node 1, 2 and 3 mapped to selves)
    FG.add_edges_from([(1, 1), (2, 2), (3, 3)])

    SG = FG.copy()
    SG.remove_edge(13, 0)
    assert FG.number_of_edges() == SG.number_of_edges() + 1

    mono = "mono" in iso_ic.__name__
    assert mono == iso_ic(Gclass(FG), Gclass(SG), symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("mono_iter", mono_iters)
def test_monomorphism_count_for_path_in_cycle(mono_iter, symmetry, Gclass):
    FG = nx.cycle_graph(14, create_using=nx.MultiDiGraph)
    # for multiedges
    FG.add_edges_from([e for i, e in enumerate(FG.edges()) if i % 2 == 0])
    # for selfloops (node 1, 2 and 3 mapped to selves)
    FG.add_edges_from([(1, 1), (2, 2), (3, 3)])

    SG = FG.copy()
    SG.remove_edge(13, 0)
    assert FG.number_of_edges() == SG.number_of_edges() + 1

    FG = Gclass(FG)
    SG = Gclass(SG)

    mappings = mono_iter(FG, SG, symmetry=symmetry)
    ans = 1 if (FG.is_directed() or FG.is_multigraph()) else 2
    assert sum(1 for _ in mappings) == ans

    # switch order of FG and SG (bigger cannot be subgraph)
    assert sum(1 for _ in mono_iter(SG, FG, symmetry=symmetry)) == 0


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("SG_ic", is_SG_funcs + is_mono_funcs)
def test_subgraph_mono(SG_ic, symmetry, Gclass):
    # wikipedia example
    FG = Gclass(
        ["ag", "ah", "ai", "bg", "bh", "bj", "cg", "ci", "cj", "dh", "di", "dj"]
    )
    SG = Gclass([(1, 5), (8, 5), (8, 4), (3, 4), (6, 5)])
    # check that FG is always subgraph morphic to itself
    assert SG_ic(FG, FG, symmetry=symmetry)

    # true if is_mono, false if is_SG
    assert SG_ic(FG, SG, symmetry=symmetry) == ("mono" in SG_ic.__name__)

    # switch order of FG and SG (bigger cannot be subgraph)
    assert not SG_ic(SG, FG, symmetry=symmetry)

    SG.add_edge(8, 1)
    assert not SG_ic(FG, SG, symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("SG_ic", is_SG_funcs + is_mono_funcs + is_iso_funcs)
def test_subgraph_mono_small(SG_ic, symmetry, Gclass):
    # small cycles
    FG = nx.cycle_graph("abcd", create_using=Gclass)
    SG = nx.path_graph(3, create_using=Gclass)

    subgraph_morph = "SG" in SG_ic.__name__
    mono_morph = "mono" in SG_ic.__name__
    # isolated node not in SG. is_iso => False, subgraph_is_* => True
    assert SG_ic(FG, SG, symmetry=symmetry) == subgraph_morph

    # add isolated node so SG_iso is False, but SG_mono still True
    SG.add_node(3)
    assert SG_ic(FG, SG, symmetry=symmetry) == mono_morph

    # add edge to SG so not any kind of morphism
    SG.add_edge(0, 2)
    assert not SG_ic(FG, SG, symmetry=symmetry)


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("SG_ic", is_SG_funcs + is_mono_funcs + is_iso_funcs)
def test_multiedge_mono_subgraph(SG_ic, symmetry, Gclass):
    # small cycles
    FG = nx.cycle_graph("abcd", create_using=Gclass)
    SG = nx.path_graph(3, create_using=Gclass)

    subgraph_morph = "SG" in SG_ic.__name__  # induced iso or mono
    mono_morph = "mono" in SG_ic.__name__
    not_multi = not SG.is_multigraph()
    multi_mono = mono_morph or (not_multi and subgraph_morph)

    nm = nmatch
    em = mematch if SG.is_multigraph() else ematch

    # add multiedges
    FG.add_edges_from(["ab", "ab"])
    SG.add_edges_from([(0, 1), (0, 1)])
    assert SG_ic(FG, SG, symmetry=symmetry) == subgraph_morph
    result = SG_ic(FG, SG, node_label=nm, edge_label=em, symmetry=symmetry)
    assert result == subgraph_morph

    # change color of one multiedge
    if SG.is_multigraph():
        SG[0][1][1]["foo"] = "pink"
        assert not SG_ic(FG, SG, node_label=nm, edge_label=em, symmetry=symmetry)
        del SG[0][1][1]["foo"]

    # change number of multiedges
    FG.add_edges_from(["ab"])

    assert SG_ic(FG, SG, symmetry=symmetry) == multi_mono
    result = SG_ic(FG, SG, node_label=nm, edge_label=em, symmetry=symmetry)
    assert result == multi_mono

    # change SG to hve more multiedges than FG (not iso unless not multigraph)
    SG.add_edges_from([(0, 1), (0, 1)])
    assert SG_ic(FG, SG, symmetry=symmetry) == (not_multi and subgraph_morph)

    # match multiedge count by adding edge to FG
    FG.add_edges_from(["ab"])
    assert SG_ic(FG, SG, symmetry=symmetry) == subgraph_morph


@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("SG_ic", is_SG_funcs + is_mono_funcs + is_iso_funcs)
def test_multiedge_colors_like_multiple_graphs(SG_ic, symmetry, Gclass):
    FG = nx.empty_graph(10, create_using=nx.MultiDiGraph)
    SG = nx.empty_graph(10, create_using=nx.MultiDiGraph)
    for i, G in enumerate(solo_graphs):
        # The edges from each test graph are added with a different color
        tmpG = G()
        nx.set_edge_attributes(tmpG, i, "foo")
        FG.add_edges_from(tmpG.edges(data="foo"))
        # only some of the test graphs are added to the subgraph
        if i < len(solo_graphs) / 2:
            SG.add_edges_from(tmpG.edges(data="foo"))

    FG = Gclass(FG)
    SG = Gclass(SG)

    mono_morph = "mono" in SG_ic.__name__

    nm = nmatch
    em = mematch if SG.is_multigraph() else ematch

    assert SG_ic(SG, SG, symmetry=symmetry)
    assert SG_ic(FG, FG, symmetry=symmetry)
    assert SG_ic(FG, FG, node_label=nm, edge_label=em, symmetry=symmetry)
    assert SG_ic(SG, SG, node_label=nm, edge_label=em, symmetry=symmetry)

    assert not SG_ic(SG, FG, symmetry=symmetry)  # small graph is 1st input
    assert SG_ic(FG, SG, symmetry=symmetry) == mono_morph
    assert SG_ic(FG, SG, node_label=nm, edge_label=em, symmetry=symmetry) == mono_morph


@pytest.mark.parametrize("symmetry", [True, False])
@pytest.mark.parametrize("SG_ic", is_SG_funcs + is_mono_funcs + is_iso_funcs)
def test_match_multiedge_to_simple_graph(SG_ic, symmetry):
    MDG = cycle6_plus_3_2paths()
    DG = nx.DiGraph(MDG)
    MG = nx.MultiGraph(MDG)
    G = nx.Graph(MDG)

    mono_morph = "mono" in SG_ic.__name__

    assert SG_ic(MDG, DG, symmetry=symmetry) == mono_morph
    assert SG_ic(MG, G, symmetry=symmetry) == mono_morph
    assert not SG_ic(DG, MDG, symmetry=symmetry)  # should be "not SG_ic..."
    assert not SG_ic(G, MG, symmetry=symmetry)  # should be "not SG_ic..."
