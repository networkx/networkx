"""
Operations on graphs; including  union, complement, subgraph. 

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
__date__ = "$Date: 2005-06-15 08:09:52 -0600 (Wed, 15 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1024 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

#from networkx.base import *
import networkx
from networkx.utils import is_string_like

def subgraph(G, nbunch, inplace=False, create_using=None):
    """Return the subgraph induced on nodes in nbunch.

    nbunch: either a singleton node, a string (which is treated
    as a singleton node, or any iterable (non-string) container
    of nodes for which len(nbunch) is defined. For example, a list,
    dict, set, Graph, numeric array, or user-defined iterable object. 

    Setting inplace=True will return induced subgraph in original graph
    by deleting nodes not in nbunch.

    Unless otherwise specified, return a new graph of the same
    type as self.  Use (optional) create_using=R to return the
    resulting subgraph in R. R can be an existing graph-like
    object (to be emptied) or R is a call to a graph object,
    e.g. create_using=DiGraph(). See documentation for
    empty_graph.

    Implemented for Graph, DiGraph, XGraph, XDiGraph

    Note: subgraph(G) calls G.subgraph()

       """
    H=G.subgraph(nbunch, inplace, create_using)
    return H
                                                                                
def union(G,H,create_using=None,rename=False,**kwds):
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
    newname=kwds.get("name", "union( %s, %s )"%(G.name,H.name) )
    if create_using is None:
        R=create_empty_copy(G)
    else:
        R=create_using
        R.clear()
    R.name=newname

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
            raise networkx.NetworkXError,"node sets of G and H are not disjoint. Use appropriate rename=('Gprefix','Hprefix')"
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


def compose(G,H,create_using=None, **kwds):
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
    newname= kwds.get("name", "compose( %s, %s )"%(G.name,H.name) )
    if create_using is None:
        R=create_empty_copy(G)
    else:
        R=create_using
        R.clear()
    R.name=newname
    R.add_nodes_from([v for v in G.nodes() ])
    R.add_edges_from(G.edges())
    R.add_nodes_from([v for v in H.nodes() ])
    R.add_edges_from(H.edges())
    return R


def complement(G,create_using=None, **kwds):
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
    newname=kwds.get("name", "complement(%s)"%(G.name) )
    if create_using is None:
        R=create_empty_copy(G)
    else:
        R=create_using
        R.clear()
    R.name=newname
    R.add_nodes_from([v for v in G.nodes() ])
    for v in G.nodes():
        for u in G.nodes():
            if not G.has_edge(v,u):
                R.add_edge(v,u) 
    return R


def create_empty_copy(G):
    """Return a new, empty graph-like object of the same type/class as G.

    Works for Graph, DiGraph, XGraph, XDiGraph

    """
    H=subgraph(G,[])
    H.name="No Name"
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

def convert_node_labels_to_integers(G,first_label=0,ordering="default",discard_old_labels=True):
    """
    Return a copy of G, with n node labels replaced with integers,
    starting at first_label.

    first_label: (optional, default=1)

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
       labels to old labels, and set self.dna["node_labeled"]=True

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
#    counting labeled vs. unlabeled graphs. When implementing graph
#    algorithms it is often convenient to strip off the original node
#    and edge information and appropriately relabel the n nodes with
#    the integer values 1,..,n. This is the purpose of this function,
#    and it provides the option (see discard_old_labels variable) to either
#    preserve the original labels in separate dicts (these are not
#    returned but inserted into the dna of the new graph, or to discard that
#    information if it is superfluous.


    H=subgraph(G,[]) # create empty copy, works also for XGraph & XDiGraph
    H.name="("+G.name+")_with_int_labels"
    v_to_int_map={}
    v_int=first_label
    nodes=G.nodes_iter()

    if ordering=="default":
        for v in nodes:
            v_to_int_map[v]=v_int
#           print v_int, "-->", v
            H.add_node(v_int)
            v_int+=1
    elif ordering=="sorted":
        for v in sorted(G.nodes()):
            v_to_int_map[v]=v_int
#           print v_int, "-->", v
            H.add_node(v_int)
            v_int+=1
    elif ordering=="increasing degree":
        deg_v_pairs=[]
        # create sequence of degree-node pairs
        for v in nodes:
            deg_v_pairs.append([G.degree(v),v])
        deg_v_pairs.sort() # in-place sort from lowest to highest degree
        for _,v in deg_v_pairs:
            v_to_int_map[v]=v_int
#           print v_int, "-->", v
            H.add_node(v_int)
            v_int+=1
    elif ordering=="decreasing degree":
        deg_v_pairs=[]
        # create sequence of degree-node pairs
        for v in nodes:
            deg_v_pairs.append([G.degree(v),v])
        deg_v_pairs.sort() # in-place sort from lowest to highest degree
        deg_v_pairs.reverse()
        for _,v in deg_v_pairs:
            v_to_int_map[v]=v_int
#           print v_int, "-->", v
            H.add_node(v_int)
            v_int+=1        
    else:
        raise networkx.NetworkXError,"unknown value of node ordering variable: ordering"

    edges=G.edges_iter()
    for e in edges:
        v_int=v_to_int_map[e[0]]
        w_int=v_to_int_map[e[1]]
#       print "edge ",v,"--",w, " mapped to ", v_int,"--",w_int
        if len(e)==2:
            H.add_edge(v_int,w_int)
        else:
            H.add_edge(v_int,w_int,e[2])

    if discard_old_labels:
        H.dna["has_node_labels"]=False
        H.dna["node_labels"]=None
    else:
        H.dna["has_node_labels"]=True
        H.dna["node_labels"]=v_to_int_map                
    return H
    
def relabel_nodes_with_function(G, func):
    """
    Return new graph from input graph G, such that each node name is
    relabeled by the application of the specified function func.
    """
    H=create_empty_copy(G)
    H.name="(%s)" % G.name
    nodes=G.nodes_iter()
    for node in nodes:
        try:
            H.add_node(func(node))
        except:
            raise networkx.NetworkXError,\
                  "relabeling function cannot be applied to node %s" % node
    edges=G.edges_iter()    
    for n1, n2 in edges:
        try:
            H.add_edge(func(n1), func(n2))
        except:
            raise networkx.NetworkXError,\
                  "relabeling function cannot be applied to edge (%s, %s)" % \
                  (n1, n2)
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
    
