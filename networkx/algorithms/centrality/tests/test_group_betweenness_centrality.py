"""
    Tests for Group Betweenness Centrality
"""

from __future__ import division
from nose.tools import *
import networkx as nx


class TestGroupBetweennessCentrality:
    def test_group_betweenness_centrality_1(self):
        """Group betweenness centrality in P5 for single node group"""
        G = nx.path_graph(5)
        C = [1]
        b = nx.algorithms.centrality.group.group_betweenness_centrality(G, weight=None, normalized=False)
        b_answer = 3.0
        assert_equal(b, b_answer)
    def test_group_betweenness_centrality_2(self):
        """Group etweenness centrality in P5 for group with more than 1 node and normalized"""
        G = nx.path_graph(5)
        C = [1, 3]
        b = nx.algorithms.centrality.group.group_betweenness_centrality(G, weight=None, normalized=True)
        b_answer = 0.25
        assert_equal(b, b_answer)
