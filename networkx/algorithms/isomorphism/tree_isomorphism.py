"""An algorithm for finding if two undirected trees are isomorphic. 

This algorithm uses a routine to tell if two rooted trees (trees with a
specified root node) are isomorphic, which may be independently useful.

References
----------
  .. [1] A. V. Aho, J. E. Hopcroft y J. D. Ullman, "The Desing And Analysis of
     Computer Algorithms", Addison Wesley Publishing Company, (1974): 78-86.

  .. [2] M. Suderman, "Homework Assignment 5", McGill University SOCS 308-250B,
     (Winter 2002): http://crypto.cs.mcgill.ca/~crepeau/CS250/2004/HW5+.pdf

  .. [3] G. Valiente, "Algorithms on Trees and Graphs", Springer (2002): 
     151-166.

  .. [4] M. Carrasco-Ruiz, "Herramientas para el Manejo Computacional de
     Gráficas", Bachelor of Science Thesis, UNAM, (2022): 55-77.

"""

from collections import Counter

import networkx as nx
from networkx.utils.decorators import not_implemented_for

__all__ = ["rooted_tree_isomorphism", "tree_isomorphism"]


def categorize_entries(S):
    """Groups the entries of the lists by its position.

    Given a list of lists whose entries are numbers between 0 and m. Define a
    NONEMPTY map such that NONEMPTY(i) are the numbers in the i-th position of
    some list in S; this numbers are sorted.

    For example, given ((1), (1, 2, 3), (1, 2, 2)), NONEMPTY(2) = [2, 3].

    Parameters
    ----------
    S : list of lists of ints (natural numbers)
        The list of lists of natural numbers.

    Returns
    -------
    NONEMPTY : dict of int: list of ints
        The NONEMPTY map such that NONEMPTY(i) are the numbers in the i-th
        position of some list in S; this list of numbers is sorted.

    Notes
    -----
    This algorithm runs in O(l_total + m) time and O(l_total) space, where
    l_total is the sum of the lengths of the lists in S and m is the max value
    of all the lists in S.

    """
    # Define the an empty NONEMPTY map.
    NONEMPTY = {}

    # The max length found in S.
    l_max = max([len(s) for s in S])

    # Traverse all the entries contained in the lists of S.
    for i in range(l_max):
        # Define a counter to keep track of the entries found in the i-th
        # position.
        C = Counter()

        for s in S:
            # Only consider lists of length greater or equal than i, and whose
            # i-th entry is not already contained in the multiset.
            if len(s) < (i + 1) or s[i] in C:
                continue
            else:
                C[s[i]] = 1

        # Obtain a sorted representation of the entries found in the i-th
        # position.
        NONEMPTY[i] = [x for x in range(max(C) + 1) for _ in range(C.get(x, 0))]

    return NONEMPTY


def categorize_lists(S):
    """Groups the lists by its length.

    Given a list of lists whose entries are numbers between 0 and m. Define a
    LENGTH map such that LENGTH(i) are the lists of S with length i.

    For example, given ((1), (1, 2, 3), (1, 2, 2)), NONEMPTY(3) = [(1, 2, 3),
    (1, 2, 2)].

    Parameters
    ----------
    S : list of lists of ints (natural numbers)
        The list of lists of natural numbers.

    Returns
    -------
    LENGTH : dict of int: list of lists of ints
        The LENGTH map such that LENGTH(i) are the lists of S with length i.

    Notes
    -----
    This algorithm runs in O(|S|) time and space.

    """
    # Define an empty LENGTH map.
    LENGTH = {}

    # Traverse the lists in S and add them to the LENGTH.
    for s in S:
        if len(s) in LENGTH:
            LENGTH[len(s)].append(s)
        else:
            LENGTH[len(s)] = [s]

    return LENGTH


def sort_lists_of_naturals(S):
    """Lexicographically sort a list of lists of natural numbers.

    Given a list of lists whose entries are numbers between 0 and m. Perform an
    algorithm similar to bucket sort to return a sorted list with the elements
    of S. The expected order is a lexicographical order.

    Parameters
    ----------
    S : list of lists of ints (natural numbers)
        The list of lists of natural numbers.

    Returns
    -------
    sorted_list : list of lists of ints (natural numbers)
        A lexicographically sorted list with the elements of S.

    Notes
    -----
    This algorithm runs in O(l_total + m) time and O(l_total) space, where
    l_total is the sum of the lengths of the lists in S and m is the max value
    of all the lists in S.

    """
    # Get the maximum value contained in S.
    m = max([max(s) for s in S])

    # Define a list that will behave like a queue.
    Q = []

    # Define an empty array of size m whose entries are empty queues.
    A = [[] for i in range(m + 1)]

    # The max length found in S.
    l_max = max([len(s) for s in S])

    # Obtain the NONEMPTY and LENGTH maps.
    NONEMPTY = categorize_entries(S)
    LENGTH = categorize_lists(S)

    l = l_max
    while l >= 1:
        # All of the elements in Q have length greater than l. For each element
        # s in Q, append q to the queue A[s[l]].
        while len(Q) > 0:
            s = Q.pop()
            A[s[l - 1]].append(s)

        # Add the lists s of size l to the queue A[s[l]] if there are any.
        if l in LENGTH:
            for s in LENGTH[l]:
                A[s[l - 1]].append(s)

        # Sort the elements of A according to its l-th entry.
        for i in NONEMPTY[l - 1]:
            while len(A[i]) > 0:
                s = A[i].pop()
                Q.append(s)

        # Proceed with the lists of size l-1.
        l = l - 1

    # Q now contains all of the elements of S sorted lexicographically.
    return Q


def get_levels(T, root, height):
    """Groups the vertices by the level they're on the rooted tree.


    Define a LEVELS map such that, for each i in {0,...,h}, LEVELS(i) is the set
    of vertices found on the i-th level of T.

    Let h be the height of the tree. The amount of levels a tree has is equal to
    its height. If a vertex v is on the i-th level, then its childs are on the
    (i-1)-th level. Thus, by definition, the only vertex in the h-th level is
    the root of the tree and the only vertices on the level 0 are leaves.

    Parameters
    ----------
    T : NetworkX Graph
        The rooted tree.

    root : node
        The root of the tree.

    height : int
        The height of the tree.

    Returns
    -------
    LEVELS : dict of int: set of nodes
        A LEVELS map such that, for each i in {0,...,h}, LEVELS(i) is the set of
        vertices found on the i-th level of T.

    Notes
    -----
    The algorithm runs in O(n) time and space.

    """
    # Define an empty LEVELS map.
    LEVELS = {}

    # Define a map in_lvl such that in_lvl(v) is the level where v is found.
    in_lvl = {}

    # Define the root height.
    in_lvl[root] = height

    # Perform a BFS traversal to fill the in_lvl map.
    for (parent, child) in nx.bfs_edges(T, root):
        in_lvl[child] = in_lvl[parent] - 1

    # Traverse all vertices and group them by levels.
    for v in in_lvl.keys():
        l = in_lvl[v]
        if l in LEVELS:
            LEVELS[l].add(v)
        else:
            LEVELS[l] = {v}

    return LEVELS


def get_initial_values(T, root):
    """Returns a map with the initial values of the nodes.

    Returns a map VALUES such that, for every vertex v in the rooted tree, if v
    is a leaf then v's initial value is 0, otherwise its defined as -1.

    Parameters
    ----------
    T : NetworkX Graph
        The rooted tree.

    root : node
        The root of the tree.

    Returns
    -------
    VALUES : dict of node: int
        A map VALUES such that, for each vertex v in the rooted tree, if v is a
        leaf then v's initial value is 0, otherwise its defined as -1.

    Notes
    -----
    The algorithm runs in O(n) time and space.

    """
    # Define an empty map VALUES.
    VALUES = {}

    # Define a set for leaves and non-leaves vertices of T.
    non_leaves = set()
    leaves = set()

    # Perform a BFS traversal to determine which vertices are leaves and
    # non-leaves.
    for (parent, child) in nx.bfs_edges(T, root):
        # A parent can't be a leave.
        non_leaves.add(parent)

        # If a vertex was thought to be a leave but has a child, then it is not
        # a leave.
        if parent in leaves:
            leaves.remove(parent)

        leaves.add(child)

    # Set the initial value of the non-leave vertices as -1.
    for v in non_leaves:
        VALUES[v] = -1

    # Set the initial value of the leaves as 0.
    for v in leaves:
        VALUES[v] = 0

    return VALUES


def get_initial_children(parenthood, levels):
    """Returns a map with the initial children defined by the parenthood map.

    Defines a map CHILDREN where CHILDREN(v) is the ordered list of children of
    v in the rooted tree. This map determines who are the parents of the leaves
    found on the 0-th level.

    Parameters
    ----------
    parenthood : dict of node: node
        The parenthood map defined for the rooted tree.

    levels: dict of int: set of nodes
        The LEVELS map such that LEVELS(i) are the vertices found on the i-th
        level of the rooted tree.

    Returns
    -------
    CHILDREN : dict of node: set of nodes
        A mapping CHILDREN such that CHILDREN(v) is the ordered list of children
        of v in the rooted tree. This map determines who are the parents of the
        leaves found on the 0-th level.

    Note
    ----
    This algorithm runs in O(m_0) time and space where m_0 are the vertices
    found on the 0-th level of the rooted tree.

    """
    # Define an empty map CHILDREN.
    CHILDREN = {}

    # Traverse all the vertices found on the 0-th level.
    for v in levels[0]:
        # If the current vertex has a parent, add the child to the parent's
        # list of children.
        if v in parenthood:
            u = parenthood[v]

            # Add the child to the list of children of the parent.
            if u in CHILDREN:
                CHILDREN[u].append(v)
            else:
                CHILDREN[u] = [v]

    return CHILDREN


def assign_structure(parenthood, levels, values, i):
    """Assign a structure to all the vertices found on the i-th level.

    The structure of a vertex is defined as the natural multiset that contains
    the values of all its child; thus, a leaf has no structure. Informally, the
    structure of a vertex can be thought as the structure or "form" the sub-tree
    rooted on v has.

    Parameters
    ----------
    parenthood : dict of node: node
        The parenthood map defined for the rooted tree.

    levels: dict of int: set of nodes
        The LEVELS map such that LEVELS(i) are the vertices found on the i-th
        level of the rooted tree.

    values : dict of node: int
        The VALUES map such that, for each vertex v in the rooted tree,
        VALUES(v) is the value associated to v.

    i : int
        The current level of the rooted tree.

    Returns
    -------
    STRUCT : dict of node: natural multiset
        A STRUCT map such that struct(v) is the structure (natural multiset)
        corresponding to vertex v.

    leaves : set of nodes
        The leaves of the current level.

    Note
    ----
    This algorithm runs in O(m_{i-1} + m_i) time and space where m_{j} are the
    vertices found on the j-th level of the rooted tree.

    """
    # Define an empty map STRUCT.
    STRUCT = {}

    # Define an empty set to keep track of the leaves on the current level.
    leaves = set()

    # Traverse all the vertices on the i-th level and define an empty multiset
    # for each non-leave vertex.
    for v in levels[i]:
        if values[v] != 0:
            STRUCT[v] = Counter()
        else:
            leaves.add(v)

    # Traverse all the vertices on the (i-1)-th level and append them to its
    # father multiset.
    for u in levels[i - 1]:
        # Obtain u's father.
        v = parenthood[u]

        # Obtain u's value.
        uval = values[u]

        # Add u's value to the father's multiset.
        STRUCT[v][uval] += 1

    # Return the defined STRUCT map and leaves.
    return STRUCT, leaves


def get_multisets_list_of_level(levels, values, struct, i):
    """Obtain the structures found on the i-th level as a list.

    Build a list of multisets that correspond to the structures of the vertices
    found on the i-th level and a mapping of structures to the vertices that
    have said structure.

    Parameters
    ----------
    levels: dict of int: set of nodes
        The LEVELS map such that LEVELS(i) are the vertices found on the i-th
        level of the rooted tree.

    values : dict of node: int
        The VALUES map such that, for each vertex v in the rooted tree,
        VALUES(v) is the value associated to v.

    struct : dict of node: natural multiset
        The STRUCT map such that struct(v) is the structure (natural multiset)
        corresponding to vertex v.

    i : int
        The current level of the rooted tree.

    Returns
    -------
    list_multisets : list of natural multisets
        A list of multisets that correspond to the structures of the vertices
        found on the i-th level.

    MS : dict of natural multiset: set of nodes
        A mapping of structures to the vertices that have said structure.

    Note
    ----
    This algorithm runs in O(m_{i-1} + m_i) time and space where m_{j} are the
    vertices found on the j-th level of the rooted tree.

    """
    # Define an empty list of list representations of counters.
    S = []

    # Define a mapping of structures to the vertices that have said structure.
    MS = {}

    # Traverse each non-leave vertex on the i-th level and append its structure
    # to the list.
    for u in levels[i]:
        if values[u] != 0:
            # Get the structure (counter) associated with u.
            c = struct[u]

            # Get the list representation of the counter.
            lc = tuple(x for x in range(max(c) + 1) for _ in range(c.get(x, 0)))

            # Append the list representation to the list.
            S.append(lc)

            # Indicate that c is a structure u has.
            if lc in MS:
                MS[lc].add(u)
            else:
                MS[lc] = {u}

    return S, MS


def update_values(S, MS, values, children, parenthood, leaves):
    """Updates the values of current level.

    Given a sorted list of multisets. Updates the values of the vertices found
    on the map MS in the order specifies by the list.

    Two vertices on the same level have the same value if and only if they have
    the same structure. It also defines an order for the children of the
    vertices in the next level.

    Parameters
    ----------
    S : list of natural multisets
        The sorted list of multisets.

    MS : dict of natural multiset: set of nodes
        A mapping of structures to the vertices that have said structure.

    values : dict of node: int
        The VALUES map such that, for each vertex v in the rooted tree,
        VALUES(v) is the value associated to v.

    children : dict of node: set of nodes
        A mapping CHILDREN such that CHILDREN(v) is the ordered list of children
        of v in the rooted tree.

    parenthood : dict of node: node
        The parenthood map defined for the rooted tree.

    leaves : set of nodes
        The leaves of the current level.

    Note
    ----
    This algorithm runs in O(m_{i-1} + m_i) time and space where m_{j} are the
    vertices found on the j-th level of the rooted tree.

    """
    # The first vertices in the order of children are the leaves.
    for v in leaves:
        # If it exists, get the leave's parent; the previous case is considered
        # for the root, who doesn't have a parent.
        if v in parenthood:
            u = parenthood[v]

            # Add the child to the list of children of the parent.
            if u in children:
                children[u].append(v)
            else:
                children[u] = [v]

    # The current value can't be 0 as this value is reserved to leaves.
    current_val = 1

    for j in range(len(S)):
        # Ignore repeated multistructures.
        if j > 0 and (S[j] == S[j - 1]):
            continue

        # For each vertex that have the current structure, assing the current
        # value.
        for v in MS[S[j]]:
            values[v] = current_val

            # If the current vertex has a parent, get the parent.
            if v in parenthood:
                u = parenthood[v]

                # Add the child to the parent's list of children.
                if u in children:
                    children[u].append(v)
                else:
                    children[u] = [v]

        # For the next unique structure, assign a new value.
        current_val += 1


def build_isomorphism(root_T1, root_T2, children_T1, children_T2):
    """Return an isomorphism between two rooted trees.

    Given two isomorph rooted trees. Build an isomorphism between the vertices
    of T1 and T2.

    Parameters
    ----------
    root_T1 : node
        The root of the rooted tree T1.

    root_T2 : node
        The root of the rooted tree T2.

    children_T1 : dict of node: set of nodes
        A mapping CHILDREN such that CHILDREN(v) is the ordered list of children
        of v in the rooted tree T1.

    children_T2 : dict of node: set of nodes
        A mapping CHILDREN such that CHILDREN(v) is the ordered list of children
        of v in the rooted tree T_2.

    Returns
    -------
    isomorphism : dict of node: node
        An isomorphism map of the vertices T1 to the vertices of T2.

    Note
    ----
    This algorithm runs in O(n) time and space.

    """
    # Empty isomorphism
    isomorphism = {}

    # Perform a DFS traversal to define the isomorphism.
    Q = [(root_T1, root_T2)]

    while len(Q) > 0:
        # Get the head of the stack.
        (v_T1, v_T2) = Q.pop()

        isomorphism[v_T1] = v_T2

        if v_T1 in children_T1:
            for i in range(len(children_T1[v_T1])):
                u_T1 = children_T1[v_T1][i]
                u_T2 = children_T2[v_T2][i]

                Q.append((u_T1, u_T2))

    return isomorphism


def levels_verification(
    root_T1,
    root_T2,
    values_T1,
    values_T2,
    levels_T1,
    levels_T2,
    parenthood_T1,
    parenthood_T2,
    height,
):
    """Check for all levels that both trees share the same structure.

    For each level i in T1, check that all the structures present on the i-th
    level are also present in i-th level of T2. If all the levels are the same
    for both trees, return true.

    Parameters
    ----------
    root_T1 : node
        The root of the rooted tree T1.

    root_T2 : node
        The root of the rooted tree T2.

    values_T1 : dict of node: int
        The VALUES map such that, for each vertex v in the rooted tree T1,
        VALUES(v) is the value associated to v.

    values_T2 : dict of node: int
        The VALUES map such that, for each vertex v in the rooted tree T2,
        VALUES(v) is the value associated to v.

    levels_T1: dict of int: set of nodes
        The LEVELS map such that LEVELS(i) are the vertices found on the i-th
        level of the rooted tree T1.

    levels_T2: dict of int: set of nodes
        The LEVELS map such that LEVELS(i) are the vertices found on the i-th
        level of the rooted tree T2.

    parenthood_T1 : dict of node: node
        The parenthood map defined for the rooted tree T1.

    parenthood_T2 : dict of node: node
        The parenthood map defined for the rooted tree T2.

    height : int
        The height of the trees T1 and T2.

    Note
    ----
    This algorithm runs in O(n) time and space.

    """
    # Get the initial children found on the 0-th level.
    children_T1 = get_initial_children(parenthood_T1, levels_T1)
    children_T2 = get_initial_children(parenthood_T2, levels_T2)

    # Start at level 1 as all the vertices at level 0 are leaves.
    current_level = 1

    # check that all the structures present on the i-th level are also present
    # in i-th level of T2.
    while current_level <= height:
        # Assign the structures for the vertices of the current level for T1 and
        # T2.
        struct_T1, leaves_T1 = assign_structure(
            parenthood_T1, levels_T1, values_T1, current_level
        )

        struct_T2, leaves_T2 = assign_structure(
            parenthood_T2, levels_T2, values_T2, current_level
        )

        # Build the list of structures and the mapping.
        S_T1, MS_T1 = get_multisets_list_of_level(
            levels_T1, values_T1, struct_T1, current_level
        )

        S_T2, MS_T2 = get_multisets_list_of_level(
            levels_T2, values_T2, struct_T2, current_level
        )

        # Sort the list of structures.
        sorted_S_T1 = sort_lists_of_naturals(S_T1)
        sorted_S_T2 = sort_lists_of_naturals(S_T2)

        # If the sorted lists are different, return false.
        if sorted_S_T1 != sorted_S_T2:
            return False, {}

        # Update the values and the children.
        update_values(
            sorted_S_T1, MS_T1, values_T1, children_T1, parenthood_T1, leaves_T1
        )

        update_values(
            sorted_S_T2, MS_T2, values_T2, children_T2, parenthood_T2, leaves_T2
        )

        # Move to the next level.
        current_level += 1

    # If all the previous levels are equal, then build an isomorphism with the
    # previous information.
    isomorphism = build_isomorphism(root_T1, root_T2, children_T1, children_T2)

    return True, isomorphism


def get_height(T, root):
    """Returns the height of a rooted tree.

    Parameters
    ----------
    T : NetworkX Graph
        A rooted tree.

    root : node
        The root of the tree.

    Returns
    -------
    height : int
        The height of the rooted tree.

    Note
    ----
    This algorithm runs in O(n) time and space.

    """
    # Define a map for the distance to the root.
    distance_to_root = {}

    # The max distance between a root and another vertex.
    max_distance = 0

    distance_to_root[root] = 0

    # Perform a BFS traversal to determine the distances.
    for (parent, child) in nx.bfs_edges(T, root):
        distance_to_root[child] = distance_to_root[parent] + 1

        if max_distance < distance_to_root[child]:
            max_distance = distance_to_root[child]

    return max_distance


def get_parenthood(T, root):
    """Returns the parenthood map of a rooted tree.

    Parameters
    ----------
    T : NetworkX Graph
        A rooted tree.

    root : node
        The root of the tree.

    Returns
    -------
    parenthood : dict of node: node
        The parenthood map of the rooted tree.

    Note
    ----
    This algorithm runs in O(n) time and space.

    """
    # Define an empty parenthood map.
    parenthood = {}

    # Perform a BFS traversal to determine the parenthood map.
    for (parent, child) in nx.bfs_edges(T, root):
        parenthood[child] = parent

    return parenthood


def rooted_tree_isomorphism_n(T1, root_T1, T2, root_T2):
    """Returns an isomorphism between two rooted trees, if it exists.

    Parameters
    ----------
    T1 : NetworkX Graph
        A rooted tree.

    root_T1 : node
        The root of the rooted tree T1.

    T2 : NetworkX Graph
        A rooted tree.

    root_t2 : node
        The root of the rooted tree T2.

    Returns
    -------
    are_iso : bool
        Returns True if the given rooted trees are isomorphic, False otherwise.

    isomorphism : dict of node of T1: node of T2
        The isomorphism mapping f such that (u, v) is in E_T1 if and only if
        (f(u), f(v)) is in E_T2. This dictionary is empty when there is no
        isomorphism between the trees.

    Note
    ----
    This algorithm runs in O(n) time and space.

    """
    # If both trees have different amount of vertices, return false.
    if T1.order() != T2.order():
        return False, {}

    # If both trees are empty, return true.
    if T1.order() == 0:
        return True, {}

    # If trees have more than one node, verify that they're indeed trees.
    assert nx.is_tree(T1)
    assert nx.is_tree(T2)

    # Get the height's of the trees.
    height_T1 = get_height(T1, root_T1)
    height_T2 = get_height(T2, root_T2)

    # If the trees differ in height, return false.
    if height_T1 != height_T2:
        return False, {}
    elif height_T1 == 0:
        # If both trees have height 0, then there are only conformed by the
        # roots, they're isomorph.
        return True, {root_T1: root_T2}
    else:
        # If they have the same amount of levels, check that all levels coincide
        # in structure.
        levels_T1 = get_levels(T1, root_T1, height_T1)
        levels_T2 = get_levels(T2, root_T2, height_T2)

        # For every level i, check that both trees have the same amount of
        # vertices on the i-th level. If they differ for some level, return
        # false.
        for i in range(height_T1):
            if len(levels_T1[i]) != len(levels_T2[i]):
                return False, {}

        # Set the initial values for T1 and T2.
        values_T1 = get_initial_values(T1, root_T1)
        values_T2 = get_initial_values(T2, root_T2)

        # Define the parenthood map for T1 and T2.
        parenthood_T1 = get_parenthood(T1, root_T1)
        parenthood_T2 = get_parenthood(T2, root_T2)

        # Check that all levels have the same structure.
        return levels_verification(
            root_T1,
            root_T2,
            values_T1,
            values_T2,
            levels_T1,
            levels_T2,
            parenthood_T1,
            parenthood_T2,
            height_T1,
        )


def get_centers_of_tree(T):
    """Returns the center (or centers) of the tree.

    Parameters
    ----------
    T : NetworkX Graph
        A tree.

    Returns
    -------
    centers : set of nodes
        Returns the center or centers of the tree as a set.

    Note
    ----
    This algorithm runs in O(n) time and space.

    """
    # Get a random node.
    v = list(T)[0]

    # Perform a BFS with v as a root and save the last explored vertex.
    x = v
    for (parent, child) in nx.bfs_edges(T, x):
        x = child

    # Perform again a BFS with x now as a root and save the last explored
    # vertex.
    y = x
    parenthood = {}
    for (parent, child) in nx.bfs_edges(T, x):
        parenthood[child] = parent
        y = child

    # Build the xy-path found in T using the parenthood map defined in the
    # previous traversal. This path's length is the tree's diameter.
    P = [y]
    current = y
    while current in parenthood:
        current = parenthood[current]
        P.append(current)

    # The vertices found on the middle of this path are the centers.
    n = len(P)
    if n % 2 == 0:
        # If the xy-path has even length, then the vertices found in the
        # (n/2)-th and ((n/2)-1)-th position are the centers.
        p0 = int(n / 2)
        p1 = int((n / 2) - 1)
        centers = {P[p0], P[p1]}
    else:
        # If the xy-path has odd length, then the vertex found in the
        # ((n-1)/2)-th position is the center.
        p0 = int((n - 1) / 2)
        centers = {P[p0]}

    return centers


def tree_isomorphism_n(T1, T2):
    """Returns an isomorphism between two rooted trees, if it exists.

    Given two undirected trees T1 and T2. This function determines if they are
    isomorphic. It returns the a boolean, indicating if they are isomorphic. And
    the isomorphism, a mapping of the nodes of T1 onto the nodes of T2.

    Note that two trees may have more than one isomorphism, and this
    routine just returns one valid mapping.

    Parameters
    ----------
    T1 : undirected NetworkX graph
        One of the trees being compared

    T2 : undirected NetworkX graph
        The other tree being compared

    Returns
    -------
    are_isomorphic : bool
        Returns True if the given rooted trees are isomorph, False otherwise.

    isomorphism : dict of node of T1: node of T2
        The isomorphism mapping f such that (u, v) is in E_T1 if and only if
        (f(u), f(v)) is in E_T2. This dictionary is empty when there is no
        isomorphism between the trees.

    Notes
    -----
    This runs in O(n) time for trees with n nodes.

    """
    # If the trees differ in order, return false.
    if T1.order() != T2.order():
        return False, {}

    # If the trees are emtpy graphs, then they're isomorphic by definition.
    if T1.order() == 0:
        return True, {}

    # If trees have more than one node, verify that they're indeed trees.
    assert nx.is_tree(T1)
    assert nx.is_tree(T2)

    # Another shortcut is that the degree sequences need to be the same.
    degrees_T1 = Counter([d for (n, d) in T1.degree()])
    degrees_T2 = Counter([d for (n, d) in T2.degree()])
    if degrees_T1 != degrees_T2:
        return False, {}

    # Find the centers of T1 and T2.
    centers_T1 = get_centers_of_tree(T1)
    centers_T2 = get_centers_of_tree(T2)

    # If they differ on the amount of centers, return false.
    if len(centers_T1) != len(centers_T2):
        return False, {}

    # Otherwise, form every posible pairs of centers of T1 with centers of T2
    # and check if the rooted trees are isomorphic. If one of them are, return
    # the found isomorphism.
    for u in centers_T1:
        for v in centers_T2:
            is_iso, iso = rooted_tree_isomorphism_n(T1, u, T2, v)
            if is_iso:
                return is_iso, iso

        # If none of the previous trees were isomorphic, then return false.
        return False, {}


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


# figure out the level of each node, with 0 at root
def assign_levels(G, root):
    level = {}
    level[root] = 0
    for (v1, v2) in nx.bfs_edges(G, root):
        level[v2] = level[v1] + 1

    return level


# now group the nodes at each level
def group_by_levels(levels):
    L = {}
    for (n, lev) in levels.items():
        if lev not in L:
            L[lev] = []
        L[lev].append(n)

    return L


# now lets get the isomorphism by walking the ordered_children
def generate_isomorphism(v, w, M, ordered_children):
    # make sure tree1 comes first
    assert v < w
    M.append((v, w))
    for i, (x, y) in enumerate(zip(ordered_children[v], ordered_children[w])):
        generate_isomorphism(x, y, M, ordered_children)


def rooted_tree_isomorphism(t1, root1, t2, root2):
    """
    Given two rooted trees `t1` and `t2`,
    with roots `root1` and `root2` respectivly
    this routine will determine if they are isomorphic.

    These trees may be either directed or undirected,
    but if they are directed, all edges should flow from the root.

    It returns the isomorphism, a mapping of the nodes of `t1` onto the nodes
    of `t2`, such that two trees are then identical.

    Note that two trees may have more than one isomorphism, and this
    routine just returns one valid mapping.

    Parameters
    ----------
    `t1` :  NetworkX graph
        One of the trees being compared

    `root1` : a node of `t1` which is the root of the tree

    `t2` : undirected NetworkX graph
        The other tree being compared

    `root2` : a node of `t2` which is the root of the tree

    This is a subroutine used to implement `tree_isomorphism`, but will
    be somewhat faster if you already have rooted trees.

    Returns
    -------
    isomorphism : list
        A list of pairs in which the left element is a node in `t1`
        and the right element is a node in `t2`.  The pairs are in
        arbitrary order.  If the nodes in one tree is mapped to the names in
        the other, then trees will be identical. Note that an isomorphism
        will not necessarily be unique.

        If `t1` and `t2` are not isomorphic, then it returns the empty list.
    """

    assert nx.is_tree(t1)
    assert nx.is_tree(t2)

    # get the rooted tree formed by combining them
    # with unique names
    (dT, namemap, newroot1, newroot2) = root_trees(t1, root1, t2, root2)

    # compute the distance from the root, with 0 for our
    levels = assign_levels(dT, 0)

    # height
    h = max(levels.values())

    # collect nodes into a dict by level
    L = group_by_levels(levels)

    # each node has a label, initially set to 0
    label = {v: 0 for v in dT}
    # and also ordered_labels and ordered_children
    # which will store ordered tuples
    ordered_labels = {v: () for v in dT}
    ordered_children = {v: () for v in dT}

    # nothing to do on last level so start on h-1
    # also nothing to do for our fake level 0, so skip that
    for i in range(h - 1, 0, -1):
        # update the ordered_labels and ordered_childen
        # for any children
        for v in L[i]:
            # nothing to do if no children
            if dT.out_degree(v) > 0:
                # get all the pairs of labels and nodes of children
                # and sort by labels
                s = sorted((label[u], u) for u in dT.successors(v))

                # invert to give a list of two tuples
                # the sorted labels, and the corresponding children
                ordered_labels[v], ordered_children[v] = list(zip(*s))

        # now collect and sort the sorted ordered_labels
        # for all nodes in L[i], carrying along the node
        forlabel = sorted((ordered_labels[v], v) for v in L[i])

        # now assign labels to these nodes, according to the sorted order
        # starting from 0, where idential ordered_labels get the same label
        current = 0
        for i, (ol, v) in enumerate(forlabel):
            # advance to next label if not 0, and different from previous
            if (i != 0) and (ol != forlabel[i - 1][0]):
                current += 1
            label[v] = current

    # they are isomorphic if the labels of newroot1 and newroot2 are 0
    isomorphism = []
    if label[newroot1] == 0 and label[newroot2] == 0:
        generate_isomorphism(newroot1, newroot2, isomorphism, ordered_children)

        # get the mapping back in terms of the old names
        # return in sorted order for neatness
        isomorphism = [(namemap[u], namemap[v]) for (u, v) in isomorphism]

    return isomorphism


@not_implemented_for("directed", "multigraph")
def tree_isomorphism(t1, t2):
    """
    Given two undirected (or free) trees `t1` and `t2`,
    this routine will determine if they are isomorphic.
    It returns the isomorphism, a mapping of the nodes of `t1` onto the nodes
    of `t2`, such that two trees are then identical.

    Note that two trees may have more than one isomorphism, and this
    routine just returns one valid mapping.

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

    Notes
    -----
    This runs in O(n*log(n)) time for trees with n nodes.
    """

    assert nx.is_tree(t1)
    assert nx.is_tree(t2)

    # To be isomrophic, t1 and t2 must have the same number of nodes.
    if nx.number_of_nodes(t1) != nx.number_of_nodes(t2):
        return []

    # Another shortcut is that the sorted degree sequences need to be the same.
    degree_sequence1 = sorted(d for (n, d) in t1.degree())
    degree_sequence2 = sorted(d for (n, d) in t2.degree())

    if degree_sequence1 != degree_sequence2:
        return []

    # A tree can have either 1 or 2 centers.
    # If the number doesn't match then t1 and t2 are not isomorphic.
    center1 = nx.center(t1)
    center2 = nx.center(t2)

    if len(center1) != len(center2):
        return []

    # If there is only 1 center in each, then use it.
    if len(center1) == 1:
        return rooted_tree_isomorphism(t1, center1[0], t2, center2[0])

    # If there both have 2 centers,  then try the first for t1
    # with the first for t2.
    attemps = rooted_tree_isomorphism(t1, center1[0], t2, center2[0])

    # If that worked we're done.
    if len(attemps) > 0:
        return attemps

    # Otherwise, try center1[0] with the center2[1], and see if that works
    return rooted_tree_isomorphism(t1, center1[0], t2, center2[1])
