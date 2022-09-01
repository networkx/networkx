import pytest

import networkx as nx
from networkx.exception import NetworkXError


def test_m_separation():
    digraph = nx.path_graph(4, create_using=nx.DiGraph)
    digraph.add_edge(2, 4)
    bigraph = nx.Graph([(2, 3)])
    bigraph.add_nodes_from(digraph)
    G = nx.MixedEdgeGraph([digraph, bigraph], ["directed", "bidirected"])

    # error should be raised if someone does not use a MixedEdgeGraph
    with pytest.raises(
        NetworkXError, match="m-separation should only be run on a MixedEdgeGraph"
    ):
        nx.m_separated(digraph, {0}, {1}, set())

    # error should be raised if the directed edges form a cycle
    G_error = G.copy()
    G_error.add_edge(4, 2, "directed")
    with pytest.raises(
        NetworkXError, match="directed edge graph should be directed acyclic"
    ):
        nx.m_separated(G_error, {0}, {3}, set())

    # if passing in non-default names for edge types, then m_separated will not work
    G_error = G.copy()
    G_error._edge_graphs["bi-directed"] = G_error.get_graphs("bidirected")
    G_error._edge_graphs.pop("bidirected")
    with pytest.raises(
        NetworkXError,
        match="m-separation only works on graphs with directed and bidirected edges.",
    ):
        nx.m_separated(G_error, {0}, {3}, set())
    assert not nx.m_separated(
        G_error, {0}, {3}, set(), bidirected_edge_name="bi-directed"
    )

    # basic d-separation statements based on blocking paths should work
    assert not nx.m_separated(G, {0}, {3}, set())
    assert nx.m_separated(G, {0}, {3}, {1})

    # conditioning on a collider via bidirected edge opens the collider
    assert not nx.m_separated(G, {0}, {3}, {2})
    assert nx.m_separated(G, {0}, {3}, {1, 2})

    # conditioning on a descendant of a collider via bidirected edge opens the collider
    assert not nx.m_separated(G, {0}, {3}, {4})
