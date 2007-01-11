"""
Operations on graphs; including  union, complement, subgraph. 

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
__date__ = "$Date$"
__credits__ = """"""
__revision__ = "$Revision: 1024 $"
#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import networkx
from networkx.utils import is_string_like

def subgraph(G, nbunch, inplace=False, create_using=None):
    """
    Return the subgraph induced on nodes in nbunch.

    nbunch: can be a singleton node, a string (which is treated
    as a singleton node), or any iterable container of
    of nodes. (It can be an iterable or an iterator, e.g. a list,
    set, graph, file, numeric array, etc.)

    Setting inplace=True will return the induced subgraph in the
    original graph by deleting nodes not in nbunch. This overrides
    create_using.  Warning: this can destroy the graph.

    Unless otherwise specified, return a new graph of the same
    type as self.  Use (optional) create_using=R to return the
    resulting subgraph in R. R can be an existing graph-like
    object (to be emptied) or R is a call to a graph object,
    e.g. create_using=DiGraph(). See documentation for
    empty_graph.

    Implemented for Graph, DiGraph, XGraph, XDiGraph

    Note: subgraph(G) calls G.subgraph()

    """
    H = G.subgraph(nbunch, inplace, create_using)
    return H
                                                                                
def union(G,H,create_using=None,rename=False,name=None):
    """ Return the union of graphs G and H.
    
    Graphs G and H must be disjoint, otherwise an exception is raised.

    Node names of G and H can be changed be specifying the tuple
    rename=('G-','H-') (for example).
    Node u in G is then renamed "G-u" and v in H is renamed "H-v".

    To force a disjoint union with node relabeling, use
    disjoint_union(G,H) or convert_node_labels_to integers().

    Optional create_using=R returns graph R filled in with the
    union of G and H.  Otherwise a new graph is created, of the
    same class as G.  It is recommended that G and H be either
    both directed or both undirected.

    A new name can be specified in the form
    X=graph_union(G,H,name="new_name")

    Implemented for Graph, DiGraph, XGraph, XDiGraph.        

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
    # note that for objects w/o succinct __name__,
    # the new labels can be quite verbose
    # See also disjoint_union
    Gname={}
    Hname={}
    if rename: # create new string labels
        for v in G:
            if is_string_like(v):
                Gname.setdefault(v,rename[0]+v)
            else:
                Gname.setdefault(v,rename[0]+repr(v))
        for v in H:
            if is_string_like(v):
                Hname.setdefault(v,rename[1]+v)
            else:
                Hname.setdefault(v,rename[1]+repr(v))
    else:
        for v in G:
            Gname.setdefault(v,v)
        for v in H:
            Hname.setdefault(v,v)

    # node name check
    for n in Gname.values():
        if n in Hname.values():
            raise networkx.NetworkXError,\
            "node sets of G and H are not disjoint. Use appropriate rename=('Gprefix','Hprefix')"
    # node names OK, now build union
    for v in G:
        R.add_node(Gname[v])
    G_edges=G.edges_iter()
    for e in G_edges:
        if len(e)==2:
            u,v=e
            R.add_edge(Gname[u],Gname[v])
        else:
            u,v,x=e
            R.add_edge(Gname[u],Gname[v],x)
    for v in H:
        R.add_node(Hname[v])
    H_edges=H.edges_iter()
    for e in H_edges:
        if len(e)==2:
            u,v=e
            R.add_edge(Hname[u],Hname[v])
        else:
            u,v,x=e
            R.add_edge(Hname[u],Hname[v],x)        
    return R


def disjoint_union(G,H):
    """ Return the disjoint union of graphs G and H, forcing distinct integer
    node labels.

    A new graph is created, of the same class as G.
    It is recommended that G and H be either both directed or both
    undirected.

    Implemented for Graph, DiGraph, XGraph, XDiGraph.

    """

    R1=convert_node_labels_to_integers(G)
    R2=convert_node_labels_to_integers(H,first_label=networkx.number_of_nodes(R1))
    R=union(R1,R2)
    R.name="disjoint_union( %s, %s )"%(G.name,H.name)
    return R


def cartesian_product(G,H):
    """ Return the Cartesian product of G and H.

    Tested only on Graph class.
    
    """

    Prod=networkx.Graph()

    for v in G:
        for w in H:
            Prod.add_node((v,w)) 

    H_edges=H.edges_iter()
    for (w1,w2) in H_edges:
        for v in G:
            Prod.add_edge((v,w1),(v,w2))

    G_edges=G.edges_iter()
    for (v1,v2) in G_edges:
        for w in H:
            Prod.add_edge((v1,w),(v2,w))

    Prod.name="Cartesian Product("+G.name+","+H.name+")"
    return Prod


def compose(G,H,create_using=None, name=None):
    """ Return a new graph of G composed with H.
    
    The node sets of G and H need not be disjoint.

    A new graph is returned, of the same class as G.
    It is recommended that G and H be either both directed or both
    undirected.

    Optional create_using=R returns graph R filled in with the
    compose(G,H).  Otherwise a new graph is created, of the
    same class as G.  It is recommended that G and H be either
    both directed or both undirected.

    Implemented for Graph, DiGraph, XGraph, XDiGraph    

    """
    if name is None:
        name="compose( %s, %s )"%(G.name,H.name)
    if create_using is None:
        R=G.__class__()
    else:
        R=create_using
        R.clear()
    R.name=name
    R.add_nodes_from([v for v in G.nodes() ])
    R.add_edges_from(G.edges())
    R.add_nodes_from([v for v in H.nodes() ])
    R.add_edges_from(H.edges())
    return R


def complement(G,create_using=None,name=None):
    """ Return graph complement of G.

    Unless otherwise specified, return a new graph of the same type as
    self.  Use (optional) create_using=R to return the resulting
    subgraph in R. R can be an existing graph-like object (to be
    emptied) or R can be a call to a graph object,
    e.g. create_using=DiGraph(). See documentation for empty_graph()

    Implemented for Graph, DiGraph, XGraph, XDiGraph.    
    Note that complement() is not well-defined for XGraph and XDiGraph
    objects that allow multiple edges or self-loops.

    """
    if name is None:
        name="complement(%s)"%(G.name) 
    if create_using is None:
        R=G.__class__()
    else:
        R=create_using
        R.clear()
    R.name=name
    R.add_nodes_from([v for v in G.nodes() ])
    for v in G.nodes():
        for u in G.nodes():
            if not G.has_edge(v,u):
                R.add_edge(v,u) 
    return R


def create_empty_copy(G):
    """Return a copy of the graph G with all of the edges removed.

    """
    H=G.__class__()
    H.name='empty '+G.name
    H.add_nodes_from(G)
    return H


def convert_to_undirected(G):
    """Return a new undirected representation of the graph G.

    Works for Graph, DiGraph, XGraph, XDiGraph.

    Note: convert_to_undirected(G)=G.to_undirected()

    """
    return G.to_undirected()


def convert_to_directed(G):
    """Return a new directed representation of the graph G.

    Works for Graph, DiGraph, XGraph, XDiGraph.

    Note: convert_to_directed(G)=G.to_directed()
    
    """
    return G.to_directed()

def relabel_nodes(G,mapping):
    """Return a copy of G with node labels transformed by mapping.

    mapping is either
      - a dictionary with the old labels as keys and new labels as values
      - a function transforming an old label with a new label

    In either case, the new labels must be hashable Python objects.

    mapping as dictionary:

    >>> G=path_graph(3)  # nodes 0-1-2
    >>> mapping={0:'a',1:'b',2:'c'}
    >>> H=relabel_nodes(G,mapping)
    >>> print H.nodes()
    ['a', 'c', 'b']

    >>> G=path_graph(26) # nodes 0..25
    >>> mapping=dict(zip(G.nodes(),"abcdefghijklmnopqrstuvwxyz"))
    >>> H=relabel_nodes(G,mapping) # nodes a..z
    >>> mapping=dict(zip(G.nodes(),xrange(1,27)))
    >>> G1=relabel_nodes(G,mapping) # nodes 1..26

    mapping as function

    >>> G=path_graph(3)
    >>> def mapping(x):
    ...    return x**2
    >>> H=relabel_nodes(G,mapping)
    >>> print H.nodes()
    [0, 1, 4]

    Also see convert_node_labels_to_integers.

    """
#    H=create_empty_copy(G)
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

    for e in G.edges_iter():
        u=map_func(e[0])
        v=map_func(e[1])
        if len(e)==2:
            H.add_edge(u,v)
        else:
            H.add_edge(u,v,e[2])

    return H        
    

def relabel_nodes_with_function(G, func):
    """Deprecated: call relabel_nodes(G,func)."""
    return relabel_nodes(G,func)


def convert_node_labels_to_integers(G,first_label=0,
                                    ordering="default",
                                    discard_old_labels=True):
    """ Return a copy of G, with n node labels replaced with integers,
    starting at first_label.

    first_label: (optional, default=0)

       An integer specifying the offset in numbering nodes.
       The n new integer labels are numbered first_label, ..., n+first_label.
    
    ordering: (optional, default="default")

       A string specifying how new node labels are ordered. 
       Possible values are: 

          "default" : inherit node ordering from G.nodes() 
          "sorted"  : inherit node ordering from sorted(G.nodes())
          "increasing degree" : nodes are sorted by increasing degree
          "decreasing degree" : nodes are sorted by decreasing degree

    *discard_old_labels*
       if True (default) discard old labels
       if False, create a dict self.node_labels that maps new
       labels to old labels

    Works for Graph, DiGraph, XGraph, XDiGraph
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
        dv_pairs=[(G.degree(n),n) for n in G]
        dv_pairs.sort() # in-place sort from lowest to highest degree
        mapping=dict(zip([n for d,n in dv_pairs],range(first_label,N)))
    elif ordering=="decreasing degree":
        dv_pairs=[(G.degree(n),n) for n in G]
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
    

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/operators.txt',package='networkx')
    return suite

if __name__ == "__main__":
    import os
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    # directory of networkx package (relative to this)
    nxbase=sys.path[0]+os.sep+os.pardir
    sys.path.insert(0,nxbase) # prepend to search path
    unittest.TextTestRunner().run(_test_suite())
    
