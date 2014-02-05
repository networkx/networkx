from contextlib import contextmanager
import networkx as nx
from networkx import NetworkXError


@contextmanager
def hide_nodes_edges(G, nodes=[], edges=[]):
    """context manager hiding specified nodes and edges from G

    Parameters
    ----------
    G : NetworkX graph
        direct/undirected graph

    nodes : list of networkx nodes

    edges : list of tuples
        (source, target)
        if G is directed, the edges are treated as directed
        otherwise edges are treated as bi-directional

    Returns
    -------

    Examples
    --------
    >>> G = nx.house_graph()
    >>> with hide_nodes_edges(G, [1], [(0, 2)]):
    ...     print list(G.neighbors_iter(0))
    []
    """
    import types

    def successors_iter(G, n):
        try:
            if n in nodes:
                return iter([])
            else:
                return iter(s for s in G.adj[n]
                            if s not in nodes and (n, s) not in edges)
        except KeyError:
            raise NetworkXError("The node %s is not in the digraph." % (n,))

    def predecessors_iter(G, n):
        try:
            if n in nodes:
                return iter([])
            else:
                return iter(s for s in G.pred[n]
                            if s not in nodes and (s, n) not in edges)
        except KeyError:
            raise NetworkXError("The node %s is not in the digraph." % (n,))

    def neighbors_iter(G, n):
        try:
            if n in nodes:
                return iter([])
            else:
                return iter(s for s in G.adj[n] if s not in nodes
                            and (s, n) not in edges and (n, s) not in edges)
        except KeyError:
            raise NetworkXError("The node %s is not in the digraph." % (n,))
    try:
        if G.is_directed():
            si = G.successors_iter
            G.successors_iter = types.MethodType(successors_iter, G)
            # use neighbors_iter when directedness is not specified. the
            # default neighbors_iter() inherited from Graph should also be
            # replaced.
            G.neighbors_iter = types.MethodType(successors_iter, G)
            pi = G.predecessors_iter
            G.predecessors_iter = types.MethodType(predecessors_iter, G)
        else:
            ni = G.neighbors_iter
            G.neighbors_iter = types.MethodType(neighbors_iter, G)
        yield G

    finally:
        if G.is_directed():
            G.successors_iter = si
            G.predecessors_iter = pi
        else:
            G.neighbors_iter = ni
