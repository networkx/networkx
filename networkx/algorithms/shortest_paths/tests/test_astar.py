import pytest

import networkx as nx
from networkx.utils import pairwise


from networkx.algorithms.shortest_paths.rtaa_star import (
    rtaa_star_path,
    rtaa_star_path_length,
)


class TestAStar:
    @classmethod
    def setup_class(cls):
        edges = [
            ("s", "u", 10),
            ("s", "x", 5),
            ("u", "v", 1),
            ("u", "x", 2),
            ("v", "y", 1),
            ("x", "u", 3),
            ("x", "v", 5),
            ("x", "y", 2),
            ("y", "s", 7),
            ("y", "v", 6),
        ]
        cls.XG = nx.DiGraph()
        cls.XG.add_weighted_edges_from(edges)

    def test_multiple_optimal_paths(self):
        """Tests that A* algorithm finds any of multiple optimal paths"""
        heuristic_values = {"a": 1.35, "b": 1.18, "c": 0.67, "d": 0}

        def h(u, v):
            return heuristic_values[u]

        graph = nx.Graph()
        points = ["a", "b", "c", "d"]
        edges = [("a", "b", 0.18), ("a", "c", 0.68), ("b", "c", 0.50), ("c", "d", 0.67)]

        graph.add_nodes_from(points)
        graph.add_weighted_edges_from(edges)

        path1 = ["a", "c", "d"]
        path2 = ["a", "b", "c", "d"]
        assert nx.astar_path(graph, "a", "d", h) in (path1, path2)

    def test_astar_directed(self):
        assert nx.astar_path(self.XG, "s", "v") == ["s", "x", "u", "v"]
        assert nx.astar_path_length(self.XG, "s", "v") == 9

    def test_astar_directed_weight_function(self):
        def w1(u, v, d):
            return d["weight"]

        assert nx.astar_path(self.XG, "x", "u", weight=w1) == ["x", "u"]
        assert nx.astar_path_length(self.XG, "x", "u", weight=w1) == 3
        assert nx.astar_path(self.XG, "s", "v", weight=w1) == ["s", "x", "u", "v"]
        assert nx.astar_path_length(self.XG, "s", "v", weight=w1) == 9

        def w2(u, v, d):
            return None if (u, v) == ("x", "u") else d["weight"]

        assert nx.astar_path(self.XG, "x", "u", weight=w2) == ["x", "y", "s", "u"]
        assert nx.astar_path_length(self.XG, "x", "u", weight=w2) == 19
        assert nx.astar_path(self.XG, "s", "v", weight=w2) == ["s", "x", "v"]
        assert nx.astar_path_length(self.XG, "s", "v", weight=w2) == 10

        def w3(u, v, d):
            return d["weight"] + 10

        assert nx.astar_path(self.XG, "x", "u", weight=w3) == ["x", "u"]
        assert nx.astar_path_length(self.XG, "x", "u", weight=w3) == 13
        assert nx.astar_path(self.XG, "s", "v", weight=w3) == ["s", "x", "v"]
        assert nx.astar_path_length(self.XG, "s", "v", weight=w3) == 30

    def test_astar_multigraph(self):
        G = nx.MultiDiGraph(self.XG)
        G.add_weighted_edges_from((u, v, 1000) for (u, v) in list(G.edges()))
        assert nx.astar_path(G, "s", "v") == ["s", "x", "u", "v"]
        assert nx.astar_path_length(G, "s", "v") == 9

    def test_astar_undirected(self):
        GG = self.XG.to_undirected()
        # make sure we get lower weight
        # to_undirected might choose either edge with weight 2 or weight 3
        GG["u"]["x"]["weight"] = 2
        GG["y"]["v"]["weight"] = 2
        assert nx.astar_path(GG, "s", "v") == ["s", "x", "u", "v"]
        assert nx.astar_path_length(GG, "s", "v") == 8

    def test_astar_directed2(self):
        XG2 = nx.DiGraph()
        edges = [
            (1, 4, 1),
            (4, 5, 1),
            (5, 6, 1),
            (6, 3, 1),
            (1, 3, 50),
            (1, 2, 100),
            (2, 3, 100),
        ]
        XG2.add_weighted_edges_from(edges)
        assert nx.astar_path(XG2, 1, 3) == [1, 4, 5, 6, 3]

    def test_astar_undirected2(self):
        XG3 = nx.Graph()
        edges = [(0, 1, 2), (1, 2, 12), (2, 3, 1), (3, 4, 5), (4, 5, 1), (5, 0, 10)]
        XG3.add_weighted_edges_from(edges)
        assert nx.astar_path(XG3, 0, 3) == [0, 1, 2, 3]
        assert nx.astar_path_length(XG3, 0, 3) == 15

    def test_astar_undirected3(self):
        XG4 = nx.Graph()
        edges = [
            (0, 1, 2),
            (1, 2, 2),
            (2, 3, 1),
            (3, 4, 1),
            (4, 5, 1),
            (5, 6, 1),
            (6, 7, 1),
            (7, 0, 1),
        ]
        XG4.add_weighted_edges_from(edges)
        assert nx.astar_path(XG4, 0, 2) == [0, 1, 2]
        assert nx.astar_path_length(XG4, 0, 2) == 4

    """ Tests that A* finds correct path when multiple paths exist
        and the best one is not expanded first (GH issue #3464)
    """

    def test_astar_directed3(self):
        heuristic_values = {"n5": 36, "n2": 4, "n1": 0, "n0": 0}

        def h(u, v):
            return heuristic_values[u]

        edges = [("n5", "n1", 11), ("n5", "n2", 9), ("n2", "n1", 1), ("n1", "n0", 32)]
        graph = nx.DiGraph()
        graph.add_weighted_edges_from(edges)
        answer = ["n5", "n2", "n1", "n0"]
        assert nx.astar_path(graph, "n5", "n0", h) == answer

    """ Tests that parent is not wrongly overridden when a node
        is re-explored multiple times.
    """

    def test_astar_directed4(self):
        edges = [
            ("a", "b", 1),
            ("a", "c", 1),
            ("b", "d", 2),
            ("c", "d", 1),
            ("d", "e", 1),
        ]
        graph = nx.DiGraph()
        graph.add_weighted_edges_from(edges)
        assert nx.astar_path(graph, "a", "e") == ["a", "c", "d", "e"]

    # >>> MXG4=NX.MultiGraph(XG4)
    # >>> MXG4.add_edge(0,1,3)
    # >>> NX.dijkstra_path(MXG4,0,2)
    # [0, 1, 2]

    def test_astar_w1(self):
        G = nx.DiGraph()
        G.add_edges_from(
            [
                ("s", "u"),
                ("s", "x"),
                ("u", "v"),
                ("u", "x"),
                ("v", "y"),
                ("x", "u"),
                ("x", "w"),
                ("w", "v"),
                ("x", "y"),
                ("y", "s"),
                ("y", "v"),
            ]
        )
        assert nx.astar_path(G, "s", "v") == ["s", "u", "v"]
        assert nx.astar_path_length(G, "s", "v") == 2

    def test_astar_nopath(self):
        with pytest.raises(nx.NodeNotFound):
            nx.astar_path(self.XG, "s", "moon")

    def test_astar_cutoff(self):
        with pytest.raises(nx.NetworkXNoPath):
            # optimal path_length in XG is 9
            nx.astar_path(self.XG, "s", "v", cutoff=8.0)
        with pytest.raises(nx.NetworkXNoPath):
            nx.astar_path_length(self.XG, "s", "v", cutoff=8.0)

    def test_astar_admissible_heuristic_with_cutoff(self):
        heuristic_values = {"s": 36, "y": 4, "x": 0, "u": 0, "v": 0}

        def h(u, v):
            return heuristic_values[u]

        assert nx.astar_path_length(self.XG, "s", "v") == 9
        assert nx.astar_path_length(self.XG, "s", "v", heuristic=h) == 9
        assert nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=12) == 9
        assert nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=9) == 9
        with pytest.raises(nx.NetworkXNoPath):
            nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=8)

    def test_astar_inadmissible_heuristic_with_cutoff(self):
        heuristic_values = {"s": 36, "y": 14, "x": 10, "u": 10, "v": 0}

        def h(u, v):
            return heuristic_values[u]

        # optimal path_length in XG is 9. This heuristic gives over-estimate.
        assert nx.astar_path_length(self.XG, "s", "v", heuristic=h) == 10
        assert nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=15) == 10
        with pytest.raises(nx.NetworkXNoPath):
            nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=9)
        with pytest.raises(nx.NetworkXNoPath):
            nx.astar_path_length(self.XG, "s", "v", heuristic=h, cutoff=12)

    def test_astar_cutoff2(self):
        assert nx.astar_path(self.XG, "s", "v", cutoff=10.0) == ["s", "x", "u", "v"]
        assert nx.astar_path_length(self.XG, "s", "v") == 9

    def test_cycle(self):
        C = nx.cycle_graph(7)
        assert nx.astar_path(C, 0, 3) == [0, 1, 2, 3]
        assert nx.dijkstra_path(C, 0, 4) == [0, 6, 5, 4]

    def test_unorderable_nodes(self):
        """Tests that A* accommodates nodes that are not orderable.

        For more information, see issue #554.

        """
        # Create the cycle graph on four nodes, with nodes represented as (unorderable) Python objects.
        nodes = [object() for n in range(4)]
        G = nx.Graph()
        G.add_edges_from(pairwise(nodes, cyclic=True))
        path = nx.astar_path(G, nodes[0], nodes[2])
        assert len(path) == 3

    def test_astar_NetworkXNoPath(self):
        """Tests that exception is raised when there exists no
        path between source and target"""
        G = nx.gnp_random_graph(10, 0.2, seed=10)
        with pytest.raises(nx.NetworkXNoPath):
            nx.astar_path(G, 4, 9)

    def test_astar_NodeNotFound(self):
        """Tests that exception is raised when either
        source or target is not in graph"""
        G = nx.gnp_random_graph(10, 0.2, seed=10)
        with pytest.raises(nx.NodeNotFound):
            nx.astar_path_length(G, 11, 9)


class TestRTAAStar:
    @staticmethod
    def test_source_node_not_found():
        """Source node is not in the graph."""
        G = nx.Graph()
        G.add_node(1)  # only node 1 exists
        with pytest.raises(nx.NodeNotFound):
            rtaa_star_path(G, source=2, target=1)

    @staticmethod
    def test_target_node_not_found():
        """Target node is not in the graph."""
        G = nx.Graph()
        G.add_node("A")
        # Source is present, target is missing
        with pytest.raises(nx.NodeNotFound):
            rtaa_star_path_length(G, source="A", target="B")

    @staticmethod
    def test_no_path_undirected():
        """No path should raise NetworkXNoPath 
        in an undirected graph."""
        G = nx.Graph()
        G.add_edge("a", "b")
        G.add_node("c")  # 'c' is isolated
        with pytest.raises(nx.NetworkXNoPath):
            rtaa_star_path_length(G, source="a", target="c")

    @staticmethod
    def test_no_path_directed():
        """No path should raise NetworkXNoPath 
        in a directed graph."""
        G = nx.DiGraph()
        G.add_edge(1, 2)
        G.add_node(3)  # 3 is present but unreachable from 1
        with pytest.raises(nx.NetworkXNoPath):
            rtaa_star_path(G, source=1, target=3)

    @staticmethod
    def test_same_source_target():
        """Path from a node to itself should be [node] with length 0."""
        G = nx.Graph()
        G.add_edge("X", "Y")  # add at least one edge to have the node in G
        assert rtaa_star_path(G, "X", "X") == ["X"]
        assert rtaa_star_path_length(G, "X", "X") == 0

    @staticmethod
    def test_directed_simple_path():
        """Find a simple path in a directed, 
        unweighted graph."""
        G = nx.DiGraph()
        G.add_edge("A", "B")
        G.add_edge("B", "C")
        # In this simple chain, 
        # the path should be A -> B -> C
        expected_path = ["A", "B", "C"]
        result_path = rtaa_star_path(G, "A", "C")
        result_length = rtaa_star_path_length(G, "A", "C")
        assert result_path == expected_path
        # Path length in unweighted graph = number of edges
        assert result_length == 2
        # Also verify against NetworkX shortest_path for sanity
        assert result_path == nx.shortest_path(G, "A", "C")

    @staticmethod
    def test_undirected_simple_path():
        """Find a simple path in an undirected, 
        unweighted graph."""
        G = nx.Graph()
        G.add_edge(1, 2)
        G.add_edge(2, 3)
        # Only one path exists: 1-2-3
        expected_path = [1, 2, 3]
        result_path = rtaa_star_path(G, 1, 3)
        result_length = rtaa_star_path_length(G, 1, 3)
        assert result_path == expected_path
        assert result_length == 2
        # Compare to NetworkX shortest_path as a cross-check
        assert result_path == nx.shortest_path(G, 1, 3)

    @staticmethod
    def test_weighted_directed_path():
        """Find shortest path in a directed graph 
        with weighted edges."""
        G = nx.DiGraph()
        # Two possible paths from A to C: A->C 
        # (cost 10) vs A->B->C (cost 2+2=4)
        G.add_edge("A", "C", weight=10)
        G.add_edge("A", "B", weight=2)
        G.add_edge("B", "C", weight=2)
        # Expect the algorithm to choose 
        # A -> B -> C with total cost 4
        result_path = rtaa_star_path(G, "A", "C")
        result_length = rtaa_star_path_length(G, "A", "C")
        expected_path = ["A", "B", "C"]
        expected_length = 4
        assert result_path == expected_path
        assert result_length == expected_length
        # Cross-verify with Dijkstra's algorithm
        assert result_path == nx.dijkstra_path(G, "A", "C")
        assert result_length == nx.dijkstra_path_length(G, "A", "C")

    @staticmethod
    def test_null_heuristic_equivalence():
        """With a null heuristic and unlimited lookahead, 
        results match Dijkstra'salgorithm."""
        G = nx.Graph()
        # Create a weighted graph with a unique shortest path
        G.add_edge(1, 2, weight=5)
        G.add_edge(2, 3, weight=1)
        G.add_edge(1, 3, weight=10)

        # Use heuristic = 0 and no lookahead limit
        def zero_heuristic(u, v):
            return 0

        path_none = rtaa_star_path(G, 1, 3, heuristic=zero_heuristic, lookahead=None)
        path_zero = rtaa_star_path(G, 1, 3, heuristic=zero_heuristic, lookahead=0)
        path_neg = rtaa_star_path(G, 1, 3, heuristic=zero_heuristic, lookahead=-1)
        length_none = rtaa_star_path_length(
            G, 1, 3, heuristic=zero_heuristic, lookahead=None
        )
        # All should produce the same result as Dijkstra
        expected_path = nx.dijkstra_path(G, 1, 3)
        expected_length = nx.dijkstra_path_length(G, 1, 3)
        assert path_none == expected_path
        assert length_none == expected_length
        # lookahead=0 or negative values should 
        # be treated as unlimited, so same path
        assert path_zero == expected_path
        assert path_neg == expected_path

    @staticmethod
    def test_heuristic_function_manhattan():
        """Use an explicit Manhattan distance 
        heuristic and compare to astar_path."""
        G = nx.Graph()
        # Assign coordinates for Manhattan distance 
        # calculation using node 'pos' attributes
        G.add_node("A", pos=(0, 0))
        G.add_node("B", pos=(1, 0))
        G.add_node("C", pos=(1, 1))
        # Weighted edges (A-B and B-C small, A-C larger) 
        # to ensure A-B-C is optimal
        G.add_edge("A", "B", weight=1)
        G.add_edge("B", "C", weight=1)
        G.add_edge("A", "C", weight=3)

        # Manhattan distance heuristic 
        # using node 'pos' attributes
        def manhattan(u, v):
            ux, uy = G.nodes[u]["pos"]
            vx, vy = G.nodes[v]["pos"]
            return abs(ux - vx) + abs(uy - vy)

        result_path = rtaa_star_path(G, "A", "C", heuristic=manhattan)
        result_length = rtaa_star_path_length(G, "A", "C", heuristic=manhattan)
        # Compute expected path and length 
        # using NetworkX A* for comparison
        expected_path = nx.astar_path(G, "A", "C", heuristic=manhattan, weight="weight")
        expected_length = nx.astar_path_length(
            G, "A", "C", heuristic=manhattan, weight="weight"
        )
        assert result_path == expected_path
        # The length returned by rtaa_star_path_length is 
        # float; compare with expected as numeric
        assert pytest.approx(result_length) == expected_length

    @staticmethod
    def test_landmarks_int_values():
        """Test various integer values for 
        landmarks parameter (including edge cases)."""
        # Graph: 0--1--2--3--4 (line graph)
        G = nx.path_graph(5)  # nodes 0,1,2,3,4 in a line (unweighted)
        baseline_path = rtaa_star_path(G, 0, 2)  # shortest path without landmarks
        # Try landmarks = 0 (no landmarks), 
        # positive ints, and a negative int
        for landmarks in [0, 1, 2, 3, 4, 5, -1]:
            path = rtaa_star_path(G, 0, 2, landmarks=landmarks)
            assert path == baseline_path

    @staticmethod
    def test_landmarks_list_valid():
        """Use an explicit list of landmarks 
        and verify correct path and length."""
        G = nx.path_graph(5)  # 0-1-2-3-4 line
        # Provide landmarks that exist in G 
        # (not necessarily including source/target)
        landmarks_list = [1, 3]
        result_path = rtaa_star_path(G, 0, 2, landmarks=landmarks_list)
        result_length = rtaa_star_path_length(G, 0, 2, landmarks=landmarks_list)
        # Baseline expected path and length without landmarks
        expected_path = nx.shortest_path(G, 0, 2)
        expected_length = nx.shortest_path_length(G, 0, 2)
        assert result_path == expected_path
        assert result_length == expected_length

    @staticmethod
    def test_landmarks_list_invalid():
        """Landmarks list containing a non-existent 
        node should raise NodeNotFound."""
        G = nx.path_graph(5)  # nodes 0-4
        # Landmarks includes node '5' which is not in the graph
        with pytest.raises(nx.NodeNotFound):
            rtaa_star_path(G, 0, 2, landmarks=[5])

    @staticmethod
    def test_move_limit_effect():
        """Different move_limit values should 
        yield the same final path for a given lookahead."""
        G = nx.path_graph(4)  # 0-1-2-3
        expected_path = [0, 1, 2, 3]
        # Use a small lookahead (e.g., 2 expansions) 
        # and vary move_limit
        base_path = rtaa_star_path(G, 0, 3, lookahead=2, move_limit=1)
        assert base_path == expected_path
        # move_limit=0 (treated as 1), move_limit=2, 
        # and a large move_limit should all give same path
        path_m0 = rtaa_star_path(G, 0, 3, lookahead=2, move_limit=0)
        path_m2 = rtaa_star_path(G, 0, 3, lookahead=2, move_limit=2)
        path_m_big = rtaa_star_path(G, 0, 3, lookahead=2, move_limit=10)
        assert path_m0 == expected_path
        assert path_m2 == expected_path
        assert path_m_big == expected_path

    @staticmethod
    def test_partial_lookahead_steps():
        """With limited lookahead, algorithm 
        still reaches target with correct path."""
        G = nx.path_graph(6)  # 0-1-2-3-4-5
        # Limit lookahead to 1 expansion per iteration 
        # (most restrictive) and default move_limit=1
        result_path = rtaa_star_path(G, 0, 5, lookahead=1, move_limit=1)
        result_length = rtaa_star_path_length(G, 0, 5, lookahead=1, move_limit=1)
        # Expected shortest path in this line 
        # graph is just the straight sequence of nodes
        expected_path = list(range(6))  # [0,1,2,3,4,5]
        expected_length = 5  # 5 edges
        assert result_path == expected_path
        assert result_length == expected_length

    @staticmethod
    def test_landmarks_with_lookahead():
        """Combine landmarks with limited lookahead and ensure correct behavior."""
        G = nx.path_graph(6)  # 0-1-2-3-4-5
        # Use landmarks and a limited lookahead, 
        # compare with same lookahead without landmarks
        path_with_lm = rtaa_star_path(G, 0, 5, lookahead=2, move_limit=1, landmarks=2)
        path_no_lm = rtaa_star_path(G, 0, 5, lookahead=2, move_limit=1, landmarks=None)
        assert path_with_lm == path_no_lm
        # Both should be the direct sequence [0,1,2,3,4,5]
        assert path_with_lm == list(range(6))

    @staticmethod
    def test_non_orderable_nodes():
        """Ensure algorithm works with nodes 
        that are not orderable (no __lt__ defined)."""

        # Define a simple class for unorderable nodes
        class Unorderable:
            def __init__(self, name):
                self.name = name

            def __repr__(self):
                return f"Unorderable({self.name})"

        # Create three nodes and a simple path between them
        a = Unorderable("a")
        b = Unorderable("b")
        c = Unorderable("c")
        G = nx.Graph()
        G.add_edge(a, b)  # unweighted edges
        G.add_edge(b, c)
        result_path = rtaa_star_path(G, a, c)
        result_length = rtaa_star_path_length(G, a, c)
        # Expected path is [a, b, c] with length 2
        assert result_path == [a, b, c]
        assert result_length == 2
