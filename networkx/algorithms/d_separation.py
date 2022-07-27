"""
Algorithm for testing d-separation in DAGs.

*d-separation* is a test for conditional independence in probability
distributions that can be factorized using DAGs.  It is a purely
graphical test that uses the underlying graph and makes no reference
to the actual distribution parameters.  See [1]_ for a formal
definition.

The implementation is based on the conceptually simple linear time
algorithm presented in [2]_.  Refer to [3]_, [4]_ for a couple of
alternative algorithms.


Examples
--------

>>>
>>> # HMM graph with five states and observation nodes
... g = nx.DiGraph()
>>> g.add_edges_from(
...     [
...         ("S1", "S2"),
...         ("S2", "S3"),
...         ("S3", "S4"),
...         ("S4", "S5"),
...         ("S1", "O1"),
...         ("S2", "O2"),
...         ("S3", "O3"),
...         ("S4", "O4"),
...         ("S5", "O5"),
...     ]
... )
>>>
>>> # states/obs before 'S3' are d-separated from states/obs after 'S3'
... nx.d_separated(g, {"S1", "S2", "O1", "O2"}, {"S4", "S5", "O4", "O5"}, {"S3"})
True


References
----------

.. [1] Pearl, J.  (2009).  Causality.  Cambridge: Cambridge University Press.

.. [2] Darwiche, A.  (2009).  Modeling and reasoning with Bayesian networks. 
   Cambridge: Cambridge University Press.

.. [3] Shachter, R.  D.  (1998).
   Bayes-ball: rational pastime (for determining irrelevance and requisite
   information in belief networks and influence diagrams).
   In , Proceedings of the Fourteenth Conference on Uncertainty in Artificial
   Intelligence (pp.  480–487).
   San Francisco, CA, USA: Morgan Kaufmann Publishers Inc.

.. [4] Koller, D., & Friedman, N. (2009).
   Probabilistic graphical models: principles and techniques. The MIT Press.

"""

from collections import deque

import networkx as nx
from networkx.utils import UnionFind, not_implemented_for

__all__ = ["d_separated", "compute_minimal_separating_set", "is_separating_set_minimal"]


@not_implemented_for("undirected")
def d_separated(G, x, y, z):
    """
    Return whether node sets ``x`` and ``y`` are d-separated by ``z``.

    Parameters
    ----------
    G : graph
        A NetworkX DAG.

    x : set
        First set of nodes in ``G``.

    y : set
        Second set of nodes in ``G``.

    z : set
        Set of conditioning nodes in ``G``. Can be empty set.

    Returns
    -------
    b : bool
        A boolean that is true if ``x`` is d-separated from ``y`` given ``z`` in ``G``.

    Raises
    ------
    NetworkXError
        The *d-separation* test is commonly used with directed
        graphical models which are acyclic.  Accordingly, the algorithm
        raises a :exc:`NetworkXError` if the input graph is not a DAG.

    NodeNotFound
        If any of the input nodes are not found in the graph,
        a :exc:`NodeNotFound` exception is raised.

    """

    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("graph should be directed acyclic")

    union_xyz = x.union(y).union(z)

    if any(n not in G.nodes for n in union_xyz):
        raise nx.NodeNotFound("one or more specified nodes not found in the graph")

    G_copy = G.copy()

    # transform the graph by removing leaves that are not in x | y | z
    # until no more leaves can be removed.
    leaves = deque([n for n in G_copy.nodes if G_copy.out_degree[n] == 0])
    while len(leaves) > 0:
        leaf = leaves.popleft()
        if leaf not in union_xyz:
            for p in G_copy.predecessors(leaf):
                if G_copy.out_degree[p] == 1:
                    leaves.append(p)
            G_copy.remove_node(leaf)

    # transform the graph by removing outgoing edges from the
    # conditioning set.
    edges_to_remove = list(G_copy.out_edges(z))
    G_copy.remove_edges_from(edges_to_remove)

    # use disjoint-set data structure to check if any node in `x`
    # occurs in the same weakly connected component as a node in `y`.
    disjoint_set = UnionFind(G_copy.nodes())
    for component in nx.weakly_connected_components(G_copy):
        disjoint_set.union(*component)
    disjoint_set.union(*x)
    disjoint_set.union(*y)

    if x and y and disjoint_set[next(iter(x))] == disjoint_set[next(iter(y))]:
        return False
    else:
        return True


@not_implemented_for("undirected")
def compute_minimal_separating_set(G, x, y):
    """Compute a minimal separating set between X and Y.

    Uses the algorithm presented in [1]_.

    Parameters
    ----------
    G : graph
        A networkx DAG.
    x : node
        Node X in the graph, G.
    y : node
        Node Y in the graph, G.

    Raises
    ------
    NetworkXError
        The *d-separation* test is commonly used with directed
        graphical models which are acyclic.  Accordingly, the algorithm
        raises a :exc:`NetworkXError` if the input graph is not a DAG.

    NodeNotFound
        If any of the input nodes are not found in the graph,
        a :exc:`NodeNotFound` exception is raised.

    References
    ----------
    .. [1] Tian, J., & Paz, A. (1998). Finding Minimal D-separators.
    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("graph should be directed acyclic")

    union_xy = x.union(y)

    if any(n not in G.nodes for n in union_xy):
        raise nx.NodeNotFound("one or more specified nodes not found in the graph")

    # first construct the set of ancestors of X and Y
    x_anc = set(G.ancestors(x))
    y_anc = set(G.ancestors(y))
    D_anc_xy = x_anc.union(y_anc)
    D_anc_xy = D_anc_xy.union((x, y))

    # second, construct the moralization of the subgraph of Anc(X,Y)
    moral_G = nx.moralize_graph(G.subgraph(D_anc_xy))

    # find a separating set Z' in moral_G
    Z_prime = set(G.parents(x)).union(set(G.parents(y)))

    # perform BFS on the graph from 'x' to mark
    Z_dprime = _bfs_with_marks(moral_G, x, Z_prime)
    Z = _bfs_with_marks(moral_G, y, Z_dprime)
    return Z


@not_implemented_for("undirected")
def is_separating_set_minimal(G, x, y, z):
    """Determine if a separating set is minimal.

    Uses the algorithm 2 presented in :footcite:`Tian1998FindingMD`.

    Parameters
    ----------
    G : nx.DiGraph
        The graph.
    x : node
        X node.
    y : node
        Y node.
    z : Set
        The separating set to check is minimal.

    Returns
    -------
    bool
        Whether or not the `z` separating set is minimal.

    References
    ----------
    .. footbibliography::
    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("graph should be directed acyclic")

    union_xyz = x.union(y).union(z)

    if any(n not in G.nodes for n in union_xyz):
        raise nx.NodeNotFound("one or more specified nodes not found in the graph")

    x_anc = G.ancestors(x)
    y_anc = G.ancestors(y)
    xy_anc = x_anc.union(y_anc)

    # if Z contains any node which is not in ancestors of X or Y
    # then it is definitely not minimal
    if any(node not in xy_anc for node in z):
        return False

    D_anc_xy = x_anc.union(y_anc)
    D_anc_xy = D_anc_xy.union((x, y))

    # second, construct the moralization of the subgraph
    moral_G = nx.moralize_graph(G.subgraph(D_anc_xy))

    # start BFS from X
    marks = _bfs_with_marks(moral_G, x, z)

    # if not all the Z is marked, then the set is not minimal
    if any(node not in marks for node in z):
        return False

    # similarly, start BFS from Y and check the marks
    marks = _bfs_with_marks(moral_G, y, z)
    # if not all the Z is marked, then the set is not minimal
    if any(node not in marks for node in z):
        return False

    return True


def _bfs_with_marks(G, start_node, check_set):
    """Breadth-first-search with markings.

    Performs BFS starting from ``start_node`` and whenever a node
    inside ``check_set`` is met, it is "marked". Once a node is marked,
    BFS does not continue along that path. The resulting marked nodes
    are returned.

    Parameters
    ----------
    G : nx.Graph
        An undirected graph.
    start_node : node
        The start of the BFS.
    check_set : set
        The set of nodes to check against.

    Returns
    -------
    marked : set
        A set of nodes that were marked.
    """
    visited = dict()
    marked = dict()
    queue = []

    visited[start_node] = None
    queue.append(start_node)
    while queue:
        m = queue.pop(0)

        for neighbr in G.neighbors(m):
            if neighbr not in visited:
                # memoize where we visited so far
                visited[neighbr] = None

                # mark the node in Z' and do not continue
                # along that path
                if neighbr in check_set:
                    marked[neighbr] = None
                else:
                    queue.append(neighbr)
    return set(marked.keys())
