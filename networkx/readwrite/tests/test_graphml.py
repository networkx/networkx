#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
import networkx as nx
import io
import tempfile
import os

class TestGraph(object):
    @classmethod
    def setupClass(cls):
        try:
            import xml.etree.ElementTree
        except ImportError:
            raise SkipTest('xml.etree.ElementTree not available.')

    def setUp(self):
        self.simple_directed_data="""<?xml version="1.0" encoding="UTF-8"?>
<!-- This file was written by the JAVA GraphML Library.-->
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <graph id="G" edgedefault="directed">
    <node id="n0"/>
    <node id="n1"/>
    <node id="n2"/>
    <node id="n3"/>
    <node id="n4"/>
    <node id="n5"/>
    <node id="n6"/>
    <node id="n7"/>
    <node id="n8"/>
    <node id="n9"/>
    <node id="n10"/>
    <edge id="foo" source="n0" target="n2"/>
    <edge source="n1" target="n2"/>
    <edge source="n2" target="n3"/>
    <edge source="n3" target="n5"/>
    <edge source="n3" target="n4"/>
    <edge source="n4" target="n6"/>
    <edge source="n6" target="n5"/>
    <edge source="n5" target="n7"/>
    <edge source="n6" target="n8"/>
    <edge source="n8" target="n7"/>
    <edge source="n8" target="n9"/>
  </graph>
</graphml>"""
        self.simple_directed_graph=nx.DiGraph()
        self.simple_directed_graph.add_node('n10')
        self.simple_directed_graph.add_edge('n0','n2',id='foo')
        self.simple_directed_graph.add_edges_from([('n1','n2'),
                                                   ('n2','n3'),
                                                   ('n3','n5'),
                                                   ('n3','n4'),
                                                   ('n4','n6'),
                                                   ('n6','n5'),
                                                   ('n5','n7'),
                                                   ('n6','n8'),
                                                   ('n8','n7'),
                                                   ('n8','n9'),
                                                   ])

        self.simple_directed_fh = \
            io.BytesIO(self.simple_directed_data.encode('UTF-8'))


        self.attribute_data="""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
        http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="d0" for="node" attr.name="color" attr.type="string">
    <default>yellow</default>
  </key>
  <key id="d1" for="edge" attr.name="weight" attr.type="double"/>
  <graph id="G" edgedefault="directed">
    <node id="n0">
      <data key="d0">green</data>
    </node>
    <node id="n1"/>
    <node id="n2">
      <data key="d0">blue</data>
    </node>
    <node id="n3">
      <data key="d0">red</data>
    </node>
    <node id="n4"/>
    <node id="n5">
      <data key="d0">turquoise</data>
    </node>
    <edge id="e0" source="n0" target="n2">
      <data key="d1">1.0</data>
    </edge>
    <edge id="e1" source="n0" target="n1">
      <data key="d1">1.0</data>
    </edge>
    <edge id="e2" source="n1" target="n3">
      <data key="d1">2.0</data>
    </edge>
    <edge id="e3" source="n3" target="n2"/>
    <edge id="e4" source="n2" target="n4"/>
    <edge id="e5" source="n3" target="n5"/>
    <edge id="e6" source="n5" target="n4">
      <data key="d1">1.1</data>
    </edge>
  </graph>
</graphml>
"""
        self.attribute_graph=nx.DiGraph(id='G')
        self.attribute_graph.graph['node_default']={'color':'yellow'}
        self.attribute_graph.add_node('n0',color='green')
        self.attribute_graph.add_node('n2',color='blue')
        self.attribute_graph.add_node('n3',color='red')
        self.attribute_graph.add_node('n4')
        self.attribute_graph.add_node('n5',color='turquoise')
        self.attribute_graph.add_edge('n0','n2',id='e0',weight=1.0)
        self.attribute_graph.add_edge('n0','n1',id='e1',weight=1.0)
        self.attribute_graph.add_edge('n1','n3',id='e2',weight=2.0)
        self.attribute_graph.add_edge('n3','n2',id='e3')
        self.attribute_graph.add_edge('n2','n4',id='e4')
        self.attribute_graph.add_edge('n3','n5',id='e5')
        self.attribute_graph.add_edge('n5','n4',id='e6',weight=1.1)
        self.attribute_fh = io.BytesIO(self.attribute_data.encode('UTF-8'))

        self.simple_undirected_data="""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <graph id="G">
    <node id="n0"/>
    <node id="n1"/>
    <node id="n2"/>
    <node id="n10"/>
    <edge id="foo" source="n0" target="n2"/>
    <edge source="n1" target="n2"/>
    <edge source="n2" target="n3"/>
  </graph>
</graphml>"""
#    <edge source="n8" target="n10" directed="false"/>
        self.simple_undirected_graph=nx.Graph()
        self.simple_undirected_graph.add_node('n10')
        self.simple_undirected_graph.add_edge('n0','n2',id='foo')
        self.simple_undirected_graph.add_edges_from([('n1','n2'),
                                                   ('n2','n3'),
                                                   ])

        self.simple_undirected_fh = io.BytesIO(self.simple_undirected_data.encode('UTF-8'))


    def test_read_simple_directed_graphml(self):
        G=self.simple_directed_graph
        H=nx.read_graphml(self.simple_directed_fh)
        assert_equal(sorted(G.nodes()),sorted(H.nodes()))
        assert_equal(sorted(G.edges()),sorted(H.edges()))
        assert_equal(sorted(G.edges(data=True)),
                     sorted(H.edges(data=True)))
        self.simple_directed_fh.seek(0)

    def test_write_read_simple_directed_graphml(self):
        G=self.simple_directed_graph
        fh=io.BytesIO()
        nx.write_graphml(G,fh)
        fh.seek(0)
        H=nx.read_graphml(fh)
        assert_equal(sorted(G.nodes()),sorted(H.nodes()))
        assert_equal(sorted(G.edges()),sorted(H.edges()))
        assert_equal(sorted(G.edges(data=True)),
                     sorted(H.edges(data=True)))
        self.simple_directed_fh.seek(0)

    def test_read_simple_undirected_graphml(self):
        G=self.simple_undirected_graph
        H=nx.read_graphml(self.simple_undirected_fh)
        assert_equal(sorted(G.nodes()),sorted(H.nodes()))
        assert_equal(
            sorted(sorted(e) for e in G.edges()),
            sorted(sorted(e) for e in H.edges()))
        self.simple_undirected_fh.seek(0)

    def test_read_attribute_graphml(self):
        G=self.attribute_graph
        H=nx.read_graphml(self.attribute_fh)
        assert_equal(sorted(G.nodes(True)),sorted(H.nodes(data=True)))
        ge=sorted(G.edges(data=True))
        he=sorted(H.edges(data=True))
        for a,b in zip(ge,he):
            assert_equal(a,b)
        self.attribute_fh.seek(0)

    def test_directed_edge_in_undirected(self):
        s="""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <graph id="G">
    <node id="n0"/>
    <node id="n1"/>
    <node id="n2"/>
    <edge source="n0" target="n1"/>
    <edge source="n1" target="n2" directed='true'/>
  </graph>
</graphml>"""
        fh = io.BytesIO(s.encode('UTF-8'))
        assert_raises(nx.NetworkXError,nx.read_graphml,fh)

    def test_undirected_edge_in_directed(self):
        s="""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <graph id="G" edgedefault='directed'>
    <node id="n0"/>
    <node id="n1"/>
    <node id="n2"/>
    <edge source="n0" target="n1"/>
    <edge source="n1" target="n2" directed='false'/>
  </graph>
</graphml>"""
        fh = io.BytesIO(s.encode('UTF-8'))
        assert_raises(nx.NetworkXError,nx.read_graphml,fh)

    def test_key_error(self):
        s="""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
        http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="d0" for="node" attr.name="color" attr.type="string">
    <default>yellow</default>
  </key>
  <key id="d1" for="edge" attr.name="weight" attr.type="double"/>
  <graph id="G" edgedefault="directed">
    <node id="n0">
      <data key="d0">green</data>
    </node>
    <node id="n1"/>
    <node id="n2">
      <data key="d0">blue</data>
    </node>
    <edge id="e0" source="n0" target="n2">
      <data key="d2">1.0</data>
    </edge>
  </graph>
</graphml>
"""
        fh = io.BytesIO(s.encode('UTF-8'))
        assert_raises(nx.NetworkXError,nx.read_graphml,fh)

    def test_hyperedge_error(self):
        s="""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
        http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="d0" for="node" attr.name="color" attr.type="string">
    <default>yellow</default>
  </key>
  <key id="d1" for="edge" attr.name="weight" attr.type="double"/>
  <graph id="G" edgedefault="directed">
    <node id="n0">
      <data key="d0">green</data>
    </node>
    <node id="n1"/>
    <node id="n2">
      <data key="d0">blue</data>
    </node>
    <hyperedge id="e0" source="n0" target="n2">
       <endpoint node="n0"/>
       <endpoint node="n1"/>
       <endpoint node="n2"/>
    </hyperedge>
  </graph>
</graphml>
"""
        fh = io.BytesIO(s.encode('UTF-8'))
        assert_raises(nx.NetworkXError,nx.read_graphml,fh)

    # remove test until we get the "name" issue sorted
    # https://networkx.lanl.gov/trac/ticket/544
    def test_default_attribute(self):
        G=nx.Graph()
        G.add_node(1,label=1,color='green')
        G.add_path([0,1,2,3])
        G.add_edge(1,2,weight=3)
        G.graph['node_default']={'color':'yellow'}
        G.graph['edge_default']={'weight':7}
        fh = io.BytesIO()
        nx.write_graphml(G,fh)
        fh.seek(0)
        H=nx.read_graphml(fh,node_type=int)
        assert_equal(sorted(G.nodes()),sorted(H.nodes()))
        assert_equal(
            sorted(sorted(e) for e in G.edges()),
            sorted(sorted(e) for e in H.edges()))
        assert_equal(G.graph,H.graph)

    def test_multigraph_keys(self):
        # test that multigraphs use edge id attributes as key
        pass

    def test_multigraph_to_graph(self):
        # test converting multigraph to graph if no parallel edges are found
        pass

    def test_yfiles_extension(self):
        data="""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
  <!--Created by yFiles for Java 2.7-->
  <key for="graphml" id="d0" yfiles.type="resources"/>
  <key attr.name="url" attr.type="string" for="node" id="d1"/>
  <key attr.name="description" attr.type="string" for="node" id="d2"/>
  <key for="node" id="d3" yfiles.type="nodegraphics"/>
  <key attr.name="Description" attr.type="string" for="graph" id="d4">
    <default/>
  </key>
  <key attr.name="url" attr.type="string" for="edge" id="d5"/>
  <key attr.name="description" attr.type="string" for="edge" id="d6"/>
  <key for="edge" id="d7" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <node id="n0">
      <data key="d3">
        <y:ShapeNode>
          <y:Geometry height="30.0" width="30.0" x="125.0" y="100.0"/>
          <y:Fill color="#FFCC00" transparent="false"/>
          <y:BorderStyle color="#000000" type="line" width="1.0"/>
          <y:NodeLabel alignment="center" autoSizePolicy="content" borderDistance="0.0" fontFamily="Dialog" fontSize="13" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="19.1328125" modelName="internal" modelPosition="c" textColor="#000000" visible="true" width="12.27099609375" x="8.864501953125" y="5.43359375">1</y:NodeLabel>
          <y:Shape type="rectangle"/>
        </y:ShapeNode>
      </data>
    </node>
    <node id="n1">
      <data key="d3">
        <y:ShapeNode>
          <y:Geometry height="30.0" width="30.0" x="183.0" y="205.0"/>
          <y:Fill color="#FFCC00" transparent="false"/>
          <y:BorderStyle color="#000000" type="line" width="1.0"/>
          <y:NodeLabel alignment="center" autoSizePolicy="content" borderDistance="0.0" fontFamily="Dialog" fontSize="13" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="19.1328125" modelName="internal" modelPosition="c" textColor="#000000" visible="true" width="12.27099609375" x="8.864501953125" y="5.43359375">2</y:NodeLabel>
          <y:Shape type="rectangle"/>
        </y:ShapeNode>
      </data>
    </node>
    <edge id="e0" source="n0" target="n1">
      <data key="d7">
        <y:PolyLineEdge>
          <y:Path sx="0.0" sy="0.0" tx="0.0" ty="0.0"/>
          <y:LineStyle color="#000000" type="line" width="1.0"/>
          <y:Arrows source="none" target="standard"/>
          <y:BendStyle smoothed="false"/>
        </y:PolyLineEdge>
      </data>
    </edge>
  </graph>
  <data key="d0">
    <y:Resources/>
  </data>
</graphml>
"""
        fh = io.BytesIO(data.encode('UTF-8'))
        G=nx.read_graphml(fh)
        assert_equal(G.edges(),[('n0','n1')])
        assert_equal(G['n0']['n1']['id'],'e0')
        assert_equal(G.node['n0']['label'],'1')
        assert_equal(G.node['n1']['label'],'2')

    def test_unicode(self):
        G = nx.Graph()
        try: # Python 3.x
            name1 = chr(2344) + chr(123) + chr(6543)
            name2 = chr(5543) + chr(1543) + chr(324)
            node_type=str
        except ValueError: # Python 2.6+
            name1 = unichr(2344) + unichr(123) + unichr(6543)
            name2 = unichr(5543) + unichr(1543) + unichr(324)
            node_type=unicode
        G.add_edge(name1, 'Radiohead', attr_dict={'foo': name2})
        fd, fname = tempfile.mkstemp()
        nx.write_graphml(G, fname)
        H = nx.read_graphml(fname,node_type=node_type)
        assert_equal(G.adj, H.adj)
        os.close(fd)
        os.unlink(fname)


    def test_bool(self):
        s="""<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
        http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="d0" for="node" attr.name="test" attr.type="boolean">
    <default>false</default>
  </key>
  <graph id="G" edgedefault="directed">
    <node id="n0">
      <data key="d0">True</data>
    </node>
    <node id="n1"/>
    <node id="n2">
      <data key="d0">False</data>
    </node>
    <node id="n3">
      <data key="d0">true</data>
    </node>
    <node id="n4">
      <data key="d0">false</data>
    </node>


  </graph>
</graphml>
"""
        fh = io.BytesIO(s.encode('UTF-8'))
        G=nx.read_graphml(fh)
        assert_equal(G.node['n0']['test'],True)
        assert_equal(G.node['n2']['test'],False)
