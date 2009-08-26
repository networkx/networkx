"""
Functional interface to graph properties.
    
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#

# functional style helpers

__all__ = ['nodes', 'edges', 'degree', 'degree_histogram', 'neighbors',
           'number_of_nodes', 'number_of_edges', 'density',
           'nodes_iter', 'edges_iter', 'is_directed','info']

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

def degree(G,nbunch=None,with_labels=False):
    """Return degree of single node or of nbunch of nodes.
    If nbunch is ommitted, then return degrees of *all* nodes.
    """
    return G.degree(nbunch,with_labels=with_labels)

def neighbors(G,n):
    """Return a list of nodes connected to node n. """
    return G.neighbors(n)

def number_of_nodes(G):
    """Return the order of a graph = number of nodes."""
    return G.number_of_nodes()

def number_of_edges(G):
    """Return the size of a graph = number of edges. """
    return G.number_of_edges()
    
def density(G):
    """Return the density of a graph.
    
    density = size/(order*(order-1)/2)
    density()=0.0 for an edge-less graph and 1.0 for a complete graph.
    """
    n=number_of_nodes(G)
    e=number_of_edges(G)
    if e==0: # includes cases n==0 and n==1
        return 0.0
    else:
        return e*2.0/float(n*(n-1))

def degree_histogram(G):
    """Return a list of the frequency of each degree value.
    
    The degree values are the index in the list.
    Note: the bins are width one, hence len(list) can be large
    (Order(number_of_edges))
    """
    degseq=G.degree()
    dmax=max(degseq)+1
    freq= [ 0 for d in xrange(dmax) ]
    for d in degseq:
        freq[d] += 1
    return freq

def is_directed(G):
    """ Return True if graph is directed."""
    return G.is_directed()

def info(G, n=None):
    """Print short info summary for graph G or node n."""
    import textwrap
    width_left = 22

    if n is None:
        print ("Name:").ljust(width_left), G.name
        type_name = [type(G).__name__]
        print ("Type:").ljust(width_left), ",".join(type_name)
        print ("Number of nodes:").ljust(width_left), G.number_of_nodes()
        print ("Number of edges:").ljust(width_left), G.number_of_edges()
        if len(G) > 0:
            if G.is_directed():
                print ("Average in degree:").ljust(width_left), \
                    round( sum(G.in_degree())/float(len(G)), 4)
                print ("Average out degree:").ljust(width_left), \
                    round( sum(G.out_degree())/float(len(G)), 4)
            else:
                print ("Average degree:").ljust(width_left), \
                    round( sum(G.degree())/float(len(G)), 4)

    else:
        try:
            list_neighbors = G.neighbors(n)
        except (KeyError, TypeError):
            raise NetworkXError, "node %s not in graph"%(n,)
        print "\nNode", n, "has the following properties:"
        print ("Degree:").ljust(width_left), len(list_neighbors)
        str_neighbors = str(list_neighbors)
        str_neighbors = str_neighbors[1:len(str_neighbors)-1]
        wrapped_neighbors = textwrap.wrap(str_neighbors, 50)
        print ("Neighbors:").ljust(width_left), wrapped_neighbors[0]
        for i in wrapped_neighbors[1:]:
            print "".ljust(width_left), i
