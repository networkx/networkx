from nose.tools import *

import networkx as nx
from networkx.utils.decorators import open_file,require

def test_require_decorator():
    @require('os','sys')
    def test1():
        import os
        import sys

    @require('blahhh')
    def test2():
        import blahhh

    test1()
    assert_raises(nx.NetworkXError,
                  test2)

def test_open_file_decorator():
    @open_file(0,'w')
    def test_writer(path):
        path.write("Blah... ")
        path.write("BLAH ")
        path.write("BLAH!!!! ")

    @open_file(0,'r')
    def test_reader(path):
        return path.readlines()

    test_writer("test.txt")
    assert_equal(test_reader("test.txt")[0],
                 'Blah... BLAH BLAH!!!! ')

    fh = open("test.txt",'w')
    test_writer(fh)
    assert_false(fh.closed)
    fh.close()
    fh = open("test.txt",'r')
    assert_equal(test_reader(fh)[0],
                 'Blah... BLAH BLAH!!!! ')
    assert_false(fh.closed)

    
    @open_file(1,'w')
    def test_writer1(a,path):
        path.write("Blah... ")
        path.write("BLAH ")
        path.write("BLAH!!!! ")

    @open_file(1,'r')
    def test_reader1(a,path):
        return path.readlines()

    test_writer1(None,"test.txt")
    assert_equal(test_reader1(None,"test.txt")[0],
                 'Blah... BLAH BLAH!!!! ')

    fh = open("test.txt",'w')
    test_writer1(None,fh)
    assert_false(fh.closed)
    fh.close()
    fh = open("test.txt",'r')
    assert_equal(test_reader1(None,fh)[0],
                 'Blah... BLAH BLAH!!!! ')
    assert_false(fh.closed)
