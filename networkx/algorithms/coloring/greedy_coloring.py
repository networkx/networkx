"""
Greedy graph coloring using various strategies.
"""
import itertools
from collections import defaultdict, deque
from queue import PriorityQueue

import networkx as nx
from networkx.utils import arbitrary_element, py_random_state

__all__ = [
    "greedy_color",
    "strategy_connected_sequential",
    "strategy_connected_sequential_bfs",
    "strategy_connected_sequential_dfs",
    "strategy_independent_set",
    "strategy_largest_first",
    "strategy_random_sequential",
    "strategy_saturation_largest_first",
    "strategy_smallest_last",
    "strategy_rlf",
]


def strategy_largest_first(G, colors):
    """Returns a list of the nodes of ``G`` in decreasing order by
    degree.

    ``G`` is a NetworkX graph. ``colors`` is ignored.

    """
    return sorted(G, key=G.degree, reverse=True)


@py_random_state(2)
def strategy_random_sequential(G, colors, seed=None):
    """Returns a random permutation of the nodes of ``G`` as a list.

    ``G`` is a NetworkX graph. ``colors`` is ignored.

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.
    """
    nodes = list(G)
    seed.shuffle(nodes)
    return nodes


def strategy_smallest_last(G, colors):
    """Returns a deque of the nodes of ``G``, "smallest" last.

    Specifically, the degrees of each node are tracked in a bucket queue.
    From this, the node of minimum degree is repeatedly popped from the
    graph, updating its neighbors' degrees.

    ``G`` is a NetworkX graph. ``colors`` is ignored.

    This implementation of the strategy runs in $O(n + m)$ time
    (ignoring polylogarithmic factors), where $n$ is the number of nodes
    and $m$ is the number of edges.

    This strategy is related to :func:`strategy_independent_set`: if we
    interpret each node removed as an independent set of size one, then
    this strategy chooses an independent set of size one instead of a
    maximal independent set.

    """
    H = G.copy()
    result = deque()

    # Build initial degree list (i.e. the bucket queue data structure)
    degrees = defaultdict(set)  # set(), for fast random-access removals
    lbound = float("inf")
    for node, d in H.degree():
        degrees[d].add(node)
        lbound = min(lbound, d)  # Lower bound on min-degree.

    def find_min_degree():
        # Save time by starting the iterator at `lbound`, not 0.
        # The value that we find will be our new `lbound`, which we set later.
        return next(d for d in itertools.count(lbound) if d in degrees)

    for _ in G:
        # Pop a min-degree node and add it to the list.
        min_degree = find_min_degree()
        u = degrees[min_degree].pop()
        if not degrees[min_degree]:  # Clean up the degree list.
            del degrees[min_degree]
        result.appendleft(u)

        # Update degrees of removed node's neighbors.
        for v in H[u]:
            degree = H.degree(v)
            degrees[degree].remove(v)
            if not degrees[degree]:  # Clean up the degree list.
                del degrees[degree]
            degrees[degree - 1].add(v)

        # Finally, remove the node.
        H.remove_node(u)
        lbound = min_degree - 1  # Subtract 1 in case of tied neighbors.

    return result


def _maximal_independent_set(G):
    """Returns a maximal independent set of nodes in ``G`` by repeatedly
    choosing an independent node of minimum degree (with respect to the
    subgraph of unchosen nodes).

    """
    result = set()
    remaining = set(G)
    while remaining:
        G = G.subgraph(remaining)
        v = min(remaining, key=G.degree)
        result.add(v)
        remaining -= set(G[v]) | {v}
    return result


def strategy_independent_set(G, colors):
    """Uses a greedy independent set removal strategy to determine the
    colors.

    This function updates ``colors`` **in-place** and return ``None``,
    unlike the other strategy functions in this module.

    This algorithm repeatedly finds and removes a maximal independent
    set, assigning each node in the set an unused color.

    ``G`` is a NetworkX graph.

    This strategy is related to :func:`strategy_smallest_last`: in that
    strategy, an independent set of size one is chosen at each step
    instead of a maximal independent set.

    """
    remaining_nodes = set(G)
    while len(remaining_nodes) > 0:
        nodes = _maximal_independent_set(G.subgraph(remaining_nodes))
        remaining_nodes -= nodes
        yield from nodes


def strategy_connected_sequential_bfs(G, colors):
    """Returns an iterable over nodes in ``G`` in the order given by a
    breadth-first traversal.

    The generated sequence has the property that for each node except
    the first, at least one neighbor appeared earlier in the sequence.

    ``G`` is a NetworkX graph. ``colors`` is ignored.

    """
    return strategy_connected_sequential(G, colors, "bfs")


def strategy_connected_sequential_dfs(G, colors):
    """Returns an iterable over nodes in ``G`` in the order given by a
    depth-first traversal.

    The generated sequence has the property that for each node except
    the first, at least one neighbor appeared earlier in the sequence.

    ``G`` is a NetworkX graph. ``colors`` is ignored.

    """
    return strategy_connected_sequential(G, colors, "dfs")


def strategy_connected_sequential(G, colors, traversal="bfs"):
    """Returns an iterable over nodes in ``G`` in the order given by a
    breadth-first or depth-first traversal.

    ``traversal`` must be one of the strings ``'dfs'`` or ``'bfs'``,
    representing depth-first traversal or breadth-first traversal,
    respectively.

    The generated sequence has the property that for each node except
    the first, at least one neighbor appeared earlier in the sequence.

    ``G`` is a NetworkX graph. ``colors`` is ignored.

    """
    if traversal == "bfs":
        traverse = nx.bfs_edges
    elif traversal == "dfs":
        traverse = nx.dfs_edges
    else:
        raise nx.NetworkXError(
            "Please specify one of the strings 'bfs' or"
            " 'dfs' for connected sequential ordering"
        )
    for component in nx.connected_components(G):
        source = arbitrary_element(component)
        # Yield the source node, then all the nodes in the specified
        # traversal order.
        yield source
        for _, end in traverse(G.subgraph(component), source):
            yield end


def strategy_saturation_largest_first(G, colors):
    """Returns an iterable over the nodes in ``G`` in the order they would
    be colored using their "saturation order" (also known as the Dsatur
    algorithm).

    Parameters
    ----------
    ``G`` is a NetworkX graph. ``colors`` is ignored.

    Notes
    -----
    If ``G`` is a cycle graph, a wheel graph, or a bipartite graph, the
    generated sequence, when used with the greedy coloring algorithm, results
    in a solution that uses the minimal number of colors  (that is, the
    algorithm is **exact** for such graphs).

    This implementation of the DSatur algorithm has a complexity of
    $O(n lg n + m lg m)$. See [1]_ for further details.

    References
    ----------
    .. [1] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
        Applications, 2nd Ed. Springer, ISBN: 978-3-030-81053-5.
        <https://link.springer.com/book/10.1007/978-3-030-81054-2>

    """
    # First initialise the data structures. These are:
    # the colors of each vertex c[v]; the degree d[v] of each
    # uncolored vertex in the graph induced by uncolored nodes; the set of
    # colors adjacent to each uncolored vertex (initially empty sets); and
    # a priority queue q;
    c, d, adjcols, q = {}, {}, {}, PriorityQueue()
    for u in G.nodes:
        d[u] = G.degree(u)
        adjcols[u] = set()
        q.put((0, d[u] * (-1), u))
    while len(c) < len(G):
        # Get the uncolored vertex u with max saturation degree, breaking
        # ties using the highest value for d. Remove u from q.
        _, _, u = q.get()
        if u not in c:
            yield u
            # Get lowest color label i for uncolored vertex u
            for i in itertools.count():
                if i not in adjcols[u]:
                    break
            c[u] = i
            # Update the data structures
            for v in G[u]:
                if v not in c:
                    adjcols[v].add(i)
                    d[v] -= 1
                    q.put((len(adjcols[v]) * (-1), d[v] * (-1), v))


def strategy_rlf(G, colors):
    """Returns an iterable over the nodes in ``G`` in the order they would
    be colored using the "recursive largest first" (RLF) algorithm.

    Parameters
    ----------
    ``G`` is a NetworkX graph. ``colors`` is ignored.

    Notes
    -----
    If ``G`` is a cycle graph, a wheel graph, or a bipartite graph, the
    generated sequence, when used with the greedy coloring algorithm, results
    in a solution that uses the minimal number of colors  (that is, the
    algorithm is **exact** for such graphs).

    This implementation of the RLF algorithm has a complexity of $O(nm)$.
    See [1]_ for further details.

    References
    ----------
    .. [1] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
        Applications, 2nd Ed. Springer, ISBN: 978-3-030-81053-5.
        <https://link.springer.com/book/10.1007/978-3-030-81054-2>

    """

    def update_rlf(u):
        # Remove u from X (it has been colored) and move all uncolored
        # neighbors of u from X to Y
        X.remove(u)
        for v in G[u]:
            if v not in c:
                X.discard(v)
                Y.add(v)
        # Recalculate the contets of NInX and NInY. First calculate a set D2
        # of all uncolored nodes within distance two of u.
        D2 = set()
        for v in G[u]:
            if v not in c:
                D2.add(v)
                for w in G[v]:
                    if w not in c:
                        D2.add(w)
        # For each vertex v in D2, recalculate the number of (uncolored)
        # neighbors in X and Y
        for v in D2:
            NInX[v] = 0
            NInY[v] = 0
            for w in G[v]:
                if w not in c:
                    if w in X:
                        NInX[v] += 1
                    elif w in Y:
                        NInY[v] += 1

    # Main algorithm. Here, X is the set of uncolored vertices not adjacent
    # to any vertices colored with color i, and Y is the set of uncolored
    # vertices that are adjcent to vertices colored with i.
    c, Y, n, i = {}, set(), len(G), 0
    X = set(G.nodes())
    while X:
        # Construct color class i. First, for each vertex u in X, calculate the
        # number of neighbors it has in X and Y
        NInX, NInY = {u: 0 for u in X}, {u: 0 for u in X}
        for u in X:
            for v in G[u]:
                if v in X:
                    NInX[u] += 1
        # Identify and colur the uncolored vertex u in X that has the most
        # neighbors in X
        maxVal = -1
        for v in X:
            if NInX[v] > maxVal:
                maxVal, u = NInX[v], v
        yield u
        c[u] = i
        update_rlf(u)
        while X:
            # Identify and color the vertex u in X that has the largest
            # number of neighbors in Y. Break ties according to the min
            # neighbors in X
            maxVal, minVal = -1, n
            for v in X:
                if NInY[v] > maxVal or (NInY[v] == maxVal and NInX[v] < minVal):
                    maxVal, minVal, u = NInY[v], NInX[v], v
            yield u
            c[u] = i
            update_rlf(u)
        # Have finished constructing color class i
        X, Y = Y, X
        i += 1


@py_random_state(2)
def tabusearch(G, inputtuple, seed=None):
    """Applies a tabu search algorithm that attempts to reduce the number of
    colors being used to color the vertices of ``G`` (see [1]_).

    Parameters
    ----------
    G : NetworkX graph

    inputtuple : a tuple containing two items

        inputtuple[0] : dict()
            This defines a proper $k$-coloring of the vertices of ``G``
            using color labels $0,1,...,k-1$. This coloring is expressed as a
            dictionary, with keys representing nodes and values representing
            the colors. Adjacent vertices must have different colors.

        inputtuple[1] : integer
            Specifies the maximum number of iterations to perform. Each iteration
            has complexity $O(kn+m)$

    seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    A dictionary with keys representing nodes and values representing
    their colors.

    References
    ----------
    .. [1] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
        Applications, 2nd Ed. Springer, ISBN: 978-3-030-81053-5.
        <https://link.springer.com/book/10.1007/978-3-030-81054-2>

    """

    #
    # The tabusearch implementation used here is based on the C++ implementation
    # of PartialCol available at <www.rhydlewis.eu/gcol>. Both versions
    # were programmed by the author of [1] above.
    #
    def partialcol():
        def domove(vpos, j):
            # Used by partialcol to move vertex v (at U[vPos]) to color j and
            # update the data structures C, T and U
            v = U[vpos]
            c[v] = j
            U[vpos] = U[-1]
            U.pop()
            for u in G[v]:
                C[u, j] += 1
                if c[u] == j:
                    T[u, j] = tabuits + t
                    U.append(u)
                    c[u] = -1
                    for w in G[u]:
                        C[w, j] -= 1

        # First populate the data structures.
        # C[v, j] gives the number of neighbors of v in color j,
        # T is the tabu list, and U is the list of uncolored nodes.
        # "its" is the overall iterations counter from the enclosing fuction
        C, T, U = {}, {}, []
        nonlocal its
        for v in G:
            for j in range(k):
                C[v, j] = 0
                T[v, j] = 0
        for v in G:
            if c[v] == -1:
                U.append(v)
            for u in G[v]:
                if c[u] != -1:
                    C[v, c[u]] += 1
        if len(U) == 0:
            return 0
        globalbest, tabuits, t = len(U), 0, 0
        while its < maxits:
            its += 1
            tabuits += 1
            vposbest, jbest, bestval, numbestval = -1, -1, len(G), 0
            # Evaluate effect of assigning each uncolored node v to each color j
            for vpos in range(len(U)):
                v = U[vpos]
                for j in range(k):
                    if C[v, j] <= bestval:
                        if C[v, j] < bestval:
                            numbestval = 0
                        # Consider the move if it is non-tabu or leads to a new global best
                        if T[v, j] < tabuits or (C[v, j] == 0 and len(U) == globalbest):
                            # Choose between the observed best moves and stores
                            if seed.randint(0, numbestval) == 0:
                                vposbest, jbest, bestval = vpos, j, C[v, j]
                            numbestval += 1
            if vposbest == -1:
                # No non-tabu moves were found, so select a random move
                vposbest = seed.randint(0, len(U) - 1)
                jbest = seed.randint(0, k - 1)
            # Apply the move, update T, and determine the next tabu tenure t
            domove(vposbest, jbest)
            t = int(0.6 * len(U)) + seed.randint(0, 9)
            if len(U) < globalbest:
                globalbest = len(U)
            if globalbest == 0:
                break
        return globalbest

    # Main tabu search algorithm (assumes colors being used are 0,...,k-1)
    c = inputtuple[0]
    maxits = inputtuple[1]
    k, bestc, its = max(c.values()) + 1, dict(c), 0
    # Decrement k and try to find a k coloring for this lower value of k
    k -= 1
    while its < maxits and k > 2:
        # Select a random color class j and mark its nodes as uncolored
        # (maintaining the use of colors 0,...,k-1)
        j = seed.randint(0, k - 1)
        for v in c:
            if c[v] == j:
                c[v] = -1
            elif c[v] == k:
                c[v] = j
        # Run partialcol using k colors until all nodes are colored or
        # maxits is exceeded
        cost = partialcol()
        if cost == 0:
            bestc = dict(c)
        k -= 1
    return bestc


#: Dictionary mapping name of a strategy as a string to the strategy function.
STRATEGIES = {
    "largest_first": strategy_largest_first,
    "random_sequential": strategy_random_sequential,
    "smallest_last": strategy_smallest_last,
    "independent_set": strategy_independent_set,
    "connected_sequential_bfs": strategy_connected_sequential_bfs,
    "connected_sequential_dfs": strategy_connected_sequential_dfs,
    "connected_sequential": strategy_connected_sequential,
    "saturation_largest_first": strategy_saturation_largest_first,
    "DSATUR": strategy_saturation_largest_first,
    "rlf": strategy_rlf,
}


@nx._dispatchable
def greedy_color(G, strategy="largest_first", interchange=False, tabu=0):
    """Colors the nodes of a graph using a greedy graph coloring algorithm
    and, optionally, a subsequent optimisation algorithm based on tabu search.
    The method assigns a color to each vertex such that neighbouring
    vertices always have different colors. The aim is to construct a coloring
    that uses as few different colors as possible.

    The given ``strategy`` determines the order that nodes are to be colored
    by the $O(n+m)$ "greedy algorithm" for graph coloring. If the ``interchange``
    operator is used, this ordering is adjusted before the application of the
    greedy algorithm in an attempt to reduce the resultant number of colors.
    Note that ``interchange`` cannot be used with the strategies
    ``'saturation_largest_first'``, ``'DSATUR'`` or ``'rlf'``.

    If the strategies ``'saturation_largest_first'``, ``'DSATUR'`` or ``'rlf'``
    are used, the algorithm is exact for bipartite, cycle, and wheel graphs
    (that is, solutions with the minimum number of colors are guaranteed).

    On production of a solution via the greedy algorithm, an optional optimization
    process can also be employed that seeks to further reduce the number of colors
    being used. This algorithm is based on tabu search.

    The greedy strategies are described in more detail in [1]_, [2]_, [3]_, and [4]_.
    The tabu search algorithm is described in [4]_.

    Parameters
    ----------
    G : NetworkX graph

    strategy : string or function(G, colors), optional (default='largest_first')
       A function (or string representing a function) that provides
       an ordering of the vertices that is then passed to the
       greedy algorithm. ``G`` is the graph. The function must
       return an iterable over all nodes in ``G``.

       If ``strategy`` is a string, it must be one of the following,
       each of which represents one of the built-in strategy functions.

       * ``'largest_first'``
       * ``'random_sequential'``
       * ``'smallest_last'``
       * ``'independent_set'``
       * ``'connected_sequential_bfs'``
       * ``'connected_sequential_dfs'``
       * ``'connected_sequential'`` (alias for the previous strategy)
       * ``'saturation_largest_first'``
       * ``'DSATUR'`` (alias for the previous strategy)
       * ``'rlf'``

    interchange: bool
       Will use the color interchange algorithm described by [3]_ if set
       to ``True``.

       Note that ``saturation_largest_first``, ``independent_set``, and ``rlf``
       do not work with interchange.

    tabu : integer, optional (default=0)
       Runs a tabu search algorithm for the specified number of iterations.
       The algorithm takes a proper coloring formed by the chosen strategy
       above and attempts to reduce the number of colors being used.
       The method is based on an iterated version of PartialCol, described in
       [4]_. Given a proper $k$-coloring, the algorithm first "uncolors"
       all vertices in a randomly chosen color class. The PartialCol
       algorithm (based on tabu search) is then executed, which attempts to
       reduce the cardinality of the set of uncolored vertices.
       If this cardinality is reduced to zero, $k$ is decremented
       by one, and the process is repeated. The algorithm terminates once the
       iteration limit is exceeded. Fewer colors (but longer run times)
       occur with larger iteration limits. Given a graph with $n$ vertices,
       $m$ edges, and $k$ colors, each iteration of PartialCol has complexity
       $O(nk + m)$. The process also uses $O(nk + m)$ memory.

    Returns
    -------
    A dictionary with keys representing nodes and values representing the
    corresponding coloring.

    Examples
    --------
    >>> G = nx.cycle_graph(4)
    >>> d = nx.coloring.greedy_color(G, strategy="largest_first")
    >>> d in [{0: 0, 1: 1, 2: 0, 3: 1}, {0: 1, 1: 0, 2: 1, 3: 0}]
    True

    Notes
    -----
    In general, the use of ``strategy='rlf'`` yields solutions using fewer colors
    than the other methods, though it is computationally more expensive. If
    expense is an issue, then ``'saturation_largest_first'`` is a cheaper alternative
    that also offers high quality solutions in most cases.

    The subseuent use of tabu search usually allows solutions with fewer colors to
    be identified. Larger values for ``tabusearch`` yield better results but also
    longer run times.

    Further information on the relative performance of these algorithms can be found
    in [4]_.

    Raises
    ------
    NetworkXPointlessConcept
        If ``strategy`` is ``saturation_largest_first``, ``rlf``, or
        ``independent_set``, and ``interchange`` is ``True``.

    NetworkXError
        If an invalid string for ``strategy`` is used.

    References
    ----------
    .. [1] Adrian Kosowski, and Krzysztof Manuszewski,
       Classical Coloring of Graphs, Graph Colorings, 2-19, 2004.
       ISBN 0-8218-3458-4.
    .. [2] David W. Matula, and Leland L. Beck, "Smallest-last
       ordering and clustering and graph coloring algorithms." *J. ACM* 30,
       3 (July 1983), 417–427. <https://doi.org/10.1145/2402.322385>
    .. [3] Maciej M. Sysło, Narsingh Deo, Janusz S. Kowalik,
       Discrete Optimization Algorithms with Pascal Programs, 415-424, 1983.
       ISBN 0-486-45353-7.
    .. [4] Lewis, R. (2021) A Guide to Graph Colouring: Algorithms and
       Applications, 2nd Ed. Springer, ISBN: 978-3-030-81053-5
       <https://link.springer.com/book/10.1007/978-3-030-81054-2>

    """
    if len(G) == 0:
        return {}
    # Determine the strategy provided by the caller.
    strategy = STRATEGIES.get(strategy, strategy)
    if not callable(strategy):
        raise nx.NetworkXError(
            f"strategy must be callable or a valid string. {strategy} not valid."
        )
    # Perform some validation on the arguments before executing any
    # strategy functions.
    if interchange:
        if strategy is strategy_independent_set:
            msg = "interchange cannot be used with independent_set"
            raise nx.NetworkXPointlessConcept(msg)
        if strategy is strategy_saturation_largest_first:
            msg = "interchange cannot be used with" " saturation_largest_first"
            raise nx.NetworkXPointlessConcept(msg)
        if strategy is strategy_rlf:
            msg = "interchange cannot be used with rlf"
            raise nx.NetworkXPointlessConcept(msg)
    colors = {}
    nodes = strategy(G, colors)
    if interchange:
        return _greedy_coloring_with_interchange(G, nodes)
    for u in nodes:
        # Set to keep track of colors of neighbors
        nbr_colors = {colors[v] for v in G[u] if v in colors}
        # Find the first unused color.
        for color in itertools.count():
            if color not in nbr_colors:
                break
        # Assign the new color to the current node.
        colors[u] = color
    # If tabu > 0, try to reduce the number of colors being used using tabu search
    if tabu > 0:
        colors = tabusearch(G, (colors, tabu))
    return colors


# Tools for coloring with interchanges
class _Node:
    __slots__ = ["node_id", "color", "adj_list", "adj_color"]

    def __init__(self, node_id, n):
        self.node_id = node_id
        self.color = -1
        self.adj_list = None
        self.adj_color = [None for _ in range(n)]

    def __repr__(self):
        return (
            f"Node_id: {self.node_id}, Color: {self.color}, "
            f"Adj_list: ({self.adj_list}), adj_color: ({self.adj_color})"
        )

    def assign_color(self, adj_entry, color):
        adj_entry.col_prev = None
        adj_entry.col_next = self.adj_color[color]
        self.adj_color[color] = adj_entry
        if adj_entry.col_next is not None:
            adj_entry.col_next.col_prev = adj_entry

    def clear_color(self, adj_entry, color):
        if adj_entry.col_prev is None:
            self.adj_color[color] = adj_entry.col_next
        else:
            adj_entry.col_prev.col_next = adj_entry.col_next
        if adj_entry.col_next is not None:
            adj_entry.col_next.col_prev = adj_entry.col_prev

    def iter_neighbors(self):
        adj_node = self.adj_list
        while adj_node is not None:
            yield adj_node
            adj_node = adj_node.next

    def iter_neighbors_color(self, color):
        adj_color_node = self.adj_color[color]
        while adj_color_node is not None:
            yield adj_color_node.node_id
            adj_color_node = adj_color_node.col_next


class _AdjEntry:
    __slots__ = ["node_id", "next", "mate", "col_next", "col_prev"]

    def __init__(self, node_id):
        self.node_id = node_id
        self.next = None
        self.mate = None
        self.col_next = None
        self.col_prev = None

    def __repr__(self):
        col_next = None if self.col_next is None else self.col_next.node_id
        col_prev = None if self.col_prev is None else self.col_prev.node_id
        return (
            f"Node_id: {self.node_id}, Next: ({self.next}), "
            f"Mate: ({self.mate.node_id}), "
            f"col_next: ({col_next}), col_prev: ({col_prev})"
        )


def _greedy_coloring_with_interchange(G, nodes):
    """Return a coloring for `original_graph` using interchange approach

    This procedure is an adaption of the algorithm described by [1]_,
    and is an implementation of coloring with interchange. Please be
    advised, that the datastructures used are rather complex because
    they are optimized to minimize the time spent identifying
    subcomponents of the graph, which are possible candidates for color
    interchange.

    Parameters
    ----------
    G : NetworkX graph
        The graph to be colored

    nodes : list
        nodes ordered using the strategy of choice

    Returns
    -------
    dict :
        A dictionary keyed by node to a color value

    References
    ----------
    .. [1] Maciej M. Syslo, Narsingh Deo, Janusz S. Kowalik,
       Discrete Optimization Algorithms with Pascal Programs, 415-424, 1983.
       ISBN 0-486-45353-7.
    """
    n = len(G)

    graph = {node: _Node(node, n) for node in G}

    for node1, node2 in G.edges():
        adj_entry1 = _AdjEntry(node2)
        adj_entry2 = _AdjEntry(node1)
        adj_entry1.mate = adj_entry2
        adj_entry2.mate = adj_entry1
        node1_head = graph[node1].adj_list
        adj_entry1.next = node1_head
        graph[node1].adj_list = adj_entry1
        node2_head = graph[node2].adj_list
        adj_entry2.next = node2_head
        graph[node2].adj_list = adj_entry2

    k = 0
    for node in nodes:
        # Find the smallest possible, unused color
        neighbors = graph[node].iter_neighbors()
        col_used = {graph[adj_node.node_id].color for adj_node in neighbors}
        col_used.discard(-1)
        k1 = next(itertools.dropwhile(lambda x: x in col_used, itertools.count()))

        # k1 is now the lowest available color
        if k1 > k:
            connected = True
            visited = set()
            col1 = -1
            col2 = -1
            while connected and col1 < k:
                col1 += 1
                neighbor_cols = graph[node].iter_neighbors_color(col1)
                col1_adj = list(neighbor_cols)

                col2 = col1
                while connected and col2 < k:
                    col2 += 1
                    visited = set(col1_adj)
                    frontier = list(col1_adj)
                    i = 0
                    while i < len(frontier):
                        search_node = frontier[i]
                        i += 1
                        col_opp = col2 if graph[search_node].color == col1 else col1
                        neighbor_cols = graph[search_node].iter_neighbors_color(col_opp)

                        for neighbor in neighbor_cols:
                            if neighbor not in visited:
                                visited.add(neighbor)
                                frontier.append(neighbor)

                    # Search if node is not adj to any col2 vertex
                    connected = (
                        len(
                            visited.intersection(graph[node].iter_neighbors_color(col2))
                        )
                        > 0
                    )

            # If connected is false then we can swap !!!
            if not connected:
                # Update all the nodes in the component
                for search_node in visited:
                    graph[search_node].color = (
                        col2 if graph[search_node].color == col1 else col1
                    )
                    col2_adj = graph[search_node].adj_color[col2]
                    graph[search_node].adj_color[col2] = graph[search_node].adj_color[
                        col1
                    ]
                    graph[search_node].adj_color[col1] = col2_adj

                # Update all the neighboring nodes
                for search_node in visited:
                    col = graph[search_node].color
                    col_opp = col1 if col == col2 else col2
                    for adj_node in graph[search_node].iter_neighbors():
                        if graph[adj_node.node_id].color != col_opp:
                            # Direct reference to entry
                            adj_mate = adj_node.mate
                            graph[adj_node.node_id].clear_color(adj_mate, col_opp)
                            graph[adj_node.node_id].assign_color(adj_mate, col)
                k1 = col1

        # We can color this node color k1
        graph[node].color = k1
        k = max(k1, k)

        # Update the neighbors of this node
        for adj_node in graph[node].iter_neighbors():
            adj_mate = adj_node.mate
            graph[adj_node.node_id].assign_color(adj_mate, k1)

    return {node.node_id: node.color for node in graph.values()}
