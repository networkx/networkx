#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
from nose.plugins.attrib import attr
import networkx

class TestMICMAC:

    def setup(self):
        G = networkx.DiGraph()
        edges=[(0,5),(1,0),(3,0),\
            (1,2),(1,9),(3,1),(2,9),\
            (2,3),(3,5),(4,3),(6,3),\
            (6,5),(6,7),(6,8),(7,9)]
        G.add_edges_from(edges)
        self.G=G
        self.G.micmac_inf = dict(zip(G,[0.0,0.25,0.1875,0.1875,0.1875,0.0,0.1875,0.0,0.0,0.0]))
        self.G.micmac_dep = dict(zip(G,[0.125,0.0625,0.0625,0.1875,0.0,0.3125,0.0,0.0,0.0,0.25]))

    def test_micmac(self):
        G=self.G
        T = networkx.micmac(G,4)
        inf = T['influences']
        dep = T['dependences']
        for n in G:
            assert_almost_equal(inf[n],G.micmac_inf[n],places=4)
            assert_almost_equal(dep[n],G.micmac_dep[n],places=4)
