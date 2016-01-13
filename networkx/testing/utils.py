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
    # Assumes iterables with u,v nodes as
    # edge tuples (u,v), or
    # edge tuples with data dicts (u,v,d), or
    # edge tuples with keys and data dicts (u,v,k, d)
    from collections import defaultdict
    d1 = defaultdict(dict)
    d2 = defaultdict(dict)
    for e in edges1:
        u,v = e[0],e[1]
        data = e[2:]
        d1[u][v] = data
        d1[v][u] = data
    for e in edges2:
        u,v = e[0],e[1]
        data = e[2:]
        d2[u][v] = data
        d2[v][u] = data
    assert_equal(len(d1), len(d2))
    for k in d1:
        assert_equal(d1[k], d2[k])


def assert_graphs_equal(graph1, graph2):
    if graph1.is_multigraph():
        edges1 = graph1.edges(data=True,keys=True)
    else:
        edges1 = graph1.edges(data=True)
    if graph2.is_multigraph():
        edges2 = graph2.edges(data=True,keys=True)
    else:
        edges2 = graph2.edges(data=True)
    assert_nodes_equal(graph1.nodes(data=True),
                       graph2.nodes(data=True))
    assert_edges_equal(edges1, edges2)
    assert_equal(graph1.graph,graph2.graph)
    return
