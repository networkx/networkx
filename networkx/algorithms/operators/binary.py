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
]


def union(G, H, rename=(None, None)):
    """Return the union of graphs G and H.

    Graphs G and H must be disjoint, otherwise an exception is raised.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph

    rename : tuple , default=(None, None)
       Node names of G and H can be changed by specifying the tuple
       rename=('G-','H-') (for example).  Node "u" in G is then renamed
       "G-u" and "v" in H is renamed "H-v".

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

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.operators import *
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_edges_from([(0, 1), (0, 2), (1, 2)])
    >>> H.add_edges_from([(3, 4), (3, 6), (4, 5), (5, 6)])
    >>> U = union(G, H, rename=("G", "H"))
    >>> U.nodes
    NodeView(('G0', 'G1', 'G2', 'H3', 'H4', 'H6', 'H5'))
    >>> U.edges
    EdgeView([('G0', 'G1'), ('G0', 'G2'), ('G1', 'G2'), ('H3', 'H4'), ('H3', 'H6'), ('H4', 'H5'), ('H6', 'H5')])

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
    R.add_nodes_from(G.nodes(data=True))
    R.add_nodes_from(H.nodes(data=True))
    # add edges
    R.add_edges_from(G_edges)
    R.add_edges_from(H_edges)

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

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.operators import *
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_edges_from([(0, 1), (0, 2), (1, 2)])
    >>> H.add_edges_from([(0, 3), (1, 2), (2, 3)])
    >>> G.nodes[0]["key1"] = 5
    >>> H.nodes[0]["key2"] = 10
    >>> U = disjoint_union(G, H)
    >>> U.nodes(data=True)
    NodeDataView({0: {'key1': 5}, 1: {}, 2: {}, 3: {'key2': 10}, 4: {}, 5: {}, 6: {}})
    >>> U.edges
    EdgeView([(0, 1), (0, 2), (1, 2), (3, 4), (4, 6), (5, 6)])
    """
    R1 = nx.convert_node_labels_to_integers(G)
    R2 = nx.convert_node_labels_to_integers(H, first_label=len(R1))
    R = union(R1, R2)
    R.graph.update(G.graph)
    R.graph.update(H.graph)
    return R


def intersection(G, H):
    """Returns a new graph that contains only the nodes and the edges that exist in
    both G and H.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph. G and H can have different node sets but must be both graphs or both multigraphs.

    Raises
    ------
    NetworkXError
        If one is a MultiGraph and the other one is a graph.

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
    >>> R.remove_edges_from(e for e in G.edges if e not in H.edges)

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.operators import *
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_edges_from([(0, 1), (0, 2), (1, 2)])
    >>> H.add_edges_from([(0, 3), (1, 2), (2, 3)])
    >>> R = intersection(G, H)
    >>> R.nodes
    NodeView((0, 1, 2))
    >>> R.edges
    EdgeView([(1, 2)])
    """
    if not G.is_multigraph() == H.is_multigraph():
        raise nx.NetworkXError("G and H must both be graphs or multigraphs.")

    # create new graph
    if set(G) != set(H):
        R = G.__class__()
        R.add_nodes_from(set(G.nodes).intersection(set(H.nodes)))
    else:
        R = nx.create_empty_copy(G)

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
       A NetworkX graph. G and H must have the same node sets.

    Returns
    -------
    D : A new graph with the same type as G.

    Notes
    -----
    Attributes from the graph, nodes, and edges are not copied to the new
    graph.  If you want a new graph of the difference of G and H with
    the attributes (including edge data) from G use remove_nodes_from()
    as follows:

    >>> G = nx.path_graph(3)
    >>> H = nx.path_graph(5)
    >>> R = G.copy()
    >>> R.remove_nodes_from(n for n in G if n in H)

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.operators import *
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_edges_from([(0, 1), (0, 2), (1, 2), (1, 3)])
    >>> H.add_edges_from([(0, 1), (1, 2), (0, 3)])
    >>> R = difference(G, H)
    >>> R.nodes
    NodeView((0, 1, 2, 3))
    >>> R.edges
    EdgeView([(0, 2), (1, 3)])
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

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.operators import *
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_edges_from([(0, 1), (0, 2), (1, 2), (1, 3)])
    >>> H.add_edges_from([(0, 1), (1, 2), (0, 3)])
    >>> R = symmetric_difference(G, H)
    >>> R.nodes
    NodeView((0, 1, 2, 3))
    >>> R.edges
    EdgeView([(0, 2), (0, 3), (1, 3)])
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

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.operators import *
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_edges_from([(0, 1), (0, 2)])
    >>> H.add_edges_from([(0, 1), (1, 2)])
    >>> R = compose(G, H)
    >>> R.nodes
    NodeView((0, 1, 2))
    >>> R.edges
    EdgeView([(0, 1), (0, 2), (1, 2)])
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

    rename : tuple , default=(None, None)
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

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms.operators import *
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_edges_from([(0, 1), (0, 2)])
    >>> H.add_edge(3, 4)
    >>> R = full_join(G, H, rename=("G", "H"))
    >>> R.nodes
    NodeView(('G0', 'G1', 'G2', 'H3', 'H4'))
    >>> R.edges
    EdgeView([('G0', 'G1'), ('G0', 'G2'), ('G0', 'H3'), ('G0', 'H4'), ('G1', 'H3'), ('G1', 'H4'), ('G2', 'H3'), ('G2', 'H4'), ('H3', 'H4')])

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
