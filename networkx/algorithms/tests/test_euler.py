#!/usr/bin/env python
# coding: utf-8
# run with nose: nosetests -v test_euler.py

from nose.tools import *
import networkx as nx
from networkx import is_eulerian, eulerian_circuit, is_semieulerian, eulerian_path

class TestEuler:

    def test_is_eulerian(self):
        assert_true(is_eulerian(nx.complete_graph(5)))
        assert_true(is_eulerian(nx.complete_graph(7)))
        assert_true(is_eulerian(nx.hypercube_graph(4)))
        assert_true(is_eulerian(nx.hypercube_graph(6)))

        assert_false(is_eulerian(nx.complete_graph(4)))
        assert_false(is_eulerian(nx.complete_graph(6)))
        assert_false(is_eulerian(nx.hypercube_graph(3)))
        assert_false(is_eulerian(nx.hypercube_graph(5)))

        assert_false(is_eulerian(nx.petersen_graph()))
        assert_false(is_eulerian(nx.path_graph(4)))

    def test_is_eulerian2(self):
        # not connected
        G = nx.Graph()
        G.add_nodes_from([1,2,3])
        assert_false(is_eulerian(G))
        # not strongly connected
        G = nx.DiGraph()
        G.add_nodes_from([1,2,3])
        assert_false(is_eulerian(G))
        G = nx.MultiDiGraph()
        G.add_edge(1,2)
        G.add_edge(2,3)
        G.add_edge(2,3)
        G.add_edge(3,1)
        assert_false(is_eulerian(G))

    def test_eulerian_circuit_cycle(self):
        G=nx.cycle_graph(4)

        edges=list(eulerian_circuit(G,source=0))
        nodes=[u for u,v in edges]
        assert_equal(nodes,[0,3,2,1])
        assert_equal(edges,[(0,3),(3,2),(2,1),(1,0)])

        edges=list(eulerian_circuit(G,source=1))
        nodes=[u for u,v in edges]
        assert_equal(nodes,[1,2,3,0])
        assert_equal(edges,[(1,2),(2,3),(3,0),(0,1)])

        G=nx.complete_graph(3)

        edges=list(eulerian_circuit(G,source=0))
        nodes=[u for u,v in edges]
        assert_equal(nodes,[0,2,1])
        assert_equal(edges,[(0,2),(2,1),(1,0)])

        edges=list(eulerian_circuit(G,source=1))
        nodes=[u for u,v in edges]
        assert_equal(nodes,[1,2,0])
        assert_equal(edges,[(1,2),(2,0),(0,1)])

    def test_eulerian_circuit_digraph(self):
        G=nx.DiGraph()
        G.add_cycle([0,1,2,3])

        edges=list(eulerian_circuit(G,source=0))
        nodes=[u for u,v in edges]
        assert_equal(nodes,[0,1,2,3])
        assert_equal(edges,[(0,1),(1,2),(2,3),(3,0)])

        edges=list(eulerian_circuit(G,source=1))
        nodes=[u for u,v in edges]
        assert_equal(nodes,[1,2,3,0])
        assert_equal(edges,[(1,2),(2,3),(3,0),(0,1)])

    def test_eulerian_circuit_multigraph(self):
        G=nx.MultiGraph()
        G.add_cycle([0,1,2,3])
        G.add_edge(1,2)
        G.add_edge(1,2)
        edges=list(eulerian_circuit(G,source=0))
        nodes=[u for u, v in edges]
        assert_equal(nodes,[0,3,2,1,2,1])
        assert_equal(edges,[(0,3),(3,2),(2,1),(1,2),(2,1),(1,0)])

    @raises(nx.NetworkXError)
    def test_not_eulerian(self):
        next(list(eulerian_circuit(nx.complete_graph(4))))


class TestEulerianPath:

    # Use the bridges of Königsberg
    bridges = nx.MultiGraph([('W', 'N'), ('W', 'N'), ('N', 'E'), ('E', 'W'),
                             ('W', 'S'), ('W', 'S'), ('S', 'E')])

    def verify_path(self, G, path):
        g = G.__class__(G)  # copy graph structure (not attributes)

        if len(path) == 0:
            return False

        current_vertex = None

        for edge in path:
            u, v = edge
            if not current_vertex:
                current_vertex = u
            if current_vertex == u:
                g.remove_edge(*edge)
            else:
                raise nx.NetworkXError("Bad edge on path" + str(edge))
            current_vertex = v
        if len(list(g.edges())) > 0:
            raise nx.NetworkXError("Path did not use all edges")
        return True

    def test_eulerian_path(self):
        G = nx.Graph([('W', 'N'), ('N', 'E'), ('E', 'W'),
                      ('W', 'S'), ('S', 'E')])
        edges = list(eulerian_path(G))
        assert_true(self.verify_path(G, edges))

    def test_eulerian_path_directed(self):
        # An example, directed:
        G = nx.DiGraph([("W", "N"), ("N", "E"), ("S", "E"), ("W", "S"),
                        ("E", "W")])
        edges = list(nx.eulerian_path(G))
        self.verify_path(G, edges)

    def test_eulerian_path_multigraph(self):
        # An example, multi edge, undirected:
        G = nx.MultiGraph([("W", "N"), ("N", "E"), ("E", "W"),
                           ("E", "W"), ("W", "S"), ("S", "E"),
                           ("S", "E")])

        edges = list(nx.eulerian_path(G))
        self.verify_path(G, edges)

    def test_is_semieulerian(self):
        assert_false(is_semieulerian(self.bridges))

    @raises(nx.NetworkXError)
    def test_no_eulerian_path(self):
        next(list(eulerian_path(self.bridges)))

    @raises(nx.NetworkXError)
    def test_badpath(self):
        G = nx.Graph([('W', 'N'), ('N', 'E'), ('E', 'W'), ('W', 'S'), ('S', 'E')])
        edges = list(eulerian_path(G))
        self.verify_path(G, edges[1:])
