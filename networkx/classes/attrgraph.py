# Experimental prototype of graph class that uses dictionaries
# for graph, node and edge attributes

__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
#    Copyright (C) 2009 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from graph import Graph
from digraph import DiGraph
from multigraph import  MultiGraph
from multidigraph import  MultiDiGraph
from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert

class AttrGraph(Graph):
    def __init__(self, data=None, name='', weighted=False):
        # dictionary for graph attributes
        self.graph = defaultdict(dict)
        if hasattr(data,'graph') and isinstance(data.graph,dict):
            self.graph.update(data.graph)
        # dictionary for node attributes
        self.node = defaultdict(dict)
        if hasattr(data,'node') and isinstance(data.node,dict):
            self.node.update(data.node)
        self.adj = {}  # empty adjacency hash
        super(AttrGraph,self).__init__(data,name,weighted)
        # edge attributes are stored as edge data
        # alias e.g G.edge[u][v] = G[u][v]
        self.edge=self.adj


    # nodes and node attributes        
    def add_node(self, n, **attr):
        # add single node
        super(AttrGraph,self).add_node(n)
        # with attributes
        if attr is not None:
            self.node[n].update(attr)

    def add_nodes_from(self, nbunch, **attr):
        # add multiple nodes, all with same attributes
        for n in nbunch:
            self.add_node(n,**attr)
        
    def remove_node(self, n):
        # remove node
        super(AttrGraph,self).remove_node(n)
        # and attributes
        try:
            del self.node[n]
        except KeyError:
            pass

    def remove_nodes_from(self, nbunch):
        for n in nbunch:
            try:
                self.remove_node(n)
            except NetworkXError:
                pass

    def nodes_iter(self, nbunch=None, data=False):
        # data keyword True|False to return attribute dict
        if nbunch is None:
            nbunch=self.adj.iterkeys()
        else:
            nbunch=self.nbunch_iter(nbunch)
        if data:
            for n in nbunch:
                nattr=self.node.get(n,None)
                yield (n,nattr)
        else:
            for n in nbunch:            
                yield n

    def nodes(self, nbunch=None, data=False):
        # data keyword True|False to return attribute dict
        if data:    
            return dict(self.nodes_iter(nbunch,data))
        else:       
            return list(self.nodes_iter(nbunch))

    # edges 
    def add_edge(self, u, v, data=None, **attr):  
        # would be more clear to use "weight" instead of "data" 
        if G.weighted:
            # weighted graph, use data as edge data
            if data is None: 
                data=1
        else:
            # dictionary as edge data
            data={}            
            if attr is not None:
                data.update(attr)
            if data is not None:
                data['weight']=data
        super(AttrGraph,self).add_edge(u,v,data=data)

    def add_edges_from(self, ebunch, **attr):  
         for e in ebunch:
             self.add_edge(*e,**attr)

    def clear(self):
        super(AttrGraph,self).clear()
        # clear node and graph attributes
        self.graph=defaultdict(dict)
        self.node=defaultdict(dict)

    def subgraph(self, nbunch, copy=True):
        H=super(AttrGraph,self).subgraph(nbunch, copy)
        # copy node and graph attributes
        H.node=dict( (k,v) for k,v in self.node.items() if k in H)
        H.graph=dict( (k,v) for k,v in self.graph.items())
        return H

    def to_directed(self):
        H=super(AttrGraph,self).to_directed()
        # copy node and graph attributes
        H.node=dict( (k,v) for k,v in self.node.items() if k in H)
        H.graph=dict( (k,v) for k,v in self.graph.items())
        return H

    def to_weighted(self,weight='weight'):
        H=Graph(weighted=True)
        H.add_nodes_from(self)
        for u,nbrs in self.adjacency_iter():
            for v,data in nbrs.iteritems():
                d=data.get(weight,1) # get key or if missing set to 1
                H.add_edge(u,v,d)
        return H


class AttrDiGraph(AttrGraph,DiGraph):

    def to_weighted(self,weight='weight'):
        H=DiGraph(weighted=True)
        H.add_nodes_from(self)
        for u,nbrs in self.adjacency_iter():
            for v,data in nbrs.iteritems():
                d=data.get(weight,1) # get key or if missing set to 1
                H.add_edge(u,v,d)
        return H


# wait for updated MultiGraph and MultiDiGraph
class AttrMultiGraph(AttrGraph,MultiGraph):

    # These methods are needed to handle the 'key' argument for MultiGraph
    # edges 
    def add_edge(self, u, v, data=None, key=None, **attr):  
        if G.weighted:
            # weighted graph, use data as edge data
            if data is None: 
                data=1
            else:
                data=data
        else:
            data={}            
            if attr is not None:
                data.update(attr)
            if data is not None:
                data['weight']=data
        super(AttrGraph,self).add_edge(u,v,data=data,key=key)


    def to_weighted(self,weight='weight'):
        H=MultiGraph(weighted=True)
        H.add_nodes_from(self)
        for u,nbrs in self.adjacency_iter():
            for v,datadict in nbrs.iteritems():
                for key,data in datadict.items():
                    d=data.get(weight,1) # get key or if missing set to 1
                    H.add_edge(u,v,d)
        return H

        

class AttrMultiDiGraph(AttrMultiGraph,AttrGraph,MultiDiGraph):

    def to_weighted(self,weight='weight'):
        H=MultiDiGraph(weighted=True)
        H.add_nodes_from(self)
        for u,nbrs in self.adjacency_iter():
            for v,datadict in nbrs.iteritems():
                for key,data in datadict.items():
                    d=data.get(weight,1) # get key or if missing set to 1
                    H.add_edge(u,v,d)
        return H


# until we require python2.5 fall back to pure Python defaultdict 
# from http://code.activestate.com/recipes/523034/
try:
    from collections import defaultdict
except:
    class defaultdict(dict):
        def __init__(self, default_factory=None, *a, **kw):
            if (default_factory is not None and
                not hasattr(default_factory, '__call__')):
                raise TypeError('first argument must be callable')
            dict.__init__(self, *a, **kw)
            self.default_factory = default_factory
        def __getitem__(self, key):
            try:
                return dict.__getitem__(self, key)
            except KeyError:
                return self.__missing__(key)
        def __missing__(self, key):
            if self.default_factory is None:
                raise KeyError(key)
            self[key] = value = self.default_factory()
            return value
        def __reduce__(self):
            if self.default_factory is None:
                args = tuple()
            else:
                args = self.default_factory,
            return type(self), args, None, None, self.items()
        def copy(self):
            return self.__copy__()
        def __copy__(self):
            return type(self)(self.default_factory, self)
        def __deepcopy__(self, memo):
            import copy
            return type(self)(self.default_factory,
                              copy.deepcopy(self.items()))
        def __repr__(self):
            return 'defaultdict(%s, %s)' % (self.default_factory,
                                            dict.__repr__(self))


if __name__ == '__main__':

    G=AttrGraph()

    # graph attributes
    G.graph['foo']='bar'
    print G.graph['foo']
    del G.graph['foo']
    print G.graph

    # node attributes
    G.add_node(1,foo='bar')
    print G.nodes()
    print G.nodes(data=True)
    G.node[1]['foo']='baz' # another way to set attribute
    print G.nodes(data=True)

    # edge attributes
    G.add_edge(1,2,foo='bar')
    print G.edges()
    print G.edges(data=True)
    # edge 3-4 and 4-5 get same attribute
    G.add_edges_from(((3,4),(4,5)),foo='foo')
    print G.edges(data=True)
    G.remove_edge(1,2)
    G.add_edge(1,2,data=7,foo='bar',bar='foo')
    print G.edges(data=True)
    G[1][2]['data']=10 # OK to set data like this
    print G.edges(data=True)
    G.edge[1][2]['data']=20 # another spelling, "edge"
    G.edge[1][2]['listdata']=[20,200] 
    G.edge[1][2]['weight']=20 
    print G.edges(data=True)
    H=G.to_weighted()
    print H.edges(data=True)
    print 

    G=AttrGraph(weighted=True)
    # edge attributes
    G.add_edge(1,2,foo='bar')
    print G.edges()
    print G.edges(data=True)
    # edge 3-4 and 4-5 get same attribute
    G.add_edges_from(((3,4),(4,5)),foo='foo')
    print G.edges(data=True)
    G.remove_edge(1,2)
    G.add_edge(1,2,data=7,foo='bar',bar='foo')
    print G.edges(data=True)
    G[1][2]=10 # still not OK to set data like this!
    print G.edges(data=True)
    
