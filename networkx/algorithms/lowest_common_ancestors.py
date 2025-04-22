"""Algorithms for finding the lowest common ancestor of trees and DAGs."""

from collections import defaultdict
from collections.abc import Mapping, Set
from itertools import combinations_with_replacement

import networkx as nx
from networkx.utils import UnionFind, arbitrary_element, not_implemented_for

__all__ = [
    "is_lowest_common_ancestor",
    "all_pairs_all_lowest_common_ancestors",
    "all_pairs_lowest_common_ancestor",
    "all_lowest_common_ancestors",
    "lowest_common_ancestor",
    "tree_all_pairs_lowest_common_ancestor",
]


@not_implemented_for("undirected")
@nx._dispatchable
def is_lowest_common_ancestor(G, u, v, x):
    """Return True if x is a lowest common ancestor of u and v.

    A node is a lowest common ancestor of two nodes if:

    1. It is an ancestor of both nodes
    2. None of its descendants is a common ancestor of both nodes

    Parameters
    ----------
    G : NetworkX directed graph
    u, v : nodes in the graph G
    x : the node to verify as a possible lowest common ancestor

    Returns
    -------
    bool
        True if x is a lowest common ancestor of u and v, False otherwise.

    Raises
    ------
    NetworkXError
        If G is not a DAG (Directed Acyclic Graph).

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> nx.add_path(G, [0, 1, 3])
    >>> nx.add_path(G, [0, 2, 3])
    >>> nx.is_lowest_common_ancestor(G, 1, 2, 0)  # 0 is a common ancestor of 1 and 2
    True
    >>> nx.is_lowest_common_ancestor(G, 1, 2, 3)  # 3 is not an ancestor of 1 or 2
    False
    >>> nx.is_lowest_common_ancestor(G, 3, 3, 3)  # A node is its own LCA
    True
    >>> nx.is_lowest_common_ancestor(G, 1, 3, 0)  # 0 is an ancestor of both 1 and 3
    False
    >>> nx.is_lowest_common_ancestor(G, 1, 3, 1)  # 1 is an ancestor of both 1 and 3
    True
    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("LCA only defined on directed acyclic graphs.")

    # Check if x is an ancestor of both u and v
    u_ancestors = nx.ancestors(G, u).union({u})
    v_ancestors = nx.ancestors(G, v).union({v})

    # x must be an ancestor of both u and v
    if x not in u_ancestors or x not in v_ancestors:
        return False

    # None of x's descendants can be ancestors of both u and v
    if any(
        successor in u_ancestors and successor in v_ancestors
        for successor in G.successors(x)
    ):
        return False

    return True


@not_implemented_for("undirected")
@nx._dispatchable
def all_pairs_all_lowest_common_ancestors(G, pairs=None):
    """Return lists of lowest common ancestors of all pairs or the provided pairs.

    The LCA (Lowest Common Ancestor) of a pair of nodes is a node that is an ancestor
    of both nodes and has no descendants that are also ancestors of both nodes.
    Nodes may have multiple LCAs in a DAG (Directed Acyclic Graph).

    Parameters
    ----------
    G : NetworkX directed graph

    pairs : iterable of pairs of nodes, optional (default: all pairs)
        The pairs of nodes of interest.
        If None, will find the LCAs of all pairs of nodes.

    Yields
    ------
    ((node1, node2), [lca1, lca2, ...]) : 2-tuple
        Where [lca1, lca2, ...] are the least common ancestors of node1 and node2.
        Note that for the default case, the order of the node pair is not considered,
        e.g. you will not get both ``(a, b)`` and ``(b, a)``

    Raises
    ------
    NetworkXPointlessConcept
        If `G` is null.
    NetworkXError
        If `G` is not a DAG.
    NodeNotFound
        If any node in the provided pairs is not in `G`.

    Examples
    --------
    The default behavior is to yield the lowest common ancestor for all
    possible combinations of nodes in `G`, including self-pairings:

    >>> G = nx.DiGraph([(0, 1), (0, 3), (1, 2)])
    >>> dict(nx.all_pairs_all_lowest_common_ancestors(G))
    {(0, 0): [0], (0, 1): [0], (0, 3): [0], (0, 2): [0], (1, 1): [1], (1, 3): [0], (1, 2): [1], (3, 3): [3], (3, 2): [0], (2, 2): [2]}

    The pairs argument can be used to limit the output to only the
    specified node pairings:

    >>> dict(nx.all_pairs_all_lowest_common_ancestors(G, pairs=[(1, 2), (2, 3)]))
    {(1, 2): [1], (2, 3): [0]}

    If a pair has multiple lowest common ancestors, all are returned:

    >>> G = nx.DiGraph([(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 4)])
    >>> dict(nx.all_pairs_all_lowest_common_ancestors(G, pairs=[(3, 4)]))
    {(3, 4): [1, 2]}

    If a pair has no common ancestors, an empty list is returned:

    >>> G = nx.DiGraph([(0, 1), (2, 3)])
    >>> dict(nx.all_pairs_all_lowest_common_ancestors(G, pairs=[(1, 3)]))
    {(1, 3): []}

    Notes
    -----
    Only defined on non-null directed acyclic graphs.

    See Also
    --------
    all_pairs_lowest_common_ancestor
    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("LCA only defined on directed acyclic graphs.")
    if len(G) == 0:
        raise nx.NetworkXPointlessConcept("LCA meaningless on null graphs.")

    if pairs is None:
        pairs = combinations_with_replacement(G, 2)
    else:
        # Convert iterator to iterable, if necessary. Trim duplicates.
        pairs = dict.fromkeys(pairs)
        # Verify that each of the nodes in the provided pairs is in G
        nodeset = set(G)
        for pair in pairs:
            if set(pair) - nodeset:
                raise nx.NodeNotFound(
                    f"Node(s) {set(pair) - nodeset} from pair {pair} not in G."
                )

    # Once input validation is done, construct the generator
    def generate_lcas_from_pairs(G, pairs):
        ancestor_cache = {}

        for v, w in pairs:
            if v not in ancestor_cache:
                ancestor_cache[v] = nx.ancestors(G, v)
                ancestor_cache[v].add(v)
            if w not in ancestor_cache:
                ancestor_cache[w] = nx.ancestors(G, w)
                ancestor_cache[w].add(w)

            common_ancestors = ancestor_cache[v] & ancestor_cache[w]
            lowest_common_ancestors = []
            for common_ancestor in common_ancestors:
                if all(
                    successor not in common_ancestors
                    for successor in G.successors(common_ancestor)
                ):
                    lowest_common_ancestors.append(common_ancestor)
            yield ((v, w), lowest_common_ancestors)

    return generate_lcas_from_pairs(G, pairs)


@not_implemented_for("undirected")
@nx._dispatchable
def all_pairs_lowest_common_ancestor(G, pairs=None, key=None):
    """Return the lowest common ancestor of all pairs or the provided pairs.

    The LCA (Lowest Common Ancestor) of a pair of nodes is a node that is an ancestor
    of both nodes and has no descendants that are also ancestors of both nodes.
    Nodes may have multiple LCAs in a DAG (Directed Acyclic Graph).

    If there are multiple LCAs and key is provided, returns the LCA that has the
    minimal value according to the key function. If key is None, returns an
    arbitrary LCA.

    If you want to get all LCAs, use
    :func:`all_pairs_all_lowest_common_ancestors`.

    Parameters
    ----------
    G : NetworkX directed graph

    pairs : iterable of pairs of nodes, optional (default: all pairs)
        The pairs of nodes of interest.
        If None, will find the LCA of all pairs of nodes.

    key : callable, optional
        Function to choose among multiple LCAs; the returned LCA is the minimal
        element in the set of LCAs according to this key. If None, an arbitrary
        LCA is returned.

    Yields
    ------
    ((node1, node2), lca) : 2-tuple
        lca is the lowest common ancestor of node1 and node2. Pairs with no
        common ancestors are omitted. For the default case, ordering of pairs
        is not considered (i.e. yields only one of (a, b) and (b, a)).
        If there are multiple LCAs, the minimal one according to the key
        function is returned.

    Raises
    ------
    NetworkXPointlessConcept
        If `G` is null.
    NetworkXError
        If `G` is not a DAG.
    NodeNotFound
        If any node in the provided pairs is not in `G`.

    Examples
    --------
    The default behavior is to yield the lowest common ancestor for all
    possible combinations of nodes in `G`, including self-pairings:

    >>> G = nx.DiGraph([(0, 1), (0, 3), (1, 2)])
    >>> dict(nx.all_pairs_lowest_common_ancestor(G))
    {(0, 0): 0, (0, 1): 0, (0, 3): 0, (0, 2): 0, (1, 1): 1, (1, 3): 0, (1, 2): 1, (3, 3): 3, (3, 2): 0, (2, 2): 2}

    The pairs argument can be used to limit the output to only the
    specified node pairings:

    >>> dict(nx.all_pairs_lowest_common_ancestor(G, pairs=[(1, 2), (2, 3)]))
    {(1, 2): 1, (2, 3): 0}

    Notes
    -----
    Only defined on non-null directed acyclic graphs.

    See Also
    --------
    all_pairs_all_lowest_common_ancestors
    """
    if key is None:
        select_lca = nx.utils.arbitrary_element
    else:

        def select_lca(lca):
            return min(lca, key=key)

    all_pairs_all_lca = all_pairs_all_lowest_common_ancestors(G, pairs)

    def generate_lca():
        for (u, v), lca in all_pairs_all_lca:
            if len(lca) > 0:
                yield ((u, v), select_lca(lca))

    return generate_lca()


@not_implemented_for("undirected")
@nx._dispatchable
def all_lowest_common_ancestors(G, node1, node2):
    """Compute all lowest common ancestors for the given pair of nodes.

    The LCA (Lowest Common Ancestor) of a pair of nodes is a node that is an ancestor
    of both nodes and has no descendants that are also ancestors of both nodes.
    Nodes may have multiple LCAs in a DAG (Directed Acyclic Graph).

    Parameters
    ----------
    G : NetworkX directed graph

    node1, node2 : nodes in the graph

    Returns
    -------
    list
        A list containing all lowest common ancestors of node1 and node2.
        Returns an empty list if they have no common ancestors.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> nx.add_path(G, (0, 1, 2, 3))
    >>> nx.add_path(G, (0, 4, 3))
    >>> nx.all_lowest_common_ancestors(G, 2, 4)
    [0]

    >>> G = nx.DiGraph([(0, 1), (0, 2), (1, 3), (2, 3), (1, 4), (2, 4)])
    >>> nx.all_lowest_common_ancestors(G, 3, 4)
    [1, 2]

    See Also
    --------
    lowest_common_ancestor, all_pairs_all_lowest_common_ancestors
    """
    ans = list(all_pairs_all_lowest_common_ancestors(G, pairs=[(node1, node2)]))
    assert len(ans) == 1
    assert len(ans[0]) == 2

    return ans[0][1]


@not_implemented_for("undirected")
@nx._dispatchable
def lowest_common_ancestor(G, node1, node2, default=None, key=None):
    """Compute the lowest common ancestor of the given pair of nodes.

    The LCA (Lowest Common Ancestor) of a pair of nodes is a node that is an ancestor
    of both nodes and has no descendants that are also ancestors of both nodes.
    Nodes may have multiple LCAs in a DAG (Directed Acyclic Graph).

    If there are multiple LCAs and key is provided, returns the LCA that has the
    minimal value according to the key function. If key is None, returns an
    arbitrary LCA.

    If you want to get all LCAs, use
    :func:`all_lowest_common_ancestors`.

    Parameters
    ----------
    G : NetworkX directed graph

    node1, node2 : nodes in the graph.

    default : object, optional
        Returned if no common ancestor between `node1` and `node2`.

    key : callable, optional
        Function to choose among multiple LCAs; if multiple LCAs exist, the one
        with the minimal key value is returned. If None, an arbitrary LCA is returned.

    Returns
    -------
    The lowest common ancestor of node1 and node2,
    or default if they have no common ancestors.
    If there are multiple LCAs, the minimal one according to the key
    function is returned.

    Examples
    --------
    >>> G = nx.DiGraph()
    >>> nx.add_path(G, (0, 1, 2, 3))
    >>> nx.add_path(G, (0, 4, 3))
    >>> nx.lowest_common_ancestor(G, 2, 4)
    0

    See Also
    --------
    all_lowest_common_ancestors, all_pairs_lowest_common_ancestor
    """

    ans = list(all_pairs_lowest_common_ancestor(G, pairs=[(node1, node2)], key=key))
    if ans:
        assert len(ans) == 1
        return ans[0][1]
    return default


@not_implemented_for("undirected")
@nx._dispatchable
def tree_all_pairs_lowest_common_ancestor(G, root=None, pairs=None):
    r"""Yield the lowest common ancestor for sets of pairs in a tree.

    Parameters
    ----------
    G : NetworkX directed graph (must be a tree)

    root : node, optional (default: None)
        The root of the subtree to operate on.
        If None, assume the entire graph has exactly one source and use that.

    pairs : iterable or iterator of pairs of nodes, optional (default: None)
        The pairs of interest. If None, Defaults to all pairs of nodes
        under `root` that have a lowest common ancestor.

    Returns
    -------
    lcas : generator of tuples `((u, v), lca)` where `u` and `v` are nodes
        in `pairs` and `lca` is their lowest common ancestor.

    Examples
    --------
    >>> import pprint
    >>> G = nx.DiGraph([(1, 3), (2, 4), (1, 2)])
    >>> pprint.pprint(dict(nx.tree_all_pairs_lowest_common_ancestor(G)))
    {(1, 1): 1,
     (2, 1): 1,
     (2, 2): 2,
     (3, 1): 1,
     (3, 2): 1,
     (3, 3): 3,
     (3, 4): 1,
     (4, 1): 1,
     (4, 2): 2,
     (4, 4): 4}

    We can also use `pairs` argument to specify the pairs of nodes for which we
    want to compute lowest common ancestors. Here is an example:

    >>> dict(nx.tree_all_pairs_lowest_common_ancestor(G, pairs=[(1, 4), (2, 3)]))
    {(2, 3): 1, (1, 4): 1}

    Notes
    -----
    Only defined on non-null trees represented with directed edges from
    parents to children. Uses Tarjan's off-line lowest-common-ancestors
    algorithm. Runs in time $O(4 \times (V + E + P))$ time, where 4 is the largest
    value of the inverse Ackermann function likely to ever come up in actual
    use, and $P$ is the number of pairs requested (or $V^2$ if all are needed).

    Tarjan, R. E. (1979), "Applications of path compression on balanced trees",
    Journal of the ACM 26 (4): 690-715, doi:10.1145/322154.322161.

    See Also
    --------
    all_pairs_lowest_common_ancestor: similar routine for general DAGs
    lowest_common_ancestor: just a single pair for general DAGs
    """
    if len(G) == 0:
        raise nx.NetworkXPointlessConcept("LCA meaningless on null graphs.")

    # Index pairs of interest for efficient lookup from either side.
    if pairs is not None:
        pair_dict = defaultdict(set)
        # See note on all_pairs_lowest_common_ancestor.
        if not isinstance(pairs, Mapping | Set):
            pairs = set(pairs)
        for u, v in pairs:
            for n in (u, v):
                if n not in G:
                    msg = f"The node {str(n)} is not in the digraph."
                    raise nx.NodeNotFound(msg)
            pair_dict[u].add(v)
            pair_dict[v].add(u)

    # If root is not specified, find the exactly one node with in degree 0 and
    # use it. Raise an error if none are found, or more than one is. Also check
    # for any nodes with in degree larger than 1, which would imply G is not a
    # tree.
    if root is None:
        for n, deg in G.in_degree:
            if deg == 0:
                if root is not None:
                    msg = "No root specified and tree has multiple sources."
                    raise nx.NetworkXError(msg)
                root = n
            # checking deg>1 is not sufficient for MultiDiGraphs
            elif deg > 1 and len(G.pred[n]) > 1:
                msg = "Tree LCA only defined on trees; use DAG routine."
                raise nx.NetworkXError(msg)
    if root is None:
        raise nx.NetworkXError("Graph contains a cycle.")

    # Iterative implementation of Tarjan's offline lca algorithm
    # as described in CLRS on page 521 (2nd edition)/page 584 (3rd edition)
    uf = UnionFind()
    ancestors = {}
    for node in G:
        ancestors[node] = uf[node]

    colors = defaultdict(bool)
    for node in nx.dfs_postorder_nodes(G, root):
        colors[node] = True
        for v in pair_dict[node] if pairs is not None else G:
            if colors[v]:
                # If the user requested both directions of a pair, give it.
                # Otherwise, just give one.
                if pairs is not None and (node, v) in pairs:
                    yield (node, v), ancestors[uf[v]]
                if pairs is None or (v, node) in pairs:
                    yield (v, node), ancestors[uf[v]]
        if node != root:
            parent = arbitrary_element(G.pred[node])
            uf.union(parent, node)
            ancestors[uf[parent]] = parent
