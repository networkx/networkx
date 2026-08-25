import pytest

import networkx as nx
from networkx.algorithms import flow
from networkx.algorithms.connectivity import minimum_st_edge_cut, minimum_st_node_cut

flow_funcs = [
    flow.boykov_kolmogorov,
    flow.dinitz,
    flow.edmonds_karp,
    flow.preflow_push,
    flow.shortest_augmenting_path,
]

interface_funcs = [nx.minimum_node_cut, nx.minimum_edge_cut]


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_articulation_points(flow_func):
    # Graph instance which is connected but *not* biconnected
    G = nx.fast_gnp_random_graph(100, 0.0575, seed=42)
    assert nx.is_connected(G) and not nx.is_biconnected(G)
    cut = nx.minimum_node_cut(G, flow_func=flow_func)
    assert len(cut) == 1
    assert cut.pop() in set(nx.articulation_points(G))


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_brandes_erlebach_book(flow_func):
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
    # edge cutsets
    assert 3 == len(nx.minimum_edge_cut(G, 1, 11, flow_func=flow_func))
    edge_cut = nx.minimum_edge_cut(G, flow_func=flow_func)
    # Node 5 has only two edges
    assert 2 == len(edge_cut)
    H = G.copy()
    H.remove_edges_from(edge_cut)
    assert not nx.is_connected(H)
    # node cuts
    assert {6, 7} == minimum_st_node_cut(G, 1, 11, flow_func=flow_func)
    assert {6, 7} == nx.minimum_node_cut(G, 1, 11, flow_func=flow_func)
    node_cut = nx.minimum_node_cut(G, flow_func=flow_func)
    assert 2 == len(node_cut)
    H = G.copy()
    H.remove_nodes_from(node_cut)
    assert not nx.is_connected(H)


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_white_harary_paper(flow_func):
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

    # edge cuts
    edge_cut = nx.minimum_edge_cut(G, flow_func=flow_func)
    assert 3 == len(edge_cut)
    H = G.copy()
    H.remove_edges_from(edge_cut)
    assert not nx.is_connected(H)
    # node cuts
    node_cut = nx.minimum_node_cut(G, flow_func=flow_func)
    assert {0} == node_cut
    H = G.copy()
    H.remove_nodes_from(node_cut)
    assert not nx.is_connected(H)


@pytest.mark.parametrize("flow_func", flow_funcs)
@pytest.mark.parametrize(
    ("G", "expected"),
    [
        (nx.petersen_graph(), 3),
        (nx.octahedral_graph(), 4),
        (nx.icosahedral_graph(), 5),
    ],
)
def test_node_edge_cutsets(flow_func, G, expected):
    # edge cuts
    edge_cut = nx.minimum_edge_cut(G, flow_func=flow_func)
    assert len(edge_cut) == expected
    H = G.copy()
    H.remove_edges_from(edge_cut)
    assert not nx.is_connected(H)
    # node cuts
    node_cut = nx.minimum_node_cut(G, flow_func=flow_func)
    assert len(node_cut) == expected
    H = G.copy()
    H.remove_nodes_from(node_cut)
    assert not nx.is_connected(H)


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_node_cutset_exception(flow_func):
    G = nx.Graph([(1, 2), (3, 4)])
    with pytest.raises(nx.NetworkXError, match="is not connected"):
        nx.minimum_node_cut(G, flow_func=flow_func)


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_node_cutset_random_graphs(flow_func):
    G = nx.fast_gnp_random_graph(50, 0.25, seed=42)  # A connected graph
    assert nx.is_connected(G)

    cutset = nx.minimum_node_cut(G, flow_func=flow_func)
    assert nx.node_connectivity(G) == len(cutset)
    G.remove_nodes_from(cutset)
    assert not nx.is_connected(G)


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_edge_cutset_random_graphs(flow_func):
    G = nx.fast_gnp_random_graph(50, 0.25, seed=42)  # A connected graph
    assert nx.is_connected(G)

    cutset = nx.minimum_edge_cut(G, flow_func=flow_func)
    assert nx.edge_connectivity(G) == len(cutset)
    G.remove_edges_from(cutset)
    assert not nx.is_connected(G)


@pytest.mark.parametrize("flow_func", flow_funcs)
@pytest.mark.parametrize("interface_func", interface_funcs)
@pytest.mark.parametrize("graph", [nx.Graph, nx.DiGraph])
def test_empty_graphs(flow_func, interface_func, graph):
    G = graph()

    with pytest.raises(nx.NetworkXPointlessConcept):
        interface_func(G, flow_func=flow_func)


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_unbounded(flow_func):
    G = nx.complete_graph(5)
    assert 4 == len(minimum_st_edge_cut(G, 1, 4, flow_func=flow_func))


@pytest.mark.parametrize("flow_func", flow_funcs)
@pytest.mark.parametrize("interface_func", interface_funcs)
def test_missing_source_target(flow_func, interface_func):
    G = nx.path_graph(4)

    # Source node not in graph
    with pytest.raises(nx.NetworkXError, match="node 10 not in graph"):
        interface_func(G, 10, 1, flow_func=flow_func)

    # Target node not in graph
    with pytest.raises(nx.NetworkXError, match="node 10 not in graph"):
        interface_func(G, 1, 10, flow_func=flow_func)


@pytest.mark.parametrize("flow_func", flow_funcs)
@pytest.mark.parametrize("interface_func", interface_funcs)
@pytest.mark.parametrize("graph", [nx.Graph, nx.DiGraph])
def test_not_connected(flow_func, interface_func, graph):
    # Input must be connected (weakly connected if digraph)
    G = graph([(1, 2), (2, 3), (4, 5)])

    with pytest.raises(nx.NetworkXError, match="graph is not connected"):
        interface_func(G, flow_func=flow_func)


@pytest.mark.parametrize("flow_func", flow_funcs)
@pytest.mark.parametrize("interface_func", interface_funcs)
@pytest.mark.parametrize("graph", [nx.Graph, nx.DiGraph])
def tests_min_cut_complete(flow_func, interface_func, graph):
    G = nx.complete_graph(5, create_using=graph)
    assert 4 == len(interface_func(G, flow_func=flow_func))


def tests_minimum_st_node_cut():
    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, 3, 7, 8, 11, 12])
    G.add_edges_from([(7, 11), (1, 11), (1, 12), (12, 8), (0, 1)])
    nodelist = minimum_st_node_cut(G, 7, 11)
    assert nodelist == set()


def test_invalid_auxiliary():
    G = nx.complete_graph(5)
    with pytest.raises(nx.NetworkXError, match="Invalid auxiliary digraph"):
        minimum_st_node_cut(G, 0, 3, auxiliary=G)


@pytest.mark.parametrize("interface_func", interface_funcs)
def test_interface_only_source(interface_func):
    G = nx.complete_graph(5)

    with pytest.raises(nx.NetworkXError, match="source and target must be specified"):
        interface_func(G, s=0)

    with pytest.raises(nx.NetworkXError, match="source and target must be specified"):
        interface_func(G, t=3)


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_directed_minimum_st_node_cut_reverse_edge(flow_func):
    # In a digraph an edge from t to s is not an s-t path, so s can still be
    # separated from t. Only a direct edge from s to t makes the pair
    # inseparable, and then the empty set is returned.
    G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])  # the directed triangle
    assert minimum_st_node_cut(G, 0, 2, flow_func=flow_func) == {1}
    assert minimum_st_node_cut(G, 0, 1, flow_func=flow_func) == set()


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_directed_minimum_node_cut(flow_func):
    # The node connectivity of the directed triangle is 1, so its minimum node
    # cut holds a single node. The initial cutset has to isolate the starting
    # node through its predecessors or its successors, whichever is smaller,
    # and not through its successors alone.
    G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])
    cut = nx.minimum_node_cut(G, flow_func=flow_func)
    assert len(cut) == nx.node_connectivity(G) == 1
    H = G.copy()
    H.remove_nodes_from(cut)
    assert not nx.is_strongly_connected(H)


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_directed_minimum_node_cut_not_strongly_connected(flow_func):
    # A weakly connected digraph that is not strongly connected is already
    # disconnected, so no node has to be removed and the cut is empty.
    G = nx.DiGraph([(0, 1), (1, 2), (2, 0), (3, 0)])  # a triangle and a source
    assert nx.is_weakly_connected(G)
    assert not nx.is_strongly_connected(G)
    assert nx.minimum_node_cut(G, flow_func=flow_func) == set()


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_directed_minimum_node_cut_both_orders(flow_func):
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
    cut = nx.minimum_node_cut(G, flow_func=flow_func)
    assert len(cut) == 1
    H = G.copy()
    H.remove_nodes_from(cut)
    assert not nx.is_strongly_connected(H)


@pytest.mark.parametrize("flow_func", flow_funcs)
def test_minimum_node_cut_self_loops(flow_func):
    # Self-loops do not affect node connectivity, so they must not enlarge the
    # minimum node cut either. The initial cutset is built from the neighbors
    # of the starting node, and a self-loop puts that node in its own cutset.
    G = nx.complete_graph(5)
    G.add_edges_from((u, u) for u in G)
    D = G.to_directed()
    assert len(nx.minimum_node_cut(G, flow_func=flow_func)) == 4
    assert len(nx.minimum_node_cut(D, flow_func=flow_func)) == 4
