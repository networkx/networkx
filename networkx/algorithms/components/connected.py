# -*- coding: utf-8 -*-
"""
Connected components.
"""
__authors__ = "\n".join(['Eben Kenah',
                         'Aric Hagberg (hagberg@lanl.gov)'
                         'Christopher Ellison'])
#    Copyright (C) 2004-2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

__all__ = ['number_connected_components', 
           'connected_components',
           'connected_component_subgraphs',
           'is_connected',
           'node_connected_component',
           'IncrementalConnectedComponents',
           ]

from collections import defaultdict
import networkx as nx

def connected_components(G):
    """Return nodes in connected components of graph.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    comp : list of lists
       A list of nodes for each component of G.

    See Also       
    --------
    strongly_connected_components

    Notes
    -----
    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 
    """
    if G.is_directed():
        raise nx.NetworkXError("""Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph.""")
    seen={}
    components=[]
    for v in G:      
        if v not in seen:
            c=nx.single_source_shortest_path_length(G,v)
            components.append(list(c.keys()))
            seen.update(c)
    components.sort(key=len,reverse=True)            
    return components            


def number_connected_components(G):
    """Return number of connected components in graph.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    n : integer
       Number of connected components

    See Also       
    --------
    connected_components

    Notes
    -----
    For undirected graphs only. 
    """
    return len(connected_components(G))


def is_connected(G):
    """Test graph connectivity.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    connected : bool
      True if the graph is connected, false otherwise.

    Examples
    --------
    >>> G=nx.path_graph(4)
    >>> print(nx.is_connected(G))
    True

    See Also
    --------
    connected_components

    Notes
    -----
    For undirected graphs only. 
    """
    if G.is_directed():
        raise nx.NetworkXError(\
            """Not allowed for directed graph G.
Use UG=G.to_undirected() to create an undirected graph.""")

    if len(G)==0:
        raise nx.NetworkXPointlessConcept(
            """Connectivity is undefined for the null graph.""")

    return len(nx.single_source_shortest_path_length(G,
                                              next(G.nodes_iter())))==len(G)


def connected_component_subgraphs(G):
    """Return connected components as subgraphs.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    Returns
    -------
    glist : list
      A list of graphs, one for each connected component of G.

    Examples
    --------
    Get largest connected component as subgraph

    >>> G=nx.path_graph(4)
    >>> G.add_edge(5,6)
    >>> H=nx.connected_component_subgraphs(G)[0]

    See Also
    --------
    connected_components

    Notes
    -----
    The list is ordered from largest connected component to smallest.
    For undirected graphs only. 
    """
    cc=connected_components(G)
    graph_list=[]
    for c in cc:
        graph_list.append(G.subgraph(c))
    return graph_list


def node_connected_component(G,n):
    """Return nodes in connected components of graph containing node n.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph.

    n : node label       
       A node in G

    Returns
    -------
    comp : lists
       A list of nodes in component of G containing node n.

    See Also       
    --------
    connected_components

    Notes
    -----
    For undirected graphs only. 
    """
    if G.is_directed():
        raise nx.NetworkXError("""Not allowed for directed graph G.
              Use UG=G.to_undirected() to create an undirected graph.""")
    return list(nx.single_source_shortest_path_length(G,n).keys())

class IncrementalConnectedComponents(object):
    """Class to incrementally maintain list of connected components.

    This class maintains a partition of the nodes in a graph as edges are added 
    to that graph.  It does not handle the removal of edges and thus, loses       
    integrity whenever an edge is removed from the graph. To handle edge 
    deletion, a persistent union-find data structure might be helpful:
    
       http://portal.acm.org/citation.cfm?id=1292541

    For the case of adding edges only, the partition is maintained efficently 
    using the standard union-find algorithm, which has amortized time 
    complexity per operation of O(alpha(n)) where alpha is the inverse 
    Ackermann function and n is the number of nodes in the graph.

    Practically, there are additional costs to consider:
      1) When adding edges to the graph, the edge attribute dictionary is
         updated. 
      2) For MultiGraphs, a key must be calculated if one is not provided.

    Nevertheless, the take-home point is that maintaining the partition when 
    adding edges to a graph costs essentially nothing.

    The data structure provided by the union-find algorithm allows us to quickly
    update and check if two nodes are part of the same connected component, but
    to determine all the nodes in each connected component still requires O(N)
    operations, if building the list from scratch. So if one needs to know the
    connected components after each edge addition, this technique is only 
    slightly better than simply calling the O(N+E) connected_components().
    
    To speed things up, the class maintains a dictionary of sets. The keys are
    nodes which are representatives of the components.  Whenever a component
    is merged by the union-find algorithm, it is merged in the dictionary of
    sets. This provides an updated, reverse list of memberships.

    Additional discussion:
        http://en.wikipedia.org/wiki/Disjoint-set_data_structure
        http://www.boost.org/doc/libs/1_44_0/libs/graph/doc/incremental_components.html
    
    """
    def __init__(self, G):
        """Initializes the connnected components.
        
        Parameters
        ----------
        G : Graph, MultiGraph
            The graph used to track connected components.

        Examples
        --------
        >>> G = Graph()
        >>> G.add_edge(0,1)
        >>> G.add_edge(2,3)
        >>> cc = IncrementalConnectedComponents(G)
        >>> cc.connected_components()
        [set([0, 1]), set([2, 3])]
        >>> cc.add_edge(1,2)
        >>> cc.connected_components()
        [set([0, 1, 2, 3])]
        >>> cc.add_edge(4,5)
        >>> cc.connected_components()
        [set([0, 1, 2, 3]), set([4, 5])]
        >>> cc.same_component(0,4)
        False
        
        """
        if G.is_directed():
            msg = 'Not allowed for directed graph G. '
            msg += 'Use UG=G.to_undirected() to create an undireced graph.'
            raise nx.NetworkXError(msg)

        self.G = G
        self.uf = nx.utils.UnionFind()
        self.cc = defaultdict(set)

        if len(G):
            cc = connected_components(G)
            for component in cc:
                # Populate UnionFind structure
                self.uf.union(*component)
               
                # Store the components
                root = self.uf[component[0]]
                self.cc[root].update(component)

    def __getitem__(self, u):
        """Returns the connected component that `u` belongs to.

        """
        return self.connected_component(u)
                        
    def __len__(self):
        """Returns the current number of connected components.
        
        """
        return len(self.cc)
                
    def add_edge(self, u, v, *args, **kwargs):
        """Adds an edge to G and updates the connected component structure.
        
        """
        self.G.add_edge(u, v, *args, **kwargs)
        uroot, vroot = self.uf[u], self.uf[v]
                
        if uroot != vroot:
            # This only has permanent effects if the nodes are new.
            self.cc[uroot].add(u)
            self.cc[vroot].add(v)
            
            # Join the groups since they are connected.
            self.uf.union(u, v)
            
            # Need to unionize just joined groups in the dict of components.
            alive = self.uf[u]
            if alive == uroot:
                dead = vroot
            else:
                dead = uroot
            self.cc[alive].update(self.cc[dead])
            del self.cc[dead]

    def connected_component(self, u):
        """Returns the connected component that `u` belongs to.
        
        Raises
        ------
        NetworkXError
            When `u` is not in the graph.
        
        """
        return self.cc[self.index(u)]
            
    def connected_components(self):
        """Returns the current list of connected components, sorted by size.
        
        """
        components = self.cc.values()
        components.sort(key=len,reverse=True)    
        return components
        
    def index(self, u):
        """Returns the index of the connected component to which `u` belongs.
        
        Raises
        ------
        NetworkXError
            When `u` is not in the graph.
            
        """
        if u not in self.G:
            msg = 'Node %r not in graph.' % (u,)
            raise nx.NetworkXError(msg)
        else:
            return self.uf[u]
            
    def is_connected(self):
        """Returns True if G presently consists of a single connected component.
        
        """
        return len(self.cc) == 1
    
    def same_component(self, u, v):
        """Returns `True` if `u` and `v` are in the same component.
        
        Notes
        -----
        If one of `u` or `v` is not in the graph, then `False` is returned.
        
        """
        if u in self.G and v in self.G:
            same = self.uf[u] == self.uf[v]
        else:
            same = False
        return same
        
