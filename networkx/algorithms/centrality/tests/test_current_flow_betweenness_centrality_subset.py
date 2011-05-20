#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
import networkx

from networkx import edge_current_flow_betweenness_centrality \
    as edge_current_flow

from networkx import edge_current_flow_betweenness_centrality_subset \
    as edge_current_flow_subset

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
        b=networkx.current_flow_betweenness_centrality_subset(G,
                                                              G.nodes(),
                                                              G.nodes(),
                                                              normalized=True)
        b_answer=networkx.current_flow_betweenness_centrality(G,normalized=True)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])


    def test_K4(self):
        """Betweenness centrality: K4"""
        G=networkx.complete_graph(4)
        b=networkx.current_flow_betweenness_centrality_subset(G,
                                                              G.nodes(),
                                                              G.nodes(),
                                                              normalized=True)
        b_answer=networkx.current_flow_betweenness_centrality(G,normalized=True)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])
        # test weighted network
        G.add_edge(0,1,{'weight':0.5,'other':0.3})
        b=networkx.current_flow_betweenness_centrality_subset(G,
                                                              G.nodes(),
                                                              G.nodes(),
                                                              normalized=True,
                                                              weight=None)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])
        b=networkx.current_flow_betweenness_centrality_subset(G,
                                                              G.nodes(),
                                                              G.nodes(),
                                                              normalized=True)
        b_answer=networkx.current_flow_betweenness_centrality(G,normalized=True)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])
        b=networkx.current_flow_betweenness_centrality_subset(G,
                                                              G.nodes(),
                                                              G.nodes(),
                                                              normalized=True,
                                                              weight='other')
        b_answer=networkx.current_flow_betweenness_centrality(G,normalized=True,weight='other')
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])


    def test_P4_normalized(self):
        """Betweenness centrality: P4 normalized"""
        G=networkx.path_graph(4)
        b=networkx.current_flow_betweenness_centrality_subset(G,
                                                              G.nodes(),
                                                              G.nodes(),
                                                              normalized=True)
        b_answer=networkx.current_flow_betweenness_centrality(G,normalized=True)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])


    def test_P4(self):
        """Betweenness centrality: P4"""
        G=networkx.path_graph(4)
        b=networkx.current_flow_betweenness_centrality_subset(G,
                                                              G.nodes(),
                                                              G.nodes(),
                                                              normalized=True)
        b_answer=networkx.current_flow_betweenness_centrality(G,normalized=True)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])

    def test_star(self):
        """Betweenness centrality: star """
        G=networkx.Graph()
        G.add_star(['a','b','c','d'])
        b=networkx.current_flow_betweenness_centrality_subset(G,
                                                              G.nodes(),
                                                              G.nodes(),
                                                              normalized=True)
        b_answer=networkx.current_flow_betweenness_centrality(G,normalized=True)
        for n in sorted(G):
            assert_almost_equal(b[n],b_answer[n])



# class TestWeightedFlowBetweennessCentrality():
#     pass


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
        b=edge_current_flow_subset(G,G.nodes(),G.nodes(),normalized=True)
        b_answer=edge_current_flow(G,normalized=True)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])

    def test_K4(self):
        """Betweenness centrality: K4"""
        G=networkx.complete_graph(4)
        b=edge_current_flow_subset(G,G.nodes(),G.nodes(),normalized=False)
        b_answer=edge_current_flow(G,normalized=False)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])
        # test weighted network
        G.add_edge(0,1,{'weight':0.5,'other':0.3})
        b=edge_current_flow_subset(G,G.nodes(),G.nodes(),normalized=False,weight=None)
        # weight is None => same as unweighted network
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])
        b=edge_current_flow_subset(G,G.nodes(),G.nodes(),normalized=False)
        b_answer=edge_current_flow(G,normalized=False)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])
        b=edge_current_flow_subset(G,G.nodes(),G.nodes(),normalized=False,weight='other')
        b_answer=edge_current_flow(G,normalized=False,weight='other')
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])

    def test_C4(self):
        """Edge betweenness centrality: C4"""
        G=networkx.cycle_graph(4)
        b=edge_current_flow_subset(G,G.nodes(),G.nodes(),normalized=True)
        b_answer=edge_current_flow(G,normalized=True)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])


    def test_P4(self):
        """Edge betweenness centrality: P4"""
        G=networkx.path_graph(4)
        b=edge_current_flow_subset(G,G.nodes(),G.nodes(),normalized=True)
        b_answer=edge_current_flow(G,normalized=True)
        for n in sorted(G.edges()):
            assert_almost_equal(b[n],b_answer[n])

