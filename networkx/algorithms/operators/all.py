"""Operations on many graphs.
"""
from itertools import zip_longest

import networkx as nx

__all__ = ["union_all", "compose_all", "disjoint_union_all", "intersection_all"]


def union_all(graphs, rename=(None,)):
    """Returns the union of all graphs.

    The graphs must be disjoint, otherwise an exception is raised.

    Parameters
    ----------
    graphs : list of graphs
       List of NetworkX graphs

    rename : bool , default=(None, None)
       Node names of G and H can be changed by specifying the tuple
       rename=('G-','H-') (for example).  Node "u" in G is then renamed
       "G-u" and "v" in H is renamed "H-v".

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
    # collect the graphs in case an iterator was passed
    graphs = list(graphs)

    if not graphs:
        raise ValueError("cannot apply union_all to an empty list")

    U = graphs[0]

    if any(G.is_multigraph() != U.is_multigraph() for G in graphs):
        raise nx.NetworkXError("All graphs must be graphs or multigraphs.")

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

    graphs = [add_prefix(G, name) for G, name in zip_longest(graphs, rename)]

    if sum(len(G) for G in graphs) != len(set().union(*graphs)):
        raise nx.NetworkXError(
            "The node sets of the graphs are not disjoint.",
            "Use appropriate rename"
            "=(G1prefix,G2prefix,...,GNprefix)"
            "or use disjoint_union(G1,G2,...,GN).",
        )

    # Union is the same type as first graph
    R = U.__class__()

    # add graph attributes, later attributes take precedent over earlier ones
    for G in graphs:
        R.graph.update(G.graph)

    # add nodes and attributes
    for G in graphs:
        R.add_nodes_from(G.nodes(data=True))

    if U.is_multigraph():
        for G in graphs:
            R.add_edges_from(G.edges(keys=True, data=True))
    else:
        for G in graphs:
            R.add_edges_from(G.edges(data=True))

    return R


def disjoint_union_all(graphs):
    """Returns the disjoint union of all graphs.

    This operation forces distinct integer node labels starting with 0
    for the first graph in the list and numbering consecutively.

    Parameters
    ----------
    graphs : list
       List of NetworkX graphs

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
    graphs = list(graphs)

    if not graphs:
        raise ValueError("cannot apply disjoint_union_all to an empty list")

    first_labels = [0]
    for G in graphs[:-1]:
        first_labels.append(len(G) + first_labels[-1])

    relabeled = [
        nx.convert_node_labels_to_integers(G, first_label=first_label)
        for G, first_label in zip(graphs, first_labels)
    ]
    R = union_all(relabeled)
    for G in graphs:
        R.graph.update(G.graph)
    return R


def compose_all(graphs):
    """Returns the composition of all graphs.

    Composition is the simple union of the node sets and edge sets.
    The node sets of the supplied graphs need not be disjoint.

    Parameters
    ----------
    graphs : list
       List of NetworkX graphs

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
    graphs = list(graphs)

    if not graphs:
        raise ValueError("cannot apply compose_all to an empty list")

    U = graphs[0]

    if any(G.is_multigraph() != U.is_multigraph() for G in graphs):
        raise nx.NetworkXError("All graphs must be graphs or multigraphs.")

    R = U.__class__()
    # add graph attributes, H attributes take precedent over G attributes
    for G in graphs:
        R.graph.update(G.graph)

    for G in graphs:
        R.add_nodes_from(G.nodes(data=True))

    if U.is_multigraph():
        for G in graphs:
            R.add_edges_from(G.edges(keys=True, data=True))
    else:
        for G in graphs:
            R.add_edges_from(G.edges(data=True))
    return R


def intersection_all(graphs):
    """Returns a new graph that contains only the nodes and the edges that exist in
    all graphs.

    Parameters
    ----------
    graphs : list
       List of NetworkX graphs

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
    graphs = list(graphs)

    if not graphs:
        raise ValueError("cannot apply intersection_all to an empty list")

    U = graphs[0]

    if any(G.is_multigraph() != U.is_multigraph() for G in graphs):
        raise nx.NetworkXError("All graphs must be graphs or multigraphs.")

    # create new graph
    node_intersection = set.intersection(*[set(G.nodes) for G in graphs])
    R = U.__class__()
    R.add_nodes_from(node_intersection)

    if U.is_multigraph():
        edge_sets = [set(G.edges(keys=True)) for G in graphs]
    else:
        edge_sets = [set(G.edges()) for G in graphs]

    edge_intersection = set.intersection(*edge_sets)
    R.add_edges_from(edge_intersection)

    return R
