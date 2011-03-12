#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestBipartiteProject:


    def test_path_projected_graph(self):
        G=nx.path_graph(4)
        P=nx.projected_graph(G,[1,3]) 
        assert_equal(sorted(P.nodes()),[1,3])
        assert_equal(sorted(P.edges()),[(1,3)])
        P=nx.projected_graph(G,[0,2]) 
        assert_equal(sorted(P.nodes()),[0,2])
        assert_equal(sorted(P.edges()),[(0,2)])

    def test_path_projected_properties_graph(self):
        G=nx.path_graph(4)
        G.add_node(1,name='one')
        G.add_node(2,name='two')
        P=nx.projected_graph(G,[1,3]) 
        assert_equal(sorted(P.nodes()),[1,3])
        assert_equal(sorted(P.edges()),[(1,3)])
        assert_equal(P.node[1]['name'],G.node[1]['name'])
        P=nx.projected_graph(G,[0,2]) 
        assert_equal(sorted(P.nodes()),[0,2])
        assert_equal(sorted(P.edges()),[(0,2)])
        assert_equal(P.node[2]['name'],G.node[2]['name'])


    def test_path_weighted_projected_graph(self):
        G=nx.path_graph(4)
        P=nx.weighted_projected_graph(G,[1,3]) 
        assert_equal(sorted(P.nodes()),[1,3])
        assert_equal(sorted(P.edges()),[(1,3)])
        P[1][3]['weight']=1
        P=nx.weighted_projected_graph(G,[0,2]) 
        assert_equal(sorted(P.nodes()),[0,2])
        assert_equal(sorted(P.edges()),[(0,2)])
        P[0][2]['weight']=1

    def test_path_collaboration_projected_graph(self):
        G=nx.path_graph(4)
        P=nx.weighted_projected_graph(G,[1,3],collaboration=True) 
        assert_equal(sorted(P.nodes()),[1,3])
        assert_equal(sorted(P.edges()),[(1,3)])
        P[1][3]['weight']=1
        P=nx.weighted_projected_graph(G,[0,2],collaboration=True) 
        assert_equal(sorted(P.nodes()),[0,2])
        assert_equal(sorted(P.edges()),[(0,2)])
        P[0][2]['weight']=1

    def test_star_projected_graph(self):
        G=nx.star_graph(3)
        P=nx.projected_graph(G,[1,2,3])
        assert_equal(sorted(P.nodes()),[1,2,3])
        assert_equal(sorted(P.edges()),[(1,2),(1,3),(2,3)])
        P=nx.weighted_projected_graph(G,[1,2,3])
        assert_equal(sorted(P.nodes()),[1,2,3])
        assert_equal(sorted(P.edges()),[(1,2),(1,3),(2,3)])

        P=nx.projected_graph(G,[0])
        assert_equal(sorted(P.nodes()),[0])
        assert_equal(sorted(P.edges()),[])

    def test_project_multigraph(self):
        G=nx.Graph()
        G.add_edge('a',1)
        G.add_edge('b',1)
        G.add_edge('a',2)
        G.add_edge('b',2)
        P=nx.projected_graph(G,'ab')
        assert_equal(sorted(P.edges()),[('a','b')])
        P=nx.weighted_projected_graph(G,'ab')
        assert_equal(sorted(P.edges()),[('a','b')])
        P=nx.projected_graph(G,'ab',multigraph=True)
        assert_equal(sorted(P.edges()),[('a','b'),('a','b')])
        
    def test_project_collaboration(self):
        G=nx.Graph()
        G.add_edge('a',1)
        G.add_edge('b',1)
        G.add_edge('b',2)
        G.add_edge('c',2)
        G.add_edge('c',3)
        G.add_edge('c',4)
        G.add_edge('b',4)
        P=nx.weighted_projected_graph(G,'abc',collaboration=True)
        assert_equal(P['a']['b']['weight'],1)
        assert_equal(P['b']['c']['weight'],2)

    def test_directed_projection(self):
        G=nx.DiGraph()
        G.add_edge('A',1)
        G.add_edge(1,'B')
        G.add_edge('A',2)
        G.add_edge('B',2)
        P=nx.projected_graph(G,'AB')
        assert_equal(sorted(P.edges()),[('A','B')])
        P=nx.weighted_projected_graph(G,'AB')
        assert_equal(sorted(P.edges()),[('A','B')])
        assert_equal(P['A']['B']['weight'],1)

        P=nx.projected_graph(G,'AB',multigraph=True)
        assert_equal(sorted(P.edges()),[('A','B')])

        G=nx.DiGraph()
        G.add_edge('A',1)
        G.add_edge(1,'B')
        G.add_edge('A',2)
        G.add_edge(2,'B')
        P=nx.projected_graph(G,'AB')
        assert_equal(sorted(P.edges()),[('A','B')])
        P=nx.weighted_projected_graph(G,'AB')
        assert_equal(sorted(P.edges()),[('A','B')])
        assert_equal(P['A']['B']['weight'],2)

        P=nx.projected_graph(G,'AB',multigraph=True)
        assert_equal(sorted(P.edges()),[('A','B'),('A','B')])

    def test_project_weighted(self):
        # Tore Opsahl's example
        # http://toreopsahl.com/2009/05/01/projecting-two-mode-networks-onto-weighted-one-mode-networks/
        G=nx.Graph()
        G.add_edge('A',1)
        G.add_edge('A',2)
        G.add_edge('B',1)
        G.add_edge('B',2)
        G.add_edge('B',3)
        G.add_edge('B',4)
        G.add_edge('B',5)
        G.add_edge('C',1)
        G.add_edge('D',3)
        G.add_edge('E',4)
        G.add_edge('E',5)
        G.add_edge('E',6)
        G.add_edge('F',6)

        edges=[('A','B',2),
               ('A','C',1),
               ('B','C',1),
               ('B','D',1),
               ('B','E',2),
               ('E','F',1)]
        Panswer=nx.Graph()
        Panswer.add_weighted_edges_from(edges)

        # binary projected
        P=nx.projected_graph(G,'ABCDEF')
        assert_equal(P.edges(),Panswer.edges())

        # weighted projected
        P=nx.weighted_projected_graph(G,'ABCDEF')
        assert_equal(P.edges(),Panswer.edges())
        for u,v in P.edges():
            assert_equal(P[u][v]['weight'],Panswer[u][v]['weight'])
        

        edges=[('A','B',1.5),
               ('A','C',0.5),
               ('B','C',0.5),
               ('B','D',1),
               ('B','E',2),
               ('E','F',1)]
        Panswer=nx.Graph()
        Panswer.add_weighted_edges_from(edges)

        # collaboration projected
        P=nx.weighted_projected_graph(G,'ABCDEF',collaboration=True)
        assert_equal(P.edges(),Panswer.edges())
        for u,v in P.edges():
            assert_equal(P[u][v]['weight'],Panswer[u][v]['weight'])

            
