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
   a "bunch" of nodes (vertices).  an nbunch is any iterable container
   of nodes that is not itself a node in the graph. (It can be an
   iterable or an iterator, e.g. a list, set, graph, file, etc..)
   
e=(n1,n2):
   an edge (a python "2-tuple"), also written u-v. In Xgraph
   G.add_edge(n1,n2) is equivalent to add_edge(n1,n2,1). However,
   G.delete_edge(n1,n2) will delete all edges between n1 and n2.

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
>>> G.add_nodes_from( H )

(H can be another graph, or dict, or set, or even a file.)

>>> G.add_node( H )

(Any hashable object can represent a node, e.g. a Graph,
a customized node object, etc.)

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

# Exception handling

# the root of all Exceptions
class NetworkXException(Exception):
    """Base class for exceptions in NetworkX."""

class NetworkXError(NetworkXException):
    """Exception for a serious error in NetworkX"""

# functional style helpers

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

def degree(G,nbunch=None):
    """Return degree of single node or of nbunch of nodes.
    If nbunch is ommitted, then return degrees of *all* nodes.
    """
    return G.degree(nbunch)

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


class Graph(object):
    """Graph is a simple graph without any multiple (parallel) edges
    or self-loops.  Attempting to add either will not change
    the graph and will not report an error.
    
    """
    def __init__(self, **kwds):
        """Initialize Graph.

        G=Graph(name="empty") creates empty graph G with G.name="empty"

        """
        self.name=kwds.get("name","No Name")
        # dna is a dictionary attached to each graph and used to store
        # information about the graph structure
        self.dna={}
        self.dna["datastructure"]="vdict_of_dicts"

        self.adj={}  # empty adjacency hash
            
    def __str__(self):
        return self.name

    def __iter__(self):
        """Return an iterator over the nodes in G.

        This is the iterator for the underlying adjacency dict.
        (Allows the expression 'for n in G')
        """
        return self.adj.iterkeys()

    def __contains__(self,n):
        """Return True if n is a node in graph.

        Allows the expression 'n in G'.

        Testing whether an unhashable object, such as a list, is in the
        dict datastructure (self.adj) will raise a TypeError.
        Rather than propagate this to the calling method, just
        return False.

        """
        try:
            return self.adj.__contains__(n)
        except TypeError:
            return False
        
    def __len__(self):
        """Return the number of nodes in graph."""
        return len(self.adj)

    def __getitem__(self,n):
        """Return the neighbors of node n as a list.

        This provides graph G the natural property that G[n] returns
        the neighbors of G. 

        """
        try:
            return self.adj[n].keys()
        except (KeyError, TypeError):
            raise NetworkXError, "node %s not in graph"%n

    
    def print_dna(self):
        """Print graph "DNA": a dictionary of graph names and properties.
        
        In this version the dna is provided as a user-defined variable
        and should not be relied on.
        """
        for key in self.dna:
            print "%-15s: %s"%(key,self.dna[key])



    def info(self, n=None):
        """Print short info for graph G or node n."""
        import textwrap
        width_left = 18

        if n is None:
            print ("Name:").ljust(width_left), self.name
            type_name = [type(self).__name__]
            try:
                if self.selfloops:
                    type_name.append("self-loops") 
            except:
                pass
            try:
                if self.multiedges:
                    type_name.append("multi-edges") 
            except:
                pass
                        
            print ("Type:").ljust(width_left), ",".join(type_name)
            print ("Number of nodes:").ljust(width_left), self.number_of_nodes()
            print ("Number of edges:").ljust(width_left), self.number_of_edges()
            if self.order() > 0:
                print ("Average Degree:").ljust(width_left), \
                      round( self.size()/float(self.order()) ,4)
        else:
            try:
                list_neighbors = self.neighbors(n)
                print "\nNode", n, "has the following properties:"
                print ("Degree:").ljust(width_left), self.degree(n)
                str_neighbors = str(list_neighbors)
                str_neighbors = str_neighbors[1:len(str_neighbors)-1]
                wrapped_neighbors = textwrap.wrap(str_neighbors, 50)
                num_line = 0
                for i in wrapped_neighbors:
                    if num_line == 0:
                        print ("Neighbors:").ljust(width_left), i
                    else:
                        print "".ljust(width_left), i
                    num_line += 1
            except:
                print "Node", n, "is not the graph"

    def add_node(self, n):
        """
        Add a single node n to the graph.

        The node n can be any hashable object
        (it is used as a key in a dictionary).
        On many platforms this includes mutables such as Graphs e.g.,
        though one should be careful the hash doesn't change on mutables.

        Example:

        >>> from networkx import *
        >>> G=Graph()
        >>> K3=complete_graph(3)
        >>> G.add_node(1)
        >>> G.add_node('Hello')
        >>> G.add_node(K3)
        >>> G.number_of_nodes()
        3

        """
        if n not in self.adj:
            self.adj[n]={}


    def add_nodes_from(self, nbunch):
        """Add multiple nodes to the graph.

        nbunch:
        A container of nodes that will be iterated through once
        (thus it should be an iterator or be iterable)
        Each element of the container should be hashable.

        Examples:
        
        >>> from networkx import *
        >>> G=Graph()
        >>> K3=complete_graph(3)
        >>> G.add_nodes_from('Hello')
        >>> G.add_nodes_from(K3)
        >>> sorted(G.nodes())
        [0, 1, 2, 'H', 'e', 'l', 'o']

        """
        for n in nbunch:
            if n not in self.adj:
                self.adj[n]={}


    def delete_node(self,n):
        """Delete node n from graph.  
        Attempting to delete a non-existent node will raise an exception.

        """
        try:
            for u in self.adj[n].keys():  
                del self.adj[u][n]  # (faster) remove all edges n-u in graph
#                self.delete_edge(n,u)# remove all edges n-u in graph
            del self.adj[n]          # now remove node
        except KeyError: # NetworkXError if n not in self
            raise NetworkXError, "node %s not in graph"%n

    def delete_nodes_from(self,nbunch):
        """Remove nodes in nbunch from graph.

        nbunch:
        an iterable or iterator containing valid (hashable) node names.

        Attempting to delete a non-existent node will raise an exception.
        This could mean some nodes got deleted and other valid nodes did
        not.

        """
        for n in nbunch: 
             try:
                for u in self.adj[n].keys():  
                    del self.adj[u][n]  # (faster) remove all edges n-u in graph
#                    self.delete_edge(n,u)# remove all edges n-u in graph
                del self.adj[n]          # now remove node
             except KeyError: # NetworkXError if n not in self
                 raise NetworkXError, "node %s not in graph"%n


    def nodes_iter(self):
        """Return an iterator over the graph nodes."""
        return self.adj.iterkeys()

    def nodes(self):
        """Return a copy of the graph nodes in a list."""
        return self.adj.keys()

    def number_of_nodes(self):
        """Return number of nodes."""
        return len(self.adj)

    def has_node(self,n):
        """Return True if graph has node n.

        (duplicates self.__contains__)
        "n in G" is a more readable version of "G.has_node(n)"?
        
        """
        try:
            return self.adj.__contains__(n)
        except TypeError:
            return False

    def order(self):
        """Return the order of a graph = number of nodes."""
        return len(self.adj)


    def add_edge(self, u, v=None):  
        """Add a single edge (u,v) to the graph.

        Can be used in two basic forms:
        G.add_edge(u,v) or G.add_edge( (u,v) ) are equivalent
        forms of adding a single edge between nodes u and
        v. Nodes are nor required to exist before adding an
        edge; they will be added in silence.

        The following examples all add the edge (1,2) to graph G.

        >>> G=Graph()
        >>> G.add_edge( 1, 2 )          # explicit two node form
        >>> G.add_edge( (1,2) )         # single edge as tuple of two nodes
        >>> G.add_edges_from( [(1,2)] ) # add edges from iterable container

        """
        if v is None:
            (u,v)=u  # no v given, assume u is an edge tuple
        # add nodes            
        if u not in self.adj:
            self.adj[u]={}
        if v not in self.adj:
            self.adj[v]={}
        # don't create self loops, fail silently, nodes are still added
        if u==v: 
            return  
        self.adj[u][v]=None
        self.adj[v][u]=None

    def add_edges_from(self, ebunch):  
        """Add all the edges in ebunch to the graph.

        ebunch: Container of 2-tuples (u,v). The container must be
        iterable or an iterator.  It is iterated over once. Adding the
        same edge twice has no effect and does not raise an exception.

        """
        for e in ebunch:
            (u,v)=e
            # add nodes
            if u not in self.adj:
                self.adj[u]={}
            if v not in self.adj:
                self.adj[v]={}
            # don't create self loops, fail silently, nodes are still added
            if u==v:
                continue  
            self.adj[u][v]=None
            self.adj[v][u]=None # add both u-v and v-u


    def delete_edge(self, u, v=None): 
        """Delete the single edge (u,v).

        Can be used in two basic forms: Both
        G.delete_edge(u,v)
        and
        G.delete_edge( (u,v) )
        are equivalent forms of deleting a single edge between nodes u and v.

        Return without complaining if the nodes or the edge do not exist.

        """
        if v is None:
            (u,v)=u
        if self.adj.has_key(u) and self.adj[u].has_key(v):
            del self.adj[u][v]   
            del self.adj[v][u]   

    def delete_edges_from(self, ebunch): 
        """Delete the edges in ebunch from the graph.

        ebunch: an iterator or iterable of 2-tuples (u,v).

        Edges that are not in the graph are ignored.

        """
        for (u,v) in ebunch:
            if self.adj.has_key(u) and self.adj[u].has_key(v):
                del self.adj[u][v]   
                del self.adj[v][u]   

    def has_edge(self, u, v=None):
        """Return True if graph contains the edge u-v. """
        if  v is None:
            (u,v)=u    # split tuple in first position
        return self.adj.has_key(u) and self.adj[u].has_key(v)

    def has_neighbor(self, u, v=None):
        """Return True if node u has neighbor v.

        This is equivalent to has_edge(u,v).

        """
        return self.has_edge(u,v)


    def neighbors_iter(self,n):
         """Return an iterator over all neighbors of node n.  """
         try:
             return self.adj[n].iterkeys()
         except KeyError:
             raise NetworkXError, "node %s not in graph"%n

    def neighbors(self, n):
        """Return a list of nodes connected to node n.  """
        # return lists now, was dictionary for with_labels=True
        return list(self.neighbors_iter(n))

    def edges_iter(self, nbunch=None):
        """Return iterator that iterates once over each edge adjacent
        to nodes in nbunch, or over all edges in graph if no
        nodes are specified.

        See add_node for definition of nbunch.
        
        Those nodes in nbunch that are not in the graph will be
        (quietly) ignored.
        
        """
        # prepare nbunch
        if nbunch is None: # include all nodes via iterator
            nbunch=self.nodes_iter()
        e={}     # helper dict to keep track of multiply stored edges
        # if nbunch is a single node 
        if nbunch in self:
            n1=nbunch
            for n2 in self.adj[n1]:
                if not e.has_key((n1,n2)):
                    e[(n2,n1)]=None
                    yield (n1,n2)
        else: # treat nbunch as a container of nodes
            try:
                for n1 in nbunch:
                    if n1 in self.adj: 
                        for n2 in self.adj[n1]:
                            if not e.has_key((n1,n2)):
                                e.setdefault((n2,n1),1)
                                yield (n1,n2)
            except TypeError:
                pass
        del(e) # clear copy of temp dictionary
               # iterators can remain after they finish returning values.


    def edges(self, nbunch=None):
        """Return list of all edges that are adjacent to a node in nbunch,
        or a list of all edges in graph if no nodes are specified.

        See add_node for definition of nbunch.

        Those nodes in nbunch that are not in the graph will be
        (quietly) ignored.
        
        For digraphs, edges=out_edges

        """
        return list(self.edges_iter(nbunch))

    def edge_boundary(self, nbunch1, nbunch2=None):
        """Return list of edges (n1,n2) with n1 in nbunch1 and n2 in
        nbunch2.  If nbunch2 is omitted or nbunch2=None, then nbunch2
        is all nodes not in nbunch1.

        Nodes in nbunch1 and nbunch2 that are not in the graph are
        ignored.

        nbunch1 and nbunch2 must be disjoint, else raise an exception.

        """
        bdy=[]
        # listify to avoid exhausting a once-through iterable container
        # nlist1 and nlist2 contains only nodes that are in the graph
        nlist1=[n for n in nbunch1 if n in self]
        len1=len(nlist1)

        if nbunch2 is None: # use nbunch2 = complement of nbunch1
            nlist2=[n for n in self if n not in nlist1]
            len2=len(nlist2) # size of node complement
        else:
            nlist2=[n for n in nbunch2 if n in self]
            len2=len(nlist2)
            # check for non-empty intersection:
            # nbunch1, nbunch2 and self.nodes() should have no nodes
            # in common
            # use shortest outer loop
            if len1 <= len2:
                for n in nlist1:
                    if n in nlist2:
                        raise NetworkXError,\
                        "nbunch1 and nbunch2 are not disjoint"
            else:
                for n in nlist2:
                    if n in nlist1:
                        raise NetworkXError, \
                        "nbunch1 and nbunch2 are not disjoint"
        if len1 <= len2:
            for n1 in nlist1:
                for n2 in self.adj[n1]:
                    if n2 in nlist2:
                        bdy.append((n1,n2))
        elif len2 <= len1:
            for n2 in nlist2:
                for n1 in self.adj[n2]:
                    if n1 in nlist1:
                        bdy.append((n1,n2))
        return bdy

    def node_boundary(self, nbunch1, nbunch2=None):
        """Return list of all nodes on external boundary of nbunch1 that are
        in nbunch2.  If nbunch2 is omitted or nbunch2=None, then nbunch2
        is all nodes not in nbunch1.

        Note that by definition the node_boundary is external to nbunch1.
        
        Nodes in nbunch1 and nbunch2 that are not in the graph are
        ignored.

        nbunch1 and nbunch2 must be disjoint (when restricted to the
        graph), else a NetworkXError is raised.

        """
        bdy=[]
        # listify to avoid exhausting a once-through iterable container
        # nlist1 and nlist2 contains only nodes that are in the graph
        nlist1=[n for n in nbunch1 if n in self]
        len1=len(nlist1)

        if nbunch2 is None: # use nbunch2 = complement of nbunch1
            nlist2=[n for n in self if n not in nlist1]
            len2=len(nlist2) # size of node complement
        else:
            nlist2=[n for n in nbunch2 if n in self]
            len2=len(nlist2)
            # check for non-empty intersection:
            # nbunch1, nbunch2 and self.nodes() should have no nodes
            # in common
            # use shortest outer loop
            if len1 <= len2:
                for n in nlist1:
                    if n in nlist2:
                        raise NetworkXError,\
                        "nbunch1 and nbunch2 are not disjoint"
            else:
                for n in nlist2:
                    if n in nlist1:
                        raise NetworkXError,\
                        "nbunch1 and nbunch2 are not disjoint"
        # use shortest outer loop
        if len1 <= len2:
            # find external boundary of nlist1
            for n1 in nlist1:
                for n2 in self.adj[n1]:
                    if (not n2 in bdy) and (n2 in nlist2):
                            bdy.append(n2)
        else:
            # find internal boundary of nlist2
            for n2 in nlist2:
                if not n2 in bdy:
                    for n in self.adj[n2]:
                        if n in nlist1:
                            bdy.append(n2)
                            break        
        return bdy

    def degree(self,nbunch=None,with_labels=False):
        """Return degree of single node or of nbunch of nodes.
        If nbunch is omitted or nbunch=None, then return
        degrees of *all* nodes.

        The degree of a node is the number of edges attached to that
        node.

        Can be called in three ways:

        G.degree(n):       return the degree of node n
        G.degree(nbunch):  return a list of values, one for each n in nbunch
        (nbunch is any iterable container of nodes.)
        G.degree():        same as nbunch = all nodes in graph.
        
        If with_labels==True, then return a dict that maps each n
        in nbunch to degree(n).

        Any nodes in nbunch that are not in the graph are
        (quietly) ignored.
        
        """
        # prepare nbunch
        if nbunch is None: # include all nodes via iterator
            nbunch=self.adj.iterkeys()
        # if nbunch is a single node, return value
        if nbunch in self:
            n=nbunch
            if with_labels:
                return {n:len(self.adj[n])} # useless but self-consistent?
            else:
                return len(self.adj[n])
        else: # do bunch of nodes
            d={}
            for n in nbunch:
                if n in self:
                    d.setdefault(n,len(self.adj[n]))
            if with_labels:
                return d
            else:
                return d.values()

    def degree_iter(self,nbunch=None,with_labels=False):
        """Return iterator that return degree(n) or (n,degree(n))
        for all n in nbunch. If nbunch is ommitted, then iterate
        over all nodes.

        Can be called in three ways:
        G.degree_iter(n):       return iterator the degree of node n
        G.degree_iter(nbunch):  return a list of values,
        one for each n in nbunch (nbunch is any iterable container of nodes.)
        G.degree_iter():        same as nbunch = all nodes in graph.
        
        If with_labels==True, iterator will return an (n,degree(n)) tuple of
        node and degree.

        Those nodes in nbunch that are not in the graph will be
        (quietly) ignored.

        """
        # prepare nbunch
        if nbunch is None: # iterate over entire graph
            nbunch=self.adj.iterkeys()

        # if nbunch is a single node in the graph
        if nbunch in self:
            n=nbunch
            if with_labels:
                yield (n,len(self.adj[n])) # useless but self-consistent?
            else:
                yield len(self.adj[n])
        else: # do bunch of nodes
            if with_labels:
                for n in nbunch:
                    if n in self:
                        yield (n,len(self.adj[n])) # tuple (n,degree)
            else:
                for n in nbunch:
                    if n in self:
                        yield len(self.adj[n])     # just degree
                        
    def clear(self):
        """Remove name and delete all nodes and edges from graph."""
        self.name=""
        self.adj.clear() # WARNING: the dna is not scrubbed to
                       # recover its state at time of object creation

    def copy(self):
        """Return a (shallow) copy of the graph.

        Identical to dict.copy() of adjacency dict adj, with name and
        dna copied as well.
        
        """
        H=self.__class__()
        H.name=self.name
        H.dna=self.dna.copy()
        H.adj=self.adj.copy()
        for v in H.adj:
            H.adj[v]=self.adj[v].copy()
        return H

    def to_undirected(self):
        """Return the undirected representation of the graph G.

        This graph is undirected, so merely return a copy.

        """
        return self.copy()

        
    def to_directed(self):
        """Return a directed representation of the graph G.

        A new digraph is returned with the same name, same nodes and
        with each edge u-v represented by two directed edges
        u->v and v->u.
        
        """
        H=DiGraph()
        H.name=self.name
        H.dna=self.dna.copy()
        H.adj=self.adj.copy() # copy nodes
        H.succ=H.adj  # fix pointer again
        for v in H.adj:
            H.pred[v]=self.adj[v].copy()  # copy adj list to predecessor
            H.succ[v]=self.adj[v].copy()  # copy adj list to successor
        return H


    def subgraph(self, nbunch, inplace=False, create_using=None):
        """
        Return the subgraph induced on nodes in nbunch.

        nbunch: either a singleton node, a string (which is treated
        as a singleton node), or any iterable (non-string) container
        of nodes for which len(nbunch) is defined. For example, a list,
        dict, set, Graph, numeric array, or user-defined iterable object. 

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
        # if nbunch is a single node in the graph then convert into a list
        # instead of iterating over it, this allows nodes to be iterable
        if nbunch in self: nbunch=[nbunch]

        if inplace: # demolish all nodes (and attached edges) not in nbunch
                    # override any setting of create_using
            if hasattr(nbunch,"next"): # if we are an simple iterator
                nbunch=dict.fromkeys(nbunch) # make a dict
            self.delete_nodes_from([n for n in self if not n in nbunch])
            self.name="Subgraph of (%s)"%(self.name)
            return self

        else:  # create new graph        
            if create_using is not None:  # user specified graph
                H=create_using
                H.clear()
            else:           # Graph object of the same type as current graph
                H=self.__class__()

            H.name="Subgraph of (%s)"%(self.name)
            # H.dna=self.dna.copy()  # do not copy dna to a subgraph

            H.add_nodes_from([n for n in nbunch if n in self])
            # add edges
            for n in H:
                gn=self.adj[n]    # store in local variables for speed
                hn=H.adj[n]
                for u in H:
                    if u in gn:
                        hn[u]=None
        return H




# End of basic operations (under the hood and close to the datastructure)
# The following remaining Graph methods use the above methods and not the
# datastructure directly

    def add_path(self, nlist):
        """Add the path through the nodes in nlist to graph"""
        fromv = nlist.pop(0)
        while len(nlist) > 0:
            tov=nlist.pop(0)
            self.add_edge(fromv,tov)
            fromv=tov

    def add_cycle(self, nlist):
        """Add the cycle of nodes in nlist to graph"""
        self.add_path(nlist+[nlist[0]])  # wrap first element

    def is_directed(self):
        """ Return True if graph is directed."""
        return False

    def size(self):
        """Return the size of a graph = number of edges. """
        return sum(self.degree())/2

    def number_of_edges(self):
        """Return the size of a graph = number of edges. """
        return sum(self.degree())/2
    
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
    def __init__(self,**kwds):
        super(DiGraph,self).__init__(**kwds)
        self.pred={}        # predecessor
        self.succ=self.adj  # successor

    def __getitem__(self,n):
        """Return the in- and out-neighbors of node n as a list.

        This provides digraph G the natural property that G[n] returns
        the neighbors of G. 

        """
        return self.neighbors(n)
        
    def add_node(self, n):
        """Add a single node to the digraph.

        n can be any hashable object (it is used as a key in a
        dictionary).  On many platforms this includes mutables
        such as Graphs e.g., though one should be careful the hash
        doesn't change during the lifetime of the graph.

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
        A container of nodes that will be iterated through
        once (thus it can be an iterator or an iterable).  A node can
        be any hashable object (it is used as a key in a dictionary

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
        
        nbunch: an iterable or iterator containing valid (hashable)
        node names.

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

        Can be used in two basic forms:
        G.add_edge(u,v) or G.add_edge( (u,v) ) are equivalent
        forms of adding a single edge between nodes u and
        v. Nodes are nor required to exist before adding an
        edge; they will be added in silence.

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

        Can be used in two basic forms. Both 
        G.delete_edge(u,v), or
        G.delete_edge( (u,v) )

        are equivalent forms of deleting a directed edge u->v.

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
        
        Those nodes in nbunch that are not in the graph will be
        (quietly) ignored.
        
        """
        # prepare nbunch
        if nbunch is None: # include all nodes via iterator
            nbunch=self.nodes_iter()
        if nbunch in self:
            v=nbunch
            for u in self.succ[v]:
                yield (v,u)
        else: # treat nbunch as a container of nodes
            try:
                for v in nbunch:
                    if v in self.succ:
                        for u in self.succ[v]:
                            yield (v,u)
            except TypeError:
                pass

    def in_edges_iter(self, nbunch=None):
        """Return iterator that iterates once over each edge adjacent
        to nodes in nbunch, or over all edges in digraph if no
        nodes are specified.

        See add_node for definition of nbunch.
        
        Those nodes in nbunch that are not in the graph will be
        (quietly) ignored.
        
        """
        # prepare nbunch
        if nbunch is None: # include all nodes via iterator
            nbunch=self.nodes_iter()
        if nbunch in self:
            v=nbunch
            for u in self.pred[v]:
                yield (u,v)
        else: # treat nbunch as a container of nodes
            try:
                for v in nbunch:
                    if v in self.pred:
                        for u in self.pred[v]:
                            yield (u,v)
            except TypeError:
                pass


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
        """Return iterator that return degree(n) or (n,degree(n))
        for all n in nbunch. If nbunch is ommitted, then iterate
        over *all* nodes.
 
        nbunch: a singleton node, a string (which is treated
                as a singleton node), or any iterable (non-string)
                container of nodes for which len(nbunch) is
                defined. For example, a list, dict, set, Graph,
                numeric array, or user-defined iterable object.
 
        If with_labels=True, iterator will return an (n,degree(n)) tuple of
        node and degree.
 
        Any nodes in nbunch but not in the graph will be (quietly) ignored.
 
        """
        # prepare nbunch
        if nbunch is None: # iterate over entire graph
            nbunch=self.nodes_iter()
            
        # if nbunch is a single node in the graph
        if nbunch in self:
            n=nbunch
            deg=len(self.succ[n])+len(self.pred[n])
            if with_labels:
                yield (n,deg) # useless but self-consistent?
            else:
                yield deg
        else:
            if with_labels:   # yield tuple (n,degree)
                for n in nbunch:
                    if n in self:
                        yield (n,len(self.succ[n])+len(self.pred[n])) 
            else:
                for n in nbunch:
                    if n in self:
                        yield len(self.succ[n])+len(self.pred[n]) 


    def in_degree_iter(self,nbunch=None,with_labels=False):
        """Return iterator for in_degree(n) or (n,in_degree(n))
        for all n in nbunch.

        If nbunch is ommitted, then iterate over *all* nodes.
 
        See degree_iter method for Digraph Class for more details. 
        """
        # prepare nbunch
        if nbunch is None: # iterate over entire graph
            nbunch=self.nodes_iter()
            
        # if nbunch is a single node in the graph
        if nbunch in self:
            n=nbunch
            deg=len(self.pred[n])
            if with_labels:
                yield (n,deg) # useless but self-consistent?
            else:
                yield deg
        else:
            if with_labels:   # yield tuple (n,degree)
                for n in nbunch:
                    if n in self:
                        yield (n,len(self.pred[n])) 
            else:
                for n in nbunch:
                    if n in self:
                        yield len(self.pred[n]) 

    def out_degree_iter(self,nbunch=None,with_labels=False):
        """Return iterator for out_degree(n) or (n,out_degree(n))
        for all n in nbunch.

        If nbunch is ommitted, then iterate over *all* nodes.
 
        See degree_iter method for Digraph Class for more details. 
        """
        # prepare nbunch
        if nbunch is None: # iterate over entire graph
            nbunch=self.nodes_iter()
            
        # if nbunch is a single node in the graph
        if nbunch in self:
            n=nbunch
            deg=len(self.succ[n])
            if with_labels:
                yield (n,deg) # useless but self-consistent?
            else:
                yield deg
        else:
            if with_labels:   # yield tuple (n,degree)
                for n in nbunch:
                    if n in self:
                        yield (n,len(self.succ[n]))
            else:
                for n in nbunch:
                    if n in self:
                        yield len(self.succ[n])


    def degree(self,nbunch=None,with_labels=False):
        """Return degree of single node or of nbunch of nodes.

        If nbunch is omitted or nbunch=None, then return
        degrees of *all* nodes.

        If nbunch is a single node n, return degree of n.
        If nbunch is an iterable (non-string) container
        of nodes, return a list of values, one for each n in nbunch.
        (omitting nbunch or nbunch=None is interpreted as nbunch = all
        nodes in graph.)

        If with_labels==True, then return a dict that maps each n
        in nbunch to degree(n).

        Any nodes in nbunch that are not in the graph are
        (quietly) ignored.
        
        """
        # prepare nbunch
        if nbunch is None: # include all nodes via iterator
            nbunch=self.nodes_iter()
        # if single node, return value
        elif nbunch in self:
            n=nbunch
            deg=len(self.succ[n])+len(self.pred[n])
            if with_labels:
                return {n:deg} # useless but self-consistent?
            else:
                return deg
        # do bunch of nodes
        d={}
        for n in nbunch:
            if n in self:
                d[n]=len(self.pred[n])+len(self.succ[n])
        if with_labels:
            return d
        else:
            return d.values()


    def out_degree(self,nbunch=None, with_labels=False):
        """Return out-degree of single node or of nbunch of nodes.

        If nbunch is omitted or nbunch=None, then return
        out-degrees of *all* nodes.
        
        """
        # prepare nbunch
        if nbunch is None: # include all nodes via iterator
            nbunch=self.nodes_iter()
        # if single node, return value
        elif nbunch in self:
            n=nbunch
            deg=len(self.succ[n])
            if with_labels:
                return {n:deg} # useless but self-consistent?
            else:
                return deg
        # do bunch of nodes
        d={}
        for n in nbunch:
            if n in self:
                d[n]=len(self.succ[n])
        if with_labels:
            return d
        else:
            return d.values()
        
    def in_degree(self,nbunch=None, with_labels=False):
        """Return in-degree of single node or of nbunch of nodes.

        If nbunch is omitted or nbunch=None, then return
        in-degrees of *all* nodes.

        """
        # prepare nbunch
        if nbunch is None: # include all nodes via iterator
            nbunch=self.nodes_iter()
        # if single node, return value
        elif nbunch in self:
            n=nbunch
            deg=len(self.pred[n])
            if with_labels:
                return {n:deg} # useless but self-consistent?
            else:
                return deg
        # do bunch of nodes
        d={}
        for n in nbunch:
            if n in self:
                d[n]=len(self.pred[n])
        if with_labels:
            return d
        else:
            return d.values()

    def clear(self):
        """Remove name and delete all nodes and edges from digraph."""
        self.name=""
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

        nbunch: either a singleton node, a string (which is treated
        as a singleton node), or any iterable (non-string) container
        of nodes for which len(nbunch) is defined. For example, a list,
        dict, set, Graph, numeric array, or user-defined iterable object. 

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
        # if nbunch is a single node in the graph then convert into a list
        # instead of iterating over it, this allows nodes to be iterable
        if nbunch in self: nbunch=[nbunch]

        if inplace: # demolish all nodes (and attached edges) not in nbunch
                    # override any setting of create_using
            if hasattr(nbunch,"next"): # if we are an simple iterator
                nbunch=dict.fromkeys(nbunch) # make a dict
            self.delete_nodes_from([n for n in self if not n in nbunch])
            self.name="Subgraph of (%s)"%(self.name)
            return self

        else:  # create new graph        
            if create_using is not None:  # user specified graph
                H=create_using
                H.clear()
            else:           # Graph object of the same type as current graph
                H=self.__class__()

            H.name="Subgraph of (%s)"%(self.name)
            # H.dna=self.dna.copy()  # do not copy dna to a subgraph

            H.add_nodes_from([n for n in nbunch if n in self])
            # add edges
            for n in H:
                gsn=self.succ[n]    # store in local variables for speed
                hsn=H.succ[n]
                for u in H:
                    if u in gsn:
                        hsn[u]=None
                        H.pred[u][n]=None
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
    suite = doctest.DocFileSuite('tests/base_Graph.txt',
                                 'tests/base_DiGraph.txt',
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
    
