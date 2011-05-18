#!/usr/bin/env python
from nose.tools import *
import networkx as nx

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
        assert_equal(nx.shortest_path_length(self.cycle,0,3,weight=True),3)
        assert_equal(nx.shortest_path_length(self.grid,1,12,weight=True),5)
        assert_equal(nx.shortest_path_length(self.directed_cycle,0,4,weight=True),4)


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


