"""Generators for geometric graphs.
"""

import math
from bisect import bisect_left
from itertools import accumulate, combinations, product

import networkx as nx
from networkx.utils import py_random_state

__all__ = [
    "geometric_edges",
    "geographical_threshold_graph",
    "navigable_small_world_graph",
    "random_geometric_graph",
    "soft_random_geometric_graph",
    "thresholded_random_geometric_graph",
    "waxman_graph",
    "S1_graph",
]


@nx._dispatch(preserve_node_attrs={"G": {"pos": None}})
def geometric_edges(G, radius, p=2):
    """Returns edge list of node pairs within `radius` of each other.

    Parameters
    ----------
    G : networkx graph
        The graph from which to generate the edge list. The nodes in `G` should
        have an attribute ``pos`` corresponding to the node position, which is
        used to compute the distance to other nodes.
    radius : scalar
        The distance threshold. Edges are included in the edge list if the
        distance between the two nodes is less than `radius`.
    p : scalar, default=2
        The `Minkowski distance metric
        <https://en.wikipedia.org/wiki/Minkowski_distance>`_ used to compute
        distances. The default value is 2, i.e. Euclidean distance.

    Returns
    -------
    edges : list
        List of edges whose distances are less than `radius`

    Notes
    -----
    Radius uses Minkowski distance metric `p`.
    If scipy is available, `scipy.spatial.cKDTree` is used to speed computation.

    Examples
    --------
    Create a graph with nodes that have a "pos" attribute representing 2D
    coordinates.

    >>> G = nx.Graph()
    >>> G.add_nodes_from([
    ...     (0, {"pos": (0, 0)}),
    ...     (1, {"pos": (3, 0)}),
    ...     (2, {"pos": (8, 0)}),
    ... ])
    >>> nx.geometric_edges(G, radius=1)
    []
    >>> nx.geometric_edges(G, radius=4)
    [(0, 1)]
    >>> nx.geometric_edges(G, radius=6)
    [(0, 1), (1, 2)]
    >>> nx.geometric_edges(G, radius=9)
    [(0, 1), (0, 2), (1, 2)]
    """
    # Input validation - every node must have a "pos" attribute
    for n, pos in G.nodes(data="pos"):
        if pos is None:
            raise nx.NetworkXError(
                f"All nodes in `G` must have a 'pos' attribute. Check node {n}"
            )

    # NOTE: See _geometric_edges for the actual implementation. The reason this
    # is split into two functions is to avoid the overhead of input validation
    # every time the function is called internally in one of the other
    # geometric generators
    return _geometric_edges(G, radius, p)


def _geometric_edges(G, radius, p=2):
    """
    Implements `geometric_edges` without input validation. See `geometric_edges`
    for complete docstring.
    """
    nodes_pos = G.nodes(data="pos")
    try:
        import scipy as sp
    except ImportError:
        # no scipy KDTree so compute by for-loop
        radius_p = radius**p
        edges = [
            (u, v)
            for (u, pu), (v, pv) in combinations(nodes_pos, 2)
            if sum(abs(a - b) ** p for a, b in zip(pu, pv)) <= radius_p
        ]
        return edges
    # scipy KDTree is available
    nodes, coords = list(zip(*nodes_pos))
    kdtree = sp.spatial.cKDTree(coords)  # Cannot provide generator.
    edge_indexes = kdtree.query_pairs(radius, p)
    edges = [(nodes[u], nodes[v]) for u, v in sorted(edge_indexes)]
    return edges


@py_random_state(5)
def random_geometric_graph(n, radius, dim=2, pos=None, p=2, seed=None):
    """Returns a random geometric graph in the unit cube of dimensions `dim`.

    The random geometric graph model places `n` nodes uniformly at
    random in the unit cube. Two nodes are joined by an edge if the
    distance between the nodes is at most `radius`.

    Edges are determined using a KDTree when SciPy is available.
    This reduces the time complexity from $O(n^2)$ to $O(n)$.

    Parameters
    ----------
    n : int or iterable
        Number of nodes or iterable of nodes
    radius: float
        Distance threshold value
    dim : int, optional
        Dimension of graph
    pos : dict, optional
        A dictionary keyed by node with node positions as values.
    p : float, optional
        Which Minkowski distance metric to use.  `p` has to meet the condition
        ``1 <= p <= infinity``.

        If this argument is not specified, the :math:`L^2` metric
        (the Euclidean distance metric), p = 2 is used.
        This should not be confused with the `p` of an Erdős-Rényi random
        graph, which represents probability.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    Graph
        A random geometric graph, undirected and without self-loops.
        Each node has a node attribute ``'pos'`` that stores the
        position of that node in Euclidean space as provided by the
        ``pos`` keyword argument or, if ``pos`` was not provided, as
        generated by this function.

    Examples
    --------
    Create a random geometric graph on twenty nodes where nodes are joined by
    an edge if their distance is at most 0.1::

    >>> G = nx.random_geometric_graph(20, 0.1)

    Notes
    -----
    This uses a *k*-d tree to build the graph.

    The `pos` keyword argument can be used to specify node positions so you
    can create an arbitrary distribution and domain for positions.

    For example, to use a 2D Gaussian distribution of node positions with mean
    (0, 0) and standard deviation 2::

    >>> import random
    >>> n = 20
    >>> pos = {i: (random.gauss(0, 2), random.gauss(0, 2)) for i in range(n)}
    >>> G = nx.random_geometric_graph(n, 0.2, pos=pos)

    References
    ----------
    .. [1] Penrose, Mathew, *Random Geometric Graphs*,
           Oxford Studies in Probability, 5, 2003.

    """
    # TODO Is this function just a special case of the geographical
    # threshold graph?
    #
    #     half_radius = {v: radius / 2 for v in n}
    #     return geographical_threshold_graph(nodes, theta=1, alpha=1,
    #                                         weight=half_radius)
    #
    G = nx.empty_graph(n)
    # If no positions are provided, choose uniformly random vectors in
    # Euclidean space of the specified dimension.
    if pos is None:
        pos = {v: [seed.random() for i in range(dim)] for v in G}
    nx.set_node_attributes(G, pos, "pos")

    G.add_edges_from(_geometric_edges(G, radius, p))
    return G


@py_random_state(6)
def soft_random_geometric_graph(
    n, radius, dim=2, pos=None, p=2, p_dist=None, seed=None
):
    r"""Returns a soft random geometric graph in the unit cube.

    The soft random geometric graph [1] model places `n` nodes uniformly at
    random in the unit cube in dimension `dim`. Two nodes of distance, `dist`,
    computed by the `p`-Minkowski distance metric are joined by an edge with
    probability `p_dist` if the computed distance metric value of the nodes
    is at most `radius`, otherwise they are not joined.

    Edges within `radius` of each other are determined using a KDTree when
    SciPy is available. This reduces the time complexity from :math:`O(n^2)`
    to :math:`O(n)`.

    Parameters
    ----------
    n : int or iterable
        Number of nodes or iterable of nodes
    radius: float
        Distance threshold value
    dim : int, optional
        Dimension of graph
    pos : dict, optional
        A dictionary keyed by node with node positions as values.
    p : float, optional
        Which Minkowski distance metric to use.
        `p` has to meet the condition ``1 <= p <= infinity``.

        If this argument is not specified, the :math:`L^2` metric
        (the Euclidean distance metric), p = 2 is used.

        This should not be confused with the `p` of an Erdős-Rényi random
        graph, which represents probability.
    p_dist : function, optional
        A probability density function computing the probability of
        connecting two nodes that are of distance, dist, computed by the
        Minkowski distance metric. The probability density function, `p_dist`,
        must be any function that takes the metric value as input
        and outputs a single probability value between 0-1. The scipy.stats
        package has many probability distribution functions implemented and
        tools for custom probability distribution definitions [2], and passing
        the .pdf method of scipy.stats distributions can be used here.  If the
        probability function, `p_dist`, is not supplied, the default function
        is an exponential distribution with rate parameter :math:`\lambda=1`.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    Graph
        A soft random geometric graph, undirected and without self-loops.
        Each node has a node attribute ``'pos'`` that stores the
        position of that node in Euclidean space as provided by the
        ``pos`` keyword argument or, if ``pos`` was not provided, as
        generated by this function.

    Examples
    --------
    Default Graph:

    G = nx.soft_random_geometric_graph(50, 0.2)

    Custom Graph:

    Create a soft random geometric graph on 100 uniformly distributed nodes
    where nodes are joined by an edge with probability computed from an
    exponential distribution with rate parameter :math:`\lambda=1` if their
    Euclidean distance is at most 0.2.

    Notes
    -----
    This uses a *k*-d tree to build the graph.

    The `pos` keyword argument can be used to specify node positions so you
    can create an arbitrary distribution and domain for positions.

    For example, to use a 2D Gaussian distribution of node positions with mean
    (0, 0) and standard deviation 2

    The scipy.stats package can be used to define the probability distribution
    with the .pdf method used as `p_dist`.

    ::

    >>> import random
    >>> import math
    >>> n = 100
    >>> pos = {i: (random.gauss(0, 2), random.gauss(0, 2)) for i in range(n)}
    >>> p_dist = lambda dist: math.exp(-dist)
    >>> G = nx.soft_random_geometric_graph(n, 0.2, pos=pos, p_dist=p_dist)

    References
    ----------
    .. [1] Penrose, Mathew D. "Connectivity of soft random geometric graphs."
           The Annals of Applied Probability 26.2 (2016): 986-1028.
    .. [2] scipy.stats -
           https://docs.scipy.org/doc/scipy/reference/tutorial/stats.html

    """
    G = nx.empty_graph(n)
    G.name = f"soft_random_geometric_graph({n}, {radius}, {dim})"
    # If no positions are provided, choose uniformly random vectors in
    # Euclidean space of the specified dimension.
    if pos is None:
        pos = {v: [seed.random() for i in range(dim)] for v in G}
    nx.set_node_attributes(G, pos, "pos")

    # if p_dist function not supplied the default function is an exponential
    # distribution with rate parameter :math:`\lambda=1`.
    if p_dist is None:

        def p_dist(dist):
            return math.exp(-dist)

    def should_join(edge):
        u, v = edge
        dist = (sum(abs(a - b) ** p for a, b in zip(pos[u], pos[v]))) ** (1 / p)
        return seed.random() < p_dist(dist)

    G.add_edges_from(filter(should_join, _geometric_edges(G, radius, p)))
    return G


@py_random_state(7)
def geographical_threshold_graph(
    n, theta, dim=2, pos=None, weight=None, metric=None, p_dist=None, seed=None
):
    r"""Returns a geographical threshold graph.

    The geographical threshold graph model places $n$ nodes uniformly at
    random in a rectangular domain.  Each node $u$ is assigned a weight
    $w_u$. Two nodes $u$ and $v$ are joined by an edge if

    .. math::

       (w_u + w_v)p_{dist}(r) \ge \theta

    where `r` is the distance between `u` and `v`, `p_dist` is any function of
    `r`, and :math:`\theta` as the threshold parameter. `p_dist` is used to
    give weight to the distance between nodes when deciding whether or not
    they should be connected. The larger `p_dist` is, the more prone nodes
    separated by `r` are to be connected, and vice versa.

    Parameters
    ----------
    n : int or iterable
        Number of nodes or iterable of nodes
    theta: float
        Threshold value
    dim : int, optional
        Dimension of graph
    pos : dict
        Node positions as a dictionary of tuples keyed by node.
    weight : dict
        Node weights as a dictionary of numbers keyed by node.
    metric : function
        A metric on vectors of numbers (represented as lists or
        tuples). This must be a function that accepts two lists (or
        tuples) as input and yields a number as output. The function
        must also satisfy the four requirements of a `metric`_.
        Specifically, if $d$ is the function and $x$, $y$,
        and $z$ are vectors in the graph, then $d$ must satisfy

        1. $d(x, y) \ge 0$,
        2. $d(x, y) = 0$ if and only if $x = y$,
        3. $d(x, y) = d(y, x)$,
        4. $d(x, z) \le d(x, y) + d(y, z)$.

        If this argument is not specified, the Euclidean distance metric is
        used.

        .. _metric: https://en.wikipedia.org/wiki/Metric_%28mathematics%29
    p_dist : function, optional
        Any function used to give weight to the distance between nodes when
        deciding whether or not they should be connected. `p_dist` was
        originally conceived as a probability density function giving the
        probability of connecting two nodes that are of metric distance `r`
        apart. The implementation here allows for more arbitrary definitions
        of `p_dist` that do not need to correspond to valid probability
        density functions. The :mod:`scipy.stats` package has many
        probability density functions implemented and tools for custom
        probability density definitions, and passing the ``.pdf`` method of
        scipy.stats distributions can be used here. If ``p_dist=None``
        (the default), the exponential function :math:`r^{-2}` is used.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    Graph
        A random geographic threshold graph, undirected and without
        self-loops.

        Each node has a node attribute ``pos`` that stores the
        position of that node in Euclidean space as provided by the
        ``pos`` keyword argument or, if ``pos`` was not provided, as
        generated by this function. Similarly, each node has a node
        attribute ``weight`` that stores the weight of that node as
        provided or as generated.

    Examples
    --------
    Specify an alternate distance metric using the ``metric`` keyword
    argument. For example, to use the `taxicab metric`_ instead of the
    default `Euclidean metric`_::

        >>> dist = lambda x, y: sum(abs(a - b) for a, b in zip(x, y))
        >>> G = nx.geographical_threshold_graph(10, 0.1, metric=dist)

    .. _taxicab metric: https://en.wikipedia.org/wiki/Taxicab_geometry
    .. _Euclidean metric: https://en.wikipedia.org/wiki/Euclidean_distance

    Notes
    -----
    If weights are not specified they are assigned to nodes by drawing randomly
    from the exponential distribution with rate parameter $\lambda=1$.
    To specify weights from a different distribution, use the `weight` keyword
    argument::

    >>> import random
    >>> n = 20
    >>> w = {i: random.expovariate(5.0) for i in range(n)}
    >>> G = nx.geographical_threshold_graph(20, 50, weight=w)

    If node positions are not specified they are randomly assigned from the
    uniform distribution.

    References
    ----------
    .. [1] Masuda, N., Miwa, H., Konno, N.:
       Geographical threshold graphs with small-world and scale-free
       properties.
       Physical Review E 71, 036108 (2005)
    .. [2]  Milan Bradonjić, Aric Hagberg and Allon G. Percus,
       Giant component and connectivity in geographical threshold graphs,
       in Algorithms and Models for the Web-Graph (WAW 2007),
       Antony Bonato and Fan Chung (Eds), pp. 209--216, 2007
    """
    G = nx.empty_graph(n)
    # If no weights are provided, choose them from an exponential
    # distribution.
    if weight is None:
        weight = {v: seed.expovariate(1) for v in G}
    # If no positions are provided, choose uniformly random vectors in
    # Euclidean space of the specified dimension.
    if pos is None:
        pos = {v: [seed.random() for i in range(dim)] for v in G}
    # If no distance metric is provided, use Euclidean distance.
    if metric is None:
        metric = math.dist
    nx.set_node_attributes(G, weight, "weight")
    nx.set_node_attributes(G, pos, "pos")

    # if p_dist is not supplied, use default r^-2
    if p_dist is None:

        def p_dist(r):
            return r**-2

    # Returns ``True`` if and only if the nodes whose attributes are
    # ``du`` and ``dv`` should be joined, according to the threshold
    # condition.
    def should_join(pair):
        u, v = pair
        u_pos, v_pos = pos[u], pos[v]
        u_weight, v_weight = weight[u], weight[v]
        return (u_weight + v_weight) * p_dist(metric(u_pos, v_pos)) >= theta

    G.add_edges_from(filter(should_join, combinations(G, 2)))
    return G


@py_random_state(6)
def waxman_graph(
    n, beta=0.4, alpha=0.1, L=None, domain=(0, 0, 1, 1), metric=None, seed=None
):
    r"""Returns a Waxman random graph.

    The Waxman random graph model places `n` nodes uniformly at random
    in a rectangular domain. Each pair of nodes at distance `d` is
    joined by an edge with probability

    .. math::
            p = \beta \exp(-d / \alpha L).

    This function implements both Waxman models, using the `L` keyword
    argument.

    * Waxman-1: if `L` is not specified, it is set to be the maximum distance
      between any pair of nodes.
    * Waxman-2: if `L` is specified, the distance between a pair of nodes is
      chosen uniformly at random from the interval `[0, L]`.

    Parameters
    ----------
    n : int or iterable
        Number of nodes or iterable of nodes
    beta: float
        Model parameter
    alpha: float
        Model parameter
    L : float, optional
        Maximum distance between nodes.  If not specified, the actual distance
        is calculated.
    domain : four-tuple of numbers, optional
        Domain size, given as a tuple of the form `(x_min, y_min, x_max,
        y_max)`.
    metric : function
        A metric on vectors of numbers (represented as lists or
        tuples). This must be a function that accepts two lists (or
        tuples) as input and yields a number as output. The function
        must also satisfy the four requirements of a `metric`_.
        Specifically, if $d$ is the function and $x$, $y$,
        and $z$ are vectors in the graph, then $d$ must satisfy

        1. $d(x, y) \ge 0$,
        2. $d(x, y) = 0$ if and only if $x = y$,
        3. $d(x, y) = d(y, x)$,
        4. $d(x, z) \le d(x, y) + d(y, z)$.

        If this argument is not specified, the Euclidean distance metric is
        used.

        .. _metric: https://en.wikipedia.org/wiki/Metric_%28mathematics%29

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    Graph
        A random Waxman graph, undirected and without self-loops. Each
        node has a node attribute ``'pos'`` that stores the position of
        that node in Euclidean space as generated by this function.

    Examples
    --------
    Specify an alternate distance metric using the ``metric`` keyword
    argument. For example, to use the "`taxicab metric`_" instead of the
    default `Euclidean metric`_::

        >>> dist = lambda x, y: sum(abs(a - b) for a, b in zip(x, y))
        >>> G = nx.waxman_graph(10, 0.5, 0.1, metric=dist)

    .. _taxicab metric: https://en.wikipedia.org/wiki/Taxicab_geometry
    .. _Euclidean metric: https://en.wikipedia.org/wiki/Euclidean_distance

    Notes
    -----
    Starting in NetworkX 2.0 the parameters alpha and beta align with their
    usual roles in the probability distribution. In earlier versions their
    positions in the expression were reversed. Their position in the calling
    sequence reversed as well to minimize backward incompatibility.

    References
    ----------
    .. [1]  B. M. Waxman, *Routing of multipoint connections*.
       IEEE J. Select. Areas Commun. 6(9),(1988) 1617--1622.
    """
    G = nx.empty_graph(n)
    (xmin, ymin, xmax, ymax) = domain
    # Each node gets a uniformly random position in the given rectangle.
    pos = {v: (seed.uniform(xmin, xmax), seed.uniform(ymin, ymax)) for v in G}
    nx.set_node_attributes(G, pos, "pos")
    # If no distance metric is provided, use Euclidean distance.
    if metric is None:
        metric = math.dist
    # If the maximum distance L is not specified (that is, we are in the
    # Waxman-1 model), then find the maximum distance between any pair
    # of nodes.
    #
    # In the Waxman-1 model, join nodes randomly based on distance. In
    # the Waxman-2 model, join randomly based on random l.
    if L is None:
        L = max(metric(x, y) for x, y in combinations(pos.values(), 2))

        def dist(u, v):
            return metric(pos[u], pos[v])

    else:

        def dist(u, v):
            return seed.random() * L

    # `pair` is the pair of nodes to decide whether to join.
    def should_join(pair):
        return seed.random() < beta * math.exp(-dist(*pair) / (alpha * L))

    G.add_edges_from(filter(should_join, combinations(G, 2)))
    return G


@py_random_state(5)
def navigable_small_world_graph(n, p=1, q=1, r=2, dim=2, seed=None):
    r"""Returns a navigable small-world graph.

    A navigable small-world graph is a directed grid with additional long-range
    connections that are chosen randomly.

      [...] we begin with a set of nodes [...] that are identified with the set
      of lattice points in an $n \times n$ square,
      $\{(i, j): i \in \{1, 2, \ldots, n\}, j \in \{1, 2, \ldots, n\}\}$,
      and we define the *lattice distance* between two nodes $(i, j)$ and
      $(k, l)$ to be the number of "lattice steps" separating them:
      $d((i, j), (k, l)) = |k - i| + |l - j|$.

      For a universal constant $p >= 1$, the node $u$ has a directed edge to
      every other node within lattice distance $p$---these are its *local
      contacts*. For universal constants $q >= 0$ and $r >= 0$ we also
      construct directed edges from $u$ to $q$ other nodes (the *long-range
      contacts*) using independent random trials; the $i$th directed edge from
      $u$ has endpoint $v$ with probability proportional to $[d(u,v)]^{-r}$.

      -- [1]_

    Parameters
    ----------
    n : int
        The length of one side of the lattice; the number of nodes in
        the graph is therefore $n^2$.
    p : int
        The diameter of short range connections. Each node is joined with every
        other node within this lattice distance.
    q : int
        The number of long-range connections for each node.
    r : float
        Exponent for decaying probability of connections.  The probability of
        connecting to a node at lattice distance $d$ is $1/d^r$.
    dim : int
        Dimension of grid
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    References
    ----------
    .. [1] J. Kleinberg. The small-world phenomenon: An algorithmic
       perspective. Proc. 32nd ACM Symposium on Theory of Computing, 2000.
    """
    if p < 1:
        raise nx.NetworkXException("p must be >= 1")
    if q < 0:
        raise nx.NetworkXException("q must be >= 0")
    if r < 0:
        raise nx.NetworkXException("r must be >= 1")

    G = nx.DiGraph()
    nodes = list(product(range(n), repeat=dim))
    for p1 in nodes:
        probs = [0]
        for p2 in nodes:
            if p1 == p2:
                continue
            d = sum((abs(b - a) for a, b in zip(p1, p2)))
            if d <= p:
                G.add_edge(p1, p2)
            probs.append(d**-r)
        cdf = list(accumulate(probs))
        for _ in range(q):
            target = nodes[bisect_left(cdf, seed.uniform(0, cdf[-1]))]
            G.add_edge(p1, target)
    return G


@py_random_state(7)
def thresholded_random_geometric_graph(
    n, radius, theta, dim=2, pos=None, weight=None, p=2, seed=None
):
    r"""Returns a thresholded random geometric graph in the unit cube.

    The thresholded random geometric graph [1] model places `n` nodes
    uniformly at random in the unit cube of dimensions `dim`. Each node
    `u` is assigned a weight :math:`w_u`. Two nodes `u` and `v` are
    joined by an edge if they are within the maximum connection distance,
    `radius` computed by the `p`-Minkowski distance and the summation of
    weights :math:`w_u` + :math:`w_v` is greater than or equal
    to the threshold parameter `theta`.

    Edges within `radius` of each other are determined using a KDTree when
    SciPy is available. This reduces the time complexity from :math:`O(n^2)`
    to :math:`O(n)`.

    Parameters
    ----------
    n : int or iterable
        Number of nodes or iterable of nodes
    radius: float
        Distance threshold value
    theta: float
        Threshold value
    dim : int, optional
        Dimension of graph
    pos : dict, optional
        A dictionary keyed by node with node positions as values.
    weight : dict, optional
        Node weights as a dictionary of numbers keyed by node.
    p : float, optional (default 2)
        Which Minkowski distance metric to use.  `p` has to meet the condition
        ``1 <= p <= infinity``.

        If this argument is not specified, the :math:`L^2` metric
        (the Euclidean distance metric), p = 2 is used.

        This should not be confused with the `p` of an Erdős-Rényi random
        graph, which represents probability.
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    Graph
        A thresholded random geographic graph, undirected and without
        self-loops.

        Each node has a node attribute ``'pos'`` that stores the
        position of that node in Euclidean space as provided by the
        ``pos`` keyword argument or, if ``pos`` was not provided, as
        generated by this function. Similarly, each node has a nodethre
        attribute ``'weight'`` that stores the weight of that node as
        provided or as generated.

    Examples
    --------
    Default Graph:

    G = nx.thresholded_random_geometric_graph(50, 0.2, 0.1)

    Custom Graph:

    Create a thresholded random geometric graph on 50 uniformly distributed
    nodes where nodes are joined by an edge if their sum weights drawn from
    a exponential distribution with rate = 5 are >= theta = 0.1 and their
    Euclidean distance is at most 0.2.

    Notes
    -----
    This uses a *k*-d tree to build the graph.

    The `pos` keyword argument can be used to specify node positions so you
    can create an arbitrary distribution and domain for positions.

    For example, to use a 2D Gaussian distribution of node positions with mean
    (0, 0) and standard deviation 2

    If weights are not specified they are assigned to nodes by drawing randomly
    from the exponential distribution with rate parameter :math:`\lambda=1`.
    To specify weights from a different distribution, use the `weight` keyword
    argument::

    ::

    >>> import random
    >>> import math
    >>> n = 50
    >>> pos = {i: (random.gauss(0, 2), random.gauss(0, 2)) for i in range(n)}
    >>> w = {i: random.expovariate(5.0) for i in range(n)}
    >>> G = nx.thresholded_random_geometric_graph(n, 0.2, 0.1, 2, pos, w)

    References
    ----------
    .. [1] http://cole-maclean.github.io/blog/files/thesis.pdf

    """
    G = nx.empty_graph(n)
    G.name = f"thresholded_random_geometric_graph({n}, {radius}, {theta}, {dim})"
    # If no weights are provided, choose them from an exponential
    # distribution.
    if weight is None:
        weight = {v: seed.expovariate(1) for v in G}
    # If no positions are provided, choose uniformly random vectors in
    # Euclidean space of the specified dimension.
    if pos is None:
        pos = {v: [seed.random() for i in range(dim)] for v in G}
    # If no distance metric is provided, use Euclidean distance.
    nx.set_node_attributes(G, weight, "weight")
    nx.set_node_attributes(G, pos, "pos")

    edges = (
        (u, v)
        for u, v in _geometric_edges(G, radius, p)
        if weight[u] + weight[v] >= theta
    )
    G.add_edges_from(edges)
    return G


@py_random_state(5)
def S1_graph(beta, *, n=None, gamma=None, mean_degree=None, kappas=None, seed=None):
    r"""Returns a $\mathbb{S}^1$ model.

    The $\mathbb{S}^1$ model is the simplest among the class of geometric models [1]_.
    The similarity space is a one dimensional sphere—a circle of radius R—where N nodes are
    distributed with a fixed density, set to one without loss of generality, so that $N = 2\pi R$.
    Each node is also given a hidden variable ``kappa`` proportional to its expected degree.
    The connection probability between a node i and a node j takes the form of a gravity law

    $p_{ij} = \frac{1}{1 + \frac{d_{ij}^\beta}{\left(\mu \kappa_i \kappa_j\right)^{\max(1, \beta)}}}$

    where $d_{ij} = R\Delta\theta_{ij}$ is the arc length of the circle between
    nodes i and j separated by an angular distance $\Delta\theta_{ij}$. Parameters $\mu$ and $\beta$
    control the average degree and the clustering coefficient, respectively.

    Parameters
    ----------
    beta: float
        Inverse temperature
    n: int, optional
        Size of the network
    gamma: float, optional
        Exponent of powerlaw distribution of the hidden degrees
    mean_degree: float, optional
        The mean degree in the network
    kappas: list, optional
        Values of hidden degrees for each node
    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    Graph
        A $\mathbb{S}^1$ model, undirected and without self-loops.
        Each node has two attributes: ``kappa`` that represents the
        hidden degree and ``theta`` the position in the similarity space.

    Examples
    --------
    Default Graph:

    >>> G = nx.S1_graph(1.5, n=100, gamma=2.7, mean_degree=5)

    Create a $\mathbb{S}^1$ model with 100 nodes. The $\beta$ parameter is set to 1.5
    and the exponent of the powerlaw distribution of the hidden degrees is 2.7
    with mean value of 5.


    Custom Graph:

    >>> kappas = [10] * 100
    >>> G = nx.S1_graph(2.5, kappas=kappas)

    Create a $\mathbb{S}^1$ model with 100 nodes. The $\beta$ parameter is set to 2.5
    and every node has the same $\kappa=10$ value.


    Notes
    -----
    If the ``kappas`` parameter is provided then parameters ``n``, ``gamma``
    and ``mean_degree`` are ignored.


    References
    ----------
    .. [1] Serrano, M. Angeles, Dmitri, Krioukov, and Marián, Boguñá. "Self-Similarity
    of Complex Networks and Hidden Metric Spaces". Phys. Rev. Lett. 100 (2008): 078701.
    """
    if beta < 0:
        raise nx.NetworkXError("The inverse temperature cannot be smaller than 0.")

    if kappas is not None:
        if not all((n is None, gamma is None, mean_degree is None)):
            raise nx.NetworkXError(
                "When kappas is set other parameters should be empty."
            )

        n = len(kappas)
        mean_degree = sum(kappas) / len(kappas)
    else:
        if any((n is None, gamma is None, mean_degree is None)):
            raise nx.NetworkXError(
                "Please provide all parameters: n, gamma and mean_degree."
            )

        # Generate hidden degrees from the powerlaw distribution with given exponent `gamma`
        #  and mean value `mean_degree`
        kappa_0 = (
            (1 - 1 / n)
            / (1 - n ** ((2 - gamma) / (gamma - 1)))
            * (gamma - 2)
            / (gamma - 1)
            * mean_degree
        )
        kappa_c = kappa_0 * n ** (1 / (gamma - 1))

        kappas = []
        for _ in range(n):
            kappas.append(
                kappa_0
                * (1 - seed.uniform(0, 1) * (1 - (kappa_c / kappa_0) ** (1 - gamma)))
                ** (1 / (1 - gamma))
            )

    G = nx.empty_graph(n)
    R = n / (2 * math.pi)

    # Approximate values for mu in the thermodynamic limit (when n -> infinity)
    if beta > 1:
        mu = beta * math.sin(math.pi / beta) / (2 * math.pi * mean_degree)
    elif beta == 1:
        mu = 1 / (2 * mean_degree * math.log(n))
    else:
        mu = (1 - beta) / (2**beta * mean_degree * n ** (1 - beta))

    # Generate random positions on a circle
    thetas = [seed.uniform(0, 2 * math.pi) for _ in range(n)]

    for i in range(n):
        for j in range(i):
            angle = math.pi - math.fabs(math.pi - math.fabs(thetas[i] - thetas[j]))
            dij = math.pow(R * angle, beta)
            mu_kappas = math.pow(mu * kappas[i] * kappas[j], max(1, beta))
            p_ij = 1 / (1 + dij / mu_kappas)

            # Create an edge with a certain connection probability
            if seed.random() < p_ij:
                G.add_edge(i, j)

    nx.set_node_attributes(G, dict(zip(range(n), thetas)), "theta")
    nx.set_node_attributes(G, dict(zip(range(n), kappas)), "kappa")
    return G
