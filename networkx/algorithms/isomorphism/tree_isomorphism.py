"""
An algorithm for finding if two undirected trees are isomorphic,
and if so returns an isomorphism between the two sets of nodes.

This algorithm uses a routine to tell if two rooted trees (trees with a
specified root node) are isomorphic, which may be independently useful.

This implements an algorithm from:
The Design and Analysis of Computer Algorithms
by Aho, Hopcroft, and Ullman
Addison-Wesley Publishing 1974
Example 3.2 pp. 84-86.

A more understandable version of this algorithm is described in:
Homework Assignment 5
McGill University SOCS 308-250B, Winter 2002
by Matthew Suderman
http://crypto.cs.mcgill.ca/~crepeau/CS250/2004/HW5+.pdf
"""

from collections import defaultdict

import networkx as nx
from networkx.utils.decorators import not_implemented_for

__all__ = ["rooted_tree_isomorphism", "tree_isomorphism"]


@nx._dispatchable(graphs={"t1": 0, "t2": 2}, returns_graph=True)
def root_trees(t1, root1, t2, root2):
    """Create a single digraph dT of free trees t1 and t2
    #   with roots root1 and root2 respectively
    # rename the nodes with consecutive integers
    # so that all nodes get a unique name between both trees

    # our new "fake" root node is 0
    # t1 is numbers from 1 ... n
    # t2 is numbered from n+1 to 2n
    """

    dT = nx.DiGraph()

    newroot1 = 1  # left root will be 1
    newroot2 = nx.number_of_nodes(t1) + 1  # right will be n+1

    # may be overlap in node names here so need separate maps
    # given the old name, what is the new
    namemap1 = {root1: newroot1}
    namemap2 = {root2: newroot2}

    # add an edge from our new root to root1 and root2
    dT.add_edge(0, namemap1[root1])
    dT.add_edge(0, namemap2[root2])

    for i, (v1, v2) in enumerate(nx.bfs_edges(t1, root1)):
        namemap1[v2] = i + namemap1[root1] + 1
        dT.add_edge(namemap1[v1], namemap1[v2])

    for i, (v1, v2) in enumerate(nx.bfs_edges(t2, root2)):
        namemap2[v2] = i + namemap2[root2] + 1
        dT.add_edge(namemap2[v1], namemap2[v2])

    # now we really want the inverse of namemap1 and namemap2
    # giving the old name given the new
    # since the values of namemap1 and namemap2 are unique
    # there won't be collisions
    namemap = {}
    for old, new in namemap1.items():
        namemap[new] = old
    for old, new in namemap2.items():
        namemap[new] = old

    return (dT, namemap, newroot1, newroot2)


def _root_trees_optimized(t1, root1, t2, root2):
    """Optimized version of root_trees using list-based adjacency structure.

    Create a tree structure combining t1 and t2 with roots root1 and root2.
    Uses list-based adjacency and computes levels during BFS for better performance.

    Returns
    -------
    children : list of lists
        Adjacency list representation where children[v] contains the children of node v
    namemap : list
        Maps new node IDs to original node names
    levels : list
        Distance from fake root for each node
    newroot1 : int
        New ID for root1
    newroot2 : int
        New ID for root2
    total_nodes : int
        Total number of nodes in the combined structure
    """
    n1 = nx.number_of_nodes(t1)
    total_nodes = n1 + nx.number_of_nodes(t2) + 1  # +1 for fake root

    newroot1 = 1  # left root will be 1
    newroot2 = n1 + 1  # right will be n+1

    # Build adjacency list representation (more efficient than DiGraph for this use)
    # children[v] = list of children of v
    children = [[] for _ in range(total_nodes)]
    children[0] = [newroot1, newroot2]

    # Build inverse namemap directly: namemap[new_id] = old_name
    # We don't need the forward map since we build inverse directly
    namemap = [None] * total_nodes
    namemap[newroot1] = root1
    namemap[newroot2] = root2

    # Level/distance from fake root for each node
    levels = [0] * total_nodes
    levels[newroot1] = 1
    levels[newroot2] = 1

    # Process t1: BFS and assign consecutive IDs, track levels
    namemap1_forward = {root1: newroot1}  # temporary forward map for BFS
    next_id = newroot1 + 1
    for v1, v2 in nx.bfs_edges(t1, root1):
        new_v2 = next_id
        next_id += 1
        namemap1_forward[v2] = new_v2
        namemap[new_v2] = v2
        new_v1 = namemap1_forward[v1]
        children[new_v1].append(new_v2)
        levels[new_v2] = levels[new_v1] + 1

    # Process t2: BFS and assign consecutive IDs, track levels
    namemap2_forward = {root2: newroot2}  # temporary forward map for BFS
    next_id = newroot2 + 1
    for v1, v2 in nx.bfs_edges(t2, root2):
        new_v2 = next_id
        next_id += 1
        namemap2_forward[v2] = new_v2
        namemap[new_v2] = v2
        new_v1 = namemap2_forward[v1]
        children[new_v1].append(new_v2)
        levels[new_v2] = levels[new_v1] + 1

    return (children, namemap, levels, newroot1, newroot2, total_nodes)


def _rooted_tree_isomorphism_core(t1, root1, t2, root2):
    """Core implementation of rooted tree isomorphism without is_tree checks.

    This is called internally when we've already verified the trees are valid.
    Uses the optimized _root_trees_optimized for better performance.
    """
    # get the rooted tree formed by combining them with unique names
    # children: adjacency list, namemap: new->old mapping, levels: distance from root
    (children, namemap, levels, newroot1, newroot2, total_nodes) = _root_trees_optimized(t1, root1, t2, root2)
    # Group nodes by their level/distance from the root
    # Use list of lists since levels are consecutive integers
    h = max(levels)  # height
    L = [[] for _ in range(h + 1)]
    for v in range(total_nodes):
        L[levels[v]].append(v)

    # Use lists instead of dicts since node IDs are consecutive integers 0..total_nodes-1
    label = [0] * total_nodes
    ordered_labels = [() for _ in range(total_nodes)]
    ordered_children = [() for _ in range(total_nodes)]

    # nothing to do on last level so start on h-1
    # also nothing to do for our fake level 0, so skip that
    for i in range(h - 1, 0, -1):
        # update the ordered_labels and ordered_children for any children
        for v in L[i]:
            node_children = children[v]
            # nothing to do if no children
            if node_children:
                # get all the pairs of labels and nodes of children and sort by labels
                # reverse=True to preserve DFS order, see gh-7945
                s = sorted(((label[u], u) for u in node_children), reverse=True)

                # invert to give a list of two tuples
                # the sorted labels, and the corresponding children
                ordered_labels[v], ordered_children[v] = tuple(zip(*s))

        # now collect and sort the sorted ordered_labels
        # for all nodes in L[i], carrying along the node
        forlabel = sorted((ordered_labels[v], v) for v in L[i])

        # now assign labels to these nodes, according to the sorted order
        # starting from 0, where identical ordered_labels get the same label
        current = 0
        prev_ol = None
        for ol, v in forlabel:
            # advance to next label if different from previous
            if prev_ol is not None and ol != prev_ol:
                current += 1
            label[v] = current
            prev_ol = ol

    # they are isomorphic if the labels of newroot1 and newroot2 are equal
    if label[newroot1] != label[newroot2]:
        return []

    # now lets get the isomorphism by walking the ordered_children
    isomorphism = []
    stack = [(newroot1, newroot2)]
    while stack:
        curr_v, curr_w = stack.pop()
        isomorphism.append((namemap[curr_v], namemap[curr_w]))
        # Extend stack with paired children
        oc_v = ordered_children[curr_v]
        oc_w = ordered_children[curr_w]
        if oc_v:  # both have same structure if isomorphic
            stack.extend(zip(oc_v, oc_w))

    return isomorphism


@nx._dispatchable(graphs={"t1": 0, "t2": 2})
def rooted_tree_isomorphism(t1, root1, t2, root2):
    """
    Return an isomorphic mapping between rooted trees `t1` and `t2` with roots
    `root1` and `root2`, respectively.

    These trees may be either directed or undirected,
    but if they are directed, all edges should flow from the root.

    It returns the isomorphism, a mapping of the nodes of `t1` onto the nodes
    of `t2`, such that two trees are then identical.

    Note that two trees may have more than one isomorphism, and this
    routine just returns one valid mapping.
    This is a subroutine used to implement `tree_isomorphism`, but will
    be somewhat faster if you already have rooted trees.

    Parameters
    ----------
    t1 :  NetworkX graph
        One of the trees being compared

    root1 : node
        A node of `t1` which is the root of the tree

    t2 : NetworkX graph
        The other tree being compared

    root2 : node
        a node of `t2` which is the root of the tree

    Returns
    -------
    isomorphism : list
        A list of pairs in which the left element is a node in `t1`
        and the right element is a node in `t2`.  The pairs are in
        arbitrary order.  If the nodes in one tree is mapped to the names in
        the other, then trees will be identical. Note that an isomorphism
        will not necessarily be unique.

        If `t1` and `t2` are not isomorphic, then it returns the empty list.

    Raises
    ------
    NetworkXError
        If either `t1` or `t2` is not a tree
    """
    if not nx.is_tree(t1):
        raise nx.NetworkXError("t1 is not a tree")
    if not nx.is_tree(t2):
        raise nx.NetworkXError("t2 is not a tree")

    return _rooted_tree_isomorphism_core(t1, root1, t2, root2)


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable(graphs={"t1": 0, "t2": 1})
def tree_isomorphism(t1, t2):
    """
    Return an isomorphic mapping between two trees `t1` and `t2`.

    If `t1` and `t2` are not isomorphic, an empty list is returned.
    Note that two trees may have more than one isomorphism, and this routine just
    returns one valid mapping.

    Parameters
    ----------
    t1 : undirected NetworkX graph
        One of the trees being compared

    t2 : undirected NetworkX graph
        The other tree being compared

    Returns
    -------
    isomorphism : list
        A list of pairs in which the left element is a node in `t1`
        and the right element is a node in `t2`.  The pairs are in
        arbitrary order.  If the nodes in one tree is mapped to the names in
        the other, then trees will be identical. Note that an isomorphism
        will not necessarily be unique.

        If `t1` and `t2` are not isomorphic, then it returns the empty list.

    Raises
    ------
    NetworkXError
        If either `t1` or `t2` is not a tree

    Notes
    -----
    This runs in ``O(n*log(n))`` time for trees with ``n`` nodes.
    """
    if not nx.is_tree(t1):
        raise nx.NetworkXError("t1 is not a tree")
    if not nx.is_tree(t2):
        raise nx.NetworkXError("t2 is not a tree")

    # To be isomorphic, t1 and t2 must have the same number of nodes and sorted
    # degree sequences
    if not nx.faster_could_be_isomorphic(t1, t2):
        return []

    # A tree can have either 1 or 2 centers.
    # If the number doesn't match then t1 and t2 are not isomorphic.
    center1 = nx.center(t1)
    center2 = nx.center(t2)

    if len(center1) != len(center2):
        return []

    # If there is only 1 center in each, then use it.
    # Use _rooted_tree_isomorphism_core to skip redundant is_tree checks
    if len(center1) == 1:
        return _rooted_tree_isomorphism_core(t1, center1[0], t2, center2[0])

    # If they both have 2 centers, try the first for t1 with the first for t2.
    attempts = _rooted_tree_isomorphism_core(t1, center1[0], t2, center2[0])

    # If that worked we're done.
    if attempts:
        return attempts

    # Otherwise, try center1[0] with the center2[1], and see if that works
    return _rooted_tree_isomorphism_core(t1, center1[0], t2, center2[1])
