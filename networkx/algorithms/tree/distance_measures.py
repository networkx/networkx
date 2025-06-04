import networkx as nx

__all__ = [
    "tree_centroid",
]


def _subtree_sizes(T, root):
    """Return a `dict` of subtree sizes in a tree rooted at a given node.

    Parameters
    ----------
    T : NetworkX graph
       A tree.

    root : node
       A node in `T`.

    Returns
    -------
    s : dict
       Dictionary of subtree sizes keyed on nodes.

    Examples
    --------
    >>> _subtree_sizes(nx.path_graph(4), 0)
    {0: 4, 1: 3, 2: 2, 3: 1}

    >>> _subtree_sizes(nx.path_graph(4), 2)
    {2: 4, 1: 2, 0: 1, 3: 1}
    """
    sizes = {root: 1}
    stack = [root]
    for a, b in nx.dfs_edges(T, root):
        while stack[-1] != a:
            x = stack.pop()
            sizes[stack[-1]] += sizes[x]
        stack.append(b)
        sizes[b] = 1
    for b, a in nx.utils.pairwise(reversed(stack)):
        sizes[a] += sizes[b]
    return sizes


@nx.utils.not_implemented_for("directed")
@nx._dispatchable
def tree_centroid(T):
    """Return the centroid of a tree.

    The centroid is the set of nodes where if any one is removed from
    the tree it would split the tree into a forest of trees of size no
    more than ``N / 2``, where ``N`` is the number of nodes in the
    original tree. This may wind up being two nodes if removal of an
    edge would result in two trees of size exactly ``N / 2``.

    This is different from the concept of the graph center, which is
    the set of nodes that minimize the maximum distance to all other
    nodes.

    Parameters
    ----------
    T : NetworkX graph
       A tree.

    Returns
    -------
    c : list
       List of nodes in centroid of the tree. This could be one or two nodes.

    Raises
    ------
    NotATree
        If the input graph is not a tree.
    NotImplementedException
        If the input graph is directed.
    NetworkXPointlessConcept
        If `T` has no nodes or edges.

    Notes
    -----
    This algorithm's time complexity is ``O(N)`` where ``N`` is the number of nodes in the tree.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> tree_centroid(G)
    [1, 2]

    A good example of where the tree_centroid diverges from the center
    is with a star graph with one long branch. The center doesn't care
    that there are a bunch of length 1 branches, it will wind up being
    near the middle of the long branch.  The centroid, however, puts a
    hard limit on the number of nodes down any given branch from the
    chosen centroid. If the star has enough branches, the center of
    the star is forced to be the centroid.

    >>> G = nx.star_graph(6)
    >>> nx.add_path(G, [6, 7, 8, 9, 10])
    >>> tree_centroid(G)  # nx.center(G) would equal [7] here.
    [0]

    See Also
    --------
    :func:`~networkx.algorithms.distance_measures.center`

    """
    if not nx.is_tree(T):
        raise nx.NotATree("provided graph is not a tree")
    prev, root = None, next(iter(T.nodes))
    sizes = _subtree_sizes(T, root)
    total_size = T.number_of_nodes()

    def _heaviest_child(prev, root):
        return max(
            (x for x in T.neighbors(root) if x != prev), key=sizes.get, default=None
        )

    hc = _heaviest_child(prev, root)
    while max(total_size - sizes[root], sizes.get(hc, 0)) > total_size / 2:
        prev, root = root, hc
        hc = _heaviest_child(prev, root)

    return [root] + [
        x for x in T.neighbors(root) if x != prev and sizes[x] == total_size / 2
    ]
