# -*- coding: utf-8 -*-
"""
Flow based connectivity algorithms
"""
import itertools
import networkx as nx

__author__ = '\n'.join(['Jordi Torrents <jtorrents@milnou.net>'])

__all__ = [ 'average_node_connectivity',
            'local_node_connectivity',
            'node_connectivity',
            'local_edge_connectivity',
            'edge_connectivity',
            'all_pairs_node_connectivity_matrix',
            'dominating_set',
            ]

def average_node_connectivity(G):
    r"""Returns the average connectivity of a graph G.

    The average connectivity `\bar{\kappa}` of a graph G is the average 
    of local node connectivity over all pairs of nodes of G [1]_ .

    .. math::

        \bar{\kappa}(G) = \frac{\sum_{u,v} \kappa_{G}(u,v)}{{n \choose 2}}

    Parameters
    ----------

    G : NetworkX graph
        Undirected graph

    Returns
    -------
    K : float
        Average node connectivity

    See also
    --------
    local_node_connectivity
    node_connectivity
    local_edge_connectivity
    edge_connectivity
    max_flow
    ford_fulkerson 

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

    H, mapping = _aux_digraph_node_connectivity(G)
    num = 0.
    den = 0.
    for u,v in iter_func(G, 2):
        den += 1
        num += local_node_connectivity(G, u, v, aux_digraph=H, mapping=mapping)
    
    if den == 0: # Null Graph
        return 0
    return num/den

def _aux_digraph_node_connectivity(G):
    r""" Creates a directed graph D from an undirected graph G to compute flow
    based node connectivity.

    For an undirected graph G having `n` nodes and `m` edges we derive a 
    directed graph D with 2n nodes and 2m+n arcs by replacing each 
    original node `v` with two nodes `vA`,`vB` linked by an (internal) 
    arc in D. Then for each edge (u,v) in G we add two arcs (uB,vA) 
    and (vB,uA) in D. Finally we set the attribute capacity = 1 for each 
    arc in D [1].

    For a directed graph having `n` nodes and `m` arcs we derive a 
    directed graph D with 2n nodes and m+n arcs by replacing each 
    original node `v` with two nodes `vA`,`vB` linked by an (internal) 
    arc `(vA,vB)` in D. Then for each arc (u,v) in G we add one arc (uB,vA) 
    in D. Finally we set the attribute capacity = 1 for each arc in D.

    References
    ----------
    .. [1] Kammer, Frank and Hanjo Taubig. Graph Connectivity. in Brandes and 
        Erlebach, 'Network Analysis: Methodological Foundations', Lecture 
        Notes in Computer Science, Volume 3418, Springer-Verlag, 2005. 
        http://www.informatik.uni-augsburg.de/thi/personen/kammer/Graph_Connectivity.pdf
 
    """
    directed = G.is_directed()

    mapping = {}
    D = nx.DiGraph()
    for i,node in enumerate(G):
        mapping[node] = i
        D.add_node('%dA' % i,id=node)
        D.add_node('%dB' % i,id=node)
        D.add_edge('%dA' % i, '%dB' % i, capacity=1)
    
    edges = []
    for (source, target) in G.edges():
        edges.append(('%sB' % mapping[source], '%sA' % mapping[target]))
        if not directed:
            edges.append(('%sB' % mapping[target], '%sA' % mapping[source]))
    
    D.add_edges_from(edges, capacity=1)
    return D, mapping

def local_node_connectivity(G, s, t, aux_digraph=None, mapping=None):
    r"""Computes local node connectivity for nodes s and t.

    Local node connectivity for two non adjacent nodes s and t is the
    minimum number of nodes that must be removed (along with their incident 
    edges) to disconnect them.

    This is a flow based implementation of node connectivity. We compute the
    maximum flow on an auxiliary digraph build from the original input
    graph (see below for details). This is equal to the local node 
    connectivity because the value of a maximum s-t-flow is equal to the 
    capacity of a minimum s-t-cut (Ford and Fulkerson theorem) [1]_ .

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    s : node
        Source node

    t : node
        Target node

    aux_digraph : NetworkX DiGraph (default=None)
        Auxiliary digraph to compute flow based node connectivity. If None
        the auxiliary digraph is build.

    mapping : dict (default=None)
        Dictionary with a mapping of node names in G and in the auxiliary digraph.

    Returns
    -------
    K : integer
        local node connectivity for nodes s and t

    Examples
    --------
    >>> # Platonic icosahedral graph has node connectivity 5 
    >>> # for each non adjacent node pair
    >>> G = nx.icosahedral_graph()
    >>> nx.local_node_connectivity(G,0,6)
    5

    Notes
    -----
    This is a flow based implementation of node connectivity. We compute the
    maximum flow using the Ford and Fulkerson algorithm on an auxiliary digraph 
    build from the original input graph:

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
    node_connectivity
    all_pairs_node_connectivity_matrix
    local_edge_connectivity
    edge_connectivity
    max_flow
    ford_fulkerson 

    References
    ----------
    .. [1] Kammer, Frank and Hanjo Taubig. Graph Connectivity. in Brandes and 
        Erlebach, 'Network Analysis: Methodological Foundations', Lecture 
        Notes in Computer Science, Volume 3418, Springer-Verlag, 2005. 
        http://www.informatik.uni-augsburg.de/thi/personen/kammer/Graph_Connectivity.pdf
    
    """ 
    if aux_digraph is None or mapping is None:
        H, mapping = _aux_digraph_node_connectivity(G)
    else:
        H = aux_digraph 
    return nx.max_flow(H,'%sB' % mapping[s], '%sA' % mapping[t])

def node_connectivity(G, s=None, t=None):
    r"""Returns node connectivity for a graph or digraph G.

    Node connectivity is equal to the minimum number of nodes that 
    must be removed to disconnect G or render it trivial. If source 
    and target nodes are provided, this function returns the local node
    connectivity: the minimum number of nodes that must be removed to break
    all paths from source to target in G.

    This is a flow based implementation. The algorithm is based in 
    solving a number of max-flow problems (ie local st-node connectivity, 
    see local_node_connectivity) to determine the capacity of the
    minimum cut on an auxiliary directed network that corresponds to the 
    minimum node cut of G. It handles both directed and undirected graphs.
   
    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    s : node
        Source node. Optional (default=None)

    t : node
        Target node. Optional (default=None)

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
    
    Notes
    -----
    This is a flow based implementation of node connectivity. The 
    algorithm works by solving `O((n-\delta-1+\delta(\delta-1)/2)` max-flow 
    problems on an auxiliary digraph. Where `\delta` is the minimum degree 
    of G. For details about the auxiliary digraph and the computation of
    local node connectivity see local_node_connectivity.

    This implementation is based on algorithm 11 in [1]_. We use the Ford 
    and Fulkerson algorithm to compute max flow (see ford_fulkerson).
    
    See also
    --------
    local_node_connectivity
    all_pairs_node_connectivity_matrix
    local_edge_connectivity
    edge_connectivity
    max_flow
    ford_fulkerson 

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
        return local_node_connectivity(G, s, t)
    # Global node connectivity
    if G.is_directed():
        if not nx.is_weakly_connected(G):
            return 0
        iter_func = itertools.permutations
        # I think that it is necessary to consider both predecessors
        # and successors for directed graphs
        def neighbors(v):
            return itertools.chain.from_iterable([G.predecessors_iter(v),
                                                  G.successors_iter(v)])
    else:
        if not nx.is_connected(G):
            return 0
        iter_func = itertools.combinations
        neighbors = G.neighbors_iter
    # Initial guess \kappa = n - 1
    K = G.order()-1
    deg = G.degree()
    min_deg = min(deg.values())
    v = next(n for n,d in deg.items() if d==min_deg)
    # Reuse the auxiliary digraph
    H, mapping = _aux_digraph_node_connectivity(G)
    # compute local node connectivity with all non-neighbors nodes
    for w in set(G) - set(neighbors(v)) - set([v]):
        K = min(K, local_node_connectivity(G, v, w, 
                                            aux_digraph=H, mapping=mapping))
    # Same for non adjacent pairs of neighbors of v
    for x,y in iter_func(neighbors(v), 2):
        if y in G[x]: continue
        K = min(K, local_node_connectivity(G, x, y, 
                                            aux_digraph=H, mapping=mapping))
    return K

def all_pairs_node_connectivity_matrix(G):
    """Return a numpy 2d ndarray with node connectivity between all pairs
    of nodes.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    K : 2d numpy ndarray
         node connectivity between all pairs of nodes.

    See also
    --------
    local_node_connectivity
    node_connectivity
    local_edge_connectivity
    edge_connectivity
    max_flow
    ford_fulkerson 

    """
    try:
        import numpy
    except ImportError:
        raise ImportError(\
            "all_pairs_node_connectivity_matrix() requires NumPy")

    n = G.order()
    M = numpy.zeros((n, n), dtype=int)
    # Create auxiliary Digraph
    D, mapping = _aux_digraph_node_connectivity(G)

    if G.is_directed():
        for u, v in itertools.permutations(G, 2):
            K = local_node_connectivity(G, u, v, aux_digraph=D, mapping=mapping)
            M[mapping[u],mapping[v]] = K
    else:
        for u, v in itertools.combinations(G, 2):
            K = local_node_connectivity(G, u, v, aux_digraph=D, mapping=mapping)
            M[mapping[u],mapping[v]] = M[mapping[v],mapping[u]] = K

    return M

def _aux_digraph_edge_connectivity(G):
    """Auxiliary digraph for computing flow based edge connectivity
    
    If the input graph is undirected, we replace each edge (u,v) with
    two reciprocal arcs (u,v) and (v,u) and then we set the attribute 
    'capacity' for each arc to 1. If the input graph is directed we simply
    add the 'capacity' attribute. Part of algorithm 1 in [1]_ .
    
    References
    ----------
    .. [1] Abdol-Hossein Esfahanian. Connectivity Algorithms. (this is a 
        chapter, look for the reference of the book).
        http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf
    """
    if G.is_directed():
        if nx.get_edge_attributes(G, 'capacity'):
            return G
        D = G.copy()
        capacity = dict((e,1) for e in D.edges())
        nx.set_edge_attributes(D, 'capacity', capacity)
        return D
    else:
        D = G.to_directed()
        capacity = dict((e,1) for e in D.edges())
        nx.set_edge_attributes(D, 'capacity', capacity)
        return D

def local_edge_connectivity(G, u, v, aux_digraph=None):
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

    aux_digraph : NetworkX DiGraph (default=None)
        Auxiliary digraph to compute flow based edge connectivity. If None
        the auxiliary digraph is build.

    Returns
    -------
    K : integer
        local edge connectivity for nodes s and t

    Examples
    --------
    >>> # Platonic icosahedral graph has edge connectivity 5 
    >>> # for each non adjacent node pair
    >>> G = nx.icosahedral_graph()
    >>> nx.local_edge_connectivity(G,0,6)
    5

    Notes
    -----
    This is a flow based implementation of edge connectivity. We compute the
    maximum flow using the Ford and Fulkerson algorithm on an auxiliary digraph 
    build from the original graph:

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
    local_node_connectivity
    node_connectivity
    edge_connectivity
    max_flow
    ford_fulkerson 

    References
    ----------
    .. [1] Abdol-Hossein Esfahanian. Connectivity Algorithms.
        http://www.cse.msu.edu/~cse835/Papers/Graph_connectivity_revised.pdf
 
    """
    if aux_digraph is None: 
        H = _aux_digraph_edge_connectivity(G)
    else:
        H = aux_digraph
    return nx.max_flow(H, u, v)

def edge_connectivity(G, s=None, t=None):
    r"""Returns the edge connectivity of the graph or digraph G.

    The edge connectivity is equal to the minimum number of edges that 
    must be removed to disconnect G or render it trivial. If source 
    and target nodes are provided, this function returns the local edge
    connectivity: the minimum number of edges that must be removed to 
    break all paths from source to target in G.
    
    This is a flow based implementation. The algorithm is based in solving 
    a number of max-flow problems (ie local st-edge connectivity, see 
    local_edge_connectivity) to determine the capacity of the minimum 
    cut on an auxiliary directed network that corresponds to the minimum 
    edge cut of G. It handles both directed and undirected graphs.
 
    Parameters
    ----------
    G : NetworkX graph
        Undirected or directed graph

    s : node
        Source node. Optional (default=None)

    t : node
        Target node. Optional (default=None)
 
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

    Notes
    -----
    This is a flow based implementation of global edge connectivity. For
    undirected graphs the algorithm works by finding a 'small' dominating 
    set of nodes of G (see algorithm 7 in [1]_ ) and computing local max flow 
    (see local_edge_connectivity) between an arbitrary node in the dominating 
    set and the rest of nodes in it. This is an implementation of 
    algorithm 6 in [1]_ .

    For directed graphs, the algorithm does n calls to the max flow function.
    This is an implementation of algorithm 8 in [1]_ . We use the Ford and 
    Fulkerson algorithm to compute max flow (see ford_fulkerson).
    
    See also
    --------
    local_node_connectivity
    node_connectivity
    local_edge_connectivity
    max_flow
    ford_fulkerson 

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
        return local_edge_connectivity(G, s, t)
    # Global edge connectivity
    if G.is_directed():
        # Algorithm 8 in [1]
        if not nx.is_weakly_connected(G):
            return 0
        # initial value for lambda is min degree (\delta(G))
        L = min(G.degree().values())
        # reuse auxiliary digraph
        H = _aux_digraph_edge_connectivity(G)
        nodes = G.nodes()
        n = len(nodes)
        for i in range(n):
            try:
                L = min(L, local_edge_connectivity(G, nodes[i], 
                                                    nodes[i+1], aux_digraph=H))
            except IndexError: # last node!
                L = min(L, local_edge_connectivity(G, nodes[i], 
                                                    nodes[0], aux_digraph=H))
        return L
    else: # undirected
        # Algorithm 6 in [1]
        if not nx.is_connected(G):
            return 0
        # initial value for lambda is min degree (\delta(G))
        L = min(G.degree().values())
        # reuse auxiliary digraph
        H = _aux_digraph_edge_connectivity(G)
        # A dominating set is \lambda-covering
        # We need a dominating set with at least two nodes
        for node in G:
            D = dominating_set(G, start_with=node)
            v = D.pop()
            if D: break
        else: 
            # in complete graphs the dominating sets will always be of one node
            # thus we return min degree
            return L
        for w in D:
            L = min(L, local_edge_connectivity(G, v, w, aux_digraph=H))
        return L

def dominating_set(G, start_with=None):
    # Algorithm 7 in [1]
    all_nodes = set(G)
    if start_with is None:
        v = set(G).pop() # pick a node
    else:
        if start_with not in G:
            raise nx.NetworkXError('node %s not in G' % start_with)
        v = start_with
    D = set([v])
    ND = set([nbr for nbr in G[v]])
    other = all_nodes - ND - D
    while other:
        w = other.pop()
        D.add(w)
        ND.update([nbr for nbr in G[w] if nbr not in D])
        other = all_nodes - ND - D
    return D

def is_dominating_set(G, nbunch):
    # Proposed by Dan on the mailing list
    allnodes=set(G)
    testset=set(n for n in nbunch if n in G)
    nbrs=set()
    for n in testset:
        nbrs.update(G[n])
    if nbrs - allnodes:  # some nodes left--not dominating
        return False
    else:
        return True

