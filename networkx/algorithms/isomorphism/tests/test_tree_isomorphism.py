import random
import time
from collections import Counter, defaultdict

import networkx as nx
from networkx.algorithms.isomorphism.tree_isomorphism import (
    get_centers_of_tree,
    get_initial_maps_and_height,
    group_structures_in_level,
    rooted_tree_isomorphism,
    tree_isomorphism,
    update_values,
)
from networkx.classes.function import is_directed


# Test the get_initial_maps_and_height function.
def test_get_intial_maps_and_height():
    # Test for an arbitrary graph.
    edges_t1 = [
        ("v0", "v1"),
        ("v0", "v2"),
        ("v0", "v3"),
        ("v1", "v4"),
        ("v1", "v5"),
        ("v3", "v6"),
    ]
    T1 = nx.Graph(edges_t1)

    expected_levels = {
        2: {"v0"},
        1: {"v1", "v2", "v3"},
        0: {"v4", "v5", "v6"},
    }

    expected_values = {
        "v0": -1,
        "v1": -1,
        "v2": 0,
        "v3": -1,
        "v4": 0,
        "v5": 0,
        "v6": 0,
    }

    expected_intial_children = {
        "v1": {"v4", "v5"},
        "v3": {"v6"},
    }

    expected_parenthood = {
        "v1": "v0",
        "v2": "v0",
        "v3": "v0",
        "v4": "v1",
        "v5": "v1",
        "v6": "v3",
    }

    expected_height = 2

    o_l, o_v, o_c, o_p, obt_h = get_initial_maps_and_height(T1, "v0")

    assert expected_levels == o_l
    assert expected_values == o_v

    for v in expected_intial_children.keys():
        assert v in o_c

        for u in expected_intial_children[v]:
            assert u in o_c[v]

    assert expected_parenthood == o_p
    assert expected_height == 2


# Tests the function group_structures_in_level. The returned counter should
# correspond to the structures of the vertices found on the i-th level, and the
# map should correspond to a mapping of structures to the vertices that have
# said structure.
def test_group_structures_in_level():
    # Test for an specific scenario.
    levels = {
        2: {"v0"},
        1: {"v1", "v2", "v3", "v7"},
        0: {"v4", "v5", "v6", "v8"},
    }

    values = {
        "v0": 1,
        "v1": 2,
        "v2": 0,
        "v3": 1,
        "v7": 1,
        "v4": 0,
        "v5": 0,
        "v6": 0,
        "v8": 0,
    }

    parenthood = {
        "v1": "v0",
        "v2": "v0",
        "v3": "v0",
        "v7": "v0",
        "v4": "v1",
        "v5": "v1",
        "v6": "v3",
        "v8": "v7",
    }

    structures_lvl_2 = {
        "v0": Counter([0, 1, 2]),
    }

    structures_lvl_1 = {
        "v1": Counter([0, 0]),
        "v3": Counter([0]),
        "v7": Counter([0]),
        "v2": Counter(),
    }

    expected_counter_lvl_2 = Counter([(0, 1, 2)])
    expected_counter_lvl_1 = Counter(
        [
            (0, 0),
            (0,),
            (0,),
            (),
        ]
    )

    expected_mapping_lvl_2 = {
        (0, 1, 2): {"v0"},
    }

    expected_mapping_lvl_1 = {
        (0, 0): {"v1"},
        (0,): {"v3", "v7"},
        (): {"v2"},
    }

    obt_counter_lvl_1, obt_mapping_lvl_1 = group_structures_in_level(
        levels, values, structures_lvl_1, 1
    )
    obt_counter_lvl_2, obt_mapping_lvl_2 = group_structures_in_level(
        levels, values, structures_lvl_2, 2
    )

    assert expected_counter_lvl_1 == obt_counter_lvl_1
    assert obt_mapping_lvl_1 == expected_mapping_lvl_1

    assert expected_counter_lvl_2 == obt_counter_lvl_2
    assert obt_mapping_lvl_2 == expected_mapping_lvl_2


def test_update_values():
    # Test for an specific scenario.
    vals_T1 = {
        "v0": -1,
        "v1": -1,
        "v2": 0,
        "v3": -1,
        "v7": -1,
        "v4": 0,
        "v5": 0,
        "v6": 0,
        "v8": 0,
    }

    parenthood_T1 = {
        "v1": "v0",
        "v2": "v0",
        "v3": "v0",
        "v7": "v0",
        "v4": "v1",
        "v5": "v1",
        "v6": "v3",
        "v8": "v7",
    }

    structures_lvl_1 = Counter([(0, 0), (0,)])

    mapping_lvl_1_T1 = {
        (0, 0): {"v1"},
        (0,): {"v3", "v7"},
    }

    children_T1 = defaultdict(list)
    children_T1["v1"] = ["v4", "v5"]
    children_T1["v3"] = ["v6"]
    children_T1["v7"] = ["v8"]

    leaves_lvl_1_T1 = {"v2"}

    vals_T2 = {
        "w0": -1,
        "w1": 0,
        "w2": -1,
        "w3": -1,
        "w4": -1,
        "w5": 0,
        "w6": 0,
        "w7": 0,
        "w8": 0,
    }

    parenthood_T2 = {
        "w1": "w0",
        "w2": "w0",
        "w3": "w0",
        "w4": "w0",
        "w5": "w2",
        "w6": "w3",
        "w7": "w4",
        "w8": "w4",
    }

    mapping_lvl_1_T2 = {
        (0, 0): {"w4"},
        (0,): {"w2", "w3"},
    }

    children_T2 = defaultdict(list)
    children_T2["w4"] = ["w7", "w8"]
    children_T2["w2"] = ["w5"]
    children_T2["w3"] = ["w6"]

    leaves_lvl_1_T2 = {"w1"}

    possible_vals_T1_1 = {
        "v0": -1,
        "v1": 2,
        "v2": 0,
        "v3": 1,
        "v7": 1,
        "v4": 0,
        "v5": 0,
        "v6": 0,
        "v8": 0,
    }

    possible_vals_T1_2 = {
        "v0": -1,
        "v1": 1,
        "v2": 0,
        "v3": 2,
        "v7": 2,
        "v4": 0,
        "v5": 0,
        "v6": 0,
        "v8": 0,
    }

    possible_vals_T2_1 = {
        "w0": -1,
        "w1": 0,
        "w2": 1,
        "w3": 1,
        "w4": 2,
        "w5": 0,
        "w6": 0,
        "w7": 0,
        "w8": 0,
    }

    possible_vals_T2_2 = {
        "w0": -1,
        "w1": 0,
        "w2": 2,
        "w3": 2,
        "w4": 1,
        "w5": 0,
        "w6": 0,
        "w7": 0,
        "w8": 0,
    }

    update_values(
        structures_lvl_1,
        mapping_lvl_1_T1,
        mapping_lvl_1_T2,
        vals_T1,
        vals_T2,
        children_T1,
        children_T2,
        parenthood_T1,
        parenthood_T2,
    )

    assert (vals_T1 == possible_vals_T1_1) or (vals_T1 == possible_vals_T1_2)
    assert (vals_T2 == possible_vals_T2_1) or (vals_T2 == possible_vals_T2_2)

    for struct in structures_lvl_1:
        for v_T1 in mapping_lvl_1_T1[struct]:
            for v_T2 in mapping_lvl_1_T2[struct]:
                assert vals_T1[v_T1] == vals_T2[v_T2]

    structures_lvl_2 = Counter([(0, 1, 2)])

    mapping_lvl_2_T1 = {
        (0, 1, 2): {"v0"},
    }

    mapping_lvl_2_T2 = {
        (0, 1, 2): {"w0"},
    }

    possible_vals_T1_1 = {
        "v0": 1,
        "v1": 2,
        "v2": 0,
        "v3": 1,
        "v7": 1,
        "v4": 0,
        "v5": 0,
        "v6": 0,
        "v8": 0,
    }

    possible_vals_T1_2 = {
        "v0": 1,
        "v1": 1,
        "v2": 0,
        "v3": 2,
        "v7": 2,
        "v4": 0,
        "v5": 0,
        "v6": 0,
        "v8": 0,
    }

    possible_vals_T2_1 = {
        "w0": 1,
        "w1": 0,
        "w2": 1,
        "w3": 1,
        "w4": 2,
        "w5": 0,
        "w6": 0,
        "w7": 0,
        "w8": 0,
    }

    possible_vals_T2_2 = {
        "w0": 1,
        "w1": 0,
        "w2": 2,
        "w3": 2,
        "w4": 1,
        "w5": 0,
        "w6": 0,
        "w7": 0,
        "w8": 0,
    }

    update_values(
        structures_lvl_2,
        mapping_lvl_2_T1,
        mapping_lvl_2_T2,
        vals_T1,
        vals_T2,
        children_T1,
        children_T2,
        parenthood_T1,
        parenthood_T2,
    )

    assert (vals_T1 == possible_vals_T1_1) or (vals_T1 == possible_vals_T1_2)
    assert (vals_T2 == possible_vals_T2_1) or (vals_T2 == possible_vals_T2_2)

    for struct in structures_lvl_1:
        for v_T1 in mapping_lvl_1_T1[struct]:
            for v_T2 in mapping_lvl_1_T2[struct]:
                assert vals_T1[v_T1] == vals_T2[v_T2]


# Auxiliary function to determine if an isomorphism is valid.  Let f be an
# isomorphism, then u and v are adjacent if and only if f(u) and f(v) are
# adjacent.
def is_valid_isomorphism(T1, T2, isomorphism):
    # Test that for all (u, v) in E_T1 then (f(u), f(v)) in E_T2.
    for (u, v) in T1.edges():
        if not T2.has_edge(isomorphism[u], isomorphism[v]):
            return False

    # Define the inverse mapping of the isomorphism.
    inverse_iso = {}

    for v in isomorphism:
        inverse_iso[isomorphism[v]] = v

    # Test that for all (u, v) in E_T2 then (f^-1(u), f^-1(v)) in E_T1.
    for (u, v) in T2.edges():
        if not T1.has_edge(inverse_iso[u], inverse_iso[v]):
            return False

    # If both conditions are satisfied, return true.
    return True


# Tests the function rooted_tree_isomorphism.
def test_rooted_tree_isomorphism_hardcoded():
    # The following trees are isomorph.
    edges_t1 = [
        ("v0", "v1"),
        ("v0", "v2"),
        ("v0", "v3"),
        ("v1", "v4"),
        ("v1", "v5"),
        ("v3", "v6"),
        ("v4", "v7"),
        ("v4", "v8"),
        ("v4", "v9"),
        ("v6", "v10"),
        ("v6", "v11"),
        ("v9", "v12"),
    ]
    T1 = nx.Graph(edges_t1)

    edged_t2 = [
        ("w0", "w1"),
        ("w0", "w2"),
        ("w0", "w3"),
        ("w2", "w4"),
        ("w4", "w5"),
        ("w4", "w6"),
        ("w3", "w7"),
        ("w3", "w8"),
        ("w8", "w9"),
        ("w8", "w10"),
        ("w8", "w11"),
        ("w10", "w12"),
    ]

    T2 = nx.Graph(edged_t2)

    are_iso, iso = rooted_tree_isomorphism(T1, "v0", T2, "w0")

    assert are_iso
    assert is_valid_isomorphism(T1, T2, iso)


# Tests the function get_centers_of_tree.
def test_get_centers_of_tree():
    # Hardcoded trees.
    edges_t1 = [
        ("v0", "v1"),
        ("v1", "v3"),
        ("v3", "v2"),
        ("v3", "v4"),
        ("v3", "v5"),
        ("v5", "v6"),
        ("v6", "v7"),
        ("v7", "v8"),
    ]
    T1 = nx.Graph(edges_t1)

    centers_t1 = get_centers_of_tree(T1)
    assert centers_t1 == {"v5"}

    edges_t2 = [
        ("u0", "u1"),
        ("u1", "u2"),
        ("u2", "u3"),
        ("u3", "u4"),
        ("u4", "u5"),
        ("u4", "u6"),
        ("u4", "u7"),
        ("u7", "u8"),
    ]
    T2 = nx.Graph(edges_t2)

    centers_t2 = get_centers_of_tree(T2)
    assert centers_t2 == {"u3"}

    edges_t3 = [("w0", "w1"), ("w1", "w2"), ("w2", "w3"), ("w3", "w4"), ("w4", "w5")]
    T3 = nx.Graph(edges_t3)

    centers_t3 = get_centers_of_tree(T3)
    assert centers_t3 == {"w2", "w3"}


# Tests the function tree_isomorphism.
def test_tree_isomorphism_hardcoded():
    # Hardcoded trees.
    edges_t1 = [
        ("v0", "v1"),
        ("v1", "v3"),
        ("v3", "v2"),
        ("v3", "v4"),
        ("v3", "v5"),
        ("v5", "v6"),
        ("v6", "v7"),
        ("v7", "v8"),
    ]
    T1 = nx.Graph(edges_t1)

    edges_t2 = [
        ("u0", "u1"),
        ("u1", "u2"),
        ("u2", "u3"),
        ("u3", "u4"),
        ("u4", "u5"),
        ("u4", "u6"),
        ("u4", "u7"),
        ("u7", "u8"),
    ]
    T2 = nx.Graph(edges_t2)

    is_iso, isomorphism = tree_isomorphism(T1, T2)
    assert is_iso
    assert is_valid_isomorphism(T1, T2, isomorphism)

    # Previous hardcoded test
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
    T1 = nx.Graph(edges_1)

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
    T2 = nx.Graph(edges_2)

    # Possible isomorphisms.
    isomorphism1 = {
        "a": "n",
        "b": "q",
        "c": "o",
        "d": "p",
        "e": "v",
        "f": "u",
        "g": "s",
        "h": "r",
        "i": "t",
        "j": "y",
        "k": "z",
        "l": "x",
        "m": "w",
    }

    # could swap y and z
    isomorphism2 = {
        "a": "n",
        "b": "q",
        "c": "o",
        "d": "p",
        "e": "v",
        "f": "u",
        "g": "s",
        "h": "r",
        "i": "t",
        "j": "z",
        "k": "y",
        "l": "x",
        "m": "w",
    }

    is_iso, isomorphism = tree_isomorphism(T1, T2)

    assert is_iso
    assert (isomorphism == isomorphism1) or (isomorphism == isomorphism2)
    assert is_valid_isomorphism(T1, T2, isomorphism)


# Tests the function tree_isomorphism_n with some trivial graphs.
def test_tree_isomorphism_trivials():
    # Test the trivial case of empty trees, i.e. no nodes.
    T1 = nx.Graph()
    T2 = nx.Graph()

    is_iso, isomorphism = tree_isomorphism(T1, T2)
    assert is_iso
    assert isomorphism == {}

    # Test the trivial case of a single node in each tree.
    T1 = nx.Graph()
    T1.add_node("a")

    T2 = nx.Graph()
    T2.add_node("n")

    is_iso, isomorphism = tree_isomorphism(T1, T2)

    assert is_iso
    assert isomorphism == {"a": "n"}
    assert is_valid_isomorphism(T1, T2, isomorphism)

    # Test another trivial case where the two graphs have different numbers of
    # nodes.

    edges_1 = [("a", "b"), ("a", "c")]

    edges_2 = [("v", "y")]

    T1 = nx.Graph(edges_1)
    T2 = nx.Graph(edges_2)

    is_iso, isomorphism = tree_isomorphism(T1, T2)

    assert not is_iso
    assert isomorphism == {}

    # Test another trivial case where the two graphs have the same different
    # numbers of nodes but differ in structure.
    edges_1 = [("a", "b"), ("b", "c"), ("c", "d"), ("d", "e")]
    edges_2 = [("a", "b"), ("b", "c"), ("b", "d"), ("c", "e")]

    T1 = nx.Graph(edges_1)
    T2 = nx.Graph(edges_2)

    is_iso, isomorphism = tree_isomorphism(T1, T2)

    assert not is_iso
    assert isomorphism == {}


# Given a tree T1, create a new tree T2 that is isomorphic to T1.
def generate_isomorphism(T1):

    assert nx.is_tree(T1)

    # Get a random permutation of the nodes of T1.
    nodes1 = list(T1)
    nodes2 = nodes1.copy()
    random.shuffle(nodes2)

    # this is one isomorphism, however they may be multiple
    # so we don't necessarily get this one back
    someisomorphism = [(u, v) for (u, v) in zip(nodes1, nodes2)]

    # map from old to new
    map1to2 = {u: v for (u, v) in someisomorphism}

    # get the edges with the transformed names
    edges2 = [random_swap((map1to2[u], map1to2[v])) for (u, v) in T1.edges()]
    # randomly permute, to ensure we're not relying on edge order somehow
    random.shuffle(edges2)

    # so t2 is isomorphic to t1
    T2 = nx.Graph(edges2)

    return T2


# The function nonisomorphic_trees generates all the non-isomorphic trees of a
# given order. Take each tree, make a "copy" of it, and its copy should be
# isomorphic to the original; verify that the function tree_isomorphism returns
# True and a proper isomorphism. For k=15 the tests take 4.16 seconds aprox.
def test_tree_isomorphism_positive(maxk=13):
    print("\nPositive test with new function\n")

    for k in range(2, maxk + 1):
        start_time = time.time()
        trial = 0
        for T1 in nx.nonisomorphic_trees(k):
            T2 = generate_isomorphism(T1)

            is_iso, isomorphism = tree_isomorphism(T1, T2)

            assert is_iso
            assert is_valid_isomorphism(T1, T2, isomorphism)

            trial += 1

        print(k, trial, time.time() - start_time)


# The function nonisomorphic_trees generates all the non-isomorphic trees of a
# given order. Take each pair of trees verify that the function tree_isomorphism
# returns False and an empty isomorphism. For k = 11 the tests take 1.28 seconds
# aprox.
def test_tree_isomorphism_negative(maxk=11):
    print("\nNegative test with new function\n")

    for k in range(4, maxk + 1):
        test_trees = list(nx.nonisomorphic_trees(k))
        start_time = time.time()
        trial = 0
        for i in range(len(test_trees) - 1):
            T1 = test_trees[i]
            for j in range(i + 1, len(test_trees)):
                trial += 1

                T2 = test_trees[j]
                is_iso, isomorphism = tree_isomorphism(T1, T2)

                assert not is_iso

        print(k, trial, time.time() - start_time)


# randomly swap a tuple (a,b)
def random_swap(t):
    (a, b) = t
    if random.randint(0, 1) == 1:
        return (a, b)
    else:
        return (b, a)
