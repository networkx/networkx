
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

