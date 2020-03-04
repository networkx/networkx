"""
Algorithms for reducing the number of edges in a graph
"""
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ['dedensify', 'densify']


def dedensify(G, **kwargs):
    """
    Reduce the number of edges in a graph by adding compressor nodes

    Reduces the number of edges in a graph by removing edges around high-degree
    nodes by adding compressor nodes

    Parameters
    ----------
    G: graph
       A networkx graph

    Keyword Parameters
    ------------------
    threshold: int, optional (default=2)
       Number of edges a node must have to be considered a high degree node
    expansive: bool, (default=False)
       Indicates if densification should occur in cases where the number of
       edges are not reduced
    prefix: str or None, optional (default: None)
       An optional prefix for denoting compressor nodes
    inplace: bool, optional (default: False)
       Indicates if dedensification should be done inplace

    Returns
    -------
    G: NetworkX graph
       The dedensified graph

    Notes
    -----
    According to the algorithm in [1]_, dedensification identifies low degree
    nodes connecting to the same set of high degree nodes, and re-routes the
    edges between the two sets of nodes through a compressor node.

    When expansiveness is used, dedensification is performend on all sets of
    low/high degree nodes, even when it will not reduce the number of edges.

    When expansiveness is not used, dedensification will only be applied when
    it would result in fewer edges.

    References
    ----------
    .. [1] Maccioni, A., & Abadi, D. J. (2016, August).
       Scalable pattern matching over compressed graphs via dedensification.
       In Proceedings of the 22nd ACM SIGKDD International Conference on
       Knowledge Discovery and Data Mining (pp. 1755-1764).
       http://www.cs.umd.edu/~abadi/papers/graph-dedense.pdf

    See Also
    --------
    densify
    """
    high_degree_nodes = set()
    low_degree_nodes = set()
    for node in G.nodes():
        if isinstance(G, nx.DiGraph):
            node_degrees = G.in_degree(node)
        else:
            node_degrees = G.degree(node)
        if node_degrees > kwargs.get('threshold', 2):
            high_degree_nodes.add(node)
        else:
            low_degree_nodes.add(node)

    auxillary = dict()
    for node in high_degree_nodes | low_degree_nodes:
        node_neighbors = set(G.neighbors(node))
        high_degree_neighbors = frozenset(node_neighbors & high_degree_nodes)
        if high_degree_neighbors:
            low_degree_neighbors = auxillary.get(high_degree_neighbors)
            if not low_degree_neighbors:
                auxillary[high_degree_neighbors] = set([node])
            else:
                low_degree_neighbors.add(node)

    if kwargs.get('inplace', False):
        G = G.copy()

    prefix = kwargs.get('prefix')
    compressor_nodes = set()
    for index, (high_degree_nodes, low_degree_nodes) in enumerate(auxillary.items()):
        if not kwargs.get('expansive', False):
            low_degree_node_count = len(low_degree_nodes)
            high_degree_node_count = len(high_degree_nodes)
            old_edges = high_degree_node_count * low_degree_node_count
            new_edges = high_degree_node_count + low_degree_node_count
            if old_edges <= new_edges:
                continue
        compression_node = ''.join(str(node) for node in high_degree_nodes)
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


@not_implemented_for('undirected')
def densify(G, compressor_nodes, **kwargs):
    """
    Densifies a compressed graph

    Parameters
    ----------
    G: dedensified graph
       A networkx graph
    compressor_nodes: list
       Iterable of compressor nodes in the dedensified graph

    Keyword Parameters
    ------------------
    inplace: bool, optional (default: False)
       Indicates if densification should be done inplace

    Returns
    -------
    G: graph
       A densified networkx graph

    Notes
    -----
    Removes compressor nodes and adds the original edges between nodes

    References
    ----------
    .. [1] Maccioni, A., & Abadi, D. J. (2016, August).
       Scalable pattern matching over compressed graphs via dedensification.
       In Proceedings of the 22nd ACM SIGKDD International Conference on
       Knowledge Discovery and Data Mining (pp. 1755-1764).
       http://www.cs.umd.edu/~abadi/papers/graph-dedense.pdf


    """
    if kwargs.get('inplace', False):
        G = G.copy()
    for compressor_node in compressor_nodes:
        all_neighbors = set(nx.all_neighbors(G, compressor_node))
        out_neighbors = set(G.neighbors(compressor_node))
        for out_neighbor in out_neighbors:
            G.remove_edge(compressor_node, out_neighbor)
        in_neighbors = all_neighbors - out_neighbors
        for in_neighbor in in_neighbors:
            G.remove_edge(in_neighbor, compressor_node)
            for out_neighbor in out_neighbors:
                G.add_edge(in_neighbor, out_neighbor)
        G.remove_node(compressor_node)
    return G
