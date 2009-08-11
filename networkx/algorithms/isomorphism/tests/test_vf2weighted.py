"""
    Tests for VF2 isomorphism algorithm for weighted graphs.
"""

from nose.tools import assert_true, assert_false
import networkx as nx

def test_simple():
    # 16 simple tests
    w = True
    rtol = 1e-6
    atol = 1e-9
    edges = [(0,0,1),(0,0,1.5),(0,1,2),(1,0,3)]
    for g1 in [nx.Graph(weighted=w), 
               nx.DiGraph(weighted=w),
               nx.MultiGraph(weighted=w),
               nx.MultiDiGraph(weighted=w)
               ]:

        print g1.__class__
        g1.add_weighted_edges_from(edges)
        g2 = g1.subgraph(g1.nodes())
        assert_true( nx.is_isomorphic(g1,g2,True,rtol,atol) )

        for mod1, mod2 in [(False, True), (True, False), (True, True)]:
            # mod1 tests a regular edge
            # mod2 tests a selfloop
            print "Modification:", mod1, mod2
            if g2.is_multigraph():
                if mod1:
                    data1 = {0:{'weight':10}}
                if mod2:
                    data2 = {0:{'weight':1},1:{'weight':2.5}}
            else:
                if mod1:
                    data1 = {'weight':10}
                if mod2:
                    data2 = {'weight':2.5}

            g2 = g1.subgraph(g1.nodes())
            if mod1:
                if not g1.is_directed():
                    g2.adj[1][0] = data1
                    g2.adj[0][1] = data1
                else:
                    g2.succ[1][0] = data1
                    g2.pred[0][1] = data1
            if mod2:
                if not g1.is_directed():
                    g2.adj[0][0] = data2
                else:
                    g2.succ[0][0] = data2
                    g2.pred[0][0] = data2

            assert_false(nx.is_isomorphic(g1,g2,True,rtol,atol))

    
