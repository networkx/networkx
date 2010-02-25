#!/usr/bin/env python
from nose.tools import *
import networkx

class TestCycles:
    def setUp(self):
        G=networkx.Graph() 
        G.add_cycle([0,1,2,3])
        G.add_cycle([0,3,4,5])
        G.add_cycle([0,1,6,7,8])
        self.G=G

    def test_cycle_basis(self):
        G=self.G
        cy=networkx.cycle_basis(G,0)
        sort_cy= sorted( sorted(c) for c in cy )
        assert_equal(sort_cy, [[0,1,2,3],[0,1,6,7,8],[0,3,4,5]])
        cy=networkx.cycle_basis(G)
        sort_cy= sorted( sorted(c) for c in cy )
        assert_equal(sort_cy, [[0,1,2,3],[0,1,6,7,8],[0,3,4,5]])



