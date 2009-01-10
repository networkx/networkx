#!/usr/bin/env python
from nose.tools import *
import networkx

class TestMST:

    def setUp(self):
    # example from Wikipedia: http://en.wikipedia.org/wiki/Kruskal's_algorithm
        G=networkx.Graph() 
        edgelist = [(0,3,5),(0,1,7),(1,3,9),
                    (1,2,8),(1,4,7),(3,4,15),
                    (3,5,6),(2,4,5),(4,5,8),
                    (4,6,9),(5,6,11)]
        G.add_edges_from(edgelist)
        self.G=G
        tree_edgelist = ([(0,1,7),(0,3,5),(3,5,6),
                               (1,4,7),(4,2,5),(4,6,9)])
        self.tree_edgelist=sorted(tuple(sorted((u,v,d)))
                                  for u,v,d in tree_edgelist)

    def test_kruskal_mst(self):
        edgelist=sorted(networkx.kruskal_mst(self.G))
        assert_equal(edgelist,self.tree_edgelist)



