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
        assert_equals(sorted(G.nodes()),\
            [u'n0', u'n1', u'n10', u'n2', u'n3', u'n4', u'n5', u'n6', u'n7', u'n8', u'n9'])
        assert_equals( [sorted(e) for e in sorted(G.edges(keys=True))],\
            [[u'foo', u'n0', u'n2'], [0, u'n1', u'n2'], [0, u'n10', u'n8'], \
             [0, u'n2', u'n3'], [0, u'n3', u'n4'], [0, u'n3', u'n5'], \
             [0, u'n4', u'n6'], [0, u'n5', u'n7'], [0, u'n5', u'n6'], \
             [0, u'n6', u'n8'], [0, u'n10', u'n8'], [0, u'n7', u'n8'], \
             [0, u'n8', u'n9']] )

        G=networkx.parse_graphml(self.attribute_data.split('\n'))
        assert_equals(sorted(G.nodes()),[u'n0', u'n1', u'n2', u'n3', u'n4', u'n5'])
        assert_equals( sorted(G.edges(keys=True)),\
                [(u'n0', u'n1', u'e1'), (u'n0', u'n2', u'e0'), (u'n1', u'n3', u'e2'), \
                 (u'n2', u'n4', u'e4'), (u'n3', u'n2', u'e3'), (u'n3', u'n5', u'e5'), \
                 (u'n5', u'n3', u'e5'), (u'n5', u'n4', u'e6')] )
        assert_equals(sorted(G.nodes(data=True)),\
                [(u'n0', {u'color': u'green', u'id': u'n0'}),\
                (u'n1', {u'color': u'yellow', u'id': u'n1'}),\
                (u'n2', {u'color': u'blue', u'id': u'n2'}),\
                (u'n3', {u'color': u'yellow', u'id': u'n3', u'd3': u'red'}),\
                (u'n4', {u'color': u'yellow', u'id': u'n4'}),\
                (u'n5', {u'color': u'turquoise', u'id': u'n5'})] )
        assert_equals( sorted(G.edges(keys=True,data=True)),\
           [(u'n0', u'n1', u'e1', {u'source': u'n0', u'id': u'e1', u'weight': 1.0, u'target': u'n1'}),\
            (u'n0', u'n2', u'e0', {u'source': u'n0', u'id': u'e0', u'weight': 1.0, u'target': u'n2'}),\
            (u'n1', u'n3', u'e2', {u'source': u'n1', u'id': u'e2', u'weight': 2.0, u'target': u'n3'}),\
            (u'n2', u'n4', u'e4', {u'source': u'n2', u'id': u'e4', u'target': u'n4'}),\
            (u'n3', u'n2', u'e3', {u'source': u'n3', u'id': u'e3', u'target': u'n2'}),\
            (u'n3', u'n5', u'e5', {u'directed': u'false', u'source': u'n3', u'target': u'n5', u'id': u'e5'}),\
            (u'n5', u'n3', u'e5', {u'directed': u'false', u'source': u'n3', u'target': u'n5', u'id': u'e5'}),\
            (u'n5', u'n4', u'e6', {u'source': u'n5', u'id': u'e6', u'weight': 1.1, u'target': u'n4'})] )




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

