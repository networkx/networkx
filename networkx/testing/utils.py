import json
import itertools
from nose.tools import assert_equal
__all__ = ['assert_nodes_equal', 'assert_edges_equal','assert_graphs_equal']

def assert_nodes_equal(nodes1, nodes2):
    # Assumes iterables of nodes, or (node,datadict) tuples
    nlist1 = list(nodes1)
    nlist2 = list(nodes2)
    try:
        d1 = dict(nlist1)
        d2 = dict(nlist2)
    except (ValueError, TypeError):
        d1 = dict.fromkeys(nlist1)
        d2 = dict.fromkeys(nlist2)
    assert_equal(d1, d2)

def assert_edges_equal(edges1, edges2):
    """Compare lists of (Multi)Graph edges.

    Not suitable for DiGraph or MultiDiGraph, use
    `sorted(edges1) == sorted(edge2)` instead.
    """
    # Assumes iterables with u,v nodes as
    # edge tuples (u,v), or
    # edge tuples with data dicts (u,v,d), or
    # edge tuples with keys and data dicts (u,v,k, d)
    from collections import defaultdict
    d1 = defaultdict(lambda: defaultdict(list))
    d2 = defaultdict(lambda: defaultdict(list))
    c1 = 0
    for c1,e in enumerate(edges1):
        u,v = e[0],e[1]
        data = e[2:]
        d1[u][v].append(data)
        d1[v][u].append(data)
    c2 = 0
    for c2,e in enumerate(edges2):
        u,v = e[0],e[1]
        data = e[2:]
        d2[u][v].append(data)
        d2[v][u].append(data)

    # For MultiGraphs
    for d in itertools.chain(d1.values(), d2.values()):
        for l in d.values():
            try:
                l.sort()
            except TypeError:
                # Dictionaries/sets?
                l.sort(key=lambda x: json.dumps(x, sort_keys=True))

    assert_equal(c1, c2)
    assert_equal(d1, d2)


def assert_graphs_equal(graph1, graph2):
    assert_equal(graph1.adj, graph2.adj)
    assert_equal(graph1.node, graph2.node)
    assert_equal(graph1.graph, graph2.graph)
