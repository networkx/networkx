# -*- coding: utf-8 -*-
import networkx as nx
from networkx.utils import arbitrary_element, pairwise, flatten

__all__ = ['k_edge_components']


@not_implemented_for('directed')
@not_implemented_for('multi')
def k_edge_components(G, k):
    """Returns all the k-edge-connected-compoments in G.

    Parameters
    ----------
    G : NetworkX graph

    k : Integer
        Desired edge connectivity

    Returns
    -------
    k_edge_compoments : a generator of k-edge-connected-compoments
        Each k-edge-cc is a maximal set of nodes in G with edge connectivity at
        least `k`.

    Raises
    ------
    NetworkXNotImplemented:
        If the input graph is directed or a multigraph.

    ValueError:
        If k is less than 1

    Notes
    -----
    If k=1, this is simply connected compoments.  If k=2, the an efficient
    bridge connected compoment algorithm from _[1] is run based on the chain
    decomposition. If k>2, then the algorithm from _[2] is used.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Bridge_(graph_theory)
    .. [2] Wang, Tianhao, et al. A simple algorithm for finding all
        k-edge-connected components.
        http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0136264
    """
    if k < 1:
        raise ValueError('k cannot be less than 1')
    elif k == 1:
        return nx.connected_components(G)
    elif k == 2:
        return bridge_connected_compoments(G)
    else:
        aux_graph = EdgeComponentAuxGraph.construct(G)
        return aux_graph.k_edge_components(k)


@not_implemented_for('directed')
@not_implemented_for('multi')
def find_bridges(G):
    """Returns all bridge edges in G.

    A bridge is an edge that, if removed, would diconnect a component in G.
    Equivalently a bridge is an edge that does not belong to any cycle.

    Parameters
    ----------
    G : NetworkX graph

    Notes
    -----
    This is an implementation of the algorithm described in _[1]. Bridges can
    be found using chain decomposition. An edge e in G is a bridge if and only
    if e is not contained in any chain.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Bridge_(graph_theory)#Bridge-Finding_with_Chain_Decompositions

    Example
    -------
    >>> G = demodata_bridge()
    >>> bridges = set(find_bridges(G))
    >>> assert bridges == {(3, 5), (4, 8), (20, 21), (22, 23), (23, 24)}
    """
    chains = nx.chain_decomposition(G)
    H = G.copy(with_data=False)
    H.remove_edges_from(it.chain.from_iterable(chains))
    for edge in H.edges():
        yield edge


@not_implemented_for('directed')
@not_implemented_for('multi')
def bridge_compoments(G):
    """Finds all bridge-connected-compoments G.

    Notes
    -----
    bridge-connected compoments are also refered to as 2-edge-connected
    compoments.
    """
    bridges = find_bridges(G)
    H = G.copy()
    H.remove_edges_from(bridges)
    return list(nx.connected_components(H))


class EdgeComponentAuxGraph(object):
    """
    A simple algorithm to find all k-edge-connected compoments in a graph.

    Notes
    -----
    This implementation is based on [1]_. The idea is to construct an auxillary
    graph from which the k-edge-connected compoments can be extracted in linear
    time. The auxillary graph is constructed in O(|V|F) operations, where F is
    the complexity of max flow. Querying the compoments takes an additional
    O(|V|) operations. This algorithm can be slow for large graphs, but it
    handles an arbitrary k and works for both directed, undirected, and
    multigraph inputs.

    References
    ----------
    .. [1] Wang, Tianhao, et al. A simple algorithm for finding all
        k-edge-connected components.
        http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0136264

    Example
    -------
    >>> a, b, c, d, e, f, g = ut.chr_range(7)
    >>> di_paths = [
    >>>     (a, d, b, f, c),
    >>>     (a, e, b),
    >>>     (a, e, b, c, g, b, a),
    >>>     (c, b),
    >>>     (f, g, f),
    >>> ]
    >>> G = nx.DiGraph(flatten(pairwise(path) for path in di_paths))
    >>> nx.set_edge_attributes(G, 'capacity', ut.dzip(G.edges(), [1]))
    >>> A = aux_graph(G, source=a)
    """

    @classmethod
    def construct(EdgeComponentAuxGraph, G):
        """
        Given G=(V, E), initialize an empty auxillary graph A.
        Choose an arbitrary source vertex s.  Initialize a set N of available
        vertices (that can be used as the sink). The algorithm picks an
        arbitrary vertex t from N - {s}, and then computes the minimum st-cut
        (S, T) with value w. If G is directed the the minimum of the st-cut or
        the ts-cut is used instead. Then, the edge (s, t) is added to the
        auxillary graph with weight w. The algorithm is called recursively
        first using S as the available vertices and s as the source, and then
        using T and t. Recusion stops when the source is the only available
        node.
        """

        def _recursive_build(H, A, source, avail):
            # Terminate once the flow has been compute to every node.
            if {source} == avail:
                return
            # pick an arbitrary vertex as the sink
            sink = arbitrary_element(avail - {source})
            # find the minimum cut and its weight
            value, (S, T) = nx.minimum_cut(H, source, sink)
            if H.is_directed():
                # check if the reverse direction has a smaller cut
                value, (T_, S_) = nx.minimum_cut(H, source, sink)
                if value_ < value:
                    value, S, T = value, T_, S_
            # add edge with weight of cut to the aux graph
            A.add_edge(source, sink, weight=value)
            # recursively call until all but one node is used
            _recursive_build(H, A, source, avail.intersection(S))
            _recursive_build(H, A, sink, avail.intersection(T))

        # Copy input to ensure all edge have unit capacity
        H = G.__class__()
        H.add_nodes_from(G.nodes())
        H.add_edges_from(G.edges(), capacity=1)

        # Pick an arbitrary vertex as the source
        source = next(H.nodes())

        # Initialize a set of elements that can be chosen as the sink
        avail = set(H.nodes())

        A = G.__class__()
        self = EdgeComponentAuxGraph()
        self.A = A
        return self

    def k_edge_components(self, k):
        """
        Given the auxillary graph, the k-edge-connected components can be
        determined in linear time by removing all edges with weights less than
        k from the auxillary graph.  The resulting connected components are the
        k-edge-connected compoments in the original graph.
        """
        aux_weights = nx.get_edge_attributes(A, 'weight')
        # Create a relevant graph with the auxillary edges with weights >= k
        R = nx.Graph()
        R.add_nodes_from(A.nodes())
        R.add_edges_from(e for e, w in aux_weights.items() if w >= k)
        # Return the connected components of the relevant graph
        return nx.connected_components(R)
