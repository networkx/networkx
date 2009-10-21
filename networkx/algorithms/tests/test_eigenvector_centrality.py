#!/usr/bin/env python
from nose.tools import *
import networkx

class TestEigenvectorCentrality:

    def setUp(self):
        
        G=networkx.DiGraph()

        edges=[(0,1),(0,2),(1,3),(2,1),(2,4),(3,1),(3,4),(3,5),\
                   (4,5),(4,6),(4,7),(5,7),(6,0),(6,4),\
                   (6,7),(7,5),(7,6)]

        G.add_edges_from(edges,weight=1.0)
        self.G=G
        self.G.evc=[0.09539322, 0.07361262, 0.12340075,  0.15203039,
                    0.18124403, 0.05912812, 0.19307497,  0.12211591]

        H=networkx.DiGraph()
        H.add_edges_from(edges)
        self.H=H
        self.H.evc=[0.09539322, 0.07361262, 0.12340075,  0.15203039,
                    0.18124403, 0.05912812, 0.19307497,  0.12211591]

    def test_eigenvector_centrality_weighted(self):
        G=self.G
        p=networkx.eigenvector_centrality(G,tol=1.e-08)
        for (a,b) in zip(p.values(),self.G.evc):
            assert_almost_equal(a,b)

    def test_eigenvector_centrality_unweighted(self):
        G=self.H
        p=networkx.eigenvector_centrality(G,tol=1.e-08)
        for (a,b) in zip(p.values(),self.G.evc):
            assert_almost_equal(a,b)



