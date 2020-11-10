"""
Graph summarization finds smaller representations of graphs resulting in faster
runtime of algorithms, reduced storage needs, and noise reduction.
Summarization has applications in areas such as visualization, pattern mining,
clustering and community detection, and more.  Core graph summarization
techniques are grouping/aggregation, bit-compression,
simplification/sparsification, and influence based. Graph summarization
algorithms often produce either summary graphs in the form of supergraphs or
sparsified graphs, or a list of independent structures. Supergraphs are the
most common product, which consist of supernodes and original nodes and are
connected by edges and superedges, which represent aggregate edges between
nodes and supernodes.

Grouping/aggregation based techniques compress graphs by representing
close/connected nodes and edges in a graph by a single node/edge in a
supergraph. Nodes can be grouped together into supernodes based on their
structural similarities or proximity within a graph to reduce the total number
of nodes in a graph. Edge-grouping techniques group edges into lossy/lossless
nodes called compressor or virtual nodes to reduce the total number of edges in
a graph. Edge-grouping techniques can be lossless, meaning that they can be
used to re-create the original graph, or techniques can be lossy, requiring
less space to store the summary graph, but at the expense of lower
recontruction accuracy of the original graph.

Bit-compression techniques minimize the amount of information needed to
describe the original graph, while revealing structural patterns in the
original graph.  The two-part minimum description length (MDL) is often used to
represent the model and the original graph in terms of the model.  A key
difference between graph compression and graph summarization is that graph
summarization focuses on finding structural patterns within the original graph,
whereas graph compression focuses on compressions the original graph to be as
small as possible.  **NOTE**: Some bit-compression methods exist solely to
compress a graph without creating a summary graph or finding comprehensible
structural patterns.

Simplification/Sparsification techniques attempt to create a sparse
representation of a graph by removing unimportant nodes and edges from the
graph.  Sparsified graphs differ from supergraphs created by
grouping/aggregation by only containing a subset of the original nodes and
edges of the original graph.

Influence based techniques aim to find a high-level description of influence
propagation in a large graph.  These methods are scarce and have been mostly
applied to social graphs.

*dedensification* is a grouping/aggregation based technique to compress the
neighborhoods around high-degree nodes in unweighted graphs by adding
compressor nodes that summarize multiple edges of the same type to
high-degree nodes (nodes with a degree greater than a given threshold).
Dedensification was developed for the purpose of increasing performance of
query processing around high-degree nodes in graph databases and enables direct
operations on the compressed graph.  The structural patterns surrounding
high-degree nodes in the original is preserved while using fewer edges and
adding a small number of compressor nodes.  The degree of nodes present in the
original graph is also preserved. The current implementation of dedensification
supports graphs with one edge type.

For more information on graph summarization, see `Graph Summarization Methods
and Applications: A Survey <https://dl.acm.org/doi/abs/10.1145/3186727>`_
"""
import networkx as nx

__all__ = [
    "dedensify",
]


def dedensify(G, threshold, prefix=None, copy=True):
    """Compresses neighborhoods around high-degree nodes

    Reduces the number of edges to high-degree nodes by adding compressor nodes
    that summarize multiple edges of the same type to high-degree nodes (nodes
    with a degree greater than a given threshold).  Dedensification also has
    the added benefit of reducing the number of edges around high-degree nodes.
    The implementation currently supports graphs with a single edge type.

    Parameters
    ----------
    G: graph
       A networkx graph
    threshold: int
       Minimum degree threshold of a node to be considered a high degree node.
       The threshold must be greater than or equal to 2.
    prefix: str or None, optional (default: None)
       An optional prefix for denoting compressor nodes
    copy: bool, optional (default: True)
       Indicates if dedensification should be done inplace

    Returns
    -------
    dedensified networkx graph : (graph, set)
        2-tuple of the dedensified graph and set of compressor nodes

    Notes
    -----
    According to the algorithm in [1]_, removes edges in a graph by
    compressing/decompressing the neighborhoods around high degree nodes by
    adding compressor nodes that summarize multiple edges of the same type
    to high-degree nodes.  Dedensification will only add a compressor node when
    doing so will reduce the total number of edges in the given graph. This
    implementation currently supports graphs with a single edge type.

    Examples
    --------
    Dedensification will only add compressor nodes when doing so would result
    in fewer edges::

        >>> original_graph = nx.DiGraph()
        >>> original_graph.add_nodes_from(
        ...     ["1", "2", "3", "4", "5", "6", "A", "B", "C"]
        ... )
        >>> original_graph.add_edges_from(
        ...     [
        ...         ("1", "C"), ("1", "B"),
        ...         ("2", "C"), ("2", "B"), ("2", "A"),
        ...         ("3", "B"), ("3", "A"), ("3", "6"),
        ...         ("4", "C"), ("4", "B"), ("4", "A"),
        ...         ("5", "B"), ("5", "A"),
        ...         ("6", "5"),
        ...         ("A", "6")
        ...     ]
        ... )
        >>> c_graph, c_nodes = nx.dedensify(original_graph, threshold=2)
        >>> original_graph.number_of_edges()
        15
        >>> c_graph.number_of_edges()
        14

    A dedensified, directed graph can be "densified" to reconstruct the
    original graph::

        >>> original_graph = nx.DiGraph()
        >>> original_graph.add_nodes_from(
        ...     ["1", "2", "3", "4", "5", "6", "A", "B", "C"]
        ... )
        >>> original_graph.add_edges_from(
        ...     [
        ...         ("1", "C"), ("1", "B"),
        ...         ("2", "C"), ("2", "B"), ("2", "A"),
        ...         ("3", "B"), ("3", "A"), ("3", "6"),
        ...         ("4", "C"), ("4", "B"), ("4", "A"),
        ...         ("5", "B"), ("5", "A"),
        ...         ("6", "5"),
        ...         ("A", "6")
        ...     ]
        ... )
        >>> c_graph, c_nodes = nx.dedensify(original_graph, threshold=2)
        >>> # re-densifies the compressed graph into the original graph
        >>> for c_node in c_nodes:
        ...     all_neighbors = set(nx.all_neighbors(c_graph, c_node))
        ...     out_neighbors = set(c_graph.neighbors(c_node))
        ...     for out_neighbor in out_neighbors:
        ...         c_graph.remove_edge(c_node, out_neighbor)
        ...     in_neighbors = all_neighbors - out_neighbors
        ...     for in_neighbor in in_neighbors:
        ...         c_graph.remove_edge(in_neighbor, c_node)
        ...         for out_neighbor in out_neighbors:
        ...             c_graph.add_edge(in_neighbor, out_neighbor)
        ...     c_graph.remove_node(c_node)
        ...
        >>> nx.is_isomorphic(original_graph, c_graph)
        True

    References
    ----------
    .. [1] Maccioni, A., & Abadi, D. J. (2016, August).
       Scalable pattern matching over compressed graphs via dedensification.
       In Proceedings of the 22nd ACM SIGKDD International Conference on
       Knowledge Discovery and Data Mining (pp. 1755-1764).
       http://www.cs.umd.edu/~abadi/papers/graph-dedense.pdf
    """
    if threshold < 2:
        raise nx.NetworkXError("The degree threshold must be >= 2")

    degrees = G.in_degree if G.is_directed() else G.degree
    # Group nodes based on degree threshold
    high_degree_nodes = set([n for n, d in degrees if d > threshold])
    low_degree_nodes = G.nodes() - high_degree_nodes

    auxillary = {}
    for node in G:
        high_degree_neighbors = frozenset(high_degree_nodes & set(G[node]))
        if high_degree_neighbors:
            if high_degree_neighbors in auxillary:
                auxillary[high_degree_neighbors].add(node)
            else:
                auxillary[high_degree_neighbors] = {node}

    if copy:
        G = G.copy()

    compressor_nodes = set()
    for index, (high_degree_nodes, low_degree_nodes) in enumerate(auxillary.items()):
        low_degree_node_count = len(low_degree_nodes)
        high_degree_node_count = len(high_degree_nodes)
        old_edges = high_degree_node_count * low_degree_node_count
        new_edges = high_degree_node_count + low_degree_node_count
        if old_edges <= new_edges:
            continue
        compression_node = "".join(str(node) for node in high_degree_nodes)
        if prefix:
            compression_node = str(prefix) + compression_node
        for node in low_degree_nodes:
            for high_node in high_degree_nodes:
                if G.has_edge(node, high_node):
                    G.remove_edge(node, high_node)

            G.add_edge(node, compression_node)
        for node in high_degree_nodes:
            G.add_edge(compression_node, node)
        compressor_nodes.add(compression_node)
    return G, compressor_nodes
