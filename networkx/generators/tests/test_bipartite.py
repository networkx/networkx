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

        GU=project(G,range(len(aseq)))
        assert_equal(GU.number_of_nodes(), 6)

        GD=project(G,range(len(aseq),len(aseq)+len(bseq)))
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

        GU=project(G,range(len(aseq)))
        assert_equal(GU.number_of_nodes(), 6)

        GD=project(G,range(len(aseq),len(aseq)+len(bseq)))
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

        GU=project(G,range(len(aseq)))
        assert_equal(GU.number_of_nodes(), 6)

        GD=project(G,range(len(aseq),len(aseq)+len(bseq)))
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

        GU=project(G,range(len(aseq)))
        assert_equal(GU.number_of_nodes(), 6)

        GD=project(G,range(len(aseq),len(aseq)+len(bseq)))
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

