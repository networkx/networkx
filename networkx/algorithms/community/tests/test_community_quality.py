import networkx as nx
from nose.tools import *

def test_cut_size():
    G = nx.barbell_graph(3,0)
    C = [set([0,1,4]),set([2,3,5])]
    assert_equal(nx.cut_size(G,C[0],C[1]),4)
    assert_equal(nx.cut_size(G,C[1],C[0]),4)
    
    C = [set([0,1,2]),set([3,4,5])]
    assert_equal(nx.cut_size(G,C[0],C[1]),1)
    assert_equal(nx.cut_size(G,C[1],C[0]),1)

    GD = G.to_directed()
    assert_equal(nx.cut_size(GD,C[0],C[1]),2)
    assert_equal(nx.cut_size(GD,C[1],C[0]),2)
    
    C = [set([0,1,4]),set([2,3,5])]
    assert_equal(nx.cut_size(GD,C[0],C[1]),8)
    assert_equal(nx.cut_size(GD,C[1],C[0]),8)

    G = nx.MultiGraph()
    G.add_edge('a','b')
    G.add_edge('a','b')
    assert_equal(2,nx.cut_size(G,set(['a']),set(['b'])))

def test_modularity():
    G = nx.barbell_graph(3,0)

    C = [set([0,1,4]),set([2,3,5])]

    assert_almost_equal(-16/(14.**2),nx.modularity(G,C))

    C = [set([0,1,2]),set([3,4,5])]

    assert_almost_equal((35*2)/(14**2.),nx.modularity(G,C))

def test_community_performance():
    G = nx.barbell_graph(3,0)

    C = [set([0,1,4]),set([2,3,5])]

    assert_almost_equal(8/15., nx.community_performance(G,C))

    C = [set([0,1,2]),set([3,4,5])]

    assert_almost_equal(14./15,nx.community_performance(G,C))

def test_community_coverage():
    G = nx.barbell_graph(3,0)
    C = [set([0,1,4]),set([2,3,5])]
    assert_almost_equal(3/7.,nx.community_coverage(G,C))

    C = [set([0,1,2]),set([3,4,5])]
    assert_almost_equal(6/7.,nx.community_coverage(G,C))
