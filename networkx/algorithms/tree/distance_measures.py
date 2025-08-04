"""
Algorithms for computing distance measures on trees.
"""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = [
    "center",
]


@not_implemented_for("directed")
def center(G):
    """Returns the center of an undirected tree graph.

    The center of a tree consists of nodes that minimize the maximum eccentricity.
    That is, these nodes minimize the maximum distance to all other nodes.
    This implementation currently only works for unweighted edges.

    If the input graph is not a tree, results are not guaranteed to be correct and while
    some non-trees will raise a `nx.NotATree` exception; not all non-trees will be discovered.
    Thus, this function should not be used if caller is unsure whether the input graph
    is a tree. Use ``nx.is_tree(G)`` to check.

    Parameters
    ----------
    G : NetworkX graph
        A tree graph (undirected, acyclic graph).

    Returns
    -------
    center : list
        A list of nodes in the center of the tree. This could be one or two nodes.

    Raises
    ------
    NotATree
        If the algorithm detects input graph is not a tree. There is no guarantee
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

    if (n := len(center_candidates_degree)) not in {1, 2} or n == 2 and not leaves:
        # We detected graph is not a tree. This check does not necessarily cover all cases?
        raise nx.NotATree("input graph is not a tree")

    return list(center_candidates_degree)
