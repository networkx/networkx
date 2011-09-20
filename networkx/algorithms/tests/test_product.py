import networkx as nx
from networkx import tensor_product,cartesian_product,lexicographic_product,strong_product
from nose.tools import assert_raises, assert_true, assert_equal

def test_tensor_product_raises():
    G = nx.DiGraph()
    H = nx.Graph()
    assert_raises(nx.NetworkXError,tensor_product,G,H)

def test_tensor_product_null():
    null=nx.null_graph()
    empty10=nx.empty_graph(10)
    K3=nx.complete_graph(3)
    K10=nx.complete_graph(10)
    P3=nx.path_graph(3)
    P10=nx.path_graph(10)
    # null graph
    G=tensor_product(null,null)
    assert_true(nx.is_isomorphic(G,null))
    # null_graph X anything = null_graph and v.v.
    G=tensor_product(null,empty10)
    assert_true(nx.is_isomorphic(G,null))
    G=tensor_product(null,K3)
    assert_true(nx.is_isomorphic(G,null))
    G=tensor_product(null,K10)
    assert_true(nx.is_isomorphic(G,null))
    G=tensor_product(null,P3)
    assert_true(nx.is_isomorphic(G,null))
    G=tensor_product(null,P10)
    assert_true(nx.is_isomorphic(G,null))
    G=tensor_product(empty10,null)
    assert_true(nx.is_isomorphic(G,null))
    G=tensor_product(K3,null)
    assert_true(nx.is_isomorphic(G,null))
    G=tensor_product(K10,null)
    assert_true(nx.is_isomorphic(G,null))
    G=tensor_product(P3,null)
    assert_true(nx.is_isomorphic(G,null))
    G=tensor_product(P10,null)
    assert_true(nx.is_isomorphic(G,null))

def test_tensor_product_size():
    P5 = nx.path_graph(5)
    K3 = nx.complete_graph(3)
    K5 = nx.complete_graph(5)
    
    G=tensor_product(P5,K3)
    assert_equal(nx.number_of_nodes(G),5*3)
    G=tensor_product(K3,K5)
    assert_equal(nx.number_of_nodes(G),3*5)

def test_tensor_product_classic_result():
    K2 = nx.complete_graph(2)
    G = nx.petersen_graph()
    G = tensor_product(G,K2)
    assert_true(nx.is_isomorphic(G,nx.desargues_graph()))

    G = nx.cycle_graph(5)
    G = tensor_product(G,K2)
    assert_true(nx.is_isomorphic(G,nx.cycle_graph(10)))

    G = nx.tetrahedral_graph()
    G = tensor_product(G,K2)
    assert_true(nx.is_isomorphic(G,nx.cubical_graph()))

def test_tensor_product_random():
    G = nx.erdos_renyi_graph(10,2/10.)
    H = nx.erdos_renyi_graph(10,2/10.)
    GH = tensor_product(G,H)

    for (u_G,u_H) in GH.nodes_iter():
        for (v_G,v_H) in GH.nodes_iter():
            if H.has_edge(u_H,v_H) and G.has_edge(u_G,v_G):
                assert_true(GH.has_edge((u_G,u_H),(v_G,v_H)))
            else:
                assert_true(not GH.has_edge((u_G,u_H),(v_G,v_H)))


def test_cartesian_product_multigraph():
    G=nx.MultiGraph()
    G.add_edge(1,2,key=0)
    G.add_edge(1,2,key=1)
    H=nx.MultiGraph()
    H.add_edge(3,4,key=0)
    H.add_edge(3,4,key=1)
    GH=cartesian_product(G,H)
    assert_equal( set(GH) , set([(1, 3), (2, 3), (2, 4), (1, 4)]))
    assert_equal( set(GH.edges(keys=True)) ,
                  set([((1, 3), (2, 3), 0), ((1, 3), (2, 3), 1), 
                       ((1, 3), (1, 4), 0), ((1, 3), (1, 4), 1), 
                       ((2, 3), (2, 4), 0), ((2, 3), (2, 4), 1), 
                       ((2, 4), (1, 4), 0), ((2, 4), (1, 4), 1)]))    

def test_cartesian_product_raises():
    G = nx.DiGraph()
    H = nx.Graph()
    assert_raises(nx.NetworkXError,cartesian_product,G,H)

def test_cartesian_product_null():
    null=nx.null_graph()
    empty10=nx.empty_graph(10)
    K3=nx.complete_graph(3)
    K10=nx.complete_graph(10)
    P3=nx.path_graph(3)
    P10=nx.path_graph(10)
    # null graph
    G=cartesian_product(null,null)
    assert_true(nx.is_isomorphic(G,null))
    # null_graph X anything = null_graph and v.v.
    G=cartesian_product(null,empty10)
    assert_true(nx.is_isomorphic(G,null))
    G=cartesian_product(null,K3)
    assert_true(nx.is_isomorphic(G,null))
    G=cartesian_product(null,K10)
    assert_true(nx.is_isomorphic(G,null))
    G=cartesian_product(null,P3)
    assert_true(nx.is_isomorphic(G,null))
    G=cartesian_product(null,P10)
    assert_true(nx.is_isomorphic(G,null))
    G=cartesian_product(empty10,null)
    assert_true(nx.is_isomorphic(G,null))
    G=cartesian_product(K3,null)
    assert_true(nx.is_isomorphic(G,null))
    G=cartesian_product(K10,null)
    assert_true(nx.is_isomorphic(G,null))
    G=cartesian_product(P3,null)
    assert_true(nx.is_isomorphic(G,null))
    G=cartesian_product(P10,null)
    assert_true(nx.is_isomorphic(G,null))

def test_cartesian_product_size():
    # order(GXH)=order(G)*order(H)
    K5=nx.complete_graph(5)
    P5=nx.path_graph(5)
    K3=nx.complete_graph(3)
    G=cartesian_product(P5,K3)
    assert_equal(nx.number_of_nodes(G),5*3)
    assert_equal(nx.number_of_edges(G),
                 nx.number_of_edges(P5)*nx.number_of_nodes(K3)+
                 nx.number_of_edges(K3)*nx.number_of_nodes(P5))
    G=cartesian_product(K3,K5)
    assert_equal(nx.number_of_nodes(G),3*5)
    assert_equal(nx.number_of_edges(G),
                 nx.number_of_edges(K5)*nx.number_of_nodes(K3)+
                 nx.number_of_edges(K3)*nx.number_of_nodes(K5))

def test_cartesian_product_classic():
    # test some classic product graphs
    P2 = nx.path_graph(2)
    P3 = nx.path_graph(3)
    # cube = 2-path X 2-path
    G=cartesian_product(P2,P2)
    G=cartesian_product(P2,G)
    assert_true(nx.is_isomorphic(G,nx.cubical_graph()))

    # 3x3 grid
    G=cartesian_product(P3,P3)
    assert_true(nx.is_isomorphic(G,nx.grid_2d_graph(3,3)))

def test_cartesian_product_random():
    G = nx.erdos_renyi_graph(10,2/10.)
    H = nx.erdos_renyi_graph(10,2/10.)
    GH = cartesian_product(G,H)

    for (u_G,u_H) in GH.nodes_iter():
        for (v_G,v_H) in GH.nodes_iter():
            if (u_G==v_G and H.has_edge(u_H,v_H)) or \
               (u_H==v_H and G.has_edge(u_G,v_G)):
                assert_true(GH.has_edge((u_G,u_H),(v_G,v_H)))
            else:
                assert_true(not GH.has_edge((u_G,u_H),(v_G,v_H)))

def test_lexicographic_product_raises():
    G = nx.DiGraph()
    H = nx.Graph()
    assert_raises(nx.NetworkXError,lexicographic_product,G,H)

def test_lexicographic_product_null():
    null=nx.null_graph()
    empty10=nx.empty_graph(10)
    K3=nx.complete_graph(3)
    K10=nx.complete_graph(10)
    P3=nx.path_graph(3)
    P10=nx.path_graph(10)
    # null graph
    G=lexicographic_product(null,null)
    assert_true(nx.is_isomorphic(G,null))
    # null_graph X anything = null_graph and v.v.
    G=lexicographic_product(null,empty10)
    assert_true(nx.is_isomorphic(G,null))
    G=lexicographic_product(null,K3)
    assert_true(nx.is_isomorphic(G,null))
    G=lexicographic_product(null,K10)
    assert_true(nx.is_isomorphic(G,null))
    G=lexicographic_product(null,P3)
    assert_true(nx.is_isomorphic(G,null))
    G=lexicographic_product(null,P10)
    assert_true(nx.is_isomorphic(G,null))
    G=lexicographic_product(empty10,null)
    assert_true(nx.is_isomorphic(G,null))
    G=lexicographic_product(K3,null)
    assert_true(nx.is_isomorphic(G,null))
    G=lexicographic_product(K10,null)
    assert_true(nx.is_isomorphic(G,null))
    G=lexicographic_product(P3,null)
    assert_true(nx.is_isomorphic(G,null))
    G=lexicographic_product(P10,null)
    assert_true(nx.is_isomorphic(G,null))

def test_lexicographic_product_size():
    K5=nx.complete_graph(5)
    P5=nx.path_graph(5)
    K3=nx.complete_graph(3)
    G=lexicographic_product(P5,K3)
    assert_equal(nx.number_of_nodes(G),5*3)
    G=lexicographic_product(K3,K5)
    assert_equal(nx.number_of_nodes(G),3*5)

    #No classic easily found classic results for lexicographic product
def test_lexicographic_product_random():
    G = nx.erdos_renyi_graph(10,2/10.)
    H = nx.erdos_renyi_graph(10,2/10.)
    GH = lexicographic_product(G,H)

    for (u_G,u_H) in GH.nodes_iter():
        for (v_G,v_H) in GH.nodes_iter():
            if G.has_edge(u_G,v_G) or (u_G==v_G and H.has_edge(u_H,v_H)):
                assert_true(GH.has_edge((u_G,u_H),(v_G,v_H)))
            else:
                assert_true(not GH.has_edge((u_G,u_H),(v_G,v_H)))

def test_strong_product_raises():
    G = nx.DiGraph()
    H = nx.Graph()
    assert_raises(nx.NetworkXError,strong_product,G,H)

def test_strong_product_null():
    null=nx.null_graph()
    empty10=nx.empty_graph(10)
    K3=nx.complete_graph(3)
    K10=nx.complete_graph(10)
    P3=nx.path_graph(3)
    P10=nx.path_graph(10)
    # null graph
    G=strong_product(null,null)
    assert_true(nx.is_isomorphic(G,null))
    # null_graph X anything = null_graph and v.v.
    G=strong_product(null,empty10)
    assert_true(nx.is_isomorphic(G,null))
    G=strong_product(null,K3)
    assert_true(nx.is_isomorphic(G,null))
    G=strong_product(null,K10)
    assert_true(nx.is_isomorphic(G,null))
    G=strong_product(null,P3)
    assert_true(nx.is_isomorphic(G,null))
    G=strong_product(null,P10)
    assert_true(nx.is_isomorphic(G,null))
    G=strong_product(empty10,null)
    assert_true(nx.is_isomorphic(G,null))
    G=strong_product(K3,null)
    assert_true(nx.is_isomorphic(G,null))
    G=strong_product(K10,null)
    assert_true(nx.is_isomorphic(G,null))
    G=strong_product(P3,null)
    assert_true(nx.is_isomorphic(G,null))
    G=strong_product(P10,null)
    assert_true(nx.is_isomorphic(G,null))

def test_strong_product_size():
    K5=nx.complete_graph(5)
    P5=nx.path_graph(5)
    K3 = nx.complete_graph(3)
    G=strong_product(P5,K3)
    assert_equal(nx.number_of_nodes(G),5*3)
    G=strong_product(K3,K5)
    assert_equal(nx.number_of_nodes(G),3*5)

    #No classic easily found classic results for strong product
def test_strong_product_random():
    G = nx.erdos_renyi_graph(10,2/10.)
    H = nx.erdos_renyi_graph(10,2/10.)
    GH = strong_product(G,H)

    for (u_G,u_H) in GH.nodes_iter():
        for (v_G,v_H) in GH.nodes_iter():
            if (u_G==v_G and H.has_edge(u_H,v_H)) or \
               (u_H==v_H and G.has_edge(u_G,v_G)) or \
               (G.has_edge(u_G,v_G) and H.has_edge(u_H,v_H)):
                assert_true(GH.has_edge((u_G,u_H),(v_G,v_H)))
            else:
                assert_true(not GH.has_edge((u_G,u_H),(v_G,v_H)))
