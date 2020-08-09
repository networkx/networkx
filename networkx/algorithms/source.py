"""
Functions for identifying sources (in-degree zero) nodes.
"""
import networkx as nx
from networkx.utils.decorators import not_implemented_for

_author__ = """\n""".join(['Tomas Jelinek <tomasjelinek96@gmail.com>'])

__all__ = ['is_source', 'sources', 'number_of_sources']


@not_implemented_for('undirected')
def is_source(G, n):
    """Determines whether a node is a source.

    A *source* is a node with no incoming arcs (that is, with in-degree
    zero).

    Parameters
    ----------
    G : NetworkX DiGraph

    n : node
        A node in `G`.

    Returns
    -------
    is_source : bool
       True if and only if `n` has incoming arcs.

    Examples
    --------
    >>> G=nx.DiGraph()
    >>> G.add_edge(1,2)
    >>> G.add_node(3)
    >>> nx.is_source(G,1)
    True
    >>> nx.is_source(G,2)
    False
    >>> nx.is_source(G,3)
    True
    """
    return G.in_degree(n) == 0


@not_implemented_for('undirected')
def sources(G):
    """Iterator over sinks in the graph.

    A *source* is a node with no incoming arcs (that is, with in-degree
    zero).

    Parameters
    ----------
    G : NetworkX DiGraph

    Returns
    -------
    iterator
        An iterator over the sources of `G`.

    Examples
    --------
    To get a list of all sources of a directed graph, use the :class:`list`
    constructor::

        >>> G = nx.DiGraph()
        >>> G.add_edge(1, 2)
        >>> G.add_node(3)
        >>> list(nx.sources(G))
        [1, 3]

    To remove all sources in the graph, first create a list of the
    sources, then use :meth:`Graph.remove_nodes_from`::

        >>> G.remove_nodes_from(list(nx.sources(G)))
        >>> list(G)
        [3]
    """
    return (n for n, d in G.in_degree() if d == 0)


@not_implemented_for('undirected')
def number_of_sources(G):
    """Returns the number of sources in the graph.

    A *source* is a node with no incoming arcs (that is, with in-degree
    zero).

    Parameters
    ----------
    G : NetworkX DiGraph

    Returns
    -------
    int
        The number of degree zero nodes in the directed graph `G`.

    """
    # TODO This can be parallelized.
    return sum(1 for v in sources(G))
