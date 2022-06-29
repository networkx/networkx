import pytest

import networkx as nx
from networkx.algorithms.community import (
    edge_betweenness_partition,
    edge_current_flow_betweenness_partition,
)


def test_edge_betweenness_partition():
    G = nx.barbell_graph(3, 0)
    C = edge_betweenness_partition(G, 2)
    assert C == [{0, 1, 2}, {3, 4, 5}]

    G = nx.barbell_graph(3, 1)
    C = edge_betweenness_partition(G, 3)
    assert C == list([{0, 1, 2}, {4, 5, 6}, {3}])

    C = edge_betweenness_partition(G, 7)
    assert C == list(map(set, [[n] for n in G]))

    C = edge_betweenness_partition(G, 1)
    assert C == [set(G)]

    with pytest.raises(nx.NetworkXError):
        edge_betweenness_partition(G, 0)

    with pytest.raises(nx.NetworkXError):
        edge_betweenness_partition(G, -1)
    with pytest.raises(nx.NetworkXError):
        edge_betweenness_partition(G, 10)


def test_edge_current_flow_betweenness_partition():
    G = nx.barbell_graph(3, 0)
    C = edge_current_flow_betweenness_partition(G, 2)
    assert C == [{0, 1, 2}, {3, 4, 5}]

    G = nx.barbell_graph(3, 1)
    C = edge_current_flow_betweenness_partition(G, 7)
    assert C == list(map(set, [[n] for n in G]))

    C = edge_current_flow_betweenness_partition(G, 1)
    assert C == [set(G)]
    with pytest.raises(nx.NetworkXError):
        edge_current_flow_betweenness_partition(G, 0)

    with pytest.raises(nx.NetworkXError):
        edge_current_flow_betweenness_partition(G, -1)
    with pytest.raises(nx.NetworkXError):
        edge_current_flow_betweenness_partition(G, 10)
