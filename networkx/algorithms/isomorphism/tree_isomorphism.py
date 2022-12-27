"""
An algorithm for finding if two undirected trees are isomorphic, and if so 
returns an isomorphism between the two sets of nodes.

This algorithm uses a routine to tell if two rooted trees (trees with a
specified root node) are isomorphic, which may be independently useful.

References
----------
  .. [1] A. V. Aho, J. E. Hopcroft y J. D. Ullman, The Desing And Analysis of
     Computer Algorithms, Addison Wesley Publishing Company, 1974.

  .. [2] M. Suderman, Homework Assignment 5, McGill University SOCS 308-250B,
     Winter 2002. http://crypto.cs.mcgill.ca/~crepeau/CS250/2004/HW5+.pdf

  .. [3] G. Valiente, Algorithms on Trees and Graphs, Springer 2002.

  .. [4] M. Carrasco-Ruiz, Herramientas para el Manejo Computacional de
     Gráficas, Bachelor of Science Thesis, UNAM, 2021.
"""

import networkx as nx
import numpy as np
from networkx.utils.decorators import not_implemented_for

__all__ = ["rooted_tree_isomorphism", "tree_isomorphism"]

class NaturalMultiset():
    """
    Class to represent a multiset M of natural numbers (0, ..., n). Define a
    multiset as a set where repetition of elements is allowed. Mathematically, a
    multiset M is an ordered pair (X, m) where X is a set and m : X -> N such
    that, for every x in X, m(x) is the number of ocurrences of x in M.
    
    This class only has the neccessary operations for the tree isomorphism
    algorithm to work; it is not expected to be used anywhere else.
    
    Parameters
    ----------
    X : set
        The set of elements of M.
    
    m : dictionary
        The number of occurrences of the elements of X in M.

    length : int
        The amount of elements in M.
    """
    
    def __init__(self):
        """
        Initializes an empty multiset.
        """
        self.X = set()
        self.m = {}
        self.length = 0
        
    def add(self, x):
        """
        Adds an element to the multiset. If the element is in the multiset,
        then increase the number of occurrences of said element in the map.
        
        Parameters
        ----------
        x : any
            The value to add to the multiset.

        Notes
        -----
        This runs in O(1) time and space.
        """
        if x in self.X:
            self.m[x] = self.m[x] + 1
        else:
            self.X.add(x)
            self.m[x] = 1

        self.length = self.length + 1
        
    def contains(self, x):
        """
        Returns whether the multiset contains a given element.
        """
        return (x in self.X)
            
    def to_list(self):
        """
        Returns the elements of the multiset as an ordered list. The method
        is basically a bucket sort.
        
        Returns
        -------
        A sorted list of the elements of the multiset.
        
        Notes
        -----
        This runs in O(|X| + k) where k = max(X).
        """
        # Max value of X.
        m = max(self.X)
        
        # Define an array of size m.
        A = np.zeros(m+1, dtype='int')
        
        # The array S now keeps the number of occurrences.
        for x in self.X:
            A[x] = self.m[x]
        
        # Build a sorted list of elements.
        S = []
        for i in range(m+1):
            for j in range(A[i]):
                S.append(i)
        
        return S
    
    def from_list(self, L):
        """
        Adds the elements from the list to the multiset.
        
        Parameters
        ----------
        L : list
            The list of naturals to add to the multiset.
        
        Notes
        -----
        This runs in O(|L|).
        """
        for x in L:
            self.add(x)
            
    def __eq__(self, M):
        """
        Two multisets M1 = (X1, m1) and M2 = (X2, m2) are equal if and only
        if X1 = X2 and m1 = m2.
        """
        return (self.X == M.X) and (self.m == M.m)

    def __len__(self):
        """
        The length of a multiset is defined as the amount of elements it
        contains.
        """
        return self.length

def categorize_entries(S):
    """
    Given a list of lists whose entries are numbers between 0 and m. The
    function categorize_entries returns a function (map or dict) NONEMPTY : N ->
    P(N) such that NONEMPTY(i) are the numbers in the i-th position of some list
    in S; this numbers are sorted. For example, given ((1), (1, 2, 3), (1, 2,
    2)), NONEMPTY(2) = [2, 3].
    
    Parameters
    ----------
    S : list
        The list of lists of natural numbers.
    
    Returns
    -------
    A NONEMPTY: N -> P(N) function such that NONEMPTY(i) are the numbers in the 
    i-th position of some list in S; this numbers are sorted.
    
    References
    ----------
        .. [1] A. V. Aho, J. E. Hopcroft y J. D. Ullman, The Desing And Analysis
               of Computer Algorithms, Addison Wesley Publishing Company, 1974.
               Pages 80-82.

        .. [4] M. Carrasco-Ruiz, Herramientas para el Manejo Computacional de
               Gráficas, Bachelor of Science Thesis, UNAM, 2021.
    
    Notes
    -----
    This algorithm runs in O(l_total + m) time and O(l_total) space, where 
    l_total is the sum of the lengths of the lists in S and m is the max value
    of all the lists in S.
    """
    # Define the function NONEMPTY.
    NONEMPTY = {}
    
    # The max length found in S.
    l_max = max([len(s) for s in S])
    
    # Traverse all the entries contained in the lists of S.
    for i in range(l_max):
        # Define a multiset to keep the entries found in the i-th position.
        M = NaturalMultiset()
        
        for s in S:
            # Only consider lists of length greater or equal than i, and whose
            # i-th entry is not already contained in the multiset.
            if len(s) < (i+1) or M.contains(s[i]):
                continue
            else:
                M.add(s[i])

        # Obtain a sorted representation of M.
        NONEMPTY[i] = M.to_list()

    return NONEMPTY

def categorize_lists(S):
    """
    Given a list of lists whose entries are numbers between 0 and m. The
    function categorize_lists returns a function (map or dict) LENGTH such that
    LENGTH(i) are the lists of S with length i. For example, given ((1), (1, 2,
    3), (1, 2, 2)), NONEMPTY(3) = [(1, 2, 3), (1, 2, 2)].
    
    Parameters
    ----------
    S : list
        The list of lists of natural numbers.
    
    Returns
    -------
    A LENGTH function such that LENGTH(i) are the lists of S with length i.
    
    References
    ----------
        .. [1] A. V. Aho, J. E. Hopcroft y J. D. Ullman, The Desing And Analysis 
               of Computer Algorithms, Addison Wesley Publishing Company, 1974.
               Pages 80-82.

        .. [4] M. Carrasco-Ruiz, Herramientas para el Manejo Computacional de
               Gráficas, Bachelor of Science Thesis, UNAM, 2021.
    
    Notes
    -----
    This algorithm runs in O(|S|) time and space.
    """
    # Define the function LENGTH.
    LENGTH = {}
    
    # Traverse the lists in S and add them to the LENGTH.
    for s in S:
        if len(s) in LENGTH:
            LENGTH[len(s)].append(s)
        else:
            LENGTH[len(s)] = [s]
            
    return LENGTH

def sort_lists_of_naturals(S):
    """
    Given a list of lists whose entries are numbers between 0 and m. The
    function sort_lists_of_naturals performs an algorithm similar to bucket sort
    to return a sorted list with the elements of S. The expected order is a
    lexicographical order.
    
    Parameters
    ----------
    S : list
        The list of lists of natural numbers.
    
    Returns
    -------
    A sorted list with the elements of S.
    
    References
    ----------
        .. [1] A. V. Aho, J. E. Hopcroft y J. D. Ullman, The Desing And Analysis 
               of Computer Algorithms, Addison Wesley Publishing Company, 1974.
               Pages 80-82.

        .. [4] M. Carrasco-Ruiz, Herramientas para el Manejo Computacional de
               Gráficas, Bachelor of Science Thesis, UNAM, 2021.
    
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
    A = [[] for i in range(m+1)]
    
    print(A)
    
    # The max length found in S.
    l_max = max([len(s) for s in S])
    
    # Obtain the NONEMPTY and LENGTH functions.
    NONEMPTY = categorize_entries(S)
    LENGTH = categorize_lists(S)
    
    l = l_max
    while (l >= 1):
        # All of the elements in Q have length greater than l. For each element
        # s in Q, append q to the queue A[s[l]].
        while (len(Q) > 0):
            s = Q.pop()
            A[s[l-1]].append(s)

        # Add the lists s of size l to the queue A[s[l]] if there are any.
        if l in LENGTH:
            for s in LENGTH[l]:
                A[s[l-1]].append(s)
            
        # Sort the elements of A according to its l-th entry.
        for i in NONEMPTY[l-1]:
            while (len(A[i]) > 0):
                s = A[i].pop()
                Q.append(s)
        
        # Proceed with the lists of size l-1.
        l = l - 1
    
    # Q now contains all of the elements of S sorted lexicographically.
    return Q

def sort_natural_multisets(S):
    """
    Given a list of multisets whose entries are numbers between 0 and m. The
    function sort_natural_multisets returns a sorted list with the elements of
    S. If each multiset is represented as a string or a list of naturals, the
    expected order is a lexicographical order taking into consideration the
    previous representation.
    
    Parameters
    ----------
    S : list
        The list of natural multisets.
    
    Returns
    -------
    A sorted list with the elements of S.
    
    References
    ----------
        .. [1] A. V. Aho, J. E. Hopcroft y J. D. Ullman, The Desing And Analysis 
               of Computer Algorithms, Addison Wesley Publishing Company, 1974.
               Pages 80-82.

        .. [4] M. Carrasco-Ruiz, Herramientas para el Manejo Computacional de
               Gráficas, Bachelor of Science Thesis, UNAM, 2021.
    
    Notes
    -----
    This algorithm runs in O(M_total + k) time and O(M_total) space, where 
    M_total is the sum of the lengths of the multisets in S and k is the max 
    value of all the multisets in S.
    """
    # Define a list of lists.
    L = []
    
    # For each multiset in S, add its list representation to S.
    for m in S:
        lm = m.to_list()
        L.append(lm)
        
    # Obtain an ordering of S.
    sorted_L = sort_lists_of_naturals(L)
    
    # Transform each list into a multiset.
    sorted_S = []
    for l in sorted_L:
        m = NaturalMultiset()
        m.from_list(l)
        sorted_S.append(m)
    
    # Return the sorted multisets.
    return sorted_S
        

def get_levels(T, root, height):
    """
    Returns a function (map or dict) M: N -> P(V) such that, for each i in
    {0,...,h}, M(i) is the set of vertices that are found in the i-th level
    of T.
    
    Let h be the height of the tree. The amount of levels a tree has is equal to
    its height. If a vertex v is in the i-th level, then its childs are in the
    (i-1)-th level. Thus, by definition, the only vertex in the h-th level is
    the root of the tree and the only vertices in the level 0 are leaves.
    
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
    M : dictionary
        A map M: N -> P(V) such that, for each i in {0,...,h}, M(i) is the set
        of vertices that are found in the i-th level of T.
    
    Notes
    -----
    The algorithm runs in O(n) time and space.
    """
    # Map M such that M(i) is the set of vertices that are in the i-th level.
    lvl = {}
    
    # Map in_lvl such that in_lvl(v) is the level where v is found.
    in_lvl = {}
    
    # Define the root height.
    in_lvl[root] = height
    
    # Perform a BFS traversal to fill the in_lvl function.
    for (parent, child) in nx.bfs_edges(T, root):
        in_lvl[child] = in_lvl[parent] - 1
        
    # Traverse all vertices and group them by levels.
    for v in in_lvl.keys():
        l = in_lvl[v]
        if l in lvl:
            lvl[l].add(v)
        else:
            lvl[l] = {v}
            
    return lvl

def get_initial_values(T, root):
    """
    Returns a function (map or dict) M: N -> P(V) such that, for every
    vertex v in the tree T, if v is a leave then v's initial value is 0,
    otherwise its defined as -1.
    
    Parameters
    ----------
    T : NetworkX Graph
        The rooted tree.
    
    root : node
        The root of the tree.
    
    Returns
    -------
    M : dictionary
        A map M: N -> P(V) such that, for each vertex v in the tree T, if v is 
        a leave then v's initial value is 0, otherwise its defined as -1.
    
    Notes
    -----
    The algorithm runs in O(n) time and space.
    """
    # Map M such that M(v) is initial value of v.
    vals = {}

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
        vals[v] = -1
    
    # Set the initial value of the leaves as 0.    
    for v in leaves:
        vals[v] = 0
        
    return vals

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
