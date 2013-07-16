#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
from nose.plugins.attrib import attr
import networkx

class TestPWP:

    def setup(self):
        G = networkx.DiGraph()
        edges=[(0,5),(1,0),(3,0),\
            (1,2),(1,9),(3,1),(2,9),\
            (2,3),(3,5),(4,3),(6,3),\
            (6,5),(6,7),(6,8),(7,9)]
        G.add_edges_from(edges)
        self.G=G
        self.G.pwp_inf = dict(zip(G,[0.036591667810678942,\
            0.19015631678285358, 0.15818225978149383, 0.20722606653528863,\
            0.1215905919708149, 0.0, 0.24966142930819119, 0.036591667810678942, 0.0, 0.0]))
        self.G.pwp_dep = dict(zip(G,[0.17525200953392886,\
            0.10007814371008028, 0.075173865823848579, 0.1391219798265681,\
            0.0, 0.24119065373913912, 0.0, 0.036591667810678942, 0.036591667810678942,\
            0.19600001174507722]))

    def test_pwp(self):
        G=self.G
        inf,dep = networkx.pwp(G,1)
        for n in G:
            assert_almost_equal(inf[n],G.pwp_inf[n],places=4)
            assert_almost_equal(dep[n],G.pwp_dep[n],places=4)
