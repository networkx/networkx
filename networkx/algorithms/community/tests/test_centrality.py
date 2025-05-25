"""Unit tests for the :mod:`networkx.algorithms.community.centrality`
module.

"""

import itertools
from operator import itemgetter

import networkx as nx


def set_of_sets(iterable):
    return set(map(frozenset, iterable))


def validate_communities(result, expected):
    assert set_of_sets(result) == set_of_sets(expected)


def validate_possible_communities(result, *expected):
    assert any(set_of_sets(result) == set_of_sets(p) for p in expected)


def compare_all_depth_communities(com1, com2):
    assert len(com1) == len(com2)

    depth = len(com1)
    for d in range(depth):
        assert set_of_sets(com1[d]) == set_of_sets(com2[d])


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

    def test_diff_approach_same_result(self):
        """
        Test whether different computing approaches yield identical result
        under the traditional betweenness-centrality based edge selection setting
        """
        G = nx.complete_graph(25)

        def most_valuable_edge(G, weight=None):
            betweenness = nx.edge_betweenness_centrality(
                G, normalized=False, weight=weight
            )
            return max(
                betweenness,
                key=lambda edge: (round(betweenness[edge], 8), max(edge), min(edge)),
            )

        def most_valuable_edge_metric(G, weight=None):
            betweenness = nx.edge_betweenness_centrality(
                G, normalized=False, weight=weight
            )
            edge = max(
                betweenness,
                key=lambda edge: (round(betweenness[edge], 8), max(edge), min(edge)),
            )
            metric = betweenness[edge]
            return edge, metric

        fast_communities = list(nx.community.girvan_newman(G))
        old_communities = list(
            nx.community.girvan_newman(G, most_valuable_edge=most_valuable_edge)
        )
        compo_communities = list(
            nx.community.girvan_newman(
                G, most_valuable_edge_metric=most_valuable_edge_metric
            )
        )

        compare_all_depth_communities(fast_communities, old_communities)
        compare_all_depth_communities(fast_communities, compo_communities)

    def test_benchmark_graphs(self):
        """
        Test the implementation on benchmark datasets
        used in the [original paper](https://arxiv.org/abs/cond-mat/0112110)
        introducing the Girvan Newman algorithm.

        The results of the implementation are expected to
        match that of the original paper.

        The datasets include:
          - [Zachary Karate Club](http://konect.cc/networks/ucidata-zachary/) (Unweighted version)
        """

        graphs = {"ZKC": nx.karate_club_graph()}
        ground_truth = {
            "ZKC": [
                (
                    {0, 1, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17, 19, 21},
                    {
                        2,
                        8,
                        9,
                        14,
                        15,
                        18,
                        20,
                        22,
                        23,
                        24,
                        25,
                        26,
                        27,
                        28,
                        29,
                        30,
                        31,
                        32,
                        33,
                    },
                ),
                (
                    {0, 1, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17, 19, 21},
                    {
                        2,
                        8,
                        14,
                        15,
                        18,
                        20,
                        22,
                        23,
                        24,
                        25,
                        26,
                        27,
                        28,
                        29,
                        30,
                        31,
                        32,
                        33,
                    },
                    {9},
                ),
                (
                    {0, 1, 3, 7, 11, 12, 13, 17, 19, 21},
                    {
                        2,
                        8,
                        14,
                        15,
                        18,
                        20,
                        22,
                        23,
                        24,
                        25,
                        26,
                        27,
                        28,
                        29,
                        30,
                        31,
                        32,
                        33,
                    },
                    {4, 5, 6, 10, 16},
                    {9},
                ),
                (
                    {0, 1, 3, 7, 11, 12, 13, 17, 19, 21},
                    {2, 24, 25, 27, 28, 31},
                    {4, 5, 6, 10, 16},
                    {8, 14, 15, 18, 20, 22, 23, 26, 29, 30, 32, 33},
                    {9},
                ),
                (
                    {0, 1, 3, 7, 12, 13, 17, 19, 21},
                    {2, 24, 25, 27, 28, 31},
                    {4, 5, 6, 10, 16},
                    {8, 14, 15, 18, 20, 22, 23, 26, 29, 30, 32, 33},
                    {9},
                    {11},
                ),
                (
                    {0, 1, 3, 7, 12, 13, 17, 19, 21},
                    {2, 24, 25, 27, 28, 31},
                    {4, 5, 6, 10, 16},
                    {8, 14, 15, 18, 20, 22, 23, 29, 30, 32, 33},
                    {9},
                    {11},
                    {26},
                ),
                (
                    {0, 1, 3, 7, 13, 17, 19, 21},
                    {2, 24, 25, 27, 28, 31},
                    {4, 5, 6, 10, 16},
                    {8, 14, 15, 18, 20, 22, 23, 29, 30, 32, 33},
                    {9},
                    {11},
                    {12},
                    {26},
                ),
                (
                    {0, 1, 3, 7, 13, 17, 19, 21},
                    {2, 24, 25, 27, 28, 31},
                    {4, 5, 6, 10, 16},
                    {8, 15, 18, 20, 22, 23, 29, 30, 32, 33},
                    {9},
                    {11},
                    {12},
                    {14},
                    {26},
                ),
                (
                    {0, 1, 3, 7, 13, 17, 19, 21},
                    {2, 24, 25, 27, 28, 31},
                    {4, 5, 6, 10, 16},
                    {8, 18, 20, 22, 23, 29, 30, 32, 33},
                    {9},
                    {11},
                    {12},
                    {14},
                    {15},
                    {26},
                ),
            ]
        }

        for g_name, G in graphs.items():
            max_depth_to_compare = len(ground_truth[g_name])
            comp = nx.community.girvan_newman(G)
            compare_all_depth_communities(
                list(itertools.islice(comp, max_depth_to_compare)), ground_truth[g_name]
            )
