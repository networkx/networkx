"""
Algorithm for testing d-separation in DAGs.

*d-separation* is a test for conditional independence in probability
distributions that can be factorized using DAGs.  It is a purely
graphical test that uses the underlying graph and makes no reference
to the actual distribution parameters.  See [1]_ for a formal
definition.

To understand d-separation intuitively, consider the following example:

For a pair of two nodes, u and v, all paths are considered open initially, unless
they contain a collider along the path. d-separation is concerned with blocking all
paths between these u and v. A path is considered blocked by the
separating set if all open paths contain some variable in the d-separating
set that is not a collider, or the descendant of a collider.

A collider is a triplet of variables along a path that is like the following:
``... u -> c <- v ...``), where 'c' is a common child of 'u' and 'v'. If the
d-separating set contains a collider, or a descendant of a collider, then the
path through the collider is opened. 

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
from networkx.algorithms.traversal.breadth_first_search import _bfs_with_marks
from networkx.utils import UnionFind, not_implemented_for

__all__ = ["d_separated", "minimal_d_separator", "is_minimal_d_separator"]


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

    Notes
    -----
    A d-separating set in a DAG is a set that when conditioned on
    blocks all paths between the two sets of variables.

    https://en.wikipedia.org/wiki/Bayesian_network#d-separation
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
def minimal_d_separator(G, u, v):
    """Compute a minimal d-separating set between X and Y.

    A d-separating set in a DAG is a set that when conditioned on
    blocks all paths between the two sets of variables. This function
    constructs a set that is "minimal", meaning it is the smallest
    d-separating set between the two variables. This is not necessarily
    unique. For more details, see Notes.

    Parameters
    ----------
    G : graph
        A networkx DAG.
    u : node
        A node in the graph, G.
    v : node
        A node in the graph, G.

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

    Notes
    -----
    This function only finds ``a`` minimal d-separator. It does not guarantee
    uniqueness, since in a DAG there may be more than one minimal d-separator
    between two nodes.

    Moreover, this only checks for minimal separators between two nodes, not
    two sets. Finding minimal d-separators between two sets of nodes is not
    supported.

    Uses the algorithm presented in [1]_. The complexity of the algorithm
    is :math:`O(|E_{An}^m|)`, where :math:`E_{An}^m` stands for the
    number of edges in the moralized graph of the sub-graph consisting
    of only the ancestors of X and Y. For full details, see [1]_.

    https://en.wikipedia.org/wiki/Bayesian_network#d-separation
    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("graph should be directed acyclic")

    union_xy = set(u).union(set(v))

    if any(n not in G.nodes for n in union_xy):
        raise nx.NodeNotFound("one or more specified nodes not found in the graph")

    # first construct the set of ancestors of X and Y
    x_anc = nx.ancestors(G, u)
    y_anc = nx.ancestors(G, v)
    D_anc_xy = x_anc.union(y_anc)
    D_anc_xy = D_anc_xy.union((u, v))

    # second, construct the moralization of the subgraph of Anc(X,Y)
    moral_G = nx.moral_graph(G.subgraph(D_anc_xy))

    # find a separating set Z' in moral_G
    Z_prime = set(G.predecessors(u)).union(set(G.predecessors(v)))

    # perform BFS on the graph from 'x' to mark
    Z_dprime = _bfs_with_marks(moral_G, u, Z_prime)
    Z = _bfs_with_marks(moral_G, v, Z_dprime)
    return Z


@not_implemented_for("undirected")
def is_minimal_d_separator(G, u, v, z):
    """Determine if a d-separating set is minimal.

    A d-separating set in a DAG is a set that when conditioned on
    blocks all paths between the two sets of variables. This function
    verifies that a set is "minimal", meaning there is no possibly
    d-separating set with fewer variables between the two nodes.

    Parameters
    ----------
    G : nx.DiGraph
        The graph.
    u : node
        X node.
    v : node
        Y node.
    z : Set
        The separating set to check is minimal.

    Returns
    -------
    bool
        Whether or not the `z` separating set is minimal.

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

    Notes
    -----
    This function only works on verifying a d-separating set is minimal
    between two nodes. To verify that a d-separating set is minimal between
    two sets of nodes is not supported.

    Uses the algorithm 2 presented in [1]_. The complexity of the algorithm
    is :math:`O(|E_{An}^m|)`, where :math:`E_{An}^m` stands for the
    number of edges in the moralized graph of the sub-graph consisting
    of only the ancestors of ``u`` and ``v``.

    The algorithm works by constructing the moral graph consisting of just
    the ancestors of ``u`` and ``v``. First, it performs BFS on the moral graph
    starting from ``u`` and marking any nodes it encounters that is part of
    the separating set, ``z``. If a node is marked, then it does not continue
    along that path. Then it performs BFS with markings is repeated on the
    moral graph starting from ``v``. If at any stage, any node in ``z`` is
    not marked, then ``z`` is considered not minimal. If the end of the algorithm
    is reached, then ``z`` is minimal.

    For full details, see [1]_.

    https://en.wikipedia.org/wiki/Bayesian_network#d-separation
    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("graph should be directed acyclic")

    union_xy = set(u).union(set(v)).union(z)

    if any(n not in G.nodes for n in union_xy):
        raise nx.NodeNotFound("one or more specified nodes not found in the graph")

    x_anc = nx.ancestors(G, u)
    y_anc = nx.ancestors(G, v)
    xy_anc = x_anc.union(y_anc)

    # if Z contains any node which is not in ancestors of X or Y
    # then it is definitely not minimal
    if any(node not in xy_anc for node in z):
        return False

    D_anc_xy = x_anc.union(y_anc)
    D_anc_xy = D_anc_xy.union((u, v))

    # second, construct the moralization of the subgraph
    moral_G = nx.moral_graph(G.subgraph(D_anc_xy))

    # start BFS from X
    marks = _bfs_with_marks(moral_G, u, z)

    # if not all the Z is marked, then the set is not minimal
    if any(node not in marks for node in z):
        return False

    # similarly, start BFS from Y and check the marks
    marks = _bfs_with_marks(moral_G, v, z)
    # if not all the Z is marked, then the set is not minimal
    if any(node not in marks for node in z):
        return False

    return True
