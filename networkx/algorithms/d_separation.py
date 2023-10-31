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
... nx.is_d_separator(g, {"S1", "S2", "O1", "O2"}, {"S4", "S5", "O4", "O5"}, {"S3"})
True


References
----------

.. [1] Pearl, J.  (2009).  Causality.  Cambridge: Cambridge University Press.

.. [2] Darwiche, A.  (2009).  Modeling and reasoning with Bayesian networks.
   Cambridge: Cambridge University Press.

.. [3] Shachter, Ross D. "Bayes-ball: The rational pastime (for
   determining irrelevance and requisite information in belief networks
   and influence diagrams)." In Proceedings of the Fourteenth Conference
   on Uncertainty in Artificial Intelligence (UAI), (pp. 480–487). 1998.

.. [4] Koller, D., & Friedman, N. (2009).
   Probabilistic graphical models: principles and techniques. The MIT Press.

.. [5] https://en.wikipedia.org/wiki/Causal_Markov_condition

"""

from collections import deque
from itertools import chain

import networkx as nx
from networkx.utils import UnionFind, not_implemented_for

__all__ = ["is_d_separator", "is_minimal_d_separator", "find_minimal_d_separator"]


@not_implemented_for("undirected")
@nx._dispatch
def is_d_separator(G, x, y, z):
    """Return whether node sets ``x`` and ``y`` are d-separated by ``z``.

    Parameters
    ----------
    G : nx.DiGraph
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
        The *d-separation* test is commonly used on disjoint sets of
        nodes in acyclic directed graphs.  Accordingly, the algorithm
        raises a :exc:`NetworkXError` if the node sets are not
        disjoint or if the input graph is not a DAG.

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
def find_minimal_d_separator(G, x, y, *, included=None, restricted=None):
    """Returns a minimal d-separating set between `x` and `y` if possible

    A d-separating set in a DAG is a set of nodes that blocks all
    paths between the two sets of nodes, `x` and `y`. This function
    constructs a d-separating set that is "minimal", meaning it is the
    smallest d-separating set for `x` and `y`. This is not necessarily
    unique. In the case where there are no d-separating sets between `x`
    and `y`, the function will return None.

    For more details, see Notes.

    Parameters
    ----------
    G : graph
        A networkx DAG.
    x : set | node
        A node in the graph, or a set of nodes.
    y : set | node
        A node in the graph, or a set of nodes.
    included : set | node | None
        A node or set of nodes which must be included in the found separating set,
        default is None, which is later set to empty set.
    restricted : set | node | None
        Restricted node or set of nodes to consider. Only these nodes can be in
        the found separating set, default is None meaning all vertices in ``G``.

    Returns
    -------
    z : set | None
        The minimal d-separating set, if at least one d-separating set exists,
        otherwise None.

    Raises
    ------
    NetworkXError
        Raises a :exc:`NetworkXError` if the input graph is not a DAG
        or if node sets `x`, `y`, and `included` are not disjoint.

    NodeNotFound
        If any of the input nodes are not found in the graph,
        a :exc:`NodeNotFound` exception is raised.

    References
    ----------
    .. [1] van der Zander, Benito, and Maciej Liśkiewicz. "Finding
        minimal d-separators in linear time and applications." In
        Uncertainty in Artificial Intelligence, pp. 637-647. PMLR, 2020.

    Notes
    -----
    This function only finds ``a`` minimal d-separator, if at least one
    d-separator exists. It does not guarantee uniqueness, since in a DAG
    there may be more than one minimal d-separator between two sets of nodes.

    Uses the algorithm presented in [1]_. The complexity of the algorithm
    is :math:`O(m)`, where :math:`m` stands for the number of edges in
    the subgraph of G consisting of only the ancestors of `x` and `y`.
    For full details, see [1]_.
    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("graph should be directed acyclic")

    if not isinstance(x, set):
        x = {x}
    if x - G.nodes:
        raise nx.NodeNotFound(f"The node {x} is not found in G.")
    if not isinstance(y, set):
        y = {y}
    if y - G.nodes:
        raise nx.NodeNotFound(f"The node {y} is not found in G.")

    if included is None:
        included = set()
    elif not isinstance(included, set):
        included = {included}
    if restricted is None:
        restricted = set(G)
    elif not isinstance(restricted, set):
        restricted = {restricted}

    set_y = x | y | included | restricted
    if set_y - G.nodes:
        raise nx.NodeNotFound(f"The node(s) {set_y - G.nodes} are not found in G")
    if not included <= restricted:
        raise nx.NetworkXError(
            f"Minimal set {included} should be no larger than maximal set {restricted}"
        )

    intersection = (
        x.intersection(y) or x.intersection(included) or y.intersection(included)
    )
    if intersection:
        raise nx.NetworkXError(
            f"The sets are not disjoint, with intersection {intersection}"
        )

    nodeset = x.union(y).union(included)
    ancestors_x_y_included = nodeset.union(*[nx.ancestors(G, node) for node in nodeset])

    z_init = restricted.intersection(ancestors_x_y_included.difference(x.union(y)))

    x_closure = _reachable(G, x, ancestors_x_y_included, z_init)
    z_updated = z_init.intersection(x_closure).union(included)

    y_closure = _reachable(G, y, ancestors_x_y_included, z_updated)
    if x_closure.intersection(y):
        return None
    return z_updated.intersection(y_closure).union(included)


@not_implemented_for("undirected")
@nx._dispatch
def is_minimal_d_separator(G, x, y, z, *, included=None, restricted=None):
    """Determine if `z` is a minimal d-separating set for `x` and `y`.

    A d-separating set, `z`, in a DAG is a set of nodes that blocks
    all paths between the sets `x` and `y`. This function verifies
    that a set is "minimal", meaning there is no smaller d-separating
    set between the two nodes.

    Note: This function checks whether `z` is a d-separator AND is
    minimal. One can use the function `is_d_separator` to only check if
    `z` is a d-separator. See examples below.

    Parameters
    ----------
    G : nx.DiGraph
        A NetworkX DAG.
    x : node | set
        A node in the graph, or a set of nodes.
    y : node | set
        A node in the graph, or a set of nodes.
    z : node | set
        The node or set of nodes to check if it is a minimal d-separating set.
        The function :func:`is_d_separator` is called inside this function
        to verify that `z` is in fact a d-separator.
    included : set | node | None
        A node or set of nodes which must be included in the found separating set,
        default is None, which is later set to empty set.
    restricted : set | node | None
        Restricted node or set of nodes to consider. Only these nodes can be in
        the found separating set, default is None meaning all vertices in ``G``.

    Returns
    -------
    bool
        Whether or not the set `z` is a d-separator and is also minimal.

    Examples
    --------
    >>> G = nx.path_graph([0, 1, 2, 3], create_using=nx.DiGraph)
    >>> G.add_node(4)
    >>> nx.is_minimal_d_separator(G, 0, 2, {1})
    True
    >>> # since {1} is the minimal d-separator, {1, 3, 4} is not minimal
    >>> nx.is_minimal_d_separator(G, 0, 2, {1, 3, 4})
    False
    >>> # alternatively, if we only want to check that {1, 3, 4} is a d-separator
    >>> nx.is_d_separator(G, 0, 2, {1, 3, 4})
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
    .. [1] van der Zander, Benito, and Maciej Liśkiewicz. "Finding
        minimal d-separators in linear time and applications." In
        Uncertainty in Artificial Intelligence, pp. 637-647. PMLR, 2020.

    Notes
    -----
    This function works on verifying that a set is minimal and
    d-separating between two nodes. Uses criterion (a), (b), (c) on
    page 4 of [1]_. The complexity is :math:`O(m)`, where :math:`m`
    stands for the number of edges in the subgraph of G consisting of
    only the ancestors of `x` and `y`.

    For full details, see [1]_.
    """
    if not nx.is_directed_acyclic_graph(G):
        raise nx.NetworkXError("graph should be directed acyclic")
    if not isinstance(x, set):
        x = {x}
    if x - G.nodes:
        raise nx.NodeNotFound(f"The node {x} is not found in G.")
    if not isinstance(y, set):
        y = {y}
    if y - G.nodes:
        raise nx.NodeNotFound(f"The node {y} is not found in G.")
    if not isinstance(z, set):
        z = {z}
    if z - G.nodes:
        raise nx.NodeNotFound(f"The node {z} is not found in G.")

    if included is None:
        included = set()
    elif not isinstance(included, set):
        included = {included}
    if restricted is None:
        restricted = set(G.nodes())
    elif not isinstance(restricted, set):
        restricted = {restricted}

    set_y = x | y | z | included | restricted
    if set_y - G.nodes:
        raise nx.NodeNotFound(f"The node(s) {set_y - G.nodes} are not found in G")

    if not included <= z:
        raise nx.NetworkXError(
            f"Minimal set {included} should be no larger than proposed separating set {z}"
        )
    if not z <= restricted:
        raise nx.NetworkXError(
            f"Separating set {z} should be no larger than maximum set {restricted}"
        )

    intersection = x.intersection(y) or x.intersection(z) or y.intersection(z)
    if intersection:
        raise nx.NetworkXError(
            f"The sets are not disjoint, with intersection {intersection}"
        )

    nodeset = x.union(y).union(included)
    ancestors_x_y_included = nodeset.union(*[nx.ancestors(G, node) for node in nodeset])

    # criterion (a) -- check that z is actually a separator
    x_closure = _reachable(G, x, ancestors_x_y_included, z)
    crit_a = not any(x_closure.intersection(y))

    # criterion (b) -- basic constraint; included and restricted already checked above
    crit_b = z <= ancestors_x_y_included

    # criterion (c) -- check that z is minimal
    y_closure = _reachable(G, y, ancestors_x_y_included, z)
    crit_c = z.difference(included) <= x_closure.intersection(y_closure)

    return crit_a and crit_b and crit_c


@not_implemented_for("undirected")
def _reachable(G, x, a, z):
    """Modified Bayes-Ball algorithm for finding d-connected nodes.

    Find all nodes in `a` that are d-connected to those in `x` by
    those in `z`. This is an implementation of the function
    `REACHABLE` in [1]_ (which is itself a modification of the
    Bayes-Ball algorithm [2]_) when restricted to DAGs.

    Parameters
    ----------
    G : nx.DiGraph
        A NetworkX DAG.
    x : node | set
        A node in the DAG, or a set of nodes.
    a : node | set
        A (set of) node(s) in the DAG containing the ancestors of `x`.
    z : node | set
        The node or set of nodes conditioned on when checking d-connectedness.

    Returns
    -------
    w : set
        The closure of `x` in `a` with respect to d-connectedness
        given `z`.

    References
    ----------
    .. [1] van der Zander, Benito, and Maciej Liśkiewicz. "Finding
        minimal d-separators in linear time and applications." In
        Uncertainty in Artificial Intelligence, pp. 637-647. PMLR, 2020.

    .. [2] Shachter, Ross D. "Bayes-ball: The rational pastime
       (for determining irrelevance and requisite information in
       belief networks and influence diagrams)." In Proceedings of the
       Fourteenth Conference on Uncertainty in Artificial Intelligence
       (UAI), (pp. 480–487). 1998.
    """

    def _pass(e, v, f, n):
        """Whether a ball entering node `v` along edge `e` passes to `n` along `f`.

        Boolean function defined on page 6 of [1]_.

        Parameters
        ----------
        e : bool
            Directed edge by which the ball got to node `v`; `True` iff directed into `v`.
        v : node
            Node where the ball is.
        f : bool
            Directed edge connecting nodes `v` and `n`; `True` iff directed `n`.
        n : node
            Checking whether the ball passes to this node.

        Returns
        -------
        b : bool
            Whether the ball passes or not.

        References
        ----------
        .. [1] van der Zander, Benito, and Maciej Liśkiewicz. "Finding
           minimal d-separators in linear time and applications." In
           Uncertainty in Artificial Intelligence, pp. 637-647. PMLR, 2020.
        """
        is_element_of_A = n in a
        # almost_definite_status = True  # always true for DAGs; not so for RCGs
        collider_if_in_Z = v not in z or (e and not f)
        return is_element_of_A and collider_if_in_Z  # and almost_definite_status

    queue = deque([])
    for node in x:
        if bool(G.pred[node]):
            queue.append((True, node))
        if bool(G.succ[node]):
            queue.append((False, node))
    processed = queue.copy()

    while any(queue):
        e, v = queue.popleft()
        preds = ((False, n) for n in G.pred[v])
        succs = ((True, n) for n in G.succ[v])
        f_n_pairs = chain(preds, succs)
        for f, n in f_n_pairs:
            if (f, n) not in processed and _pass(e, v, f, n):
                queue.append((f, n))
                processed.append((f, n))

    return {w for (_, w) in processed}
