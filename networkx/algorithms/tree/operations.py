"""Operations on trees."""
from functools import partial
from itertools import accumulate, chain

import networkx as nx

__all__ = ["join", "join_trees"]


def join(rooted_trees, label_attribute=None):
    """A deprecated name for `join_trees`

    Returns a new rooted tree with a root node joined with the roots
    of each of the given rooted trees.

    .. deprecated:: 3.2

       `join` is deprecated in NetworkX v3.2 and will be removed in v3.4.
       It has been renamed join_trees with the same syntax/interface.

    """
    import warnings

    warnings.warn(
        "The function `join` is deprecated and is renamed `join_trees`.\n"
        "The ``join`` function itself will be removed in v3.4",
        DeprecationWarning,
        stacklevel=2,
    )

    return join_trees(rooted_trees, label_attribute=label_attribute)


def join_trees(rooted_trees, label_attribute=None):
    """Returns a new rooted tree made by joining `rooted_trees`

    Constructs a new tree by joining each tree in `rooted_trees`.
    A new root node is added and connected to each of the roots
    of the input trees. While copying the nodes from the trees,
    relabeling to integers occurs and the old name stored as an
    attribute of the new node in the returned graph.

    Parameters
    ----------
    rooted_trees : list
        A list of pairs in which each left element is a NetworkX graph
        object representing a tree and each right element is the root
        node of that tree. The nodes of these trees will be relabeled to
        integers.

    label_attribute : str
        If provided, the old node labels will be stored in the new tree
        under this node attribute. If not provided, the node attribute
        ``'_old'`` will store the original label of the node in the
        rooted trees given in the input.

    Returns
    -------
    NetworkX graph
        The rooted tree whose subtrees are the given rooted trees. The
        new root node is labeled 0. Each non-root node has an attribute,
        as described under the keyword argument ``label_attribute``,
        that indicates the label of the original node in the input tree.

    Notes
    -----
    Trees are stored in NetworkX as NetworkX Graphs. There is no specific
    enforcement of the fact that these are trees. Testing for each tree
    can be done using :func:`networkx.is_tree`.

    Graph, edge, and node attributes are propagated from the given
    rooted trees to the created tree. If there are any overlapping graph
    attributes, those from later trees will overwrite those from earlier
    trees in the tuple of positional arguments.

    Examples
    --------
    Join two full balanced binary trees of height *h* to get a full
    balanced binary tree of depth *h* + 1::

        >>> h = 4
        >>> left = nx.balanced_tree(2, h)
        >>> right = nx.balanced_tree(2, h)
        >>> joined_tree = nx.join([(left, 0), (right, 0)])
        >>> nx.is_isomorphic(joined_tree, nx.balanced_tree(2, h + 1))
        True

    """
    if len(rooted_trees) == 0:
        return nx.empty_graph(1)

    # Unzip the zipped list of (tree, root) pairs.
    trees, roots = zip(*rooted_trees)

    # The join of the trees has the same type as the type of the first
    # tree.
    R = type(trees[0])()

    # Relabel the nodes so that their union is the integers starting at 1.
    if label_attribute is None:
        label_attribute = "_old"
    relabel = partial(
        nx.convert_node_labels_to_integers, label_attribute=label_attribute
    )
    lengths = (len(tree) for tree in trees[:-1])
    first_labels = chain([0], accumulate(lengths))
    trees = [
        relabel(tree, first_label=first_label + 1)
        for tree, first_label in zip(trees, first_labels)
    ]

    # Get the relabeled roots.
    roots = [
        next(v for v, d in tree.nodes(data=True) if d.get(label_attribute) == root)
        for tree, root in zip(trees, roots)
    ]

    # Add all sets of nodes and edges, attributes
    for tree in trees:
        R.update(tree)

    # Finally, join the subtrees at the root. We know 0 is unused by the
    # way we relabeled the subtrees.
    R.add_node(0)
    R.add_edges_from((0, root) for root in roots)

    return R
