import random
from itertools import chain, combinations, product

import pytest

import networkx as nx

tree_all_pairs_lca = nx.tree_all_pairs_lowest_common_ancestor
all_pairs_lca = nx.all_pairs_lowest_common_ancestor


def get_pair(dictionary, n1, n2):
    if (n1, n2) in dictionary:
        return dictionary[n1, n2]
    else:
        return dictionary[n2, n1]


def is_lca(G, u, v, lca):
    """Returns True if lca is a lowest common ancestor of u and v.

    A node is a lowest common ancestor of two nodes if:
    1. It is an ancestor of both nodes
    2. None of its descendants is a common ancestor of both nodes

    Parameters
    ----------
    G : NetworkX directed graph
    u, v : nodes in the graph G
    lca : the node to verify as a possible lowest common ancestor

    Returns
    -------
    bool
        True if lca is a lowest common ancestor of u and v, False otherwise.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> nx.add_path(G, [0, 1, 3])
    >>> nx.add_path(G, [0, 2, 3])
    >>> is_lca(G, 1, 2, 0)  # 0 is a common ancestor of 1 and 2
    True
    >>> is_lca(G, 1, 2, 3)  # 3 is not an ancestor of 1 or 2
    False
    >>> is_lca(G, 3, 3, 3)  # A node is its own LCA
    True
    >>> is_lca(G, 1, 3, 0)  # 0 is an ancestor of both 1 and 3
    False
    >>> is_lca(G, 1, 3, 1)  # 1 is an ancestor of both 1 and 3
    True
    """
    # Check if lca is an ancestor of both u and v
    u_ancestors = nx.ancestors(G, u).union({u})
    v_ancestors = nx.ancestors(G, v).union({v})

    # lca must be an ancestor of both u and v
    if lca not in u_ancestors or lca not in v_ancestors:
        return False

    # None of lca's descendants can be ancestors of both u and v
    if any(
        successor in u_ancestors and successor in v_ancestors
        for successor in G.successors(lca)
    ):
        return False

    return True


def test_is_lca():
    G = nx.DiGraph()
    nx.add_path(G, (0, 1, 3))
    nx.add_path(G, (0, 2, 3))

    # Case 1: 1 and 2's lowest common ancestor is 0
    assert is_lca(G, 1, 2, 0)
    # Case 2: 1/2 is not the lowest common ancestor of 1 and 2
    assert not is_lca(G, 1, 2, 1)
    assert not is_lca(G, 1, 2, 2)
    # Case 3: A non-ancestor node (3) will return False for 1 and 2
    assert not is_lca(G, 1, 2, 3)
    # Case 4: The same node is its own ancestor
    assert is_lca(G, 3, 3, 3)


class TestTreeLCA:
    @classmethod
    def setup_class(cls):
        cls.DG = nx.DiGraph()
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
        cls.DG.add_edges_from(edges)
        cls.ans = dict(tree_all_pairs_lca(cls.DG, 0))
        gold = {(n, n): n for n in cls.DG}
        gold.update({(0, i): 0 for i in range(1, 7)})
        gold.update(
            {
                (1, 2): 0,
                (1, 3): 1,
                (1, 4): 1,
                (1, 5): 0,
                (1, 6): 0,
                (2, 3): 0,
                (2, 4): 0,
                (2, 5): 2,
                (2, 6): 2,
                (3, 4): 1,
                (3, 5): 0,
                (3, 6): 0,
                (4, 5): 0,
                (4, 6): 0,
                (5, 6): 2,
            }
        )

        cls.gold = gold

    @staticmethod
    def assert_has_same_pairs(d1, d2):
        for a, b in ((min(pair), max(pair)) for pair in chain(d1, d2)):
            assert get_pair(d1, a, b) == get_pair(d2, a, b)

    def test_tree_all_pairs_lca_default_root(self):
        assert dict(tree_all_pairs_lca(self.DG)) == self.ans

    def test_tree_all_pairs_lca_return_subset(self):
        test_pairs = [(0, 1), (0, 1), (1, 0)]
        ans = dict(tree_all_pairs_lca(self.DG, 0, test_pairs))
        assert (0, 1) in ans and (1, 0) in ans
        assert len(ans) == 2

    def test_tree_all_pairs_lca(self):
        all_pairs = chain(combinations(self.DG, 2), ((node, node) for node in self.DG))

        ans = dict(tree_all_pairs_lca(self.DG, 0, all_pairs))
        self.assert_has_same_pairs(ans, self.ans)

    def test_tree_all_pairs_gold_example(self):
        ans = dict(tree_all_pairs_lca(self.DG))
        self.assert_has_same_pairs(self.gold, ans)

    def test_tree_all_pairs_lca_invalid_input(self):
        empty_digraph = tree_all_pairs_lca(nx.DiGraph())
        pytest.raises(nx.NetworkXPointlessConcept, list, empty_digraph)

        bad_pairs_digraph = tree_all_pairs_lca(self.DG, pairs=[(-1, -2)])
        pytest.raises(nx.NodeNotFound, list, bad_pairs_digraph)

    def test_tree_all_pairs_lca_subtrees(self):
        ans = dict(tree_all_pairs_lca(self.DG, 1))
        gold = {
            pair: lca
            for (pair, lca) in self.gold.items()
            if all(n in (1, 3, 4) for n in pair)
        }
        self.assert_has_same_pairs(gold, ans)

    def test_tree_all_pairs_lca_disconnected_nodes(self):
        G = nx.DiGraph()
        G.add_node(1)
        assert {(1, 1): 1} == dict(tree_all_pairs_lca(G))

        G.add_node(0)
        assert {(1, 1): 1} == dict(tree_all_pairs_lca(G, 1))
        assert {(0, 0): 0} == dict(tree_all_pairs_lca(G, 0))

        pytest.raises(nx.NetworkXError, list, tree_all_pairs_lca(G))

    def test_tree_all_pairs_lca_error_if_input_not_tree(self):
        # Cycle
        G = nx.DiGraph([(1, 2), (2, 1)])
        pytest.raises(nx.NetworkXError, list, tree_all_pairs_lca(G))
        # DAG
        G = nx.DiGraph([(0, 2), (1, 2)])
        pytest.raises(nx.NetworkXError, list, tree_all_pairs_lca(G))

    def test_tree_all_pairs_lca_generator(self):
        pairs = iter([(0, 1), (0, 1), (1, 0)])
        some_pairs = dict(tree_all_pairs_lca(self.DG, 0, pairs))
        assert (0, 1) in some_pairs and (1, 0) in some_pairs
        assert len(some_pairs) == 2

    def test_tree_all_pairs_lca_nonexisting_pairs_exception(self):
        lca = tree_all_pairs_lca(self.DG, 0, [(-1, -1)])
        pytest.raises(nx.NodeNotFound, list, lca)
        # check if node is None
        lca = tree_all_pairs_lca(self.DG, None, [(-1, -1)])
        pytest.raises(nx.NodeNotFound, list, lca)

    def test_tree_all_pairs_lca_routine_bails_on_DAGs(self):
        G = nx.DiGraph([(3, 4), (5, 4)])
        pytest.raises(nx.NetworkXError, list, tree_all_pairs_lca(G))

    def test_tree_all_pairs_lca_not_implemented(self):
        NNI = nx.NetworkXNotImplemented
        G = nx.Graph([(0, 1)])
        with pytest.raises(NNI):
            next(tree_all_pairs_lca(G))
        with pytest.raises(NNI):
            next(all_pairs_lca(G))
        pytest.raises(NNI, nx.lowest_common_ancestor, G, 0, 1)
        G = nx.MultiGraph([(0, 1)])
        with pytest.raises(NNI):
            next(tree_all_pairs_lca(G))
        with pytest.raises(NNI):
            next(all_pairs_lca(G))
        pytest.raises(NNI, nx.lowest_common_ancestor, G, 0, 1)

    def test_tree_all_pairs_lca_trees_without_LCAs(self):
        G = nx.DiGraph()
        G.add_node(3)
        ans = list(tree_all_pairs_lca(G))
        assert ans == [((3, 3), 3)]


class TestMultiTreeLCA(TestTreeLCA):
    @classmethod
    def setup_class(cls):
        cls.DG = nx.MultiDiGraph()
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
        cls.DG.add_edges_from(edges)
        cls.ans = dict(tree_all_pairs_lca(cls.DG, 0))
        # add multiedges
        cls.DG.add_edges_from(edges)

        gold = {(n, n): n for n in cls.DG}
        gold.update({(0, i): 0 for i in range(1, 7)})
        gold.update(
            {
                (1, 2): 0,
                (1, 3): 1,
                (1, 4): 1,
                (1, 5): 0,
                (1, 6): 0,
                (2, 3): 0,
                (2, 4): 0,
                (2, 5): 2,
                (2, 6): 2,
                (3, 4): 1,
                (3, 5): 0,
                (3, 6): 0,
                (4, 5): 0,
                (4, 6): 0,
                (5, 6): 2,
            }
        )

        cls.gold = gold


class TestDAGLCA:
    @classmethod
    def setup_class(cls):
        cls.DG = nx.DiGraph()
        nx.add_path(cls.DG, (0, 1, 2, 3))
        nx.add_path(cls.DG, (0, 4, 3))
        nx.add_path(cls.DG, (0, 5, 6, 8, 3))
        nx.add_path(cls.DG, (5, 7, 8))
        cls.DG.add_edge(6, 2)
        cls.DG.add_edge(7, 2)

        cls.gold = {
            (1, 1): 1,
            (1, 2): 1,
            (1, 3): 1,
            (1, 4): 0,
            (1, 5): 0,
            (1, 6): 0,
            (1, 7): 0,
            (1, 8): 0,
            (2, 2): 2,
            (2, 3): 2,
            (2, 4): 0,
            (2, 5): 5,
            (2, 6): 6,
            (2, 7): 7,
            (2, 8): 7,
            (3, 3): 3,
            (3, 4): 4,
            (3, 5): 5,
            (3, 6): 6,
            (3, 7): 7,
            (3, 8): 8,
            (4, 4): 4,
            (4, 5): 0,
            (4, 6): 0,
            (4, 7): 0,
            (4, 8): 0,
            (5, 5): 5,
            (5, 6): 5,
            (5, 7): 5,
            (5, 8): 5,
            (6, 6): 6,
            (6, 7): 5,
            (6, 8): 6,
            (7, 7): 7,
            (7, 8): 7,
            (8, 8): 8,
        }
        cls.gold.update(((0, n), 0) for n in cls.DG)

    def test_all_pairs_lca_gold_example(self):
        result = dict(all_pairs_lca(self.DG))
        for (u, v), lca in result.items():
            assert is_lca(self.DG, u, v, lca)

    def test_all_pairs_lca_all_pairs_given(self):
        all_pairs = list(product(self.DG.nodes(), self.DG.nodes()))
        result = dict(all_pairs_lca(self.DG, pairs=all_pairs))
        for (u, v), lca in result.items():
            assert is_lca(self.DG, u, v, lca)

    def test_all_pairs_lca_generator(self):
        all_pairs = product(self.DG.nodes(), self.DG.nodes())
        result = dict(all_pairs_lca(self.DG, pairs=all_pairs))
        for (u, v), lca in result.items():
            assert is_lca(self.DG, u, v, lca)

    def test_all_pairs_lca_input_graph_with_two_roots(self):
        G = self.DG.copy()
        G.add_edge(9, 10)
        G.add_edge(9, 4)
        gold = self.gold.copy()
        gold[9, 9] = 9
        gold[9, 10] = 9
        gold[9, 4] = 9
        gold[9, 3] = 9
        gold[10, 4] = 9
        gold[10, 3] = 9
        gold[10, 10] = 10

        testing = dict(all_pairs_lca(G))

        for (u, v), lca in testing.items():
            assert is_lca(G, u, v, lca)

    def test_all_pairs_lca_nonexisting_pairs_exception(self):
        pytest.raises(nx.NodeNotFound, all_pairs_lca, self.DG, [(-1, -1)])

    def test_all_pairs_lca_pairs_without_lca(self):
        G = self.DG.copy()
        G.add_node(-1)
        gen = all_pairs_lca(G, [(-1, -1), (-1, 0)])
        assert dict(gen) == {(-1, -1): -1}

    def test_all_pairs_lca_null_graph(self):
        pytest.raises(nx.NetworkXPointlessConcept, all_pairs_lca, nx.DiGraph())

    def test_all_pairs_lca_non_dags(self):
        pytest.raises(nx.NetworkXError, all_pairs_lca, nx.DiGraph([(3, 4), (4, 3)]))

    def test_all_pairs_lca_nonempty_graph_without_lca(self):
        G = nx.DiGraph()
        G.add_node(3)
        ans = list(all_pairs_lca(G))
        assert ans == [((3, 3), 3)]

    def test_all_pairs_lca_bug_gh4942(self):
        G = nx.DiGraph([(0, 2), (1, 2), (2, 3)])
        ans = list(all_pairs_lca(G))
        assert len(ans) == 9

    def test_all_pairs_lca_default_kwarg(self):
        G = nx.DiGraph([(0, 1), (2, 1)])
        sentinel = object()
        assert nx.lowest_common_ancestor(G, 0, 2, default=sentinel) is sentinel

    def test_all_pairs_lca_identity(self):
        G = nx.DiGraph()
        G.add_node(3)
        assert nx.lowest_common_ancestor(G, 3, 3) == 3

    def test_all_pairs_lca_issue_4574(self):
        G = nx.DiGraph()
        G.add_nodes_from(range(17))
        G.add_edges_from(
            [
                (2, 0),
                (1, 2),
                (3, 2),
                (5, 2),
                (8, 2),
                (11, 2),
                (4, 5),
                (6, 5),
                (7, 8),
                (10, 8),
                (13, 11),
                (14, 11),
                (15, 11),
                (9, 10),
                (12, 13),
                (16, 15),
            ]
        )

        assert nx.lowest_common_ancestor(G, 7, 9) is None

    def test_all_pairs_lca_one_pair_gh4942(self):
        G = nx.DiGraph()
        # Note: order edge addition is critical to the test
        G.add_edge(0, 1)
        G.add_edge(2, 0)
        G.add_edge(2, 3)
        G.add_edge(4, 0)
        G.add_edge(5, 2)

        lca = nx.lowest_common_ancestor(G, 1, 3)
        assert lca == 2
        assert is_lca(G, 1, 3, lca)

    def test_all_pairs_lca_key_parameter(self):
        # Test that key parameter selects among multiple LCAs for all_pairs_lowest_common_ancestor
        G = nx.DiGraph()
        edges = [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 4)]
        G.add_edges_from(edges)
        # nodes 3 and 4 have LCAs {1, 2}
        # default yields smallest id
        result_default = dict(all_pairs_lca(G, pairs=[(3, 4)]))
        assert result_default[(3, 4)] == 1
        # with key chooses largest id
        result_key = dict(all_pairs_lca(G, pairs=[(3, 4)], key=lambda x: -x))
        assert result_key[(3, 4)] == 2


class TestMultiDiGraph_DAGLCA(TestDAGLCA):
    @classmethod
    def setup_class(cls):
        cls.DG = nx.MultiDiGraph()
        nx.add_path(cls.DG, (0, 1, 2, 3))
        # add multiedges
        nx.add_path(cls.DG, (0, 1, 2, 3))
        nx.add_path(cls.DG, (0, 4, 3))
        nx.add_path(cls.DG, (0, 5, 6, 8, 3))
        nx.add_path(cls.DG, (5, 7, 8))
        cls.DG.add_edge(6, 2)
        cls.DG.add_edge(7, 2)

        cls.gold = {
            (1, 1): 1,
            (1, 2): 1,
            (1, 3): 1,
            (1, 4): 0,
            (1, 5): 0,
            (1, 6): 0,
            (1, 7): 0,
            (1, 8): 0,
            (2, 2): 2,
            (2, 3): 2,
            (2, 4): 0,
            (2, 5): 5,
            (2, 6): 6,
            (2, 7): 7,
            (2, 8): 7,
            (3, 3): 3,
            (3, 4): 4,
            (3, 5): 5,
            (3, 6): 6,
            (3, 7): 7,
            (3, 8): 8,
            (4, 4): 4,
            (4, 5): 0,
            (4, 6): 0,
            (4, 7): 0,
            (4, 8): 0,
            (5, 5): 5,
            (5, 6): 5,
            (5, 7): 5,
            (5, 8): 5,
            (6, 6): 6,
            (6, 7): 5,
            (6, 8): 6,
            (7, 7): 7,
            (7, 8): 7,
            (8, 8): 8,
        }
        cls.gold.update(((0, n), 0) for n in cls.DG)


def test_all_pairs_lca_self_ancestors():
    """Self-ancestors should always be the node itself, i.e. lca of (0, 0) is 0.
    See gh-4458."""
    # DAG for test - note order of node/edge addition is relevant
    G = nx.DiGraph()
    G.add_nodes_from(range(5))
    G.add_edges_from([(1, 0), (2, 0), (3, 2), (4, 1), (4, 3)])

    ap_lca = nx.all_pairs_lowest_common_ancestor
    assert all(u == v == a for (u, v), a in ap_lca(G) if u == v)
    MG = nx.MultiDiGraph(G)
    assert all(u == v == a for (u, v), a in ap_lca(MG) if u == v)
    MG.add_edges_from([(1, 0), (2, 0)])
    assert all(u == v == a for (u, v), a in ap_lca(MG) if u == v)


def test_lca_on_null_graph():
    G = nx.null_graph(create_using=nx.DiGraph)
    with pytest.raises(
        nx.NetworkXPointlessConcept, match="LCA meaningless on null graphs"
    ):
        nx.lowest_common_ancestor(G, 0, 0)


def test_lca_on_cycle_graph():
    G = nx.cycle_graph(6, create_using=nx.DiGraph)
    with pytest.raises(
        nx.NetworkXError, match="LCA only defined on directed acyclic graphs"
    ):
        nx.lowest_common_ancestor(G, 0, 3)


def test_lca_multiple_valid_solutions():
    G = nx.DiGraph()
    G.add_nodes_from(range(4))
    G.add_edges_from([(2, 0), (3, 0), (2, 1), (3, 1)])
    lca = nx.lowest_common_ancestor(G, 0, 1)
    assert lca in {2, 3}
    assert is_lca(G, 0, 1, lca)


def test_lca_dont_rely_on_single_successor():
    # Nodes 0 and 1 have nodes 2 and 3 as immediate ancestors,
    # and node 2 also has node 3 as an immediate ancestor.
    G = nx.DiGraph()
    G.add_nodes_from(range(4))
    G.add_edges_from([(2, 0), (2, 1), (3, 1), (3, 0), (3, 2)])
    lca = nx.lowest_common_ancestor(G, 0, 1)
    assert lca == 2
    assert is_lca(G, 0, 1, lca)


def test_lowest_common_ancestor_key_parameter():
    # Test behavior of key parameter and arbitrary selection
    G = nx.DiGraph()
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 4)]
    G.add_edges_from(edges)
    # nodes 3 and 4 have LCAs {1, 2}
    # without key, returns arbitrary LCA
    lca = nx.lowest_common_ancestor(G, 3, 4)
    assert lca in {1, 2}
    # with key, returns specific LCA
    assert nx.lowest_common_ancestor(G, 3, 4, key=lambda x: x) == 1
    assert nx.lowest_common_ancestor(G, 3, 4, key=lambda x: -x) == 2


def test_all_pairs_lca_key_parameter():
    # Test behavior of key parameter and arbitrary selection
    G = nx.DiGraph()
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 4)]
    G.add_edges_from(edges)
    # nodes 3 and 4 have LCAs {1, 2}
    # without key, returns arbitrary LCA
    result = dict(all_pairs_lca(G, pairs=[(3, 4)]))
    assert result[(3, 4)] in {1, 2}
    # with key chooses specific LCA
    result_min = dict(all_pairs_lca(G, pairs=[(3, 4)], key=lambda x: x))
    assert result_min[(3, 4)] == 1
    result_max = dict(all_pairs_lca(G, pairs=[(3, 4)], key=lambda x: -x))
    assert result_max[(3, 4)] == 2


class TestAllPairsAllLowestCommonAncestors:
    """Test the all_pairs_all_lowest_common_ancestors function."""

    def test_empty_graph(self):
        # Test that empty graph raises PointlessConcept
        with pytest.raises(nx.NetworkXPointlessConcept):
            nx.all_pairs_all_lowest_common_ancestors(nx.DiGraph())

    def test_nonexistent_pairs(self):
        # Test that non-existent node pairs raise NodeNotFound
        G = nx.DiGraph()
        G.add_nodes_from([1, 2])
        with pytest.raises(nx.NodeNotFound):
            list(nx.all_pairs_all_lowest_common_ancestors(G, pairs=[(1, 3)]))

    def test_self_pairing(self):
        # Test that self-pairing returns the node itself
        G = nx.DiGraph()
        G.add_node(3)
        result = dict(nx.all_pairs_all_lowest_common_ancestors(G))
        assert result == {(3, 3): [3]}
        result2 = dict(nx.all_pairs_all_lowest_common_ancestors(G, pairs=[(3, 3)]))
        assert result2 == {(3, 3): [3]}

    def test_non_dag_raises(self):
        # Test that non-DAG graph raises NetworkXError
        G = nx.DiGraph([(1, 2), (2, 1)])
        with pytest.raises(nx.NetworkXError):
            list(nx.all_pairs_all_lowest_common_ancestors(G))

    def test_multiple_lcas(self):
        # Test graph with multiple lowest common ancestors
        G = nx.DiGraph()
        edges = [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 4)]
        G.add_edges_from(edges)
        result = dict(nx.all_pairs_all_lowest_common_ancestors(G, pairs=[(3, 4)]))
        lcas = result.get((3, 4), result.get((4, 3)))
        assert sorted(lcas) == [1, 2]
        for lca in lcas:
            assert is_lca(G, 3, 4, lca)


@pytest.mark.parametrize("seed", range(5))
def test_random_dag_all_pairs_all_lcas(seed):
    # Test random DAGs for correctness of LCAs
    rng = random.Random(seed)
    n = 20
    nodes = list(range(n))
    edges = [(u, v) for u in nodes for v in nodes if u < v and rng.random() < 0.2]
    G = nx.DiGraph(edges)
    assert nx.is_directed_acyclic_graph(G)
    result = dict(nx.all_pairs_all_lowest_common_ancestors(G))
    for (u, v), lcas in result.items():
        lcas = set(lcas)
        for node in G.nodes():
            if node in lcas:
                assert is_lca(G, u, v, node)
            else:
                assert not is_lca(G, u, v, node)


def test_all_lowest_common_ancestors_no_lca():
    G = nx.DiGraph()
    G.add_nodes_from([1, 2])
    assert nx.all_lowest_common_ancestors(G, 1, 2) == []


def test_all_lowest_common_ancestors_simple():
    G = nx.DiGraph()
    nx.add_path(G, (0, 1, 2, 3))
    nx.add_path(G, (0, 4, 3))
    assert nx.all_lowest_common_ancestors(G, 2, 4) == [0]


def test_all_lowest_common_ancestors_multiple():
    G = nx.DiGraph()
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 4)]
    G.add_edges_from(edges)
    lcas = nx.all_lowest_common_ancestors(G, 3, 4)
    assert sorted(lcas) == [1, 2]
    for lca in lcas:
        assert is_lca(G, 3, 4, lca)


def test_all_lowest_common_ancestors_node_not_found():
    G = nx.DiGraph()
    G.add_nodes_from([1, 2])
    with pytest.raises(nx.NodeNotFound):
        nx.all_lowest_common_ancestors(G, 1, 3)


def test_all_lowest_common_ancestors_empty_graph():
    G = nx.DiGraph()
    with pytest.raises(nx.NetworkXPointlessConcept):
        nx.all_lowest_common_ancestors(G, 0, 0)


def test_all_lowest_common_ancestors_non_dag():
    G = nx.DiGraph([(1, 2), (2, 1)])
    with pytest.raises(nx.NetworkXError):
        nx.all_lowest_common_ancestors(G, 1, 2)
