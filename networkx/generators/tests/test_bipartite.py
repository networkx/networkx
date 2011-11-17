#!/usr/bin/env python

from nose.tools import *
from networkx import *
from networkx.generators.bipartite import *

"""Generators - Bipartite
----------------------
"""

class TestGeneratorsBipartite():
    def test_configuration_model(self):
        aseq=[3,3,3,3]
        bseq=[2,2,2,2,2]
        assert_raises(networkx.exception.NetworkXError,
                      bipartite_configuration_model, aseq, bseq)
        
        aseq=[3,3,3,3]
        bseq=[2,2,2,2,2,2]
        G=bipartite_configuration_model(aseq,bseq)
        assert_equal(sorted(G.degree().values()),
                     [2, 2, 2, 2, 2, 2, 3, 3, 3, 3])

        aseq=[2,2,2,2,2,2]
        bseq=[3,3,3,3]
        G=bipartite_configuration_model(aseq,bseq)
        assert_equal(sorted(G.degree().values()),
                     [2, 2, 2, 2, 2, 2, 3, 3, 3, 3])

        aseq=[2,2,2,1,1,1]
        bseq=[3,3,3]
        G=bipartite_configuration_model(aseq,bseq)
        assert_equal(sorted(G.degree().values()),
                     [1, 1, 1, 2, 2, 2, 3, 3, 3])

        GU=project(Graph(G),range(len(aseq)))
        assert_equal(GU.number_of_nodes(), 6)

        GD=project(Graph(G),range(len(aseq),len(aseq)+len(bseq)))
        assert_equal(GD.number_of_nodes(), 3)

        assert_raises(networkx.exception.NetworkXError,
                      bipartite_configuration_model, aseq, bseq,
                      create_using=DiGraph())

    def test_havel_hakimi_graph(self):
        aseq=[3,3,3,3]
        bseq=[2,2,2,2,2]
        assert_raises(networkx.exception.NetworkXError,
                      bipartite_havel_hakimi_graph, aseq, bseq)
        
        bseq=[2,2,2,2,2,2]
        G=bipartite_havel_hakimi_graph(aseq,bseq)
        assert_equal(sorted(G.degree().values()),
                     [2, 2, 2, 2, 2, 2, 3, 3, 3, 3])

        aseq=[2,2,2,2,2,2]
        bseq=[3,3,3,3]
        G=bipartite_havel_hakimi_graph(aseq,bseq)
        assert_equal(sorted(G.degree().values()),
                     [2, 2, 2, 2, 2, 2, 3, 3, 3, 3])

        GU=project(Graph(G),range(len(aseq)))
        assert_equal(GU.number_of_nodes(), 6)

        GD=project(Graph(G),range(len(aseq),len(aseq)+len(bseq)))
        assert_equal(GD.number_of_nodes(), 4)
        assert_raises(networkx.exception.NetworkXError,
                      bipartite_havel_hakimi_graph, aseq, bseq,
                      create_using=DiGraph())
            
    def test_reverse_havel_hakimi_graph(self):
        aseq=[3,3,3,3]
        bseq=[2,2,2,2,2]
        assert_raises(networkx.exception.NetworkXError,
                      bipartite_reverse_havel_hakimi_graph, aseq, bseq)
        
        bseq=[2,2,2,2,2,2]
        G=bipartite_reverse_havel_hakimi_graph(aseq,bseq)
        assert_equal(sorted(G.degree().values()),
                     [2, 2, 2, 2, 2, 2, 3, 3, 3, 3])

        aseq=[2,2,2,2,2,2]
        bseq=[3,3,3,3]
        G=bipartite_reverse_havel_hakimi_graph(aseq,bseq)
        assert_equal(sorted(G.degree().values()),
                     [2, 2, 2, 2, 2, 2, 3, 3, 3, 3])

        aseq=[2,2,2,1,1,1]
        bseq=[3,3,3]
        G=bipartite_reverse_havel_hakimi_graph(aseq,bseq)
        assert_equal(sorted(G.degree().values()),
                     [1, 1, 1, 2, 2, 2, 3, 3, 3])

        GU=project(Graph(G),range(len(aseq)))
        assert_equal(GU.number_of_nodes(), 6)

        GD=project(Graph(G),range(len(aseq),len(aseq)+len(bseq)))
        assert_equal(GD.number_of_nodes(), 3)
        assert_raises(networkx.exception.NetworkXError,
                      bipartite_reverse_havel_hakimi_graph, aseq, bseq,
                      create_using=DiGraph())
        
    def test_alternating_havel_hakimi_graph(self):
        aseq=[3,3,3,3]
        bseq=[2,2,2,2,2]
        assert_raises(networkx.exception.NetworkXError,
                      bipartite_alternating_havel_hakimi_graph, aseq, bseq)
        
        bseq=[2,2,2,2,2,2]
        G=bipartite_alternating_havel_hakimi_graph(aseq,bseq)
        assert_equal(sorted(G.degree().values()),
                     [2, 2, 2, 2, 2, 2, 3, 3, 3, 3])

        aseq=[2,2,2,2,2,2]
        bseq=[3,3,3,3]
        G=bipartite_alternating_havel_hakimi_graph(aseq,bseq)
        assert_equal(sorted(G.degree().values()),
                     [2, 2, 2, 2, 2, 2, 3, 3, 3, 3])

        aseq=[2,2,2,1,1,1]
        bseq=[3,3,3]
        G=bipartite_alternating_havel_hakimi_graph(aseq,bseq)
        assert_equal(sorted(G.degree().values()),
                     [1, 1, 1, 2, 2, 2, 3, 3, 3])

        GU=project(Graph(G),range(len(aseq)))
        assert_equal(GU.number_of_nodes(), 6)

        GD=project(Graph(G),range(len(aseq),len(aseq)+len(bseq)))
        assert_equal(GD.number_of_nodes(), 3)

        assert_raises(networkx.exception.NetworkXError,
                      bipartite_alternating_havel_hakimi_graph, aseq, bseq,
                      create_using=DiGraph())
        
    def test_preferential_attachment(self):
        aseq=[3,2,1,1]
        G=bipartite_preferential_attachment_graph(aseq,0.5)
        assert_raises(networkx.exception.NetworkXError,
                      bipartite_preferential_attachment_graph, aseq, 0.5,
                      create_using=DiGraph())

    """def test_random_regular_bipartite(self):
        # FIXME: test this somehow
        G=bipartite_random_regular_graph(2,12)
        assert_equal(list(G.degree().values()),
                [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4])
        assert_true(is_bipartite(G))
    """

    def test_bipartite_random_graph(self):
        n=10
        m=20
        G=bipartite_random_graph(n,m,0.9)
        assert_equal(len(G),30)
        assert_true(is_bipartite(G))
        X,Y=nx.algorithms.bipartite.sets(G)
        assert_equal(set(range(n)),X)
        assert_equal(set(range(n,n+m)),Y)

    def test_directed_bipartite_random_graph(self):
        n=10
        m=20
        G=bipartite_random_graph(n,m,0.9,directed=True)
        assert_equal(len(G),30)
        assert_true(is_bipartite(G))
        X,Y=nx.algorithms.bipartite.sets(G)
        assert_equal(set(range(n)),X)
        assert_equal(set(range(n,n+m)),Y)

    def test_bipartite_gnmk_random_graph(self):
        n = 10
        m = 20
        edges = 100
        G = bipartite_gnmk_random_graph(n, m, edges)
        assert_equal(len(G),30)
        assert_true(is_bipartite(G))
        X,Y=nx.algorithms.bipartite.sets(G)
        print(X)
        assert_equal(set(range(n)),X)
        assert_equal(set(range(n,n+m)),Y)
        assert_equal(edges, len(G.edges()))

