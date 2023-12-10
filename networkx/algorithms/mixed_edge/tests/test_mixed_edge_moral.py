import networkx as nx


def test_mixed_edge_moral_graph():
    digraph = nx.DiGraph()
    digraph.add_nodes_from([1, 2, 3, 4, 5, 6, 7])
    digraph.add_edges_from([(2, 3), (3, 6)])
    bigraph = nx.Graph([(3, 4), (4, 5), (7, 5)])
    bigraph.add_nodes_from(digraph)
    ungraph = nx.Graph([(1, 2), (4, 5), (2, 7)])
    ungraph.add_nodes_from(digraph)
    G = nx.MixedEdgeGraph(
        [digraph, bigraph, ungraph], ["directed", "bidirected", "undirected"]
    )

    expected_G = nx.Graph()
    expected_G.add_edges_from(
        [
            (1, 2),
            (2, 3),
            (2, 7),
            (3, 4),
            (4, 5),
            (3, 5),
            (3, 6),
            (5, 7),
            (2, 4),
            (7, 3),
            (7, 4),
            (2, 5),
        ]
    )

    result = nx.algorithms.mixed_edge_moral_graph(G)

    assert expected_G.edges() == result.edges()
