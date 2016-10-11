import networkx as nx
from networkx.algorithms.approximation import feedback_vertex_set
from networkx.exception import NetworkXError, NetworkXNotImplemented
from nose.tools import *


class TestFeedbackVertexSet():
    def test_cycle(self):
        G = nx.cycle_graph(10)
        F = feedback_vertex_set(G)
        assert_equal(len(F), 1)

    def test_complete(self):
        G = nx.complete_graph(10)
        F = feedback_vertex_set(G)
        assert_equal(len(F), 8)

    def test_path(self):
        G = nx.path_graph(10)
        F = feedback_vertex_set(G)
        assert_equal(F, [])

    def test_tree(self):
        G = nx.balanced_tree(4,4)
        F = feedback_vertex_set(G)
        assert_equal(F, [])       

    def test_empty(self):
        G = nx.Graph()
        F = feedback_vertex_set(G)
        assert_equal(F, [])   

    def test_weighted_cycle(self):
        # should remove the lowest weighted vertex only
        G = nx.cycle_graph(10)
        w = {v:(2.0 - 0.1*v) for v in G.nodes()}
        F = feedback_vertex_set(G, w)
        assert_equal(F, [9]) 

    def test_weighted_complete(self):
        # should remove all but the two highest weighted vertices
        G = nx.complete_graph(10)
        w = {v:(2.0 - 0.1*v) for v in G.nodes()}
        F = feedback_vertex_set(G, w)
        assert_equal(sorted(F), range(2,10))        

    def test_house(self):
        G = nx.house_graph()
        F = feedback_vertex_set(G)
        assert_true(F==[2] or F==[3])   

    def test_weights_exception(self):
        G = nx.complete_graph(10)
        w = {v:1 for v in range(9)}
        assert_raises(NetworkXError, feedback_vertex_set, G, w)

    def test_digraph(self):
        G = nx.DiGraph()
        assert_raises(NetworkXNotImplemented, feedback_vertex_set, G)

    def test_multigraph(self):
        G = nx.MultiGraph()
        assert_raises(NetworkXNotImplemented, feedback_vertex_set, G)
