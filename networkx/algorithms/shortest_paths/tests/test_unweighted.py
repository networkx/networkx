#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from random import random, choice

class TestUnweightedPath:

    def setUp(self):
        from networkx import convert_node_labels_to_integers as cnlti
        self.grid=cnlti(nx.grid_2d_graph(4,4),first_label=1,ordering="sorted")
        self.cycle=nx.cycle_graph(7)
        self.directed_cycle=nx.cycle_graph(7,create_using=nx.DiGraph())


    def test_bidirectional_shortest_path(self):
        assert_equal(nx.bidirectional_shortest_path(self.cycle,0,3),
                     [0, 1, 2, 3])
        assert_equal(nx.bidirectional_shortest_path(self.cycle,0,4),
                     [0, 6, 5, 4])
        assert_equal(nx.bidirectional_shortest_path(self.grid,1,12),
                     [1, 2, 3, 4, 8, 12])
        assert_equal(nx.bidirectional_shortest_path(self.directed_cycle,0,3),
                     [0, 1, 2, 3])

    def test_shortest_path_length(self):
        assert_equal(nx.shortest_path_length(self.cycle,0,3),3)
        assert_equal(nx.shortest_path_length(self.grid,1,12),5)
        assert_equal(nx.shortest_path_length(self.directed_cycle,0,4),4)
        # now with weights
        assert_equal(nx.shortest_path_length(self.cycle,0,3,weighted=True),3)
        assert_equal(nx.shortest_path_length(self.grid,1,12,weighted=True),5)
        assert_equal(nx.shortest_path_length(self.directed_cycle,0,4,weighted=True),4)


    def test_single_source_shortest_path(self):
        p=nx.single_source_shortest_path(self.cycle,0)
        assert_equal(p[3],[0,1,2,3])

    def test_single_source_shortest_path_length(self):
        assert_equal(nx.single_source_shortest_path_length(self.cycle,0),
                     {0:0,1:1,2:2,3:3,4:3,5:2,6:1})

    def test_all_pairs_shortest_path(self):
        p=nx.all_pairs_shortest_path(self.cycle)
        assert_equal(p[0][3],[0,1,2,3])
        p=nx.all_pairs_shortest_path(self.grid)
        assert_equal(p[1][12],[1, 2, 3, 4, 8, 12])

    def test_all_pairs_shortest_path_length(self):
        l=nx.all_pairs_shortest_path_length(self.cycle)
        assert_equal(l[0],{0:0,1:1,2:2,3:3,4:3,5:2,6:1})
        l=nx.all_pairs_shortest_path_length(self.grid)
        assert_equal(l[1][16],6)

    def test_predecessor(self):
        G=nx.path_graph(4)
        assert_equal(nx.predecessor(G,0),{0: [], 1: [0], 2: [1], 3: [2]})
        assert_equal(nx.predecessor(G,0,3),[2])
        G=nx.grid_2d_graph(2,2)
        assert_equal(sorted(nx.predecessor(G,(0,0)).items()),
                     [((0, 0), []), ((0, 1), [(0, 0)]), 
                      ((1, 0), [(0, 0)]), ((1, 1), [(0, 1), (1, 0)])])


    def test_floyd_warshall(self):
        XG=nx.DiGraph()
        XG.add_weighted_edges_from([('s','u',10) ,('s','x',5) ,
                                    ('u','v',1) ,('u','x',2) ,
                                    ('v','y',1) ,('x','u',3) ,
                                    ('x','v',5) ,('x','y',2) ,
                                    ('y','s',7) ,('y','v',6)])
        dist, path =nx.floyd_warshall(XG)
        assert_equal(dist['s']['v'],9)
        assert_equal(path['s']['v'],'u')
        assert_equal(dist,
                     {'y': {'y': 0, 'x': 12, 's': 7, 'u': 15, 'v': 6}, 
                      'x': {'y': 2, 'x': 0, 's': 9, 'u': 3, 'v': 4}, 
                      's': {'y': 7, 'x': 5, 's': 0, 'u': 8, 'v': 9}, 
                      'u': {'y': 2, 'x': 2, 's': 9, 'u': 0, 'v': 1}, 
                      'v': {'y': 1, 'x': 13, 's': 8, 'u': 16, 'v': 0}})


        GG=XG.to_undirected()
        dist, path = nx.floyd_warshall(GG)
        assert_equal(dist['s']['v'],8)
        assert_equal(path['s']['v'],'y')

        G=nx.DiGraph()  # no weights
        G.add_edges_from([('s','u'), ('s','x'), 
                          ('u','v'), ('u','x'), 
                          ('v','y'), ('x','u'), 
                          ('x','v'), ('x','y'), 
                          ('y','s'), ('y','v')])
        dist, path = nx.floyd_warshall(G)
        assert_equal(dist['s']['v'],2)
        assert_equal(path['s']['v'],'x')


        dist, path = nx.floyd_warshall(self.cycle)
        assert_equal(dist[0][3],3)
        assert_equal(path[0][3],2)
        assert_equal(dist[0][4],3)

        XG3=nx.Graph()
        XG3.add_weighted_edges_from([ [0,1,2],[1,2,12],[2,3,1],
                                      [3,4,5],[4,5,1],[5,0,10] ])
        dist, path = nx.floyd_warshall(XG3)
        assert_equal(dist[0][3],15)
        assert_equal(path[0][3],2)

        XG4=nx.Graph()
        XG4.add_weighted_edges_from([ [0,1,2],[1,2,2],[2,3,1],
                                      [3,4,1],[4,5,1],[5,6,1],
                                      [6,7,1],[7,0,1] ])
        dist, path = nx.floyd_warshall(XG4)
        assert_equal(dist[0][2],4)
        assert_equal(path[0][2],1)

