import pytest

import networkx as nx
from networkx.algorithms.traversal import bsdfs, bsdfs_edges


def test_bsdfs_length_bound_and_target_set():
    G = nx.DiGraph([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 0)])

    assert list(bsdfs(G, 0, 3, 1)) == []
    assert list(bsdfs(G, 0, 3, 2)) == [[0, 1, 3], [0, 2, 3]]
    assert list(bsdfs(G, 0, {2, 3}, 3)) == [
        [0, 1, 2],
        [0, 1, 2, 3],
        [0, 1, 3],
        [0, 2],
        [0, 2, 3],
    ]


def test_bsdfs_cycles_and_trivial_path():
    G = nx.DiGraph([(0, 1), (1, 2), (2, 0)])

    assert list(bsdfs(G, 0, 0, 2)) == []
    assert list(bsdfs(G, 0, 0, 3)) == [[0, 1, 2, 0]]
    assert list(bsdfs(G, 0, {0}, 3)) == [[0]]


def test_bsdfs_validation():
    G = nx.DiGraph([(0, 1)])

    with pytest.raises(ValueError, match="length bound"):
        list(bsdfs(G, 0, 1, -1))
    with pytest.raises(ValueError, match="non-empty"):
        list(bsdfs(G, 0, set(), 1))
    with pytest.raises(nx.NodeNotFound, match="source node"):
        list(bsdfs(G, 2, 1, 1))
    with pytest.raises(nx.NodeNotFound, match="target"):
        list(bsdfs(G, 0, 2, 1))


def test_bsdfs_edges_simple_graph():
    G = nx.DiGraph([(0, 1), (0, 2), (1, 3), (2, 3)])

    assert list(bsdfs_edges(G, 0, 3, 2)) == [
        [(0, 1), (1, 3)],
        [(0, 2), (2, 3)],
    ]
    assert list(bsdfs_edges(G, 0, {0}, 2)) == [[]]


def test_bsdfs_edges_multigraph_parallel_edges():
    G = nx.MultiDiGraph()
    G.add_edges_from([(0, 1), (0, 1), (1, 2), (1, 2)])

    assert list(bsdfs(G, 0, 2, 2)) == [[0, 1, 2]]
    assert list(bsdfs_edges(G, 0, 2, 2)) == [
        [(0, 1, 0), (1, 2, 0)],
        [(0, 1, 0), (1, 2, 1)],
        [(0, 1, 1), (1, 2, 0)],
        [(0, 1, 1), (1, 2, 1)],
    ]


def test_bsdfs_hard_cycle_instances():
    # examples from:
    # Finding All Bounded-Length Simple Cycles in a Directed Graph -- Revisited
    # Frank Bauernöppel, Jörg-Rüdiger Sack 2026; https://arxiv.org/abs/2512.08392
    #
    # vs. CYCLE_SEARCH by Gupta-Suzumura https://arxiv.org/abs/2105.10094

    # A Counter-Example to CYCLE_SEARCH Completeness
    G = nx.parse_edgelist(
        ["A D", "A E", "B D", "B E", "C A", "C B", "D A", "D B", "E C"],
        create_using=nx.DiGraph,
    )
    s = "A"
    t = s
    k = 5
    assert list(bsdfs(G, s, t, k)) == [
        ["A", "D", "A"],
        ["A", "D", "B", "E", "C", "A"],
        ["A", "E", "C", "A"],
        ["A", "E", "C", "B", "D", "A"],  # missed by CYCLE_SEARCH
    ]

    # A Vertex Revisited Beyond the CYCLE_SEARCH Stated Bound
    G = nx.DiGraph()
    G.add_edges_from(
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
    assert list(bsdfs(G, s, t, k)) == [[1, 0, 2, 1], [1, 2, 1]]
    # nothing missed by CYCLE_SEARCH, so CYCLE_SEARCH would not assert, but detailed tracing will show:
    # with s = 1 and k =8, vertex 8 violates the stated delay bound:
    # between the outputs [1,0,2] and [1,2] it is visited 9 times — exceeding both k−1 = 7 and k = 8.


def test_bsdfs_hard_path_instances():
    # examples from:
    # Enumerating Length-Bounded Simple Paths and Cycles in Directed Graphs
    # with O(k(n+m)) Delay Using Edge-Consistent Node Barriers
    # Frank Bauernöppel, Jörg-Rüdiger Sack 2026; https://arxiv.org/abs/2607.14745
    #
    # vs. BC-DFS (You Peng et al. 2021; doi:10.1007/s00778-021-00674-5)

    # A Counter-Example to BC-DFS Completeness (Graph X)
    G = nx.parse_edgelist(
        ["A B", "A C", "B C", "B D", "B E", "C B", "C D", "D B"],
        create_using=nx.DiGraph,
    )
    s = "A"
    t = "E"
    k = 4
    assert list(bsdfs(G, s, t, k)) == [
        ["A", "B", "E"],
        ["A", "C", "B", "E"],
        ["A", "C", "D", "B", "E"],  # missed by BC-DFS
    ]

    #  A Counter-Example to BC-DFS Monotonicity (Graph Y)
    G = nx.parse_adjlist(
        ["A D", "B D E F", "C", "D A B C", "E A B D", "F B"], create_using=nx.DiGraph
    )
    s = "E"
    t = "C"
    k = 6
    assert list(bsdfs(G, s, t, k)) == [
        ["E", "A", "D", "C"],
        ["E", "B", "D", "C"],
        ["E", "D", "C"],
    ]
    # nothing missed by BC-DFS, so BC-DFS would not assert, but detailed tracing will show:
    # within the same interval, F is unstacked fruitless twice, contradicting their monotonicity claim
