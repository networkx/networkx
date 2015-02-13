#!/usr/bin/env python
import random
from nose.tools import *
import networkx as nx

class TestFunction(object):
    def setUp(self):
        self.G=nx.Graph({0:[1,2,3], 1:[1,2,0], 4:[]}, name='Test')
        self.Gdegree={0:3, 1:2, 2:2, 3:1, 4:0}
        self.Gnodes=list(range(5))
        self.Gedges=[(0,1),(0,2),(0,3),(1,0),(1,1),(1,2)]
        self.DG=nx.DiGraph({0:[1,2,3], 1:[1,2,0], 4:[]})
        self.DGin_degree={0:1, 1:2, 2:2, 3:1, 4:0}
        self.DGout_degree={0:3, 1:3, 2:0, 3:0, 4:0}
        self.DGnodes=list(range(5))
        self.DGedges=[(0,1),(0,2),(0,3),(1,0),(1,1),(1,2)]

    def test_nodes(self):
        assert_equal(self.G.nodes(),nx.nodes(self.G))
        assert_equal(self.DG.nodes(),nx.nodes(self.DG))
    def test_edges(self):
        assert_equal(self.G.edges(),nx.edges(self.G))
        assert_equal(self.DG.edges(),nx.edges(self.DG))
        assert_equal(self.G.edges(nbunch=[0,1,3]),nx.edges(self.G,nbunch=[0,1,3]))
        assert_equal(self.DG.edges(nbunch=[0,1,3]),nx.edges(self.DG,nbunch=[0,1,3]))
    def test_nodes_iter(self):
        assert_equal(list(self.G.nodes_iter()),list(nx.nodes_iter(self.G)))
        assert_equal(list(self.DG.nodes_iter()),list(nx.nodes_iter(self.DG)))
    def test_edges_iter(self):
        assert_equal(list(self.G.edges_iter()),list(nx.edges_iter(self.G)))
        assert_equal(list(self.DG.edges_iter()),list(nx.edges_iter(self.DG)))
        assert_equal(list(self.G.edges_iter(nbunch=[0,1,3])),list(nx.edges_iter(self.G,nbunch=[0,1,3])))
        assert_equal(list(self.DG.edges_iter(nbunch=[0,1,3])),list(nx.edges_iter(self.DG,nbunch=[0,1,3])))
    def test_degree(self):
        assert_equal(self.G.degree(),nx.degree(self.G))
        assert_equal(self.DG.degree(),nx.degree(self.DG))
        assert_equal(self.G.degree(nbunch=[0,1]),nx.degree(self.G,nbunch=[0,1]))
        assert_equal(self.DG.degree(nbunch=[0,1]),nx.degree(self.DG,nbunch=[0,1]))
        assert_equal(self.G.degree(weight='weight'),nx.degree(self.G,weight='weight'))
        assert_equal(self.DG.degree(weight='weight'),nx.degree(self.DG,weight='weight'))
    def test_neighbors(self):
        assert_equal(self.G.neighbors(1),nx.neighbors(self.G,1))
        assert_equal(self.DG.neighbors(1),nx.neighbors(self.DG,1))
    def test_number_of_nodes(self):
        assert_equal(self.G.number_of_nodes(),nx.number_of_nodes(self.G))
        assert_equal(self.DG.number_of_nodes(),nx.number_of_nodes(self.DG))
    def test_number_of_edges(self):
        assert_equal(self.G.number_of_edges(),nx.number_of_edges(self.G))
        assert_equal(self.DG.number_of_edges(),nx.number_of_edges(self.DG))
    def test_is_directed(self):
        assert_equal(self.G.is_directed(),nx.is_directed(self.G))
        assert_equal(self.DG.is_directed(),nx.is_directed(self.DG))
    def test_subgraph(self):
        assert_equal(self.G.subgraph([0,1,2,4]).adj,nx.subgraph(self.G,[0,1,2,4]).adj)
        assert_equal(self.DG.subgraph([0,1,2,4]).adj,nx.subgraph(self.DG,[0,1,2,4]).adj)

    def test_create_empty_copy(self):
        G=nx.create_empty_copy(self.G, with_nodes=False)
        assert_equal(G.nodes(),[])
        assert_equal(G.graph,{})
        assert_equal(G.node,{})
        assert_equal(G.edge,{})
        G=nx.create_empty_copy(self.G)
        assert_equal(G.nodes(),self.G.nodes())
        assert_equal(G.graph,{})
        assert_equal(G.node,{}.fromkeys(self.G.nodes(),{}))
        assert_equal(G.edge,{}.fromkeys(self.G.nodes(),{}))

    def test_degree_histogram(self):
        assert_equal(nx.degree_histogram(self.G), [1,1,1,1,1])

    def test_density(self):
        assert_equal(nx.density(self.G), 0.5)
        assert_equal(nx.density(self.DG), 0.3)
        G=nx.Graph()
        G.add_node(1)
        assert_equal(nx.density(G), 0.0)

    def test_density_selfloop(self):
        G = nx.Graph()
        G.add_edge(1,1)
        assert_equal(nx.density(G), 0.0)
        G.add_edge(1,2)
        assert_equal(nx.density(G), 2.0)

    def test_freeze(self):
        G=nx.freeze(self.G)
        assert_equal(G.frozen,True)
        assert_raises(nx.NetworkXError, G.add_node, 1)
        assert_raises(nx.NetworkXError, G.add_nodes_from, [1])
        assert_raises(nx.NetworkXError, G.remove_node, 1)
        assert_raises(nx.NetworkXError, G.remove_nodes_from, [1])
        assert_raises(nx.NetworkXError, G.add_edge, 1,2)
        assert_raises(nx.NetworkXError, G.add_edges_from, [(1,2)])
        assert_raises(nx.NetworkXError, G.remove_edge, 1,2)
        assert_raises(nx.NetworkXError, G.remove_edges_from, [(1,2)])
        assert_raises(nx.NetworkXError, G.clear)

    def test_is_frozen(self):
        assert_equal(nx.is_frozen(self.G), False)
        G=nx.freeze(self.G)
        assert_equal(G.frozen, nx.is_frozen(self.G))
        assert_equal(G.frozen,True)

    def test_info(self):
        G=nx.path_graph(5)
        info=nx.info(G)
        expected_graph_info='\n'.join(['Name: path_graph(5)',
                                       'Type: Graph',
                                       'Number of nodes: 5',
                                       'Number of edges: 4',
                                       'Average degree:   1.6000'])
        assert_equal(info,expected_graph_info)

        info=nx.info(G,n=1)
        expected_node_info='\n'.join(
            ['Node 1 has the following properties:',
             'Degree: 2',
             'Neighbors: 0 2'])
        assert_equal(info,expected_node_info)

    def test_info_digraph(self):
        G=nx.DiGraph(name='path_graph(5)')
        G.add_path([0,1,2,3,4])
        info=nx.info(G)
        expected_graph_info='\n'.join(['Name: path_graph(5)',
                                       'Type: DiGraph',
                                       'Number of nodes: 5',
                                       'Number of edges: 4',
                                       'Average in degree:   0.8000',
                                       'Average out degree:   0.8000'])
        assert_equal(info,expected_graph_info)

        info=nx.info(G,n=1)
        expected_node_info='\n'.join(
            ['Node 1 has the following properties:',
             'Degree: 2',
             'Neighbors: 2'])
        assert_equal(info,expected_node_info)

        assert_raises(nx.NetworkXError,nx.info,G,n=-1)

    def test_neighbors(self):
        graph = nx.complete_graph(100)
        pop = random.sample(graph.nodes(), 1)
        nbors = list(nx.neighbors(graph, pop[0]))
        # should be all the other vertices in the graph
        assert_equal(len(nbors), len(graph) - 1)

        graph = nx.path_graph(100)
        node = random.sample(graph.nodes(), 1)[0]
        nbors = list(nx.neighbors(graph, node))
        # should be all the other vertices in the graph
        if node != 0 and node != 99:
            assert_equal(len(nbors), 2)
        else:
            assert_equal(len(nbors), 1)

        # create a star graph with 99 outer nodes
        graph = nx.star_graph(99)
        nbors = list(nx.neighbors(graph, 0))
        assert_equal(len(nbors), 99)

    def test_non_neighbors(self):
        graph = nx.complete_graph(100)
        pop = random.sample(graph.nodes(), 1)
        nbors = list(nx.non_neighbors(graph, pop[0]))
        # should be all the other vertices in the graph
        assert_equal(len(nbors), 0)

        graph = nx.path_graph(100)
        node = random.sample(graph.nodes(), 1)[0]
        nbors = list(nx.non_neighbors(graph, node))
        # should be all the other vertices in the graph
        if node != 0 and node != 99:
            assert_equal(len(nbors), 97)
        else:
            assert_equal(len(nbors), 98)

        # create a star graph with 99 outer nodes
        graph = nx.star_graph(99)
        nbors = list(nx.non_neighbors(graph, 0))
        assert_equal(len(nbors), 0)

        # disconnected graph
        graph = nx.Graph()
        graph.add_nodes_from(range(10))
        nbors = list(nx.non_neighbors(graph, 0))
        assert_equal(len(nbors), 9)

    def test_non_edges(self):
        # All possible edges exist
        graph = nx.complete_graph(5)
        nedges = list(nx.non_edges(graph))
        assert_equal(len(nedges), 0)

        graph = nx.path_graph(4)
        expected = [(0, 2), (0, 3), (1, 3)]
        nedges = list(nx.non_edges(graph))
        for (u, v) in expected:
            assert_true( (u, v) in nedges or (v, u) in nedges )

        graph = nx.star_graph(4)
        expected = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]
        nedges = list(nx.non_edges(graph))
        for (u, v) in expected:
            assert_true( (u, v) in nedges or (v, u) in nedges )

        # Directed graphs
        graph = nx.DiGraph()
        graph.add_edges_from([(0, 2), (2, 0), (2, 1)])
        expected = [(0, 1), (1, 0), (1, 2)]
        nedges = list(nx.non_edges(graph))
        for e in expected:
            assert_true(e in nedges)


class TestCommonNeighbors():
    def setUp(self):
        self.func = nx.common_neighbors
        def test_func(G, u, v, expected):
            result = sorted(self.func(G, u, v))
            assert_equal(result, expected)
        self.test = test_func

    def test_K5(self):
        G = nx.complete_graph(5)
        self.test(G, 0, 1, [2, 3, 4])

    def test_P3(self):
        G = nx.path_graph(3)
        self.test(G, 0, 2, [1])

    def test_S4(self):
        G = nx.star_graph(4)
        self.test(G, 1, 2, [0])

    @raises(nx.NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])
        self.func(G, 0, 2)

    def test_nonexistent_nodes(self):
        G = nx.complete_graph(5)
        assert_raises(nx.NetworkXError, nx.common_neighbors, G, 5, 4)
        assert_raises(nx.NetworkXError, nx.common_neighbors, G, 4, 5)
        assert_raises(nx.NetworkXError, nx.common_neighbors, G, 5, 6)

    def test_custom1(self):
        """Case of no common neighbors."""
        G = nx.Graph()
        G.add_nodes_from([0, 1])
        self.test(G, 0, 1, [])

    def test_custom2(self):
        """Case of equal nodes."""
        G = nx.complete_graph(4)
        self.test(G, 0, 0, [1, 2, 3])


def test_set_node_attributes():
    graphs = [nx.Graph(), nx.DiGraph(), nx.MultiGraph(), nx.MultiDiGraph()]
    for G in graphs:
        G = nx.path_graph(3, create_using=G)

        # Test single value
        attr = 'hello'
        vals = 100
        nx.set_node_attributes(G, attr, vals)
        assert_equal(G.node[0][attr], vals)
        assert_equal(G.node[1][attr], vals)
        assert_equal(G.node[2][attr], vals)

        # Test multiple values
        attr = 'hi'
        vals = dict(zip(sorted(G.nodes()), range(len(G))))
        nx.set_node_attributes(G, attr, vals)
        assert_equal(G.node[0][attr], 0)
        assert_equal(G.node[1][attr], 1)
        assert_equal(G.node[2][attr], 2)

def test_set_edge_attributes():
    graphs = [nx.Graph(), nx.DiGraph()]
    for G in graphs:
        G = nx.path_graph(3, create_using=G)

        # Test single value
        attr = 'hello'
        vals = 3
        nx.set_edge_attributes(G, attr, vals)
        assert_equal(G[0][1][attr], vals)
        assert_equal(G[1][2][attr], vals)

        # Test multiple values
        attr = 'hi'
        edges = [(0,1), (1,2)]
        vals = dict(zip(edges, range(len(edges))))
        nx.set_edge_attributes(G, attr, vals)
        assert_equal(G[0][1][attr], 0)
        assert_equal(G[1][2][attr], 1)

def test_set_edge_attributes_multi():
    graphs = [nx.MultiGraph(), nx.MultiDiGraph()]
    for G in graphs:
        G = nx.path_graph(3, create_using=G)

        # Test single value
        attr = 'hello'
        vals = 3
        nx.set_edge_attributes(G, attr, vals)
        assert_equal(G[0][1][0][attr], vals)
        assert_equal(G[1][2][0][attr], vals)

        # Test multiple values
        attr = 'hi'
        edges = [(0,1,0), (1,2,0)]
        vals = dict(zip(edges, range(len(edges))))
        nx.set_edge_attributes(G, attr, vals)
        assert_equal(G[0][1][0][attr], 0)
        assert_equal(G[1][2][0][attr], 1)

def test_get_node_attributes():
    graphs = [nx.Graph(), nx.DiGraph(), nx.MultiGraph(), nx.MultiDiGraph()]
    for G in graphs:
        G = nx.path_graph(3, create_using=G)
        attr = 'hello'
        vals = 100
        nx.set_node_attributes(G, attr, vals)
        attrs = nx.get_node_attributes(G, attr)
        assert_equal(attrs[0], vals)
        assert_equal(attrs[1], vals)
        assert_equal(attrs[2], vals)


def test_get_edge_attributes():
    graphs = [nx.Graph(), nx.DiGraph(), nx.MultiGraph(), nx.MultiDiGraph()]
    for G in graphs:
        G = nx.path_graph(3, create_using=G)
        attr = 'hello'
        vals = 100
        nx.set_edge_attributes(G, attr, vals)
        attrs = nx.get_edge_attributes(G, attr)

        assert_equal(len(attrs), 2)
        if G.is_multigraph():
            keys = [(0,1,0), (1,2,0)]
        else:
            keys = [(0,1), (1,2)]
        for key in keys:
            assert_equal(attrs[key], 100)
