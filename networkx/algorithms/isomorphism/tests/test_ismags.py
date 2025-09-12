"""
Tests for ISMAGS isomorphism algorithm.
"""

import pytest

import networkx as nx
from networkx.algorithms import isomorphism as iso


def _matches_to_sets(matches):
    """
    Helper function to facilitate comparing collections of dictionaries in
    which order does not matter.
    """
    return {frozenset(m.items()) for m in matches}


class Testfind_start_node:
    def test_candidates_min_of_len(self):
        G = nx.path_graph(range(10, 15))
        H = nx.path_graph(range(20, 25))
        assert iso.ISMAGS(G, H).is_isomorphic()

        cand_sets = {
            10: set([frozenset([21, 22]), frozenset([20, 23, 22])]),
            11: set([frozenset([20]), frozenset([20, 23, 22, 21])]),
            12: set([frozenset([21, 22]), frozenset([20, 23, 22])]),
            13: set([frozenset([21, 22]), frozenset([20, 23, 22])]),
        }
        start_sgn = min(cand_sets, key=lambda n: min(len(x) for x in cand_sets[n]))
        assert start_sgn == 11
#        old_start_sgn = min(cand_sets, key=lambda n: min(cand_sets[n], key=len))
#        print(f"{start_sgn=} {old_start_sgn=}")
#        print(f"{min(len(x) for x in cand_sets[start_sgn])=}")
#        print(f"{min(cand_sets[start_sgn], key=len)=}")
#        assert start_sgn == old_start_sgn  # fails. min numb vs min size of frozensets

data = [
    # node_data, edge_data
    (range(1, 5), [(1, 2), (2, 4), (4, 3), (3, 1)]),
    (
        [
            (0, {"name": "a"}),
            (1, {"name": "a"}),
            (2, {"name": "b"}),
            (3, {"name": "b"}),
            (4, {"name": "a"}),
            (5, {"name": "a"}),
        ],
        [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
    ),
    (
        [],
        [  # 5-cycle with 2-paths stuck onto nodes 0, 2, 4
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 0),
            (0, 6),
            (6, 7),
            (2, 8),
            (8, 9),
            (4, 10),
            (10, 11),
        ],
    ),
    ([], [(0, 1), (1, 2), (1, 4), (2, 3), (3, 5), (3, 6)]),
    (
        # 5 - 4 \     / 12 - 13
        #        0 - 3
        # 9 - 8 /     \ 16 - 17
        # Assume 0 and 3 are coupled and no longer equivalent.
        # Coupling node 4 to 8 means that 5 and 9
        # are no longer equivalent, pushing them in their own partitions.
        # However, {5, 9} was considered equivalent to {13, 17}, which is *not*
        # taken into account in the second refinement, tripping a (former)
        # assertion failure. Note that this is actually the minimal failing
        # example.
        [],
        [
            (0, 3),
            (0, 4),
            (4, 5),
            (0, 8),
            (8, 9),
            (3, 12),
            (12, 13),
            (3, 16),
            (16, 17),
        ],
    ),
]


@pytest.mark.parametrize(["node_data", "edge_data"], data)
class TestSelfIsomorphism:
    def test_self_isomorphism(self, node_data, edge_data):
        """
        For some small, symmetric graphs, make sure that 1) they are isomorphic
        to themselves, and 2) that only the identity mapping is found.
        """
        graph = nx.Graph()
        graph.add_nodes_from(node_data)
        graph.add_edges_from(edge_data)

        ismags = iso.ISMAGS(
            graph, graph, node_match=iso.categorical_node_match("name", None)
        )
        assert ismags.is_isomorphic()
        assert ismags.is_isomorphic(True)
        assert ismags.subgraph_is_isomorphic()
        assert list(ismags.subgraph_isomorphisms_iter(symmetry=True)) == [
            {n: n for n in graph.nodes}
        ]

    def test_edgecase_self_isomorphism(self, node_data, edge_data):
        """
        This edgecase is one of the cases in which it is hard to find all
        symmetry elements.
        """
        graph = nx.Graph()
        nx.add_path(graph, range(5))
        graph.add_edges_from([(2, 5), (5, 6)])

        ismags = iso.ISMAGS(graph, graph)
        ismags_answer = list(ismags.find_isomorphisms(True))
        assert ismags_answer == [{n: n for n in graph.nodes}]

        graph = nx.relabel_nodes(graph, {0: 0, 1: 1, 2: 2, 3: 3, 4: 6, 5: 4, 6: 5})
        ismags = iso.ISMAGS(graph, graph)
        ismags_answer = list(ismags.find_isomorphisms(True))
        assert ismags_answer == [{n: n for n in graph.nodes}]

    def test_directed_self_isomorphism(self, node_data, edge_data):
        """
        For some small, directed, symmetric graphs, make sure that 1) they are
        isomorphic to themselves, and 2) that only the identity mapping is
        found.
        """
        graph = nx.Graph()
        graph.add_nodes_from(node_data)
        graph.add_edges_from(edge_data)

        ismags = iso.ISMAGS(
            graph, graph, node_match=iso.categorical_node_match("name", None)
        )
        assert ismags.is_isomorphic()
        assert ismags.subgraph_is_isomorphic()
        assert list(ismags.subgraph_isomorphisms_iter(symmetry=True)) == [
            {n: n for n in graph.nodes}
        ]


class TestSubgraphIsomorphism:
    def test_isomorphism(self):
        g1 = nx.Graph()
        nx.add_cycle(g1, range(4))

        g2 = nx.Graph()
        nx.add_cycle(g2, range(4))
        g2.add_edges_from(list(zip(g2, range(4, 8))))
        ismags = iso.ISMAGS(g2, g1)
        assert list(ismags.subgraph_isomorphisms_iter(symmetry=True)) == [
            {n: n for n in g1.nodes}
        ]

    def test_isomorphism2(self):
        g1 = nx.Graph()
        nx.add_path(g1, range(3))

        g2 = g1.copy()
        g2.add_edge(1, 3)

        ismags = iso.ISMAGS(g2, g1)
        matches = ismags.subgraph_isomorphisms_iter(symmetry=True)
        expected_symmetric = [
            {0: 0, 1: 1, 2: 2},
            {0: 0, 1: 1, 3: 2},
            {2: 0, 1: 1, 3: 2},
        ]
        assert _matches_to_sets(matches) == _matches_to_sets(expected_symmetric)

        matches = ismags.subgraph_isomorphisms_iter(symmetry=False)
        expected_asymmetric = [
            {0: 2, 1: 1, 2: 0},
            {0: 2, 1: 1, 3: 0},
            {2: 2, 1: 1, 3: 0},
        ]
        assert _matches_to_sets(matches) == _matches_to_sets(
            expected_symmetric + expected_asymmetric
        )

    def test_labeled_nodes(self):
        g1 = nx.Graph()
        nx.add_cycle(g1, range(3))
        g1.nodes[1]["attr"] = True

        g2 = g1.copy()
        g2.add_edge(1, 3)
        ismags = iso.ISMAGS(g2, g1, node_match=lambda x, y: x == y)
        matches = ismags.subgraph_isomorphisms_iter(symmetry=True)
        expected_symmetric = [{0: 0, 1: 1, 2: 2}]
        assert _matches_to_sets(matches) == _matches_to_sets(expected_symmetric)

        matches = ismags.subgraph_isomorphisms_iter(symmetry=False)
        expected_asymmetric = [{0: 2, 1: 1, 2: 0}]
        assert _matches_to_sets(matches) == _matches_to_sets(
            expected_symmetric + expected_asymmetric
        )

    def test_labeled_edges(self):
        g1 = nx.Graph()
        nx.add_cycle(g1, range(3))
        g1.edges[1, 2]["attr"] = True

        g2 = g1.copy()
        g2.add_edge(1, 3)
        ismags = iso.ISMAGS(g2, g1, edge_match=lambda x, y: x == y)
        matches = ismags.subgraph_isomorphisms_iter(symmetry=True)
        expected_symmetric = [{0: 0, 1: 1, 2: 2}]
        assert _matches_to_sets(matches) == _matches_to_sets(expected_symmetric)

        matches = ismags.subgraph_isomorphisms_iter(symmetry=False)
        expected_asymmetric = [{1: 2, 0: 0, 2: 1}]
        assert _matches_to_sets(matches) == _matches_to_sets(
            expected_symmetric + expected_asymmetric
        )


class TestWikipediaExample:
    # example in wikipedia is g1a and g2b
    # 1 have letter nodes, 2 have number nodes
    # b have some edges reversed vs a (undirected still isomorphic)
    # reversed edges marked with blank comment `#`
    # isomorphism = {'a': 1, 'g': 2, 'b': 3, 'c': 6, 'h': 4, 'i': 5, 'j': 7, 'd': 8}

    # Nodes 'a', 'b', 'c' and 'd' form a column.
    # Nodes 'g', 'h', 'i' and 'j' form a column.
    g1a_edges = [
        ["a", "g"],
        ["a", "h"], #
        ["a", "i"],
        ["b", "g"], #
        ["b", "h"],
        ["b", "j"],
        ["c", "g"], #
        ["c", "i"], #
        ["c", "j"],
        ["d", "h"], #
        ["d", "i"],
        ["d", "j"], #
    ]
    g1b_edges = [
        ["a", "g"],
        ["h", "a"], #
        ["a", "i"],
        ["g", "b"], #
        ["b", "h"],
        ["b", "j"],
        ["g", "c"], #
        ["i", "c"], #
        ["c", "j"],
        ["h", "d"], #
        ["d", "i"],
        ["j", "d"], #
    ]
    g2b_edges = [
        [1, 2],
        [1, 4], #
        [1, 5],
        [3, 2], #
        [3, 4],
        [3, 7],
        [6, 2], #
        [6, 5], #
        [6, 7],
        [8, 4], #
        [8, 5],
        [8, 7], #
    ]

    # Nodes 1,2,3,4 form the clockwise corners of a large square.
    # Nodes 5,6,7,8 form the clockwise corners of a small square
    g2a_edges = [
        [1, 2],
        [4, 1], #
        [1, 5],
        [2, 3], #
        [3, 4],
        [3, 7],
        [2, 6], #
        [5, 6], #
        [6, 7],
        [4, 8], #
        [8, 5],
        [7, 8], #
    ]

    def test_graph(self):
        g1a = nx.Graph(self.g1a_edges)
        g1b = nx.Graph(self.g1b_edges)
        g2a = nx.Graph(self.g2a_edges)
        g2b = nx.Graph(self.g2b_edges)
        assert iso.ISMAGS(g1a, g1b).is_isomorphic()
        assert iso.ISMAGS(g1a, g2a).is_isomorphic()
        assert iso.ISMAGS(g1a, g2b).is_isomorphic()

    def test_digraph(self):
        # 1 have letter nodes, 2 have number nodes
        # b have some edges reversed vs a
        # example in wikipedia is g1a and g2b
        g1a = nx.DiGraph(self.g1a_edges)
        g1b = nx.DiGraph(self.g1b_edges)
        g2a = nx.DiGraph(self.g2a_edges)
        g2b = nx.DiGraph(self.g2b_edges)
        assert iso.ISMAGS(g1a, g2b).is_isomorphic()
        assert iso.ISMAGS(g1b, g2a).is_isomorphic()
        assert not iso.ISMAGS(g1a, g1b).is_isomorphic()
        assert not iso.ISMAGS(g2a, g2b).is_isomorphic()
        assert not iso.ISMAGS(g1a, g2a).is_isomorphic()
        assert not iso.ISMAGS(g1b, g2b).is_isomorphic()


class TestLargestCommonSubgraph:
    def test_mcis(self):
        # Example graphs from DOI: 10.1002/spe.588
        graph1 = nx.Graph()
        graph1.add_edges_from([(1, 2), (2, 3), (2, 4), (3, 4), (4, 5)])
        graph1.nodes[1]["color"] = 0

        graph2 = nx.Graph()
        graph2.add_edges_from(
            [(1, 2), (2, 3), (2, 4), (3, 4), (3, 5), (5, 6), (5, 7), (6, 7)]
        )
        graph2.nodes[1]["color"] = 1
        graph2.nodes[6]["color"] = 2
        graph2.nodes[7]["color"] = 2

        ismags = iso.ISMAGS(
            graph1, graph2, node_match=iso.categorical_node_match("color", None)
        )
        assert list(ismags.subgraph_isomorphisms_iter(True)) == []
        assert list(ismags.subgraph_isomorphisms_iter(False)) == []
        found_mcis = _matches_to_sets(ismags.largest_common_subgraph())
        expected = _matches_to_sets(
            [{2: 2, 3: 4, 4: 3, 5: 5}, {2: 4, 3: 2, 4: 3, 5: 5}]
        )
        assert expected == found_mcis

        ismags = iso.ISMAGS(
            graph2, graph1, node_match=iso.categorical_node_match("color", None)
        )
        assert list(ismags.subgraph_isomorphisms_iter(True)) == []
        assert list(ismags.subgraph_isomorphisms_iter(False)) == []
        found_mcis = _matches_to_sets(ismags.largest_common_subgraph())
        # Same answer, but reversed.
        expected = _matches_to_sets(
            [{2: 2, 3: 4, 4: 3, 5: 5}, {4: 2, 2: 3, 3: 4, 5: 5}]
        )
        assert expected == found_mcis

    def test_symmetry_mcis(self):
        graph1 = nx.Graph()
        nx.add_path(graph1, range(4))

        graph2 = nx.Graph()
        nx.add_path(graph2, range(3))
        graph2.add_edge(1, 3)

        # Only the symmetry of graph2 is taken into account here.
        ismags1 = iso.ISMAGS(
            graph1, graph2, node_match=iso.categorical_node_match("color", None)
        )
        assert list(ismags1.subgraph_isomorphisms_iter(True)) == []
        found_mcis = _matches_to_sets(ismags1.largest_common_subgraph())
        expected = _matches_to_sets([{0: 0, 1: 1, 2: 2}, {1: 0, 3: 2, 2: 1}])
        assert expected == found_mcis

        # Only the symmetry of graph1 is taken into account here.
        ismags2 = iso.ISMAGS(
            graph2, graph1, node_match=iso.categorical_node_match("color", None)
        )
        assert list(ismags2.subgraph_isomorphisms_iter(True)) == []
        found_mcis = _matches_to_sets(ismags2.largest_common_subgraph())
        expected = _matches_to_sets(
            [
                {3: 2, 0: 0, 1: 1},
                {2: 0, 0: 2, 1: 1},
                {3: 0, 0: 2, 1: 1},
                {3: 0, 1: 1, 2: 2},
                {0: 0, 1: 1, 2: 2},
                {2: 0, 3: 2, 1: 1},
            ]
        )

        assert expected == found_mcis

        found_mcis1 = _matches_to_sets(ismags1.largest_common_subgraph(False))
        found_mcis2 = ismags2.largest_common_subgraph(False)
        found_mcis2 = [{v: k for k, v in d.items()} for d in found_mcis2]
        found_mcis2 = _matches_to_sets(found_mcis2)

        expected = _matches_to_sets(
            [
                {3: 2, 1: 3, 2: 1},
                {2: 0, 0: 2, 1: 1},
                {1: 2, 3: 3, 2: 1},
                {3: 0, 1: 3, 2: 1},
                {0: 2, 2: 3, 1: 1},
                {3: 0, 1: 2, 2: 1},
                {2: 0, 0: 3, 1: 1},
                {0: 0, 2: 3, 1: 1},
                {1: 0, 3: 3, 2: 1},
                {1: 0, 3: 2, 2: 1},
                {0: 3, 1: 1, 2: 2},
                {0: 0, 1: 1, 2: 2},
            ]
        )
        assert expected == found_mcis1
        assert expected == found_mcis2
