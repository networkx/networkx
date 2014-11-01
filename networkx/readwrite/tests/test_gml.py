#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals

import io
from nose.tools import *
import networkx

class TestGraph(object):

    def setUp(self):
        self.simple_data="""graph [
           comment "This is a sample graph"
           directed 1
           IsPlanar 1
           pos  [ x 0 y 1 ]
           node [
             id 1
             label "Node 1"
             pos [ x 1 y 1 ]
             features 0
             features 1
           ]

           NOTE "this"
           # AND
           NOTE "this"

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

        self.gml_without_graph = """ [
            name "G1"
            node [
              id 1
            node []
          ]"""

        self.gml_missing_source_graph = """graph[
            node[]
            node[]
            edge[
              target 1
            ]
          ]"""

        self.gml_missing_target_graph = """graph[
            node[]
            node[]
            edge[
              source 1
            ]
          ]"""

    def test_parse_gml(self):
        graph = {
            'comment': "This is a sample graph",
            'IsPlanar': 1,
            'pos': { 'x': 0, 'y': 1 },
            'NOTE': ['this', 'this']
        }
        node_ids = [
            (1, {'label': "Node 1",
                 'pos': { 'x': 1, 'y': 1 },
                 'features': [0, 1] }),
            (2, {'label': "Node 2",
                 'pos': { 'x': 1, 'y': 2 }}),
            (3, {'label': "Node 3",
                 'pos': { 'x': 1, 'y': 3 }})
        ]
        e12 = {'label': 'Edge from node 1 to node 2',
               'color': {'line': 'blue', 'thickness': 3}}
        e23 = {'label': 'Edge from node 2 to node 3'}
        e31 = {'label': 'Edge from node 3 to node 1'}

        G = networkx.parse_gml(self.simple_data)
        for k, v in G.graph.items(): assert_equals(v, graph[k])
        assert_equals(node_ids[0][1], G.node["Node 1"])
        assert_equals(node_ids[1][1], G.node["Node 2"])
        assert_equals(node_ids[2][1], G.node["Node 3"])
        assert_equals(e12, G.edge["Node 1"]["Node 2"])
        assert_equals(e23, G.edge["Node 2"]["Node 3"])
        assert_equals(e31, G.edge["Node 3"]["Node 1"])

        G = networkx.parse_gml(self.simple_data, relabel=False)
        for k, v in G.graph.items(): assert_equals(v, graph[k])
        for i, (n, d) in enumerate(G.nodes_iter(data=True)):
            assert_equals(n, node_ids[i][0])
            assert_equals(d, node_ids[i][1])

        G = networkx.parse_gml("graph[]")
        assert_equals(0, len(G))
        assert_equals(0, len(G.edge))


    @raises(SyntaxError)
    def test_missing_graph_parse_gml(self):
        networkx.parse_gml(self.gml_without_graph)


    @raises(networkx.NetworkXError)
    def test_missing_source_for_edge_parse_gml(self):
        networkx.parse_gml(self.gml_missing_source_graph)


    @raises(networkx.NetworkXError)
    def test_missing_target_for_edge_parse_gml(self):
        networkx.parse_gml(self.gml_missing_target_graph)


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
              label ""
              directed	1
              node
              [
                id 0
                label "same"
              ]
              node
              [
                id 1
                label "same"
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
        data = networkx.generate_gml(G)
        answer ="""graph [
  node [
    id 1
    on 1
  ]
  node [
    id 2
  ]
  edge [
    source 1
    target 2
    on 0
  ]
]"""
        assert_equal(data,answer)


    def test_tuplelabels(self):
        # https://github.com/networkx/networkx/pull/1048
        # Writing tuple labels to GML failed.
        G = networkx.Graph()
        G.add_edge((0,1), (1,0))
        data = networkx.generate_gml(G)
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
        assert_equal(answer, data)


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
    demo "This is &quot;quoted&quot; and this is a copyright: &copy;"
  ]
]"""
        assert_equal(data, answer)
        G = networkx.read_gml(fobj.name)
        assert_equal('path_graph(1)', G.graph['name'])
        assert_equal(1, len(G))
        assert_equal(G.node[0], {'demo': 'This is "quoted" and this is a copyright: ©'})


    def test_generate_gml_directed_attribute(self):
        gml = """graph [
  directed 1
]"""
        G = networkx.MultiDiGraph()
        assert_equal(gml, networkx.generate_gml(G))
        gml = """graph [
]"""
        G = networkx.MultiGraph()
        assert_equal(gml, networkx.generate_gml(G))


    # def test_parse_gml_directed_attribute(self):
    #     gml = "graph []"
    #     G = networkx.parse_gml(gml)
    #     assert(isinstance(G, networkx.Graph))
    #     assert_false(isinstance(G, networkx.DiGraph))
    #     assert_false(isinstance(G, networkx.MultiGraph))
    #     gml = "graph [directed 1 node[] node[] edge[source 0 target 1]]"
    #     G = networkx.parse_gml(gml, relabel=False)
    #     assert(isinstance(G, networkx.DiGraph))
    #     assert_equal({0: {1: {}}, 1: {}}, G.edge)
    #     assert_false(isinstance(G, networkx.MultiDiGraph))
    #     gml = """graph [
    #         node []
    #         node []
    #         edge [source 0 target 1]
    #         edge [source 0 target 1]
    #     ]"""
    #     G = networkx.parse_gml(gml, relabel=False)
    #     assert(isinstance(G, networkx.MultiGraph))
    #     assert_false(isinstance(G, networkx.MultiDiGraph))
    #     gml = """graph [
    #         directed 1
    #         node []
    #         node []
    #         edge [source 0 target 1]
    #         edge [source 0 target 1]
    #     ]"""
    #     G = networkx.parse_gml(gml, relabel=False)
    #     assert(isinstance(G, networkx.MultiDiGraph))

    def test_parse_gml_graph_type(self):
        gml = """graph [
            node []
            node []
            edge [source 0 target 1]
        ]"""
        G = networkx.parse_gml(gml, relabel=False)
        assert(isinstance(G, networkx.Graph))
        assert_equal({0: {1: {}}, 1: {0: {}}}, G.edge)
        assert_false(isinstance(G, (networkx.DiGraph, networkx.MultiGraph)))


    def test_parse_gml_digraph_type(self):
        gml = """graph [
            node []

            directed 1

            node []
            edge [source 0 target 1]
        ]"""
        G = networkx.parse_gml(gml, relabel=False)
        assert(isinstance(G, networkx.DiGraph))
        assert_equal({0: {1: {}}, 1: {}}, G.edge)
        assert_false(isinstance(G, (networkx.MultiGraph, networkx.MultiDiGraph)))


    def test_parse_gml_multigraph_type(self):
        gml = """graph [
            node []
            node []
            edge [source 0 target 1]
            edge [source 0 target 1]
        ]"""
        G = networkx.parse_gml(gml, relabel=False)
        assert_equal({0: {1: {0: {}, 1: {}}}, 1: {0: {0: {}, 1: {}}}}, G.edge)
        assert(isinstance(G, networkx.MultiGraph))
        assert_false(isinstance(G, networkx.MultiDiGraph))


    def test_parse_gml_multidigraph_type(self):
        gml = """graph [
            directed 1
            node []
            node []
            edge [source 0 target 1]
            edge [source 0 target 1]
        ]"""
        G = networkx.parse_gml(gml, relabel=False)
        assert(isinstance(G, networkx.MultiDiGraph))
        assert_equal({0: {1: {0: {}, 1: {}}}, 1: {}}, G.edge)

