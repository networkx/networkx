#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
from nose.plugins.attrib import attr
import networkx

class TestHeatKernel:

    def setup(self):
        G = networkx.DiGraph()
        edges=[(0,5),(1,0),(3,0),\
            (1,2),(1,9),(3,1),(2,9),\
            (2,3),(3,5),(4,3),(6,3),\
            (6,5),(6,7),(6,8),(7,9)]
        G.add_edges_from(edges)
        self.G=G
        self.G.heatkernel_inf = dict(zip(G,[0.05357818,0.16600425,\
            0.14259576,0.17850117,0.11580666,0.02678909,0.20956849,\
            0.05357818,0.02678909,0.02678909]))
        self.G.heatkernel_dep = dict(zip(G,[0.15509267,0.10005720,\
            0.08182456,0.12864155,0.02678909,0.20336695,0.02678909,\
            0.05357818,0.05357818,0.17028248]))

    def test_heatkernel(self):
        G=self.G
        inf,dep = networkx.heatkernel(G,1)
        for n in G:
            assert_almost_equal(inf[n],G.heatkernel_inf[n],places=4)
            assert_almost_equal(dep[n],G.heatkernel_dep[n],places=4)
