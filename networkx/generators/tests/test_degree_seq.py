#!/usr/bin/env python
from nose.tools import *
import networkx
from networkx import *
from networkx.generators.degree_seq import *
from networkx.utils import uniform_sequence,powerlaw_sequence

"""Generators - Degree Sequence
----------------------
"""

class TestGeneratorsDegreeSequence():
    def test_configuration_model(self):
        # empty graph has empty degree sequence
        deg_seq=[]
        G=configuration_model(deg_seq)
        assert_equal(G.degree(), {})

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

        z=[5,3,3,3,3,2,2,2,1,1,1]
        assert_true(is_valid_degree_sequence(z, method='hh'))
        assert_true(is_valid_degree_sequence(z, method='eg'))       

        assert_raises(networkx.exception.NetworkXError,
                      configuration_model, z, create_using=DiGraph())

        G=havel_hakimi_graph(z)
        G=configuration_model(z)
        z=[1000,3,3,3,3,2,2,2,1,1,1]
        assert_false(is_valid_degree_sequence(z, method='hh'))
        assert_false(is_valid_degree_sequence(z, method='eg'))

    def test_expected_degree_graph(self):
        # empty graph has empty degree sequence
        deg_seq=[]
        G=expected_degree_graph(deg_seq)
        assert_equal(G.degree(), {})
        
        # test that fixed seed delivers the same graph
        deg_seq=[3,3,3,3,3,3,3,3,3,3,3,3]
        G1=expected_degree_graph(deg_seq,seed=1000)
        G2=expected_degree_graph(deg_seq,seed=1000)
        assert_true(is_isomorphic(G1,G2))

        G1=expected_degree_graph(deg_seq,seed=10)
        G2=expected_degree_graph(deg_seq,seed=10)
        assert_true(is_isomorphic(G1,G2))

    def test_havel_hakimi_construction(self):
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
        assert_false(is_valid_degree_sequence(z, method='hh'))
        assert_false(is_valid_degree_sequence(z, method='eg'))
        assert_raises(networkx.exception.NetworkXError,
                      havel_hakimi_graph, z)

        z=[10,3,3,3,3,2,2,2,2,2,2]
        assert_true(is_valid_degree_sequence(z, method='hh'))
        assert_true(is_valid_degree_sequence(z, method='eg'))        
        G=havel_hakimi_graph(z)

        assert_raises(networkx.exception.NetworkXError,
                      havel_hakimi_graph, z, create_using=DiGraph())

        assert_raises(networkx.exception.NetworkXError,
                      havel_hakimi_graph, z, create_using=MultiGraph())

    def test_degree_sequence_tree(self):
        z=[1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
        assert_true(is_valid_degree_sequence(z, method='hh'))
        assert_true(is_valid_degree_sequence(z, method='eg'))        
        G=degree_sequence_tree(z)
        assert_true(len(G.nodes())==len(z))
        assert_true(len(G.edges())==sum(z)/2)

        assert_raises(networkx.exception.NetworkXError,
                      degree_sequence_tree, z, create_using=DiGraph())

        z=[1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
        assert_false(is_valid_degree_sequence(z, method='hh'))
        assert_false(is_valid_degree_sequence(z, method='eg'))        
        assert_raises(networkx.exception.NetworkXError,
                      degree_sequence_tree, z)

    def test_degree_sequences(self):
        seq=create_degree_sequence(10,uniform_sequence)
        assert_equal(len(seq), 10)
        seq=create_degree_sequence(10,powerlaw_sequence)
        assert_equal(len(seq), 10)


    def test_double_edge_swap(self):
        graph = barabasi_albert_graph(200,1)

        degreeStart = sorted(graph.degree().values())
        G = connected_double_edge_swap(graph, 40)
        assert_true(is_connected(graph))

        degseq = sorted(graph.degree().values())
        assert_true(degreeStart == degseq)

        G = double_edge_swap(graph, 40)
        degseq2 = sorted(graph.degree().values())
        assert_true(degreeStart == degseq2)

    def test_degree_seq_c4(self):
        G = networkx.cycle_graph(4)
        degree_start = sorted(G.degree().values())
        G = double_edge_swap(G,1,100)
        degseq = sorted(G.degree().values())
        assert_true(degree_start == degseq)

    def test_construction_smax_graph0(self):
        z=["A",3,3,3,3,2,2,2,1,1,1]
        assert_raises(networkx.exception.NetworkXError,
                      li_smax_graph, z)

    def test_construction_smax_graph1(self):
        z=[5,4,3,3,3,2,2,2]
        G=li_smax_graph(z)

        degs = sorted(degree(G).values(),reverse=True)
        assert_equal(degs, z)

    def test_construction_smax_graph2(self):
        z=[6,5,4,4,2,1,1,1]
        assert_false(is_valid_degree_sequence(z, method='hh'))
        assert_false(is_valid_degree_sequence(z, method='eg'))        

        assert_raises(networkx.exception.NetworkXError,
                      li_smax_graph, z)

    def test_construction_smax_graph3(self):
        z=[10,3,3,3,3,2,2,2,2,2,2]
        assert_true(is_valid_degree_sequence(z, method='hh'))
        assert_true(is_valid_degree_sequence(z, method='eg'))        
        G=li_smax_graph(z)

        degs = sorted(degree(G).values(),reverse=True)
        assert_equal(degs, z)

        assert_raises(networkx.exception.NetworkXError,
                      li_smax_graph, z, create_using=DiGraph())



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
    Gdegseq = sorted(G.degree().values(),reverse=True) #degree sequence
    # Tests the 'unconstrained version'
    assert_true(not (sum(Gdegseq)%2)) 
    Gmax = networkx.li_smax_graph(Gdegseq) 
    Gmaxdegseq = sorted(Gmax.degree().values(),reverse=True)
    assert_equal(G.order(),Gmax.order()) #Sanity Check on the nodes
    # make sure both graphs have the same degree sequence
    assert_equal(Gdegseq,Gmaxdegseq) 
    # make sure the smax graph is actually bigger
    assert_true(networkx.s_metric(G) <= networkx.s_metric(Gmax)) 
    
def test_valid_degree_sequence1():
    # Erdos-Renyi Graph
    from networkx.generators import degree_seq as ds
    n = 100
    p = .3
    for i in range(10):
        G = nx.erdos_renyi_graph(n,p)
        deg = list(G.degree().values())
        assert_true( ds.is_valid_degree_sequence(deg, method='eg') )
        assert_true( ds.is_valid_degree_sequence(deg, method='hh') )        

def test_valid_degree_sequence2():
    # Barabasi-Albert Graph
    from networkx.generators import degree_seq as ds
    n = 100
    for i in range(10):
        G = nx.barabasi_albert_graph(n,1)
        deg = list(G.degree().values())
        assert_true( ds.is_valid_degree_sequence(deg, method='eg') )
        assert_true( ds.is_valid_degree_sequence(deg, method='hh') )        

