import networkx as nx

class SmokeTestOrdered(object):
    # Just test instantiation.
    def test_graph():
        G = nx.OrderedGraph()

    def test_digraph():
        G = nx.OrderedDiGraph()

    def test_multigraph():
        G = nx.OrderedMultiGraph()

    def test_multidigraph():
        G = nx.OrderedMultiDiGraph()

