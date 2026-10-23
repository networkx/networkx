import pytest

import networkx as nx
from networkx.algorithms.traversal import bsdfs, bsdfs_edges


def test_bsdfs_length_bound_and_target_set():
    G = nx.DiGraph([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 0)])

    assert list(bsdfs(G, 0, 3, length_bound=1)) == []
    assert list(bsdfs(G, 0, 3, length_bound=2)) == [[0, 1, 3], [0, 2, 3]]
    assert list(bsdfs(G, 0, {2, 3}, length_bound=3)) == [
        [0, 1, 2],
        [0, 1, 2, 3],
        [0, 1, 3],
        [0, 2],
        [0, 2, 3],
    ]


def test_bsdfs_cycles_and_trivial_path():
    G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])

    assert list(bsdfs(G, 0, 0, length_bound=2)) == []
    assert list(bsdfs(G, 0, 0, length_bound=3)) == [[0, 1, 2, 0]]
    assert list(bsdfs(G, 0, {0}, length_bound=3)) == [[0]]


def test_bsdfs_one_element_target_set():
    # a one-element set without the source gives the same paths as its
    # single node, although a search could continue through 2 to 1 and 3
    G = nx.DiGraph([(0, 1), (0, 2), (1, 2), (2, 1), (2, 3), (3, 0)])

    expected = [[0, 1, 2], [0, 2]]
    assert list(bsdfs(G, 0, 2, length_bound=3)) == expected
    assert list(bsdfs(G, 0, {2}, length_bound=3)) == expected


@pytest.mark.parametrize("func", [bsdfs, bsdfs_edges])
def test_bsdfs_validation(func):
    G = nx.DiGraph([(0, 1)])

    with pytest.raises(ValueError, match="length bound"):
        list(func(G, 0, 1, length_bound=-1))
    with pytest.raises(ValueError, match="non-empty"):
        list(func(G, 0, set(), length_bound=1))
    with pytest.raises(nx.NodeNotFound, match="source node"):
        list(func(G, 2, 1, length_bound=1))
    with pytest.raises(nx.NodeNotFound, match="target"):
        list(func(G, 0, 2, length_bound=1))


def test_bsdfs_edges_simple_graph():
    G = nx.DiGraph([(0, 1), (0, 2), (1, 3), (2, 3)])

    assert list(bsdfs_edges(G, 0, 3, length_bound=2)) == [
        [(0, 1), (1, 3)],
        [(0, 2), (2, 3)],
    ]
    assert list(bsdfs_edges(G, 0, {0}, length_bound=2)) == [[]]


def test_bsdfs_edges_multigraph_parallel_edges():
    G = nx.MultiDiGraph()
    G.add_edges_from([(0, 1), (0, 1), (1, 2), (1, 2)])

    assert list(bsdfs(G, 0, 2, length_bound=2)) == [[0, 1, 2]]
    assert list(bsdfs_edges(G, 0, 2, length_bound=2)) == [
        [(0, 1, 0), (1, 2, 0)],
        [(0, 1, 0), (1, 2, 1)],
        [(0, 1, 1), (1, 2, 0)],
        [(0, 1, 1), (1, 2, 1)],
    ]


def test_bsdfs_length_bound_zero():
    G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])

    assert list(bsdfs(G, 0, 0, length_bound=0)) == []
    assert list(bsdfs(G, 0, 2, length_bound=0)) == []
    assert list(bsdfs(G, 0, {0, 2}, length_bound=0)) == [[0]]


def test_bsdfs_self_loops():
    G = nx.DiGraph([(0, 0), (0, 1), (1, 1), (1, 2), (2, 2), (2, 0)])

    # a self-loop at the source is a cycle; self-loops elsewhere are skipped
    assert list(bsdfs(G, 0, 0, length_bound=3)) == [[0, 0], [0, 1, 2, 0]]
    assert list(bsdfs(G, 0, 2, length_bound=3)) == [[0, 1, 2]]
    assert list(bsdfs(G, 0, {1, 2}, length_bound=3)) == [[0, 1], [0, 1, 2]]


def test_bsdfs_undirected_graph():
    G = nx.Graph([(0, 1), (1, 2), (2, 0), (2, 3)])

    # cycles: [0, u, 0] for each neighbor u, longer cycles in both orientations
    assert list(bsdfs(G, 0, 0, length_bound=3)) == [
        [0, 1, 0],
        [0, 1, 2, 0],
        [0, 2, 1, 0],
        [0, 2, 0],
    ]
    assert list(bsdfs(G, 0, 3, length_bound=3)) == [[0, 1, 2, 3], [0, 2, 3]]
    assert list(bsdfs_edges(G, 0, 0, length_bound=2)) == [
        [(0, 1), (1, 0)],
        [(0, 2), (2, 0)],
    ]


def test_bsdfs_multiple_sources_via_virtual_source():
    # the recipe from the Notes: a virtual source joined to each source
    G = nx.DiGraph([(0, 1), (1, 2), (2, 3)])
    G.add_edges_from(("virtual", s) for s in [0, 1])

    # the bound is increased by 1 for the virtual edge; the sources do not
    # block one another, so [0, 1, 2, 3] passes through the source 1
    paths = [p[1:] for p in bsdfs(G, "virtual", 3, length_bound=3 + 1)]
    assert paths == [[0, 1, 2, 3], [1, 2, 3]]
    paths = [p[1:] for p in bsdfs(G, "virtual", 3, length_bound=2 + 1)]
    assert paths == [[1, 2, 3]]


def test_bsdfs_edges_cycle_and_target_set():
    G = nx.DiGraph([(0, 1), (0, 2), (1, 2), (2, 0)])

    assert list(bsdfs_edges(G, 0, 0, length_bound=3)) == [
        [(0, 1), (1, 2), (2, 0)],
        [(0, 2), (2, 0)],
    ]
    assert list(bsdfs_edges(G, 0, {1, 2}, length_bound=2)) == [
        [(0, 1)],
        [(0, 1), (1, 2)],
        [(0, 2)],
    ]


def test_bsdfs_cascade_reaches_indirect_predecessors():
    # A cascade that lowers only the barriers of direct predecessors
    # misses the cycle [4, 3, 1, 0, 2, 4].
    G = nx.DiGraph(
        [(0, 2), (0, 3), (1, 0), (2, 1), (2, 4), (3, 1), (4, 0), (4, 2), (4, 3)]
    )

    assert list(bsdfs(G, 4, 4, length_bound=5)) == [
        [4, 0, 2, 4],
        [4, 2, 4],
        [4, 3, 1, 0, 2, 4],
    ]


def test_bsdfs_shortest_distance_passed_to_parent():
    # A search that does not pass a finished node's shortest distance on
    # to its parent misses the path [2, 3, 1, 0].
    G = nx.DiGraph([(1, 0), (1, 2), (2, 1), (2, 3), (3, 1)])

    assert list(bsdfs(G, 2, {0, 2}, length_bound=4)) == [[2], [2, 1, 0], [2, 3, 1, 0]]


def test_bsdfs_edges_undirected_multigraph():
    G = nx.MultiGraph([(0, 1), (0, 1), (1, 2), (2, 0)])

    assert list(bsdfs(G, 0, 0, length_bound=2)) == [[0, 1, 0], [0, 2, 0]]
    assert list(bsdfs_edges(G, 0, 0, length_bound=2)) == [
        [(0, 1, 0), (1, 0, 0)],
        [(0, 1, 0), (1, 0, 1)],
        [(0, 1, 1), (1, 0, 0)],
        [(0, 1, 1), (1, 0, 1)],
        [(0, 2, 0), (2, 0, 0)],
    ]


def test_bsdfs_hard_cycle_instances():
    # examples from:
    # Finding All Bounded-Length Simple Cycles in a Directed Graph -- Revisited
    # Frank Bauernöppel, Jörg-Rüdiger Sack, 2026, https://arxiv.org/abs/2512.08392v2

    G = nx.parse_edgelist(
        ["A D", "A E", "B D", "B E", "C A", "C B", "D A", "D B", "E C"],
        create_using=nx.DiGraph,
    )
    s = "A"
    t = s
    k = 5
    assert list(bsdfs(G, s, t, length_bound=k)) == [
        ["A", "D", "A"],
        ["A", "D", "B", "E", "C", "A"],
        ["A", "E", "C", "A"],
        ["A", "E", "C", "B", "D", "A"],
    ]

    H = nx.DiGraph(
        [
            (0, 2),
            (0, 3),
            (0, 8),
            (1, 0),
            (1, 2),
            (2, 0),
            (2, 1),
            (2, 5),
            (3, 4),
            (3, 7),
            (3, 8),
            (4, 6),
            (4, 8),
            (5, 3),
            (6, 8),
            (7, 0),
            (8, 0),
        ]
    )
    s = 1
    t = s
    k = 8
    assert list(bsdfs(H, s, t, length_bound=k)) == [[1, 0, 2, 1], [1, 2, 1]]


def test_bsdfs_hard_path_instances():
    # examples from:
    # Enumerating Length-Bounded Simple Paths and Cycles in Directed Graphs
    # with O(k(n+m)) Delay Using Edge-Consistent Node Barriers
    # Frank Bauernöppel, Jörg-Rüdiger Sack 2026; https://arxiv.org/abs/2607.14745

    X = nx.parse_edgelist(
        ["A B", "A C", "B C", "B D", "B E", "C B", "C D", "D B"],
        create_using=nx.DiGraph,
    )
    s = "A"
    t = "E"
    k = 4
    assert list(bsdfs(X, s, t, length_bound=k)) == [
        ["A", "B", "E"],
        ["A", "C", "B", "E"],
        ["A", "C", "D", "B", "E"],
    ]

    Y = nx.parse_adjlist(
        ["A D", "B D E F", "C", "D A B C", "E A B D", "F B"], create_using=nx.DiGraph
    )
    s = "E"
    t = "C"
    k = 6
    assert list(bsdfs(Y, s, t, length_bound=k)) == [
        ["E", "A", "D", "C"],
        ["E", "B", "D", "C"],
        ["E", "D", "C"],
    ]
