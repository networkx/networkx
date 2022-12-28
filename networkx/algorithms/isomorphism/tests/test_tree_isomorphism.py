import random
import time

import networkx as nx
from networkx.algorithms.isomorphism.tree_isomorphism import (
    NaturalMultiset,
    categorize_entries,
    categorize_lists,
    sort_lists_of_naturals,
    sort_natural_multisets,
    get_levels,
    get_initial_values,
    assign_structure,
    get_multisets_list_of_level,
    update_values,
    rooted_tree_isomorphism_n,
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

# Tests the function sort_lists_of_naturals. The expected sorted list should
# have a lexicographical ordering.
def test_sort_list_of_naturals():
    # An arbitrary list of lists of natural numbers.
    S = [
        [0, 0, 1, 2, 3],
        [1, 2, 3],
        [0, 1, 1, 4],
        [3, 3, 4],
        [4],
        [4, 4, 5],
    ]
    
    expected_ordering = [
        [0, 0, 1, 2, 3],
        [0, 1, 1, 4],
        [1, 2, 3],
        [3, 3, 4],
        [4],
        [4, 4, 5],
    ]
    
    obtained_ordering = sort_lists_of_naturals(S)
    
    assert expected_ordering == obtained_ordering
    
    # Test for another list of lists of natural numbers.
    S = [
        [1, 2, 3, 7, 8],
        [2, 2, 3, 4],
        [2, 2, 4, 3],
        [0, 1],
        [0, 0],
        [1, 3, 4],
        [2, 3, 4],
        [7],
        [8, 8],
    ]
    
    expected_ordering = [
        [0, 0],
        [0, 1],
        [1, 2, 3, 7, 8],
        [1, 3, 4],
        [2, 2, 3, 4],
        [2, 2, 4, 3],
        [2, 3, 4],
        [7],
        [8, 8],
    ]

    obtained_ordering = sort_lists_of_naturals(S)
    
    assert expected_ordering == obtained_ordering

# Tests the function sort_natural_multisets. The expected sorted list should
# follow the lexicographical ordering of the multiset representation.
def test_sort_natural_multisets():
    # An arbitrary list of lists of multisets.
    M1 = NaturalMultiset()
    M2 = NaturalMultiset()
    M3 = NaturalMultiset()
    M4 = NaturalMultiset()
    M5 = NaturalMultiset()
    M6 = NaturalMultiset()
    
    M1.from_list([0, 0, 1, 2, 3])
    M2.from_list([1, 2, 3])
    M3.from_list([0, 1, 1, 4])
    M4.from_list([3, 3, 4])
    M5.from_list([4])
    M6.from_list([4, 4, 5])
    
    S = [M1, M2, M3, M4, M5, M6]
    
    expected_ordering = [M1, M3, M2, M4, M5, M6]
    
    obtained_ordering = sort_natural_multisets(S)
    
    assert expected_ordering == obtained_ordering
    
    # Test for another list of lists of natural numbers.
    M1 = NaturalMultiset()
    M2 = NaturalMultiset()
    M3 = NaturalMultiset()
    M4 = NaturalMultiset()
    M5 = NaturalMultiset()
    M6 = NaturalMultiset()
    M7 = NaturalMultiset()
    M8 = NaturalMultiset()
    M9 = NaturalMultiset()
    
    M1.from_list([1, 2, 3, 7, 8])
    M2.from_list([2, 2, 3, 4])
    M3.from_list([2, 2, 4, 3])
    M4.from_list([0, 1])
    M5.from_list([0, 0])
    M6.from_list([1, 3, 4])
    M7.from_list([2, 3, 4])
    M8.from_list([7])
    M9.from_list([8, 8])
    
    S = [M1, M2, M3, M4, M5, M6, M7, M8, M9]
    expected_ordering = [M5, M4, M1, M6, M2, M3, M7, M8, M9]

    obtained_ordering = sort_natural_multisets(S)
    
    assert expected_ordering == obtained_ordering

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

# Tests the function assign_values. The returned function should assign to all
# the vertices found on the i-th level a structure.
def test_assign_values():
    # Test for an specific scenario.
    levels = {
        2 : {"v0"},
        1 : {"v1", "v2", "v3"},
        0 : {"v4", "v5", "v6"},
    }
    
    values = {
        "v0" : 1,
        "v1" : 2,
        "v2" : 0,
        "v3" : 1,
        "v4" : 0,
        "v5" : 0,
        "v6" : 0,
    }
    
    parenthood = {
        "v1" : "v0",
        "v2" : "v0",
        "v3" : "v0",
        "v4" : "v1",
        "v5" : "v1",
        "v6" : "v3",
    }
    
    expected_structure_lvl_2 = {
        "v0" : NaturalMultiset([0, 1, 2]),
    }

    expected_structure_lvl_1 = {
        "v1" : NaturalMultiset([0, 0]),
        "v3" : NaturalMultiset([0]),
    }

    obtained_structure_lvl_1 = assign_structure(parenthood, levels, values, 1)
    obtained_structure_lvl_2 = assign_structure(parenthood, levels, values, 2)
    
    assert obtained_structure_lvl_1 == expected_structure_lvl_1
    assert obtained_structure_lvl_2 == expected_structure_lvl_2

# Tests the function get_multisets_list_of_level. The returned list should
# correspond to the structures of the vertices found on the i-th level, and the
# map should correspond to a mapping of structures to the vertices that have
# said structure.
def test_get_multisets_list_of_level():
    # Test for an specific scenario.
    levels = {
        2 : {"v0"},
        1 : {"v1", "v2", "v3", "v7"},
        0 : {"v4", "v5", "v6", "v8"},
    }
    
    values = {
        "v0" : 1,
        "v1" : 2,
        "v2" : 0,
        "v3" : 1,
        "v7" : 1,
        "v4" : 0,
        "v5" : 0,
        "v6" : 0,
        "v8" : 0,
    }
    
    parenthood = {
        "v1" : "v0",
        "v2" : "v0",
        "v3" : "v0",
        "v7" : "v0",
        "v4" : "v1",
        "v5" : "v1",
        "v6" : "v3",
        "v8" : "v7",
    }
    
    structures_lvl_2 = {
        "v0" : NaturalMultiset([0, 1, 2]),
    }

    structures_lvl_1 = {
        "v1" : NaturalMultiset([0, 0]),
        "v3" : NaturalMultiset([0]),
        "v7" : NaturalMultiset([0]),
    }

    expected_mapping_lvl_2 = {
        NaturalMultiset([0, 1, 2]) : {"v0"},
    }

    expected_mapping_lvl_1 = {
        NaturalMultiset([0, 0]) : {"v1"},
        NaturalMultiset([0]) : {"v3", "v7"},
    }
    
    obt_list_lvl_1, obt_mapping_lvl_1 = get_multisets_list_of_level(levels, values, structures_lvl_1, 1)
    obt_list_lvl_2, obt_mapping_lvl_2 = get_multisets_list_of_level(levels, values, structures_lvl_2, 2)

    assert len(structures_lvl_1) == len(obt_list_lvl_1)
    for key in structures_lvl_1:
        assert structures_lvl_1[key] in obt_list_lvl_1

    assert len(structures_lvl_2) == len(obt_list_lvl_2)
    for key in structures_lvl_2:
        assert structures_lvl_2[key] in obt_list_lvl_2
    
    assert obt_mapping_lvl_1 == expected_mapping_lvl_1
    assert obt_mapping_lvl_2 == expected_mapping_lvl_2

def test_get_multisets_list_of_level():
    # Test for an specific scenario.
    # Starting values.
    values = {
        "v0" : -1,
        "v1" : -1,
        "v2" : 0,
        "v3" : -1,
        "v7" : -1,
        "v4" : 0,
        "v5" : 0,
        "v6" : 0,
        "v8" : 0,
    }

    mapping_lvl_1 = {
        NaturalMultiset([0, 0]) : {"v1"},
        NaturalMultiset([0]) : {"v3", "v7"},
    }
    
    structures_list_lvl_1 = (
        NaturalMultiset([0]),
        NaturalMultiset([0]),
        NaturalMultiset([0, 0]),
    )

    expected_values_after_lvl_1 = {
        "v0" : -1,
        "v1" : 2,
        "v2" : 0,
        "v3" : 1,
        "v7" : 1,
        "v4" : 0,
        "v5" : 0,
        "v6" : 0,
        "v8" : 0,
    }
    
    update_values(structures_list_lvl_1, mapping_lvl_1, values)
    
    assert expected_values_after_lvl_1 == values

    structures_list_lvl_2 = (
        NaturalMultiset([2, 0, 1]),
    )
    
    mapping_lvl_2 = {
        NaturalMultiset([0, 1, 2]) : {"v0"},
    }

    expected_values_after_lvl_2 = {
        "v0" : 1,
        "v1" : 2,
        "v2" : 0,
        "v3" : 1,
        "v7" : 1,
        "v4" : 0,
        "v5" : 0,
        "v6" : 0,
        "v8" : 0,
    }

    update_values(structures_list_lvl_2, mapping_lvl_2, values)
    
    assert expected_values_after_lvl_2 == values

# Tests the function rooted_tree_isomorphism_n.
def test_rooted_tree_isomorphism_n_hardcoded():
    # The following trees are isomorph.
    edges_t1 = [("v0", "v1"), ("v0", "v2"), ("v0", "v3"),
                ("v1", "v4"), ("v1", "v5"), ("v3", "v6"), 
                ("v4", "v7"), ("v4", "v8"), ("v4", "v9"), 
                ("v6", "v10"), ("v6", "v11"), ("v9", "v12")]
    T1 = nx.Graph(edges_t1)
    
    edged_t2 = [("w0", "w1"), ("w0", "w2"), ("w0", "w3"),
                ("w2", "w4"), ("w4", "w5"), ("w4", "w6"),
                ("w3", "w7"), ("w3", "w8"), ("w8", "w9"), 
                ("w8", "w10"), ("w8", "w11"), ("w10", "w12")]
    
    T2 = nx.Graph(edged_t2)
    
    assert rooted_tree_isomorphism_n(T1, "v0", T2, "w0")

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
