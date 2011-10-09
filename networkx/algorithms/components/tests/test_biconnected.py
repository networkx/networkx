#!/usr/bin/env python
from nose.tools import *
import networkx as nx
from networkx.algorithms.components import biconnected

def assert_components_equal(x,y):
    sx = set((frozenset([frozenset(e) for e in c]) for c in x))
    sy = set((frozenset([frozenset(e) for e in c]) for c in y))
    assert_equal(sx,sy)

def test_barbell():
    G=nx.barbell_graph(8,4)
    G.add_path([7,20,21,22])
    G.add_cycle([22,23,24,25])
    pts=set(biconnected.articulation_points(G))
    assert_equal(pts,set([7,8,9,10,11,12,20,21,22]))

    answer = [set([12, 13, 14, 15, 16, 17, 18, 19]),
                set([0, 1, 2, 3, 4, 5, 6, 7]),
                set([22, 23, 24, 25]),
                set([11, 12]),
                set([10, 11]),
                set([9, 10]),
                set([8, 9]),
                set([7, 8]),
                set([21, 22]),
                set([20, 21]),
                set([7, 20])]  
    bcc=list(biconnected.biconnected_components(G))
    bcc.sort(key=len, reverse=True)
    assert_equal(bcc,answer)

    G.add_edge(2,17)
    pts=set(biconnected.articulation_points(G))
    assert_equal(pts,set([7,20,21,22]))

def test_articulation_points_cycle():
    G=nx.cycle_graph(3)
    G.add_cycle([1,3,4])
    pts=set(biconnected.articulation_points(G))
    assert_equal(pts,set([1]))

def test_is_biconnected():
    G=nx.cycle_graph(3)
    assert_true(biconnected.is_biconnected(G))
    G.add_cycle([1,3,4])
    assert_false(biconnected.is_biconnected(G))

def test_empty_is_biconnected():
    G=nx.empty_graph(5)
    assert_false(biconnected.is_biconnected(G))
    G.add_edge(0,1)
    assert_false(biconnected.is_biconnected(G))

def test_biconnected_components_cycle():
    G=nx.cycle_graph(3)
    G.add_cycle([1,3,4])
    pts = set(map(frozenset,biconnected.biconnected_components(G)))
    assert_equal(pts,set([frozenset([0,1,2]),frozenset([1,3,4])]))

def test_biconnected_component_subgraphs_cycle():
    G=nx.cycle_graph(3)
    G.add_cycle([1,3,4,5])
    G.add_edge(1,3,eattr='red')  # test copying of edge data
    G.node[1]['nattr']='blue'
    G.graph['gattr']='green'
    Gc = set(biconnected.biconnected_component_subgraphs(G))
    assert_equal(len(Gc),2)
    g1,g2=Gc
    if 0 in g1:
        assert_true(nx.is_isomorphic(g1,nx.Graph([(0,1),(0,2),(1,2)])))
        assert_true(nx.is_isomorphic(g2,nx.Graph([(1,3),(1,5),(3,4),(4,5)])))
        assert_equal(g2[1][3]['eattr'],'red')
        assert_equal(g2.node[1]['nattr'],'blue')
        assert_equal(g2.graph['gattr'],'green')
        g2[1][3]['eattr']='blue'
        assert_equal(g2[1][3]['eattr'],'blue')
        assert_equal(G[1][3]['eattr'],'red')
    else:
        assert_true(nx.is_isomorphic(g1,nx.Graph([(1,3),(1,5),(3,4),(4,5)])))
        assert_true(nx.is_isomorphic(g2,nx.Graph([(0,1),(0,2),(1,2)])))
        assert_equal(g1[1][3]['eattr'],'red')
        assert_equal(g1.node[1]['nattr'],'blue')
        assert_equal(g1.graph['gattr'],'green')
        g1[1][3]['eattr']='blue'
        assert_equal(g1[1][3]['eattr'],'blue')
        assert_equal(G[1][3]['eattr'],'red')


def test_biconnected_components1():
    # graph example from
    # http://www.ibluemojo.com/school/articul_algorithm.html 
    edges=[(0,1),
           (0,5),
           (0,6),
           (0,14),
           (1,5),
           (1,6),
           (1,14),
           (2,4),
           (2,10),
           (3,4),
           (3,15),
           (4,6),
           (4,7),
           (4,10),
           (5,14),
           (6,14),
           (7,9),
           (8,9),
           (8,12),
           (8,13),
           (10,15),
           (11,12),
           (11,13),
           (12,13)]   
    G=nx.Graph(edges)
    pts = set(biconnected.articulation_points(G))
    assert_equal(pts,set([4,6,7,8,9]))
    comps = list(biconnected.biconnected_component_edges(G))
    answer = [
        [(3,4),(15,3),(10,15),(10,4),(2,10),(4,2)],
        [(13,12),(13,8),(11,13),(12,11),(8,12)],
        [(9,8)],
        [(7,9)],
        [(4,7)],
        [(6,4)],
        [(14,0),(5,1),(5,0),(14,5),(14,1),(6,14),(6,0),(1,6),(0,1)],
        ]
    assert_components_equal(comps,answer)

def test_biconnected_components2():
    G=nx.Graph()
    G.add_cycle('ABC')
    G.add_cycle('CDE')
    G.add_cycle('FIJHG')
    G.add_cycle('GIJ')
    G.add_edge('E','G')
    comps = list(biconnected.biconnected_component_edges(G))
    answer = [
        [tuple('GF'),tuple('FI'),tuple('IG'),tuple('IJ'),tuple('JG'),tuple('JH'),tuple('HG')],
        [tuple('EG')],
        [tuple('CD'),tuple('DE'),tuple('CE')],
        [tuple('AB'),tuple('BC'),tuple('AC')]
        ]
    assert_components_equal(comps,answer)

def test_biconnected_davis():
    D = nx.davis_southern_women_graph()
    bcc = list(biconnected.biconnected_components(D))[0]
    assert_true(set(D) == bcc) # All nodes in a giant bicomponent
    # So no articulation points
    assert_equal(list(biconnected.articulation_points(D)),[])

def test_biconnected_karate():
    K = nx.karate_club_graph()
    answer = [set([0, 1, 2, 3, 7, 8, 9, 12, 13, 14, 15, 17, 18, 19,
                20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]),
                set([0, 4, 5, 6, 10, 16]),
                set([0, 11])]
    bcc = list(biconnected.biconnected_components(K))
    bcc.sort(key=len, reverse=True)
    assert_true(list(biconnected.biconnected_components(K)) == answer)
    assert_equal(list(biconnected.articulation_points(K)),[0])

def test_biconnected_eppstein():
    # tests from http://www.ics.uci.edu/~eppstein/PADS/Biconnectivity.py
    G1 = nx.Graph({
        0: [1,2,5],
        1: [0,5],
        2: [0,3,4],
        3: [2,4,5,6],
        4: [2,3,5,6],
        5: [0,1,3,4],
        6: [3,4]})
    G2 = nx.Graph({
        0: [2,5],
        1: [3,8],
        2: [0,3,5],
        3: [1,2,6,8],
        4: [7],
        5: [0,2],
        6: [3,8],
        7: [4],
        8: [1,3,6]})
    assert_true(biconnected.is_biconnected(G1))
    assert_false(biconnected.is_biconnected(G2))
    answer_G2 = [set([1, 3, 6, 8]), set([0, 2, 5]), set([2, 3]), set([4, 7])]
    bcc = list(biconnected.biconnected_components(G2))
    bcc.sort(key=len, reverse=True)
    assert_equal(bcc, answer_G2)
