from itertools import chain
from itertools import combinations

from nose.tools import assert_equal, assert_in

import networkx as nx
from networkx.algorithms.community import asyn_lpa_communities


class TestAsynLpaCommunities(object):

    def _check_communities(self, G, expected):
        """Checks that the communities computed from the given graph ``G``
        using the :func:`~networkx.asyn_lpa_communities` function match
        the set of nodes given in ``expected``.

        ``expected`` must be a :class:`set` of :class:`frozenset`
        instances, each element of which is a node in the graph.

        """
        communities = asyn_lpa_communities(G)
        result = {frozenset(c) for c in communities}
        assert_equal(result, expected)

    def test_null_graph(self):
        G = nx.null_graph()
        ground_truth = set()
        self._check_communities(G, ground_truth)

    def test_single_node(self):
        G = nx.empty_graph(1)
        ground_truth = {frozenset([0])}
        self._check_communities(G, ground_truth)

    def test_simple_communities(self):
        # This graph is the disjoint union of two triangles.
        G = nx.Graph(['ab', 'ac', 'bc', 'de', 'df', 'fe'])
        ground_truth = {frozenset('abc'), frozenset('def')}
        self._check_communities(G, ground_truth)

    def test_several_communities(self):
        # This graph is the disjoint union of five triangles.
        ground_truth = {frozenset(range(3 * i, 3 * (i + 1))) for i in range(5)}
        edges = chain.from_iterable(combinations(c, 2) for c in ground_truth)
        G = nx.Graph(edges)
        self._check_communities(G, ground_truth)
