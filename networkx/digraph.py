"""
Base classes for graphs and digraphs.

Unless otherwise specified, by graph we mean a simple graph that has
no self-loops or multiple (parallel) edges. (See the module xbase.py
for graph classes XGraph and XDiGraph that allow for self-loops,
mutiple edges and arbitrary objects associated with edges.)

The following classes are provided:

Graph
   The basic operations common to graph-like classes.

DiGraph
   Operations common to digraphs, a graph with directed edges.
   Subclass of Graph.

An empty graph or digraph is created with
 - G=Graph()
 - G=DiGraph()

This module implements graphs using data structures based on an
adjacency list implemented as a node-centric dictionary of
dictionaries. The dictionary contains keys corresponding to the nodes
and the values are dictionaries of neighboring node keys with the
value None (the Python None type).  This allows fast addition,
deletion and lookup of nodes and neighbors in large graphs.  The
underlying datastructure should only be visible in this module. In all
other modules, instances of graph-like objects are manipulated solely
via the methods defined here and not by acting directly on the
datastructure.

The following notation is used throughout NetworkX documentation and
code: (we use mathematical notation n,v,w,... to indicate a node,
v=vertex=node).
 
G,G1,G2,H,etc:
   Graphs

n,n1,n2,u,v,v1,v2:
   nodes (v stands for vertex=node)

nlist,vlist:
   a list of nodes 

nbunch:
   a "bunch" of nodes (vertices).  An nbunch is any iterable container
   of nodes that is not itself a node in the graph. (It can be an
   iterable or an iterator, e.g. a list, set, graph, file, etc..)
   
e=(n1,n2):
   an edge (a python "2-tuple") in the Graph and DiGraph classes,
   also written n1-n2 (if undirected), or n1->n2 (if directed).
   Note that 3-tuple edges of the form (n1,n2,x) are used in the
   XGraph and XDiGraph classes. See xbase.py for details on how
   2-tuple edges, such as (n1,n2), are translated when 3-tuple edges
   are expected. For example, if G is an XGraph, then G.add_edge(n1,n2)
   will add the edge (n1,n2,None), and G.delete_edge(n1,n2) will attempt
   to delete the edge (n1,n2,None). In the case of multiple edges between
   nodes n1 and n2, one can use G.delete_multiedge(n1,n2) to delete all
   edges between n1 and n2.

elist:
   a list of edges (as tuples)

ebunch:
   a bunch of edges (as tuples)
   an ebunch is any iterable (non-string) container
   of edge-tuples. (Similar to nbunch, also see add_edge).

Warning:
  - The ordering of objects within an arbitrary nbunch/ebunch
    can be machine- or implementation-dependent.
  - Algorithms should treat an arbitrary nbunch/ebunch as
    once-through-and-exhausted iterable containers.
  - len(nbunch) and len(ebunch) need not be defined.    


Methods
=======

The Graph class provides rudimentary graph operations:

Mutating Graph methods
----------------------
   
    - G.add_node(n), G.add_nodes_from(nbunch)
    - G.delete_node(n), G.delete_nodes_from(nbunch)
    - G.add_edge(n1,n2), G.add_edge(e), where e=(u,v)
    - G.add_edges_from(ebunch)
    - G.delete_edge(n1,n2), G.delete_edge(e), where e=(u,v)
    - G.delete_edges_from(ebunch)
    - G.add_path(nlist)
    - G.add_cycle(nlist)
    - G.clear()
    - G.subgraph(nbunch,inplace=True)

Non-mutating Graph methods
--------------------------

    - len(G)
    - n in G (equivalent to G.has_node(n))
    - G.has_node(n)
    - G.nodes()
    - G.nodes_iter()
    - G.has_edge(n1,n2)
    - G.edges(), G.edges(n), G.edges(nbunch)      
    - G.edges_iter(), G.edges_iter(n), G.edges_iter(nbunch)
    - G.neighbors(n)
    - G[n]  (equivalent to G.neighbors(n))
    - G.neighbors_iter(n) # iterator over neighbors
    - G.number_of_nodes()
    - G.number_of_edges()
    - G.degree(n), G.degree(nbunch)
    - G.degree_iter(n), G.degree_iter(nbunch)
    - G.is_directed()

Methods returning a new graph
-----------------------------

    - G.subgraph(nbunch)
    - G.subgraph(nbunch,create_using=H)
    - G.copy()
    - G.to_undirected()
    - G.to_directed()
    
Examples
========

Create an empty graph structure (a "null graph") with
zero nodes and zero edges.

>>> from networkx import *
>>> G=Graph()

G can be grown in several ways.
By adding one node at a time:

>>> G.add_node(1)

by adding a list of nodes:

>>> G.add_nodes_from([2,3])

by using an iterator:

>>> G.add_nodes_from(xrange(100,110))

or by adding any nbunch of nodes (see above definition of an nbunch):

>>> H=path_graph(10)
>>> G.add_nodes_from(H)

H can be another graph, or dict, or set, or even a file.
Any hashable object (except None) can represent a node, e.g. a Graph,
a customized node object, etc.

>>> G.add_node(H)

G can also be grown by adding one edge at a time:

>>> G.add_edge( (1,2) )

by adding a list of edges: 

>>> G.add_edges_from([(1,2),(1,3)])

or by adding any ebunch of edges (see above definition of an ebunch):

>>> G.add_edges_from(H.edges())

There are no complaints when adding existing nodes or edges:

>>> G=Graph()
>>> G.add_edge([(1,2),(1,3)])

will add new nodes as required.
    
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
__date__ = "$Date: 2005-06-24 14:16:40 -0600 (Fri, 24 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1061 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

from graph import Graph
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert

class DiGraph(Graph):
    """ A graph with directed edges. Subclass of Graph.

    DiGraph inherits from Graph, overriding the following methods:

    - __init__: replaces self.adj with the dicts self.pred and self.succ
    - __getitem__
    - add_node
    - delete_node
    - add_edge
    - delete_edge
    - add_nodes_from
    - delete_nodes_from
    - add_edges_from
    - delete_edges_from
    - edges_iter
    - degree_iter
    - degree
    - copy
    - clear
    - subgraph
    - is_directed
    - to_directed
    - to_undirected
    
    Digraph adds the following methods to those of Graph:

    - successors
    - successors_iter
    - predecessors
    - predecessors_iter
    - out_degree
    - out_degree_iter
    - in_degree
    - in_degree_iter

    """
# we store two adjacency lists:
#    the  predecessors of node n are stored in the dict self.pred
#    the successors of node n are stored in the dict self.succ=self.adj
    def __init__(self,data=None,name=None,**kwds):

        self.name=''
        # dna is a dictionary attached to each graph and used to store
        # information about the graph structure
        self.dna={}
        self.dna["datastructure"]="vdict_of_dicts"

        self.adj={}  # empty adjacency hash
        self.pred={}        # predecessor
        self.succ=self.adj  # successor

        if data is not None:
            self=convert.from_whatever(data,create_using=self)

        if name is not None:
            self.name=name

    def __getitem__(self,n):
        """Return the in- and out-neighbors of node n as a list.

        This provides digraph G the natural property that G[n] returns
        the neighbors of G. 

        """
        return self.neighbors(n)
        
    def add_node(self, n):
        """Add a single node to the digraph.

        The node n can be any hashable object except None.

        A hashable object is one that can be used as a key in a Python
        dictionary. This includes strings, numbers, tuples of strings
        and numbers, etc.  On many platforms this also includes
        mutables such as Graphs, though one should be careful that the
        hash doesn't change on mutables.

        >>> from networkx import *
        >>> G=DiGraph()
        >>> K3=complete_graph(3)
        >>> G.add_nodes_from(K3)    # add the nodes from K3 to G
        >>> G.nodes()
        [0, 1, 2]
        >>> G.clear()
        >>> G.add_node(K3)          # add the graph K3 as a node in G.
        >>> G.number_of_nodes()
        1

        """
        if n not in self.succ:
            self.succ[n]={}
        if n not in self.pred:
            self.pred[n]={}

    def add_nodes_from(self, nbunch):
        """Add multiple nodes to the digraph.

        nbunch:
        A container of nodes that will be iterated through once
        (thus it should be an iterator or be iterable).
        Each element of the container should be a valid node type:
        any hashable type except None.  See add_node for details.

        """
        for n in nbunch:
            if n not in self.succ:
                self.succ[n]={}
            if n not in self.pred:
                self.pred[n]={}

    def delete_node(self,n):
        """Delete node n from the digraph.  
        Attempting to delete a non-existent node will raise a NetworkXError.
        
        """
        try:
            for u in self.succ[n].keys():  
                del self.pred[u][n] # remove all edges n-u in graph
            del self.succ[n]          # remove node from succ
            for u in self.pred[n].keys():  
                del self.succ[u][n] # remove all edges n-u in graph
            del self.pred[n]          # remove node from pred
        except KeyError: # NetworkXError if n not in self
            raise NetworkXError, "node %s not in graph"%n

    def delete_nodes_from(self,nbunch):
        """Remove nodes in nbunch from the digraph.
        
        nbunch: an iterable or iterator containing valid node names.

        Attempting to delete a non-existent node will raise an exception.
        This could mean some nodes in nbunch were deleted and some valid
        nodes were not!
        
        """
        for n in nbunch: 
            try:
                for u in self.succ[n].keys():  
#                    self.delete_edge(n,u)# remove all edges n-u in graph
                    del self.pred[u][n] # remove all edges n-u in graph
                del self.succ[n]          # now remove node
                for u in self.pred[n].keys():  
#                    self.delete_edge(u,n)# remove all edges u-n in graph
                    del self.succ[u][n] # remove all edges n-u in graph
                del self.pred[n]          # now remove node
            except KeyError: # NetworkXError if n not in self
                raise NetworkXError, "node %s not in graph"%n


    def add_edge(self, u, v=None):  
        """Add a single directed edge (u,v) to the digraph.

        >> G.add_edge(u,v)
        and
        >>> G.add_edge( (u,v) )
        are equivalent forms of adding a single edge between nodes u and v.
        The nodes u and v will be automatically added if not already in
        the graph.  They must be a hashable (except None) Python object.

        For example, the following examples all add the edge (1,2) to
        the digraph G.

        >>> G=DiGraph()
        >>> G.add_edge( 1, 2 )          # explicit two node form
        >>> G.add_edge( (1,2) )         # single edge as tuple of two nodes
        >>> G.add_edges_from( [(1,2)] ) # list of edges form

        """
        if v is None:
            (u,v)=u  # no v given, assume u is an edge tuple
        # add nodes            
        if u not in self.succ:
            self.succ[u]={}
        if u not in self.pred:
            self.pred[u]={}
        if v not in self.succ:
            self.succ[v]={}
        if v not in self.pred:
            self.pred[v]={}

        # don't create self loops, fail silently, nodes are still added
        if u==v: 
            return  
        self.succ[u][v]=None
        self.pred[v][u]=None

    def add_edges_from(self, ebunch):  
        """Add all the edges in ebunch to the graph.

        ebunch: Container of 2-tuples (u,v). The container must be
        iterable or an iterator.  It is iterated over once. Adding the
        same edge twice has no effect and does not raise an exception.

        See add_edge for an example.

        """
        for e in ebunch:
            (u,v)=e
            # add nodes
            if u not in self.succ:
                self.succ[u]={}
            if u not in self.pred:
                self.pred[u]={}
            if v not in self.succ:
                self.succ[v]={}
            if v not in self.pred:
                self.pred[v]={}

            # don't create self loops, fail silently, nodes are still added
            if u==v:
                continue
            self.succ[u][v]=None
            self.pred[v][u]=None


    def delete_edge(self, u, v=None): 
        """Delete the single directed edge (u,v) from the digraph.

        Can be used in two basic forms 
        >>> G.delete_edge(u,v)
        and
        G.delete_edge( (u,v) )
        are equivalent ways of deleting a directed edge u->v.

        If the edge does not exist return without complaining.

        """
        if v is None:
            (u,v)=u
        if u in self.pred[v] and v in self.succ[u]:
            del self.succ[u][v]   
            del self.pred[v][u]               

    def delete_edges_from(self, ebunch): 
        """Delete the directed edges in ebunch from the digraph.

        ebunch: Container of 2-tuples (u,v). The container must be
        iterable or an iterator.  It is iterated over once.

        Edges that are not in the digraph are ignored.
        
        """
        for (u,v) in ebunch:
            if u in self.pred[v] and v in self.succ[u]:
                del self.succ[u][v]   
                del self.pred[v][u]        

    def out_edges_iter(self, nbunch=None):
        """Return iterator that iterates once over each edge pointing out
        of nodes in nbunch, or over all edges in digraph if no
        nodes are specified.

        See add_node for definition of nbunch.
        
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        
        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        for n in bunch:
            for u in self.succ[n]:
                yield (n,u)

    def in_edges_iter(self, nbunch=None):
        """Return iterator that iterates once over each edge adjacent
        to nodes in nbunch, or over all edges in digraph if no
        nodes are specified.

        See add_node for definition of nbunch.
        
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        
        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        for n in bunch:
            for u in self.pred[n]:
                yield (u,n)


    # define edges to be out_edges implicitly since edges uses edges_iter
    edges_iter=out_edges_iter
            
    def out_edges(self, nbunch=None):
        """Return list of all edges that point out of nodes in nbunch,
        or a list of all edges in graph if no nodes are specified.

        See add_node for definition of nbunch.

        Those nodes in nbunch that are not in the graph will be
        (quietly) ignored.
        
        """
        return list(self.out_edges_iter(nbunch))

    def in_edges(self, nbunch=None):
        """Return list of all edges that point in to nodes in nbunch,
        or a list of all edges in graph if no nodes are specified.

        See add_node for definition of nbunch.

        Those nodes in nbunch that are not in the graph will be
        (quietly) ignored.
        
        """
        return list(self.in_edges_iter(nbunch))


    def successors_iter(self,v):
         """Return an iterator for successor nodes of v."""
         try:
             return self.succ[v].iterkeys()
         except KeyError:
             raise NetworkXError, "node %s not in graph"%v


    def predecessors_iter(self,v):
        """Return an iterator for predecessor nodes of v."""
        try:
            return self.pred[v].iterkeys()
        except KeyError:
            raise NetworkXError, "node %s not in graph"%v


    def successors(self, v):
        """Return sucessor nodes of v."""
        return list(self.successors_iter(v))


    def predecessors(self, v):
        """Return predecessor nodes of v."""
        return list(self.predecessors_iter(v))

    # digraph definintions 
    out_neighbors=successors
    in_neighbors=predecessors
    neighbors=successors
    neighbors_iter=successors_iter

    def degree_iter(self,nbunch=None,with_labels=False):
        """Return iterator that returns in_degree(n)+out_degree(n)
        or (n,in_degree(n)+out_degree(n)) for all n in nbunch. 
        If nbunch is ommitted, then iterate over *all* nodes.
 
        Can be called in three ways:
        G.degree_iter(n):       return iterator the degree of node n
        G.degree_iter(nbunch):  return a list of values,
        one for each n in nbunch (nbunch is any iterable container of nodes.)
        G.degree_iter():        same as nbunch = all nodes in graph.
 
        If with_labels=True, iterator will return an
        (n,in_degree(n)+out_degree(n)) tuple of node and degree.
 
        Any nodes in nbunch but not in the graph will be (quietly) ignored.
 
        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        if with_labels:   # yield tuple (n,degree)
            for n in bunch:
                yield (n,len(self.succ[n])+len(self.pred[n])) 
        else:
            for n in bunch:
                yield len(self.succ[n])+len(self.pred[n]) 

    def in_degree_iter(self,nbunch=None,with_labels=False):
        """Return iterator for in_degree(n) or (n,in_degree(n))
        for all n in nbunch.

        If nbunch is ommitted, then iterate over *all* nodes.
 
        See degree_iter method for Digraph Class for more details. 
        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        if with_labels:   # yield tuple (n,degree)
            for n in bunch:
                yield (n,len(self.pred[n])) 
        else:
            for n in bunch:
                yield len(self.pred[n]) 

    def out_degree_iter(self,nbunch=None,with_labels=False):
        """Return iterator for out_degree(n) or (n,out_degree(n))
        for all n in nbunch.

        If nbunch is ommitted, then iterate over *all* nodes.
 
        See degree_iter method for Digraph Class for more details. 
        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        if with_labels:   # yield tuple (n,degree)
            for n in bunch:
                yield (n,len(self.succ[n]))
        else:
            for n in bunch:
                yield len(self.succ[n])

    def out_degree(self, nbunch=None, with_labels=False):
        """Return out-degree of single node or of nbunch of nodes.

        If nbunch is omitted or nbunch=None, then return
        out-degrees of *all* nodes.
        
        """
        if with_labels:           # return a dict
            return dict(self.out_degree_iter(nbunch,with_labels))
        elif nbunch in self:      # return a single node
            return self.out_degree_iter(nbunch,with_labels).next()
        else:                     # return a list
            return list(self.out_degree_iter(nbunch,with_labels))
        
    def in_degree(self, nbunch=None, with_labels=False):
        """Return in-degree of single node or of nbunch of nodes.

        If nbunch is omitted or nbunch=None, then return
        in-degrees of *all* nodes.

        """
        if with_labels:           # return a dict
            return dict(self.in_degree_iter(nbunch,with_labels))
        elif nbunch in self:      # return a single node
            return self.in_degree_iter(nbunch,with_labels).next()
        else:                     # return a list
            return list(self.in_degree_iter(nbunch,with_labels))

    def clear(self):
        """Remove name and delete all nodes and edges from digraph."""
        self.name=None
        self.succ.clear() # WARNING: the dna is not scrubbed to
        self.pred.clear() # recover its state at time of object creation

    def copy(self):
        """Return a (shallow) copy of the digraph.

        Identical to dict.copy() of adjacency dicts pred and succ,
        with name and dna copied as well.
        
        """
        H=self.__class__()
        H.name=self.name
        H.dna=self.dna.copy()
        H.adj=self.adj.copy()
        H.succ=H.adj  # fix pointer again
        for v in H.adj:
            H.pred[v]=self.pred[v].copy()
            H.succ[v]=self.succ[v].copy()
        return H


    def subgraph(self, nbunch, inplace=False, create_using=None):
        """
        Return the subgraph induced on nodes in nbunch.

        nbunch: can be a singleton node, a string (which is treated
        as a singleton node), or any iterable container of
        of nodes. (It can be an iterable or an iterator, e.g. a list,
        set, graph, file, etc.)

        Setting inplace=True will return the induced subgraph in original graph
        by deleting nodes not in nbunch. This overrides create_using.
        Warning: this can destroy the graph.

        Unless otherwise specified, return a new graph of the same
        type as self.  Use (optional) create_using=R to return the
        resulting subgraph in R. R can be an existing graph-like
        object (to be emptied) or R can be a call to a graph object,
        e.g. create_using=DiGraph(). See documentation for empty_graph()
        
        Note: use subgraph(G) rather than G.subgraph() to access the more
        general subgraph() function from the operators module.

        """
        bunch=self.prepare_nbunch(nbunch)

        if inplace: # demolish all nodes (and attached edges) not in nbunch
                    # override any setting of create_using
            bunch=dict.fromkeys(bunch) # make a dict
            self.delete_nodes_from([n for n in self if n not in bunch])
            self.name="Subgraph of (%s)"%(self.name)
            return self

        # create new graph        
        if create_using is None:  # Graph object of the same type as current graph
            H=self.__class__()
        else:                     # user specified graph
            H=create_using
            H.clear()
        H.name="Subgraph of (%s)"%(self.name)
        H.add_nodes_from(bunch)

        # add edges
        H_succ=H.succ       # cache
        H_pred=H.pred       
        self_succ=self.succ 
        self_pred=self.pred 
        dict_fromkeys=dict.fromkeys
        for n in H:
            H_succ[n]=dict_fromkeys([u for u in self_succ[n] if u in H_succ], None)
            H_pred[n]=dict_fromkeys([u for u in self_pred[n] if u in H_succ], None)
        return H

    def is_directed(self):
        """ Return True if a directed graph."""
        return True

    def to_undirected(self):
        """Return the undirected representation of the digraph.

        A new graph is returned (the underlying graph). The edge u-v
        is in the underlying graph if either u->v or v->u is in the
        digraph.
        
        """
        H=Graph()
        H.name=self.name
        H.dna=self.dna.copy()
        H.adj=self.succ.copy()  # copy nodes
        for u in H.adj:
            H.adj[u]=self.succ[u].copy()  # copy successors
            for v in self.pred[u]:        # now add predecessors to adj too
                H.adj[u][v]=None
        return H

    def to_directed(self):
        """Return a directed representation of the digraph.

        This is already directed, so merely return a copy.

        """
        return self.copy()
        
    def reverse(self):
        """
        Return a new digraph with the same vertices and edges
        as G but with the directions of the edges reversed.
        """
        H=self.__class__() # new empty DiGraph

        H.name="Reverse of (%s)"%(self.name)
        # H.dna=self.dna.copy()  # do not copy dna to reverse

        H.add_nodes_from(self)
        H.add_edges_from([(v,u) for (u,v) in self.edges_iter()])
        return H

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/digraph_DiGraph.txt',
                                 package='networkx')
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
    
