import copy
import json

import pytest

import networkx as nx
from networkx.readwrite.json_graph import cytoscape_data, cytoscape_graph


def test_graph():
    G = nx.path_graph(4)
    H = cytoscape_graph(cytoscape_data(G))
    assert nx.is_isomorphic(G, H)


@pytest.mark.parametrize(
    "make_graph",
    [
        lambda: nx.path_graph(4),
        lambda: nx.DiGraph([(1, 2), (2, 3)]),
        lambda: nx.MultiGraph([(1, 2)]),
        lambda: nx.MultiDiGraph([(1, 2), (1, 2)]),
        lambda: nx.cartesian_product(
            nx.DiGraph([("a", "b")]), nx.DiGraph([("a", "b")])
        ),
        lambda: nx.Graph([((1, 2), (3, 4)), ((3, 4), (5, 6))]),
    ],
    ids=["path", "digraph", "multigraph", "multidigraph", "cartesian", "tuple-nodes"],
)
def test_export_edge_ends_match_node_ids(make_graph):
    # Every edge's source/target must reference a node id that exists in the
    # export (gh-7962: cartesian-product graphs exported edges as arrays).
    G = make_graph()
    data = cytoscape_data(G)
    ids = {el["data"]["id"] for el in data["elements"]["nodes"]}
    for el in data["elements"]["edges"]:
        assert el["data"]["source"] in ids
        assert el["data"]["target"] in ids
    H = cytoscape_graph(json.loads(json.dumps(data)))
    assert nx.is_isomorphic(G, H)


@pytest.mark.parametrize(
    "nodes",
    [
        [0, 1, 2],
        ["a", "b", "c"],
        [(1, 2), (3, 4), (5, 6)],
        [1.5, "x", (1, 2)],
    ],
    ids=["int", "str", "tuple", "mixed"],
)
def test_roundtrip_complex_node_types(nodes):
    G = nx.DiGraph()
    nx.add_path(G, nodes)
    data = cytoscape_data(G)
    H = cytoscape_graph(json.loads(json.dumps(data)))
    assert nx.is_isomorphic(G, H)


def test_legacy_export_with_list_edge_ends():
    # Exports written before gh-7962 stored raw tuple node objects in edge
    # ends, which serialize to JSON arrays. Reading those must still round-trip.
    legacy = {
        "data": [],
        "directed": False,
        "multigraph": False,
        "elements": {
            "nodes": [
                {"data": {"id": "(1, 2)", "value": [1, 2], "name": "(1, 2)"}},
                {"data": {"id": "(3, 4)", "value": [3, 4], "name": "(3, 4)"}},
            ],
            "edges": [{"data": {"source": [1, 2], "target": [3, 4]}}],
        },
    }
    H = cytoscape_graph(json.loads(json.dumps(legacy)))
    assert nx.is_isomorphic(nx.Graph([((1, 2), (3, 4))]), H)
    assert (1, 2) in H.nodes
    assert (3, 4) in H.nodes


def test_input_data_is_not_modified_when_building_graph():
    G = nx.path_graph(4)
    input_data = cytoscape_data(G)
    orig_data = copy.deepcopy(input_data)
    # Ensure input is unmodified by cytoscape_graph (gh-4173)
    cytoscape_graph(input_data)
    assert input_data == orig_data


def test_graph_attributes():
    G = nx.path_graph(4)
    G.add_node(1, color="red")
    G.add_edge(1, 2, width=7)
    G.graph["foo"] = "bar"
    G.graph[1] = "one"
    G.add_node(3, name="node", id="123")

    H = cytoscape_graph(cytoscape_data(G))
    assert H.graph["foo"] == "bar"
    assert H.nodes[1]["color"] == "red"
    assert H[1][2]["width"] == 7
    assert H.nodes[3]["name"] == "node"
    assert H.nodes[3]["id"] == "123"

    d = json.dumps(cytoscape_data(G))
    H = cytoscape_graph(json.loads(d))
    assert H.graph["foo"] == "bar"
    assert H.graph[1] == "one"
    assert H.nodes[1]["color"] == "red"
    assert H[1][2]["width"] == 7
    assert H.nodes[3]["name"] == "node"
    assert H.nodes[3]["id"] == "123"


def test_digraph():
    G = nx.DiGraph()
    nx.add_path(G, [1, 2, 3])
    H = cytoscape_graph(cytoscape_data(G))
    assert H.is_directed()
    assert nx.is_isomorphic(G, H)


def test_multidigraph():
    G = nx.MultiDiGraph()
    nx.add_path(G, [1, 2, 3])
    H = cytoscape_graph(cytoscape_data(G))
    assert H.is_directed()
    assert H.is_multigraph()


def test_multigraph():
    G = nx.MultiGraph()
    G.add_edge(1, 2, key="first")
    G.add_edge(1, 2, key="second", color="blue")
    H = cytoscape_graph(cytoscape_data(G))
    assert nx.is_isomorphic(G, H)
    assert H[1][2]["second"]["color"] == "blue"


def test_exception():
    with pytest.raises(nx.NetworkXError):
        G = nx.MultiDiGraph()
        cytoscape_data(G, name="foo", ident="foo")
