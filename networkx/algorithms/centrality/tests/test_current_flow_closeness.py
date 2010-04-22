#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
import networkx

class TestFlowClosenessCentrality(object):
    @classmethod
    def setupClass(cls):
        global np
        try:
            import numpy as np
        except ImportError:
            raise SkipTest('NumPy not available.')
        
        
    def test_K4(self):
        """Closeness centrality: K4"""
        G=networkx.complete_graph(4)
        b=networkx.current_flow_closeness_centrality(G,normalized=True)
        b_answer={0: 2.0, 1: 2.0, 2: 2.0, 3: 2.0}
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])


    def test_P4_normalized(self):
        """Closeness centrality: P4 normalized"""
        G=networkx.path_graph(4)
        b=networkx.current_flow_closeness_centrality(G,normalized=True)
        b_answer={0: 1./2, 1: 3./4, 2: 3./4, 3:1./2}
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])


    def test_P4(self):
        """Closeness centrality: P4"""
        G=networkx.path_graph(4)
        b=networkx.current_flow_closeness_centrality(G,normalized=False)
        b_answer={0: 1.0/6, 1: 1.0/4, 2: 1.0/4, 3:1.0/6}
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])

    def test_star(self):
        """Closeness centrality: star """
        G=networkx.Graph()
        G.add_star(['a','b','c','d'])
        b=networkx.current_flow_closeness_centrality(G,normalized=True)
        b_answer={'a': 1.0, 'b': 0.6, 'c': 0.6, 'd':0.6}
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])



class TestWeightedFlowClosenessCentrality(object):
    pass
