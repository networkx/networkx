import networkx as nx
from networkx.algorithms.split_graph import is_complete_split_graph, is_split_graph


def test_is_split_graph():
    G1 = nx.complete_graph(4)
    assert is_split_graph(G1)

    G2 = nx.star_graph(3)
    assert is_split_graph(G2)

    G3 = nx.Graph([(1, 2), (1, 3), (2, 3), (3, 4)])
    assert is_split_graph(G3)

    G4 = nx.path_graph(4)
    assert is_split_graph(G4)

    G5 = nx.cycle_graph(4)
    assert not is_split_graph(G5)


def test_is_complete_split_graph():
    G1 = nx.star_graph(3)
    assert is_complete_split_graph(G1)

    G2 = nx.Graph([(1, 2), (1, 3), (2, 3), (3, 4)])
    assert not is_complete_split_graph(G2)

    G3 = nx.path_graph(4)
    assert not is_complete_split_graph(G3)

    G4 = nx.cycle_graph(4)
    assert not is_complete_split_graph(G4)

    G5 = nx.complete_graph(4)
    assert is_complete_split_graph(G5)
