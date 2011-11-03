#!/usr/bin/env python
from nose.tools import *
import networkx as nx
def test_li_smax():
    G = nx.barabasi_albert_graph(25,1) #Any old graph
    Gdegseq = sorted(G.degree().values(),reverse=True) #degree sequence
    # Tests the 'unconstrained version'
    assert_true(not (sum(Gdegseq)%2)) 
    Gmax = nx.li_smax_graph(Gdegseq) 
    Gmaxdegseq = sorted(Gmax.degree().values(),reverse=True)
    assert_equal(G.order(),Gmax.order()) #Sanity Check on the nodes
    # make sure both graphs have the same degree sequence
    assert_equal(Gdegseq,Gmaxdegseq) 
    # make sure the smax graph is actually bigger
    assert_true(nx.s_metric(G) <= nx.s_metric(Gmax)) 

def test_construction_smax_graph0():
    z=["A",3,3,3,3,2,2,2,1,1,1]
    assert_raises(nx.exception.NetworkXError,
                  nx.li_smax_graph, z)

def test_construction_smax_graph1():
    z=[5,4,3,3,3,2,2,2]
    G=nx.li_smax_graph(z)

    degs = sorted(G.degree().values(),reverse=True)
    assert_equal(degs, z)

def test_construction_smax_graph2():
    z=[6,5,4,4,2,1,1,1]
    assert_raises(nx.exception.NetworkXError,
                  nx.li_smax_graph, z)

def test_construction_smax_graph3():
    z=[10,3,3,3,3,2,2,2,2,2,2]
    G=nx.li_smax_graph(z)

    degs = sorted(G.degree().values(),reverse=True)
    assert_equal(degs, z)

    assert_raises(nx.exception.NetworkXError,
                  nx.li_smax_graph, z, create_using=nx.DiGraph())

