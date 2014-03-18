# -*- coding: utf-8 -*-


"""
===============
NetworkX-Matrix
===============

:Author:
    Moritz E. Beber <moritz.beber@gmail.com>
    Aric Hagberg <hagberg@lanl.gov>
    Dan Schult <dschult@colgate.edu>
    Pieter Swart <swart@lanl.gov>
:Date:
    2014-03-18
:Copyright:
    Copyright |c| 2004-2010 by
    Aric Hagberg <hagberg@lanl.gov>
    Dan Schult <dschult@colgate.edu>
    Pieter Swart <swart@lanl.gov>
    All rights reserved.
    See LICENSE.rst and the LICENSES folder for detailed information.
    Copyright |c| 2014, Moritz E. Beber, all rights reserved.
:File:
    __init__.py

.. |c| unicode:: U+A9
"""


# SparseGraph: A NetworkX graph class that uses scipy.sparse as data storage

# Possible use cases: want more compact storage than NetworkX dict-of-dicts,
# want access to scipy graph algorithms.

# Current features and limitations
# - Initializes a fixed maximum order n of graph (settable, default= 1000)
# - Nodes must be integers in [0,n-1]
# - Can use lil, csc, csr, dok sparse formats (on init)
# - Stores node attributes
# - Uses the matrix entry value as the edge attribute "weight". Weight 1 and 0 
#   are special (0 = no edge, 1 = no weight attribute reported).
# - No edge attributes (other than 'weight') are stored
# - Interface is very beta - probably doesn't work with all algorithms
# - Access scipy adjacency matrix as SparseGraph.matrix

from collections import MutableMapping
import networkx as nx
from networkx.classes.graph import Graph
from networkx.exception import NetworkXError
# import networkx.convert as convert
import scipy
from scipy import sparse

__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>'])

# class that acts like an adjacency dict for a single node
# see __getitem__() and adj()
class Adjacency(MutableMapping):
    def __init__(self, node, matrix):
        self.node = node
        self.adjset = set(matrix[self.node,:].nonzero()[1]) # <-performance tuning here
        self.matrix = matrix
    def __getitem__(self, n):
        if n not in self.adjset:
            raise KeyError
        d = self.matrix[self.node,n]
        if d == 1:
            return {}  # makes tests pass, but could (should?) return {'weight':d}
        else:
            return {'weight':d}
    def __len__(self):
        return len(self.adjset)
    def __iter__(self):
        return iter(self.adjset)
    def __contains__(self,item):
        return self.adjset.__contains__(item)
    def __repr__(self):
        return dict((nbr,self[nbr]) for nbr in self.adjset).__repr__()
    def __setitem__(self, item, value):
        raise NotImplemented("Can't set Graph[u][v] data dict directly")
    def __delitem__(self, item):
        raise NotImplemented("Can't delete Graph[u][v] data dict directly")


class SparseGraph(Graph):

    def __init__(self, matrix=None, nnodes=None, format='lil',**attr):
        self.graph = {}   # dictionary for graph attributes
        # attempt to load graph with data 
        # not implemented for general data
#        if data is not None:
#            convert.to_networkx_graph(data,create_using=self)
        if matrix is None:
            if nnodes is None:
                nnodes=1000
            if format=='lil':
                self.matrix = sparse.lil_matrix((nnodes,nnodes))
            elif format=='csr':
                self.matrix = sparse.csr_matrix((nnodes,nnodes))
            elif format=='csc':
                self.matrix = sparse.csc_matrix((nnodes,nnodes))
            elif format=='dok':
                self.matrix = sparse.dok_matrix((nnodes,nnodes))
            else:
                raise NetworkXError('%s format matrices not supported, ',
                                    'convert to one of lil,csr,csc,dok')
            self.node = {} # used to keep track of "live" nodes as well as node attrs
        else:
            self.matrix = matrix
            self.node = dict((n,{}) for n in range(matrix.shape[0]))
        self.graph.update(attr)

    def __getitem__(self, n):
        if n in self.node:
            return Adjacency(n, self.matrix)
        else:
            raise KeyError("The node %s is not in the graph."%(n,))

    @property
    def adj(self):
        return dict((n,Adjacency(n, self.matrix)) for n in self.node)

    @property
    def edge(self):
        return dict((n,Adjacency(n, self.matrix)) for n in self.node)

    def add_node(self, n, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        if not (isinstance(n,int) or issubclass(type(n),scipy.integer)):
            raise NetworkXError("SparseGraph nodes must be integers")
        if n < 0 or n >= self.matrix.shape[0]:
            raise NetworkXError("Matrix storage exceeded %d > %d"%
                                (n,self.matrix.shape[0]-1))
        if n not in self.node:
            self.node[n] = attr_dict
        else: # update attr even if node already exists
            self.node[n].update(attr_dict)

    def add_nodes_from(self, nodes, **attr):
        for n in nodes:
            try:
                newnode = n not in self.node
            except TypeError:
                nn,ndict = n
                if nn not in self.node:
                    newdict = attr.copy()
                    newdict.update(ndict)
                    self.node[nn] = newdict
                else:
                    olddict = self.node[nn]
                    olddict.update(attr)
                    olddict.update(ndict)
                continue
            if newnode:
                if not isinstance(n,int):
                    raise NetworkXError("SparseGraph nodes must be integers")

                if n < 0 or n > self.matrix.shape[0]:
                    raise NetworkXError("Matrix storage exceeded %d > %d"%
                                        (n,self.matrix.shape[0]))

                self.node[n] = attr.copy()
            else:
                self.node[n].update(attr)

    def remove_node(self,n):
        if n in self.node:
            self.remove_edges_from(self.edges(n))
            del self.node[n]
        else:
            raise NetworkXError("The node %s is not in the graph."%(n,))


    def remove_nodes_from(self, nodes):
        for n in nodes:
            if n in self.node:
                self.remove_edges_from(self.edges(n))
                del self.node[n]

    def add_edge(self, u, v, attr_dict=None, **attr):
        # set up attribute dictionary
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        # add nodes
        self.add_node(u)
        self.add_node(v)
        weight = attr_dict.get('weight',1)
        self.matrix[u,v] = weight
        self.matrix[v,u] = weight


    def add_edges_from(self, ebunch, attr_dict=None, **attr):
        # set up attribute dict
        if attr_dict is None:
            attr_dict=attr
        else:
            try:
                attr_dict.update(attr)
            except AttributeError:
                raise NetworkXError(\
                    "The attr_dict argument must be a dictionary.")
        # process ebunch
        for e in ebunch:
            ne=len(e)
            if ne==3:
                u,v,dd = e
            elif ne==2:
                u,v = e
                dd = {}
            else:
                raise NetworkXError(\
                    "Edge tuple %s must be a 2-tuple or 3-tuple."%(e,))
            # add nodes
            self.add_node(u)
            self.add_node(v)
            weight = dd.get('weight',attr_dict.get('weight',1))
            self.matrix[u,v] = weight
            self.matrix[v,u] = weight

    def remove_edge(self, u, v):
        if self.matrix[u,v] != 0:
            self.matrix[u,v] = 0
            if u != v:  # self-loop needs only one entry removed
                self.matrix[v,u] = 0
        else:
            raise NetworkXError("The edge %s-%s is not in the graph"%(u,v))


    def remove_edges_from(self, ebunch):
        for e in ebunch:
            u,v = e[:2]  # ignore edge data if present
            self.matrix[u,v] = 0
            if u != v:  # self-loop needs only one entry removed
                self.matrix[v,u] = 0

    def clear(self):
        self.name = ''
        self.adj.clear()
        self.node.clear()
        self.graph.clear()
        # create new matrix, is there a way to set all elements to zero instead?
        shape = self.matrix.shape
        matrix_class = self.matrix.__class__
        self.matrix = matrix_class(shape)

    def to_directed(self):
        raise NetworkXError("Not implemented")

    def subgraph(self, nbunch):
        # probably a more efficient way to do this with slicing?
        bunch = list(self.nbunch_iter(nbunch))
        H = self.__class__(nnodes=self.matrix.shape[0])
        H.add_nodes_from((n,self.node[n]) for n in bunch)
        for n in bunch:
            for nbr,data in self[n].items():
                if nbr in H:
                    H.add_edge(n,nbr,data)
        # copy attribute dictionaries
        H.graph=self.graph

        return H


# ideas for potentially higher performance methods

    # def degree_iter(self, nbunch=None, weight=None):
    #     if nbunch is None:
    #         nodes = self.node.keys()
    #     else:
    #         nodes = self.nbunch_iter(nbunch)

    #     if weight is None:
    #         for n in nodes:
    #             nnbrs = len(self.matrix.getrow(n).nonzero()[1])
    #             selfloop = self.matrix[n,n]!=0
    #             yield (n, nnbrs + selfloop)
    #     else:
    #         for n in nodes:
    #             nnbrs = self.matrix[n,:].sum()
    #             selfloop = self.matrix[n,n]
    #             yield (n, nnbrs + selfloop)


#    def nodes_with_selfloops(self):
#        return [ n for n in self.node if self.matrix[n,n]!=0 ]

    # def selfloop_edges(self, data=False):
    #     if data:
    #         s = []
    #         for n in self.node:
    #             d = self.matrix[n,n]
    #             if d == 0:
    #                 continue
    #             if d == 1:
    #                 s.append((n,n,{}))
    #             else:
    #                 s.append((n,n,{'weight':self.matrix[n,n]}))
    #         return s

    #         return [ (n,n,{'weight':self.matrix[n,n]})
    #                  for n in self.node if self.matrix[n,n]!=0 ]
    #     else:
    #         return [ (n,n)
    #                  for n in self.node if self.matrix[n,n]!=0 ]

    # def size(self, weight=None):
    #     if weight is None:
    #         return int(self.matrix.getnnz()/2.0)
    #     else:
    #         return self.matrix.sum()/2.0


    # def get_edge_data(self, u, v, default=None):
    #     try:
    #         d = self.matrix[u,v]
    #     except IndexError:
    #         return default
    #     if d != 0:
    #         if d ==1:
    #             return {}
    #         else:
    #             return {'weight':d}
    #     else:
    #         return default


    # def has_edge(self, u, v):
    #     return self.matrix[u,v] != 0


if __name__=='__main__':
    A = sparse.lil_matrix((4,4))
    A.setdiag([1,1,1],k=1)
    A.setdiag([1,1,1],k=-1)
    print A.todense()
    G = SparseGraph(A)
    print(G.nodes())
    print(G.edges())
    print(nx.adjacency_matrix(G))
    G = SparseGraph(nnodes=4,format='lil')
    G.add_path([0,1,2,3])
    print(G.matrix.format)
    for n in G:
        print(n)
    print(3 in G)
    print(0 in G)
    print(4 in G)
    print(len(G))
    print(G[0])
    print(G.adjacency_list())

