import json

import pytest

import networkx as nx


@pytest.mark.parametrize(
    "graph_type", [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
)
@pytest.mark.parametrize(
    "nodes", [(0, 1), (("a", "b"), ("c", "d")), (("a", ("b", 1)), ("c", ("d", 2)))]
)
def test_cytoscape_edge_ids_and_json_roundtrip(graph_type, nodes):
    graph = graph_type()
    graph.add_edge(*nodes, weight=7)
    data = nx.cytoscape_data(graph)
    ids = {item["data"]["id"] for item in data["elements"]["nodes"]}
    for edge in data["elements"]["edges"]:
        assert edge["data"]["source"] in ids
        assert edge["data"]["target"] in ids
    restored = nx.cytoscape_graph(json.loads(json.dumps(data)))
    assert set(restored) == set(graph)
    assert set(restored.edges) == set(graph.edges)


@pytest.mark.parametrize(
    "graph_type", [nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
)
def test_cytoscape_custom_ids(graph_type):
    graph = graph_type()
    graph.add_node("a", external_id="node-a")
    graph.add_node("b", external_id="node-b")
    graph.add_edge("a", "b", weight=7)
    data = nx.cytoscape_data(graph, ident="external_id")
    edge = data["elements"]["edges"][0]["data"]
    assert edge["source"] == "node-a"
    assert edge["target"] == "node-b"
    restored = nx.cytoscape_graph(json.loads(json.dumps(data)), ident="external_id")
    assert set(restored) == {"a", "b"}
    assert restored.has_edge("a", "b")


def test_cytoscape_legacy_numeric_endpoints():
    graph = nx.path_graph(3)
    data = nx.cytoscape_data(graph)
    for edge, (source, target) in zip(data["elements"]["edges"], graph.edges):
        edge["data"].update(source=source, target=target)
    restored = nx.cytoscape_graph(data)
    assert set(restored.edges) == set(graph.edges)