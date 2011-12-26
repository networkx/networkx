from nose.tools import *
__all__ = ['assert_nodes_equal', 'assert_edges_equal','assert_graphs_equal']

def assert_nodes_equal(nlist1, nlist2):
    try:
        l = len(nlist1[0])
        assert_equal(sorted((sorted(n) for n in nlist1)),
                     sorted((sorted(n) for n in nlist2)))
    except TypeError:
        assert_equal(set(nlist1),set(nlist2))
    return

def assert_edges_equal(elist1, elist2):
    assert_equal(sorted((sorted(e) for e in elist1)),
                 sorted((sorted(e) for e in elist2)))
    return

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
