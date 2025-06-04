"""
Algorithms for computing distance measures on trees.
"""
import networkx as nx

__all__ = [
    "center",
    "centroid",
]


@nx.utils.not_implemented_for("directed")
def center(G):
    """Returns the center of an undirected tree graph.

    The center of a tree consists of nodes that minimize the maximum eccentricity.
    That is, these nodes minimize the maximum distance to all other nodes.
    This implementation currently only works for unweighted edges.

    If the input graph is not a tree, results are not guaranteed to be correct and while
    some non-trees will raise an ``nx.NotATree`` exception, not all non-trees will be discovered.
    Thus, this function should not be used if caller is unsure whether the input graph
    is a tree. Use ``nx.is_tree(G)`` to check.

    Parameters
    ----------
    G : NetworkX graph
        A tree graph (undirected, acyclic graph).

    Returns
    -------
    center : list
        A list of nodes forming the center of the tree. This can be one or two nodes.

    Raises
    ------
    NetworkXNotImplemented
        If the input graph is directed.

    NotATree
        If the algorithm detects the input graph is not a tree. There is no guarantee
        this error will always raise if a non-tree is passed.

    Notes
    -----
    This algorithm iteratively removes leaves (nodes with degree 1) from the tree until
    there are only 1 or 2 nodes left. The remaining nodes form the center of the tree.

    This algorithm's time complexity is ``O(N)`` where ``N`` is the number of nodes in the tree.

    Examples
    --------
    >>> G = nx.Graph([(1, 2), (1, 3), (2, 4), (2, 5)])
    >>> nx.tree.center(G)
    [1, 2]

    >>> G = nx.path_graph(5)
    >>> nx.tree.center(G)
    [2]
    """
    center_candidates_degree = dict(G.degree)
    leaves = {node for node, degree in center_candidates_degree.items() if degree == 1}

    # It's better to fail than an infinite loop, so check leaves to ensure progress.
    while len(center_candidates_degree) > 2 and leaves:
        new_leaves = set()
        for leaf in leaves:
            del center_candidates_degree[leaf]
            for neighbor in G.neighbors(leaf):
                if neighbor not in center_candidates_degree:
                    continue
                center_candidates_degree[neighbor] -= 1
                if (cddn := center_candidates_degree[neighbor]) == 1:
                    new_leaves.add(neighbor)
                elif cddn == 0 and len(center_candidates_degree) != 1:
                    raise nx.NotATree("input graph is not a tree")
        leaves = new_leaves

    n = len(center_candidates_degree)
    # check disconnected or cyclic
    if (n == 2 and not leaves) or n not in {1, 2}:
        # We have detected graph is not a tree. This check does not cover all cases.
        # For example, `nx.Graph([(0, 0)])` will not raise an error.
        raise nx.NotATree("input graph is not a tree")

    return list(center_candidates_degree)


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
def centroid(T):
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
    >>> nx.tree.centroid(G)
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
    >>> nx.tree.centroid(G), nx.tree.center(G)
    ([0], [7])

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
