"""
Base class for graphs.

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
#    Copyright (C) 2004-206 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert

class Graph(object):
    """Graph is a simple graph without any multiple (parallel) edges
    or self-loops.  Attempting to add either will not change
    the graph and will not report an error.

    """
    def __init__(self, data=None, name=''):
        """Initialize Graph.
        
        >>> G=Graph(name="empty")

        creates empty graph G with G.name="empty"

        """
        self.adj={}  # empty adjacency hash
        # attempt to load graph with data
        if data is not None:
            convert.from_whatever(data,create_using=self)
        self.name=name

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
            return n in self.adj
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
        return list(self.neighbors_iter(n))
    
    def prepare_nbunch(self,nbunch=None):
        """
        Return a sequence (or iterator) of nodes contained
        in nbunch which are also in the graph.

        The input nbunch can be a single node, a sequence or
        iterator of nodes or None (omitted).  If None, all
        nodes in the graph are returned.

        Note: This routine exhausts any iterator nbunch.
        
        Note: To test whether nbunch is a single node,
        one can use "if nbunch in self:", even after processing
        with this routine.
        
        Note: This routine raises a NetworkXError exception if
        nbunch is not either a node, sequence, iterator, or None.
        You can catch this exception if you want to change this
        behavior.
        """
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try:   # capture error for nonsequence/iterator entries.
                bunch=[n for n in nbunch if n in self]
                # bunch=(n for n in nbunch if n in self) # need python 2.4
            except TypeError:
               raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        return bunch

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
            if len(self) > 0:
                print ("Average degree:").ljust(width_left), \
                      round( 2*self.size()/float(len(self)), 4)
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
            except (KeyError, TypeError):
                raise NetworkXError, "node %s not in graph"%n


    def add_node(self, n):
        """
        Add a single node n to the graph.

        The node n can be any hashable object except None.

        A hashable object is one that can be used as a key in a Python
        dictionary. This includes strings, numbers, tuples of strings
        and numbers, etc.  On many platforms this also includes
        mutables such as Graphs e.g., though one should be careful the
        hash doesn't change on mutables.

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
        (thus it should be an iterator or be iterable).
        Each element of the container should be a valid node type:
        any hashable type except None.  See add_node for details.

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
        an iterable or iterator containing valid node names.

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
            return n in self.adj
        except TypeError:
            return False

    def order(self):
        """Return the order of a graph = number of nodes."""
        return len(self.adj)


    def add_edge(self, u, v=None):  
        """Add a single edge (u,v) to the graph.

        >> G.add_edge(u,v)
        and
        >>> G.add_edge( (u,v) )
        are equivalent forms of adding a single edge between nodes u and v.
        The nodes u and v will be automatically added if not already in
        the graph.  They must be a hashable (except None) Python object.

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

        Can be used in two basic forms: 
        >>> G.delete_edge(u,v)
        and
        >> G.delete_edge( (u,v) )
        are equivalent ways of deleting a single edge between nodes u and v.

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
        """Return True if graph contains the edge u-v, return False otherwise."""
        if  v is None:
            (u,v)=u    # split tuple in first position
        return self.adj.has_key(u) and self.adj[u].has_key(v)

    def has_neighbor(self, u, v):
        """Return True if node u has neighbor v.

        This is equivalent to has_edge(u,v).

        """
        return self.adj.has_key(u) and self.adj[u].has_key(v)


    def get_edge(self, u, v):
        """Return 1 if graph contains the edge u-v. 
        Raise an exception otherwise.
    
        """
        # useful for helping build adjacency matrix representation
        if v is None:
            (u,v)=u

        if self.has_edge(u,v):
            return 1
        else:
            raise NetworkXError, "no edge (%s,%s) in graph"%(u,v)


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
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        seen={}     # helper dict to keep track of multiply stored edges
        for n1 in bunch:
            for n2 in self.adj[n1]:
                if n2 not in seen:
                    yield (n1,n2)
            seen[n1]=1
        del(seen) # clear copy of temp dictionary
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

        nbunch1 and nbunch2 are usually meant to be disjoint, 
        but in the interest of speed and generality, that is 
        not required here.

        This routine is faster if nbunch1 is smaller than nbunch2.

        """
        if nbunch2 is None:     # Then nbunch2 is complement of nbunch1
            ndict1=dict.fromkeys([n for n in nbunch1 if n in self])
            return [(n1,n2) for n1 in ndict1 for n2 in self.adj[n1] \
                    if n2 not in ndict1]

        ndict2=dict.fromkeys(nbunch2)
        return [(n1,n2) for n1 in nbunch1 if n1 in self for n2 in self.adj[n1] \
                if n2 in ndict2]

    def node_boundary(self, nbunch1, nbunch2=None):
        """Return list of all nodes on external boundary of nbunch1 that are
        in nbunch2.  If nbunch2 is omitted or nbunch2=None, then nbunch2
        is all nodes not in nbunch1.

        Note that by definition the node_boundary is external to nbunch1.
        
        Nodes in nbunch1 and nbunch2 that are not in the graph are
        ignored.

        nbunch1 and nbunch2 are usually meant to be disjoint, 
        but in the interest of speed and generality, that is 
        not required here.

        This routine is faster if nbunch1 is smaller than nbunch2.

        """
        if nbunch2 is None:     # Then nbunch2 is complement of nbunch1
            ndict1=dict.fromkeys([n for n in nbunch1 if n in self])
            bdy={}
            for n1 in ndict1:
                for n2 in self.adj[n1]:
                    if n2 not in ndict1: 
                        bdy[n2]=1 # make dict to avoid duplicates
            return bdy.keys()
        
        ndict2=dict.fromkeys(nbunch2)
        bdy=[]
        for n1 in [n for n in nbunch1 if n in self]:
            for n2 in self.adj[n1]:
                if n2 in ndict2:
                    bdy.append(n2)
                    del ndict2[n2]  # avoid duplicates
        return bdy

    def degree(self, nbunch=None, with_labels=False):
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
        if with_labels:           # return a dict
            return dict(self.degree_iter(nbunch,with_labels))
        elif nbunch in self:      # return a single node
            return self.degree_iter(nbunch,with_labels).next()
        else:                     # return a list
            return list(self.degree_iter(nbunch,with_labels))

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
        if nbunch is None:   # include all nodes via iterator
            bunch=self.nodes_iter()
        elif nbunch in self: # if nbunch is a single node 
            bunch=[nbunch]
        else:                # if nbunch is a sequence of nodes
            try: bunch=[n for n in nbunch if n in self]
            except TypeError:
                raise NetworkXError, "nbunch is not a node or a sequence of nodes."
        # nbunch ready
        if with_labels:
            for n in bunch:
                yield (n,len(self.adj[n])) # tuple (n,degree)
        else:
            for n in bunch:
                yield len(self.adj[n])     # just degree
                        
    def clear(self):
        """Remove name and delete all nodes and edges from graph."""
        self.name=None
        self.adj.clear() 

    def copy(self):
        """Return a (shallow) copy of the graph.

        Identical to dict.copy() of adjacency dict adj, with name
        copied as well.
        
        """
        H=self.__class__()
        H.name=self.name
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
        from networkx.digraph import DiGraph
        H=DiGraph()
        H.name=self.name
        H.adj=self.adj.copy() # copy nodes
        H.succ=H.adj  # fix pointer again
        for v in H.adj:
            H.pred[v]=self.adj[v].copy()  # copy adj list to predecessor
            H.succ[v]=self.adj[v].copy()  # copy adj list to successor
        return H


    def subgraph(self, nbunch, inplace=False, create_using=None):
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
        H_adj=H.adj       # cache
        self_adj=self.adj # cache
        dict_fromkeys=dict.fromkeys
        for n in H:
            H_adj[n]=dict_fromkeys([u for u in self_adj[n] if u in H_adj], None)
        return H




# End of basic operations (under the hood and close to the datastructure)
# The following remaining Graph methods use the above methods and not the
# datastructure directly

    def add_path(self, nlist):
        """Add the path through the nodes in nlist to graph"""
        fromv = nlist[0]
        for tov in nlist[1:]:
            self.add_edge(fromv,tov)
            fromv=tov

    def add_cycle(self, nlist):
        """Add the cycle of nodes in nlist to graph"""
        self.add_path(nlist)
        self.add_edge(nlist[-1],nlist[0])  # wrap first element

    def is_directed(self):
        """ Return True if graph is directed."""
        return False

    def size(self):
        """Return the size of a graph = number of edges. """
        return sum(self.degree_iter())/2

    def number_of_edges(self):
        """Return the size of a graph = number of edges. """
        return sum(self.degree_iter())/2


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/graph_Graph.txt',
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
    
