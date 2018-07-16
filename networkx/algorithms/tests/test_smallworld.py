#!/usr/bin/env python
from nose.tools import assert_true, assert_raises
import random

from networkx import random_reference, lattice_reference, sigma, omega
import networkx as nx

rng = random.Random(0)
rng = 42


def test_random_reference():
    G = nx.connected_watts_strogatz_graph(50, 6, 0.1, seed=rng)
    Gr = random_reference(G, niter=1, seed=rng)
    C = nx.average_clustering(G)
    Cr = nx.average_clustering(Gr)
    assert_true(C > Cr)

    assert_raises(nx.NetworkXError, random_reference, nx.Graph())
    assert_raises(nx.NetworkXNotImplemented, random_reference, nx.DiGraph())

    H = nx.Graph(((0, 1), (2, 3)))
    Hl = random_reference(H, niter=1, seed=rng)


def test_lattice_reference():
    G = nx.connected_watts_strogatz_graph(50, 6, 1, seed=rng)
    Gl = lattice_reference(G, niter=1, seed=rng)
    L = nx.average_shortest_path_length(G)
    Ll = nx.average_shortest_path_length(Gl)
    assert_true(Ll > L)

    assert_raises(nx.NetworkXError, lattice_reference, nx.Graph())
    assert_raises(nx.NetworkXNotImplemented, lattice_reference, nx.DiGraph())

    H = nx.Graph(((0, 1), (2, 3)))
    Hl = lattice_reference(H, niter=1)


def test_sigma():
    Gs = nx.connected_watts_strogatz_graph(50, 6, 0.1, seed=rng)
    Gr = nx.connected_watts_strogatz_graph(50, 6, 1, seed=rng)
    sigmas = sigma(Gs, niter=1, nrand=2, seed=rng)
    sigmar = sigma(Gr, niter=1, nrand=2, seed=rng)
    assert_true(sigmar < sigmas)


def test_omega():
    Gl = nx.connected_watts_strogatz_graph(50, 6, 0, seed=rng)
    Gr = nx.connected_watts_strogatz_graph(50, 6, 1, seed=rng)
    Gs = nx.connected_watts_strogatz_graph(50, 6, 0.1, seed=rng)
    omegal = omega(Gl, niter=1, nrand=1, seed=rng)
    omegar = omega(Gr, niter=1, nrand=1, seed=rng)
    omegas = omega(Gs, niter=1, nrand=1, seed=rng)
    print("omegas, omegal, omegar")
    print(omegas, omegal, omegar)
    assert_true(omegal < omegas and omegas < omegar)


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
