#!/usr/bin/env python
from nose.tools import *
import networkx as nx

def test_all_simple_paths():
    G = nx.path_graph(4)
    paths = nx.all_simple_paths(G,0,3)
    assert_equal(list(list(p) for p in paths),[[0,1,2,3]])

def test_all_simple_paths_cutoff():
    G = nx.complete_graph(4)
    paths = nx.all_simple_paths(G,0,1,cutoff=1)
    assert_equal(list(list(p) for p in paths),[[0,1]])
    paths = nx.all_simple_paths(G,0,1,cutoff=2)
    assert_equal(list(list(p) for p in paths),[[0,1],[0,2,1],[0,3,1]])

def test_all_simple_paths_multigraph():
    G = nx.MultiGraph([(1,2),(1,2)])
    paths = nx.all_simple_paths(G,1,2)
    assert_equal(list(list(p) for p in paths),[[1,2],[1,2]])

def test_all_simple_paths_multigraph_with_cutoff():
    G = nx.MultiGraph([(1,2),(1,2),(1,10),(10,2)])
    paths = nx.all_simple_paths(G,1,2, cutoff=1)
    assert_equal(list(list(p) for p in paths),[[1,2],[1,2]])


def test_all_simple_paths_directed():
    G = nx.DiGraph()
    G.add_path([1,2,3])
    G.add_path([3,2,1])
    paths = nx.all_simple_paths(G,1,3)
    assert_equal(list(list(p) for p in paths),[[1,2,3]])

def test_all_simple_paths_empty():
    G = nx.path_graph(4)
    paths = nx.all_simple_paths(G,0,3,cutoff=2)
    assert_equal(list(list(p) for p in paths),[])

def hamiltonian_path(G,source):
    source = next(G.nodes_iter())
    neighbors = set(G[source])-set([source])
    n = len(G)
    for target in neighbors:
        for path in nx.all_simple_paths(G,source,target):
            if len(path) == n:
                yield path

def test_hamiltonian_path():
    from itertools import permutations
    G=nx.complete_graph(4)
    paths = [list(p) for p in hamiltonian_path(G,0)]
    exact = [[0]+list(p) for p in permutations([1,2,3],3) ]
    assert_equal(sorted(paths),sorted(exact))

def test_cutoff_zero():
    G = nx.complete_graph(4)
    paths = nx.all_simple_paths(G,0,3,cutoff=0)
    assert_equal(list(list(p) for p in paths),[])
    paths = nx.all_simple_paths(nx.MultiGraph(G),0,3,cutoff=0)
    assert_equal(list(list(p) for p in paths),[])

@raises(nx.NetworkXError)
def test_source_missing():
    G = nx.Graph()
    G.add_path([1,2,3])
    paths = list(nx.all_simple_paths(nx.MultiGraph(G),0,3))

@raises(nx.NetworkXError)
def test_target_missing():
    G = nx.Graph()
    G.add_path([1,2,3])
    paths = list(nx.all_simple_paths(nx.MultiGraph(G),1,4))
