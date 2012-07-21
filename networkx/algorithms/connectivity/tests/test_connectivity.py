from nose.tools import assert_equal, assert_true, assert_false
import networkx as nx

# helper functions for tests
def _generate_no_biconnected(max_attempts=50):
    attempts = 0
    while True:
        G = nx.fast_gnp_random_graph(100,0.0575)
        if nx.is_connected(G) and not nx.is_biconnected(G):
            attempts = 0
            yield G
        else:
            if attempts >= max_attempts:
                msg = "Tried %d times: no suitable Graph."
                raise Exception(msg % max_attempts)
            else:
                attempts += 1

def is_dominating_set(G, nbunch):
    # Proposed by Dan on the mailing list
    allnodes=set(G)
    testset=set(n for n in nbunch if n in G)
    nbrs=set()
    for n in testset:
        nbrs.update(G[n])
    if nbrs - allnodes:  # some nodes left--not dominating
        return False
    else:
        return True

# Tests for node and edge connectivity
def test_average_connectivity():
    # figure 1 from:
    # Beineke, L., O. Oellermann, and R. Pippert (2002). The average 
    # connectivity of a graph. Discrete mathematics 252(1-3), 31-45
    # http://www.sciencedirect.com/science/article/pii/S0012365X01001807
    G1 = nx.path_graph(3)
    G1.add_edges_from([(1,3),(1,4)])
    assert_equal(nx.average_node_connectivity(G1),1)
    G2 = nx.path_graph(3)
    G2.add_edges_from([(1,3),(1,4),(0,3),(0,4),(3,4)])
    assert_equal(nx.average_node_connectivity(G2),2.2)
    G3 = nx.Graph()
    assert_equal(nx.average_node_connectivity(G3),0)

def test_articulation_points():
    Ggen = _generate_no_biconnected()
    for i in range(5):
        G = next(Ggen)
        assert_equal(nx.node_connectivity(G), 1)

def test_brandes_erlebach():
    # Figure 1 chapter 7: Connectivity
    # http://www.informatik.uni-augsburg.de/thi/personen/kammer/Graph_Connectivity.pdf
    G = nx.Graph()
    G.add_edges_from([(1,2),(1,3),(1,4),(1,5),(2,3),(2,6),(3,4),
                    (3,6),(4,6),(4,7),(5,7),(6,8),(6,9),(7,8),
                    (7,10),(8,11),(9,10),(9,11),(10,11)])
    assert_equal(3,nx.local_edge_connectivity(G,1,11))
    assert_equal(3,nx.edge_connectivity(G,1,11))
    assert_equal(2,nx.local_node_connectivity(G,1,11))
    assert_equal(2,nx.node_connectivity(G,1,11))
    assert_equal(2,nx.edge_connectivity(G)) # node 5 has degree 2
    assert_equal(2,nx.node_connectivity(G))

def test_white_harary_1():
    # Figure 1b white and harary (2001)
    # # http://eclectic.ss.uci.edu/~drwhite/sm-w23.PDF
    # A graph with high adhesion (edge connectivity) and low cohesion
    # (vertex connectivity)
    G = nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(4))
    G.remove_node(7)
    for i in range(4,7):
        G.add_edge(0,i)
    G = nx.disjoint_union(G, nx.complete_graph(4))
    G.remove_node(G.order()-1)
    for i in range(7,10):
        G.add_edge(0,i)
    assert_equal(1, nx.node_connectivity(G))
    assert_equal(3, nx.edge_connectivity(G))

def test_white_harary_2():
    # Figure 8 white and harary (2001)
    # # http://eclectic.ss.uci.edu/~drwhite/sm-w23.PDF
    G = nx.disjoint_union(nx.complete_graph(4), nx.complete_graph(4))
    G.add_edge(0,4)
    # kappa <= lambda <= delta
    assert_equal(3, min(nx.core_number(G).values()))
    assert_equal(1, nx.node_connectivity(G))
    assert_equal(1, nx.edge_connectivity(G))

def test_complete_graphs():
    for n in range(5, 25, 5):
        G = nx.complete_graph(n)
        assert_equal(n-1, nx.node_connectivity(G))
        assert_equal(n-1, nx.node_connectivity(G.to_directed()))
        assert_equal(n-1, nx.edge_connectivity(G))
        assert_equal(n-1, nx.edge_connectivity(G.to_directed()))

def test_empty_graphs():
    for k in range(5, 25, 5):
        G = nx.empty_graph(k)
        assert_equal(0, nx.node_connectivity(G))
        assert_equal(0, nx.edge_connectivity(G))

def test_petersen():
    G = nx.petersen_graph()
    assert_equal(3, nx.node_connectivity(G))
    assert_equal(3, nx.edge_connectivity(G))

def test_tutte():
    G = nx.tutte_graph()
    assert_equal(3, nx.node_connectivity(G))
    assert_equal(3, nx.edge_connectivity(G))

def test_dodecahedral():
    G = nx.dodecahedral_graph()
    assert_equal(3, nx.node_connectivity(G))
    assert_equal(3, nx.edge_connectivity(G))

def test_octahedral():
    G=nx.octahedral_graph()
    assert_equal(4, nx.node_connectivity(G))
    assert_equal(4, nx.edge_connectivity(G))

def test_icosahedral():
    G=nx.icosahedral_graph()
    assert_equal(5, nx.node_connectivity(G))
    assert_equal(5, nx.edge_connectivity(G))

def test_directed_edge_connectivity():
    G = nx.cycle_graph(10,create_using=nx.DiGraph()) # only one direction
    D = nx.cycle_graph(10).to_directed() # 2 reciprocal edges
    assert_equal(1, nx.edge_connectivity(G))
    assert_equal(1, nx.local_edge_connectivity(G,1,4))
    assert_equal(1, nx.edge_connectivity(G,1,4))
    assert_equal(2, nx.edge_connectivity(D))
    assert_equal(2, nx.local_edge_connectivity(D,1,4))
    assert_equal(2, nx.edge_connectivity(D,1,4))

def test_dominating_set():
    for i in range(5):
        G = nx.gnp_random_graph(100,0.1)
        D = nx.dominating_set(G)
        assert_true(is_dominating_set(G,D))
