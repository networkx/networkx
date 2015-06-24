# -*- coding: utf-8 -*-
#    Copyright (C) 2015 by
#    André Dietrich <dietrich@ivs.cs.uni-magdeburg.de>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = """\n""".join(['André Dietrich <dietrich@ivs.cs.uni-magdeburg.de>',
                            'Sebastian Zug <zug@ivs.cs.uni-magdeburg.de>'])
__all__ = ['all_simple_paths',
	   'all_shortest_paths',
	   'has_path']


def all_simple_paths(G, source, target, cutoff=None):
    """Generate all simple paths in graph G from source to target.
    
    A simple path is a path with no repeated nodes.
    
    The result paths are returned ordered by there length, starting
    from the shortest paths.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path

    cutoff : integer, optional
        Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    path_generator: generator
       A generator that produces lists of simple paths, ordered by their
       length starting from the shortes path. If there are no paths between
       the source and target within the given cutoff the generator
       produces no output.

    Examples
    --------
    >>> import networkx as nx
    >>>
    >>> G = nx.complete_graph(4)
    >>> for path in nx.bidirectional.all_simple_paths(G, source=0, target=3):
    ...     print(path)
    ...
    [0, 3]
    [0, 1, 3]
    [0, 2, 3]
    [0, 2, 1, 3]
    [0, 1, 2, 3]
    >>> paths = nx.bidirectional.all_simple_paths(G, source=0, target=3, cutoff=2)
    >>> print(list(paths))
    [[0, 3], [0, 1, 3], [0, 2, 3]]

    Notes
    -----
    This algorithm constructs sequentially two trees, one from the source
    in direction to the target and one from the target in direction to the
    source. The leaves of both growing trees are continuously compared, if
    there are matching leaves in both trees, a new path is identified.
    
    This algorithm actually reduces the search space by half, which results
    in a faster identification of simple paths than in the original
    "all_simple_paths" algorithm. But it requires more memory, which can
    have a negative effect on the speed in fully connected graphs.
    
              
                           source    
                             /\
                            /\ \
                           / /\ \
                          /   /\ \
                         /\  /\  /\
                        /  \/   /  \
                       /    \  /\   \
                      /_____/_/__\___\_________  meeting points
                     /\     \    /   /\
                    /XX\    /  \/   /XX\
                   /XXXX\   \/  \  /XXXX\
                  /XXXXXX\  /    \/XXXXXX\
                 /XXXXXXXX\ \/   /XXXXXXXX\
                /XXXXXXXXXX\ \  /XXXXXXXXXX\
               /XXXXXXXXXXXX\ \/XXXXXXXXXXXX\
              /XXXXXXXXXXXXXX\/XXXXXXXXXXXXXX\
                           target
    Authors
    -------
    André Dietrich and Sebastian Zug
    {dietrich, zug}@ivs.cs.uni-magdeburg.de

    See Also
    --------
    nx.all_simple_paths, nx.all_shortest_paths, nx.shortest_path,
    nx.bidirectional.all_shortest_paths, nx.bidirectional.has_path
    """
    
    if source not in G:
        raise nx.NetworkXError('source node %s not in graph'%source)
    if target not in G:
        raise nx.NetworkXError('target node %s not in graph'%target)
    if cutoff is None:
        cutoff = len(G)-1
    if G.is_multigraph():
        return _all_simple_paths_multigraph(G, source, target, cutoff=cutoff)
    else:
        return _all_simple_paths_graph(G, source, target, cutoff=cutoff)


def _all_simple_paths_graph(G, source, target, cutoff):
  
    if cutoff < 1:
        return
    
    tree = [{(source,)}, {(target,)}]
     
    for i in range(cutoff):      
        
        tree1  = tree[i%2]
        tree2  = tree[(i+1)%2]
        temp   = set()
        
        leaves = {x[-1] for x in iter(tree1)} # only to reduce some effort        
        for path in iter(tree2):
            for s in iter(G[path[-1]]):
                if s not in path:
                    if s in leaves:
                        for _path in iter(tree1):
                            if s == _path[-1]:
                                if not set(_path).intersection(path):
                                    if i % 2:
                                        yield list(path)  + [x for x in reversed(_path)]
                                    else:
                                        yield list(_path) + [x for x in reversed(path)]
                    temp.add(path + (s,))
        
        tree[(i+1)%2] = temp
        
def _all_simple_paths_multigraph(G, source, target, cutoff):
  
    if cutoff < 1:
        return
    
    tree = [[(source,)], [(target,)]]
     
    for i in range(cutoff):      
        
        tree1  = tree[i%2]
        tree2  = tree[(i+1)%2]
        temp   = []
        
        leaves = {x[-1] for x in iter(tree1)} # only to reduce some effort        
        for path in iter(tree2):
            for s in [v for u,v in G.edges([path[-1]])]:
                if s not in path:
                    if s in leaves:
                        for _path in iter(tree1):
                            if s == _path[-1]:
                                if not set(_path).intersection(path):
                                    if i % 2:
                                        yield list(path)  + [x for x in reversed(_path)]
                                    else:
                                        yield list(_path) + [x for x in reversed(path)]
                    temp.append(path + (s,))
        
        tree[(i+1)%2] = temp

def all_shortest_paths(G, source, target):
    """Generate all shortest paths in graph G from source to target.

    Parameters
    ----------
    G : NetworkX graph

    source : node
       Starting node for path

    target : node
       Ending node for path

    Returns
    -------
    path_generator: generator
       A generator that produces lists of shortest paths. If there are
       no paths between the source and target the generator produces no
       output.

    Examples
    --------
    >>> import networkx as nx
    >>>
    >>> G = nx.complete_graph(4)
    >>> for path in nx.bidirectional.all_shortest_paths(G, source=0, target=3):
    ...     print(path)
    ...
    [0, 3]
    
    Notes
    -----
    This algorithm constructs sequentially two trees, one from the source
    in direction to the target and one from the target in direction to the
    source. The leaves of both growing trees are continuously compared, if
    there are matching leaves in both trees, a new path is identified.
    
    This algorithm actually reduces the search space by half, which results
    in a faster identification of simple paths than in the original
    "all_simple_paths" algorithm. But it requires more memory, which can
    have a negative effect on the speed in fully connected graphs.
    
              
                           source    
                             /\
                            /\ \
                           / /\ \
                          /   /\ \
                         /\  /\  /\
                        /  \/   /  \
                       /    \  /\   \
                      /_____/_/__\___\_________   meeting points
                     /\ \   \    /   /\
                    /XX\ \  /  \/   /XX\
                   /XXXX\ \ \/  \  /XXXX\
                  /XXXXXX\ \/    \/XXXXXX\
                 /XXXXXXXX\ \/   /XXXXXXXX\
                /XXXXXXXXXX\ \  /XXXXXXXXXX\
               /XXXXXXXXXXXX\ \/XXXXXXXXXXXX\
              /XXXXXXXXXXXXXX\/XXXXXXXXXXXXXX\
                           target
    Authors
    -------
    André Dietrich and Sebastian Zug
    {dietrich, zug}@ivs.cs.uni-magdeburg.de

    See Also
    --------
    nx.all_simple_paths, nx.all_shortest_paths, nx.shortest_path,
    nx.bidirectional.all_simple_paths, nx.bidirectional.has_path
    """
    
    
    if source not in G:
        raise nx.NetworkXError('source node %s not in graph'%source)
    if target not in G:
        raise nx.NetworkXError('target node %s not in graph'%target)
    if G.is_multigraph():
        return _all_shortest_paths_multigraph(G, source, target)
    else:
        return _all_shortest_paths_graph(G, source, target)
    

def _all_shortest_paths_graph(G, source, target):
    
    tree = [{(source,)}, {(target,)}]
    node = [{source}, {target}]
    found = 0
    i     = 0
    while not found and tree[0] and tree[1]:      
        
        tree1 = tree[i%2]
        tree2 = tree[(i+1)%2]
        
        node1 = node[i%2]
        node2 = node[(i+1)%2]
        
        temp   = set()
        
        for path in iter(tree2):
            for s in iter(G[path[-1]]):
                if s not in path:
                    if s in node1:
                        for _path in iter(tree1):
                            if s == _path[-1]:
                                if not set(_path).intersection(path):
                                    found = 1
                                    if i % 2:
                                        yield list(path) + [x for x in reversed(_path)]
                                    else:
                                        yield list(_path) + [x for x in reversed(path)]
                    elif s not in node2:
                        node2.add(s)
                        temp.add(path + (s,))
        
        tree[(i+1)%2] = temp
        i += 1
        
def _all_shortest_paths_multigraph(G, source, target):
    
    tree = [[(source,)], [(target,)]]
    #node = [{source}, {target}]
    found = 0
    i     = 0
    while not found and tree[0] and tree[1]:      
        
        tree1 = tree[i%2]
        tree2 = tree[(i+1)%2]
        
        #node1 = node[i%2]
        #node2 = node[(i+1)%2]
        
        temp   = []
        
        for path in iter(tree2):
            for s in [v for u,v in G.edges([path[-1]])]:
                if s not in path:
                    #if s in node1:
                    for _path in iter(tree1):
                        if s == _path[-1]:
                            if not set(_path).intersection(path):
                                found = 1
                                if i % 2:
                                    yield list(path) + [x for x in reversed(_path)]
                                else:
                                    yield list(_path) + [x for x in reversed(path)]
                    #elif s not in node2:
                    #    node2.add(s)
                    temp.append(path + (s,))
        
        tree[(i+1)%2] = temp
        i += 1


def has_path(G, source, target):
    
    if source not in G:
        raise nx.NetworkXError('source node %s not in graph'%source)
    if target not in G:
        raise nx.NetworkXError('target node %s not in graph'%target)
    if G.is_multigraph():
        return _has_path_multigraph(G, source, target)
    else:
        return _has_path_graph(G, source, target)
        
      
def _has_path_graph(G, source, target):
  
    leaves = [{source}, {target}]
    nodes  = [{source}, {target}]
    i      = 1
  
    while leaves[0] and leaves[1]:      
        
        node2 = nodes[i%2]
        node1 = nodes[(i+1)%2]
        
        temp   = set()
        
        for leave in iter(leaves[i%2]):
            for s in iter(G[leave]):
                if s in node1:
                    return True
                elif s not in node2:
                    node2.add(s)
                    temp.add(s)
        
        leaves[i%2] = temp
        
        i += 1

    return False
  
def _has_path_multigraph(G, source, target):
  
    leaves = [{source}, {target}]
    nodes  = [{source}, {target}]
    i      = 1
  
    while leaves[0] and leaves[1]:      
        
        node2 = nodes[i%2]
        node1 = nodes[(i+1)%2]
        
        temp   = set()
        
        for leave in iter(leaves[i%2]):
            for s in [v for u,v in G.edges([leave])]:
                if s in node1:
                    return True
                elif s not in node2:
                    node2.add(s)
                    temp.add(s)
        
        leaves[i%2] = temp
        
        i += 1

    return False
