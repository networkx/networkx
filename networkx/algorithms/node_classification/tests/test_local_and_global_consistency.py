#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from networkx.algorithms import node_classification

def test_path_graph():
  G = nx.path_graph(4)
  label_name = 'label'
  G.node[0][label_name] = 'A'
  G.node[3][label_name] = 'B'
  predicted = node_classification.local_and_global_consistency(G, label_name=label_name)
  assert_equal(predicted[0], 'A')
  assert_equal(predicted[1], 'A')
  assert_equal(predicted[2], 'B')
  assert_equal(predicted[3], 'B')

@raises(nx.NetworkXError)
def test_no_labels():
  G = nx.path_graph(4)
  node_classification.local_and_global_consistency(G)

@raises(nx.NetworkXError)
def test_no_nodes():
  G = nx.Graph()
  node_classification.local_and_global_consistency(G)

@raises(nx.NetworkXError)
def test_no_edges():
  G = nx.Graph()
  G.add_node(1)
  G.add_node(2)
  node_classification.local_and_global_consistency(G)

def test_one_labeled_node():
  G = nx.path_graph(4)
  label_name = 'label'
  G.node[0][label_name] = 'A'
  predicted = node_classification.local_and_global_consistency(G, label_name=label_name)
  assert_equal(predicted[0], 'A')
  assert_equal(predicted[1], 'A')
  assert_equal(predicted[2], 'A')
  assert_equal(predicted[3], 'A')

def test_karate_club_graph():
  G = nx.karate_club_graph()
  label_name = 'club'

def test_nodes_all_labeled():
  G = nx.karate_club_graph()
  label_name = 'club'
  predicted = node_classification.local_and_global_consistency(G, alpha=0, label_name=label_name)
  for i in range(len(G)):
    assert_equal(predicted[i], G.node[i][label_name])
