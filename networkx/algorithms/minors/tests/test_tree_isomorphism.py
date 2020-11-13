import networkx as nx
import textwrap
from networkx.utils import create_py_random_state
from networkx.algorithms.string.balanced_isomorphism import (
    available_impls_longest_common_balanced_isomorphism,
)
from networkx.generators.random_graphs import random_ordered_tree
from networkx import isomorphism


def test_all_implementations_are_same():
    """
    Tests several random sequences
    """

    seed = 24658885408229410362279507020239
    rng = create_py_random_state(seed)

    maxsize = 20
    num_trials = 30

    node_affinity = "eq"

    for _ in range(num_trials):
        n1 = rng.randint(1, maxsize)
        n2 = rng.randint(1, maxsize)

        tree1 = random_ordered_tree(n1, seed=rng, directed=True)
        tree2 = random_ordered_tree(n2, seed=rng, directed=True)

        # Note: the returned sequences may be different (maximum embeddings may
        # not be unique), but the values should all be the same.
        affinity_funcs = ["eq", None]
        for node_affinity in affinity_funcs:
            results = {}
            impls = available_impls_longest_common_balanced_isomorphism()
            for impl in impls:
                # FIXME: do we need to rework the return value here?
                subtree1, subtree2, _ = nx.maximum_common_ordered_subtree_isomorphism(
                    tree1, tree2, node_affinity=node_affinity, impl=impl
                )
                _check_subtree_isomorphism_invariants(
                    tree1, tree2, subtree1, subtree2, node_affinity
                )
                results[impl] = len(subtree1.nodes)

            x = max(results.values())
            assert all(v == x for v in results.values())


def check_btree_case():
    tree1 = nx.balanced_tree(3, 2, create_using=nx.OrderedDiGraph)
    tree2 = nx.balanced_tree(2, 2, create_using=nx.OrderedDiGraph)

    nx.set_node_attributes(
        tree1, dict(zip(tree1.nodes, map(str, tree1.nodes))), "label"
    )
    nx.set_node_attributes(
        tree2, dict(zip(tree2.nodes, map(str, tree2.nodes))), "label"
    )
    # tree1.remove_node(6)
    # tree1.remove_node(7)

    node_affinity = "eq"

    item_type = "auto"
    impl = "auto"

    node_affinity = "eq"

    subtree1, subtree2, _ = nx.maximum_common_ordered_subtree_isomorphism(
        tree1, tree2, node_affinity=node_affinity, item_type=item_type, impl=impl
    )
    nx.set_node_attributes(
        subtree1, dict(zip(subtree1.nodes, map(str, subtree1.nodes))), "label"
    )
    nx.set_node_attributes(
        subtree2, dict(zip(subtree2.nodes, map(str, subtree2.nodes))), "label"
    )

    embedding1, embedding2, _ = nx.maximum_common_ordered_subtree_embedding(
        tree1,
        tree2,
        node_affinity=node_affinity,
    )

    def node_match(n1, n2):
        return n1 == n2

    matcher = isomorphism.DiGraphMatcher(tree1, tree2, node_match=node_match)
    print(list(matcher.isomorphisms_iter()))
    print(list(matcher.subgraph_isomorphisms_iter()))
    print(list(matcher.subgraph_monomorphisms_iter()))
    print(matcher.subgraph_is_isomorphic())

    matcher = isomorphism.DiGraphMatcher(tree1, subtree2, node_match=node_match)
    print(list(matcher.isomorphisms_iter()))
    print(list(matcher.subgraph_isomorphisms_iter()))
    print(list(matcher.subgraph_monomorphisms_iter()))
    print(matcher.subgraph_is_isomorphic())

    verbose = 1
    if verbose:
        print("tree1")
        print(nx.forest_str(tree1))
        print("tree2")
        print(nx.forest_str(tree2))

        print("subtree1")
        print(nx.forest_str(subtree1))
        print("subtree2")
        print(nx.forest_str(subtree2))

        print("embedding1")
        print(nx.forest_str(embedding1))
        print("embedding2")
        print(nx.forest_str(embedding2))


def check_dfs_relabel_case():
    tree1 = nx.balanced_tree(2, 4, create_using=nx.OrderedDiGraph)
    tree2 = nx.balanced_tree(3, 4, create_using=nx.OrderedDiGraph)
    # Relabel trees so DFS nodes in the first path match
    mapping1 = dict(zip(nx.dfs_preorder_nodes(tree1), range(len(tree1))))
    mapping2 = dict(zip(nx.dfs_preorder_nodes(tree2), range(len(tree2))))
    tree1 = nx.relabel_nodes(tree1, mapping1)
    tree2 = nx.relabel_nodes(tree2, mapping2)
    print("tree1")
    print(nx.forest_str(tree1))
    print("tree2")
    print(nx.forest_str(tree2))

    subtree1, subtree2, _ = nx.maximum_common_ordered_subtree_isomorphism(tree1, tree2)
    print("subtree1")
    print(nx.forest_str(subtree1))
    print("subtree2")
    print(nx.forest_str(subtree2))
    assert set(subtree1.nodes) == set(range(6))


def check_any_match_case():
    # Allow any node to match any node. The result should be an r2-h2 btree
    tree1 = nx.balanced_tree(2, 3, create_using=nx.OrderedDiGraph)
    tree2 = nx.balanced_tree(3, 2, create_using=nx.OrderedDiGraph)
    print("tree1")
    print(nx.forest_str(tree1))
    print("tree2")
    print(nx.forest_str(tree2))
    subtree1, subtree2, _ = nx.maximum_common_ordered_subtree_isomorphism(
        tree1, tree2, node_affinity=None
    )
    print("subtree1")
    print(nx.forest_str(subtree1))
    print("subtree2")
    print(nx.forest_str(subtree2))
    assert set(subtree1.nodes) == set(range(6))

    expected = nx.balanced_tree(2, 2, create_using=nx.OrderedDiGraph)
    # print(nx.forest_str(expected))
    assert isomorphism.is_isomorphic(subtree1, expected)
    assert isomorphism.is_isomorphic(subtree2, expected)

    matcher = isomorphism.DiGraphMatcher(
        tree1, subtree2, node_match=lambda n1, n2: True
    )
    assert matcher.subgraph_is_isomorphic()

    matcher = isomorphism.DiGraphMatcher(
        tree2, subtree1, node_match=lambda n1, n2: True
    )
    assert matcher.subgraph_is_isomorphic()
    list(matcher.subgraph_isomorphisms_iter())


def check_simple_skip_head_case():
    tree1 = nx.OrderedDiGraph()
    tree1.add_edge(0, 1)
    tree1.add_edge(1, 4)
    tree1.add_edge(1, 5)

    tree2 = nx.OrderedDiGraph()
    tree2.add_edge(0, 1)
    tree2.add_edge(1, 3)
    tree2.add_edge(1, 4)

    item_type = "number"

    subtree1, subtree2, _ = nx.maximum_common_ordered_subtree_isomorphism(
        tree1, tree2, item_type=item_type
    )

    print("tree1")
    print(nx.forest_str(tree1))
    print("tree2")
    print(nx.forest_str(tree2))

    print("subtree1")
    print(nx.forest_str(subtree1))
    print("subtree2")
    print(nx.forest_str(subtree2))


def _check_subtree_isomorphism_invariants(
    tree1, tree2, subtree1, subtree2, node_affinity
):

    # Subtrees should already be isomorphic
    assert isomorphism.is_isomorphic(subtree1, subtree2)

    if len(subtree1) == 0:
        return

    # Maximum isomorphism should be the same between already found subtrees
    alt_subtree1, alt_subtree2, _ = nx.maximum_common_ordered_subtree_isomorphism(
        subtree1, subtree2, node_affinity=node_affinity
    )
    assert set(alt_subtree1.edges) == set(subtree1.edges)
    assert set(alt_subtree2.edges) == set(subtree2.edges)

    embedding1, embedding2, _ = nx.maximum_common_ordered_subtree_embedding(
        tree1, tree2, node_affinity=node_affinity
    )
    assert len(embedding1) >= len(
        subtree1
    ), "embeddings should at least as big as induced-isomorphisms"
    assert len(embedding2) >= len(
        subtree2
    ), "embeddings should at least as big as induced-isomorphisms"

    assert isomorphism.DiGraphMatcher(tree1, subtree1).subgraph_is_isomorphic()
    assert isomorphism.DiGraphMatcher(tree2, subtree2).subgraph_is_isomorphic()

    alt_subtree1, _, _ = nx.maximum_common_ordered_subtree_isomorphism(
        subtree1, tree2, node_affinity=node_affinity
    )
    _, alt_subtree2, _ = nx.maximum_common_ordered_subtree_isomorphism(
        tree1, subtree2, node_affinity=node_affinity
    )
    assert set(alt_subtree1.edges) == set(subtree1.edges)
    assert set(alt_subtree2.edges) == set(subtree2.edges)

    alt_embed1, _, _ = nx.maximum_common_ordered_subtree_embedding(
        subtree1, tree2, node_affinity=node_affinity
    )
    _, alt_embed2, _ = nx.maximum_common_ordered_subtree_embedding(
        tree1, subtree2, node_affinity=node_affinity
    )
    assert set(alt_embed1.edges) == set(subtree1.edges)
    assert set(alt_embed2.edges) == set(subtree2.edges)

    verbose = 0
    if verbose:
        print("tree1")
        print(nx.forest_str(tree1))
        print("tree2")
        print(nx.forest_str(tree2))

        print("subtree1")
        print(nx.forest_str(subtree1))
        print("subtree2")
        print(nx.forest_str(subtree2))


def test_custom_large_case():
    # Create two trees that have a reasonably complex shared structure
    random_ordered_tree = nx.generators.random_graphs.random_ordered_tree
    tree1 = random_ordered_tree(10, seed=3)
    tree2 = random_ordered_tree(10, seed=2)
    tree1.add_edges_from(tree2.edges, weight=1)
    tree1 = nx.minimum_spanning_arborescence(tree1)
    tree2.add_edges_from(tree1.edges, weight=1)
    tree2 = nx.minimum_spanning_arborescence(tree2)

    tree1.remove_edge(4, 7)
    tree1.remove_edge(4, 9)
    tree1.add_edge(4, 10)
    tree1.add_edge(10, 7)
    tree1.add_edge(10, 9)
    tree1.add_edges_from([(9, 11), (11, 12)])
    tree2.add_edges_from([(9, 11), (11, 12)])
    tree2.add_edge(100, 0)
    tree1.add_edge(102, 100)
    tree1.add_edge(100, 101)
    tree1.add_edge(101, 0)
    tree1.add_edge(5, 201)
    tree1.add_edge(5, 202)
    tree1.add_edge(5, 203)
    tree1.add_edge(201, 2000)
    tree1.add_edge(2000, 2001)
    tree1.add_edge(2001, 2002)
    tree1.add_edge(2002, 2003)

    tree2.add_edge(5, 202)
    tree2.add_edge(5, 203)
    tree2.add_edge(5, 201)
    tree2.add_edge(201, 2000)
    tree2.add_edge(2000, 2001)
    tree2.add_edge(2001, 2002)
    tree2.add_edge(2002, 2003)

    print("-----")
    print("tree1")
    print(nx.forest_str(tree1))
    print("tree2")
    print(nx.forest_str(tree2))

    subtree1, subtree2, weight = nx.maximum_common_ordered_subtree_isomorphism(
        tree1, tree2
    )
    subtree1_got = nx.forest_str(subtree1)
    subtree2_got = nx.forest_str(subtree2)
    target = textwrap.dedent(
        """
        ╙── 0
            ├─╼ 3
            │   └─╼ 8
            └─╼ 1
                ├─╼ 6
                └─╼ 5
                    ├─╼ 2
                    │   └─╼ 4
                    └─╼ 201
                        └─╼ 2000
                            └─╼ 2001
                                └─╼ 2002
                                    └─╼ 2003
        """
    ).strip()
    print("-----")
    print("subtree1")
    print(subtree1_got)
    print("subtree2")
    print(subtree2_got)

    assert target == subtree1_got
    assert target == subtree2_got

    # Compare the subtree isomorphism to the subtree embedding
    embedding1, embedding2, _ = nx.maximum_common_ordered_subtree_embedding(
        tree1, tree2
    )
    print("-----")
    print("embedding1")
    print(nx.forest_str(embedding1))
    print("embedding2")
    print(nx.forest_str(embedding2))

    if 0:
        import timerit

        ti = timerit.Timerit(6, bestof=2, verbose=2)
        for timer in ti.reset("isomorphism"):
            with timer:
                nx.maximum_common_ordered_subtree_isomorphism(tree1, tree2)
        for timer in ti.reset("embedding"):
            with timer:
                nx.maximum_common_ordered_subtree_embedding(tree1, tree2)

    assert isomorphism.DiGraphMatcher(tree1, subtree1).subgraph_is_isomorphic()
    assert isomorphism.DiGraphMatcher(tree2, subtree2).subgraph_is_isomorphic()

    if 0:
        list(isomorphism.DiGraphMatcher(tree1, tree2).subgraph_isomorphisms_iter())
        list(isomorphism.DiGraphMatcher(tree1, tree2).subgraph_monomorphisms_iter())

        list(
            isomorphism.DiGraphMatcher(subtree1, subtree2).subgraph_isomorphisms_iter()
        )
        list(isomorphism.DiGraphMatcher(tree1, subtree1).subgraph_isomorphisms_iter())
        list(isomorphism.DiGraphMatcher(tree2, subtree2).subgraph_isomorphisms_iter())
