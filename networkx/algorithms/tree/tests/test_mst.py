# test_mst.py - unit tests for minimum spanning tree functions
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.algorithms.tree.mst` module."""
from nose.tools import assert_equal
from nose.tools import assert_true
from nose.tools import raises

import networkx as nx


class TestMST:

    def setUp(self):
        # example from Wikipedia:
        # <https://en.wikipedia.org/wiki/Kruskal's_algorithm>
        G = nx.Graph()
        edges = [(0, 1, 7), (0, 3, 5), (1, 2, 8), (1, 3, 9), (1, 4, 7),
                 (2, 4, 5), (3, 4, 15), (3, 5, 6), (4, 5, 8), (4, 6, 9),
                 (5, 6, 11)]
        G.add_weighted_edges_from(edges)
        self.G = G
        minimum_spanning_edgelist = [(0, 1, {'weight': 7}),
                                     (0, 3, {'weight': 5}),
                                     (3, 5, {'weight': 6}),
                                     (1, 4, {'weight': 7}),
                                     (4, 2, {'weight': 5}),
                                     (4, 6, {'weight': 9})]

        self.minimum_spanning_edgelist = sorted(
            (min(u, v), max(u, v), d) for u, v, d in minimum_spanning_edgelist)

        maximum_spanning_edgelist = [(0, 1, {'weight': 7}),
                                     (1, 2, {'weight': 8}),
                                     (1, 3, {'weight': 9}),
                                     (3, 4, {'weight': 15}),
                                     (4, 6, {'weight': 9}),
                                     (5, 6, {'weight': 11})]

        self.maximum_spanning_edgelist = sorted(
            (min(u, v), max(u, v), d) for u, v, d in maximum_spanning_edgelist)

    def test_kruskal_minimum_spanning_tree(self):
        T = nx.minimum_spanning_tree(self.G, algorithm='kruskal')
        assert_equal(sorted(T.edges(data=True)), self.minimum_spanning_edgelist)

    def test_maximum_spanning_tree(self):
        T = nx.maximum_spanning_tree(self.G, algorithm='kruskal')
        assert_equal(sorted(T.edges(data=True)), self.maximum_spanning_edgelist)

    def test_kruskal_minimum_spanning_edges(self):
        edgelist = sorted(nx.minimum_spanning_edges(self.G, algorithm='kruskal'))
        assert_equal(edgelist, self.minimum_spanning_edgelist)

    def test_kruskal_maximum_spanning_edges(self):
        edgelist = sorted(nx.maximum_spanning_edges(self.G, algorithm='kruskal'))
        assert_equal(edgelist, self.maximum_spanning_edgelist)

    def test_kruskal_minimum_spanning_tree_disconnected(self):
        G = nx.Graph()
        G.add_edge(1, 2)
        G.add_edge(10, 20)
        T = nx.minimum_spanning_tree(G, algorithm='kruskal')
        assert_equal(sorted(map(sorted, T.edges())), [[1, 2], [10, 20]])
        assert_equal(sorted(T.nodes()), [1, 2, 10, 20])

    def test_kruskal_maximum_spanning_tree_disconnected(self):
        G = nx.Graph()
        G.add_edge(1, 2)
        G.add_edge(10, 20)
        T = nx.maximum_spanning_tree(G, algorithm='kruskal')
        assert_equal(sorted(map(sorted, T.edges())), [[1, 2], [10, 20]])
        assert_equal(sorted(T.nodes()), [1, 2, 10, 20])

    def test_kruskal_minimum_spanning_tree_isolate(self):
        G = nx.Graph()
        G.add_nodes_from([1, 2])
        T = nx.minimum_spanning_tree(G, algorithm='kruskal')
        assert_equal(sorted(T.nodes()), [1, 2])
        assert_equal(sorted(T.edges()), [])

    def test_kruskal_maximum_spanning_tree_isolate(self):
        G = nx.Graph()
        G.add_nodes_from([1, 2])
        T = nx.maximum_spanning_tree(G, algorithm='kruskal')
        assert_equal(sorted(T.nodes()), [1, 2])
        assert_equal(sorted(T.edges()), [])

    def test_kruskal_minimum_spanning_tree_attributes(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=1, color='red', distance=7)
        G.add_edge(2, 3, weight=1, color='green', distance=2)
        G.add_edge(1, 3, weight=10, color='blue', distance=1)
        G.add_node(13, color='purple')
        G.graph['foo'] = 'bar'
        T = nx.minimum_spanning_tree(G, algorithm='kruskal')
        assert_equal(T.graph, G.graph)
        assert_equal(T.node[13], G.node[13])
        assert_equal(T.edge[1][2], G.edge[1][2])

    def test_kruskal_maximum_spanning_tree_attributes(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=1, color='red', distance=7)
        G.add_edge(2, 3, weight=1, color='green', distance=2)
        G.add_edge(1, 3, weight=10, color='blue', distance=1)
        G.add_node(13, color='purple')
        G.graph['foo'] = 'bar'
        T = nx.maximum_spanning_tree(G, algorithm='kruskal')
        assert_equal(T.graph, G.graph)
        assert_equal(T.node[13], G.node[13])
        assert_equal(T.edge[1][2], G.edge[1][2])

    def test_kruskal_minimum_spanning_tree_edges_specify_weight(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=1, color='red', distance=7)
        G.add_edge(1, 3, weight=30, color='blue', distance=1)
        G.add_edge(2, 3, weight=1, color='green', distance=1)
        G.add_node(13, color='purple')
        G.graph['foo'] = 'bar'
        T = nx.minimum_spanning_tree(G, algorithm='kruskal')
        assert_equal(sorted(T.nodes()), [1, 2, 3, 13])
        assert_equal(sorted(T.edges()), [(1, 2), (2, 3)])
        T = nx.minimum_spanning_tree(G, algorithm='kruskal', weight='distance')
        assert_equal(sorted(T.edges()), [(1, 3), (2, 3)])
        assert_equal(sorted(T.nodes()), [1, 2, 3, 13])

    def test_kruskal_maximum_spanning_tree_edges_specify_weight(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=1, color='red', distance=7)
        G.add_edge(1, 3, weight=30, color='blue', distance=1)
        G.add_edge(2, 3, weight=1, color='green', distance=1)
        G.add_node(13, color='purple')
        G.graph['foo'] = 'bar'
        T = nx.maximum_spanning_tree(G, algorithm='kruskal')
        assert_equal(sorted(T.nodes()), [1, 2, 3, 13])
        assert_equal(sorted(T.edges()), [(1, 2), (1, 3)])
        T = nx.maximum_spanning_tree(G, algorithm='kruskal', weight='distance')
        assert_equal(sorted(T.edges()), [(1, 2), (1, 3)])
        assert_equal(sorted(T.nodes()), [1, 2, 3, 13])

    def test_prim_minimum_spanning_tree(self):
        T = nx.minimum_spanning_tree(self.G, algorithm='prim')
        assert_equal(sorted(T.edges(data=True)), self.minimum_spanning_edgelist)

    def test_prim_maximum_spanning_tree(self):
        T = nx.maximum_spanning_tree(self.G, algorithm='prim')
        assert_equal(sorted(T.edges(data=True)), self.maximum_spanning_edgelist)

    def test_prim_minimum_spanning_edges(self):
        edgelist = sorted(nx.minimum_spanning_edges(self.G, algorithm='prim'))
        edgelist = sorted((sorted((u, v))[0], sorted((u, v))[1], d)
                          for u, v, d in edgelist)
        assert_equal(edgelist, self.minimum_spanning_edgelist)

    def test_prim_maximum_spanning_edges(self):
        edgelist = sorted(nx.maximum_spanning_edges(self.G, algorithm='prim'))
        edgelist = sorted((sorted((u, v))[0], sorted((u, v))[1], d)
                          for u, v, d in edgelist)
        assert_equal(edgelist, self.maximum_spanning_edgelist)

    def test_prim_minimum_spanning_tree_disconnected(self):
        G = nx.Graph()
        G.add_edge(1, 2)
        G.add_edge(10, 20)
        T = nx.minimum_spanning_tree(G, algorithm='prim')
        assert_equal(sorted(map(sorted, T.edges())), [[1, 2], [10, 20]])
        assert_equal(sorted(T.nodes()), [1, 2, 10, 20])

    def test_prim_maximum_spanning_tree_disconnected(self):
        G = nx.Graph()
        G.add_edge(1, 2)
        G.add_edge(10, 20)
        T = nx.maximum_spanning_tree(G, algorithm='prim')
        assert_equal(sorted(map(sorted, T.edges())), [[1, 2], [10, 20]])
        assert_equal(sorted(T.nodes()), [1, 2, 10, 20])

    def test_prim_minimum_spanning_tree_isolate(self):
        G = nx.Graph()
        G.add_nodes_from([1, 2])
        T = nx.minimum_spanning_tree(G, algorithm='prim')
        assert_equal(sorted(T.nodes()), [1, 2])
        assert_equal(sorted(T.edges()), [])

    def test_prim_maximum_spanning_tree_isolate(self):
        G = nx.Graph()
        G.add_nodes_from([1, 2])
        T = nx.maximum_spanning_tree(G, algorithm='prim')
        assert_equal(sorted(T.nodes()), [1, 2])
        assert_equal(sorted(T.edges()), [])

    def test_prim_minimum_spanning_tree_attributes(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=1, color='red', distance=7)
        G.add_edge(2, 3, weight=1, color='green', distance=2)
        G.add_edge(1, 3, weight=10, color='blue', distance=1)
        G.add_node(13, color='purple')
        G.graph['foo'] = 'bar'
        T = nx.minimum_spanning_tree(G, algorithm='prim')
        assert_equal(T.graph, G.graph)
        assert_equal(T.node[13], G.node[13])
        assert_equal(T.edge[1][2], G.edge[1][2])

    def test_prim_maximum_spanning_tree_attributes(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=1, color='red', distance=7)
        G.add_edge(2, 3, weight=1, color='green', distance=2)
        G.add_edge(1, 3, weight=10, color='blue', distance=1)
        G.add_node(13, color='purple')
        G.graph['foo'] = 'bar'
        T = nx.maximum_spanning_tree(G, algorithm='prim')
        assert_equal(T.graph, G.graph)
        assert_equal(T.node[13], G.node[13])
        assert_equal(T.edge[1][2], G.edge[1][2])

    def test_prim_minimum_spanning_tree_edges_specify_weight(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=1, color='red', distance=7)
        G.add_edge(1, 3, weight=30, color='blue', distance=1)
        G.add_edge(2, 3, weight=1, color='green', distance=1)
        G.add_node(13, color='purple')
        G.graph['foo'] = 'bar'
        T = nx.minimum_spanning_tree(G, algorithm='prim')
        assert_equal(sorted(T.nodes()), [1, 2, 3, 13])
        assert_equal(sorted(T.edges()), [(1, 2), (2, 3)])
        T = nx.minimum_spanning_tree(G, weight='distance', algorithm='prim')
        assert_equal(sorted(T.edges()), [(1, 3), (2, 3)])
        assert_equal(sorted(T.nodes()), [1, 2, 3, 13])

    def test_prim_maximum_spanning_tree_edges_specify_weight(self):
        G = nx.Graph()
        G.add_edge(1, 2, weight=1, color='red', distance=7)
        G.add_edge(1, 3, weight=30, color='blue', distance=1)
        G.add_edge(2, 3, weight=1, color='green', distance=1)
        G.add_node(13, color='purple')
        G.graph['foo'] = 'bar'
        T = nx.maximum_spanning_tree(G, algorithm='prim')
        assert_equal(sorted(T.nodes()), [1, 2, 3, 13])
        assert_equal(sorted(T.edges()), [(1, 2), (1, 3)])
        T = nx.maximum_spanning_tree(G, weight='distance', algorithm='prim')
        assert_equal(sorted(T.edges()), [(1, 2), (1, 3)])
        assert_equal(sorted(T.nodes()), [1, 2, 3, 13])

    @raises(ValueError)
    def test_wrong_value(self):
        nx.minimum_spanning_tree(self.G, algorithm='random')

    def test_multigraph_keys(self):
        """Tests that the minimum spanning edges of a multigraph
        preserves edge keys.

        """
        G = nx.MultiGraph()
        G.add_edge(0, 1, key='a', weight=2)
        G.add_edge(0, 1, key='b', weight=1)
        mst_edges = nx.minimum_spanning_edges(G, algorithm='kruskal',
                                              data=False)
        assert_equal([(0, 1, 'b')], list(mst_edges))
        mst_edges = nx.minimum_spanning_edges(G, algorithm='prim', data=False)
        assert_equal([(0, 1, 'b')], list(mst_edges))

    def test_multigraph_keys_max(self):
        """Tests that the maximum spanning edges of a multigraph
        preserves edge keys.

        """
        G = nx.MultiGraph()
        G.add_edge(0, 1, key='a', weight=2)
        G.add_edge(0, 1, key='b', weight=1)
        mst_edges = nx.maximum_spanning_edges(G, algorithm='kruskal',
                                              data=False)
        assert_equal([(0, 1, 'a')], list(mst_edges))
        mst_edges = nx.maximum_spanning_edges(G, algorithm='prim', data=False)
        assert_equal([(0, 1, 'a')], list(mst_edges))

    def test_multigraph_keys_tree(self):
        G = nx.MultiGraph()
        G.add_edge(0, 1, key='a', weight=2)
        G.add_edge(0, 1, key='b', weight=1)
        T = nx.minimum_spanning_tree(G)
        assert_equal([(0, 1, 1)], list(T.edges(data='weight')))

    def test_multigraph_keys_tree_max(self):
        G = nx.MultiGraph()
        G.add_edge(0, 1, key='a', weight=2)
        G.add_edge(0, 1, key='b', weight=1)
        T = nx.maximum_spanning_tree(G)
        assert_equal([(0, 1, 2)], list(T.edges(data='weight')))

    def test_maximum_spanning_tree_as_multigraph(self):
        G = nx.MultiGraph()
        G.add_edge(0, 1, key='a', weight=2)
        G.add_edge(0, 1, key='b', weight=1)
        T = nx.maximum_spanning_tree(G, as_multigraph=True)
        assert_true(T.is_multigraph())
        assert_equal([(0, 1, 'a', 2)], list(T.edges(keys=True, data='weight')))

    def test_minimum_spanning_tree_as_multigraph(self):
        G = nx.MultiGraph()
        G.add_edge(0, 1, key='a', weight=2)
        G.add_edge(0, 1, key='b', weight=1)
        T = nx.minimum_spanning_tree(G, as_multigraph=True)
        assert_true(T.is_multigraph())
        assert_equal([(0, 1, 'b', 1)], list(T.edges(keys=True, data='weight')))
