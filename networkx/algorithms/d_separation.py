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

Here, we provide a brief overview of d-separation and related concepts that
are relevant for understanding it:

Blocking paths
--------------

Before we overview, we introduce the following terminology to describe paths:

- "open" path: A path between two nodes that can be traversed
- "blocked" path: A path between two nodes that cannot be traversed

A **collider** is a triplet of nodes along a path that is like the following:
``... u -> c <- v ...``), where 'c' is a common successor of ``u`` and ``v``. A path
through a collider is considered "blocked". When
a node that is a collider, or a descendant of a collider is included in
the d-separating set, then the path through that collider node is "open". If the
path through the collider node is open, then we will call this node an open collider.

The d-separation set blocks the paths between ``u`` and ``v``. If you include colliders,
or their descendant nodes in the d-separation set, then those colliders will open up,
enabling a path to be traversed if it is not blocked some other way.

Illustration of D-separation with examples
------------------------------------------

For a pair of two nodes, ``u`` and ``v``, all paths are considered open if
there is a path between ``u`` and ``v`` that is not blocked. That means, there is an open
path between ``u`` and ``v`` that does not encounter a collider, or a variable in the
d-separating set.

For example, if the d-separating set is the empty set, then the following paths are
unblocked between ``u`` and ``v``:

- u <- z -> v
- u -> w -> ... -> z -> v

If for example, 'z' is in the d-separating set, then 'z' blocks those paths
between ``u`` and ``v``.

Colliders block a path by default if they and their descendants are not included
in the d-separating set. An example of a path that is blocked when the d-separating
set is empty is:

- u -> w -> ... -> z <- v

because 'z' is a collider in this path and 'z' is not in the d-separating set. However,
if 'z' or a descendant of 'z' is included in the d-separating set, then the path through
the collider at 'z' (... -> z <- ...) is now "open".

D-separation is concerned with blocking all paths between u and v. Therefore, a
d-separating set between ``u`` and ``v`` is one where all paths are blocked.

D-separation and its applications in probability
------------------------------------------------

D-separation is commonly used in probabilistic graphical models. D-separation
connects the idea of probabilistic "dependence" with separation in a graph. If
one assumes the causal Markov condition [5]_, then d-separation implies conditional
independence in probability distributions.

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

.. [5] https://en.wikipedia.org/wiki/Causal_Markov_condition

"""

from collections import deque

import networkx as nx
from networkx.utils import UnionFind, not_implemented_for

__all__ = ["d_separated", "minimal_d_separated", "find_minimal_d_separator"]


@not_implemented_for("undirected")
@nx._dispatch
def d_separated(G, x, y, z):
    """
    Return whether node sets ``x`` and ``y`` are d-separated by ``z``.

    Parameters
    ----------
    G : graph
        A NetworkX DAG.

    x : set | node
        First set of nodes in ``G``.

    y : set | node
        Second set of nodes in ``G``.

    z : set | node
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
        a :exc:`NodeNotFound` exception is raised
    Notes
    -----
    A d-separating set in a DAG is a set of nodes that
    blocks all paths between the two sets. Nodes in `z`
    block a path if they are part of the path and are not a collider,
    or a descendant of a collider. A collider structure along a path
    is ``... -> c <- ...`` where ``c`` is the collider node.

    https://en.wikipedia.org/wiki/Bayesian_network#d-separation
    """

    if not isinstance(x, set):
        x = {x}
    if x - G.nodes:
        raise nx.NodeNotFound(f"The node(s) {x} are not found in G.")
    if not isinstance(y, set):
        y = {y}
    if y - G.nodes:
        raise nx.NodeNotFound(f"The node(s) {y} are not found in G.")
    if not isinstance(z, set):
        z = {z}
    if z - G.nodes:
        raise nx.NodeNotFound(f"The node(s) {z} are not found in G.")

    intersection = x.intersection(y) or x.intersection(z) or y.intersection(z)
    if intersection:
        raise nx.NetworkXError(
            f"The sets are not disjoint, with intersection {intersection}"
        )

    set_v = x | y | z
    if set_v - G.nodes:
        raise nx.NodeNotFound(f"The node(s) {set_v - G.nodes} are not found in G")

    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("graph should be directed acyclic")

    # contains -> and <-> edges from starting node T
    forward_deque = deque([])
    forward_visited = set()

    # contains <- and - edges from starting node T
    backward_deque = deque(x)
    backward_visited = set()

    an_z = set().union(*[nx.ancestors(G, node) for node in x]) | z | x

    while forward_deque or backward_deque:
        if backward_deque:
            node = backward_deque.popleft()
            backward_visited.add(node)
            if node in y:
                return False
            if node in z:
                continue

            # add <- edges to backward deque
            for x, _ in G.in_edges(nbunch=node):
                if x not in backward_visited:
                    backward_deque.append(x)

            # add -> edges to forward deque
            for _, x in G.out_edges(nbunch=node):
                if x not in forward_visited:
                    forward_deque.append(x)

        if forward_deque:
            node = forward_deque.popleft()
            forward_visited.add(node)
            if node in y:
                return False

            # Consider if -> node <- is opened due to conditioning on collider,
            # or descendant of collider
            if node in an_z:
                # add <- edges to backward deque
                for x, _ in G.in_edges(nbunch=node):
                    if x not in backward_visited:
                        backward_deque.append(x)

            if node not in z:
                # add -> edges to forward deque
                for _, x in G.out_edges(nbunch=node):
                    if x not in forward_visited:
                        forward_deque.append(x)

    return True


@not_implemented_for("undirected")
@nx._dispatch
def find_minimal_d_separator(G, u, v, i=None, r=None):
    """Returns a minimal d-separating set between 'u' and 'v' if possible

    A d-separating set in a DAG is a set of nodes that blocks all paths
    between the two sets of nodes, 'u' and 'v'. This function
    constructs a d-separating set that is "minimal", meaning it is the smallest
    d-separating set for 'u' and 'v'. This is not necessarily
    unique. In the case where there are no d-separating sets between 'u' and
    'v', the function will return None.

    For more details, see Notes.

    TODO: need to explain the difference between strongly minimal vs I-minimal


    Parameters
    ----------
    G : graph
        A networkx DAG.
    u : set | node
        A node in the graph, or a set of nodes.
    v : set | node
        A node in the graph, or a set of nodes.
    i : set
        Set of nodes which are always included in the found separating set,
        default is None, which is later set to empty set.
    r : set
        Largest set of nodes which may be included in the found separating set,
        default is None, which is later set to all vertices in ``G``.

    Returns
    -------
    Z : set | None
        The minimal d-separating set, if at least one d-separating set exists,
        otherwise None.

    Raises
    ------
    NetworkXError
        Raises a :exc:`NetworkXError` if the input graph is not a DAG.

    NodeNotFound
        If any of the input nodes are not found in the graph,
        a :exc:`NodeNotFound` exception is raised.

    References
    ----------
    .. [1] B. van der Zander, M. Liśkiewicz, and J. Textor, “Separators and Adjustment
       Sets in Causal Graphs: Complete Criteria and an Algorithmic Framework,” Artificial
       Intelligence, vol. 270, pp. 1–40, May 2019, doi: 10.1016/j.artint.2018.12.006.
    Notes
    -----
    This function only finds ``a`` minimal d-separator, if at least one
    d-separator exists. It does not guarantee uniqueness, since in a DAG
    there may be more than one minimal d-separator between two sets of nodes.

    Uses the algorithm presented in [1]_. The complexity of the algorithm
    is :math:`O(n^2)`, where :math:`n` stands for the
    number of nodes in the moralized graph of the sub-graph consisting
    of only the ancestors of 'u' and 'v'. For full details, see [1]_.

    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("graph should be directed acyclic")
    if not isinstance(u, set):
        u = {u}
    if u - G.nodes:
        raise nx.NodeNotFound(f"The node {u} is not found in G.")

    if not isinstance(v, set):
        v = {v}
    if v - G.nodes:
        raise nx.NodeNotFound(f"The node {v} is not found in G.")

    if i is None:
        i = set()
    if r is None:
        r = set(G.nodes())
    set_v = u | v | i | r
    if set_v - G.nodes:
        raise nx.NodeNotFound(f"The node(s) {set_v - G.nodes} are not found in G")
    if not i <= r:
        raise nx.NetworkError(
            f"Minimal set {i} should be no larger than maximal set {r}"
        )

    G_copy = G.copy()

    nodeset = u.union(v).union(i)

    ancestor_nodes_G = nodeset.union(*[nx.ancestors(G_copy, node) for node in nodeset])
    G_p = G.subgraph(ancestor_nodes_G)
    aug_G_p = nx.moral_graph(G_p)
    for node in i:
        aug_G_p.remove_node(node)
    for node in i:
        aug_G_p.remove_node(node)
    for node in i:
        G_p.remove_node(node)

    uv = u.union(v)

    z_prime = r.intersection(set().union(*[nx.ancestors(G_copy, node) for node in uv]))
    z_dprime = _bfs_with_marks(aug_G_p, u, z_prime)
    z = _bfs_with_marks(aug_G_p, v, z_dprime)

    if not d_separated(G_p, u, v, z):
        return None

    return z.union(i)


@not_implemented_for("undirected")
@nx._dispatch
def minimal_d_separated(G, u, v, z, i=None, r=None):
    """Determine if `z` is a minimal d-separating set for `u` and `v`.

    A d-separating set, `z`, in a DAG is a set of nodes that blocks
    all paths between the two nodes, `u` and `v`. This function
    verifies that a set is "minimal", meaning there is no smaller
    d-separating set between the two nodes.

    Note: This function checks whether `z` is a d-separator AND is minimal.
    One can use the function `d_separated` to only check if `z` is a d-separator.
    See examples below.

    Parameters
    ----------
    G : nx.DiGraph
        The graph.
    u : node | set
        A node in the graph, or a set of nodes.
    v : node | set
        A node in the graph, or a set of nodes.
    z : node | set
        The node or set of nodes to check if it is a minimal d-separating set.
        The function :func:`d_separated` is called inside this function
        to verify that `z` is in fact a d-separator.
    i : set
        Set of nodes which are always included in the found separating set,
        default is None, which is later set to empty set.
    r : set
        Largest set of nodes which may be included in the found separating set,

    Returns
    -------
    bool
        Whether or not the set `z` is a d-separator and is also minimal.

    Examples
    --------
    >>> G = nx.path_graph([0, 1, 2, 3], create_using=nx.DiGraph)
    >>> G.add_node(4)
    >>> nx.minimal_d_separated(G, 0, 2, {1})
    True
    >>> # since {1} is the minimal d-separator, {1, 3, 4} is not minimal
    >>> nx.minimal_d_separated(G, 0, 2, {1, 3, 4})
    False
    >>> # alternatively, if we only want to check that {1, 3, 4} is a d-separator
    >>> nx.d_separated(G, {0}, {4}, {1, 3, 4})
    True

    Raises
    ------
    NetworkXError
        Raises a :exc:`NetworkXError` if the input graph is not a DAG.

    NodeNotFound
        If any of the input nodes are not found in the graph,
        a :exc:`NodeNotFound` exception is raised.

    References
    ----------
    .. [1] B. van der Zander, M. Liśkiewicz, and J. Textor, “Separators and Adjustment
       Sets in Causal Graphs: Complete Criteria and an Algorithmic Framework,” Artificial
       Intelligence, vol. 270, pp. 1–40, May 2019, doi: 10.1016/j.artint.2018.12.006.

    Notes
    -----
    This function works on verifying that a set is minimal
     and d-separating between two nodes.
    Uses algorithm TESTMINSEP presented in [1]_. The complexity of the algorithm
    is :math:`O(n^2)`, where :math:`n` stands for the
    number of nodes.

    For full details, see [1]_.

    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("graph should be directed acyclic")
    if not isinstance(u, set):
        u = {u}
    if u - G.nodes:
        raise nx.NodeNotFound(f"The node {u} is not found in G.")
    if not isinstance(v, set):
        v = {v}
    if v - G.nodes:
        raise nx.NodeNotFound(f"The node {v} is not found in G.")
    if not isinstance(z, set):
        z = {z}
    if z - G.nodes:
        raise nx.NodeNotFound(f"The node {z} is not found in G.")

    if i is None:
        i = set()
    if r is None:
        r = set(G.nodes())

    set_v = u | v | z | i | r
    if set_v - G.nodes:
        raise nx.NodeNotFound(f"The node(s) {set_v - G.nodes} are not found in G")

    if not i <= z:
        raise nx.NetworkXError(
            f"Minimal set {i} should be no larger than proposed separating set {z}"
        )
    if not z <= r:
        raise nx.NetworkXError(
            f"Separating set {z} should be no larger than maximum set {r}"
        )

    uvi = u | v | i

    if z - uvi.union(*[nx.ancestors(G, node) for node in uvi]) != set() or not z <= r:
        return False
    if not d_separated(G, u, v, z):
        return False

    G_copy = G.copy()

    nodeset = u.union(v).union(i)

    ancestor_nodes_G = nodeset.union(*[nx.ancestors(G_copy, node) for node in nodeset])
    aug_G_p = nx.moral_graph(G.subgraph(ancestor_nodes_G))
    for node in i:
        aug_G_p.remove_node(node)

    r_u = _bfs_with_marks(aug_G_p, u, z)

    # Note: we check z - i != r_x instead of z != r_x since
    # all nodes in i are removed from graph and so x will never have a path
    # to i. Appears to be bug in the original algorithm.
    if z - i != r_u:
        return False
    r_v = _bfs_with_marks(aug_G_p, v, z)

    # Note: we check z - i != r_y for similar reasons as above.
    if z - i != r_v:
        return False

    return True


@not_implemented_for("directed")
def _bfs_with_marks(G, start_set, check_set):
    """Breadth-first-search with markings.

    Performs BFS starting from ``start_set`` and whenever a node
    inside ``check_set`` is met, it is "marked". Once a node is marked,
    BFS does not continue along that path. The resulting marked nodes
    are returned.

    Parameters
    ----------
    G : nx.Graph
        An undirected graph.
    start_set : set | node
        The set of starting nodes of the BFS.
    check_set : set
        The set of nodes to check against.

    Returns
    -------
    marked : set
        A set of nodes that were marked.
    """
    if start_set in G:
        start_set = {start_set}

    visited = {}
    marked = set()
    queue = []
    for node in start_set:
        visited[node] = None
        queue.append(node)
    while queue:
        m = queue.pop(0)

        for nbr in G.neighbors(m):
            if nbr not in visited:
                # memoize where we visited so far
                visited[nbr] = None

                # mark the node in Z' and do not continue along that path
                if nbr in check_set:
                    marked.add(nbr)
                else:
                    queue.append(nbr)
    return marked
