from nose.tools import assert_equal, assert_true, assert_false, assert_raises
import networkx as nx

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
    for i in range(5):
        G = next(Ggen)
        cut = nx.minimum_node_cut(G)
        assert_true(len(cut) == 1)
        assert_true(cut.pop() in set(nx.articulation_points(G)))

def test_brandes_erlebach_book():
    # Figure 1 chapter 7: Connectivity
    # http://www.informatik.uni-augsburg.de/thi/personen/kammer/Graph_Connectivity.pdf
    G = nx.Graph()
    G.add_edges_from([(1,2),(1,3),(1,4),(1,5),(2,3),(2,6),(3,4),
                    (3,6),(4,6),(4,7),(5,7),(6,8),(6,9),(7,8),
                    (7,10),(8,11),(9,10),(9,11),(10,11)])
    # edge cutsets
    assert_equal(3, len(nx.minimum_edge_cut(G,1,11)))
    edge_cut = nx.minimum_edge_cut(G)
    assert_equal(2, len(edge_cut)) # Node 5 has only two edges
    H = G.copy()
    H.remove_edges_from(edge_cut)
    assert_false(nx.is_connected(H))
    # node cuts
    assert_equal(set([6,7]), nx.minimum_st_node_cut(G,1,11))
    assert_equal(set([6,7]), nx.minimum_node_cut(G,1,11))
    node_cut = nx.minimum_node_cut(G)
    assert_equal(2,len(node_cut))
    H = G.copy()
    H.remove_nodes_from(node_cut)
    assert_false(nx.is_connected(H))

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
    # edge cuts
    edge_cut = nx.minimum_edge_cut(G)
    assert_equal(3, len(edge_cut))
    H = G.copy()
    H.remove_edges_from(edge_cut)
    assert_false(nx.is_connected(H))
    # node cuts
    node_cut = nx.minimum_node_cut(G)
    assert_equal(set([0]), node_cut)
    H = G.copy()
    H.remove_nodes_from(node_cut)
    assert_false(nx.is_connected(H))

def test_petersen_cutset():
    G = nx.petersen_graph()
    # edge cuts
    edge_cut = nx.minimum_edge_cut(G)
    assert_equal(3, len(edge_cut))
    H = G.copy()
    H.remove_edges_from(edge_cut)
    assert_false(nx.is_connected(H))
    # node cuts
    node_cut = nx.minimum_node_cut(G)
    assert_equal(3,len(node_cut))
    H = G.copy()
    H.remove_nodes_from(node_cut)
    assert_false(nx.is_connected(H))

def test_octahedral_cutset():
    G=nx.octahedral_graph()
    # edge cuts
    edge_cut = nx.minimum_edge_cut(G)
    assert_equal(4, len(edge_cut))
    H = G.copy()
    H.remove_edges_from(edge_cut)
    assert_false(nx.is_connected(H))
    # node cuts
    node_cut = nx.minimum_node_cut(G)
    assert_equal(4,len(node_cut))
    H = G.copy()
    H.remove_nodes_from(node_cut)
    assert_false(nx.is_connected(H))

def test_icosahedral_cutset():
    G=nx.icosahedral_graph()
    # edge cuts
    edge_cut = nx.minimum_edge_cut(G)
    assert_equal(5, len(edge_cut))
    H = G.copy()
    H.remove_edges_from(edge_cut)
    assert_false(nx.is_connected(H))
    # node cuts
    node_cut = nx.minimum_node_cut(G)
    assert_equal(5,len(node_cut))
    H = G.copy()
    H.remove_nodes_from(node_cut)
    assert_false(nx.is_connected(H))

def test_node_cutset_exception():
    G=nx.Graph()
    G.add_edges_from([(1,2),(3,4)])
    assert_raises(nx.NetworkXError, nx.minimum_node_cut,G)

def test_node_cutset_random_graphs():
    for i in range(5):
        G = nx.fast_gnp_random_graph(50,0.2)
        if not nx.is_connected(G):
            ccs = iter(nx.connected_components(G))
            start = next(ccs)[0]
            G.add_edges_from( (start,c[0]) for c in ccs )
        cutset = nx.minimum_node_cut(G)
        assert_equal(nx.node_connectivity(G), len(cutset))
        G.remove_nodes_from(cutset)
        assert_false(nx.is_connected(G))

def test_edge_cutset_random_graphs():
    for i in range(5):
        G = nx.fast_gnp_random_graph(50,0.2)
        if not nx.is_connected(G):
            ccs = iter(nx.connected_components(G))
            start = next(ccs)[0]
            G.add_edges_from( (start,c[0]) for c in ccs )
        cutset = nx.minimum_edge_cut(G)
        assert_equal(nx.edge_connectivity(G), len(cutset))
        G.remove_edges_from(cutset)
        assert_false(nx.is_connected(G))

# Test empty graphs
def test_empty_graphs():
    G = nx.Graph()
    D = nx.DiGraph()
    assert_raises(nx.NetworkXPointlessConcept, nx.minimum_node_cut, G)
    assert_raises(nx.NetworkXPointlessConcept, nx.minimum_node_cut, D)
    assert_raises(nx.NetworkXPointlessConcept, nx.minimum_edge_cut, G)
    assert_raises(nx.NetworkXPointlessConcept, nx.minimum_edge_cut, D)
