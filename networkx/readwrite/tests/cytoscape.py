import pytest

import networkx as nx


def write_and_read(G, tmp_path):
    fname = tmp_path / "cytoscape.cyjs"
    nx.write_cytoscape(G, fname)
    return nx.read_cytoscape(fname)


def test_graph(tmp_path):
    G = nx.path_graph(4)
    H = write_and_read(G, tmp_path)
    assert nx.is_isomorphic(G, H)


def test_digraph(tmp_path):
    G = nx.DiGraph()
    nx.add_path(G, [1, 2, 3])
    H = write_and_read(G, tmp_path)
    assert H.is_directed()
    assert nx.is_isomorphic(G, H)


def test_multidigraph(tmp_path):
    G = nx.MultiDiGraph()
    nx.add_path(G, [1, 2, 3])
    H = write_and_read(G, tmp_path)
    assert H.is_directed()
    assert H.is_multigraph()


def test_multigraph(tmp_path):
    G = nx.MultiGraph()
    G.add_edge(1, 2, key="first")
    G.add_edge(1, 2, key="second", color="blue")
    H = write_and_read(G, tmp_path)
    assert nx.is_isomorphic(G, H)
    assert H[1][2]["second"]["color"] == "blue"


def test_exception(tmp_path):
    with pytest.raises(nx.NetworkXError):
        G = nx.MultiDiGraph()
        fname = tmp_path / "cytoscape.cyjs"
        nx.write_cytoscape(G, fname, name="foo", ident="foo")
        H = nx.read_cytoscape(fname, name="foo", ident="foo")
