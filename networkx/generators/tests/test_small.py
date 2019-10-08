#!/usr/bin/env python

from nose.tools import *
import networkx as nx
from networkx.algorithms.isomorphism.isomorph import graph_could_be_isomorphic
is_isomorphic = graph_could_be_isomorphic

"""Generators - Small
=====================

Some small graphs
"""

null = nx.null_graph()


class TestGeneratorsSmall():
    def test_make_small_graph(self):
        d = ["adjacencylist", "Bull Graph", 5, [[2, 3], [1, 3, 4], [1, 2, 5], [2], [3]]]
        G = nx.make_small_graph(d)
        assert_true(is_isomorphic(G, nx.bull_graph()))

    def test__LCF_graph(self):
        # If n<=0, then return the null_graph
        G = nx.LCF_graph(-10, [1, 2], 100)
        assert_true(is_isomorphic(G, null))
        G = nx.LCF_graph(0, [1, 2], 3)
        assert_true(is_isomorphic(G, null))
        G = nx.LCF_graph(0, [1, 2], 10)
        assert_true(is_isomorphic(G, null))

        # Test that LCF(n,[],0) == cycle_graph(n)
        for a, b, c in [(5, [], 0), (10, [], 0), (5, [], 1), (10, [], 10)]:
            G = nx.LCF_graph(a, b, c)
            assert_true(is_isomorphic(G, nx.cycle_graph(a)))

        # Generate the utility graph K_{3,3}
        G = nx.LCF_graph(6, [3, -3], 3)
        utility_graph = nx.complete_bipartite_graph(3, 3)
        assert_true(is_isomorphic(G, utility_graph))

    def test_properties_named_small_graphs(self):
        G = nx.bull_graph()
        assert_equal(G.number_of_nodes(), 5)
        assert_equal(G.number_of_edges(), 5)
        assert_equal(sorted(d for n, d in G.degree()), [1, 1, 2, 3, 3])
        assert_equal(nx.diameter(G), 3)
        assert_equal(nx.radius(G), 2)

        G = nx.chvatal_graph()
        assert_equal(G.number_of_nodes(), 12)
        assert_equal(G.number_of_edges(), 24)
        assert_equal(list(d for n, d in G.degree()), 12 * [4])
        assert_equal(nx.diameter(G), 2)
        assert_equal(nx.radius(G), 2)

        G = nx.cubical_graph()
        assert_equal(G.number_of_nodes(), 8)
        assert_equal(G.number_of_edges(), 12)
        assert_equal(list(d for n, d in G.degree()), 8 * [3])
        assert_equal(nx.diameter(G), 3)
        assert_equal(nx.radius(G), 3)

        G = nx.desargues_graph()
        assert_equal(G.number_of_nodes(), 20)
        assert_equal(G.number_of_edges(), 30)
        assert_equal(list(d for n, d in G.degree()), 20 * [3])

        G = nx.diamond_graph()
        assert_equal(G.number_of_nodes(), 4)
        assert_equal(sorted(d for n, d in G.degree()), [2, 2, 3, 3])
        assert_equal(nx.diameter(G), 2)
        assert_equal(nx.radius(G), 1)

        G = nx.dodecahedral_graph()
        assert_equal(G.number_of_nodes(), 20)
        assert_equal(G.number_of_edges(), 30)
        assert_equal(list(d for n, d in G.degree()), 20 * [3])
        assert_equal(nx.diameter(G), 5)
        assert_equal(nx.radius(G), 5)

        G = nx.frucht_graph()
        assert_equal(G.number_of_nodes(), 12)
        assert_equal(G.number_of_edges(), 18)
        assert_equal(list(d for n, d in G.degree()), 12 * [3])
        assert_equal(nx.diameter(G), 4)
        assert_equal(nx.radius(G), 3)

        G = nx.heawood_graph()
        assert_equal(G.number_of_nodes(), 14)
        assert_equal(G.number_of_edges(), 21)
        assert_equal(list(d for n, d in G.degree()), 14 * [3])
        assert_equal(nx.diameter(G), 3)
        assert_equal(nx.radius(G), 3)

        G = nx.hoffman_singleton_graph()
        assert_equal(G.number_of_nodes(), 50)
        assert_equal(G.number_of_edges(), 175)
        assert_equal(list(d for n, d in G.degree()), 50 * [7])
        assert_equal(nx.diameter(G), 2)
        assert_equal(nx.radius(G), 2)

        G = nx.house_graph()
        assert_equal(G.number_of_nodes(), 5)
        assert_equal(G.number_of_edges(), 6)
        assert_equal(sorted(d for n, d in G.degree()), [2, 2, 2, 3, 3])
        assert_equal(nx.diameter(G), 2)
        assert_equal(nx.radius(G), 2)

        G = nx.house_x_graph()
        assert_equal(G.number_of_nodes(), 5)
        assert_equal(G.number_of_edges(), 8)
        assert_equal(sorted(d for n, d in G.degree()), [2, 3, 3, 4, 4])
        assert_equal(nx.diameter(G), 2)
        assert_equal(nx.radius(G), 1)

        G = nx.icosahedral_graph()
        assert_equal(G.number_of_nodes(), 12)
        assert_equal(G.number_of_edges(), 30)
        assert_equal(list(d for n, d in G.degree()),
                     [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5])
        assert_equal(nx.diameter(G), 3)
        assert_equal(nx.radius(G), 3)

        G = nx.krackhardt_kite_graph()
        assert_equal(G.number_of_nodes(), 10)
        assert_equal(G.number_of_edges(), 18)
        assert_equal(sorted(d for n, d in G.degree()),
                     [1, 2, 3, 3, 3, 4, 4, 5, 5, 6])

        G = nx.moebius_kantor_graph()
        assert_equal(G.number_of_nodes(), 16)
        assert_equal(G.number_of_edges(), 24)
        assert_equal(list(d for n, d in G.degree()), 16 * [3])
        assert_equal(nx.diameter(G), 4)

        G = nx.octahedral_graph()
        assert_equal(G.number_of_nodes(), 6)
        assert_equal(G.number_of_edges(), 12)
        assert_equal(list(d for n, d in G.degree()), 6 * [4])
        assert_equal(nx.diameter(G), 2)
        assert_equal(nx.radius(G), 2)

        G = nx.pappus_graph()
        assert_equal(G.number_of_nodes(), 18)
        assert_equal(G.number_of_edges(), 27)
        assert_equal(list(d for n, d in G.degree()), 18 * [3])
        assert_equal(nx.diameter(G), 4)

        G = nx.petersen_graph()
        assert_equal(G.number_of_nodes(), 10)
        assert_equal(G.number_of_edges(), 15)
        assert_equal(list(d for n, d in G.degree()), 10 * [3])
        assert_equal(nx.diameter(G), 2)
        assert_equal(nx.radius(G), 2)

        G = nx.sedgewick_maze_graph()
        assert_equal(G.number_of_nodes(), 8)
        assert_equal(G.number_of_edges(), 10)
        assert_equal(sorted(d for n, d in G.degree()), [1, 2, 2, 2, 3, 3, 3, 4])

        G = nx.tetrahedral_graph()
        assert_equal(G.number_of_nodes(), 4)
        assert_equal(G.number_of_edges(), 6)
        assert_equal(list(d for n, d in G.degree()), [3, 3, 3, 3])
        assert_equal(nx.diameter(G), 1)
        assert_equal(nx.radius(G), 1)

        G = nx.truncated_cube_graph()
        assert_equal(G.number_of_nodes(), 24)
        assert_equal(G.number_of_edges(), 36)
        assert_equal(list(d for n, d in G.degree()), 24 * [3])

        G = nx.truncated_tetrahedron_graph()
        assert_equal(G.number_of_nodes(), 12)
        assert_equal(G.number_of_edges(), 18)
        assert_equal(list(d for n, d in G.degree()), 12 * [3])

        G = nx.tutte_graph()
        assert_equal(G.number_of_nodes(), 46)
        assert_equal(G.number_of_edges(), 69)
        assert_equal(list(d for n, d in G.degree()), 46 * [3])

        # Test create_using with directed or multigraphs on small graphs
        assert_raises(nx.NetworkXError, nx.tutte_graph,
                      create_using=nx.DiGraph)
        MG = nx.tutte_graph(create_using=nx.MultiGraph)
        assert_equal(sorted(MG.edges()), sorted(G.edges()))
