#!/usr/bin/env python
from nose.tools import *
import networkx as nx
import networkx.readwrite.sparsegraph6 as sg6
import os,tempfile

class TestGraph6Utils(object):

    def test_n_data_n_conversion(self):
	for i in [0, 1, 42, 62, 63, 64, 258047, 258048, 7744773, 68719476735]:
	    assert_equal(sg6.data_to_n(sg6.n_to_data(i))[0], i)
	    assert_equal(sg6.data_to_n(sg6.n_to_data(i))[1], [])
	    assert_equal(sg6.data_to_n(sg6.n_to_data(i) + [42, 43])[1], [42, 43])

    def test_data_sparse6_data_conversion(self):
	for data in [[], [0], [63], [63, 63], [0]*42,
		     [0, 1, 62, 42, 3, 11, 0, 11]]:
	    assert_equal(sg6.graph6_to_data(sg6.data_to_graph6(data)), data)
	    assert_equal(len(sg6.data_to_graph6(data)), len(data))


class TestGraph6(object):

    def test_parse_graph6(self):
        data="""DF{"""
        G=nx.parse_graph6(data)
        assert_equal(sorted(G.nodes()),[0, 1, 2, 3, 4])
        assert_equal([e for e in sorted(G.edges())],
                     [(0, 3), (0, 4), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)])

    def test_read_graph6(self):
        data="""DF{"""
        G=nx.parse_graph6(data)
        (fd,fname)=tempfile.mkstemp()
        fh=open(fname,'w')
        b=fh.write(data)
        fh.close()
        Gin=nx.read_graph6(fname)
        assert_equal(sorted(G.nodes()),sorted(Gin.nodes()))
        assert_equal(sorted(G.edges()),sorted(Gin.edges()))
        os.close(fd)
        os.unlink(fname)

    def test_read_many_graph6(self):
        # Read many graphs into list
        data="""DF{\nD`{\nDqK\nD~{\n"""
        (fd,fname)=tempfile.mkstemp()
        fh=open(fname,'w')
        b=fh.write(data)
        fh.close()
        glist=nx.read_graph6_list(fname)
        assert_equal(len(glist),4)
        for G in glist:
            assert_equal(sorted(G.nodes()),[0, 1, 2, 3, 4])
        os.close(fd)
        os.unlink(fname)


class TestSparseGraph6(object):

    def test_parse_sparse6(self):
        data=""":Q___eDcdFcDeFcE`GaJ`IaHbKNbLM"""
        G=nx.parse_sparse6(data)
        assert_equal(sorted(G.nodes()),
                     [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 
                      10, 11, 12, 13, 14, 15, 16, 17])
        assert_equal([e for e in sorted(G.edges())],
                     [(0, 1), (0, 2), (0, 3), (1, 12), (1, 14), (2, 13), 
                      (2, 15), (3, 16), (3, 17), (4, 7), (4, 9), (4, 11), 
                      (5, 6), (5, 8), (5, 9), (6, 10), (6, 11), (7, 8), 
                      (7, 10), (8, 12), (9, 15), (10, 14), (11, 13), 
                      (12, 16), (13, 17), (14, 17), (15, 16)])


    def test_read_sparse6(self):
        data=""":Q___eDcdFcDeFcE`GaJ`IaHbKNbLM"""
        G=nx.parse_sparse6(data)
        (fd,fname)=tempfile.mkstemp()
        fh=open(fname,'w')
        b=fh.write(data)
        fh.close()
        Gin=nx.read_sparse6(fname)
        assert_equal(sorted(G.nodes()),sorted(Gin.nodes()))
        assert_equal(sorted(G.edges()),sorted(Gin.edges()))
        os.close(fd)
        os.unlink(fname)

    def test_read_many_graph6(self):
        # Read many graphs into list
        data=""":Q___eDcdFcDeFcE`GaJ`IaHbKNbLM\n:Q___dCfDEdcEgcbEGbFIaJ`JaHN`IM"""
        (fd,fname)=tempfile.mkstemp()
        fh=open(fname,'w')
        b=fh.write(data)
        fh.close()
        glist=nx.read_sparse6_list(fname)
        assert_equal(len(glist),2)
        for G in glist:
            assert_equal(sorted(G.nodes()),
                         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 
                          10, 11, 12, 13, 14, 15, 16, 17])
        os.close(fd)
        os.unlink(fname)

