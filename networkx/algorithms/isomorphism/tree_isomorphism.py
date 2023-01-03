"""An algorithm for finding if two undirected trees are isomorphic. 

This algorithm uses a routine to tell if two rooted trees (trees with a
specified root node) are isomorphic, which may be independently useful.

References
----------
  .. [1] A. V. Aho, J. E. Hopcroft and J. D. Ullman, "The Desing And Analysis of
     Computer Algorithms", Addison Wesley Publishing Company, (1974): 78-86.

  .. [2] M. Suderman, "Homework Assignment 5", McGill University SOCS 308-250B,
     (Winter 2002): http://crypto.cs.mcgill.ca/~crepeau/CS250/2004/HW5+.pdf

  .. [3] G. Valiente, "Algorithms on Trees and Graphs", Springer (2002): 
     151-166.

  .. [4] M. Carrasco-Ruiz, "Herramientas para el Manejo Computacional de
     Gráficas", Bachelor of Science Thesis, UNAM, (2022): 55-77.

"""

from collections import Counter, defaultdict

import networkx as nx
from networkx.utils.decorators import not_implemented_for

__all__ = ["rooted_tree_isomorphism", "tree_isomorphism"]


def get_initial_maps_and_height(T, root):
    """Get the initial maps and height used by the rooted tree isomorphism alg.

    Define and return the following maps: LEVELS, VALUES, PARENTHOOD and
    CHILDREN. Also return the rooted tree's height.

    For the LEVELS map. Let h be the height of the tree. The amount of
    levels a tree has is equal to its height. If a vertex v is on the i-th
    level, then its childs are on the (i-1)-th level. Thus, by definition, the
    only vertex in the h-th level is the root of the tree and the only vertices
    on the level 0 are leaves. Define a LEVELS map such that, for each i in
    {0,...,h}, LEVELS(i) is the set of vertices found on the i-th level of T.

    For the VALUES map. A value of a vertex corresponds to the structure it has
    on the rooted tree. Informally, the structure of a vertex can be thought as
    the structure or "form" the sub-tree rooted on v has. Define the initial
    values of the VALUES map such that, for every vertex v in the rooted tree,
    if v is a leaf then v's initial value is 0, otherwise its defined as -1.

    The PARENTHOOD map is the parent-child relationship obtained when traversing
    the rooted tree, in this case the algorithm used is BFS.

    For the CHILDREN map. Defines a map CHILDREN where CHILDREN(v) is the
    ordered list of children of v in the rooted tree. This map determines who
    are the parents of the leaves found on the 0-th level.

    Parameters
    ----------
    T : NetworkX Graph
        The rooted tree.

    root : node
        The root of the tree.

    Returns
    -------
    LEVELS : dict of int: set of nodes
        A LEVELS map such that, for each i in {0,...,h}, LEVELS(i) is the set of
        vertices found on the i-th level of T.

    VALUES : dict of node: int
        A VALUES map such that, for each vertex v in the rooted tree, if v is a
        leaf then v's initial value is 0, otherwise its defined as -1.

    CHILDREN : dict of node: list of nodes
        A CHILDREN map such that CHILDREN(v) is the ordered list of children
        of v in the rooted tree. This map determines who are the parents of the
        leaves found on the 0-th level.

    PARENTHOOD : dict of node: node
        The parenthood map of the rooted tree.

    height : int
        The height of the rooted tree.

    Note
    ----
    This algorithm runs in O(n) time and space.

    """
    # Define an empty map for LEVELS, VALUES, CHILDREN and PARENTHOOD.
    LEVELS = defaultdict(set)
    CHILDREN = defaultdict(list)
    VALUES = {}
    PARENTHOOD = {}

    # Auxiliary variables.
    non_leaves = set()
    leaves = set()

    from_distance = defaultdict(set)
    distance_to_root = {}
    distance_to_root[root] = 0
    from_distance[0].add(root)
    max_distance_to_root = 0

    # Perform a single BFS traversal to obtain the necessary information.
    for (parent, child) in nx.bfs_edges(T, root):
        # Define child's parent.
        PARENTHOOD[child] = parent

        # The parent can't be a leave.
        non_leaves.add(parent)

        # If a vertex was thought to be a leave but has a child, then it isn't a
        # leave.
        if parent in leaves:
            leaves.remove(parent)

        # The child can be a leave.
        leaves.add(child)

        # Define d(child, root) = d(parent, root) + 1
        distance_to_root[child] = distance_to_root[parent] + 1

        # Add the child to the set of vertices have the same distance to the
        # root.
        d_child = distance_to_root[child]
        from_distance[d_child].add(child)

        # If the previous distance is greater than the max, update it.
        if max_distance_to_root < distance_to_root[child]:
            max_distance_to_root = distance_to_root[child]

    # The max distance to the root is the rooted tree's height.
    height = max_distance_to_root

    # Build the LEVELS map.
    current_lvl = height
    for d in range(height + 1):
        for v in from_distance[d]:
            LEVELS[current_lvl].add(v)

        current_lvl -= 1

    # Build the VALUES map.
    for v in non_leaves:
        VALUES[v] = -1

    for v in leaves:
        VALUES[v] = 0

    # Traverse all the vertices found on the 0-th level and set the initial
    # children for the CHILDREN map.
    for v in LEVELS[0]:
        # If the current vertex has a parent, add the child to the parent's
        # list of children.
        if v in PARENTHOOD:
            u = PARENTHOOD[v]
            CHILDREN[u].append(v)

    return LEVELS, VALUES, CHILDREN, PARENTHOOD, height


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
    STRUCT : dict of node: counter
        A STRUCT map such that struct(v) is the structure (counter of ints)
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


def group_structures_in_level(levels, values, struct, i):
    """Obtain the structures found on the i-th level as a Counter.

    Build a Counter which contains the list representation of the structures of
    the vertices found on the i-th level. Also, define a mapping of structures
    to the vertices that have said structure.

    Parameters
    ----------
    levels: dict of int: set of nodes
        The LEVELS map such that LEVELS(i) are the vertices found on the i-th
        level of the rooted tree.

    values : dict of node: int
        The VALUES map such that, for each vertex v in the rooted tree,
        VALUES(v) is the value associated to v.

    struct : dict of node: counter of natural numbers
        The STRUCT map such that struct(v) is the structure corresponding to
        vertex v.

    i : int
        The current level of the rooted tree.

    Returns
    -------
    structures_on_lvl : counter of lists of ints
        A counter that correspond to the list representation of the structures
        of the vertices found on the i-th level.

    MS : dict of natural multiset: set of nodes
        A mapping of structures to the vertices that have said structure.

    Note
    ----
    This algorithm runs in O(m_{i-1} + m_i) time and space where m_{j} are the
    vertices found on the j-th level of the rooted tree.

    """
    # Define an empty counter of lists of ints.
    S = Counter()

    # Define a mapping of structures to the vertices that have said structure.
    MS = defaultdict(set)

    # Traverse all vertices on the i-th level.
    for u in levels[i]:
        # If the vertex is not leave, add its structure to the list.
        if values[u] != 0:
            # Get the structure (counter) associated with u.
            c = struct[u]

            # Get the list representation of the counter.
            lc = tuple(x for x in range(max(c) + 1) for _ in range(c[x]))

            # Add the list representation to the counter.
            S[lc] += 1

            # Indicate that c is a structure that u has.
            MS[lc].add(u)

    return S, MS


def update_values(
    C,
    MS_T1,
    MS_T2,
    values_T1,
    values_T2,
    children_T1,
    children_T2,
    parenthood_T1,
    parenthood_T2,
    leaves_T1,
    leaves_T2,
):
    """Updates the values of current level.

    Given a counter of multisets, which are the structures found on the current
    level of both trees. Updates the values of the vertices found on the map MS.
    Two vertices on the same level have the same value if and only if they have
    the same structure.

    It also defines an order for the children of the vertices in the next level.

    Parameters
    ----------
    C : Counter of lists of ints
        The counter of the list representation of the structures of the level.

    MS_T1 : dict of tuples of ints: set of nodes
        A mapping of structures to the vertices of T1 that have said structure.

    MS_T2 : dict of tuples of ints: set of nodes
        A mapping of structures to the vertices of T2 that have said structure.

    values_T1 : dict of node: int
        The VALUES map such that, for each vertex v in the rooted tree T1,
        VALUES(v) is the value associated to v.

    values_T2 : dict of node: int
        The VALUES map such that, for each vertex v in the rooted tree T2,
        VALUES(v) is the value associated to v.

    children_T1 : dict of node: set of nodes
        A mapping CHILDREN such that CHILDREN(v) is the ordered list of children
        of v in the rooted tree T1.

    children_T2 : dict of node: set of nodes
        A mapping CHILDREN such that CHILDREN(v) is the ordered list of children
        of v in the rooted tree T1.

    parenthood_T1 : dict of node: node
        The parenthood map defined for the rooted tree T1.

    parenthood_T2 : dict of node: node
        The parenthood map defined for the rooted tree T2.

    leaves_T1 : set of nodes
        The leaves of the current level in the rooted tree T1.

    leaves_T2 : set of nodes
        The leaves of the current level in the rooted tree T1.

    Note
    ----
    This algorithm runs in O(m_{i-1} + m_i) time and space where m_{j} are the
    vertices found on the j-th level of both rooted trees.

    """
    # The first vertices in the order of children are the leaves.
    for v in leaves_T1:
        # If it exists, get the leave's parent; the previous case is considered
        # for the root, who doesn't have a parent.
        if v in parenthood_T1:
            u = parenthood_T1[v]

            # Add the child to the list of children of the parent.
            children_T1[u].append(v)

    # Repeat the process with the leaves of T2.
    for v in leaves_T2:
        # If it exists, get the leave's parent; the previous case is considered
        # for the root, who doesn't have a parent.
        if v in parenthood_T2:
            u = parenthood_T2[v]

            # Add the child to the list of children of the parent.
            children_T2[u].append(v)

    # Traverse all the structures contained in the counter. As the current level
    # of both trees share the same structures in the same amount, we can use
    # this traversal to update the vertices of both trees.

    # The current value is 1 as the value 0 is reserved for leaves.
    current_val = 1
    for struct in C:
        # Get the vertices of T1 who have the current structure.
        for v in MS_T1[struct]:
            # Update the value of v.
            values_T1[v] = current_val

            # Add v to the list of children of his parent, if it has one.
            if v in parenthood_T1:
                u = parenthood_T1[v]
                children_T1[u].append(v)

        # Get the vertices of T2 who have the current structure.
        for v in MS_T2[struct]:
            # Update the value of v.
            values_T2[v] = current_val

            # Add v to the list of children of his parent, if it has one.
            if v in parenthood_T2:
                u = parenthood_T2[v]
                children_T2[u].append(v)

        # The next unique structure should have a different value.
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


def levels_verification(T1, root_T1, T2, root_T2):
    """Check for all levels that both trees share the same structure.

    For each level i in T1, check that all the structures present on the i-th
    level are also present in i-th level of T2. If all the levels are the same
    for both trees, return true.

    Parameters
    ----------
    T1 : NetworkX Graph
        The rooted tree T1.

    root_T1 : node
        The root of the rooted tree T1.

    T2 : NetworkX Graph
        The rooted tree T2.

    root_T2 : node
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
    # Get the intial maps and height for each tree.
    (
        levels_T1,
        values_T1,
        children_T1,
        parenthood_T1,
        height_T1,
    ) = get_initial_maps_and_height(T1, root_T1)

    (
        levels_T2,
        values_T2,
        children_T2,
        parenthood_T2,
        height_T2,
    ) = get_initial_maps_and_height(T2, root_T2)

    # If the trees differ in height, return false.
    if height_T1 != height_T2:
        return False, {}

    # If both trees have height 0, then there are only conformed by its roots,
    # they're isomorphic.
    if height_T1 == 0:
        return True, {root_T1: root_T2}

    # For every level i, check that both trees have the same amount of
    # vertices on the i-th level. If they differ for some level, return
    # false.
    for i in range(height_T1):
        if len(levels_T1[i]) != len(levels_T2[i]):
            return False, {}

    # Start at level 1 as all the vertices at level 0 are leaves. Check that
    # all the structures present on the i-th level are also present in i-th
    # level of T2.
    for current_level in range(1, height_T1 + 1):
        # Assign the structures for the vertices of the current level for T1 and
        # T2.
        struct_T1, leaves_T1 = assign_structure(
            parenthood_T1, levels_T1, values_T1, current_level
        )

        struct_T2, leaves_T2 = assign_structure(
            parenthood_T2, levels_T2, values_T2, current_level
        )

        # Build the counter of structures and the mapping.
        C_T1, MS_T1 = group_structures_in_level(
            levels_T1, values_T1, struct_T1, current_level
        )

        C_T2, MS_T2 = group_structures_in_level(
            levels_T2, values_T2, struct_T2, current_level
        )

        # If the counters are different, return false.
        if C_T1 != C_T2:
            return False, {}

        # Otherwise, update the values and the children of both trees.
        update_values(
            C_T1,
            MS_T1,
            MS_T2,
            values_T1,
            values_T2,
            children_T1,
            children_T2,
            parenthood_T1,
            parenthood_T2,
            leaves_T1,
            leaves_T2,
        )

        # Move to the next level.
        current_level += 1

    # If all the previous levels are equal, then build an isomorphism with the
    # previous information.
    isomorphism = build_isomorphism(root_T1, root_T2, children_T1, children_T2)

    return True, isomorphism


def rooted_tree_isomorphism(T1, root_T1, T2, root_T2):
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

    # Check that all levels have the same structure.
    return levels_verification(T1, root_T1, T2, root_T2)


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


def tree_isomorphism(T1, T2):
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
            is_iso, iso = rooted_tree_isomorphism(T1, u, T2, v)
            if is_iso:
                return is_iso, iso

        # If none of the previous trees were isomorphic, then return false.
        return False, {}
