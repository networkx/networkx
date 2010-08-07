"""
Functional interface to graph methods and assorted utilities.

"""
from __future__ import print_function

__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
                           'Pieter Swart (swart@lanl.gov)',
                           'Dan Schult(dschult@colgate.edu)'])
#    Copyright (C) 2004-2010 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
import networkx as nx

# functional style helpers


__all__ = ['nodes', 'edges', 'degree', 'degree_histogram', 'neighbors',
           'number_of_nodes', 'number_of_edges', 'density',
           'nodes_iter', 'edges_iter', 'is_directed','info',
           'freeze','is_frozen','subgraph','create_empty_copy']

def nodes(G):
    """Return a copy of the graph nodes in a list."""
    return G.nodes()

def nodes_iter(G):
    """Return an iterator over the graph nodes."""
    return G.nodes_iter()

def edges(G,nbunch=None):
    """Return list of  edges adjacent to nodes in nbunch.

    Return all edges if nbunch is unspecified or nbunch=None.

    For digraphs, edges=out_edges
    """
    return G.edges(nbunch)

def edges_iter(G,nbunch=None):
    """Return iterator over  edges adjacent to nodes in nbunch.

    Return all edges if nbunch is unspecified or nbunch=None.

    For digraphs, edges=out_edges
    """
    return G.edges_iter(nbunch)

def degree(G,nbunch=None,weighted=False):
    """Return degree of single node or of nbunch of nodes.
    If nbunch is ommitted, then return degrees of *all* nodes.
    """
    return G.degree(nbunch,weighted=weighted)

def neighbors(G,n):
    """Return a list of nodes connected to node n. """
    return G.neighbors(n)

def number_of_nodes(G):
    """Return the number of nodes in the graph."""
    return G.number_of_nodes()

def number_of_edges(G):
    """Return the number of edges in the graph. """
    return G.number_of_edges()

def density(G):
    """Return the density of a graph.

    The density for undirected graphs is

    .. math::

       d = \\frac{2m}{n(n-1)},

    and for directed graphs is

    .. math::

       d = \\frac{m}{n(n-1)},

    where :math:`n` is the number of nodes and :math:`m`
    is the number of edges in :math:`G`.

    Notes
    -----
    The density is 0 for an graph without edges and 1.0 for a complete graph.

    The density of multigraphs can be higher than 1.

    """
    n=number_of_nodes(G)
    m=number_of_edges(G)
    if m==0: # includes cases n==0 and n==1
        d=0.0
    else:
        if G.is_directed():
            d=m/float(n*(n-1))
        else:
            d= m*2.0/float(n*(n-1))
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
    degseq=list(G.degree().values())
    dmax=max(degseq)+1
    freq= [ 0 for d in range(dmax) ]
    for d in degseq:
        freq[d] += 1
    return freq

def is_directed(G):
    """ Return True if graph is directed."""
    return G.is_directed()


def freeze(G):
    """Modify graph to prevent addition of nodes or edges.

    Parameters
    -----------
    G : graph
      A NetworkX graph

    Examples
    --------
    >>> G=nx.Graph()
    >>> G.add_path([0,1,2,3])
    >>> G=nx.freeze(G)
    >>> try:
    ...    G.add_edge(4,5)
    ... except nx.NetworkXError as e:
    ...    print(str(e))
    Frozen graph can't be modified

    Notes
    -----
    This does not prevent modification of edge data.

    To "unfreeze" a graph you must make a copy.

    See Also
    --------
    is_frozen

    """
    def frozen(*args):
        raise nx.NetworkXError("Frozen graph can't be modified")
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
    -----------
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

def create_empty_copy(G,with_nodes=True):
    """Return a copy of the graph G with all of the edges removed.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    with_nodes :  bool (default=True)
       Include nodes.

    Notes
    -----
    Graph, node, and edge data is not propagated to the new graph.
    """
    H=G.__class__()

    H.name='empty '+G.name
    if with_nodes:
        H.add_nodes_from(G)
    return H


def info(G, n=None, file=None):
    """Print short summary of information for graph G or node n.

    Parameters
    ----------
    G : Networkx graph
       A graph
    n : node (any hashable)
       A node from the graph G
    file:  filehandle, optional (default=sys.stdout)
       Write data to opened file
    """
    
    import textwrap
    width_left = 22

    if file is None:
        import sys
        f=sys.stdout
    else:
        f=file

    if n is None:
        print(("Name:").ljust(width_left), G.name, file=f)
        type_name = [type(G).__name__]
        print(("Type:").ljust(width_left), ",".join(type_name), file=f)
        print(("Number of nodes:").ljust(width_left), 
              G.number_of_nodes(), file=f)
        print(("Number of edges:").ljust(width_left), 
              G.number_of_edges(), file=f)
        if len(G) > 0:
            if G.is_directed():
                print(("Average in degree:").ljust(width_left), 
                      round( sum(G.in_degree().values())/float(len(G)), 4), 
                      file=f)
                print(("Average out degree:").ljust(width_left), 
                      round( sum(G.out_degree().values())/float(len(G)), 4), 
                      file=f)
            else:
                print(("Average degree:").ljust(width_left), 
                      round( sum(G.degree().values())/float(len(G)), 4), 
                      file=f)

    else:
        try:
            list_neighbors = G.neighbors(n)
        except (KeyError, TypeError):
            raise NetworkXError("node %s not in graph"%(n,))
        print("Node", n, "has the following properties:", file=f)
        print(("Degree:").ljust(width_left), len(list_neighbors), file=f)
        str_neighbors = str(list_neighbors)
        str_neighbors = str_neighbors[1:len(str_neighbors)-1]
        wrapped_neighbors = textwrap.wrap(str_neighbors, 50)
        print(("Neighbors:").ljust(width_left), wrapped_neighbors[0], file=f)
        for i in wrapped_neighbors[1:]:
            print("".ljust(width_left), i, file=f)
