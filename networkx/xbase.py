""" Methods for general graphs (XGraph) and digraphs (XDiGraph)
allowing self-loops, multiple edges, arbitrary (hashable) objects as
nodes and arbitrary objects associated with edges.

The XGraph and XDiGraph classes are extensions of the Graph and
DiGraph classes in base.py. The key difference
is that an XGraph edge is a 3-tuple e=(n1,n2,x), representing an
undirected edge between nodes n1 and n2 that is decorated with the
object x. Here n1 and n2 are (hashable) node objects and x is a (not
necessarily hashable) edge object. Since the edge is undirected,
edge (n1,n2,x) is equivalent to edge (n2,n1,x).

An XDiGraph edge is a similar 3-tuple e=(n1,n2,x), with the additional
property of directedness. I.e. e=(n1,n2,x) is a directed edge from n1 to
n2 decorated with the object x, and is not equivalent to the edge (n2,n1,x).

Whether a graph or digraph allow self-loops or multiple edges is
determined at the time of object instantiation via
specifying the parameters selfloops=True/False and
multiedges=True/False. For example,

an empty XGraph is created with:

>>> G=XGraph()

which is equivalent to

>>> G=XGraph(name="No Name", selfloops=False, multiedges=False)

and similarly for XDiGraph.

>>> G=XDiGraph(name="empty", multiedges=True)

creates an empty digraph G with G.name="empty", that do not
allow the addition of selfloops but do allow for multiple edges.


XGraph and XDiGraph are implemented using a data structure based on an
adjacency list implemented as a dictionary of dictionaries. The outer
dictionary is keyed by node to an inner dictionary keyed by
neighboring nodes to the edge data/labels/objects (which default to 1
to correspond the datastructure used in classes Graph and DiGraph).
If multiedges=True, a list of edge data/labels/objects is stored as
the value of the inner dictionary.  This double dict structure
mimics a sparse matrix and allows fast addition, deletion and lookup
of nodes and neighbors in large graphs.  The underlying datastructure
should only be visible in this module. In all other modules,
graph-like objects are manipulated solely via the methods defined here
and not by acting directly on the datastructure.

Similarities between XGraph and Graph

XGraph and Graph differ fundamentally; XGraph edges are 3-tuples
(n1,n2,x) and Graph edges are 2-tuples (n1,n2). XGraph inherits from the
Graph class, and XDiGraph from the DiGraph class.

They do share important similarities.

1. Edgeless graphs are the same in XGraph and Graph.
For an edgeless graph, represented by G (member of the Graph class)
and XG (member of XGraph class), there is no difference between
the datastructures G.adj and XG.adj, other than in the ordering of the
keys in the adj dict.

2. Basic graph construction code for G=Graph() will also work for G=XGraph().
In the Graph class, the simplest graph construction consists of a graph
creation command G=Graph() followed by a list of graph construction commands,
consisting of successive calls to the methods:

G.add_node, G.add_nodes_from, G.add_edge, G.add_edges, G.add_path,
G.add_cycle G.delete_node, G.delete_nodes_from, G.delete_edge,
G.delete_edges_from

with all edges specified as 2-tuples,  

If one replaces the graph creation command with G=XGraph(), and then
apply the identical list of construction commands, the resulting XGraph
object will be a simple graph G with identical datastructure G.adj. This
property ensures reuse of code developed for graph generation in the
Graph class.


Notation

The following shorthand is used throughout NetworkX documentation and code:
(we use mathematical notation n,v,w,... to indicate a node, v=vertex=node).
 
G,G1,G2,H,etc:
   Graphs

n,n1,n2,u,v,v1,v2:
   nodes (vertices)

nlist:
   a list of nodes (vertices)

nbunch:
   a "bunch" of nodes (vertices).
   an nbunch is any iterable (non-string) container 
   of nodes that is not itself a node of the graph.

e=(n1,n2):
   an edge (a python "2-tuple"), also written n1-n2 (if undirected)
   and n1->n2 (if directed). In Xgraph G.add_edge(n1,n2) is equivalent
   to add_edge(n1,n2,1). However, G.delete_edge(n1,n2) will delete all
   edges between n1 and n2.

e=(n1,n2,x):
   an edge triple ("3-tuple") containing the two nodes connected and the 
   edge data/label/object stored associated with the edge. The object x,
   or a list of objects (if multiedges=True), can be obtained using
   G.get_edge(n1,n2)

elist:
   a list of edges (as 2- or 3-tuples)

ebunch:
   a bunch of edges (as 2- or 3-tuples)
   an ebunch is any iterable (non-string) container
   of edge-tuples (either 2-tuples, 3-tuples or a mixture).
   (similar to nbunch, also see add_edge).

Warning:
  - The ordering of objects within an arbitrary nbunch/ebunch
    can be machine-dependent.
  - Algorithms should treat an arbitrary nbunch/ebunch as
    once-through-and-exhausted iterable containers.
  - len(nbunch) and len(ebunch) need not be defined.
    

Methods
=======

The XGraph class provides rudimentary graph operations:

Mutating Graph methods
----------------------
   
    - G.add_node(n), G.add_nodes_from(nbunch)
    - G.delete_node(n), G.delete_nodes_from(nbunch)
    - G.add_edge(n1,n2,x), G.add_edge(e), 
    - G.add_edges_from(ebunch)
    - G.delete_edge(n1,n2), G.delete_edge(n1,n2,x), G.delete_edge(e), 
    - G.delete_edges_from(ebunch)
    - G.add_path(nlist)
    - G.add_cycle(nlist)

    - G.to_directed()
    - G.ban_multiedges()
    - G.allow_multiedges()
    - G.delete_multiedges()
    - G.ban_selfloops()
    - G.allow_selfloops()
    - G.delete_selfloops()
    - G.clear()
    - G.subgraph(nbunch, inplace=True)

Non-mutating Graph methods
--------------------------

    - G.has_node(n)
    - G.nodes()
    - G.nodes_iter()
    - G.order()
    - G.neighbors(n), G.neighbors_iter(n) 
    - G.has_edge(n1,n2), G.has_neighbor(n1,n2)
    - G.edges(), G.edges(nbunch)
      G.edges_iter(), G.edges_iter(nbunch,
    - G.size()
    - G.get_edge(n1,n2)
    - G.degree(), G.degree(n), G.degree(nbunch)
    - G.degree_iter(), G.degree_iter(n), G.degree_iter(nbunch)
    - G.number_of_selfloops()
    - G.nodes_with_selfloops()
    - G.selfloop_edges()
    - G.copy()
    - G.subgraph(nbunch)
    
Examples
========

Create an empty graph structure (a "null graph") with
zero nodes and zero edges

>>> from networkx import *
>>> G=XGraph(directed=True)  # default no-loops, no-multiedges

You can add nodes in the same way as the simple Graph class
>>> G.add_nodes_from(xrange(100,110))

You can add edges as for simple Graph class, but with optional edge
data/labels/objects.

>>> G.add_edges_from([(1,2,0.776),(1,3,0.535)])

For graph coloring problems, one could use
>>> G.add_edges_from([(1,2,"blue"),(1,3,"red")])

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""

#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

from networkx.base import Graph, DiGraph, NetworkXException, NetworkXError


class XGraph(Graph):
    """A class implementing general undirected graphs, allowing
    (optional) self-loops, multiple edges, arbitrary (hashable)
    objects as nodes and arbitrary objects associated with
    edges.

    An XGraph edge is specified by a 3-tuple e=(n1,n2,x),
    where n1 and n2 are (hashable) objects (nodes) and x is an
    arbitrary (and not necessarily unique) object associated with that
    edge.

     >>> G=XGraph()

    creates an empty simple and undirected graph (no self-loops or
    multiple edges allowed).  It is equivalent to the expression:

    >>> G=XGraph(name="No Name",selfloops=False,multiedges=False)

    >>> G=XGraph(name="empty",multiedges=True)

    creates an empty graph with G.name="empty", that do not allow the
    addition of self-loops but do allow for multiple edges.
    
    See also the XDiGraph class below.

    """


    def __init__(self,**kwds):
        """Initialize XGraph.

        Optional arguments::
        name: graph name (default="No Name")
        selfloops: if True selfloops are allowed (default=False)
        multiedges: if True multiple edges are allowed (default=False)

        """
        self.name=kwds.get("name","No Name")
        self.selfloops=kwds.get("selfloops",False)    # no self-loops
        self.multiedges=kwds.get("multiedges",False)  # no multiedges

        # dna is a dictionary attached to each graph and used to store
        # information about the graph structure. In this version the
        # dna is provided as a user-defined variable and should not be
        # relied on.
        self.dna={}
        self.dna["datastructure"]="xgraph_dict_of_dicts"
        
        self.adj={}      # adjacency list

    def add_edge(self, n1, n2=None, x=None):  
        """Add a single edge to the graph.

        Can be called as G.add_edge(n1,n2,x)
        or as G.add_edge(e), where e=(n1,n2,x).

        n1,n2 are (hashable) node objects, and are added silently to
        the Graph if not already present.

        x is an arbitrary (not necessarily hashable) object associated
        with this edge. It can be used to associate one or more:
        labels, data records, weights or any arbirary objects to
        edges. 

        For example, if the graph G was created with

        >>> G=XGraph()

        then G.add_edge(1,2,"blue") will add the edge (1,2,"blue").

        If G.multiedges=False, then a subsequent G.add_edge(1,2,"red")
        will change the above edge (1,2,"blue") into the edge (1,2,"red").

        
        If G.multiedges=True, then two successive calls to
        G.add_edge(1,2,"red") will result in 2 edges of the form
        (1,2,"red") that can not be distinguished from one another.
        
        G.add_edge(1,2,"green") will add both edges (1,2,X) and (2,1,X).

        If self.selfloops=False, then calling add_edge(n1,n1,x) will have no
        effect on the Graph.

        Objects associated to an edge can be retrieved using edges(),
        edge_iter(), or get_edge().

        """
        if n2 is None:
            # add_edge was called as add_edge(e), with  e=(n1,n2,x)
            if len(n1)==3: #case e=(n1,n2,x)
                n1,n2,x=n1
            else:          # assume e=(n1,n2)
                n1,n2=n1
                x=1
        else:
            if x is None:
                # add_edge was called as add_edge(n1,n2)
                # interpret this as add_edge(n1,n2,1)
                x=1
        
        # don't create self loops, quietly return if not allowed
        if not self.selfloops and n1==n2: 
            return

        # if edge exists, quietly return if multiple edges are not allowed
        if not self.multiedges and self.has_edge(n1,n2,x):
            return

        # add nodes 
        self.adj.setdefault(n1,{})
        self.adj.setdefault(n2,{})
        if self.multiedges: # add x to the end of the list of objects
                            # that defines the edges between n1 and n2
            self.adj[n1][n2]=self.adj[n1].get(n2,[])+ [x]
            if n1!=n2:
                self.adj[n2][n1]=self.adj[n2].get(n1,[])+ [x]
        else:               # x becomes the new object associated with the
            #edge=x          # single edge between n1 and n2
            self.adj[n1][n2]=x
            if n1!=n2:
                self.adj[n2][n1]=x # a copy is required to avoid
                                        # modifying both at the same time
                                     # when doing a delete_edge

    def add_edges_from(self, ebunch):  
        """Add multiple edges to the graph.

        ebunch: Container of edges. Each edge must be a 3-tuple
        (n1,n2,x) or a 2-tuple (n1,n2). See add_edge documentation.

        The container must be iterable or an iterator.  It is iterated
        over once.

        """
        for e in ebunch:
            self.add_edge(e)

    def has_edge(self, n1, n2=None, x=None):
        """Return True if graph contains edge (n1,n2,x).

        Can be called as G.has_edge(n1,n2,x)
        or as G.has_edge(e), where e=(n1,n2,x).

        If x is unspecified, i.e. if called with an edge of the form
        e=(n1,n2), then return True if there exists ANY edge between
        n1 and n2 (equivalent to has_neighbor(n1,n2))

        """
        if n2 is None:
            # has_edge was called as has_edge(e)
            if len(n1)==3: #case e=(n1,n2,x)
                n1,n2,x=n1
            else:          # assume e=(n1,n2)
                n1,n2=n1
                return self.has_neighbor(n1,n2)
        else:
            if x is None:
                # has_edge was called as has_edge(n1,n2)
                # return True if there exists ANY
                # edge between n1 and n2
                return self.has_neighbor(n1,n2)
        # case where x is specified
        if self.multiedges:
            return (self.adj.has_key(n1) and
                self.adj[n1].has_key(n2) and
                x in self.adj[n1][n2])
        else:
            return (self.adj.has_key(n1) and
                self.adj[n1].has_key(n2) and
                x==self.adj[n1][n2])            


    def has_neighbor(self, n1, n2):
        """Return True if node n1 has neighbor n2.

        Note that this returns True if there exists ANY edge (n1,n2,x)
        for some x.

        """
        return (self.adj.has_key(n1) and
                self.adj[n1].has_key(n2))
    

    def neighbors_iter(self,n,with_labels=False):
        """Return an iterator for neighbors of n."""
        try:
            if with_labels:
                return self.adj[n].iteritems()
            else:
                return self.adj[n].iterkeys()
        except KeyError:
            raise NetworkXError, "node %s not in graph"%n

    def neighbors(self, n, with_labels=False):
        """Return a list of nodes connected to node n. 

        If with_labels=True, return a dict keyed by neighbors to 
        edge data for that edge. 

        """
        try:
            if with_labels:
                return self.adj[n].copy()
            else:
                return self.adj[n].keys()
        except KeyError:
            raise NetworkXError, "node %s not in graph"%n

    def get_edge(self, n1, n2):
        """Return the objects associated with each edge between n1 and n2.

        If multiedges=False, a single object is returned.
        If multiedges=True, a list of objects is returned.
        If no edge exists, raise an exception.

        """
        try:
            return self.adj[n1][n2]    # raises KeyError if edge not found
        except KeyError:
            raise NetworkXError, "no edge (%s,%s) in graph"%(n1,n2)
            
    def edges_iter(self, nbunch=None, with_labels=False):
        """Return iterator that iterates once over each edge adjacent
        to nodes in nbunch, or over all nodes in graph if nbunch=None.

        See add_node for definition of nbunch.
        
        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        
        with_labels=True option is not supported (in that case
        you should probably use neighbors()).           

        """
        if with_labels:
            # node labels not supported
            # rather use neighbors() method 
            raise NetworkXError, "with_labels=True option not supported. Rather use neighbors()"

        # prepare nbunch
        if nbunch is None: # include all nodes via iterator
            nbunch=self.nodes_iter()
        else:  # try nbunch as a single node
            n1=nbunch
            try:
                if self.multiedges:
                    for n2 in self.adj[n1]:
                        for x in self.adj[n1][n2]:
                            yield (n1,n2,x)
                else:   
                    for n2 in self.adj[n1]:
                        yield (n1,n2,self.adj[n1][n2])
                raise StopIteration
            except (KeyError,TypeError), e:  # n is not a node of self
                pass                         # treat as iterable
        # this part reached only if nbunch is a container of (possible) nodes 
        e={}  # helper dict used to avoid duplicate edges
        try:  # reach this only if nbunch should be iterated over
            for n1 in nbunch:
                if n1 in self.adj:          # if n1 in graph 
                    for n2 in self.adj[n1]: # if some edge n1-n2
                        if e.has_key((n2,n1)):
                            continue
                        e.setdefault((n1,n2),1)
                        if self.multiedges:
                            for x in self.adj[n1][n2]:
                                yield (n1,n2,x)
                        else:   
                            yield (n1,n2,self.adj[n1][n2])                            
        except TypeError:
            pass
        del(e) # clear copy of temp dictionary
               # iterators can remain after they finish returning values.

    def edges(self, nbunch=None, with_labels=False):
        """Return a list of all edges that originate at a node in nbunch,
        or a list of all edges if nbunch=None.

        See add_node for definition of nbunch.

        Nodes in nbunch that are not in the graph will be (quietly) ignored.
        
        with_labels=True option is not supported because in that case
        you should probably use neighbors().
        
        """
        return list(self.edges_iter(nbunch, with_labels))

    def delete_node(self,n):
        """Delete node n from graph.  

        Attempting to delete a non-existent node will raise an exception.

        """
        try:
            for n1 in self.adj[n].keys():  
                del self.adj[n1][n]  # remove all edges n1-n in graph
            del self.adj[n]          # now remove node and edges n-n1
        except KeyError: 
            raise NetworkXError, "node %s not in graph"%n

    def delete_nodes_from(self,nbunch):
        """Remove nodes in nbunch from graph.

        nbunch: an iterable or iterator containing valid(hashable) node names.

        Attempting to delete a non-existent node will raise an exception.
        This could result in a partial deletion of those nodes both in
        nbunch and in the graph.

        """
        for n in nbunch: 
            try:
                for n1 in self.adj[n].keys():  
                    del self.adj[n1][n]  # remove all edges n-n1 in graph
                del self.adj[n]          # now remove node
            except KeyError: 
                raise NetworkXError, "node %s not in graph"%n

    def delete_edge(self, n1, n2=None, x=None): 
        """Delete the edge (n1,n2,x) from the graph.

        Can be called either as G.delete_edge(n1,n2,x)
        or as G.delete_edge(e), where e=(n1,n2,x).

        If x is unspecified, i.e. if called with an edge e=(n1,n2),
        or as G.delete_edge(n1,n2), then delete all edges between n1 and n2.
        
        If the edge does not exist, do nothing.

        """
        if n2 is None:
            # delete_edge was called as delete_edge(e)
            if len(n1)==3:  #case e=(n1,n2,x)
                n1,n2,x=n1
            else:          # assume e=(n1,n2), x unspecified
                n1,n2=n1
                x=None
        if x is None:
                # delete all edges between n1 and n2.
                if not self.has_neighbor(n1,n2):
                    return
                if self.multiedges:
                    elist=[(n1,n2,x) for x in self.get_edge(n1,n2)]
                    self.delete_edges_from(elist)
                    return
                else:
                    x=self.get_edge(n1,n2)
                    
        elif not self.has_edge(n1,n2,x):
            return
        # (n1,n2,x) is an edge; now remove
        if self.multiedges:
            self.adj[n1][n2].remove(x)
            if n1!=n2:
                self.adj[n2][n1].remove(x)
            if len(self.adj[n1][n2])==0: # if last edge between n1 and n2
                del self.adj[n1][n2]     # was deleted
                if n1!=n2:
                    del self.adj[n2][n1]
        else:        
            # delete single edge
            del self.adj[n1][n2]
            if n1!=n2:
                del self.adj[n2][n1]
        return

    def delete_edges_from(self, ebunch): 
        """Delete edges in ebunch from the graph.

        ebunch: Container of edges. Each edge must be a 3-tuple
        (n1,n2,x) or a 2-tuple (n1,n2).  In the latter case all edges
        between n1 and n2 will be deleted. See delete_edge above.

        The container must be iterable or an iterator, and
        is iterated over once. Edges that are not in the graph are ignored.

        """
        for e in ebunch:
            # the function-call-in-a-loop cost can be avoided by pasting
            # in the code from delete_edge, do we have a good reason ?
            self.delete_edge(e)

    def degree(self, nbunch=None, with_labels=False):
        """Return degree of single node or of nbunch of nodes.
        If nbunch is omitted or nbunch=None, then return
        degrees of *all* nodes.
        
        The degree of a node is the number of edges attached to that
        node.

        Can be called in three ways:
          - G.degree(n):       return the degree of node n
          - G.degree(nbunch):  return a list of values,
             one for each n in nbunch
             (nbunch is any iterable container of nodes.)
          - G.degree(): same as nbunch = all nodes in graph.
             Always return a list.

        If with_labels==True, then return a dict that maps each n
        in nbunch to degree(n).

        Any nodes in nbunch that are not in the graph are
        (quietly) ignored.

        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            nbunch=self.adj.iterkeys()
        else:  
            try: # nbunch as a single node
                n=nbunch
                if self.multiedges:
                    deg=sum([ len(e) for e in self.adj[n].itervalues() ])
                    if self.adj[n].has_key(n) and self.selfloops:
                        deg+= len(self.adj[n][n])  # self loops double count
                    if with_labels:
                        return {n:deg} # useless but self-consistent?
                    else:
                        return deg
                else: # case without multiedges
                    deg=len(self.adj[n])
                    # self loops
                    deg+= self.has_edge(n,n)  # self loops double count
                    if with_labels:
                        return {n:deg} # useless but self-consistent?
                    else:
                        return deg
            except (KeyError,TypeError):  # n is not a node
                pass                      # treat as iterable
        # do bunch of nodes
        d={}
        if self.multiedges:
            for n in nbunch:
                if n in self:
                    deg = sum([len(e) for e in self.adj[n].itervalues()])
                    if self.adj[n].has_key(n) and self.selfloops:
                        deg+= len(self.adj[n][n])  # double count self-loops 
                    d[n]=deg
        else:
            # not multiedge
            for n in nbunch:
                if n in self:
                    deg=len(self.adj[n])
                    # self loops
                    deg+= self.adj[n].has_key(n)  # double count self-loop
                    d[n]=deg
        # return degree values of those nodes in the graph
        if with_labels:
            return d
        else:
            return d.values()

    def degree_iter(self,nbunch=None,with_labels=False):
        """This is the degree() method returned in interator form.
        If with_labels=True, iterator yields 2-tuples of form (n,degree(n))
        (like iteritems() on a dict.)
        """
        # prepare nbunch
        if nbunch is None:   # most likely case
            nbunch=self.adj.iterkeys()
        else:  
            try: # nbunch as a single node
                n=nbunch
                if self.multiedges:
                    deg=sum([ len(e) for e in self.adj[n].itervalues() ])
                    if self.adj[n].has_key(n) and self.selfloops:
                        deg+= len(self.adj[n][n])  # self loops double count
                    if with_labels:
                        yield (n,deg) # useless but self-consistent?
                    else:
                        yield deg
                else: # case without multiedges
                    deg=len(self.adj[n])
                    # self loops
                    deg+= self.has_edge(n,n)  # self loops double count
                    if with_labels:
                        yield (n,deg) # useless but self-consistent? 
                    else:
                        yield deg
                raise StopIteration       # don't leave this elif
            except (KeyError,TypeError):  # n is not a node
                pass                      # treat as iterable
        # do bunch of nodes
        if self.multiedges:
            for n in nbunch:
                if n in self:
                    deg = sum([len(e) for e in self.adj[n].itervalues()])
                    if self.adj[n].has_key(n) and self.selfloops:
                        deg+= len(self.adj[n][n])  # double count self-loops 
                    if with_labels:
                        yield (n,deg) # tuple (n,degree)
                    else:
                        yield deg
        else:
            # not multiedge
            for n in nbunch:
                if n in self:
                    deg=len(self.adj[n])
                    # self loops
                    deg+= self.adj[n].has_key(n)  # double count self-loop
                    if with_labels:
                        yield (n,deg) # tuple (n,degree)
                    else:
                        yield deg

    
    def number_of_edges(self):
        """Return number of edges"""
        return sum(self.degree_iter())/2

    def size(self):
        """Return the size of a graph = number of edges. """
        return self.number_of_edges()
    
    def copy(self):
        """Return a (shallow) copy of the graph.

        Return a new XGraph with same name and same attributes for
        selfloop and multiededges. Each node and each edge in original
        graph are added to the copy.
                
        """
        H=self.__class__(multiedges=self.multiedges,selfloops=self.selfloops)
        H.name=self.name
        H.dna=self.dna.copy()
        for n in self:
            H.add_node(n)
        for e in self.edges_iter():
            H.add_edge(e)
        return H
        
    def to_directed(self):
        """Return a directed representation of the XGraph G.

        A new XDigraph is returned with the same name, same nodes and
        with each edge (u,v,x) replaced by two directed edges
        (u,v,x) and (v,u,x).
        
        """
        H=XDiGraph(selfloops=self.selfloops,multiedges=self.multiedges)
        H.name=self.name
        H.dna=self.dna.copy()
        for n in self:
            H.add_node(n)
        for e in self.edges_iter():
            H.add_edge(e[0],e[1],e[2])
            H.add_edge(e[1],e[0],e[2])
        return H

    def nodes_with_selfloops(self):
        """Return list of all nodes having self-loops."""
        if not self.selfloops:
            return []
        else:
            return [n for n in self if self.adj[n].has_key(n)]

    def selfloop_edges(self):
        """Return all edges that are self-loops."""
        nlist=self.nodes_with_selfloops()
        loops=[]
        for n in nlist:
            if self.multiedges:
                for x in self.adj[n][n]:
                    loops.append((n,n,x))
            else:
                loops.append((n,n,self.adj[n][n]))
        return loops
            
    def number_of_selfloops(self):
        """Return number of self-loops in graph."""
        return len(self.selfloop_edges())

    def allow_selfloops(self):
        """Henceforth allow addition of self-loops
        (edges from a node to itself).

        This doesn't change the graph structure, only what you can do to it.
        """
        self.selfloops=True

    def delete_selfloops(self):
        """Remove self-loops from the graph (edges from a node to itself)."""
        if not self.selfloops:
            # nothing to do
            return
        for n in self.adj:
            if self.adj[n].has_key(n):
                del self.adj[n][n]            
 
    def ban_selfloops(self):
        """Remove self-loops from the graph and henceforth do not allow
        their creation.
        """
        self.delete_selfloops()
        self.selfloops=False


    def allow_multiedges(self):
        """Henceforth allow addition of multiedges (more than one
        edge between two nodes).  

        Warning: This causes all edge data to be converted to lists.
        """
        if self.multiedges: return # already multiedges
        self.multiedges=True
        for v in self.adj:
            for (u,edgedata) in self.adj[v].iteritems():
                self.adj[v][u]=[edgedata]

    def delete_multiedges(self):
        """Remove multiedges retaining the data from the first edge"""
        if not self.multiedges: # nothing to do
            return
        for v in self.adj:
            for (u,edgedata) in self.adj[v].iteritems():
                if len(edgedata)>1:
                    self.adj[v][u]=[edgedata[0]]

    def ban_multiedges(self):
        """Remove multiedges retaining the data from the first edge.
        Henceforth do not allow multiedges.
        """
        if not self.multiedges: # nothing to do
            return
        self.multiedges=False
        for v in self.adj:
            for (u,edgedata) in self.adj[v].iteritems():
                self.adj[v][u]=edgedata[0]
        
    def subgraph(self, nbunch, inplace=False, create_using=None):
        """Return the subgraph induced on nodes in nbunch.

       nbunch: either a singleton node, a string (which is treated
       as a singleton node), or any non-string iterable or iterator.
       For example, a list, dict, set, Graph, numeric array, or 
       user-defined iterable object. 

       Setting inplace=True will return induced subgraph in original
       graph by deleting nodes not in nbunch. It overrides any setting
       of create_using.

       WARNING: specifying inplace=True makes it easy to destroy the graph.

       Unless otherwise specified, return a new graph of the same
       type as self.  Use (optional) create_using=R to return the
       resulting subgraph in R. R can be an existing graph-like
       object (to be emptied) or R can be a call to a graph object,
       e.g. create_using=DiGraph(). See documentation for
       empty_graph()

       Note: use subgraph(G) rather than G.subgraph() to access the more
       general subgraph() function from the operators module.

        """
        # if nbunch is a single node convert into a list
        try: # duck typing
            if nbunch in self.adj:
                nbunch=[nbunch]
        except (KeyError,TypeError):
            pass

# WARNING: setting inplace=True makes it easy to destroy the graph.
        if inplace:
            # Demolish all nodes (and attached edges) not in nbunch
            # inplace=True overrides any setting of create_using
            #
            # We use a lookup table to avoid exhausting a "once-through"
            # nbunch iterator.
            # 
            # check if <iterator>
            if hasattr(nbunch,"next") and iter(nbunch) is nbunch: 
                # replace nbunch by a dict
                # this works OK if len(nbunch), which is undefined for
                # say a file, is much smaller than number of nodes in graph
                nbunch={}.fromkeys(nbunch,0) 
                
            # construct (possibly huge) helper list of nodes to delete,
            # required since we cannot delete nodes while iterating over graph 
            to_delete=[ n for n in self.adj if n not in nbunch ]
            for n in to_delete:
                self.delete_node(n)
            self.name="Subgraph of (%s)"%(self.name)
            return self

# Create new graph   (not inplace)       
        if create_using is None:
            # return a Graph object of the same type as current graph
            # subgraph inherits multiedges and selfloops settings
            H=self.__class__(multiedges=self.multiedges,
                             selfloops=self.selfloops)
        else:
            # Recreate subgraph with create_using.
            # Add nodes in subgraph, followed by iterating over
            # each edge e in subgraph with H.add_edge(e)
            # Currently create_using must be an XGraph type object
            # or a multi-edge list will be copied as a single edge
            H=create_using
            H.clear()
        H.name="Subgraph of (%s)"%(self.name)
        for n in nbunch:
            if n in self:
                H.adj.setdefault(n,{})  # add_node

        no_nodes_subgraph=len(H)
        no_nodes_graph=len(self)
        if self.multiedges:
            for n in H: # 
                s_adj_n=self.adj[n]    # store in local variables
                h_adj_n=H.adj[n]
                # loop over shorter sequence
                if no_nodes_subgraph > no_nodes_graph:
                    for u in s_adj_n:
                        if u in H:
                            h_adj_n[u]=s_adj_n[u][:]  # copy list
                else:
                    for u in H:
                        if u in s_adj_n:
                            h_adj_n[u]=s_adj_n[u][:]  # copy list
        else: # No multiedges
            for n in H: # 
                s_adj_n=self.adj[n]    # store in local variables
                h_adj_n=H.adj[n]
                # loop over shorter sequence
                if no_nodes_subgraph > no_nodes_graph:
                    for u in s_adj_n:
                        if u in H:
                            h_adj_n[u]=s_adj_n[u]
                else:
                    for u in H:
                        if u in s_adj_n:
                            h_adj_n[u]=s_adj_n[u]
        return H



# End of basic operations (under the hood and close to the datastructure)
# The following remaining Graph methods use the above methods and not the
# datastructure directly

    def add_path(self, nlist):
        """Add the path through the nodes in nlist to graph"""
        nfrom = nlist.pop(0)
        while len(nlist) > 0:
            nto=nlist.pop(0)
            self.add_edge(nfrom,nto)
            nfrom=nto

    def add_cycle(self, nlist):
        """Add the cycle of nodes in nlist to graph"""
        self.add_path(nlist+[nlist[0]])  # wrap first element

class XDiGraph(DiGraph):
    """ A class implementing general undirected digraphs, allowing
    (optional) self-loops, multiple edges, arbitrary (hashable)
    objects as nodes and arbitrary objects associated with
    edges.

    As in XGraph, an XDiGraph edge is uniquely specified by a 3-tuple
    e=(n1,n2,x), where n1 and n2 are (hashable) objects (nodes) and x
    is an arbitrary (and not necessarily unique) object associated with
    that edge.

    XDiGraph inherits from DiGraph, with all purely node-specific methods
    identical to those of DiGraph. XDiGraph edges are identical to XGraph
    edges, except that they are directed rather than undirected.
    XDiGraph replaces the following DiGraph methods:

    - __init__: read multiedges and selfloops kwds.
    - add_edge
    - add_edges_from
    - delete_edge
    - delete_edges_from
    - has_edge
    - edges_iter
    - degree_iter
    - degree
    - copy
    - clear
    - subgraph
    - is_directed
    - to_directed
    
    XDiGraph also adds the following methods to those of DiGraph:

    - allow_selfloops
    - remove_selfloops
    - ban_selfloops
    - allow_multiedges
    - remove_multiedges
    - ban_multiedges

    XDigraph adds the following methods to those of XGraph:

    - has_successor
    - successors
    - successors_iter
    - has_predecessor
    - predecessors
    - predecessors_iter
    - out_degree
    - out_degree_iter
    - in_degree
    - in_degree_iter
    - to_undirected
    - is_directed

    """
#    XDiGraph, like DiGraph, uses two adjacency lists:
#    predecessors of node n are stored in the dict
#    self.pred successors of node n are stored in the
#    dict self.succ=self.adj
#
#    For each edge (n1,n2,x) in self.succ there exists a corresponding edge
#    (n2,n1,x) in self.pred

    def __init__(self,**kwds):
        """Initialize XDiGraph.

        Optional arguments::
        name: digraph name (default="No Name")
        selfloops: if True then selfloops are allowed (default=False)
        multiedges: if True then multiple edges are allowed (default=False)

        """
        self.name=kwds.get("name","No Name")
        self.selfloops=kwds.get("selfloops",False)    # no self-loops
        self.multiedges=kwds.get("multiedges",False)  # no multiedges

        # dna is a dictionary attached to each graph and used to store
        # information about the graph structure. In this version the
        # dna is provided as a user-defined variable and should not be
        # relied on.
        self.dna={}
        self.dna["datastructure"]="xgraph_dict_of_dicts"
        
        self.adj={}         # adjacency list
        self.pred={}        # predecessor
        self.succ=self.adj  # successor is same as adj


    def add_edge(self, n1, n2=None, x=None):  
        """Add a single directed edge to the digraph.

        Can be called as G.add_edge(n1,n2,x)
        or as G.add_edge(e), where e=(n1,n2,x).

        If called as G.add_edge(n1,n2) or G.add_edge(e), with e=(n1,n2),
        then this is interpreted as adding the edge (n1,n2,1), so as to
        be compatible with the Graph and DiGraph classes.

        n1,n2 are (hashable) node objects, and are added silently to
        the Graph if not already present.

        x is an arbitrary (not necessarily hashable) object associated
        with this edge. It can be used to associate one or more,
        labels, data records, weights or any arbirary objects to
        edges. 

        For example, if the graph G was created with

        >>> G=XDiGraph()

        then G.add_edge(1,2,"blue") will add the directed edge (1,2,"blue").

        If G.multiedges=False, then a subsequent G.add_edge(1,2,"red")
        will change the above edge (1,2,"blue") into the edge (1,2,"red").
        
        On the other hand, if G.multiedges=True, then two successive calls to
        G.add_edge(1,2,"red") will result in 2 edges of the form
        (1,2,"red") that can not be distinguished from one another.
        
        If self.selfloops=False, then any attempt to create a self-loop
        with add_edge(n1,n1,x) will have no effect on the digraph and
        will not elicit a warning.

        Objects imbedded in the edges from n1 to n2 (if any), can be
        retrieved using get_edge(n1,n2), or calling edges(n1) or
        edge_iter(n1) to return all edges attached to n1.

        """
        # parse args
        if n2 is None:
            # add_edge was called as add_edge(e), with e a tuple
            if len(n1)==3: #case e=(n1,n2,x)
                n1,n2,x=n1
            else:          # assume e=(n1,n2)
                n1,n2=n1
                x=1
        else:
            if x is None:
                # add_edge was called as add_edge(n1,n2)
                # interpret this as add_edge(n1,n2,1)
                x=1
        
        # if edge is a self-loop, quietly return if not allowed
        if not self.selfloops and n1==n2: 
            return

        # if edge exists, quietly return if multiple edges are not allowed
        if not self.multiedges and self.has_edge(n1,n2,x):
            return
        # add nodes if they do not exist
        self.succ.setdefault(n1,{})
        self.succ.setdefault(n2,{})
        self.pred.setdefault(n1,{})
        self.pred.setdefault(n2,{})
        if self.multiedges: # append x to the end of the list of objects
                            # that defines the edges between n1 and n2
            self.succ[n1][n2]=self.succ[n1].get(n2,[])+ [x]
            self.pred[n2][n1]=self.pred[n2].get(n1,[])+ [x]
        else:               # x becomes the new object associated with the
           # edge=x          # single edge from n1 to n2
            self.succ[n1][n2]=x
            self.pred[n2][n1]=x # note that the same object is referred to
                                # from both succ and pred

    def add_edges_from(self, ebunch):  
        """Add multiple directed edges to the digraph.

        ebunch: Container of edges. Each edge e in container will be added
        using add_edge(e). See add_edge documentation.

        The container must be iterable or an iterator.
        It is iterated over once.

        """
        for e in ebunch:
            # the function-call-in-a-loop cost can be avoided by pasting
            # in the code from add_edge, do we have a good reason ?
            self.add_edge(e)
        
    def has_edge(self, n1, n2=None, x=None):
        """Return True if digraph contains directed edge (n1,n2,x).

        Can be called as G.has_edge(n1,n2,x)
        or as G.has_edge(e), where e=(n1,n2,x).

        If x is unspecified, i.e. if called with an edge of the form
        e=(n1,n2), then return True if there exists ANY edge from n1
        to n2 (equivalent to has_successor(n1,n2)).

        """
        # parse args
        if n2 is None:
            # has_edge was called as has_edge(e)
            if len(n1)==3: # case e=(n1,n2,x)
                n1,n2,x=n1
            else:          # case=(n1,n2)
                n1,n2=n1   # return True if there exists ANY edge n1->n2
                return self.has_successor(n1,n2)
        else:
            if x is None:
                # has_edge was called as has_edge(n1,n2)
                # return True if there exists ANY edge n1->n2
                return self.has_successor(n1,n2)
        # case where x is specified
        if self.multiedges:
            return (self.succ.has_key(n1) and
                self.succ[n1].has_key(n2) and
                x in self.succ[n1][n2])
        else:
            return (self.succ.has_key(n1) and
                self.succ[n1].has_key(n2) and
                x==self.succ[n1][n2])            

    def has_successor(self, n1, n2):
        """Return True if node n1 has a successor n2.

        Return True if there exists ANY edge (n1,n2,x) for some x.

         """
        return (self.succ.has_key(n1) and
                self.succ[n1].has_key(n2))

    def has_predecessor(self, n1, n2):
        """Return True if node n1 has a predecessor n2.

        Return True if there exists ANY edge (n2,n1,x) for some x.

        """
        return (self.pred.has_key(n1) and
                self.pred[n1].has_key(n2))    
    
    def has_neighbor(self, n1, n2):
        """Return True if node n1 and n2 are connected.

        True if there exists ANY edge (n1,n2,x) or (n2,n1,x)
        for some x.

        """
        return ((self.succ.has_key(n1) and
                 self.succ[n1].has_key(n2))
                 or
                (self.pred.has_key(n1) and
                 self.pred[n1].has_key(n2))) 

    def get_edge(self, n1, n2):
        """Return the objects associated with each edge between n1 and n2.

        If multiedges=False, a single object is returned.
        If multiedges=True, a list of objects is returned.
        If no edge exists, raise an exception.

        """
        try:
            return self.adj[n1][n2]    # raises KeyError if edge not found
        except KeyError:
            raise NetworkXError, "no edge (%s,%s) in graph"%(n1,n2)


    def delete_edge(self, n1, n2=None, x=None): 
        """Delete the directed edge (n1,n2,x) from the graph.

        Can be called either as G.delete_edge(n1,n2,x)
        or as G.delete_edge(e), where e=(n1,n2,x).

        If x is unspecified, i.e. if called with an edge e=(n1,n2),
        or as G.delete_edge(n1,n2), then delete all edges between n1 and n2.
        
        If the edge does not exist, do nothing.

        """
        # parse arguments
        if n2 is None:
            # delete_edge was called as delete_edge(e)
            if len(n1)==3:  #case e=(n1,n2,x)
                n1,n2,x=n1
            else:          # assume e=(n1,n2), x unspecified
                n1,n2=n1
                x=None
        if x is None:
                # delete all edges between n1 and n2.
                if not self.has_neighbor(n1,n2):
                    return
                if self.multiedges:
                    elist=[(n1,n2,x) for x in self.get_edge(n1,n2)]
                    self.delete_edges_from(elist)
                    return
                else:
                    x=self.get_edge(n1,n2)
                    
        elif not self.has_edge(n1,n2,x):
            return
        # (n1,n2,x) is an edge; now remove
        if self.multiedges:
            self.succ[n1][n2].remove(x)
            self.pred[n2][n1].remove(x)
            if len(self.succ[n1][n2])==0: # if last edge between n1 and n2
                del self.succ[n1][n2]     # was deleted
                del self.pred[n2][n1]
        else:        
            # delete single edge
            del self.succ[n1][n2]
            del self.pred[n2][n1]
        return

    def delete_edges_from(self, ebunch, data=None): 
        """Delete edges in ebunch from the graph.

        ebunch: Container of edges. Each edge must be a 3-tuple
        (n1,n2,x) or a 2-tuple (n1,n2).  The container must be
        iterable or an iterator, and is iterated over once. Edges
        that are not in the graph are ignored.

        """
        # FIXME - handle data?
        for e in ebunch:
            self.delete_edge(e)

    def edges_iter(self, nbunch=None,with_labels=False):
        """Return iterator that iterates once over each edge adjacent
        to nodes in nbunch, or over all edges in digraph if no
        nodes are specified.

        See add_node for definition of nbunch.
        
        Those nodes in nbunch that are not in the graph will be
        (quietly) ignored.
        
        with_labels=True is not supported. (In that case
        you should probably use neighbors().)           

        """

        if with_labels:
            # node labels not supported
            # rather use neighbors() method 
            raise NetworkXError, "with_labels=True option not supported. Rather use neighbors()"


        if nbunch is None: # include all nodes via iterator
            nbunch=self.nodes_iter()
        # try nbunch as a single node
        else: # try nbunch as a single node
              # note that nbunch can be anything, and testing for
              # nbunch in self can raise a TypeError if nbunch is unhashable,
              # e.g. if nbunch is a list
            n1=nbunch
            try:
                if self.multiedges:
                    for n2 in self.succ[n1]:
                        for x in self.succ[n1][n2]:
                                yield (n1,n2,x)
                    for n2 in self.pred[n1]:
                        for x in self.pred[n1][n2]:
                                yield (n2,n1,x)                
                else:
                    for n2 in self.succ[n1]:
                        yield (n1,n2,self.succ[n1][n2])
                    for n2 in self.pred[n1]:
                        yield (n2,n1,self.pred[n1][n2])
                raise StopIteration
            except (KeyError,TypeError), e:  # n is not a node of self
                pass                         # treat as iterable    
        # this part reached only if nbunch is a container of (possible) nodes
        e={}  # helper dict used to avoid duplicate edges
        try:
            for n1 in nbunch:
                if n1 in self.succ:
                    for n2 in self.succ[n1]:
                        if not e.has_key((n1,n2)):
                            e.setdefault((n2,n1),1)
                            if self.multiedges:
                                for x in self.succ[n1][n2]:
                                    yield (n1,n2,x)
                            else:
                                yield (n1,n2,self.succ[n1][n2])
                if n1 in self.pred:
                    for n2 in self.pred[n1]:
                        if not e.has_key((n1,n2)):
                            e.setdefault((n2,n1),1)
                            if self.multiedges:
                                for x in self.pred[n1][n2]:
                                   yield (n2,n1,x)
                            else:
                                yield (n2,n1,self.pred[n1][n2])
        except TypeError:
            pass
        del(e) # clear copy of temp dictionary
               # iterators can remain after they finish returning values.

    def successors(self, n, with_labels=False):
        """Return a list of all successor nodes of node n. 

        If with_labels=True, return a dict keyed by successors to 
        edge data for that edge. 

        """
        try:
            if with_labels:
                return self.succ[n].copy()
            else:
                return self.succ[n].keys()
        except KeyError:
            raise NetworkXError, "node %s not in graph"%n


    def predecessors(self, n, with_labels=False):
        """Return a list of predecessor nodes of node n. 

        If with_labels=True, return a dict keyed by predecessors to 
        edge data for that edge. 

        """
        try:
            if with_labels:
                return self.pred[n].copy()
            else:
                return self.pred[n].keys()
        except KeyError:
            raise NetworkXError, "node %s not in graph"%n


    def neighbors(self, n, with_labels=False):
        """Return a list of all nodes connected to node n. 

        If with_labels=True, return a dict keyed by neighbors to 
        edge data for that edge.  If neighbor has both in and out
        edge, the edge data is returned as the list [indata, outdata] 

        The node n will be a neighbor of itself if a selfloop exists.
        """
        if n not in self:
            raise NetworkXError, "node %s not in graph"%n

        # n is both in pred and succ
        if with_labels:
            nbrs=self.pred[n].copy()   # nbrs starts as pred dict
            # succs=self.succ[n]
            if self.multiedges:
                # add lists from succs
                for (v,data) in self.succ[n].iteritems():
                    nbrs[v]=nbrs.get(v,[])+data
            else:
                for (v,data) in self.succ[n].iteritems():
                    if v in nbrs:
                        nbrs[v]=[nbrs[v],data]
                    else:
                        nbrs[v]=data
            return nbrs
        else:
            nbrs=self.pred[n].copy()   # nbrs starts as pred dict
            for v in self.succ[n]:
                nbrs[v]=1
            return nbrs.keys()

    def neighbors_iter(self,n,with_labels=False):
        """Return an iterator for neighbors of n.

        If with_labels=True, the iterator returns (neighbor, edge_data) tuples
        for each edge.  If neighbor has both in and out edges, the edge data 
        is either:
        1) concatenated as lists if multiedges==True,   or
        2) returned as the list [indata, outdata]  if multiedges==False.

        The node n will be a neighbor of itself if a selfloop exists.
        """
        try:
            succs=self.succ[n]
            preds=self.pred[n]
            if with_labels:
                if self.multiedges:
                    for (v,pd) in preds.iteritems():
                        if v in succs:
                            yield (v,pd+succs[v])
                        else:
                            yield (v,pd)
                    for (v,sd) in succs.iteritems():
                        if v not in preds:
                            yield (v,sd)
                else:
                    for (v,pd) in preds.iteritems():
                        if v in succs:
                            yield (v,[pd,succs[v]])
                        else:
                            yield (v,pd)
                    for (v,sd) in succs.iteritems():
                        if v not in preds:
                            yield (v,sd)
            else:
                for v in preds:
                    yield v
                for v in succs:
                    if v not in preds:
                        yield v
        except KeyError:
            raise NetworkXError, "node %s not in graph"%n

    def in_degree(self, nbunch=None, with_labels=False):
        """Return the in-degree of single node or of nbunch of nodes.
        If nbunch is omitted or nbunch=None, then return
        in-degrees of *all* nodes.
        
        If with_labels=True, then return a dict that maps each n
        in nbunch to in_degree(n).

        Any nodes in nbunch that are not in the graph are
        (quietly) ignored.

        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            nbunch=self.pred.iterkeys()
        else:  
            try: # nbunch as a single node
                n=nbunch
                if self.multiedges:
                    deg=sum([len(edge) for edge in self.pred[n].itervalues()])
                else: # case without multiedges
                    deg=len(self.pred[n])
                if with_labels:
                    return {n:deg} # useless but self-consistent?
                else:
                    return deg
            except (KeyError,TypeError):  # n is not a node
                pass                      # treat as iterable
        # do bunch of nodes
        d={}
        if self.multiedges:
            for n in nbunch:
                if n in self:
                    d[n] = sum([len(edge)
                               for edge in self.pred[n].itervalues()])
        else:
            # not multiedge
            for n in nbunch:
                if n in self:
                    d[n]=len(self.pred[n])
        # return degree values of those nodes in the graph
        if with_labels:
            return d
        else:
            return d.values()

    def out_degree(self, nbunch=None, with_labels=False):
        """Return the out-degree of single node or of nbunch of nodes.
        If nbunch is omitted or nbunch=None, then return
        out-degrees of *all* nodes.
        
        If with_labels=True, then return a dict that maps each n
        in nbunch to out_degree(n).

        Any nodes in nbunch that are not in the graph are
        (quietly) ignored.

        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            nbunch=self.succ.iterkeys()
        else:  
            try: # nbunch as a single node
                n=nbunch
                if self.multiedges:
                    deg=sum([len(edge) for edge in self.succ[n].itervalues()])
                else: # case without multiedges
                    deg=len(self.succ[n])
                if with_labels:
                    return {n:deg} # useless but self-consistent?
                else:
                    return deg
            except (KeyError,TypeError):  # n is not a node
                pass                      # treat as iterable
        # do bunch of nodes
        d={}
        if self.multiedges:
            for n in nbunch:
                if n in self:
                    d[n] = sum([len(edge)
                               for edge in self.succ[n].itervalues()])
        else:
            # not multiedge
            for n in nbunch:
                if n in self:
                    d[n]=len(self.succ[n])
        if with_labels:
            return d
        else:
            return d.values()

    def degree(self, nbunch=None, with_labels=False):
        """Return the out-degree of single node or of nbunch of nodes.
        If nbunch is omitted or nbunch=None, then return
        out-degrees of *all* nodes.
        
        If with_labels=True, then return a dict that maps each n
        in nbunch to out_degree(n).

        Any nodes in nbunch that are not in the graph are
        (quietly) ignored.

        """
        # prepare nbunch
        if nbunch is None:   # include all nodes via iterator
            nbunch=self.succ.iterkeys()
        else:  
            try: # nbunch as a single node
                n=nbunch
                if self.multiedges:
                    deg=sum([len(e) for e in self.succ[n].itervalues()])  + \
                        sum([len(e) for e in self.pred[n].itervalues()])
                else:
                    deg=len(self.succ[n])+len(self.pred[n])
                if with_labels:
                    return {n:deg} 
                else:
                    return deg
            except (KeyError,TypeError):  # n is not a node
                pass                      # treat as iterable
        # case where nbunch is a container of (possible) nodes 
        d={}
        if self.multiedges:
            for n in nbunch:
                if n in self:
                    d[n]=sum([len(e) for e in self.succ[n].itervalues()]) + \
                         sum([len(e) for e in self.pred[n].itervalues()])
        else:
            # not multiedge
            for n in nbunch:
                if n in self:
                    d[n]=len(self.succ[n])+len(self.pred[n])
        if with_labels:
            return d
        else:
            return d.values()

    def nodes_with_selfloops(self):
        """Return list of all nodes having self-loops."""
        if not self.selfloops:
            return []
        else:
            # only need to do this for succ
            return [n for n in self if self.succ[n].has_key(n)]

    def selfloop_edges(self):
        """Return all edges that are self-loops."""
        nlist=self.nodes_with_selfloops()
        loops=[]
        for n in nlist:
            if self.multiedges:
                for x in self.succ[n][n]:
                    loops.append((n,n,x))
            else:
                loops.append((n,n,self.succ[n][n]))
        return loops
            
    def number_of_selfloops(self):
        """Return number of self-loops in graph."""
        return len(self.selfloop_edges())

    def allow_selfloops(self):
        """Henceforth allow addition of self-loops
        (edges from a node to itself).

        This doesn't change the graph structure, only what you can do to it.
        """
        self.selfloops=True

    def delete_selfloops(self):
        """Remove self-loops from the graph (edges from a node to itself)."""
        for n in self.succ:
            if self.succ[n].has_key(n):
                del self.succ[n][n]
                del self.pred[n][n]
 
    def ban_selfloops(self):
        """Remove self-loops from the graph and henceforth do not allow
        their creation.
        """
        self.delete_selfloops()
        self.selfloops=False


    def allow_multiedges(self):
        """Henceforth allow addition of multiedges (more than one
        edge between two nodes).  

        Warning: This causes all edge data to be converted to lists.
        """
        if self.multiedges: return # already multiedges
        self.multiedges=True
        for v in self.succ:
            for (u,edgedata) in self.succ[v].iteritems():
                self.succ[v][u]=[edgedata]
                self.pred[u][v]=[edgedata]

    def delete_multiedges(self):
        """Remove multiedges retaining the data from the first edge"""
        if not self.multiedges: # nothing to do
            return
        for v in self.succ:
            for (u,edgedata) in self.succ[v].iteritems():
                if len(edgedata)>1:
                    self.succ[v][u]=[edgedata[0]]
                    self.pred[u][v]=[edgedata[0]]

    def ban_multiedges(self):
        """Remove multiedges retaining the data from the first edge.
        Henceforth do not allow multiedges.
        """
        if not self.multiedges: # nothing to do
            return
        self.multiedges=False
        for v in self.succ:
            for (u,edgedata) in self.succ[v].iteritems():
                self.succ[v][u]=edgedata[0]
                self.pred[u][v]=edgedata[0]
        
    def subgraph(self, nbunch, inplace=False, create_using=None):
        """Return the subgraph induced on nodes in nbunch.

       nbunch: either a singleton node, a string (which is treated
       as a singleton node), or any non-string iterable or iterator.
       For example, a list, dict, set, Graph, numeric array, or 
       user-defined iterable object. 

       Setting inplace=True will return induced subgraph in original
       graph by deleting nodes not in nbunch. It overrides any setting
       of create_using.

       WARNING: specifying inplace=True makes it easy to destroy the graph.

       Unless otherwise specified, return a new graph of the same
       type as self.  Use (optional) create_using=R to return the
       resulting subgraph in R. R can be an existing graph-like
       object (to be emptied) or R can be a call to a graph object,
       e.g. create_using=DiGraph(). See documentation for
       empty_graph()

       Note: use subgraph(G) rather than G.subgraph() to access the more
       general subgraph() function from the operators module.

        """
        # if nbunch is a single node convert into a list
        try: # duck typing
            if nbunch in self.adj:
                nbunch=[nbunch]
        except (KeyError,TypeError):
            pass

        # WARNING: setting inplace=True makes it easy to destroy the graph.

        if inplace:
            # Demolish all nodes (and attached edges) not in nbunch
            # inplace=True overrides any setting of create_using
            #
            # We use a lookup table to avoid exhausting a "once-through"
            # nbunch iterator.
            # 
            # check if <iterator>
            if hasattr(nbunch,"next") and iter(nbunch) is nbunch: 
                # replace nbunch by a dict
                # this works OK if len(nbunch), which is undefined for
                # say a file, is much smaller than number of nodes in graph
                nbunch={}.fromkeys(nbunch,0) 
                
            # construct (possibly huge) helper list of nodes to delete,
            # required since we cannot delete nodes while iterating over graph 
            to_delete=[ n for n in self.succ if n not in nbunch ]
            for n in to_delete:
                self.delete_node(n)
            self.name="Subgraph of (%s)"%(self.name)
            return self
        # create new graph        
        if create_using is None:
            # return a Graph object of the same type as current graph
            # subgraph inherits multiedges and selfloops settings
            H=self.__class__(multiedges=self.multiedges,
                             selfloops=self.selfloops)
        else:
            # Recreate subgraph with create_using.
            # Add nodes in subgraph, followed by iterating over
            # each edge e in subgraph with H.add_edge(e)
            # Currently create_using must be an XGraph type object
            # or a multi-edge list will be copied as a single edge
            H=create_using
            H.clear()
        H.name="Subgraph of (%s)"%(self.name)
        for n in nbunch:
            if n in self:
                H.succ.setdefault(n,{})  # add_node
                H.pred.setdefault(n,{})  

        # Copy edge data
        no_nodes_subgraph=len(H)
        no_nodes_graph=len(self)
        if self.multiedges:
            for n in H: # 
                s_succ_n=self.succ[n]    # store in local variables
                h_succ_n=H.succ[n]
                # loop over shorter sequence
                if no_nodes_subgraph > no_nodes_graph:
                    for u in s_succ_n:
                        if u in H:
                            edata=s_succ_n[u][:] # copy edge data
                            h_succ_n[u]=edata
                            H.pred[u][n]=edata
                else:
                    for u in H:
                        if u in s_succ_n:
                            edata=s_succ_n[u][:] # copy edge data
                            h_succ_n[u]=edata
                            H.pred[u][n]=edata
        else: # No multiedges
            for n in H: # 
                s_succ_n=self.succ[n]    # store in local variables
                h_succ_n=H.succ[n]
                # loop over shorter sequence
                if no_nodes_subgraph > no_nodes_graph:
                    for u in s_succ_n:
                        if u in H:
                            edata=s_succ_n[u]
                            h_succ_n[u]=edata
                            H.pred[u][n]=edata
                else:
                    for u in H:
                        if u in s_succ_n:
                            edata=s_succ_n[u]
                            h_succ_n[u]=edata
                            H.pred[u][n]=edata
        return H

    def copy(self):
        """Return a (shallow) copy of the digraph.

        Return a new XDiGraph with same name and same attributes for
        selfloop and multiededges. Each node and each edge in original
        graph are added to the copy.
        
        """
        H=self.__class__(multiedges=self.multiedges,selfloops=self.selfloops)
        H.name=self.name
        H.dna=self.dna.copy()
        for n in self:
            H.add_node(n)
        for e in self.edges_iter():
            H.add_edge(e)
        return H        

    def to_undirected(self):
        """Return the underlying graph of G.
        
        The underlying graph is its undirected representation: each directed
        edge is replaced with an undirected edge.

        If multiedges=True, then an XDiGraph with only two directed
        edges (1,2,"red") and (2,1,"blue") will be converted into an
        XGraph with two undirected edges (1,2,"red") and (1,2,"blue").
        Two directed edges (1,2,"red") and (2,1,"red") will result in
        in two undirected edges (1,2,"red") and (1,2,"red").

        If multiedges=False, then two directed edges (1,2,"red") and
        (2,1,"blue") can only result in one undirected edge, and there
        is no garantee which one it is.
        
        """
        H=XGraph(multiedges=self.multiedges,selfloops=self.selfloops)
        H.name=self.name
        H.dna=self.dna.copy()
        for n in self:
            H.add_node(n)                   # copy nodes
        for e in self.edges_iter():
            H.add_edge(e)                   # convert each edge
        return H

        
def _test_suite():
    import doctest
    suite = doctest.DocFileSuite(
                                'tests/xbase_Graph.txt',
                                'tests/xbase_PseudoGraph.txt',
                                'tests/xbase_DiGraph.txt',
                                 package='networkx')
    return suite


if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    
