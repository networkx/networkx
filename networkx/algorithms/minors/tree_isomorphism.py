from networkx.algorithms.string.balanced_isomorphism import (
    longest_common_balanced_isomorphism,
)
from networkx.algorithms.minors.tree_embedding import tree_to_seq, seq_to_tree


def maximum_common_ordered_subtree_isomorphism(
    tree1, tree2, node_affinity="auto", impl="auto", item_type="auto"
):
    """
    Finds the maximum common subtree-isomorphism between two ordered trees.

    This function computes the maximum-weight common subtrees S1 and S2 between
    two trees T1 and T2. S1 and S2 are isomorphic to subgraphs of T1 and T2
    with maximal size such that S1 and S2 are also isomorphic to each other.

    This function is similar to :func:`maximum_common_ordered_subtree_embedding`
    with the main difference being that returned solution from this function
    will be proper subgraphs (i.e. all edges in the subgraphs will exist in the
    original graph), whereas in the subtree embedding problem the returned
    solutions are allowed to be minors of the input graphs (i.e. edges are
    allowed to be contracted).

    Parameters
    ----------
    tree1, tree2 : nx.OrderedDiGraph
        Trees to find the maximum subtree isomorphism between

    node_affinity : None | str | callable
        Function for to determine if two nodes can be matched. The return is
        interpreted as a weight that is used to break ties. If None then any
        node can match any other node and only the topology is important.
        The default is "eq", which is the same as ``operator.eq``.

    impl : str
        Determines the backend implementation. Defaults to "auto".
        See :func:`networkx.algorithms.string.balanced_sequence.longest_common_balanced_sequence`
        for details. Other valid options are "iter", "recurse", and
        "iter-cython".

    item_type : str
        Determines the backend data structure used to encode the tree as a
        balanced sequence. Defaults to "auto", other valid options are "chr"
        and "number".

    Returns
    -------
    S1, S2, value: Tuple[nx.OrderedDiGraph, nx.OrderedDiGraph, int]
        The maximum value common subtree isomorphism for each tree with respect
        to the chosen ``node_affinity`` function. The topology of both graphs
        will always be the same, the only difference is that the node labels in
        the first and second embeddings will correspond to ``tree1`` and
        ``tree2`` respectively. When ``node_affinity='eq'`` then embeddings
        should be identical. The last return value is the "size" of the
        solution with respect to ``node_affinity``.

    See Also
    --------
    `maximum_common_ordered_subtree_embedding`
    """
    import networkx as nx

    # Note: checks that inputs are forests are handled by tree_to_seq
    if not isinstance(tree1, nx.OrderedDiGraph):
        raise nx.NetworkXNotImplemented("only implemented for directed ordered trees")
    if not isinstance(tree1, nx.OrderedDiGraph):
        raise nx.NetworkXNotImplemented("only implemented for directed ordered trees")

    if tree1.number_of_nodes() == 0 or tree2.number_of_nodes() == 0:
        raise nx.NetworkXPointlessConcept

    if item_type == "label":
        # If we do allow label, I think the algorithm will work, but the
        # returned tree embeddings will only be embedding wrt to the label
        # structure.
        raise AssertionError(
            "allowing sequences to be specified by the labels breaks assumptions"
        )

    # Convert the trees to balanced sequences.
    # Each sequence will contain each token at most once, this is an important
    # assumption in subsequent steps.
    seq1, open_to_close, node_to_open = tree_to_seq(
        tree1,
        open_to_close=None,
        node_to_open=None,
        item_type=item_type,
        container_type="auto",
    )
    seq2, open_to_close, node_to_open = tree_to_seq(
        tree2, open_to_close, node_to_open, item_type=item_type, container_type="auto"
    )
    open_to_node = {tok: node for node, tok in node_to_open.items()}

    # Solve the longest common balanced sequence problem
    best, value = longest_common_balanced_isomorphism(
        seq1,
        seq2,
        open_to_close,
        open_to_node=open_to_node,
        node_affinity=node_affinity,
        impl=impl,
    )
    subseq1, subseq2 = best

    # Convert the subsequence back into a tree.
    subtree1 = seq_to_tree(subseq1, open_to_close, open_to_node)
    subtree2 = seq_to_tree(subseq2, open_to_close, open_to_node)
    return subtree1, subtree2, value
