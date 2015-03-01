from nose.tools import assert_equal, assert_true, assert_false, assert_raises
import networkx as nx

from networkx.algorithms.flow import (edmonds_karp, preflow_push,
    shortest_augmenting_path)

flow_funcs = [edmonds_karp, preflow_push, shortest_augmenting_path]

# import connectivity functions not in base namespace
from networkx.algorithms.connectivity import (minimum_st_edge_cut,
    minimum_st_node_cut)

msg = "Assertion failed in function: {0}"

# Tests for node and edge cutsets
def _generate_no_biconnected(max_attempts=50):
    attempts = 0
    while True:
        G = nx.fast_gnp_random_graph(100,0.0575)
        if nx.is_connected(G) and not nx.is_biconnected(G):
            attempts = 0
            yield G
        else:
            if attempts >= max_attempts:
                msg = "Tried %d times: no suitable Graph."%attempts
                raise Exception(msg % max_attempts)
            else:
                attempts += 1
 
def test_articulation_points():
    Ggen = _generate_no_biconnected()
    for flow_func in flow_funcs:
        for i in range(3):
            G = next(Ggen)
            cut = nx.minimum_node_cut(G, flow_func=flow_func)
            assert_true(len(cut) == 1, msg=msg.format(flow_func.__name__))
            assert_true(cut.pop() in set(nx.articulation_points(G)),
                        msg=msg.format(flow_func.__name__))

def test_brandes_erlebach_book():
    # Figure 1 chapter 7: Connectivity
    # http://www.informatik.uni-augsburg.de/thi/personen/kammer/Graph_Connectivity.pdf
    G = nx.Graph()
    G.add_edges_from([(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 6), (3, 4),
                      (3, 6), (4, 6), (4, 7), (5, 7), (6, 8), (6, 9), (7, 8),
                      (7, 10), (8, 11), (9, 10), (9, 11), (10, 11)])
    for flow_func in flow_funcs:
        kwargs = dict(flow_func=flow_func)
        # edge cutsets
        assert_equal(3, len(nx.minimum_edge_cut(G, 1, 11, **kwargs)),
                     msg=msg.format(flow_func.__name__))
        edge_cut = nx.minimum_edge_cut(G, **kwargs)
        # Node 5 has only two edges
        assert_equal(2, len(edge_cut), msg=msg.format(flow_func.__name__))
        H = G.copy()
        H.remove_edges_from(edge_cut)
        assert_false(nx.is_connected(H), msg=msg.format(flow_func.__name__))
        # node cuts
        assert_equal(set([6, 7]), minimum_st_node_cut(G, 1, 11, **kwargs),
                     msg=msg.format(flow_func.__name__))
        assert_equal(set([6, 7]), nx.minimum_node_cut(G, 1, 11, **kwargs),
                     msg=msg.format(flow_func.__name__))
        node_cut = nx.minimum_node_cut(G, **kwargs)
        assert_equal(2, len(node_cut), msg=msg.format(flow_func.__name__))
        H = G.copy()
        H.remove_nodes_from(node_cut)
        assert_false(nx.is_connected(H), msg=msg.format(flow_func.__name__))

def test_white_harary_paper():
    # Figure 1b white and harary (2001)
    # http://eclectic.ss.uci.edu/~drwhite/sm-w23.PDF
    # A graph with high adhesion (edge connectivity) and low cohesion
    # (node connectivity)
    G = nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(4))
    G.remove_node(7)
    for i in range(4,7):
        G.add_edge(0,i)
    G = nx.disjoint_union(G, nx.complete_graph(4))
    G.remove_node(G.order()-1)
    for i in range(7,10):
        G.add_edge(0,i)
    for flow_func in flow_funcs:
        kwargs = dict(flow_func=flow_func)
        # edge cuts
        edge_cut = nx.minimum_edge_cut(G, **kwargs)
        assert_equal(3, len(edge_cut), msg=msg.format(flow_func.__name__))
        H = G.copy()
        H.remove_edges_from(edge_cut)
        assert_false(nx.is_connected(H), msg=msg.format(flow_func.__name__))
        # node cuts
        node_cut = nx.minimum_node_cut(G, **kwargs)
        assert_equal(set([0]), node_cut, msg=msg.format(flow_func.__name__))
        H = G.copy()
        H.remove_nodes_from(node_cut)
        assert_false(nx.is_connected(H), msg=msg.format(flow_func.__name__))

def test_petersen_cutset():
    G = nx.petersen_graph()
    for flow_func in flow_funcs:
        kwargs = dict(flow_func=flow_func)
        # edge cuts
        edge_cut = nx.minimum_edge_cut(G, **kwargs)
        assert_equal(3, len(edge_cut), msg=msg.format(flow_func.__name__))
        H = G.copy()
        H.remove_edges_from(edge_cut)
        assert_false(nx.is_connected(H), msg=msg.format(flow_func.__name__))
        # node cuts
        node_cut = nx.minimum_node_cut(G, **kwargs)
        assert_equal(3, len(node_cut), msg=msg.format(flow_func.__name__))
        H = G.copy()
        H.remove_nodes_from(node_cut)
        assert_false(nx.is_connected(H), msg=msg.format(flow_func.__name__))

def test_octahedral_cutset():
    G=nx.octahedral_graph()
    for flow_func in flow_funcs:
        kwargs = dict(flow_func=flow_func)
        # edge cuts
        edge_cut = nx.minimum_edge_cut(G, **kwargs)
        assert_equal(4, len(edge_cut), msg=msg.format(flow_func.__name__))
        H = G.copy()
        H.remove_edges_from(edge_cut)
        assert_false(nx.is_connected(H), msg=msg.format(flow_func.__name__))
        # node cuts
        node_cut = nx.minimum_node_cut(G, **kwargs)
        assert_equal(4, len(node_cut), msg=msg.format(flow_func.__name__))
        H = G.copy()
        H.remove_nodes_from(node_cut)
        assert_false(nx.is_connected(H), msg=msg.format(flow_func.__name__))

def test_icosahedral_cutset():
    G=nx.icosahedral_graph()
    for flow_func in flow_funcs:
        kwargs = dict(flow_func=flow_func)
        # edge cuts
        edge_cut = nx.minimum_edge_cut(G, **kwargs)
        assert_equal(5, len(edge_cut), msg=msg.format(flow_func.__name__))
        H = G.copy()
        H.remove_edges_from(edge_cut)
        assert_false(nx.is_connected(H), msg=msg.format(flow_func.__name__))
        # node cuts
        node_cut = nx.minimum_node_cut(G, **kwargs)
        assert_equal(5, len(node_cut), msg=msg.format(flow_func.__name__))
        H = G.copy()
        H.remove_nodes_from(node_cut)
        assert_false(nx.is_connected(H), msg=msg.format(flow_func.__name__))

def test_node_cutset_exception():
    G=nx.Graph()
    G.add_edges_from([(1, 2), (3, 4)])
    for flow_func in flow_funcs:
        assert_raises(nx.NetworkXError, nx.minimum_node_cut, G, flow_func=flow_func)

def test_node_cutset_random_graphs():
    for flow_func in flow_funcs:
        for i in range(3):
            G = nx.fast_gnp_random_graph(50, 0.25)
            if not nx.is_connected(G):
                ccs = iter(nx.connected_components(G))
                start = next(ccs)[0]
                G.add_edges_from((start, c[0]) for c in ccs)
            cutset = nx.minimum_node_cut(G, flow_func=flow_func)
            assert_equal(nx.node_connectivity(G), len(cutset),
                         msg=msg.format(flow_func.__name__))
            G.remove_nodes_from(cutset)
            assert_false(nx.is_connected(G), msg=msg.format(flow_func.__name__))

def test_edge_cutset_random_graphs():
    for flow_func in flow_funcs:
        for i in range(3):
            G = nx.fast_gnp_random_graph(50, 0.25)
            if not nx.is_connected(G):
                ccs = iter(nx.connected_components(G))
                start = next(ccs)[0]
                G.add_edges_from( (start,c[0]) for c in ccs )
            cutset = nx.minimum_edge_cut(G, flow_func=flow_func)
            assert_equal(nx.edge_connectivity(G), len(cutset),
                         msg=msg.format(flow_func.__name__))
            G.remove_edges_from(cutset)
            assert_false(nx.is_connected(G), msg=msg.format(flow_func.__name__))

def test_empty_graphs():
    G = nx.Graph()
    D = nx.DiGraph()
    for interface_func in [nx.minimum_node_cut, nx.minimum_edge_cut]:
        for flow_func in flow_funcs:
            assert_raises(nx.NetworkXPointlessConcept, interface_func, G,
                          flow_func=flow_func)
            assert_raises(nx.NetworkXPointlessConcept, interface_func, D,
                          flow_func=flow_func)

def test_unbounded():
    G = nx.complete_graph(5)
    for flow_func in flow_funcs:
        assert_equal(4, len(minimum_st_edge_cut(G, 1, 4, flow_func=flow_func)))

def test_missing_source():
    G = nx.path_graph(4)
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            assert_raises(nx.NetworkXError, interface_func, G, 10, 1,
                          flow_func=flow_func)

def test_missing_target():
    G = nx.path_graph(4)
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            assert_raises(nx.NetworkXError, interface_func, G, 1, 10,
                          flow_func=flow_func)

def test_not_weakly_connected():
    G = nx.DiGraph()
    G.add_path([1, 2, 3])
    G.add_path([4, 5])
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            assert_raises(nx.NetworkXError, interface_func, G,
                          flow_func=flow_func)

def test_not_connected():
    G = nx.Graph()
    G.add_path([1, 2, 3])
    G.add_path([4, 5])
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            assert_raises(nx.NetworkXError, interface_func, G,
                          flow_func=flow_func)

def tests_min_cut_complete():
    G = nx.complete_graph(5)
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            assert_equal(4, len(interface_func(G, flow_func=flow_func)))

def tests_min_cut_complete_directed():
    G = nx.complete_graph(5)
    G = G.to_directed()
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            assert_equal(4, len(interface_func(G, flow_func=flow_func)))

def test_invalid_auxiliary():
    G = nx.complete_graph(5)
    assert_raises(nx.NetworkXError, minimum_st_node_cut, G, 0, 3,
                   auxiliary=G)

def test_interface_only_source():
    G = nx.complete_graph(5)
    for interface_func in [nx.minimum_node_cut, nx.minimum_edge_cut]:
        assert_raises(nx.NetworkXError, interface_func, G, s=0)

def test_interface_only_target():
    G = nx.complete_graph(5)
    for interface_func in [nx.minimum_node_cut, nx.minimum_edge_cut]:
        assert_raises(nx.NetworkXError, interface_func, G, t=3)
