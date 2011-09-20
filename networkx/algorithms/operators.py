"""
Operations on graphs including union, intersection, difference,
complement, subgraph. 
"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
                           'Pieter Swart (swart@lanl.gov)',
                           'Dan Schult(dschult@colgate.edu)'])

__all__ = ['union', 'compose', 'complement',
           'disjoint_union', 'intersection', 
           'difference', 'symmetric_difference']

import networkx as nx
from networkx.utils import is_string_like

def union(G,H,create_using=None,rename=False,name=None):
    """ Return the union of graphs G and H.
    
    Graphs G and H must be disjoint, otherwise an exception is raised.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph 

    create_using : NetworkX graph
       Use specified graph for result.  Otherwise a new graph is created
       with the same type as G.

    rename : bool (default=False)         
       Node names of G and H can be changed be specifying the tuple
       rename=('G-','H-') (for example).  Node u in G is then renamed
       "G-u" and v in H is renamed "H-v".

    name : string       
       Specify the name for the union graph

    Notes       
    -----
    To force a disjoint union with node relabeling, use
    disjoint_union(G,H) or convert_node_labels_to integers().

    Graph, edge, and node attributes are propagated from G and H
    to the union graph.  If a graph attribute is present in both
    G and H the value from G is used.


    See Also
    --------
    disjoint_union

    """
    if name is None:
        name="union( %s, %s )"%(G.name,H.name)
    if create_using is None:
        R=G.__class__()
    else:
        R=create_using
        R.clear()
    R.name=name

    # rename graph to obtain disjoint node labels
    if rename: # create new string labels
        def add_prefix0(x):
            prefix=rename[0]
            if is_string_like(x):
                name=prefix+x
            else:
                name=prefix+repr(x)
            return name
        def add_prefix1(x):
            prefix=rename[1]
            if is_string_like(x):
                name=prefix+x
            else:
                name=prefix+repr(x)
            return name
        G=nx.relabel_nodes(G,add_prefix0)
        H=nx.relabel_nodes(H,add_prefix1)

    if set(G) & set(H):
        raise nx.NetworkXError(\
            """The node sets of G and H are not disjoint. 
Use appropriate rename=('Gprefix','Hprefix') or use disjoint_union(G,H).""")
    # node names OK, now build union
    R.add_nodes_from(G)
    if G.is_multigraph():
        R.add_edges_from(e for e in G.edges_iter(keys=True,data=True))
    else:
        R.add_edges_from(e for e in G.edges_iter(data=True))
    R.add_nodes_from(H)
    if H.is_multigraph():
        R.add_edges_from(e for e in H.edges_iter(keys=True,data=True))
    else:
        R.add_edges_from(e for e in H.edges_iter(data=True))

    # add node attributes
    R.node.update(G.node)
    R.node.update(H.node)
    # add graph attributes, G attributes take precedent over H attributes
    R.graph.update(H.graph)
    R.graph.update(G.graph)
    return R


def disjoint_union(G,H):
    """ Return the disjoint union of graphs G and H, forcing distinct integer node labels.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph 

    Notes
    -----
    A new graph is created, of the same class as G.  It is recommended
    that G and H be either both directed or both undirected.

    """
    R1=nx.convert_node_labels_to_integers(G)
    R2=nx.convert_node_labels_to_integers(H,first_label=len(R1))
    R=union(R1,R2)
    R.name="disjoint_union( %s, %s )"%(G.name,H.name)
    return R


def intersection(G,H,create_using=None ):
    """Return a new graph that contains only the edges that exist in both G and H.   

    The node sets of H and G must be the same.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph.  G and H must have the same node sets. 

    create_using : NetworkX graph
       Use specified graph for result.  Otherwise a new graph is created
       with the same type as G.

    Notes
    -----
    Attributes from the graph, nodes, and edges are not copied to the new
    graph.  If you want a new graph of the intersection of G and H
    with the attributes (including edge data) from G use remove_nodes_from()
    as follows

    >>> G=nx.path_graph(3)
    >>> H=nx.path_graph(5)
    >>> R=G.copy()
    >>> R.remove_nodes_from(n for n in G if n not in H)

    """
    # create new graph         
    if create_using is None:  # Graph object of the same type as G
        R=nx.create_empty_copy(G)
    else:                     # user specified graph 
        R=create_using 
        R.clear() 

    R.name="Intersection of (%s and %s)"%(G.name, H.name)

    if set(G)!=set(H):
        raise nx.NetworkXError("Node sets of graphs are not equal")     
    
    if G.number_of_edges()<=H.number_of_edges():
        if G.is_multigraph():
            edges=G.edges_iter(keys=True)
        else:
            edges=G.edges_iter()
        for e in edges:
            if H.has_edge(*e):
                R.add_edge(*e)
    else:
        if H.is_multigraph():
            edges=H.edges_iter(keys=True)
        else:
            edges=H.edges_iter()
        for e in edges:
            if G.has_edge(*e):
                R.add_edge(*e)

    return R

def difference(G,H,create_using=None):
    """Return a new graph that contains the edges that exist in G 
    but not in H.  

    The node sets of H and G must be the same.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph.  G and H must have the same node sets. 

    create_using : NetworkX graph
       Use specified graph for result.  Otherwise a new graph is created
       with the same type as G.

    Notes
    -----
    Attributes from the graph, nodes, and edges are not copied to the new
    graph.  If you want a new graph of the difference of G and H with
    with the attributes (including edge data) from G use remove_nodes_from()
    as follows

    >>> G=nx.path_graph(3)
    >>> H=nx.path_graph(5)
    >>> R=G.copy()
    >>> R.remove_nodes_from(n for n in G if n in H)

    """
    # create new graph         
    if create_using is None:  # Graph object of the same type as G
        R=nx.create_empty_copy(G)
    else:                     # user specified graph 
        R=create_using 
        R.clear() 

    R.name="Difference of (%s and %s)"%(G.name, H.name)

    if set(G)!=set(H):
        raise nx.NetworkXError("Node sets of graphs not equal")        
    
    if G.is_multigraph():
        edges=G.edges_iter(keys=True)
    else:
        edges=G.edges_iter()
    for e in edges:
        if not H.has_edge(*e):
            R.add_edge(*e)
    return R

def symmetric_difference(G,H,create_using=None ):
    """Return new graph with edges that exist in either G or H but not both.

    The node sets of H and G must be the same.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph.  G and H must have the same node sets. 

    create_using : NetworkX graph
       Use specified graph for result.  Otherwise a new graph is created
       with the same type as G.

    Notes
    -----
    Attributes from the graph, nodes, and edges are not copied to the new
    graph. 
    """
    # create new graph         
    if create_using is None:  # Graph object of the same type as G
        R=nx.create_empty_copy(G)
    else:                     # user specified graph 
        R=create_using 
        R.clear() 

    R.name="Symmetric difference of (%s and %s)"%(G.name, H.name)

    if set(G)!=set(H):
        raise nx.NetworkXError("Node sets of graphs not equal")        
    
    gnodes=set(G) # set of nodes in G
    hnodes=set(H) # set of nodes in H
    nodes=gnodes.symmetric_difference(hnodes)
    R.add_nodes_from(nodes)
    
    if G.is_multigraph():
        edges=G.edges_iter(keys=True)
    else:
        edges=G.edges_iter()
    # we could copy the data here but then this function doesn't
    # match intersection and difference
    for e in edges:
        if not H.has_edge(*e):
            R.add_edge(*e)

    if H.is_multigraph():
        edges=H.edges_iter(keys=True)
    else:
        edges=H.edges_iter()
    for e in edges:
        if not G.has_edge(*e):
            R.add_edge(*e)
    return R

def compose(G,H,create_using=None, name=None):
    """ Return a new graph of G composed with H.
    
    Composition is the simple union of the node sets and edge sets.
    The node sets of G and H need not be disjoint.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph 

    create_using : NetworkX graph
       Use specified graph for result.  Otherwise a new graph is created
       with the same type as G

    name : string       
       Specify name for new graph

    Notes
    -----
    A new graph is returned, of the same class as G.  It is
    recommended that G and H be either both directed or both
    undirected.  Attributes from G take precedent over attributes
    from H.

    """
    if name is None:
        name="compose( %s, %s )"%(G.name,H.name)
    if create_using is None:
        R=G.__class__()
    else:
        R=create_using
        R.clear()
    R.name=name
    R.add_nodes_from(H.nodes())
    R.add_nodes_from(G.nodes())
    if H.is_multigraph():
        R.add_edges_from(H.edges_iter(keys=True,data=True))
    else:
        R.add_edges_from(H.edges_iter(data=True))
    if G.is_multigraph():
        R.add_edges_from(G.edges_iter(keys=True,data=True))
    else:
        R.add_edges_from(G.edges_iter(data=True))

    # add node attributes, G attributes take precedent over H attributes
    R.node.update(H.node)
    R.node.update(G.node)
    # add graph attributes, G attributes take precedent over H attributes
    R.graph.update(H.graph)
    R.graph.update(G.graph)

    return R


def complement(G,create_using=None,name=None):
    """ Return graph complement of G.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    create_using : NetworkX graph
       Use specified graph for result.  Otherwise a new graph is created.

    name : string       
       Specify name for new graph

    Notes
    ------
    Note that complement() does not create self-loops and also 
    does not produce parallel edges for MultiGraphs.

    Graph, node, and edge data are not propagated to the new graph.
    """
    if name is None:
        name="complement(%s)"%(G.name) 
    if create_using is None:
        R=G.__class__()
    else:
        R=create_using
        R.clear()
    R.name=name
    R.add_nodes_from(G)
    R.add_edges_from( ((n,n2) 
                       for n,nbrs in G.adjacency_iter() 
                       for n2 in G if n2 not in nbrs 
                       if n != n2) )
    return R



