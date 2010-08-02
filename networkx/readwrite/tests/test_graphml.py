#!/usr/bin/env python
import copy
import unittest
from nose.tools import *
import networkx

class TestGraph(object):
    def setUp(self):
        self.simple_data="""<?xml version="1.0" encoding="UTF-8"?>
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
    <edge source="n8" target="n10" directed="false"/>
  </graph>
</graphml>"""

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
      <data key="d3">red</data>
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
    <edge id="e5" source="n3" target="n5" directed="false"/>
    <edge id="e6" source="n5" target="n4">
      <data key="d1">1.1</data>
    </edge>
  </graph>
</graphml>
"""

    def test_parse_graphml(self):
        G=networkx.parse_graphml(self.simple_data)
        assert_equals(sorted(G.nodes()),
            ['n0', 'n1', 'n10', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8', 'n9'])
        
        assert_equals( [set(e) for e in sorted(G.edges(keys=True))],
            [set(['foo', 'n0', 'n2']), set([0, 'n1', 'n2']),
             set([0, 'n10', 'n8']), set([0, 'n2', 'n3']),
             set([0, 'n3', 'n4']), set([0, 'n3', 'n5']),
             set([0, 'n4', 'n6']), set([0, 'n5', 'n7']), set([0, 'n5', 'n6']),
             set([0, 'n6', 'n8']), set([0, 'n10', 'n8']), set([0, 'n7', 'n8']),
             set([0, 'n8', 'n9'])] )

        G=networkx.parse_graphml(self.attribute_data.split('\n'))
        assert_equals(sorted(G.nodes()),['n0', 'n1', 'n2', 'n3', 'n4', 'n5'])
        assert_equals( sorted(G.edges(keys=True)),\
                [('n0', 'n1', 'e1'), ('n0', 'n2', 'e0'), ('n1', 'n3', 'e2'), \
                 ('n2', 'n4', 'e4'), ('n3', 'n2', 'e3'), ('n3', 'n5', 'e5'), \
                 ('n5', 'n3', 'e5'), ('n5', 'n4', 'e6')] )
        assert_equals(sorted(G.nodes(data=True)),\
                [('n0', {'color': 'green', 'id': 'n0'}),\
                ('n1', {'color': 'yellow', 'id': 'n1'}),\
                ('n2', {'color': 'blue', 'id': 'n2'}),\
                ('n3', {'color': 'yellow', 'id': 'n3', 'd3': 'red'}),\
                ('n4', {'color': 'yellow', 'id': 'n4'}),\
                ('n5', {'color': 'turquoise', 'id': 'n5'})] )
        assert_equals( sorted(G.edges(keys=True,data=True)),\
           [('n0', 'n1', 'e1', {'source': 'n0', 'id': 'e1', 'weight': 1.0, 'target': 'n1'}),\
            ('n0', 'n2', 'e0', {'source': 'n0', 'id': 'e0', 'weight': 1.0, 'target': 'n2'}),\
            ('n1', 'n3', 'e2', {'source': 'n1', 'id': 'e2', 'weight': 2.0, 'target': 'n3'}),\
            ('n2', 'n4', 'e4', {'source': 'n2', 'id': 'e4', 'target': 'n4'}),\
            ('n3', 'n2', 'e3', {'source': 'n3', 'id': 'e3', 'target': 'n2'}),\
            ('n3', 'n5', 'e5', {'directed': 'false', 'source': 'n3', 'target': 'n5', 'id': 'e5'}),\
            ('n5', 'n3', 'e5', {'directed': 'false', 'source': 'n3', 'target': 'n5', 'id': 'e5'}),\
            ('n5', 'n4', 'e6', {'source': 'n5', 'id': 'e6', 'weight': 1.1, 'target': 'n4'})] )




    def test_read_graphml(self):
        import os,tempfile
        (fd,fname)=tempfile.mkstemp()
        fh=open(fname,'w')
        fh.write(self.simple_data)
        fh.close()
        Gin=networkx.read_graphml(fname)
        G=networkx.parse_graphml(self.simple_data)
        assert_equals( sorted(G.nodes(data=True)), sorted(Gin.nodes(data=True)))
        assert_equals( sorted(G.edges(data=True)), sorted(Gin.edges(data=True)))
        os.close(fd)
        os.unlink(fname)

