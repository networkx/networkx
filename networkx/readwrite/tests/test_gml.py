#!/usr/bin/env python
# encoding: utf-8

from ast import literal_eval
import io
from nose.tools import *
from nose import SkipTest
import networkx as nx
from networkx.readwrite.gml import literal_stringizer, literal_destringizer
import os
import tempfile

try:
    unichr
except NameError:
    unichr = chr


class TestGraph(object):

    def setUp(self):
        self.simple_data = """Creator me
Version xx
graph [
 comment "This is a sample graph"
 directed 1
 IsPlanar 1
 pos  [ x 0 y 1 ]
 node [
   id 1
   label "Node 1"
   pos [ x 1 y 1 ]
 ]
 node [
    id 2
    pos [ x 1 y 2 ]
    label "Node 2"
    ]
  node [
    id 3
    label "Node 3"
    pos [ x 1 y 3 ]
  ]
  edge [
    source 1
    target 2
    label "Edge from node 1 to node 2"
    color [line "blue" thickness 3]

  ]
  edge [
    source 2
    target 3
    label "Edge from node 2 to node 3"
  ]
  edge [
    source 3
    target 1
    label "Edge from node 3 to node 1"
  ]
]
"""

    def test_parse_gml(self):
        G = nx.parse_gml(self.simple_data, label='label')
        assert_equals(sorted(G.nodes()),
                      ['Node 1', 'Node 2', 'Node 3'])
        assert_equals([e for e in sorted(G.edges())],
                      [('Node 1', 'Node 2'),
                       ('Node 2', 'Node 3'),
                       ('Node 3', 'Node 1')])

        assert_equals([e for e in sorted(G.edges(data=True))],
                      [('Node 1', 'Node 2',
                        {'color': {'line': 'blue', 'thickness': 3},
                         'label': 'Edge from node 1 to node 2'}),
                       ('Node 2', 'Node 3',
                        {'label': 'Edge from node 2 to node 3'}),
                       ('Node 3', 'Node 1',
                        {'label': 'Edge from node 3 to node 1'})])

    def test_read_gml(self):
        (fd, fname) = tempfile.mkstemp()
        fh = open(fname, 'w')
        fh.write(self.simple_data)
        fh.close()
        Gin = nx.read_gml(fname, label='label')
        G = nx.parse_gml(self.simple_data, label='label')
        assert_equals(sorted(G.nodes(data=True)), sorted(Gin.nodes(data=True)))
        assert_equals(sorted(G.edges(data=True)), sorted(Gin.edges(data=True)))
        os.close(fd)
        os.unlink(fname)

    def test_relabel_duplicate(self):
        data = """
graph
[
	label	""
	directed	1
	node
	[
		id	0
		label	"same"
	]
	node
	[
		id	1
		label	"same"
	]
]
"""
        fh = io.BytesIO(data.encode('UTF-8'))
        fh.seek(0)
        assert_raises(
            nx.NetworkXError, nx.read_gml, fh, label='label')

    def test_tuplelabels(self):
        # https://github.com/networkx/networkx/pull/1048
        # Writing tuple labels to GML failed.
        G = nx.Graph()
        G.add_edge((0, 1), (1, 0))
        data = '\n'.join(nx.generate_gml(G, stringizer=literal_stringizer))
        answer = """graph [
  node [
    id 0
    label "(0,1)"
  ]
  node [
    id 1
    label "(1,0)"
  ]
  edge [
    source 0
    target 1
  ]
]"""
        assert_equal(data, answer)

    def test_quotes(self):
        # https://github.com/networkx/networkx/issues/1061
        # Encoding quotes as HTML entities.
        G = nx.path_graph(1)
        # This is a unicode string (due to the __future__ import)
        # It was decoded from utf-8 since that the encoding of this file.
        attr = 'This is "quoted" and this is a copyright: ' + unichr(169)
        G.node[0]['demo'] = attr
        fobj = tempfile.NamedTemporaryFile()
        nx.write_gml(G, fobj)
        fobj.seek(0)
        # Should be bytes in 2.x and 3.x
        data = fobj.read().strip().decode('ascii')
        answer = """graph [
  name "path_graph(1)"
  node [
    id 0
    label 0
    demo "This is &#34;quoted&#34; and this is a copyright: &#169;"
  ]
]"""
        assert_equal(data, answer)

    def test_graph_types(self):
        for directed in [None, False, True]:
            for multigraph in [None, False, True]:
                gml = 'graph ['
                if directed is not None:
                    gml += ' directed ' + str(int(directed))
                if multigraph is not None:
                    gml += ' multigraph ' + str(int(multigraph))
                gml += ' ]'
                G = nx.parse_gml(gml)
                assert_equal(bool(directed), G.is_directed())
                assert_equal(bool(multigraph), G.is_multigraph())
                gml = 'graph [\n'
                if directed is True:
                    gml += '  directed 1\n'
                if multigraph is True:
                    gml += '  multigraph 1\n'
                gml += ']'
                assert_equal(gml, '\n'.join(nx.generate_gml(G)))

    def test_data_types(self):
        data = [10 ** 20, -2e33, "'", '"&&amp;&&#34;"',
                {(b'\xfd',): '\x7f', unichr(0x4444): (1, 2)}]
        try:
            data.append(unichr(0x14444))  # fails under IronPython
        except ValueError:
            data.append(unichr(0x1444))
        try:
            data.append(literal_eval('{2.3j, 1 - 2.3j, ()}'))  # fails under Python 2.7
        except ValueError:
            data.append([2.3j, 1 - 2.3j, ()])
        G = nx.Graph()
        G.name = data
        G.graph['data'] = data
        G.add_node(0, int=-1, data=dict(data=data))
        G.add_edge(0, 0, float=-2.5, data=data)
        gml = '\n'.join(nx.generate_gml(G, stringizer=literal_stringizer))
        G = nx.parse_gml(gml, destringizer=literal_destringizer)
        assert_equal(data, G.name)
        assert_equal(dict(name=data, data=data), G.graph)
        assert_equal(G.nodes(data=True),
                     [(0, dict(int=-1, data=dict(data=data)))])
        assert_equal(G.edges(data=True), [(0, 0, dict(float=-2.5, data=data))])
