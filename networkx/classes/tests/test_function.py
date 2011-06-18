#!/usr/bin/env python
from nose.tools import *
import networkx

class TestFunction(object):
    def setUp(self):
        self.G=networkx.Graph({0:[1,2,3], 1:[1,2,0], 4:[]}, name='Test')
        self.Gdegree={0:3, 1:2, 2:2, 3:1, 4:0}
        self.Gnodes=list(range(5))
        self.Gedges=[(0,1),(0,2),(0,3),(1,0),(1,1),(1,2)]
        self.DG=networkx.DiGraph({0:[1,2,3], 1:[1,2,0], 4:[]})
        self.DGin_degree={0:1, 1:2, 2:2, 3:1, 4:0}
        self.DGout_degree={0:3, 1:3, 2:0, 3:0, 4:0}
        self.DGnodes=list(range(5))
        self.DGedges=[(0,1),(0,2),(0,3),(1,0),(1,1),(1,2)]

    def test_nodes(self):
        assert_equal(self.G.nodes(),networkx.nodes(self.G))
        assert_equal(self.DG.nodes(),networkx.nodes(self.DG))
    def test_edges(self):
        assert_equal(self.G.edges(),networkx.edges(self.G))
        assert_equal(self.DG.edges(),networkx.edges(self.DG))
        assert_equal(self.G.edges(nbunch=[0,1,3]),networkx.edges(self.G,nbunch=[0,1,3]))
        assert_equal(self.DG.edges(nbunch=[0,1,3]),networkx.edges(self.DG,nbunch=[0,1,3]))
    def test_nodes_iter(self):
        assert_equal(list(self.G.nodes_iter()),list(networkx.nodes_iter(self.G)))
        assert_equal(list(self.DG.nodes_iter()),list(networkx.nodes_iter(self.DG)))
    def test_edges_iter(self):
        assert_equal(list(self.G.edges_iter()),list(networkx.edges_iter(self.G)))
        assert_equal(list(self.DG.edges_iter()),list(networkx.edges_iter(self.DG)))
        assert_equal(list(self.G.edges_iter(nbunch=[0,1,3])),list(networkx.edges_iter(self.G,nbunch=[0,1,3])))
        assert_equal(list(self.DG.edges_iter(nbunch=[0,1,3])),list(networkx.edges_iter(self.DG,nbunch=[0,1,3])))
    def test_degree(self):
        assert_equal(self.G.degree(),networkx.degree(self.G))
        assert_equal(self.DG.degree(),networkx.degree(self.DG))
        assert_equal(self.G.degree(nbunch=[0,1]),networkx.degree(self.G,nbunch=[0,1]))
        assert_equal(self.DG.degree(nbunch=[0,1]),networkx.degree(self.DG,nbunch=[0,1]))
        assert_equal(self.G.degree(weight='weight'),networkx.degree(self.G,weight='weight'))
        assert_equal(self.DG.degree(weight='weight'),networkx.degree(self.DG,weight='weight'))
    def test_neighbors(self):
        assert_equal(self.G.neighbors(1),networkx.neighbors(self.G,1))
        assert_equal(self.DG.neighbors(1),networkx.neighbors(self.DG,1))
    def test_number_of_nodes(self):
        assert_equal(self.G.number_of_nodes(),networkx.number_of_nodes(self.G))
        assert_equal(self.DG.number_of_nodes(),networkx.number_of_nodes(self.DG))
    def test_number_of_edges(self):
        assert_equal(self.G.number_of_edges(),networkx.number_of_edges(self.G))
        assert_equal(self.DG.number_of_edges(),networkx.number_of_edges(self.DG))
    def test_is_directed(self):
        assert_equal(self.G.is_directed(),networkx.is_directed(self.G))
        assert_equal(self.DG.is_directed(),networkx.is_directed(self.DG))
    def test_subgraph(self):
        assert_equal(self.G.subgraph([0,1,2,4]).adj,networkx.subgraph(self.G,[0,1,2,4]).adj)
        assert_equal(self.DG.subgraph([0,1,2,4]).adj,networkx.subgraph(self.DG,[0,1,2,4]).adj)

    def test_create_empty_copy(self):
        G=networkx.create_empty_copy(self.G, with_nodes=False)
        assert_equal(G.nodes(),[])
        assert_equal(G.graph,{})
        assert_equal(G.node,{})
        assert_equal(G.edge,{})
        G=networkx.create_empty_copy(self.G)
        assert_equal(G.nodes(),self.G.nodes())
        assert_equal(G.graph,{})
        assert_equal(G.node,{}.fromkeys(self.G.nodes(),{}))
        assert_equal(G.edge,{}.fromkeys(self.G.nodes(),{}))

    def test_degree_histogram(self):
        assert_equal(networkx.degree_histogram(self.G), [1,1,1,1,1])
    def test_density(self):
        assert_equal(networkx.density(self.G), 0.5)
        assert_equal(networkx.density(self.DG), 0.3)
    def test_freeze(self):
        G=networkx.freeze(self.G)
        assert_equal(G.frozen,True)
        assert_raises(networkx.NetworkXError, G.add_node, 1)
        assert_raises(networkx.NetworkXError, G.add_nodes_from, [1])
        assert_raises(networkx.NetworkXError, G.remove_node, 1)
        assert_raises(networkx.NetworkXError, G.remove_nodes_from, [1])
        assert_raises(networkx.NetworkXError, G.add_edge, 1,2)
        assert_raises(networkx.NetworkXError, G.add_edges_from, [(1,2)])
        assert_raises(networkx.NetworkXError, G.remove_edge, 1,2)
        assert_raises(networkx.NetworkXError, G.remove_edges_from, [(1,2)])
        assert_raises(networkx.NetworkXError, G.clear)

    def test_is_frozen(self):
        assert_equal(networkx.is_frozen(self.G), False)
        G=networkx.freeze(self.G)
        assert_equal(G.frozen, networkx.is_frozen(self.G))
        assert_equal(G.frozen,True)

    def test_info(self):
        G=networkx.path_graph(5)
        info=networkx.info(G)
        expected_graph_info='\n'.join(['Name: path_graph(5)',
                                       'Type: Graph',
                                       'Number of nodes: 5',
                                       'Number of edges: 4',
                                       'Average degree:   1.6000'])
        assert_equal(info,expected_graph_info)

        info=networkx.info(G,n=1)
        expected_node_info='\n'.join(
            ['Node 1 has the following properties:',
             'Degree: 2',
             'Neighbors: 0 2'])
        assert_equal(info,expected_node_info)

    def test_info_digraph(self):
        G=networkx.DiGraph(name='path_graph(5)')
        G.add_path([0,1,2,3,4])
        info=networkx.info(G)
        expected_graph_info='\n'.join(['Name: path_graph(5)',
                                       'Type: DiGraph',
                                       'Number of nodes: 5',
                                       'Number of edges: 4',
                                       'Average in degree:   0.8000',
                                       'Average out degree:   0.8000'])
        assert_equal(info,expected_graph_info)

        info=networkx.info(G,n=1)
        expected_node_info='\n'.join(
            ['Node 1 has the following properties:',
             'Degree: 2',
             'Neighbors: 2'])
        assert_equal(info,expected_node_info)
