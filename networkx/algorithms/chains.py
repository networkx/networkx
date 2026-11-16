"""Functions for finding chains in a graph."""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["chain_decomposition"]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable
def chain_decomposition(G, root=None):
    """Returns the chain decomposition of a graph.

    The *chain decomposition* of a graph with respect a depth-first
    search tree is a set of cycles or paths derived from the set of
    fundamental cycles of the tree in the following manner. Consider
    each fundamental cycle with respect to the given tree, represented
    as a list of edges beginning with the nontree edge oriented away
    from the root of the tree. For each fundamental cycle, if it
    overlaps with any previous fundamental cycle, just take the initial
    non-overlapping segment, which is a path instead of a cycle. Each
    cycle or path is called a *chain*. For more information, see [1]_.

    Parameters
    ----------
    G : undirected graph

    root : node (optional)
       A node in the graph `G`. If specified, only the chain
       decomposition for the connected component containing this node
       will be returned. This node indicates the root of the depth-first
       search tree.

    Yields
    ------
    chain : list
       A list of edges representing a chain. There is no guarantee on
       the orientation of the edges in each chain (for example, if a
       chain includes the edge joining nodes 1 and 2, the chain may
       include either (1, 2) or (2, 1)).

    Raises
    ------
    NodeNotFound
       If `root` is not in the graph `G`.

    Examples
    --------
    >>> G = nx.Graph([(0, 1), (1, 4), (3, 4), (3, 5), (4, 5)])
    >>> list(nx.chain_decomposition(G))
    [[(4, 5), (5, 3), (3, 4)]]

    Notes
    -----
    The worst-case running time of this implementation is linear in the
    number of nodes and number of edges [1]_.

    References
    ----------
    .. [1] Jens M. Schmidt (2013). "A simple test on 2-vertex-
       and 2-edge-connectivity." *Information Processing Letters*,
       113, 241–244. Elsevier. <https://doi.org/10.1016/j.ipl.2013.01.016>

    """

    # Check if the root is in the graph G. If not, raise NodeNotFound
    if root is not None and root not in G:
        raise nx.NodeNotFound(f"Root node {root} is not in graph")

    # Depth-first search from `root`, or from each connected component
    # if `root` is None. `parent` maps each node to its parent in the DFS
    # tree (None for a root) and doubles as the set of nodes seen so far,
    # `nontree` maps each node to the nodes at the far end of the nontree
    # edges directed away from the root, and `nodes` lists the nodes in
    # DFS preorder.
    parent, nontree, nodes = {}, {}, []
    for start in [root] if root is not None else G:
        if start in parent:
            continue
        parent[start] = None
        nontree[start] = {}
        nodes.append(start)
        stack = [(start, G.neighbors(start))]
        while stack:
            node, nbrs = stack[-1]
            for nbr in nbrs:
                if nbr in parent:
                    # Each nontree edge is found from both ends; keep the
                    # first, oriented from the ancestor to the descendant.
                    if nbr != parent[node] and nbr not in nontree[node]:
                        nontree[nbr][node] = None
                else:
                    parent[nbr] = node
                    nontree[nbr] = {}
                    nodes.append(nbr)
                    stack.append((nbr, G.neighbors(nbr)))
                    break
            else:
                stack.pop()

    # Visit the nodes again in DFS order. For each node, and for each
    # nontree edge leaving that node, compute the fundamental cycle for
    # that nontree edge starting with that edge. If the fundamental
    # cycle overlaps with any visited nodes, just take the prefix of the
    # cycle up to the point of visited nodes.
    #
    # We repeat this process for each connected component (implicitly,
    # since `nodes` already has a list of the nodes grouped by connected
    # component).
    visited = set()
    for u in nodes:
        visited.add(u)
        # For each nontree edge going out of node u...
        for v in nontree[u]:
            # Create the cycle or cycle prefix starting with the
            # nontree edge.
            chain = [(u, v)]
            while v not in visited:
                visited.add(v)
                chain.append((v, v := parent[v]))
            yield chain
