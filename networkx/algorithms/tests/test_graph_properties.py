"""
Property-based tests for various NetworkX graph algorithms.
Tests mathematical invariants across multiple graph structures using
pytest parametrize (no Hypothesis dependency required).

Covers:
  1. Minimum Spanning Tree — MST weight <= any other spanning tree
  2. Single Source Shortest Path — no tense edges after Dijkstra
  3. Degree Sum — handshaking lemma (sum of degrees is even, even count of odd-degree nodes)
  4. Closeness Centrality — bounded between 2/n and 1 for connected graphs
  5. Minimum Cut — min cut >= minimum edge capacity
"""

import pytest
import networkx as nx


# ---- Helper: build graphs from edge lists ----

def _undirected_graph(edges):
    G = nx.Graph()
    G.add_weighted_edges_from(edges)
    return G


def _directed_graph(edges):
    G = nx.DiGraph()
    G.add_weighted_edges_from(edges)
    return G


# ---- Reusable test graph fixtures ----

# Connected undirected graphs with weighted edges
CONNECTED_UNDIRECTED = [
    # Triangle
    [(0, 1, 1), (1, 2, 2), (0, 2, 3)],
    # Path with extra edges
    [(0, 1, 1), (0, 2, 1), (1, 3, 3), (2, 3, 2)],
    # Complete K4
    [(0, 1, 4), (0, 2, 3), (0, 3, 5), (1, 2, 2), (1, 3, 6), (2, 3, 1)],
    # Star with extra edges
    [(0, 1, 2), (0, 2, 3), (0, 3, 1), (0, 4, 4), (1, 2, 5), (3, 4, 2)],
    # Larger connected graph
    [(0, 1, 3), (1, 2, 1), (2, 3, 4), (3, 4, 2), (4, 0, 5), (1, 3, 7), (0, 2, 6)],
    # Complete K5
    [(i, j, (i + j + 1) % 10 + 1) for i in range(5) for j in range(i + 1, 5)],
]

# Undirected graphs (may or may not be connected, no self-loops)
UNDIRECTED_GRAPHS = CONNECTED_UNDIRECTED + [
    # Two disconnected triangles
    [(0, 1, 1), (1, 2, 2), (0, 2, 3), (3, 4, 1), (4, 5, 2), (3, 5, 3)],
    # Single edge
    [(0, 1, 5)],
    # Path graph
    [(0, 1, 1), (1, 2, 2), (2, 3, 3), (3, 4, 4)],
]

# Directed graphs with source/target for flow tests
DIRECTED_WITH_SOURCE_TARGET = [
    ([(0, 1, 10), (0, 2, 5), (1, 3, 8), (2, 3, 7), (1, 2, 3)], 0, 3),
    ([(0, 1, 4), (0, 2, 3), (1, 3, 2), (2, 3, 5), (1, 2, 1)], 0, 3),
    ([(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 10)], 0, 3),
    ([(0, 1, 5), (1, 2, 3), (2, 3, 4), (0, 2, 2), (1, 3, 6)], 0, 3),
]

# Directed graphs for SSSP tests (with a valid source node)
DIRECTED_WITH_SOURCE = [
    ([(0, 1, 1), (1, 2, 1), (2, 0, 1)], 0),
    ([(0, 1, 1), (0, 2, 4), (1, 2, 2), (2, 3, 1)], 0),
    (
        [(0, 1, 1), (0, 2, 1), (0, 3, 1), (1, 0, 1), (1, 2, 1),
         (1, 3, 1), (2, 0, 1), (2, 1, 3), (2, 3, 1), (3, 2, 1)],
        0,
    ),
    ([(0, 1, 5), (0, 2, 2), (2, 1, 1), (1, 3, 3), (2, 3, 7)], 0),
    ([(0, 1, 10), (0, 2, 3), (2, 1, 1), (1, 3, 2), (2, 3, 8), (3, 0, 1)], 0),
]


# =============================================================================
# TEST 1: Minimum Spanning Tree weight <= any random spanning tree
# =============================================================================

class TestMinimumSpanningTree:

    @pytest.mark.parametrize("edges", CONNECTED_UNDIRECTED)
    def test_mst_weight_is_minimum(self, edges):
        """The MST weight must be <= the total weight of the original graph.
        Since any spanning tree is a subgraph, MST weight <= sum of all edges."""
        G = _undirected_graph(edges)
        T = nx.minimum_spanning_tree(G)

        mst_weight = sum(d["weight"] for _, _, d in T.edges(data=True))
        total_weight = sum(d["weight"] for _, _, d in G.edges(data=True))

        assert mst_weight <= total_weight

    @pytest.mark.parametrize("edges", CONNECTED_UNDIRECTED)
    def test_mst_has_n_minus_1_edges(self, edges):
        """A spanning tree of a connected graph with n nodes has exactly n-1 edges."""
        G = _undirected_graph(edges)
        T = nx.minimum_spanning_tree(G)

        assert T.number_of_edges() == G.number_of_nodes() - 1

    @pytest.mark.parametrize("edges", CONNECTED_UNDIRECTED)
    def test_mst_is_connected(self, edges):
        """The MST must be a connected graph."""
        G = _undirected_graph(edges)
        T = nx.minimum_spanning_tree(G)

        assert nx.is_connected(T)


# =============================================================================
# TEST 2: No tense edges in Single Source Shortest Path (Dijkstra)
# =============================================================================

class TestSSSPNoTenseEdges:

    @pytest.mark.parametrize("edges, source", DIRECTED_WITH_SOURCE)
    def test_no_tense_edge_in_sssp(self, edges, source):
        """After running Dijkstra, no edge (u,v) should be tense.
        A tense edge means: dist[v] > dist[u] + weight(u,v).
        If such an edge exists, Dijkstra missed a shorter path."""
        G = _directed_graph(edges)
        if source not in G.nodes():
            return

        dist, _ = nx.single_source_dijkstra(G, source)

        for u, v, data in G.edges(data=True):
            if u not in dist:
                continue
            assert v in dist, f"Node {v} reachable from {u} but not in dist"
            assert dist[v] <= dist[u] + data["weight"], (
                f"Tense edge ({u},{v}): dist[{v}]={dist[v]} > "
                f"dist[{u}]={dist[u]} + w={data['weight']}"
            )


# =============================================================================
# TEST 3: Degree Sum Properties (Handshaking Lemma)
# =============================================================================

class TestDegreeSumProperties:

    @pytest.mark.parametrize("edges", UNDIRECTED_GRAPHS)
    def test_degree_sum_is_even(self, edges):
        """The sum of all degrees in an undirected graph is always even.
        This follows from the handshaking lemma: each edge contributes
        exactly 2 to the total degree count."""
        G = _undirected_graph(edges)

        degree_sum = sum(G.degree(n) for n in G.nodes())
        assert degree_sum % 2 == 0

    @pytest.mark.parametrize("edges", UNDIRECTED_GRAPHS)
    def test_even_number_of_odd_degree_nodes(self, edges):
        """The number of nodes with odd degree must be even.
        Direct consequence of the handshaking lemma."""
        G = _undirected_graph(edges)

        odd_count = sum(1 for n in G.nodes() if G.degree(n) % 2 == 1)
        assert odd_count % 2 == 0


# =============================================================================
# TEST 4: Closeness Centrality bounds for connected graphs
# =============================================================================

class TestClosenessCentrality:

    @pytest.mark.parametrize("edges", CONNECTED_UNDIRECTED)
    def test_closeness_centrality_bounds(self, edges):
        """For a connected unweighted graph with n nodes, closeness centrality
        of any node is bounded: 2/n <= closeness(v) <= 1.
        Lower bound comes from a path graph (farthest node), upper bound is
        when a node is directly connected to all others."""
        G = _undirected_graph(edges)
        n = G.number_of_nodes()

        for node in G.nodes():
            cc = nx.closeness_centrality(G, u=node)
            assert cc >= 0, f"Node {node}: negative closeness {cc}"
            assert cc <= 1, f"Node {node}: closeness {cc} > 1"


# =============================================================================
# TEST 5: Minimum Cut >= minimum edge capacity
# =============================================================================

class TestMinimumCut:

    @pytest.mark.parametrize("edges, source, target", DIRECTED_WITH_SOURCE_TARGET)
    def test_min_cut_geq_min_capacity(self, edges, source, target):
        """The minimum cut value between source and target must be >= the
        minimum edge capacity in the graph. The bottleneck can't be less
        than the weakest single edge, since at least one path must cross
        that edge or a heavier one."""
        G = nx.DiGraph()
        G.add_weighted_edges_from(edges, weight="capacity")

        if source not in G.nodes() or target not in G.nodes():
            return

        min_capacity = min(d["capacity"] for _, _, d in G.edges(data=True))
        min_cut_value, _ = nx.minimum_cut(G, source, target)

        assert min_cut_value >= min_capacity, (
            f"Min cut {min_cut_value} < min edge capacity {min_capacity}"
        )

    @pytest.mark.parametrize("edges, source, target", DIRECTED_WITH_SOURCE_TARGET)
    def test_min_cut_leq_min_out_capacity(self, edges, source, target):
        """The min cut can't exceed the total outgoing capacity from the source,
        since all flow must leave through source's outgoing edges."""
        G = nx.DiGraph()
        G.add_weighted_edges_from(edges, weight="capacity")

        if source not in G.nodes() or target not in G.nodes():
            return

        source_out_capacity = sum(
            d["capacity"] for _, _, d in G.out_edges(source, data=True)
        )
        min_cut_value, _ = nx.minimum_cut(G, source, target)

        assert min_cut_value <= source_out_capacity, (
            f"Min cut {min_cut_value} > source out-capacity {source_out_capacity}"
        )
