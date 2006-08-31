"""
EXPERIMENTAL: Base classes for trees and forests.
    
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
#

from networkx.base import Graph, DiGraph, NetworkXException, NetworkXError
import networkx.paths as paths
import networkx.convert as convert

# Yes, these aren't the natural datastructures for trees. 

class Tree(Graph):
    """ A free (unrooted) tree."""
    def __init__(self,data=None,**kwds):
        Graph.__init__(self,**kwds)
        if data is not None:
            try: # build a graph
                G=Graph()
                G=convert.from_whatever(data,create_using=G)
            except:
                raise NetworkXError, "Data %s is not a tree"%data
            # check if it is a tree.
            if G.order()==G.size()+1 and \
                   paths.number_connected_components(G)==1:
                self.adj=G.adj.copy()
                del G
            else:
                raise NetworkXError, "Data %s is not a tree"%data
             
    def add_node(self, n):
        if n in self:
            return # already in tree
        elif len(self.adj)==0:
            Graph.add_node(self,n) # first node
        else:  # not allowed
            raise NetworkXError(\
                "adding single node %s not allowed in tree"%(n))

    def add_nodes_from(self, nbunch):
        for n in nbunch:
            self.add_node(n)

    def delete_node(self, n):
        try:
            if len(self.adj[n])==1: # allowed for leaf node
                Graph.delete_node(self,n)
            else:
                raise NetworkXError(
              "deleting interior node %s not allowed in tree"%(n))
        except KeyError: # NetworkXError if n not in self
            raise NetworkXError("node %s not in graph"%n)

    def delete_nodes_from(self, nbunch):
        for n in nbunch:
            self.delete_node(n)

    def add_edge(self, u, v=None):  
        if v is None: (u,v)=u  # no v given, assume u is an edge tuple
        if self.has_edge(u,v): return # no parallel edges allowed
        elif u in self and v in self:
            raise NetworkXError("adding edge %s-%s not allowed in tree"%(u,v))
        elif u in self or v in self:
            Graph.add_edge(self,u,v)
            return
        elif len(self.adj)==0: # first leaf
            Graph.add_edge(self,u,v)            
            return
        else:
            raise NetworkXError("adding edge %s-%s not allowed in tree"%(u,v))
            
    def add_edges_from(self, ebunch):  
        for e in ebunch:
            self.add_edge(e)
            
    def delete_edge(self, u, v=None): 
        if v is None: (u,v)=u
        if self.degree(u)==1 or self.degree(v)==1: # leaf edge
            Graph.delete_edge(self,u,v)
        else: # interior edge
            raise NetworkXError(\
                  "deleting interior edge %s-%s not allowed in tree"%(u,v))
        if self.degree(u)==0:  # OK to delete remaining isolated node
            Graph.delete_node(self,u)
        if self.degree(v)==0:  # OK to delete remaining isolated node          
            Graph.delete_node(self,v)

    def delete_edges_from(self, ebunch):  
        for e in ebunch:
            self.delete_edge(e)

    # leaf notation            
    def add_leaf(self, u, v=None):  
        self.add_edge(u,v)

    def delete_leaf(self, u, v=None): 
        self.delete_edge(u,v)

    def add_leaves_from(self, ebunch):  
        for e in ebunch:
            self.add_leaf(e)

    def delete_leaves_from(self, ebunch):  
        for e in ebunch:
            self.delete_leaf(e)


class RootedTree(Tree,Graph):
    """ A rooted tree."""
    def __init__(self,root,data=None,**kwds):
        Tree.__init__(self,data=data,**kwds)
        self.root=root
        self.par={} # keep track of parent
        if data is not None: # handle input data, could be Tree, etc.
            # now root tree for this data
            self.root_tree(root)            

    # parents, use predecessors
    # children, use successors

    def delete_node(self, n):
        try:
            if len(self.adj[n])==1: # allowed for leaf node
                Graph.delete_node(self,n)
                del self.par[n]
            else:
                raise NetworkXError, \
              "deleting interior node %s not allowed in tree"%(n)
        except KeyError: # NetworkXError if n not in self
            raise NetworkXError, "node %s not in graph"%n


    def add_edge(self, u, v=None):  
        if v is None:
            (u,v)=u  # no v given, assume u is an edge tuple
        if self.has_edge(u,v):  # no parallel edges
            return
        elif u in self and v in self:
            raise NetworkXError, "adding edge %s-%s not allowed in tree"%(u,v)
        elif u in self:
            Graph.add_edge(self,u,v)
            self.par[v]=u
            return
        elif v in self:
            Graph.add_edge(self,u,v)
            self.par[u]=v
            return
        elif len(self.adj)==0: # first leaf
            Graph.add_edge(self,u,v)            
            self.par[v]=u   # u is v's parent          
            return
        else:
            raise NetworkXError, "adding edge %s-%s not allowed in tree"%(u,v)
            
    def parent(self,u):
        try:
            return self.par[u]
        except:
            return None

            
    def children(self,u):
        #FIXME reverse parent dict
        pass


    def root_tree(self,root):        
        preds=paths.predecessor(self,root)
        del preds[root]
        for p in preds:
            self.par[p]=preds[p][0] # preds[node] is an array 


class DirectedTree(Tree,DiGraph):
    """ A directed tree."""
    def __init__(self,data=None,**kwds):
        DiGraph.__init__(self,**kwds)
        if data is not None:

            try: # build a rooted tree
                D=DiGraph()
                for (child,parent) in data.par.iteritems():
                    D.add_edge(parent,child)
            except AttributeError: 
                D=DiGraph(data)
            except: # else nothing we can do
                raise NetworkXError, "Data %s is not a rooted tree:"%data
                    
            if D.order()==D.size()+1:
                self.pred=D.pred.copy()
                self.succ=D.succ.copy()
                self.adj=self.succ
                del D
            else: # not a tree
                raise NetworkXError, "Data %s is not a rooted tree:"%data
             
    def delete_node(self, n):
        try:
            if len(self.succ[n])+len(self.pred[n])==1: # allowed for leaf node
                DiGraph.delete_node(self,n) # deletes adjacent edge too
            else:
                raise NetworkXError( \
              "deleting interior node %s not allowed in tree"%(n))
        except KeyError: # NetworkXError if n not in self
            raise NetworkXError, "node %s not in graph"%n
            
    def add_edge(self, u, v=None):  
        if v is None: (u,v)=u  # no v given, assume u is an edge tuple
        if self.has_edge(u,v): return # no parallel edges
        elif u in self and v in self:
            raise NetworkXError, "adding edge %s-%s not allowed in tree"%(u,v)
        elif u in self or v in self:
            DiGraph.add_edge(self,u,v) # u->v
            return
        elif len(self.adj)==0: # first leaf
            DiGraph.add_edge(self,u,v) # u->v           
            return
        else:
            raise NetworkXError("adding edge %s-%s not allowed in tree"%(u,v))
            
    def delete_edge(self, u, v=None): 
        if v is None: (u,v)=u
        if self.degree(u)==1 or self.degree(v)==1:
            DiGraph.delete_edge(self,u,v)
        else:
            raise NetworkXError(
                  "deleting interior edge %s-%s not allowed in tree"%(u,v))
        if self.degree(u)==0: DiGraph.delete_node(self,u)
        if self.degree(v)==0: DiGraph.delete_node(self,v)


class Forest(Tree,Graph):
    """ A forest."""
    def __init__(self,data=None,**kwds):
        Tree.__init__(self,**kwds)
        self.comp={}  # dictionary mapping node to component
        self.nc=0 # component index, start at zero, sequential (with holes)
        if data is not None:
            try:
                self=convert.from_whatever(data,create_using=self)
            except:
                raise NetworkXError("Data %s is not a forest"%data)
        
    def add_node(self, n):
        Graph.add_node(self,n)
        # this is not called from add_edge so we must assign
        # and component (else that is assigned in add_edge)
        self.comp[n]=self.nc
        self.nc+=1


    def delete_node(self, n):
        # get neighbors first since this will remove all edges to them
        neighbors=self.neighbors(n)
        Graph.delete_node(self,n) # delete node and adjacent edges
        if len(neighbors)==1: return # n was a leaf node
        for nbr in neighbors:
            # make new components of each nbr and connected graph
            # FIXME this does more work then is necessary
            # since nbrs of n could be in same conected component
            # and then will get renumbered more than once
            vnodes=paths.node_connected_component(self,nbr)
            for v in vnodes:
                self.comp[v]=self.nc
            self.nc+=1
        del self.comp[n]     # remove node from component dictionary

    def add_edge(self, u, v=None):  
        if v is None: (u,v)=u  # no v given, assume u is an edge tuple
        if self.has_edge(u,v):  return # no parallel edges
        if u in self:  # u is in forest
            if v in self: # v is in forest
                if self.comp[u]==self.comp[v]: # same tree?
                    raise NetworkXError, \
                          "adding edge %s-%s not allowed in forest"%(u,v)
                else:  # join two trees 
                    Graph.add_edge(self,u,v)
                    ucomp=self.comp[u]
                    # set component number of v tree to u tree
                    for n in paths.node_connected_component(self,v):
                        self.comp[n]=ucomp
            else: # add u-v to tree in component with u
                Graph.add_edge(self,u,v)
                self.comp[v]=self.comp[u]
        else: # make new tree with only u-v
            Graph.add_edge(self,u,v)
            self.comp[u]=self.nc
            self.comp[v]=self.nc
            self.nc+=1
        
    def delete_edge(self, u, v=None): 
        if v is None: (u,v)=u   # no v given, assume u is an edge tuple
        Graph.delete_edge(self,u,v)
        # this will always break a tree into two trees
        # put nodes connected to v in a new component
        vnodes=paths.node_connected_component(self,v)
        for n in vnodes:
            self.comp[n]=self.nc
        self.nc+=1

    def tree(self,n=None):
        """Return tree containing node n.
        If no node is specified return list of all trees in forest.
        """
        if n is not None:
            ncomp=self.comp[n]
            vnodes=[v for v in self if self.comp[v]==ncomp]
            return Tree(self.subgraph(vnodes))
        else:
            trees=[]
            uniqc={}
            # make a unique list of component id's (integers)
            for c in self.comp.values(): 
                uniqc[c]=True
            for c in uniqc.keys():
                vnodes=[v for v in self if self.comp[v]==c]
                trees.append(Tree(self.subgraph(vnodes)))
            return trees

    def tree_nodes(self,n=None):
        """Return tree containing node n.
        If no node is specified return list of all trees in forest.
        """
        if n is not None:
            return self.tree(n).nodes()
        else:
            tlist=[]
            for t in self.tree():
                tlist.append(t.nodes())
            return tlist
        

class DirectedForest(DiGraph,Tree):
    # not implemented
    pass


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/tree.txt',
                                 'tests/forest.txt',
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
    
 
