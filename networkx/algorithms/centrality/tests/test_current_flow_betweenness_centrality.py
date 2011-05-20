#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
import networkx

from networkx import edge_current_flow_betweenness_centrality \
    as edge_current_flow

class TestFlowBetweennessCentrality(object):
    @classmethod
    def setupClass(cls):
        global np
        try:
            import numpy as np
        except ImportError:
            raise SkipTest('NumPy not available.')
        
    def test_K4_normalized(self):
        """Betweenness centrality: K4"""
        G=networkx.complete_graph(4)
        b=networkx.current_flow_betweenness_centrality(G,normalized=True)
        b_answer={0: 0.25, 1: 0.25, 2: 0.25, 3: 0.25}
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])
        G.add_edge(0,1,{'weight':0.5,'other':0.3})
        b=networkx.current_flow_betweenness_centrality(G,normalized=True,weight=None)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])
        wb_answer={0: 0.2222222, 1: 0.2222222, 2: 0.30555555, 3: 0.30555555}
        b=networkx.current_flow_betweenness_centrality(G,normalized=True)
        for n in sorted(G):
            assert_almost_equal(b[n],wb_answer[n])
        wb_answer={0: 0.2051282, 1: 0.2051282, 2: 0.33974358, 3: 0.33974358}
        b=networkx.current_flow_betweenness_centrality(G,normalized=True,weight='other')
        for n in sorted(G):
            assert_almost_equal(b[n],wb_answer[n])

    def test_K4(self):
        """Betweenness centrality: K4"""
        G=networkx.complete_graph(4)
        b=networkx.current_flow_betweenness_centrality(G,normalized=False)
        b_answer={0: 0.75, 1: 0.75, 2: 0.75, 3: 0.75}
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])


    def test_P4_normalized(self):
        """Betweenness centrality: P4 normalized"""
        G=networkx.path_graph(4)
        b=networkx.current_flow_betweenness_centrality(G,normalized=True)
        b_answer={0: 0, 1: 2./3, 2: 2./3, 3:0}
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])


    def test_P4(self):
        """Betweenness centrality: P4"""
        G=networkx.path_graph(4)
        b=networkx.current_flow_betweenness_centrality(G,normalized=False)
        b_answer={0: 0, 1: 2, 2: 2, 3: 0}
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])

    def test_star(self):
        """Betweenness centrality: star """
        G=networkx.Graph()
        G.add_star(['a','b','c','d'])
        b=networkx.current_flow_betweenness_centrality(G,normalized=True)
        b_answer={'a': 1.0, 'b': 0.0, 'c': 0.0, 'd':0.0}
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])



class TestWeightedFlowBetweennessCentrality(object):
    pass


class TestEdgeFlowBetweennessCentrality(object):
    @classmethod
    def setupClass(cls):
        global np
        try:
            import numpy as np
        except ImportError:
            raise SkipTest('NumPy not available.')

    def test_K4_normalized(self):
        """Betweenness centrality: K4"""
        G=networkx.complete_graph(4)
        b=edge_current_flow(G,normalized=True)
        b_answer=dict.fromkeys(G.edges(),0.25)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])

    def test_K4_normalized(self):
        """Betweenness centrality: K4"""
        G=networkx.complete_graph(4)
        b=edge_current_flow(G,normalized=False)
        b_answer=dict.fromkeys(G.edges(),0.75)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])

    def test_C4(self):
        """Edge betweenness centrality: C4"""
        G=networkx.cycle_graph(4)
        b=edge_current_flow(G,normalized=False)
        b_answer={(0, 1):1.25,(0, 3):1.25, (1, 2):1.25, (2, 3): 1.25}
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])


    def test_P4(self):
        """Edge betweenness centrality: P4"""
        G=networkx.path_graph(4)
        b=edge_current_flow(G,normalized=False)
        b_answer={(0, 1):1.5,(1, 2):2.0, (2, 3):1.5}
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])

