"""
    Tests for VF2 isomorphism algorithm for weighted graphs.
"""

from nose.tools import assert_true, assert_false
import networkx as nx

def test_simple():
    # 16 simple tests
    w = 'weight'
    edges = [(0,0,1),(0,0,1.5),(0,1,2),(1,0,3)]
    for g1 in [nx.Graph(),
               nx.DiGraph(),
               nx.MultiGraph(),
               nx.MultiDiGraph(),
               ]:

        g1.add_weighted_edges_from(edges)
        g2 = g1.subgraph(g1.nodes())
        assert_true( nx.is_isomorphic(g1,g2,weight=w) )

        for mod1, mod2 in [(False, True), (True, False), (True, True)]:
            # mod1 tests a regular edge
            # mod2 tests a selfloop
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

            assert_false(nx.is_isomorphic(g1,g2,weight=w))
            
def test_weightkey():
    g1 = nx.DiGraph()
    g2 = nx.DiGraph()
    
    g1.add_edge('A','B', weight=1)
    g2.add_edge('C','D', weight=0)
    
    assert_true(  nx.is_isomorphic(g1, g2) )
    assert_true(  nx.is_isomorphic(g1, g2, weight='nonexistent attribute') )
    assert_false( nx.is_isomorphic(g1, g2, weight='weight') )
    
    g2 = nx.DiGraph()
    g2.add_edge('C','D')
    assert_true( nx.is_isomorphic(g1, g2, weight='weight') )    

def test_nodematch():

    g1 = nx.DiGraph()
    g2 = nx.DiGraph()

    g1.add_node('A', color='red')
    g2.add_node('C', color='blue')
        
    g1.add_edge('A','B', weight=1)
    g2.add_edge('C','D', weight=1)

    assert_true(  nx.is_isomorphic(g1, g2) )
    assert_true(  nx.is_isomorphic(g1, g2, weight='weight') )
    
    def nm(n1_attrs, n2_attrs):
        return n1_attrs.get('color', '') == n2_attrs.get('color', '')
    assert_false(  nx.is_isomorphic(g1, g2, node_match=nm, weight='weight') )
    assert_false(  nx.is_isomorphic(g1, g2, node_match=nm, weight=None) )
    g1.node['A']['color'] = 'blue'
    assert_true(  nx.is_isomorphic(g1, g2, node_match=nm, weight='weight') )
    
    # make the weights disagree
    g1.add_edge('A', 'B', weight=2)
    assert_false(  nx.is_isomorphic(g1, g2, node_match=None, weight='weight') )
    assert_true(  nx.is_isomorphic(g1, g2, node_match=nm, weight=None) )
    assert_false(  nx.is_isomorphic(g1, g2, node_match=nm, weight='weight') )    
    
