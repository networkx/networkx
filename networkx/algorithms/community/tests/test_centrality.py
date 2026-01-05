"""Unit tests for the :mod:`networkx.algorithms.community.centrality`
module.

"""

from operator import itemgetter

import networkx as nx


def set_of_sets(iterable):
    return set(map(frozenset, iterable))


def validate_communities(result, expected):
    assert set_of_sets(result) == set_of_sets(expected)


def validate_possible_communities(result, *expected):
    assert any(set_of_sets(result) == set_of_sets(p) for p in expected)


class TestGirvanNewman:
    """Unit tests for the
    :func:`networkx.algorithms.community.centrality.girvan_newman`
    function.

    """

    def test_no_edges(self):
        G = nx.empty_graph(3)
        communities = list(nx.community.girvan_newman(G))
        assert len(communities) == 1
        validate_communities(communities[0], [{0}, {1}, {2}])

    def test_undirected(self):
        # Start with the graph .-.-.-.
        G = nx.path_graph(4)
        communities = list(nx.community.girvan_newman(G))
        assert len(communities) == 3
        # After one removal, we get the graph .-. .-.
        validate_communities(communities[0], [{0, 1}, {2, 3}])
        # After the next, we get the graph .-. . ., but there are two
        # symmetric possible versions.
        validate_possible_communities(
            communities[1], [{0}, {1}, {2, 3}], [{0, 1}, {2}, {3}]
        )
        # After the last removal, we always get the empty graph.
        validate_communities(communities[2], [{0}, {1}, {2}, {3}])

    def test_directed(self):
        G = nx.DiGraph(nx.path_graph(4))
        communities = list(nx.community.girvan_newman(G))
        assert len(communities) == 3
        validate_communities(communities[0], [{0, 1}, {2, 3}])
        validate_possible_communities(
            communities[1], [{0}, {1}, {2, 3}], [{0, 1}, {2}, {3}]
        )
        validate_communities(communities[2], [{0}, {1}, {2}, {3}])

    def test_selfloops(self):
        G = nx.path_graph(4)
        G.add_edge(0, 0)
        G.add_edge(2, 2)
        communities = list(nx.community.girvan_newman(G))
        assert len(communities) == 3
        validate_communities(communities[0], [{0, 1}, {2, 3}])
        validate_possible_communities(
            communities[1], [{0}, {1}, {2, 3}], [{0, 1}, {2}, {3}]
        )
        validate_communities(communities[2], [{0}, {1}, {2}, {3}])

    def test_most_valuable_edge(self):
        G = nx.Graph()
        G.add_weighted_edges_from([(0, 1, 3), (1, 2, 2), (2, 3, 1)])
        # Let the most valuable edge be the one with the highest weight.

        def heaviest(G):
            return max(G.edges(data="weight"), key=itemgetter(2))[:2]

        communities = list(nx.community.girvan_newman(G, heaviest))
        assert len(communities) == 3
        validate_communities(communities[0], [{0}, {1, 2, 3}])
        validate_communities(communities[1], [{0}, {1}, {2, 3}])
        validate_communities(communities[2], [{0}, {1}, {2}, {3}])


class TestGirvanNewmanKarateClub:
    """Tests using Zachary's Karate Club - a graph from the original paper."""

    def test_first_split_separates_factions(self):
        """The first split should separate Mr. Hi (node 0) and Officer (node 33)."""
        G = nx.karate_club_graph()
        communities_generator = nx.community.girvan_newman(G)
        first_split = next(communities_generator)

        # Should split into exactly 2 communities
        assert len(first_split) == 2

        # Mr. Hi (0) and Officer (33) should be in different communities
        comm1, comm2 = first_split
        node_0_in_comm1 = 0 in comm1
        node_33_in_comm1 = 33 in comm1

        # They should NOT be in the same community
        assert node_0_in_comm1 != node_33_in_comm1

    def test_final_result_is_singletons(self):
        """After all splits, each node should be in its own community."""
        G = nx.karate_club_graph()
        communities = list(nx.community.girvan_newman(G))

        # Last result should have 34 communities (one per node)
        final_communities = communities[-1]
        assert len(final_communities) == G.number_of_nodes()

        # Each community should have exactly 1 node
        for comm in final_communities:
            assert len(comm) == 1
