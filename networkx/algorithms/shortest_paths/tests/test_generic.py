#!/usr/bin/env python
from nose.tools import *
import networkx as nx

class TestGenericPath:

    def setUp(self):
        from networkx import convert_node_labels_to_integers as cnlti
        self.grid=cnlti(nx.grid_2d_graph(4,4),first_label=1,ordering="sorted")
        self.cycle=nx.cycle_graph(7)
        self.directed_cycle=nx.cycle_graph(7,create_using=nx.DiGraph())


    def test_shortest_path(self):
        assert_equal(nx.shortest_path(self.cycle,0,3),[0, 1, 2, 3])
        assert_equal(nx.shortest_path(self.cycle,0,4),[0, 6, 5, 4])
        assert_equal(nx.shortest_path(self.grid,1,12),[1, 2, 3, 4, 8, 12])
        assert_equal(nx.shortest_path(self.directed_cycle,0,3),[0, 1, 2, 3])
        # now with weights
        assert_equal(nx.shortest_path(self.cycle,0,3,weight='weight'),[0, 1, 2, 3])
        assert_equal(nx.shortest_path(self.cycle,0,4,weight='weight'),[0, 6, 5, 4])
        assert_equal(nx.shortest_path(self.grid,1,12,weight='weight'),[1, 2, 3, 4, 8, 12])
        assert_equal(nx.shortest_path(self.directed_cycle,0,3,weight='weight'),
                     [0, 1, 2, 3])


    def test_shortest_path_length(self):
        assert_equal(nx.shortest_path_length(self.cycle,0,3),3)
        assert_equal(nx.shortest_path_length(self.grid,1,12),5)
        assert_equal(nx.shortest_path_length(self.directed_cycle,0,4),4)
        # now with weights
        assert_equal(nx.shortest_path_length(self.cycle,0,3,weight='weight'),3)
        assert_equal(nx.shortest_path_length(self.grid,1,12,weight='weight'),5)
        assert_equal(nx.shortest_path_length(self.directed_cycle,0,4,weight='weight'),4)


    def test_single_source_shortest_path(self):
        p=nx.shortest_path(self.cycle,0)
        assert_equal(p[3],[0,1,2,3])
        assert_equal(p,nx.single_source_shortest_path(self.cycle,0))
        p=nx.shortest_path(self.grid,1)
        assert_equal(p[12],[1, 2, 3, 4, 8, 12])
        # now with weights
        p=nx.shortest_path(self.cycle,0,weight='weight')
        assert_equal(p[3],[0,1,2,3])
        assert_equal(p,nx.single_source_dijkstra_path(self.cycle,0))
        p=nx.shortest_path(self.grid,1,weight='weight')
        assert_equal(p[12],[1, 2, 3, 4, 8, 12])


    def test_single_source_shortest_path_length(self):
        l=nx.shortest_path_length(self.cycle,0)
        assert_equal(l,{0:0,1:1,2:2,3:3,4:3,5:2,6:1})
        assert_equal(l,nx.single_source_shortest_path_length(self.cycle,0))
        l=nx.shortest_path_length(self.grid,1)
        assert_equal(l[16],6)
        # now with weights
        l=nx.shortest_path_length(self.cycle,0,weight='weight')
        assert_equal(l,{0:0,1:1,2:2,3:3,4:3,5:2,6:1})
        assert_equal(l,nx.single_source_dijkstra_path_length(self.cycle,0))
        l=nx.shortest_path_length(self.grid,1,weight='weight')
        assert_equal(l[16],6)


    def test_all_pairs_shortest_path(self):
        p=nx.shortest_path(self.cycle)
        assert_equal(p[0][3],[0,1,2,3])
        assert_equal(p,nx.all_pairs_shortest_path(self.cycle))
        p=nx.shortest_path(self.grid)
        assert_equal(p[1][12],[1, 2, 3, 4, 8, 12])
        # now with weights
        p=nx.shortest_path(self.cycle,weight='weight')
        assert_equal(p[0][3],[0,1,2,3])
        assert_equal(p,nx.all_pairs_dijkstra_path(self.cycle))
        p=nx.shortest_path(self.grid,weight='weight')
        assert_equal(p[1][12],[1, 2, 3, 4, 8, 12])


    def test_all_pairs_shortest_path_length(self):
        l=nx.shortest_path_length(self.cycle)
        assert_equal(l[0],{0:0,1:1,2:2,3:3,4:3,5:2,6:1})
        assert_equal(l,nx.all_pairs_shortest_path_length(self.cycle))
        l=nx.shortest_path_length(self.grid)
        assert_equal(l[1][16],6)
        # now with weights
        l=nx.shortest_path_length(self.cycle,weight='weight')
        assert_equal(l[0],{0:0,1:1,2:2,3:3,4:3,5:2,6:1})
        assert_equal(l,nx.all_pairs_dijkstra_path_length(self.cycle))
        l=nx.shortest_path_length(self.grid,weight='weight')
        assert_equal(l[1][16],6)

    def test_average_shortest_path(self):
        l=nx.average_shortest_path_length(self.cycle)
        assert_almost_equal(l,2)
        l=nx.average_shortest_path_length(nx.path_graph(5))
        assert_almost_equal(l,2)

    def test_weighted_average_shortest_path(self):
        G=nx.Graph()
        G.add_cycle(range(7),weight=2)
        l=nx.average_shortest_path_length(G,weight='weight')
        assert_almost_equal(l,4)
        G=nx.Graph()
        G.add_path(range(5),weight=2)
        l=nx.average_shortest_path_length(G,weight='weight')
        assert_almost_equal(l,4)


    def test_average_shortest_disconnected(self):
        g = nx.Graph()
        g.add_nodes_from(range(3))
        g.add_edge(0, 1)
        assert_raises(nx.NetworkXError,nx.average_shortest_path_length,g)


    def test_has_path(self):
        G = nx.Graph()
        G.add_path(range(3))
        G.add_path(range(3,5))
        assert_true(nx.has_path(G,0,2))
        assert_false(nx.has_path(G,0,4))
