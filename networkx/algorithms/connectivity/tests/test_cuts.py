import pytest

import networkx as nx
from networkx.algorithms import flow
from networkx.algorithms.connectivity import minimum_st_edge_cut, minimum_st_node_cut
from networkx.utils import arbitrary_element

flow_funcs = [
    flow.boykov_kolmogorov,
    flow.dinitz,
    flow.edmonds_karp,
    flow.preflow_push,
    flow.shortest_augmenting_path,
]

# Tests for node and edge cutsets


def _generate_no_biconnected(max_attempts=50):
    attempts = 0
    while True:
        G = nx.fast_gnp_random_graph(100, 0.0575, seed=42)
        if nx.is_connected(G) and not nx.is_biconnected(G):
            attempts = 0
            yield G
        else:
            if attempts >= max_attempts:
                msg = f"Tried {attempts} times: no suitable Graph."
                raise Exception(msg)
            else:
                attempts += 1


def test_articulation_points():
    Ggen = _generate_no_biconnected()
    for flow_func in flow_funcs:
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        for i in range(1):  # change 1 to 3 or more for more realizations.
            G = next(Ggen)
            cut = nx.minimum_node_cut(G, flow_func=flow_func)
            assert len(cut) == 1, errmsg
            assert cut.pop() in set(nx.articulation_points(G)), errmsg


def test_brandes_erlebach_book():
    # Figure 1 chapter 7: Connectivity
    # http://www.informatik.uni-augsburg.de/thi/personen/kammer/Graph_Connectivity.pdf
    G = nx.Graph()
    G.add_edges_from(
        [
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 5),
            (2, 3),
            (2, 6),
            (3, 4),
            (3, 6),
            (4, 6),
            (4, 7),
            (5, 7),
            (6, 8),
            (6, 9),
            (7, 8),
            (7, 10),
            (8, 11),
            (9, 10),
            (9, 11),
            (10, 11),
        ]
    )
    for flow_func in flow_funcs:
        kwargs = {"flow_func": flow_func}
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        # edge cutsets
        assert 3 == len(nx.minimum_edge_cut(G, 1, 11, **kwargs)), errmsg
        edge_cut = nx.minimum_edge_cut(G, **kwargs)
        # Node 5 has only two edges
        assert 2 == len(edge_cut), errmsg
        H = G.copy()
        H.remove_edges_from(edge_cut)
        assert not nx.is_connected(H), errmsg
        # node cuts
        assert {6, 7} == minimum_st_node_cut(G, 1, 11, **kwargs), errmsg
        assert {6, 7} == nx.minimum_node_cut(G, 1, 11, **kwargs), errmsg
        node_cut = nx.minimum_node_cut(G, **kwargs)
        assert 2 == len(node_cut), errmsg
        H = G.copy()
        H.remove_nodes_from(node_cut)
        assert not nx.is_connected(H), errmsg


def test_white_harary_paper():
    # Figure 1b white and harary (2001)
    # https://doi.org/10.1111/0081-1750.00098
    # A graph with high adhesion (edge connectivity) and low cohesion
    # (node connectivity)
    G = nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(4))
    G.remove_node(7)
    for i in range(4, 7):
        G.add_edge(0, i)
    G = nx.disjoint_union(G, nx.complete_graph(4))
    G.remove_node(G.order() - 1)
    for i in range(7, 10):
        G.add_edge(0, i)
    for flow_func in flow_funcs:
        kwargs = {"flow_func": flow_func}
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        # edge cuts
        edge_cut = nx.minimum_edge_cut(G, **kwargs)
        assert 3 == len(edge_cut), errmsg
        H = G.copy()
        H.remove_edges_from(edge_cut)
        assert not nx.is_connected(H), errmsg
        # node cuts
        node_cut = nx.minimum_node_cut(G, **kwargs)
        assert {0} == node_cut, errmsg
        H = G.copy()
        H.remove_nodes_from(node_cut)
        assert not nx.is_connected(H), errmsg


def test_petersen_cutset():
    G = nx.petersen_graph()
    for flow_func in flow_funcs:
        kwargs = {"flow_func": flow_func}
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        # edge cuts
        edge_cut = nx.minimum_edge_cut(G, **kwargs)
        assert 3 == len(edge_cut), errmsg
        H = G.copy()
        H.remove_edges_from(edge_cut)
        assert not nx.is_connected(H), errmsg
        # node cuts
        node_cut = nx.minimum_node_cut(G, **kwargs)
        assert 3 == len(node_cut), errmsg
        H = G.copy()
        H.remove_nodes_from(node_cut)
        assert not nx.is_connected(H), errmsg


def test_octahedral_cutset():
    G = nx.octahedral_graph()
    for flow_func in flow_funcs:
        kwargs = {"flow_func": flow_func}
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        # edge cuts
        edge_cut = nx.minimum_edge_cut(G, **kwargs)
        assert 4 == len(edge_cut), errmsg
        H = G.copy()
        H.remove_edges_from(edge_cut)
        assert not nx.is_connected(H), errmsg
        # node cuts
        node_cut = nx.minimum_node_cut(G, **kwargs)
        assert 4 == len(node_cut), errmsg
        H = G.copy()
        H.remove_nodes_from(node_cut)
        assert not nx.is_connected(H), errmsg


def test_icosahedral_cutset():
    G = nx.icosahedral_graph()
    for flow_func in flow_funcs:
        kwargs = {"flow_func": flow_func}
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        # edge cuts
        edge_cut = nx.minimum_edge_cut(G, **kwargs)
        assert 5 == len(edge_cut), errmsg
        H = G.copy()
        H.remove_edges_from(edge_cut)
        assert not nx.is_connected(H), errmsg
        # node cuts
        node_cut = nx.minimum_node_cut(G, **kwargs)
        assert 5 == len(node_cut), errmsg
        H = G.copy()
        H.remove_nodes_from(node_cut)
        assert not nx.is_connected(H), errmsg


def test_node_cutset_exception():
    G = nx.Graph()
    G.add_edges_from([(1, 2), (3, 4)])
    for flow_func in flow_funcs:
        pytest.raises(nx.NetworkXError, nx.minimum_node_cut, G, flow_func=flow_func)


def test_node_cutset_random_graphs():
    for flow_func in flow_funcs:
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        for i in range(3):
            G = nx.fast_gnp_random_graph(50, 0.25, seed=42)
            if not nx.is_connected(G):
                ccs = iter(nx.connected_components(G))
                start = arbitrary_element(next(ccs))
                G.add_edges_from((start, arbitrary_element(c)) for c in ccs)
            cutset = nx.minimum_node_cut(G, flow_func=flow_func)
            assert nx.node_connectivity(G) == len(cutset), errmsg
            G.remove_nodes_from(cutset)
            assert not nx.is_connected(G), errmsg


def test_edge_cutset_random_graphs():
    for flow_func in flow_funcs:
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        for i in range(3):
            G = nx.fast_gnp_random_graph(50, 0.25, seed=42)
            if not nx.is_connected(G):
                ccs = iter(nx.connected_components(G))
                start = arbitrary_element(next(ccs))
                G.add_edges_from((start, arbitrary_element(c)) for c in ccs)
            cutset = nx.minimum_edge_cut(G, flow_func=flow_func)
            assert nx.edge_connectivity(G) == len(cutset), errmsg
            G.remove_edges_from(cutset)
            assert not nx.is_connected(G), errmsg


def test_empty_graphs():
    G = nx.Graph()
    D = nx.DiGraph()
    for interface_func in [nx.minimum_node_cut, nx.minimum_edge_cut]:
        for flow_func in flow_funcs:
            pytest.raises(
                nx.NetworkXPointlessConcept, interface_func, G, flow_func=flow_func
            )
            pytest.raises(
                nx.NetworkXPointlessConcept, interface_func, D, flow_func=flow_func
            )


def test_unbounded():
    G = nx.complete_graph(5)
    for flow_func in flow_funcs:
        assert 4 == len(minimum_st_edge_cut(G, 1, 4, flow_func=flow_func))


def test_missing_source():
    G = nx.path_graph(4)
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            pytest.raises(
                nx.NetworkXError, interface_func, G, 10, 1, flow_func=flow_func
            )


def test_missing_target():
    G = nx.path_graph(4)
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            pytest.raises(
                nx.NetworkXError, interface_func, G, 1, 10, flow_func=flow_func
            )


def test_not_weakly_connected():
    G = nx.DiGraph()
    nx.add_path(G, [1, 2, 3])
    nx.add_path(G, [4, 5])
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            pytest.raises(nx.NetworkXError, interface_func, G, flow_func=flow_func)


def test_not_connected():
    G = nx.Graph()
    nx.add_path(G, [1, 2, 3])
    nx.add_path(G, [4, 5])
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            pytest.raises(nx.NetworkXError, interface_func, G, flow_func=flow_func)


def tests_min_cut_complete():
    G = nx.complete_graph(5)
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            assert 4 == len(interface_func(G, flow_func=flow_func))


def tests_min_cut_complete_directed():
    G = nx.complete_graph(5)
    G = G.to_directed()
    for interface_func in [nx.minimum_edge_cut, nx.minimum_node_cut]:
        for flow_func in flow_funcs:
            assert 4 == len(interface_func(G, flow_func=flow_func))


def tests_minimum_st_node_cut():
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, 3, 7, 8, 11, 12])
    G.add_edges_from([(7, 11), (1, 11), (1, 12), (12, 8), (0, 1)])
    nodelist = minimum_st_node_cut(G, 7, 11)
    assert nodelist == set()


def test_invalid_auxiliary():
    G = nx.complete_graph(5)
    pytest.raises(nx.NetworkXError, minimum_st_node_cut, G, 0, 3, auxiliary=G)


def test_interface_only_source():
    G = nx.complete_graph(5)
    for interface_func in [nx.minimum_node_cut, nx.minimum_edge_cut]:
        pytest.raises(nx.NetworkXError, interface_func, G, s=0)


def test_interface_only_target():
    G = nx.complete_graph(5)
    for interface_func in [nx.minimum_node_cut, nx.minimum_edge_cut]:
        pytest.raises(nx.NetworkXError, interface_func, G, t=3)


def test_directed_minimum_st_node_cut_reverse_edge():
    # In a digraph an edge from t to s is not an s-t path, so s can still be
    # separated from t. Only a direct edge from s to t makes the pair
    # inseparable, and then the empty set is returned.
    G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])  # the directed triangle
    for flow_func in flow_funcs:
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        assert minimum_st_node_cut(G, 0, 2, flow_func=flow_func) == {1}, errmsg
        assert minimum_st_node_cut(G, 0, 1, flow_func=flow_func) == set(), errmsg


def test_directed_minimum_node_cut():
    # The node connectivity of the directed triangle is 1, so its minimum node
    # cut holds a single node. The initial cutset has to isolate the starting
    # node through its predecessors or its successors, whichever is smaller,
    # and not through its successors alone.
    G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])
    for flow_func in flow_funcs:
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        cut = nx.minimum_node_cut(G, flow_func=flow_func)
        assert len(cut) == nx.node_connectivity(G) == 1, errmsg
        H = G.copy()
        H.remove_nodes_from(cut)
        assert not nx.is_strongly_connected(H), errmsg


def test_directed_minimum_node_cut_not_strongly_connected():
    # A weakly connected digraph that is not strongly connected is already
    # disconnected, so no node has to be removed and the cut is empty.
    G = nx.DiGraph([(0, 1), (1, 2), (2, 0), (3, 0)])  # a triangle and a source
    assert nx.is_weakly_connected(G)
    assert not nx.is_strongly_connected(G)
    for flow_func in flow_funcs:
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        assert nx.minimum_node_cut(G, flow_func=flow_func) == set(), errmsg


def test_directed_minimum_node_cut_both_orders():
    # A minimum node cut of a digraph separates an ordered pair, and the two
    # orders need not agree, so the starting node has to be tried as source
    # and as target. Removing node 4 leaves this digraph not strongly
    # connected, so the minimum node cut has one node and not two.
    G = nx.DiGraph(
        [
            (0, 1),
            (0, 2),
            (0, 3),
            (1, 0),
            (1, 2),
            (2, 0),
            (2, 5),
            (3, 4),
            (3, 5),
            (4, 0),
            (4, 1),
            (4, 2),
            (4, 3),
            (4, 5),
            (5, 3),
            (5, 4),
        ]
    )
    assert nx.is_strongly_connected(G)
    for flow_func in flow_funcs:
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        cut = nx.minimum_node_cut(G, flow_func=flow_func)
        assert len(cut) == 1, errmsg
        H = G.copy()
        H.remove_nodes_from(cut)
        assert not nx.is_strongly_connected(H), errmsg


def test_minimum_node_cut_self_loops():
    # Self-loops do not affect node connectivity, so they must not enlarge the
    # minimum node cut either. The initial cutset is built from the neighbors
    # of the starting node, and a self-loop puts that node in its own cutset.
    G = nx.complete_graph(5)
    G.add_edges_from((u, u) for u in G)
    D = G.to_directed()
    for flow_func in flow_funcs:
        errmsg = f"Assertion failed in function: {flow_func.__name__}"
        assert len(nx.minimum_node_cut(G, flow_func=flow_func)) == 4, errmsg
        assert len(nx.minimum_node_cut(D, flow_func=flow_func)) == 4, errmsg
