#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
import networkx as nx
from networkx.algorithms import node_classification


class TestHarmonicFunction:

    @classmethod
    def setupClass(cls):
        global numpy
        global scipy
        try:
            import numpy
        except ImportError:
            raise SkipTest('NumPy not available.')
        try:
            import scipy
        except ImportError:
            raise SkipTest('SciPy not available.')

    def test_path_graph(self):
        G = nx.path_graph(4)
        label_name = 'label'
        G.node[0][label_name] = 'A'
        G.node[3][label_name] = 'B'
        predicted = node_classification.harmonic_function(
            G, label_name=label_name)
        assert_equal(predicted[0], 'A')
        assert_equal(predicted[1], 'A')
        assert_equal(predicted[2], 'B')
        assert_equal(predicted[3], 'B')

    @raises(nx.NetworkXError)
    def test_no_labels(self):
        G = nx.path_graph(4)
        node_classification.harmonic_function(G)

    @raises(nx.NetworkXError)
    def test_no_nodes(self):
        G = nx.Graph()
        node_classification.harmonic_function(G)

    @raises(nx.NetworkXError)
    def test_no_edges(self):
        G = nx.Graph()
        G.add_node(1)
        G.add_node(2)
        node_classification.harmonic_function(G)

    @raises(nx.NetworkXNotImplemented)
    def test_digraph(self):
        G = nx.DiGraph()
        G.add_edge(0, 1)
        G.add_edge(1, 2)
        G.add_edge(2, 3)
        label_name = 'label'
        G.node[0][label_name] = 'A'
        G.node[3][label_name] = 'B'
        node_classification.harmonic_function(G)

    def test_one_labeled_node(self):
        G = nx.path_graph(4)
        label_name = 'label'
        G.node[0][label_name] = 'A'
        predicted = node_classification.harmonic_function(
            G, label_name=label_name)
        assert_equal(predicted[0], 'A')
        assert_equal(predicted[1], 'A')
        assert_equal(predicted[2], 'A')
        assert_equal(predicted[3], 'A')

    def test_nodes_all_labeled(self):
        G = nx.karate_club_graph()
        label_name = 'club'
        predicted = node_classification.harmonic_function(
            G, label_name=label_name)
        for i in range(len(G)):
            assert_equal(predicted[i], G.node[i][label_name])

    def test_labeled_nodes_are_not_changed(self):
        G = nx.karate_club_graph()
        label_name = 'club'
        label_removed = set([0, 1, 2, 3, 4, 5, 6, 7])
        for i in label_removed:
            del G.node[i][label_name]
        predicted = node_classification.harmonic_function(
            G, label_name=label_name)
        label_not_removed = set(list(range(len(G)))) - label_removed
        for i in label_not_removed:
            assert_equal(predicted[i], G.node[i][label_name])
