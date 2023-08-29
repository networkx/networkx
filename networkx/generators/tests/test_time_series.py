"""Unit tests for the :mod:`networkx.generators.time_series` module."""
import networkx


class TestVisibilityGraph:
    """Unit tests for :func:`networkx.generators.time_series.visibility_graph`"""

    def test_static_series(self):
        # arrange
        series = range(10)
        expected_series_length = len(series)

        # act
        actual_graph = networkx.generators.time_series.visibility_graph(series)

        # assert
        assert actual_graph.number_of_nodes() == expected_series_length
        assert actual_graph.number_of_edges() == 9

    def test_cyclic_series(self):
        # arrange
        series = [2, 1, 3, 2, 1, 3, 2, 1, 3, 2, 1, 3]
        expected_series_length = len(series)

        # act
        actual_graph = networkx.generators.time_series.visibility_graph(series)

        # assert
        assert actual_graph.number_of_nodes() == expected_series_length
        assert actual_graph.number_of_edges() == 18
