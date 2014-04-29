# -*- coding: utf-8 -*-
"""
Flow based connectivity algorithms
"""
from __future__ import division

import itertools
import networkx as nx

# Define the default maximum flow function to use in all flow based
# connectivity algorithms. 
from networkx.algorithms.flow import edmonds_karp
from networkx.algorithms.flow import shortest_augmenting_path
from networkx.algorithms.flow.utils import build_residual_network
default_flow_func = edmonds_karp

from networkx.algorithms.connectivity.utils import (
    build_auxiliary_node_connectivity, build_auxiliary_edge_connectivity)

__author__ = '\n'.join(['Jordi Torrents <jtorrents@milnou.net>'])

__all__ = ['average_node_connectivity',
           'local_node_connectivity',
           'node_connectivity',
           'local_edge_connectivity',
           'edge_connectivity',
           'all_pairs_node_connectivity_matrix']


def local_node_connectivity(G, s, t, flow_func=None, aux_digraph=None,
                            mapping=None, residual=None, cutoff=None):
    r"""Computes local node connectivity for nodes s and t.

    Local node connectivity for two non adjacent nodes s and t is the
    minimum number of nodes that must be removed (along with their incident
    edges) to disconnect them.

    This is a flow based implementation of node connectivity. We compute the
    maximum flow on an auxiliary digraph build from the original input
    graph (see below for details). 

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    s : node
        Source node

    t : node
        Target node

    flow_func : function
        A function for computing the maximum flow among a pair of nodes.
        The function has to accept at least three parameters: a Digraph, 
        a source node, and a target node. And return a residual network 
        that follows NetworkX conventions (see :meth:`maximum_flow` for 
        details). If flow_func is None, the default maximum flow function 
        (:meth:`edmonds_karp`) is used. See :meth:`node_connectivity` for
        details. The choice of the default function may change from version
        to version and should not be relied on. Default value: None.

    aux_digraph : NetworkX DiGraph
        Auxiliary digraph to compute flow based node connectivity. If None
        the auxiliary digraph is build. Default value: None.

    mapping : dict
        Dictionary with a mapping of node names in G and in the auxiliary
        digraph. Default value: None.

    residual : NetworkX DiGraph
        Residual network to compute maximum flow. If provided it will be
        reused instead of recreated. Default value: None.

    cutoff : integer, float
        If specified, the maximum flow algorithm will terminate when the 
        flow value reaches or exceeds the cutoff. This is only for the
        algorithms that support the cutoff parameter: :meth:`edmonds_karp` 
        and :meth:`shortest_augmenting_path`. Other algorithms will ignore
        this parameter. Default value: None.

    Returns
    -------
    K : integer
        local node connectivity for nodes s and t

    Examples
    --------
    >>> # Platonic icosahedral graph has node connectivity 5
    >>> # for each non adjacent node pair
    >>> G = nx.icosahedral_graph()
    >>> nx.local_node_connectivity(G, 0, 6)
    5

    If you need to compute local connectivity on several pairs of
    nodes in the same graph, it is recommended that you reuse the
    data structures that NetworkX uses for computing the maximum 
    flow and the node connectivity: the auxiliary digraph for
    node connectivity, and the residual network for maximum flow:

    >>> # Import the function for building the auxiliary digraph
    >>> from networkx.algorithms.connectivity.utils import (
    ...     build_auxiliary_node_connectivity)
    >>> H, mapping = build_auxiliary_node_connectivity(G)
    >>> # Import the function for building the resudual network
    >>> from networkx.algorithms.flow.utils import build_residual_network
    >>> R = build_residual_network(H, 'capacity')
    >>> # You can reuse them by passing them as parameters
    >>> kwargs = dict(aux_digraph=H, mapping=mapping, residual=R) 
    >>> nx.local_node_connectivity(G, 0, 6, **kwargs)
    5

    You can also use alternative flow algorithms for computing node 
    connectivity. For instance, in dense networks the algorithm
    :meth:`shortest_augmenting_path` will usually perform better than
    the default :meth:`edmonds_karp` which is faster for sparse 
    network with highly skewed degree distributions:

    >>> nx.local_node_connectivity(G, 0, 6, flow_func=nx.shortest_augmenting_path)
    5

    Notes
    -----
    This is a flow based implementation of node connectivity. We compute the
    maximum flow using, by default, the :meth:`edmonds_karp` algorithm on an 
    auxiliary digraph build from the original input graph:

    For an undirected graph G having `n` nodes and `m` edges we derive a
    directed graph D with 2n nodes and 2m+n arcs by replacing each
    original node `v` with two nodes `v_A`, `v_B` linked by an (internal)
    arc in `D`. Then for each edge (`u`, `v`) in G we add two arcs
    (`u_B`, `v_A`) and (`v_B`, `u_A`) in `D`. Finally we set the attribute
    capacity = 1 for each arc in `D` [1]_ .

    For a directed graph G having `n` nodes and `m` arcs we derive a
    directed graph `D` with `2n` nodes and `m+n` arcs by replacing each
    original node `v` with two nodes `v_A`, `v_B` linked by an (internal)
    arc `(v_A, v_B)` in D. Then for each arc `(u,v)` in G we add one arc
    `(u_B,v_A)` in `D`. Finally we set the attribute capacity = 1 for
    each arc in `D`.

    This is equal to the local node connectivity because the value of
    a maximum s-t-flow is equal to the capacity of a minimum s-t-cut (Ford
    and Fulkerson theorem).

    See also
    --------
    :meth:`node_connectivity`
    :meth:`edge_connectivity`
    :meth:`maximum_flow`
    :meth:`edmonds_karp`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    References
    ----------
    .. [1] Kammer, Frank and Hanjo Taubig. Graph Connectivity. in Brandes and
        Erlebach, 'Network Analysis: Methodological Foundations', Lecture
        Notes in Computer Science, Volume 3418, Springer-Verlag, 2005.
        http://www.informatik.uni-augsburg.de/thi/personen/kammer/Graph_Connectivity.pdf

    """
    if flow_func is None:
        flow_func = default_flow_func

    if aux_digraph is None or mapping is None:
        H, mapping = build_auxiliary_node_connectivity(G)
    else:
        H = aux_digraph

    kwargs = dict(flow_func=flow_func, residual=residual)
    if flow_func is shortest_augmenting_path:
        kwargs['cutoff'] = cutoff
        kwargs['two_phase'] = True
    elif flow_func is edmonds_karp:
        kwargs['cutoff'] = cutoff

    return nx.maximum_flow_value(H, '%sB' % mapping[s], '%sA' % mapping[t],
                                 **kwargs)


def node_connectivity(G, s=None, t=None, flow_func=None):
    r"""Returns node connectivity for a graph or digraph G.

    Node connectivity is equal to the minimum number of nodes that
    must be removed to disconnect G or render it trivial. If source
    and target nodes are provided, this function returns the local node
    connectivity: the minimum number of nodes that must be removed to break
    all paths from source to target in G.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    s : node
        Source node. Optional. Default value: None.

    t : node
        Target node. Optional. Default value: None.

    flow_func : function
        A function for computing the maximum flow among a pair of nodes.
        The function has to accept at least three parameters: a Digraph, 
        a source node, and a target node. And return a residual network 
        that follows NetworkX conventions (see :meth:`maximum_flow` for 
        details). If flow_func is None, the default maximum flow function 
        (:meth:`edmonds_karp`) is used. See below for details. The
        choice of the default function may change from version
        to version and should not be relied on. Default value: None.

    Returns
    -------
    K : integer
        Node connectivity of G, or local node connectivity if source
        and target were provided

    Examples
    --------
    >>> # Platonic icosahedral graph is 5-node-connected
    >>> G = nx.icosahedral_graph()
    >>> nx.node_connectivity(G)
    5
    >>> nx.node_connectivity(G, 3, 7)
    5

    You can use alternative flow algorithms for the underlying
    maximum flow compututions. See meth:`local_node_connectivity`
    and Notes for details.

    >>> nx.node_connectivity(G, flow_func=nx.shortest_augmenting_path)
    5
    >>> nx.node_connectivity(G, 3, 7, flow_func=nx.shortest_augmenting_path)
    5

    Notes
    -----
    This is a flow based implementation of node connectivity. The
    algorithm works by solving `O((n-\delta-1+\delta(\delta-1)/2)` 
    maximum flow problems on an auxiliary digraph. Where `\delta` 
    is the minimum degree of G. For details about the auxiliary 
    digraph and the computation of local node connectivity see 
    :meth:`local_node_connectivity`. This implementation is based 
    on algorithm 11 in [1]_.

    You can use alternative flow algorithms for the underlying maximum
    flow computation. In dense networks the algorithm
    :meth:`shortest_augmenting_path` will usually perform better
    than the default :meth:`edmonds_karp`, which is faster for
    sparse networks with highly skewed degree distributions.

    See also
    --------
    :meth:`local_node_connectivity`
    :meth:`edge_connectivity`
    :meth:`local_edge_connectivity`
    :meth:`maximum_flow`
    :meth:`edmonds_karp`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`
    :meth:`stoer_wagner`

    References
    ----------
    .. [1] Abdol-Hossein Esfahanian. Connectivity Algorithms.
        http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf

    """
    # Local node connectivity
    if s is not None and t is not None:
        if s not in G:
            raise nx.NetworkXError('node %s not in graph' % s)
        if t not in G:
            raise nx.NetworkXError('node %s not in graph' % t)
        return local_node_connectivity(G, s, t, flow_func=flow_func)

    # Global node connectivity
    if G.is_directed():
        if not nx.is_weakly_connected(G):
            return 0
        iter_func = itertools.permutations
        # It is necessary to consider both predecessors
        # and successors for directed graphs
        def neighbors(v):
            return itertools.chain.from_iterable([G.predecessors_iter(v),
                                                  G.successors_iter(v)])
    else:
        if not nx.is_connected(G):
            return 0
        iter_func = itertools.combinations
        neighbors = G.neighbors_iter

    # Reuse the auxiliary digraph and the residual network
    H, mapping = build_auxiliary_node_connectivity(G)
    R = build_residual_network(H, 'capacity')
    kwargs = dict(flow_func=flow_func, aux_digraph=H, mapping=mapping,
                  residual=R)

    # Initial guess \kappa = n - 1
    K = G.order() - 1
    # Pick a node with minimum degree
    degree = G.degree()
    v = next(n for n, d in degree.items() if d == min(degree.values()))
    # compute local node connectivity with all its non-neighbors nodes
    for w in set(G) - set(neighbors(v)) - set([v]):
        kwargs['cutoff'] = K
        K = min(K, local_node_connectivity(G, v, w, **kwargs))
    # Same for non adjacent pairs of neighbors of v
    for x, y in iter_func(neighbors(v), 2):
        if y in G[x]:
            continue
        kwargs['cutoff'] = K
        K = min(K, local_node_connectivity(G, x, y, **kwargs)) 

    return K


def average_node_connectivity(G, flow_func=None):
    r"""Returns the average connectivity of a graph G.

    The average connectivity `\bar{\kappa}` of a graph G is the average
    of local node connectivity over all pairs of nodes of G [1]_ .

    .. math::

        \bar{\kappa}(G) = \frac{\sum_{u,v} \kappa_{G}(u,v)}{{n \choose 2}}

    Parameters
    ----------

    G : NetworkX graph
        Undirected graph

    flow_func : function
        A function for computing the maximum flow among a pair of nodes.
        The function has to accept at least three parameters: a Digraph, 
        a source node, and a target node. And return a residual network 
        that follows NetworkX conventions (see :meth:`maximum_flow` for 
        details). If flow_func is None, the default maximum flow function 
        (:meth:`edmonds_karp`) is used. See :meth:`node_connectivity` for
        details. The choice of the default function may change from version
        to version and should not be relied on. Default value: None.

    Returns
    -------
    K : float
        Average node connectivity

    See also
    --------
    :meth:`local_node_connectivity`
    :meth:`edge_connectivity`
    :meth:`local_edge_connectivity`
    :meth:`maximum_flow`
    :meth:`edmonds_karp`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    References
    ----------
    .. [1]  Beineke, L., O. Oellermann, and R. Pippert (2002). The average
            connectivity of a graph. Discrete mathematics 252(1-3), 31-45.
            http://www.sciencedirect.com/science/article/pii/S0012365X01001807

    """
    if G.is_directed():
        iter_func = itertools.permutations
    else:
        iter_func = itertools.combinations

    # Reuse the auxiliary digraph and the residual network
    H, mapping = build_auxiliary_node_connectivity(G)
    R = build_residual_network(H, 'capacity')
    kwargs = dict(flow_func=flow_func, aux_digraph=H, mapping=mapping,
                  residual=R)

    num, den = 0, 0
    for u, v in iter_func(G, 2):
        num += local_node_connectivity(G, u, v, **kwargs)
        den += 1

    if den == 0: # Null Graph
        return 0
    return num / den


def all_pairs_node_connectivity_matrix(G, nodelist=None, flow_func=None):
    """Return a numpy 2d ndarray with node connectivity between all pairs
    of nodes.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    nodelist: list
        Ordering of nodes for rows and columns of matrix

    flow_func : function
        A function for computing the maximum flow among a pair of nodes.
        The function has to accept at least three parameters: a Digraph, 
        a source node, and a target node. And return a residual network 
        that follows NetworkX conventions (see :meth:`maximum_flow` for 
        details). If flow_func is None, the default maximum flow function 
        (:meth:`edmonds_karp`) is used. See below for details. The
        choice of the default function may change from version
        to version and should not be relied on. Default value: None.

    Returns
    -------
    K : 2d numpy ndarray
         node connectivity between all pairs of nodes.

    See also
    --------
    :meth:`local_node_connectivity`
    :meth:`edge_connectivity`
    :meth:`local_edge_connectivity`
    :meth:`maximum_flow`
    :meth:`edmonds_karp`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    """
    import numpy as np
    if nodelist is None:
        nodelist = G

    nlen = len(nodelist)

    if nlen == 0:
        raise nx.NetworkXError("Graph has no nodes or edges")

    if len(nodelist) != len(set(nodelist)):
        msg = "Ambiguous ordering: `nodelist` contained duplicates."
        raise nx.NetworkXError(msg)

    n = G.order()
    M = np.zeros((n, n), dtype=int)
    # Reuse auxiliary digraph and residual network
    D, mapping = build_auxiliary_node_connectivity(G)
    R = build_residual_network(D, 'capacity')
    kwargs = dict(flow_func=flow_func, aux_digraph=D, mapping=mapping,
                  residual=R)

    if G.is_directed():
        for u, v in itertools.permutations(G, 2):
            K = local_node_connectivity(G, u, v, **kwargs)
            M[mapping[u], mapping[v]] = K
    else:
        for u, v in itertools.combinations(G, 2):
            K = local_node_connectivity(G, u, v, **kwargs)
            M[mapping[u], mapping[v]] = M[mapping[v], mapping[u]] = K

    return M


def local_edge_connectivity(G, u, v, flow_func=None, aux_digraph=None,
                            residual=None, cutoff=None):
    r"""Returns local edge connectivity for nodes s and t in G.

    Local edge connectivity for two nodes s and t is the minimum number
    of edges that must be removed to disconnect them.

    This is a flow based implementation of edge connectivity. We compute the
    maximum flow on an auxiliary digraph build from the original
    network (see below for details). This is equal to the local edge
    connectivity because the value of a maximum s-t-flow is equal to the
    capacity of a minimum s-t-cut (Ford and Fulkerson theorem) [1]_ .

    Parameters
    ----------
    G : NetworkX graph
        Undirected or directed graph

    s : node
        Source node

    t : node
        Target node

    flow_func : function
        A function for computing the maximum flow among a pair of nodes.
        The function has to accept at least three parameters: a Digraph, 
        a source node, and a target node. And return a residual network 
        that follows NetworkX conventions (see :meth:`maximum_flow` for 
        details). If flow_func is None, the default maximum flow function 
        (:meth:`edmonds_karp`) is used. See below for details. The
        choice of the default function may change from version
        to version and should not be relied on. Default value: None.

    aux_digraph : NetworkX DiGraph
        Auxiliary digraph to compute flow based edge connectivity. If None
        the auxiliary digraph is build. Default value: None.

    residual : NetworkX DiGraph
        Residual network to compute maximum flow. If provided it will be
        reused instead of recreated. Default value: None.

    cutoff : integer, float
        If specified, the maximum flow algorithm will terminate when the 
        flow value reaches or exceeds the cutoff. This is only for the
        algorithms that support the cutoff parameter: :meth:`edmonds_karp` 
        and :meth:`shortest_augmenting_path`. Other algorithms will ignore
        this parameter. Default value: None.

    Returns
    -------
    K : integer
        local edge connectivity for nodes s and t

    Examples
    --------
    >>> # Platonic icosahedral graph has edge connectivity 5
    >>> # for each non adjacent node pair
    >>> G = nx.icosahedral_graph()
    >>> nx.local_edge_connectivity(G, 0, 6)
    5

    If you need to compute local connectivity on several pairs of
    nodes in the same graph, it is recommended that you reuse the
    data structures that NetworkX uses for computing the maximum 
    flow and the node connectivity: the auxiliary digraph for
    node connectivity, and the residual network for maximum flow:

    >>> # Import the function for building the auxiliary digraph
    >>> from networkx.algorithms.connectivity.utils import (
    ...     build_auxiliary_edge_connectivity)
    >>> H = build_auxiliary_edge_connectivity(G)
    >>> # Import the function for building the resudual network
    >>> from networkx.algorithms.flow.utils import build_residual_network
    >>> R = build_residual_network(H, 'capacity')
    >>> # You can reuse them by passing them as parameters
    >>> kwargs = dict(aux_digraph=H, residual=R)
    >>> nx.local_edge_connectivity(G, 0, 6, **kwargs)
    5

    You can also use alternative flow algorithms for computing edge
    connectivity. For instance, in dense networks the algorithm
    :meth:`shortest_augmenting_path` will usually perform better than
    the default :meth:`edmonds_karp` which is faster for sparse
    network with highly skewed degree distributions:

    >>> nx.local_edge_connectivity(G, 0, 6, flow_func=nx.shortest_augmenting_path)
    5

    Notes
    -----
    This is a flow based implementation of edge connectivity. We compute the
    maximum flow using, by default, the :meth:`edmonds_karp` algorithm on an 
    auxiliary digraph build from the original input graph:

    If the input graph is undirected, we replace each edge (u,v) with
    two reciprocal arcs `(u,v)` and `(v,u)` and then we set the attribute
    'capacity' for each arc to 1. If the input graph is directed we simply
    add the 'capacity' attribute. This is an implementation of algorithm 1
    in [1]_.

    The maximum flow in the auxiliary network is equal to the local edge
    connectivity because the value of a maximum s-t-flow is equal to the
    capacity of a minimum s-t-cut (Ford and Fulkerson theorem).

    See also
    --------
    :meth:`edge_connectivity`
    :meth:`local_node_connectivity`
    :meth:`node_connectivity`
    :meth:`maximum_flow`
    :meth:`edmonds_karp`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    References
    ----------
    .. [1] Abdol-Hossein Esfahanian. Connectivity Algorithms.
        http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf

    """
    if flow_func is None:
        flow_func = default_flow_func

    if aux_digraph is None:
        H = build_auxiliary_edge_connectivity(G)
    else:
        H = aux_digraph

    kwargs = dict(flow_func=flow_func, residual=residual)
    if flow_func is shortest_augmenting_path:
        kwargs['cutoff'] = cutoff
        kwargs['two_phase'] = True
    elif flow_func is edmonds_karp:
        kwargs['cutoff'] = cutoff

    return nx.maximum_flow_value(H, u, v, **kwargs)

def edge_connectivity(G, s=None, t=None, flow_func=None):
    r"""Returns the edge connectivity of the graph or digraph G.

    The edge connectivity is equal to the minimum number of edges that
    must be removed to disconnect G or render it trivial. If source
    and target nodes are provided, this function returns the local edge
    connectivity: the minimum number of edges that must be removed to
    break all paths from source to target in G.

    Parameters
    ----------
    G : NetworkX graph
        Undirected or directed graph

    s : node
        Source node. Optional. Default value: None.

    t : node
        Target node. Optional. Default value: None.

    flow_func : function
        A function for computing the maximum flow among a pair of nodes.
        The function has to accept at least three parameters: a Digraph, 
        a source node, and a target node. And return a residual network 
        that follows NetworkX conventions (see :meth:`maximum_flow` for 
        details). If flow_func is None, the default maximum flow function 
        (:meth:`edmonds_karp`) is used. See below for details. The
        choice of the default function may change from version
        to version and should not be relied on. Default value: None.

    Returns
    -------
    K : integer
        Edge connectivity for G, or local edge connectivity if source
        and target were provided

    Examples
    --------
    >>> # Platonic icosahedral graph is 5-edge-connected
    >>> G = nx.icosahedral_graph()
    >>> nx.edge_connectivity(G)
    5

    You can use alternative flow algorithms for the underlying
    maximum flow compututions. See meth:`local_edge_connectivity`
    and Notes for details.

    >>> nx.edge_connectivity(G, flow_func=nx.shortest_augmenting_path)
    5
    >>> nx.edge_connectivity(G, 3, 7, flow_func=nx.shortest_augmenting_path)
    5

    Notes
    -----
    This is a flow based implementation of global edge connectivity.
    For undirected graphs the algorithm works by finding a 'small' 
    dominating set of nodes of G (see algorithm 7 in [1]_ ) and 
    computing local maximum flow (see :meth:`local_edge_connectivity`)
    between an arbitrary node in the dominating set and the rest of 
    nodes in it. This is an implementation of algorithm 6 in [1]_ . 
    For directed graphs, the algorithm does n calls to the maximum 
    flow function. This is an implementation of algorithm 8 in [1]_ .

    You can use alternative flow algorithms for the underlying 
    maximum flow computation. In dense networks the algorithm 
    :meth:`shortest_augmenting_path` will usually perform better 
    than the default :meth:`edmonds_karp`, which is faster for 
    sparse networks with highly skewed degree distributions.

    See also
    --------
    :meth:`edge_connectivity`
    :meth:`local_node_connectivity`
    :meth:`node_connectivity`
    :meth:`maximum_flow`
    :meth:`edmonds_karp`
    :meth:`preflow_push`
    :meth:`shortest_augmenting_path`

    References
    ----------
    .. [1] Abdol-Hossein Esfahanian. Connectivity Algorithms.
        http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf

    """
    # Local edge connectivity
    if s is not None and t is not None:
        if s not in G:
            raise nx.NetworkXError('node %s not in graph' % s)
        if t not in G:
            raise nx.NetworkXError('node %s not in graph' % t)
        return local_edge_connectivity(G, s, t, flow_func=flow_func)

    # Global edge connectivity
    # reuse auxiliary digraph and residual network
    H = build_auxiliary_edge_connectivity(G)
    R = build_residual_network(H, 'capacity')
    kwargs = dict(flow_func=flow_func, aux_digraph=H, residual=R)

    if G.is_directed():
        # Algorithm 8 in [1]
        if not nx.is_weakly_connected(G):
            return 0

        # initial value for \lambda is minimum degree
        L = min(G.degree().values())
        nodes = G.nodes()
        n = len(nodes)
        for i in range(n):
            kwargs['cutoff'] = L
            try:
                L = min(L, local_edge_connectivity(G, nodes[i], nodes[i+1],
                                                   **kwargs))
            except IndexError: # last node!
                L = min(L, local_edge_connectivity(G, nodes[i], nodes[0],
                                                   **kwargs))
        return L
    else: # undirected
        # Algorithm 6 in [1]
        if not nx.is_connected(G):
            return 0

        # initial value for \lambda is minimum degree
        L = min(G.degree().values())
        # A dominating set is \lambda-covering
        # We need a dominating set with at least two nodes
        for node in G:
            D = nx.dominating_set(G, start_with=node)
            v = D.pop()
            if D:
                break
        else:
            # in complete graphs the dominating sets will always be of one node
            # thus we return min degree
            return L
        for w in D:
            kwargs['cutoff'] = L
            L = min(L, local_edge_connectivity(G, v, w, **kwargs))

        return L
