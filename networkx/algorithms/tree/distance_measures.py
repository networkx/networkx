import networkx as nx

__all__ = [
    "tree_centroid",
]


def _subtree_sizes(G, root):
    """Return a `dict` of the size of each subtree, for every subtree
    of a tree rooted at a given node.

    For every node in the given tree, consider the new tree that would
    be created by detaching it from its parent node (if any). The
    number of nodes in the resulting tree rooted at that node is then
    assigned as the value for that node in the return dictionary.

    Parameters
    ----------
    G : NetworkX graph
       A tree.

    root : node
       A node in `G`.

    Returns
    -------
    s : dict
       Dictionary of number of nodes in every subtree of this tree,
       keyed on the root node for each subtree.

    Examples
    --------
    >>> _subtree_sizes(nx.path_graph(4), 0)
    {0: 4, 1: 3, 2: 2, 3: 1}

    >>> _subtree_sizes(nx.path_graph(4), 2)
    {2: 4, 1: 2, 0: 1, 3: 1}

    """
    sizes = {root: 1}
    stack = [root]
    for parent, child in nx.dfs_edges(G, root):
        while stack[-1] != parent:
            descendant = stack.pop()
            sizes[stack[-1]] += sizes[descendant]
        stack.append(child)
        sizes[child] = 1
    for child, parent in nx.utils.pairwise(reversed(stack)):
        sizes[parent] += sizes[child]
    return sizes


@nx.utils.not_implemented_for("directed")
@nx._dispatchable
def tree_centroid(G):
    """Return the centroid of an unweighted tree.

    The centroid of a tree is the set of nodes such that removing any
    one of them would split the tree into a forest of subtrees, each
    with at most ``N / 2`` nodes, where ``N`` is the number of nodes
    in the original tree. This set may contain two nodes if removing
    an edge between them results in two trees of size exactly ``N /
    2``.

    Parameters
    ----------
    G : NetworkX graph
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
        If `G` has no nodes or edges.

    Notes
    -----
    This algorithm's time complexity is ``O(N)`` where ``N`` is the
    number of nodes in the tree.

    In unweighted trees the centroid coincides with the barycenter,
    the node or nodes that minimize the sum of distances to all other
    nodes. However, this concept is different from that of the graph
    center, which is the set of nodes minimizing the maximum distance
    to all other nodes.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> nx.tree_centroid(G)
    [1, 2]

    A star-shaped tree with one long branch illustrates the difference
    between the centroid and the center. The center lies near the
    middle of the long branch, minimizing maximum distance. The
    centroid, however, limits the size of any resulting subtree to at
    most half the total nodes, forcing it to remain near the hub when
    enough short branches are present.

    >>> G = nx.star_graph(6)
    >>> nx.add_path(G, [6, 7, 8, 9, 10])
    >>> nx.tree_centroid(G), nx.center(G)
    ([0], [7])

    See Also
    --------
    :func:`~networkx.algorithms.distance_measures.barycenter`
    :func:`~networkx.algorithms.distance_measures.center`

    """
    if not nx.is_tree(G):
        raise nx.NotATree("provided graph is not a tree")
    prev, root = None, nx.utils.arbitrary_element(G)
    sizes = _subtree_sizes(G, root)
    total_size = G.number_of_nodes()

    def _heaviest_child(prev, root):
        return max(
            (x for x in G.neighbors(root) if x != prev), key=sizes.get, default=None
        )

    hc = _heaviest_child(prev, root)
    while max(total_size - sizes[root], sizes.get(hc, 0)) > total_size / 2:
        prev, root = root, hc
        hc = _heaviest_child(prev, root)

    return [root] + [
        x for x in G.neighbors(root) if x != prev and sizes[x] == total_size / 2
    ]
