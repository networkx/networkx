import json
from nose.tools import assert_equal, assert_raises, assert_not_equal,assert_true
import networkx as nx
from networkx.readwrite.json_graph import *

class TestAdjacency:

    def test_graph(self):
        G = nx.path_graph(4)
        H = adjacency_graph(adjacency_data(G))
        nx.is_isomorphic(G,H)

    def test_graph_attributes(self):
        G = nx.path_graph(4)
        G.add_node(1,color='red')
        G.add_edge(1,2,width=7)
        G.graph['foo']='bar'
        G.graph[1]='one'

        H = adjacency_graph(adjacency_data(G))
        assert_equal(H.graph['foo'],'bar')
        assert_equal(H.node[1]['color'],'red')
        assert_equal(H[1][2]['width'],7)

        d = json.dumps(adjacency_data(G))
        H = adjacency_graph(json.loads(d))
        assert_equal(H.graph['foo'],'bar')
        assert_equal(H.graph[1],'one')
        assert_equal(H.node[1]['color'],'red')
        assert_equal(H[1][2]['width'],7)
        
    def test_digraph(self):
        G = nx.DiGraph()
        H = adjacency_graph(adjacency_data(G))
        assert_true(H.is_directed())

    def test_multidigraph(self):
        G = nx.MultiDiGraph()
        H = adjacency_graph(adjacency_data(G))
        assert_true(H.is_directed())
        assert_true(H.is_multigraph())
