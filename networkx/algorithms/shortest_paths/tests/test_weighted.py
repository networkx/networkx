#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from random import random, choice

class TestWeightedPath:

    def setUp(self):
        from networkx import convert_node_labels_to_integers as cnlti
        self.grid=cnlti(nx.grid_2d_graph(4,4),first_label=1,ordering="sorted")
        self.cycle=nx.cycle_graph(7)
        self.directed_cycle=nx.cycle_graph(7,create_using=nx.DiGraph())
        self.XG=nx.DiGraph()
        self.XG.add_weighted_edges_from([('s','u',10) ,('s','x',5) ,
                                         ('u','v',1) ,('u','x',2) ,
                                         ('v','y',1) ,('x','u',3) ,
                                         ('x','v',5) ,('x','y',2) ,
                                         ('y','s',7) ,('y','v',6)])
        self.MXG=nx.MultiDiGraph(self.XG)
        self.MXG.add_edge('s','u',weight=15)
        self.XG2=nx.DiGraph()
        self.XG2.add_weighted_edges_from([[1,4,1],[4,5,1],
                                          [5,6,1],[6,3,1],
                                          [1,3,50],[1,2,100],[2,3,100]])

        self.XG3=nx.Graph()
        self.XG3.add_weighted_edges_from([ [0,1,2],[1,2,12],
                                           [2,3,1],[3,4,5],
                                           [4,5,1],[5,0,10] ])

        self.XG4=nx.Graph()
        self.XG4.add_weighted_edges_from([ [0,1,2],[1,2,2],
                                           [2,3,1],[3,4,1],
                                           [4,5,1],[5,6,1],
                                           [6,7,1],[7,0,1] ])
        self.MXG4=nx.MultiGraph(self.XG4)
        self.MXG4.add_edge(0,1,weight=3)
        self.G=nx.DiGraph()  # no weights
        self.G.add_edges_from([('s','u'), ('s','x'), 
                          ('u','v'), ('u','x'), 
                          ('v','y'), ('x','u'), 
                          ('x','v'), ('x','y'), 
                          ('y','s'), ('y','v')])

    def test_dijkstra(self):
        (D,P)= nx.single_source_dijkstra(self.XG,'s')
        assert_equal(P['v'], ['s', 'x', 'u', 'v'])
        assert_equal(D['v'],9)

        assert_equal(nx.single_source_dijkstra_path(self.XG,'s')['v'], 
                     ['s', 'x', 'u', 'v'])
        assert_equal(nx.single_source_dijkstra_path_length(self.XG,'s')['v'],9)
        
        assert_equal(nx.single_source_dijkstra(self.XG,'s')[1]['v'],
                     ['s', 'x', 'u', 'v'])

        assert_equal(nx.single_source_dijkstra_path(self.MXG,'s')['v'],
                     ['s', 'x', 'u', 'v'])

        GG=self.XG.to_undirected()
        (D,P)= nx.single_source_dijkstra(GG,'s')
        assert_equal(P['v'] , ['s', 'x', 'u', 'v'])
        assert_equal(D['v'],8)     # uses lower weight of 2 on u<->x edge
        assert_equal(nx.dijkstra_path(GG,'s','v'), ['s', 'x', 'u', 'v'])
        assert_equal(nx.dijkstra_path_length(GG,'s','v'),8)

        assert_equal(nx.dijkstra_path(self.XG2,1,3), [1, 4, 5, 6, 3])
        assert_equal(nx.dijkstra_path(self.XG3,0,3), [0, 1, 2, 3])
        assert_equal(nx.dijkstra_path_length(self.XG3,0,3),15)
        assert_equal(nx.dijkstra_path(self.XG4,0,2), [0, 1, 2])
        assert_equal(nx.dijkstra_path_length(self.XG4,0,2), 4)
        assert_equal(nx.dijkstra_path(self.MXG4,0,2), [0, 1, 2])

        assert_equal(nx.single_source_dijkstra(self.G,'s','v')[1]['v'],
                     ['s', 'u', 'v'])
        assert_equal(nx.single_source_dijkstra(self.G,'s')[1]['v'],
                     ['s', 'u', 'v'])

        assert_equal(nx.dijkstra_path(self.G,'s','v'), ['s', 'u', 'v'])
        assert_equal(nx.dijkstra_path_length(self.G,'s','v'), 2)

        # NetworkXError: node s not reachable from moon
        assert_raises(nx.NetworkXError,nx.dijkstra_path,self.G,'s','moon')
        assert_raises(nx.NetworkXError,nx.dijkstra_path_length,self.G,'s','moon')

        assert_equal(nx.dijkstra_path(self.cycle,0,3),[0, 1, 2, 3])
        assert_equal(nx.dijkstra_path(self.cycle,0,4), [0, 6, 5, 4])


    def test_bidirectional_dijkstra(self):
        assert_equal(nx.bidirectional_dijkstra(self.XG, 's', 'v'),
                     (9, ['s', 'x', 'u', 'v']))
        assert_equal(nx.bidirectional_dijkstra(self.G,'s','v'),
                     (2, ['s', 'x', 'v']))
        assert_equal(nx.bidirectional_dijkstra(self.cycle,0,3),
                     (3, [0, 1, 2, 3]))
        assert_equal(nx.bidirectional_dijkstra(self.cycle,0,4),
                     (3, [0, 6, 5, 4]))
        assert_equal(nx.bidirectional_dijkstra(self.XG3,0,3),
                     (15, [0, 1, 2, 3]))
        assert_equal(nx.bidirectional_dijkstra(self.XG4,0,2),
                     (4, [0, 1, 2]))

        # need more tests here
        assert_equal(nx.dijkstra_path(self.XG,'s','v'),
                     nx.single_source_dijkstra_path(self.XG,'s')['v'])

    def test_dijkstra_predecessor(self):
        G=nx.path_graph(4)
        assert_equal(nx.dijkstra_predecessor_and_distance(G,0),
                     ({0: [], 1: [0], 2: [1], 3: [2]}, {0: 0, 1: 1, 2: 2, 3: 3}))
        G=nx.grid_2d_graph(2,2)
        pred,dist=nx.dijkstra_predecessor_and_distance(G,(0,0))
        assert_equal(sorted(pred.items()),
                     [((0, 0), []), ((0, 1), [(0, 0)]), 
                      ((1, 0), [(0, 0)]), ((1, 1), [(0, 1), (1, 0)])])
        assert_equal(sorted(dist.items()),
                     [((0, 0), 0), ((0, 1), 1), ((1, 0), 1), ((1, 1), 2)])

        XG=nx.DiGraph()
        XG.add_weighted_edges_from([('s','u',10) ,('s','x',5) ,
                                    ('u','v',1) ,('u','x',2) ,
                                    ('v','y',1) ,('x','u',3) ,
                                    ('x','v',5) ,('x','y',2) ,
                                    ('y','s',7) ,('y','v',6)])
        (P,D)= nx.dijkstra_predecessor_and_distance(XG,'s')
        assert_equal(P['v'],['u'])
        assert_equal(D['v'],9)




