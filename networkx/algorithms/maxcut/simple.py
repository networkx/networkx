import numpy as np
import networkx as nx
from networkx.utils.decorators import preserve_random_state


@preserve_random_state
def randomized_2_approx(G, seed=0, weight=None):
    """
    Implementation of a 2 approximation algorithm for MaxCut

    Parameters
    ----------
    G: NetworkX graph

    seed: int
        To control randomization

    weight : object
        Edge attribute key to use as weight. If not specified, edges
        have weight one.

    Returns
    -------
    cut_size : integer, float
        Value of the minimum cut.

    partition : pair of node sets
        A partitioning of the nodes that defines a minimum cut.
    """
    np.random.seed(seed)
    cut = set()
    for node in G.nodes():
        if np.random.random_sample() < 0.5:
            cut.add(node)
    cut_size = nx.algorithms.cut_size(G, cut, weight=weight)
    partition = (cut, set(G.nodes) - cut)
    return cut_size, partition


def _swap_node_parition(cut, node):
    if node in cut:
        new_cut = cut - {node}
    else:
        new_cut = cut.union({node})
    return new_cut


@preserve_random_state
def one_exchange(G, initial_cut=None, seed=0, weight=None):
    """
    Parameters
    ----------
    G: networkx Graph
        Graph to find a maximum cut for
    initial_cut: set
        Cut to use as a starting point
    seed: int
        To control randomization
    weight : object
        Edge attribute key to use as weight. If not specified, edges
        have weight one.

    Returns
    -------
    cut_value : integer, float
        Value of the maximum cut.

    partition : pair of node sets
        A partitioning of the nodes that defines a maximum cut.
    """
    if initial_cut is None:
        initial_cut = set()
    np.random.seed(seed)
    cut = set(initial_cut)
    current_cut_size = nx.algorithms.cut_size(G, cut, weight=weight)
    while True:
        nodes = list(G.nodes())
        np.random.shuffle(nodes)
        best_node_to_swap = max(nodes,
                                key=lambda v: nx.algorithms.cut_size(G, _swap_node_parition(cut, v), weight=weight),
                                default=None)
        potential_cut = _swap_node_parition(cut, best_node_to_swap)
        potential_cut_size = nx.algorithms.cut_size(G, potential_cut, weight=weight)

        if potential_cut_size > current_cut_size:
            cut = potential_cut
            current_cut_size = potential_cut_size
        else:
            break

    partition = (cut, set(G.nodes) - cut)
    return current_cut_size, partition
