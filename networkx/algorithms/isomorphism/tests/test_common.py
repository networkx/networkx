import itertools as it

import pytest

import networkx as nx
from networkx.algorithms import isomorphism as iso

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

nm = iso.categorical_node_match("label", "")
em = iso.categorical_edge_match("foo", "")


def ismags_is_iso(G1, G2, node_label=None, edge_label=None):
    return iso.ISMAGS(G1, G2, node_label, edge_label).is_isomorphic()


def ismags_iter(G1, G2, node_label=None, edge_label=None):
    return iso.ISMAGS(G1, G2, node_label, edge_label).isomorphisms_iter(symmetry=False)


def ismags_is_SG_iso(G1, G2, node_label=None, edge_label=None):
    return iso.ISMAGS(G1, G2, node_label, edge_label).subgraph_is_isomorphic()


def ismags_subgraph_iter(G1, G2, node_label=None, edge_label=None):
    return iso.ISMAGS(G1, G2, node_label, edge_label).subgraph_isomorphisms_iter(symmetry=False)


def ismags_is_SG_mono(G1, G2, node_label=None, edge_label=None):
    return NotImplemented
    return True


def ismags_mono_iter(G1, G2, node_label=None, edge_label=None):
    return NotImplemented


def vf2_is_iso(G1, G2, node_label=None, edge_label=None):
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).is_isomorphic()


def vf2_iter(G1, G2, node_label=None, edge_label=None):
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).isomorphisms_iter()


def vf2_is_SG_iso(G1, G2, node_label=None, edge_label=None):
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).subgraph_is_isomorphic()


def vf2_subgraph_iter(G1, G2, node_label=None, edge_label=None):
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).subgraph_isomorphisms_iter()


def vf2_is_SG_mono(G1, G2, node_label=None, edge_label=None):
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).subgraph_is_monomorphic()


def vf2_mono_iter(G1, G2, node_label=None, edge_label=None):
    gm = iso.GraphMatcher if not G1.is_directed() else iso.DiGraphMatcher
    return gm(G1, G2, node_label, edge_label).subgraph_monomorphisms_iter()


def vf2pp_is_iso(G1, G2, node_label=None, edge_label=None):
    return nx.vf2pp_is_isomorphic(G1, G2, node_label, edge_label)


def vf2pp_iter(G1, G2, node_label=None, edge_label=None):
    return nx.vf2pp_all_isomorphisms(G1, G2, node_label, edge_label)


def vf2pp_is_SG_iso(G1, G2, node_label=None, edge_label=None):
    return NotImplemented


def vf2pp_subgraph_iter(G1, G2, node_label=None, edge_label=None):
    return NotImplemented


def vf2pp_is_SG_mono(G1, G2, node_label=None, edge_label=None):
    return NotImplemented


def vf2pp_mono_iter(G1, G2, node_label=None, edge_label=None):
    return NotImplemented


# functions to test:
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
#
def asymm_graph1():
    G = nx.MultiDiGraph(
        [(1, 2), (1, 3), (1, 4), (2, 3), (2, 6), (3, 4), (5, 1), (5, 2)]
    )
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])

    G.graph["name"] = "asymm_graph1"
    G.graph["id"] = "asymm-graph1",
    G.graph["numb_symmetries"] = 1
    G.graph["show"] = r"""
   5-1-4
   |/ \|
 6-2---3
"""
    return G

def symm_graph1():
    G = nx.MultiDiGraph(
        [(1, 2), (1, 3), (1, 4), (2, 3), (3, 2), (2, 6), (4, 3), (3, 7), (1, 5), (5, 2)]
    )
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])

    G.graph["name"] = "symm_graph1"
    G.graph["id"] = "symm_graph1",
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
#symm_graph1 = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 6), (3, 4), (3, 7), (5, 1), (5, 2)]
#symm_graph1_mapping = {1: 1, 2: 3, 3: 2, 4: 5, 5: 4, 6: 7, 7: 6}
# Multigraph version of same graph
# move all 2-6 to 3-6 and remove all 1-4. Should now be new symmetry
# add selfloops & multiselfloops 5-5, 5-5, 1-1 check vs orig F. add 4-4,4-4,1-1 check T
# remove 1-4 add 1-5 keeping degree seq same, check F

def asymm_graph2():
    G = nx.MultiDiGraph(
         [(1, 2), (1, 5), (5, 6), (2, 3), (2, 4), (3, 4), (4, 5), (2, 7)]
    )
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])

    G.graph["name"] = "asymm_graph2"
    G.graph["id"] = "asymm_graph2",
    G.graph["numb_symmetries"] = 1
    G.graph["subgraph_nodes"] = [[2,3,4,7], [1,4,5,6]]
    G.graph["show"] = r"""
  7-2-1
   /| |     mapping {1: 1, 3: 2, 2: 3, 5: 4, 7: 6, 6: 7, 4: 5}
  3-4-5-6
"""
    return G
{1: 1, 3: 2, 2: 3, 5: 4, 7: 6, 6: 7, 4: 5}
#asymm_graph2 = [(1, 2), (1, 5), (5, 6), (2, 3), (2, 4), (3, 4), (4, 5), (2, 7)]
#subgraph2a = nx.Graph(graph2.subgraph([2, 3, 4, 7])
#subgraph2a_edges = [(2, 3), (3, 4), (2, 4), (2, 7)]
#subgraph2b = nx.Graph(graph2.subgraph([1, 4, 5, 6])
#subgraph2b_edges = [(1, 5), (5, 6), (5, 4)]  # 2->5 6->7 1->3 4->4
# check F. add 1-4 to 2b, check T. add 3-7, 4-7 to 2a & 1-6, 4-6 to 2b, check T

def cycle6_plus_3_2paths():
    G = nx.cycle_graph(6, create_using=nx.MultiDiGraph)
    nx.add_path(G, [0, 5, 4, 3, 2, 1, 0])  # for directed graphs
    nx.add_path(G, [0, 6, 7])
    nx.add_path(G, [2, 8, 9])
    nx.add_path(G, [4, 10, 11])
    # for multiedges
    G.add_edges_from([e for i, e in enumerate(G.edges) if i % 2 == 0])

    G.graph["name"] = "cycle6_plus_3_2paths"
    G.graph["id"] = "sun:6_cycle_with_2_path_rays",
    G.graph["show"] = "6-cycle with 2-paths stuck onto nodes 0, 2, 4"
    G.graph["numb_symmetries"] = 6
    return G

solo_graphs = [
    asymm_graph1,
    symm_graph1,
    asymm_graph2,
    cycle6_plus_3_2paths,
]

graph_classes = [nx.Graph, nx.MultiGraph, nx.DiGraph, nx.MultiDiGraph]

is_iso_funcs = [
    vf2_is_iso,
    vf2pp_is_iso,
    ismags_is_iso,
    vf2_is_SG_iso,
#    vf2pp_is_SG_iso,
    ismags_is_SG_iso,
    vf2_is_SG_mono,
#    vf2pp_is_SG_mono,
#    ismags_is_SG_mono,
]

mapping_iters = [
    vf2_iter,
    vf2pp_iter,
    ismags_iter,
    vf2_subgraph_iter,
#    vf2pp_subgraph_iter,
    ismags_subgraph_iter,
    vf2_mono_iter,
#    vf2pp_mono_iter,
#    ismags_mono_iter,
]

names = [
    "vf2",
    "vf2pp",
    "ismags",
    "vf2SG",
#    "vf2ppSG",
    "ismagsSG",
    "vf2_mono",
#    "vf2pp_mono",
#    "ismags_mono",
]

iso_and_mapping = [
    pytest.param(i, m, id=name) for i,m,name in zip(is_iso_funcs, mapping_iters, names)
]


@pytest.mark.parametrize("G", solo_graphs)
@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("iso_ic, iso_iter", iso_and_mapping)
def test_single_graph(G, Gclass, iso_ic, iso_iter):
    G1 = Gclass(G())
    assert iso_ic(G1, G1)

    sym = G1.graph.get("numb_symmetries", None)
    mappings = G1.graph.get("mappings", None)
    if sym is not None:
        iter_out = iso_iter(G1, G1)
        print(iter_out)
        if iter_out is not None:
            all_mappings = list(iter_out)
            print(f"{all_mappings=}")
            print(f"{G1.edges=}")
            print(G1.graph["show"])
            print(f"{mappings=}")
            assert sym == len(all_mappings)

    mappings = G1.graph.get("mappings", None)
    if mappings is not None:
        iter_out = iso_iter(G1, G1)
        if iter_out is not None:
            all_mappings = list(iso_iter(G1, G1))
            assert all(m in all_mappings for m in mappings)
            assert len(all_mappings) == len(mappings) + 1


@pytest.mark.parametrize("G", solo_graphs)
@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("iso_ic", is_iso_funcs)
def test_check_mappings(G, Gclass, iso_ic):
    G1 = Gclass(G())

    N = len(G1)
    numb = 1 if N < 2 else N // 2 if N < 26 else 10
    mapping = dict(enumerate("acdefghijklmnopqrstuvwxyz"[:numb]))
    G2 = nx.relabel_nodes(G1, mapping)

    assert iso_ic(G1, G2)


@pytest.mark.parametrize("G", solo_graphs)
@pytest.mark.parametrize("Gclass", graph_classes)
@pytest.mark.parametrize("iso_ic", is_iso_funcs)
def test_single_graph_node_and_edge_labels(G, Gclass, iso_ic):
    G1 = Gclass(G())
    nx.set_node_attributes(G1, dict(zip(G1, it.cycle(labels_same))), "label")
    nx.set_edge_attributes(G1, dict(zip(G1.edges, it.cycle(labels_same))), "foo")
    assert iso_ic(G1, G1, node_label=nm, edge_label=None)
    assert iso_ic(G1, G1, node_label=None, edge_label=em)
    assert iso_ic(G1, G1, node_label=nm, edge_label=em)

    nx.set_node_attributes(G1, dict(zip(G1, it.cycle(labels_many))), "label")
    nx.set_edge_attributes(G1, dict(zip(G1.edges, it.cycle(labels_many))), "foo")
    assert iso_ic(G1, G1, node_label=nm, edge_label=None)
    assert iso_ic(G1, G1, node_label=None, edge_label=em)
    assert iso_ic(G1, G1, node_label=nm, edge_label=em)
