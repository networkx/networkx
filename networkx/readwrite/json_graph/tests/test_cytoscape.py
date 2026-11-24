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


def test_cartesian_product():
    G = nx.DiGraph()
    G.add_edge("a", "b")
    C = nx.cartesian_product(G, G)

    cyto_data = cytoscape_data(C)
    # Edge source and target must be valid strings matching node IDs (gh-7962)
    node_ids = {n["data"]["id"] for n in cyto_data["elements"]["nodes"]}
    for edge in cyto_data["elements"]["edges"]:
        assert edge["data"]["source"] in node_ids
        assert edge["data"]["target"] in node_ids
        assert isinstance(edge["data"]["source"], str)
        assert isinstance(edge["data"]["target"], str)

    # JSON serialization and deserialization roundtrip
    dumped = json.dumps(cyto_data)
    loaded = json.loads(dumped)
    H = cytoscape_graph(loaded)
    assert nx.is_isomorphic(C, H)
    assert set(H.nodes) == set(C.nodes)
    assert set(H.edges) == set(C.edges)


def test_custom_ident():
    G = nx.Graph()
    G.add_node(1, my_id="node_one")
    G.add_node(2, my_id="node_two")
    G.add_edge(1, 2)

    cyto_data = cytoscape_data(G, ident="my_id")
    assert cyto_data["elements"]["edges"][0]["data"]["source"] == "node_one"
    assert cyto_data["elements"]["edges"][0]["data"]["target"] == "node_two"

    dumped = json.dumps(cyto_data)
    H = cytoscape_graph(json.loads(dumped), ident="my_id")
    assert nx.is_isomorphic(G, H)
    assert set(H.nodes) == {1, 2}
    assert (1, 2) in H.edges


def test_missing_value_fallback():
    data = {
        "data": [],
        "directed": False,
        "multigraph": False,
        "elements": {
            "nodes": [
                {"data": {"id": "n1"}},
                {"data": {"id": "n2"}},
            ],
            "edges": [{"data": {"source": "n1", "target": "n2"}}],
        },
    }
    G = cytoscape_graph(data)
    assert set(G.nodes) == {"n1", "n2"}
    assert ("n1", "n2") in G.edges
