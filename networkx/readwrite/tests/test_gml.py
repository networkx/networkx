#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import io
from nose.tools import *
from nose import SkipTest
import networkx

class TestGraph(object):
    @classmethod
    def setupClass(cls):
        global pyparsing
        try:
            import pyparsing
        except ImportError:
            try:
                import matplotlib.pyparsing as pyparsing
            except:
                raise SkipTest('gml test: pyparsing not available.')

    def setUp(self):
        self.simple_data="""Creator me
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
        G=networkx.parse_gml(self.simple_data,relabel=True)
        assert_equals(sorted(G.nodes()),\
                          ['Node 1', 'Node 2', 'Node 3'])
        assert_equals( [e for e in sorted(G.edges())],\
                           [('Node 1', 'Node 2'),
                            ('Node 2', 'Node 3'),
                            ('Node 3', 'Node 1')])

        assert_equals( [e for e in sorted(G.edges(data=True))],\
                           [('Node 1', 'Node 2',
                             {'color': {'line': 'blue', 'thickness': 3},
                              'label': 'Edge from node 1 to node 2'}),
                            ('Node 2', 'Node 3',
                             {'label': 'Edge from node 2 to node 3'}),
                            ('Node 3', 'Node 1',
                             {'label': 'Edge from node 3 to node 1'})])


    def test_read_gml(self):
        import os,tempfile
        (fd,fname)=tempfile.mkstemp()
        fh=open(fname,'w')
        fh.write(self.simple_data)
        fh.close()
        Gin=networkx.read_gml(fname,relabel=True)
        G=networkx.parse_gml(self.simple_data,relabel=True)
        assert_equals( sorted(G.nodes(data=True)), sorted(Gin.nodes(data=True)))
        assert_equals( sorted(G.edges(data=True)), sorted(Gin.edges(data=True)))
        os.close(fd)
        os.unlink(fname)

    def test_relabel_duplicate(self):
        data="""
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
        assert_raises(networkx.NetworkXError,networkx.read_gml,fh,relabel=True)

    def test_bool(self):
        G=networkx.Graph()
        G.add_node(1,on=True)
        G.add_edge(1,2,on=False)
        data = '\n'.join(list(networkx.generate_gml(G)))
        answer ="""graph [
  node [
    id 0
    label "1"
    on 1
  ]
  node [
    id 1
    label "2"
  ]
  edge [
    source 0
    target 1
    on 0
  ]
]"""
        assert_equal(data,answer)


    def test_tuplelabels(self):
        # https://github.com/networkx/networkx/pull/1048
        # Writing tuple labels to GML failed.
        G = networkx.Graph()
        G.add_edge((0,1), (1,0))
        data = '\n'.join(list(networkx.generate_gml(G)))
        answer = """graph [
  node [
    id 0
    label "(0, 1)"
  ]
  node [
    id 1
    label "(1, 0)"
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
        import tempfile
        G = networkx.path_graph(1)
        # This is a unicode string (due to the __future__ import)
        # It was decoded from utf-8 since that the encoding of this file.
        attr = 'This is "quoted" and this is a copyright: ©'  # u'\xa9'
        G.node[0]['demo'] = attr
        fobj = tempfile.NamedTemporaryFile()
        networkx.write_gml(G, fobj)
        fobj.seek(0)
        # Should be bytes in 2.x and 3.x
        data = fobj.read().strip()
        answer = b"""graph [
  name "path_graph(1)"
  node [
    id 0
    label "0"
    demo "This is &quot;quoted&quot; and this is a copyright: &#169;"
  ]
]"""
        assert_equal(data, answer)
