#!/usr/bin/env python
from nose.tools import *
import networkx
from networkx import *
from networkx.generators.degree_seq import *
from networkx.utils import uniform_sequence,powerlaw_sequence

def test_configuration_model_empty():
    # empty graph has empty degree sequence
    deg_seq=[]
    G=configuration_model(deg_seq)
    assert_equal(G.degree(), {})

def test_configuration_model():
    deg_seq=[5,3,3,3,3,2,2,2,1,1,1]
    G=configuration_model(deg_seq,seed=12345678)
    assert_equal(sorted(G.degree().values(),reverse=True),
                 [5, 3, 3, 3, 3, 2, 2, 2, 1, 1, 1])
    assert_equal(sorted(G.degree(range(len(deg_seq))).values(),
                        reverse=True),
                 [5, 3, 3, 3, 3, 2, 2, 2, 1, 1, 1])

    # test that fixed seed delivers the same graph
    deg_seq=[3,3,3,3,3,3,3,3,3,3,3,3]
    G1=configuration_model(deg_seq,seed=1000)
    G2=configuration_model(deg_seq,seed=1000)
    assert_true(is_isomorphic(G1,G2))
    G1=configuration_model(deg_seq,seed=10)
    G2=configuration_model(deg_seq,seed=10)
    assert_true(is_isomorphic(G1,G2))

@raises(NetworkXError)
def test_configuation_raise():
    z=[5,3,3,3,3,2,2,2,1,1,1]
    G = configuration_model(z, create_using=DiGraph())

@raises(NetworkXError)
def test_configuation_raise_odd():
    z=[5,3,3,3,3,2,2,2,1,1]
    G = configuration_model(z, create_using=DiGraph())

@raises(NetworkXError)
def test_directed_configuation_raise_unequal():
    zin = [5,3,3,3,3,2,2,2,1,1]
    zout = [5,3,3,3,3,2,2,2,1,2]
    G = directed_configuration_model(zin, zout)

def test_directed_configuation_mode():
    G = directed_configuration_model([],[],seed=0)
    assert_equal(len(G),0)


def test_expected_degree_graph_empty():
    # empty graph has empty degree sequence
    deg_seq=[]
    G=expected_degree_graph(deg_seq)
    assert_equal(G.degree(), {})


def test_expected_degree_graph():
    # test that fixed seed delivers the same graph
    deg_seq=[3,3,3,3,3,3,3,3,3,3,3,3]
    G1=expected_degree_graph(deg_seq,seed=1000)
    G2=expected_degree_graph(deg_seq,seed=1000)
    assert_true(is_isomorphic(G1,G2))

    G1=expected_degree_graph(deg_seq,seed=10)
    G2=expected_degree_graph(deg_seq,seed=10)
    assert_true(is_isomorphic(G1,G2))


def test_expected_degree_graph_selfloops():
    deg_seq=[3,3,3,3,3,3,3,3,3,3,3,3]
    G1=expected_degree_graph(deg_seq,seed=1000, selfloops=False)
    G2=expected_degree_graph(deg_seq,seed=1000, selfloops=False)
    assert_true(is_isomorphic(G1,G2))

def test_expected_degree_graph_skew():
    deg_seq=[10,2,2,2,2]
    G1=expected_degree_graph(deg_seq,seed=1000)
    G2=expected_degree_graph(deg_seq,seed=1000)
    assert_true(is_isomorphic(G1,G2))


def test_havel_hakimi_construction():
    G = havel_hakimi_graph([])
    assert_equal(len(G),0)

    z=[1000,3,3,3,3,2,2,2,1,1,1]
    assert_raises(networkx.exception.NetworkXError,
                  havel_hakimi_graph, z)
    z=["A",3,3,3,3,2,2,2,1,1,1]
    assert_raises(networkx.exception.NetworkXError,
                  havel_hakimi_graph, z)

    z=[5,4,3,3,3,2,2,2]
    G=havel_hakimi_graph(z)
    G=configuration_model(z)
    z=[6,5,4,4,2,1,1,1]
    assert_raises(networkx.exception.NetworkXError,
                  havel_hakimi_graph, z)

    z=[10,3,3,3,3,2,2,2,2,2,2]

    G=havel_hakimi_graph(z)

    assert_raises(networkx.exception.NetworkXError,
                  havel_hakimi_graph, z, create_using=DiGraph())

    assert_raises(networkx.exception.NetworkXError,
                  havel_hakimi_graph, z, create_using=MultiGraph())

def test_degree_sequence_tree():
    G = degree_sequence_tree([0])
    assert_equal(len(G),0)

    z=[1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
    G=degree_sequence_tree(z)
    assert_true(len(G.nodes())==len(z))
    assert_true(len(G.edges())==sum(z)/2)

    assert_raises(networkx.exception.NetworkXError,
                  degree_sequence_tree, z, create_using=DiGraph())

    z=[1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
    assert_raises(networkx.exception.NetworkXError,
                  degree_sequence_tree, z)

def test_random_degree_sequence_graph():
    d=[1,2,2,3]
    G = nx.random_degree_sequence_graph(d)
    assert_equal(d, list(G.degree().values()))

def test_random_degree_sequence_graph_raise():
    z=[1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
    assert_raises(networkx.exception.NetworkXUnfeasible,
                  random_degree_sequence_graph, z)

def test_random_degree_sequence_large():
    G = nx.fast_gnp_random_graph(100,0.1)
    d = G.degree().values()
    G = nx.random_degree_sequence_graph(d, seed=0)
    assert_equal(sorted(d), sorted(list(G.degree().values())))
