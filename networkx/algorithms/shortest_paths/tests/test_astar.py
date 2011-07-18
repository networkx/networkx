#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from random import random, choice

class TestAStar:

    def setUp(self):
        self.XG=nx.DiGraph()
        self.XG.add_edges_from([('s','u',{'weight':10}),
                                ('s','x',{'weight':5}),
                                ('u','v',{'weight':1}),
                                ('u','x',{'weight':2}),
                                ('v','y',{'weight':1}),
                                ('x','u',{'weight':3}),
                                ('x','v',{'weight':5}),
                                ('x','y',{'weight':2}),
                                ('y','s',{'weight':7}),
                                ('y','v',{'weight':6})])

    def test_random_graph(self):        

        def dist(a, b):
            (x1, y1) = a
            (x2, y2) = b
            return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        G = nx.Graph()

        points = [(random(), random()) for _ in range(100)]

        # Build a path from points[0] to points[-1] to be sure it exists
        for p1, p2 in zip(points[:-1], points[1:]):
            G.add_edge(p1, p2, weight=dist(p1, p2))

        # Add other random edges
        for _ in range(100):
            p1, p2 = choice(points), choice(points)
            G.add_edge(p1, p2, weight=dist(p1, p2))

        path = nx.astar_path(G, points[0], points[-1], dist)
        assert path == nx.dijkstra_path(G, points[0], points[-1])

        
    def test_astar_directed(self):
        assert nx.astar_path(self.XG,'s','v')==['s', 'x', 'u', 'v']
        assert nx.astar_path_length(self.XG,'s','v')==9

    def test_astar_multigraph(self):
         G=nx.MultiDiGraph(self.XG)
         assert_raises((TypeError,nx.NetworkXError),
                      nx.astar_path, [G,'s','v'])
         assert_raises((TypeError,nx.NetworkXError),
                      nx.astar_path_length, [G,'s','v'])

    def test_astar_undirected(self):
        GG=self.XG.to_undirected()
        GG['y']['v']['weight'] = 2
        assert nx.astar_path(GG,'s','v')==['s', 'x', 'u', 'v']
        assert nx.astar_path_length(GG,'s','v')==8

    def test_astar_directed2(self):
        XG2=nx.DiGraph()
        XG2.add_edges_from([[1,4,{'weight':1}],
                            [4,5,{'weight':1}],
                            [5,6,{'weight':1}],
                            [6,3,{'weight':1}],
                            [1,3,{'weight':50}],
                            [1,2,{'weight':100}],
                            [2,3,{'weight':100}]])
        assert nx.astar_path(XG2,1,3)==[1, 4, 5, 6, 3]

    def test_astar_undirected2(self):
        XG3=nx.Graph()
        XG3.add_edges_from([ [0,1,{'weight':2}],
                             [1,2,{'weight':12}],
                             [2,3,{'weight':1}],
                             [3,4,{'weight':5}],
                             [4,5,{'weight':1}],
                             [5,0,{'weight':10}] ])
        assert nx.astar_path(XG3,0,3)==[0, 1, 2, 3]
        assert nx.astar_path_length(XG3,0,3)==15


    def test_astar_undirected3(self):
        XG4=nx.Graph()
        XG4.add_edges_from([ [0,1,{'weight':2}],
                             [1,2,{'weight':2}],
                             [2,3,{'weight':1}],
                             [3,4,{'weight':1}],
                             [4,5,{'weight':1}],
                             [5,6,{'weight':1}],
                             [6,7,{'weight':1}],
                             [7,0,{'weight':1}] ])
        assert nx.astar_path(XG4,0,2)==[0, 1, 2]
        assert nx.astar_path_length(XG4,0,2)==4


# >>> MXG4=NX.MultiGraph(XG4)
# >>> MXG4.add_edge(0,1,3)
# >>> NX.dijkstra_path(MXG4,0,2)
# [0, 1, 2]

    def test_astar_w1(self):
        G=nx.DiGraph() 
        G.add_edges_from([('s','u'), ('s','x'), ('u','v'), ('u','x'),
            ('v','y'), ('x','u'), ('x','w'), ('w', 'v'), ('x','y'),
            ('y','s'), ('y','v')])
        assert nx.astar_path(G,'s','v')==['s', 'u', 'v']
        assert nx.astar_path_length(G,'s','v')== 2

    def test_astar_nopath(self):
        G=self.XG
        assert_raises((TypeError,nx.NetworkXError),
                      nx.astar_path, [G,'s','moon'])
        

    def test_cycle(self):        
        C=nx.cycle_graph(7)
        assert nx.astar_path(C,0,3)==[0, 1, 2, 3]
        assert nx.dijkstra_path(C,0,4)==[0, 6, 5, 4]


    def test_orderable(self):
        class UnorderableClass: pass
        node_1 = UnorderableClass()
        node_2 = UnorderableClass()
        node_3 = UnorderableClass()
        node_4 = UnorderableClass()
        G = nx.Graph()
        G.add_edge(node_1, node_2)
        G.add_edge(node_1, node_3)
        G.add_edge(node_2, node_4)
        G.add_edge(node_3, node_4)
        path=nx.algorithms.shortest_paths.astar.astar_path(G, node_1, node_4) 

