"""
Base class for MultiDiGraph.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""

#    Copyright (C) 2004-2009 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

from networkx.classes.graph import Graph  # for doctests
from networkx.classes.digraph import DiGraph
from networkx.classes.multigraph import MultiGraph
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert


class MultiDiGraph(MultiGraph,DiGraph):
    """A directed graph that allows multiple (parallel) edges with arbitrary
    data on the edges.

    Subclass of MultiGraph and DiGraph (which are both subclasses of Graph).

    Examples
    ========

    Create an empty graph structure (a "null graph") with no nodes and no edges

    >>> G=nx.MultiDiGraph()

    You can add nodes in the same way as the simple Graph class
    >>> G.add_nodes_from(xrange(100,110))

    You can add edges with data/labels/objects as for the Graph class,
    but here the same two nodes can have more than one edge between them.

    >>> G.add_edges_from([(1,2,0.776),(1,3,0.535)])

    For graph coloring problems, one could use
    >>> G.add_edges_from([(1,2,"blue"),(1,3,"red")])

    A MultiDiGraph edge is uniquely specified by a 3-tuple
    e=(u,v,k), where u and v are (hashable) objects (nodes) and k
    is an arbitrary (and necessarily unique) key associated with
    that edge.  If the key is not specified, one will be assigned internally.

    The multidigraph is directed and multiple edges between the same nodes
    are allowed.

    MultiDiGraph inherits all purely node-specific methods from DiGraph
    and some edge methods from MultliGraph.
    MultiDiGraph edges are identical to MultiGraph
    edges, except that they are directed rather than undirected.

    MultiDiGraph replaces the following DiGraph methods:

    - add_edge
    - add_edges_from
    - remove_edge
    - remove_edges_from
    - has_edge
    - get_edge
    - edges_iter
    - degree_iter
    - in_degree_iter
    - out_degree_iter
    - selfloop_edges
    - number_of_selfloops
    - subgraph
    - to_undirected

    MultiDigraph adds the following methods to those of MultiGraph:

    - has_successor
    - has_predecessor
    - successors
    - predecessors
    - successors_iter
    - predecessors_iter
    - in_degree
    - out_degree
    - in_degree_iter
    - out_degree_iter

    """
    multigraph=True
    directed=True

    def add_edge(self, u, v, data=1, key=None):
        """Add a single directed edge (u,v) to the multidigraph.

        Parameters
        ----------
        u, v : nodes
            Nodes can be any hashable Python objects such as strings or
            numbers, but None is not allowed as a node object. The order of
            u and v specifies the direction of the edge. In this case, the
            method adds a directed edge from u to v.

        data : any Python object (default: 1)
            Data can be arbitrary (not necessarily hashable) object associated
            with the edge (u,v). It can be used to associate one or more
            labels, data records, weights or any arbitrary objects to edges.

        key : any hashable Python object (default: None)
            A key associated with a directed edge can be any arbitrary Python
            object. It is used for distinguishing between directed edges with
            the same nodes. If more than one directed edge share the same pair
            of nodes, then the keys associated with those edges must each be
            unique. If the key is not specified, one will be assigned
            internally.

        For example, after creation, the edge (1,2,"blue") can be added

        >>> G=nx.MultiDiGraph()
        >>> G.add_edge(1,2,"blue")

        Two successive calls to G.add_edge(1, 2, "red") will result in 2 edges
        of the form (1, 2, "red") that can be distinguished from one another by
        their keys.

        >>> g = networkx.MultiDiGraph()
        >>> g.add_edge(1, 2, "red") # key internally assigned
        >>> g.add_edge(1, 2, "red") # key internally assigned
        >>> g.edges()
        [(1, 2), (1, 2)]
        >>> g.edges(keys=True, data=True)
        [(1, 2, 0, 'red'), (1, 2, 1, 'red')]

        See Also
        --------
        DiGraph.add_edge : the DiGraph class does *not* allow parallel 
        directed edges
        """
        # add nodes
        if u not in self.succ:
            self.succ[u] = {}
            self.pred[u] = {}
        if v not in self.succ:
            self.succ[v] = {}
            self.pred[v] = {}
        # add data to the list of edgedata between u and v
        datalist = [data]
        if v in self.succ[u]:
            datadict=self.adj[u][v]
            if key is None:
                # find a unique integer key
                # other methods might be better here?
                key=0
                while key in datadict:
                    key+=1
            datadict[key]=data
        else:
            # selfloops work this way without special treatment
            if key is None:
                key=0
            datadict={key:data}
            self.succ[u][v] = datadict
            self.pred[v][u] = datadict

    def remove_edge(self, u, v, key=None):
        """Remove the directed edge (u,v).

        If key is specified, only remove the first edge found with the given
        key. If key is None, remove all edges between u and v.

        Parameters
        ----------
        u, v : nodes
            Nodes can be any hashable Python objects such as strings or
            numbers, but None is not allowed as a node object. The order of
            u and v specifies the direction of the edge. In this case, the
            method removes a directed edge from u to v.

        key : any hashable Python object (default: None)
            A key associated with a directed edge can be any arbitrary Python
            object. It is used for distinguishing between directed edges with
            the same nodes. If more than one directed edge share the same pair
            of nodes, then the keys associated with those edges must each be
            unique.

        Examples
        --------
        Remove the edge with a specified key.

        >>> g = networkx.MultiDiGraph()
        >>> g.add_edge(1, 2)
        >>> g.add_edge(1, 2, "arbitrary data")
        >>> g.edges(data=True, keys=True)
        [(1, 2, 0, 1), (1, 2, 1, 'arbitrary data')]
        >>> g.remove_edge(1, 2, key=0)
        >>> g.edges(data=True, keys=True)
        [(1, 2, 1, 'arbitrary data')]

        Remove all parallel edges between a pair of nodes.

        >>> g = networkx.MultiDiGraph()
        >>> g.add_edge(1, 2)
        >>> g.add_edge(1, 2, "too much data")
        >>> g.add_edge(1, 2, "some data")
        >>> g.add_edge(3, 4, "very little data")
        >>> g.edges(data=True, keys=True)
        [(1, 2, 0, 1), (1, 2, 1, 'too much data'), (1, 2, 2, 'some data'), (3, 4, 0, 'very little data')]
        >>> g.remove_edge(1, 2)
        >>> g.edges(data=True, keys=True)
        [(3, 4, 0, 'very little data')]

        See Also
        --------
        DiGraph.remove_edge : the DiGraph class does *not* allow parallel edges
        """
        if key is None:
            super(MultiDiGraph,self).remove_edge(u,v)
        else:
            try:
                d=self.adj[u][v]
                # remove the edge with specified key
                del d[key]
                if len(d)==0:
                    # remove the key entries if last edge
                    del self.succ[u][v]
                    del self.pred[v][u]
            except (KeyError,ValueError):
                raise NetworkXError(
                    "edge %s-%s with key %s not in graph"%(u,v,key))

    delete_edge = remove_edge


    def edges_iter(self, nbunch=None, data=False, keys=False):
        """Return an iterator over the edges.

        Parameters
        ----------
        nbunch : list, iterable (default: None)
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return all edges in the 
            multidigraph. Nodes in nbunch that are not in the multidigraph
            will be (quietly) ignored.

        data : bool (default: False)
            Return 2-tuples (u,v) (False) or 3-tuples (u,v,data) (True). If
            both of the arguments data and keys are True, then return
            4-tuples (u,v,key,data).

        keys : bool (default: False)
            Return 2-tuples (u,v) (False) or 3-tuples (u,v,key) (True). If
            both of the arguments data and keys are True, then return
            4-tuples (u,v,key,data).

        Returns
        --------
        Edges that have nodes in nbunch as start nodes, or a list of all
        edges if nbunch is not specified. If (u,v) is a directed edge of this
        multidigraph, then u is the start node and v is the end node.

        Examples
        --------
        Get all the edges of a multidigraph.

        >>> g = networkx.MultiDiGraph()
        >>> nbunch = [(1, 2), (1, 2, "some data"), (3, 2)]
        >>> g.add_edges_from(nbunch)
        >>> list(g.edges_iter())  # get all edges
        [(1, 2), (1, 2), (3, 2)]
        >>> [e for e in g.edges_iter()]  # another way to get the edges
        [(1, 2), (1, 2), (3, 2)]
        >>> g.edges()  # recommended way to get all the edges
        [(1, 2), (1, 2), (3, 2)]

        Get all edges with the specified start nodes.

        >>> g = networkx.MultiDiGraph()
        >>> nbunch = [(1, 2), (1, 2, "some data"), (3, 2), (4, 3), (5, 3)]
        >>> g.add_edges_from(nbunch)
        >>> g.edges()
        [(1, 2), (1, 2), (3, 2), (4, 3), (5, 3)]
        >>> ebunch = [1, 3, 5]  # get the edges having these start nodes
        >>> list(g.edges_iter(ebunch))
        [(1, 2), (1, 2), (3, 2), (5, 3)]

        See Also
        --------
        in_edges_iter : return edges with specified end nodes
        DiGraph.edges_iter : the DiGraph class does *not* allow parallel edges
        """
        if nbunch is None:
            nodes_nbrs = self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    for key,data in datadict.iteritems():
                        if keys:
                            yield (n,nbr,key,data)
                        else:
                            yield (n,nbr,data)
        else:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    for key,data in datadict.iteritems():
                        if keys:
                            yield (n,nbr,key)
                        else:
                            yield (n,nbr)

    # alias out_edges to edges
    out_edges_iter=edges_iter

    def in_edges_iter(self, nbunch=None, data=False, keys=False):
        """Return an iterator over the edges.

        Parameters
        ----------
        nbunch : list, iterable (default: None)
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return all edges in the 
            multidigraph. Nodes in nbunch that are not in the multidigraph
            will be (quietly) ignored.

        data : bool (default: False)
            Return 2-tuples (u,v) (False) or 3-tuples (u,v,data) (True). If
            both of the arguments data and keys are True, then return
            4-tuples (u,v,key,data).

        keys : bool (default: False)
            Return 2-tuples (u,v) (False) or 3-tuples (u,v,key) (True). If
            both of the arguments data and keys are True, then return
            4-tuples (u,v,key,data).

        Returns
        --------
        Edges that have nodes in nbunch as end nodes, or a list of all
        edges if nbunch is not specified. If (u,v) is a directed edge of this
        multidigraph, then u is the start node and v is the end node.

        Examples
        --------
        Get all the edges.

        >>> nbunch = [(1, 2), (1, 2), (3, 2), (4, 3), (5, 3)]
        >>> g = networkx.MultiDiGraph()
        >>> g.add_edges_from(nbunch)
        >>> g.edges()  # recommended way to get all the edges
        [(1, 2), (1, 2), (3, 2), (4, 3), (5, 3)]
        >>> list(g.in_edges_iter())  # another way to get the edges
        [(1, 2), (1, 2), (3, 2), (4, 3), (5, 3)]
        >>> [e for e in g.in_edges_iter()]  # still another way
        [(1, 2), (1, 2), (3, 2), (4, 3), (5, 3)]

        Get only the edges with specified end nodes.

        >>> nbunch = [(1, 2), (1, 2, "some data"), (3, 2), (4, 3), (5, 3)]
        >>> g = networkx.MultiDiGraph()
        >>> g.add_edges_from(nbunch)
        >>> g.edges()
        [(1, 2), (1, 2), (3, 2), (4, 3), (5, 3)]
        >>> ebunch = [3, 5]  # get the edges having these end nodes
        >>> list(g.in_edges_iter(ebunch))
        [(4, 3), (5, 3)]

        See Also
        --------
        edges_iter : return edges with specified start nodes
        DiGraph.in_edges_iter :
        """
        if nbunch is None:
            nodes_nbrs=self.pred.iteritems()
        else:
            nodes_nbrs=((n,self.pred[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    for key,data in datadict.iteritems():
                        if keys:
                            yield (nbr,n,key,data)
                        else:
                            yield (nbr,n,data)
        else:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    for key,data in datadict.iteritems():
                        if keys:
                            yield (nbr,n,key)
                        else:
                            yield (nbr,n)

    in_edges_iter.__doc__ = DiGraph.in_edges_iter.__doc__


    def degree_iter(self, nbunch=None, weighted=False):
        """Return an iterator for (node, degree).

        The node degree is the number of edges adjacent to that node.

        Parameters
        ----------
        nbunch : list, iterable (default: None)
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return the degree iterator of all
            nodes in the multidigraph. Nodes in nbunch that are not in the
            multidigraph will be (quietly) ignored.

        weighted : bool (default: False)
            If the multidigraph is weighted, return the weighted degree
            (the sum of edge weights).

        Examples
        --------
        Get the degree iterator of all nodes.

        >>> ebunch = [(1, 2), (2, 1, "some data"), (3, 4), (5, 2, "more data")]
        >>> g = networkx.MultiDiGraph()
        >>> g.add_edges_from(ebunch)
        >>> list(g.degree_iter())  # get degree iterator of all nodes
        [(1, 2), (2, 3), (3, 1), (4, 1), (5, 1)]
        >>> [d for d in g.degree_iter()]  # another way
        [(1, 2), (2, 3), (3, 1), (4, 1), (5, 1)]

        Only get the degree iterator of specified nodes.

        >>> ebunch = [(1, 2), (2, 1, "some data"), (3, 4), (5, 2, "more data")]
        >>> g = networkx.MultiDiGraph()
        >>> g.add_edges_from(ebunch)
        >>> nbunch = [1, 3, 5]  # get degree iterator of nodes 1, 3, 5
        >>> list(g.degree_iter(nbunch))
        [(1, 2), (3, 1), (5, 1)]

        See Also
        --------
        in_degree_iter : degree iterator for in-edges
        out_degree_iter : degree iterator for out-edges
        DiGraph.degree_iter : the DiGraph class does *not* allow parallel edges
        """
        if nbunch is None:
            nodes_nbrs=self.succ.iteritems()
        else:
            nodes_nbrs=((n,self.succ[n]) for n in self.nbunch_iter(nbunch))

        if self.weighted and weighted:
        # edge weighted graph - degree is sum of nbr edge weights
            for n,nbrs in nodes_nbrs:
                indeg = sum([sum(data.values())
                             for data in self.pred[n].itervalues()])
                outdeg = sum([sum(data.values())
                              for data in nbrs.itervalues()])
                yield (n, indeg + outdeg  # double counted selfloop so subtract
                       - (n in nbrs and sum(nbrs[n])))
        else:
            for n,nbrs in nodes_nbrs:
                indeg = sum([len(data) for data in self.pred[n].itervalues()])
                outdeg = sum([len(data) for data in nbrs.itervalues()])
                yield (n, indeg + outdeg  # double counted selfloop so subtract
                       - (n in nbrs and len(nbrs[n])))

    degree_iter.__doc__ = DiGraph.degree_iter.__doc__

    def in_degree_iter(self, nbunch=None, weighted=False):
        """Return an iterator for (node, in-degree).

        The node in-degree is the number of edges pointing in to that node.

        Parameters
        ----------
        nbunch : list, iterable (default: None)
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return the in-degree iterator of
            all nodes in the multidigraph. Nodes in nbunch that are not in the
            multidigraph will be (quietly) ignored.

        weighted : bool (default: False)
            If the multidigraph is weighted, return the weighted in-degree
            (the sum of in-edge weights).

        Examples
        --------
        Get the in-degree iterator of all nodes.

        >>> ebunch = [(1, 2), (2, 1), (2, 3), (4, 3)]
        >>> g = networkx.MultiDiGraph()
        >>> g.add_edges_from(ebunch)
        >>> list(g.in_degree_iter())  # get in-degree interator of all nodes
        [(1, 1), (2, 1), (3, 2), (4, 0)]
        >>> [d for d in g.in_degree_iter()]  # another way
        [(1, 1), (2, 1), (3, 2), (4, 0)]

        Only get the in-degree iterator of specified nodes.

        >>> ebunch = [(1, 2), (2, 1), (2, 3), (4, 3)]
        >>> g = networkx.MultiDiGraph()
        >>> g.add_edges_from(ebunch)
        >>> nbunch = [1, 3]  # get in-degree iterator for nodes 1, 3
        >>> list(g.in_degree_iter(nbunch))
        [(1, 1), (3, 2)]

        See Also
        --------
        degree_iter : degree iterator for nodes
        out_degree_iter : degree iterator for out-edges
        DiGraph.in_degree_iter : the DiGraph class does *not* allow parallel edges
        """
        if nbunch is None:
            nodes_nbrs=self.pred.iteritems()
        else:
            nodes_nbrs=((n,self.pred[n]) for n in self.nbunch_iter(nbunch))

        if self.weighted and weighted:
        # edge weighted graph - degree is sum of nbr edge weights
            for n,nbrs in nodes_nbrs:
                yield (n, sum([sum(data.values())
                               for data in nbrs.itervalues()]) )
        else:
            for n,nbrs in nodes_nbrs:
                yield (n, sum([len(data) for data in nbrs.itervalues()]) )

    in_degree_iter.__doc__ = DiGraph.in_degree_iter.__doc__

    def out_degree_iter(self, nbunch=None, weighted=False):
        """Return an iterator for (node, out-degree).

        The node out-degree is the number of edges pointing out of that node.

        Parameters
        ----------
        nbunch : list, iterable (default: None)
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. If nbunch is None, return the out-degree iterator of
            all nodes in the multidigraph. Nodes in nbunch that are not in the
            multidigraph will be (quietly) ignored.

        weighted : bool (default: False)
            If the multidigraph is weighted, return the weighted out-degree
            (the sum of out-edge weights).

        Examples
        --------
        Get the out-degree iterator of all nodes.

        >>> ebunch = [(1, 2), (2, 1), (2, 3), (4, 3)]
        >>> g = networkx.MultiDiGraph()
        >>> g.add_edges_from(ebunch)
        >>> list(g.out_degree_iter())  # get out-degree iterator of all nodes
        [(1, 1), (2, 2), (3, 0), (4, 1)]
        >>> [d for d in g.out_degree_iter()]  # another way
        [(1, 1), (2, 2), (3, 0), (4, 1)]

        Only get the out-degree iterator of specified nodes.

        >>> ebunch = [(1, 2), (2, 1), (2, 3), (4, 3)]
        >>> g = networkx.MultiDiGraph()
        >>> g.add_edges_from(ebunch)
        >>> nbunch = [2, 4]  # get out-degree iterator for nodes 2, 4
        >>> list(g.out_degree_iter(nbunch))
        [(2, 2), (4, 1)]

        See Also
        --------
        degree_iter : degree iterator for nodes
        in_degree_iter : degree iterator for in-edges
        DiGraph.out_degree_iter : the DiGraph class does *not* allow parallel edges
        """
        if nbunch is None:
            nodes_nbrs=self.succ.iteritems()
        else:
            nodes_nbrs=((n,self.succ[n]) for n in self.nbunch_iter(nbunch))

        if self.weighted and weighted:
        # edge weighted graph - degree is sum of nbr edge weights
            for n,nbrs in nodes_nbrs:
                yield (n, sum([sum(data.values())
                               for data in nbrs.itervalues()]) )
        else:
            for n,nbrs in nodes_nbrs:
                yield (n, sum([len(data) for data in nbrs.itervalues()]) )

    out_degree_iter.__doc__ = DiGraph.out_degree_iter.__doc__

    def subgraph(self, nbunch, copy=True):
        """Return the subgraph induced on nodes in nbunch.

        Parameters
        ----------
        nbunch : list, iterable 
            A container of nodes that will be iterated through once (thus it
            should be an iterator or be iterable). Each element of the
            container should be a valid node type, i.e. any hashable type
            except None. Nodes in nbunch that are not in the multidigraph will
            be (quietly) ignored.

        copy : bool (default: True)
            If True then return a new multidigraph holding the subgraph.
            Otherwise, the subgraph is created in the original multidigraph by
            deleting nodes not in nbunch. Warning: this can destroy the
            multidigraph.

        Examples
        --------
        >>> ebunch = [(1, 2), (1, 1), (1, 2), (3, 2), (4, 4), (4, 4)]
        >>> g = networkx.MultiDiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.edges()
        [(1, 1), (1, 2), (1, 2), (3, 2), (4, 4), (4, 4)]
        >>> nbunch = [1, 2, 3]
        >>> sg = g.subgraph(nbunch)  # get subgraph induced by nodes 1, 2, 3
        >>> sg.edges()
        [(1, 1), (1, 2), (1, 2), (3, 2)]

        See Also
        --------
        DiGraph.subgraph : the DiGraph class does *not* allow parallel edges
        """
        bunch = set(self.nbunch_iter(nbunch))
        if not copy:
            # demolish all nodes (and attached edges) not in nbunch
            self.remove_nodes_from([n for n in self if n not in bunch])
            self.name = "Subgraph of (%s)"%(self.name)
            return self
        else:
            # create new graph and copy subgraph into it
            H = self.__class__()
            H.name = "Subgraph of (%s)"%(self.name)
            H.add_nodes_from(bunch)
            # add edges
            H_succ=H.succ       # store in local variables
            H_pred=H.pred
            self_succ=self.succ
            self_pred=self.pred
            for n in bunch:
                for u,d in self_succ[n].iteritems():
                    if u in bunch:
                        data=d.copy() # copy of edge data dict
                        H_succ[n][u]=data
                        H_pred[u][n]=data
            return H

    subgraph.__doc__ = DiGraph.subgraph.__doc__


    def to_undirected(self):
        """Return an undirected representation of the multidigraph.

        A new multidigraph is returned with the same name and nodes and
        with edge (u,v,data) if either (u,v,data) or (v,u,data)
        is in the multidigraph.  If both edges exist in the multidigraph, they
        appear as a double edge in the new multidigraph.

        Examples
        --------
        >>> ebunch = [(1, 2), (1, 1), (2, 1), (3, 2), (4, 4)]
        >>> g = networkx.MultiDiGraph()
        >>> g.add_edges_from(ebunch)
        >>> g.edges()
        [(1, 1), (1, 2), (2, 1), (3, 2), (4, 4)]
        >>> ug = g.to_undirected()  # get the undirected representation
        >>> ug.edges()
        [(1, 1), (1, 2), (2, 3), (4, 4)]
        """
        H=MultiGraph()
        H.name=self.name
        H.add_nodes_from(self)
        H.add_edges_from( ((u,v,data,key)
                           for u,nbrs in self.adjacency_iter()
                           for v,datadict in nbrs.iteritems()
                           for key,data in datadict.items()))
        return H


    def copy(self):
        """Return a copy of the multidigraph.

        Notes
        -----
        This makes a complete copy of the multidigraph, but does not make
        copies of any underlying node or edge data.  The node and edge data
        in the copy still point to the same objects as in the original.

        Examples
        --------
        >>> ebunch = [(1, 2), (2, 1), (3, 2), (4, 4)]
        >>> g = networkx.MultiDiGraph()
        >>> g.add_edges_from(ebunch)
        >>> cg = g.copy()
        >>> g.edges()
        [(1, 2), (2, 1), (3, 2), (4, 4)]
        >>> cg.edges()
        [(1, 2), (2, 1), (3, 2), (4, 4)]
        >>> cg == g
        False
        """
        H=self.__class__()
        H.name=self.name
        H.succ={}
        H.pred={}
        H.adj=H.succ
        for u,nbrs in self.adjacency_iter():
            H.succ[u]={}
            for v,d in nbrs.iteritems():
                data=d.copy()
                H.succ[u][v]=data
                if not v in H.pred:
                    H.pred[v]={}
                H.pred[v][u]=data
        return H

    to_directed=copy

