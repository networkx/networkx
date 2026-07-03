import pytest

import networkx as nx
from networkx import convert_node_labels_to_integers as cnlti


@pytest.fixture(params=[nx.find_cliques, nx.find_cliques_recursive])
def find_clique_fn(request):
    return request.param


@pytest.fixture
def G():
    z = [3, 4, 3, 4, 2, 4, 2, 1, 1, 1, 1]
    return cnlti(nx.generators.havel_hakimi_graph(z), first_label=1)


@pytest.mark.parametrize(
    ("nodes", "expected"),
    [
        (None, [[2, 6, 1, 3], [2, 6, 4], [5, 4, 7], [8, 9], [10, 11]]),
        ([2], [[2, 6, 1, 3], [2, 6, 4]]),
        ([2, 3], [[2, 6, 1, 3]]),
        ([2, 6, 4], [[2, 6, 4]]),
    ],
)
def test_find_cliques(G, find_clique_fn, nodes, expected):
    cl = list(find_clique_fn(G, nodes))
    assert sorted(map(sorted, cl)) == sorted(map(sorted, expected))


def test_selfloops(G, find_clique_fn):
    G.add_edge(1, 1)
    cl = list(find_clique_fn(G))
    expected = [[2, 6, 1, 3], [2, 6, 4], [5, 4, 7], [8, 9], [10, 11]]
    assert sorted(map(sorted, cl)) == sorted(map(sorted, expected))


def test_find_cliques2(find_clique_fn):
    H = nx.relabel_nodes(nx.complete_graph(6), {i: i + 1 for i in range(6)})
    H.remove_edges_from([(2, 6), (2, 5), (2, 4), (1, 3), (5, 3)])
    hcl = list(find_clique_fn(H))
    expected = [[1, 2], [1, 4, 5, 6], [2, 3], [3, 4, 6]]
    assert sorted(map(sorted, hcl)) == expected


def test_find_cliques_null(find_clique_fn):
    assert list(find_clique_fn(nx.null_graph())) == []


def test_find_cliques_not_clique(G, find_clique_fn):
    with pytest.raises(ValueError, match="do not form a clique"):
        list(find_clique_fn(G, [2, 6, 4, 1]))


@pytest.mark.parametrize("graph_type", [nx.DiGraph, nx.MultiDiGraph])
def test_find_cliques_directed(find_clique_fn, graph_type):
    DG = nx.path_graph(4, create_using=graph_type)
    msg = "not implemented for directed"
    with pytest.raises(nx.NetworkXNotImplemented, match=msg):
        list(find_clique_fn(DG))


@pytest.fixture
def cl(G):
    return list(nx.find_cliques(G))


def test_number_of_cliques_default_args(G, cl):
    expected = {
        1: 1,
        2: 2,
        3: 1,
        4: 2,
        5: 1,
        6: 2,
        7: 1,
        8: 1,
        9: 1,
        10: 1,
        11: 1,
    }
    assert nx.number_of_cliques(G) == expected
    assert nx.number_of_cliques(G, nodes=list(G)) == expected
    assert nx.number_of_cliques(G, cliques=cl) == expected
    assert nx.number_of_cliques(G, nodes=list(G), cliques=cl) == expected


@pytest.mark.parametrize(
    ("nodes", "expected"),
    [
        (1, 1),
        ([1], {1: 1}),
        ([1, 2], {1: 1, 2: 2}),
        (2, 2),
        (
            [2, 3, 4],
            {2: 2, 3: 1, 4: 2},
        ),
    ],
)
def test_number_of_cliques_nodes(G, cl, nodes, expected):
    assert nx.number_of_cliques(G, nodes=nodes) == expected
    assert nx.number_of_cliques(G, nodes=nodes, cliques=cl) == expected


def test_node_clique_number_default_args(G, cl):
    expected = {
        1: 4,
        2: 4,
        3: 4,
        4: 3,
        5: 3,
        6: 4,
        7: 3,
        8: 2,
        9: 2,
        10: 2,
        11: 2,
    }
    assert nx.node_clique_number(G) == expected
    assert nx.node_clique_number(G, nodes=list(G)) == expected
    assert nx.node_clique_number(G, cliques=cl) == expected
    assert nx.node_clique_number(G, nodes=list(G), cliques=cl) == expected


@pytest.mark.parametrize(
    ("nodes", "expected"), [(1, 4), ([1], {1: 4}), ([1, 2], {1: 4, 2: 4}), (2, 4)]
)
def test_node_clique_number_nodes(G, cl, nodes, expected):
    assert nx.node_clique_number(G, nodes=nodes) == expected
    assert nx.node_clique_number(G, nodes=nodes, cliques=cl) == expected


def test_make_clique_bipartite(G):
    B = nx.make_clique_bipartite(G)
    assert sorted(B) == [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    # Project onto the nodes of the original graph.
    H = nx.projected_graph(B, range(1, 12))
    assert H.adj == G.adj
    # Project onto the nodes representing the cliques.
    H1 = nx.projected_graph(B, range(-5, 0))
    # Relabel the negative numbers as positive ones.
    H1 = nx.relabel_nodes(H1, {-v: v for v in range(1, 6)})
    assert sorted(H1) == [1, 2, 3, 4, 5]


def test_make_max_clique_graph(G):
    """Tests that the maximal clique graph is the same as the bipartite
    clique graph after being projected onto the nodes representing the
    cliques.

    """
    B = nx.make_clique_bipartite(G)
    # Project onto the nodes representing the cliques.
    H1 = nx.projected_graph(B, range(-5, 0))
    # Relabel the negative numbers as nonnegative ones, starting at
    # 0.
    H1 = nx.relabel_nodes(H1, {-v: v - 1 for v in range(1, 6)})
    H2 = nx.make_max_clique_graph(G)
    assert H1.adj == H2.adj


def test_make_max_clique_graph_create_using():
    G = nx.Graph([(1, 2), (3, 1), (4, 1), (5, 6)])
    E = nx.Graph([(0, 1), (0, 2), (1, 2)])
    E.add_node(3)
    assert nx.is_isomorphic(nx.make_max_clique_graph(G, create_using=nx.Graph), E)


def test_enumerate_all_cliques():
    # Same graph as given in Fig. 4 of paper enumerate_all_cliques is
    # based on.
    # http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1559964&isnumber=33129
    G = nx.Graph()
    edges_fig_4 = [
        ("a", "b"),
        ("a", "c"),
        ("a", "d"),
        ("a", "e"),
        ("b", "c"),
        ("b", "d"),
        ("b", "e"),
        ("c", "d"),
        ("c", "e"),
        ("d", "e"),
        ("f", "b"),
        ("f", "c"),
        ("f", "g"),
        ("g", "f"),
        ("g", "c"),
        ("g", "d"),
        ("g", "e"),
    ]
    G.add_edges_from(edges_fig_4)

    cliques = list(nx.enumerate_all_cliques(G))
    clique_sizes = list(map(len, cliques))
    assert sorted(clique_sizes) == clique_sizes

    expected_cliques = [
        ["a"],
        ["b"],
        ["c"],
        ["d"],
        ["e"],
        ["f"],
        ["g"],
        ["a", "b"],
        ["a", "b", "d"],
        ["a", "b", "d", "e"],
        ["a", "b", "e"],
        ["a", "c"],
        ["a", "c", "d"],
        ["a", "c", "d", "e"],
        ["a", "c", "e"],
        ["a", "d"],
        ["a", "d", "e"],
        ["a", "e"],
        ["b", "c"],
        ["b", "c", "d"],
        ["b", "c", "d", "e"],
        ["b", "c", "e"],
        ["b", "c", "f"],
        ["b", "d"],
        ["b", "d", "e"],
        ["b", "e"],
        ["b", "f"],
        ["c", "d"],
        ["c", "d", "e"],
        ["c", "d", "e", "g"],
        ["c", "d", "g"],
        ["c", "e"],
        ["c", "e", "g"],
        ["c", "f"],
        ["c", "f", "g"],
        ["c", "g"],
        ["d", "e"],
        ["d", "e", "g"],
        ["d", "g"],
        ["e", "g"],
        ["f", "g"],
        ["a", "b", "c"],
        ["a", "b", "c", "d"],
        ["a", "b", "c", "d", "e"],
        ["a", "b", "c", "e"],
    ]

    assert sorted(map(sorted, cliques)) == sorted(map(sorted, expected_cliques))
