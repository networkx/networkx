"""Unit tests for the :mod:`networkx.algorithms.approximation.kcutsets` module."""

import itertools

import pytest

import networkx as nx
from networkx.algorithms import approximation as approx


class TestMinMultiwayCut:
    """Unit tests for the approximate Minimum Multiway Cut function
    :func:`~networkx.algorithms.approximation.kcutsets.minimum_multiway_cut`.
    """

    def test_null_graph(self):
        """Test empty graph."""
        G = nx.null_graph()
        with pytest.raises(
            nx.NetworkXError, match="Expected non-empty NetworkX graph!"
        ):
            approx.minimum_multiway_cut(G, G.nodes())

    def test_undirected_non_connected(self):
        """Test an undirected disconnected graph."""
        G = nx.path_graph(10)
        G.remove_edge(3, 4)
        with pytest.raises(nx.NetworkXError, match="Graph not connected."):
            approx.minimum_multiway_cut(G, G.nodes())

    def test_invalid_terminals(self):
        """Test empty terminals."""

        G = nx.path_graph(10)
        with pytest.raises(
            nx.NetworkXError, match="At least two terminals should be provided."
        ):
            approx.minimum_multiway_cut(G, [])

    def test_path_graph_unweighted(self):
        """Test min multiway cut for a path graph."""
        G = nx.path_graph(2)
        cut_value, cutset = approx.minimum_multiway_cut(G, [0, 1])
        assert cut_value == 1
        G.remove_edges_from(cutset)
        assert len(list(nx.connected_components(G))) == 2

    def test_path_graph_weighted(self):
        """Test min multiway cut for a path graph with weights."""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [(0, 1, 10), (1, 2, 10), (2, 3, 5)], weight="capacity"
        )
        cut_value, cutset = approx.minimum_multiway_cut(G, [0, 3], weight="capacity")
        assert cut_value == 5

    def test_complete_graph(self):
        """Test min multiway cut for a complete graph."""
        G = nx.complete_graph(5)
        cut_value, cutset = approx.minimum_multiway_cut(G, G.nodes())
        assert cut_value == 10
        # remove the edges
        G.remove_edges_from(cutset)
        assert set(G.edges()) == set()

    def test_single_terminal(self):
        """Test that a single terminal raises an error."""
        G = nx.path_graph(5)
        with pytest.raises(
            nx.NetworkXError, match="At least two terminals should be provided."
        ):
            approx.minimum_multiway_cut(G, [0])

    def test_terminals_not_in_graph(self):
        """Test terminals that are not in the graph are ignored."""
        G = nx.path_graph(5)
        # terminals 100 and 200 don't exist, only 0 and 4 are valid
        cut_value, cutset = approx.minimum_multiway_cut(G, [0, 4, 100, 200])
        assert cut_value == 1
        G.remove_edges_from(cutset)
        components = list(nx.connected_components(G))
        assert len(components) == 2

    def test_directed_graph_raises(self):
        """Test that directed graphs raise NetworkXNotImplemented."""
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3)])
        with pytest.raises(nx.NetworkXNotImplemented):
            approx.minimum_multiway_cut(G, [0, 3])

    def test_multigraph_raises(self):
        """Test that multigraphs raise NetworkXNotImplemented."""
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3)])
        with pytest.raises(nx.NetworkXNotImplemented):
            approx.minimum_multiway_cut(G, [0, 3])

    @pytest.mark.parametrize(
        "graph_class",
        [
            nx.krackhardt_kite_graph,
            nx.icosahedral_graph,
            nx.petersen_graph,
            nx.pappus_graph,
            nx.truncated_cube_graph,
            nx.tutte_graph,
        ],
    )
    @pytest.mark.parametrize("s,t", itertools.combinations(range(5), 2))
    def test_compare_min_cut(self, graph_class, s, t):
        """Compare minimum_cut_value and minimum_multiway_cut considering 2 nodes.

        For two nodes the minimum_cut_value(G, s, t) should be equivalent to
        minimum_multiway_cut(G, {s,t}).
        """
        G = graph_class()
        nx.set_edge_attributes(G, values=10, name="weight")
        cut_value, cutset = approx.minimum_multiway_cut(G, {s, t}, weight="weight")
        assert cut_value == nx.minimum_cut_value(G, s, t, capacity="weight")


class TestMinkCut:
    """Unit tests for the approximate Minimum k-Cut function
    :func:`~networkx.algorithms.approximation.kcutsets.minimum_k_cut`.
    """

    def test_null_graph(self):
        """Test empty graph."""
        G = nx.null_graph()
        with pytest.raises(
            nx.NetworkXError, match="Expected non-empty NetworkX graph!"
        ):
            approx.minimum_k_cut(G, 3)

    def test_undirected_non_connected(self):
        """Test an undirected disconnected graph."""
        G = nx.path_graph(10)
        G.remove_edge(3, 4)
        with pytest.raises(nx.NetworkXError, match="Graph not connected."):
            approx.minimum_k_cut(G, 3)

    def test_invalid_k(self):
        """Test invalid k values."""
        G = nx.path_graph(10)
        with pytest.raises(nx.NetworkXError, match="k should be within 1 and 10"):
            approx.minimum_k_cut(G, 0)
        with pytest.raises(nx.NetworkXError, match="k should be within 1 and 10"):
            approx.minimum_k_cut(G, 11)

    def test_directed_graph_raises(self):
        """Test that directed graphs raise NetworkXNotImplemented."""
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3)])
        with pytest.raises(nx.NetworkXNotImplemented):
            approx.minimum_k_cut(G, 2)

    def test_multigraph_raises(self):
        """Test that multigraphs raise NetworkXNotImplemented."""
        G = nx.MultiGraph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3)])
        with pytest.raises(nx.NetworkXNotImplemented):
            approx.minimum_k_cut(G, 2)

    def test_k_equals_one(self):
        """Test k=1 returns empty cutset with zero cut value."""
        G = nx.complete_graph(5)
        cut_value, cutset = approx.minimum_k_cut(G, 1)
        assert cut_value == 0
        assert len(cutset) == 0

    @pytest.mark.parametrize("k,expected", [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4)])
    def test_path_graph(self, k, expected):
        """Test various k for a path graph of 5 nodes."""
        G = nx.path_graph(n=5)
        cut_value, cutset = approx.minimum_k_cut(G, k, weight="capacity")
        assert cut_value == expected
        G.remove_edges_from(cutset)
        assert len(list(nx.connected_components(G))) == k

    @pytest.mark.parametrize("k,expected", [(1, 0), (2, 4), (3, 7), (4, 9), (5, 10)])
    def test_complete_graph(self, k, expected):
        """Test various k for a complete graph of 5 nodes."""
        G = nx.complete_graph(5)
        cut_value, cutset = approx.minimum_k_cut(G, k)
        assert cut_value == expected
        G.remove_edges_from(cutset)
        assert len(list(nx.connected_components(G))) >= k

    @pytest.mark.parametrize(
        "graph_class",
        [
            nx.krackhardt_kite_graph,
            nx.icosahedral_graph,
            nx.petersen_graph,
            nx.pappus_graph,
            nx.truncated_cube_graph,
            nx.tutte_graph,
        ],
    )
    @pytest.mark.parametrize("k", list(range(1, 11)))
    def test_connected_components(self, graph_class, k):
        """Test multiple graph types and k."""
        G = graph_class()
        cut_value, cutset = approx.minimum_k_cut(G, k)
        G.remove_edges_from(cutset)
        assert len(list(nx.connected_components(G))) >= k

    def test_complete_graph_weighted(self):
        """Test min k-cut for a weighted complete graph."""
        G = nx.complete_graph(5)
        nx.set_edge_attributes(G, values=10, name="weight")
        cut_value, cutset = approx.minimum_k_cut(G, 5, weight="weight")
        assert cut_value == 100
        # remove the edges
        G.remove_edges_from(cutset)
        assert set(G.edges()) == set()

    def test_path_graph_weighted(self):
        """Test min k-cut for a weighted path graph."""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [(0, 1, 10), (1, 2, 10), (2, 3, 5)], weight="capacity"
        )
        cut_value, cutset = approx.minimum_k_cut(G, 3, weight="capacity")
        assert cut_value == 15
        G.remove_edges_from(cutset)
        assert len(list(nx.connected_components(G))) == 3
