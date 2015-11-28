# -*- coding: utf-8 -*-
#    Copyright (C) 2015 by
#    André Dietrich <dietrich@ivs.cs.uni-magdeburg.de>
#    Sebastian Zug <zug@ivs.cs.uni-magdeburg.de>
#    All rights reserved.
#    BSD license.
import networkx as nx

__all__ = ['bidirectional_all_simple_paths',
           'bidirectional_all_shortest_paths',
           'bidirectional_has_path']


def bidirectional_all_simple_paths(G, source, target, cutoff=None):
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

    Raises
    ------
    NetworkXError
       If source or target nodes are not in the input graph.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> for path in nx.bidirectional_all_simple_paths(G, source=0, target=3):
    ...     print(path)
    ...
    [0, 3]
    [0, 1, 3]
    [0, 2, 3]
    [0, 1, 2, 3]
    [0, 2, 1, 3]

    >>> paths = nx.bidirectional_all_simple_paths(G, 0, 3, cutoff=2)
    >>> print(list(paths))
    [[0, 3], [0, 1, 3], [0, 2, 3]]

    Notes
    -----
    This algorithm constructs sequentially two trees, one from the source
    in direction to the target and one from the target in direction to the
    source. Only the tree with fewer leaves is increased within the next step.
    The leaves of both growing trees are continuously compared, and if
    there are matching leaves in both trees, a new path is identified.

    This algorithm actually reduces the search space by half, which results
    in a faster identification of simple paths than in the original
    `nx.all_simple_paths` algorithm. But it might require more memory, which
    can have a negative effect on the speed in fully connected graphs.
    See the benchmark at: http://www.aizac.info/bi-graph-search-benchmark

                           source                                      |
                             /\                                        |
                            /\ \                                       |
                           / /\ \                                      |
                          /   /\ \                                     |
                         /\  /\  /\                                    |
                        /  \/   /  \                                   |
                       /    \  /\   \                                  |
                      /_____/_/__\___\_________   meeting points       |
                     /\ \   \    /   /\                                |
                    /XX\ \  /  \/   /XX\                               |
                   /XXXX\ \ \/  \  /XXXX\                              |
                  /XXXXXX\ \/    \/XXXXXX\                             |
                 /XXXXXXXX\ \/   /XXXXXXXX\                            |
                /XXXXXXXXXX\ \  /XXXXXXXXXX\                           |
               /XXXXXXXXXXXX\ \/XXXXXXXXXXXX\                          |
              /XXXXXXXXXXXXXX\/XXXXXXXXXXXXXX\                         |
                           target                                      |
    Authors
    -------
    André Dietrich and Sebastian Zug
    {dietrich, zug}@ivs.cs.uni-magdeburg.de

    See Also
    --------
    nx.all_simple_paths, nx.all_shortest_paths, nx.shortest_path,
    nx.bidirectional_all_shortest_paths, nx.bidirectional_has_path
    """

    if source not in G:
        raise nx.NetworkXError('source node %s not in graph' % source)
    if target not in G:
        raise nx.NetworkXError('target node %s not in graph' % target)
    if cutoff is None:
        cutoff = len(G) - 1
    if G.is_multigraph():
        return _bidirectional_all_simple_paths_multi(G, source,
                                                     target, cutoff=cutoff)
    else:
        return _bidirectional_all_simple_paths(G, source,
                                               target, cutoff=cutoff)


def _bidirectional_all_simple_paths(G, source, target, cutoff):

    if cutoff < 1:
        return

    tree = [{(source,)}, {(target,)}]
    leaves = [{source}, {target}]

    # used if the graph is not directed
    neighbors = lambda node: iter(G[node])

    for _ in range(cutoff):

        if len(tree[1]) < len(tree[0]):
            modus = 1
            tree_source = tree[1]
            tree_target = tree[0]
            leaves_ = leaves[0]

            if G.is_directed():
                neighbors = G.predecessors
        else:
            modus = 0
            tree_source = tree[0]
            tree_target = tree[1]
            leaves_ = leaves[1]

            if G.is_directed():
                neighbors = G.successors

        temp_tree = set()
        temp_leaves = set()

        for path_s in tree_source:
            for s in neighbors(path_s[-1]):
                if s not in path_s:
                    if s in leaves_:
                        for path_t in tree_target:
                            if s == path_t[-1]:
                                if not set(path_t).intersection(path_s):
                                    if modus:
                                        yield list(path_t) + \
                                            [x for x in reversed(path_s)]
                                    else:
                                        yield list(path_s) + \
                                            [x for x in reversed(path_t)]

                    temp_tree.add(path_s + (s,))
                    temp_leaves.add(s)

        tree[modus] = temp_tree
        leaves[modus] = temp_leaves


def _bidirectional_all_simple_paths_multi(G, source, target, cutoff):

    if cutoff < 1:
        return

    tree = [[(source,)], [(target,)]]
    leaves = [{source}, {target}]

    for _ in range(cutoff):

        if len(tree[1]) < len(tree[0]):
            modus = 1
            tree_source = tree[1]
            tree_target = tree[0]
            leaves_ = leaves[0]

        else:
            modus = 0
            tree_source = tree[0]
            tree_target = tree[1]
            leaves_ = leaves[1]

        temp_tree = []
        temp_leaves = []

        for path_s in tree_source:
            for s in [v for u, v in G.edges([path_s[-1]])]:
                if s not in path_s:
                    if s in leaves_:
                        for path_t in tree_target:
                            if s == path_t[-1]:
                                if not set(path_t).intersection(path_s):
                                    if modus:
                                        yield list(path_t) + \
                                            [x for x in reversed(path_s)]
                                    else:
                                        yield list(path_s) + \
                                            [x for x in reversed(path_t)]
                    temp_tree.append(path_s + (s,))
                    temp_leaves.append(s)

        tree[modus] = temp_tree
        leaves[modus] = temp_leaves


def bidirectional_all_shortest_paths(G, source, target):
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

    Raises
    ------
    NetworkXError
       If source or target nodes are not in the input graph.

    NetworkXNoPath
        If no path exists between source and target.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.complete_graph(4)
    >>> for path in nx.bidirectional_all_shortest_paths(G, source=0, target=3):
    ...     print(path)
    ...
    [0, 3]

    Notes
    -----
    This algorithm constructs sequentially two trees, one from the source
    in direction to the target and one from the target in direction to the
    source. Only the tree with fewer leaves is increased within the next step.
    The leaves of both growing trees are continuously compared, and if
    there are matching leaves in both trees, a new path is identified.

    This algorithm actually reduces the search space by half, which results
    in a faster identification of simple paths than in the original
    `nx.all_simple_paths` algorithm. But it might require more memory, which
    can have a negative effect on the speed in fully connected graphs.
    See the benchmark at: http://www.aizac.info/bi-graph-search-benchmark

                           source                                      |
                             /\                                        |
                            /\ \                                       |
                           / /\ \                                      |
                          /   /\ \                                     |
                         /\  /\  /\                                    |
                        /  \/   /  \                                   |
                       /    \  /\   \                                  |
                      /_____/_/__\___\_________   meeting points       |
                     /\ \   \    /   /\                                |
                    /XX\ \  /  \/   /XX\                               |
                   /XXXX\ \ \/  \  /XXXX\                              |
                  /XXXXXX\ \/    \/XXXXXX\                             |
                 /XXXXXXXX\ \/   /XXXXXXXX\                            |
                /XXXXXXXXXX\ \  /XXXXXXXXXX\                           |
               /XXXXXXXXXXXX\ \/XXXXXXXXXXXX\                          |
              /XXXXXXXXXXXXXX\/XXXXXXXXXXXXXX\                         |
                           target                                      |

    Authors
    -------
    André Dietrich and Sebastian Zug
    {dietrich, zug}@ivs.cs.uni-magdeburg.de

    See Also
    --------
    nx.all_simple_paths, nx.all_shortest_paths, nx.shortest_path,
    nx.bidirectional_all_simple_paths, nx.bidirectional_has_path
    """

    if source not in G:
        raise nx.NetworkXError('source node %s not in graph' % source)
    if target not in G:
        raise nx.NetworkXError('target node %s not in graph' % target)
    if G.is_multigraph():
        return _bidirectional_all_shortest_paths_multi(G, source, target)
    else:
        return _bidirectional_all_shortest_paths(G, source, target)


def _bidirectional_all_shortest_paths(G, source, target):

    tree = [{(source,)}, {(target,)}]
    nodes = [{source}, {target}]
    found = 0

    # used if the graph is not directed
    neighbors = lambda node: iter(G[node])

    while not found and tree[0] and tree[1]:

        if len(tree[1]) < len(tree[0]):
            modus = 1
            tree_source = tree[1]
            tree_target = tree[0]
            nodes_source = nodes[1]
            nodes_target = nodes[0]

            if G.is_directed():
                neighbors = G.predecessors

        else:
            modus = 0
            tree_source = tree[0]
            tree_target = tree[1]
            nodes_source = nodes[0]
            nodes_target = nodes[1]

            if G.is_directed():
                neighbors = G.successors

        temp_tree = set()

        for path_s in tree_source:
            for s in neighbors(path_s[-1]):
                if s not in path_s:
                    if s in nodes_target:
                        for path_t in tree_target:
                            if s == path_t[-1]:
                                if not set(path_t).intersection(path_s):
                                    found = 1
                                    if modus:
                                        yield list(path_t) + \
                                            [x for x in reversed(path_s)]
                                    else:
                                        yield list(path_s) + \
                                            [x for x in reversed(path_t)]
                    # elif s not in node2:
                    nodes_source.add(s)
                    temp_tree.add(path_s + (s,))

        tree[modus] = temp_tree

    if not found:
        raise nx.NetworkXNoPath("No path between %s and %s." % (source,
                                                                target))


def _bidirectional_all_shortest_paths_multi(G, source, target):

    tree = [[(source,)], [(target,)]]
    found = 0

    while not found and tree[0] and tree[1]:

        if len(tree[1]) < len(tree[0]):
            modus = 1
            tree_source = tree[1]
            tree_target = tree[0]

        else:
            modus = 0
            tree_source = tree[0]
            tree_target = tree[1]

        temp_tree = []

        for path_s in tree_source:
            for s in [v for u, v in G.edges([path_s[-1]])]:
                if s not in path_s:
                    for path_t in tree_target:
                        if s == path_t[-1]:
                            if not set(path_t).intersection(path_s):
                                found = 1
                                if modus:
                                    yield list(path_t) + \
                                        [x for x in reversed(path_s)]
                                else:
                                    yield list(path_s) + \
                                        [x for x in reversed(path_t)]

                    temp_tree.append(path_s + (s,))

        tree[modus] = temp_tree

    if not found:
        raise nx.NetworkXNoPath("No path between %s and %s." % (source,
                                                                target))


def bidirectional_has_path(G, source, target):

    if source not in G:
        raise nx.NetworkXError('source node %s not in graph' % source)
    if target not in G:
        raise nx.NetworkXError('target node %s not in graph' % target)
    if G.is_multigraph():
        return _bidirectional_has_path_multi(G, source, target)
    else:
        return _bidirectional_has_path(G, source, target)


def _bidirectional_has_path(G, source, target):

    leaves = [{source}, {target}]
    nodes = [{source}, {target}]

    neighbors = lambda node: iter(G[node])

    while leaves[0] and leaves[1]:

        if len(leaves[1]) < len(leaves[0]):
            modus = 1
            nodes_s = nodes[1]
            leaves_t = leaves[0]
            leaves_s = leaves[1]

            if G.is_directed():
                neighbors = G.predecessors
        else:
            modus = 0
            nodes_s = nodes[0]
            leaves_t = leaves[1]
            leaves_s = leaves[0]

            if G.is_directed():
                neighbors = G.successors

        temp = set()

        for leave in leaves_s:
            for s in neighbors(leave):
                if s not in nodes_s:
                    if s in leaves_t:
                        return True
                    temp.add(s)

        leaves[modus] = temp
        nodes[modus].update(temp)

    return False


def _bidirectional_has_path_multi(G, source, target):

    leaves = [{source}, {target}]
    nodes = [{source}, {target}]

    while leaves[0] and leaves[1]:

        if len(leaves[1]) < len(leaves[0]):
            modus = 1
            nodes_s = nodes[1]
            leaves_t = leaves[0]
            leaves_s = leaves[1]
        else:
            modus = 0
            nodes_s = nodes[0]
            leaves_t = leaves[1]
            leaves_s = leaves[0]

        temp = set()

        for leave in leaves_s:
            for s in [v for u, v in G.edges([leave])]:
                if s not in nodes_s:
                    if s in leaves_t:
                        return True
                    temp.add(s)

        leaves[modus] = temp
        nodes[modus].update(temp)

    return False
