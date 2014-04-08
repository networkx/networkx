from nose.tools import assert_equal, assert_true, assert_false, raises
import networkx as nx
from networkx.algorithms.flow import preflow_push_value
from networkx.algorithms.flow import ford_fulkerson_value

flow_funcs = [None, ford_fulkerson_value, preflow_push_value]

# helper functions for tests
def _generate_no_biconnected(max_attempts=50):
    attempts = 0
    while True:
        G = nx.fast_gnp_random_graph(100, 0.0575)
        if nx.is_connected(G) and not nx.is_biconnected(G):
            attempts = 0
            yield G
        else:
            if attempts >= max_attempts:
                msg = "Tried %d times: no suitable Graph."
                raise Exception(msg % max_attempts)
            else:
                attempts += 1


# Tests for node and edge connectivity
def test_average_connectivity():
    # figure 1 from:
    # Beineke, L., O. Oellermann, and R. Pippert (2002). The average 
    # connectivity of a graph. Discrete mathematics 252(1-3), 31-45
    # http://www.sciencedirect.com/science/article/pii/S0012365X01001807
    G1 = nx.path_graph(3)
    G1.add_edges_from([(1, 3), (1, 4)])
    for flow_func in flow_funcs:
        assert_equal(nx.average_node_connectivity(G1, flow_func=flow_func), 1)
    G2 = nx.path_graph(3)
    G2.add_edges_from([(1, 3), (1, 4), (0, 3), (0, 4), (3, 4)])
    for flow_func in flow_funcs:
        assert_equal(nx.average_node_connectivity(G2, flow_func=flow_func), 2.2)
    G3 = nx.Graph()
    for flow_func in flow_funcs:
        assert_equal(nx.average_node_connectivity(G3, flow_func=flow_func), 0)

def test_average_connectivity_directed():
    G = nx.DiGraph([(1, 3), (1, 4), (1, 5)])
    for flow_func in flow_funcs:
        assert_equal(nx.average_node_connectivity(G, flow_func=flow_func), 0.25)


def test_articulation_points():
    Ggen = _generate_no_biconnected()
    for i in range(3):
        G = next(Ggen)
        for flow_func in flow_funcs:
            assert_equal(nx.node_connectivity(G, flow_func=flow_func), 1)

def test_brandes_erlebach():
    # Figure 1 chapter 7: Connectivity
    # http://www.informatik.uni-augsburg.de/thi/personen/kammer/Graph_Connectivity.pdf
    G = nx.Graph()
    G.add_edges_from([(1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 6), (3, 4),
                    (3, 6), (4, 6), (4, 7), (5, 7), (6, 8), (6, 9), (7, 8),
                    (7, 10), (8, 11), (9, 10), (9, 11), (10, 11)])
    for flow_func in flow_funcs:
        assert_equal(3, nx.local_edge_connectivity(G, 1, 11, flow_func=flow_func))
        assert_equal(3, nx.edge_connectivity(G, 1, 11, flow_func=flow_func))
        assert_equal(2, nx.local_node_connectivity(G, 1, 11, flow_func=flow_func))
        assert_equal(2, nx.node_connectivity(G, 1, 11, flow_func=flow_func))
        assert_equal(2, nx.edge_connectivity(G, flow_func=flow_func))
        assert_equal(2, nx.node_connectivity(G, flow_func=flow_func))

def test_white_harary_1():
    # Figure 1b white and harary (2001)
    # # http://eclectic.ss.uci.edu/~drwhite/sm-w23.PDF
    # A graph with high adhesion (edge connectivity) and low cohesion
    # (vertex connectivity)
    G = nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(4))
    G.remove_node(7)
    for i in range(4, 7):
        G.add_edge(0, i)
    G = nx.disjoint_union(G, nx.complete_graph(4))
    G.remove_node(G.order() - 1)
    for i in range(7, 10):
        G.add_edge(0, i)
    for flow_func in flow_funcs:
        assert_equal(1, nx.node_connectivity(G, flow_func=flow_func))
        assert_equal(3, nx.edge_connectivity(G, flow_func=flow_func))

def test_white_harary_2():
    # Figure 8 white and harary (2001)
    # # http://eclectic.ss.uci.edu/~drwhite/sm-w23.PDF
    G = nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(4))
    G.add_edge(0, 4)
    # kappa <= lambda <= delta
    assert_equal(3, min(nx.core_number(G).values()))
    for flow_func in flow_funcs:
        assert_equal(1, nx.node_connectivity(G, flow_func=flow_func))
        assert_equal(1, nx.edge_connectivity(G, flow_func=flow_func))

def test_complete_graphs():
    for n in range(5, 25, 5):
        G = nx.complete_graph(n)
        for flow_func in flow_funcs:
            assert_equal(n - 1, nx.node_connectivity(G, flow_func=flow_func))
            assert_equal(n - 1, nx.node_connectivity(G.to_directed(), 
                                                        flow_func=flow_func))
            assert_equal(n - 1, nx.edge_connectivity(G, flow_func=flow_func))
            assert_equal(n - 1, nx.edge_connectivity(G.to_directed(), 
                                                        flow_func=flow_func))

def test_empty_graphs():
    for k in range(5, 25, 5):
        G = nx.empty_graph(k)
        for flow_func in flow_funcs:
            assert_equal(0, nx.node_connectivity(G, flow_func=flow_func))
            assert_equal(0, nx.edge_connectivity(G, flow_func=flow_func))

def test_petersen():
    G = nx.petersen_graph()
    for flow_func in flow_funcs:
        assert_equal(3, nx.node_connectivity(G, flow_func=flow_func))
        assert_equal(3, nx.edge_connectivity(G, flow_func=flow_func))

def test_tutte():
    G = nx.tutte_graph()
    for flow_func in flow_funcs:
        assert_equal(3, nx.node_connectivity(G, flow_func=flow_func))
        assert_equal(3, nx.edge_connectivity(G, flow_func=flow_func))

def test_dodecahedral():
    G = nx.dodecahedral_graph()
    for flow_func in flow_funcs:
        assert_equal(3, nx.node_connectivity(G, flow_func=flow_func))
        assert_equal(3, nx.edge_connectivity(G, flow_func=flow_func))

def test_octahedral():
    G=nx.octahedral_graph()
    for flow_func in flow_funcs:
        assert_equal(4, nx.node_connectivity(G, flow_func=flow_func))
        assert_equal(4, nx.edge_connectivity(G, flow_func=flow_func))

def test_icosahedral():
    G=nx.icosahedral_graph()
    for flow_func in flow_funcs:
        assert_equal(5, nx.node_connectivity(G, flow_func=flow_func))
        assert_equal(5, nx.edge_connectivity(G, flow_func=flow_func))


@raises(nx.NetworkXError)
def test_missing_source():
    G = nx.path_graph(4)
    nx.node_connectivity(G, 10, 1)

@raises(nx.NetworkXError)
def test_missing_target():
    G = nx.path_graph(4)
    nx.node_connectivity(G, 1, 10)

@raises(nx.NetworkXError)
def test_edge_missing_source():
    G = nx.path_graph(4)
    nx.edge_connectivity(G, 10, 1)

@raises(nx.NetworkXError)
def test_edge_missing_target():
    G = nx.path_graph(4)
    nx.edge_connectivity(G, 1, 10)

def test_not_weakly_connected():
    G = nx.DiGraph()
    G.add_path([1, 2, 3])
    G.add_path([4, 5])
    assert_equal(nx.node_connectivity(G), 0)
    assert_equal(nx.edge_connectivity(G), 0)

def test_not_connected():
    G = nx.Graph()
    G.add_path([1, 2, 3])
    G.add_path([4, 5])
    assert_equal(nx.node_connectivity(G), 0)
    assert_equal(nx.edge_connectivity(G), 0)

def test_directed_edge_connectivity():
    G = nx.cycle_graph(10,create_using=nx.DiGraph()) # only one direction
    D = nx.cycle_graph(10).to_directed() # 2 reciprocal edges
    for flow_func in flow_funcs:
        assert_equal(1, nx.edge_connectivity(G, flow_func=flow_func))
        assert_equal(1, nx.local_edge_connectivity(G, 1, 4, flow_func=flow_func))
        assert_equal(1, nx.edge_connectivity(G, 1, 4, flow_func=flow_func))
        assert_equal(2, nx.edge_connectivity(D, flow_func=flow_func))
        assert_equal(2, nx.local_edge_connectivity(D, 1, 4, flow_func=flow_func))
        assert_equal(2, nx.edge_connectivity(D, 1, 4, flow_func=flow_func))
