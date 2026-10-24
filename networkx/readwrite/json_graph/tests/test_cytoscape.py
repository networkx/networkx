import copy
import json

import pytest

import networkx as nx
from networkx.readwrite.json_graph import cytoscape_data, cytoscape_graph


def test_graph():
    G = nx.path_graph(4)
    H = cytoscape_graph(cytoscape_data(G))
    assert nx.is_isomorphic(G, H)


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


@pytest.mark.parametrize(
    "graph_type", [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
)
def test_cartesian_product_round_trip(graph_type):
    base = nx.DiGraph([("a", "b")])
    G = graph_type(nx.cartesian_product(base, base))
    data = json.loads(json.dumps(cytoscape_data(G)))
    node_ids = {node["data"]["id"] for node in data["elements"]["nodes"]}
    for edge in data["elements"]["edges"]:
        assert isinstance(edge["data"]["source"], str)
        assert isinstance(edge["data"]["target"], str)
        assert edge["data"]["source"] in node_ids
        assert edge["data"]["target"] in node_ids

    H = cytoscape_graph(data)
    assert set(H) == set(G)
    assert set(H.edges) == set(G.edges)
    assert type(H) is type(G)


@pytest.mark.parametrize(
    "graph_type", [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
)
@pytest.mark.parametrize("ident", ["id", "custom_id"])
@pytest.mark.parametrize("labels", [(1, 2), ("right", "left")])
def test_edges_reference_custom_node_ids(graph_type, ident, labels):
    source, target = labels
    G = graph_type()
    G.add_node(source, **{ident: "left"})
    G.add_node(target, **{ident: "right"})
    G.add_edge(source, target, color="blue")
    if G.is_multigraph():
        G.add_edge(source, target, key="second", color="red")

    original = copy.deepcopy(G)
    data = cytoscape_data(G, ident=ident)
    for edge in data["elements"]["edges"]:
        assert edge["data"]["source"] == "left"
        assert edge["data"]["target"] == "right"

    H = cytoscape_graph(json.loads(json.dumps(data)), ident=ident)
    assert set(H) == set(G)
    assert set(H.edges) == set(G.edges)
    if G.is_multigraph():
        assert H[source][target]["second"]["color"] == "red"
    else:
        assert H[source][target]["color"] == "blue"
    assert nx.utils.graphs_equal(G, original)


def test_nested_tuple_node_round_trip():
    G = nx.Graph()
    node = ("a", (1, 2))
    G.add_edge(node, "b")
    H = cytoscape_graph(json.loads(json.dumps(cytoscape_data(G))))
    assert set(H) == set(G)
    assert H.has_edge(node, "b")


@pytest.mark.parametrize("nodes", [(0, 1), (("a", (1, 2)), ("b", (2, 3)))])
def test_legacy_edge_endpoints(nodes):
    source, target = nodes
    data = {
        "data": [],
        "elements": {
            "nodes": [
                {"data": {"id": "0", "value": source}},
                {"data": {"id": "1", "value": target}},
            ],
            "edges": [{"data": {"source": source, "target": target}}],
        },
    }
    H = cytoscape_graph(json.loads(json.dumps(data)))
    assert set(H) == set(nodes)
    assert H.has_edge(source, target)


@pytest.mark.parametrize(
    "graph_type", [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
)
@pytest.mark.parametrize(
    "node_ids, kwargs", [(("b", "c", "d"), {}), (("b", "c", "a"), {"legacy": True})]
)
def test_legacy_string_edge_endpoints(graph_type, node_ids, kwargs):
    G = graph_type([("a", "b", {"weight": 3}), ("b", "c", {"weight": 5})])
    data = {
        "data": [],
        "directed": G.is_directed(),
        "multigraph": G.is_multigraph(),
        "elements": {
            "nodes": [
                {"data": {"id": node_id, "value": node}}
                for node, node_id in zip(G, node_ids)
            ],
            "edges": [
                {"data": {"source": "b", "target": "c", "weight": 5}},
                {"data": {"source": "a", "target": "b", "weight": 3}},
            ],
        },
    }
    original = copy.deepcopy(data)
    H = cytoscape_graph(data, **kwargs)
    assert type(H) is graph_type
    assert set(H) == set(G)
    assert set(H.edges) == set(G.edges)
    assert nx.get_edge_attributes(H, "weight") == nx.get_edge_attributes(G, "weight")
    assert data == original


@pytest.mark.parametrize("missing_ids", [("a",), ("a", "b")])
def test_nodes_without_ids(missing_ids):
    data = {
        "data": [],
        "elements": {
            "nodes": [
                {"data": {"id": "a", "value": "a"}},
                {"data": {"id": "b", "value": "b"}},
            ],
            "edges": [{"data": {"source": "a", "target": "b"}}],
        },
    }
    for node in data["elements"]["nodes"]:
        if node["data"]["value"] in missing_ids:
            del node["data"]["id"]
    original = copy.deepcopy(data)
    H = cytoscape_graph(data)
    assert set(H) == {"a", "b"}
    assert set(H.edges) == {("a", "b")}
    assert data == original


def test_duplicate_node_ids():
    G = nx.Graph()
    G.add_nodes_from([1, "1"])
    with pytest.raises(nx.NetworkXError, match="unique"):
        cytoscape_data(G)
