"""
Operations on graphs; including  union, intersection, difference,
complement, subgraph. 
"""
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
                           'Pieter Swart (swart@lanl.gov)',
                           'Dan Schult(dschult@colgate.edu)'])

__all__ = ['union', 'cartesian_product', 
           'compose', 'complement',
           'disjoint_union', 'intersection', 
           'difference', 'symmetric_difference',
           'convert_node_labels_to_integers', 'relabel_nodes']

import networkx
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
        import functools
        def add_prefix(x,prefix=''):
            if is_string_like(x):
                name=prefix+x
            else:
                name=prefix+repr(x)
            return name
        mapping=functools.partial(add_prefix,prefix=rename[0])
        G=relabel_nodes(G,mapping)
        mapping=functools.partial(add_prefix,prefix=rename[1])
        H=relabel_nodes(H,mapping)

    if set(G) & set(H):
        raise networkx.NetworkXError(\
            """The node sets of G and H are not disjoint. 
Use appropriate rename=('Gprefix','Hprefix') or use disjoint_union(G,H).""")
    # node names OK, now build union
    R.add_nodes_from(G)
    R.add_edges_from(e for e in G.edges_iter(data=True))
    R.add_nodes_from(H)
    R.add_edges_from(e for e in H.edges_iter(data=True))

    # add node attributes
    R.node.update(G.node)
    R.node.update(H.node)
    # add graph attributes, G attributes take precedent over H attributes
    R.graph.update(H.graph)
    R.graph.update(G.graph)
    return R


def disjoint_union(G,H):
    """ Return the disjoint union of graphs G and H, forcing distinct integer
    node labels.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph 

    Notes
    -----
    A new graph is created, of the same class as G.  It is recommended
    that G and H be either both directed or both undirected.

    """
    R1=convert_node_labels_to_integers(G)
    R2=convert_node_labels_to_integers(H,first_label=len(R1))
    R=union(R1,R2)
    R.name="disjoint_union( %s, %s )"%(G.name,H.name)
    return R


def intersection(G,H,create_using=None ):
    """Return a new graph that contains only the edges that exist in 
    both G and H.   

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
        R=networkx.create_empty_copy(G)
    else:                     # user specified graph 
        R=create_using 
        R.clear() 

    R.name="Intersection of (%s and %s)"%(G.name, H.name)

    if set(G)!=set(H):
        raise networkx.NetworkXError("Node sets of graphs are not equal")     
    
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
    """Return a new graph that contains the edges that exist in 
    in G but not in H.  

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
        R=networkx.create_empty_copy(G)
    else:                     # user specified graph 
        R=create_using 
        R.clear() 

    R.name="Difference of (%s and %s)"%(G.name, H.name)

    if set(G)!=set(H):
        raise networkx.NetworkXError("Node sets of graphs not equal")        
    
    if G.number_of_edges()<=H.number_of_edges():
        if G.is_multigraph():
            edges=G.edges_iter(keys=True)
        else:
            edges=G.edges_iter()
        for e in edges:
            if not H.has_edge(*e):
                R.add_edge(*e)
    else:
        if H.is_multigraph():
            edges=H.edges_iter(keys=True)
        else:
            edges=H.edges_iter()
        for e in edges:
            if not G.has_edge(*e):
                R.add_edge(*e)

    return R

def symmetric_difference(G,H,create_using=None ):
    """Return new graph with edges that exist in in either G or H but
    not both.

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
        R=networkx.create_empty_copy(G)
    else:                     # user specified graph 
        R=create_using 
        R.clear() 

    R.name="Symmetric difference of (%s and %s)"%(G.name, H.name)

    if set(G)!=set(H):
        raise networkx.NetworkXError("Node sets of graphs not equal")        
    
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

def cartesian_product(G,H,create_using=None):
    """ Return the Cartesian product of G and H.

    Parameters
    ----------
    G,H : graph
       A NetworkX graph 

    Notes
    -----
    Only tested with Graph class.  Graph, node, and edge attributes
    are not copied to the new graph.
    """
    if create_using is None:
        Prod=G.__class__()
    else:
        Prod=create_using
        Prod.clear()

    for v in G:
        for w in H:
            Prod.add_node((v,w)) 

    if G.is_multigraph():
        Prod.add_edges_from( (((v,w1),(v,w2),k,d) 
                              for w1,w2,k,d 
                              in H.edges_iter(keys=True,data=True) 
                              for v in G) )
        Prod.add_edges_from( (((v1,w),(v2,w),k,d) 
                              for v1,v2,k,d 
                              in G.edges_iter(keys=True,data=True) 
                              for w in H) )

    else:
        Prod.add_edges_from( (((v,w1),(v,w2),d) 
                              for w1,w2,d in H.edges_iter(data=True) 
                              for v in G) )
        Prod.add_edges_from( (((v1,w),(v2,w),d) 
                              for v1,v2,d in G.edges_iter(data=True) 
                              for w in H) )

    Prod.name="Cartesian Product("+G.name+","+H.name+")"
    return Prod


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

    Graph, node, and edge data is not propagated to the new graph.
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
    R.add_edges_from( ((n,n2) for n,nbrs in G.adjacency_iter() for n2 in G 
        if n2 not in nbrs if n is not n2) )
    return R



def convert_to_undirected(G):
    """Return a new undirected representation of the graph G.

    """
    return G.to_undirected()


def convert_to_directed(G):
    """Return a new directed representation of the graph G.

    """
    return G.to_directed()


def relabel_nodes(G,mapping):
    """Return a copy of G with node labels transformed by mapping.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    mapping : dictionary or function
       Either a dictionary with the old labels as keys and new labels as values
       or a function transforming an old label with a new label.
       In either case, the new labels must be hashable Python objects.

    Examples
    --------
    mapping as dictionary

    >>> G=nx.path_graph(3)  # nodes 0-1-2
    >>> mapping={0:'a',1:'b',2:'c'}
    >>> H=nx.relabel_nodes(G,mapping)
    >>> print H.nodes()
    ['a', 'c', 'b']

    >>> G=nx.path_graph(26) # nodes 0..25
    >>> mapping=dict(zip(G.nodes(),"abcdefghijklmnopqrstuvwxyz"))
    >>> H=nx.relabel_nodes(G,mapping) # nodes a..z
    >>> mapping=dict(zip(G.nodes(),xrange(1,27)))
    >>> G1=nx.relabel_nodes(G,mapping) # nodes 1..26

    mapping as function

    >>> G=nx.path_graph(3)
    >>> def mapping(x):
    ...    return x**2
    >>> H=nx.relabel_nodes(G,mapping)
    >>> print H.nodes()
    [0, 1, 4]

    See Also
    --------
    convert_node_labels_to_integers()

    """
    H=G.__class__()
    H.name="(%s)" % G.name

    if hasattr(mapping,"__getitem__"):   # if we are a dict
        map_func=mapping.__getitem__   # call as a function
    else:
        map_func=mapping

    for node in G:
        try:
            H.add_node(map_func(node))
        except:
            raise networkx.NetworkXError,\
                  "relabeling function cannot be applied to node %s" % node

    #for n1,n2,d in G.edges_iter(data=True):
    #    u=map_func(n1)
    #    v=map_func(n2)
    #    H.add_edge(u,v,d)
    if G.is_multigraph():
        H.add_edges_from( (map_func(n1),map_func(n2),k,d) 
                          for (n1,n2,k,d) in G.edges_iter(keys=True,data=True)) 
    else:
        H.add_edges_from( (map_func(n1),map_func(n2),d) 
                          for (n1,n2,d) in G.edges_iter(data=True)) 

    H.node.update(dict((map_func(n),d) for n,d in G.node.iteritems()))
    H.graph.update(G.graph)

    return H        
    

def relabel_nodes_with_function(G, func):
    """Deprecated: call relabel_nodes(G,func)."""
    return relabel_nodes(G,func)


def convert_node_labels_to_integers(G,first_label=0,
                                    ordering="default",
                                    discard_old_labels=True):
    """ Return a copy of G node labels replaced with integers.

    Parameters
    ----------
    G : graph
       A NetworkX graph 

    first_label : int, optional (default=0)       
       An integer specifying the offset in numbering nodes.
       The n new integer labels are numbered first_label, ..., n+first_label.

    ordering : string
        "default" : inherit node ordering from G.nodes() 
        "sorted"  : inherit node ordering from sorted(G.nodes())
        "increasing degree" : nodes are sorted by increasing degree
        "decreasing degree" : nodes are sorted by decreasing degree

    discard_old_labels : bool, optional (default=True)
       if True (default) discard old labels
       if False, create a dict self.node_labels that maps new
       labels to old labels
    """
#    This function strips information attached to the nodes and/or
#    edges of a graph, and returns a graph with appropriate integer
#    labels. One can view this as a re-labeling of the nodes. Be
#    warned that the term "labeled graph" has a loaded meaning
#    in graph theory. The fundamental issue is whether the names
#    (labels) of the nodes (and edges) matter in deciding when two
#    graphs are the same. For example, in problems of graph enumeration
#    there is a distinct difference in techniques required when
#    counting labeled vs. unlabeled graphs.

#    When implementing graph
#    algorithms it is often convenient to strip off the original node
#    and edge information and appropriately relabel the n nodes with
#    the integer values 1,..,n. This is the purpose of this function,
#    and it provides the option (see discard_old_labels variable) to either
#    preserve the original labels in separate dicts (these are not
#    returned but made an attribute of the new graph.

    N=G.number_of_nodes()+first_label
    if ordering=="default":
        mapping=dict(zip(G.nodes(),range(first_label,N)))
    elif ordering=="sorted":
        nlist=G.nodes()
        nlist.sort()
        mapping=dict(zip(nlist,range(first_label,N)))
    elif ordering=="increasing degree":
        dv_pairs=[(d,n) for (n,d) in G.degree_iter()]
        dv_pairs.sort() # in-place sort from lowest to highest degree
        mapping=dict(zip([n for d,n in dv_pairs],range(first_label,N)))
    elif ordering=="decreasing degree":
        dv_pairs=[(d,n) for (n,d) in G.degree_iter()]
        dv_pairs.sort() # in-place sort from lowest to highest degree
        dv_pairs.reverse()
        mapping=dict(zip([n for d,n in dv_pairs],range(first_label,N)))
    else:
        raise networkx.NetworkXError,\
              "unknown value of node ordering variable: ordering"

    H=relabel_nodes(G,mapping)

    H.name="("+G.name+")_with_int_labels"
    if not discard_old_labels:
        H.node_labels=mapping
    return H




