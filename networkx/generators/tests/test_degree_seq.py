#!/usr/bin/env python
from nose.tools import *
import networkx

class TestRandomClusteredGraph:

    def test_valid(self):
        node=[1,1,1,2,1,2,0,0]
        tri=[0,0,0,0,0,1,1,1]  
        joint_degree_sequence=zip(node,tri)
        G = networkx.random_clustered_graph(joint_degree_sequence)
        assert_equal(G.number_of_nodes(),8)
        assert_equal(G.number_of_edges(),7)
        
    def test_valid2(self):
        G = networkx.random_clustered_graph(\
            [(1,2),(2,1),(1,1),(1,1),(1,1),(2,0)])        
        assert_equal(G.number_of_nodes(),6)
        assert_equal(G.number_of_edges(),10)

    def test_invalid1(self):
        assert_raises((TypeError,networkx.NetworkXError),
                      networkx.random_clustered_graph,[[1,1],[2,1],[0,1]])

    def test_invalid2(self):
        assert_raises((TypeError,networkx.NetworkXError),
                      networkx.random_clustered_graph,[[1,1],[1,2],[0,1]])

def test_li_smax():
    G = networkx.barabasi_albert_graph(25,1) #Any old graph
    Gdegseq = G.degree().values() #degree sequence
    Gdegseq.sort(reverse=True)
    assert_true(not (sum(Gdegseq)%2)) #Tests the 'unconstrained version'
    Gmax = networkx.li_smax_graph(Gdegseq) 
    Gmaxdegseq = Gmax.degree().values()
    Gmaxdegseq.sort(reverse=True)
    assert_equal(G.order(),Gmax.order()) #Sanity Check on the nodes
    assert_equal(Gdegseq,Gmaxdegseq) #make sure both graphs have the same degree sequence
    assert_true(networkx.s_metric(G) <= networkx.s_metric(Gmax)) #make sure the smax graph is actually bigger


