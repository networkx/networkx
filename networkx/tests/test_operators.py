
import os, tempfile
from nose import SkipTest
from nose.tools import assert_raises, assert_true, assert_false, assert_equal

import networkx as nx

def test_union():
    g = nx.Graph()
    g.add_node(0, x=4)
    g.add_node(1, x=5)
    g.add_edge(0, 1, size=5)
    g.graph['name'] = 'g'

    h = g.copy()
    h.graph['name'] = 'h'
    h.graph['attr'] = 'attr'
    h.node[0]['x'] = 7

    gh = nx.union(g, h, rename=('g', 'h'))
    assert_equal( set(gh.nodes()) , set(['h0', 'h1', 'g0', 'g1']) )
    for n in gh:
        graph, node = n
        assert_equal( gh.node[n], eval(graph).node[int(node)] )

    for k,v in gh.graph.items():
        assert_equal( v, (g.graph.get(k), h.graph.get(k)) )


def test_intersection():
    g = nx.Graph()
    g.add_node(0, x=4)
    g.add_node(1, x=5)
    g.add_edge(0, 1, size=5)
    g.graph['name'] = 'g'

    h = g.copy()
    h.graph['name'] = 'h'
    h.graph['attr'] = 'attr'
    h.node[0]['x'] = 7

    gh = nx.intersection(g, h)
    assert_equal( set(gh.nodes()) , set(g.nodes()) )
    assert_equal( set(gh.nodes()) , set(h.nodes()) )
    assert_equal( sorted(gh.edges()) , sorted(g.edges()) )

    h.remove_node(0)
    assert_raises(nx.NetworkXError, nx.intersection, g, h)



def test_intersection_multigraph():
    g = nx.MultiGraph()
    g.add_edge(0, 1, key=0)
    g.add_edge(0, 1, key=1)
    g.add_edge(0, 1, key=2)
    h = nx.MultiGraph()
    h.add_edge(0, 1, key=0)
    h.add_edge(0, 1, key=3)
    gh = nx.intersection(g, h)
    assert_equal( set(gh.nodes()) , set(g.nodes()) )
    assert_equal( set(gh.nodes()) , set(h.nodes()) )
    assert_equal( sorted(gh.edges()) , [(0,1)] )
    assert_equal( sorted(gh.edges(keys=True)) , [(0,1,0)] )

def test_difference():
    g = nx.Graph()
    g.add_node(0, x=4)
    g.add_node(1, x=5)
    g.add_edge(0, 1, size=5)
    g.graph['name'] = 'g'

    h = g.copy()
    h.graph['name'] = 'h'
    h.graph['attr'] = 'attr'
    h.node[0]['x'] = 7

    gh = nx.difference(g, h)
    assert_equal( set(gh.nodes()) , set(g.nodes()) )
    assert_equal( set(gh.nodes()) , set(h.nodes()) )
    assert_equal( sorted(gh.edges()) , [])

    h.remove_node(0)
    assert_raises(nx.NetworkXError, nx.intersection, g, h)

def test_difference_multigraph():
    g = nx.MultiGraph()
    g.add_edge(0, 1, key=0)
    g.add_edge(0, 1, key=1)
    g.add_edge(0, 1, key=2)
    h = nx.MultiGraph()
    h.add_edge(0, 1, key=0)
    h.add_edge(0, 1, key=3)
    gh = nx.difference(g, h)
    assert_equal( set(gh.nodes()) , set(g.nodes()) )
    assert_equal( set(gh.nodes()) , set(h.nodes()) )
    assert_equal( sorted(gh.edges()) , [(0,1)] )
    assert_equal( sorted(gh.edges(keys=True)) , [(0,1,3)] )


def test_symmetric_difference_multigraph():
    g = nx.MultiGraph()
    g.add_edge(0, 1, key=0)
    g.add_edge(0, 1, key=1)
    g.add_edge(0, 1, key=2)
    h = nx.MultiGraph()
    h.add_edge(0, 1, key=0)
    h.add_edge(0, 1, key=3)
    gh = nx.symmetric_difference(g, h)
    assert_equal( set(gh.nodes()) , set(g.nodes()) )
    assert_equal( set(gh.nodes()) , set(h.nodes()) )
    assert_equal( sorted(gh.edges()) , 3*[(0,1)] )
    assert_equal( sorted(sorted(e) for e in gh.edges(keys=True)), 
                  [[0,1,1],[0,1,2],[0,1,3]] )

def test_relabel_nodes():
    pass

def test_compose():
    pass

def test_cartesian_product():
    pass

def test_create_empty_copy():
    pass
