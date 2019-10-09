""" Tests for subgraphs attributes
"""
from copy import deepcopy
import networkx as nx

# deprecated in 2.1 for removal in 2.2


class TestSubgraphAttributesDicts:

    @classmethod
    def setup_class(cls):
        cls.undirected = [
            nx.connected_component_subgraphs,
            nx.biconnected_component_subgraphs,
        ]
        cls.directed = [
            nx.weakly_connected_component_subgraphs,
            nx.strongly_connected_component_subgraphs,
            nx.attracting_component_subgraphs,
        ]
        cls.subgraph_funcs = cls.undirected + cls.directed

        cls.D = nx.DiGraph()
        cls.D.add_edge(1, 2, eattr='red')
        cls.D.add_edge(2, 1, eattr='red')
        cls.D.nodes[1]['nattr'] = 'blue'
        cls.D.graph['gattr'] = 'green'

        cls.G = nx.Graph()
        cls.G.add_edge(1, 2, eattr='red')
        cls.G.nodes[1]['nattr'] = 'blue'
        cls.G.graph['gattr'] = 'green'

    def test_subgraphs_default_copy_behavior(self):
        # Test the default behavior of subgraph functions
        # For the moment (1.10) the default is to copy
        for subgraph_func in self.subgraph_funcs:
            G = deepcopy(self.G if subgraph_func in self.undirected else self.D)
            SG = list(subgraph_func(G))[0]
            assert SG[1][2]['eattr'] == 'red'
            assert SG.nodes[1]['nattr'] == 'blue'
            assert SG.graph['gattr'] == 'green'
            SG[1][2]['eattr'] = 'foo'
            assert G[1][2]['eattr'] == 'red'
            assert SG[1][2]['eattr'] == 'foo'
            SG.nodes[1]['nattr'] = 'bar'
            assert G.nodes[1]['nattr'] == 'blue'
            assert SG.nodes[1]['nattr'] == 'bar'
            SG.graph['gattr'] = 'baz'
            assert G.graph['gattr'] == 'green'
            assert SG.graph['gattr'] == 'baz'

    def test_subgraphs_copy(self):
        for subgraph_func in self.subgraph_funcs:
            test_graph = self.G if subgraph_func in self.undirected else self.D
            G = deepcopy(test_graph)
            SG = list(subgraph_func(G, copy=True))[0]
            assert SG[1][2]['eattr'] == 'red'
            assert SG.nodes[1]['nattr'] == 'blue'
            assert SG.graph['gattr'] == 'green'
            SG[1][2]['eattr'] = 'foo'
            assert G[1][2]['eattr'] == 'red'
            assert SG[1][2]['eattr'] == 'foo'
            SG.nodes[1]['nattr'] = 'bar'
            assert G.nodes[1]['nattr'] == 'blue'
            assert SG.nodes[1]['nattr'] == 'bar'
            SG.graph['gattr'] = 'baz'
            assert G.graph['gattr'] == 'green'
            assert SG.graph['gattr'] == 'baz'

    def test_subgraphs_no_copy(self):
        for subgraph_func in self.subgraph_funcs:
            G = deepcopy(self.G if subgraph_func in self.undirected else self.D)
            SG = list(subgraph_func(G, copy=False))[0]
            assert SG[1][2]['eattr'] == 'red'
            assert SG.nodes[1]['nattr'] == 'blue'
            assert SG.graph['gattr'] == 'green'
            SG[1][2]['eattr'] = 'foo'
            assert G[1][2]['eattr'] == 'foo'
            assert SG[1][2]['eattr'] == 'foo'
            SG.nodes[1]['nattr'] = 'bar'
            assert G.nodes[1]['nattr'] == 'bar'
            assert SG.nodes[1]['nattr'] == 'bar'
            SG.graph['gattr'] = 'baz'
            assert G.graph['gattr'] == 'baz'
            assert SG.graph['gattr'] == 'baz'
