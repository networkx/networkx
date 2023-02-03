"""Operations on many graphs.
"""
from itertools import chain, repeat

import networkx as nx

__all__ = ["union_all", "compose_all", "disjoint_union_all", "intersection_all"]


def union_all(graphs, rename=()):
    """Returns the union of all graphs.

    The graphs must be disjoint, otherwise an exception is raised.

    Parameters
    ----------
    graphs : iterable
       Iterable of NetworkX graphs

    rename : iterable , optional
       Node names of graphs can be changed by specifying the tuple
       rename=('G-','H-') (for example).  Node "u" in G is then renamed
       "G-u" and "v" in H is renamed "H-v". Infinite generators (like itertools.count)
       are also supported.

    Returns
    -------
    U : a graph with the same type as the first graph in list

    Raises
    ------
    ValueError
       If `graphs` is an empty list.

    Notes
    -----
    To force a disjoint union with node relabeling, use
    disjoint_union_all(G,H) or convert_node_labels_to integers().

    Graph, edge, and node attributes are propagated to the union graph.
    If a graph attribute is present in multiple graphs, then the value
    from the last graph in the list with that attribute is used.

    See Also
    --------
    union
    disjoint_union_all
    """
    R = None
    seen_nodes = set()

    # rename graph to obtain disjoint node labels
    def add_prefix(graph, prefix):
        if prefix is None:
            return graph

        def label(x):
            return f"{prefix}{x}"

        return nx.relabel_nodes(graph, label)

    rename = chain(rename, repeat(None))
    graphs = (add_prefix(G, name) for G, name in zip(graphs, rename))

    for i, G in enumerate(graphs):
        G_nodes_set = set(G.nodes)
        if i == 0:
            # Union is the same type as first graph
            R = G.__class__()
        elif G.is_multigraph() != R.is_multigraph():
            raise nx.NetworkXError("All graphs must be graphs or multigraphs.")
        elif not seen_nodes.isdisjoint(G_nodes_set):
            raise nx.NetworkXError(
                "The node sets of the graphs are not disjoint.",
                "Use appropriate rename"
                "=(G1prefix,G2prefix,...,GNprefix)"
                "or use disjoint_union(G1,G2,...,GN).",
            )

        seen_nodes |= G_nodes_set
        R.graph.update(G.graph)
        R.add_nodes_from(G.nodes(data=True))
        R.add_edges_from(
            G.edges(keys=True, data=True) if G.is_multigraph() else G.edges(data=True)
        )

    if R is None:
        raise ValueError("cannot apply union_all to an empty list")

    return R


def disjoint_union_all(graphs):
    """Returns the disjoint union of all graphs.

    This operation forces distinct integer node labels starting with 0
    for the first graph in the list and numbering consecutively.

    Parameters
    ----------
    graphs : iterable
       Iterable of NetworkX graphs

    Returns
    -------
    U : A graph with the same type as the first graph in list

    Raises
    ------
    ValueError
       If `graphs` is an empty list.

    Notes
    -----
    It is recommended that the graphs be either all directed or all undirected.

    Graph, edge, and node attributes are propagated to the union graph.
    If a graph attribute is present in multiple graphs, then the value
    from the last graph in the list with that attribute is used.
    """

    def yield_relabeled(graphs):
        first_label = 0
        for G in graphs:
            yield nx.convert_node_labels_to_integers(G, first_label=first_label)
            first_label += len(G)

    R = union_all(yield_relabeled(graphs))

    return R


def compose_all(graphs):
    """Returns the composition of all graphs.

    Composition is the simple union of the node sets and edge sets.
    The node sets of the supplied graphs need not be disjoint.

    Parameters
    ----------
    graphs : iterable
       Iterable of NetworkX graphs

    Returns
    -------
    C : A graph with the same type as the first graph in list

    Raises
    ------
    ValueError
       If `graphs` is an empty list.

    Notes
    -----
    It is recommended that the supplied graphs be either all directed or all
    undirected.

    Graph, edge, and node attributes are propagated to the union graph.
    If a graph attribute is present in multiple graphs, then the value
    from the last graph in the list with that attribute is used.
    """
    R = None

    # add graph attributes, H attributes take precedent over G attributes
    for i, G in enumerate(graphs):
        if i == 0:
            # create new graph
            R = G.__class__()
        elif G.is_multigraph() != R.is_multigraph():
            raise nx.NetworkXError("All graphs must be graphs or multigraphs.")

        R.graph.update(G.graph)
        R.add_nodes_from(G.nodes(data=True))
        R.add_edges_from(
            G.edges(keys=True, data=True) if G.is_multigraph() else G.edges(data=True)
        )

    if R is None:
        raise ValueError("cannot apply compose_all to an empty list")

    return R


def intersection_all(graphs):
    """Returns a new graph that contains only the nodes and the edges that exist in
    all graphs.

    Parameters
    ----------
    graphs : iterable
       Iterable of NetworkX graphs

    Returns
    -------
    R : A new graph with the same type as the first graph in list

    Raises
    ------
    ValueError
       If `graphs` is an empty list.

    Notes
    -----
    Attributes from the graph, nodes, and edges are not copied to the new
    graph.
    """
    R = None

    for i, G in enumerate(graphs):
        G_nodes_set = set(G.nodes)
        G_edges_set = set(G.edges(keys=True) if G.is_multigraph() else G.edges())
        if i == 0:
            # create new graph
            R = G.__class__()
            node_intersection = G_nodes_set
            edge_intersection = G_edges_set
        elif G.is_multigraph() != R.is_multigraph():
            raise nx.NetworkXError("All graphs must be graphs or multigraphs.")
        else:
            node_intersection &= G_nodes_set
            edge_intersection &= G_edges_set

        R.graph.update(G.graph)

    if R is None:
        raise ValueError("cannot apply intersection_all to an empty list")

    R.add_nodes_from(node_intersection)
    R.add_edges_from(edge_intersection)

    return R
