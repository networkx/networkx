import random
import time

import networkx as nx
from networkx.algorithms.isomorphism.tree_isomorphism import (
    NaturalMultiset,
    categorize_entries,
    categorize_lists,
    get_levels,
    get_initial_values,
    rooted_tree_isomorphism,
    tree_isomorphism,
)
from networkx.classes.function import is_directed

# Tests the function to_list from the Natural Multiset class.
def test_multiset_to_list():
    M = NaturalMultiset()
    # Add the values (0, 1, 2, 0, 0, 1)
    M.add(0)
    M.add(1)
    M.add(2)
    M.add(0)
    M.add(0)
    M.add(1)
    
    expected_list = [0, 0, 0, 1, 1, 2]
    
    obtained_list = M.to_list()
    
    assert expected_list == obtained_list
    
# Tests the function __eq__ from the Natural Multiset class.
def test_multiset__eq__():
    M1 = NaturalMultiset()
    M2 = NaturalMultiset()
    
    # Empty multisets should be equal.
    assert M1 == M2
    
    # Add different elements to M1 and M2.
    M1.add(1)
    M2.add(2)
    
    assert M1 != M2
    
    # Add the values that are missing to each multiset.
    M1.add(2)
    M2.add(1)
    
    assert M1 == M2
    
    # Increase the occurrences of one element in each multiset.
    M1.add(1)
    assert M1 != M2
    
    M2.add(1)
    assert M1 == M2

# Tests the function __len__ from the Natural Multiset class.
def test_multiset__len__():
    M = NaturalMultiset()
    
    # An empty multiset length is 0.
    assert len(M) == 0
    
    # Add different elements and check the length.
    for i in range(10):
        M.add(i)
        assert len(M) == (i + 1)

    # Add the same elements as before and check the length.
    for i in range(10):
        M.add(i)
        assert len(M) == (11 + i)

# Tests the function categorize_entries. The returned function should behave
# like a function NONEMPTY : N -> P(N) such that NONEMPTY(i) are the numbers in
# the i-th position of some list in S; this numbers are sorted
def test_categorize_entries():
    # An arbitrary list of lists of natural numbers.
    S = [
        [0, 0, 1, 2, 3],
        [1, 2, 3],
        [0, 1, 1, 4],
        [3, 3, 4],
        [4],
        [4, 4, 5],
    ]
    
    # Expected NONEMPTY function.
    expected_NONEMPTY = {
        0 : [0, 1, 3, 4],
        1 : [0, 1, 2, 3, 4],
        2 : [1, 3, 4, 5],
        3 : [2, 4],
        4 : [3],
    }
    
    # Obtained NONEMPTY function.
    obtained_NONEMPTY = categorize_entries(S)
    
    assert expected_NONEMPTY == obtained_NONEMPTY

# Tests the function categorize_lists. The returned function should behave like
# a function LENGTH such that LENGTH(i) are the lists of S with length i.
def test_categorize_lists():
    # An arbitrary list of lists of natural numbers.
    S = [
        [0, 0, 1, 2, 3],
        [1, 2, 3],
        [0, 1, 1, 4],
        [3, 3, 4],
        [4],
        [4, 4, 5],
    ]
    
    # Expected LENGTH function.
    expected_LENGTH = {
        1: [[4]],
        3: [[1, 2, 3], [3, 3, 4], [4, 4, 5]],
        4: [[0, 1, 1, 4]],
        5: [[0, 0, 1, 2, 3]],
    }
    
    # Obtained LENGTH function.
    obtained_LENGTH = categorize_lists(S)
    
    assert expected_LENGTH == obtained_LENGTH

# Test the get_levels function. The returned function should behave like a
# function M: N -> P(V) such that, for each i in {0,...,h}, M(i) is the set of
# vertices that are found in the i-th level of T.
def test_isomorphism_trees_get_levels():
    # Test for an arbitrary graph.
    edges_t1 = [("v0", "v1"), ("v0", "v2"), ("v0", "v3"),
                ("v1", "v4"), ("v1", "v5"), ("v3", "v6")]
    T1 = nx.Graph(edges_t1)

    # Expected level function.
    expected_levels = {
        2 : {"v0"},
        1 : {"v1", "v2", "v3"},
        0 : {"v4", "v5", "v6"},
    }
    
    # Obtained level function.
    obtained_levels = get_levels(T1, "v0", 2)

    assert expected_levels == obtained_levels
    
    # Test for another arbitrary graph.
    edges_t2 = [("u3", "u4"), ("u3", "u2"),
                ("u4", "u5"), ("u4", "u6"), ("u4", "u7"),
                ("u2", "u1"), ("u7", "u8"), ("u1", "u0")]
    T2 = nx.Graph(edges_t2)
    
    # Expected level function.
    expected_levels = {
        3: {"u3"},
        2: {"u2", "u4"},
        1: {"u5", "u6", "u7", "u1"},
        0: {"u8", "u0"},
    }
    
    obtained_levels = get_levels(T2, "u3", 3)
    
    assert expected_levels == obtained_levels

# Test the get_initial_values function. The returned function should behave like
# a function M: N -> P(V) such that, such that, for every vertex v in the tree
# T, if v is a leave then v's initial value is 0, otherwise its defined as -1.
def test_isomorphism_trees_set_initial_values():
    # Test for an arbitrary graph.
    edges_t1 = [("v0", "v1"), ("v0", "v2"), ("v0", "v3"),
                ("v1", "v4"), ("v1", "v5"), ("v3", "v6")]
    T1 = nx.Graph(edges_t1)

    # Expected level function.
    expected_values = {
        "v0" : -1,
        "v1" : -1,
        "v2" : 0,
        "v3" : -1,
        "v4" : 0,
        "v5" : 0,
        "v6" : 0,
    }
    
    # Obtained level function.
    obtained_values = get_initial_values(T1, "v0")

    assert expected_values == obtained_values
    
    # Test for another arbitrary graph.
    edges_t2 = [("u3", "u4"), ("u3", "u2"),
                ("u4", "u5"), ("u4", "u6"), ("u4", "u7"),
                ("u2", "u1"), ("u7", "u8"), ("u1", "u0")]
    T2 = nx.Graph(edges_t2)
    
    # Expected level function.
    expected_levels = {
        "u3" : -1,
        "u4" : -1,
        "u2" : -1,
        "u5" : 0,
        "u6" : 0,
        "u7" : -1,
        "u1" : -1,
        "u8" : 0,
        "u0" : 0,
    }
    
    obtained_levels = get_initial_values(T2, "u3")
    
    assert expected_values == obtained_values

# have this work for graph
# given two trees (either the directed or undirected)
# transform t2 according to the isomorphism
# and confirm it is identical to t1
# randomize the order of the edges when constructing
def check_isomorphism(t1, t2, isomorphism):

    # get the name of t1, given the name in t2
    mapping = {v2: v1 for (v1, v2) in isomorphism}

    # these should be the same
    d1 = is_directed(t1)
    d2 = is_directed(t2)
    assert d1 == d2

    edges_1 = []
    for (u, v) in t1.edges():
        if d1:
            edges_1.append((u, v))
        else:
            # if not directed, then need to
            # put the edge in a consistent direction
            if u < v:
                edges_1.append((u, v))
            else:
                edges_1.append((v, u))

    edges_2 = []
    for (u, v) in t2.edges():
        # translate to names for t1
        u = mapping[u]
        v = mapping[v]
        if d2:
            edges_2.append((u, v))
        else:
            if u < v:
                edges_2.append((u, v))
            else:
                edges_2.append((v, u))

    return sorted(edges_1) == sorted(edges_2)


def test_hardcoded():

    print("hardcoded test")

    # define a test problem
    edges_1 = [
        ("a", "b"),
        ("a", "c"),
        ("a", "d"),
        ("b", "e"),
        ("b", "f"),
        ("e", "j"),
        ("e", "k"),
        ("c", "g"),
        ("c", "h"),
        ("g", "m"),
        ("d", "i"),
        ("f", "l"),
    ]

    edges_2 = [
        ("v", "y"),
        ("v", "z"),
        ("u", "x"),
        ("q", "u"),
        ("q", "v"),
        ("p", "t"),
        ("n", "p"),
        ("n", "q"),
        ("n", "o"),
        ("o", "r"),
        ("o", "s"),
        ("s", "w"),
    ]

    # there are two possible correct isomorphisms
    # it currently returns isomorphism1
    # but the second is also correct
    isomorphism1 = [
        ("a", "n"),
        ("b", "q"),
        ("c", "o"),
        ("d", "p"),
        ("e", "v"),
        ("f", "u"),
        ("g", "s"),
        ("h", "r"),
        ("i", "t"),
        ("j", "y"),
        ("k", "z"),
        ("l", "x"),
        ("m", "w"),
    ]

    # could swap y and z
    isomorphism2 = [
        ("a", "n"),
        ("b", "q"),
        ("c", "o"),
        ("d", "p"),
        ("e", "v"),
        ("f", "u"),
        ("g", "s"),
        ("h", "r"),
        ("i", "t"),
        ("j", "z"),
        ("k", "y"),
        ("l", "x"),
        ("m", "w"),
    ]

    t1 = nx.Graph()
    t1.add_edges_from(edges_1)
    root1 = "a"

    t2 = nx.Graph()
    t2.add_edges_from(edges_2)
    root2 = "n"

    isomorphism = sorted(rooted_tree_isomorphism(t1, root1, t2, root2))

    # is correct by hand
    assert (isomorphism == isomorphism1) or (isomorphism == isomorphism2)

    # check algorithmically
    assert check_isomorphism(t1, t2, isomorphism)

    # try again as digraph
    t1 = nx.DiGraph()
    t1.add_edges_from(edges_1)
    root1 = "a"

    t2 = nx.DiGraph()
    t2.add_edges_from(edges_2)
    root2 = "n"

    isomorphism = sorted(rooted_tree_isomorphism(t1, root1, t2, root2))

    # is correct by hand
    assert (isomorphism == isomorphism1) or (isomorphism == isomorphism2)

    # check algorithmically
    assert check_isomorphism(t1, t2, isomorphism)


# randomly swap a tuple (a,b)
def random_swap(t):
    (a, b) = t
    if random.randint(0, 1) == 1:
        return (a, b)
    else:
        return (b, a)


# given a tree t1, create a new tree t2
# that is isomorphic to t1, with a known isomorphism
# and test that our algorithm found the right one
def positive_single_tree(t1):

    assert nx.is_tree(t1)

    nodes1 = [n for n in t1.nodes()]
    # get a random permutation of this
    nodes2 = nodes1.copy()
    random.shuffle(nodes2)

    # this is one isomorphism, however they may be multiple
    # so we don't necessarily get this one back
    someisomorphism = [(u, v) for (u, v) in zip(nodes1, nodes2)]

    # map from old to new
    map1to2 = {u: v for (u, v) in someisomorphism}

    # get the edges with the transformed names
    edges2 = [random_swap((map1to2[u], map1to2[v])) for (u, v) in t1.edges()]
    # randomly permute, to ensure we're not relying on edge order somehow
    random.shuffle(edges2)

    # so t2 is isomorphic to t1
    t2 = nx.Graph()
    t2.add_edges_from(edges2)

    # lets call our code to see if t1 and t2 are isomorphic
    isomorphism = tree_isomorphism(t1, t2)

    # make sure we got a correct solution
    # although not necessarily someisomorphism
    assert len(isomorphism) > 0
    assert check_isomorphism(t1, t2, isomorphism)


# run positive_single_tree over all the
# non-isomorphic trees for k from 4 to maxk
# k = 4 is the first level that has more than 1 non-isomorphic tree
# k = 13 takes about 2.86 seconds to run on my laptop
# larger values run slow down significantly
# as the number of trees grows rapidly
def test_positive(maxk=14):

    print("positive test")

    for k in range(2, maxk + 1):
        start_time = time.time()
        trial = 0
        for t in nx.nonisomorphic_trees(k):
            positive_single_tree(t)
            trial += 1
        print(k, trial, time.time() - start_time)


# test the trivial case of a single node in each tree
# note that nonisomorphic_trees doesn't work for k = 1
def test_trivial():

    print("trivial test")

    # back to an undirected graph
    t1 = nx.Graph()
    t1.add_node("a")
    root1 = "a"

    t2 = nx.Graph()
    t2.add_node("n")
    root2 = "n"

    isomorphism = rooted_tree_isomorphism(t1, root1, t2, root2)

    assert isomorphism == [("a", "n")]

    assert check_isomorphism(t1, t2, isomorphism)


# test another trivial case where the two graphs have
# different numbers of nodes
def test_trivial_2():

    print("trivial test 2")

    edges_1 = [("a", "b"), ("a", "c")]

    edges_2 = [("v", "y")]

    t1 = nx.Graph()
    t1.add_edges_from(edges_1)

    t2 = nx.Graph()
    t2.add_edges_from(edges_2)

    isomorphism = tree_isomorphism(t1, t2)

    # they cannot be isomorphic,
    # since they have different numbers of nodes
    assert isomorphism == []


# the function nonisomorphic_trees generates all the non-isomorphic
# trees of a given size.  Take each pair of these and verify that
# they are not isomorphic
# k = 4 is the first level that has more than 1 non-isomorphic tree
# k = 11 takes about 4.76 seconds to run on my laptop
# larger values run slow down significantly
# as the number of trees grows rapidly
def test_negative(maxk=11):

    print("negative test")

    for k in range(4, maxk + 1):
        test_trees = list(nx.nonisomorphic_trees(k))
        start_time = time.time()
        trial = 0
        for i in range(len(test_trees) - 1):
            for j in range(i + 1, len(test_trees)):
                trial += 1
                assert tree_isomorphism(test_trees[i], test_trees[j]) == []
        print(k, trial, time.time() - start_time)
