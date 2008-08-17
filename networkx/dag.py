# -*- coding: utf-8 -*-
"""
Algorithms for directed acyclic graphs (DAGs).
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
___revision__ = ""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import networkx

def is_directed_acyclic_graph(G):
    """Return True if the graph G is a directed acyclic graph (DAG).

    Otherwise return False.
    
    """
    if topological_sort(G) is None:
        return False
    else:
        return True

def topological_sort(G, comparator=None):
    """
    Return a list of nodes of the digraph G in topological sort order.

    A topological sort is a nonunique permutation of the nodes
    such that an edge from u to v implies that u appears before v in the
    topological sort order.

    If G is not a directed acyclic graph no topological sort exists
    and the Python keyword None is returned.

    This algorithm is based on a description and proof at
    http://www2.toki.or.id/book/AlgDesignManual/book/book2/node70.htm

    See also is_directed_acyclic_graph()
    
    """
    # nonrecursive version

    seen={}
    order_explored=[] # provide order and 
    explored={}       # fast search without more general priorityDictionary
                     
    if not G.is_directed():  G.successors_iter=G.neighbors_iter

    if comparator:
        nodes_iter = sorted(G.nodes_iter(), cmp=comparator)
    else:
        nodes_iter = G.nodes_iter()
    for v in nodes_iter:     # process all vertices in G
        if v in explored: continue

        fringe=[v]   # nodes yet to look at
        while fringe:
            w=fringe[-1]  # depth first search
            if w in explored: # already looked down this branch
                fringe.pop()
                continue
            seen[w]=1     # mark as seen
            # Check successors for cycles and for new nodes
            new_nodes=[]
            for n in G.successors_iter(w):  
                if n not in explored:
                    if n in seen: return #CYCLE !!
                    new_nodes.append(n)
            if new_nodes:   # Add new_nodes to fringe
                fringe.extend(new_nodes)
            else:           # No new nodes so w is fully explored
                explored[w]=1
                order_explored.insert(0,w) # reverse order explored
                fringe.pop()    # done considering this node
    return order_explored

def topological_sort_recursive(G, comparator=None):
    """
    Return a list of nodes of the digraph G in topological sort order.

    This is a recursive version of topological sort.
    
    """
    # function for recursive dfs
    def _dfs(G,seen,explored,v):
        seen[v]=1
        for w in G.successors(v):
            if w not in seen: 
                if not _dfs(G,seen,explored,w):
                    return
            elif w in seen and w not in explored:
                # cycle Found--- no topological sort
                return False
        explored.insert(0,v) # inverse order of when explored 
        return v

    seen={}
    explored=[]

    if not G.is_directed():  G.successors=G.neighbors
    
    if comparator:
        nodes_iter = sorted(G.nodes_iter(), cmp=comparator)
    else:
        nodes_iter = G.nodes_iter()
    for v in nodes_iter:  # process all nodes
        if v not in explored:
            if not _dfs(G,seen,explored,v): 
                return 
    return explored


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/dag.txt',package='networkx')
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
    



