"""Unit tests for the :mod:`networkx.algorithms.approximation.kcutsets` module."""

import pytest
import networkx as nx
from networkx.algorithms.approximation import minimum_multiway_cut, minimum_k_cut
from networkx import minimum_cut_value


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
            minimum_multiway_cut(G, G.nodes())

    def test_undirected_non_connected(self):
        """Test an undirected disconnected graph."""
        G = nx.path_graph(10)
        G.remove_edge(3, 4)
        with pytest.raises(nx.NetworkXError, match="Graph not connected."):
            minimum_multiway_cut(G, G.nodes())

    def test_invalid_terminals(self):
        """Test empty terminals."""

        G = nx.path_graph(10)
        with pytest.raises(
            nx.NetworkXError, match="At least two terminals should be provided."
        ):
            minimum_multiway_cut(G, [])

    def test_path_graph_unweighted(self):
        """Test min multiway cut for a path graph."""
        G = nx.path_graph(2)
        cut_value, cutset = minimum_multiway_cut(G, [0, 1])
        assert cut_value == 1
        G.remove_edges_from(cutset)
        assert len(list(nx.connected_components(G))) == 2

    def test_path_graph_weighted(self):
        """Test min multiway cut for a path graph with weights."""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [(0, 1, 10), (1, 2, 10), (2, 3, 5)], weight="capacity"
        )
        cut_value, cutset = minimum_multiway_cut(G, [0, 3], weight="capacity")
        assert cut_value == 5

    def test_complete_graph(self):
        """Test min multiway cut for a complete graph."""
        G = nx.complete_graph(5)
        cut_value, cutset = minimum_multiway_cut(G, G.nodes())
        assert cut_value == 10
        # remove the edges
        G.remove_edges_from(cutset)
        assert set(G.edges()) == set()

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
    def test_compare_min_cut(self, graph_class):
        """Compare minimum_cut_value and minimum_multiway_cut considering 2 nodes.

        For two nodes the minimum_cut_value(G, s, t) should be equivalent to
        minimum_multiway_cut(G, {s,t}).
        """
        G = graph_class()
        nx.set_edge_attributes(G, values=10, name="weight")
        s, t = min(G), max(G)
        cut_value, cutset = minimum_multiway_cut(G, {s, t}, weight="weight")
        assert cut_value == minimum_cut_value(G, s, t, capacity="weight")


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
            minimum_k_cut(G, 3)

    def test_undirected_non_connected(self):
        """Test an undirected disconnected graph."""
        G = nx.path_graph(10)
        G.remove_edge(3, 4)
        with pytest.raises(nx.NetworkXError, match="Graph not connected."):
            minimum_k_cut(G, 3)

    def test_invalid_k(self):
        """Test empty terminals."""
        G = nx.path_graph(10)
        with pytest.raises(nx.NetworkXError, match="k should be within 1 and 10"):
            minimum_k_cut(G, 0)
        with pytest.raises(nx.NetworkXError, match="k should be within 1 and 10"):
            minimum_k_cut(G, 11)

    def test_path_graph_unweighted(self):
        """Test min k-cut for a path graph."""
        G = nx.path_graph(2)
        cut_value, cutset = minimum_k_cut(G, 2)
        assert cut_value == 1
        G.remove_edges_from(cutset)
        assert len(list(nx.connected_components(G))) == 2

    def test_path_graph_weighted_k2(self):
        """Test min k-cut for a path graph with weights."""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [(0, 1, 10), (1, 2, 10), (2, 3, 5)], weight="capacity"
        )
        cut_value, cutset = minimum_k_cut(G, 2, weight="capacity")
        assert cut_value == 5
        G.remove_edges_from(cutset)
        assert len(list(nx.connected_components(G))) == 2

    def test_path_graph_weighted_k3(self):
        """Test min k-cut for a path graph with weights."""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [(0, 1, 10), (1, 2, 10), (2, 3, 5)], weight="capacity"
        )
        cut_value, cutset = minimum_k_cut(G, 3, weight="capacity")
        assert cut_value == 15
        G.remove_edges_from(cutset)
        assert len(list(nx.connected_components(G))) == 3

    def test_complete_graph_k2(self):
        """Test min k-cut for a complete graph for k=2."""
        G = nx.complete_graph(5)
        cut_value, cutset = minimum_k_cut(G, 2)
        # it should contain all the edges incident to a node
        assert cut_value == 4
        # remove the edges
        G.remove_edges_from(cutset)
        assert len(list(nx.connected_components(G))) == 2

    def test_complete_graph_all(self):
        """Test min k-cut for a complete graph."""
        G = nx.complete_graph(5)
        cut_value, cutset = minimum_k_cut(G, 5)
        assert cut_value == 10
        # remove the edges
        G.remove_edges_from(cutset)
        assert set(G.edges()) == set()

    def test_complete_graph_weighted(self):
        """Test min k-cut for a weighted complete graph."""
        G = nx.complete_graph(5)
        nx.set_edge_attributes(G, values=10, name="weight")
        cut_value, cutset = minimum_k_cut(G, 5, weight="weight")
        assert cut_value == 100
        # remove the edges
        G.remove_edges_from(cutset)
        assert set(G.edges()) == set()

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
    def test_compare_min_cut(self, graph_class, k):
        """Test multiple graph types and k."""
        G = graph_class()
        cut_value, cutset = minimum_k_cut(G, k)
        G.remove_edges_from(cutset)
        assert len(list(nx.connected_components(G))) >= k
