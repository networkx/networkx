#!/usr/bin/env python

from nose.tools import *
from networkx import *
from networkx.generators.degree_seq import *
from networkx.algorithms.isomorphism.isomorph import graph_could_be_isomorphic

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
        assert_equal(sorted(G.degree(range(len(deg_seq))).values(),reverse=True),
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
        assert_true(is_valid_degree_sequence(z))

        assert_raises(networkx.exception.NetworkXError,
                      configuration_model, z, create_using=DiGraph())

        G=havel_hakimi_graph(z)
        G=configuration_model(z)
        z=[1000,3,3,3,3,2,2,2,1,1,1]
        assert_false(is_valid_degree_sequence(z))

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

        assert_raises(networkx.exception.NetworkXError,
                      expected_degree_graph, z, create_using=DiGraph())

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
        assert_false(is_valid_degree_sequence(z))
        assert_raises(networkx.exception.NetworkXError,
                      havel_hakimi_graph, z)

        z=[10,3,3,3,3,2,2,2,2,2,2]
        assert_true(is_valid_degree_sequence(z))
        G=havel_hakimi_graph(z)

        assert_raises(networkx.exception.NetworkXError,
                      havel_hakimi_graph, z, create_using=DiGraph())

        assert_raises(networkx.exception.NetworkXError,
                      havel_hakimi_graph, z, create_using=MultiGraph())

    def test_degree_sequence_tree(self):
        z=[1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
        assert_true(is_valid_degree_sequence(z))
        G=degree_sequence_tree(z)
        assert_true(len(G.nodes())==len(z))
        assert_true(len(G.edges())==sum(z)/2)

        assert_raises(networkx.exception.NetworkXError,
                      degree_sequence_tree, z, create_using=DiGraph())

        z=[1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 4]
        assert_false(is_valid_degree_sequence(z))
        assert_raises(networkx.exception.NetworkXError,
                      degree_sequence_tree, z)

    def test_degree_sequences(self):
        seq=create_degree_sequence(10,uniform_sequence)
        assert_equal(len(seq), 10)
        seq=create_degree_sequence(10,powerlaw_sequence)
        assert_equal(len(seq), 10)

        graph = barabasi_albert_graph(200,1)

        degreeStart = sorted(degree(graph))

        swaps = connected_double_edge_swap(graph, 40)
        assert_true(is_connected(graph))

        degseq = sorted(degree(graph))
        assert_true(degreeStart == degseq)

        swaps = double_edge_swap(graph, 40)
        degseq2 = sorted(degree(graph))
        assert_true(degreeStart == degseq2)

    def test_contruction_smax_graph(self):
        z=["A",3,3,3,3,2,2,2,1,1,1]
        assert_raises(networkx.exception.NetworkXError,
                      li_smax_graph, z)

        z=[5,4,3,3,3,2,2,2]
        G=li_smax_graph(z)
        assert_true(is_connected(G))

        degs = degree(G).values()
        degs.sort()
        degs.reverse()
        assert_equal(degs, z)

        z=[6,5,4,4,2,1,1,1]
        assert_false(is_valid_degree_sequence(z))

        assert_raises(networkx.exception.NetworkXError,
                      li_smax_graph, z)

        z=[10,3,3,3,3,2,2,2,2,2,2]
        assert_true(is_valid_degree_sequence(z))
        G=li_smax_graph(z)

        assert_true(is_connected(G))
        degs = degree(G).values()
        degs.sort()
        degs.reverse()
        assert_equal(degs, z)

        assert_raises(networkx.exception.NetworkXError,
                      li_smax_graph, z, create_using=DiGraph())


