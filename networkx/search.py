"""
Search algorithms.

See also networkx.path.

"""
__authors__ = """Eben Kenah (ekenah@t7.lanl.gov)\nAric Hagberg (hagberg@lanl.gov)"""
__date__ = ""
__revision__ = ""
#    Copyright (C) 2004-2007 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

import networkx
def dfs_preorder(G,source=None,reverse_graph=False):
    """
    Return list of nodes connected to source in DFS preorder.
    Traverse the graph G with depth-first-search from source.
    Non-recursive algorithm.
    """
    if source is None:
        nlist=G.nodes() # process entire graph
    else:
        nlist=[source]  # only process component with source

    if reverse_graph==True:
        try:
            neighbors=G.in_neighbors
        except:
            neighbors=G.neighbors
    else:
        neighbors=G.neighbors

    seen={} # nodes seen      
    pre=[]  # list of nodes in a DFS preorder
    for source in nlist:
        if source in seen: continue
        lifo=[source]
        while lifo:
            v = lifo.pop()
            if v in seen: continue
            pre.append(v)
            seen[v]=True
            lifo.extend((w for w in G.neighbors(v) if w not in seen))
    return pre


def dfs_postorder(G,source=None,reverse_graph=False):
    """
    Return list of nodes connected to source in DFS preorder.
    Traverse the graph G with depth-first-search from source.
    Non-recursive algorithm.
    """
    if source is None:
        nlist=G.nodes() # process entire graph
    else:
        nlist=[source]  # only process component with source
    
    if reverse_graph==True:
        try:
            neighbors=G.in_neighbors
        except:
            neighbors=G.neighbors
    else:
        neighbors=G.neighbors
    
    seen={} # nodes seen      
    post=[] # list of nodes in a DFS postorder

    for source in nlist:
        if source in seen: continue
        queue=[source]     # use as LIFO queue
        while queue:
            v=queue[-1]
            if v not in seen:
                seen[v]=True
            done=1
            for w in neighbors(v):
                if w not in seen:
                    queue.append(w)
                    done=0
                    break
            if done==1:
                post.append(v)
                queue.pop()
    return post


def dfs_tree(G,source=None,reverse_graph=False):
    """Return directed graph (tree) of depth-first-search with root at source.
    If the graph is disconnected, return a disconnected graph (forest).
    """
    succ=dfs_successor(G,source=source,reverse_graph=reverse_graph)
    return networkx.DiGraph(succ)

def dfs_predecessor(G,source=None,reverse_graph=False):
    """
    Return predecessors of depth-first-search with root at source.
    """
    if source is None:
        nlist=G.nodes() # process entire graph
    else:
        nlist=[source]  # only process component with source

    if reverse_graph==True:
        try:
            neighbors=G.in_neighbors
        except:
            neighbors=G.neighbors
    else:
        neighbors=G.neighbors

    seen={}   # nodes seen      
    pred={}
    for source in nlist:
        if source in seen: continue
        queue=[source]     # use as LIFO queue
        pred[source]=[]
        while queue:
            v=queue[-1]
            if v not in seen:
                seen[v]=True
            done=1
            for w in neighbors(v):
                if w not in seen:
                    queue.append(w)
                    pred[w]=[v]     # Each node has at most one predecessor
                    done=0
                    break
            if done==1:
                queue.pop()
    return pred


def dfs_successor(G,source=None,reverse_graph=False):
    """
    Return succesors of depth-first-search with root at source.
    """

    if source is None:
        nlist=G.nodes() # process entire graph
    else:
        nlist=[source]  # only process component with source

    if reverse_graph==True:
        try:
            neighbors=G.in_neighbors
        except:
            neighbors=G.neighbors
    else:
        neighbors=G.neighbors

    seen={}   # nodes seen      
    succ={}
    for source in nlist:
        if source in seen: continue
        queue=[source]     # use as LIFO queue
        while queue:
            v=queue[-1]
            if v not in seen:
                seen[v]=True
                succ[v]=[]
            done=1
            for w in neighbors(v):
                if w not in seen:
                    queue.append(w)
                    succ[v].append(w)
                    done=0
                    break
            if done==1:
                queue.pop()
    return succ


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/search.txt',package='networkx')
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
    
