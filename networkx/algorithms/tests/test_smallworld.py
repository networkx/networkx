#!/usr/bin/env python
from nose.tools import *
from networkx.algorithms.smallworld import *
import networkx as nx

import random
random.seed(0)

def test_random_reference():
    G = nx.generators.random_graphs.connected_watts_strogatz_graph(100,6,0.1)
    Gr = random_reference(G)
    C = nx.average_clustering(G)
    Cr = nx.average_clustering(Gr)
    assert_true(C>Cr)

def test_lattice_reference():
    G = nx.generators.random_graphs.connected_watts_strogatz_graph(100,6,1)
    Gl = lattice_reference(G)
    L = nx.average_shortest_path_length(G)
    Ll = nx.average_shortest_path_length(Gl)
    assert_true(Ll>L)

def test_sigma():
    Gs = nx.generators.random_graphs.connected_watts_strogatz_graph(100,6,0.1)
    Gr = nx.generators.random_graphs.connected_watts_strogatz_graph(100,6,1)
    sigmas = sigma(Gs)
    sigmar = sigma(Gr)
    assert_true(sigmar<sigmas)

def test_omega():
    Gs = nx.generators.random_graphs.connected_watts_strogatz_graph(100,6,0.1)
    Gl = nx.generators.random_graphs.connected_watts_strogatz_graph(100,6,0)
    Gr = nx.generators.random_graphs.connected_watts_strogatz_graph(100,6,1)
    omegas = omega(Gs)
    omegal = omega(Gl)
    omegar = omega(Gr)
    assert_true(omegal<omegas and omegas<omegar)

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
