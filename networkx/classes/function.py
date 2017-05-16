#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors: Aric Hagberg <hagberg@lanl.gov>
#          Pieter Swart <swart@lanl.gov>
#          Dan Schult <dschult@colgate.edu>
"""Functional interface to graph methods and assorted utilities.
"""
from __future__ import division

from collections import Counter
from itertools import chain
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest

import networkx as nx
from networkx.utils import not_implemented_for
from networkx.utils import pairwise

__all__ = ['nodes', 'edges', 'degree', 'degree_histogram', 'neighbors',
           'number_of_nodes', 'number_of_edges', 'density',
           'is_directed', 'info', 'freeze', 'is_frozen', 'subgraph',
           'add_star', 'add_path', 'add_cycle',
           'create_empty_copy', 'set_node_attributes',
           'get_node_attributes', 'set_edge_attributes',
           'get_edge_attributes', 'all_neighbors', 'non_neighbors',
           'non_edges', 'common_neighbors', 'is_weighted',
           'is_negatively_weighted', 'is_empty']


def nodes(G):
    """Return an iterator over the graph nodes."""
    return G.nodes()


def edges(G, nbunch=None):
    """Return iterator over edges incident to nodes in nbunch.

    Return all edges if nbunch is unspecified or nbunch=None.

    For digraphs, edges=out_edges
    """
    return G.edges(nbunch)


def degree(G, nbunch=None, weight=None):
    """Return degree of single node or of nbunch of nodes.
    If nbunch is ommitted, then return degrees of *all* nodes.
    """
    return G.degree(nbunch, weight)


def neighbors(G, n):
    """Return a list of nodes connected to node n. """
    return G.neighbors(n)


def number_of_nodes(G):
    """Return the number of nodes in the graph."""
    return G.number_of_nodes()


def number_of_edges(G):
    """Return the number of edges in the graph. """
    return G.number_of_edges()


def density(G):
    r"""Return the density of a graph.

    The density for undirected graphs is

    .. math::

       d = \frac{2m}{n(n-1)},

    and for directed graphs is

    .. math::

       d = \frac{m}{n(n-1)},

    where `n` is the number of nodes and `m`  is the number of edges in `G`.

    Notes
    -----
    The density is 0 for a graph without edges and 1 for a complete graph.
    The density of multigraphs can be higher than 1.

    Self loops are counted in the total number of edges so graphs with self
    loops can have density higher than 1.
    """
    n = number_of_nodes(G)
    m = number_of_edges(G)
    if m == 0 or n <= 1:
        return 0
    d = m / (n * (n - 1))
    if not G.is_directed():
        d *= 2
    return d


def degree_histogram(G):
    """Return a list of the frequency of each degree value.

    Parameters
    ----------
    G : Networkx graph
       A graph

    Returns
    -------
    hist : list
       A list of frequencies of degrees.
       The degree values are the index in the list.

    Notes
    -----
    Note: the bins are width one, hence len(list) can be large
    (Order(number_of_edges))
    """
    counts = Counter(d for n, d in G.degree())
    return [counts.get(i, 0) for i in range(max(counts) + 1)]


def is_directed(G):
    """ Return True if graph is directed."""
    return G.is_directed()


def frozen(*args):
    """Dummy method for raising errors when trying to modify frozen graphs"""
    raise nx.NetworkXError("Frozen graph can't be modified")


def freeze(G):
    """Modify graph to prevent further change by adding or removing
    nodes or edges.

    Node and edge data can still be modified.

    Parameters
    ----------
    G : graph
      A NetworkX graph

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> G=nx.freeze(G)
    >>> try:
    ...    G.add_edge(4,5)
    ... except nx.NetworkXError as e:
    ...    print(str(e))
    Frozen graph can't be modified

    Notes
    -----
    To "unfreeze" a graph you must make a copy by creating a new graph object:

    >>> graph = nx.path_graph(4)
    >>> frozen_graph = nx.freeze(graph)
    >>> unfrozen_graph = nx.Graph(frozen_graph)
    >>> nx.is_frozen(unfrozen_graph)
    False

    See Also
    --------
    is_frozen
    """
    G.add_node=frozen
    G.add_nodes_from=frozen
    G.remove_node=frozen
    G.remove_nodes_from=frozen
    G.add_edge=frozen
    G.add_edges_from=frozen
    G.remove_edge=frozen
    G.remove_edges_from=frozen
    G.clear=frozen
    G.frozen=True
    return G


def is_frozen(G):
    """Return True if graph is frozen.

    Parameters
    ----------
    G : graph
      A NetworkX graph

    See Also
    --------
    freeze
    """
    try:
        return G.frozen
    except AttributeError:
        return False


def add_star(G, nodes, **attr):
    """Add a star to Graph G.

    The first node in nodes is the middle of the star.
    It is connected to all other nodes.

    Parameters
    ----------
    nodes : iterable container
        A container of nodes.
    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to every edge in star.

    See Also
    --------
    add_path, add_cycle

    Examples
    --------
    >>> G = nx.Graph()
    >>> nx.add_star(G, [0, 1, 2, 3])
    >>> nx.add_star(G, [10, 11, 12], weight=2)
    """
    nlist = iter(nodes)
    v = next(nlist)
    edges = ((v, n) for n in nlist)
    G.add_edges_from(edges, **attr)


def add_path(G, nodes, **attr):
    """Add a path to the Graph G.

    Parameters
    ----------
    nodes : iterable container
        A container of nodes.  A path will be constructed from
        the nodes (in order) and added to the graph.
    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to every edge in path.

    See Also
    --------
    add_star, add_cycle

    Examples
    --------
    >>> G = nx.Graph()
    >>> nx.add_path(G, [0, 1, 2, 3])
    >>> nx.add_path(G, [10, 11, 12], weight=7)
    """
    G.add_edges_from(pairwise(nodes), **attr)


def add_cycle(G, nodes, **attr):
    """Add a cycle to the Graph G.

    Parameters
    ----------
    nodes: iterable container
        A container of nodes.  A cycle will be constructed from
        the nodes (in order) and added to the graph.
    attr : keyword arguments, optional (default= no attributes)
        Attributes to add to every edge in cycle.

    See Also
    --------
    add_path, add_star

    Examples
    --------
    >>> G = nx.Graph()   # or DiGraph, MultiGraph, MultiDiGraph, etc
    >>> nx.add_cycle(G, [0, 1, 2, 3])
    >>> nx.add_cycle(G, [10, 11, 12], weight=7)
    """
    G.add_edges_from(pairwise(nodes, cyclic=True), **attr)


def subgraph(G, nbunch):
    """Return the subgraph induced on nodes in nbunch.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    nbunch : list, iterable
       A container of nodes that will be iterated through once (thus
       it should be an iterator or be iterable).  Each element of the
       container should be a valid node type: any hashable type except
       None.  If nbunch is None, return all edges data in the graph.
       Nodes in nbunch that are not in the graph will be (quietly)
       ignored.

    Notes
    -----
    subgraph(G) calls G.subgraph()
    """
    return G.subgraph(nbunch)


def create_empty_copy(G, with_data=True):
    """Return a copy of the graph G with all of the edges removed.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    with_data :  bool (default=True)
       Propagate Graph and Nodes data to the new graph.

    See Also
    -----
    empty_graph

    """
    H = G.__class__()
    H.add_nodes_from(G.nodes(data=with_data))
    if with_data:
        H.graph.update(G.graph)
    return H


def info(G, n=None):
    """Print short summary of information for the graph G or the node n.

    Parameters
    ----------
    G : Networkx graph
       A graph
    n : node (any hashable)
       A node in the graph G
    """
    info='' # append this all to a string
    if n is None:
        info+="Name: %s\n"%G.name
        type_name = [type(G).__name__]
        info+="Type: %s\n"%",".join(type_name)
        info+="Number of nodes: %d\n"%G.number_of_nodes()
        info+="Number of edges: %d\n"%G.number_of_edges()
        nnodes=G.number_of_nodes()
        if len(G) > 0:
            if G.is_directed():
                info+="Average in degree: %8.4f\n"%\
                    (sum(d for n, d in G.in_degree())/float(nnodes))
                info+="Average out degree: %8.4f"%\
                    (sum(d for n, d in G.out_degree())/float(nnodes))
            else:
                s=sum(dict(G.degree()).values())
                info+="Average degree: %8.4f"%\
                    (float(s)/float(nnodes))

    else:
        if n not in G:
            raise nx.NetworkXError("node %s not in graph"%(n,))
        info+="Node % s has the following properties:\n"%n
        info+="Degree: %d\n"%G.degree(n)
        info+="Neighbors: "
        info+=' '.join(str(nbr) for nbr in G.neighbors(n))
    return info


def set_node_attributes(G, name, values):
    """Sets node attributes from a given value or dictionary of values.

    Parameters
    ----------
    G : NetworkX Graph

    name : string
       Name of the node attribute to set.

    values : dict
       Dictionary of attribute values keyed by node. If `values` is
       not a dictionary, then it is treated as a single attribute value
       that is then applied to every node in `G`. This means that if
       you provide a mutable object, like a list, updates to that object
       will be reflected in the node attribute for each node.

    Examples
    --------
    After computing some property of the nodes of a graph, you may want
    to assign a node attribute to store the value of that property for
    each node::

        >>> G = nx.path_graph(3)
        >>> bb = nx.betweenness_centrality(G)  # this is a dictionary
        >>> nx.set_node_attributes(G, 'betweenness', bb)
        >>> G.node[1]['betweenness']
        1.0

    If you provide a list as the third argument, updates to the list
    will be reflected in the node attribute for each node::

        >>> labels = []
        >>> nx.set_node_attributes(G, 'labels', labels)
        >>> labels.append('foo')
        >>> G.node[0]['labels']
        ['foo']
        >>> G.node[1]['labels']
        ['foo']
        >>> G.node[2]['labels']
        ['foo']

    """
    # Treat `value` as the attribute value for each node.
    if not isinstance(values, dict):
        values = dict(zip_longest(G, [], fillvalue=values))

    for node, value in values.items():
        G.node[node][name] = value


def get_node_attributes(G, name):
    """Get node attributes from graph

    Parameters
    ----------
    G : NetworkX Graph

    name : string
       Attribute name

    Returns
    -------
    Dictionary of attributes keyed by node.

    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_nodes_from([1,2,3],color='red')
    >>> color=nx.get_node_attributes(G,'color')
    >>> color[1]
    'red'
    """
    return {n: d[name] for n, d in G.node.items() if name in d}


def set_edge_attributes(G, name, values):
    """Sets edge attributes from a given value or dictionary of values.

    Parameters
    ----------
    G : NetworkX Graph

    name : string
       Name of the edge attribute to set.

    values : dict
       Dictionary of attribute values keyed by edge (tuple). For
       multigraphs, the tuples must be of the form ``(u, v, key)``,
       where `u` and `v` are nodes and `key` is the key corresponding to
       the edge. For non-multigraphs, the keys must be tuples of the
       form ``(u, v)``.

       If `values` is not a dictionary, then it is treated as a single
       attribute value that is then applied to every edge in `G`. This
       means that if you provide a mutable object, like a list, updates
       to that object will be reflected in the edge attribute for each
       edge.

    Examples
    --------
    After computing some property of the nodes of a graph, you may want
    to assign a node attribute to store the value of that property for
    each node::

        >>> G = nx.path_graph(3)
        >>> bb = nx.edge_betweenness_centrality(G, normalized=False)
        >>> nx.set_edge_attributes(G, 'betweenness', bb)
        >>> G.edge[1][2]['betweenness']
        2.0

    If you provide a list as the third argument, updates to the list
    will be reflected in the edge attribute for each node::

        >>> labels = []
        >>> nx.set_edge_attributes(G, 'labels', labels)
        >>> labels.append('foo')
        >>> G.edge[0][1]['labels']
        ['foo']
        >>> G.edge[1][2]['labels']
        ['foo']

    """
    # Treat `value` as the attribute value for each node.
    if not isinstance(values, dict):
        if G.is_multigraph():
            edges = G.edges(keys=True)
        else:
            edges = G.edges()
        values = dict(zip_longest(edges, [], fillvalue=values))

    if G.is_multigraph():
        for (u, v, key), value in values.items():
            G[u][v][key][name] = value
    else:
        for (u, v), value in values.items():
            G[u][v][name] = value


def get_edge_attributes(G, name):
    """Get edge attributes from graph

    Parameters
    ----------
    G : NetworkX Graph

    name : string
       Attribute name

    Returns
    -------
    Dictionary of attributes keyed by edge. For (di)graphs, the keys are
    2-tuples of the form: (u,v). For multi(di)graphs, the keys are 3-tuples of
    the form: (u, v, key).

    Examples
    --------
    >>> G=nx.Graph()
    >>> nx.add_path(G, [1, 2, 3], color='red')
    >>> color=nx.get_edge_attributes(G, 'color')
    >>> color[(1, 2)]
    'red'
    """
    if G.is_multigraph():
        edges = G.edges(keys=True, data=True)
    else:
        edges = G.edges(data=True)
    return {x[:-1]: x[-1][name] for x in edges if name in x[-1]}


def all_neighbors(graph, node):
    """ Returns all of the neighbors of a node in the graph.

    If the graph is directed returns predecessors as well as successors.

    Parameters
    ----------
    graph : NetworkX graph
        Graph to find neighbors.

    node : node
        The node whose neighbors will be returned.

    Returns
    -------
    neighbors : iterator
        Iterator of neighbors
    """
    if graph.is_directed():
        values = chain(graph.predecessors(node), graph.successors(node))
    else:
        values = graph.neighbors(node)
    return values


def non_neighbors(graph, node):
    """Returns the non-neighbors of the node in the graph.

    Parameters
    ----------
    graph : NetworkX graph
        Graph to find neighbors.

    node : node
        The node whose neighbors will be returned.

    Returns
    -------
    non_neighbors : iterator
        Iterator of nodes in the graph that are not neighbors of the node.
    """
    nbors = set(neighbors(graph, node)) | {node}
    return (nnode for nnode in graph if nnode not in nbors)


def non_edges(graph):
    """Returns the non-existent edges in the graph.

    Parameters
    ----------
    graph : NetworkX graph.
        Graph to find non-existent edges.

    Returns
    -------
    non_edges : iterator
        Iterator of edges that are not in the graph.
    """
    if graph.is_directed():
        for u in graph:
            for v in non_neighbors(graph, u):
                yield (u, v)
    else:
        nodes = set(graph)
        while nodes:
            u = nodes.pop()
            for v in nodes - set(graph[u]):
                yield (u, v)


@not_implemented_for('directed')
def common_neighbors(G, u, v):
    """Return the common neighbors of two nodes in a graph.

    Parameters
    ----------
    G : graph
        A NetworkX undirected graph.

    u, v : nodes
        Nodes in the graph.

    Returns
    -------
    cnbors : iterator
        Iterator of common neighbors of u and v in the graph.

    Raises
    ------
    NetworkXError
        If u or v is not a node in the graph.

    Examples
    --------
    >>> G = nx.complete_graph(5)
    >>> sorted(nx.common_neighbors(G, 0, 1))
    [2, 3, 4]
    """
    if u not in G:
        raise nx.NetworkXError('u is not in the graph.')
    if v not in G:
        raise nx.NetworkXError('v is not in the graph.')

    # Return a generator explicitly instead of yielding so that the above
    # checks are executed eagerly.
    return (w for w in G[u] if w in G[v] and w not in (u, v))


def is_weighted(G, edge=None, weight='weight'):
    """Returns True if `G` has weighted edges.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    edge : tuple, optional
        A 2-tuple specifying the only edge in `G` that will be tested. If
        None, then every edge in `G` is tested.

    weight: string, optional
        The attribute name used to query for edge weights.

    Returns
    -------
    bool
        A boolean signifying if `G`, or the specified edge, is weighted.

    Raises
    ------
    NetworkXError
        If the specified edge does not exist.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> nx.is_weighted(G)
    False
    >>> nx.is_weighted(G, (2, 3))
    False

    >>> G = nx.DiGraph()
    >>> G.add_edge(1, 2, weight=1)
    >>> nx.is_weighted(G)
    True

    """
    if edge is not None:
        data = G.get_edge_data(*edge)
        if data is None:
            msg = 'Edge {!r} does not exist.'.format(edge)
            raise nx.NetworkXError(msg)
        return weight in data

    if is_empty(G):
        # Special handling required since: all([]) == True
        return False

    return all(weight in data for u, v, data in G.edges(data=True))


def is_negatively_weighted(G, edge=None, weight='weight'):
    """Returns True if `G` has negatively weighted edges.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    edge : tuple, optional
        A 2-tuple specifying the only edge in `G` that will be tested. If
        None, then every edge in `G` is tested.

    weight: string, optional
        The attribute name used to query for edge weights.

    Returns
    -------
    bool
        A boolean signifying if `G`, or the specified edge, is negatively
        weighted.

    Raises
    ------
    NetworkXError
        If the specified edge does not exist.

    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_edges_from([(1, 3), (2, 4), (2, 6)])
    >>> G.add_edge(1, 2, weight=4)
    >>> nx.is_negatively_weighted(G, (1, 2))
    False
    >>> G[2][4]['weight'] = -2
    >>> nx.is_negatively_weighted(G)
    True
    >>> G = nx.DiGraph()
    >>> G.add_weighted_edges_from([('0', '3', 3), ('0', '1', -5), ('1', '0', -2)])
    >>> nx.is_negatively_weighted(G)
    True

    """
    if edge is not None:
        data = G.get_edge_data(*edge)
        if data is None:
            msg = 'Edge {!r} does not exist.'.format(edge)
            raise nx.NetworkXError(msg)
        return weight in data and data[weight] < 0

    return any(weight in data and data[weight] < 0
               for u, v, data in G.edges(data=True))


def is_empty(G):
    """Returns True if `G` has no edges.

    Parameters
    ----------
    G : graph
        A NetworkX graph.

    Returns
    -------
    bool
        True if `G` has no edges, and False otherwise.

    Notes
    -----
    An empty graph can have nodes but not edges. The empty graph with zero
    nodes is known as the null graph. This is an O(n) operation where n is the
    number of nodes in the graph.

    """
    return not any(G.adj.values())

