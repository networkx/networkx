#!/usr/bin/env python
from nose.tools import *
import networkx

class TestDistance:

    def setUp(self):
        G=networkx.Graph() 
        from networkx import convert_node_labels_to_integers as cnlti
        G=cnlti(networkx.grid_2d_graph(4,4),first_label=1,ordering="sorted")
        self.G=G

    def test_eccentricity(self):
        assert_equal(networkx.eccentricity(self.G,1),6)
        e=networkx.eccentricity(self.G)
        assert_equal(e[1],6) 
        
    def test_diameter(self):
        assert_equal(networkx.diameter(self.G),6)

    def test_radius(self):
        assert_equal(networkx.radius(self.G),4)

    def test_periphery(self):
        assert_equal(set(networkx.periphery(self.G)),set([1, 4, 13, 16]))

    def test_center(self):
        assert_equal(set(networkx.center(self.G)),set([6, 7, 10, 11]))

    def test_radius_exception(self):
        G=networkx.Graph()
        G.add_edge(1,2)
        G.add_edge(3,4)
        assert_raises(networkx.NetworkXError, networkx.diameter, G)

    def test_eccentricity_exception(self):
        G=networkx.Graph()
        G.add_edge(1,2)
        G.add_edge(3,4)
        assert_raises(networkx.NetworkXError, networkx.eccentricity, G)

