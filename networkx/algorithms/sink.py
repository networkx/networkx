"""
Functions for identifying sinks (out-degree zero) nodes.
"""
import networkx as nx
from networkx.utils.decorators import not_implemented_for

_author__ = """\n""".join(['Tomas Jelinek <tomasjelinek96@gmail.com>'])

__all__ = ['is_sink', 'sinks', 'number_of_sinks']


@not_implemented_for('undirected')
def is_sink(G, n):
    """Determines whether a node is a sink.

    A *sink* is a node with no outgoing arcs (that is, with out-degree
    zero).

    Parameters
    ----------
    G : NetworkX DiGraph

    n : node
        A node in `G`.

    Returns
    -------
    is_sink : bool
       True if and only if `n` has no neighbors.

    Examples
    --------
    >>> G=nx.DiGraph()
    >>> G.add_edge(1,2)
    >>> G.add_node(3)
    >>> nx.is_sink(G,1)
    False
    >>> nx.is_sink(G,2)
    True
    >>> nx.is_sink(G,3)
    True
    """
    return G.out_degree(n) == 0


@not_implemented_for('undirected')
def sinks(G):
    """Iterator over sinks in the graph.

    A *sink* is a node with no outgoing arcs (that is, with out-degree
    zero).

    Parameters
    ----------
    G : NetworkX DiGraph

    Returns
    -------
    iterator
        An iterator over the sinks of `G`.

    Examples
    --------
    To get a list of all sinkss of a graph, use the :class:`list`
    constructor::

        >>> G = nx.DiGraph()
        >>> G.add_edge(1, 2)
        >>> G.add_node(3)
        >>> list(nx.sinks(G))
        [2, 3]

    To remove all sinks in the graph, first create a list of the
    sinks, then use :meth:`Graph.remove_nodes_from`::

        >>> G.remove_nodes_from(list(nx.sinks(G)))
        >>> list(G)
        [1]
    """
    return (n for n, d in G.out_degree() if d == 0)


@not_implemented_for('undirected')
def number_of_sinks(G):
    """Returns the number of sinks in the graph.

    A *sink* is a node with no outgoing arcs (that is, with out-degree
    zero).

    Parameters
    ----------
    G : NetworkX DiGraph

    Returns
    -------
    int
        The number of out-degree zero nodes in the directed graph `G`.

    """
    return sum(1 for v in sinks(G))