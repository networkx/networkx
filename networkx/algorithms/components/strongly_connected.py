"""Strongly connected components."""

import networkx as nx
from networkx.utils.decorators import not_implemented_for

__all__ = [
    "number_strongly_connected_components",
    "strongly_connected_components",
    "is_strongly_connected",
    "kosaraju_strongly_connected_components",
    "condensation",
]


@not_implemented_for("undirected")
@nx._dispatchable
def strongly_connected_components(G):
    """Generate nodes in strongly connected components of graph.

    Parameters
    ----------
    G : NetworkX Graph
        A directed graph.

    Returns
    -------
    comp : generator of sets
        A generator of sets of nodes, one for each strongly connected
        component of G.

    Raises
    ------
    NetworkXNotImplemented
        If G is undirected.

    Examples
    --------
    Generate a sorted list of strongly connected components, largest first.

    >>> G = nx.cycle_graph(4, create_using=nx.DiGraph())
    >>> nx.add_cycle(G, [10, 11, 12])
    >>> [
    ...     len(c)
    ...     for c in sorted(nx.strongly_connected_components(G), key=len, reverse=True)
    ... ]
    [4, 3]

    If you only want the largest component, it's more efficient to
    use max instead of sort.

    >>> largest = max(nx.strongly_connected_components(G), key=len)

    See Also
    --------
    connected_components
    weakly_connected_components
    kosaraju_strongly_connected_components

    Notes
    -----
    Iterative version of Tarjan's algorithm using the improvements
    described by Tarjan and Zwick in their survey [1]_, plus a trick
    borrowed from the Rust implementation of the WebGraph framework [2]_.

    References
    ----------
    .. [1] Robert E. Tarjan and Uri Zwick, "Finding strong components using
       depth-first search", European Journal of Combinatorics, 119, 2024.
       https://doi.org/10.1016/j.ejc.2023.103815

    .. [2] Tommaso Fontana, Sebastiano Vigna, and Stefano Zacchiroli,
       "WebGraph: The next generation (is in Rust)", Companion Proceedings
       of the ACM Web Conference 2024, pp. 686-689, 2024.
       https://doi.org/10.1145/3589335.3651581
    """
    N = len(G)
    if N == 0:
        return
    adj = G._adj
    # lowlink[v] doubles as preorder timestamp and low-link: on first visit
    # it is set to v's preorder number and may then only decrease, via
    # back / cross arcs, toward the preorder number of some ancestor.
    lowlink = {}
    scc_found = set()
    # Parallel stacks representing the current DFS path. Each frame holds
    # (node, iterator over remaining successors, lead flag). A stack
    # of triples is measurably slower.
    dfs_v = []
    dfs_it = []
    dfs_lead = []
    # Nodes popped from the DFS path but not yet assigned to any SCC.
    comp_stack = []
    index = 0

    for source in G:
        if source in lowlink:
            continue
        index += 1
        root_low = index
        lowlink[source] = index
        dfs_v.append(source)
        dfs_it.append(iter(adj[source]))
        dfs_lead.append(True)

        while dfs_v:
            v = dfs_v[-1]
            for w in dfs_it[-1]:
                if w not in lowlink:
                    # Tree arc: previsit w and descend.
                    index += 1
                    lowlink[w] = index
                    dfs_v.append(w)
                    dfs_it.append(iter(adj[w]))
                    dfs_lead.append(True)
                    break
                # Back/cross arc.
                if w not in scc_found and lowlink[v] > lowlink[w]:
                    dfs_lead[-1] = False
                    lowlink[v] = lowlink[w]
                    # Early exit: every node has been preordered during
                    # this DFS tree and v has just linked back to the
                    # root, so the whole graph is a single SCC.
                    if lowlink[v] == root_low and index == N:
                        scc = set(comp_stack)
                        scc.update(dfs_v)
                        yield scc
                        return
            else:
                # All successors of v processed: postvisit.
                dfs_v.pop()
                dfs_it.pop()
                if dfs_lead.pop():
                    # v is an SCC root: pull its members off comp_stack.
                    v_low = lowlink[v]
                    scc = {v}
                    while comp_stack and lowlink[comp_stack[-1]] >= v_low:
                        scc.add(comp_stack.pop())
                    scc_found.update(scc)
                    yield scc
                else:
                    # v is not a root: park it on comp_stack and propagate
                    # its lowlink to the parent frame.
                    comp_stack.append(v)
                    parent = dfs_v[-1]
                    if lowlink[parent] > lowlink[v]:
                        dfs_lead[-1] = False
                        lowlink[parent] = lowlink[v]


@not_implemented_for("undirected")
@nx._dispatchable
def kosaraju_strongly_connected_components(G, source=None):
    """Generate nodes in strongly connected components of graph.

    Parameters
    ----------
    G : NetworkX Graph
        A directed graph.

    source : node, optional (default=None)
        Specify a node from which to start the depth-first search.
        If not provided, the algorithm will start from an arbitrary node.

    Yields
    ------
    set
        A set of all nodes in a strongly connected component of `G`.

    Raises
    ------
    NetworkXNotImplemented
        If `G` is undirected.

    NetworkXError
        If `source` is not a node in `G`.

    Examples
    --------
    Generate a list of strongly connected components of a graph:

    >>> G = nx.cycle_graph(4, create_using=nx.DiGraph())
    >>> nx.add_cycle(G, [10, 11, 12])
    >>> sorted(nx.kosaraju_strongly_connected_components(G), key=len, reverse=True)
    [{0, 1, 2, 3}, {10, 11, 12}]

    If you only want the largest component, it's more efficient to
    use `max()` instead of `sorted()`.

    >>> max(nx.kosaraju_strongly_connected_components(G), key=len)
    {0, 1, 2, 3}

    See Also
    --------
    strongly_connected_components

    Notes
    -----
    Uses Kosaraju's algorithm.
    """
    post = list(nx.dfs_postorder_nodes(G.reverse(copy=False), source=source))
    n = len(post)
    seen = set()
    while post and len(seen) < n:
        r = post.pop()
        if r in seen:
            continue
        new = {r}
        seen.add(r)
        stack = [r]
        while stack and len(seen) < n:
            v = stack.pop()
            for w in G._adj[v]:
                if w not in seen:
                    new.add(w)
                    seen.add(w)
                    stack.append(w)
        yield new


@not_implemented_for("undirected")
@nx._dispatchable
def number_strongly_connected_components(G):
    """Returns number of strongly connected components in graph.

    Parameters
    ----------
    G : NetworkX graph
       A directed graph.

    Returns
    -------
    n : integer
       Number of strongly connected components

    Raises
    ------
    NetworkXNotImplemented
        If G is undirected.

    Examples
    --------
    >>> G = nx.DiGraph(
    ...     [(0, 1), (1, 2), (2, 0), (2, 3), (4, 5), (3, 4), (5, 6), (6, 3), (6, 7)]
    ... )
    >>> nx.number_strongly_connected_components(G)
    3

    See Also
    --------
    strongly_connected_components
    number_connected_components
    number_weakly_connected_components

    Notes
    -----
    For directed graphs only.
    """
    return sum(1 for scc in strongly_connected_components(G))


@not_implemented_for("undirected")
@nx._dispatchable
def is_strongly_connected(G):
    """Test directed graph for strong connectivity.

    A directed graph is strongly connected if and only if every vertex in
    the graph is reachable from every other vertex.

    Parameters
    ----------
    G : NetworkX Graph
       A directed graph.

    Returns
    -------
    connected : bool
      True if the graph is strongly connected, False otherwise.

    Examples
    --------
    >>> G = nx.DiGraph([(0, 1), (1, 2), (2, 3), (3, 0), (2, 4), (4, 2)])
    >>> nx.is_strongly_connected(G)
    True
    >>> G.remove_edge(2, 3)
    >>> nx.is_strongly_connected(G)
    False

    Raises
    ------
    NetworkXNotImplemented
        If G is undirected.

    See Also
    --------
    is_weakly_connected
    is_semiconnected
    is_connected
    is_biconnected
    strongly_connected_components

    Notes
    -----
    For directed graphs only.
    """
    if len(G) == 0:
        raise nx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph."""
        )

    return len(next(strongly_connected_components(G))) == len(G)


@not_implemented_for("undirected")
@nx._dispatchable(returns_graph=True)
def condensation(G, scc=None):
    """Returns the condensation of G.

    The condensation of G is the graph with each of the strongly connected
    components contracted into a single node.

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph.

    scc:  list or generator (optional, default=None)
       Strongly connected components. If provided, the elements in
       `scc` must partition the nodes in `G`. If not provided, it will be
       calculated as scc=nx.strongly_connected_components(G).

    Returns
    -------
    C : NetworkX DiGraph
       The condensation graph C of G.  The node labels are integers
       corresponding to the index of the component in the list of
       strongly connected components of G.  C has a graph attribute named
       'mapping' with a dictionary mapping the original nodes to the
       nodes in C to which they belong.  Each node in C also has a node
       attribute 'members' with the set of original nodes in G that
       form the SCC that the node in C represents.

    Raises
    ------
    NetworkXNotImplemented
        If G is undirected.

    Examples
    --------
    Contracting two sets of strongly connected nodes into two distinct SCC
    using the barbell graph.

    >>> G = nx.barbell_graph(4, 0)
    >>> G.remove_edge(3, 4)
    >>> G = nx.DiGraph(G)
    >>> H = nx.condensation(G)
    >>> H.nodes.data()
    NodeDataView({0: {'members': {0, 1, 2, 3}}, 1: {'members': {4, 5, 6, 7}}})
    >>> H.graph["mapping"]
    {0: 0, 1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 1}

    Contracting a complete graph into one single SCC.

    >>> G = nx.complete_graph(7, create_using=nx.DiGraph)
    >>> H = nx.condensation(G)
    >>> H.nodes
    NodeView((0,))
    >>> H.nodes.data()
    NodeDataView({0: {'members': {0, 1, 2, 3, 4, 5, 6}}})

    Notes
    -----
    After contracting all strongly connected components to a single node,
    the resulting graph is a directed acyclic graph.

    """
    if scc is None:
        scc = nx.strongly_connected_components(G)
    mapping = {}
    members = {}
    C = nx.DiGraph()
    # Add mapping dict as graph attribute
    C.graph["mapping"] = mapping
    if len(G) == 0:
        return C
    for i, component in enumerate(scc):
        members[i] = component
        mapping.update((n, i) for n in component)
    number_of_components = i + 1
    C.add_nodes_from(range(number_of_components))
    C.add_edges_from(
        (mapping[u], mapping[v]) for u, v in G.edges() if mapping[u] != mapping[v]
    )
    # Add a list of members (ie original nodes) to each node (ie scc) in C.
    nx.set_node_attributes(C, members, "members")
    return C
