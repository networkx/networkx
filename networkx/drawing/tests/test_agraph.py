"""
    Unit tests for PyGraphviz intefaace.
"""

import os
import tempfile

from nose import SkipTest
from nose.tools import assert_true

import networkx as nx

class TestAGraph(object):
    @classmethod
    def setupClass(cls):
        global pygraphviz
        try:
            import pygraphviz
        except ImportError:
            raise SkipTest('PyGraphviz not available.')

    def build_graph(self, G):
        G.add_edge('A','B')
        G.add_edge('A','C')
        G.add_edge('A','C')
        G.add_edge('B','C')
        G.add_edge('A','D')
        G.add_node('E')
        return G

    def assert_equal(self, G1, G2):
        assert_true( sorted(G1.nodes())==sorted(G2.nodes()) )
        assert_true( sorted(G1.edges())==sorted(G2.edges()) )


    def agraph_checks(self, G):
        G = self.build_graph(G)
        A=nx.to_agraph(G)
        H=nx.from_agraph(A)
        self.assert_equal(G, H)


        fname=tempfile.mktemp()
        nx.drawing.nx_agraph.write_dot(H,fname)
        Hin=nx.drawing.nx_agraph.read_dot(fname)
        os.unlink(fname)
        self.assert_equal(H,Hin)
       

        (fd,fname)=tempfile.mkstemp()
        fh=open(fname,'w')
        nx.drawing.nx_agraph.write_dot(H,fh)
        fh.close()

        fh=open(fname,'r')
        Hin=nx.drawing.nx_agraph.read_dot(fh)
        fh.close()
        os.unlink(fname)
        self.assert_equal(H,Hin)


    def testUndirected(self):
        self.agraph_checks(nx.Graph())

    def testDirected(self):
        self.agraph_checks(nx.DiGraph())

    def testMultiUndirected(self):
        self.agraph_checks(nx.MultiGraph())

    def testMultiDirected(self):
        self.agraph_checks(nx.MultiDiGraph())


        
