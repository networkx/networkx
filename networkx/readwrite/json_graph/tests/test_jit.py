import json
from nose.tools import assert_true
import networkx as nx
from networkx.readwrite.json_graph import jit_data, jit_graph

class TestJIT:

    def test_jit_graph(self):
        G = nx.Graph()
        G.add_node('Node1', node_data = 'foobar')
        G.add_node('Node3', node_data = 'bar')
        G.add_edge('Node1', 'Node2', weight = 9, something='isSomething')
        G.add_edge('Node2', 'Node3', weight = 4, something='isNotSomething')
        G.add_edge('Node1', 'Node2')
        d = jit_data(G)
        K = jit_graph(json.loads(d))
        assert_true(nx.is_isomorphic(G, K))
