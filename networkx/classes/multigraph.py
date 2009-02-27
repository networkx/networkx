"""
Base class for MultiGraph.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""

#    Copyright (C) 2004-2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

from networkx.classes.graph import Graph
from networkx import NetworkXException, NetworkXError
import networkx.convert as convert


class MultiGraph(Graph):
    """
    An undirected graph that allows multiple (parallel) edges with arbitrary 
    data on the edges.

    Subclass of Graph.

    An empty multigraph is created with

    >>> G=nx.MultiGraph()

    
    Examples
    ========

    Create an empty graph structure (a "null graph") with no nodes and no edges
    
    >>> G=nx.MultiGraph()  

    You can add nodes in the same way as the simple Graph class
    >>> G.add_nodes_from(xrange(100,110))

    You can add edges with data/labels/objects as for the Graph class, 
    but here the same two nodes can have more than one edge between them.

    >>> G.add_edges_from([(1,2,0.776),(1,2,0.535)])

    To distinguish between two edges connecting the same nodes you
    can use a key attribute
    
    >>> G.add_edges_from([(1,2,0.776,'first'),(1,2,0.535,'second')])

    See also the MultiDiGraph class for a directed graph version.

    MultiGraph inherits from Graph, overriding the following methods:

    - add_edge
    - add_edges_from
    - remove_edge
    - remove_edges_from
    - has_edge
    - edges_iter
    - get_edge
    - degree_iter
    - selfloop_edges
    - number_of_selfloops
    - number_of_edges
    - to_directed
    - subgraph
    - copy

    """
    multigraph=True
    directed=False

    def add_edge(self, u, v, data=1, key=None):  
        if u not in self.adj: 
            self.adj[u] = {}
        if v not in self.adj: 
            self.adj[v] = {}
        if v in self.adj[u]:
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
            self.adj[u][v] = datadict
            self.adj[v][u] = datadict

    add_edge.__doc__ = Graph.add_edge.__doc__

    def add_edges_from(self, ebunch, data=1):  
        for e in ebunch:
            ne=len(e)
            if ne==4:
                u,v,d,k = e                
            elif ne==3:
                u,v,d = e
                k=None
            elif ne==2:
                u,v = e  
                d = data
                k=None
            else: 
                raise NetworkXError(
                    "Edge tuple %s must be a 2-tuple or 3-tuple."%(e,))
            self.add_edge(u,v,data=d,key=k)                

    add_edges_from.__doc__ = Graph.add_edges_from.__doc__

    def remove_edge(self, u, v, key=None):
        """Remove the edge between (u,v).

        If key is not specified remove all edges between u and v.
        """
        if key is None: 
            super(MultiGraph, self).remove_edge(u,v)
        else:
            try:
                d=self.adj[u][v]
                # remove the edge with specified data
                del d[key]
                if len(d)==0: 
                    # remove the key entries if last edge
                    del self.adj[u][v]
                    del self.adj[v][u]
            except (KeyError,ValueError): 
                raise NetworkXError(
                    "edge %s-%s with key %s not in graph"%(u,v,key))

    delete_edge = remove_edge            

    def remove_edges_from(self, ebunch): 
        for e in ebunch:
            u,v = e[:2]
            if u in self.adj and v in self.adj[u]:
                try:
                    key=e[2]
                except IndexError:
                    key=None
                self.remove_edge(u,v,key=key)

    remove_edges_from.__doc__ = Graph.remove_edges_from.__doc__
    delete_edges_from = remove_edges_from            

    def has_edge(self, u, v, key=None):
        try:
            if key is None:
                return v in self.adj[u]
            else:
                return key in self.adj[u][v]
        except KeyError:
            return False

#    has_edge.__doc__ = Graph.has_edge.__doc__

    def edges(self, nbunch=None, data=False, keys=False):
        return list(self.edges_iter(nbunch, data=data,keys=keys))

    def edges_iter(self, nbunch=None, data=False, keys=False):
        seen={}     # helper dict to keep track of multiply stored edges
        if nbunch is None:
            nodes_nbrs = self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
        if data:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    if nbr not in seen:
                        for key,data in datadict.iteritems():
                            if keys:
                                yield (n,nbr,key,data)
                            else:
                                yield (n,nbr,data)
                seen[n]=1
        else:
            for n,nbrs in nodes_nbrs:
                for nbr,datadict in nbrs.iteritems():
                    if nbr not in seen:
                        for key,data in datadict.iteritems():
                            if keys:
                                yield (n,nbr,key)
                            else:
                                yield (n,nbr)

                seen[n] = 1
        del seen

    edges_iter.__doc__ = Graph.edges_iter.__doc__

    def get_edge_data(self, u, v, key=None, default=None):
        """Return the data associated with the edge (u,v).

        For multigraphs this returns a list with data for all edges
        (u,v).  Each element of the list is data for one of the 
        edges. 

        Parameters
        ----------
        u,v : nodes

        default:  any Python object            
            Value to return if the edge (u,v) is not found.
            The default is the Python None object.

        Notes
        -----
        It is faster to use G[u][v].

        """
        try:
            if key is None:
                return self.adj[u][v]
            else:
                return self.adj[u][v][key]
        except KeyError:
            return default

    def degree_iter(self, nbunch=None, weighted=False):
        if nbunch is None:
            nodes_nbrs = self.adj.iteritems()
        else:
            nodes_nbrs=((n,self.adj[n]) for n in self.nbunch_iter(nbunch))
  
        if self.weighted and weighted:                        
        # edge weighted graph - degree is sum of nbr edge weights
            for n,nbrs in nodes_nbrs:
                deg = sum([sum(data) for data in nbrs.itervalues()])
                yield (n, deg+(n in nbrs and sum(nbrs[n])))
        else:
            for n,nbrs in nodes_nbrs:
                deg = sum([len(data) for data in nbrs.itervalues()])
                yield (n, deg+(n in nbrs and len(nbrs[n])))

    degree_iter.__doc__ = Graph.degree_iter.__doc__

    def selfloop_edges(self,data=False):
        """Return a list of selfloop edges"""
        if data:
            return [ (n,n,d) 
                     for n,nbrs in self.adj.iteritems() 
                     if n in nbrs for d in nbrs[n].values()]
        else:
            return [ (n,n)
                     for n,nbrs in self.adj.iteritems() 
                     if n in nbrs for d in nbrs[n].values()]



    def number_of_selfloops(self):
        """Return the number of selfloop edges counting multiple edges."""
        return len(self.selfloop_edges())


    def number_of_edges(self, u=None, v=None):
        if u is None: return self.size()
        try:
            edgedata=self.adj[u][v]
        except KeyError:
            return 0 # no such edge
        return len(edgedata)

    number_of_edges.__doc__ = Graph.number_of_edges.__doc__

    def subgraph(self, nbunch, copy=True):
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
            # add edges
            H_adj = H.adj # cache
            self_adj = self.adj # cache
            for n in bunch:
                H_adj[n] = dict([(u,d.copy()) 
                                 for u,d in self_adj[n].iteritems() 
                                 if u in bunch])
            return H

    subgraph.__doc__ = Graph.subgraph.__doc__

    def to_directed(self):
        """Return a directed representation of the graph.

        A new multidigraph is returned with the same name, same nodes and
        with each edge (u,v,data) replaced by two directed edges
        (u,v,data) and (v,u,data).
      
        """
        from multidigraph import MultiDiGraph
        G=MultiDiGraph()
        G.add_nodes_from(self)
        G.add_edges_from( ((u,v,data,key) 
                           for u,nbrs in self.adjacency_iter() 
                           for v,datadict in nbrs.iteritems() 
                           for key,data in datadict.items()))
        return G

    def copy(self):
        """Return a copy of the graph.

        Notes
        -----
        This makes a complete of the graph but does not make copies
        of any underlying node or edge data.  The node and edge data
        in the copy still point to the same objects as in the original.
        """
        H=self.__class__()
        H.name=self.name
        H.adj={}
        for u,nbrs in self.adjacency_iter():
            H.adj[u]={}
            for v,d in nbrs.iteritems():
                H.adj[u][v]=d.copy()
        return H



if __name__ == '__main__':

    G=MultiGraph()
    G.add_edge(1,2) 
    G.add_edge(1,2,'data0')
    G.add_edge(1,2,data='data1',key='key1')
    G.add_edge(1,2,'data2','key2')
    print G.edges()
    print G.edges(data=True)
    print G.edges(keys=True)
    print G.edges(data=True,keys=True)
    print G[1][2]
    print G[1][2]['key1']
    G[1][2]['key1']='spam' # OK to set here
    print G[1][2]['key1']
    print G.edges(data=True)
    print G[1][2].keys()
