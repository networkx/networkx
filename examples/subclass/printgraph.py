"""
Example subclass of the Graph class.
"""
# Author: Aric Hagberg (hagberg@lanl.gov)

#    Copyright (C) 2004-2016 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
__docformat__ = "restructuredtext en"

from networkx import Graph

from networkx.exception import NetworkXException, NetworkXError
import networkx.convert as convert
from copy import deepcopy

class PrintGraph(Graph):
    """
    Example subclass of the Graph class.

    Prints activity log to file or standard output.
    """
    def __init__(self, data=None, name='', file=None, **attr):
        Graph.__init__(self, data=data,name=name,**attr)
        if file is None:
            import sys
            self.fh=sys.stdout
        else:
            self.fh=open(file,'w')

    def add_node(self, n, attr_dict=None, **attr):
        Graph.add_node(self,n,attr_dict=attr_dict,**attr)
        self.fh.write("Add node: %s\n"%n)

    def add_nodes_from(self, nodes, **attr):
        for n in nodes:
            self.add_node(n, **attr)

    def remove_node(self,n):
        Graph.remove_node(self,n)
        self.fh.write("Remove node: %s\n"%n)

    def remove_nodes_from(self, nodes):
        adj = self.adj
        for n in nodes:
            self.remove_node(n)

    def add_edge(self, u, v, attr_dict=None, **attr):
        Graph.add_edge(self,u,v,attr_dict=attr_dict,**attr)
        self.fh.write("Add edge: %s-%s\n"%(u,v))

    def add_edges_from(self, ebunch, attr_dict=None, **attr):
        for e in ebunch:
            u,v=e[0:2]
            self.add_edge(u,v,attr_dict=attr_dict,**attr)

    def remove_edge(self, u, v):
        Graph.remove_edge(self,u,v)
        self.fh.write("Remove edge: %s-%s\n"%(u,v))

    def remove_edges_from(self, ebunch):
        for e in ebunch:
            u,v=e[0:2]
            self.remove_edge(u,v)

    def clear(self):
        self.name = ''
        self.adj.clear()
        self.node.clear()
        self.graph.clear()
        self.fh.write("Clear graph\n")

    def subgraph(self, nbunch, copy=True):
        # subgraph is needed here since it can destroy edges in the
        # graph (copy=False) and we want to keep track of all changes.
        #
        # Also for copy=True Graph() uses dictionary assignment for speed
        # Here we use H.add_edge()
        bunch =set(self.nbunch_iter(nbunch))

        if not copy:
            # remove all nodes (and attached edges) not in nbunch
            self.remove_nodes_from([n for n in self if n not in bunch])
            self.name = "Subgraph of (%s)"%(self.name)
            return self
        else:
            # create new graph and copy subgraph into it
            H = self.__class__()
            H.name = "Subgraph of (%s)"%(self.name)
            # add nodes
            H.add_nodes_from(bunch)
            # add edges
            seen=set()
            for u,nbrs in self.adjacency_iter():
                if u in bunch:
                    for v,datadict in nbrs.items():
                        if v in bunch and v not in seen:
                            dd=deepcopy(datadict)
                            H.add_edge(u,v,dd)
                    seen.add(u)
            # copy node and graph attr dicts
            H.node=dict( (n,deepcopy(d))
                         for (n,d) in self.node.items() if n in H)
            H.graph=deepcopy(self.graph)
            return H



if __name__=='__main__':
    G=PrintGraph()
    G.add_node('foo')
    G.add_nodes_from('bar',weight=8)
    G.remove_node('b')
    G.remove_nodes_from('ar')
    print(G.nodes(data=True))
    G.add_edge(0,1,weight=10)
    print(list(G.edges(data=True)))
    G.remove_edge(0,1)
    G.add_edges_from(list(zip(list(range(0o3)),list(range(1,4)))),weight=10)
    print(list(G.edges(data=True)))
    G.remove_edges_from(list(zip(list(range(0o3)),list(range(1,4)))))
    print(list(G.edges(data=True)))


    G=PrintGraph()
    nx.add_path(G, range(10))
    print("subgraph")
    H1=G.subgraph(range(4), copy=False)
    H2=G.subgraph(range(4), copy=False)
    print(list(H1.edges()))
    print(list(H2.edges()))
