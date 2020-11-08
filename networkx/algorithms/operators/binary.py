"""
Operations on graphs including union, intersection, difference.
"""
import networkx as nx

__all__ = [
    "union",
    "compose",
    "disjoint_union",
    "intersection",
    "difference",
    "symmetric_difference",
    "full_join",
    "relational_compose",
]


def union(G, H, rename=(None, None), name=None):
    """Return the union of graphs G and H.

    Graphs G and H must be disjoint, otherwise an exception is raised.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph

    rename : bool , default=(None, None)
       Node names of G and H can be changed by specifying the tuple
       rename=('G-','H-') (for example).  Node "u" in G is then renamed
       "G-u" and "v" in H is renamed "H-v".

    name : string
       Specify the name for the union graph

    Returns
    -------
    U : A union graph with the same type as G.

    Notes
    -----
    To force a disjoint union with node relabeling, use
    disjoint_union(G,H) or convert_node_labels_to integers().

    Graph, edge, and node attributes are propagated from G and H
    to the union graph.  If a graph attribute is present in both
    G and H the value from H is used.

    See Also
    --------
    disjoint_union
    """
    if not G.is_multigraph() == H.is_multigraph():
        raise nx.NetworkXError("G and H must both be graphs or multigraphs.")
    # Union is the same type as G
    R = G.__class__()
    # add graph attributes, H attributes take precedent over G attributes
    R.graph.update(G.graph)
    R.graph.update(H.graph)

    # rename graph to obtain disjoint node labels
    def add_prefix(graph, prefix):
        if prefix is None:
            return graph

        def label(x):
            if isinstance(x, str):
                name = prefix + x
            else:
                name = prefix + repr(x)
            return name

        return nx.relabel_nodes(graph, label)

    G = add_prefix(G, rename[0])
    H = add_prefix(H, rename[1])
    if set(G) & set(H):
        raise nx.NetworkXError(
            "The node sets of G and H are not disjoint.",
            "Use appropriate rename=(Gprefix,Hprefix)" "or use disjoint_union(G,H).",
        )
    if G.is_multigraph():
        G_edges = G.edges(keys=True, data=True)
    else:
        G_edges = G.edges(data=True)
    if H.is_multigraph():
        H_edges = H.edges(keys=True, data=True)
    else:
        H_edges = H.edges(data=True)

    # add nodes
    R.add_nodes_from(G)
    R.add_nodes_from(H)
    # add edges
    R.add_edges_from(G_edges)
    R.add_edges_from(H_edges)
    # add node attributes
    for n in G:
        R.nodes[n].update(G.nodes[n])
    for n in H:
        R.nodes[n].update(H.nodes[n])

    return R


def disjoint_union(G, H):
    """Return the disjoint union of graphs G and H.

    This algorithm forces distinct integer node labels.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph

    Returns
    -------
    U : A union graph with the same type as G.

    Notes
    -----
    A new graph is created, of the same class as G.  It is recommended
    that G and H be either both directed or both undirected.

    The nodes of G are relabeled 0 to len(G)-1, and the nodes of H are
    relabeled len(G) to len(G)+len(H)-1.

    Graph, edge, and node attributes are propagated from G and H
    to the union graph.  If a graph attribute is present in both
    G and H the value from H is used.
    """
    R1 = nx.convert_node_labels_to_integers(G)
    R2 = nx.convert_node_labels_to_integers(H, first_label=len(R1))
    R = union(R1, R2)
    R.graph.update(G.graph)
    R.graph.update(H.graph)
    return R


def intersection(G, H):
    """Returns a new graph that contains only the edges that exist in
    both G and H.

    The node sets of H and G must be the same.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph.  G and H must have the same node sets.

    Returns
    -------
    GH : A new graph with the same type as G.

    Notes
    -----
    Attributes from the graph, nodes, and edges are not copied to the new
    graph.  If you want a new graph of the intersection of G and H
    with the attributes (including edge data) from G use remove_nodes_from()
    as follows

    >>> G = nx.path_graph(3)
    >>> H = nx.path_graph(5)
    >>> R = G.copy()
    >>> R.remove_nodes_from(n for n in G if n not in H)
    """
    # create new graph
    R = nx.create_empty_copy(G)

    if not G.is_multigraph() == H.is_multigraph():
        raise nx.NetworkXError("G and H must both be graphs or multigraphs.")
    if set(G) != set(H):
        raise nx.NetworkXError("Node sets of graphs are not equal")

    if G.number_of_edges() <= H.number_of_edges():
        if G.is_multigraph():
            edges = G.edges(keys=True)
        else:
            edges = G.edges()
        for e in edges:
            if H.has_edge(*e):
                R.add_edge(*e)
    else:
        if H.is_multigraph():
            edges = H.edges(keys=True)
        else:
            edges = H.edges()
        for e in edges:
            if G.has_edge(*e):
                R.add_edge(*e)
    return R


def difference(G, H):
    """Returns a new graph that contains the edges that exist in G but not in H.

    The node sets of H and G must be the same.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph.  G and H must have the same node sets.

    Returns
    -------
    D : A new graph with the same type as G.

    Notes
    -----
    Attributes from the graph, nodes, and edges are not copied to the new
    graph.  If you want a new graph of the difference of G and H with
    with the attributes (including edge data) from G use remove_nodes_from()
    as follows:

    >>> G = nx.path_graph(3)
    >>> H = nx.path_graph(5)
    >>> R = G.copy()
    >>> R.remove_nodes_from(n for n in G if n in H)
    """
    # create new graph
    if not G.is_multigraph() == H.is_multigraph():
        raise nx.NetworkXError("G and H must both be graphs or multigraphs.")
    R = nx.create_empty_copy(G)

    if set(G) != set(H):
        raise nx.NetworkXError("Node sets of graphs not equal")

    if G.is_multigraph():
        edges = G.edges(keys=True)
    else:
        edges = G.edges()
    for e in edges:
        if not H.has_edge(*e):
            R.add_edge(*e)
    return R


def symmetric_difference(G, H):
    """Returns new graph with edges that exist in either G or H but not both.

    The node sets of H and G must be the same.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph.  G and H must have the same node sets.

    Returns
    -------
    D : A new graph with the same type as G.

    Notes
    -----
    Attributes from the graph, nodes, and edges are not copied to the new
    graph.
    """
    # create new graph
    if not G.is_multigraph() == H.is_multigraph():
        raise nx.NetworkXError("G and H must both be graphs or multigraphs.")
    R = nx.create_empty_copy(G)

    if set(G) != set(H):
        raise nx.NetworkXError("Node sets of graphs not equal")

    gnodes = set(G)  # set of nodes in G
    hnodes = set(H)  # set of nodes in H
    nodes = gnodes.symmetric_difference(hnodes)
    R.add_nodes_from(nodes)

    if G.is_multigraph():
        edges = G.edges(keys=True)
    else:
        edges = G.edges()
    # we could copy the data here but then this function doesn't
    # match intersection and difference
    for e in edges:
        if not H.has_edge(*e):
            R.add_edge(*e)

    if H.is_multigraph():
        edges = H.edges(keys=True)
    else:
        edges = H.edges()
    for e in edges:
        if not G.has_edge(*e):
            R.add_edge(*e)
    return R


def compose(G, H):
    """Returns a new graph of G composed with H.

    Composition is the simple union of the node sets and edge sets.
    The node sets of G and H do not need to be disjoint.

    Parameters
    ----------
    G, H : graph
       A NetworkX graph

    Returns
    -------
    C: A new graph  with the same type as G

    Notes
    -----
    It is recommended that G and H be either both directed or both undirected.
    Attributes from H take precedent over attributes from G.

    For MultiGraphs, the edges are identified by incident nodes AND edge-key.
    This can cause surprises (i.e., edge `(1, 2)` may or may not be the same
    in two graphs) if you use MultiGraph without keeping track of edge keys.
    """
    if not G.is_multigraph() == H.is_multigraph():
        raise nx.NetworkXError("G and H must both be graphs or multigraphs.")

    R = G.__class__()
    # add graph attributes, H attributes take precedent over G attributes
    R.graph.update(G.graph)
    R.graph.update(H.graph)

    R.add_nodes_from(G.nodes(data=True))
    R.add_nodes_from(H.nodes(data=True))

    if G.is_multigraph():
        R.add_edges_from(G.edges(keys=True, data=True))
    else:
        R.add_edges_from(G.edges(data=True))
    if H.is_multigraph():
        R.add_edges_from(H.edges(keys=True, data=True))
    else:
        R.add_edges_from(H.edges(data=True))
    return R


def relational_compose(G, H, with_keys=False, with_data=True, edge_data_combiner=None):
    """Returns a new graph of G composed with H.

    Relational composition is the composition of G and H viewed as relations.
    We compute G; H, i.e., H o G. The nodes of the result are the union of the nodes of G and H. The result contains an edge from a node a in G to a node c in H if there is an node b in G and H such that G contains an edge from a to b and H contains an edge from b to c.
    For a multigraph, given m edges from a to b and n edges from b to c, the result will have mxn edges from a to c.  The user can define attributes of these edges as a function edge_data_combiner of the attributes of a participating edge instance for each particpating edge.
    Where two nodes are connected by more than one intermediate node, a single edge is created in a Graph or DiGraph (it is not defined in this case which pair is used to calculate the attribute data), and multiple edges are created in a MultiGraph or MultiDiGraph (so attribute data calculated from each pair is preserved), but note the restrictions imposed by the with_keys parameter.
    An undirected graph is treated as a directed graph with dual directed edges between the connected nodes, in each direction, as by to_directed, so can be composed with a directed graph in either direction.
    The relational composition of hypergraphs would contain a hyperedge with nodeset U if G contains a hyperedge with nodeset V and H contains a hyperedge with nodeset W, with U the symmetric difference of V and W.

    Parameters
    ----------
    G, H : graph
       A NetworkX graph
    with_keys : bool, optional (default=False)
       Ignored for simple graphs.
       For multigraphs:
          If with_keys=True, keys of edges being composed must match.  This may be desired if keys are set explicitly.
          Otherwise, keys are ignored and reassigned.
    with_data : bool, optional (default=True)
    edge_data_combiner: function of two arguments

    Returns
    -------
    C: A new graph that is a multigraph if both G and H are multigraphs; directed if either G or H is directed; an undirected graph if both G and H are undirected graphs; and an error otherwise

    Notes
    -----
    Attributes from the graph and nodes are copied to the new graph if with_data is set.  For consistency with other routines, attributes from H take precedence over attributes from G.
    Attributes from the edges are copied to the new graph if with_data is set and a edge_data_combiner is provided.
    """
    # specify result graph
    # ultimately promote simple graphs to multigraphs
    if not G.is_multigraph() == H.is_multigraph():
        raise nx.NetworkXError("G and H must both be graphs or multigraphs.")
    is_multigraph = G.is_multigraph()

    if not (G.is_directed() or H.is_directed()):
        is_directed = False
    else:
        if not G.is_directed():
            G = G.to_directed()
        elif not H.is_directed():
            H = H.to_directed()
        is_directed = True

    # create result graph
    R = nx.create_empty_copy(G, with_data=with_data)
    if with_data:
        for k, v in H.graph.items():
            R.graph[k] = v
        R.add_nodes_from(H.nodes(data=True))

    # add composite edges to result graph
    for (gsource, nbrdict) in G.adjacency_iter():
        for gtarget in nbrdict.keys():
            succ_nodes = H[gtarget] if gtarget in H else {}
            if is_multigraph:
                for succ_node in succ_nodes:
                    if with_keys:
                        # for each edge in H from gtarget to succ_node with the same key as the edge from gsource to gtarget in G, create an edge in R with that key pre-composing the edge from gsource to gtarget in G
                        for k in succ_nodes[succ_node]:
                            if k in G[gsource][gtarget]:
                                R.add_edge(gsource, succ_node, key=k, **(edge_data_combiner(G[gsource][gtarget][k], H[gtarget][succ_node][k]) if with_data and edge_data_combiner else {}))
                    else:
                        # Create an edge in R pre-composing the edge from gsource to gtarget in G for each edge in H from gtarget to succ_node
                        for gk in G[gsource][gtarget]:
                            for hk in H[gtarget][succ_node]:
                                R.add_edge(gsource, succ_node, **(edge_data_combiner(G[gsource][gtarget][gk], H[gtarget][succ_node][hk]) if with_data and edge_data_combiner else {}))
            else:
                # Create an edge in R pre-composing the edge from gsource to gtarget in G for each edge in H from gtarget to any succ_node of gtarget
                for succ_node in succ_nodes:
                    R.add_edge(gsource, succ_node, **(edge_data_combiner(G[gsource][gtarget], H[gtarget][succ_node]) if with_data and edge_data_combiner else {}))

    return R


def full_join(G, H, rename=(None, None)):
    """Returns the full join of graphs G and H.

    Full join is the union of G and H in which all edges between
    G and H are added.
    The node sets of G and H must be disjoint,
    otherwise an exception is raised.

    Parameters
    ----------
    G, H : graph
       A NetworkX graph

    rename : bool , default=(None, None)
       Node names of G and H can be changed by specifying the tuple
       rename=('G-','H-') (for example).  Node "u" in G is then renamed
       "G-u" and "v" in H is renamed "H-v".

    Returns
    -------
    U : The full join graph with the same type as G.

    Notes
    -----
    It is recommended that G and H be either both directed or both undirected.

    If G is directed, then edges from G to H are added as well as from H to G.

    Note that full_join() does not produce parallel edges for MultiGraphs.

    The full join operation of graphs G and H is the same as getting
    their complement, performing a disjoint union, and finally getting
    the complement of the resulting graph.

    Graph, edge, and node attributes are propagated from G and H
    to the union graph.  If a graph attribute is present in both
    G and H the value from H is used.

    See Also
    --------
    union
    disjoint_union
    """
    R = union(G, H, rename)

    def add_prefix(graph, prefix):
        if prefix is None:
            return graph

        def label(x):
            if isinstance(x, str):
                name = prefix + x
            else:
                name = prefix + repr(x)
            return name

        return nx.relabel_nodes(graph, label)

    G = add_prefix(G, rename[0])
    H = add_prefix(H, rename[1])

    for i in G:
        for j in H:
            R.add_edge(i, j)
    if R.is_directed():
        for i in H:
            for j in G:
                R.add_edge(i, j)

    return R
