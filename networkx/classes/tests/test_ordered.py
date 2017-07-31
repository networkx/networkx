from nose.tools import assert_equals
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

class TestOrderedFeatures(object):
    def setUp(self):
        self.G = nx.OrderedDiGraph()
        self.G.add_nodes_from([1,2,3])
        self.G.add_edges_from([(2, 3), (1, 3)])

    def test_subgraph_order(self):
        G = self.G
        G_sub = G.subgraph([1,2,3])
        #G_sub = nx.induced_subgraph(G, [1,2,3])
        assert_equals(list(G.nodes), list(G_sub.nodes))
        assert_equals(list(G.edges), list(G_sub.edges))
        # This is a bug pointed out in #2048   
        # Will be fixed in coming commit and these tests changed
        # FIXME take out the sorted. replace with list
        assert_equals(list(G.pred[3]), sorted(G_sub.pred[3], reverse=True))
        assert_equals([2, 1], sorted(G_sub.pred[3], reverse=True))
        assert_equals([], list(G_sub.succ[3]))

