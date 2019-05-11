"""
    Tests for Group Betweenness Centrality
"""


from nose.tools import *
import networkx as nx


class TestGroupBetweennessCentrality:

    def test_group_betweenness_single_node(self):
        """
            Group betweenness centrality for single node group
        """
        G = nx.path_graph(5)
        C = [1]
        b = nx.group_betweenness_centrality(G, C,
                                            weight=None, normalized=False)
        b_answer = 3.0
        assert_equal(b, b_answer)

    def test_group_betweenness_normalized(self):
        """
            Group betweenness centrality for group with more than
            1 node and normalized
        """
        G = nx.path_graph(5)
        C = [1, 3]
        b = nx.group_betweenness_centrality(G, C,
                                            weight=None, normalized=True)
        b_answer = 1.0
        assert_equal(b, b_answer)

    def test_group_betweenness_value_zero(self):
        """
            Group betweenness centrality value of 0
        """
        G = nx.cycle_graph(6)
        C = [0, 1, 5]
        b = nx.group_betweenness_centrality(G, C, weight=None)
        b_answer = 0.0
        assert_equal(b, b_answer)

    def test_group_betweenness_disconnected_graph(self):
        """
            Group betweenness centrality in a disconnected graph
        """
        G = nx.path_graph(5)
        G.remove_edge(0, 1)
        C = [1]
        b = nx.group_betweenness_centrality(G, C, weight=None)
        b_answer = 0.0
        assert_equal(b, b_answer)
