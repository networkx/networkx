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
    assert_equal(dict(G.degree()), {})

def test_configuration_model():
    deg_seq=[5,3,3,3,3,2,2,2,1,1,1]
    G=configuration_model(deg_seq,seed=12345678)
    assert_equal(sorted((d for n, d in G.degree()), reverse=True),
                 [5, 3, 3, 3, 3, 2, 2, 2, 1, 1, 1])
    assert_equal(sorted((d for n, d in G.degree(range(len(deg_seq)))),
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
    assert_equal(dict(G.degree()), {})


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

def test_directed_havel_hakimi():
    # Test range of valid directed degree sequences
    n, r = 100, 10
    p = 1.0 / r
    for i in range(r):
        G1 = nx.erdos_renyi_graph(n,p*(i+1),None,True)
        din1 = list(d for n, d in G1.in_degree())
        dout1 = list(d for n, d in G1.out_degree())
        G2 = nx.directed_havel_hakimi_graph(din1, dout1)
        din2 = list(d for n, d in G2.in_degree())
        dout2 = list(d for n, d in G2.out_degree())
        assert_equal(sorted(din1), sorted(din2))
        assert_equal(sorted(dout1), sorted(dout2))

    # Test non-graphical sequence
    dout = [1000,3,3,3,3,2,2,2,1,1,1]
    din=[103,102,102,102,102,102,102,102,102,102]
    assert_raises(nx.exception.NetworkXError,
                  nx.directed_havel_hakimi_graph, din, dout)
    # Test valid sequences
    dout=[1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
    din=[2, 2, 2, 2, 2, 2, 2, 2, 0, 2]
    G2 = nx.directed_havel_hakimi_graph(din, dout)
    dout2 = (d for n, d in G2.out_degree())
    din2 = (d for n, d in G2.in_degree())
    assert_equal(sorted(dout), sorted(dout2))
    assert_equal(sorted(din), sorted(din2))
    # Test unequal sums
    din=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    assert_raises(nx.exception.NetworkXError,
                  nx.directed_havel_hakimi_graph, din, dout)
    # Test for negative values
    din=[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, -2]
    assert_raises(nx.exception.NetworkXError,
                  nx.directed_havel_hakimi_graph, din, dout)

def test_degree_sequence_tree():
    z=[1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
    G=degree_sequence_tree(z)
    assert_equal(len(G), len(z))
    assert_true(len(list(G.edges())) == sum(z)/2)

    assert_raises(networkx.exception.NetworkXError,
                  degree_sequence_tree, z, create_using=DiGraph())

    z=[1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
    assert_raises(networkx.exception.NetworkXError,
                  degree_sequence_tree, z)

def test_random_degree_sequence_graph():
    d=[1,2,2,3]
    G = nx.random_degree_sequence_graph(d)
    assert_equal(d, sorted(d for n, d in G.degree()))

def test_random_degree_sequence_graph_raise():
    z=[1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
    assert_raises(networkx.exception.NetworkXUnfeasible,
                  random_degree_sequence_graph, z)

def test_random_degree_sequence_large():
    G1 = nx.fast_gnp_random_graph(100,0.1)
    d1 = (d for n, d in G1.degree())
    G2 = nx.random_degree_sequence_graph(d1, seed=0)
    d2 = (d for n, d in G2.degree())
    assert_equal(sorted(d1), sorted(d2))
