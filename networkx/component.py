# -*- coding: utf-8 -*-
"""
Connected components.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
___revision__ = ""
#    Copyright (C) 2004-2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
import networkx
from networkx.shortest_path import \
     single_source_shortest_path,\
     single_source_shortest_path_length


def connected_components(G):
    """
    Return a list of lists of nodes in each connected component of G.

    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 
    """
    if G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph."""
    seen={}
    components=[]
    for v in G:      
        if v not in seen:
            c=single_source_shortest_path_length(G,v)
            components.append(c.keys())
            seen.update(c)
    components.sort(lambda x, y: cmp(len(y),len(x)))
    return components            


def number_connected_components(G):
    """Return the number of connected components in G.
    For undirected graphs only. 
    """
    return len(connected_components(G))


def is_connected(G):
    """Return True if G is connected.
    For undirected graphs only. 
    """
    if G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph."""
    return len(single_source_shortest_path(G, G.nodes_iter().next()))==len(G)


def connected_component_subgraphs(G):
    """
    Return a list of graphs of each connected component of G.
    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 

    For example, to get the largest connected component:
    >>> H=connected_component_subgraphs(G)[0]

    """
    cc=connected_components(G)
    graph_list=[]
    for c in cc:
        graph_list.append(G.subgraph(c,inplace=False))
    return graph_list


def node_connected_component(G,n):
    """
    Return a list of nodes of the connected component containing node n.

    For undirected graphs only. 

    """
    if G.is_directed():
        raise networkx.NetworkXError,\
              """Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph."""
    return single_source_shortest_path_length(G,n).keys()


def _test_suite():
    import doctest
    suite = doctest.DocFileSuite('tests/component.txt',package='networkx')
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
    
