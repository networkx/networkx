#!/usr/bin/env python
from nose.tools import *
from nose import SkipTest
import networkx as nx
import io

class TestGEXF(object):
    @classmethod
    def setupClass(cls):
        try:
            import xml.etree.ElementTree
        except ImportError:
            raise SkipTest('xml.etree.ElementTree not available.')

    def setUp(self):
        self.simple_directed_data="""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.1draft" version="1.1">
    <graph mode="static" defaultedgetype="directed">
        <nodes>
            <node id="0" label="Hello" />
            <node id="1" label="Word" />
        </nodes>
        <edges>
            <edge id="0" source="0" target="1" />
        </edges>
    </graph>
</gexf>
"""
        self.simple_directed_graph=nx.DiGraph()
        self.simple_directed_graph.add_node('0',label='Hello')
        self.simple_directed_graph.add_node('1',label='World')
        self.simple_directed_graph.add_edge('0','1',id='0')
                            
        self.simple_directed_fh = \
            io.BytesIO(self.simple_directed_data.encode('UTF-8'))


        self.attribute_data="""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.1draft" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.gexf.net/1.1draft http://www.gexf.net/1.1draft/gexf.xsd" version="1.1">
  <meta lastmodifieddate="2009-03-20">
    <creator>Gephi.org</creator>
    <description>A Web network</description>
  </meta>
  <graph defaultedgetype="directed">
    <attributes class="node">
      <attribute id="0" title="url" type="string"/>
      <attribute id="1" title="indegree" type="integer"/>
      <attribute id="2" title="frog" type="boolean">
        <default>true</default>
      </attribute>
    </attributes>
    <nodes>
      <node id="0" label="Gephi">
        <attvalues>
          <attvalue for="0" value="http://gephi.org"/>
          <attvalue for="1" value="1"/>
        </attvalues>
      </node>
      <node id="1" label="Webatlas">
        <attvalues>
          <attvalue for="0" value="http://webatlas.fr"/>
          <attvalue for="1" value="2"/>
        </attvalues>
      </node>
      <node id="2" label="RTGI">
        <attvalues>
          <attvalue for="0" value="http://rtgi.fr"/>
          <attvalue for="1" value="1"/>
        </attvalues>
      </node>
      <node id="3" label="BarabasiLab">
        <attvalues>
          <attvalue for="0" value="http://barabasilab.com"/>
          <attvalue for="1" value="1"/>
          <attvalue for="2" value="false"/>
        </attvalues>
      </node>
    </nodes>
    <edges>
      <edge id="0" source="0" target="1"/>
      <edge id="1" source="0" target="2"/>
      <edge id="2" source="1" target="0"/>
      <edge id="3" source="2" target="1"/>
      <edge id="4" source="0" target="3"/>
    </edges>
  </graph>
</gexf>
"""
        self.attribute_graph=nx.DiGraph()
        self.attribute_graph.graph['node_default']={'frog':True}
        self.attribute_graph.add_node('0',
                                      label='Gephi',
                                      url='http://gephi.org',
                                      indegree=1)
        self.attribute_graph.add_node('1',
                                      label='Webatlas',
                                      url='http://webatlas.fr',
                                      indegree=2)

        self.attribute_graph.add_node('2',
                                      label='RTGI',
                                      url='http://rtgi.fr',
                                      indegree=1)

        self.attribute_graph.add_node('3',
                                      label='BarabasiLab',
                                      url='http://barabasilab.com',
                                      indegree=1,
                                      frog=False)
        self.attribute_graph.add_edge('0','1',id='0')
        self.attribute_graph.add_edge('0','2',id='1')
        self.attribute_graph.add_edge('1','0',id='2')
        self.attribute_graph.add_edge('2','1',id='3')
        self.attribute_graph.add_edge('0','3',id='4')
        self.attribute_fh = io.BytesIO(self.attribute_data.encode('UTF-8'))

        self.simple_undirected_data="""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.1draft" version="1.1">
    <graph mode="static" defaultedgetype="undirected">
        <nodes>
            <node id="0" label="Hello" />
            <node id="1" label="Word" />
        </nodes>
        <edges>
            <edge id="0" source="0" target="1" />
        </edges>
    </graph>
</gexf>
"""
        self.simple_undirected_graph=nx.Graph()
        self.simple_undirected_graph.add_node('0',label='Hello')
        self.simple_undirected_graph.add_node('1',label='World')
        self.simple_undirected_graph.add_edge('0','1',id='0')

        self.simple_undirected_fh = io.BytesIO(self.simple_undirected_data.encode('UTF-8'))


    def test_read_simple_directed_graphml(self):
        G=self.simple_directed_graph
        H=nx.read_gexf(self.simple_directed_fh)
        assert_equal(sorted(G.nodes()),sorted(H.nodes()))
        assert_equal(sorted(G.edges()),sorted(H.edges()))
        assert_equal(sorted(G.edges(data=True)),
                     sorted(H.edges(data=True)))
        self.simple_directed_fh.seek(0)

    def test_write_read_simple_directed_graphml(self):
        G=self.simple_directed_graph
        fh=io.BytesIO()
        nx.write_gexf(G,fh)
        fh.seek(0)
        H=nx.read_gexf(fh)
        assert_equal(sorted(G.nodes()),sorted(H.nodes()))
        assert_equal(sorted(G.edges()),sorted(H.edges()))
        assert_equal(sorted(G.edges(data=True)),
                     sorted(H.edges(data=True)))
        self.simple_directed_fh.seek(0)

    def test_read_simple_undirected_graphml(self):
        G=self.simple_undirected_graph
        H=nx.read_gexf(self.simple_undirected_fh)
        assert_equal(sorted(G.nodes()),sorted(H.nodes()))
        assert_equal(
            sorted(sorted(e) for e in G.edges()),
            sorted(sorted(e) for e in H.edges()))
        self.simple_undirected_fh.seek(0)

    def test_read_attribute_graphml(self):
        G=self.attribute_graph
        H=nx.read_gexf(self.attribute_fh)
        assert_equal(sorted(G.nodes(True)),sorted(H.nodes(data=True)))
        ge=sorted(G.edges(data=True))
        he=sorted(H.edges(data=True))
        for a,b in zip(ge,he):
            assert_equal(a,b)
        self.attribute_fh.seek(0)

    def test_directed_edge_in_undirected(self):
        s="""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.1draft" version="1.1">
    <graph mode="static" defaultedgetype="undirected">
        <nodes>
            <node id="0" label="Hello" />
            <node id="1" label="Word" />
        </nodes>
        <edges>
            <edge id="0" source="0" target="1" type="directed"/>
        </edges>
    </graph>
</gexf>
"""
        fh = io.BytesIO(s.encode('UTF-8'))
        assert_raises(nx.NetworkXError,nx.read_gexf,fh)
    
    def test_undirected_edge_in_directed(self):
        s="""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.1draft" version="1.1">
    <graph mode="static" defaultedgetype="directed">
        <nodes>
            <node id="0" label="Hello" />
            <node id="1" label="Word" />
        </nodes>
        <edges>
            <edge id="0" source="0" target="1" type="undirected"/>
        </edges>
    </graph>
</gexf>
"""
        fh = io.BytesIO(s.encode('UTF-8'))
        assert_raises(nx.NetworkXError,nx.read_gexf,fh)


    def test_key_error(self):
        s="""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.1draft" version="1.1">
    <graph mode="static" defaultedgetype="directed">
        <nodes>
            <node id="0" label="Hello">
	      <attvalues>
		<attvalue for='0' value='1'/>
              </attvalues>		
            </node>
            <node id="1" label="Word" />
        </nodes>
        <edges>
            <edge id="0" source="0" target="1" type="undirected"/>
        </edges>
    </graph>
</gexf>
"""
        fh = io.BytesIO(s.encode('UTF-8'))
        assert_raises(nx.NetworkXError,nx.read_gexf,fh)

    def test_relabel(self):
        s="""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.1draft" version="1.1">
    <graph mode="static" defaultedgetype="directed">
        <nodes>
            <node id="0" label="Hello" />
            <node id="1" label="Word" />
        </nodes>
        <edges>
            <edge id="0" source="0" target="1"/>
        </edges>
    </graph>
</gexf>
"""
        fh = io.BytesIO(s.encode('UTF-8'))
        G=nx.read_gexf(fh,relabel=True)
        assert_equal(sorted(G.nodes()),["Hello","Word"])


    def test_default_attribute(self):
        G=nx.Graph()
        G.add_node(1,label='1',color='green')
        G.add_path([0,1,2,3])
        G.add_edge(1,2,foo=3)
        G.graph['node_default']={'color':'yellow'}
        G.graph['edge_default']={'foo':7}
        fh = io.BytesIO()
        nx.write_gexf(G,fh)
        fh.seek(0)
        H=nx.read_gexf(fh,node_type=int)
        assert_equal(sorted(G.nodes()),sorted(H.nodes()))
        assert_equal(
            sorted(sorted(e) for e in G.edges()),
            sorted(sorted(e) for e in H.edges()))
        assert_equal(G.graph,H.graph)
    
