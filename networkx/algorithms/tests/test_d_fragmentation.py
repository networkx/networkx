import pytest
import networkx as nx
import networkx.generators.trees as tree_constructors
import networkx.algorithms.d_fragmentation as sut
import random as rand
from networkx.algorithms.shortest_paths.unweighted import (
    single_source_shortest_path_length as sssp,
)
from networkx.algorithms.shortest_paths.unweighted import (
    all_pairs_shortest_path_length as apsp,
)
from networkx.algorithms.tree import recognition
from networkx.algorithms.components import connected


TREE_SIZE = {"LOWER_BOUND": 1, "UPPER_BOUND": 10000}

# The value for d in the d-club.
CLUB_SIZE = {"LOWER_BOUND": 1, "UPPER_BOUND": 50}


def _get_random_number_from_bound(l_bound: int, u_bound: int):
    assert min(l_bound, u_bound) >= 0
    assert u_bound >= l_bound
    return rand.randint(l_bound, u_bound)


def _get_random_number_of_nodes():
    return _get_random_number_from_bound(
        TREE_SIZE["LOWER_BOUND"], TREE_SIZE["UPPER_BOUND"]
    )


def _get_random_number_of_edges(nodes):
    upper_edges = max(0, (nodes * (nodes - 1)) // 2)
    # To get a sparse graph, we divide the upper bound of edges by a large
    # enough number like 2**5.
    return _get_random_number_from_bound(0, max(1, upper_edges // (2 ** 5)))


def _get_random_club_size():
    return _get_random_number_from_bound(
        CLUB_SIZE["LOWER_BOUND"], CLUB_SIZE["UPPER_BOUND"]
    )


def _get_random_tree():
    num_nodes = _get_random_number_of_nodes()
    return tree_constructors.random_tree(num_nodes)


def _remove_edges(g: nx.Graph, edges_to_remove):
    nx.freeze(g)
    h = nx.Graph(g)
    h.remove_edges_from(edges_to_remove)
    return h


def _get_random_node(G: nx.Graph):
    it = list(G.nodes)
    return it[0]


def _get_non_tree_diameter(g: nx.Graph) -> int:
    """
    Compute the diameter in a graph that is not a tree.

    Parameters
    ----------
    g: nx.Graph
        A networkX graph.


    Notes
    _____
        Relies on an efficient implementation of the
        APSP. Currently relies on Bellman-Ford and runs
        in O(|V|^3).

    Returns
    -------

    """
    apsp_values = dict(apsp(g))

    highest = 0

    for x in g.nodes:
        for y in g.nodes:
            highest = max(highest, apsp_values[x][y])
    return highest


def _get_tree_diameter(tree: nx.Graph) -> int:
    """
    Calculate the diameter of the tree using the
    classic two BFS/DFS approach.

    Parameters
    ----------
    tree: An unweighted undirected simple Tree.

    Returns
    -------
    The diameter of the tree.
    """
    start = _get_random_node(tree)
    distances_from_start = sssp(tree, start)

    if len(distances_from_start) == 0:
        return 0

    antipodal_one = max(distances_from_start, key=lambda x: distances_from_start[x])
    distances_from_antipodal_one = sssp(tree, antipodal_one)
    antipodal_two = max(
        distances_from_antipodal_one, key=lambda x: distances_from_antipodal_one[x]
    )

    return distances_from_antipodal_one[antipodal_two]


def _get_diameters_of_components(g: nx.Graph):
    """
    Get the diameters of the connected components
    in g.
    Parameters
    ----------
    g: A networkX graph.

    Returns
    -------
    The diameters of its connected components in some order.
    """
    for comp in connected.connected_components(g):
        h = g.subgraph(comp)
        if not recognition.is_tree(h):
            yield _get_non_tree_diameter(h)
        else:
            yield _get_tree_diameter(h)


def d_fragmentation_in_graphs(g: nx.Graph, d: int):
    """
    A testing helper that tests if the result of the
    `d-fragmented` algorithm on g produces a d-club cluster graph.

    A computation verification of optimality is through a brute force
    in which, one tries removing every subset of size smaller than that
    produced by `d-fragmented` and verifying if the resultant graph is
    a d-club cluster graph.

    Due to its exponential runtime, we rely on a proof of correctness
    given in a (WIP) paper by Oellerman O., and Patel A. (2020).

    Parameters
    ----------
    g: A networkX graph.
    d: The size of the club.

    Returns
    -------
    None

    """
    if d < 0:
        with pytest.raises(ValueError):
            sut.d_fragmented(g, d)
    elif d == 0:
        assert set(sut.d_fragmented(g, d)) == set(g.edges)
    elif recognition.is_forest(g):

        # After removing the selected edge_set,
        # check that the diameter in all the components
        # of the resultant graph is at most d.
        # Hence the resultant graph is a d-club cluster graph.

        chosen_edges = list(sut.d_fragmented(g, d))
        h = _remove_edges(g, chosen_edges)
        diam_list = list(_get_diameters_of_components(h))
        assert max(diam_list) <= d

    return


def test_multiple(count: int = 5):
    """
    Test the `d-fragmented` algorithm on
    multiple random trees and graphs
    on some order (defined in `TREE_SIZE`, and
    `CLUB_SIZE`).

    Parameters
    ----------
    count: The number of graphs to be tested.

    Returns
    -------
    None
    """
    trees = count

    # Check some random trees on some order.
    for _ in range(trees):
        g = _get_random_tree()
        d = _get_random_club_size()
        d_fragmentation_in_graphs(g, d)
    print(f"Tested d-club cluster graphs for {trees:02d} random trees successfully!")
    return
