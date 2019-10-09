import networkx as nx
import networkx.algorithms.approximation as a


def test_independent_set():
    # smoke test
    G = nx.Graph()
    assert len(a.maximum_independent_set(G)) == 0
