import networkx as nx

def test_richcore():
    G=nx.Graph()
    G.add_edge('a','b',weight=0.6)
    G.add_edge('a','c',weight=0.2)
    G.add_edge('c','d',weight=0.1)
    G.add_edge('c','e',weight=0.7)
    G.add_edge('c','f',weight=0.9)
    G.add_edge('a','d',weight=0.3)

    sigmas, ranked_nodes, r_star = nx.richcore.extract_rich_core(G, weight='weight')
    assert_equal(sigmas, [0, 19.0, 19.0, 19.0, 10.999999999999998, 30.0])
    assert_equal(ranked_nodes, ['c', 'a', 'f', 'e', 'b', 'd'])
    assert_equal(r_star, 5)   
