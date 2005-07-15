"""
Search algorithms, shortest path, spanning trees, etc.

See also networkx.paths.

The following search methods available, see the documentation below.

 - number_connected_components(G)
 - connected_components(G)
 - connected_component_subgraphs(G)
 - dfs_preorder(G,v=None)
 - dfs_postorder(G,v=None)
 - dfs_predecessor(G,v=None)
 - dfs_successor(G,v=None)
 - bfs_length(G,source=None,target=None)
 - bfs_path(G,source,target=None)
 - dfs_forest(G,v=None)

These algorithms are based on Program 18.10 "Generalized graph search",
page 128, Algorithms in C, Part 5, Graph Algorithms by Robert Sedgewick

Reference::

  @Book{sedgewick-2001-algorithms-5,
  author = 	 {Robert Sedgewick},
  title = 	 {Algorithms in C, Part 5: Graph Algorithms},
  publisher = 	 {Addison Wesley Professional},
  year = 	 {2001},
  edition = 	 {3rd},
  }

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult(dschult@colgate.edu)"""
__date__ = "$Date: 2005-06-15 08:19:25 -0600 (Wed, 15 Jun 2005) $"
__credits__ = """"""
__revision__ = "$Revision: 1026 $"
#    Copyright (C) 2004,2005 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import networkx.queues
import search_class as SC

def dfs_preorder(G,v=None):
    """
    Return a list of nodes ordered by depth first search (DFS) preorder. 
    If the graph has more than one component return a list of lists.
    Optional v=v limits search to component of graph containing v.
    """
    V=SC.Preorder(G, queue=networkx.queues.DFS)
    V.search(v)
    return V.forest

def dfs_postorder(G,v=None):
    """
    Return a list of nodes ordered by depth first search (DFS) postorder. 
    If the graph has more than one component return a list of lists.
    Optional v=v limits search to component of graph containing v.
    """
    V=SC.Postorder(G,queue=networkx.queues.DFS)
    V.search(v)
    return V.forest


def dfs_predecessor(G,v=None):
    """
    Return a dictionary of nodes each with a list of predecessor
    nodes in depth first search (DFS) order.
    Optional v=v limits search to component of graph containing v.
    """
    V=SC.Predecessor(G,queue=networkx.queues.DFS)
    V.search(v)
    return V.data


def dfs_successor(G,v=None):
    """
    Return a dictionary of nodes each with a list of successor
    nodes in depth first search (DFS) order.
    Optional v=v limits search to component of graph containing v.
    """
    V=SC.Predecessor(G,queue=networkx.queues.DFS)
    V.search(v)
    return V.data

def bfs_length(G,source,target=None):
    """
    Return a dictionary of nodes with the shortest path length from source.
    """
    V=SC.Length(G,queue=networkx.queues.BFS)
    V.search(source)
    if target!=None:
        try:
            return V.length[target]
        except KeyError:
            return -1 # no target in graph
    else:
        return V.length

def bfs_path(G,source,target=None):
    """
    Return a dictionary of nodes with the paths 
    from source to all reachable nodes.
    Optional target=target produces only one path as a list.
    """
    V=SC.Predecessor(G,queue=networkx.queues.BFS)
    V.search(source)
    if target!=None:
        path=V.path(target)
        path.insert(0,source)
        return path # return one path
    else:
        paths={}
        for k in V.data.keys():
            paths[k]=V.path(k)
            paths[k].insert(0,source)
        return paths


def number_connected_components(G):
    """
    Return number of connected components of G.
    """
    V=SC.Preorder(G,queue=networkx.queues.DFS)
    V.search(None)
    return len(V.forest)

def is_connected(G):
    """True if G is connected"""
    return number_connected_components(G)==1

def connected_components(G):
    """
    Return a list of lists of nodes in each connected component of G.
    The list is ordered from largest connected component to smallest.
    """
    V=SC.Preorder(G,queue=networkx.queues.DFS)
    V.search(None)
    cc=V.forest
    cc.sort(lambda x, y: cmp(len(y),len(x)))
    return cc

def connected_component_subgraphs(G):
    """
    Return a list of graphs of each connected component of G.
    The list is ordered from largest connected component to smallest.
    To get the largest connected component:
    
    >>> H=connected_component_subgraphs(G)[0]

    """
    cc=connected_components(G)
    graph_list=[]
    for c in cc:
        graph_list.append(G.subgraph(c,inplace=False))
    return graph_list


def dfs_forest(G,v=None):
    """
    Return a forest of trees built from depth first search (DFS).
    Optional v=v limits search to component of graph containing v
    and will return a single tree.
    """
    V=SC.Forest(G,queue=networkx.queues.DFS)
    V.search(v)
    return V.forest

def node_connected_component(G,v):
    """
    Return the connected component to which v belongs as a list of nodes.
    """
    component=dfs_forest(G,v)
    return component[0].nodes()

# YANGI:
# add loop/loop length counters, will need to implement back edge for that

def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('../tests/search.txt',package='networkx')
    return suite


if __name__ == "__main__":
    import sys
    import unittest
    if sys.version_info[:2] < (2, 4):
        print "Python version 2.4 or later required for tests (%d.%d detected)." %  sys.version_info[:2]
        sys.exit(-1)
    unittest.TextTestRunner().run(_test_suite())
    
