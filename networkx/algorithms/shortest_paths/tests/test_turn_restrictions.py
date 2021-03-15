import pytest

import networkx as nx


class TestTurnRestrictions:
    @classmethod
    def setup_class(cls):
        # graph generated from Gutiérrez, E., & Medaglia, A. L. (2007). Labeling
        # algorithm for the shortest path problem with turn prohibitions with
        # application to large-scale road networks. Annals of Operations
        # Research, 157(1), 169–182. doi:10.1007/s10479-007-0198-9
        #
        #       6
        #
        #       ^
        #       |
        #       v
        #
        # 1 <-> 2 <-> 3
        #
        #       ^     ^
        #       |     |
        #       v     v
        #
        #       4 <-> 5
        #
        cls.G = nx.Graph()
        cls.G.add_edges_from([(1, 2), (2, 3), (2, 4), (2, 6), (2, 3), (3, 5), (4, 5)])

    @staticmethod
    def _restricted(u, v, w, _uv_edge, _vw_edge):
        """
        Implement the turn restrictions for the default graph.

        - no left turns at node 2
        - no U-Turns
        """
        invalid_left_turns = [(1, 2, 6), (3, 2, 4), (4, 2, 1)]

        triple = (u, v, w)
        return (triple in invalid_left_turns) or u == w

    def test_simple_graph(self):
        (length, path) = nx.shortest_path_with_turn_restrictions(
            self.G, 1, 6, self._restricted
        )

        assert length == 6
        assert path == [1, 2, 3, 5, 4, 2, 6]

    def test_multi_graph(self):
        MG = nx.MultiGraph(self.G)

        (length, path) = nx.shortest_path_with_turn_restrictions(
            MG, 1, 6, self._restricted
        )

        assert length == 6
        assert path == [1, 2, 3, 5, 4, 2, 6]

    def test_source_is_target(self):
        (length, path) = nx.shortest_path_with_turn_restrictions(
            self.G, 2, 2, self._restricted
        )

        assert length == 0
        assert path == [2]

    def test_source_not_found(self):
        with pytest.raises(nx.NodeNotFound):
            nx.shortest_path_with_turn_restrictions(self.G, 0, 6, self._restricted)

    def test_target_not_found(self):
        with pytest.raises(nx.NetworkXNoPath):
            nx.shortest_path_with_turn_restrictions(self.G, 1, 7, self._restricted)
