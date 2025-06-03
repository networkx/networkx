import networkx as nx

__all__ = [
    "tree_centroid",
]


def _subtree_sizes(T, root):
    """Returns a dict of the subtree sizes, taken considering `root` as the root of the tree `T`.

    Parameters
    ----------
    T : NetworkX graph
       A graph

    root : node label
       A node in T

    Returns
    -------
    s : a dict keyed on node labels to its integer subtree size value

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
    for a, b in zip(stack[-2::-1], stack[-1::-1]):
        sizes[a] += sizes[b]
    return sizes


@nx.utils.not_implemented_for("directed")
@nx._dispatchable
def tree_centroid(T):
    """Returns the centroid of the tree T.

    The centroid is the set of nodes where if any one is removed from
    the tree it would split the tree into a forest of trees of size no
    more than N / 2.

    Parameters
    ----------
    T : NetworkX graph
       A graph

    Returns
    -------
    c : list
       List of nodes in centroid of the tree.  This could be one or two nodes.

    Raises
    ------
    NetworkXError
        If algorithm detects input graph is not a tree.
    NetworkXPointlessConcept
        If T is empty

    Notes
    -----
    This algorithm's time complexity is O(N) where N is the number of nodes in the tree.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> tree_centroid(G)
    [1, 2]

    >>> G = nx.Graph([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (4, 6), (5, 7), (5, 8)])
    >>> tree_centroid(G)
    [0]

    """
    if not nx.is_tree(T):
        raise nx.NotATree("provided graph is not a tree")
    prev, root = None, next(iter(T.nodes))
    sizes = _subtree_sizes(T, root)
    total_size = T.number_of_nodes()

    while (
        max(
            total_size - sizes[root],
            max((sizes[x] for x in T.neighbors(root) if x != prev), default=0),
        )
        > total_size / 2
    ):
        prev, root = root, max((sizes[x], x) for x in T.neighbors(root) if x != prev)[1]

    return [root] + [
        x for x in T.neighbors(root) if x != prev and sizes[x] == total_size / 2
    ]
