#!/usr/bin/env python
# run with nose: nosetests -v test_bridges.py

from nose.tools import *
import networkx as nx
from networkx import bridges


class TestBridges:

    def test_triangle(self):
        '''
        ~~~
        a---b
         \ /
          c
        ~~~
        '''
        G = nx.Graph()
        G.add_edge(1, 2)
        G.add_edge(2, 3)
        G.add_edge(3, 1)
        # Graph forms a triangle so no edge is a bridge.
        assert_equal(list(bridges(G)), [])

    def test_singeEdge(self):
        '''
        Just a single edge in the graph, so this must be the edge.
        ~~~
        a-b
        ~~~
        '''
        G = nx.Graph()
        G.add_edge('a', 'b')
        assert_equal(list(bridges(G)), [('a', 'b')])

    def test_twoDisconnectedComponents(self):
        '''
        ~~~
        a-b-c
        e-f-g
        ~~~
        '''
        G=nx.Graph()
        G.add_edge(1, 2)
        G.add_edge(3, 4)

        # Both edges are bridges.
        assert_equal(list(bridges(G)), [(1, 2), (3, 4)])


    def test_twoCycles(self):
        '''
        a---b
         \ /
          c
          |
          d
         / \
        e---f
        '''
        G=nx.Graph()
        G.add_edge('a', 'b')
        G.add_edge('b', 'c')
        G.add_edge('c', 'a')
        G.add_edge('c', 'd')
        G.add_edge('d', 'e')
        G.add_edge('e', 'f')
        G.add_edge('f', 'd')

        assert_equal(list(bridges(G)), [('c', 'd')])

    def test_parallelEdge(self):
        '''
        a----b
         \__/
        '''
        G = nx.MultiGraph()
        G.add_edge(1, 2)
        G.add_edge(1, 2)
        print G.edges(), G[1][2]
        assert_equal(list(bridges(G)), [])
