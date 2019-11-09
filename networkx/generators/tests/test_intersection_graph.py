# -*- encoding: utf-8 -*-
# test_intersection_graph.py - unit tests for intersection_graph generators
#
# Copyright 2010-2019 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Unit tests for the :mod:`networkx.generators.intersection_graph` module.
"""
import networkx as nx
from networkx.generators.intersection_graph import intersection_graph
import pytest


class TestIntersectionGraph:
    """Unit tests for
    :func:`networkx.generators.intersection_graph.intersection_graph`"""

    def test_intersection_graph_check_invalid(self):
        """ Tests for conditions that raise Exceptions """

        none_set = None
        assert intersection_graph(none_set) is None

        empty_set = []
        assert intersection_graph(empty_set) is None

        sets_not_collections = 12
        with pytest.raises(TypeError):
            intersection_graph(sets_not_collections)

        sets_string = 'intersection_graph'
        with pytest.raises(TypeError):
            intersection_graph(sets_string)

        invalids_having_none = [None, (1, 2)]
        with pytest.raises(TypeError):
            intersection_graph(invalids_having_none)

        invalids_having_length_0 = [[], (1, 2)]
        with pytest.raises(TypeError):
            intersection_graph(invalids_having_length_0)

        invalids_having_length_0 = [{}, (1, 2)]
        with pytest.raises(TypeError):
            intersection_graph(invalids_having_length_0)

        invalids_having_dict = [{1: 1}]
        with pytest.raises(TypeError):
            intersection_graph(invalids_having_dict)

    def test_intersection_graph_1(self):
        v1 = {1, 2}
        v2 = {1, 3}

        sets = [v1, v2]
        expected_graph = nx.Graph()
        expected_graph.add_nodes_from({tuple(sorted(v1)), tuple(sorted(v2))})

        e = ((1, 2), (1, 3))
        expected_graph.add_edge(*e)
        actual_g = intersection_graph(sets)

        assert actual_g.nodes == expected_graph.nodes
        assert actual_g.edges == expected_graph.edges

    def test_intersection_graph_2(self):
        v1 = [1, 2]
        v2 = (1, 3)

        sets = [v1, v2]
        expected_graph = nx.Graph()
        expected_graph.add_nodes_from({tuple(sorted(v1)), tuple(sorted(v2))})

        e = ((1, 2), (1, 3))
        expected_graph.add_edge(*e)
        actual_g = intersection_graph(sets)

        assert actual_g.nodes == expected_graph.nodes
        assert actual_g.edges == expected_graph.edges

    def test_intersection_graph_3(self):
        v1 = [1, 2]
        v2 = (1, 3)
        v3 = {1, 2}
        v4 = [2, 1]
        v5 = (2, 1)

        sets = [v1, v2, v3, v4, v5]
        expected_graph = nx.Graph()
        expected_graph.add_nodes_from({(1, 2), (1, 3)})

        e = ((1, 2), (1, 3))
        expected_graph.add_edge(*e)
        actual_g = intersection_graph(sets)

        assert actual_g.nodes == expected_graph.nodes
        assert actual_g.edges == expected_graph.edges

    def test_intersection_graph_4(self):
        v1 = [1, 2]
        v2 = (1, 3)
        v3 = {2, 4}
        v4 = {3, 4}

        sets = [v1, v2, v3, v4]
        expected_graph = nx.Graph()
        expected_graph.add_nodes_from({(1, 2), (1, 3), (2, 4), (3, 4)})

        e1 = ((1, 2), (1, 3))
        e2 = ((1, 2), (2, 4))
        e3 = ((1, 3), (3, 4))
        e4 = ((2, 4), (3, 4))
        expected_graph.add_edge(*e1)
        expected_graph.add_edge(*e2)
        expected_graph.add_edge(*e3)
        expected_graph.add_edge(*e4)

        actual_g = intersection_graph(sets)

        assert actual_g.nodes == expected_graph.nodes
        assert actual_g.edges == expected_graph.edges

    def test_intersection_graph_5(self):
        v1 = [1, 2]
        v2 = 3
        v3 = list(range(1, 6))

        sets = [v1, v2, v3]
        expected_graph = nx.Graph()
        expected_graph.add_nodes_from({(1, 2), (3, ), (1, 2, 3, 4, 5)})

        e1 = ((1, 2), (1, 2, 3, 4, 5))
        e2 = ((1, 2, 3, 4, 5), (3, ))

        expected_graph.add_edge(*e1)
        expected_graph.add_edge(*e2)

        actual_g = intersection_graph(sets)
        assert actual_g.nodes == expected_graph.nodes
        assert actual_g.edges == expected_graph.edges
