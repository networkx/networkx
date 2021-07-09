"""Strongly connected components."""
import networkx as nx
from networkx.utils.decorators import not_implemented_for

__all__ = [
    "number_strongly_connected_components",
    "strongly_connected_components",
    "is_strongly_connected",
    "strongly_connected_components_recursive",
    "kosaraju_strongly_connected_components",
    "condensation",
]


@not_implemented_for("undirected")
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
    Uses Tarjan's algorithm[1]_ with Nuutila's modifications[2]_.
    Nonrecursive version of algorithm.

    References
    ----------
    .. [1] Depth-first search and linear graph algorithms, R. Tarjan
       SIAM Journal of Computing 1(2):146-160, (1972).

    .. [2] On finding the strongly connected components in a directed graph.
       E. Nuutila and E. Soisalon-Soinen
       Information Processing Letters 49(1): 9-14, (1994)..

    """
    preorder = {}
    lowlink = {}
    scc_found = set()
    scc_queue = []
    i = 0  # Preorder counter
    for source in G:
        if source not in scc_found:
            queue = [source]
            while queue:
                v = queue[-1]
                if v not in preorder:
                    i = i + 1
                    preorder[v] = i
                done = True
                for w in G[v]:
                    if w not in preorder:
                        queue.append(w)
                        done = False
                        break
                if done:
                    lowlink[v] = preorder[v]
                    for w in G[v]:
                        if w not in scc_found:
                            if preorder[w] > preorder[v]:
                                lowlink[v] = min([lowlink[v], lowlink[w]])
                            else:
                                lowlink[v] = min([lowlink[v], preorder[w]])
                    queue.pop()
                    if lowlink[v] == preorder[v]:
                        scc = {v}
                        while scc_queue and preorder[scc_queue[-1]] > preorder[v]:
                            k = scc_queue.pop()
                            scc.add(k)
                        scc_found.update(scc)
                        yield scc
                    else:
                        scc_queue.append(v)


@not_implemented_for("undirected")
def kosaraju_strongly_connected_components(G, source=None):
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
    ...     for c in sorted(
    ...         nx.kosaraju_strongly_connected_components(G), key=len, reverse=True
    ...     )
    ... ]
    [4, 3]

    If you only want the largest component, it's more efficient to
    use max instead of sort.

    >>> largest = max(nx.kosaraju_strongly_connected_components(G), key=len)

    See Also
    --------
    strongly_connected_components

    Notes
    -----
    Uses Kosaraju's algorithm.

    """
    post = list(nx.dfs_postorder_nodes(G.reverse(copy=False), source=source))

    seen = set()
    while post:
        r = post.pop()
        if r in seen:
            continue
        c = nx.dfs_preorder_nodes(G, r)
        new = {v for v in c if v not in seen}
        seen.update(new)
        yield new


@not_implemented_for("undirected")
def strongly_connected_components_recursive(G):
    """Generate nodes in strongly connected components of graph.

    Recursive version of algorithm.

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
    ...     for c in sorted(
    ...         nx.strongly_connected_components_recursive(G), key=len, reverse=True
    ...     )
    ... ]
    [4, 3]

    If you only want the largest component, it's more efficient to
    use max instead of sort.

    >>> largest = max(nx.strongly_connected_components_recursive(G), key=len)

    To create the induced subgraph of the components use:
    >>> S = [G.subgraph(c).copy() for c in nx.weakly_connected_components(G)]

    See Also
    --------
    connected_components

    Notes
    -----
    Uses Tarjan's algorithm[1]_ with Nuutila's modifications[2]_.

    References
    ----------
    .. [1] Depth-first search and linear graph algorithms, R. Tarjan
       SIAM Journal of Computing 1(2):146-160, (1972).

    .. [2] On finding the strongly connected components in a directed graph.
       E. Nuutila and E. Soisalon-Soinen
       Information Processing Letters 49(1): 9-14, (1994)..

    """

    def visit(v, cnt):
        root[v] = cnt
        visited[v] = cnt
        cnt += 1
        stack.append(v)
        for w in G[v]:
            if w not in visited:
                yield from visit(w, cnt)
            if w not in component:
                root[v] = min(root[v], root[w])
        if root[v] == visited[v]:
            component[v] = root[v]
            tmpc = {v}  # hold nodes in this component
            while stack[-1] != v:
                w = stack.pop()
                component[w] = root[v]
                tmpc.add(w)
            stack.remove(v)
            yield tmpc

    visited = {}
    component = {}
    root = {}
    cnt = 0
    stack = []
    for source in G:
        if source not in visited:
            yield from visit(source, cnt)


@not_implemented_for("undirected")
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

    return len(list(strongly_connected_components(G))[0]) == len(G)


@not_implemented_for("undirected")
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


@not_implemented_for("undirected")
def in_component(G, scc_comp):
    """Generate the IN component of a graph with respect to
    a given strongly connected component.

    Parameters
    ----------
    G : NetworkX Graph
        A directed graph.

    scc_comp : set
        A set of nodes belonging to a strongly connected
        component of G.

    Returns
    -------
    set
        A set of nodes belonging to the IN component with
        respect to `scc_comp`.

    Raises
    ------
    NetworkXNotImplemented
        If G is undirected.

    Notes
    -----
    The IN component is part of the Web's graph structure as
    described by Broder et al.[1]_.

    References
    ----------
    .. [1] Graph structure in the web,
       A. Broder, R. Kumar, F. Maghoul, P. Raghavan,
       S. Rajagopalan, R. Stata, A. Tomkins, J. Wiener
       Computer Networks, 33(1-6):309-320, (2000).

    """
    return in_or_out_component(G, scc_comp, comp_type="in")


@not_implemented_for("undirected")
def out_component(G, scc_comp):
    """Generate the OUT component of a graph with respect to
    a given strongly connected component.

    Parameters
    ----------
    G : NetworkX Graph
        A directed graph.

    scc_comp : set
        A set of nodes belonging to a strongly connected
        component of G.

    Returns
    -------
    set
        A set of nodes belonging to the OUT component with
        respect to `scc_comp`.

    Raises
    ------
    NetworkXNotImplemented
        If G is undirected.

    Notes
    -----
    The OUT component is part of the Web's graph structure as
    described by Broder et al.[1]_.

    References
    ----------
    .. [1] Graph structure in the web,
       A. Broder, R. Kumar, F. Maghoul, P. Raghavan,
       S. Rajagopalan, R. Stata, A. Tomkins, J. Wiener
       Computer Networks, 33(1-6):309-320, (2000).

    """
    return in_or_out_component(G, scc_comp, comp_type="out")


@not_implemented_for("undirected")
def in_or_out_component(G, scc_comp, comp_type):
    """Generate the IN/OUT component of a graph with respect to
    a given strongly connected component.

    Parameters
    ----------
    G : NetworkX Graph
        A directed graph.

    scc_comp : set
        A set of nodes belonging to a strongly connected
        component of G.

    comp_type : str
        Specify which component to return. If 'in', returns
        the IN component. If 'out', returns the OUT component.

    Returns
    -------
    comp : set
        A set of nodes belonging to the IN/OUT component with
        respect to `scc_comp`.

    Raises
    ------
    NetworkXNotImplemented
        If G is undirected.

    ValueError
        If `comp_type` is neither 'in' nor 'out'.

    Notes
    -----
    The IN/OUT component is part of the Web's graph structure as
    described by Broder et al.[1]_.

    References
    ----------
    .. [1] Graph structure in the web,
       A. Broder, R. Kumar, F. Maghoul, P. Raghavan,
       S. Rajagopalan, R. Stata, A. Tomkins, J. Wiener
       Computer Networks, 33(1-6):309-320, (2000).

    """
    import random

    # Gets a random node from the strongly connected component
    # as a root for executing BFS.
    random_scc_node = random.sample(scc_comp, 1)[0]

    visited = [random_scc_node]
    queue = [random_scc_node]
    while queue:
        node = queue.pop(0)

        if comp_type == "in":
            neighbors = G.predecessors(node)
        elif comp_type == "out":
            neighbors = G.successors(node)
        else:
            raise ValueError("Expect `comp_type` to be 'in' or 'out'.")

        for n in neighbors:
            if n not in visited:
                visited.append(n)
                queue.append(n)

    # `visited` contains the IN/OUT component together with the
    # strongly connected component. Use set difference to just
    # get the IN/OUT component.
    comp = set(visited).difference(scc_comp)
    return comp
