"""Provides functions for computing minors of a graph."""
from collections import Counter, defaultdict
from itertools import chain

import networkx as nx
from networkx.exception import NetworkXException
from networkx.utils import arbitrary_element

__all__ = [
    "contracted_edge",
    "contracted_nodes",
    "equivalence_classes",
    "identified_nodes",
    "quotient_graph",
]


def equivalence_classes(iterable, relation):
    """Returns equivalence classes of `relation` when applied to `iterable`.

    The equivalence classes, or blocks, consist of objects from `iterable`
    which are all equivalent. They are defined to be equivalent if the
    `relation` function returns `True` when passed any two objects from that
    class, and `False` otherwise. To define an equivalence relation the
    function must be reflexive, symmetric and transitive.

    Parameters
    ----------
    iterable : list, tuple, or set
        An iterable of elements/nodes.

    relation : function
        A Boolean-valued function that implements an equivalence relation
        (reflexive, symmetric, transitive binary relation) on the elements
        of `iterable` - it must take two elements and return `True` if
        they are related, or `False` if not.

    Returns
    -------
    set of frozensets
        A set of frozensets representing the partition induced by the equivalence
        relation function `relation` on the elements of `iterable`. Each
        member set in the return set represents an equivalence class, or
        block, of the partition.

        Duplicate elements will be ignored so it makes the most sense for
        `iterable` to be a :class:`set`.

    Notes
    -----
    This function does not check that `relation` represents an equivalence
    relation. You can check that your equivalence classes provide a partition
    using `is_partition`.

    Examples
    --------
    Let `X` be the set of integers from `0` to `9`, and consider an equivalence
    relation `R` on `X` of congruence modulo `3`: this means that two integers
    `x` and `y` in `X` are equivalent under `R` if they leave the same
    remainder when divided by `3`, i.e. `(x - y) mod 3 = 0`.

    The equivalence classes of this relation are `{0, 3, 6, 9}`, `{1, 4, 7}`,
    `{2, 5, 8}`: `0`, `3`, `6`, `9` are all divisible by `3` and leave zero
    remainder; `1`, `4`, `7` leave remainder `1`; while `2`, `5` and `8` leave
    remainder `2`. We can see this by calling `equivalence_classes` with
    `X` and a function implementation of `R`.

    >>> X = set(range(10))
    >>> def mod3(x, y): return (x - y) % 3 == 0
    >>> equivalence_classes(X, mod3)    # doctest: +SKIP
    {frozenset({1, 4, 7}), frozenset({8, 2, 5}), frozenset({0, 9, 3, 6})}
    """
    # For simplicity of implementation, we initialize the return value as a
    # list of lists, then convert it to a set of sets at the end of the
    # function.
    blocks = []
    # Determine the equivalence class for each element of the iterable.
    for y in iterable:
        # Each element y must be in *exactly one* equivalence class.
        #
        # Each block is guaranteed to be non-empty
        for block in blocks:
            x = arbitrary_element(block)
            if relation(x, y):
                block.append(y)
                break
        else:
            # If the element y is not part of any known equivalence class, it
            # must be in its own, so we create a new singleton equivalence
            # class for it.
            blocks.append([y])
    return {frozenset(block) for block in blocks}


@nx._dispatch(preserve_edge_attrs=True)
def quotient_graph(
    G,
    partition,
    node_data=None,
    edge_data_reduce=None,
    edge_data_default=None,
    weight="weight",
    self_loops=False,
    create_using=None,
):
    """Returns the quotient graph of `G` under the specified equivalence
    relation on nodes. The nodes in the quotient graph are labeled by
    non-negative integers.

    Parameters
    ----------
    G : NetworkX graph
        The graph for which to return the quotient graph with the
        specified node relation.

    partition : function, or dict or list of lists, tuples or sets
        If a function, this function must represent an equivalence
        relation on the nodes of `G`. It must take two arguments *u*
        and *v* and return True exactly when *u* and *v* are in the
        same equivalence class. The equivalence classes form the nodes
        in the returned graph.

        If a dict of lists/tuples/sets, the keys can be any meaningful
        block labels, but the values must be the block lists/tuples/sets
        (one list/tuple/set per block), and the blocks must form a valid
        partition of the nodes of the graph. That is, each node must be
        in exactly one block of the partition.

        If a list of sets, the list must form a valid partition of
        the nodes of the graph. That is, each node must be in exactly
        one block of the partition.

    node_data : function
        This function takes one argument, *B*, a set of nodes in `G`,
        and must return a dictionary representing the node data
        attributes to set on the node representing *B* in the quotient graph.
        If None, the no node attributes are set.

    edge_data_reduce : function
        This function takes two arguments, both dictionaries of
        edge attributes and returns a combined dictionary.

        This parameter may only be specified if `edge_data` is None.
        Specifying `edge_data_reduce` is much more efficient than `edge_data`,
        so it's advised to do so when possible.

        By default, each edge is queried to find its weight attribute specified
        by the `weight` parameter, and these attributes are summed.

    edge_data_default : function
        Factory function taking no parameters for initial value of each
        quotient graph edge attributes. Any edges in the original graph will
        be reduced with this value. By default, `dict` is used.

    weight : string or None, optional (default="weight")
        The name of an edge attribute that holds the numerical value
        used as a weight. If None then each edge has weight 1. This is only
        used if `edge_data_reduce` is None.

    self_loops : bool
        If True, create self edges in the quotient graph for any edges in `G`
        that belong to the same equivalence class.

    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    NetworkX graph
        The quotient graph of `G` under the equivalence relation
        specified by `partition`.

    Raises
    ------
    NetworkXException
        If the given partition is not a valid partition of the nodes of
        `G`.

    Examples
    --------
    The quotient graph of the complete bipartite graph under the "same
    neighbors" equivalence relation is `K_2`. Under this relation, two nodes
    are equivalent if they are not adjacent but have the same neighbor set.

    >>> G = nx.complete_bipartite_graph(2, 3)
    >>> same_neighbors = lambda u, v: (
    ...     u not in G[v] and v not in G[u] and G[u] == G[v]
    ... )
    >>> Q = nx.quotient_graph(G, same_neighbors)
    >>> K2 = nx.complete_graph(2)
    >>> nx.is_isomorphic(Q, K2)
    True

    The quotient graph of a directed graph under the "same strongly connected
    component" equivalence relation is the condensation of the graph (see
    :func:`condensation`). This example comes from the Wikipedia article
    *`Strongly connected component`_*.

    >>> G = nx.DiGraph()
    >>> edges = [
    ...     "ab",
    ...     "be",
    ...     "bf",
    ...     "bc",
    ...     "cg",
    ...     "cd",
    ...     "dc",
    ...     "dh",
    ...     "ea",
    ...     "ef",
    ...     "fg",
    ...     "gf",
    ...     "hd",
    ...     "hf",
    ... ]
    >>> G.add_edges_from(tuple(x) for x in edges)
    >>> components = list(nx.strongly_connected_components(G))
    >>> sorted(sorted(component) for component in components)
    [['a', 'b', 'e'], ['c', 'd', 'h'], ['f', 'g']]
    >>>
    >>> C = nx.condensation(G, components)
    >>> component_of = C.graph["mapping"]
    >>> same_component = lambda u, v: component_of[u] == component_of[v]
    >>> Q = nx.quotient_graph(G, same_component)
    >>> nx.is_isomorphic(C, Q)
    True

    Node identification can be represented as the quotient of a graph under the
    equivalence relation that places the two nodes in one block and each other
    node in its own singleton block.

    >>> K24 = nx.complete_bipartite_graph(2, 4)
    >>> K34 = nx.complete_bipartite_graph(3, 4)
    >>> C = nx.contracted_nodes(K34, 1, 2)
    >>> nodes = {1, 2}
    >>> is_contracted = lambda u, v: u in nodes and v in nodes
    >>> Q = nx.quotient_graph(K34, is_contracted)
    >>> nx.is_isomorphic(Q, C)
    True
    >>> nx.is_isomorphic(Q, K24)
    True

    The blockmodeling technique described in [1]_ can be implemented as a
    quotient graph.

    >>> G = nx.path_graph(6)
    >>> partition = [{0, 1}, {2, 3}, {4, 5}]
    >>> M = nx.quotient_graph(G, partition)
    >>> list(M.edges())
    [(0, 1), (1, 2)]

    Here is the sample example but using partition as a dict of block sets.

    >>> G = nx.path_graph(6)
    >>> partition = {0: {0, 1}, 2: {2, 3}, 4: {4, 5}}
    >>> M = nx.quotient_graph(G, partition)
    >>> list(M.edges())
    [(0, 1), (1, 2)]

    Partitions can be represented in various ways:

    0. a list/tuple/set of block lists/tuples/sets
    1. a dict with block labels as keys and blocks lists/tuples/sets as values
    2. a dict with block lists/tuples/sets as keys and block labels as values
    3. a function from nodes in the original iterable to block labels
    4. an equivalence relation function on the target iterable

    As `quotient_graph` is designed to accept partitions represented as (0), (1) or
    (4) only, the `equivalence_classes` function can be used to get the partitions
    in the right form, in order to call `quotient_graph`.

    .. _Strongly connected component: https://en.wikipedia.org/wiki/Strongly_connected_component

    References
    ----------
    .. [1] Patrick Doreian, Vladimir Batagelj, and Anuska Ferligoj.
           *Generalized Blockmodeling*.
           Cambridge University Press, 2004.

    """
    if isinstance(partition, dict):
        partition = list(partition.values())
    if callable(partition):
        partition = equivalence_classes(G, partition)
    else:
        partition_nodes = set().union(*partition)
        if len(partition_nodes) != len(G):
            G = G.subgraph(partition_nodes)
        if not nx.community.is_partition(G, partition):
            raise NetworkXException(
                "each node must be in exactly one part of `partition`"
            )

    return _quotient_graph(
        G,
        partition,
        node_data,
        edge_data_reduce,
        edge_data_default,
        weight,
        self_loops,
        create_using,
    )


def _quotient_graph(
    G,
    partition,
    node_data,
    edge_data_reduce,
    edge_data_default,
    weight,
    self_loops,
    create_using,
):
    """Construct the quotient graph assuming input has been checked"""
    if create_using is None:
        H = G.__class__()
    else:
        H = nx.empty_graph(0, create_using)

    if node_data is None:
        node_data = lambda _: {}

    reduce_weights = edge_data_reduce is None
    if reduce_weights:
        if edge_data_default is not None:
            raise ValueError(
                "`edge_data_default` may not be set if `edge_data_reduce is None."
            )
    elif edge_data_default is None:
        edge_data_default = dict

    node2partition = {}
    for i, nbunch in enumerate(partition):
        H.add_node(i, **node_data(nbunch))
        node2partition.update((u, i) for u in nbunch)

    if H.is_multigraph():
        edges = _map_edges(G, node2partition, self_loops, data=True)
        H.add_edges_from(edges)

    elif reduce_weights:
        edges = _map_edges(G, node2partition, self_loops, data=weight, default=1)
        agg_edges = Counter()
        for u, v, weight in edges:
            agg_edges[u, v] += weight
        H.add_edges_from((u, v, {"weight": w}) for (u, v), w in agg_edges.items())

    else:
        edges = _map_edges(G, node2partition, self_loops, data=True)
        agg_edges = defaultdict(lambda: _reducible(edge_data_default))
        for u, v, data in edges:
            agg_edges[u, v](edge_data_reduce, data)
        H.add_edges_from((u, v, d.value) for (u, v), d in agg_edges.items())

    return H


@nx._dispatch(preserve_all_attrs=True)
def contracted_nodes(G, u, v, self_loops=True, copy=True):
    """Returns the graph that results from contracting `u` and `v`.

    Node contraction identifies the two nodes as a single node incident to any
    edge that was incident to the original two nodes.

    Parameters
    ----------
    G : NetworkX graph
        The graph whose nodes will be contracted.

    u, v : nodes
        Must be nodes in `G`.

    self_loops : Boolean
        If this is True, any edges joining `u` and `v` in `G` become
        self-loops on the new node in the returned graph.

    copy : Boolean
        If this is True (default True), make a copy of
        `G` and return that instead of directly changing `G`.


    Returns
    -------
    Networkx graph
        If Copy is True,
        A new graph object of the same type as `G` (leaving `G` unmodified)
        with `u` and `v` identified in a single node. The right node `v`
        will be merged into the node `u`, so only `u` will appear in the
        returned graph.
        If copy is False,
        Modifies `G` with `u` and `v` identified in a single node.
        The right node `v` will be merged into the node `u`, so
        only `u` will appear in the returned graph.

    Notes
    -----
    For multigraphs, the edge keys for the realigned edges may
    not be the same as the edge keys for the old edges. This is
    natural because edge keys are unique only within each pair of nodes.

    For non-multigraphs where `u` and `v` are adjacent to a third node
    `w`, the edge (`v`, `w`) will be contracted into the edge (`u`,
    `w`) with its attributes stored into a "contraction" attribute.

    This function is also available as `identified_nodes`.

    Examples
    --------
    Contracting two nonadjacent nodes of the cycle graph on four nodes `C_4`
    yields the path graph (ignoring parallel edges):

    >>> G = nx.cycle_graph(4)
    >>> M = nx.contracted_nodes(G, 1, 3)
    >>> P3 = nx.path_graph(3)
    >>> nx.is_isomorphic(M, P3)
    True

    >>> G = nx.MultiGraph(P3)
    >>> M = nx.contracted_nodes(G, 0, 2)
    >>> M.edges
    MultiEdgeView([(0, 1, 0), (0, 1, 1)])

    >>> G = nx.Graph([(1, 2), (2, 2)])
    >>> H = nx.contracted_nodes(G, 1, 2, self_loops=False)
    >>> list(H.nodes())
    [1]
    >>> list(H.edges())
    [(1, 1)]

    See Also
    --------
    contracted_edge
    quotient_graph

    """
    # Copying has significant overhead and can be disabled if needed
    if copy:
        H = G.copy()
    else:
        H = G

    # edge code uses G.edges(v) instead of G.adj[v] to handle multiedges
    if H.is_directed():
        edges_to_remap = chain(G.in_edges(v, data=True), G.out_edges(v, data=True))
    else:
        edges_to_remap = G.edges(v, data=True)

    # If the H=G, the generators change as H changes
    # This makes the edges_to_remap independent of H
    if not copy:
        edges_to_remap = list(edges_to_remap)

    v_data = H.nodes[v]
    H.remove_node(v)

    for prev_w, prev_x, d in edges_to_remap:
        w = prev_w if prev_w != v else u
        x = prev_x if prev_x != v else u

        if ({prev_w, prev_x} == {u, v}) and not self_loops:
            continue

        if not H.has_edge(w, x) or G.is_multigraph():
            H.add_edge(w, x, **d)
        else:
            if "contraction" in H.edges[(w, x)]:
                H.edges[(w, x)]["contraction"][(prev_w, prev_x)] = d
            else:
                H.edges[(w, x)]["contraction"] = {(prev_w, prev_x): d}

    if "contraction" in H.nodes[u]:
        H.nodes[u]["contraction"][v] = v_data
    else:
        H.nodes[u]["contraction"] = {v: v_data}
    return H


identified_nodes = contracted_nodes


@nx._dispatch(preserve_edge_attrs=True)
def contracted_edge(G, edge, self_loops=True, copy=True):
    """Returns the graph that results from contracting the specified edge.

    Edge contraction identifies the two endpoints of the edge as a single node
    incident to any edge that was incident to the original two nodes. A graph
    that results from edge contraction is called a *minor* of the original
    graph.

    Parameters
    ----------
    G : NetworkX graph
       The graph whose edge will be contracted.

    edge : tuple
       Must be a pair of nodes in `G`.

    self_loops : Boolean
       If this is True, any edges (including `edge`) joining the
       endpoints of `edge` in `G` become self-loops on the new node in the
       returned graph.

    copy : Boolean (default True)
        If this is True, a the contraction will be performed on a copy of `G`,
        otherwise the contraction will happen in place.

    Returns
    -------
    Networkx graph
       A new graph object of the same type as `G` (leaving `G` unmodified)
       with endpoints of `edge` identified in a single node. The right node
       of `edge` will be merged into the left one, so only the left one will
       appear in the returned graph.

    Raises
    ------
    ValueError
       If `edge` is not an edge in `G`.

    Examples
    --------
    Attempting to contract two nonadjacent nodes yields an error:

    >>> G = nx.cycle_graph(4)
    >>> nx.contracted_edge(G, (1, 3))
    Traceback (most recent call last):
      ...
    ValueError: Edge (1, 3) does not exist in graph G; cannot contract it

    Contracting two adjacent nodes in the cycle graph on *n* nodes yields the
    cycle graph on *n - 1* nodes:

    >>> C5 = nx.cycle_graph(5)
    >>> C4 = nx.cycle_graph(4)
    >>> M = nx.contracted_edge(C5, (0, 1), self_loops=False)
    >>> nx.is_isomorphic(M, C4)
    True

    See also
    --------
    contracted_nodes
    quotient_graph

    """
    u, v = edge[:2]
    if not G.has_edge(u, v):
        raise ValueError(f"Edge {edge} does not exist in graph G; cannot contract it")
    return contracted_nodes(G, u, v, self_loops=self_loops, copy=copy)


class _reducible:
    "helper class to reduce edge dictionary in-place."

    def __init__(self, default_factory):
        self.value = default_factory()

    def __call__(self, reduce_fn, other):
        self.value = reduce_fn(self.value, other)


def _map_edges(G, mapping, self_loops=True, data=None, **kw):
    "project edge src and dst through mapping and iterate over edges with data."
    data = (data is None) or data
    for u, v, data in G.edges(data=data, **kw):
        pu, pv = mapping[u], mapping[v]
        if not self_loops and pu == pv:
            continue
        yield pu, pv, data
