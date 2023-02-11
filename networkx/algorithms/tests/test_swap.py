import pytest

import networkx as nx

def test_directed_edge_swap():
    ## Testing a path graph
    G=nx.DiGraph()
    G.add_nodes_from([1,200])
    for i in range(200):
        if(i!=0):
            G.add_edges_from([(i,i+1)])

    G_orig=G.copy() 
    directed_edge_swap(G)
    in_degrees_orig = sorted((n, d) for n, d in G_orig.in_degree())
    out_degrees_orig = sorted((n, d) for n, d in G_orig.out_degree())

    assert in_degrees_orig == sorted((n, d) for n, d in G.in_degree())
    assert out_degrees_orig == sorted((n, d) for n, d in G.out_degree())
    assert sorted((n, d) for n, d in G_orig.edges)!=sorted((n, d) for n, d in G.edges)

    
    ## Testing a complete graph with one directed edge for each pair
    graph=nx.DiGraph()
    no_of_nodes=200
    graph.add_nodes_from([1,no_of_nodes])
    temp=2
    for i in range(1,no_of_nodes-1):
        if(i!=no_of_nodes and i!=no_of_nodes-1):
            graph.add_edge(i,temp)
            temp+=1
            graph.add_edge(i,temp)
    graph.add_edges_from([(no_of_nodes-1,no_of_nodes),(no_of_nodes-1,1),(no_of_nodes,1),(no_of_nodes,2)])

    H=graph.copy()
    directed_edge_swap(graph)
    in_degrees_orig = sorted((n, d) for n, d in H.in_degree())
    out_degrees_orig = sorted((n, d) for n, d in H.out_degree())
    assert in_degrees_orig == sorted((n, d) for n, d in graph.in_degree())
    assert out_degrees_orig == sorted((n, d) for n, d in graph.out_degree())
    assert sorted((n, d) for n, d in graph.edges)!=sorted((n, d) for n, d in H.edges)


def test_edge_cases_directed_edge_swap():
    # Tests cases when swaps are impossible, either too few edges exist, or self loops/cycles are unavoidable
    # TODO: Rewrite function to explicitly check for impossible swaps and raise error
    e = (
        "Maximum number of swap attempts \\(11\\) exceeded "
        "before desired swaps achieved \\(\\d\\)."
    )
    graph = nx.DiGraph([(0, 0), (0, 1), (1, 0), (2, 3), (3, 2)])
    with pytest.raises(nx.NetworkXAlgorithmError, match=e):
        nx.directed_edge_swap(graph, nswap=1, max_tries=10, seed=1)


def test_double_edge_swap():
    graph = nx.barabasi_albert_graph(200, 1)
    degrees = sorted(d for n, d in graph.degree())
    G = nx.double_edge_swap(graph, 40)
    assert degrees == sorted(d for n, d in graph.degree())


def test_double_edge_swap_seed():
    graph = nx.barabasi_albert_graph(200, 1)
    degrees = sorted(d for n, d in graph.degree())
    G = nx.double_edge_swap(graph, 40, seed=1)
    assert degrees == sorted(d for n, d in graph.degree())


def test_connected_double_edge_swap():
    graph = nx.barabasi_albert_graph(200, 1)
    degrees = sorted(d for n, d in graph.degree())
    G = nx.connected_double_edge_swap(graph, 40, seed=1)
    assert nx.is_connected(graph)
    assert degrees == sorted(d for n, d in graph.degree())


def test_connected_double_edge_swap_low_window_threshold():
    graph = nx.barabasi_albert_graph(200, 1)
    degrees = sorted(d for n, d in graph.degree())
    G = nx.connected_double_edge_swap(graph, 40, _window_threshold=0, seed=1)
    assert nx.is_connected(graph)
    assert degrees == sorted(d for n, d in graph.degree())


def test_connected_double_edge_swap_star():
    # Testing ui==xi in connected_double_edge_swap
    graph = nx.star_graph(40)
    degrees = sorted(d for n, d in graph.degree())
    G = nx.connected_double_edge_swap(graph, 1, seed=4)
    assert nx.is_connected(graph)
    assert degrees == sorted(d for n, d in graph.degree())


def test_connected_double_edge_swap_star_low_window_threshold():
    # Testing ui==xi in connected_double_edge_swap with low window threshold
    graph = nx.star_graph(40)
    degrees = sorted(d for n, d in graph.degree())
    G = nx.connected_double_edge_swap(graph, 1, _window_threshold=0, seed=4)
    assert nx.is_connected(graph)
    assert degrees == sorted(d for n, d in graph.degree())


def test_directed_edge_swap_small():
    with pytest.raises(nx.NetworkXError):
        G = nx.directed_edge_swap(nx.path_graph(3, create_using=nx.DiGraph))


def test_directed_edge_swap_tries():
    with pytest.raises(nx.NetworkXError):
        G = nx.directed_edge_swap(
            nx.path_graph(3, create_using=nx.DiGraph), nswap=1, max_tries=0
        )


def test_directed_exception_undirected():
    graph = nx.Graph([(0, 1), (2, 3)])
    with pytest.raises(nx.NetworkXNotImplemented):
        G = nx.directed_edge_swap(graph)


def test_directed_edge_max_tries():
    with pytest.raises(nx.NetworkXAlgorithmError):
        G = nx.directed_edge_swap(
            nx.complete_graph(4, nx.DiGraph()), nswap=1, max_tries=5
        )


def test_double_edge_swap_small():
    with pytest.raises(nx.NetworkXError):
        G = nx.double_edge_swap(nx.path_graph(3))


def test_double_edge_swap_tries():
    with pytest.raises(nx.NetworkXError):
        G = nx.double_edge_swap(nx.path_graph(10), nswap=1, max_tries=0)


def test_double_edge_directed():
    graph = nx.DiGraph([(0, 1), (2, 3)])
    with pytest.raises(nx.NetworkXError, match="not defined for directed graphs."):
        G = nx.double_edge_swap(graph)


def test_double_edge_max_tries():
    with pytest.raises(nx.NetworkXAlgorithmError):
        G = nx.double_edge_swap(nx.complete_graph(4), nswap=1, max_tries=5)


def test_connected_double_edge_swap_small():
    with pytest.raises(nx.NetworkXError):
        G = nx.connected_double_edge_swap(nx.path_graph(3))


def test_connected_double_edge_swap_not_connected():
    with pytest.raises(nx.NetworkXError):
        G = nx.path_graph(3)
        nx.add_path(G, [10, 11, 12])
        G = nx.connected_double_edge_swap(G)


def test_degree_seq_c4():
    G = nx.cycle_graph(4)
    degrees = sorted(d for n, d in G.degree())
    G = nx.double_edge_swap(G, 1, 100)
    assert degrees == sorted(d for n, d in G.degree())


def test_fewer_than_4_nodes():
    G = nx.DiGraph()
    G.add_nodes_from([0, 1, 2])
    with pytest.raises(nx.NetworkXError, match=".*fewer than four nodes."):
        nx.directed_edge_swap(G)


def test_less_than_3_edges():
    G = nx.DiGraph([(0, 1), (1, 2)])
    G.add_nodes_from([3, 4])
    with pytest.raises(nx.NetworkXError, match=".*fewer than 3 edges"):
        nx.directed_edge_swap(G)

    G = nx.Graph()
    G.add_nodes_from([0, 1, 2, 3])
    with pytest.raises(nx.NetworkXError, match=".*fewer than 2 edges"):
        nx.double_edge_swap(G)
