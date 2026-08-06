from collections import defaultdict, deque
from heapq import heappop, heappush
from itertools import count

import networkx as nx
from networkx.algorithms.shortest_paths.weighted import _weight_function
from networkx.utils import not_implemented_for, pairwise

__all__ = [
    "all_simple_paths",
    "is_simple_path",
    "shortest_simple_paths",
    "all_simple_edge_paths",
]


@nx._dispatchable
def is_simple_path(G, nodes):
    """Returns True if and only if `nodes` form a simple path in `G`.

    A *simple path* in a graph is a nonempty sequence of nodes in which
    no node appears more than once in the sequence, and each adjacent
    pair of nodes in the sequence is adjacent in the graph.

    Parameters
    ----------
    G : graph
        A NetworkX graph.
    nodes : list
        A list of one or more nodes in the graph `G`.

    Returns
    -------
    bool
        Whether the given list of nodes represents a simple path in `G`.

    Notes
    -----
    An empty list of nodes is not a path but a list of one node is a
    path. Here's an explanation why.

    This function operates on *node paths*. One could also consider
    *edge paths*. There is a bijection between node paths and edge
    paths.

    The *length of a path* is the number of edges in the path, so a list
    of nodes of length *n* corresponds to a path of length *n* - 1.
    Thus the smallest edge path would be a list of zero edges, the empty
    path. This corresponds to a list of one node.

    To convert between a node path and an edge path, you can use code
    like the following::

        >>> from networkx.utils import pairwise
        >>> nodes = [0, 1, 2, 3]
        >>> edges = list(pairwise(nodes))
        >>> edges
        [(0, 1), (1, 2), (2, 3)]
        >>> nodes = [edges[0][0]] + [v for u, v in edges]
        >>> nodes
        [0, 1, 2, 3]

    Examples
    --------
    >>> G = nx.cycle_graph(4)
    >>> nx.is_simple_path(G, [2, 3, 0])
    True
    >>> nx.is_simple_path(G, [0, 2])
    False

    """
    # The empty list is not a valid path. Could also return
    # NetworkXPointlessConcept here.
    if len(nodes) == 0:
        return False

    # If the list is a single node, just check that the node is actually
    # in the graph.
    if len(nodes) == 1:
        return nodes[0] in G

    # check that all nodes in the list are in the graph, if at least one
    # is not in the graph, then this is not a simple path
    if not all(n in G for n in nodes):
        return False

    # If the list contains repeated nodes, then it's not a simple path
    if len(set(nodes)) != len(nodes):
        return False

    # Test that each adjacent pair of nodes is adjacent.
    return all(v in G[u] for u, v in pairwise(nodes))


@nx._dispatchable
def all_simple_paths(G, source, target, cutoff=None):
    """Generate all simple paths in the graph G from source to target.

    A simple path is a path with no repeated nodes.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : nodes
       Single node or iterable of nodes at which to end path

    cutoff : integer, optional
        Depth to stop the search. Only paths with length <= `cutoff` are returned.
        where the mathematical "length of a path" is `len(path) -1` (number of edges).

    Returns
    -------
    path_generator: generator
       A generator that produces lists of simple paths.  If there are no paths
       between the source and target within the given cutoff the generator
       produces no output. If it is possible to traverse the same sequence of
       nodes in multiple ways, namely through parallel edges, then it will be
       returned multiple times (once for each viable edge combination).

    Examples
    --------
    This iterator generates lists of nodes::

        >>> G = nx.complete_graph(4)
        >>> for path in nx.all_simple_paths(G, source=0, target=3):
        ...     print(path)
        ...
        [0, 1, 2, 3]
        [0, 1, 3]
        [0, 2, 1, 3]
        [0, 2, 3]
        [0, 3]

    You can generate only those paths that are shorter than a certain
    length by using the `cutoff` keyword argument::

        >>> paths = nx.all_simple_paths(G, source=0, target=3, cutoff=2)
        >>> print(list(paths))
        [[0, 1, 3], [0, 2, 3], [0, 3]]

    To get each path as the corresponding list of edges, you can use the
    :func:`networkx.utils.pairwise` helper function::

        >>> paths = nx.all_simple_paths(G, source=0, target=3)
        >>> for path in map(nx.utils.pairwise, paths):
        ...     print(list(path))
        [(0, 1), (1, 2), (2, 3)]
        [(0, 1), (1, 3)]
        [(0, 2), (2, 1), (1, 3)]
        [(0, 2), (2, 3)]
        [(0, 3)]

    Pass an iterable of nodes as target to generate all paths ending in any of several nodes::

        >>> G = nx.complete_graph(4)
        >>> for path in nx.all_simple_paths(G, source=0, target=[3, 2]):
        ...     print(path)
        ...
        [0, 1, 2]
        [0, 1, 2, 3]
        [0, 1, 3]
        [0, 1, 3, 2]
        [0, 2]
        [0, 2, 1, 3]
        [0, 2, 3]
        [0, 3]
        [0, 3, 1, 2]
        [0, 3, 2]

    The singleton path from ``source`` to itself is considered a simple path and is
    included in the results:

        >>> G = nx.empty_graph(5)
        >>> list(nx.all_simple_paths(G, source=0, target=0))
        [[0]]

        >>> G = nx.path_graph(3)
        >>> list(nx.all_simple_paths(G, source=0, target={0, 1, 2}))
        [[0], [0, 1], [0, 1, 2]]

    Iterate over each path from the root nodes to the leaf nodes in a
    directed acyclic graph using a functional programming approach::

        >>> from itertools import chain
        >>> from itertools import product
        >>> from itertools import starmap
        >>> from functools import partial
        >>>
        >>> chaini = chain.from_iterable
        >>>
        >>> G = nx.DiGraph([(0, 1), (1, 2), (0, 3), (3, 2)])
        >>> roots = (v for v, d in G.in_degree() if d == 0)
        >>> leaves = (v for v, d in G.out_degree() if d == 0)
        >>> all_paths = partial(nx.all_simple_paths, G)
        >>> list(chaini(starmap(all_paths, product(roots, leaves))))
        [[0, 1, 2], [0, 3, 2]]

    The same list computed using an iterative approach::

        >>> G = nx.DiGraph([(0, 1), (1, 2), (0, 3), (3, 2)])
        >>> roots = (v for v, d in G.in_degree() if d == 0)
        >>> leaves = (v for v, d in G.out_degree() if d == 0)
        >>> all_paths = []
        >>> for root in roots:
        ...     for leaf in leaves:
        ...         paths = nx.all_simple_paths(G, root, leaf)
        ...         all_paths.extend(paths)
        >>> all_paths
        [[0, 1, 2], [0, 3, 2]]

    Iterate over each path from the root nodes to the leaf nodes in a
    directed acyclic graph passing all leaves together to avoid unnecessary
    compute::

        >>> G = nx.DiGraph([(0, 1), (2, 1), (1, 3), (1, 4)])
        >>> roots = (v for v, d in G.in_degree() if d == 0)
        >>> leaves = [v for v, d in G.out_degree() if d == 0]
        >>> all_paths = []
        >>> for root in roots:
        ...     paths = nx.all_simple_paths(G, root, leaves)
        ...     all_paths.extend(paths)
        >>> all_paths
        [[0, 1, 3], [0, 1, 4], [2, 1, 3], [2, 1, 4]]

    If parallel edges offer multiple ways to traverse a given sequence of
    nodes, this sequence of nodes will be returned multiple times:

        >>> G = nx.MultiDiGraph([(0, 1), (0, 1), (1, 2)])
        >>> list(nx.all_simple_paths(G, 0, 2))
        [[0, 1, 2], [0, 1, 2]]

    Notes
    -----
    This algorithm uses a modified depth-first search to generate the
    paths [1]_.  A single path can be found in $O(V+E)$ time but the
    number of simple paths in a graph can be very large, e.g. $O(n!)$ in
    the complete graph of order $n$.

    This function does not check that a path exists between `source` and
    `target`. For large graphs, this may result in very long runtimes.
    Consider using `has_path` to check that a path exists between `source` and
    `target` before calling this function on large graphs.

    References
    ----------
    .. [1] R. Sedgewick, "Algorithms in C, Part 5: Graph Algorithms",
       Addison Wesley Professional, 3rd ed., 2001.

    See Also
    --------
    all_shortest_paths, shortest_path, has_path

    """
    for edge_path in all_simple_edge_paths(G, source, target, cutoff):
        yield [source] + [edge[1] for edge in edge_path]


@nx._dispatchable
def all_simple_edge_paths(G, source, target, cutoff=None):
    """Generate lists of edges for all simple paths in G from source to target.

    A simple path is a path with no repeated nodes.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : nodes
       Single node or iterable of nodes at which to end path

    cutoff : integer, optional
        Depth to stop the search. Only paths with length <= `cutoff` are returned.
        Note that the length of an edge path is the number of edges.

    Returns
    -------
    path_generator: generator
       A generator that produces lists of simple paths.  If there are no paths
       between the source and target within the given cutoff the generator
       produces no output.
       For multigraphs, the list of edges have elements of the form `(u,v,k)`.
       Where `k` corresponds to the edge key.

    Examples
    --------

    Print the simple path edges of a Graph::

        >>> g = nx.Graph([(1, 2), (2, 4), (1, 3), (3, 4)])
        >>> for path in sorted(nx.all_simple_edge_paths(g, 1, 4)):
        ...     print(path)
        [(1, 2), (2, 4)]
        [(1, 3), (3, 4)]

    Print the simple path edges of a MultiGraph. Returned edges come with
    their associated keys::

        >>> mg = nx.MultiGraph()
        >>> mg.add_edge(1, 2, key="k0")
        'k0'
        >>> mg.add_edge(1, 2, key="k1")
        'k1'
        >>> mg.add_edge(2, 3, key="k0")
        'k0'
        >>> for path in sorted(nx.all_simple_edge_paths(mg, 1, 3)):
        ...     print(path)
        [(1, 2, 'k0'), (2, 3, 'k0')]
        [(1, 2, 'k1'), (2, 3, 'k0')]

    When ``source`` is one of the targets, the empty path starting and ending at
    ``source`` without traversing any edge is considered a valid simple edge path
    and is included in the results:

        >>> G = nx.Graph()
        >>> G.add_node(0)
        >>> paths = list(nx.all_simple_edge_paths(G, 0, 0))
        >>> for path in paths:
        ...     print(path)
        []
        >>> len(paths)
        1

    You can use the `cutoff` parameter to only generate paths that are
    shorter than a certain length:

        >>> g = nx.Graph([(1, 2), (2, 3), (3, 4), (4, 5), (1, 4), (1, 5)])
        >>> for path in sorted(nx.all_simple_edge_paths(g, 1, 5)):
        ...     print(path)
        [(1, 2), (2, 3), (3, 4), (4, 5)]
        [(1, 4), (4, 5)]
        [(1, 5)]
        >>> for path in sorted(nx.all_simple_edge_paths(g, 1, 5, cutoff=1)):
        ...     print(path)
        [(1, 5)]
        >>> for path in sorted(nx.all_simple_edge_paths(g, 1, 5, cutoff=2)):
        ...     print(path)
        [(1, 4), (4, 5)]
        [(1, 5)]

    Notes
    -----
    This algorithm enumerates paths with polynomial delay, i.e., the time
    between two consecutive output paths (and before the first and after
    the last) is bounded:  $O(V+E)$ per path if ``cutoff`` is ``None``,
    using a Johnson-style blocked depth-first search [1]_, and
    $O(k(V+E))$ per path for ``cutoff=k``, using a variant of BS-DFS [2]_.
    The *number* of simple paths can nevertheless be very large,
    e.g. $\\Theta((n-2)!)$ between two fixed nodes of the complete
    graph of order n, so consume the generator lazily rather than
    materializing the full list.

    References
    ----------
    .. [1] D. B. Johnson. "Finding all the elementary circuits of a directed graph."
           SIAM J. Comput., 4(1):77-84, 1975. https://doi.org/10.1137/0204007.
    .. [2] Frank Bauernöppel, Jörg-Rüdiger Sack.
           "Enumerating Length-Bounded Simple Paths and Cycles in Directed Graphs
            with $O(k(n+m))$ Delay Using Edge-Consistent Node Barriers"
            https://arxiv.org/abs/2607.14745

    See Also
    --------
    all_shortest_paths, shortest_path, all_simple_paths

    """
    if source not in G:
        raise nx.NodeNotFound(f"source node {source} not in graph")

    if target in G:
        targets = {target}
    else:
        try:
            targets = set(target)
        except TypeError as err:
            raise nx.NodeNotFound(f"target node {target} not in graph") from err

    if cutoff is None and targets:
        yield from _johnson_all_simple_edge_paths(G, source, targets)
    elif cutoff >= 0 and targets:
        yield from _bsdfs_all_simple_edge_paths(G, source, targets, cutoff)


def _johnson_all_simple_edge_paths(G, source, targets):
    """
    Adaption of the Johnson's cycle finding algorithm [1]_
    to simple paths in NetworkX [Multi][Di]Graphs.
    The multi-target feature is implemented by introducing
    a virtual target t* to which all real targets connect.
    Johnson's algorithm produces the next output (or terminates)
    within $O(V+E)$ time with a small constant, a great
    improvement over earlier work [2]_, [3]_, [4]_.

    References
    ----------
    .. [1] D. B. Johnson. "Finding all the elementary circuits of a directed graph."
           SIAM J. Comput., 4(1):77-84, 1975. https://doi.org/10.1137/0204007.
    .. [2] J. C. Tiernan. "An efficient search algorithm to find the elementary
            circuits of a graph". Commun. ACM 13(12): 722--726, 1970,
            https://doi.org/10.1145/362814.362819
    .. [3] R. E. Tarjan. "Enumeration of the Elementary Circuits of a Directed Graph"
             SIAM J. Comput.
    .. [4] R. Sedgewick, "Algorithms in C, Part 5: Graph Algorithms",
            Addison Wesley Professional, 3rd ed., 2001.
    """
    assert targets  # ensured by caller

    adj = G._adj  # successors (directed) / neighbors (undirected)

    if G.is_multigraph():

        def out_edges(v):
            for w, keydict in adj[v].items():
                for key in keydict:
                    yield (v, w, key)
    else:

        def out_edges(v):
            for w in adj[v]:
                yield (v, w)

    blocked = set()
    B = defaultdict(set)

    def unblock(v):
        pending = [v]
        while pending:
            u = pending.pop()
            if u in blocked:
                blocked.discard(u)
                pending.extend(B[u])
                B[u].clear()

    edge_path = []
    # frame: [node, out-edge iterator, fruitful]
    blocked.add(source)
    stack = [[source, out_edges(source), source in targets]]
    if source in targets:
        yield []

    while stack:
        frame = stack[-1]
        for e in frame[1]:
            w = e[1]
            if w not in blocked:
                edge_path.append(e)
                blocked.add(w)
                stack.append([w, out_edges(w), w in targets])
                if w in targets:
                    yield list(edge_path)
                break
        else:
            # frame[0] exhausted: close the call
            stack.pop()
            v = frame[0]
            if frame[2]:
                unblock(v)
                if stack:
                    stack[-1][2] = True
            else:
                for w in adj[v]:
                    B[w].add(v)
            if stack:
                edge_path.pop()


def _bsdfs_all_simple_edge_paths(G, source, targets, cutoff):
    """
    Adaption of the BS-DFS algorithm [1]_ to NetworkX [Multi][Di]Graphs.
    The multi-target feature is implemented by introducing
    a virtual target t* to which all real targets connect.
    The BS-DFS algorithm produces the next output (or terminates) within
    $O(k(V+E))$ time with a small constant, correcting earlier work [2]_.

    References
    ----------
    .. [1] Frank Bauernöppel, Jörg-Rüdiger Sack.
           "Enumerating Length-Bounded Simple Paths and Cycles in Directed Graphs
            with $O(k(n+m))$ Delay Using Edge-Consistent Node Barriers"
            https://arxiv.org/abs/2607.14745
    .. [2]  Y. Peng et al.
            "Efficient Hop-constrained s-t Simple Path Enumeration"
            The VLDB Journal, 30(5):799-823, 2021,
            https://doi.org/10.1007/s00778-021-00674-5
    """

    assert cutoff >= 0 and targets  # ensured by caller
    k = cutoff

    get_edges = (
        (lambda v: G.edges(v, keys=True))
        if G.is_multigraph()
        else (lambda v: G.edges(v))
    )
    pred = G.pred if G.is_directed() else G.adj  # cascade direction

    b = defaultdict(int)  # barriers, persistent over the whole run
    nodes = []  # node stack S
    edges = []  # entering edge per node; edges[0] is a dummy
    on_path = set()
    sd_stack = []  # per-frame sd
    iters = []  # per-frame outgoing-edge iterator

    def fruitful(v, sd):
        b[v] = sd
        queue = deque([(v, sd)])
        while queue:
            u, d = queue.popleft()
            for p in pred[u]:
                if p not in on_path and b[p] > d + 1:
                    b[p] = d + 1
                    queue.append((p, d + 1))

    def push(v, e):
        nodes.append(v)
        edges.append(e)
        on_path.add(v)
        iters.append(iter(get_edges(v)))
        if v in targets:  # virtual edge v -> t*
            sd_stack.append(0)
            return True
        sd_stack.append(k + 1)
        return False

    if push(source, None):
        yield []

    while nodes:
        h = len(nodes) - 1  # depth of the top node v
        e = next(
            (e for e in iters[-1] if e[1] not in on_path and b[e[1]] + h < k), None
        )
        if e is not None:
            if push(e[1], e):
                yield edges[1:]  # slice copies; dummy removed
            continue

        # return from Search(v)
        v = nodes[-1]
        iters.pop()
        sd = sd_stack.pop()
        if sd <= k:
            fruitful(v, sd)  # v still on the stack
        else:
            b[v] = k - h + 1
        nodes.pop()
        edges.pop()
        on_path.discard(v)
        if sd_stack:
            sd_stack[-1] = min(sd_stack[-1], sd + 1)


@not_implemented_for("multigraph")
@nx._dispatchable(edge_attrs="weight")
def shortest_simple_paths(G, source, target, weight=None):
    """Generate all simple paths in the graph G from source to target,
       starting from shortest ones.

    A simple path is a path with no repeated nodes.

    If a weighted shortest path search is to be used, no negative weights
    are allowed.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path

    weight : string or function
        If it is a string, it is the name of the edge attribute to be
        used as a weight.

        If it is a function, the weight of an edge is the value returned
        by the function. The function must accept exactly three positional
        arguments: the two endpoints of an edge and the dictionary of edge
        attributes for that edge. The function must return a number or None.
        The weight function can be used to hide edges by returning None.
        So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
        will find the shortest red path.

        If None all edges are considered to have unit weight. Default
        value None.

    Returns
    -------
    path_generator: generator
       A generator that produces lists of simple paths, in order from
       shortest to longest.

    Raises
    ------
    NetworkXNoPath
       If no path exists between source and target.

    NetworkXError
       If source or target nodes are not in the input graph.

    NetworkXNotImplemented
       If the input graph is a Multi[Di]Graph.

    Examples
    --------

    >>> G = nx.cycle_graph(7)
    >>> paths = list(nx.shortest_simple_paths(G, 0, 3))
    >>> print(paths)
    [[0, 1, 2, 3], [0, 6, 5, 4, 3]]

    You can use this function to efficiently compute the k shortest/best
    paths between two nodes.

    >>> from itertools import islice
    >>> def k_shortest_paths(G, source, target, k, weight=None):
    ...     return list(
    ...         islice(nx.shortest_simple_paths(G, source, target, weight=weight), k)
    ...     )
    >>> for path in k_shortest_paths(G, 0, 3, 2):
    ...     print(path)
    [0, 1, 2, 3]
    [0, 6, 5, 4, 3]

    Notes
    -----
    This procedure is based on algorithm by Jin Y. Yen [1]_.  Finding
    the first $K$ paths requires $O(KN^3)$ operations.

    See Also
    --------
    all_shortest_paths
    shortest_path
    all_simple_paths

    References
    ----------
    .. [1] Jin Y. Yen, "Finding the K Shortest Loopless Paths in a
       Network", Management Science, Vol. 17, No. 11, Theory Series
       (Jul., 1971), pp. 712-716.

    """
    if source not in G:
        raise nx.NodeNotFound(f"source node {source} not in graph")

    if target not in G:
        raise nx.NodeNotFound(f"target node {target} not in graph")

    if weight is None:
        length_func = len
        shortest_path_func = _bidirectional_shortest_path
    else:
        wt = _weight_function(G, weight)

        def length_func(path):
            return sum(
                wt(u, v, G.get_edge_data(u, v)) for (u, v) in zip(path, path[1:])
            )

        shortest_path_func = _bidirectional_dijkstra

    listA = []
    listB = PathBuffer()
    prev_path = None
    while True:
        if not prev_path:
            length, path = shortest_path_func(G, source, target, weight=weight)
            listB.push(length, path)
        else:
            ignore_nodes = set()
            ignore_edges = set()
            for i in range(1, len(prev_path)):
                root = prev_path[:i]
                root_length = length_func(root)
                for path in listA:
                    if path[:i] == root:
                        ignore_edges.add((path[i - 1], path[i]))
                try:
                    length, spur = shortest_path_func(
                        G,
                        root[-1],
                        target,
                        ignore_nodes=ignore_nodes,
                        ignore_edges=ignore_edges,
                        weight=weight,
                    )
                    path = root[:-1] + spur
                    listB.push(root_length + length, path)
                except nx.NetworkXNoPath:
                    pass
                ignore_nodes.add(root[-1])

        if listB:
            path = listB.pop()
            yield path
            listA.append(path)
            prev_path = path
        else:
            break


class PathBuffer:
    def __init__(self):
        self.paths = set()
        self.sortedpaths = []
        self.counter = count()

    def __len__(self):
        return len(self.sortedpaths)

    def push(self, cost, path):
        hashable_path = tuple(path)
        if hashable_path not in self.paths:
            heappush(self.sortedpaths, (cost, next(self.counter), path))
            self.paths.add(hashable_path)

    def pop(self):
        (cost, num, path) = heappop(self.sortedpaths)
        hashable_path = tuple(path)
        self.paths.remove(hashable_path)
        return path


def _bidirectional_shortest_path(
    G, source, target, ignore_nodes=None, ignore_edges=None, weight=None
):
    """Returns the shortest path between source and target ignoring
       nodes and edges in the containers ignore_nodes and ignore_edges.

    This is a custom modification of the standard bidirectional shortest
    path implementation at networkx.algorithms.unweighted

    Parameters
    ----------
    G : NetworkX graph

    source : node
       starting node for path

    target : node
       ending node for path

    ignore_nodes : container of nodes
       nodes to ignore, optional

    ignore_edges : container of edges
       edges to ignore, optional

    weight : None
       This function accepts a weight argument for convenience of
       shortest_simple_paths function. It will be ignored.

    Returns
    -------
    path: list
       List of nodes in a path from source to target.

    Raises
    ------
    NetworkXNoPath
       If no path exists between source and target.

    See Also
    --------
    shortest_path

    """
    # call helper to do the real work
    results = _bidirectional_pred_succ(G, source, target, ignore_nodes, ignore_edges)
    pred, succ, w = results

    # build path from pred+w+succ
    path = []
    # from w to target
    while w is not None:
        path.append(w)
        w = succ[w]
    # from source to w
    w = pred[path[0]]
    while w is not None:
        path.insert(0, w)
        w = pred[w]

    return len(path), path


def _bidirectional_pred_succ(G, source, target, ignore_nodes=None, ignore_edges=None):
    """Bidirectional shortest path helper.
    Returns (pred,succ,w) where
    pred is a dictionary of predecessors from w to the source, and
    succ is a dictionary of successors from w to the target.
    """
    # does BFS from both source and target and meets in the middle
    if ignore_nodes and (source in ignore_nodes or target in ignore_nodes):
        raise nx.NetworkXNoPath(f"No path between {source} and {target}.")
    if target == source:
        return ({target: None}, {source: None}, source)

    # handle either directed or undirected
    if G.is_directed():
        Gpred = G.predecessors
        Gsucc = G.successors
    else:
        Gpred = G.neighbors
        Gsucc = G.neighbors

    # support optional nodes filter
    if ignore_nodes:

        def filter_iter(nodes):
            def iterate(v):
                for w in nodes(v):
                    if w not in ignore_nodes:
                        yield w

            return iterate

        Gpred = filter_iter(Gpred)
        Gsucc = filter_iter(Gsucc)

    # support optional edges filter
    if ignore_edges:
        if G.is_directed():

            def filter_pred_iter(pred_iter):
                def iterate(v):
                    for w in pred_iter(v):
                        if (w, v) not in ignore_edges:
                            yield w

                return iterate

            def filter_succ_iter(succ_iter):
                def iterate(v):
                    for w in succ_iter(v):
                        if (v, w) not in ignore_edges:
                            yield w

                return iterate

            Gpred = filter_pred_iter(Gpred)
            Gsucc = filter_succ_iter(Gsucc)

        else:

            def filter_iter(nodes):
                def iterate(v):
                    for w in nodes(v):
                        if (v, w) not in ignore_edges and (w, v) not in ignore_edges:
                            yield w

                return iterate

            Gpred = filter_iter(Gpred)
            Gsucc = filter_iter(Gsucc)

    # predecessor and successors in search
    pred = {source: None}
    succ = {target: None}

    # initialize fringes, start with forward
    forward_fringe = [source]
    reverse_fringe = [target]

    while forward_fringe and reverse_fringe:
        if len(forward_fringe) <= len(reverse_fringe):
            this_level = forward_fringe
            forward_fringe = []
            for v in this_level:
                for w in Gsucc(v):
                    if w not in pred:
                        forward_fringe.append(w)
                        pred[w] = v
                    if w in succ:
                        # found path
                        return pred, succ, w
        else:
            this_level = reverse_fringe
            reverse_fringe = []
            for v in this_level:
                for w in Gpred(v):
                    if w not in succ:
                        succ[w] = v
                        reverse_fringe.append(w)
                    if w in pred:
                        # found path
                        return pred, succ, w

    raise nx.NetworkXNoPath(f"No path between {source} and {target}.")


def _bidirectional_dijkstra(
    G, source, target, weight="weight", ignore_nodes=None, ignore_edges=None
):
    """Dijkstra's algorithm for shortest paths using bidirectional search.

    This function returns the shortest path between source and target
    ignoring nodes and edges in the containers ignore_nodes and
    ignore_edges.

    This is a custom modification of the standard Dijkstra bidirectional
    shortest path implementation at networkx.algorithms.weighted

    Parameters
    ----------
    G : NetworkX graph

    source : node
        Starting node.

    target : node
        Ending node.

    weight: string, function, optional (default='weight')
        Edge data key or weight function corresponding to the edge weight
        If this is a function, the weight of an edge is the value
        returned by the function. The function must accept exactly three
        positional arguments: the two endpoints of an edge and the
        dictionary of edge attributes for that edge. The function must
        return a number or None to indicate a hidden edge.

    ignore_nodes : container of nodes
        nodes to ignore, optional

    ignore_edges : container of edges
        edges to ignore, optional

    Returns
    -------
    length : number
        Shortest path length.

    Returns a tuple of two dictionaries keyed by node.
    The first dictionary stores distance from the source.
    The second stores the path from the source to that node.

    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The weight function can be used to hide edges by returning None.
    So ``weight = lambda u, v, d: 1 if d['color']=="red" else None``
    will find the shortest red path.

    In practice  bidirectional Dijkstra is much more than twice as fast as
    ordinary Dijkstra.

    Ordinary Dijkstra expands nodes in a sphere-like manner from the
    source. The radius of this sphere will eventually be the length
    of the shortest path. Bidirectional Dijkstra will expand nodes
    from both the source and the target, making two spheres of half
    this radius. Volume of the first sphere is pi*r*r while the
    others are 2*pi*r/2*r/2, making up half the volume.

    This algorithm is not guaranteed to work if edge weights
    are negative or are floating point numbers
    (overflows and roundoff errors can cause problems).

    See Also
    --------
    shortest_path
    shortest_path_length
    """
    if ignore_nodes and (source in ignore_nodes or target in ignore_nodes):
        raise nx.NetworkXNoPath(f"No path between {source} and {target}.")
    if source == target:
        if source not in G:
            raise nx.NodeNotFound(f"Node {source} not in graph")
        return (0, [source])

    # handle either directed or undirected
    if G.is_directed():
        Gpred = G.predecessors
        Gsucc = G.successors
    else:
        Gpred = G.neighbors
        Gsucc = G.neighbors

    # support optional nodes filter
    if ignore_nodes:

        def filter_iter(nodes):
            def iterate(v):
                for w in nodes(v):
                    if w not in ignore_nodes:
                        yield w

            return iterate

        Gpred = filter_iter(Gpred)
        Gsucc = filter_iter(Gsucc)

    # support optional edges filter
    if ignore_edges:
        if G.is_directed():

            def filter_pred_iter(pred_iter):
                def iterate(v):
                    for w in pred_iter(v):
                        if (w, v) not in ignore_edges:
                            yield w

                return iterate

            def filter_succ_iter(succ_iter):
                def iterate(v):
                    for w in succ_iter(v):
                        if (v, w) not in ignore_edges:
                            yield w

                return iterate

            Gpred = filter_pred_iter(Gpred)
            Gsucc = filter_succ_iter(Gsucc)

        else:

            def filter_iter(nodes):
                def iterate(v):
                    for w in nodes(v):
                        if (v, w) not in ignore_edges and (w, v) not in ignore_edges:
                            yield w

                return iterate

            Gpred = filter_iter(Gpred)
            Gsucc = filter_iter(Gsucc)

    wt = _weight_function(G, weight)
    # Init:   Forward             Backward
    dists = [{}, {}]  # dictionary of final distances
    paths = [{source: [source]}, {target: [target]}]  # dictionary of paths
    fringe = [[], []]  # heap of (distance, node) tuples for
    # extracting next node to expand
    seen = [{source: 0}, {target: 0}]  # dictionary of distances to
    # nodes seen
    c = count()
    # initialize fringe heap
    heappush(fringe[0], (0, next(c), source))
    heappush(fringe[1], (0, next(c), target))
    # neighs for extracting correct neighbor information
    neighs = [Gsucc, Gpred]
    # variables to hold shortest discovered path
    # finaldist = 1e30000
    finalpath = []
    dir = 1
    while fringe[0] and fringe[1]:
        # choose direction
        # dir == 0 is forward direction and dir == 1 is back
        dir = 1 - dir
        # extract closest to expand
        (dist, _, v) = heappop(fringe[dir])
        if v in dists[dir]:
            # Shortest path to v has already been found
            continue
        # update distance
        dists[dir][v] = dist  # equal to seen[dir][v]
        if v in dists[1 - dir]:
            # if we have scanned v in both directions we are done
            # we have now discovered the shortest path
            return (finaldist, finalpath)

        for w in neighs[dir](v):
            if dir == 0:  # forward
                minweight = wt(v, w, G.get_edge_data(v, w))
            else:  # back, must remember to change v,w->w,v
                minweight = wt(w, v, G.get_edge_data(w, v))
            if minweight is None:
                continue
            vwLength = dists[dir][v] + minweight

            if w in dists[dir]:
                if vwLength < dists[dir][w]:
                    raise ValueError("Contradictory paths found: negative weights?")
            elif w not in seen[dir] or vwLength < seen[dir][w]:
                # relaxing
                seen[dir][w] = vwLength
                heappush(fringe[dir], (vwLength, next(c), w))
                paths[dir][w] = paths[dir][v] + [w]
                if w in seen[0] and w in seen[1]:
                    # see if this path is better than the already
                    # discovered shortest path
                    totaldist = seen[0][w] + seen[1][w]
                    if finalpath == [] or finaldist > totaldist:
                        finaldist = totaldist
                        revpath = paths[1][w][:]
                        revpath.reverse()
                        finalpath = paths[0][w] + revpath[1:]
    raise nx.NetworkXNoPath(f"No path between {source} and {target}.")
