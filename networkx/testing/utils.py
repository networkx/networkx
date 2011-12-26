import operator
from nose.tools import *
__all__ = ['assert_nodes_equal', 'assert_edges_equal','assert_graphs_equal']

def assert_nodes_equal(nlist1, nlist2):
    # Assumes lists are either nodes, or (node,datadict) tuples,
    # and also that nodes are orderable/sortable.
    try:
        l = len(nlist1[0])
        n1 = sorted(nlist1,key=operator.itemgetter(0))
        n2 = sorted(nlist2,key=operator.itemgetter(0))
        assert_equal(len(n1),len(n2))
        for a,b in zip(n1,n2):
            assert_equal(a,b)
    except TypeError:
        assert_equal(set(nlist1),set(nlist2))
    return

def assert_edges_equal(elist1, elist2):
    # Assumes lists with u,v nodes either as
    # edge tuples (u,v)
    # edge tuples with data dicts (u,v,d)
    # edge tuples with keys and data dicts (u,v,k, d)
    # and also that nodes are orderable/sortable.
    e1 = sorted(elist1,key=lambda x: sorted(x[0:1]))
    e2 = sorted(elist2,key=lambda x: sorted(x[0:1]))
    assert_equal(len(e1),len(e2))
    if len(e1[0]) == 2:
        for a,b in zip(e1,e2):
            assert_equal(set(a[0:2]),set(b[0:2]))
    elif len(e1[0]) == 3:
        for a,b in zip(e1,e2):
            assert_equal(set(a[0:2]),set(b[0:2]))
            assert_equal(a[2],b[2])
    elif len(e1[0]) == 4:
        for a,b in zip(e1,e2):
            assert_equal(set(a[0:2]),set(b[0:2]))
            assert_equal(a[2],b[2])
            assert_equal(a[3],b[3])


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
