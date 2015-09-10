#!/usr/bin/env python

"""Threshold Graphs
================
"""

from nose.tools import *
from nose import SkipTest
from nose.plugins.attrib import attr
import networkx as nx
import networkx.algorithms.threshold as nxt
from networkx.algorithms.isomorphism.isomorph import graph_could_be_isomorphic

cnlti = nx.convert_node_labels_to_integers


class TestGeneratorThreshold():
    def test_threshold_sequence_graph_test(self):
        G=nx.star_graph(10)
        assert_true(nxt.is_threshold_graph(G))
        assert_true(nxt.is_threshold_sequence(list(d for n, d in G.degree())))

        G=nx.complete_graph(10)
        assert_true(nxt.is_threshold_graph(G))
        assert_true(nxt.is_threshold_sequence(list(d for n, d in G.degree())))

        deg=[3,2,2,1,1,1]
        assert_false(nxt.is_threshold_sequence(deg))

        deg=[3,2,2,1]
        assert_true(nxt.is_threshold_sequence(deg))

        G=nx.generators.havel_hakimi_graph(deg)
        assert_true(nxt.is_threshold_graph(G))

    def test_creation_sequences(self):
        deg=[3,2,2,1]
        G=nx.generators.havel_hakimi_graph(deg)
        cs0=nxt.creation_sequence(deg)
        H0=nxt.threshold_graph(cs0)
        assert_equal(''.join(cs0), 'ddid')

        cs1=nxt.creation_sequence(deg, with_labels=True)
        H1=nxt.threshold_graph(cs1)
        assert_equal(cs1, [(1, 'd'), (2, 'd'), (3, 'i'), (0, 'd')])

        cs2=nxt.creation_sequence(deg, compact=True)
        H2=nxt.threshold_graph(cs2)
        assert_equal(cs2, [2, 1, 1])
        assert_equal(''.join(nxt.uncompact(cs2)), 'ddid')
        assert_true(graph_could_be_isomorphic(H0,G))
        assert_true(graph_could_be_isomorphic(H0,H1))
        assert_true(graph_could_be_isomorphic(H0,H2))

    def test_shortest_path(self):
        deg=[3,2,2,1]
        G=nx.generators.havel_hakimi_graph(deg)
        cs1=nxt.creation_sequence(deg, with_labels=True)
        for n, m in [(3, 0), (0, 3), (0, 2), (0, 1), (1, 3),
                     (3, 1), (1, 2), (2, 3)]:
            assert_equal(nxt.shortest_path(cs1,n,m),
                         nx.shortest_path(G, n, m))

        spl=nxt.shortest_path_length(cs1,3)
        spl2=nxt.shortest_path_length([ t for v,t in cs1],2)
        assert_equal(spl, spl2)

        spld={}
        for j,pl in enumerate(spl):
            n=cs1[j][0]
            spld[n]=pl
        assert_equal(spld, dict(nx.single_source_shortest_path_length(G, 3)))

    def test_weights_thresholds(self):
        wseq=[3,4,3,3,5,6,5,4,5,6]
        cs=nxt.weights_to_creation_sequence(wseq,threshold=10)
        wseq=nxt.creation_sequence_to_weights(cs)
        cs2=nxt.weights_to_creation_sequence(wseq)
        assert_equal(cs, cs2)

        wseq=nxt.creation_sequence_to_weights(nxt.uncompact([3,1,2,3,3,2,3]))
        assert_equal(wseq,
                     [s*0.125 for s in [4,4,4,3,5,5,2,2,2,6,6,6,1,1,7,7,7]])

        wseq=nxt.creation_sequence_to_weights([3,1,2,3,3,2,3])
        assert_equal(wseq,
                     [s*0.125 for s in [4,4,4,3,5,5,2,2,2,6,6,6,1,1,7,7,7]])

        wseq=nxt.creation_sequence_to_weights(list(enumerate('ddidiiidididi')))
        assert_equal(wseq,
                     [s*0.1 for s in [5,5,4,6,3,3,3,7,2,8,1,9,0]])

        wseq=nxt.creation_sequence_to_weights('ddidiiidididi')
        assert_equal(wseq,
                     [s*0.1 for s in [5,5,4,6,3,3,3,7,2,8,1,9,0]])

        wseq=nxt.creation_sequence_to_weights('ddidiiidididid')
        ws=[s/float(12) for s in [6,6,5,7,4,4,4,8,3,9,2,10,1,11]]
        assert_true(sum([abs(c-d) for c,d in zip(wseq,ws)]) < 1e-14)

    def test_finding_routines(self):
        G=nx.Graph({1:[2],2:[3],3:[4],4:[5],5:[6]})
        G.add_edge(2,4)
        G.add_edge(2,5)
        G.add_edge(2,7)
        G.add_edge(3,6)
        G.add_edge(4,6)

        # Alternating 4 cycle
        assert_equal(nxt.find_alternating_4_cycle(G), [1, 2, 3, 6])

        # Threshold graph
        TG=nxt.find_threshold_graph(G)
        assert_true(nxt.is_threshold_graph(TG))
        assert_equal(sorted(TG.nodes()), [1, 2, 3, 4, 5, 7])

        cs=nxt.creation_sequence(dict(TG.degree()), with_labels=True)
        assert_equal(nxt.find_creation_sequence(G), cs)

    def test_fast_versions_properties_threshold_graphs(self):
        cs='ddiiddid'
        G=nxt.threshold_graph(cs)
        assert_equal(nxt.density('ddiiddid'), nx.density(G))
        assert_equal(sorted(nxt.degree_sequence(cs)),
                     sorted(d for n, d in G.degree()))

        ts=nxt.triangle_sequence(cs)
        assert_equal(ts, list(nx.triangles(G).values()))
        assert_equal(sum(ts) // 3, nxt.triangles(cs))

        c1=nxt.cluster_sequence(cs)
        c2=list(nx.clustering(G).values())
        assert_almost_equal(sum([abs(c-d) for c,d in zip(c1,c2)]), 0)

        b1=nx.betweenness_centrality(G).values()
        b2=nxt.betweenness_sequence(cs)
        assert_true(sum([abs(c-d) for c,d in zip(b1,b2)]) < 1e-14)

        assert_equal(nxt.eigenvalues(cs), [0, 1, 3, 3, 5, 7, 7, 8])

        # Degree Correlation
        assert_true(abs(nxt.degree_correlation(cs)+0.593038821954) < 1e-12)
        assert_equal(nxt.degree_correlation('diiiddi'), -0.8)
        assert_equal(nxt.degree_correlation('did'), -1.0)
        assert_equal(nxt.degree_correlation('ddd'), 1.0)
        assert_equal(nxt.eigenvalues('dddiii'), [0, 0, 0, 0, 3, 3])
        assert_equal(nxt.eigenvalues('dddiiid'), [0, 1, 1, 1, 4, 4, 7])

    def test_tg_creation_routines(self):
        s=nxt.left_d_threshold_sequence(5,7)
        s=nxt.right_d_threshold_sequence(5,7)
        s1=nxt.swap_d(s,1.0,1.0)


    @attr('numpy')
    def test_eigenvectors(self):
        try:
            import numpy as N
            eigenval=N.linalg.eigvals
            import scipy
        except ImportError:
            raise SkipTest('SciPy not available.')

        cs='ddiiddid'
        G=nxt.threshold_graph(cs)
        (tgeval,tgevec)=nxt.eigenvectors(cs)
        dot=N.dot
        assert_equal([ abs(dot(lv,lv)-1.0)<1e-9 for lv in tgevec ], [True]*8)
        lapl=nx.laplacian_matrix(G)
#        tgev=[ dot(lv,dot(lapl,lv)) for lv in tgevec ]
#        assert_true(sum([abs(c-d) for c,d in zip(tgev,tgeval)]) < 1e-9)
#        tgev.sort()
#        lev=list(eigenval(lapl))
#        lev.sort()
#        assert_true(sum([abs(c-d) for c,d in zip(tgev,lev)]) < 1e-9)

    def test_create_using(self):
        cs='ddiiddid'
        G=nxt.threshold_graph(cs)
        assert_raises(nx.exception.NetworkXError,
                      nxt.threshold_graph, cs, create_using=nx.DiGraph())
        MG=nxt.threshold_graph(cs,create_using=nx.MultiGraph())
        assert_equal(sorted(MG.edges()), sorted(G.edges()))

