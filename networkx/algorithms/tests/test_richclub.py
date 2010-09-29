import networkx as nx
from nose.tools import *


def test_richclub():
    G = nx.Graph()
    G.add_edge(0,1)
    G.add_edge(0,2)
    G.add_edge(1,2)
    G.add_edge(1,3)
    G.add_edge(1,4)
    G.add_edge(4,5)
    rc = nx.richclub.rich_club_coefficient(G,normalized=False)
    assert_equal(rc,{0: 12.0/30,1:8.0/12})
    rcNorm = nx.richclub.rich_club_coefficient(G,Q=10)
    assert_equal(rcNorm,{0:1.0,1:1.0})
    
    # test single value
    rc0 = nx.richclub.rich_club_coefficient(G,normalized=False)[0]
    assert_equal(rc0,12.0/30.0)


def test_richclub2():
    T = nx.balanced_tree(2,10)
    rc = nx.richclub.rich_club_coefficient(T,normalized=False)
    assert_equal(rc,{0:4092/(2047*2046.0),
                     1:(2044.0/(1023*1022)),
                     2:(2040.0/(1022*1021))})
    rcNorm = nx.richclub.rich_club_coefficient(T,Q=10)
    assert_true(rcNorm[0] ==1.0 and rcNorm[1] < 0.9 and rcNorm[2] < 0.9)
